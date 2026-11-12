import json
import os
from json import JSONDecodeError

from openai import OpenAI
from pydantic import ValidationError
from typing import Any, Iterator, Optional, Sequence

from .tools import Tool

class OpenModel:
    def __init__(self, model_name: str,temperature: float = 0.7, max_output_tokens: int = 1200,
                 top_p =1,
                 top_k =0,
                 top_a = 0,
                 min_p = 0,
                 thinking = False,
                 reasoning_effort: Optional[str] = None,
                 reasoning_max_tokens: Optional[int] = None,
                 reasoning_exclude: bool = True,
                 provider: Optional[dict[str, Any]] = None,
                 max_retries: int = 4,
                 api_key: Optional[str] = None,
                 base_url: str = "https://openrouter.ai/api/v1",
                 ):
        if not isinstance(max_retries, int) or isinstance(max_retries, bool) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")

        selected_api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not selected_api_key:
            raise ValueError(
                "An OpenRouter API key is required (api_key or OPENROUTER_API_KEY)."
            )
        self.client = OpenAI(api_key=selected_api_key, base_url=base_url)
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.max_retries = max_retries
        self.top_p = top_p
        self.top_k = top_k
        self.top_a = top_a
        self.min_p = min_p
        self.thinking = thinking
        self.reasoning_effort = reasoning_effort
        self.reasoning_max_tokens = reasoning_max_tokens
        self.reasoning_exclude = reasoning_exclude
        self.provider = dict(provider) if provider is not None else None

    def _extra_body(self):
        reasoning = {"exclude": self.reasoning_exclude}
        if not self.thinking:
            reasoning["enabled"] = False
        elif self.reasoning_max_tokens is not None:
            reasoning["max_tokens"] = self.reasoning_max_tokens
        elif self.reasoning_effort:
            reasoning["effort"] = self.reasoning_effort
        else:
            reasoning["enabled"] = True
        # Do not send disabled sampling extensions. With OpenRouter provider
        # filtering enabled, even a zero-valued unsupported parameter can make
        # every otherwise compatible endpoint ineligible.
        extra_body = {"reasoning": reasoning}
        if self.top_k:
            extra_body["top_k"] = self.top_k
        if self.top_a:
            extra_body["top_a"] = self.top_a
        if self.min_p:
            extra_body["min_p"] = self.min_p
        if self.provider is not None:
            extra_body["provider"] = self.provider
        return extra_body

    def generate_object(self, inputs, text_format = None,): 
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.client.responses.parse(
                    model=self.model_name,
                    input=inputs,
                    text_format=text_format,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_output_tokens=self.max_output_tokens,
                    extra_body=self._extra_body(),
                )
                output = resp.output_parsed
                if output is None:
                    status = getattr(resp, "status", None)
                    incomplete = getattr(resp, "incomplete_details", None)
                    error = getattr(resp, "error", None)
                    raise RuntimeError(
                        "The model returned no parsed object. "
                        "The structured response may be empty, refused, malformed, "
                        f"or truncated (status={status!r}, "
                        f"incomplete_details={incomplete!r}, error={error!r})."
                    )
                return output
            except (ValidationError, JSONDecodeError) as e:
                if attempt == self.max_retries:
                    raise
                print(
                    f"❌ Structured output error "
                    f"(attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                print(
                    f"🔥 API error "
                    f"(attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )

    def _create_text_completion(self, messages, **options):
        """Call Chat Completions, retrying the API request only."""
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_output_tokens,
                    extra_body=self._extra_body(),
                    **options,
                )
                if not resp.choices:
                    raise RuntimeError("The model returned no choices")
                return resp
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                print(
                    f"🔥 Text generation error "
                    f"(retry {attempt + 1}/{self.max_retries}): {e}"
                )

    def generate_text(
        self,
        inputs,
        *,
        tools: Optional[Sequence[Tool]] = None,
        tool_choice: Any = "auto",
        max_tool_rounds: int = 8,
        response_format: Optional[dict[str, Any]] = None,
    ):
        if (
            not isinstance(max_tool_rounds, int)
            or isinstance(max_tool_rounds, bool)
            or max_tool_rounds < 0
        ):
            raise ValueError("max_tool_rounds must be a non-negative integer")

        tool_list = list(tools or [])
        registry = {}
        for tool in tool_list:
            if not isinstance(tool, Tool):
                raise TypeError("tools must contain Tool instances")
            if tool.name in registry:
                raise ValueError(f"Duplicate tool name: {tool.name}")
            registry[tool.name] = tool

        definitions = [tool.definition() for tool in tool_list]
        messages = list(inputs)

        for tool_round in range(max_tool_rounds + 1):
            options = {}
            if response_format is not None:
                options["response_format"] = response_format
            if definitions:
                options["tools"] = definitions
                options["tool_choice"] = tool_choice

            resp = self._create_text_completion(messages, **options)
            choice = resp.choices[0]
            message = choice.message
            tool_calls = message.tool_calls or []

            if not tool_calls:
                text = message.content
                if not isinstance(text, str) or not text.strip():
                    raise RuntimeError(
                        "The model returned neither text nor tool calls "
                        f"(finish_reason={choice.finish_reason!r})"
                    )
                return text

            if tool_round == max_tool_rounds:
                raise RuntimeError(
                    f"Maximum number of tool rounds reached ({max_tool_rounds})"
                )

            messages.append(message.model_dump(mode="json", exclude_none=True))

            for tool_call in tool_calls:
                tool = registry.get(tool_call.function.name)
                if tool is None:
                    result = {
                        "ok": False,
                        "error": f"Unknown tool: {tool_call.function.name}",
                    }
                else:
                    try:
                        output = tool.execute(tool_call.function.arguments)
                        result = {"ok": True, "result": output}
                    except Exception as error:
                        # Tool failures are returned to the model but never retried here:
                        # a handler may have already produced side effects.
                        result = {
                            "ok": False,
                            "error": f"{type(error).__name__}: {error}",
                        }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    ),
                })

    def stream_text(self, inputs) -> Iterator[str]:
        """Génère du texte et produit chaque fragment dès sa réception."""
        for attempt in range(self.max_retries + 1):
            stream = None
            emitted_text = False
            finish_reason = None
            try:
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=inputs,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_output_tokens,
                    stream=True,
                    extra_body=self._extra_body(),
                )
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    choice = chunk.choices[0]
                    finish_reason = choice.finish_reason or finish_reason
                    content = getattr(choice.delta, "content", None)
                    if isinstance(content, str) and content:
                        emitted_text = True
                        yield content

                if not emitted_text:
                    raise RuntimeError(
                        "The model returned no streamed text "
                        f"(finish_reason={finish_reason!r})"
                    )
                return
            except Exception as e:
                if emitted_text or attempt == self.max_retries:
                    raise
                print(
                    f"🔥 Text streaming error "
                    f"(retry {attempt + 1}/{self.max_retries}): {e}"
                )
            finally:
                close = getattr(stream, "close", None)
                if callable(close):
                    try:
                        close()
                    except Exception:
                        pass

    def generate_json(self, inputs):
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=inputs,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_output_tokens,
                    response_format={"type": "json_object"},
                    extra_body=self._extra_body(),
                )
                if not resp.choices:
                    raise RuntimeError("The model returned no choices")

                text = resp.choices[0].message.content
                if not isinstance(text, str) or not text.strip():
                    finish_reason = resp.choices[0].finish_reason
                    raise RuntimeError(
                        "The model returned no JSON "
                        f"(finish_reason={finish_reason!r})"
                    )

                return json.loads(text)
            except JSONDecodeError as e:
                if attempt == self.max_retries:
                    raise
                print(
                    f"❌ Malformed JSON "
                    f"(retry {attempt + 1}/{self.max_retries}): {e}"
                )
            except Exception as e:
                if attempt == self.max_retries:
                    raise
                print(
                    f"🔥 JSON generation error "
                    f"(retry {attempt + 1}/{self.max_retries}): {e}"
                )

    def generate_object_from_prompt(self, prompt: str,text_format = None):
        inputs = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        return self.generate_object(inputs, text_format=text_format) 

    def generate_json_from_prompt(self, prompt: str):
        inputs = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        return self.generate_json(inputs)

    def generate_text_from_prompt(self, prompt: str, **options):
        inputs = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        return self.generate_text(inputs, **options) 

class ModelMessage:
    def __init__(self):
        self.inputs = []
    def add_message(self, role: str, content: str):
        self.inputs.append({
                "role": role,
                "content": content
            })
    def add_system_message(self, content: str):
        self.add_message("system", content)
    def add_user_message(self, content: str):
        self.add_message("user", content)
    def add_assistant_message(self, content: str):
        self.add_message("assistant", content)
    def pop(self):
        if self.inputs:
            return self.inputs.pop()
        else:
            return None
    def get_inputs(self):
        return self.inputs

    

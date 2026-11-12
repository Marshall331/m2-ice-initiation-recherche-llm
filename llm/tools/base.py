import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Union

from openai import pydantic_function_tool
from pydantic import BaseModel


ToolDescription = Union[str, os.PathLike[str]]


@dataclass
class Tool:
    """A callable function exposed to a language model.

    ``description`` accepts either inline text or a ``Path`` to a Markdown file.
    A string is always treated as inline text so that file loading is explicit.
    """

    name: str
    description: ToolDescription
    arguments: type[BaseModel]
    handler: Callable[..., Any]
    verbose: bool = False

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Tool name must be a non-empty string")
        if not isinstance(self.arguments, type) or not issubclass(self.arguments, BaseModel):
            raise TypeError("Tool arguments must be a Pydantic BaseModel subclass")
        if not callable(self.handler):
            raise TypeError("Tool handler must be callable")
        if not isinstance(self.verbose, bool):
            raise TypeError("Tool verbose must be a boolean")

        self.name = self.name.strip()
        self.description = self._resolve_description(self.description)

    @staticmethod
    def _resolve_description(description: ToolDescription) -> str:
        if isinstance(description, os.PathLike):
            path = Path(description)
            if path.suffix.lower() not in {".md", ".markdown"}:
                raise ValueError("Tool description files must be Markdown files")
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as error:
                raise ValueError(
                    f"Unable to read tool description file: {path}"
                ) from error
        elif isinstance(description, str):
            text = description
        else:
            raise TypeError("Tool description must be text or a Markdown Path")

        text = text.strip()
        if not text:
            raise ValueError("Tool description must not be empty")
        return text

    def definition(self) -> dict[str, Any]:
        """Return the strict function schema expected by Chat Completions."""
        return pydantic_function_tool(
            self.arguments,
            name=self.name,
            description=self.description,
        )

    def execute(self, raw_arguments: str) -> Any:
        """Validate JSON arguments, then invoke the Python handler."""
        # Some providers send an empty string for tools without parameters.
        if not raw_arguments or not raw_arguments.strip():
            raw_arguments = "{}"
        arguments = self.arguments.model_validate_json(raw_arguments)
        parameters = arguments.model_dump()
        if self.verbose:
            print(f"🔧 Tool call: {self.name} | parameters={parameters!r}")
        return self.handler(**parameters)

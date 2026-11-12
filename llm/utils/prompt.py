"""Prompt template utilities."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping


_WILDCARD_RE = re.compile(r"{{\s*([^{}\s]+)\s*}}")


class Prompt:
    """Prompt template with ``{{wildcard}}`` placeholders."""

    def __init__(
        self,
        md_file: str | Path | None = None,
        text: str | None = None,
        separator: str = "\n",
    ) -> None:
        self.md_file: Path | None = None
        parts: list[str] = []

        if md_file is not None:
            md_path = Path(md_file)
            try:
                is_file = md_path.is_file()
            except (OSError, ValueError):
                # A long inline prompt is not a valid file name
                # (e.g. "File name too long"): treat it as text.
                is_file = False
            if is_file:
                self.md_file = md_path
                parts.append(md_path.read_text(encoding="utf-8"))
            elif text is None and isinstance(md_file, str):
                looks_like_md_path = (
                    "\n" not in md_file
                    and md_file.strip().lower().endswith((".md", ".markdown"))
                )
                if looks_like_md_path:
                    # A mistyped file name must not be silently sent as the prompt.
                    raise FileNotFoundError(f"Markdown file not found: {md_file}")
                parts.append(md_file)
            else:
                raise FileNotFoundError(f"Markdown file not found: {md_file}")

        if text is not None:
            parts.append(text)

        if not parts:
            raise ValueError("Prompt requires a markdown file or a text string")

        self._text = separator.join(parts)
        self._wildcards: dict[str, str] = {}
        self._sync_wildcards()

    def _sync_wildcards(self) -> None:
        """Register wildcard names found in the current prompt text."""
        for name in _WILDCARD_RE.findall(self._text):
            self._wildcards.setdefault(name, "")

    def get_wildcards(self) -> dict[str, str]:
        """Return a copy of the wildcard dictionary."""
        return dict(self._wildcards)

    def set_wildcard(self, name: str, value: str) -> None:
        """Set the value associated with one wildcard."""
        if name not in self._wildcards:
            raise KeyError(f"Unknown wildcard: {name}")
        self._wildcards[name] = value

    def assign_wildcards(self, values: Mapping[str, str]) -> None:
        """Set several wildcard values from a dictionary-like object."""
        for name, value in values.items():
            self.set_wildcard(name, value)

    def get_text(self) -> str:
        """Return the original prompt text, with wildcard markers unchanged."""
        return self._text

    def render(self) -> str:
        """Return the prompt with every wildcard replaced by its value."""

        def replace(match: re.Match[str]) -> str:
            name = match.group(1)
            return self._wildcards.get(name, "")

        return _WILDCARD_RE.sub(replace, self._text)

    def merge(self, other: "Prompt", separator: str = "\n") -> "Prompt":
        """Extend this prompt with another prompt and merge wildcard values.

        Existing wildcard values on this prompt are preserved. New wildcard
        values are copied from the other prompt.
        """
        if not isinstance(other, Prompt):
            raise TypeError("other must be a Prompt")

        self._text = separator.join((self._text, other.get_text()))
        for name, value in other.get_wildcards().items():
            self._wildcards.setdefault(name, value)
        self._sync_wildcards()
        return self

    def merge_string(self, text: str, separator: str = "\n") -> "Prompt":
        """Extend this prompt with a raw string and register its wildcards."""
        self._text = separator.join((self._text, text))
        self._sync_wildcards()
        return self

    # Small aliases for the vocabulary used in notebooks and exploratory code.
    get_wildcard_dictionary = get_wildcards
    set = set_wildcard
    assign = assign_wildcards
    get_prompt = render
    merge_text = merge_string


Promp = Prompt

"""Petite bibliothèque pour interroger un LLM (via OpenRouter) et lui donner des outils."""

from .open_model import ModelMessage, OpenModel
from .tools import RandomChoicesTool, Tool
from .utils import Prompt

__all__ = [
    "ModelMessage",
    "OpenModel",
    "Prompt",
    "RandomChoicesTool",
    "Tool",
]

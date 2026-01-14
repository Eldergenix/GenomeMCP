"""
LLM integration module for GenomeMCP.

Provides unified interface for local LLM backends (Ollama, llama-cpp-python).
"""

from .client import LLMClient, get_client
from .tools import GENOMICS_TOOLS, get_tool_definitions

__all__ = [
    "LLMClient",
    "get_client",
    "GENOMICS_TOOLS",
    "get_tool_definitions",
]

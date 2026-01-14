"""
Unified LLM client interface for GenomeMCP.

Supports multiple backends: Ollama (primary) and llama-cpp-python (fallback).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """Response from LLM completion."""
    content: str
    tool_calls: list[ToolCall] | None = None
    finish_reason: str = "stop"
    
    @property
    def has_tool_calls(self) -> bool:
        return bool(self.tool_calls)


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Send chat completion request with optional tool calling.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions for function calling.
            temperature: Sampling temperature (0.0 - 1.0).
            
        Returns:
            LLMResponse with content and/or tool calls.
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the LLM backend is available."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name."""
        pass


def get_client(
    backend: str = "ollama",
    model: str = "qwen2.5:7b",
    base_url: Optional[str] = None,
) -> LLMClient:
    """
    Get an LLM client for the specified backend.
    
    Args:
        backend: Backend type ('ollama' or 'llamacpp').
        model: Model name/path.
        base_url: Optional API base URL.
        
    Returns:
        LLMClient instance.
        
    Raises:
        ValueError: If backend is not supported.
        ImportError: If required dependencies are not installed.
    """
    if backend == "ollama":
        from .ollama import OllamaClient
        return OllamaClient(model=model, base_url=base_url)
    elif backend == "llamacpp":
        from .llamacpp import LlamaCppClient
        return LlamaCppClient(model_path=model)
    else:
        raise ValueError(f"Unsupported backend: {backend}. Use 'ollama' or 'llamacpp'.")


async def check_available_backends() -> dict[str, bool]:
    """Check which LLM backends are available."""
    results = {}
    
    try:
        from .ollama import OllamaClient
        client = OllamaClient()
        results["ollama"] = await client.is_available()
    except ImportError:
        results["ollama"] = False
    
    try:
        from .llamacpp import LlamaCppClient
        results["llamacpp"] = True  # Always available if installed
    except ImportError:
        results["llamacpp"] = False
    
    return results

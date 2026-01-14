"""
llama-cpp-python LLM client for GenomeMCP.

Provides embedded LLM inference without external dependencies.
"""

import json
from typing import Optional

from .client import LLMClient, LLMResponse, ToolCall


class LlamaCppClient(LLMClient):
    """
    llama-cpp-python client for embedded LLM inference.
    
    Requires: pip install llama-cpp-python
    Models must be in GGUF format.
    """
    
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 8192,
        n_gpu_layers: int = -1,  # -1 = all layers on GPU
        temperature: float = 0.7,
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self._default_temp = temperature
        self._llm = None
    
    @property
    def name(self) -> str:
        return f"llamacpp/{self.model_path.split('/')[-1]}"
    
    def _load_model(self):
        """Lazy load the model."""
        if self._llm is None:
            try:
                from llama_cpp import Llama
            except ImportError:
                raise ImportError(
                    "llama-cpp-python not installed. "
                    "Install with: pip install llama-cpp-python"
                )
            
            self._llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )
        return self._llm
    
    async def is_available(self) -> bool:
        """Check if the model file exists."""
        import os
        return os.path.exists(self.model_path)
    
    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Chat completion using llama-cpp-python.
        
        Note: Tool calling requires a model with chat template support.
        """
        llm = self._load_model()
        
        # Format messages for chat completion
        response = llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None,
        )
        
        # Parse response
        choice = response["choices"][0]
        message = choice["message"]
        content = message.get("content", "") or ""
        
        # Parse tool calls
        tool_calls = None
        if "tool_calls" in message and message["tool_calls"]:
            tool_calls = []
            for i, tc in enumerate(message["tool_calls"]):
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    args = json.loads(args)
                tool_calls.append(ToolCall(
                    id=tc.get("id", f"call_{i}"),
                    name=func.get("name", ""),
                    arguments=args,
                ))
        
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", "stop"),
        )
    
    def unload(self):
        """Unload the model to free memory."""
        self._llm = None

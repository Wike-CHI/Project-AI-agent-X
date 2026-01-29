"""
LLM Service - Multi-Provider Support via AI Gateway (LiteLLM)

Supports:
- MiniMax (M2.1)
- Kimi (K2.5)

Uses LiteLLM for unified API abstraction.
"""
from typing import Optional, Dict, Any, AsyncGenerator
from enum import Enum

from app.core.config import settings
from app.services.gateway_service import (
    get_gateway_service,
    AIGatewayService,
    GatewayResponse,
)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    MINIMAX = "minimax"
    KIMI = "kimi"


class LLMService:
    """
    LLM Service with multi-provider support via AI Gateway.

    Uses LiteLLM for:
    - Unified API abstraction
    - Provider routing
    - Cost tracking
    """

    # Model aliases
    PROVIDER_MODEL_MAP = {
        LLMProvider.MINIMAX.value: "minimax-m2.1",
        LLMProvider.KIMI.value: "kimi-k2.5",
    }

    def __init__(self, provider: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self._gateway: Optional[AIGatewayService] = None

    @property
    def gateway(self) -> AIGatewayService:
        """Lazy load gateway service."""
        if self._gateway is None:
            self._gateway = get_gateway_service()
        return self._gateway

    def get_model_for_provider(self, provider: str) -> str:
        """Get the default model for a provider."""
        return self.PROVIDER_MODEL_MAP.get(provider, "minimax-m2.1")

    async def complete(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Generate completion for a prompt.

        Args:
            prompt: The prompt to complete
            provider: LLM provider to use (defaults to configured provider)
            model: Model to use (overrides provider default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments for the LLM

        Returns:
            Generated text response
        """
        provider = provider or self.provider
        model = model or self.get_model_for_provider(provider)

        messages = [{"role": "user", "content": prompt}]

        response: GatewayResponse = await self.gateway.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.content

    async def chat_complete(
        self,
        messages: list,
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> str:
        """
        Generate chat completion for messages.

        Args:
            messages: List of chat messages [{role, content}]
            provider: LLM provider to use
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Generated text response
        """
        provider = provider or self.provider
        model = model or self.get_model_for_provider(provider)

        response: GatewayResponse = await self.gateway.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return response.content

    async def stream_complete(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion for a prompt.

        Args:
            prompt: The prompt to complete
            provider: LLM provider to use
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text
        """
        provider = provider or self.provider
        model = model or self.get_model_for_provider(provider)

        messages = [{"role": "user", "content": prompt}]

        async for chunk in self.gateway.stream_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk

    async def stream_chat_complete(
        self,
        messages: list,
        provider: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion for messages.

        Args:
            messages: List of chat messages
            provider: LLM provider to use
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Yields:
            Chunks of generated text
        """
        provider = provider or self.provider
        model = model or self.get_model_for_provider(provider)

        async for chunk in self.gateway.stream_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk

    def get_available_models(self) -> list:
        """Get list of available models."""
        return self.gateway.get_available_models()

    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """Calculate cost for token usage."""
        usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
        return self.gateway.calculate_cost(model, usage)


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

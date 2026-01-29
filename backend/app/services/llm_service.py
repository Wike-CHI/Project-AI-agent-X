"""
LLM Service - Multi-Provider Support (MiniMax + Kimi)
"""
from typing import Optional, Dict, Any
from enum import Enum

from app.core.config import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    MINIMAX = "minimax"
    KIMI = "kimi"


class LLMService:
    """
    LLM Service with multi-provider support.

    Supports:
    - MiniMax (M2.1)
    - Kimi (K2.5)
    """

    def __init__(self, provider: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self._clients: Dict[str, Any] = {}

    def _get_minimax_client(self):
        """Get or create MiniMax client."""
        if "minimax" not in self._clients:
            try:
                from openai import AsyncOpenAI
                self._clients["minimax"] = AsyncOpenAI(
                    api_key=settings.MINIMAX_API_KEY,
                    base_url=settings.MINIMAX_BASE_URL
                )
            except ImportError:
                pass
        return self._clients.get("minimax")

    def _get_kimi_client(self):
        """Get or create Kimi client."""
        if "kimi" not in self._clients:
            try:
                from openai import AsyncOpenAI
                self._clients["kimi"] = AsyncOpenAI(
                    api_key=settings.KIMI_API_KEY,
                    base_url=settings.KIMI_BASE_URL
                )
            except ImportError:
                pass
        return self._clients.get("kimi")

    async def complete(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        **kwargs
    ) -> str:
        """
        Generate completion for a prompt.

        Args:
            prompt: The prompt to complete
            provider: LLM provider to use (defaults to configured provider)
            model: Model to use (provider-specific)
            **kwargs: Additional arguments for the LLM

        Returns:
            Generated text response
        """
        provider = provider or self.provider

        if provider == LLMProvider.MINIMAX.value:
            client = self._get_minimax_client()
            if client:
                response = await client.chat.completions.create(
                    model=model or settings.MINIMAX_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return response.choices[0].message.content

        elif provider == LLMProvider.KIMI.value:
            client = self._get_kimi_client()
            if client:
                response = await client.chat.completions.create(
                    model=model or settings.KIMI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return response.choices[0].message.content

        raise ValueError(f"Unsupported provider: {provider}")

    async def stream_complete(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        **kwargs
    ):
        """
        Stream completion for a prompt.

        Yields:
            Chunks of generated text
        """
        provider = provider or self.provider

        if provider == LLMProvider.MINIMAX.value:
            client = self._get_minimax_client()
            if client:
                stream = await client.chat.completions.create(
                    model=model or settings.MINIMAX_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    **kwargs
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        elif provider == LLMProvider.KIMI.value:
            client = self._get_kimi_client()
            if client:
                stream = await client.chat.completions.create(
                    model=model or settings.KIMI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    **kwargs
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

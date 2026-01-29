"""
LLM Service - Multi-Provider Support
"""
from typing import Optional, Dict, Any
from enum import Enum

from app.core.config import settings


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"


class LLMService:
    """
    LLM Service with multi-provider support.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Alibaba Qwen (通义千问)
    """

    def __init__(self, provider: str = None):
        self.provider = provider or settings.DEFAULT_LLM_PROVIDER
        self._clients: Dict[str, Any] = {}

    def _get_openai_client(self):
        """Get or create OpenAI client."""
        if "openai" not in self._clients:
            try:
                from openai import AsyncOpenAI
                self._clients["openai"] = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL
                )
            except ImportError:
                pass
        return self._clients.get("openai")

    def _get_anthropic_client(self):
        """Get or create Anthropic client."""
        if "anthropic" not in self._clients:
            try:
                from anthropic import AsyncAnthropic
                self._clients["anthropic"] = AsyncAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY
                )
            except ImportError:
                pass
        return self._clients.get("anthropic")

    def _get_qwen_client(self):
        """Get or create Qwen client."""
        if "qwen" not in self._clients:
            try:
                from openai import AsyncOpenAI
                # Qwen compatible with OpenAI API
                self._clients["qwen"] = AsyncOpenAI(
                    api_key=settings.DASHSCOPE_API_KEY,
                    base_url=settings.DASHSCOPE_BASE_URL
                )
            except ImportError:
                pass
        return self._clients.get("qwen")

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

        if provider == LLMProvider.OPENAI.value:
            client = self._get_openai_client()
            if client:
                response = await client.chat.completions.create(
                    model=model or settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    **kwargs
                )
                return response.choices[0].message.content

        elif provider == LLMProvider.ANTHROPIC.value:
            client = self._get_anthropic_client()
            if client:
                response = await client.messages.create(
                    model=model or settings.ANTHROPIC_MODEL,
                    max_tokens=kwargs.get("max_tokens", 4096),
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

        elif provider == LLMProvider.QWEN.value:
            client = self._get_qwen_client()
            if client:
                response = await client.chat.completions.create(
                    model=model or settings.DASHSCOPE_MODEL,
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

        if provider == LLMProvider.OPENAI.value:
            client = self._get_openai_client()
            if client:
                stream = await client.chat.completions.create(
                    model=model or settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    **kwargs
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

        elif provider == LLMProvider.QWEN.value:
            client = self._get_qwen_client()
            if client:
                stream = await client.chat.completions.create(
                    model=model or settings.DASHSCOPE_MODEL,
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

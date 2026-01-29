"""
AI Gateway Service - Unified LLM Interface via LiteLLM

Provides:
- Multi-provider routing (MiniMax, Kimi)
- Rate limiting support
- Cost tracking
- Unified API abstraction
"""
import os
import yaml
from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime

from app.core.config import settings


@dataclass
class GatewayResponse:
    """Standardized gateway response."""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    raw_response: Any


@dataclass
class ModelInfo:
    """Model information."""
    name: str
    provider: str
    context_length: int = 128000


class AIGatewayService:
    """
    AI Gateway Service - Unified LLM Gateway via LiteLLM

    Features:
    - Multi-provider routing (MiniMax, Kimi)
    - Unified completion interface
    - Model listing
    """

    # Available models mapping
    AVAILABLE_MODELS = {
        "minimax-m2.1": ModelInfo(
            name="minimax-m2.1",
            provider="minimax",
            context_length=256000
        ),
        "kimi-k2.5": ModelInfo(
            name="kimi-k2.5",
            provider="kimi",
            context_length=200000
        ),
    }

    def __init__(self):
        self._config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "litellm.yaml"
        )
        self._verbose = False

    def _get_model_name(self, model: str) -> str:
        """Map model alias to LiteLLM model name."""
        model_mapping = {
            "minimax-m2.1": "minimax/m2.1",
            "kimi-k2.5": "moonshot/kimi-k2.5",
            "minimax": "minimax/m2.1",
            "kimi": "moonshot/kimi-k2.5",
        }
        return model_mapping.get(model, model)

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        return [
            {
                "id": info.name,
                "provider": info.provider,
                "context_length": info.context_length,
            }
            for info in self.AVAILABLE_MODELS.values()
        ]

    def get_model_info(self, model: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        return self.AVAILABLE_MODELS.get(model)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "minimax-m2.1",
        user_id: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> GatewayResponse:
        """
        Unified chat completion via LiteLLM.

        Args:
            messages: List of chat messages [{role, content}]
            model: Model to use (minimax-m2.1, kimi-k2.5)
            user_id: User identifier for tracking
            stream: Whether to stream response
            **kwargs: Additional arguments (temperature, max_tokens, etc.)

        Returns:
            GatewayResponse with content, usage, and metadata
        """
        try:
            from litellm import acompletion

            # Map model name to LiteLLM format
            litellm_model = self._get_model_name(model)

            # Get model info for provider detection
            model_info = self.get_model_info(model)
            provider = model_info.provider if model_info else "unknown"

            # Prepare kwargs
            completion_kwargs = {
                "model": litellm_model,
                "messages": messages,
                "user": user_id,
                **kwargs
            }

            if stream:
                # Return response directly for streaming
                response = await acompletion(**completion_kwargs)
            else:
                response = await acompletion(**completion_kwargs)

            # Extract usage information
            usage = {}
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            # Get content from response
            content = ""
            if hasattr(response, "choices") and response.choices:
                choice = response.choices[0]
                if hasattr(choice, "message"):
                    content = choice.message.content or ""
                elif hasattr(choice, "delta") and choice.delta.content:
                    content = choice.delta.content

            return GatewayResponse(
                content=content,
                model=model,
                provider=provider,
                usage=usage,
                raw_response=response,
            )

        except ImportError as e:
            raise ImportError(
                "LiteLLM is not installed. Run: pip install litellm"
            ) from e

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "minimax-m2.1",
        user_id: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Streaming chat completion via LiteLLM.

        Yields:
            Content chunks as they are generated
        """
        try:
            from litellm import acompletion

            litellm_model = self._get_model_name(model)

            response = await acompletion(
                model=litellm_model,
                messages=messages,
                user=user_id,
                stream=True,
                **kwargs
            )

            async for chunk in response:
                if hasattr(chunk, "choices") and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield delta.content

        except ImportError as e:
            raise ImportError(
                "LiteLLM is not installed. Run: pip install litellm"
            ) from e

    def calculate_cost(
        self,
        model: str,
        usage: Dict[str, int]
    ) -> float:
        """
        Calculate approximate cost for API usage.

        Args:
            model: Model name
            usage: Token usage dict with prompt_tokens, completion_tokens

        Returns:
            Estimated cost in USD
        """
        # Pricing per 1M tokens (approximate)
        pricing = {
            "minimax-m2.1": {
                "input": 0.1,   # $0.1 per 1M tokens
                "output": 0.3,  # $0.3 per 1M tokens
            },
            "kimi-k2.5": {
                "input": 0.12,
                "output": 0.6,
            },
        }

        model_pricing = pricing.get(model, pricing["minimax-m2.1"])
        prompt_cost = (usage.get("prompt_tokens", 0) / 1_000_000) * model_pricing["input"]
        output_cost = (usage.get("completion_tokens", 0) / 1_000_000) * model_pricing["output"]

        return round(prompt_cost + output_cost, 6)


# Singleton instance
_gateway_service: Optional[AIGatewayService] = None


def get_gateway_service() -> AIGatewayService:
    """Get the gateway service singleton."""
    global _gateway_service
    if _gateway_service is None:
        _gateway_service = AIGatewayService()
    return _gateway_service

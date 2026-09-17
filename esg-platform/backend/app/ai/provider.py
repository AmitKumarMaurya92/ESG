"""
AI Provider abstraction layer.

All LLM calls go through this interface.
The rest of the application never imports from openai/google/anthropic directly.

Providers:
  - GeminiProvider (uses google-generativeai)
  - OpenAIProvider (uses openai)
  - MockProvider   (for testing / when no key is configured)
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base interface for all AI providers."""

    @abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2048) -> str:
        """Generate a text response."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector."""
        ...


class MockProvider(AIProvider):
    """Returns canned responses. Used when no API key is configured."""

    async def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2048) -> str:
        logger.warning("MockProvider: No LLM API key configured. Returning mock response.")
        return (
            "I am the ESG AI assistant. No LLM API key is currently configured. "
            "Please add LLM_API_KEY to your .env file to enable AI responses."
        )

    async def embed(self, text: str) -> list[float]:
        # Return a small zero vector for testing
        return [0.0] * 384


class GeminiProvider(AIProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self._api_key = api_key
        self._model_name = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self._api_key)
                self._client = genai.GenerativeModel(self._model_name)
            except ImportError:
                raise RuntimeError(
                    "google-generativeai is not installed. "
                    "Run: pip install google-generativeai"
                )
        return self._client

    async def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2048) -> str:
        import asyncio
        client = self._get_client()
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.generate_content(full_prompt)
        )
        return response.text

    async def embed(self, text: str) -> list[float]:
        try:
            import asyncio
            import google.generativeai as genai
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                )
            )
            return result["embedding"]
        except Exception as e:
            logger.error("Gemini embed failed: %s", e)
            return [0.0] * 768


class OpenAIProvider(AIProvider):
    """OpenAI provider."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self._api_key = api_key
        self._model = model

    async def generate(self, prompt: str, system: Optional[str] = None, max_tokens: int = 2048) -> str:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise RuntimeError("openai is not installed. Run: pip install openai")

        client = AsyncOpenAI(api_key=self._api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise RuntimeError("openai is not installed.")

        client = AsyncOpenAI(api_key=self._api_key)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding


def get_ai_provider() -> AIProvider:
    """
    Factory function that returns the configured AI provider.
    Falls back to MockProvider if no API key is set.
    """
    provider = settings.LLM_PROVIDER.lower()
    api_key = settings.LLM_API_KEY
    model = settings.LLM_MODEL

    if not api_key:
        logger.info("No LLM_API_KEY configured — using MockProvider.")
        return MockProvider()

    if provider == "gemini":
        logger.info("Using Gemini AI provider with model %s", model)
        return GeminiProvider(api_key=api_key, model=model or "gemini-1.5-flash")

    if provider == "openai":
        logger.info("Using OpenAI provider with model %s", model)
        return OpenAIProvider(api_key=api_key, model=model or "gpt-4o-mini")

    logger.warning("Unknown LLM_PROVIDER='%s' — falling back to MockProvider.", provider)
    return MockProvider()

import logging
import asyncio
from .base import AbstractLLMProvider, AbstractEmbedProvider
import threading

logger = logging.getLogger(__name__)

class RoundRobinLLMProvider(AbstractLLMProvider):
    def __init__(self, primaries: list[AbstractLLMProvider], fallback: AbstractLLMProvider = None):
        self.primaries = primaries
        self.fallback = fallback
        self._index = 0
        self._lock = threading.Lock()

    def _is_rate_limit(self, e: Exception) -> bool:
        error_str = str(e).lower()
        return "429" in error_str or "quota" in error_str or "rate limit" in error_str or "resource exhausted" in error_str or "invalid" in error_str or "api key not valid" in error_str or "403" in error_str or "blocked" in error_str

    def _get_next_primary(self) -> AbstractLLMProvider:
        with self._lock:
            idx = self._index
            self._index = (self._index + 1) % len(self.primaries)
            return self.primaries[idx]

    async def complete(self, prompt: str, system: str = "") -> str:
        max_attempts = len(self.primaries) * 5
        last_error = None
        for attempt in range(max_attempts):
            provider = self._get_next_primary()
            try:
                return await provider.complete(prompt, system)
            except Exception as e:
                last_error = e
                if self._is_rate_limit(e):
                    if (attempt + 1) % len(self.primaries) == 0 and attempt < max_attempts - 1:
                        logger.warning(f"All LLM keys rate limited. Sleeping 33s before retry pool...")
                        await asyncio.sleep(33)
                    else:
                        logger.warning(f"LLM exhausted. Trying next key...")
                    continue
                raise e
        if self.fallback:
            return await self.fallback.complete(prompt, system)
        raise last_error

    async def complete_with_image(self, prompt: str, image_bytes: bytes, mime_type: str, system: str = "") -> str:
        max_attempts = len(self.primaries) * 5
        last_error = None
        for attempt in range(max_attempts):
            provider = self._get_next_primary()
            try:
                return await provider.complete_with_image(prompt, image_bytes, mime_type, system)
            except Exception as e:
                last_error = e
                if self._is_rate_limit(e):
                    if (attempt + 1) % len(self.primaries) == 0 and attempt < max_attempts - 1:
                        logger.warning(f"All Vision keys rate limited. Sleeping 33s before retry pool...")
                        await asyncio.sleep(33)
                    else:
                        logger.warning(f"Vision node exhausted. Trying next key...")
                    continue
                raise e
        if self.fallback:
            return await self.fallback.complete_with_image(prompt, image_bytes, mime_type, system)
        raise last_error

class RoundRobinEmbedProvider(AbstractEmbedProvider):
    def __init__(self, primaries: list[AbstractEmbedProvider], fallback: AbstractEmbedProvider = None):
        self.primaries = primaries
        self.fallback = fallback
        self._index = 0
        self._lock = threading.Lock()

    def _is_rate_limit(self, e: Exception) -> bool:
        error_str = str(e).lower()
        return "429" in error_str or "quota" in error_str or "rate limit" in error_str or "resource exhausted" in error_str or "invalid" in error_str or "api key not valid" in error_str or "403" in error_str or "blocked" in error_str
        
    def _get_next_primary(self) -> AbstractEmbedProvider:
        with self._lock:
            idx = self._index
            self._index = (self._index + 1) % len(self.primaries)
            return self.primaries[idx]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        max_attempts = len(self.primaries) * 5
        last_error = None
        for attempt in range(max_attempts):
            provider = self._get_next_primary()
            try:
                return await provider.embed_texts(texts)
            except Exception as e:
                last_error = e
                if self._is_rate_limit(e):
                    if (attempt + 1) % len(self.primaries) == 0 and attempt < max_attempts - 1:
                        logger.warning(f"All Embed keys rate limited. Sleeping 33s before retry pool...")
                        await asyncio.sleep(33)
                    else:
                        logger.warning(f"Embed node exhausted. Trying next key...")
                    continue
                raise e
        if self.fallback:
            return await self.fallback.embed_texts(texts)
        raise last_error

    async def embed_image(self, image_bytes: bytes, mime_type: str = "") -> list[float]:
        max_attempts = len(self.primaries) * 5
        last_error = None
        for attempt in range(max_attempts):
            provider = self._get_next_primary()
            try:
                return await provider.embed_image(image_bytes, mime_type)
            except Exception as e:
                last_error = e
                if self._is_rate_limit(e):
                    if (attempt + 1) % len(self.primaries) == 0 and attempt < max_attempts - 1:
                        logger.warning(f"All Image Embed keys rate limited. Sleeping 33s before retry pool...")
                        await asyncio.sleep(33)
                    else:
                        logger.warning(f"Image Embed node exhausted. Trying next key...")
                    continue
                raise e
        if self.fallback:
            return await self.fallback.embed_image(image_bytes, mime_type)
        raise last_error

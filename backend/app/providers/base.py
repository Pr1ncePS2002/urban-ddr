from abc import ABC, abstractmethod

class AbstractLLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, system: str = "") -> str:
        """Send a text prompt, return string response."""
        pass

    @abstractmethod
    async def complete_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str, system: str = ""
    ) -> str:
        """Send prompt + image bytes, return string response."""
        pass

class AbstractEmbedProvider(ABC):
    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of text strings, return list of float vectors."""
        pass

    @abstractmethod
    async def embed_image(self, image_bytes: bytes, mime_type: str = "") -> list[float]:
        """Embed image bytes, return float vector. 
        If provider does not support image embedding, 
        first describe the image via LLM then embed the description."""
        pass

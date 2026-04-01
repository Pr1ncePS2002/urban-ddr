import base64
import anthropic
from .base import AbstractLLMProvider, AbstractEmbedProvider
from ..config import settings


class AnthropicLLMProvider(AbstractLLMProvider):
    def __init__(self, api_key: str):
        # api_key is never stored to disk or logged; held in-memory for this request only.
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = settings.anthropic_llm_model

    async def complete(self, prompt: str, system: str = "") -> str:
        kwargs = {"model": self.model, "max_tokens": 2048, "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        response = await self.client.messages.create(**kwargs)
        return response.content[0].text

    async def complete_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str, system: str = ""
    ) -> str:
        base64_image = base64.standard_b64encode(image_bytes).decode("utf-8")
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type or "image/jpeg",
                    "data": base64_image,
                },
            },
            {"type": "text", "text": prompt},
        ]
        kwargs = {
            "model": self.model,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": content}],
        }
        if system:
            kwargs["system"] = system
        response = await self.client.messages.create(**kwargs)
        return response.content[0].text


class AnthropicEmbedProvider(AbstractEmbedProvider):
    """
    Anthropic has no native embedding API. This provider uses the LLM to describe
    content and then delegates embedding to a separate embed provider passed at
    construction time. If no embed_delegate is given it raises clearly.
    """

    def __init__(self, api_key: str, embed_delegate: AbstractEmbedProvider = None):
        self.llm = AnthropicLLMProvider(api_key=api_key)
        self._delegate = embed_delegate

    def _require_delegate(self):
        if self._delegate is None:
            raise ValueError(
                "Anthropic does not support native embeddings. "
                "Please also provide a Gemini or OpenAI key for the embed provider."
            )

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self._require_delegate()
        return await self._delegate.embed_texts(texts)

    async def embed_image(self, image_bytes: bytes, mime_type: str = "") -> list[float]:
        description = await self.llm.complete_with_image(
            prompt="Describe this image in detail for a building inspection report.",
            image_bytes=image_bytes,
            mime_type=mime_type or "image/jpeg",
        )
        self._require_delegate()
        return (await self._delegate.embed_texts([description]))[0]

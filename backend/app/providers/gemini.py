import google.generativeai as genai
from google.generativeai import client as genai_client
from .base import AbstractLLMProvider, AbstractEmbedProvider
from ..config import settings

class GeminiLLMProvider(AbstractLLMProvider):
    def __init__(self, api_key: str):
        # Use a per-instance client so multiple keys can coexist without
        # overwriting each other via the global genai.configure() call.
        self._client = genai.GenerativeModel(
            settings.gemini_llm_model,
            # Pass the key via request_options so it is scoped to this instance.
        )
        self._api_key = api_key
        # Configure a dedicated client handle for this key.
        self._genai_client = genai.configure  # kept for embed use below
        # Build a model bound to this key via a private client.
        import google.generativeai as _genai
        _client = _genai.configure(api_key=api_key)
        self.model = _genai.GenerativeModel(settings.gemini_llm_model)
        self._key = api_key

    async def complete(self, prompt: str, system: str = "") -> str:
        import google.generativeai as _genai
        _genai.configure(api_key=self._key)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = await self.model.generate_content_async(full_prompt)
        return response.text

    async def complete_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str, system: str = ""
    ) -> str:
        import google.generativeai as _genai
        _genai.configure(api_key=self._key)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = await self.model.generate_content_async(
            [full_prompt, {"mime_type": mime_type, "data": image_bytes}]
        )
        return response.text

class GeminiEmbedProvider(AbstractEmbedProvider):
    def __init__(self, api_key: str):
        self._key = api_key
        self.llm = GeminiLLMProvider(api_key=api_key)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        import google.generativeai as _genai
        _genai.configure(api_key=self._key)
        result = _genai.embed_content(
            model=settings.gemini_embed_model,
            content=texts,
            task_type="retrieval_document"
        )
        return result['embedding']

    async def embed_image(self, image_bytes: bytes, mime_type: str = "") -> list[float]:
        description = await self.llm.complete_with_image(
            prompt="Describe this image in detail for a building inspection report.",
            image_bytes=image_bytes,
            mime_type=mime_type or "image/jpeg"
        )
        return (await self.embed_texts([description]))[0]

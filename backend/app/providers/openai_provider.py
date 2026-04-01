from openai import AsyncOpenAI
import base64
from .base import AbstractLLMProvider, AbstractEmbedProvider
from ..config import settings

class OpenAILLMProvider(AbstractLLMProvider):
    def __init__(self, api_key: str):
        # The api_key is NEVER stored to disk or logged. Passed in-memory and discarded.
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = settings.openai_llm_model

    async def complete(self, prompt: str, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2048
        )
        return response.choices[0].message.content

    async def complete_with_image(
        self, prompt: str, image_bytes: bytes, mime_type: str, system: str = ""
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        })

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=2048
        )
        return response.choices[0].message.content

class OpenAIEmbedProvider(AbstractEmbedProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.llm = OpenAILLMProvider(api_key=api_key)
        self.model = settings.openai_embed_model

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in response.data]

    async def embed_image(self, image_bytes: bytes, mime_type: str = "") -> list[float]:
        # Describe then embed
        description = await self.llm.complete_with_image(
            prompt="Describe this image in detail for a building inspection report.",
            image_bytes=image_bytes,
            mime_type=mime_type or "image/jpeg"
        )
        return (await self.embed_texts([description]))[0]

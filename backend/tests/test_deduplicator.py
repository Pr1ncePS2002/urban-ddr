import pytest
from app.pipeline.deduplicator import deduplicate_observations
from app.providers.base import AbstractEmbedProvider

class MockEmbedProvider(AbstractEmbedProvider):
    async def embed_text(self, text: str) -> list[float]:
        # Simple mock: if texts are exactly same, same vector
        # Otherwise orthogonal vectors for testing
        if text == "Identical text":
            return [1.0, 0.0]
        elif "Different" in text:
            return [0.0, 1.0]
        return [0.5, 0.5]

    async def embed_image(self, image_bytes, mime_type=""):
        return [0.0, 0.0]

@pytest.mark.asyncio
async def test_deduplicator():
    provider = MockEmbedProvider()
    obs = ["Identical text", "Identical text", "Different text"]
    
    # Needs async event loop provided by pytest-asyncio
    deduped = await deduplicate_observations(obs, provider, "test_job_123")
    
    # Should reduce identical texts
    assert len(deduped) == 2
    assert "Identical text" in deduped
    assert "Different text" in deduped

from app.providers.registry import get_llm_provider, get_embed_provider
from app.providers.gemini import GeminiLLMProvider
from app.providers.openai_provider import OpenAILLMProvider

def test_provider_registry():
    gemini_llm = get_llm_provider("gemini", "AIzaTestKey")
    assert isinstance(gemini_llm, GeminiLLMProvider)
    
    openai_llm = get_llm_provider("openai", "sk-proj-test")
    assert isinstance(openai_llm, OpenAILLMProvider)

def test_invalid_provider():
    try:
        get_llm_provider("invalid", "key")
        assert False
    except ValueError:
        assert True

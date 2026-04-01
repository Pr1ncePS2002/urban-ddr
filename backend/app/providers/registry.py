from .gemini import GeminiLLMProvider, GeminiEmbedProvider
from .openai_provider import OpenAILLMProvider, OpenAIEmbedProvider
from .base import AbstractLLMProvider, AbstractEmbedProvider
from .fallback import RoundRobinLLMProvider, RoundRobinEmbedProvider
from ..config import settings

def get_llm_provider(name: str, api_key: str = None) -> AbstractLLMProvider:
    openai_key = settings.openai_api_key
    openai_prov = OpenAILLMProvider(api_key=openai_key) if openai_key else None
    
    gemini_providers = []
    if api_key:
        keys = [k.strip() for k in api_key.split(",") if k.strip()]
        for key in keys:
            gemini_providers.append(GeminiLLMProvider(api_key=key))
    if settings.google_api_keys:
        keys = [k.strip() for k in settings.google_api_keys.split(",") if k.strip()]
        for key in keys:
            gemini_providers.append(GeminiLLMProvider(api_key=key))

    if name == "gemini":
        if not gemini_providers:
            raise ValueError("No Google API keys configured.")
        return RoundRobinLLMProvider(gemini_providers, None)
    elif name == "openai":
        if not openai_prov:
            raise ValueError("No OpenAI API key configured.")
        return openai_prov
    else:
        raise ValueError(f"Unknown LLM provider: {name}.")


def get_embed_provider(name: str, api_key: str = None) -> AbstractEmbedProvider:
    openai_key = settings.openai_api_key
    openai_prov = OpenAIEmbedProvider(api_key=openai_key) if openai_key else None
    
    gemini_providers = []
    if api_key:
        keys = [k.strip() for k in api_key.split(",") if k.strip()]
        for key in keys:
            gemini_providers.append(GeminiEmbedProvider(api_key=key))
    if settings.google_api_keys:
        keys = [k.strip() for k in settings.google_api_keys.split(",") if k.strip()]
        for key in keys:
            gemini_providers.append(GeminiEmbedProvider(api_key=key))

    if name == "gemini":
        if not gemini_providers:
            raise ValueError("No Google API keys configured.")
        return RoundRobinEmbedProvider(gemini_providers, None)
    elif name == "openai":
        if not openai_prov:
            raise ValueError("No OpenAI API key configured.")
        return openai_prov
    else:
        raise ValueError(f"Unknown embed provider: {name}.")

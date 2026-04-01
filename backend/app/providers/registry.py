from .gemini import GeminiLLMProvider, GeminiEmbedProvider
from .openai_provider import OpenAILLMProvider, OpenAIEmbedProvider
from .anthropic_provider import AnthropicLLMProvider, AnthropicEmbedProvider
from .base import AbstractLLMProvider, AbstractEmbedProvider
from .fallback import RoundRobinLLMProvider, RoundRobinEmbedProvider
from ..config import settings


def _resolve_key(user_key: str | None, server_key: str | None) -> str | None:
    """User-supplied key always takes priority over the server-side .env key."""
    return user_key or server_key


def get_llm_provider(name: str, api_key: str = None) -> AbstractLLMProvider:
    if name == "gemini":
        gemini_providers = []
        if api_key:
            for k in (k.strip() for k in api_key.split(",") if k.strip()):
                gemini_providers.append(GeminiLLMProvider(api_key=k))
        if settings.google_api_keys:
            for k in (k.strip() for k in settings.google_api_keys.split(",") if k.strip()):
                gemini_providers.append(GeminiLLMProvider(api_key=k))
        if not gemini_providers:
            raise ValueError("No Google API key provided. Please enter your Gemini API key.")
        return RoundRobinLLMProvider(gemini_providers, None)

    elif name == "openai":
        key = _resolve_key(api_key, settings.openai_api_key)
        if not key:
            raise ValueError("No OpenAI API key provided. Please enter your OpenAI API key.")
        return OpenAILLMProvider(api_key=key)

    elif name == "anthropic":
        key = _resolve_key(api_key, settings.anthropic_api_key)
        if not key:
            raise ValueError("No Anthropic API key provided. Please enter your Anthropic API key.")
        return AnthropicLLMProvider(api_key=key)

    else:
        raise ValueError(f"Unknown LLM provider: {name!r}. Choose from: gemini, openai, anthropic.")


def get_embed_provider(name: str, api_key: str = None) -> AbstractEmbedProvider:
    if name == "gemini":
        gemini_providers = []
        if api_key:
            for k in (k.strip() for k in api_key.split(",") if k.strip()):
                gemini_providers.append(GeminiEmbedProvider(api_key=k))
        if settings.google_api_keys:
            for k in (k.strip() for k in settings.google_api_keys.split(",") if k.strip()):
                gemini_providers.append(GeminiEmbedProvider(api_key=k))
        if not gemini_providers:
            raise ValueError("No Google API key provided. Please enter your Gemini API key.")
        return RoundRobinEmbedProvider(gemini_providers, None)

    elif name == "openai":
        key = _resolve_key(api_key, settings.openai_api_key)
        if not key:
            raise ValueError("No OpenAI API key provided. Please enter your OpenAI API key.")
        return OpenAIEmbedProvider(api_key=key)

    elif name == "anthropic":
        # Anthropic has no native embedding API; wrap with a delegate if a
        # server-side Gemini or OpenAI key is available, otherwise surface a
        # clear error asking the user to also supply a Gemini/OpenAI key.
        anthro_key = _resolve_key(api_key, settings.anthropic_api_key)
        if not anthro_key:
            raise ValueError("No Anthropic API key provided. Please enter your Anthropic API key.")

        delegate = None
        if settings.google_api_keys:
            keys = [k.strip() for k in settings.google_api_keys.split(",") if k.strip()]
            delegate = RoundRobinEmbedProvider([GeminiEmbedProvider(api_key=k) for k in keys], None)
        elif settings.openai_api_key:
            delegate = OpenAIEmbedProvider(api_key=settings.openai_api_key)

        return AnthropicEmbedProvider(api_key=anthro_key, embed_delegate=delegate)

    else:
        raise ValueError(f"Unknown embed provider: {name!r}. Choose from: gemini, openai, anthropic.")

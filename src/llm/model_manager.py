"""
model_manager.py
Central model selector. Loads providers from config and runs
single or multi-provider comparisons.
"""
import os
from typing import Dict, List, Optional
from src.llm.base_llm import BaseLLM, LLMResponse

try:
    from dotenv import load_dotenv
    import pathlib
    load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parents[2] / ".env", override=True)
except Exception:
    pass


def get_provider(provider: str, model: str = None, api_key: str = None) -> BaseLLM:
    """Instantiate a provider by name."""
    if provider == "groq":
        from src.llm.groq_provider import GroqProvider
        return GroqProvider(api_key=api_key, model=model)
    elif provider == "ollama":
        from src.llm.ollama_provider import OllamaProvider
        return OllamaProvider(model=model)
    elif provider == "openai":
        from src.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(api_key=api_key, model=model)
    elif provider == "gemini":
        from src.llm.gemini_provider import GeminiProvider
        return GeminiProvider(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}. Choose from: groq, ollama, openai, gemini")


class ModelManager:
    """
    Central model manager. Supports single provider mode and
    multi-provider comparison mode.
    """

    # Default provider configs — override via env vars or constructor
    PROVIDER_CONFIGS = {
        "groq":   {"api_key_env": "GROQ_API_KEY",   "default_model": "llama-3.3-70b-versatile"},
        "ollama": {"api_key_env": None,              "default_model": "llama3.2"},
        "openai": {"api_key_env": "OPENAI_API_KEY",  "default_model": "gpt-4o-mini"},
        "gemini": {"api_key_env": "GEMINI_API_KEY",  "default_model": "gemini-2.0-flash"},
    }

    def __init__(self, default_provider: str = "groq", default_model: str = None):
        self.default_provider = default_provider
        self.default_model    = default_model
        self._providers: Dict[str, BaseLLM] = {}

    def _get_or_create(self, provider: str, model: str = None) -> BaseLLM:
        cfg     = self.PROVIDER_CONFIGS.get(provider, {})
        api_key = os.getenv(cfg.get("api_key_env", "")) if cfg.get("api_key_env") else None
        m       = model or cfg.get("default_model")
        key     = f"{provider}:{m}"
        if key not in self._providers:
            self._providers[key] = get_provider(provider, model=m, api_key=api_key)
        return self._providers[key]

    def generate(self, prompt: str, system: str = None,
                 provider: str = None, model: str = None,
                 temperature: float = 0.1) -> LLMResponse:
        """Generate with a single provider."""
        p = self._get_or_create(provider or self.default_provider, model)
        return p.generate(prompt, system=system, temperature=temperature)

    def compare(
        self,
        prompt: str,
        system: str = None,
        providers: List[Dict] = None,
        temperature: float = 0.1,
    ) -> List[LLMResponse]:
        """
        Run the same prompt across multiple providers in parallel.

        providers format:
        [
            {"provider": "groq",   "model": "llama-3.3-70b-versatile"},
            {"provider": "ollama", "model": "llama3.2"},
            {"provider": "openai", "model": "gpt-4o-mini"},
        ]
        """
        import concurrent.futures

        if not providers:
            providers = [{"provider": p} for p in ["groq", "ollama"]]

        def run_one(cfg):
            provider_name = cfg.get("provider", "groq")
            model_name    = cfg.get("model")
            try:
                llm = self._get_or_create(provider_name, model_name)
                return llm.generate(prompt, system=system, temperature=temperature)
            except Exception as e:
                from src.llm.base_llm import LLMResponse
                return LLMResponse(
                    content="", provider=provider_name,
                    model=model_name or "unknown", latency_ms=0, error=str(e)
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(run_one, providers))

        return results

    def available_providers(self) -> List[str]:
        """Return list of providers with API keys configured."""
        available = ["groq"]  # groq is always default
        if os.getenv("OPENAI_API_KEY"):
            available.append("openai")
        if os.getenv("GEMINI_API_KEY"):
            available.append("gemini")
        # Check Ollama
        try:
            import requests
            requests.get("http://localhost:11434/api/tags", timeout=2)
            available.append("ollama")
        except Exception:
            pass
        return available
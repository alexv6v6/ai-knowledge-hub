"""
ollama_provider.py
Ollama provider — runs models locally (llama3, mistral, gemma, phi3, etc.)
Requires Ollama installed: https://ollama.com
"""
import time
from src.llm.base_llm import BaseLLM, LLMResponse


class OllamaProvider(BaseLLM):
    provider_name = "ollama"
    default_model = "llama3.2"

    MODELS = ["llama3.2", "mistral", "gemma2", "phi3", "qwen2.5"]

    def __init__(self, model: str = None, base_url: str = "http://localhost:11434"):
        self.model    = model or self.default_model
        self.base_url = base_url

    def generate(self, prompt: str, system: str = None, temperature: float = 0.1) -> LLMResponse:
        try:
            import requests
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            t0 = time.time()
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False,
                      "options": {"temperature": temperature}},
                timeout=120,
            )
            response.raise_for_status()
            latency = (time.time() - t0) * 1000
            content = response.json()["message"]["content"]
            return LLMResponse(content=content, provider=self.provider_name, model=self.model, latency_ms=round(latency, 1))
        except Exception as e:
            return LLMResponse(content="", provider=self.provider_name, model=self.model, latency_ms=0,
                               error=f"Ollama not available: {e}. Install from https://ollama.com")

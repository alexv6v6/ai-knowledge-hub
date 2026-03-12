"""
groq_provider.py
Groq API provider — LLaMA 3.3, Mixtral, Gemma via Groq cloud.
"""
import os, time
from src.llm.base_llm import BaseLLM, LLMResponse

# Load .env from project root (works regardless of working directory)
try:
    from dotenv import load_dotenv
    import pathlib
    _root = pathlib.Path(__file__).resolve().parents[2]
    load_dotenv(dotenv_path=_root / ".env", override=True)
except Exception:
    pass


class GroqProvider(BaseLLM):
    provider_name = "groq"
    default_model = "llama-3.3-70b-versatile"

    MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ]

    def __init__(self, api_key: str = None, model: str = None):
        from groq import Groq
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model  = model or self.default_model

    def generate(self, prompt: str, system: str = None, temperature: float = 0.1) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            t0 = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            latency = (time.time() - t0) * 1000
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name,
                model=self.model,
                latency_ms=round(latency, 1),
            )
        except Exception as e:
            return LLMResponse(content="", provider=self.provider_name, model=self.model, latency_ms=0, error=str(e))
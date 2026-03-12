"""
gemini_provider.py
Google Gemini API provider — gemini-2.0-flash, gemini-1.5-pro
"""
import os, time
from src.llm.base_llm import BaseLLM, LLMResponse


class GeminiProvider(BaseLLM):
    provider_name = "gemini"
    default_model = "gemini-2.0-flash"

    MODELS = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model   = model or self.default_model

    def generate(self, prompt: str, system: str = None, temperature: float = 0.1) -> LLMResponse:
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            t0     = time.time()
            model  = genai.GenerativeModel(self.model)
            result = model.generate_content(
                full_prompt,
                generation_config={"temperature": temperature},
            )
            latency = (time.time() - t0) * 1000
            return LLMResponse(
                content=result.text,
                provider=self.provider_name, model=self.model, latency_ms=round(latency, 1)
            )
        except Exception as e:
            return LLMResponse(content="", provider=self.provider_name, model=self.model, latency_ms=0, error=str(e))

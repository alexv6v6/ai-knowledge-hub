"""
openai_provider.py
OpenAI API provider — GPT-4o, GPT-4o-mini, GPT-3.5-turbo
"""
import os, time
from src.llm.base_llm import BaseLLM, LLMResponse


class OpenAIProvider(BaseLLM):
    provider_name = "openai"
    default_model = "gpt-4o-mini"

    MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model   = model or self.default_model

    def generate(self, prompt: str, system: str = None, temperature: float = 0.1) -> LLMResponse:
        try:
            from openai import OpenAI
            client   = OpenAI(api_key=self.api_key)
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})

            t0 = time.time()
            response = client.chat.completions.create(
                model=self.model, messages=messages, temperature=temperature
            )
            latency = (time.time() - t0) * 1000
            return LLMResponse(
                content=response.choices[0].message.content,
                provider=self.provider_name, model=self.model, latency_ms=round(latency, 1)
            )
        except Exception as e:
            return LLMResponse(content="", provider=self.provider_name, model=self.model, latency_ms=0, error=str(e))

"""
base_llm.py
Abstract base class for all LLM providers.
All providers must implement the generate() method.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    latency_ms: float
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


class BaseLLM(ABC):
    provider_name: str = "base"
    default_model: str = ""

    @abstractmethod
    def generate(self, prompt: str, system: str = None, temperature: float = 0.1) -> LLMResponse:
        """Generate a response from the LLM."""
        pass

    def is_available(self) -> bool:
        """Check if this provider is configured and reachable."""
        try:
            self.generate("ping", temperature=0)
            return True
        except Exception:
            return False

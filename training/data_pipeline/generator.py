from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class LLMProvider(Protocol):
    provider_name: str

    def generate_text(self, prompt: str) -> str:
        ...


@dataclass
class RuleBasedProvider:
    provider_name: str = "rule-based/demo"

    def generate_text(self, prompt: str) -> str:
        return prompt


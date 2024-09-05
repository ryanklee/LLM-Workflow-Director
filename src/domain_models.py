from dataclasses import dataclass
from typing import Dict

@dataclass
class RateLimit:
    requests_per_minute: int
    requests_per_hour: int

@dataclass
class TokenUsage:
    total_tokens: int
    tokens_per_task: Dict[str, int]

class RateLimitPolicy:
    def is_allowed(self) -> bool:
        pass

    def wait_for_next_slot(self) -> None:
        pass

class TokenUsagePolicy:
    def count_tokens(self, text: str) -> int:
        pass

    def add_tokens(self, task_id: str, input_text: str, output_text: str) -> None:
        pass

    def get_total_tokens(self) -> int:
        pass

    def get_tokens_for_task(self, task_id: str) -> int:
        pass

class TokenOptimizationPolicy:
    def optimize_prompt(self, prompt: str) -> str:
        pass

    def truncate_response(self, response: str, max_tokens: int) -> str:
        pass

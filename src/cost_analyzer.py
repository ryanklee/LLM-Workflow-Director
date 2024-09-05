from typing import Dict

class CostAnalyzer:
    def __init__(self):
        self.model_costs: Dict[str, float] = {
            "claude-3-opus-20240229": 0.015,  # Cost per 1K tokens
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.0015
        }

    def calculate_cost(self, model: str, tokens: int) -> float:
        if model not in self.model_costs:
            raise ValueError(f"Unknown model: {model}")
        return (tokens / 1000) * self.model_costs[model]

    def compare_models(self, tokens: int) -> Dict[str, float]:
        return {model: self.calculate_cost(model, tokens) for model in self.model_costs}

    def analyze_cost_effectiveness(self, model: str, tokens: int, performance_score: float) -> float:
        cost = self.calculate_cost(model, tokens)
        return performance_score / cost if cost > 0 else float('inf')

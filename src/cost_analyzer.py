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
import logging
from typing import Dict, Any

class CostAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_costs: Dict[str, float] = {
            "claude-3-opus-20240229": 0.015,  # Cost per 1K tokens
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.0015
        }
        self.model_usage: Dict[str, Dict[str, Any]] = {
            model: {"tokens": 0, "cost": 0.0} for model in self.model_costs
        }

    def calculate_cost(self, model: str, tokens: int) -> float:
        if model not in self.model_costs:
            self.logger.warning(f"Unknown model: {model}. Using default cost.")
            cost_per_1k = 0.01  # Default cost
        else:
            cost_per_1k = self.model_costs[model]
        
        cost = (tokens / 1000) * cost_per_1k
        self.model_usage[model]["tokens"] += tokens
        self.model_usage[model]["cost"] += cost
        return cost

    def get_total_cost(self) -> float:
        return sum(usage["cost"] for usage in self.model_usage.values())

    def get_model_usage(self, model: str) -> Dict[str, Any]:
        return self.model_usage.get(model, {"tokens": 0, "cost": 0.0})

    def generate_cost_report(self) -> str:
        report = "Cost Analysis Report:\n"
        report += f"Total Cost: ${self.get_total_cost():.4f}\n\n"
        report += "Model Usage:\n"
        for model, usage in self.model_usage.items():
            report += f"- {model}:\n"
            report += f"  Tokens: {usage['tokens']}\n"
            report += f"  Cost: ${usage['cost']:.4f}\n"
        return report

    def suggest_cost_optimization(self) -> str:
        suggestion = "Cost Optimization Suggestions:\n"
        total_tokens = sum(usage["tokens"] for usage in self.model_usage.values())
        
        if total_tokens == 0:
            return "No usage data available for optimization suggestions."
        
        for model, usage in self.model_usage.items():
            percentage = (usage["tokens"] / total_tokens) * 100
            if percentage > 50 and model == "claude-3-opus-20240229":
                suggestion += f"- Consider using claude-3-sonnet-20240229 for some tasks to reduce costs. {model} usage: {percentage:.2f}%\n"
            elif percentage > 70 and model == "claude-3-sonnet-20240229":
                suggestion += f"- Consider using claude-3-haiku-20240307 for simpler tasks to optimize costs. {model} usage: {percentage:.2f}%\n"
        
        if not suggestion.strip():
            suggestion += "Current model usage distribution seems optimal."
        
        return suggestion

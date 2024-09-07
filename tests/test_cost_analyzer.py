import pytest
from src.cost_analyzer import CostAnalyzer

@pytest.fixture
def cost_analyzer():
    return CostAnalyzer()

def test_calculate_cost(cost_analyzer):
    cost = cost_analyzer.calculate_cost("claude-3-opus-20240229", 1000)
    assert cost == 0.015
    assert cost_analyzer.get_model_usage("claude-3-opus-20240229")["tokens"] == 1000
    assert cost_analyzer.get_model_usage("claude-3-opus-20240229")["cost"] == 0.015

def test_calculate_cost_unknown_model(cost_analyzer):
    cost = cost_analyzer.calculate_cost("unknown-model", 1000)
    assert cost == 0.01  # Default cost
    assert cost_analyzer.get_model_usage("unknown-model")["tokens"] == 1000
    assert cost_analyzer.get_model_usage("unknown-model")["cost"] == 0.01

def test_get_total_cost(cost_analyzer):
    cost_analyzer.calculate_cost("claude-3-opus-20240229", 1000)
    cost_analyzer.calculate_cost("claude-3-sonnet-20240229", 2000)
    assert cost_analyzer.get_total_cost() == 0.015 + 0.006

def test_generate_cost_report(cost_analyzer):
    cost_analyzer.calculate_cost("claude-3-opus-20240229", 1000)
    cost_analyzer.calculate_cost("claude-3-sonnet-20240229", 2000)
    report = cost_analyzer.generate_cost_report()
    assert "Total Cost: $0.0210" in report
    assert "claude-3-opus-20240229" in report
    assert "claude-3-sonnet-20240229" in report
    assert "Tokens: 1000" in report
    assert "Tokens: 2000" in report

def test_suggest_cost_optimization(cost_analyzer):
    cost_analyzer.calculate_cost("claude-3-opus-20240229", 10000)
    suggestion = cost_analyzer.suggest_cost_optimization()
    assert "Consider using claude-3-sonnet-20240229" in suggestion

    cost_analyzer = CostAnalyzer()  # Reset the analyzer
    cost_analyzer.calculate_cost("claude-3-sonnet-20240229", 10000)
    suggestion = cost_analyzer.suggest_cost_optimization()
    assert "Consider using claude-3-haiku-20240307" in suggestion

    cost_analyzer = CostAnalyzer()  # Reset the analyzer
    cost_analyzer.calculate_cost("claude-3-haiku-20240307", 10000)
    suggestion = cost_analyzer.suggest_cost_optimization()
    assert "Current model usage distribution seems optimal" in suggestion

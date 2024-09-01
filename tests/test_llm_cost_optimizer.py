import pytest
from src.llm_manager import LLMCostOptimizer

def test_llm_cost_optimizer_initialization():
    optimizer = LLMCostOptimizer()
    assert isinstance(optimizer, LLMCostOptimizer)
    assert len(optimizer.usage_stats) == 3
    assert all(tier in optimizer.usage_stats for tier in ['fast', 'balanced', 'powerful'])

def test_update_usage():
    optimizer = LLMCostOptimizer()
    optimizer.update_usage('fast', 100)
    assert optimizer.usage_stats['fast']['count'] == 1
    assert optimizer.usage_stats['fast']['total_tokens'] == 100

def test_get_usage_report():
    optimizer = LLMCostOptimizer()
    optimizer.update_usage('fast', 100)
    optimizer.update_usage('balanced', 200)
    optimizer.update_usage('powerful', 300)
    report = optimizer.get_usage_report()
    assert 'usage_stats' in report
    assert 'total_cost' in report
    assert report['usage_stats']['fast']['count'] == 1
    assert report['usage_stats']['balanced']['count'] == 1
    assert report['usage_stats']['powerful']['count'] == 1

def test_suggest_optimization():
    optimizer = LLMCostOptimizer()
    optimizer.update_usage('fast', 100)
    optimizer.update_usage('balanced', 200)
    optimizer.update_usage('powerful', 300)
    suggestion = optimizer.suggest_optimization()
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0

def test_suggest_optimization_no_data():
    optimizer = LLMCostOptimizer()
    suggestion = optimizer.suggest_optimization()
    assert suggestion == "Not enough data to suggest optimizations."

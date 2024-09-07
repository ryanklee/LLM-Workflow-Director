import pytest
from src.token_tracker import TokenTracker, TokenOptimizer

def test_token_tracker_initialization():
    tracker = TokenTracker()
    assert tracker.get_total_tokens() == 0

def test_token_counting():
    tracker = TokenTracker()
    assert tracker.count_tokens("This is a test") == 4

def test_add_tokens():
    tracker = TokenTracker()
    tracker.add_tokens("task1", "Input text", "Output text")
    assert tracker.get_total_tokens() == 4
    assert tracker.get_tokens_for_task("task1") == 4

def test_multiple_tasks():
    tracker = TokenTracker()
    tracker.add_tokens("task1", "Input 1", "Output 1")
    tracker.add_tokens("task2", "Input 2", "Output 2")
    assert tracker.get_total_tokens() == 8
    assert tracker.get_tokens_for_task("task1") == 4
    assert tracker.get_tokens_for_task("task2") == 4

def test_token_optimizer():
    optimizer = TokenOptimizer()
    assert optimizer.optimize_prompt("  Trim spaces  ") == "Trim spaces"
    assert optimizer.truncate_response("One two three four", 2) == "One two"
import pytest
from src.token_tracker import TokenTracker, TokenOptimizer

@pytest.fixture
def token_tracker():
    return TokenTracker()

@pytest.fixture
def token_optimizer(token_tracker):
    return TokenOptimizer(token_tracker)

def test_token_tracker_add_tokens(token_tracker):
    token_tracker.add_tokens("task1", 100, 50)
    assert token_tracker.get_token_usage("task1") == 150
    assert token_tracker.get_total_token_usage() == 150

def test_token_tracker_multiple_tasks(token_tracker):
    token_tracker.add_tokens("task1", 100, 50)
    token_tracker.add_tokens("task2", 200, 100)
    assert token_tracker.get_token_usage("task1") == 150
    assert token_tracker.get_token_usage("task2") == 300
    assert token_tracker.get_total_token_usage() == 450

def test_token_tracker_reset(token_tracker):
    token_tracker.add_tokens("task1", 100, 50)
    token_tracker.reset()
    assert token_tracker.get_token_usage("task1") == 0
    assert token_tracker.get_total_token_usage() == 0

def test_token_optimizer_suggest_optimization(token_optimizer):
    token_optimizer.token_tracker.add_tokens("task1", 1000, 500)
    token_optimizer.token_tracker.add_tokens("task2", 10, 5)
    token_optimizer.token_tracker.add_tokens("task3", 100, 50)

    assert "Consider optimizing task task1" in token_optimizer.suggest_optimization("task1")
    assert "very few tokens" in token_optimizer.suggest_optimization("task2")
    assert "seems reasonable" in token_optimizer.suggest_optimization("task3")

def test_token_optimizer_get_overall_efficiency(token_optimizer):
    token_optimizer.token_tracker.add_tokens("task1", 100, 50)
    token_optimizer.token_tracker.add_tokens("task2", 200, 100)
    assert token_optimizer.get_overall_efficiency() == 225.0

def test_token_optimizer_generate_report(token_optimizer):
    token_optimizer.token_tracker.add_tokens("task1", 100, 50)
    token_optimizer.token_tracker.add_tokens("task2", 200, 100)
    token_optimizer.token_tracker.add_tokens("task3", 300, 150)
    report = token_optimizer.generate_report()
    assert "Total Tokens Used: 900" in report
    assert "Number of Tasks: 3" in report
    assert "Overall Efficiency: 300.00 tokens per task" in report
    assert "Task task3: 450 tokens" in report
    assert "Task task2: 300 tokens" in report
    assert "Task task1: 150 tokens" in report

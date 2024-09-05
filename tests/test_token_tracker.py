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

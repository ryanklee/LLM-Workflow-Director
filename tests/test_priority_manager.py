import pytest
from src.priority_manager import PriorityManager

def test_priority_manager_initialization():
    manager = PriorityManager()
    assert isinstance(manager, PriorityManager)
    assert manager.priorities == {}

def test_set_and_get_priorities():
    manager = PriorityManager()
    stage = "Test Stage"
    priorities = ["Task 1", "Task 2", "Task 3"]
    
    manager.set_priorities(stage, priorities)
    assert manager.get_priorities(stage) == priorities

def test_get_nonexistent_priorities():
    manager = PriorityManager()
    assert manager.get_priorities("Nonexistent Stage") == []

def test_determine_priority():
    manager = PriorityManager()
    stage = "Test Stage"
    priorities = ["Task 1", "Task 2", "Task 3"]
    
    manager.set_priorities(stage, priorities)
    
    assert manager.determine_priority(stage, "Task 1") == 0
    assert manager.determine_priority(stage, "Task 2") == 1
    assert manager.determine_priority(stage, "Task 3") == 2
    assert manager.determine_priority(stage, "Nonexistent Task") == 3

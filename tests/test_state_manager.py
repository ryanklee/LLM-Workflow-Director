import pytest
from src.state_manager import StateManager

def test_state_manager_initialization():
    manager = StateManager()
    assert manager.state == {}

def test_state_manager_set_get():
    manager = StateManager()
    manager.set('test_key', 'test_value')
    assert manager.get('test_key') == 'test_value'

def test_state_manager_get_default():
    manager = StateManager()
    assert manager.get('non_existent_key', 'default') == 'default'

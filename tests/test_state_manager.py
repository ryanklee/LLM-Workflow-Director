from src.state_manager import StateManager
from src.vectorstore.vector_store import VectorStore


def test_state_manager_initialization():
    manager = StateManager()
    assert isinstance(manager.vector_store, VectorStore)


def test_state_manager_set_get():
    manager = StateManager()
    manager.set('test_key', [1.0, 2.0, 3.0])
    assert manager.get('test_key') == [1.0, 2.0, 3.0]


def test_state_manager_get_default():
    manager = StateManager()
    assert manager.get('non_existent_key', 'default') == 'default'


def test_state_manager_delete():
    manager = StateManager()
    manager.set('test_key', [1.0, 2.0, 3.0])
    manager.delete('test_key')
    assert manager.get('test_key') is None

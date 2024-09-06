from src.vectorstore.vector_store import VectorStore

class StateManager:
    def __init__(self):
        self.vector_store = VectorStore()

    def get(self, key, default=None):
        try:
            return self.vector_store.Retrieve(key)
        except KeyError:
            return default

    def set(self, key, value):
        self.vector_store.Store(key, value)

    def delete(self, key):
        self.vector_store.Delete(key)

    def get_all(self):
        return self.vector_store.GetAll()

    def get_state(self):
        return self.get_all()

    def update_state(self, key, value):
        self.set(key, value)

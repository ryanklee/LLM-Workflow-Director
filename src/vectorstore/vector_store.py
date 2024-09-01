from threading import Lock

class VectorStore:
    """Represents an in-memory vector database"""

    def __init__(self):
        self.vectors = {}
        self.lock = Lock()

    def Store(self, key: str, vector: list[float]):
        """Adds or updates a vector in the store"""
        with self.lock:
            self.vectors[key] = vector

    def Retrieve(self, key: str) -> list[float]:
        """Gets a vector from the store"""
        with self.lock:
            vector = self.vectors.get(key)
            if vector is None:
                raise KeyError("Vector not found")
            return vector

    def Delete(self, key: str):
        """Removes a vector from the store"""
        with self.lock:
            self.vectors.pop(key, None)

    def GetAll(self) -> dict:
        """Returns all vectors in the store"""
        with self.lock:
            return self.vectors.copy()

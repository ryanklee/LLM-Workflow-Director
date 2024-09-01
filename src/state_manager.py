class StateManager:
    def __init__(self):
        self.state = {}

    def get(self, key, default=None):
        return self.state.get(key, default)

    def set(self, key, value):
        self.state[key] = value

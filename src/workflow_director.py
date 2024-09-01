from .state_manager import StateManager
from .llm_manager import LLMManager

class WorkflowDirector:
    def __init__(self):
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()

    def run(self):
        print("Starting LLM Workflow Director")
        while True:
            user_input = input("Enter a command (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            response = self.llm_manager.query(user_input)
            print(f"LLM response: {response}")
        print("Exiting LLM Workflow Director")

from .state_manager import StateManager
from .llm_manager import LLMManager

class WorkflowDirector:
    def __init__(self, input_func=input):
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()
        self.input_func = input_func

    def run(self):
        print("Starting LLM Workflow Director")
        while True:
            user_input = self.input_func("Enter a command (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            response = self.llm_manager.query(user_input)
            print(f"LLM response: {response}")
        print("Exiting LLM Workflow Director")

from .state_manager import StateManager
from .llm_manager import LLMManager

class WorkflowDirector:
    def __init__(self, input_func=input, print_func=print):
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()
        self.input_func = input_func
        self.print_func = print_func

    def run(self):
        self.print_func("Starting LLM Workflow Director")
        while True:
            self.print_func("Enter a command (or 'exit' to quit): ", end='')
            user_input = self.input_func()
            if user_input.lower() == 'exit':
                break
            response = self.llm_manager.query(user_input)
            self.print_func(f"LLM response: {response}")
        self.print_func("Exiting LLM Workflow Director")

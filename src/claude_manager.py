from anthropic import Anthropic

class ClaudeManager:
    def __init__(self):
        self.client = Anthropic()

    def generate_response(self, prompt):
        # Use the messages API, which is the current recommended method
        response = self.client.completion(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
        )
        return response.completion

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "highly complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

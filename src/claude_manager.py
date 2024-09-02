from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

class ClaudeManager:
    def __init__(self):
        self.client = Anthropic()

    def generate_response(self, prompt):
        # Use the completion API, which is the current recommended method for older SDK versions
        response = self.client.completions.create(
            model="claude-3-opus-20240229",
            max_tokens_to_sample=1000,
            prompt=f"{HUMAN_PROMPT} {prompt}{AI_PROMPT}",
        )
        return response.completion

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "highly complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

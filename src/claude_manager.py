import re
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

class ClaudeManager:
    def __init__(self):
        self.client = Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt):
        if not prompt or len(prompt) > 100000:
            raise ValueError("Invalid prompt length")

        response = self.client.messages.create(
            model=self.select_model(prompt),
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return self.parse_response(response.content[0].text)

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "highly complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text):
        match = re.search(r'<response>(.*?)</response>', response_text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return response_text

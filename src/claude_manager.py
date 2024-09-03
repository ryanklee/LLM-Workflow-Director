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

        try:
            response = self.client.messages.create(
                model=self.select_model(prompt),
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return self.parse_response(response.content[0].text)
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error in generate_response: {str(e)}")
            raise  # Re-raise the exception to trigger the retry mechanism

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "highly complex" in task_description.lower():
            return "claude-3-opus-20240229"
        elif "balanced" in task_description.lower():
            return "claude-3-sonnet-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text):
        # The response is the message content, so we just need to wrap it
        return f"<response>{response_text.strip()}</response>"

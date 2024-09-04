import re
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import time

class ClaudeManager:
    def __init__(self, client=None):
        self.client = client or self.create_client()
        self.messages = self.client.messages

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt):
        if not prompt or len(prompt) > 100000:
            raise ValueError("Invalid prompt length")

        try:
            response = self.messages.create(
                model=self.select_model(prompt),
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return self.parse_response(response.content[0].text)
        except Exception as e:
            if "404" in str(e):
                print(f"Model not found: {self.select_model(prompt)}. Falling back to next tier.")
                return self.fallback_response(prompt)
            elif "rate_limit_error" in str(e):
                print(f"Rate limit error encountered: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying
            else:
                print(f"Error in generate_response: {str(e)}")
            raise  # Re-raise the exception to trigger the retry mechanism

    def fallback_response(self, prompt):
        # Implement a simple fallback response
        return f"<response>Fallback response for: {prompt}</response>"

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text):
        # The response is the message content, so we just need to wrap it
        return f"<response>{response_text.strip()}</response>"

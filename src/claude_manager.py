import re
import logging
from anthropic import Anthropic, NotFoundError
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import time

class ClaudeManager:
    def __init__(self, client=None):
        self.client = client or self.create_client()
        self.messages = self.client.messages
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt):
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Invalid prompt: must be a non-empty string")
        if len(prompt) > 100000:
            raise ValueError("Invalid prompt length: exceeds 100,000 characters")

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
            self.logger.error(f"Error in generate_response: {str(e)}")
            if isinstance(e, NotFoundError):
                return self.fallback_response(prompt)
            elif "rate_limit_error" in str(e):
                self.logger.warning(f"Rate limit error encountered: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying
            raise  # Re-raise the exception to trigger the retry mechanism

    def fallback_response(self, prompt):
        self.logger.warning(f"Fallback response triggered for prompt: {prompt[:50]}...")
        return "<response>Fallback response: Unable to process the request at this time. Please try again later.</response>"

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

    def _fallback_to_lower_tier(self, prompt, current_tier):
        tiers = ['powerful', 'balanced', 'fast']
        current_index = tiers.index(current_tier)
        if current_index < len(tiers) - 1:
            next_tier = tiers[current_index + 1]
            self.logger.info(f"Falling back to {next_tier} tier")
            return self.generate_response(prompt)
        else:
            return self.fallback_response(prompt)

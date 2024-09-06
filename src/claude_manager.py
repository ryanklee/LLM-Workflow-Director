import logging
import json
from anthropic import Anthropic, NotFoundError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time
from .rate_limiter import RateLimiter
from .token_tracker import TokenTracker, TokenOptimizer

class ClaudeManager:
    def __init__(self, client=None, requests_per_minute: int = 60, requests_per_hour: int = 3600):
        self.client = client or self.create_client()
        self.logger = logging.getLogger(__name__)
        self.max_test_tokens = 1000
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
        self.token_tracker = TokenTracker()
        self.token_optimizer = TokenOptimizer()

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), retry=retry_if_exception_type(Exception), reraise=True)
    def generate_response(self, prompt, model=None):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Invalid prompt: must be a non-empty string")
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Invalid prompt length: exceeds {self.max_test_tokens} tokens")
        if '<script>' in prompt.lower() or 'ssn:' in prompt.lower():
            raise ValueError("Invalid prompt: contains potentially sensitive information")

        try:
            self.rate_limiter.wait_for_next_slot()
            response = self.client.messages.create(
                model=self.select_model(prompt) if model is None else model,
                max_tokens=self.max_test_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = self._extract_response_text(response)
            self.token_tracker.add_tokens("generate_response", prompt, response_text)
            return self.parse_response(response_text)
        except Exception as e:
            return self._handle_error(e, prompt)

    def _handle_error(self, error, prompt):
        self.logger.error(f"Error in generate_response: {str(error)}")
        if isinstance(error, NotFoundError):
            return self.fallback_response(prompt, "Model not found")
        elif isinstance(error, APIError) and "rate_limit" in str(error).lower():
            self.logger.warning(f"Rate limit error encountered: {str(error)}")
            time.sleep(5)
            return self.fallback_response(prompt, "Rate limit exceeded")
        elif isinstance(error, ValueError):
            return self.fallback_response(prompt, str(error))
        else:
            return self.fallback_response(prompt, "Unknown error")

    def fallback_response(self, prompt, error_type):
        self.logger.warning(f"Fallback response triggered for prompt: {prompt[:50]}...")
        self.logger.error(f"Error type: {error_type}")
        return f"<response>Fallback response: Unable to process the request. Error: {error_type}</response>"

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text):
        truncated_text = response_text[:self.max_test_tokens] + "..." if len(response_text) > self.max_test_tokens else response_text
        return f"<response>{truncated_text.strip()}</response>"

    def _extract_response_text(self, response):
        if isinstance(response, dict):
            if 'content' in response and isinstance(response['content'], list):
                return response['content'][0]['text']
            elif 'choices' in response and isinstance(response['choices'], list):
                return response['choices'][0]['message']['content']
        elif hasattr(response, 'content') and isinstance(response.content, list):
            return response.content[0].text
        
        raise ValueError(f"Unexpected response structure: {response}")

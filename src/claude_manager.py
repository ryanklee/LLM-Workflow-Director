import re
import logging
from anthropic import Anthropic, NotFoundError
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import time
from src.llm_manager import LLMManager
from .rate_limiter import RateLimiter
from .token_tracker import TokenTracker, TokenOptimizer

class ClaudeManager:
    def __init__(self, client=None, requests_per_minute: int = 60, requests_per_hour: int = 3600):
        self.client = client or self.create_client()
        self.messages = self.client.messages
        self.logger = logging.getLogger(__name__)
        self.llm_manager = LLMManager()
        self.max_test_tokens = 1000  # Increased from 100 to 1000
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
        self.token_tracker = TokenTracker()
        self.token_optimizer = TokenOptimizer()

    def evaluate_sufficiency(self, project_state):
        # Implement the evaluation logic here
        return True  # Placeholder implementation

    def make_decision(self, project_state):
        # Implement the decision-making logic here
        return "Next step"  # Placeholder implementation

    def evaluate_with_context(self, context, project_state):
        # Implement the evaluation with context logic here
        return "Evaluation result"  # Placeholder implementation

    def evaluate_project_state(self, project_data):
        # Implement the project state evaluation logic here
        return "Project evaluation result"  # Placeholder implementation

    def render_prompt_template(self, template, context):
        # Implement the prompt template rendering logic here
        return template.format(**context)

    def get_completion(self, prompt, model, max_tokens):
        return self.generate_response(prompt)

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt, model=None):
        if not isinstance(prompt, str):
            raise ValueError("Invalid prompt: must be a string")
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Invalid prompt length: exceeds {self.max_test_tokens} tokens")
        if not prompt.strip():
            raise ValueError("Invalid prompt: cannot be empty or only whitespace")

        try:
            self.rate_limiter.wait_for_next_slot()
            response = self.messages.create(
                model=self.select_model(prompt) if model is None else model,
                max_tokens=self.max_test_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            response_text = self._extract_response_text(response)
            self.token_tracker.add_tokens("generate_response", prompt, response_text)
            return self.parse_response(response_text)
        except Exception as e:
            self.logger.error(f"Error in generate_response: {str(e)}")
            if isinstance(e, NotFoundError):
                return self.fallback_response(prompt, "Model not found")
            elif "rate_limit_error" in str(e).lower():
                self.logger.warning(f"Rate limit error encountered: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying
                return self.fallback_response(prompt, "Rate limit exceeded")
            elif isinstance(e, ValueError) and "Unexpected response structure" in str(e):
                return self.fallback_response(prompt, "Unexpected API response")
            else:
                return self.fallback_response(prompt, "Unknown error")

    def fallback_response(self, prompt, error_type):
        self.logger.warning(f"Fallback response triggered for prompt: {prompt[:50]}...")
        self.logger.error(f"Error type: {error_type}")
        return f"<response>Fallback response: Unable to process the request at this time. Please try again later. Error type: {error_type}</response>"

    def select_model(self, task_description):
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text):
        # Truncate the response if it exceeds the max_test_tokens
        if len(response_text) > self.max_test_tokens:
            response_text = response_text[:self.max_test_tokens] + "..."
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
    def _extract_response_text(self, response):
        if isinstance(response, dict):
            if 'content' in response and isinstance(response['content'], list):
                return response['content'][0]['text']
            elif 'choices' in response and isinstance(response['choices'], list):
                return response['choices'][0]['message']['content']
            elif 'completion' in response:
                return response['completion']
        elif hasattr(response, 'content') and isinstance(response.content, list):
            return response.content[0].text
        
        raise ValueError(f"Unexpected response structure: {response}")

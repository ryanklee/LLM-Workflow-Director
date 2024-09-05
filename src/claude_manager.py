import re
import logging
from anthropic import Anthropic, NotFoundError
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import time
from src.llm_manager import LLMManager

class ClaudeManager:
    def __init__(self, client=None):
        self.client = client or self.create_client()
        self.messages = self.client.messages
        self.logger = logging.getLogger(__name__)
        self.llm_manager = LLMManager()
        self.max_test_tokens = 100  # Add this line

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
        self.max_test_tokens = self.llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)

    def get_completion(self, prompt, model, max_tokens):
        return self.generate_response(prompt)

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate_response(self, prompt):
        if not isinstance(prompt, str):
            raise ValueError("Invalid prompt: must be a string")
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Invalid prompt length: exceeds {self.max_test_tokens} tokens")
        if not prompt.strip():
            raise ValueError("Invalid prompt: cannot be empty or only whitespace")
        if not isinstance(prompt, str):
            raise ValueError("Invalid prompt: must be a string")
        if len(prompt) > self.max_test_tokens:
            raise ValueError(f"Invalid prompt length: exceeds {self.max_test_tokens} tokens")

        try:
            response = self.messages.create(
                model=self.select_model(prompt),
                max_tokens=self.max_test_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return self.parse_response(response['content'][0]['text'])
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

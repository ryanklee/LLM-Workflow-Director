import logging
import json
import anthropic
from anthropic import Anthropic, NotFoundError, APIError, APIConnectionError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
import time
from .rate_limiter import RateLimiter, RateLimitError
from .token_tracker import TokenTracker, TokenOptimizer
from .exceptions import RateLimitError

class ClaudeManager:
    def __init__(self, client=None, requests_per_minute: int = 1000, requests_per_hour: int = 10000):
        self.client = client or self.create_client()
        self.logger = logging.getLogger(__name__)
        self.max_test_tokens = 1000
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
        self.token_tracker = TokenTracker()
        self.token_optimizer = TokenOptimizer()
        self.max_context_length = 100000
        self.messages = self.client.messages

    def evaluate_response_quality(self, prompt):
        # Implement the evaluation logic here
        # This is a placeholder implementation
        response = self.generate_response(prompt)
        # You might want to implement a more sophisticated evaluation method
        return len(response) / 100  # Simple quality metric based on response length

    def count_tokens(self, text):
        # This is a simple approximation. For more accurate results, use a proper tokenizer.
        return len(text)

    @staticmethod
    def create_client():
        return Anthropic()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError)),
        reraise=True
    )
    def generate_response(self, prompt, model=None):
        if not self.rate_limiter.is_allowed():
            self.logger.warning("Rate limit reached, waiting for next available slot")
            self.rate_limiter.wait_for_next_slot()
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Invalid prompt: must be a non-empty string")
        token_count = self.count_tokens(prompt)
        if token_count > self.max_context_length:
            raise ValueError(f"Prompt length exceeds maximum context length of {self.max_context_length} tokens")
        if token_count > self.max_test_tokens:
            prompt = self._truncate_prompt(prompt, self.max_test_tokens)
        if '<script>' in prompt.lower() or 'ssn:' in prompt.lower():
            raise ValueError("Invalid prompt: contains potentially sensitive information")
        if self.count_tokens(prompt) > self.max_context_length:
            raise ValueError(f"Context overflow: prompt length {self.count_tokens(prompt)} tokens exceeds maximum context length {self.max_context_length}")
        
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        self.logger.debug(f"Using model: {model if model else 'default'}")

        try:
            selected_model = self.select_model(prompt) if model is None else model
            response = self.client.messages.create(
                model=selected_model,
                max_tokens=self.max_test_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = self._extract_response_text(response)
            self.token_tracker.add_tokens("generate_response", prompt, response_text)
            return self.parse_response(response_text)
        except (NotFoundError, APIError, APIConnectionError) as e:
            return self._handle_error(e, prompt)
        except Exception as e:
            self.logger.error(f"Unexpected error in generate_response: {str(e)}")
            return self.fallback_response(prompt, "Unexpected error")

    def _truncate_prompt(self, prompt, max_tokens):
        words = prompt.split()
        truncated_prompt = ""
        current_tokens = 0
        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens > max_tokens:
                break
            truncated_prompt += word + " "
            current_tokens += word_tokens
        return truncated_prompt.strip()

    def _handle_error(self, error, prompt):
        self.logger.error(f"Error in generate_response: {str(error)}")
        if isinstance(error, NotFoundError):
            return self.fallback_response(prompt, "Model not found")
        elif isinstance(error, APIError):
            if "rate_limit" in str(error).lower():
                self.logger.warning(f"Rate limit error encountered: {str(error)}")
                time.sleep(5)
                return self.fallback_response(prompt, "Rate limit exceeded")
            else:
                self.logger.error(f"API error: {str(error)}")
                return self.fallback_response(prompt, "API error")
        elif isinstance(error, APIConnectionError):
            self.logger.warning(f"API Connection error encountered: {str(error)}")
            time.sleep(5)
            return self.fallback_response(prompt, "API Connection error")
        elif isinstance(error, ValueError):
            return self.fallback_response(prompt, str(error))
        elif isinstance(error, RetryError):
            return self.fallback_response(prompt, "Rate limit exceeded after multiple retries")
        elif isinstance(error, TypeError):
            if "missing 2 required keyword-only arguments: 'response' and 'body'" in str(error):
                return self.fallback_response(prompt, "API response format error")
            else:
                return self.fallback_response(prompt, f"TypeError: {str(error)}")
        else:
            return self.fallback_response(prompt, f"Unknown error: {str(error)}")

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

    def evaluate_sufficiency(self, project_state):
        # Implement the evaluation logic here
        return {"is_sufficient": True, "reasoning": "Evaluation complete"}

    def make_decision(self, project_state):
        prompt = f"Make decision based on: {project_state}"
        response = self.generate_response(prompt)
        return self.parse_decision(response)

    def parse_decision(self, response):
        # Extract the decision from the response
        # This is a simple implementation and might need to be adjusted based on the actual response format
        return response.strip()

    def evaluate_project_state(self, project_data):
        # Implement the project state evaluation logic here
        return "Project state evaluation complete"

    def evaluate_with_context(self, context, project_state):
        # Implement the evaluation with context logic here
        return "Evaluation with context complete"

    def render_prompt_template(self, template, context):
        # Implement the prompt template rendering logic here
        return template.format(**context)

    def get_completion(self, prompt, model, max_tokens):
        # Implement the completion logic here
        return self.generate_response(prompt, model)

    def _handle_error(self, error, prompt):
        self.logger.error(f"Error in generate_response: {str(error)}")
        if isinstance(error, anthropic.NotFoundError):
            return self.fallback_response(prompt, "Model not found")
        elif isinstance(error, anthropic.APIError):
            if "rate_limit" in str(error).lower():
                self.logger.warning(f"Rate limit error encountered: {str(error)}")
                time.sleep(5)
                return self.fallback_response(prompt, "Rate limit exceeded")
            else:
                self.logger.error(f"API error: {str(error)}")
                return self.fallback_response(prompt, "API error")
        elif isinstance(error, anthropic.APIConnectionError):
            self.logger.warning(f"API Connection error encountered: {str(error)}")
            time.sleep(5)
            return self.fallback_response(prompt, "API Connection error")
        elif isinstance(error, ValueError):
            return self.fallback_response(prompt, str(error))
        else:
            return self.fallback_response(prompt, "Unknown error")

    def parse_response(self, response_text):
        max_length = self.max_test_tokens - 21
        truncated_text = response_text[:max_length] + "..." if len(response_text) > max_length else response_text
        parsed_response = f"<response>{truncated_text.strip()}</response>"
        return parsed_response

    def _extract_response_text(self, response):
        if isinstance(response, dict):
            if 'content' in response and isinstance(response['content'], list):
                return response['content'][0]['text']
            elif 'choices' in response and isinstance(response['choices'], list):
                return response['choices'][0]['message']['content']
        elif hasattr(response, 'content') and isinstance(response.content, list):
            return response.content[0].text
        
        raise ValueError(f"Unexpected response structure: {response}")

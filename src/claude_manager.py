import logging
import json
import asyncio
import time
from typing import Dict, List, Any
from unittest.mock import MagicMock
from anthropic import AsyncAnthropic, NotFoundError, APIError, APIConnectionError, APIStatusError
from .exceptions import RateLimitError as CustomRateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from .rate_limiter import RateLimiter
from .token_tracker import TokenTracker
from .token_optimizer import TokenOptimizer

logging.getLogger(__name__).info(f"Imported modules in {__name__}")

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.setLevel(logging.DEBUG)

import logging
import json
import asyncio
import time
from typing import Dict, List, Any
from unittest.mock import MagicMock
from anthropic import AsyncAnthropic, NotFoundError, APIError, APIConnectionError, APIStatusError
from .exceptions import RateLimitError as CustomRateLimitError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, RetryError
from .rate_limiter import RateLimiter
from .token_tracker import TokenTracker
from .token_optimizer import TokenOptimizer

class ClaudeManager:
    def __init__(self, client=None, requests_per_minute: int = 1000, requests_per_hour: int = 10000):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing ClaudeManager")
        self.client = client or self.create_client()
        self.logger.debug(f"Client initialized: {self.client}")
        
        # Add a file handler for persistent logging
        file_handler = logging.FileHandler('claude_manager.log')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.debug("File handler added for persistent logging")
        
        self.max_test_tokens = 1000
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)
        self.logger.debug(f"RateLimiter initialized with {requests_per_minute} rpm and {requests_per_hour} rph")
        self.token_tracker = TokenTracker()
        self.token_optimizer = TokenOptimizer(self.token_tracker)
        self.max_context_length = 200000  # Updated to 200k tokens
        self.messages = self.client.messages
        self.logger.info("ClaudeManager initialization complete")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        return await self.client.generate_response(prompt, model)

    async def count_tokens(self, text: str) -> int:
        return await self.client.count_tokens(text)

    async def select_model(self, task: str) -> str:
        return await self.client.select_model(task)

    async def close(self):
        self.logger.info("Closing ClaudeManager")
        await self.client.reset()
        self.logger.debug("ClaudeManager closed")

    @staticmethod
    def create_client():
        return AsyncAnthropic()

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        return await self.client.generate_response(prompt, model)

    async def count_tokens(self, text: str) -> int:
        return await self.client.count_tokens(text)

    async def select_model(self, task: str) -> str:
        return await self.client.select_model(task)

    async def close(self):
        self.logger.info("Closing ClaudeManager")
        await self.client.reset()
        self.logger.debug("ClaudeManager closed")

    async def close(self):
        self.logger.info("Closing ClaudeManager")
        # Add any cleanup logic here
        await self.client.reset()  # Assuming the client has a reset method

    async def select_model(self, task: str) -> str:
        return await self.client.select_model(task)

    @staticmethod
    def create_client():
        return AsyncAnthropic()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, APIConnectionError, TimeoutError)),
        reraise=True
    )
    async def generate_response(self, prompt, model=None):
        self.logger.debug(f"Entering generate_response with prompt: {prompt[:50]}... and model: {model}")
        self.logger.debug(f"Prompt length: {len(prompt)}")
        start_time = time.time()
        try:
            if not await self.rate_limiter.is_allowed():
                self.logger.warning("Rate limit reached, waiting for next available slot")
                await self.rate_limiter.wait_for_next_slot()
            if not isinstance(prompt, str):
                raise ValueError(f"Invalid prompt type: {type(prompt)}. Must be a string.")
            if not prompt.strip():
                raise ValueError("Invalid prompt: must be a non-empty string")
            token_count = await self.count_tokens(prompt)
            self.logger.debug(f"Token count for prompt: {token_count}")
            if token_count > self.max_context_length:
                self.logger.error(f"Prompt length ({token_count} tokens) exceeds maximum context length of {self.max_context_length} tokens")
                raise ValueError(f"Prompt length ({token_count} tokens) exceeds maximum context length of {self.max_context_length} tokens")
            if '<script>' in prompt.lower() or 'ssn:' in prompt.lower():
                raise ValueError("Invalid prompt: contains potentially sensitive information")
            
            self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
            self.logger.debug(f"Using model: {model if model else 'default'}")

            selected_model = await self.select_model(prompt) if model is None else model
            response_text = await self.client.generate_response(prompt, selected_model)

            await self.token_tracker.add_tokens("generate_response", token_count, await self.count_tokens(response_text))
            parsed_response = self.parse_response(response_text)
            end_time = time.time()
            self.logger.info(f"Response generated in {end_time - start_time:.2f} seconds. Model: {selected_model}, Input tokens: {token_count}, Output tokens: {await self.count_tokens(response_text)}")
            return parsed_response
        except CustomRateLimitError as e:
            self.logger.error(f"Rate limit error in generate_response: {str(e)}", exc_info=True)
            raise
        except ValueError as e:
            self.logger.error(f"Value error in generate_response: {str(e)}", exc_info=True)
            raise
        except (NotFoundError, APIError, APIConnectionError, APIStatusError) as e:
            self.logger.error(f"API error in generate_response: {str(e)}", exc_info=True)
            return await self._handle_error(e, prompt)
        except Exception as e:
            self.logger.error(f"Unexpected error in generate_response: {str(e)}", exc_info=True)
            return await self.fallback_response(prompt, f"Unexpected error: {str(e)}")
        finally:
            end_time = time.time()
            self.logger.debug(f"Total time in generate_response: {end_time - start_time:.2f} seconds")

    async def count_tokens(self, text: str) -> int:
        return await self.client.count_tokens(text)

    async def select_model(self, task_description: str) -> str:
        if "simple" in task_description.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task_description.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    def parse_response(self, response_text: str) -> str:
        max_length = self.max_test_tokens - 21
        truncated_text = response_text[:max_length] + "..." if len(response_text) > max_length else response_text
        parsed_response = f"<response>{truncated_text.strip()}</response>"
        return parsed_response

    async def _handle_error(self, error: Exception, prompt: str) -> str:
        self.logger.error(f"Error in generate_response: {str(error)}", exc_info=True)
        if isinstance(error, NotFoundError):
            return await self.fallback_response(prompt, "Model not found")
        elif isinstance(error, CustomRateLimitError):
            self.logger.warning(f"Rate limit error encountered: {str(error)}")
            await asyncio.sleep(5)
            return await self.fallback_response(prompt, "Rate limit exceeded")
        elif isinstance(error, (APIError, APIStatusError)):
            self.logger.error(f"API error: {str(error)}")
            return await self.fallback_response(prompt, f"API error: {str(error)}")
        elif isinstance(error, APIConnectionError):
            self.logger.warning(f"API Connection error encountered: {str(error)}")
            await asyncio.sleep(5)
            return await self.fallback_response(prompt, "API Connection error")
        elif isinstance(error, ValueError):
            self.logger.warning(f"ValueError: {str(error)}")
            return await self.fallback_response(prompt, str(error))
        elif isinstance(error, RetryError):
            self.logger.warning("Rate limit exceeded after multiple retries")
            return await self.fallback_response(prompt, "Rate limit exceeded after multiple retries")
        elif isinstance(error, TypeError):
            self.logger.error(f"TypeError: {str(error)}", exc_info=True)
            return await self.fallback_response(prompt, f"TypeError: {str(error)}")
        else:
            self.logger.error(f"Unknown error: {str(error)}", exc_info=True)
            return await self.fallback_response(prompt, f"Unknown error: {str(error)}")

    async def fallback_response(self, prompt: str, error_type: str) -> str:
        self.logger.warning(f"Fallback response triggered for prompt: {prompt[:50]}...")
        self.logger.error(f"Error type: {error_type}")
        return f"<response>Fallback response: Unable to process the request. Error: {error_type}</response>"

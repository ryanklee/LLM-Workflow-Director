import pytest
import asyncio
import logging
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError, RateLimitError
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest_asyncio.fixture
async def mock_claude_client():
    client = MockClaudeClient()
    logger.debug(f"Created MockClaudeClient instance with rate_limit_threshold={client.rate_limit_threshold}, rate_limit_reset_time={client.rate_limit_reset_time}")
    yield client
    await client.reset()
    logger.debug(f"Reset MockClaudeClient instance. Final call_count: {client.call_count}, error_count: {client.error_count}")

@pytest.fixture
def mock_claude_client_with_responses(mock_claude_client):
    async def setup_responses(responses):
        for prompt, response in responses.items():
            await mock_claude_client.set_response(prompt, response)
    return setup_responses

@pytest.fixture
def mock_claude_client_with_error_mode(mock_claude_client):
    async def set_error_mode(mode: bool):
        await mock_claude_client.set_error_mode(mode)
    return set_error_mode

@pytest.fixture
def mock_claude_client_with_rate_limit(mock_claude_client):
    async def set_rate_limit(threshold: int):
        await mock_claude_client.set_rate_limit(threshold)
    return set_rate_limit

class MockClaudeClient:
    def __init__(self):
        self.rate_limit_threshold = 5
        self.rate_limit_reset_time = 60
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.max_context_length = 200000
        self.last_reset_time = time.time()
        self.error_count_history = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"Initialized MockClaudeClient with rate_limit_threshold={self.rate_limit_threshold}, "
                         f"rate_limit_reset_time={self.rate_limit_reset_time}, max_test_tokens={self.max_test_tokens}")
        self.logger.debug(f"Initialized MockClaudeClient with rate_limit_threshold={self.rate_limit_threshold}, "
                          f"rate_limit_reset_time={self.rate_limit_reset_time}, max_test_tokens={self.max_test_tokens}")
        
    def __str__(self):
        return f"MockClaudeClient(rate_limit_threshold={self.rate_limit_threshold}, " \
               f"call_count={self.call_count}, error_count={self.error_count}, " \
               f"error_mode={self.error_mode})"

    def __str__(self):
        return f"MockClaudeClient(rate_limit_threshold={self.rate_limit_threshold}, call_count={self.call_count}, error_count={self.error_count}, error_mode={self.error_mode})"

    def __str__(self):
        return f"MockClaudeClient(rate_limit_threshold={self.rate_limit_threshold}, " \
               f"call_count={self.call_count}, error_count={self.error_count}, " \
               f"error_mode={self.error_mode})"

    async def set_rate_limit_reset_time(self, reset_time: int):
        self.rate_limit_reset_time = reset_time
        self.logger.debug(f"Set rate limit reset time to: {reset_time} seconds")

    async def get_error_count(self):
        return self.error_count

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}... using model: {model}")
        await asyncio.sleep(self.latency)
        
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.call_count = 0
            self.last_reset_time = current_time
            self.logger.debug("Rate limit counter reset")
        
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        
        if self.call_count >= self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise CustomRateLimitError("Rate limit exceeded")
        
        if self.error_mode:
            self.error_count += 1
            self.error_count_history.append(self.error_count)
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(status_code=500), body={})
        
        response = self.responses.get(prompt, "Default mock response")
        truncated_response = response[:self.max_test_tokens]
        self.logger.debug(f"Returning response: {truncated_response[:50]}...")
        return truncated_response

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency: float):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold: int):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def reset(self):
        old_call_count = self.call_count
        old_error_count = self.error_count
        self.__init__()
        self.logger.debug(f"Reset MockClaudeClient. Old call_count: {old_call_count}, Old error_count: {old_error_count}")

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count

    def reset_error_count(self):
        self.error_count = 0
        self.logger.debug("Reset error count")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"MockClaudeClient generating response for prompt: {prompt[:50]}... using model: {model}")
        await asyncio.sleep(self.latency)
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(status_code=500), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"MockClaudeClient returning response: {response[:50]}...")
        return f"<response>{response}</response>"

    async def count_tokens(self, text: str) -> int:
        return len(text.split())

    async def reset(self):
        self.__init__()
        self.logger.debug("Reset MockClaudeClient")

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def simulate_concurrent_calls(self, num_calls):
        results = []
        tasks = [self.generate_response("Test prompt") for _ in range(num_calls)]
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except RateLimitError as e:
                results.append(e)
        return results

    def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency: float):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold: int):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        logger.debug("Generating response", prompt=prompt[:50], model=model)
        await asyncio.sleep(self.latency)
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.call_count = 0
            self.last_reset_time = current_time
            self.logger.debug("Rate limit counter reset")
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise CustomRateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(status_code=500), body={})
            else:
                self.logger.info("Error mode reset after reaching max_errors")
                self.error_mode = False
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

    async def count_tokens(self, text: str) -> int:
        return len(text.split())

    async def reset(self):
        self.__init__()
        self.logger.debug("Reset MockClaudeClient")

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count

    def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def set_response(self, prompt, response):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def generate_response(self, prompt, model=None):
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

    async def count_tokens(self, text):
        return len(text.split())

    async def reset(self):
        self.__init__()
        self.logger.debug("Reset MockClaudeClient")

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count

    async def set_latency(self, latency):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_error_mode(self, mode):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_rate_limit(self, threshold):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def set_response(self, prompt, response):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def generate_response(self, prompt, model=None):
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise RateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

    async def count_tokens(self, text):
        return len(text.split())

    async def reset(self):
        self.__init__()
        self.logger.debug("Reset MockClaudeClient")

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency: float):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold: int):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        current_time = time.time()
        async with self.lock:
            if current_time - self.last_reset_time >= self.rate_limit_reset_time:
                self.logger.info(f"Resetting call count. Old count: {self.call_count}")
                self.call_count = 0
                self.last_reset_time = current_time
            self.call_count += 1
            self.logger.debug(f"Call count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
            if self.call_count > self.rate_limit_threshold:
                error_msg = f"Rate limit exceeded. Count: {self.call_count}, Threshold: {self.rate_limit_threshold}"
                self.logger.warning(error_msg)
                raise CustomRateLimitError(error_msg)
        self.logger.info(f"Generating response for model: {model}")
        self.logger.info(f"Generating response for model: {model}")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        truncated_response = response[:self.max_test_tokens]
        wrapped_response = f"<response>{truncated_response}</response>"
        self.logger.debug(f"Returning response: {wrapped_response[:50]}...")
        return wrapped_response

async def count_tokens(self, text: str) -> int:
    return len(text.split())

async def select_model(self, task: str) -> str:
    if "simple" in task.lower():
        return "claude-3-haiku-20240307"
    elif "complex" in task.lower():
        return "claude-3-opus-20240229"
    else:
        return "claude-3-sonnet-20240229"

async def reset(self):
    self.call_count = 0
    self.error_count = 0
    self.error_mode = False
    self.latency = 0
    self.responses = {}
    self.logger.debug("Reset MockClaudeClient")

async def get_call_count(self):
    return self.call_count

async def get_error_count(self):
    return self.error_count

async def simulate_concurrent_calls(self, num_calls):
    results = []
    for _ in range(num_calls):
        try:
            results.append(await self.generate_response("Test prompt"))
        except (RateLimitError, CustomRateLimitError) as e:
            results.append(e)
    return results

@pytest_asyncio.fixture
async def claude_manager(mock_claude_client):
    manager = ClaudeManager(client=mock_claude_client)
    logger.info("Created ClaudeManager instance", client_type="MockClaudeClient")
    try:
        yield manager
    finally:
        await manager.close()
        logger.info("Closed ClaudeManager instance")

@pytest.fixture(autouse=True)
async def reset_mock_claude_client(mock_claude_client):
    await mock_claude_client.reset()
    logger.info("Reset MockClaudeClient before test")
    yield
    await mock_claude_client.reset()
    logger.info("Reset MockClaudeClient after test")

@pytest.fixture(autouse=True)
def setup_teardown(caplog, request):
    caplog.set_level(logging.DEBUG)
    logger.info(f"Starting test: {request.node.name}")
    logger.debug(f"Test parameters: {request.node.callspec.params if hasattr(request.node, 'callspec') else 'No parameters'}")
    logger.debug(f"Test function source:\n{inspect.getsource(request.node.obj)}")
    yield
    logger.info(f"Finished test: {request.node.name}")
    logger.debug(f"Test result: {'Passed' if request.node.rep_call.passed else 'Failed'}")
    logger.debug(f"Log output for {request.node.name}:\n" + caplog.text)
    print(f"\nFull log output for {request.node.name}:")
    print(caplog.text)
    
    if not request.node.rep_call.passed:
        logger.error(f"Test failed: {request.node.name}")
        logger.error(f"Exception info: {request.node.rep_call.longrepr}")
        logger.error(f"Full test function:\n{inspect.getsource(request.node.obj)}")
        logger.error(f"Local variables at failure:\n{pprint.pformat(request.node.obj.__globals__)}")
        logger.error(f"Fixture values:\n{pprint.pformat(request.node.funcargs)}")

@pytest.fixture
def run_async_fixture():
    def _run_async_fixture(fixture):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fixture)
    return _run_async_fixture

async def set_error_mode(self, mode: bool):
    self.error_mode = mode
    self.logger.debug(f"Set error mode to: {mode}")

async def set_latency(self, latency: float):
    self.latency = latency
    self.logger.debug(f"Set latency to: {latency}")

async def set_rate_limit(self, threshold: int):
    self.rate_limit_threshold = threshold
    self.logger.debug(f"Set rate limit threshold to: {threshold}")

async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise CustomRateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

async def count_tokens(self, text: str) -> int:
    return len(text.split())

async def select_model(self, task: str) -> str:
    if "simple" in task.lower():
        return "claude-3-haiku-20240307"
    elif "complex" in task.lower():
        return "claude-3-opus-20240229"
    else:
        return "claude-3-sonnet-20240229"

async def reset(self):
    self.call_count = 0
    self.error_count = 0
    self.error_mode = False
    self.latency = 0
    self.responses = {}
    self.logger.debug("Reset MockClaudeClient")

def get_call_count(self):
    return self.call_count

def get_error_count(self):
    return self.error_count

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency: float):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold: int):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.logger.info(f"Resetting call count. Old count: {self.call_count}")
            self.call_count = 0
            self.last_reset_time = current_time
            self.logger.debug("Rate limit counter reset")
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}, Threshold: {self.rate_limit_threshold}")
        if self.call_count > self.rate_limit_threshold:
            error_msg = f"Rate limit exceeded. Count: {self.call_count}, Threshold: {self.rate_limit_threshold}"
            self.logger.warning(error_msg)
            raise CustomRateLimitError(error_msg)
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

    async def count_tokens(self, text: str) -> int:
        # A simple approximation of token counting
        return len(text.split())

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def reset(self):
        self.call_count = 0
        self.error_count = 0
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.logger.debug("Reset MockClaudeClient")

    async def get_call_count(self):
        return self.call_count

    async def get_error_count(self):
        return self.error_count

    async def simulate_concurrent_calls(self, num_calls):
        results = []
        tasks = [self.generate_response("Test prompt") for _ in range(num_calls)]
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except RateLimitError as e:
                results.append(e)
        successful = len([r for r in results if isinstance(r, str)])
        rate_limited = len([r for r in results if isinstance(r, RateLimitError)])
        self.logger.info(f"Simulated {num_calls} concurrent calls. Results: {successful} successful, {rate_limited} rate limited")
        return results
        self.latency = 0
        self.responses = {}
        self.max_test_tokens = 1000
        self.call_count = 0
        self.error_count = 0
        self.max_errors = 3
        self.max_context_length = 200000
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    async def set_response(self, prompt: str, response: str):
        self.responses[prompt] = response
        self.logger.debug(f"Set response for prompt: {prompt[:50]}...")

    async def set_error_mode(self, mode: bool):
        self.error_mode = mode
        self.logger.debug(f"Set error mode to: {mode}")

    async def set_latency(self, latency: float):
        self.latency = latency
        self.logger.debug(f"Set latency to: {latency}")

    async def set_rate_limit(self, threshold: int):
        self.rate_limit_threshold = threshold
        self.logger.debug(f"Set rate limit threshold to: {threshold}")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        await asyncio.sleep(self.latency)
        current_time = time.time()
        if current_time - self.last_reset_time >= self.rate_limit_reset_time:
            self.call_count = 0
            self.last_reset_time = current_time
            self.logger.debug("Rate limit counter reset")
        self.call_count += 1
        self.logger.debug(f"Call count: {self.call_count}")
        if self.call_count > self.rate_limit_threshold:
            self.logger.warning("Rate limit exceeded")
            raise CustomRateLimitError("Rate limit exceeded")
        if self.error_mode:
            self.error_count += 1
            self.logger.debug(f"Error count: {self.error_count}")
            if self.error_count <= self.max_errors:
                self.logger.error("Simulated API error")
                raise APIStatusError("Simulated API error", response=MagicMock(), body={})
        response = self.responses.get(prompt, "Default mock response")
        self.logger.debug(f"Returning response: {response[:50]}...")
        return response

    async def count_tokens(self, text: str) -> int:
        return len(text.split())

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def reset(self):
        self.call_count = 0
        self.error_count = 0
        self.error_mode = False
        self.latency = 0
        self.responses = {}
        self.logger.debug("Reset MockClaudeClient")

    def get_call_count(self):
        return self.call_count

    def get_error_count(self):
        return self.error_count

    def get_call_count(self):
        return self.call_count

    def get_error_count(self):
        return self.error_count

@pytest_asyncio.fixture
async def claude_manager(mock_claude_client):
    manager = ClaudeManager(client=mock_claude_client)
    logger.debug(f"Created ClaudeManager instance with {mock_claude_client}")
    try:
        yield manager
    finally:
        await manager.close()
        logger.debug(f"Closed ClaudeManager instance. Final state: {mock_claude_client}")

class ClaudeManager:
    def __init__(self, client):
        self.client = client
        self.max_context_length = getattr(client, 'max_context_length', 200000)  # Default to 200k if not specified
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"Initialized ClaudeManager with client: {client.__class__.__name__}")

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50] if isinstance(prompt, str) else str(prompt)[:50]}...")
        if not isinstance(prompt, str):
            error_msg = f"Invalid prompt type: {type(prompt)}. Must be a string."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if not prompt.strip():
            error_msg = "Invalid prompt: must be a non-empty string"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if len(prompt) > self.max_context_length:
            error_msg = f"Prompt length ({len(prompt)}) exceeds maximum context length of {self.max_context_length}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if len(prompt) > self.max_context_length:
            error_msg = f"Prompt length ({len(prompt)}) exceeds maximum context length of {self.max_context_length}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if "<script>" in prompt.lower():
            error_msg = "Invalid prompt: contains potentially unsafe content (<script> tag)"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', prompt):
            error_msg = "Invalid prompt: contains sensitive information (SSN pattern detected)"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            response = await self.client.generate_response(prompt, model)
            self.logger.debug(f"Response generated successfully: {response[:50]}...")
            return response
        except CustomRateLimitError as e:
            self.logger.warning(f"Rate limit reached: {str(e)}")
            raise
        except APIStatusError as e:
            self.logger.error(f"API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    async def count_tokens(self, text: str) -> int:
        return await self.client.count_tokens(text)

    async def close(self):
        await self.client.reset()

    def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def set_latency(self, latency):
        await self.client.set_latency(latency)

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50] if isinstance(prompt, str) else str(prompt)[:50]}...")
        if not isinstance(prompt, str):
            error_msg = f"Invalid prompt type: {type(prompt)}. Must be a string."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if not prompt.strip():
            error_msg = "Invalid prompt: must be a non-empty string"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if len(prompt) > self.max_context_length:
            self.logger.error(f"Prompt length exceeds maximum context length of {self.max_context_length}")
            raise ValueError(f"Prompt length exceeds maximum context length of {self.max_context_length}")
        try:
            prompt_str = str(prompt)
        except Exception as e:
            self.logger.error(f"Failed to convert prompt to string: {e}")
            raise ValueError(f"Invalid prompt: {e}")
        try:
            response = await self.client.generate_response(prompt, model)
            self.logger.debug(f"Response generated successfully: {response[:50]}...")
            return response
        except (CustomRateLimitError, RateLimitError) as e:
            self.logger.warning(f"Rate limit reached: {str(e)}")
            raise CustomRateLimitError(str(e))
        except APIStatusError as e:
            self.logger.error(f"API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise

    async def count_tokens(self, text):
        return await self.client.count_tokens(text)

    async def close(self):
        await self.client.reset()

    def select_model(self, task):
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def set_response(self, prompt, response):
        await self.client.set_response(prompt, response)

    async def set_error_mode(self, mode):
        await self.client.set_error_mode(mode)

    async def set_rate_limit(self, threshold):
        await self.client.set_rate_limit(threshold)

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Invalid prompt: must be a non-empty string")
        if len(prompt) > self.max_context_length:
            raise ValueError(f"Prompt length exceeds maximum context length of {self.max_context_length}")
        try:
            response = await self.client.generate_response(prompt, model)
            self.logger.debug(f"Response generated successfully: {response[:50]}...")
            return response
        except CustomRateLimitError as e:
            self.logger.warning(f"Rate limit reached: {str(e)}")
            raise
        except APIStatusError as e:
            self.logger.error(f"API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    async def count_tokens(self, text: str) -> int:
        self.logger.debug(f"Counting tokens for text: {text[:50]}...")
        return await self.client.count_tokens(text)

    async def select_model(self, task: str) -> str:
        self.logger.debug(f"Selecting model for task: {task}")
        return await self.client.select_model(task)

    async def close(self):
        self.logger.debug("Closing ClaudeManager")
        await self.client.reset()

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        await self.client.set_response(prompt, response)

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        await self.client.set_error_mode(mode)

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        await self.client.set_latency(latency)

    async def set_rate_limit(self, threshold: int):
        self.logger.debug(f"Setting rate limit threshold to: {threshold}")
        await self.client.set_rate_limit(threshold)

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50] if isinstance(prompt, str) else str(prompt)[:50]}...")
        if not isinstance(prompt, str):
            error_msg = f"Invalid prompt type: {type(prompt)}. Must be a string."
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if not prompt.strip():
            error_msg = "Invalid prompt: must be a non-empty string"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if len(prompt) > self.max_context_length:
            error_msg = f"Prompt length ({len(prompt)}) exceeds maximum context length of {self.max_context_length}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if "<script>" in prompt.lower():
            error_msg = "Invalid prompt: contains potentially unsafe content (<script> tag)"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', prompt):
            error_msg = "Invalid prompt: contains sensitive information (SSN pattern detected)"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        try:
            self.logger.info(f"Sending request to client for model: {model}")
            response = await self.client.generate_response(prompt, model)
            self.logger.debug(f"Response generated successfully: {response[:50]}...")
            return response
        except (RateLimitError, CustomRateLimitError) as e:
            self.logger.warning(f"Rate limit reached: {str(e)}")
            raise RateLimitError(str(e))
        except APIStatusError as e:
            self.logger.error(f"API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise

    async def count_tokens(self, text: str) -> int:
        self.logger.debug(f"Counting tokens for text: {text[:50]}...")
        return await self.client.count_tokens(text)

    async def select_model(self, task: str) -> str:
        self.logger.debug(f"Selecting model for task: {task}")
        return await self.client.select_model(task)

    async def close(self):
        self.logger.debug("Closing ClaudeManager")
        await self.client.reset()

    async def set_response(self, prompt: str, response: str):
        self.logger.debug(f"Setting response for prompt: {prompt[:50]}...")
        await self.client.set_response(prompt, response)

    async def set_error_mode(self, mode: bool):
        self.logger.debug(f"Setting error mode to: {mode}")
        await self.client.set_error_mode(mode)

    async def set_latency(self, latency: float):
        self.logger.debug(f"Setting latency to: {latency}")
        await self.client.set_latency(latency)

    async def set_rate_limit(self, threshold: int):
        self.logger.debug(f"Setting rate limit threshold to: {threshold}")
        await self.client.set_rate_limit(threshold)

@pytest.fixture(autouse=True)
async def setup_teardown(mock_claude_client, claude_manager):
    logger.info("Setting up test environment")
    yield
    logger.info("Tearing down test environment")
    await mock_claude_client.reset()
    await claude_manager.close()

@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def llm_manager(claude_manager):
    manager = LLMManager(claude_manager=claude_manager)
    logger.debug("Created LLMManager instance")
    return manager

@pytest.fixture
def mock_claude_manager():
    manager = MagicMock(spec=ClaudeManager)
    logger.debug("Created mock ClaudeManager")
    return manager

@pytest.fixture(scope="module")
def cached_responses(request):
    cache = {}
    def _cached_response(prompt, response):
        if prompt not in cache:
            cache[prompt] = response
        return cache[prompt]
    request.addfinalizer(cache.clear)
    logger.debug("Created cached_responses fixture")
    return _cached_response

@pytest.fixture(autouse=True)
def log_test_name(request):
    logger.info(f"Starting test: {request.node.name}")
    yield
    logger.info(f"Finished test: {request.node.name}")

@pytest.mark.asyncio
@log_test_start_end
async def test_claude_api_latency(claude_manager, mock_claude_client):
    try:
        await mock_claude_client.set_latency(0.5)  # Set a 500ms latency
        logger.info("Set latency to 500ms")
        start_time = time.time()
        response = await claude_manager.generate_response("Test prompt")
        end_time = time.time()
        elapsed_time = end_time - start_time
        assert elapsed_time >= 0.5, f"API call should take at least 500ms, but took {elapsed_time:.2f}s"
        logger.info(f"API call latency: {elapsed_time:.2f} seconds")
        logger.info(f"Response: {response}")
        assert "<response>" in response and "</response>" in response, "Response should be wrapped in <response> tags"
    except Exception as e:
        logger.error(f"Error in test_claude_api_latency: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Finished test_claude_api_latency")

@pytest.mark.asyncio
async def test_claude_api_rate_limiting(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    await mock_claude_client.set_rate_limit(5)  # Set a lower threshold for testing
    logger.info("Set rate limit to 5 calls")

    async def make_call(i):
        try:
            return await claude_manager.generate_response(f"Test prompt {i}")
        except CustomRateLimitError:
            return "Rate limited"

    results = await asyncio.gather(*[make_call(i) for i in range(10)], return_exceptions=True)
    
    successful_calls = [r for r in results if r != "Rate limited"]
    rate_limited_calls = [r for r in results if r == "Rate limited"]

    assert len(successful_calls) == 5, f"Expected 5 successful calls, but got {len(successful_calls)}"
    assert len(rate_limited_calls) == 5, f"Expected 5 rate-limited calls, but got {len(rate_limited_calls)}"

    call_count = await mock_claude_client.get_call_count()
    assert call_count == 10, f"Expected 10 total calls, but got {call_count}"

    logger.info(f"Rate limiting test passed. Total calls made: {call_count}")
    assert "Rate limit exceeded" in caplog.text

@pytest.mark.asyncio
async def test_claude_api_with_custom_responses(claude_manager, mock_claude_client_with_responses):
    responses = {
        "Hello": "Hi there!",
        "How are you?": "I'm doing well, thank you for asking.",
        "What's the weather like?": "I'm sorry, I don't have real-time weather information."
    }
    await mock_claude_client_with_responses(responses)

    for prompt, expected_response in responses.items():
        response = await claude_manager.generate_response(prompt)
        assert response == f"<response>{expected_response}</response>", f"Expected '{expected_response}', but got '{response}'"

@pytest.mark.asyncio
async def test_claude_api_error_handling(claude_manager, mock_claude_client_with_error_mode):
    await mock_claude_client_with_error_mode(True)
    
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt")

    await mock_claude_client_with_error_mode(False)
    response = await claude_manager.generate_response("Test prompt")
    assert "<response>" in response and "</response>" in response, "Response should be wrapped in <response> tags"

@pytest.mark.asyncio
async def test_claude_api_rate_limit_adjustment(claude_manager, mock_claude_client_with_rate_limit):
    await mock_claude_client_with_rate_limit(3)
    
    for i in range(3):
        response = await claude_manager.generate_response(f"Test prompt {i}")
        assert "<response>" in response, f"Expected a valid response for call {i+1}"

    with pytest.raises(CustomRateLimitError):
        await claude_manager.generate_response("This should fail due to rate limit")

@pytest.mark.asyncio
async def test_mock_claude_client_concurrent_calls(mock_claude_client):
    mock_claude_client.rate_limit_threshold = 5
    results = await mock_claude_client.simulate_concurrent_calls(10)

    successful_calls = [r for r in results if isinstance(r, str)]
    rate_limit_errors = [r for r in results if isinstance(r, CustomRateLimitError)]

    assert len(successful_calls) == 5, f"Expected 5 successful calls, but got {len(successful_calls)}"
    assert len(rate_limit_errors) == 5, f"Expected 5 rate limit errors, but got {len(rate_limit_errors)}"
    call_count = await mock_claude_client.get_call_count()
    assert call_count == 10, f"Expected 10 total calls, but got {call_count}"

@pytest.mark.asyncio
async def test_claude_api_rate_limiting(claude_manager, mock_claude_client):
    try:
        await mock_claude_client.set_rate_limit(5)  # Set a lower threshold for testing
        logger.info("Set rate limit to 5 calls")
        with pytest.raises(RateLimitError):
            for i in range(10):  # Attempt to make 10 calls
                logger.debug(f"Making API call {i+1}")
                await claude_manager.generate_response(f"Test prompt {i}")
            call_count = await mock_claude_client.get_call_count()
            assert call_count == 6, f"Expected 6 calls (5 successful + 1 that raises the error), but got {call_count}"
            logger.info(f"Rate limiting test passed. Total calls made: {call_count}")
    except Exception as e:
        logger.error(f"Error in test_claude_api_rate_limiting: {str(e)}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_claude_api_error_handling(claude_manager, mock_claude_client):
    await mock_claude_client.set_error_mode(True)
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt")

@pytest.mark.asyncio
async def test_claude_api_max_tokens(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    long_prompt = "a" * (claude_manager.max_context_length + 1)
    with pytest.raises(ValueError, match="Prompt length .* exceeds maximum context length"):
        await claude_manager.generate_response(long_prompt)
    assert "Prompt length" in caplog.text and "exceeds maximum context length" in caplog.text

@pytest.mark.asyncio
async def test_claude_api_response_truncation(claude_manager, mock_claude_client):
    long_response = "b" * (mock_claude_client.max_test_tokens * 2)
    await mock_claude_client.set_response("Test prompt", long_response)
    response = await claude_manager.generate_response("Test prompt")
    assert len(response) <= mock_claude_client.max_test_tokens + 50  # Allow for some overhead

@pytest.mark.asyncio
async def test_concurrent_claude_api_calls(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    num_concurrent_calls = 10
    mock_claude_client.rate_limit_threshold = 5
    await mock_claude_client.set_response("Test prompt", "Test response")

    logging.info(f"Starting concurrent API calls test with {num_concurrent_calls} calls")

    async def make_call(i):
        try:
            logging.debug(f"Making call {i}")
            response = await claude_manager.generate_response(f"Test prompt {i}", "claude-3-haiku-20240307")
            logging.debug(f"Call {i} completed with response: {response}")
            return response
        except RateLimitError as e:
            logging.debug(f"Call {i} rate limited: {str(e)}")
            return e

    tasks = [make_call(i) for i in range(num_concurrent_calls)]
    results = await asyncio.gather(*tasks)

    successful_calls = [r for r in results if isinstance(r, str)]
    rate_limit_errors = [r for r in results if isinstance(r, RateLimitError)]

    logging.info(f"Concurrent calls completed. Successful: {len(successful_calls)}, Rate Limited: {len(rate_limit_errors)}")

    assert len(successful_calls) + len(rate_limit_errors) == num_concurrent_calls, f"Expected {num_concurrent_calls} total results, got {len(successful_calls) + len(rate_limit_errors)}"
    assert len(successful_calls) == mock_claude_client.rate_limit_threshold, f"Expected {mock_claude_client.rate_limit_threshold} successful calls, got {len(successful_calls)}"
    assert len(rate_limit_errors) == num_concurrent_calls - mock_claude_client.rate_limit_threshold, f"Expected {num_concurrent_calls - mock_claude_client.rate_limit_threshold} rate limit errors, got {len(rate_limit_errors)}"
    assert all(result == "<response>Test response</response>" for result in successful_calls), "Not all successful responses match expected format"
    assert await mock_claude_client.get_call_count() == num_concurrent_calls, f"Expected {num_concurrent_calls} calls to mock client, got {await mock_claude_client.get_call_count()}"

    for i in range(num_concurrent_calls):
        assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"

    assert "Rate limit exceeded" in caplog.text, "Missing rate limit warning in logs"

    logging.info("Concurrent API calls test completed successfully")

@pytest.mark.asyncio
async def test_claude_manager_error_handling(claude_manager, mock_claude_client):
    await mock_claude_client.set_error_mode(True)
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt")
    
    await mock_claude_client.set_error_mode(False)
    response = await claude_manager.generate_response("Test prompt")
    assert "<response>" in response and "</response>" in response, "Response should be wrapped in <response> tags"

import pytest
import asyncio
import pytest_asyncio
import tenacity
import time
import anthropic
import logging
import json
import functools
import re
import inspect
import pprint
import sys
import os
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError, RateLimit
@pytest.mark.asyncio
async def test_rate_limit_reset(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    mock_claude_client.rate_limit_threshold = 3
    mock_claude_client.rate_limit_reset_time = 1  # 1 second for faster testing

    logger.info("Starting rate limit reset test")
    logger.debug(f"Rate limit threshold: {mock_claude_client.rate_limit_threshold}")
    logger.debug(f"Rate limit reset time: {mock_claude_client.rate_limit_reset_time} seconds")
    initial_call_count = await mock_claude_client.get_call_count()
    logger.debug(f"Initial call count: {initial_call_count}")
    logger.debug(f"Initial last reset time: {mock_claude_client.last_reset_time}")

    # Log the test steps
    logger.info("Step 1: Make calls until rate limit is reached")

    # Make calls until rate limit is reached
    for i in range(3):
        try:
            logger.debug(f"Attempting call {i+1}")
            response = await claude_manager.generate_response(f"Test prompt {i}")
            assert response == "<response>Default mock response</response>", f"Unexpected response for call {i+1}: {response}"
            assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"
            logger.debug(f"Call {i+1} successful")
        except Exception as e:
            logger.error(f"Unexpected error during rate limit test: {str(e)}")
            pytest.fail(f"Unexpected error during rate limit test: {str(e)}")

    logger.info("Rate limit should be reached. Attempting one more call.")
    # Next call should raise RateLimitError
    with pytest.raises(RateLimitError):
        await claude_manager.generate_response("Test prompt 3")
    assert "Rate limit reached" in caplog.text, "Missing rate limit warning in logs"
    logger.info("Rate limit error raised as expected")

    logger.info("Waiting for rate limit to reset")
    await asyncio.sleep(mock_claude_client.rate_limit_reset_time + 0.1)  # Wait slightly longer than the reset time
    logger.info("Rate limit reset period completed")

    # Should be able to make calls again
    try:
        logger.debug("Attempting call after rate limit reset")
        response = await claude_manager.generate_response("Test prompt 4")
        assert response == "<response>Default mock response</response>", f"Unexpected response after reset: {response}"
        assert "Generating response for prompt: Test prompt 4" in caplog.text, "Missing log for post-reset prompt"
        logger.info("Successfully made call after rate limit reset")
    except Exception as e:
        logger.error(f"Unexpected error after rate limit reset: {str(e)}")
        pytest.fail(f"Unexpected error after rate limit reset: {str(e)}")

    logger.info("Rate limit reset test completed successfully")

    # Log the entire captured log for debugging
    logger.debug("Captured log:")
    logger.debug(caplog.text)

@pytest.mark.asyncio
async def test_token_counting(claude_manager):
    text = "This is a test sentence."
    token_count = await claude_manager.count_tokens(text)
    assert token_count == 5, f"Expected 5 tokens, but got {token_count}"
    
    # Add more test cases
    long_text = "This is a longer test sentence with more tokens to count."
    long_token_count = await claude_manager.count_tokens(long_text)
    assert long_token_count == 11, f"Expected 11 tokens, but got {long_token_count}"
    
    empty_text = ""
    empty_token_count = await claude_manager.count_tokens(empty_text)
    assert empty_token_count == 0, f"Expected 0 tokens for empty string, but got {empty_token_count}"

@pytest.mark.asyncio
async def test_generate_response(claude_manager):
    prompt = "Tell me a joke"
    response = await claude_manager.generate_response(prompt)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"

@pytest.mark.asyncio
async def test_generate_response(mock_claude_client):
    prompt = "Tell me a joke"
    response = await mock_claude_client.generate_response(prompt)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"

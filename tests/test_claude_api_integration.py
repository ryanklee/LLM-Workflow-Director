import pytest
import pytest_asyncio
import asyncio
import logging
import time
import inspect
import pprint
from unittest.mock import MagicMock
from anthropic import APIStatusError
from src.exceptions import CustomRateLimitError, RateLimitError
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient
from pact import Consumer, Provider

from typing import List, Union

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture(scope='module')
def pact():
    return Consumer('LLMWorkflowDirector').has_pact_with(Provider('ClaudeAPI'))

@pytest_asyncio.fixture
async def mock_claude_client():
    client = MockClaudeClient(api_key="test_api_key")
    client.lock = asyncio.Lock()  # Ensure the lock is initialized
    logger.debug(f"Created MockClaudeClient instance with rate_limit_threshold={client.rate_limit_threshold}, rate_limit_reset_time={client.rate_limit_reset_time}")
    yield client
    await client.reset()
    logger.debug(f"Reset MockClaudeClient instance. Final call_count: {client.call_count}, error_count: {client.error_count}")

@pytest_asyncio.fixture
async def claude_manager(mock_claude_client):
    manager = ClaudeManager(client=mock_claude_client)
    logger.debug(f"Created ClaudeManager instance with MockClaudeClient")
    yield manager
    await manager.close()
    logger.debug(f"Closed ClaudeManager instance")

@pytest_asyncio.fixture
async def mock_claude_client_with_responses(request):
    logger = logging.getLogger(__name__)
    logger.info(f"Initializing mock_claude_client_with_responses fixture in test {request.node.name}")
    
    mock_client = None
    try:
        logger.debug("Attempting to create MockClaudeClient instance")
        mock_client = MockClaudeClient(api_key="test_api_key")
        logger.debug(f"Created MockClaudeClient instance: {mock_client}")
        
        async def setup_responses(responses):
            logger.debug(f"Setting up responses: {responses}")
            for prompt, response in responses.items():
                await mock_client.set_response(prompt, response)
                logger.debug(f"Set response for prompt: {prompt[:50]}...")
        
        logger.info(f"Returning MockClaudeClient: {mock_client}")
        yield mock_client, setup_responses
    except Exception as e:
        logger.error(f"Error creating MockClaudeClient: {str(e)}", exc_info=True)
        logger.error(f"MockClaudeClient class: {MockClaudeClient}")
        logger.error(f"MockClaudeClient.__init__ signature: {inspect.signature(MockClaudeClient.__init__)}")
        raise
    finally:
        logger.info(f"Cleaning up mock_claude_client_with_responses fixture for test {request.node.name}")
        if mock_client:
            await mock_client.reset()
        logger.debug(f"MockClaudeClient reset completed")

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
    logger = logging.getLogger(__name__)
    logger.info(f"Starting test: {request.node.name}")
    logger.debug(f"Test parameters: {request.node.callspec.params if hasattr(request.node, 'callspec') else 'No parameters'}")
    logger.debug(f"Test function source:\n{inspect.getsource(request.node.obj)}")
    yield
    logger.info(f"Finished test: {request.node.name}")
    try:
        # Use getattr to safely access rep_call attribute
        rep_call = getattr(request.node, 'rep_call', None)
        if rep_call:
            logger.debug(f"Test result: {'Passed' if rep_call.passed else 'Failed'}")
            if not rep_call.passed:
                logger.error(f"Test failed: {request.node.name}")
                logger.error(f"Exception info: {rep_call.longrepr}")
        else:
            logger.warning("Unable to determine test result. rep_call attribute not found.")
    except Exception as e:
        logger.error(f"Error accessing test result: {str(e)}", exc_info=True)

    logger.debug(f"Log output for {request.node.name}:\n" + caplog.text)
    print(f"\nFull log output for {request.node.name}:")
    print(caplog.text)
    
    logger.debug(f"Full test function:\n{inspect.getsource(request.node.obj)}")
    logger.debug(f"Local variables at failure:\n{pprint.pformat(request.node.obj.__globals__)}")
    logger.debug(f"Fixture values:\n{pprint.pformat(request.node.funcargs)}")

@pytest.mark.asyncio
async def test_claude_api_contract(pact):
    pact.given(
        'A request for message creation'
    ).upon_receiving(
        'A valid message creation request'
    ).with_request(
        'POST', '/v1/messages',
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': 'Hello, Claude!'}]
        }
    ).will_respond_with(200, body={
        'id': pytest.matchers.like('msg_123abc'),
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': pytest.matchers.like('Hello! How can I assist you today?')
            }
        ],
        'model': 'claude-3-opus-20240229',
        'stop_reason': 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': pytest.matchers.like(5),
            'output_tokens': pytest.matchers.like(9)
        }
    })

    async with pact:
        claude_manager = ClaudeManager(client=None)  # We'll mock the client
        result = await claude_manager.generate_response('Hello, Claude!', model='claude-3-opus-20240229')
        assert result.startswith('Hello!')

@pytest.mark.asyncio
async def test_mock_claude_client_custom_responses(mock_claude_client_with_responses):
    logger = logging.getLogger(__name__)
    logger.info("Starting test_mock_claude_client_custom_responses")
    
    mock_client, setup_responses = mock_claude_client_with_responses
    logger.debug(f"Received mock_client: {mock_client}")
    
    responses = {
        "Hello": "Hi there!",
        "How are you?": "I'm doing well, thank you for asking.",
        "What's the weather like?": "I'm sorry, I don't have real-time weather information."
    }
    await setup_responses(responses)
    logger.debug("Set custom responses")

    for prompt, expected_response in responses.items():
        logger.debug(f"Testing prompt: {prompt}")
        try:
            response = await mock_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            logger.debug(f"Raw response: {response}")
            actual_response = response["content"][0]["text"]
            logger.debug(f"Received response: {actual_response}")
            assert actual_response == f"<response>{expected_response}</response>", f"Expected '<response>{expected_response}</response>', but got '{actual_response}'"
            logger.debug(f"Successful response for prompt: {prompt}")
        except AttributeError as e:
            logger.error(f"AttributeError occurred. Mock client state: {await mock_client.debug_dump()}")
            raise
        except Exception as e:
            logger.error(f"Error processing prompt '{prompt}': {str(e)}", exc_info=True)
            raise

    logger.info("Completed test_mock_claude_client_custom_responses successfully")

@pytest.mark.asyncio
async def test_mock_claude_client_custom_responses(mock_claude_client_with_responses):
    logger = logging.getLogger(__name__)
    logger.info("Starting test_mock_claude_client_custom_responses")
    
    mock_client, setup_responses = mock_claude_client_with_responses
    logger.debug(f"Received mock_client: {mock_client}")
    
    responses = {
        "Hello": "Hi there!",
        "How are you?": "I'm doing well, thank you for asking.",
        "What's the weather like?": "I'm sorry, I don't have real-time weather information."
    }
    await setup_responses(responses)
    logger.debug("Set custom responses")

    for prompt, expected_response in responses.items():
        logger.debug(f"Testing prompt: {prompt}")
        try:
            response = await mock_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            logger.debug(f"Raw response: {response}")
            actual_response = response["content"][0]["text"]
            logger.debug(f"Received response: {actual_response}")
            assert actual_response == f"<response>{expected_response}</response>", f"Expected '<response>{expected_response}</response>', but got '{actual_response}'"
            logger.debug(f"Successful response for prompt: {prompt}")
        except AttributeError as e:
            logger.error(f"AttributeError occurred. Mock client state: {await mock_client.debug_dump()}")
            raise
        except Exception as e:
            logger.error(f"Error processing prompt '{prompt}': {str(e)}", exc_info=True)
            raise

    logger.info("Completed test_mock_claude_client_custom_responses successfully")

@pytest.fixture(scope="function", autouse=True)
def function_logger(request):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting test function: {request.node.name}")
    yield
    logger.info(f"Finished test function: {request.node.name}")

@pytest.fixture(scope="function")
def mock_claude_client():
    client = MockClaudeClient()
    client.logger.debug(f"Created new MockClaudeClient instance: {id(client)}")
    return client

@pytest.fixture(scope="function")
def mock_claude_client():
    client = MockClaudeClient()
    client.logger.debug(f"Created new MockClaudeClient instance: {id(client)}")
    return client

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
        self.lock = asyncio.Lock()
        
    def __str__(self):
        return f"MockClaudeClient(rate_limit_threshold={self.rate_limit_threshold}, " \
               f"call_count={self.call_count}, error_count={self.error_count}, " \
               f"error_mode={self.error_mode})"

    async def debug_dump(self):
        self.logger.debug("Starting debug_dump method")
        try:
            state = {}
            for attr, value in self.__dict__.items():
                if attr != 'logger':
                    state[attr] = str(value)
                    self.logger.debug(f"{attr}: {value}")
            self.logger.debug("Finished debug_dump method")
            return state
        except Exception as e:
            self.logger.error(f"Error in debug_dump: {str(e)}", exc_info=True)
            raise

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

    async def count_tokens(self, text: str) -> int:
        return len(text.split())

    async def select_model(self, task: str) -> str:
        if "simple" in task.lower():
            return "claude-3-haiku-20240307"
        elif "complex" in task.lower():
            return "claude-3-opus-20240229"
        else:
            return "claude-3-sonnet-20240229"

    async def simulate_concurrent_calls(self, num_calls):
        tasks = [self.generate_response(f"Test prompt {i}") for i in range(num_calls)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r if isinstance(r, str) else r for r in results]

@pytest_asyncio.fixture
async def claude_manager(mock_claude_client):
    manager = ClaudeManager(client=mock_claude_client)
    logger.info("Created ClaudeManager instance", client_type="MockClaudeClient")
    try:
        yield manager
    finally:
        await manager.close()
        logger.info("Closed ClaudeManager instance")

@pytest.mark.asyncio
async def test_claude_manager_generate_response(claude_manager, mock_claude_client_with_responses):
    mock_client, setup_responses = mock_claude_client_with_responses
    await setup_responses({"Hello, Claude!": "Hello! How can I assist you today?"})
    
    response = await claude_manager.generate_response("Hello, Claude!", model="claude-3-opus-20240229")
    assert response == "Hello! How can I assist you today?"

@pytest.mark.asyncio
async def test_backoff_and_retry_mechanism(claude_manager, mock_claude_client_with_rate_limit):
    rate_limit = 5
    await mock_claude_client_with_rate_limit(rate_limit)

    # Make requests up to the rate limit
    for _ in range(rate_limit):
        await claude_manager.generate_response("Test prompt")

    # The next request should trigger the backoff and retry mechanism
    start_time = time.time()
    response = await claude_manager.generate_response("Test prompt")
    end_time = time.time()

    # Check that the response was eventually successful
    assert response is not None

    # Check that the total time taken is consistent with our backoff strategy
    expected_min_time = sum(claude_manager.retry_delay * (2 ** i) for i in range(claude_manager.max_retries))
    assert end_time - start_time >= expected_min_time

@pytest.mark.asyncio
async def test_max_retries_exceeded(claude_manager, mock_claude_client_with_rate_limit):
    rate_limit = 5
    await mock_claude_client_with_rate_limit(rate_limit)
    claude_manager.max_retries = 3

    # Make requests up to the rate limit
    for _ in range(rate_limit):
        await claude_manager.generate_response("Test prompt")

    # Set the reset time to a very large value to ensure rate limit errors persist
    await claude_manager.client.set_rate_limit_reset_time(1000000)

    # The next request should raise a CustomRateLimitError after max_retries attempts
    with pytest.raises(CustomRateLimitError):
        await claude_manager.generate_response("Test prompt")

    # Check that the number of attempts matches max_retries
    assert await claude_manager.client.get_call_count() == rate_limit + claude_manager.max_retries

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
    logger = logging.getLogger(__name__)
    logger.info(f"Starting test: {request.node.name}")
    logger.debug(f"Test parameters: {request.node.callspec.params if hasattr(request.node, 'callspec') else 'No parameters'}")
    logger.debug(f"Test function source:\n{inspect.getsource(request.node.obj)}")
    yield
    logger.info(f"Finished test: {request.node.name}")
    try:
        # Use getattr to safely access rep_call attribute
        rep_call = getattr(request.node, 'rep_call', None)
        if rep_call:
            logger.debug(f"Test result: {'Passed' if rep_call.passed else 'Failed'}")
            if not rep_call.passed:
                logger.error(f"Test failed: {request.node.name}")
                logger.error(f"Exception info: {rep_call.longrepr}")
        else:
            logger.warning("Unable to determine test result. rep_call attribute not found.")
    except Exception as e:
        logger.error(f"Error accessing test result: {str(e)}", exc_info=True)

    logger.debug(f"Log output for {request.node.name}:\n" + caplog.text)
    print(f"\nFull log output for {request.node.name}:")
    print(caplog.text)
    
    logger.debug(f"Full test function:\n{inspect.getsource(request.node.obj)}")
    logger.debug(f"Local variables at failure:\n{pprint.pformat(request.node.obj.__globals__)}")
    logger.debug(f"Fixture values:\n{pprint.pformat(request.node.funcargs)}")

@pytest.fixture
def run_async_fixture():
    def _run_async_fixture(fixture):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fixture)
    return _run_async_fixture

@pytest.mark.asyncio
async def test_mock_claude_client_custom_responses(mock_claude_client_with_responses, request):
    logger = logging.getLogger(__name__)
    logger.info(f"Starting test_mock_claude_client_custom_responses in {request.node.name}")
    
    try:
        mock_client, setup_responses = mock_claude_client_with_responses
        logger.debug(f"MockClaudeClient: {mock_client}")
        
        # Verify mock_client is not None
        if mock_client is None:
            raise ValueError("mock_client is None")
        
        # Verify debug_dump is an async method
        if not asyncio.iscoroutinefunction(mock_client.debug_dump):
            raise TypeError("debug_dump is not an async method")
        
        # Call debug_dump to verify the client state
        try:
            state = await mock_client.debug_dump()
            logger.debug(f"MockClaudeClient state: {state}")
        except Exception as e:
            logger.error(f"Error calling debug_dump: {str(e)}", exc_info=True)
            raise
        
        responses = {
            "Hello": "Hi there!",
            "How are you?": "I'm doing well, thank you for asking.",
            "What's the weather like?": "I'm sorry, I don't have real-time weather information."
        }
        await setup_responses(responses)
        logger.debug("Set custom responses")

        for prompt, expected_response in responses.items():
            logger.debug(f"Testing prompt: {prompt}")
            try:
                response = await mock_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                logger.debug(f"Raw response: {response}")
                actual_response = response["content"][0]["text"]
                logger.debug(f"Received response: {actual_response}")
                assert actual_response == f"<response>{expected_response}</response>", f"Expected '<response>{expected_response}</response>', but got '{actual_response}'"
                logger.debug(f"Successful response for prompt: {prompt}")
            except AttributeError as e:
                logger.error(f"AttributeError: {str(e)}. MockClaudeClient structure: {dir(mock_client)}")
                raise
            except Exception as e:
                logger.error(f"Error processing prompt '{prompt}': {str(e)}", exc_info=True)
                raise

        logger.info("Completed test_mock_claude_client_custom_responses successfully")
    except Exception as e:
        logger.error(f"Error in test_mock_claude_client_custom_responses: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info(f"Finished test_mock_claude_client_custom_responses in {request.node.name}")

# ... (rest of the test file remains unchanged)

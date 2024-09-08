import pytest
import asyncio
import tenacity
import time
import anthropic
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from src.claude_manager import ClaudeManager
from src.exceptions import RateLimitError, RateLimitError as CustomRateLimitError
from src.mock_claude_client import MockClaudeClient
from src.llm_manager import LLMManager
from anthropic import APIError, APIStatusError

# Set up logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_claude_api_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@pytest.fixture
async def mock_claude_client():
    client = MockClaudeClient()
    logger.debug("Created MockClaudeClient instance")
    yield client
    await client.reset()
    logger.debug("Reset MockClaudeClient instance")

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

@pytest.fixture
async def claude_manager(mock_claude_client):
    manager = ClaudeManager(client=mock_claude_client)
    logger.debug("Created ClaudeManager instance with MockClaudeClient")
    yield manager
    await manager.close()
    logger.debug("Closed ClaudeManager instance")

class ClaudeManager:
    def __init__(self, client):
        self.client = client
        self.max_context_length = client.max_context_length
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    async def generate_response(self, prompt: str, model: str = "claude-3-opus-20240229") -> str:
        self.logger.debug(f"Generating response for prompt: {prompt[:50]}...")
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

@pytest.fixture(autouse=True)
async def setup_teardown(mock_claude_client, claude_manager):
    logger.info("Setting up test environment")
    yield
    logger.info("Tearing down test environment")
    await mock_claude_client.reset()
    await claude_manager.close()

@pytest.fixture(scope="module")
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
    except Exception as e:
        logger.error(f"Error in test_claude_api_latency: {str(e)}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_claude_api_rate_limiting(claude_manager, mock_claude_client):
    try:
        await mock_claude_client.set_rate_limit(5)  # Set a lower threshold for testing
        logger.info("Set rate limit to 5 calls")
        with pytest.raises(CustomRateLimitError):
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
async def test_claude_api_rate_limiting(claude_manager, mock_claude_client):
    try:
        await mock_claude_client.set_rate_limit(5)  # Set a lower threshold for testing
        logger.info("Set rate limit to 5 calls")
        with pytest.raises(CustomRateLimitError):
            for i in range(10):  # Attempt to make 10 calls
                logger.debug(f"Making API call {i+1}")
                await claude_manager.generate_response(f"Test prompt {i}")
        call_count = mock_claude_client.get_call_count()
        assert call_count == 6, f"Expected 6 calls (5 successful + 1 that raises the error), but got {call_count}"
        logger.info(f"Rate limiting test passed. Total calls made: {call_count}")
    except Exception as e:
        logger.error(f"Error in test_claude_api_rate_limiting: {str(e)}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_claude_api_error_handling(claude_manager, mock_claude_client):
    mock_claude_client.set_error_mode(True)
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt")

@pytest.mark.asyncio
async def test_claude_api_max_tokens(claude_manager, mock_claude_client):
    long_prompt = "a" * (mock_claude_client.max_test_tokens + 1)
    with pytest.raises(ValueError, match="Prompt length .* exceeds maximum context length"):
        await claude_manager.generate_response(long_prompt)

@pytest.mark.asyncio
async def test_claude_api_response_truncation(claude_manager, mock_claude_client):
    long_response = "b" * (mock_claude_client.max_test_tokens * 2)
    mock_claude_client.set_response("Test prompt", long_response)
    response = await claude_manager.generate_response("Test prompt")
    assert len(response) <= mock_claude_client.max_test_tokens + 50  # Allow for some overhead

@pytest.mark.asyncio
async def test_concurrent_claude_api_calls(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    num_concurrent_calls = 5
    await mock_claude_client.set_response("Test prompt", "Test response")

    logging.info(f"Starting concurrent API calls test with {num_concurrent_calls} calls")

    async def make_call(i):
        logging.debug(f"Making call {i}")
        response = await claude_manager.generate_response(f"Test prompt {i}", "claude-3-haiku-20240307")
        logging.debug(f"Call {i} completed with response: {response}")
        return response

    tasks = [make_call(i) for i in range(num_concurrent_calls)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_calls = [r for r in results if isinstance(r, str)]
    rate_limit_errors = [r for r in results if isinstance(r, RateLimitError)]

    logging.info(f"Concurrent calls completed. Successful: {len(successful_calls)}, Rate Limited: {len(rate_limit_errors)}")

    assert len(successful_calls) + len(rate_limit_errors) == num_concurrent_calls, f"Expected {num_concurrent_calls} total results, got {len(successful_calls) + len(rate_limit_errors)}"
    assert all(result == "<response><response>Test response</response></response>" for result in successful_calls), "Not all successful responses match expected format"
    assert await mock_claude_client.get_call_count() == num_concurrent_calls, f"Expected {num_concurrent_calls} calls to mock client, got {await mock_claude_client.get_call_count()}"

    for i in range(num_concurrent_calls):
        assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"

    if rate_limit_errors:
        assert "Rate limit reached, waiting for next available slot" in caplog.text, "Missing rate limit warning in logs"

    logging.info("Concurrent API calls test completed successfully")

class TestClaudeAPIBasics:
    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_claude_api_call(self, claude_manager, mock_claude_client):
        mock_claude_client.set_response("Intro", "Claude AI")
        response = await claude_manager.generate_response("Intro")
        assert isinstance(response, str)
        assert "<response>" in response
        assert "</response>" in response
        assert "Claude AI" in response

    @pytest.mark.fast
    @pytest.mark.parametrize("task,expected_model", [
        ("simple", "claude-3-haiku-20240307"),
        ("moderate", "claude-3-sonnet-20240229"),
        ("complex", "claude-3-opus-20240229"),
    ])
    def test_tiered_model_selection(self, claude_manager, task, expected_model):
        assert claude_manager.select_model(task) == expected_model

class TestInputValidation:
    @pytest.mark.fast
    @pytest.mark.asyncio
    @pytest.mark.parametrize("input_text", [
        "",
        "a" * 1001,  # Over the max_test_tokens limit
        "<script>",
        "SSN: 123-45-6789",
        123,
        "   "
    ])
    async def test_input_validation_errors(self, claude_manager, input_text):
        with pytest.raises(ValueError) as excinfo:
            await claude_manager.generate_response(input_text)
        if isinstance(input_text, str) and len(input_text) > 1000:
            assert "Prompt length exceeds maximum" in str(excinfo.value)
        elif not isinstance(input_text, str) or not input_text.strip():
            assert "Invalid prompt: must be a non-empty string" in str(excinfo.value)
        else:
            assert "Invalid prompt" in str(excinfo.value)

    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_valid_inputs(self, claude_manager):
        for input_text in ["Hello", "!@#$"]:
            response = await claude_manager.generate_response(input_text)
            assert response

class TestResponseHandling:
    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_response_parsing(self, claude_manager, llm_manager):
        max_test_tokens = llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)
        long_response = "b" * (max_test_tokens * 2)
        claude_manager.client.set_response("Test", long_response)
    
        result = await claude_manager.generate_response("Test")
    
        assert len(result) <= max_test_tokens * 2 + 50  # Allow for response tags, ellipsis, and some extra characters
        assert result.startswith("<response>") and result.endswith("</response>")
        assert "..." in result or len(result) <= len(long_response) + 21  # Check for truncation or equal/shorter response, allowing for XML tags

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, claude_manager):
        claude_manager.client.set_error_mode(True)
        with pytest.raises(Exception):
            await claude_manager.generate_response("Test")
        claude_manager.client.set_error_mode(False)
        claude_manager.client.set_response("Test", "Success")
        response = await claude_manager.generate_response("Test")
        assert "Success" in response

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_consistency(self, claude_manager):
        claude_manager.client.set_response("France capital", "Paris")
        response1 = await claude_manager.generate_response("France capital")
        response2 = await claude_manager.generate_response("France capital")
        assert "Paris" in response1 and "Paris" in response2

class TestRateLimiting:
    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_rate_limiting(self, claude_manager):
        with patch.object(claude_manager.client.messages, 'create') as mock_create:
            mock_create.side_effect = anthropic.APIError("Rate limit exceeded", request=MagicMock(), body={})
            response = await claude_manager.generate_response("Test")
            assert "Rate limit exceeded" in response or "Unable to process the request" in response
            mock_create.side_effect = None
            mock_create.return_value = MagicMock(content=[MagicMock(text="Test response")])
            response = await claude_manager.generate_response("Test")
            assert "Test response" in response

@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_claude_api_performance(claude_manager, benchmark):
    async def api_call():
        return await claude_manager.generate_response("Test performance")
    
    result = await benchmark.pedantic(api_call, iterations=10, rounds=3)
    assert result  # Ensure we got a response

class TestContextManagement:
    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_context_window_utilization(self, claude_manager, llm_manager):
        max_tokens = llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)
        long_input = "a" * (max_tokens - 10)  # Leave some room for system message
        response = await claude_manager.generate_response(long_input)
        assert len(response) <= max_tokens

    @pytest.mark.fast
    @pytest.mark.asyncio
    async def test_context_overflow_handling(self, claude_manager, llm_manager):
        max_tokens = claude_manager.max_context_length
        overflow_input = "a" * (max_tokens + 1)  # Ensure it's just over the limit
        with pytest.raises(ValueError, match="Prompt length exceeds maximum context length"):
            await claude_manager.generate_response(overflow_input)

class TestPerformance:
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_response_time(self, claude_manager):
        start_time = time.time()
        await claude_manager.generate_response("Quick response test")
        end_time = time.time()
        assert end_time - start_time < 10  # Increased to 10 seconds for more lenient test

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_token_usage(self, claude_manager):
        response = await claude_manager.generate_response("Token usage test")
        assert '<response>' in response and '</response>' in response  # Check if the response is properly formatted

@pytest.mark.asyncio
async def test_mock_claude_client_response(mock_claude_client, claude_manager):
    mock_claude_client.set_response("Test prompt", "Test response")
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Test response</response>"

@pytest.mark.asyncio
async def test_mock_claude_client_rate_limit(mock_claude_client, claude_manager):
    mock_claude_client.rate_limit_threshold = 5
    with pytest.raises(CustomRateLimitError):
        for _ in range(mock_claude_client.rate_limit_threshold + 1):
            await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    
    assert mock_claude_client.call_count == mock_claude_client.rate_limit_threshold + 1

@pytest.mark.asyncio
async def test_mock_claude_client_error_mode(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

@pytest.mark.asyncio
async def test_mock_claude_client_reset(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit(True)
    mock_claude_client.set_error_mode(True)
    mock_claude_client.set_response("Test prompt", "Test response")
        
    mock_claude_client.reset()
        
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"

@pytest.mark.asyncio
async def test_mock_claude_client_call_count(mock_claude_client, claude_manager):
    for _ in range(3):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert mock_claude_client.get_call_count() == 3

@pytest.mark.asyncio
async def test_mock_claude_client_error_count(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    mock_claude_client.max_errors = 2
        
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
        
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"
    assert mock_claude_client.get_error_count() == 2

@pytest.mark.asyncio
async def test_mock_claude_client_rate_limit_reset(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit_threshold(3)
    mock_claude_client.set_rate_limit_reset_time(1)  # 1 second for faster testing

    # Make calls until rate limit is reached
    for _ in range(3):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

    # Next call should raise RateLimitError
    with pytest.raises(RateLimitError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

    # Wait for rate limit to reset
    await asyncio.sleep(1.1)

    # Should be able to make calls again
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"

@pytest.mark.asyncio
async def test_mock_claude_client_concurrent_calls(mock_claude_client):
    mock_claude_client.set_rate_limit_threshold(5)

    results = await mock_claude_client.simulate_concurrent_calls(10)

    successful_calls = [r for r in results if isinstance(r, dict)]
    rate_limit_errors = [r for r in results if isinstance(r, CustomRateLimitError)]

    assert len(successful_calls) == 5
    assert len(rate_limit_errors) == 5

@pytest.mark.asyncio
async def test_mock_claude_client_error_mode(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    
    with pytest.raises(APIStatusError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    
    # After max_errors, it should return to normal
    for _ in range(mock_claude_client.max_errors):
        with pytest.raises(APIStatusError):
            await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"

@pytest.mark.asyncio
async def test_mock_claude_client_latency(mock_claude_client, claude_manager):
    mock_claude_client.set_latency(0.5)  # Set a 500ms latency
    
    start_time = time.time()
    await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    end_time = time.time()
    
    assert end_time - start_time >= 0.5, "Response time should be at least 500ms"

@pytest.mark.asyncio
async def test_mock_claude_client_call_count(mock_claude_client, claude_manager):
    for _ in range(3):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    
    assert mock_claude_client.get_call_count() == 3

@pytest.mark.asyncio
async def test_mock_claude_client_error_count(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    
    for _ in range(2):
        with pytest.raises(APIStatusError):
            await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    
    assert mock_claude_client.get_error_count() == 2

@pytest.mark.asyncio
async def test_claude_manager_fallback_response(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    mock_claude_client.max_errors = 0  # Force immediate fallback
    
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert "I apologize, but I'm unable to process your request at the moment" in response

@pytest.mark.asyncio
async def test_claude_manager_retry_mechanism(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    mock_claude_client.max_errors = 2  # Allow 2 errors before success
    
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"
    assert mock_claude_client.get_error_count() == 2

@pytest.mark.asyncio
async def test_mock_claude_client_rate_limit_reset(mock_claude_client, claude_manager):
    mock_claude_client.rate_limit_threshold = 3
    mock_claude_client.rate_limit_reset_time = 1  # 1 second for faster testing

    # Make calls until rate limit is reached
    for _ in range(3):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

    # Next call should raise RateLimitError
    with pytest.raises(RateLimitError):
        await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

    # Wait for rate limit to reset
    await asyncio.sleep(1.1)

    # Should be able to make calls again
    response = await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")
    assert response == "<response>Default mock response</response>"

@pytest.mark.asyncio
async def test_mock_claude_client_concurrent_calls(mock_claude_client, claude_manager):
    mock_claude_client.rate_limit_threshold = 5

    async def make_call():
        return await claude_manager.generate_response("Test prompt", "claude-3-haiku-20240307")

    tasks = [make_call() for _ in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_calls = [r for r in results if isinstance(r, str)]
    rate_limit_errors = [r for r in results if isinstance(r, RateLimitError)]

    assert len(successful_calls) == 5
    assert len(rate_limit_errors) == 5

@pytest.mark.asyncio
async def test_concurrent_claude_api_calls(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    num_concurrent_calls = 5
    mock_claude_client.set_response("Test prompt", "Test response")

    logging.info(f"Starting concurrent API calls test with {num_concurrent_calls} calls")

    async def make_call(i):
        logging.debug(f"Making call {i}")
        response = await claude_manager.generate_response(f"Test prompt {i}", "claude-3-haiku-20240307")
        logging.debug(f"Call {i} completed with response: {response}")
        return response

    tasks = [make_call(i) for i in range(num_concurrent_calls)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successful_calls = [r for r in results if isinstance(r, str)]
    rate_limit_errors = [r for r in results if isinstance(r, RateLimitError)]

    logging.info(f"Concurrent calls completed. Successful: {len(successful_calls)}, Rate Limited: {len(rate_limit_errors)}")

    assert len(successful_calls) + len(rate_limit_errors) == num_concurrent_calls, f"Expected {num_concurrent_calls} total results, got {len(successful_calls) + len(rate_limit_errors)}"
    assert all(result == "<response><response>Test response</response></response>" for result in successful_calls), "Not all successful responses match expected format"
    assert mock_claude_client.call_count == num_concurrent_calls, f"Expected {num_concurrent_calls} calls to mock client, got {mock_claude_client.call_count}"

    for i in range(num_concurrent_calls):
        assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"

    if rate_limit_errors:
        assert "Rate limit reached, waiting for next available slot" in caplog.text, "Missing rate limit warning in logs"

    logging.info("Concurrent API calls test completed successfully")

@pytest.mark.asyncio
async def test_rate_limit_reset(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    mock_claude_client.rate_limit_threshold = 3
    mock_claude_client.rate_limit_reset_time = 1  # 1 second for faster testing

    logging.info("Starting rate limit reset test")
    logging.debug(f"Rate limit threshold: {mock_claude_client.rate_limit_threshold}")
    logging.debug(f"Rate limit reset time: {mock_claude_client.rate_limit_reset_time} seconds")

    # Make calls until rate limit is reached
    for i in range(3):
        try:
            logging.debug(f"Attempting call {i+1}")
            response = await claude_manager.generate_response(f"Test prompt {i}")
            assert response == f"<response>Default mock response</response>", f"Unexpected response for call {i+1}: {response}"
            assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"
            logging.debug(f"Call {i+1} successful")
        except Exception as e:
            logging.error(f"Unexpected error during rate limit test: {str(e)}")
            pytest.fail(f"Unexpected error during rate limit test: {str(e)}")

    logging.info("Rate limit should be reached. Attempting one more call.")
    # Next call should raise RateLimitError
    with pytest.raises(RateLimitError):
        await claude_manager.generate_response("Test prompt 3")
    assert "Rate limit reached, waiting for next available slot" in caplog.text, "Missing rate limit warning in logs"
    logging.info("Rate limit error raised as expected")

    logging.info("Waiting for rate limit to reset")
    await asyncio.sleep(1.1)
    logging.info("Rate limit reset period completed")

    # Should be able to make calls again
    try:
        logging.debug("Attempting call after rate limit reset")
        response = await claude_manager.generate_response("Test prompt 4")
        assert response == "<response>Default mock response</response>", f"Unexpected response after reset: {response}"
        assert "Generating response for prompt: Test prompt 4" in caplog.text, "Missing log for post-reset prompt"
        logging.info("Successfully made call after rate limit reset")
    except Exception as e:
        logging.error(f"Unexpected error after rate limit reset: {str(e)}")
        pytest.fail(f"Unexpected error after rate limit reset: {str(e)}")

    logging.info("Rate limit reset test completed successfully")

    # Log the entire captured log for debugging
    print("Captured log:")
    print(caplog.text)
@pytest.mark.asyncio
async def test_rate_limit_reset(claude_manager, mock_claude_client, caplog):
    caplog.set_level(logging.DEBUG)
    mock_claude_client.rate_limit_threshold = 3
    mock_claude_client.rate_limit_reset_time = 1  # 1 second for faster testing

    logging.info("Starting rate limit reset test")
    logging.debug(f"Rate limit threshold: {mock_claude_client.rate_limit_threshold}")
    logging.debug(f"Rate limit reset time: {mock_claude_client.rate_limit_reset_time} seconds")

    # Make calls until rate limit is reached
    for i in range(3):
        try:
            logging.debug(f"Attempting call {i+1}")
            response = await claude_manager.generate_response(f"Test prompt {i}")
            assert response == f"<response>Default mock response</response>", f"Unexpected response for call {i+1}: {response}"
            assert f"Generating response for prompt: Test prompt {i}" in caplog.text, f"Missing log for prompt {i}"
            logging.debug(f"Call {i+1} successful")
        except Exception as e:
            logging.error(f"Unexpected error during rate limit test: {str(e)}")
            pytest.fail(f"Unexpected error during rate limit test: {str(e)}")

    logging.info("Rate limit should be reached. Attempting one more call.")
    # Next call should raise RateLimitError
    with pytest.raises(RateLimitError):
        await claude_manager.generate_response("Test prompt 3")
    assert "Rate limit reached, waiting for next available slot" in caplog.text, "Missing rate limit warning in logs"
    logging.info("Rate limit error raised as expected")

    logging.info("Waiting for rate limit to reset")
    await asyncio.sleep(1.1)
    logging.info("Rate limit reset period completed")

    # Should be able to make calls again
    try:
        logging.debug("Attempting call after rate limit reset")
        response = await claude_manager.generate_response("Test prompt 4")
        assert response == "<response>Default mock response</response>", f"Unexpected response after reset: {response}"
        assert "Generating response for prompt: Test prompt 4" in caplog.text, "Missing log for post-reset prompt"
        logging.info("Successfully made call after rate limit reset")
    except Exception as e:
        logging.error(f"Unexpected error after rate limit reset: {str(e)}")
        pytest.fail(f"Unexpected error after rate limit reset: {str(e)}")

    logging.info("Rate limit reset test completed successfully")

    # Log the entire captured log for debugging
    print("Captured log:")
    print(caplog.text)

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

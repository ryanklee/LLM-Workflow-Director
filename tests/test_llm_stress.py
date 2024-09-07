import pytest
import asyncio
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient
from src.exceptions import RateLimitError

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

@pytest.mark.asyncio
async def test_llm_stress(claude_manager):
    num_requests = 100
    max_concurrent = 10

    async def make_request(i):
        prompt = f"Stress test request {i}"
        try:
            response = await claude_manager.generate_response(prompt)
            assert response, f"Empty response for request {i}"
            return response
        except RateLimitError:
            return "Rate limited"

    tasks = [make_request(i) for i in range(num_requests)]
    responses = await asyncio.gather(*tasks)

    assert len(responses) == num_requests, f"Expected {num_requests} responses, got {len(responses)}"

    successful_responses = [r for r in responses if r != "Rate limited"]
    rate_limited_responses = [r for r in responses if r == "Rate limited"]

    print(f"Successful responses: {len(successful_responses)}")
    print(f"Rate limited responses: {len(rate_limited_responses)}")

    assert len(successful_responses) > 0, "No successful responses received"
    assert len(rate_limited_responses) > 0, "No rate limiting occurred during stress test"

@pytest.mark.asyncio
@pytest.mark.slow
async def test_llm_extended_stress(claude_manager):
    num_requests = 1000
    max_concurrent = 50

    async def make_request(i):
        prompt = f"Extended stress test request {i}"
        try:
            response = await claude_manager.generate_response(prompt)
            assert response, f"Empty response for request {i}"
            return response
        except RateLimitError:
            return "Rate limited"

    tasks = [make_request(i) for i in range(num_requests)]
    responses = await asyncio.gather(*tasks)

    assert len(responses) == num_requests, f"Expected {num_requests} responses, got {len(responses)}"

    successful_responses = [r for r in responses if r != "Rate limited"]
    rate_limited_responses = [r for r in responses if r == "Rate limited"]

    print(f"Successful responses: {len(successful_responses)}")
    print(f"Rate limited responses: {len(rate_limited_responses)}")

    assert len(successful_responses) > 0, "No successful responses received"
    assert len(rate_limited_responses) > 0, "No rate limiting occurred during extended stress test"

@pytest.mark.asyncio
async def test_rate_limit_recovery(claude_manager):
    num_requests = 20
    claude_manager.client.set_rate_limit_threshold(10)
    claude_manager.client.set_rate_limit_reset_time(2)  # 2 seconds for faster testing

    async def make_request(i):
        prompt = f"Rate limit recovery test request {i}"
        try:
            response = await claude_manager.generate_response(prompt)
            return "Success"
        except RateLimitError:
            return "Rate limited"

    # First batch of requests
    tasks = [make_request(i) for i in range(num_requests)]
    responses = await asyncio.gather(*tasks)

    rate_limited_count = responses.count("Rate limited")
    assert rate_limited_count > 0, "No rate limiting occurred in the first batch"

    # Wait for rate limit to reset
    await asyncio.sleep(2.1)

    # Second batch of requests
    tasks = [make_request(i) for i in range(num_requests)]
    responses = await asyncio.gather(*tasks)

    success_count = responses.count("Success")
    assert success_count > 0, "No successful requests after rate limit reset"

@pytest.mark.asyncio
async def test_concurrent_request_handling(claude_manager):
    num_concurrent_requests = 50
    claude_manager.client.set_rate_limit_threshold(30)

    async def make_request(i):
        prompt = f"Concurrent request {i}"
        try:
            response = await claude_manager.generate_response(prompt)
            return "Success"
        except RateLimitError:
            return "Rate limited"

    tasks = [make_request(i) for i in range(num_concurrent_requests)]
    responses = await asyncio.gather(*tasks)

    success_count = responses.count("Success")
    rate_limited_count = responses.count("Rate limited")

    print(f"Successful concurrent requests: {success_count}")
    print(f"Rate limited concurrent requests: {rate_limited_count}")

    assert success_count > 0, "No successful concurrent requests"
    assert rate_limited_count > 0, "No rate limiting occurred during concurrent requests"
    assert success_count + rate_limited_count == num_concurrent_requests, "Unexpected response count"
import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

@pytest.mark.stress
async def test_llm_stress_regular(claude_manager):
    """
    Regular stress test for LLM-related functionality.
    Sends 100 concurrent requests to the LLM.
    """
    tasks = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        for _ in range(100):
            tasks.append(executor.submit(claude_manager.generate_response, "This is a stress test."))
        await asyncio.gather(*[asyncio.to_thread(task.result) for task in tasks])

@pytest.mark.stress
@pytest.mark.slow
async def test_llm_stress_extended(claude_manager):
    """
    Extended stress test for LLM-related functionality.
    Sends 1000 concurrent requests to the LLM.
    """
    tasks = []
    with ThreadPoolExecutor(max_workers=1000) as executor:
        for _ in range(1000):
            tasks.append(executor.submit(claude_manager.generate_response, "This is an extended stress test."))
        await asyncio.gather(*[asyncio.to_thread(task.result) for task in tasks])

@pytest.mark.asyncio
async def test_concurrent_request_handling(claude_manager):
    async def make_request():
        return await claude_manager.generate_response("Hello, how are you?")
    
    tasks = [make_request() for _ in range(10)]
    responses = await asyncio.gather(*tasks)
    
    assert len(responses) == 10
    for response in responses:
        assert isinstance(response, str)
        assert len(response) > 0

@pytest.mark.asyncio
async def test_sustained_load_performance(claude_manager):
    start_time = asyncio.get_event_loop().time()
    request_count = 0
    error_count = 0
    
    async def make_request():
        try:
            response = await claude_manager.generate_response("Tell me a short joke.")
            assert isinstance(response, str)
            assert len(response) > 0
            return True
        except Exception:
            return False
    
    while asyncio.get_event_loop().time() - start_time < 300:  # Run for 5 minutes
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        request_count += 10
        error_count += results.count(False)
        
        # Check system stability every minute
        if (asyncio.get_event_loop().time() - start_time) % 60 < 1:
            error_rate = error_count / request_count
            print(f"Current error rate: {error_rate:.2%}")
            assert error_rate < 0.05, f"Error rate {error_rate:.2%} exceeds 5% threshold"
    
    print(f"Processed {request_count} requests in 5 minutes")
    assert request_count > 1000, f"Expected to process more than 1000 requests, but processed {request_count}"
    
    final_error_rate = error_count / request_count
    assert final_error_rate < 0.01, f"Final error rate {final_error_rate:.2%} exceeds 1% threshold"

@pytest.mark.asyncio
async def test_recovery_time(claude_manager):
    # Simulate high load
    high_load_tasks = [claude_manager.generate_response("Tell me a long story.") for _ in range(20)]
    await asyncio.gather(*high_load_tasks)
    
    # Measure recovery time
    start_time = asyncio.get_event_loop().time()
    response = await claude_manager.generate_response("Hello, how are you?")
    recovery_time = asyncio.get_event_loop().time() - start_time
    
    print(f"Recovery time after high load: {recovery_time:.2f} seconds")
    assert recovery_time < 5, f"Recovery time {recovery_time:.2f}s exceeds 5 seconds threshold"
import asyncio
import pytest
from unittest.mock import Mock
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.mark.asyncio
async def test_llm_stress_regular():
    mock_client = MockClaudeClient()
    claude_manager = ClaudeManager(client=mock_client)
    
    async def make_request():
        response = await claude_manager.generate_response("Test prompt")
        assert response is not None

    tasks = [make_request() for _ in range(100)]
    await asyncio.gather(*tasks)

@pytest.mark.asyncio
@pytest.mark.slow
async def test_llm_stress_extended():
    mock_client = MockClaudeClient()
    claude_manager = ClaudeManager(client=mock_client)
    
    async def make_request():
        response = await claude_manager.generate_response("Test prompt")
        assert response is not None

    tasks = [make_request() for _ in range(1000)]
    await asyncio.gather(*tasks)

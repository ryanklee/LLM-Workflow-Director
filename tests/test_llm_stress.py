import pytest
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient
import concurrent.futures

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

def test_llm_stress(claude_manager):
    num_requests = 100
    max_workers = 10

    def make_request(i):
        prompt = f"Stress test request {i}"
        response = claude_manager.generate_response(prompt)
        assert response, f"Empty response for request {i}"
        return response

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert len(responses) == num_requests, f"Expected {num_requests} responses, got {len(responses)}"

    # Check for rate limiting
    rate_limited = claude_manager.client.rate_limit_reached
    assert not rate_limited, "Rate limit was reached during stress test"

@pytest.mark.slow
def test_llm_extended_stress(claude_manager):
    num_requests = 1000
    max_workers = 20

    def make_request(i):
        prompt = f"Extended stress test request {i}"
        response = claude_manager.generate_response(prompt)
        assert response, f"Empty response for request {i}"
        return response

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        responses = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert len(responses) == num_requests, f"Expected {num_requests} responses, got {len(responses)}"

    # Check for rate limiting
    rate_limited = claude_manager.client.rate_limit_reached
    assert not rate_limited, "Rate limit was reached during extended stress test"
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

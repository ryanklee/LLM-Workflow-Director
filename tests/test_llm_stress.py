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

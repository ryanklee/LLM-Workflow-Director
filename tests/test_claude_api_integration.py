import pytest
import tenacity
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient
from src.llm_manager import LLMManager

@pytest.fixture
def mock_claude_client():
    return MockClaudeClient()

@pytest.fixture
def claude_manager(mock_claude_client):
    return ClaudeManager(client=mock_claude_client)

@pytest.fixture
def llm_manager():
    return LLMManager()

@pytest.fixture(scope="module")
def cached_responses(request):
    cache = {}
    def _cached_response(prompt, response):
        if prompt not in cache:
            cache[prompt] = response
        return cache[prompt]
    request.addfinalizer(cache.clear)
    return _cached_response

class TestClaudeAPIBasics:
    @pytest.mark.fast
    def test_claude_api_call(self, claude_manager, mock_claude_client):
        mock_claude_client.set_response("Intro", "Claude AI")
        response = claude_manager.generate_response("Intro")
        assert "Claude" in response and "AI" in response

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
    @pytest.mark.parametrize("input_text", [
        "",
        "a" * 101,  # Just over the max_test_tokens limit
        "<script>",
        "SSN: 123-45-6789",
        123,
        "   "
    ])
    def test_input_validation_errors(self, claude_manager, input_text):
        with pytest.raises(ValueError) as excinfo:
            claude_manager.generate_response(input_text)
        if isinstance(input_text, str) and len(input_text) > 100:
            assert "Invalid prompt length: exceeds" in str(excinfo.value)
        else:
            assert "Invalid prompt: must be a non-empty string" in str(excinfo.value)

    @pytest.mark.fast
    def test_valid_inputs(self, claude_manager):
        for input_text in ["Hello", "!@#$"]:
            response = claude_manager.generate_response(input_text)
            assert response

class TestResponseHandling:
    @pytest.mark.fast
    def test_response_parsing(self, claude_manager, llm_manager):
        max_test_tokens = llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)
        long_response = "b" * (max_test_tokens * 2)
        claude_manager.client.set_response("Test", long_response)
        
        result = claude_manager.generate_response("Test")
        
        assert len(result) == max_test_tokens + 3  # +3 for the "..."
        assert result.endswith("...")

    @pytest.mark.slow
    def test_retry_mechanism(self, claude_manager):
        claude_manager.client.set_error_mode(True)
        with pytest.raises(Exception):
            claude_manager.generate_response("Test")
        claude_manager.client.set_error_mode(False)
        claude_manager.client.set_response("Test", "Success")
        response = claude_manager.generate_response("Test")
        assert "Success" in response

    @pytest.mark.slow
    def test_consistency(self, claude_manager):
        claude_manager.client.set_response("France capital", "Paris")
        response1 = claude_manager.generate_response("France capital")
        response2 = claude_manager.generate_response("France capital")
        assert "Paris" in response1 and "Paris" in response2

class TestRateLimiting:
    @pytest.mark.fast
    def test_rate_limiting(self, claude_manager):
        claude_manager.client.set_rate_limit(True)
        with pytest.raises(tenacity.RetryError):
            claude_manager.generate_response("Test")
        claude_manager.client.set_rate_limit(False)
        assert claude_manager.generate_response("Test")

@pytest.mark.benchmark
def test_claude_api_performance(claude_manager, benchmark):
    def api_call():
        return claude_manager.generate_response("Test performance")
    
    result = benchmark(api_call)
    assert result  # Ensure we got a response

class TestContextManagement:
    @pytest.mark.fast
    def test_context_window_utilization(self, claude_manager, llm_manager):
        max_tokens = llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)
        long_input = "a" * (max_tokens - 10)  # Leave some room for system message
        response = claude_manager.generate_response(long_input)
        assert len(response) <= max_tokens

    @pytest.mark.fast
    def test_context_overflow_handling(self, claude_manager, llm_manager):
        max_tokens = llm_manager.config.get('test_settings', {}).get('max_test_tokens', 100)
        overflow_input = "a" * (max_tokens + 50)
        with pytest.raises(ValueError, match="Invalid prompt length"):
            claude_manager.generate_response(overflow_input)

class TestPerformance:
    @pytest.mark.benchmark
    def test_response_time(self, claude_manager, benchmark):
        result = benchmark(claude_manager.generate_response, "Quick response test")
        assert result  # Ensure we got a response

    @pytest.mark.benchmark
    def test_token_usage(self, claude_manager, benchmark):
        def token_usage_test():
            response = claude_manager.generate_response("Token usage test")
            return len(response.split())  # Rough estimate of token count
        
        result = benchmark(token_usage_test)
        assert 0 < result <= 100  # Assuming max_tokens is 100

def test_mock_claude_client_response(mock_claude_client, claude_manager):
    mock_claude_client.set_response("Test prompt", "Test response")
    response = claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert response == "<response>Test response</response>"

def test_mock_claude_client_rate_limit(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit(True)
    with pytest.raises(tenacity.RetryError) as excinfo:
        claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert "Rate limit exceeded" in str(excinfo.value)

def test_mock_claude_client_error_mode(mock_claude_client, claude_manager):
    mock_claude_client.set_error_mode(True)
    with pytest.raises(tenacity.RetryError) as excinfo:
        claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert "API error" in str(excinfo.value)

def test_mock_claude_client_reset(mock_claude_client, claude_manager):
    mock_claude_client.set_rate_limit(True)
    mock_claude_client.set_error_mode(True)
    mock_claude_client.set_response("Test prompt", "Test response")
    
    mock_claude_client.reset()
    
    response = claude_manager.get_completion("Test prompt", "claude-3-haiku-20240307", 100)
    assert response == "Default mock response"

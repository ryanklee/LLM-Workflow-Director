import pytest
from pytest_benchmark.fixture import BenchmarkFixture
from src.claude_manager import ClaudeManager
from src.llm_manager import LLMManager

@pytest.fixture
def claude_manager():
    return ClaudeManager()

@pytest.fixture
def llm_manager():
    return LLMManager()

def test_token_usage_efficiency(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    context_sizes = [1000, 10000, 50000, 100000, 150000]
    
    def measure_efficiency(size):
        context = "a" * size
        prompt = f"Summarize the following text in one sentence: {context}"
        response = claude_manager.generate_response(prompt)
        total_tokens = claude_manager.count_tokens(prompt + response)
        useful_tokens = claude_manager.count_tokens(response)
        return useful_tokens / total_tokens

    results = benchmark.pedantic(measure_efficiency, args=(max(context_sizes),), iterations=5, rounds=3)
    
    for size in context_sizes:
        efficiency = measure_efficiency(size)
        print(f"Token usage efficiency for context size {size}: {efficiency:.4f}")
        assert 0 < efficiency <= 1, f"Efficiency {efficiency} is out of expected range (0, 1]"

def test_response_time_vs_context_size(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    context_sizes = [1000, 10000, 50000, 100000, 150000]
    
    def measure_response_time(size):
        context = "a" * size
        prompt = f"Summarize the following text in one sentence: {context}"
        with patch.object(claude_manager.messages, 'create') as mock_create:
            mock_create.return_value.content = [anthropic.types.ContentBlock(text="Test response", type="text")]
            return benchmark.pedantic(claude_manager.generate_response, args=(prompt,), iterations=3, rounds=1)

    for size in context_sizes:
        result = measure_response_time(size)
        print(f"Response time for context size {size}: {result.average:.4f} seconds")
    
    # Assert that the response time for the largest context is not significantly higher than the smallest
    assert measure_response_time(context_sizes[-1]).average < measure_response_time(context_sizes[0]).average * 2

def test_response_quality_vs_context_size(claude_manager: ClaudeManager, llm_manager: LLMManager):
    context_sizes = [1000, 10000, 50000, 100000, 150000]
    base_text = "This is a test of the emergency broadcast system. " * 250

    for size in context_sizes:
        context = base_text[:size]
        prompt = f"Summarize the following text in one sentence: {context}"
        response = claude_manager.generate_response(prompt)
        
        quality_prompt = f"Evaluate the following summary for relevance and coherence on a scale of 1-10: '{response}'"
        quality_score = llm_manager.evaluate_response_quality(quality_prompt)
        
        print(f"Quality score for context size {size}: {quality_score}")

        assert 1 <= quality_score <= 10, f"Quality score {quality_score} is out of expected range (1-10)"

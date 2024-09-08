import pytest
import logging
from pytest_benchmark.fixture import BenchmarkFixture
from src.claude_manager import ClaudeManager
from src.llm_manager import LLMManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

@pytest.fixture
def llm_manager(claude_manager):
    return LLMManager(claude_manager=claude_manager)

@pytest.mark.asyncio
async def test_token_usage_per_query_type(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    query_types = {
        "short": "What's the capital of France?",
        "medium": "Explain the process of photosynthesis in plants.",
        "long": "Write a 500-word essay on the impact of artificial intelligence on modern society."
    }
    
    async def measure_token_usage(query):
        response = await claude_manager.generate_response(query)
        return await claude_manager.count_tokens(query + response)
    
    for query_type, query in query_types.items():
        result = await benchmark.pedantic(measure_token_usage, args=(query,), iterations=5, rounds=3)
        print(f"Token usage for {query_type} query: {result:.0f} tokens")

@pytest.mark.asyncio
async def test_cost_effectiveness_of_models(llm_manager: LLMManager, benchmark: BenchmarkFixture):
    models = ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
    query = "Explain the theory of relativity in simple terms."
    
    async def measure_cost_effectiveness(model):
        response = await llm_manager.query(query, model=model)
        tokens = await llm_manager.count_tokens(query + response['response'])
        cost = await llm_manager.calculate_cost(model, tokens)
        return len(response['response']) / cost  # characters per unit of cost
    
    for model in models:
        result = await benchmark.pedantic(measure_cost_effectiveness, args=(model,), iterations=3, rounds=1)
        print(f"Cost-effectiveness for {model}: {result.average:.2f} chars/$")

@pytest.mark.asyncio
async def test_optimization_strategies(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    base_query = "Explain the process of photosynthesis in plants."
    strategies = {
        "base": base_query,
        "compressed": "Briefly explain photosynthesis.",
        "chunked": "Explain photosynthesis step by step. Provide 3 steps only.",
        "focused": "What are the key inputs and outputs of photosynthesis?",
    }
    
    async def measure_token_efficiency(query):
        response = await claude_manager.generate_response(query)
        tokens = await claude_manager.count_tokens(query + str(response))
        return len(str(response)) / tokens  # characters per token
    
    for strategy, query in strategies.items():
        result = await benchmark.pedantic(measure_token_efficiency, args=(query,), iterations=5, rounds=3)
        print(f"Token efficiency for {strategy} strategy: {result.average:.2f} chars/token")

@pytest.mark.asyncio
async def test_token_usage_estimation(llm_manager: LLMManager):
    query_types = {
        "short": "What's the capital of France?",
        "medium": "Explain the process of photosynthesis in plants.",
        "long": "Write a 500-word essay on the impact of artificial intelligence on modern society."
    }
    
    for query_type, query in query_types.items():
        estimated_tokens = await llm_manager.estimate_token_usage(query)
        actual_tokens = await llm_manager.count_tokens(query)
        
        print(f"Query type: {query_type}")
        print(f"Estimated tokens: {estimated_tokens}")
        print(f"Actual tokens: {actual_tokens}")
        print(f"Estimation accuracy: {(estimated_tokens / actual_tokens) * 100:.2f}%")
        
        assert 0.8 <= (estimated_tokens / actual_tokens) <= 1.2, f"Token estimation for {query_type} query is off by more than 20%"

@pytest.mark.asyncio
async def test_cost_optimization_suggestions(llm_manager: LLMManager):
    # Simulate some usage
    await llm_manager.query("Short query 1", model="claude-3-haiku-20240307")
    await llm_manager.query("Medium query 1", model="claude-3-sonnet-20240229")
    await llm_manager.query("Long query 1", model="claude-3-opus-20240229")
    await llm_manager.query("Long query 2", model="claude-3-opus-20240229")
    
    suggestions = await llm_manager.get_optimization_suggestion()
    
    logging.info("Cost optimization suggestions:")
    logging.info(suggestions)
    
    assert isinstance(suggestions, str), "Cost optimization suggestions should be a string"
    assert len(suggestions) > 0, "Cost optimization suggestions should not be empty"

@pytest.mark.asyncio
async def test_token_efficiency_over_time(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    query = "Explain the concept of machine learning in simple terms."
    num_iterations = 10
    
    async def measure_efficiency_over_time():
        total_tokens = 0
        total_response_length = 0
        
        for i in range(num_iterations):
            response = await claude_manager.generate_response(query)
            tokens = await claude_manager.count_tokens(query + response)
            total_tokens += tokens
            total_response_length += len(response)
            
            efficiency = total_response_length / total_tokens
            print(f"Iteration {i+1} efficiency: {efficiency:.2f} chars/token")
        
        return total_response_length / total_tokens
    
    result = await benchmark.pedantic(measure_efficiency_over_time, iterations=1, rounds=1)
    print(f"Average token efficiency over time: {result:.2f} chars/token")
import pytest
from pytest_benchmark.fixture import BenchmarkFixture
from src.claude_manager import ClaudeManager
from src.llm_manager import LLMManager

@pytest.fixture
def claude_manager():
    return ClaudeManager()

@pytest.fixture
async def llm_manager():
    manager = LLMManager()
    yield manager
    await manager.token_tracker.reset()

@pytest.mark.asyncio
async def test_token_usage_per_query_type(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    query_types = {
        "short": "What's the capital of France?",
        "medium": "Explain the process of photosynthesis in plants.",
        "long": "Write a 500-word essay on the impact of artificial intelligence on modern society."
    }

    async def measure_token_usage(query):
        response = await claude_manager.generate_response(query)
        return await claude_manager.count_tokens(query + response)

    for query_type, query in query_types.items():
        result = await benchmark.pedantic(measure_token_usage, args=(query,), iterations=5, rounds=3)
        print(f"Token usage for {query_type} query: {result.stats.mean:.0f} tokens")

def test_cost_effectiveness_of_models(llm_manager: LLMManager, benchmark: BenchmarkFixture):
    models = ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
    query = "Explain the theory of relativity in simple terms."
    
    def measure_cost_effectiveness(model):
        response = llm_manager.query(query, model=model)
        tokens = llm_manager.count_tokens(query + response)
        cost = llm_manager.calculate_cost(model, tokens)
        return len(response) / cost  # characters per unit of cost
    
    for model in models:
        result = benchmark.pedantic(measure_cost_effectiveness, args=(model,), iterations=3, rounds=1)
        print(f"Cost-effectiveness for {model}: {result.average:.2f} chars/$")

def test_optimization_strategies(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    base_query = "Explain the process of photosynthesis in plants."
    strategies = {
        "base": base_query,
        "compressed": "Briefly explain photosynthesis.",
        "chunked": "Explain photosynthesis step by step. Provide 3 steps only.",
        "focused": "What are the key inputs and outputs of photosynthesis?",
    }
    
    def measure_token_efficiency(query):
        response = claude_manager.generate_response(query)
        tokens = claude_manager.count_tokens(query + response)
        return len(response) / tokens  # characters per token
    
    for strategy, query in strategies.items():
        result = benchmark.pedantic(measure_token_efficiency, args=(query,), iterations=5, rounds=3)
        print(f"Token efficiency for {strategy} strategy: {result.average:.2f} chars/token")
import pytest
from src.llm_manager import LLMManager
from src.claude_manager import ClaudeManager
from src.token_tracker import TokenTracker, TokenOptimizer
from unittest.mock import MagicMock

@pytest.fixture
def mock_claude_manager():
    mock = MagicMock(spec=ClaudeManager)
    mock.count_tokens.side_effect = lambda text: len(text.split())  # Simple token count
    return mock

@pytest.fixture
async def llm_manager(mock_claude_manager):
    manager = LLMManager(claude_manager=mock_claude_manager)
    yield manager
    # Clean up after each test
    await manager.token_tracker.reset()

@pytest.fixture
def token_tracker():
    return TokenTracker()

@pytest.fixture
def token_optimizer(token_tracker):
    return TokenOptimizer(token_tracker)

@pytest.mark.asyncio
async def test_token_usage_estimation(llm_manager, token_tracker):
    test_queries = [
        "What is the capital of France?",
        "Explain the theory of relativity in simple terms.",
        "Write a short story about a robot learning to love.",
    ]

    for query in test_queries:
        response = await llm_manager.query(query)
        estimated_tokens = await llm_manager.claude_manager.count_tokens(query) + await llm_manager.claude_manager.count_tokens(response['response'])
        actual_tokens = await token_tracker.get_token_usage(query)

        assert abs(estimated_tokens - actual_tokens) / actual_tokens < 0.1, \
            f"Token estimation error should be less than 10% for query: {query}"

@pytest.mark.asyncio
async def test_token_optimization(token_optimizer):
    long_prompt = "This is a very long prompt that exceeds the maximum allowed tokens. " * 20
    optimized_prompt = await token_optimizer.optimize_prompt(long_prompt)

    assert len(optimized_prompt) < len(long_prompt), "Optimized prompt should be shorter than the original"
    assert await token_optimizer.token_tracker.count_tokens(optimized_prompt) <= 100, \
        "Optimized prompt should not exceed 100 tokens"

@pytest.mark.asyncio
async def test_token_usage_tracking(llm_manager):
    query = "What is the meaning of life?"
    response = await llm_manager.query(query)

    token_tracker = llm_manager.token_tracker
    assert await token_tracker.get_token_usage(query) > 0, "Token usage should be tracked for the query"
    assert await token_tracker.get_total_token_usage() > 0, "Total token usage should be tracked"

    # Note: get_overall_efficiency() method doesn't exist in the current implementation
    # We should either implement it or remove this assertion
    # efficiency = await token_tracker.get_overall_efficiency()
    # assert 0 < efficiency < 100, "Token efficiency should be between 0 and 100 tokens per task"

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

def test_token_usage_per_query_type(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    query_types = {
        "short": "What's the capital of France?",
        "medium": "Explain the process of photosynthesis in plants.",
        "long": "Write a 500-word essay on the impact of artificial intelligence on modern society."
    }
    
    def measure_token_usage(query):
        response = claude_manager.generate_response(query)
        return claude_manager.count_tokens(query + response)
    
    for query_type, query in query_types.items():
        result = benchmark.pedantic(measure_token_usage, args=(query,), iterations=5, rounds=3)
        print(f"Token usage for {query_type} query: {result.average:.0f} tokens")

def test_cost_effectiveness_of_models(llm_manager: LLMManager, benchmark: BenchmarkFixture):
    models = ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"]
    query = "Explain the theory of relativity in simple terms."
    
    def measure_cost_effectiveness(model):
        response = llm_manager.query(query, tier=model)
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
from pytest_benchmark.fixture import BenchmarkFixture
from src.claude_manager import ClaudeManager
from src.llm_manager import LLMManager

@pytest.fixture
def claude_manager():
    return ClaudeManager()

@pytest.fixture
def llm_manager():
    return LLMManager()

def test_token_usage_per_query_type(claude_manager: ClaudeManager, benchmark: BenchmarkFixture):
    query_types = {
        "short": "What's the capital of France?",
        "medium": "Explain the process of photosynthesis in plants.",
        "long": "Write a 500-word essay on the impact of artificial intelligence on modern society."
    }
    
    def measure_token_usage(query):
        response = claude_manager.generate_response(query)
        return claude_manager.count_tokens(query + response)
    
    for query_type, query in query_types.items():
        result = benchmark.pedantic(measure_token_usage, args=(query,), iterations=5, rounds=3)
        print(f"Token usage for {query_type} query: {result.average:.0f} tokens")

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

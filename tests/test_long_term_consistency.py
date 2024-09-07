import pytest
import asyncio
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

@pytest.mark.asyncio
async def test_extended_conversation():
    manager = ClaudeManager(client=MockClaudeClient())
    conversation = [
        "Hello, how are you?",
        "Can you explain the concept of machine learning?",
        "What are some applications of machine learning?",
        "How does deep learning differ from traditional machine learning?",
        "Can you give an example of a real-world deep learning application?"
    ]
    
    responses = []
    for message in conversation:
        response = await manager.generate_response(message)
        responses.append(response)
    
    # Check for consistency in responses
    assert all("machine learning" in response.lower() for response in responses[1:]), "Responses should consistently mention machine learning"
    assert any("deep learning" in response.lower() for response in responses[3:]), "Later responses should mention deep learning"
    
    # Check for context retention
    assert any("as I mentioned earlier" in response.lower() or "as we discussed" in response.lower() for response in responses[2:]), "Responses should show context retention"

@pytest.mark.asyncio
async def test_long_term_memory():
    manager = ClaudeManager(client=MockClaudeClient())
    initial_prompt = "Remember this number: 42"
    await manager.generate_response(initial_prompt)
    
    # Simulate a long conversation with unrelated topics
    for _ in range(10):
        await manager.generate_response("Tell me about a random topic.")
    
    recall_prompt = "What was the number I asked you to remember at the beginning of our conversation?"
    response = await manager.generate_response(recall_prompt)
    
    assert "42" in response, "Claude should remember the number from the beginning of the conversation"

@pytest.mark.asyncio
async def test_consistency_under_load():
    manager = ClaudeManager(client=MockClaudeClient())
    base_prompt = "Explain the concept of recursion in programming."
    
    responses = await asyncio.gather(*[manager.generate_response(base_prompt) for _ in range(5)])
    
    # Check that all responses are consistent
    first_response = responses[0]
    for response in responses[1:]:
        assert response == first_response, "All responses should be consistent under load"

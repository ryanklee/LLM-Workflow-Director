import pytest
from unittest.mock import patch
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    return ClaudeManager(api_key="test_key")

@pytest.mark.asyncio
async def test_claude_consistency_across_interactions(claude_manager):
    with patch.object(claude_manager, 'client', MockClaudeClient()):
        # Test maintaining context across multiple queries
        response1 = await claude_manager.generate_response("My name is Alice.")
        assert "Alice" in response1
        
        response2 = await claude_manager.generate_response("What's my name?")
        assert "Alice" in response2
        
        # Test consistent responses to similar questions
        response3 = await claude_manager.generate_response("What is the capital of France?")
        response4 = await claude_manager.generate_response("Tell me the capital city of France.")
        assert response3.strip().lower() == response4.strip().lower()
        
        # Test handling context switches
        response5 = await claude_manager.generate_response("Let's talk about dogs. What are some popular breeds?")
        assert "dog" in response5.lower() and "breed" in response5.lower()
        
        response6 = await claude_manager.generate_response("Now, what's my name again?")
        assert "Alice" in response6

        # Test returning to previous topics
        response7 = await claude_manager.generate_response("Can you list those dog breeds again?")
        assert "dog" in response7.lower() and "breed" in response7.lower()

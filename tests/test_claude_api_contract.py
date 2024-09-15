import pytest
from pact import Consumer, Provider
from src.mock_claude_client import MockClaudeClient

@pytest.fixture(scope='session')
def pact():
    return Consumer('LLMWorkflowDirector').has_pact_with(Provider('ClaudeAPI'))

@pytest.fixture
async def claude_client():
    return MockClaudeClient()

@pytest.mark.asyncio
async def test_create_message(pact, claude_client):
    pact.given(
        'A request for message creation'
    ).upon_receiving(
        'A valid message creation request'
    ).with_request(
        'POST', '/v1/messages',
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': 'Hello, Claude!'}]
        }
    ).will_respond_with(200, body={
        'id': pytest.matchers.like('msg_123abc'),
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': pytest.matchers.like('Hello! How can I assist you today?')
            }
        ],
        'model': 'claude-3-opus-20240229',
        'stop_reason': 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': pytest.matchers.like(5),
            'output_tokens': pytest.matchers.like(9)
        }
    })

    async with pact:
        result = await claude_client.create_message(
            model='claude-3-opus-20240229',
            max_tokens=100,
            messages=[{'role': 'user', 'content': 'Hello, Claude!'}]
        )
        assert result['content'][0]['text'].startswith('Hello!')
        assert result['model'] == 'claude-3-opus-20240229'
        assert result['type'] == 'message'
        assert result['role'] == 'assistant'
        assert 'usage' in result

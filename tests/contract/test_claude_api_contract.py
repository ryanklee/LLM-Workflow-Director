import pytest
from pact import Consumer, Provider, Like
from pact.pact import Pact

@pytest.fixture(scope='session')
def pact():
    pact = Consumer('LLMWorkflowDirector').has_pact_with(
        Provider('ClaudeAPI'),
        port=1234,
        host_name='localhost',
        pact_dir='./pacts'
    )
    pact.start_service()
    yield pact
    pact.stop_service()

@pytest.fixture
def claude_client(pact):
    from src.mock_claude_client import MockClaudeClient
    yield MockClaudeClient()

@pytest.mark.asyncio
async def test_create_message(pact, claude_client):
    pact.given(
        'A request to create a message'
    ).upon_receiving(
        'A valid message creation request'
    ).with_request(
        'POST', '/v1/messages',
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 1000,
            'messages': [{'role': 'user', 'content': 'Hello, Claude!'}]
        }
    ).will_respond_with(200, body={
        'id': Like('msg_123abc'),
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': Like('Hello! How can I assist you today?')
            }
        ],
        'model': 'claude-3-opus-20240229',
        'stop_reason': 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': Like(5),
            'output_tokens': Like(9)
        }
    })

    async with pact:
        result = await claude_client.create_message('Hello, Claude!', max_tokens=1000)
        assert result['role'] == 'assistant'
        assert isinstance(result['content'][0]['text'], str)

@pytest.mark.asyncio
async def test_count_tokens(pact, claude_client):
    pact.given(
        'A request to count tokens'
    ).upon_receiving(
        'A valid token counting request'
    ).with_request(
        'POST', '/v1/tokenize',
        body={
            'model': 'claude-3-opus-20240229',
            'prompt': 'Hello, world!'
        }
    ).will_respond_with(200, body={
        'token_count': Like(3)
    })

    async with pact:
        result = await claude_client.count_tokens('Hello, world!')
        assert isinstance(result, int)
        assert result > 0

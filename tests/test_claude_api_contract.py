import pytest
from pact import Consumer, Provider, Like
from src.mock_claude_client import MockClaudeClient

@pytest.fixture(scope='session')
def pact():
    pact = Consumer('LLMWorkflowDirector').has_pact_with(
        Provider('ClaudeAPI'),
        port=1234,
        host_name='localhost'
    )
    pact.start_service()
    yield pact
    pact.stop_service()

@pytest.fixture
def pact_context(pact):
    with pact:
        yield pact

@pytest.fixture
async def claude_client():
    return MockClaudeClient()

@pytest.mark.asyncio
async def test_create_message(pact_context, claude_client):
    pact_context.given(
        'A request for message creation'
    ).upon_receiving(
        'A valid message creation request'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 100,
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

    result = await claude_client.messages.create(
        model='claude-3-opus-20240229',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Hello, Claude!'}]
    )
    assert result['content'][0]['text'].startswith('Hello!')
    assert result['model'] == 'claude-3-opus-20240229'
    assert result['type'] == 'message'
    assert result['role'] == 'assistant'
    assert 'usage' in result

@pytest.mark.asyncio
async def test_rate_limit_handling(pact_context, claude_client):
    pact_context.given(
        'A request that exceeds rate limits'
    ).upon_receiving(
        'A rate limit exceeded response'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')}
    ).will_respond_with(429, body={
        'error': {
            'type': 'rate_limit_error',
            'message': 'Rate limit exceeded'
        }
    })

    with pytest.raises(CustomRateLimitError) as exc_info:
        await claude_client.messages.create(
            model='claude-3-opus-20240229',
            max_tokens=100,
            messages=[{'role': 'user', 'content': 'Test message'}]
        )
    assert 'Rate limit exceeded' in str(exc_info.value)

@pytest.mark.asyncio
async def test_streaming_response(pact_context, claude_client):
    pact_context.given(
        'A request for streaming response'
    ).upon_receiving(
        'A valid streaming response request'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': 'Tell me a story'}],
            'stream': True
        }
    ).will_respond_with(200, body=Like('data: {"type":"content_block_delta","delta":{"type":"text","text":"Once upon a time"}}\n\ndata: {"type":"content_block_delta","delta":{"type":"text","text":" in a land far away"}}\n\ndata: {"type":"message_delta","delta":{"stop_reason":"end_turn"}}\n\ndata: [DONE]'))

    response = await claude_client.messages.create(
        model='claude-3-opus-20240229',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Tell me a story'}],
        stream=True
    )
    chunks = []
    async for chunk in response:
        chunks.append(chunk)
    assert len(chunks) > 0
    assert chunks[-1]['type'] == 'message_delta'
    assert chunks[-1]['delta']['stop_reason'] == 'end_turn'

@pytest.mark.asyncio
async def test_count_tokens(pact_context, claude_client):
    pact_context.given(
        'A request to count tokens'
    ).upon_receiving(
        'A valid token counting request'
    ).with_request(
        'POST', '/v1/tokenize',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'claude-3-opus-20240229',
            'prompt': 'Hello, world!'
        }
    ).will_respond_with(200, body={
        'token_count': Like(3)
    })

    result = await claude_client.count_tokens('Hello, world!')
    assert isinstance(result, int)
    assert result > 0

@pytest.mark.asyncio
async def test_error_handling(pact_context, claude_client):
    pact_context.given(
        'A request that causes an API error'
    ).upon_receiving(
        'An invalid request causing an error'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'invalid-model',
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': 'This should cause an error'}]
        }
    ).will_respond_with(400, body={
        'error': {
            'type': 'invalid_request_error',
            'message': Like('Invalid model specified')
        }
    })

    with pytest.raises(APIStatusError) as exc_info:
        await claude_client.messages.create(
            model='invalid-model',
            max_tokens=100,
            messages=[{'role': 'user', 'content': 'This should cause an error'}]
        )
    assert 'Invalid model specified' in str(exc_info.value)

@pytest.mark.asyncio
async def test_count_tokens(pact_context, claude_client):
    pact_context.given(
        'A request to count tokens'
    ).upon_receiving(
        'A valid token counting request'
    ).with_request(
        'POST', '/v1/tokenize',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'claude-3-opus-20240229',
            'prompt': 'Hello, world!'
        }
    ).will_respond_with(200, body={
        'token_count': Like(3)
    })

    result = await claude_client.count_tokens('Hello, world!')
    assert isinstance(result, int)
    assert result > 0

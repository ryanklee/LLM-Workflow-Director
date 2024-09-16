import pytest
import logging
from pact import Consumer, Provider, Like
from src.mock_claude_client import MockClaudeClient
from src.exceptions import CustomRateLimitError
from anthropic import APIStatusError

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    client = MockClaudeClient(api_key="test_api_key")
    logger.debug(f"Created MockClaudeClient instance: {client}")
    try:
        yield client
    finally:
        logger.debug(f"Cleaning up MockClaudeClient instance: {client}")
        await client.debug_dump()

@pytest.mark.asyncio
async def test_create_message(pact_context, claude_client):
    logger.info("Starting test_create_message")
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
    logger.debug(f"Received result: {result}")
    assert result['content'][0]['text'].startswith('Hello!')
    assert result['model'] == 'claude-3-opus-20240229'
    assert result['type'] == 'message'
    assert result['role'] == 'assistant'
    assert 'usage' in result
    logger.info("test_create_message completed successfully")

@pytest.mark.asyncio
async def test_rate_limit_handling(pact_context, claude_client):
    logger.info("Starting test_rate_limit_handling")
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
    logger.info("test_rate_limit_handling completed successfully")

@pytest.mark.asyncio
async def test_streaming_response(pact_context, claude_client):
    logger.info("Starting test_streaming_response")
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
        logger.debug(f"Received chunk: {chunk}")
    assert len(chunks) > 0
    assert chunks[-1]['type'] == 'message_delta'
    assert chunks[-1]['delta']['stop_reason'] == 'end_turn'
    logger.info("test_streaming_response completed successfully")

@pytest.mark.asyncio
async def test_count_tokens(pact_context, claude_client):
    logger.info("Starting test_count_tokens")
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
    logger.debug(f"Token count result: {result}")
    assert isinstance(result, int)
    assert result > 0
    logger.info("test_count_tokens completed successfully")

@pytest.mark.asyncio
async def test_error_handling(pact_context, claude_client):
    logger.info("Starting test_error_handling")
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
    logger.debug(f"Caught exception: {exc_info.value}")
    assert 'Invalid model specified' in str(exc_info.value)
    logger.info("test_error_handling completed successfully")

@pytest.mark.asyncio
async def test_model_selection(pact_context, claude_client):
    logger.info("Starting test_model_selection")
    pact_context.given(
        'A request for model selection'
    ).upon_receiving(
        'A valid model selection request'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': Like('claude-3-haiku-20240307'),
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': 'Simple task'}]
        }
    ).will_respond_with(200, body={
        'id': Like('msg_123abc'),
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': Like('Here is a simple response.')
            }
        ],
        'model': Like('claude-3-haiku-20240307'),
        'stop_reason': 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': Like(3),
            'output_tokens': Like(6)
        }
    })

    result = await claude_client.messages.create(
        model='claude-3-haiku-20240307',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'Simple task'}]
    )
    logger.debug(f"Received result: {result}")
    assert result['model'] == 'claude-3-haiku-20240307'
    assert len(result['content'][0]['text']) < 50  # Assuming Haiku gives shorter responses
    logger.info("test_model_selection completed successfully")

@pytest.mark.asyncio
async def test_context_window(pact_context, claude_client):
    logger.info("Starting test_context_window")
    long_context = "This is a very long context. " * 1000  # 5000 words, well within 200k token limit
    pact_context.given(
        'A request with a large context window'
    ).upon_receiving(
        'A valid large context request'
    ).with_request(
        'POST', '/v1/messages',
        headers={'X-API-Key': Like('sk-ant-api03-valid-key')},
        body={
            'model': 'claude-3-opus-20240229',
            'max_tokens': 100,
            'messages': [{'role': 'user', 'content': long_context + "\nSummarize this."}]
        }
    ).will_respond_with(200, body={
        'id': Like('msg_123abc'),
        'type': 'message',
        'role': 'assistant',
        'content': [
            {
                'type': 'text',
                'text': Like('Here is a summary of the long context...')
            }
        ],
        'model': 'claude-3-opus-20240229',
        'stop_reason': 'end_turn',
        'stop_sequence': None,
        'usage': {
            'input_tokens': Like(5000),
            'output_tokens': Like(20)
        }
    })

    result = await claude_client.messages.create(
        model='claude-3-opus-20240229',
        max_tokens=100,
        messages=[{'role': 'user', 'content': long_context + "\nSummarize this."}]
    )
    logger.debug(f"Received result: {result}")
    assert 'summary' in result['content'][0]['text'].lower()
    assert result['usage']['input_tokens'] > 1000  # Ensure it's processing a large context
    logger.info("test_context_window completed successfully")

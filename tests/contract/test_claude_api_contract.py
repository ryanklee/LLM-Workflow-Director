import pytest
from pact import Consumer, Provider

@pytest.fixture(scope='session')
def pact():
    return Consumer('LLMWorkflowDirector').has_pact_with(Provider('ClaudeAPI'))

def test_create_message(pact):
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

    with pact:
        result = claude_client.create_message('Hello, Claude!', max_tokens=1000)
        assert result['role'] == 'assistant'
        assert isinstance(result['content'][0]['text'], str)

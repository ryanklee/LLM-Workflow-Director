# Contract Testing for Claude API Integration

## Overview

Contract testing is a crucial part of our testing strategy for the LLM-Workflow Director's integration with the Claude API. It ensures that our understanding of the API's behavior is accurate and up-to-date, and that our mock implementations correctly represent the real API.

## Tools and Setup

We use [Pact](https://docs.pact.io/) as our contract testing tool. Pact allows us to define the expected interactions between our system (the consumer) and the Claude API (the provider).

### Installation

To set up Pact for Python, install the following packages:

```
pip install pytest-pact
```

## Defining Contracts

Contracts are defined in the `tests/contract` directory. Each contract test file should focus on a specific aspect of the Claude API.

Example contract test structure:

```python
import pytest
from pact import Consumer, Provider

@pytest.fixture(scope='session')
def pact():
    return Consumer('LLMWorkflowDirector').has_pact_with(Provider('ClaudeAPI'))

def test_create_completion(pact):
    pact.given(
        'A request for text completion'
    ).upon_receiving(
        'A valid completion request'
    ).with_request(
        'POST', '/v1/complete',
        body={'prompt': 'Hello, world!', 'max_tokens': 50}
    ).will_respond_with(200, body={
        'id': pytest.matchers.like('cmpl-123'),
        'object': 'text_completion',
        'created': pytest.matchers.like(1616789509),
        'model': pytest.matchers.like('claude-v1'),
        'choices': [
            {
                'text': pytest.matchers.like('Hello! How can I assist you today?'),
                'index': 0,
                'logprobs': None,
                'finish_reason': 'length'
            }
        ],
        'usage': {
            'prompt_tokens': pytest.matchers.like(3),
            'completion_tokens': pytest.matchers.like(9),
            'total_tokens': pytest.matchers.like(12)
        }
    })

    with pact:
        result = claude_client.create_completion('Hello, world!', max_tokens=50)
        assert result['choices'][0]['text'].startswith('Hello!')
```

## Running Contract Tests

To run contract tests:

```
pytest tests/contract
```

## Generating Mock Behaviors

After running contract tests, we generate mock behaviors based on the contract test results. This process ensures that our MockClaudeClient accurately represents the behavior defined in the contracts.

Example mock generation script:

```python
import json
from pact import Pact

def generate_mock_behaviors():
    pact = Pact.load('pacts/llmworkflowdirector-claudeapi.json')
    mock_behaviors = {}

    for interaction in pact['interactions']:
        request = interaction['request']
        response = interaction['response']

        mock_behaviors[request['path']] = {
            'method': request['method'],
            'request': request,
            'response': response
        }

    with open('src/mock_claude_client_behaviors.json', 'w') as f:
        json.dump(mock_behaviors, f, indent=2)

if __name__ == '__main__':
    generate_mock_behaviors()
```

## Updating MockClaudeClient

Update the MockClaudeClient to use the generated mock behaviors:

```python
import json

class MockClaudeClient:
    def __init__(self):
        with open('src/mock_claude_client_behaviors.json', 'r') as f:
            self.behaviors = json.load(f)

    def create_completion(self, prompt, max_tokens):
        behavior = self.behaviors['/v1/complete']
        if behavior['request']['body']['prompt'] == prompt and behavior['request']['body']['max_tokens'] == max_tokens:
            return behavior['response']['body']
        raise ValueError("Unexpected request parameters")
```

## Continuous Integration

Integrate contract testing into your CI/CD pipeline to ensure that changes to the Claude API are detected early:

1. Run contract tests against the latest Claude API version.
2. If changes are detected, update the contract and regenerate mock behaviors.
3. Run the full test suite with updated mocks to ensure system compatibility.

## Handling API Changes

When contract tests detect changes in the Claude API:

1. Review the changes and update the contract tests accordingly.
2. Regenerate mock behaviors based on the updated contracts.
3. Update the MockClaudeClient and any affected parts of the LLM-Workflow Director.
4. Run the full test suite to ensure compatibility with the API changes.
5. Update documentation to reflect any changes in API behavior or usage.

By following this contract testing approach, we ensure that our integration with the Claude API remains accurate and that our tests reliably represent real-world scenarios.

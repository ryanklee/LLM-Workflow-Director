# Claude API Reference

## 1. API Overview and Authentication

- The Anthropic API uses REST principles and accepts/returns JSON.
- All requests require an "x-api-key" header with your API key for authentication.
- Set the "anthropic-version" header to specify the API version (e.g., "2023-06-01").
- Use "content-type: application/json" header for requests.
- ALWAYS use the messages API for interacting with Claude models.

## 2. Messages API

- The messages API is the primary method for interacting with Claude models.
- Use the POST /v1/messages endpoint to send messages and receive responses.
- The request body should include:
  - "model": The Claude model to use (e.g., "claude-3-opus-20240229")
  - "messages": An array of message objects, each with "role" and "content"
  - "max_tokens": Maximum number of tokens in the response

Example request:
```json
{
  "model": "claude-3-opus-20240229",
  "max_tokens": 1000,
  "messages": [
    {"role": "user", "content": "Hello, Claude!"}
  ]
}
```

## 3. Response Structure

The response from the Messages API will have the following structure:

```json
{
  "id": "msg_123abc",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I assist you today?"
    }
  ],
  "model": "claude-3-opus-20240229",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 5,
    "output_tokens": 9
  }
}
```

Key elements of the response:
- "id": A unique identifier for the message
- "role": Always "assistant" for Claude's responses
- "content": An array of content objects, typically with "type" and "text" fields
- "model": The model used to generate the response
- "usage": Token usage information for the request and response

## 4. Rate Limits and Error Handling

- The API has rate limits based on requests per minute (RPM) and tokens per minute (TPM).
- Implement exponential backoff for rate limit errors (HTTP 429).
- Handle other potential errors, such as authentication issues (HTTP 401) or invalid requests (HTTP 400).

## 5. Best Practices

- Use system messages to set context or assign roles to Claude.
- Keep track of the conversation history to maintain context across multiple interactions.
- Be mindful of the token limit and manage long conversations by summarizing or truncating when necessary.
- Implement proper error handling and retry mechanisms for API calls.
- Use the appropriate Claude model based on the complexity of the task.

## 6. Supported Models

- Claude 3 Haiku: Fast and cost-effective for simpler tasks
- Claude 3 Sonnet: Balanced performance for most general applications
- Claude 3 Opus: Highest capability for complex tasks and reasoning

## 7. Authentication and Client Initialization

- Store your API key securely (e.g., in environment variables).
- Initialize the client with your API key and the desired API version.
- Example initialization (using a hypothetical Python client):

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-api-key")
```

For detailed implementation guidance and the latest updates, always refer to the official Anthropic documentation:
- https://docs.anthropic.com/claude/reference/messages_post
- https://docs.anthropic.com/claude/docs/intro-to-claude
- https://docs.anthropic.com/claude/docs/message-conventions

## 3. Prompt Engineering Best Practices

- Be clear and direct in instructions.
- Use examples (few-shot learning) for complex tasks.
- Implement chain-of-thought prompting for reasoning tasks.
- Utilize XML tags for structured input/output.
- Assign roles to Claude using system messages.
- For long contexts (200K+ tokens):
  - Place long-form data at the beginning of the conversation.
  - Structure document content with XML tags.
  - Use grounding by asking Claude to quote relevant parts before analysis.

## 4. Tool Use (Function Calling)

- Define tools in the API request using the "tools" parameter.
- Each tool definition includes:
  - name: Unique identifier for the tool
  - description: Detailed explanation of the tool's purpose and usage
  - input_schema: JSON schema defining expected parameters
- Claude will return a "tool_use" content block when invoking a tool.
- Implement tool execution on the client-side and return results using "tool_result" content blocks.
- Use "tool_choice" parameter to control tool selection behavior.

## 5. Embeddings

- Claude API provides built-in embedding functionality.
- Use the /v1/embed endpoint for generating embeddings.
- Embeddings can be used for semantic search, similarity comparisons, and efficient information retrieval.
- Refer to the official Claude API documentation for the latest information on embedding models and parameters.

## 6. API Versioning and Rate Limits

- API versions are date-based (e.g., "2023-06-01").
- Set version using the "anthropic-version" header.
- Rate limits vary by model and are based on requests per minute (RPM) and tokens per minute (TPM).
- Implement exponential backoff for rate limit errors (HTTP 429).

## 7. Best Practices

- Use XML tags to structure complex prompts and outputs.
- Implement proper error handling for API responses.
- Optimize token usage by crafting efficient prompts.
- Utilize system prompts for consistent behavior across conversations.
- Experiment with different prompt engineering techniques for optimal results.

## 8. Text Generation Capabilities

- Claude supports various text-based tasks, including summarization, content generation, entity extraction, translation, and code explanation/generation.
- Tailor prompts to specific use cases for best results.

## 9. Security Considerations

- Store API keys securely (environment variables, secret management systems).
- Implement input validation and sanitization.
- Be cautious with user-generated content in messages.
- Implement output filtering for sensitive information.
- Regularly audit and rotate API keys.
- Use HTTPS for all API communications.

## 10. Best Practices for Messages API Usage

- Always use the messages API for interacting with Claude models.
- Structure your conversation history as an array of message objects.
- Use system messages to set context or assign roles to Claude.
- Keep track of the conversation history to maintain context across multiple interactions.
- Be mindful of the token limit and manage long conversations by summarizing or truncating when necessary.
- Never use the completions API as it is deprecated.

For detailed implementation guidance, refer to the official Anthropic documentation:
- https://docs.anthropic.com/claude/reference/messages_post
- https://docs.anthropic.com/claude/docs/intro-to-claude
- https://docs.anthropic.com/claude/docs/message-conventions

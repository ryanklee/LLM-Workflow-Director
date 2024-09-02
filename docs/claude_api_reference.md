# Claude API Reference

## 1. API Overview and Authentication

- The Anthropic API uses REST principles and accepts/returns JSON.
- All requests require an "x-api-key" header with your API key for authentication.
- Set the "anthropic-version" header to specify the API version (e.g., "2023-06-01").
- Use "content-type: application/json" header for requests.

## 2. Messages API

- Primary endpoint: POST https://api.anthropic.com/v1/messages
- Key parameters:
  - model: Specify the Claude model version (e.g., "claude-3-opus-20240229")
  - max_tokens: Maximum number of tokens to generate
  - messages: Array of message objects with "role" and "content"
  - system: Optional system prompt for context/instructions
- Response includes generated content, stop reason, and token usage.

## 3. Prompt Engineering Best Practices

- Be clear and direct in instructions.
- Use examples (few-shot learning) for complex tasks.
- Implement chain-of-thought prompting for reasoning tasks.
- Utilize XML tags for structured input/output.
- Assign roles to Claude using system prompts.
- For long contexts (200K+ tokens):
  - Place long-form data at the top of the prompt.
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

- Anthropic recommends using Voyage AI for embeddings.
- Key Voyage models:
  - voyage-2: 4000 context length, 1024-dim embeddings
  - voyage-large-2: 16000 context length, 1536-dim embeddings
  - voyage-code-2: Optimized for code retrieval
- Use "input_type" parameter ("query" or "document") for enhanced retrieval quality.
- Embeddings can be used for semantic search and similarity comparisons.

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
- Be cautious with user-generated content in prompts.
- Implement output filtering for sensitive information.
- Regularly audit and rotate API keys.

## 10. Example API Integration

```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

print(message.content[0].text)
```

For detailed implementation guidance, refer to the official Anthropic documentation:
- https://docs.anthropic.com/en/api/messages
- https://docs.anthropic.com/en/api/getting-started
- https://docs.anthropic.com/en/api/messages-examples
- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- https://docs.anthropic.com/en/docs/build-with-claude/embeddings

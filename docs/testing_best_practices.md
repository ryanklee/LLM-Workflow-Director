# LLM API Testing Best Practices for LLM-Workflow Director

## 0. Test File Size and Structure

(Previous content remains unchanged)

## 1. Test Output Verbosity

(Previous content remains unchanged)

## 2. Optimizing String Usage in Tests

(Previous content remains unchanged)

## 3. Contract Testing and Mocking Strategies

3.1. Contract Test Implementation:
   - Use Pact for defining and running contract tests against the Claude API.
   - Define comprehensive contract tests covering all endpoints and behaviors of the Claude API, focusing on the Messages API endpoint.
   - Regularly run contract tests against the latest version of the Claude API to catch any changes or new features.
   - Implement tests for authentication using API keys in the `X-API-Key` header.

3.2. MockClaudeClient Implementation:
   - Develop a comprehensive MockClaudeClient that derives its behavior from contract test results.
   - Implement realistic token counting and rate limiting in the mock client based on the official rate limits documentation.
   - Add methods to simulate various error conditions and edge cases as defined in the official errors documentation.
   - Implement streaming response simulation for long-running tasks.

3.3. Fixture Usage:
   - Create fixtures for commonly used mock responses and configurations based on contract test results.
   - Implement factory fixtures for generating varied test data that aligns with the Messages API input format.

3.4. Contextual Mocking:
   - Use context managers to temporarily modify mock behavior within specific tests, ensuring alignment with contract-defined behaviors.
   - Implement mock responses that vary based on input to simulate more realistic scenarios, including different Claude model behaviors (e.g., Claude 3 Haiku, Sonnet, Opus).

3.5. Contract Test Maintenance:
   - Maintain a versioned history of contract tests to track API changes over time, aligning with the Claude API versioning strategy.
   - Implement a system to automatically update mocks and tests when contract changes are detected, particularly for new API versions.

3.6. Error Handling and Rate Limit Testing:
   - Implement tests for various error scenarios based on the official error documentation.
   - Create tests to verify proper handling of rate limits and backoff strategies.

3.7. Streaming Response Testing:
   - Develop tests specifically for handling streaming responses from the Claude API.

3.8. Version Compatibility Testing:
   - Implement tests to ensure compatibility with different versions of the Claude API.

For the most up-to-date testing strategies, regularly consult the official Anthropic documentation and Pact documentation.

## 4. Test Categorization and Execution

(Previous content remains unchanged)

## 5. Continuous Improvement

5.1. Performance Monitoring:
   - Implement test timing and resource usage tracking.
   - Regularly review and optimize slow or resource-intensive tests.
   - Compare test performance against contract-defined SLAs.

5.2. Coverage Analysis:
   - Maintain high test coverage while optimizing for performance and token usage.
   - Use coverage tools to identify untested code paths and edge cases.
   - Ensure coverage includes all scenarios defined in the contract tests.

5.3. Regression Prevention:
   - Implement automated regression testing for critical functionality.
   - Use snapshot testing for complex outputs to detect unexpected changes.
   - Regularly compare mock behaviors against the latest contract test results to prevent drift.

5.4. API Change Management:
   - Set up alerts for contract test failures or detected API changes.
   - Implement a process to review and adapt to API changes quickly.
   - Maintain documentation of API changes detected through contract testing.

By following these best practices, we can maintain a comprehensive and efficient test suite that optimizes for both thorough testing and minimal resource usage, while ensuring our tests accurately reflect the behavior of the Claude API through contract testing.

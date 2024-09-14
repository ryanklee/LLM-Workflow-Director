# LLM API Testing Best Practices for LLM-Workflow Director

## 1. Test Output Verbosity

1.1. Pytest Configuration:
   - Use quiet mode (-q) to reduce overall output verbosity.
   - Customize test output format using --tb=short for concise tracebacks.
   - Disable capture logging with --show-capture=no to reduce noise.

1.2. Logging:
   - Implement structured logging for better readability and easier parsing.
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR) consistently.
   - Consider using a logging fixture to capture and analyze logs per test.

## 2. Optimizing String Usage in Tests

2.1. Token Limit Implementation:
   - Define a maximum token limit for non-mocked LLM tests (e.g., 100 tokens).
   - Implement a utility function to truncate inputs and expected outputs to this limit.
   - Use this utility in all non-mocked LLM tests.

2.2. Test Separation:
   - Create separate test classes or modules for mocked and non-mocked LLM tests.
   - Use the new @pytest.mark.mock marker for tests using mocked LLMs.
   - Implement longer inputs/outputs only in mocked LLM tests.

2.3. Input/Output Optimization:
   - Review and update existing tests to use shorter, representative inputs and outputs.
   - For non-mocked tests, focus on essential functionality with minimal token usage.
   - Use parameterized tests to cover multiple scenarios without repeating long strings.

## 3. Mocking Strategies

3.1. MockClaudeClient Enhancement:
   - Expand MockClaudeClient to better simulate Claude API behavior.
   - Implement realistic token counting and rate limiting in the mock client.
   - Add methods to simulate various error conditions and edge cases.

3.2. Fixture Usage:
   - Create fixtures for commonly used mock responses and configurations.
   - Implement a fixture for switching between real and mock Claude clients.

## 4. Test Categories and Execution

4.1. Test Categorization:
   - Use pytest markers to categorize tests (e.g., @pytest.mark.fast, @pytest.mark.slow, @pytest.mark.mock).
   - Implement test selection in CI/CD pipelines based on these categories.

4.2. Parallel Execution:
   - Ensure tests are designed to run independently for parallel execution.
   - Use pytest-xdist for parallel test execution in CI/CD pipelines.

## 5. Continuous Improvement

5.1. Performance Monitoring:
   - Implement test timing and resource usage tracking.
   - Regularly review and optimize slow or resource-intensive tests.

5.2. Coverage Analysis:
   - Maintain high test coverage while optimizing for performance and token usage.
   - Regularly review coverage reports to identify areas needing additional testing.

By following these best practices, we can maintain a comprehensive and efficient test suite that optimizes for both thorough testing and minimal resource usage, particularly in terms of LLM API calls and token consumption.

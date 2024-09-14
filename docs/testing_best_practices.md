# LLM API Testing Best Practices for LLM-Workflow Director

## 0. Test File Size and Structure

0.1. File Size Optimization:
   - Keep test files as small as possible without sacrificing cohesion and separation of concerns.
   - Aim for a maximum file size of 500 lines per test file.
   - Split large test files into smaller, focused files based on functionality or test categories.

0.2. Test Structure:
   - Group related tests into classes or nested functions for better organization.
   - Use descriptive names for test files, classes, and functions to clearly indicate their purpose.
   - Implement shared setup and teardown methods to reduce code duplication.

0.3. Code Reusability:
   - Create utility functions for common test operations to keep individual tests concise.
   - Use fixtures and parametrization to reduce repetitive code.

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

(Sections 3, 4, and 5 remain unchanged)

By following these best practices, we can maintain a comprehensive and efficient test suite that optimizes for both thorough testing and minimal resource usage, particularly in terms of file size, test output verbosity, and LLM API calls and token consumption.

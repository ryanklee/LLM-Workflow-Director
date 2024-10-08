# Testing Guidelines for LLM-Workflow Director

## Overview
This document outlines the testing practices and guidelines for the LLM-Workflow Director project. We use pytest as our primary testing framework, with additional plugins for enhanced functionality.

## Test Structure
- Tests are organized in the `tests/` directory
- Test files are named with the prefix `test_`
- Test functions are also prefixed with `test_`

## Running Tests
To run all tests in parallel:
```
pytest
```

To run specific test files:
```
pytest tests/test_file_name.py
```

To run tests with a specific number of workers:
```
pytest -n 4
```

## Test Categories
We use pytest marks to categorize our tests:
- `@pytest.mark.fast`: Quick tests that should run frequently
- `@pytest.mark.slow`: Slower tests that might take more time
- `@pytest.mark.benchmark`: Performance benchmark tests
- `@pytest.mark.asyncio`: Asynchronous tests

To run only fast tests:
```
pytest -m fast
```

To run all tests except slow ones:
```
pytest -m "not slow"
```

## Fixtures
We use fixtures for setting up test environments and sharing resources across tests. Key fixtures include:
- `mock_claude_client`: Provides a mocked version of the Claude API client
- `claude_manager`: Provides a ClaudeManager instance for testing
- `llm_manager`: Provides an LLMManager instance for testing
- `cached_responses`: A module-scoped fixture for caching API responses

## Best Practices
1. Write descriptive test names that explain the behavior being tested
2. Use parameterized tests to cover multiple scenarios
3. Keep tests independent and idempotent
4. Use mocking to isolate the system under test
5. Aim for high test coverage, but prioritize critical paths
6. Regularly run the full test suite to catch regressions
7. Use asynchronous testing for all LLM-related functionality
8. Implement proper error handling and assertions in tests

## Continuous Integration
Our CI pipeline runs tests automatically on each pull request. Ensure all tests pass before merging.

## Performance Testing
We use pytest-benchmark for performance testing. Benchmark tests are marked with `@pytest.mark.benchmark`.

## Coverage Reporting
We use pytest-cov for coverage reporting. Coverage reports are generated automatically when running tests. We aim for a minimum of 90% code coverage.

To run tests with coverage:

```
pytest --cov=src --cov-report=term-missing --cov-report=html
```

This will generate a terminal report and an HTML report in the `coverage_html_report` directory.

Our CI/CD pipeline is configured to fail if the coverage falls below 90%. To check the current coverage without running all tests:

```
coverage report
```

To generate an HTML report:

```
coverage html
```

Remember to write tests for any new functionality you add to maintain our high coverage standards.

## Updating Tests
When adding new features or modifying existing ones, always update or add corresponding tests. Follow the existing patterns and conventions in the test files.

## LLM-Specific Testing
1. Prompt Generation Testing
   - Test prompt template rendering with various contexts
   - Verify handling of missing context variables
   - Test complex prompt scenarios

2. Context Management Testing
   - Test proper utilization of context window
   - Verify handling of context overflow situations
   - Test context summarization techniques

3. LLM-Based Evaluation Testing
   - Test sufficiency evaluation for different project states
   - Verify decision-making processes based on LLM outputs
   - Test handling of complex project evaluations

4. Performance Testing for LLM Interactions
   - Benchmark response times for different types of LLM queries
   - Test token usage optimization
   - Verify performance under various load conditions

5. Error Handling and Edge Cases
   - Test rate limiting scenarios
   - Verify proper handling of API errors
   - Test fallback mechanisms and retry logic

6. Asynchronous Testing
   - Use `@pytest.mark.asyncio` for all asynchronous tests
   - Test concurrent API calls and race conditions
   - Verify proper handling of asynchronous operations

7. Mock Claude Client Testing
   - Use MockClaudeClient for all LLM-related tests
   - Test different response scenarios using mock client
   - Verify proper integration with ClaudeManager

8. Token Efficiency Testing
   - Test token usage estimation accuracy
   - Verify cost optimization suggestions
   - Test token efficiency over time

9. Context Window Efficiency
   - Test utilization of large context windows
   - Verify handling of context overflow situations
   - Test impact of context size on response quality

10. Stress Testing
    - Implement concurrent request handling tests
    - Verify system behavior under high load
    - Test rate limit recovery scenarios

Remember to update these guidelines as new testing practices or requirements are introduced to the project.
# Testing Guidelines for LLM-Workflow Director

## Overview
This document outlines the testing practices and guidelines for the LLM-Workflow Director project. We use pytest as our primary testing framework, with additional plugins for enhanced functionality.

## Test Structure
- Tests are organized in the `tests/` directory
- Test files are named with the prefix `test_`
- Test functions are also prefixed with `test_`

## Running Tests
To run all tests:
```
pytest
```

To run specific test files:
```
pytest tests/test_file_name.py
```

## Test Categories
We use pytest marks to categorize our tests:
- `@pytest.mark.fast`: Quick tests that should run frequently
- `@pytest.mark.slow`: Slower tests that might take more time
- `@pytest.mark.benchmark`: Performance benchmark tests
- `@pytest.mark.llm`: Tests that interact with LLM services

## Fixtures
We use fixtures for setting up test environments and sharing resources across tests. Key fixtures include:
- `mock_claude_client`: Provides a mocked version of the Claude API client
- `claude_manager`: Provides a ClaudeManager instance for testing
- `llm_manager`: Provides an LLMManager instance for testing
- `test_data`: Generates test data for use in tests
- `test_prompts`: Generates test prompts for use in tests

## Best Practices
1. Write descriptive test names that explain the behavior being tested
2. Use parameterized tests to cover multiple scenarios
3. Keep tests independent and idempotent
4. Use mocking to isolate the system under test
5. Aim for high test coverage, but prioritize critical paths
6. Regularly run the full test suite to catch regressions
7. Use asynchronous testing for all LLM-related functionality
8. Implement proper error handling and assertions in tests

## Continuous Integration
Our CI pipeline runs tests automatically on each pull request. Ensure all tests pass before merging.

## Performance Testing
We use pytest-benchmark for performance testing. Benchmark tests are marked with `@pytest.mark.benchmark`.

## Coverage Reporting
We use pytest-cov for coverage reporting. Coverage reports are generated automatically when running tests. Aim for a minimum of 90% code coverage.

## Updating Tests
When adding new features or modifying existing ones, always update or add corresponding tests. Follow the existing patterns and conventions in the test files.

## Token Usage Efficiency Benchmark
We have implemented a token usage efficiency benchmark in `tests/test_context_window_efficiency.py`. This benchmark:
- Generates synthetic data for testing
- Simulates Claude API calls using a mock
- Calculates token usage efficiency
- Logs detailed information about each sample and the overall efficiency
- Asserts that the efficiency falls within expected ranges

To run this benchmark:
```
pytest tests/test_context_window_efficiency.py
```

The benchmark provides insights into how efficiently we're using the context window in our LLM interactions. Monitor the logged information and benchmark results to track improvements in token usage efficiency over time.

Remember to update these guidelines as new testing practices or requirements are introduced to the project.

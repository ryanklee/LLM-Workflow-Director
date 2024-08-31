# LLM-Workflow Director: Workflow Loop Design (Golang Implementation)

## 1. Overview

The LLM-Workflow Director is a Go-based system designed to guide AI-assisted software development processes. It emphasizes Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles, ensuring systematic progression through crucial development stages.

## 2. Workflow Stages

1. Project Initialization
2. Requirements Elaboration
3. Research Gathering and Analysis
4. Domain Modeling
5. Design
6. Test Design
7. Implementation
8. Testing
9. Review and Refinement

## 3. Core Workflow Loop

1. **State Assessment**: Analyze current project state and determine active stage/step.
2. **Constraint Validation**: Apply and validate constraints for the current stage.
3. **Priority Determination**: Set priorities based on the current stage, adhering to DDD and TDD.
4. **Direction Generation**: Create actionable directions for Aider, emphasizing current priorities.
5. **Aider Execution**: Send directions to Aider and await task completion.
6. **Result Processing**: Analyze Aider's output and update project state.
7. **User Interaction**: Handle user input when required.
8. **Progress Evaluation**: Assess step/stage completion and manage transitions.

## 4. Key Components

### 4.1 StateManager
- Maintains project state
- Tracks workflow progress
- Provides state update and query interfaces

### 4.2 ConstraintEngine
- Manages stage-specific constraints
- Validates project state
- Ensures DDD and TDD adherence

### 4.3 PriorityManager
- Determines stage-based priorities
- Focuses on requirements, research, and modeling before design/implementation

### 4.4 DirectionGenerator
- Generates Claude-Sonnet 3.5-specific directions via Aider
- Incorporates current state, priorities, and validation results
- Emphasizes DDD and TDD practices

### 4.5 AiderInterface
- Manages Aider communication
- Handles command sending and result receiving
- Processes errors and unexpected responses

### 4.6 UserInteractionHandler
- Manages user prompts and input
- Integrates user decisions into the workflow

### 4.7 ProgressTracker
- Evaluates completion criteria
- Manages stage transitions
- Ensures artifact completeness before progression

### 4.8 LLMOutputManager
- Integrates LLMOutputFormatter, LLMInteractionManager, and LLMContextProvider
- Coordinates the generation of LLM-optimized output
- Ensures consistency and coherence in communication with Claude-Sonnet 3.5

### 4.9 LLMTaskManager
- Combines LLMTaskBreakdown and LLMReasoningPrompter functionalities
- Manages the decomposition and assignment of tasks to Claude-Sonnet 3.5
- Facilitates the reasoning and explanation process for complex decisions

## 5. Stage-Specific Workflows

(Detailed workflows for each stage, similar to the original document)

## 6. Transition Constraints

- Implement strict transition rules between stages
- Require artifact completion/approval before progression
- Example: Prevent Implementation start until Design approval and Test Design completion

## 7. Reporting and Logging

- Generate detailed stage progress reports
- Maintain comprehensive decision and action logs
- Provide clear project evolution visibility

## 8. Golang-Specific Considerations

- Utilize Go's concurrency features for parallel processing where applicable
- Implement robust error handling using Go's error model
- Use Go's strong typing to ensure data integrity throughout the workflow
- Leverage Go's standard library for HTTP communication, file I/O, and other system interactions
- Implement efficient data structures for state management and constraint checking

This Golang-based LLM-Workflow Director design maintains the structured approach to AI-assisted software development, emphasizing DDD and TDD principles while leveraging Go's strengths in performance, concurrency, and type safety.

## 9. LLM-Oriented Domain Model

### 9.1 LLMOutputFormatter
- Responsible for structuring and formatting output for Claude-Sonnet 3.5
- Adapts output complexity based on project stage and task
- Incorporates project context, history, and decision-making factors

### 9.2 LLMInteractionManager
- Manages the flow of information between the system and Claude-Sonnet 3.5
- Handles clarification requests and ambiguity resolution
- Processes and interprets Claude-Sonnet 3.5's responses

### 9.3 LLMContextProvider
- Generates comprehensive project context summaries
- Maintains a history of important decisions and their rationales
- Provides relevant documentation and code snippets as needed

### 9.4 LLMTaskBreakdown
- Decomposes complex tasks into manageable sub-tasks for Claude-Sonnet 3.5
- Generates step-by-step guidance for task completion
- Ensures each sub-task aligns with DDD and TDD principles

### 9.5 LLMReasoningPrompter
- Generates prompts and questions to encourage critical thinking
- Requests explanations for decisions and approaches from Claude-Sonnet 3.5
- Validates the reasoning provided by Claude-Sonnet 3.5 against project requirements and constraints

## 10. LLM-Oriented Workflow Enhancements

10.1. Before each interaction with Claude-Sonnet 3.5, generate a comprehensive context summary using LLMContextProvider.
10.2. Use LLMOutputFormatter to structure all output for optimal comprehension by Claude-Sonnet 3.5.
10.3. Employ LLMTaskBreakdown to decompose complex tasks before sending them to Claude-Sonnet 3.5.
10.4. Utilize LLMReasoningPrompter to encourage explanations and critical thinking from Claude-Sonnet 3.5.
10.5. Process Claude-Sonnet 3.5's responses using LLMInteractionManager, handling any necessary clarifications or follow-ups.
10.6. Continuously adapt the complexity and depth of interactions based on the project's progress and Claude-Sonnet 3.5's demonstrated understanding.
10.7. Implement best practices for prompt engineering:
    a. Use clear and direct language in prompts.
    b. Provide examples (multishot prompting) when introducing new concepts or tasks.
    c. Encourage step-by-step thinking using chain-of-thought prompts.
    d. Utilize XML tags to structure complex prompts and desired response formats.
    e. Assign specific roles to Claude-Sonnet 3.5 using system prompts when appropriate.
    f. Prefill responses to guide output format and content when necessary.
    g. Chain complex prompts for multi-step tasks or reasoning.
10.8. Utilize a prompt generator to create effective prompts for various scenarios.
10.9. Implement techniques for handling long contexts:
    a. Summarize previous interactions and project state.
    b. Extract and highlight relevant information for the current task.
    c. Use efficient prompting techniques to maximize context utilization.

## 11. Prompt Engineering and LLM Interaction

11.1. Maintain a library of effective prompt templates for common development tasks.
11.2. Dynamically generate and refine prompts based on:
    a. Current project state and requirements.
    b. Task complexity and domain.
    c. Previous interaction history with Claude-Sonnet 3.5.
11.3. Implement a feedback loop to improve prompt effectiveness:
    a. Analyze Claude-Sonnet 3.5's responses for relevance and quality.
    b. Adjust prompting strategies based on successful interactions.
    c. Refine prompt templates and generation algorithms over time.
11.4. Provide clear instructions for response formatting:
    a. Use XML tags or other structured formats for complex outputs.
    b. Specify desired output length, style, and level of detail.
    c. Request specific sections or components in the response when necessary.
11.5. Implement error handling and retry mechanisms:
    a. Detect off-topic or unclear responses from Claude-Sonnet 3.5.
    b. Rephrase prompts or provide additional context for clarification.
    c. Break down complex tasks into smaller, more manageable prompts if initial attempts fail.
11.6. Optimize prompts for long-running development tasks:
    a. Provide periodic summaries of project state and progress.
    b. Use checkpoints to allow Claude-Sonnet 3.5 to resume work efficiently.
    c. Implement strategies to maintain context across multiple interactions.
# LLM-Workflow Director: Workflow Loop Design (Golang Implementation)

## 1. Overview

The LLM-Workflow Director is a Go-based system designed to guide AI-assisted software development processes. It emphasizes Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles, ensuring systematic progression through crucial development stages.

## 2. Workflow Stages

1. Project Initialization
2. Requirements Elaboration
3. Research Gathering and Analysis
4. Domain Modeling
5. Design
6. Test Design
7. Implementation
8. Testing
9. Review and Refinement

## 3. Core Workflow Loop

1. **State Assessment**: Analyze current project state and determine active stage/step.
2. **Constraint Validation**: Apply and validate constraints for the current stage.
3. **Priority Determination**: Set priorities based on the current stage, adhering to DDD and TDD.
4. **Direction Generation**: Create actionable directions for Aider, emphasizing current priorities.
5. **Aider Execution**: Send directions to Aider and await task completion.
6. **Result Processing**: Analyze Aider's output and update project state.
7. **User Interaction**: Handle user input when required.
8. **Progress Evaluation**: Assess step/stage completion and manage transitions.

## 4. Key Components

### 4.1 StateManager
- Maintains project state
- Tracks workflow progress
- Provides state update and query interfaces

### 4.2 ConstraintEngine
- Manages stage-specific constraints
- Validates project state
- Ensures DDD and TDD adherence

### 4.3 PriorityManager
- Determines stage-based priorities
- Focuses on requirements, research, and modeling before design/implementation

### 4.4 DirectionGenerator
- Generates Aider-specific directions
- Incorporates current state, priorities, and validation results
- Emphasizes DDD and TDD practices

### 4.5 AiderInterface
- Manages Aider communication
- Handles command sending and result receiving
- Processes errors and unexpected responses

### 4.6 UserInteractionHandler
- Manages user prompts and input
- Integrates user decisions into the workflow

### 4.7 ProgressTracker
- Evaluates completion criteria
- Manages stage transitions
- Ensures artifact completeness before progression

## 5. Stage-Specific Workflows

(Detailed workflows for each stage, similar to the original document)

## 6. Transition Constraints

- Implement strict transition rules between stages
- Require artifact completion/approval before progression
- Example: Prevent Implementation start until Design approval and Test Design completion

## 7. Reporting and Logging

- Generate detailed stage progress reports
- Maintain comprehensive decision and action logs
- Provide clear project evolution visibility

## 8. Golang-Specific Considerations

- Utilize Go's concurrency features for parallel processing where applicable
- Implement robust error handling using Go's error model
- Use Go's strong typing to ensure data integrity throughout the workflow
- Leverage Go's standard library for HTTP communication, file I/O, and other system interactions
- Implement efficient data structures for state management and constraint checking

This Golang-based LLM-Workflow Director design maintains the structured approach to AI-assisted software development, emphasizing DDD and TDD principles while leveraging Go's strengths in performance, concurrency, and type safety.

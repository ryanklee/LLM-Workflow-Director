# LLM-Workflow Director: Workflow Loop Design (Python Implementation)

## 1. Overview

The LLM-Workflow Director is a Python-based system designed to guide AI-assisted software development processes. It emphasizes Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles, ensuring systematic progression through crucial development stages.

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
4. **Context Header Generation**: Create a clear context header for the LLM interaction.
5. **Direction Generation**: Create actionable directions for Claude-Sonnet 3.5 via Aider, emphasizing current priorities.
6. **Aider Execution**: Send context header and directions to Aider and await task completion.
7. **Result Processing**: Analyze Claude-Sonnet 3.5's output and update project state.
8. **User Interaction**: Handle user input when required.
9. **Progress Evaluation**: Assess step/stage completion and manage transitions.

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

### 4.10 LLMContextHeaderGenerator
- Generates a clear and concise context header for each LLM interaction
- Ensures the LLM understands its role and the nature of the interaction
- Formats the header in a way that the LLM recognizes as high-priority information

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

## 12. LLM Context Header Implementation

12.1. Implement the LLMContextHeaderGenerator to create a context header for each interaction:
    a. Clearly state that the directions are for Claude-Sonnet 3.5.
    b. Explain that the directions are being issued by an automated workflow director.
    c. Briefly describe the current stage of the project and the task at hand.
    d. Use a consistent and recognizable format for the header.

12.2. Format the context header for maximum recognition:
    a. Use XML tags to clearly delineate the context header.
    b. Place the context header at the very beginning of each interaction.
    c. Use clear and direct language that the LLM is likely to understand and prioritize.

12.3. Example context header format:
    <context>
    You are Claude-Sonnet 3.5, an AI language model. You are currently being directed by an automated LLM-Workflow Director as part of an AI-assisted software development process. The project is currently in the [CURRENT_STAGE] stage. Your task is to [BRIEF_TASK_DESCRIPTION]. Please process the following directions with this context in mind.
    </context>

12.4. Integrate the context header generation into the DirectionGenerator:
    a. Generate the context header first.
    b. Prepend the context header to the generated directions.
    c. Ensure that all communication with Claude-Sonnet 3.5 includes this context header.

## 13. Information Richness and Documentation Integration

13.1. Implement a DocumentationManager component:
    a. Index and categorize all internal documentation.
    b. Provide fast retrieval of relevant documentation snippets.
    c. Maintain version history of documentation.

13.2. Enhance the DirectionGenerator to include rich information:
    a. Incorporate relevant documentation snippets in generated directions.
    b. Include project state information with each set of directions.
    c. Provide cross-references to related documentation sections.

13.3. Implement a ProjectStateReporter:
    a. Generate comprehensive project state reports.
    b. Link state information to relevant documentation.
    c. Track and report on recent changes and their impacts.

13.4. Create a ContextAwarePromptGenerator:
    a. Generate prompts based on internal documentation content.
    b. Encourage LLM to refer back to specific documentation sections.
    c. Include metadata to help LLM understand information reliability and context.

13.5. Enhance the AiderInterface to handle rich information:
    a. Format rich information for optimal presentation to Claude-Sonnet 3.5.
    b. Handle responses that reference specific documentation sections.
    c. Process and store metadata provided by Claude-Sonnet 3.5 for future reference.

13.6. Implement a CrossReferenceManager:
    a. Maintain relationships between different documentation sections.
    b. Provide relevant cross-references when generating directions or prompts.
    c. Update cross-references as documentation evolves.

13.7. Integrate version control awareness:
    a. Provide version-specific documentation and project state information.
    b. Highlight changes between versions when relevant to the current task.
    c. Maintain a history of documentation and project state changes.
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

1. **CLI Initialization**: Parse command-line arguments and set up the project environment.
2. **State Assessment**: Analyze current project state and determine active stage/step.
3. **Constraint Validation**: Apply and validate constraints for the current stage.
4. **Priority Determination**: Set priorities based on the current stage, adhering to DDD and TDD.
5. **LLM Interaction Preparation**: Prepare context and prompts for LLM interaction.
6. **Sufficiency Evaluation**: Use LLM CLI microservice to evaluate the sufficiency of the current stage.
7. **Direction Generation**: Create actionable directions for Aider, emphasizing current priorities or addressing insufficiencies, using LLM CLI for complex reasoning tasks.
8. **Aider Execution**: Send directions to Aider and await task completion.
9. **Result Processing**: Analyze Aider's output and update project state.
10. **User Interaction**: Handle user input when required.
11. **Progress Evaluation**: Assess step/stage completion and manage transitions based on sufficiency evaluation.
12. **Loop or Exit**: Continue the loop if there are more steps, or exit if the workflow is complete.

## 4. Key Components

### 4.1 StateManager
- Maintains project state
- Tracks workflow progress
- Provides state update and query interfaces
- Utilizes VectorStore for efficient information retrieval

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
- Addresses insufficiencies identified by the LLM
- Utilizes LLM CLI for complex reasoning and task breakdown

### 4.5 AiderInterface
- Manages Aider communication
- Handles command sending and result receiving
- Processes errors and unexpected responses

### 4.6 UserInteractionHandler
- Manages user prompts and input
- Integrates user decisions into the workflow

### 4.7 ProgressTracker
- Evaluates completion criteria
- Manages stage transitions based on LLM sufficiency evaluation
- Ensures artifact completeness before progression

### 4.8 SufficiencyEvaluator
- Utilizes LLM CLI microservice to perform qualitative sufficiency checks for each stage
- Provides context-aware evaluation of project state
- Generates structured responses for programmatic decision-making

### 4.9 LLMClient
- Manages communication with the LLM CLI microservice
- Handles request formatting and response parsing
- Implements error handling and retry mechanisms

### 4.10 VectorStore
- Provides efficient storage and retrieval of project-related information
- Enhances context retrieval for LLM interactions

### 4.11 CacheManager
- Implements caching mechanisms for LLM computations
- Manages cache invalidation and update strategies

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

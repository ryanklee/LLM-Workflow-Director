# LLM-Workflow Director Requirements (Golang Implementation)

1. Project Initialization
   1.1. The system shall bootstrap a project from initial requirements.
   1.2. The system shall create an initial project structure with necessary documents and workflow stages.
   1.3. The system shall identify and load existing project state if resuming an existing project.

2. Workflow Management
   2.1. The system shall define and manage workflow stages and steps, emphasizing Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles.
   2.2. The system shall track the status of each workflow stage and step.
   2.3. The system shall determine the next appropriate workflow step based on current state, validation results, and DDD/TDD priorities.
   2.4. The system shall enforce strict transition rules between stages, requiring approval or completion of key artifacts before progressing.

3. Constraint Management
   3.1. The system shall define and enforce constraints for each workflow step.
   3.2. The system shall validate documents and project state against defined constraints.
   3.3. The system shall provide clear violation messages for failed constraints.
   3.4. The system shall ensure adherence to DDD and TDD principles through specific constraints.

4. Priority Management
   4.1. The system shall determine and enforce priorities based on the current project stage.
   4.2. The system shall focus on requirements elaboration, research gathering, and domain modeling before design and implementation.

5. LLM Direction
   5.1. The system shall generate clear, actionable directions for Claude-Sonnet 3.5 via Aider based on the current workflow step, project state, and priorities.
   5.2. The system shall format its output in a way that is optimized for Claude-Sonnet 3.5's comprehension and processing capabilities.
   5.3. The system shall provide context and rationale for each direction given to Claude-Sonnet 3.5, including relevant project history and decision-making factors.
   5.4. The system shall emphasize DDD and TDD practices in the generated directions, explaining their importance in the current context.
   5.5. The system shall generate output that leverages Claude-Sonnet 3.5's strengths in natural language understanding and generation.
   5.6. The system shall include prompts and questions in its output to encourage Claude-Sonnet 3.5 to think critically about the task at hand.

6. User Interaction
   6.1. The system shall allow for user input at predefined points in the workflow.
   6.2. The system shall incorporate user input into the decision-making process for next steps.

7. Project State Management
   7.1. The system shall maintain a current state of the project, including all documents and their versions.
   7.2. The system shall provide a method to view the current project state.
   7.3. The system shall track changes to the project state over time.

8. Integration with Aider and Claude-Sonnet 3.5
   8.1. The system shall be executable from the command line by Aider.
   8.2. The system shall accept input parameters from Aider, including the current project state.
   8.3. The system shall return output in a format that Aider can parse and act upon.
   8.4. The system shall tailor its output to Claude-Sonnet 3.5's specific capabilities and limitations.
   8.5. The system shall include mechanisms to clarify ambiguities or request additional information from Claude-Sonnet 3.5 when necessary.
   8.6. The system shall provide clear instructions on how to format responses for easy parsing and integration back into the workflow.

9. Extensibility
   9.1. The system shall allow for easy addition of new workflow stages and steps.
   9.2. The system shall support the definition of custom constraints.

10. Reporting and Logging
    10.1. The system shall generate detailed progress reports at the end of each workflow stage.
    10.2. The system shall provide a final project report upon completion of all workflow stages.
    10.3. The system shall maintain a log of all decisions, actions, and transitions.
    10.4. The system shall provide clear visibility into the project's evolution and current state.

11. Performance
    11.1. The system shall process and respond to Aider commands in under 1 second for most operations.
    11.2. The system shall handle projects with up to 100,000 files and 10,000,000 lines of code.

12. Security
    12.1. The system shall not store or transmit sensitive project information outside the local environment.
    12.2. The system shall validate and sanitize all inputs from Aider to prevent injection attacks.

13. Documentation
    13.1. The system shall provide comprehensive documentation on the workflow stages and steps.
    13.2. The system shall include detailed explanations of all constraints and their rationales.
    13.3. The system shall offer examples of correctly formatted Aider commands and system responses.
    13.4. The system shall provide documentation on DDD and TDD principles and how they are applied in the workflow.

14. Testing
    14.1. The system shall include a comprehensive test suite covering all major components and workflows.
    14.2. The system shall support automated testing of new workflow stages and constraints.
    14.3. The system shall provide mechanisms for simulating various project states and user inputs for testing purposes.
    14.4. The system shall include tests to verify adherence to DDD and TDD principles throughout the workflow.

15. Domain-Driven Design Support
    15.1. The system shall guide the creation and refinement of a comprehensive domain model.
    15.2. The system shall facilitate the development of a ubiquitous language for the project.
    15.3. The system shall ensure that design decisions are based on the domain model and requirements.

16. Test-Driven Development Support
    16.1. The system shall guide the creation of test cases based on requirements and design before implementation.
    16.2. The system shall ensure comprehensive test coverage for all implemented features.
    16.3. The system shall direct Aider to run and report on test results regularly throughout the development process.

17. Golang-Specific Requirements
    17.1. The system shall utilize Go's concurrency features for parallel processing where applicable.
    17.2. The system shall implement robust error handling using Go's error model.
    17.3. The system shall use Go's strong typing to ensure data integrity throughout the workflow.
    17.4. The system shall leverage Go's standard library for HTTP communication, file I/O, and other system interactions.
    17.5. The system shall implement efficient data structures for state management and constraint checking.
    17.6. The system shall compile to a single binary for easy distribution and deployment.
    17.7. The system shall support cross-compilation for different target platforms.

18. LLM-Specific Output Enhancements
    18.1. The system shall generate comprehensive project context summaries for Claude-Sonnet 3.5 at the beginning of each interaction.
    18.2. The system shall provide step-by-step guidance for complex tasks, breaking them down into manageable sub-tasks for Claude-Sonnet 3.5.
    18.3. The system shall include relevant code snippets, documentation references, and examples in its output to aid Claude-Sonnet 3.5's understanding and task completion.
    18.4. The system shall generate output that encourages Claude-Sonnet 3.5 to explain its reasoning and decision-making process.
    18.5. The system shall adapt its language complexity and technical depth based on the current project stage and task requirements.
    18.6. The system shall implement best practices for prompt engineering with Claude-Sonnet 3.5, including:
        a. Being clear and direct in instructions and queries.
        b. Using examples (multishot prompting) when appropriate.
        c. Encouraging step-by-step thinking (chain of thought).
        d. Using XML tags to structure prompts and responses.
        e. Assigning specific roles to Claude-Sonnet 3.5 using system prompts.
        f. Prefilling responses when appropriate to guide output format.
        g. Chaining complex prompts for multi-step tasks.
        h. Optimizing prompts for long context windows when necessary.
    18.7. The system shall utilize a prompt generator to create effective prompts for various tasks and scenarios.
    18.8. The system shall implement techniques for handling long contexts, including summarization and relevant information extraction.

19. Prompt Engineering and LLM Interaction
    19.1. The system shall maintain a library of effective prompt templates for common tasks and scenarios.
    19.2. The system shall dynamically generate and refine prompts based on the current project state, task requirements, and previous interactions.
    19.3. The system shall implement a feedback loop to improve prompt effectiveness based on Claude-Sonnet 3.5's responses and task outcomes.
    19.4. The system shall provide clear instructions on how Claude-Sonnet 3.5 should format its responses for easy parsing and integration into the workflow.
    19.5. The system shall implement error handling and retry mechanisms for cases where Claude-Sonnet 3.5's responses are unclear or off-topic.

20. LLM Context Awareness
    20.1. The system shall provide a clear context header at the beginning of each interaction with Claude-Sonnet 3.5.
    20.2. The context header shall inform Claude-Sonnet 3.5 about its role, the nature of the interaction, and the fact that it's being directed by an automated workflow system.
    20.3. The system shall ensure that the context header is formatted in a way that Claude-Sonnet 3.5 recognizes and prioritizes.
# LLM-Workflow Director Requirements (Golang Implementation)

1. Project Initialization
   1.1. The system shall bootstrap a project from initial requirements.
   1.2. The system shall create an initial project structure with necessary documents and workflow stages.
   1.3. The system shall identify and load existing project state if resuming an existing project.

2. Workflow Management
   2.1. The system shall define and manage workflow stages and steps, emphasizing Domain-Driven Design (DDD) and Test-Driven Development (TDD) principles.
   2.2. The system shall track the status of each workflow stage and step.
   2.3. The system shall determine the next appropriate workflow step based on current state, validation results, and DDD/TDD priorities.
   2.4. The system shall enforce strict transition rules between stages, requiring approval or completion of key artifacts before progressing.

3. Constraint Management
   3.1. The system shall define and enforce constraints for each workflow step.
   3.2. The system shall validate documents and project state against defined constraints.
   3.3. The system shall provide clear violation messages for failed constraints.
   3.4. The system shall ensure adherence to DDD and TDD principles through specific constraints.

4. Priority Management
   4.1. The system shall determine and enforce priorities based on the current project stage.
   4.2. The system shall focus on requirements elaboration, research gathering, and domain modeling before design and implementation.

5. LLM Direction
   5.1. The system shall generate clear, actionable directions for Aider based on the current workflow step, project state, and priorities.
   5.2. The system shall format its output in a way that is easily consumable by Aider.
   5.3. The system shall provide context and rationale for each direction given to Aider.
   5.4. The system shall emphasize DDD and TDD practices in the generated directions.

6. User Interaction
   6.1. The system shall allow for user input at predefined points in the workflow.
   6.2. The system shall incorporate user input into the decision-making process for next steps.

7. Project State Management
   7.1. The system shall maintain a current state of the project, including all documents and their versions.
   7.2. The system shall provide a method to view the current project state.
   7.3. The system shall track changes to the project state over time.

8. Integration with Aider
   8.1. The system shall be executable from the command line by Aider.
   8.2. The system shall accept input parameters from Aider, including the current project state.
   8.3. The system shall return output in a format that Aider can parse and act upon.

9. Extensibility
   9.1. The system shall allow for easy addition of new workflow stages and steps.
   9.2. The system shall support the definition of custom constraints.

10. Reporting and Logging
    10.1. The system shall generate detailed progress reports at the end of each workflow stage.
    10.2. The system shall provide a final project report upon completion of all workflow stages.
    10.3. The system shall maintain a log of all decisions, actions, and transitions.
    10.4. The system shall provide clear visibility into the project's evolution and current state.

11. Performance
    11.1. The system shall process and respond to Aider commands in under 1 second for most operations.
    11.2. The system shall handle projects with up to 100,000 files and 10,000,000 lines of code.

12. Security
    12.1. The system shall not store or transmit sensitive project information outside the local environment.
    12.2. The system shall validate and sanitize all inputs from Aider to prevent injection attacks.

13. Documentation
    13.1. The system shall provide comprehensive documentation on the workflow stages and steps.
    13.2. The system shall include detailed explanations of all constraints and their rationales.
    13.3. The system shall offer examples of correctly formatted Aider commands and system responses.
    13.4. The system shall provide documentation on DDD and TDD principles and how they are applied in the workflow.

14. Testing
    14.1. The system shall include a comprehensive test suite covering all major components and workflows.
    14.2. The system shall support automated testing of new workflow stages and constraints.
    14.3. The system shall provide mechanisms for simulating various project states and user inputs for testing purposes.
    14.4. The system shall include tests to verify adherence to DDD and TDD principles throughout the workflow.

15. Domain-Driven Design Support
    15.1. The system shall guide the creation and refinement of a comprehensive domain model.
    15.2. The system shall facilitate the development of a ubiquitous language for the project.
    15.3. The system shall ensure that design decisions are based on the domain model and requirements.

16. Test-Driven Development Support
    16.1. The system shall guide the creation of test cases based on requirements and design before implementation.
    16.2. The system shall ensure comprehensive test coverage for all implemented features.
    16.3. The system shall direct Aider to run and report on test results regularly throughout the development process.

17. Golang-Specific Requirements
    17.1. The system shall utilize Go's concurrency features for parallel processing where applicable.
    17.2. The system shall implement robust error handling using Go's error model.
    17.3. The system shall use Go's strong typing to ensure data integrity throughout the workflow.
    17.4. The system shall leverage Go's standard library for HTTP communication, file I/O, and other system interactions.
    17.5. The system shall implement efficient data structures for state management and constraint checking.
    17.6. The system shall compile to a single binary for easy distribution and deployment.
    17.7. The system shall support cross-compilation for different target platforms.

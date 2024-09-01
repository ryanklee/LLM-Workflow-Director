package cli

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/sufficiency"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

func Run() error {
	fmt.Println("Starting Run function")
	
	// Create a context with a timeout
	ctx, cancel := context.WithTimeout(context.Background(), 4*time.Second)
	defer cancel()

	// Create a channel to receive the result of the run
	done := make(chan error)

	go func() {
		fmt.Println("Entering goroutine")
		// Create a new flag set
		fs := flag.NewFlagSet("workflow", flag.ExitOnError)

		// Define command-line flags
		projectPath := fs.String("project", "", "Path to the project directory")

		// Parse command-line flags
		fmt.Println("Parsing command-line flags")
		fs.Parse(os.Args[1:])

		if *projectPath == "" {
			fmt.Println("Project path is empty")
			done <- errors.New("project path is required. Use -project flag to specify the project directory")
			return
		}

		fmt.Println("Initializing components")
		// Initialize components
		stateManager := state.NewFileStateManager(*projectPath)
		constraintEngine := constraint.NewBasicConstraintEngine()
		priorityManager := priority.NewBasicPriorityManager()
		directionGenerator := direction.NewBasicDirectionGenerator()
		aiderInterface := aider.NewBasicAiderInterface()
		userInteractionHandler := user.NewBasicUserInteractionHandler()
		progressTracker := progress.NewBasicProgressTracker()
		sufficiencyEvaluator := sufficiency.NewLLMEvaluator(aiderInterface)

		fmt.Println("Creating workflow director")
		// Create and run the workflow director
		director := workflow.NewDirector(
			stateManager,
			constraintEngine,
			priorityManager,
			directionGenerator,
			aiderInterface,
			userInteractionHandler,
			progressTracker,
			sufficiencyEvaluator,
		)

		fmt.Println("Running workflow director")
		err := director.Run()
		if err != nil {
			fmt.Printf("Workflow director encountered an error: %v\n", err)
			done <- fmt.Errorf("Workflow director encountered an error: %v", err)
			return
		}

		fmt.Println("Workflow completed successfully.")
		done <- nil
	}()

	fmt.Println("Waiting for goroutine to complete")
	select {
	case <-ctx.Done():
		fmt.Println("Context deadline exceeded")
		return fmt.Errorf("Run function timed out after 4 seconds")
	case err := <-done:
		fmt.Println("Goroutine completed")
		return err
	}
}

package cli

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/component"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/config"
)

func Run() error {
	fmt.Println("Starting Run function")

	// Create a context with a timeout
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// Create a channel to receive the result of the run
	done := make(chan error)

	go func() {
		defer func() {
			if r := recover(); r != nil {
				fmt.Printf("Panic occurred: %v\n", r)
				done <- fmt.Errorf("panic occurred: %v", r)
			}
		}()

		fmt.Println("Entering goroutine")
		// Create a new flag set
		fs := flag.NewFlagSet("workflow", flag.ExitOnError)

		// Define command-line flags
		projectPath := fs.String("project", "", "Path to the project directory")
		configPath := fs.String("config", "", "Path to the configuration file")

		// Parse command-line flags
		fmt.Println("Parsing command-line flags")
		fs.Parse(os.Args[1:])

		if *projectPath == "" {
			fmt.Println("Project path is empty")
			done <- errors.New("project path is required. Use -project flag to specify the project directory")
			return
		}

		// Load configuration
		var cfg *config.WorkflowConfig
		var err error
		if *configPath != "" {
			cfg, err = config.LoadConfig(*configPath)
			if err != nil {
				fmt.Printf("Error loading configuration: %v\n", err)
				fmt.Println("Using default configuration")
				cfg = config.GetDefaultConfig()
			}
		} else {
			fmt.Println("No configuration file specified. Using default configuration")
			cfg = config.GetDefaultConfig()
		}

		fmt.Println("Initializing components")
		start := time.Now()

		// Initialize components based on configuration
		components := make([]component.WorkflowComponent, 0, len(cfg.Components))
		for _, compConfig := range cfg.Components {
			comp, err := createComponent(compConfig, *projectPath)
			if err != nil {
				done <- fmt.Errorf("failed to create component %s: %w", compConfig.Type, err)
				return
			}
			components = append(components, comp)
			fmt.Printf("%s initialization took %v\n", compConfig.Type, time.Since(start))
			start = time.Now()
		}

		fmt.Println("Creating workflow director")
		// Create and run the workflow director
		director, err := workflow.NewDirector(components...)
		if err != nil {
			done <- fmt.Errorf("failed to create workflow director: %w", err)
			return
		}

		fmt.Println("Running workflow director")
		start = time.Now()
		err := director.Run()
		fmt.Printf("Director.Run() took %v\n", time.Since(start))
		if err != nil {
			fmt.Printf("Workflow director encountered an error: %v\n", err)
			done <- fmt.Errorf("workflow director encountered an error: %w", err)
			return
		}

		fmt.Println("Workflow completed successfully.")
		done <- nil
	}()

	fmt.Println("Waiting for goroutine to complete")
	select {
	case <-ctx.Done():
		fmt.Println("Context deadline exceeded")
		return fmt.Errorf("run function timed out after 10 seconds")
	case err := <-done:
		fmt.Println("Goroutine completed")
		return err
	}
}
func createComponent(compConfig config.ComponentConfig, projectPath string) (component.WorkflowComponent, error) {
	switch compConfig.Type {
	case "stateManager":
		return state.NewFileStateManager(projectPath), nil
	case "constraintEngine":
		return constraint.NewBasicConstraintEngine(), nil
	case "priorityManager":
		return priority.NewBasicPriorityManager(), nil
	case "directionGenerator":
		return direction.NewBasicDirectionGenerator(), nil
	case "aiderInterface":
		return aider.NewBasicAiderInterface(), nil
	case "userInteractionHandler":
		return user.NewBasicUserInteractionHandler(), nil
	case "progressTracker":
		return progress.NewBasicProgressTracker(), nil
	case "sufficiencyEvaluator":
		return sufficiency.NewLLMEvaluator(aider.NewBasicAiderInterface()), nil
	default:
		return nil, fmt.Errorf("unknown component type: %s", compConfig.Type)
	}
}

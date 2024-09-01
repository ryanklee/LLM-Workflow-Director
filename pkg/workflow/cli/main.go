package cli

import (
	"errors"
	"flag"
	"fmt"
	"log"

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
	// Parse command-line flags
	projectPath := flag.String("project", "", "Path to the project directory")
	flag.Parse()

	if *projectPath == "" {
		return errors.New("project path is required. Use -project flag to specify the project directory")
	}

	// Initialize components
	stateManager := state.NewFileStateManager(*projectPath)
	constraintEngine := constraint.NewBasicConstraintEngine()
	priorityManager := priority.NewBasicPriorityManager()
	directionGenerator := direction.NewBasicDirectionGenerator()
	aiderInterface := aider.NewBasicAiderInterface()
	userInteractionHandler := user.NewBasicUserInteractionHandler()
	progressTracker := progress.NewBasicProgressTracker()
	sufficiencyEvaluator := sufficiency.NewLLMEvaluator(aiderInterface)

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

	err := director.Run()
	if err != nil {
		log.Fatalf("Workflow director encountered an error: %v", err)
	}

	fmt.Println("Workflow completed successfully.")
	return nil
}

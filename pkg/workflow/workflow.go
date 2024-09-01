package workflow

import (
	"fmt"
	"time"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/sufficiency"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

type Director struct {
	stateManager           state.StateManager
	constraintEngine       constraint.ConstraintEngine
	priorityManager        priority.PriorityManager
	directionGenerator     direction.DirectionGenerator
	aiderInterface         aider.AiderInterface
	userInteractionHandler user.UserInteractionHandler
	progressTracker        progress.ProgressTracker
	sufficiencyEvaluator   sufficiency.Evaluator
}

func NewDirector(
	stateManager state.StateManager,
	constraintEngine constraint.ConstraintEngine,
	priorityManager priority.PriorityManager,
	directionGenerator direction.DirectionGenerator,
	aiderInterface aider.AiderInterface,
	userInteractionHandler user.UserInteractionHandler,
	progressTracker progress.ProgressTracker,
	sufficiencyEvaluator sufficiency.Evaluator,
) *Director {
	return &Director{
		stateManager:           stateManager,
		constraintEngine:       constraintEngine,
		priorityManager:        priorityManager,
		directionGenerator:     directionGenerator,
		aiderInterface:         aiderInterface,
		userInteractionHandler: userInteractionHandler,
		progressTracker:        progressTracker,
		sufficiencyEvaluator:   sufficiencyEvaluator,
	}
}

func (d *Director) Run() error {
	fmt.Println("Director.Run() function started")
	overallStart := time.Now()

	fmt.Println("Determining current state")
	start := time.Now()
	currentState, err := d.stateManager.GetCurrentState()
	if err != nil {
		return fmt.Errorf("error getting current state: %w", err)
	}
	fmt.Printf("GetCurrentState took %v\n", time.Since(start))
	fmt.Printf("Current state: %+v\n", currentState)

	fmt.Println("Determining priorities")
	start = time.Now()
	priorities := d.priorityManager.DeterminePriorities(currentState)
	fmt.Printf("DeterminePriorities took %v\n", time.Since(start))
	fmt.Printf("Priorities: %+v\n", priorities)

	fmt.Println("Generating directions")
	start = time.Now()
	directions, err := d.directionGenerator.Generate(currentState, priorities)
	if err != nil {
		return fmt.Errorf("error generating directions: %w", err)
	}
	fmt.Printf("Generate directions took %v\n", time.Since(start))
	fmt.Printf("Directions: %+v\n", directions)

	fmt.Println("Evaluating sufficiency")
	start = time.Now()
	sufficient, err := d.sufficiencyEvaluator.Evaluate(currentState, directions)
	if err != nil {
		return fmt.Errorf("error evaluating sufficiency: %w", err)
	}
	fmt.Printf("Evaluate sufficiency took %v\n", time.Since(start))
	fmt.Printf("Sufficiency: %t\n", sufficient)

	fmt.Println("Updating state")
	start = time.Now()
	err = d.stateManager.UpdateState(currentState)
	if err != nil {
		return fmt.Errorf("error updating state: %w", err)
	}
	fmt.Printf("UpdateState took %v\n", time.Since(start))

	fmt.Printf("Director.Run() function completed in %v\n", time.Since(overallStart))
	return nil
}

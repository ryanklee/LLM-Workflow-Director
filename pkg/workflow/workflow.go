package workflow

import (
	"fmt"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/component"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/constraint"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/direction"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/priority"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/progress"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/state"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/sufficiency"
	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/user"
)

func NewFileStateManager(projectPath string) component.WorkflowComponent {
	sm := state.NewFileStateManager(projectPath)
	fmt.Printf("Created FileStateManager: %T\n", sm)
	return &componentWrapper{component: sm, name: "FileStateManager"}
}

func NewBasicConstraintEngine() component.WorkflowComponent {
	ce := constraint.NewBasicConstraintEngine()
	return &componentWrapper{ce, "BasicConstraintEngine"}
}

func NewBasicPriorityManager() component.WorkflowComponent {
	pm := priority.NewBasicPriorityManager()
	return &componentWrapper{pm, "BasicPriorityManager"}
}

func NewBasicDirectionGenerator() component.WorkflowComponent {
	dg := direction.NewBasicDirectionGenerator()
	return &componentWrapper{dg, "BasicDirectionGenerator"}
}

func NewBasicAiderInterface() component.WorkflowComponent {
	ai := aider.NewBasicAiderInterface()
	return &componentWrapper{ai, "BasicAiderInterface"}
}

func NewBasicUserInteractionHandler() component.WorkflowComponent {
	uih := user.NewBasicUserInteractionHandler()
	return &componentWrapper{uih, "BasicUserInteractionHandler"}
}

func NewBasicProgressTracker() component.WorkflowComponent {
	pt := progress.NewBasicProgressTracker()
	return &componentWrapper{pt, "BasicProgressTracker"}
}

func NewLLMEvaluator(ai component.WorkflowComponent) component.WorkflowComponent {
	se := sufficiency.NewLLMEvaluator(ai.(*componentWrapper).component.(aider.AiderInterface))
	return &componentWrapper{se, "LLMEvaluator"}
}

type componentWrapper struct {
	component interface{}
	name      string
}

func (cw *componentWrapper) Name() string {
	return cw.name
}

func (cw *componentWrapper) Execute(state interface{}) (interface{}, error) {
	fmt.Printf("Executing component: %s\n", cw.name)
	fmt.Printf("Component type: %T\n", cw.component)
	switch cw.name {
	case "FileStateManager":
		if sm, ok := cw.component.(state.StateManager); ok {
			fmt.Println("Successfully type-asserted to StateManager")
			return state, sm.UpdateState(state)
		} else {
			fmt.Printf("Failed to type-assert to StateManager. Actual type: %T\n", cw.component)
		}
	case "BasicConstraintEngine":
		if ce, ok := cw.component.(constraint.ConstraintEngine); ok {
			return state, ce.Validate(state)
		}
	case "BasicPriorityManager":
		if pm, ok := cw.component.(priority.PriorityManager); ok {
			return pm.DeterminePriorities(state), nil
		}
	case "BasicDirectionGenerator":
		if dg, ok := cw.component.(direction.DirectionGenerator); ok {
			return dg.Generate(state, nil)
		}
	case "BasicAiderInterface":
		if ai, ok := cw.component.(aider.AiderInterface); ok {
			return ai.Execute(state)
		}
	case "BasicUserInteractionHandler":
		if uih, ok := cw.component.(user.UserInteractionHandler); ok {
			return uih.HandleInteraction(state)
		}
	case "BasicProgressTracker":
		if pt, ok := cw.component.(progress.ProgressTracker); ok {
			return state, pt.UpdateProgress(state)
		}
	case "LLMEvaluator":
		if se, ok := cw.component.(sufficiency.Evaluator); ok {
			sufficient, reason, err := se.Evaluate(state)
			if err != nil {
				return state, err
			}
			return map[string]interface{}{"state": state, "sufficient": sufficient, "reason": reason}, nil
		}
	}
	fmt.Printf("No matching case for component: %s\n", cw.name)
	return state, nil
}

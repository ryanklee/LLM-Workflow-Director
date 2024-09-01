package workflow

import (
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
	return &componentWrapper{sm, "FileStateManager"}
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
	switch c := cw.component.(type) {
	case state.StateManager:
		return state, c.UpdateState(state)
	case constraint.ConstraintEngine:
		return state, c.Validate(state)
	case priority.PriorityManager:
		return c.DeterminePriorities(state), nil
	case direction.DirectionGenerator:
		return c.Generate(state, nil)
	case aider.AiderInterface:
		return c.Execute(state)
	case user.UserInteractionHandler:
		return state, nil // Implement user interaction logic
	case progress.ProgressTracker:
		return state, c.UpdateProgress(state)
	case sufficiency.Evaluator:
		sufficient, reason, err := c.Evaluate(state)
		if err != nil {
			return state, err
		}
		return map[string]interface{}{"state": state, "sufficient": sufficient, "reason": reason}, nil
	default:
		return state, nil
	}
}

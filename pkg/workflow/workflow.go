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
	switch cw.name {
	case "FileStateManager":
		return state, cw.component.(state.StateManager).UpdateState(state)
	case "BasicConstraintEngine":
		return state, cw.component.(constraint.ConstraintEngine).Validate(state)
	case "BasicPriorityManager":
		return cw.component.(priority.PriorityManager).DeterminePriorities(state), nil
	case "BasicDirectionGenerator":
		return cw.component.(direction.DirectionGenerator).Generate(state, nil)
	case "BasicAiderInterface":
		return cw.component.(aider.AiderInterface).Execute(state)
	case "BasicUserInteractionHandler":
		return state, nil // Implement user interaction logic
	case "BasicProgressTracker":
		return state, cw.component.(progress.ProgressTracker).UpdateProgress(state)
	case "LLMEvaluator":
		sufficient, reason, err := cw.component.(sufficiency.Evaluator).Evaluate(state)
		if err != nil {
			return state, err
		}
		return map[string]interface{}{"state": state, "sufficient": sufficient, "reason": reason}, nil
	default:
		return state, nil
	}
}

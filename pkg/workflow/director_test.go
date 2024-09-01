package workflow

import (
	"testing"
	"time"
)

// MockStateManager implements StateManager interface
type MockStateManager struct{}

func (m *MockStateManager) GetCurrentState() (interface{}, error) { return nil, nil }
func (m *MockStateManager) UpdateState(interface{}) error         { return nil }

// MockConstraintEngine implements constraint.ConstraintEngine interface
type MockConstraintEngine struct{}

func (m *MockConstraintEngine) Validate(interface{}) error { return nil }

// MockPriorityManager implements priority.PriorityManager interface
type MockPriorityManager struct{}

func (m *MockPriorityManager) DeterminePriorities(interface{}) interface{} { return nil }

// MockDirectionGenerator implements direction.DirectionGenerator interface
type MockDirectionGenerator struct{}

func (m *MockDirectionGenerator) Generate(interface{}, interface{}) (interface{}, error) {
	return nil, nil
}
func (m *MockDirectionGenerator) GenerateForInsufficiency(interface{}, interface{}, string) (interface{}, error) {
	return nil, nil
}

// MockAiderInterface implements aider.AiderInterface interface
type MockAiderInterface struct{}

func (m *MockAiderInterface) Execute(interface{}) (interface{}, error) { return nil, nil }

// MockUserInteractionHandler implements user.UserInteractionHandler interface
type MockUserInteractionHandler struct{}

func (m *MockUserInteractionHandler) IsInteractionRequired(interface{}) bool { return false }

// MockProgressTracker implements progress.ProgressTracker interface
type MockProgressTracker struct {
	completeAfter time.Time
}

func (m *MockProgressTracker) IsComplete(interface{}) bool {
	return time.Now().After(m.completeAfter)
}
func (m *MockProgressTracker) UpdateProgress(interface{}) error { return nil }

// MockSufficiencyEvaluator implements sufficiency.Evaluator interface
type MockSufficiencyEvaluator struct{}

func (m *MockSufficiencyEvaluator) Evaluate(interface{}) (bool, string, error) { return true, "", nil }

func TestNewDirector(t *testing.T) {
	director := NewDirector(
		&MockStateManager{},
		&MockConstraintEngine{},
		&MockPriorityManager{},
		&MockDirectionGenerator{},
		&MockAiderInterface{},
		&MockUserInteractionHandler{},
		&MockProgressTracker{completeAfter: time.Now().Add(100 * time.Millisecond)},
		&MockSufficiencyEvaluator{},
	)
	if director == nil {
		t.Error("NewDirector() returned nil")
	}
}

func TestDirectorRun(t *testing.T) {
	director := NewDirector(
		&MockStateManager{},
		&MockConstraintEngine{},
		&MockPriorityManager{},
		&MockDirectionGenerator{},
		&MockAiderInterface{},
		&MockUserInteractionHandler{},
		&MockProgressTracker{completeAfter: time.Now().Add(100 * time.Millisecond)},
		&MockSufficiencyEvaluator{},
	)
	err := director.Run()
	if err != nil {
		t.Errorf("Director.Run() returned an error: %v", err)
	}
}
package workflow

import (
	"testing"
	"time"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/component"
)

type MockStateManager struct{}

func (m *MockStateManager) GetCurrentState() (interface{}, error) { return nil, nil }
func (m *MockStateManager) UpdateState(interface{}) error         { return nil }
func (m *MockStateManager) Name() string                          { return "MockStateManager" }
func (m *MockStateManager) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockConstraintEngine struct{}

func (m *MockConstraintEngine) Name() string                          { return "MockConstraintEngine" }
func (m *MockConstraintEngine) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockPriorityManager struct{}

func (m *MockPriorityManager) Name() string                          { return "MockPriorityManager" }
func (m *MockPriorityManager) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockDirectionGenerator struct{}

func (m *MockDirectionGenerator) Name() string                          { return "MockDirectionGenerator" }
func (m *MockDirectionGenerator) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockAiderInterface struct{}

func (m *MockAiderInterface) Name() string                          { return "MockAiderInterface" }
func (m *MockAiderInterface) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockUserInteractionHandler struct{}

func (m *MockUserInteractionHandler) Name() string                          { return "MockUserInteractionHandler" }
func (m *MockUserInteractionHandler) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockProgressTracker struct {
	completeAfter time.Time
}

func (m *MockProgressTracker) Name() string                          { return "MockProgressTracker" }
func (m *MockProgressTracker) Execute(state interface{}) (interface{}, error) { return state, nil }

type MockSufficiencyEvaluator struct{}

func (m *MockSufficiencyEvaluator) Name() string                          { return "MockSufficiencyEvaluator" }
func (m *MockSufficiencyEvaluator) Execute(state interface{}) (interface{}, error) { return state, nil }

func TestNewDirector(t *testing.T) {
	components := []component.WorkflowComponent{
		&MockStateManager{},
		&MockConstraintEngine{},
		&MockPriorityManager{},
		&MockDirectionGenerator{},
		&MockAiderInterface{},
		&MockUserInteractionHandler{},
		&MockProgressTracker{completeAfter: time.Now().Add(2 * time.Second)},
		&MockSufficiencyEvaluator{},
	}

	director, err := NewDirector(components...)
	if err != nil {
		t.Fatalf("Failed to create Director: %v", err)
	}

	if director == nil {
		t.Fatal("Director is nil")
	}

	if len(director.components) != len(components) {
		t.Errorf("Expected %d components, got %d", len(components), len(director.components))
	}

	if director.mediator == nil {
		t.Fatal("Mediator is nil")
	}
}

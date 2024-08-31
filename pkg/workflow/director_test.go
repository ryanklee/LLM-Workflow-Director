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

func (m *MockDirectionGenerator) Generate(interface{}, interface{}) (interface{}, error) { return nil, nil }
func (m *MockDirectionGenerator) GenerateForInsufficiency(interface{}, interface{}, string) (interface{}, error) { return nil, nil }

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

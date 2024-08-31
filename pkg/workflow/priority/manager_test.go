package priority

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockPriorityManager struct {
	mock.Mock
}

func (m *MockPriorityManager) DeterminePriorities(state interface{}) interface{} {
	args := m.Called(state)
	return args.Get(0)
}

func TestPriorityManager(t *testing.T) {
	mockManager := new(MockPriorityManager)

	t.Run("DeterminePriorities", func(t *testing.T) {
		state := map[string]string{"stage": "design"}
		expectedPriorities := []string{"architecture", "interfaces", "data models"}
		mockManager.On("DeterminePriorities", state).Return(expectedPriorities)

		priorities := mockManager.DeterminePriorities(state)

		assert.Equal(t, expectedPriorities, priorities)
		mockManager.AssertExpectations(t)
	})
}

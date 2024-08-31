package sufficiency

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockAiderInterface struct {
	mock.Mock
}

func (m *MockAiderInterface) Execute(input interface{}) (interface{}, error) {
	args := m.Called(input)
	return args.Get(0), args.Error(1)
}

func TestLLMEvaluator(t *testing.T) {
	mockAider := new(MockAiderInterface)
	evaluator := NewLLMEvaluator(mockAider)

	t.Run("Evaluate sufficient state", func(t *testing.T) {
		state := map[string]string{"stage": "design", "status": "complete"}
		expectedPrompt := generateEvaluationPrompt(state)
		mockAider.On("Execute", expectedPrompt).Return(`{"sufficient": true, "reason": "Design is complete"}`, nil)

		sufficient, reason, err := evaluator.Evaluate(state)

		assert.NoError(t, err)
		assert.True(t, sufficient)
		assert.Equal(t, "Design is complete", reason)
		mockAider.AssertExpectations(t)
	})

	t.Run("Evaluate insufficient state", func(t *testing.T) {
		state := map[string]string{"stage": "implementation", "status": "in_progress"}
		expectedPrompt := generateEvaluationPrompt(state)
		mockAider.On("Execute", expectedPrompt).Return(`{"sufficient": false, "reason": "Implementation is not complete"}`, nil)

		sufficient, reason, err := evaluator.Evaluate(state)

		assert.NoError(t, err)
		assert.False(t, sufficient)
		assert.Equal(t, "Implementation is not complete", reason)
		mockAider.AssertExpectations(t)
	})
}

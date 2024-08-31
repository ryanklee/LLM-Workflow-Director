package constraint

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockConstraintEngine struct {
	mock.Mock
}

func (m *MockConstraintEngine) Validate(state interface{}) error {
	args := m.Called(state)
	return args.Error(0)
}

func TestConstraintEngine(t *testing.T) {
	mockEngine := new(MockConstraintEngine)

	t.Run("Validate success", func(t *testing.T) {
		state := map[string]string{"key": "value"}
		mockEngine.On("Validate", state).Return(nil)

		err := mockEngine.Validate(state)

		assert.NoError(t, err)
		mockEngine.AssertExpectations(t)
	})

	t.Run("Validate error", func(t *testing.T) {
		state := map[string]string{"key": "invalid"}
		expectedError := errors.New("validation failed")
		mockEngine.On("Validate", state).Return(expectedError)

		err := mockEngine.Validate(state)

		assert.Error(t, err)
		assert.Equal(t, expectedError, err)
		mockEngine.AssertExpectations(t)
	})
}

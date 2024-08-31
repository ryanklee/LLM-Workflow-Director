package state

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockStateManager struct {
	mock.Mock
}

func (m *MockStateManager) GetCurrentState() (interface{}, error) {
	args := m.Called()
	return args.Get(0), args.Error(1)
}

func (m *MockStateManager) UpdateState(state interface{}) error {
	args := m.Called(state)
	return args.Error(0)
}

func TestStateManager(t *testing.T) {
	mockManager := new(MockStateManager)

	t.Run("GetCurrentState success", func(t *testing.T) {
		expectedState := map[string]string{"key": "value"}
		mockManager.On("GetCurrentState").Return(expectedState, nil)

		state, err := mockManager.GetCurrentState()

		assert.NoError(t, err)
		assert.Equal(t, expectedState, state)
		mockManager.AssertExpectations(t)
	})

	t.Run("GetCurrentState error", func(t *testing.T) {
		expectedError := errors.New("state retrieval failed")
		mockManager.On("GetCurrentState").Return(nil, expectedError).Once()

		state, err := mockManager.GetCurrentState()

		assert.Error(t, err)
		assert.Equal(t, expectedError, err)
		assert.Nil(t, state)
		mockManager.AssertExpectations(t)
	})

	t.Run("UpdateState success", func(t *testing.T) {
		newState := map[string]string{"key": "new value"}
		mockManager.On("UpdateState", newState).Return(nil)

		err := mockManager.UpdateState(newState)

		assert.NoError(t, err)
		mockManager.AssertExpectations(t)
	})

	t.Run("UpdateState error", func(t *testing.T) {
		newState := map[string]string{"key": "invalid"}
		expectedError := errors.New("state update failed")
		mockManager.On("UpdateState", newState).Return(expectedError)

		err := mockManager.UpdateState(newState)

		assert.Error(t, err)
		assert.Equal(t, expectedError, err)
		mockManager.AssertExpectations(t)
	})
}

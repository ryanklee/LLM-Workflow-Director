package aider

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockAider struct {
	mock.Mock
}

func (m *MockAider) Execute(input interface{}) (interface{}, error) {
	args := m.Called(input)
	return args.Get(0), args.Error(1)
}

func TestAiderInterface(t *testing.T) {
	mockAider := new(MockAider)

	t.Run("Execute success", func(t *testing.T) {
		input := "test input"
		expectedOutput := "test output"
		mockAider.On("Execute", input).Return(expectedOutput, nil)

		output, err := mockAider.Execute(input)

		assert.NoError(t, err)
		assert.Equal(t, expectedOutput, output)
		mockAider.AssertExpectations(t)
	})

	t.Run("Execute error", func(t *testing.T) {
		input := "test input"
		expectedError := errors.New("execution failed")
		mockAider.On("Execute", input).Return(nil, expectedError).Once()

		output, err := mockAider.Execute(input)

		assert.Error(t, err)
		assert.Equal(t, expectedError, err)
		assert.Nil(t, output)
		mockAider.AssertExpectations(t)
	})

	// Reset mock for the next test
	mockAider = new(MockAider)
}

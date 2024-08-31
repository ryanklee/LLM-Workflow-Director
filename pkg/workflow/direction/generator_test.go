package direction

import (
	"errors"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockDirectionGenerator struct {
	mock.Mock
}

func (m *MockDirectionGenerator) Generate(state interface{}, priorities interface{}) (interface{}, error) {
	args := m.Called(state, priorities)
	return args.Get(0), args.Error(1)
}

func TestDirectionGenerator(t *testing.T) {
	mockGenerator := new(MockDirectionGenerator)

	t.Run("Generate success", func(t *testing.T) {
		state := map[string]string{"stage": "design"}
		priorities := []string{"architecture", "interfaces"}
		expectedDirections := []string{"Create high-level architecture diagram", "Define key interfaces"}
		mockGenerator.On("Generate", state, priorities).Return(expectedDirections, nil)

		directions, err := mockGenerator.Generate(state, priorities)

		assert.NoError(t, err)
		assert.Equal(t, expectedDirections, directions)
		mockGenerator.AssertExpectations(t)
	})

	t.Run("Generate error", func(t *testing.T) {
		state := map[string]string{"stage": "invalid"}
		priorities := []string{"unknown"}
		expectedError := errors.New("direction generation failed")
		mockGenerator.On("Generate", state, priorities).Return(nil, expectedError)

		directions, err := mockGenerator.Generate(state, priorities)

		assert.Error(t, err)
		assert.Equal(t, expectedError, err)
		assert.Nil(t, directions)
		mockGenerator.AssertExpectations(t)
	})
}

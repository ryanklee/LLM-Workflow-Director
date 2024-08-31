package state

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type FileStateManager struct {
	projectPath string
}

func NewFileStateManager(projectPath string) *FileStateManager {
	return &FileStateManager{projectPath: projectPath}
}

func (f *FileStateManager) GetCurrentState() (interface{}, error) {
	statePath := filepath.Join(f.projectPath, "state.json")
	data, err := os.ReadFile(statePath)
	if err != nil {
		if os.IsNotExist(err) {
			return map[string]interface{}{}, nil
		}
		return nil, fmt.Errorf("error reading state file: %w", err)
	}

	var state map[string]interface{}
	err = json.Unmarshal(data, &state)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling state: %w", err)
	}

	return state, nil
}

func (f *FileStateManager) UpdateState(state interface{}) error {
	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return fmt.Errorf("error marshaling state: %w", err)
	}

	statePath := filepath.Join(f.projectPath, "state.json")
	err = os.WriteFile(statePath, data, 0644)
	if err != nil {
		return fmt.Errorf("error writing state file: %w", err)
	}

	return nil
}

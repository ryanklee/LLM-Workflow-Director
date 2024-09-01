package config

import (
	"encoding/json"
	"fmt"
	"os"
)

type WorkflowConfig struct {
	Components  []ComponentConfig  `json:"components"`
	Constraints []ConstraintConfig `json:"constraints"`
}

type ComponentConfig struct {
	Type    string                 `json:"type"`
	Options map[string]interface{} `json:"options"`
}

type ConstraintConfig struct {
	Type    string                 `json:"type"`
	Options map[string]interface{} `json:"options"`
}

func LoadConfig(filePath string) (*WorkflowConfig, error) {
	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read configuration file: %w", err)
	}

	var config WorkflowConfig
	err = json.Unmarshal(data, &config)
	if err != nil {
		return nil, fmt.Errorf("failed to parse configuration file: %w", err)
	}

	err = validateConfig(&config)
	if err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	return &config, nil
}

func validateConfig(config *WorkflowConfig) error {
	if len(config.Components) == 0 {
		return fmt.Errorf("at least one component must be specified")
	}
	// Add more validation logic as needed
	return nil
}

func GetDefaultConfig() *WorkflowConfig {
	return &WorkflowConfig{
		Components: []ComponentConfig{
			{Type: "stateManager", Options: map[string]interface{}{}},
			{Type: "constraintEngine", Options: map[string]interface{}{}},
			{Type: "priorityManager", Options: map[string]interface{}{}},
			{Type: "directionGenerator", Options: map[string]interface{}{}},
			{Type: "aiderInterface", Options: map[string]interface{}{}},
			{Type: "userInteractionHandler", Options: map[string]interface{}{}},
			{Type: "progressTracker", Options: map[string]interface{}{}},
			{Type: "sufficiencyEvaluator", Options: map[string]interface{}{}},
		},
		Constraints: []ConstraintConfig{},
	}
}

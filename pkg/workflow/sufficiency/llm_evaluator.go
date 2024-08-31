package sufficiency

import (
	"encoding/json"
	"fmt"

	"github.com/rlk/LLM-Workflow-Director/pkg/workflow/aider"
)

type LLMEvaluator struct {
	aiderInterface aider.AiderInterface
}

func NewLLMEvaluator(ai aider.AiderInterface) *LLMEvaluator {
	return &LLMEvaluator{aiderInterface: ai}
}

func (e *LLMEvaluator) Evaluate(state interface{}) (bool, string, error) {
	prompt := generateEvaluationPrompt(state)
	result, err := e.aiderInterface.Execute(prompt)
	if err != nil {
		return false, "", fmt.Errorf("error executing LLM evaluation: %w", err)
	}

	var response struct {
		Sufficient bool   `json:"sufficient"`
		Reason     string `json:"reason"`
	}

	err = json.Unmarshal([]byte(result.(string)), &response)
	if err != nil {
		return false, "", fmt.Errorf("error parsing LLM response: %w", err)
	}

	return response.Sufficient, response.Reason, nil
}

func generateEvaluationPrompt(state interface{}) string {
	// TODO: Implement a more sophisticated prompt generation based on the state
	return fmt.Sprintf(`
Evaluate the sufficiency of the current project state:
%+v

Respond with a JSON object containing:
1. "sufficient": a boolean indicating whether the current state is sufficient to proceed
2. "reason": a string explaining the evaluation

Example response:
{"sufficient": true, "reason": "All required artifacts are complete and validated."}
`, state)
}

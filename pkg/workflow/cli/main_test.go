package cli

import (
	"flag"
	"os"
	"path/filepath"
	"testing"
)

func TestRun(t *testing.T) {
	// Save original args and restore them after the test
	originalArgs := os.Args
	defer func() { os.Args = originalArgs }()

	t.Run("Missing project path", func(t *testing.T) {
		// Set args for this test
		os.Args = []string{"cmd"}
		flag.CommandLine = flag.NewFlagSet(os.Args[0], flag.ExitOnError)

		err := Run()
		if err == nil {
			t.Error("Expected an error when project path is missing, but got nil")
		}
	})

	t.Run("Valid project path", func(t *testing.T) {
		// Create a temporary directory for the test project
		tempDir, err := os.MkdirTemp("", "test-project")
		if err != nil {
			t.Fatalf("Failed to create temp directory: %v", err)
		}
		defer os.RemoveAll(tempDir) // Clean up after the test

		// Create an initial state file with valid JSON
		initialState := []byte(`{"stage": "initialization"}`)
		err = os.WriteFile(filepath.Join(tempDir, "state.json"), initialState, 0644)
		if err != nil {
			t.Fatalf("Failed to create initial state file: %v", err)
		}

		// Set args for this test
		os.Args = []string{"cmd", "-project", tempDir}
		flag.CommandLine = flag.NewFlagSet(os.Args[0], flag.ExitOnError)

		err = Run()
		if err != nil {
			t.Errorf("Expected no error with valid project path, but got: %v", err)
		}
	})
}

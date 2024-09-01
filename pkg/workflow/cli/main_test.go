package cli

import (
	"os"
	"path/filepath"
	"testing"
)

func TestRun(t *testing.T) {
	// Save original args and restore them after the test
	originalArgs := os.Args
	defer func() { os.Args = originalArgs }()

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

	// Set up test args
	os.Args = []string{"cmd", "-project", tempDir}

	// TODO: Mock dependencies and add more detailed tests

	// For now, just ensure it doesn't panic
	Run()
}
package main

import (
	"os"
	"testing"
)

func TestRun(t *testing.T) {
	t.Run("Missing project path", func(t *testing.T) {
		// Save original args
		oldArgs := os.Args
		defer func() { os.Args = oldArgs }()

		// Set args for this test
		os.Args = []string{"cmd", "-project", ""}

		err := Run()
		if err == nil {
			t.Error("Expected an error when project path is missing, but got nil")
		}
	})

	t.Run("Valid project path", func(t *testing.T) {
		// Save original args
		oldArgs := os.Args
		defer func() { os.Args = oldArgs }()

		// Set args for this test
		os.Args = []string{"cmd", "-project", "/tmp/test-project"}

		err := Run()
		if err != nil {
			t.Errorf("Expected no error with valid project path, but got: %v", err)
		}
	})
}

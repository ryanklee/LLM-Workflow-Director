package cli

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"testing"
	"time"
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
		oldArgs := os.Args
		os.Args = []string{"cmd", "-project", tempDir}
		defer func() { os.Args = oldArgs }()

		// Create a channel to signal test completion
		done := make(chan bool)

		// Run the test in a goroutine
		go func() {
			fmt.Println("Starting Run() function...")
			err := Run()
			fmt.Println("Run() function completed")
			if err != nil {
				t.Errorf("Expected no error with valid project path, but got: %v", err)
			}
			done <- true
		}()

		// Wait for the test to complete or timeout
		select {
		case <-done:
			fmt.Println("Test completed successfully")
		case <-time.After(5 * time.Second):
			t.Fatal("Test timed out after 5 seconds")
		}
	})
}

import pytest
import json
from pathlib import Path
from update_test_progress import parse_json_report, update_test_progress_md

@pytest.fixture
def sample_json_report():
    return {
        "created": 1632825600,
        "duration": 10.5,
        "exitcode": 0,
        "root": "/path/to/project",
        "environment": {
            "Python": "3.9.5",
            "Platform": "Linux-5.4.0-42-generic-x86_64-with-glibc2.29"
        },
        "summary": {
            "passed": 95,
            "failed": 5,
            "total": 100
        },
        "tests": [
            {
                "name": "test_failing_1",
                "outcome": "failed",
                "duration": 0.1,
                "call": {
                    "longrepr": "AssertionError: assert 1 == 2"
                }
            },
            {
                "name": "test_passing_1",
                "outcome": "passed",
                "duration": 0.05
            }
        ]
    }

@pytest.fixture
def temp_md_file(tmp_path):
    md_file = tmp_path / "TEST_PROBLEM_PROGRESS.md"
    md_file.write_text("# Test Problem Analysis and Progress\n\n")
    return md_file

def test_parse_json_report(sample_json_report):
    result = parse_json_report(sample_json_report)
    assert result["date"] == "2021-09-28"
    assert result["duration"] == 10.5
    assert result["total_tests"] == 100
    assert result["passed_tests"] == 95
    assert result["failed_tests"] == 5
    assert len(result["failing_test_names"]) == 1
    assert result["failing_test_names"][0] == "test_failing_1"

def test_update_test_progress_md(temp_md_file, sample_json_report):
    update_test_progress_md(temp_md_file, sample_json_report)
    content = temp_md_file.read_text()
    assert "# Test Problem Analysis and Progress" in content
    assert "## Test Run: 2021-09-28" in content
    assert "Total tests: 100" in content
    assert "Passed tests: 95" in content
    assert "Failed tests: 5" in content
    assert "test_failing_1" in content
    assert "Duration: 10.5 seconds" in content

import json
from datetime import datetime
from pathlib import Path

def parse_json_report(report):
    return {
        "date": datetime.fromtimestamp(report["created"]).strftime("%Y-%m-%d"),
        "duration": report["duration"],
        "total_tests": report["summary"]["total"],
        "passed_tests": report["summary"]["passed"],
        "failed_tests": report["summary"]["failed"],
        "failing_test_names": [test["name"] for test in report["tests"] if test["outcome"] == "failed"]
    }

def update_test_progress_md(md_file: Path, json_report: dict):
    parsed_report = parse_json_report(json_report)
    
    with md_file.open("a") as f:
        f.write(f"\n## Test Run: {parsed_report['date']}\n")
        f.write(f"Total tests: {parsed_report['total_tests']}\n")
        f.write(f"Passed tests: {parsed_report['passed_tests']}\n")
        f.write(f"Failed tests: {parsed_report['failed_tests']}\n")
        f.write(f"Duration: {parsed_report['duration']} seconds\n")
        
        if parsed_report['failing_test_names']:
            f.write("\nFailing tests:\n")
            for test_name in parsed_report['failing_test_names']:
                f.write(f"- {test_name}\n")
        f.write("\n")

if __name__ == "__main__":
    json_report_path = Path("pytest_report.json")
    md_file_path = Path("TEST_PROBLEM_PROGRESS.md")
    
    with json_report_path.open() as f:
        json_report = json.load(f)
    
    update_test_progress_md(md_file_path, json_report)

import subprocess
import smtplib
from email.mime.text import MIMEText
import json
import os
import re

def run_tests():
    result = subprocess.run(['pytest', '--benchmark-json=output.json'], capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr

def parse_benchmark_results():
    with open('output.json', 'r') as f:
        data = json.load(f)
    return {benchmark['name']: benchmark['stats']['mean'] for benchmark in data['benchmarks']}

def parse_coverage_results(stdout):
    coverage_match = re.search(r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+%)', stdout)
    if coverage_match:
        statements, missing, coverage = coverage_match.groups()
        return int(statements), int(missing), coverage
    return None, None, None

def compare_results(current_results, previous_results):
    alerts = []
    for name, current_mean in current_results.items():
        if name in previous_results:
            previous_mean = previous_results[name]
            if current_mean > previous_mean * 1.1:  # 10% slower
                alerts.append(f"Performance regression in {name}: {previous_mean:.4f}s -> {current_mean:.4f}s")
    return alerts

def send_alert(message):
    sender = "your_email@example.com"
    receiver = "alert_recipient@example.com"
    
    msg = MIMEText(message)
    msg['Subject'] = "Test Performance and Coverage Alert"
    msg['From'] = sender
    msg['To'] = receiver
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(sender, "your_password")
        server.send_message(msg)

def main():
    success, stdout, stderr = run_tests()
    
    if not success:
        send_alert(f"Tests failed:\n\nStdout:\n{stdout}\n\nStderr:\n{stderr}")
        return
    
    current_results = parse_benchmark_results()
    statements, missing, coverage = parse_coverage_results(stdout)
    
    if os.path.exists('previous_results.json'):
        with open('previous_results.json', 'r') as f:
            previous_results = json.load(f)
        
        alerts = compare_results(current_results, previous_results)
        
        if alerts:
            alert_message = "\n".join(alerts)
            alert_message += f"\n\nCoverage: {coverage} ({statements} statements, {missing} missing)"
            send_alert(alert_message)
    
    with open('previous_results.json', 'w') as f:
        json.dump(current_results, f)

if __name__ == "__main__":
    main()

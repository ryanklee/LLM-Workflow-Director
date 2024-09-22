import pytest
from src.claude_manager import ClaudeManager
from tests.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    return ClaudeManager(client=MockClaudeClient())

# ... (previous tests remain unchanged)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_code_generation_performance(benchmark, claude_manager):
    prompt = "Generate a Python function to calculate the Fibonacci sequence up to n terms."
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_code_review_performance(benchmark, claude_manager):
    code_to_review = """
def calculate_average(numbers):
    sum = 0
    for i in range(len(numbers)):
        sum += numbers[i]
    average = sum / len(numbers)
    return average
    """
    prompt = f"Review the following Python function and suggest improvements:\n\n{code_to_review}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_architecture_suggestion_performance(benchmark, claude_manager):
    prompt = """
    Suggest a microservices architecture for an e-commerce application with the following requirements:
    - User authentication and authorization
    - Product catalog management
    - Shopping cart functionality
    - Order processing
    - Payment integration
    - Inventory management
    - Shipping and delivery tracking
    """
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_unit_test_generation_performance(benchmark, claude_manager):
    function_spec = """
    Function name: calculate_discount
    Parameters:
    - price (float): The original price of the item
    - discount_percentage (float): The discount percentage (0-100)
    
    Returns:
    - float: The discounted price
    
    Description:
    Calculate the discounted price of an item given the original price and discount percentage.
    The function should handle invalid inputs (negative prices or discount percentages outside 0-100 range) by raising a ValueError.
    """
    prompt = f"Generate unit test cases for the following function specification:\n\n{function_spec}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_api_documentation_generation_performance(benchmark, claude_manager):
    class_to_document = """
class UserManager:
    def __init__(self, database):
        self.database = database

    def create_user(self, username, email, password):
        # Create a new user in the database
        pass

    def get_user(self, user_id):
        # Retrieve a user from the database
        pass

    def update_user(self, user_id, **kwargs):
        # Update user information in the database
        pass

    def delete_user(self, user_id):
        # Delete a user from the database
        pass
    """
    prompt = f"Generate API documentation for the following Python class:\n\n{class_to_document}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_requirements_analysis_performance(benchmark, claude_manager):
    user_stories = """
    1. As a user, I want to log in to the system.
    2. As an admin, I want to view all registered users.
    3. As a user, I want to update my profile information.
    """
    prompt = f"Analyze and refine the following set of user stories:\n\n{user_stories}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_bug_report_analysis_performance(benchmark, claude_manager):
    bug_report = """
    Title: Application crashes when uploading large files
    Description: When trying to upload files larger than 100MB, the application crashes without any error message.
    Steps to reproduce:
    1. Log in to the application
    2. Navigate to the file upload section
    3. Select a file larger than 100MB
    4. Click the upload button
    Expected behavior: The file should upload successfully or display an error message if the file is too large.
    Actual behavior: The application crashes and needs to be restarted.
    """
    prompt = f"Analyze the following bug report and suggest potential causes and solutions:\n\n{bug_report}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_performance_optimization_suggestion_performance(benchmark, claude_manager):
    slow_query = """
    SELECT u.id, u.name, u.email, o.order_date, o.total_amount
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.registration_date > '2023-01-01'
    ORDER BY o.order_date DESC
    """
    prompt = f"Suggest optimizations for the following database query:\n\n{slow_query}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_security_vulnerability_identification_performance(benchmark, claude_manager):
    vulnerable_code = """
    from flask import Flask, request, redirect
    import sqlite3

    app = Flask(__name__)

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    if __name__ == '__main__':
        app.run(debug=True)
    """
    prompt = f"Identify security vulnerabilities in the following Python web application snippet:\n\n{vulnerable_code}"
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="domain_specific_tasks")
def test_refactoring_suggestions_performance(benchmark, claude_manager):
    complex_function = """
    def process_data(data):
        result = []
        for item in data:
            if item['type'] == 'A':
                value = item['value'] * 2
                if value > 100:
                    result.append({'id': item['id'], 'processed_value': value, 'category': 'high'})
                else:
                    result.append({'id': item['id'], 'processed_value': value, 'category': 'low'})
            elif item['type'] == 'B':
                value = item['value'] * 1.5
                if value > 50:
                    result.append({'id': item['id'], 'processed_value': value, 'category': 'medium'})
                else:
                    result.append({'id': item['id'], 'processed_value': value, 'category': 'low'})
            else:
                result.append({'id': item['id'], 'processed_value': item['value'], 'category': 'unknown'})
        return result
    """
    prompt = f"Suggest refactoring for the following complex function to improve readability and maintainability:\n\n{complex_function}"
    benchmark(claude_manager.generate_response, prompt)

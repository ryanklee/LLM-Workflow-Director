import pytest
import json
import xml.etree.ElementTree as ET
from src.claude_manager import ClaudeManager
from tests.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    return ClaudeManager(client=MockClaudeClient())

@pytest.fixture
def structured_output_prompt():
    def _generate_prompt(output_type, complexity):
        base_prompt = f"Generate a {complexity} {output_type} structure representing a person with name, age, and address."
        if output_type == "XML":
            base_prompt += " Wrap the response in <response> tags."
        elif output_type == "JSON":
            base_prompt += " Provide the response as a JSON object."
        return base_prompt
    return _generate_prompt

def validate_xml_structure(xml_string):
    try:
        root = ET.fromstring(xml_string)
        return True
    except ET.ParseError:
        return False

def validate_json_structure(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

@pytest.mark.parametrize("output_type", ["XML", "JSON"])
@pytest.mark.parametrize("complexity", ["simple", "complex"])
def test_generate_structured_output(claude_manager, structured_output_prompt, output_type, complexity):
    prompt = structured_output_prompt(output_type, complexity)
    response = claude_manager.generate_response(prompt)
    
    if output_type == "XML":
        assert validate_xml_structure(response), f"Invalid XML structure: {response}"
        root = ET.fromstring(response)
        assert root.tag == "response", "Root tag should be 'response'"
        person = root.find("person")
        assert person is not None, "Person element not found"
        assert person.find("name").text is not None, "Name not found"
        assert person.find("age").text is not None, "Age not found"
        assert person.find("address") is not None, "Address not found"
        if complexity == "complex":
            assert person.find("phone") is not None, "Phone not found in complex structure"
    elif output_type == "JSON":
        assert validate_json_structure(response), f"Invalid JSON structure: {response}"
        data = json.loads(response)
        assert "person" in data, "Person object not found"
        assert "name" in data["person"], "Name not found"
        assert "age" in data["person"], "Age not found"
        assert "address" in data["person"], "Address not found"
        if complexity == "complex":
            assert "phone" in data["person"], "Phone not found in complex structure"

def test_nested_structures(claude_manager):
    prompt = "Generate a complex XML structure representing a company with departments, each containing employees. Include nested elements for employee details."
    response = claude_manager.generate_response(prompt)
    assert validate_xml_structure(response), f"Invalid XML structure: {response}"
    root = ET.fromstring(response)
    company = root.find("company")
    assert company is not None, "Company element not found"
    departments = company.findall("department")
    assert len(departments) > 0, "No departments found"
    for dept in departments:
        employees = dept.findall("employee")
        assert len(employees) > 0, f"No employees found in department: {dept.get('name')}"
        for emp in employees:
            assert emp.find("name") is not None, "Employee name not found"
            assert emp.find("position") is not None, "Employee position not found"

def test_varying_sizes(claude_manager):
    sizes = ["small", "medium", "large"]
    for size in sizes:
        prompt = f"Generate a {size} JSON structure representing a library catalog with books, authors, and genres."
        response = claude_manager.generate_response(prompt)
        assert validate_json_structure(response), f"Invalid JSON structure for {size} size: {response}"
        data = json.loads(response)
        assert "library" in data, "Library object not found"
        assert "books" in data["library"], "Books not found"
        if size == "small":
            assert len(data["library"]["books"]) <= 5, "Small size should have 5 or fewer books"
        elif size == "medium":
            assert 5 < len(data["library"]["books"]) <= 20, "Medium size should have 6-20 books"
        else:
            assert len(data["library"]["books"]) > 20, "Large size should have more than 20 books"

def test_consistency_across_interactions(claude_manager):
    prompt = "Generate a JSON structure for a user profile. Include fields for username, email, and preferences."
    responses = [claude_manager.generate_response(prompt) for _ in range(5)]
    structures = [json.loads(response) for response in responses]
    
    # Check that all responses have the same structure
    base_structure = set(structures[0].keys())
    for structure in structures[1:]:
        assert set(structure.keys()) == base_structure, "Inconsistent structure across interactions"
    
    # Check that all responses have the required fields
    required_fields = {"username", "email", "preferences"}
    for structure in structures:
        assert required_fields.issubset(set(structure.keys())), "Missing required fields in some interactions"

def test_dynamic_input_based_output(claude_manager):
    inputs = [
        ("XML", "person", ["name", "age", "occupation"]),
        ("JSON", "car", ["make", "model", "year", "color"]),
        ("XML", "recipe", ["name", "ingredients", "instructions", "servings"])
    ]
    
    for output_type, entity, fields in inputs:
        prompt = f"Generate a {output_type} structure for a {entity} with the following fields: {', '.join(fields)}"
        response = claude_manager.generate_response(prompt)
        
        if output_type == "XML":
            assert validate_xml_structure(response), f"Invalid XML structure: {response}"
            root = ET.fromstring(response)
            entity_elem = root.find(entity)
            assert entity_elem is not None, f"{entity} element not found"
            for field in fields:
                assert entity_elem.find(field) is not None, f"{field} not found in {entity}"
        elif output_type == "JSON":
            assert validate_json_structure(response), f"Invalid JSON structure: {response}"
            data = json.loads(response)
            assert entity in data, f"{entity} object not found"
            for field in fields:
                assert field in data[entity], f"{field} not found in {entity}"

@pytest.mark.benchmark(group="structured_output")
@pytest.mark.parametrize("output_type", ["XML", "JSON"])
@pytest.mark.parametrize("complexity", ["simple", "complex"])
def test_structured_output_performance(benchmark, claude_manager, structured_output_prompt, output_type, complexity):
    prompt = structured_output_prompt(output_type, complexity)
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="structured_output")
def test_large_nested_structure_performance(benchmark, claude_manager):
    prompt = "Generate a large XML structure representing a company with 10 departments, each containing 20 employees. Include nested elements for employee details and department information."
    benchmark(claude_manager.generate_response, prompt)

@pytest.mark.benchmark(group="structured_output")
def test_dynamic_input_performance(benchmark, claude_manager):
    def generate_dynamic_output():
        inputs = [
            ("XML", "person", ["name", "age", "occupation", "address", "phone", "email"]),
            ("JSON", "car", ["make", "model", "year", "color", "features", "price"]),
            ("XML", "recipe", ["name", "ingredients", "instructions", "servings", "prep_time", "cook_time", "nutrition"])
        ]
        for output_type, entity, fields in inputs:
            prompt = f"Generate a {output_type} structure for a {entity} with the following fields: {', '.join(fields)}"
            claude_manager.generate_response(prompt)
    
    benchmark(generate_dynamic_output)

def test_malformed_xml_error_handling(claude_manager):
    claude_manager.client.simulate_error("malformed_xml")
    prompt = "Generate an XML structure for a person."
    with pytest.raises(ET.ParseError):
        response = claude_manager.generate_response(prompt)
        ET.fromstring(response)  # This should raise a ParseError

def test_malformed_json_error_handling(claude_manager):
    claude_manager.client.simulate_error("malformed_json")
    prompt = "Generate a JSON structure for a person."
    with pytest.raises(json.JSONDecodeError):
        response = claude_manager.generate_response(prompt)
        json.loads(response)  # This should raise a JSONDecodeError

def test_wrong_format_error_handling(claude_manager):
    claude_manager.client.simulate_error("wrong_format")
    prompt = "Generate an XML structure for a person."
    response = claude_manager.generate_response(prompt)
    assert not validate_xml_structure(response), "Response should not be valid XML"
    assert not validate_json_structure(response), "Response should not be valid JSON"

@pytest.mark.parametrize("error_type", ["malformed_xml", "malformed_json", "wrong_format"])
def test_error_recovery(claude_manager, error_type):
    claude_manager.client.simulate_error(error_type)
    prompt = "Generate a JSON structure for a person."
    try:
        response = claude_manager.generate_response(prompt)
        # Attempt to parse the response
        if "XML" in prompt:
            ET.fromstring(response)
        elif "JSON" in prompt:
            json.loads(response)
    except (ET.ParseError, json.JSONDecodeError):
        # If parsing fails, check if the ClaudeManager attempted to recover
        assert claude_manager.client.error_count > 1, "ClaudeManager should attempt to recover from errors"
        
    # Reset the error mode and check if a valid response can be generated
    claude_manager.client.reset()
    response = claude_manager.generate_response(prompt)
    assert validate_json_structure(response), "ClaudeManager should recover and generate valid JSON"

# Add more tests as needed to cover other aspects of structured output generation

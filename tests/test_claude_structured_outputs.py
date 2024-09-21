import pytest
import json
import xml.etree.ElementTree as ET
import yaml
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
async def claude_manager():
    return ClaudeManager(client=MockClaudeClient())

@pytest.mark.asyncio
async def test_generate_json_output(claude_manager):
    prompt = "Generate a JSON object representing a person with name, age, and list of hobbies."
    response = await claude_manager.generate_response(prompt)
    
    # Parse the JSON from the response
    json_output = json.loads(response)
    
    assert isinstance(json_output, dict)
    assert "name" in json_output
    assert "age" in json_output
    assert "hobbies" in json_output
    assert isinstance(json_output["hobbies"], list)

@pytest.mark.asyncio
async def test_generate_xml_output(claude_manager):
    prompt = "Generate an XML document representing a book with title, author, and publication year."
    response = await claude_manager.generate_response(prompt)
    
    # Parse the XML from the response
    root = ET.fromstring(response)
    
    assert root.tag == "book"
    assert root.find("title") is not None
    assert root.find("author") is not None
    assert root.find("year") is not None

@pytest.mark.asyncio
async def test_generate_yaml_output(claude_manager):
    prompt = "Generate a YAML document representing a simple configuration with database settings."
    response = await claude_manager.generate_response(prompt)
    
    # Parse the YAML from the response
    yaml_output = yaml.safe_load(response)
    
    assert isinstance(yaml_output, dict)
    assert "database" in yaml_output
    assert "host" in yaml_output["database"]
    assert "port" in yaml_output["database"]
    assert "username" in yaml_output["database"]

@pytest.mark.asyncio
async def test_complex_nested_structure(claude_manager):
    prompt = "Generate a JSON object representing a company with name, founded year, and a list of employees. Each employee should have a name, position, and a list of skills."
    response = await claude_manager.generate_response(prompt)
    
    json_output = json.loads(response)
    
    assert isinstance(json_output, dict)
    assert "name" in json_output
    assert "founded" in json_output
    assert "employees" in json_output
    assert isinstance(json_output["employees"], list)
    
    for employee in json_output["employees"]:
        assert "name" in employee
        assert "position" in employee
        assert "skills" in employee
        assert isinstance(employee["skills"], list)

@pytest.mark.asyncio
async def test_dynamic_input_structured_output(claude_manager):
    input_data = {
        "product_name": "Smartphone",
        "features": ["5G", "Dual Camera", "Water Resistant"],
        "price": 799.99
    }
    prompt = f"Generate an XML document for a product listing based on this data: {json.dumps(input_data)}"
    response = await claude_manager.generate_response(prompt)
    
    root = ET.fromstring(response)
    
    assert root.tag == "product"
    assert root.find("name").text == "Smartphone"
    assert len(root.find("features").findall("feature")) == 3
    assert float(root.find("price").text) == 799.99

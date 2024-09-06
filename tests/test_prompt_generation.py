import pytest
from src.claude_manager import ClaudeManager
from src.mock_claude_client import MockClaudeClient

@pytest.fixture
def claude_manager():
    mock_client = MockClaudeClient()
    return ClaudeManager(client=mock_client)

def test_prompt_template_rendering(claude_manager):
    template = "Hello, {name}! How are you feeling today?"
    context = {"name": "Alice"}
    rendered_prompt = claude_manager.render_prompt_template(template, context)
    assert rendered_prompt == "Hello, Alice! How are you feeling today?"

@pytest.mark.parametrize("template,context,expected", [
    ("The capital of {country} is {capital}.", {"country": "France", "capital": "Paris"}, "The capital of France is Paris."),
    ("My favorite color is {color}!", {"color": "blue"}, "My favorite color is blue!"),
    ("{greeting} {name}!", {"greeting": "Hi", "name": "Bob"}, "Hi Bob!"),
])
def test_prompt_template_scenarios(claude_manager, template, context, expected):
    rendered_prompt = claude_manager.render_prompt_template(template, context)
    assert rendered_prompt == expected

def test_prompt_template_missing_context(claude_manager):
    template = "Hello, {name}!"
    context = {}
    with pytest.raises(KeyError):
        claude_manager.render_prompt_template(template, context)

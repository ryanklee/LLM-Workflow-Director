import pytest
from pathlib import Path

@pytest.fixture
def domain_model_content():
    domain_model_path = Path(__file__).parent.parent / "docs" / "domain_model.md"
    return domain_model_path.read_text()

def test_domain_model_includes_core_concepts(domain_model_content):
    core_concepts = [
        "Workflow", "Stage", "Task", "Artifact", "LLM", "Prompt", "Constraint",
        "State", "Evaluation", "User", "Contract", "VectorStore"
    ]
    for concept in core_concepts:
        assert concept in domain_model_content

def test_domain_model_includes_key_processes(domain_model_content):
    key_processes = [
        "Workflow Progression", "LLM Interaction", "Constraint Enforcement",
        "State Management", "Evaluation and Sufficiency", "Contract Testing",
        "Vector-based Information Retrieval"
    ]
    for process in key_processes:
        assert process in domain_model_content

def test_domain_model_mentions_tiered_llm_approach(domain_model_content):
    assert "tiered approach (Haiku, Sonnet, Opus)" in domain_model_content

def test_domain_model_mentions_chroma_db(domain_model_content):
    assert "Chroma DB" in domain_model_content

def test_domain_model_mentions_contract_testing(domain_model_content):
    assert "contract testing" in domain_model_content

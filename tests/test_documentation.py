import pytest
from pathlib import Path

@pytest.fixture
def docs_dir():
    return Path(__file__).parent.parent / "docs"

def test_index_md_exists(docs_dir):
    assert (docs_dir / "index.md").exists()

def test_getting_started_md_exists(docs_dir):
    assert (docs_dir / "getting_started.md").exists()

def test_index_md_contains_key_sections(docs_dir):
    index_content = (docs_dir / "index.md").read_text()
    assert "## Overview" in index_content
    assert "## Table of Contents" in index_content
    assert "## Key Concepts" in index_content
    assert "## Recent Updates" in index_content

def test_getting_started_md_contains_key_sections(docs_dir):
    getting_started_content = (docs_dir / "getting_started.md").read_text()
    assert "## Prerequisites" in getting_started_content
    assert "## Installation" in getting_started_content
    assert "## Configuration" in getting_started_content
    assert "## Running the LLM-Workflow Director" in getting_started_content
    assert "## Running Tests" in getting_started_content
    assert "## Troubleshooting" in getting_started_content

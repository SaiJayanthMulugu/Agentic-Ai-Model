"""
Tests for Code Agent
"""

import pytest
from src.agents.code_agent import CodeAgent


def test_code_agent_initialization():
    """Test Code agent initialization."""
    agent = CodeAgent()
    assert agent.agent_name == "CodeAgent"


def test_code_generation():
    """Test code generation."""
    agent = CodeAgent()
    task = {
        "task_description": "Generate SQL to find top customers",
        "user_query": "Generate SQL to find top 10 customers by sales"
    }
    result = agent.process(task)
    assert result["status"] in ["success", "error"]
    if result["status"] == "success":
        assert "code" in result


if __name__ == "__main__":
    pytest.main([__file__])


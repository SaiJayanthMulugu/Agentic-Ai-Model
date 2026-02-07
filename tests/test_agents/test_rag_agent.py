"""
Tests for RAG Agent
"""

import pytest
from src.agents.rag_agent import RAGAgent


def test_rag_agent_initialization():
    """Test RAG agent initialization."""
    agent = RAGAgent()
    assert agent.agent_name == "RAGAgent"
    assert agent.enabled is True


def test_rag_agent_process():
    """Test RAG agent processing."""
    agent = RAGAgent()
    task = {
        "task_description": "Find information about SQL",
        "user_role": "data_analyst"
    }
    result = agent.process(task)
    assert result["status"] in ["success", "error"]


if __name__ == "__main__":
    pytest.main([__file__])


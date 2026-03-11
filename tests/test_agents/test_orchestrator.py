"""
Tests for Orchestrator Agent
"""

import pytest
from src.core.orchestrator import OrchestratorAgent


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orchestrator = OrchestratorAgent()
    assert orchestrator.agent_name == "OrchestratorAgent"


def test_process_request():
    """Test request processing."""
    orchestrator = OrchestratorAgent()
    response = orchestrator.process_request(
        user_query="What is SQL?",
        user_id="test_user",
        user_role="data_analyst"
    )
    assert "status" in response
    assert "request_id" in response


if __name__ == "__main__":
    pytest.main([__file__])


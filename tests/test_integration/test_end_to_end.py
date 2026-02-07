"""
End-to-end integration tests
"""

import pytest
from src.core.orchestrator import OrchestratorAgent


def test_end_to_end_query():
    """Test end-to-end query processing."""
    orchestrator = OrchestratorAgent()
    
    response = orchestrator.process_request(
        user_query="What is SQL?",
        user_id="test_user",
        user_role="data_analyst"
    )
    
    assert response["status"] in ["success", "error", "denied"]
    assert "request_id" in response


if __name__ == "__main__":
    pytest.main([__file__])


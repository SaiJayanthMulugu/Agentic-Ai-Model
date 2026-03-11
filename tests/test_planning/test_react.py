"""
Tests for ReAct Planner
"""

import pytest
from src.core.planning.react import ReActPlanner


def test_react_planner_initialization():
    """Test ReAct planner initialization."""
    planner = ReActPlanner()
    assert planner.max_iterations == 10


def test_react_planning():
    """Test ReAct planning."""
    planner = ReActPlanner()
    plan = planner.plan("Generate SQL to find top customers")
    assert len(plan) > 0
    assert all(hasattr(task, "agent_type") for task in plan)


if __name__ == "__main__":
    pytest.main([__file__])


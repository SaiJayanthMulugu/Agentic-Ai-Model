"""
Tests for Tree of Thoughts Planner
"""

import pytest
from src.core.planning.tot import ToTPlanner


def test_tot_planner_initialization():
    """Test ToT planner initialization."""
    planner = ToTPlanner()
    assert planner.max_depth == 3


def test_tot_planning():
    """Test ToT planning."""
    planner = ToTPlanner()
    plan = planner.plan("Generate SQL to find top customers")
    assert len(plan) > 0


if __name__ == "__main__":
    pytest.main([__file__])


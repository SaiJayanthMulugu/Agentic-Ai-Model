"""
Task Planner
============

Main task planner that selects and uses appropriate planning strategy.

Features:
- Strategy selection (ReAct, ToT, CoT)
- Pre-defined execution plans
- Strategy routing

Author: AI Ops Team
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.core.planning.react import ReActPlanner, AgentTask
from src.core.planning.tot import ToTPlanner
from src.core.planning.chain_of_thought import ChainOfThoughtPlanner

logger = get_logger(__name__)


class TaskPlanner:
    """
    Main task planner that routes to appropriate planning strategy.
    """
    
    def __init__(self, default_strategy: str = "react"):
        """
        Initialize TaskPlanner.
        
        Args:
            default_strategy: Default planning strategy (react, tot, chain_of_thought)
        """
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load("mas_config.yaml")
        self.default_strategy = self.config.get("mas", {}).get("planning", {}).get("default_strategy", "react")
        
        self.react_planner = ReActPlanner()
        self.tot_planner = ToTPlanner()
        self.cot_planner = ChainOfThoughtPlanner()
        
        # Load pre-defined execution plans
        self.execution_plans = self.config.get("mas", {}).get("execution_plans", {})
    
    def plan(self, user_query: str, strategy: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> List[AgentTask]:
        """
        Create an execution plan.
        
        Args:
            user_query: User's query/request
            strategy: Planning strategy to use (optional, uses default if not provided)
            context: Optional context
        
        Returns:
            List of AgentTask objects
        """
        strategy = strategy or self.default_strategy
        
        # Check for pre-defined execution plan
        plan = self._match_execution_plan(user_query)
        if plan:
            logger.info(f"Using pre-defined execution plan: {plan['name']}")
            return self._create_tasks_from_plan(plan, user_query)
        
        # Use selected strategy
        logger.info(f"Using planning strategy: {strategy}")
        
        if strategy == "react":
            return self.react_planner.plan(user_query, context)
        elif strategy == "tot":
            return self.tot_planner.plan(user_query, context)
        elif strategy == "chain_of_thought":
            return self.cot_planner.plan(user_query, context)
        else:
            logger.warning(f"Unknown strategy: {strategy}. Using ReAct.")
            return self.react_planner.plan(user_query, context)
    
    def _match_execution_plan(self, user_query: str) -> Optional[Dict[str, Any]]:
        """
        Match user query to a pre-defined execution plan.
        
        Args:
            user_query: User's query
        
        Returns:
            Execution plan dictionary or None
        """
        query_lower = user_query.lower()
        
        # Match patterns
        if "powerbi" in query_lower or "power bi" in query_lower or "dax" in query_lower:
            return self.execution_plans.get("powerbi_validation")
        elif "execute" in query_lower or "run" in query_lower:
            return self.execution_plans.get("code_execution")
        elif "test" in query_lower and ("generate" in query_lower or "create" in query_lower):
            return self.execution_plans.get("test_generation")
        elif "sql" in query_lower and ("generate" in query_lower or "create" in query_lower):
            return self.execution_plans.get("sql_generation")
        elif "learn" in query_lower or "retrain" in query_lower:
            return self.execution_plans.get("self_learning")
        elif "query" in query_lower or "answer" in query_lower or "what" in query_lower:
            return self.execution_plans.get("knowledge_query")
        
        return None
    
    def _create_tasks_from_plan(self, plan: Dict[str, Any], user_query: str) -> List[AgentTask]:
        """
        Create tasks from a pre-defined execution plan.
        
        Args:
            plan: Execution plan dictionary
            user_query: User's query
        
        Returns:
            List of AgentTask objects
        """
        tasks: List[AgentTask] = []
        agent_types = plan.get("agents", [])
        
        for i, agent_type in enumerate(agent_types):
            dependencies = [tasks[j].task_id for j in range(i)] if i > 0 else []
            
            task = AgentTask(
                agent_type=agent_type,
                task_description=f"{agent_type} task for: {user_query}",
                dependencies=dependencies
            )
            task.task_id = f"task_{i}"
            tasks.append(task)
        
        return tasks


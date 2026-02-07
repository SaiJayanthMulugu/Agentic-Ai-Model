"""
Chain of Thought (CoT) Planner
===============================

Sequential reasoning planner that breaks down problems step by step.

Features:
- Sequential step-by-step reasoning
- Linear task decomposition
- Dependency tracking
- Simple and predictable

Author: AI Ops Team
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.core.planning.react import AgentTask

logger = get_logger(__name__)


class ChainOfThoughtPlanner:
    """
    Chain of Thought planner for sequential task decomposition.
    """
    
    def __init__(self):
        """Initialize ChainOfThoughtPlanner."""
        self.config_loader = ConfigLoader()
    
    def plan(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> List[AgentTask]:
        """
        Create an execution plan using Chain of Thought strategy.
        
        Process:
        1. Break down query into steps
        2. Create sequential tasks
        3. Link dependencies
        
        Args:
            user_query: User's query/request
            context: Optional context
        
        Returns:
            List of AgentTask objects
        """
        logger.info(f"Starting Chain of Thought planning for query: {user_query}")
        
        tasks: List[AgentTask] = []
        
        # Step 1: Always start with knowledge retrieval
        task1 = AgentTask(
            agent_type="RAGAgent",
            task_description=f"Step 1: Retrieve relevant knowledge for: {user_query}",
            dependencies=[]
        )
        task1.task_id = "task_0"
        tasks.append(task1)
        
        # Step 2: Determine if code generation is needed
        if any(keyword in user_query.lower() for keyword in ["generate", "create", "sql", "code", "write"]):
            task2 = AgentTask(
                agent_type="CodeAgent",
                task_description=f"Step 2: Generate code based on knowledge for: {user_query}",
                dependencies=[task1.task_id]
            )
            task2.task_id = "task_1"
            tasks.append(task2)
            
            # Step 3: Add validation
            task3 = AgentTask(
                agent_type="TestCaseAgent",
                task_description="Step 3: Generate validation tests",
                dependencies=[task2.task_id]
            )
            task3.task_id = "task_2"
            tasks.append(task3)
            
            # Step 4: Check if execution is requested
            if any(keyword in user_query.lower() for keyword in ["execute", "run", "run this"]):
                task4 = AgentTask(
                    agent_type="ExecutionAgent",
                    task_description=f"Step 4: Execute the generated code",
                    dependencies=[task2.task_id]
                )
                task4.task_id = "task_3"
                tasks.append(task4)
                
                # Step 5: Collect feedback
                task5 = AgentTask(
                    agent_type="FeedbackAgent",
                    task_description="Step 5: Collect user feedback",
                    dependencies=[task4.task_id]
                )
                task5.task_id = "task_4"
                tasks.append(task5)
        
        logger.info(f"Chain of Thought planning completed with {len(tasks)} sequential tasks")
        return tasks


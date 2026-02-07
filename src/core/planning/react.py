"""
ReAct Planner
==============

ReAct (Reasoning + Acting) planning strategy.

Features:
- Thought-Action-Observation loop
- Iterative refinement
- Agent selection based on reasoning
- Max iteration limit

Author: AI Ops Team
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class AgentTask:
    """Represents a task for an agent."""
    
    def __init__(self, agent_type: str, task_description: str, dependencies: Optional[List[str]] = None):
        """
        Initialize AgentTask.
        
        Args:
            agent_type: Type of agent to execute task
            task_description: Description of the task
            dependencies: List of task IDs this task depends on
        """
        self.agent_type = agent_type
        self.task_description = task_description
        self.dependencies = dependencies or []
        self.task_id = None
        self.status = "pending"


class ReActPlanner:
    """
    ReAct (Reasoning + Acting) planner.
    
    Implements the Thought-Action-Observation loop for task planning.
    """
    
    def __init__(self, max_iterations: int = 10):
        """
        Initialize ReActPlanner.
        
        Args:
            max_iterations: Maximum number of planning iterations
        """
        self.max_iterations = max_iterations
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load("mas_config.yaml")
        self.max_iterations = self.config.get("mas", {}).get("planning", {}).get("max_iterations", 10)
    
    def plan(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> List[AgentTask]:
        """
        Create an execution plan using ReAct strategy.
        
        Process:
        1. Thought: Analyze what user wants
        2. Action: Choose agent
        3. Observation: Review agent output
        4. Repeat until goal achieved
        
        Args:
            user_query: User's query/request
            context: Optional context from previous interactions
        
        Returns:
            List of AgentTask objects
        """
        tasks: List[AgentTask] = []
        observations: List[str] = []
        iteration = 0
        
        logger.info(f"Starting ReAct planning for query: {user_query}")
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"ReAct iteration {iteration}/{self.max_iterations}")
            
            # Thought: Analyze what user wants
            thought = self._think(user_query, observations, tasks)
            logger.debug(f"Thought: {thought}")
            
            # Action: Choose agent and create task
            action = self._act(thought, user_query, tasks)
            
            if action is None:
                logger.info("ReAct planning complete - no more actions needed")
                break
            
            # Create task
            task = AgentTask(
                agent_type=action["agent_type"],
                task_description=action["task_description"],
                dependencies=action.get("dependencies", [])
            )
            task.task_id = f"task_{len(tasks)}"
            tasks.append(task)
            
            # Observation: Simulate what agent output would be
            observation = self._observe(task, thought)
            observations.append(observation)
            logger.debug(f"Observation: {observation}")
            
            # Check if goal is achieved
            if self._is_goal_achieved(user_query, tasks, observations):
                logger.info("ReAct planning complete - goal achieved")
                break
        
        if iteration >= self.max_iterations:
            logger.warning(f"ReAct planning reached max iterations ({self.max_iterations})")
        
        logger.info(f"ReAct planning completed with {len(tasks)} tasks")
        return tasks
    
    def _think(self, user_query: str, observations: List[str], tasks: List[AgentTask]) -> str:
        """
        Generate a thought about what needs to be done.
        
        Args:
            user_query: User's query
            observations: Previous observations
            tasks: Current task list
        
        Returns:
            Thought string
        """
        # Simplified thought generation - in production, use LLM
        if len(tasks) == 0:
            # First thought: understand the query
            if "sql" in user_query.lower() or "code" in user_query.lower():
                return "User wants to generate SQL or code. Need to retrieve relevant knowledge first."
            elif "execute" in user_query.lower() or "run" in user_query.lower():
                return "User wants to execute code. Need to generate code first, then get approval, then execute."
            elif "test" in user_query.lower():
                return "User wants to generate tests. Need knowledge and code generation first."
            else:
                return "User has a query. Need to retrieve relevant knowledge from RAG system."
        
        # Subsequent thoughts: check if we need more steps
        last_task = tasks[-1]
        if last_task.agent_type == "RAGAgent":
            return "Knowledge retrieved. Now need to generate code or provide answer."
        elif last_task.agent_type == "CodeAgent":
            return "Code generated. Should validate with tests or execute if requested."
        elif last_task.agent_type == "TestCaseAgent":
            return "Tests generated. If execution was requested, need approval and execution."
        
        return "Task sequence appears complete."
    
    def _act(self, thought: str, user_query: str, tasks: List[AgentTask]) -> Optional[Dict[str, Any]]:
        """
        Decide on an action (which agent to use).
        
        Args:
            thought: Current thought
            user_query: User's query
            tasks: Current task list
        
        Returns:
            Action dictionary or None if no action needed
        """
        # Determine next agent based on thought and current state
        if len(tasks) == 0:
            # Always start with RAG if query needs knowledge
            if any(keyword in user_query.lower() for keyword in ["sql", "code", "generate", "create", "find", "query"]):
                return {
                    "agent_type": "RAGAgent",
                    "task_description": f"Retrieve relevant knowledge for: {user_query}",
                    "dependencies": []
                }
            else:
                return {
                    "agent_type": "RAGAgent",
                    "task_description": f"Answer query: {user_query}",
                    "dependencies": []
                }
        
        last_task = tasks[-1]
        
        # After RAG, decide next step
        if last_task.agent_type == "RAGAgent":
            if "generate" in user_query.lower() or "create" in user_query.lower() or "sql" in user_query.lower():
                return {
                    "agent_type": "CodeAgent",
                    "task_description": f"Generate code based on retrieved knowledge for: {user_query}",
                    "dependencies": [last_task.task_id]
                }
            else:
                return None  # RAG answer is sufficient
        
        # After CodeAgent, add TestCaseAgent
        if last_task.agent_type == "CodeAgent":
            return {
                "agent_type": "TestCaseAgent",
                "task_description": "Generate validation tests for the generated code",
                "dependencies": [last_task.task_id]
            }
        
        # After TestCaseAgent, check if execution is needed
        if last_task.agent_type == "TestCaseAgent":
            if "execute" in user_query.lower() or "run" in user_query.lower():
                return {
                    "agent_type": "ExecutionAgent",
                    "task_description": f"Execute the generated code: {user_query}",
                    "dependencies": [tasks[-2].task_id if len(tasks) >= 2 else last_task.task_id]
                }
            else:
                return None  # No execution needed
        
        # After ExecutionAgent, collect feedback
        if last_task.agent_type == "ExecutionAgent":
            return {
                "agent_type": "FeedbackAgent",
                "task_description": "Collect user feedback on execution results",
                "dependencies": [last_task.task_id]
            }
        
        return None
    
    def _observe(self, task: AgentTask, thought: str) -> str:
        """
        Generate an observation about what the agent would produce.
        
        Args:
            task: The task that was created
            thought: The thought that led to this task
        
        Returns:
            Observation string
        """
        if task.agent_type == "RAGAgent":
            return "Knowledge retrieved from knowledge base"
        elif task.agent_type == "CodeAgent":
            return "Code generated successfully"
        elif task.agent_type == "TestCaseAgent":
            return "Test cases generated"
        elif task.agent_type == "ExecutionAgent":
            return "Code execution completed"
        elif task.agent_type == "FeedbackAgent":
            return "Feedback collected"
        else:
            return f"Task {task.agent_type} completed"
    
    def _is_goal_achieved(self, user_query: str, tasks: List[AgentTask], observations: List[str]) -> bool:
        """
        Check if the goal has been achieved.
        
        Args:
            user_query: Original user query
            tasks: List of tasks
            observations: List of observations
        
        Returns:
            True if goal is achieved
        """
        if len(tasks) == 0:
            return False
        
        last_task = tasks[-1]
        
        # Goal achieved if:
        # 1. Simple query -> RAGAgent completed
        # 2. Code generation -> CodeAgent + TestCaseAgent completed
        # 3. Execution -> ExecutionAgent + FeedbackAgent completed
        
        if "execute" in user_query.lower() or "run" in user_query.lower():
            return last_task.agent_type == "FeedbackAgent"
        elif "generate" in user_query.lower() or "create" in user_query.lower() or "sql" in user_query.lower():
            return last_task.agent_type == "TestCaseAgent"
        else:
            return last_task.agent_type == "RAGAgent"


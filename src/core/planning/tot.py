"""
Tree of Thoughts (ToT) Planner
================================

Tree of Thoughts planning strategy for exploring multiple solution paths.

Features:
- Multiple thought branches
- Branch evaluation
- Best path selection
- Backtracking support

Author: AI Ops Team
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.core.planning.react import AgentTask

logger = get_logger(__name__)


class ThoughtNode:
    """Represents a node in the tree of thoughts."""
    
    def __init__(self, thought: str, tasks: List[AgentTask], score: float = 0.0):
        """
        Initialize ThoughtNode.
        
        Args:
            thought: Thought description
            tasks: Tasks generated from this thought
            score: Evaluation score
        """
        self.thought = thought
        self.tasks = tasks
        self.score = score
        self.children: List[ThoughtNode] = []
        self.parent: Optional[ThoughtNode] = None


class ToTPlanner:
    """
    Tree of Thoughts (ToT) planner.
    
    Explores multiple solution paths and selects the best one.
    """
    
    def __init__(self, max_depth: int = 3, branching_factor: int = 3):
        """
        Initialize ToTPlanner.
        
        Args:
            max_depth: Maximum depth of the tree
            branching_factor: Number of branches to explore at each level
        """
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.config_loader = ConfigLoader()
    
    def plan(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> List[AgentTask]:
        """
        Create an execution plan using ToT strategy.
        
        Process:
        1. Generate multiple thought branches
        2. Evaluate each branch
        3. Select best path
        4. Backtrack if needed
        
        Args:
            user_query: User's query/request
            context: Optional context
        
        Returns:
            List of AgentTask objects from best path
        """
        logger.info(f"Starting ToT planning for query: {user_query}")
        
        # Create root node
        root = ThoughtNode(
            thought="Initial query analysis",
            tasks=[],
            score=0.0
        )
        
        # Build tree
        self._build_tree(root, user_query, 0)
        
        # Find best path
        best_path = self._find_best_path(root)
        
        # Extract tasks from best path
        tasks: List[AgentTask] = []
        for node in best_path:
            tasks.extend(node.tasks)
        
        logger.info(f"ToT planning completed with {len(tasks)} tasks from best path")
        return tasks
    
    def _build_tree(self, node: ThoughtNode, user_query: str, depth: int) -> None:
        """
        Recursively build the tree of thoughts.
        
        Args:
            node: Current node
            user_query: User's query
            depth: Current depth
        """
        if depth >= self.max_depth:
            return
        
        # Generate multiple thought branches
        thoughts = self._generate_thoughts(node, user_query, depth)
        
        for thought in thoughts[:self.branching_factor]:
            # Generate tasks for this thought
            tasks = self._generate_tasks_for_thought(thought, user_query, node.tasks)
            
            # Evaluate this branch
            score = self._evaluate_branch(thought, tasks, user_query)
            
            # Create child node
            child = ThoughtNode(
                thought=thought,
                tasks=tasks,
                score=score
            )
            child.parent = node
            node.children.append(child)
            
            # Recursively build subtree
            self._build_tree(child, user_query, depth + 1)
    
    def _generate_thoughts(self, node: ThoughtNode, user_query: str, depth: int) -> List[str]:
        """
        Generate multiple thought branches.
        
        Args:
            node: Current node
            user_query: User's query
            depth: Current depth
        
        Returns:
            List of thought strings
        """
        thoughts = []
        
        if depth == 0:
            # Root level: different approaches to understand the query
            thoughts = [
                "Approach 1: Direct knowledge retrieval and answer",
                "Approach 2: Knowledge retrieval followed by code generation",
                "Approach 3: Multi-step analysis with validation"
            ]
        elif depth == 1:
            # Second level: different agent sequences
            if "sql" in user_query.lower() or "code" in user_query.lower():
                thoughts = [
                    "Sequence: RAG -> Code -> Test",
                    "Sequence: RAG -> Code -> Test -> Execute",
                    "Sequence: RAG -> Code -> PowerBI validation"
                ]
            else:
                thoughts = [
                    "Sequence: RAG only",
                    "Sequence: RAG -> Code -> Answer",
                    "Sequence: RAG -> Test -> Answer"
                ]
        else:
            # Deeper levels: refinement thoughts
            thoughts = [
                "Refinement: Add validation step",
                "Refinement: Add execution step",
                "Refinement: Add feedback collection"
            ]
        
        return thoughts
    
    def _generate_tasks_for_thought(self, thought: str, user_query: str, parent_tasks: List[AgentTask]) -> List[AgentTask]:
        """
        Generate tasks for a given thought.
        
        Args:
            thought: Thought string
            user_query: User's query
            parent_tasks: Tasks from parent node
        
        Returns:
            List of AgentTask objects
        """
        tasks: List[AgentTask] = []
        
        # Parse thought to determine agent sequence
        if "RAG" in thought:
            task = AgentTask(
                agent_type="RAGAgent",
                task_description=f"Retrieve knowledge for: {user_query}",
                dependencies=[]
            )
            task.task_id = f"task_{len(parent_tasks)}"
            tasks.append(task)
        
        if "Code" in thought:
            deps = [t.task_id for t in parent_tasks if t.agent_type == "RAGAgent"]
            task = AgentTask(
                agent_type="CodeAgent",
                task_description=f"Generate code for: {user_query}",
                dependencies=deps
            )
            task.task_id = f"task_{len(parent_tasks) + len(tasks)}"
            tasks.append(task)
        
        if "Test" in thought:
            deps = [t.task_id for t in (parent_tasks + tasks) if t.agent_type == "CodeAgent"]
            task = AgentTask(
                agent_type="TestCaseAgent",
                task_description="Generate validation tests",
                dependencies=deps
            )
            task.task_id = f"task_{len(parent_tasks) + len(tasks)}"
            tasks.append(task)
        
        if "Execute" in thought:
            deps = [t.task_id for t in (parent_tasks + tasks) if t.agent_type == "CodeAgent"]
            task = AgentTask(
                agent_type="ExecutionAgent",
                task_description=f"Execute code for: {user_query}",
                dependencies=deps
            )
            task.task_id = f"task_{len(parent_tasks) + len(tasks)}"
            tasks.append(task)
        
        return tasks
    
    def _evaluate_branch(self, thought: str, tasks: List[AgentTask], user_query: str) -> float:
        """
        Evaluate a branch and assign a score.
        
        Args:
            thought: Thought string
            tasks: Tasks in this branch
            user_query: User's query
        
        Returns:
            Evaluation score (0.0 to 1.0)
        """
        score = 0.5  # Base score
        
        # Higher score for matching user intent
        if "execute" in user_query.lower() and any(t.agent_type == "ExecutionAgent" for t in tasks):
            score += 0.3
        elif "generate" in user_query.lower() and any(t.agent_type == "CodeAgent" for t in tasks):
            score += 0.3
        elif "test" in user_query.lower() and any(t.agent_type == "TestCaseAgent" for t in tasks):
            score += 0.3
        
        # Higher score for complete sequences
        if len(tasks) >= 2:
            score += 0.1
        
        # Lower score for overly complex sequences
        if len(tasks) > 5:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _find_best_path(self, root: ThoughtNode) -> List[ThoughtNode]:
        """
        Find the best path through the tree.
        
        Args:
            root: Root node
        
        Returns:
            List of nodes representing the best path
        """
        best_path: List[ThoughtNode] = []
        best_score = -1.0
        
        def dfs(node: ThoughtNode, path: List[ThoughtNode], score: float):
            nonlocal best_path, best_score
            
            current_path = path + [node]
            current_score = score + node.score
            
            if not node.children:
                # Leaf node - evaluate path
                if current_score > best_score:
                    best_score = current_score
                    best_path = current_path
            else:
                # Continue exploring children
                for child in node.children:
                    dfs(child, current_path, current_score)
        
        dfs(root, [], 0.0)
        
        return best_path if best_path else [root]


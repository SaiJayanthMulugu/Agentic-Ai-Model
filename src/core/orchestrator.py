"""
Orchestrator Agent
=================

Master controller that coordinates all agents.

Features:
- Intent detection using LLM
- Execution plan creation (ReAct/ToT)
- Task delegation via message bus
- RBAC enforcement
- Response aggregation
- Never calls agents directly - uses message bus

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
from src.core.base_agent import BaseAgent
from src.core.planning.task_planner import TaskPlanner
from src.core.agent_registry import AgentRegistry
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.utils.sanitizer import InputSanitizer
from src.governance.rbac import RBACManager

logger = get_logger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator agent that coordinates all other agents.
    """
    
    def __init__(self):
        """Initialize OrchestratorAgent."""
        super().__init__("OrchestratorAgent")
        self.task_planner = TaskPlanner()
        self.agent_registry = AgentRegistry()
        self.rbac_manager = RBACManager()
        self.sanitizer = InputSanitizer()
        
        logger.info("OrchestratorAgent initialized")
    
    def process_request(
        self,
        user_query: str,
        user_id: str,
        user_role: str = "viewer",
        planning_strategy: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user request end-to-end.
        
        Args:
            user_query: User's query/request
            user_id: User ID
            user_role: User's role for RBAC
            planning_strategy: Planning strategy to use (optional)
            context: Optional context
        
        Returns:
            Complete response dictionary
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Processing request {request_id} from user {user_id} (role: {user_role})")
        
        try:
            # Sanitize input
            sanitized_query = self.sanitizer.sanitize(user_query, allow_sql=False)
            
            # Detect intent
            intent = self._detect_intent(sanitized_query)
            logger.info(f"Detected intent: {intent}")
            
            # Check RBAC permissions
            if not self.rbac_manager.check_permission(user_role, intent):
                logger.warning(f"User {user_id} with role {user_role} denied access to intent: {intent}")
                return {
                    "request_id": request_id,
                    "status": "denied",
                    "error": "Insufficient permissions",
                    "intent": intent
                }
            
            # Create execution plan
            plan = self.task_planner.plan(sanitized_query, planning_strategy, context)
            logger.info(f"Created execution plan with {len(plan)} tasks")
            
            # Store plan in execution_plans table
            self._store_execution_plan(request_id, sanitized_query, intent, plan)
            
            # Execute plan
            results = self._execute_plan(plan, request_id, user_id, user_role)
            
            # Aggregate responses
            aggregated_response = self._aggregate_responses(results, sanitized_query)
            
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            logger.info(f"Request {request_id} completed in {duration_ms:.2f}ms")
            
            return {
                "request_id": request_id,
                "status": "success",
                "intent": intent,
                "plan": [{"agent": t.agent_type, "description": t.task_description} for t in plan],
                "results": aggregated_response,
                "duration_ms": duration_ms,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            return {
                "request_id": request_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _detect_intent(self, user_query: str) -> str:
        """
        Detect user intent from query.
        
        Args:
            user_query: User's query
        
        Returns:
            Intent string
        """
        query_lower = user_query.lower()
        
        # Simple intent detection - in production, use LLM
        if any(keyword in query_lower for keyword in ["execute", "run", "run this"]):
            return "code_execution"
        elif any(keyword in query_lower for keyword in ["generate", "create", "write", "sql"]):
            return "code_generation"
        elif any(keyword in query_lower for keyword in ["test", "validate", "validation"]):
            return "test_generation"
        elif any(keyword in query_lower for keyword in ["powerbi", "power bi", "dax"]):
            return "powerbi_validation"
        elif any(keyword in query_lower for keyword in ["learn", "retrain", "improve"]):
            return "self_learning"
        else:
            return "knowledge_query"
    
    def _store_execution_plan(
        self,
        request_id: str,
        user_query: str,
        intent: str,
        plan: List[Any]
    ) -> None:
        """
        Store execution plan in database.
        
        Args:
            request_id: Request ID
            user_query: User's query
            intent: Detected intent
            plan: Execution plan
        """
        try:
            import json
            plan_steps = []
            for task in plan:
                plan_steps.append({
                    "step_id": task.task_id,
                    "agent_type": task.agent_type,
                    "task_description": task.task_description,
                    "dependencies": task.dependencies,
                    "status": "pending",
                    "result": None
                })
            
            plan_steps_json = json.dumps(plan_steps)
            
            query = f"""
            INSERT INTO main.mas_system.execution_plans
            (plan_id, user_query, intent, planning_strategy, plan_steps, status, created_at, correlation_id)
            VALUES
            ('{request_id}', '{user_query}', '{intent}', 'react', '{plan_steps_json}', 
             'created', CURRENT_TIMESTAMP(), '{request_id}')
            """
            
            self._execute_query(query)
            
        except Exception as e:
            logger.warning(f"Failed to store execution plan: {e}")
    
    def _execute_plan(
        self,
        plan: List[Any],
        request_id: str,
        user_id: str,
        user_role: str
    ) -> List[Dict[str, Any]]:
        """
        Execute the plan by delegating tasks to agents via message bus.
        
        Args:
            plan: Execution plan
            request_id: Request ID
            user_id: User ID
            user_role: User's role
        
        Returns:
            List of task results
        """
        results: List[Dict[str, Any]] = []
        completed_tasks: Dict[str, Any] = {}  # task_id -> result
        
        for task in plan:
            # Check dependencies
            if task.dependencies:
                deps_ready = all(dep in completed_tasks for dep in task.dependencies)
                if not deps_ready:
                    logger.warning(f"Task {task.task_id} dependencies not ready, skipping")
                    continue
            
            # Get dependency results as context
            context = {}
            for dep_id in task.dependencies:
                if dep_id in completed_tasks:
                    context[dep_id] = completed_tasks[dep_id]
            
            # Send message to agent
            message_content = {
                "request_id": request_id,
                "task_id": task.task_id,
                "task_description": task.task_description,
                "user_id": user_id,
                "user_role": user_role,
                "context": context
            }
            
            message_id = self.send_message(
                to_agent=task.agent_type,
                content=message_content,
                message_type="request",
                correlation_id=request_id,
                priority=10 - len(results)  # Higher priority for earlier tasks
            )
            
            # Wait for response (in production, use async/polling)
            # For now, simulate synchronous execution
            logger.info(f"Sent task {task.task_id} to {task.agent_type}, waiting for response...")
            
            # In real implementation, poll message bus for response
            # For now, return placeholder
            result = {
                "task_id": task.task_id,
                "agent_type": task.agent_type,
                "status": "sent",
                "message_id": message_id
            }
            
            results.append(result)
            completed_tasks[task.task_id] = result
        
        return results
    
    def _aggregate_responses(self, results: List[Dict[str, Any]], user_query: str) -> Dict[str, Any]:
        """
        Aggregate responses from all agents.
        
        Args:
            results: List of task results
            user_query: Original user query
        
        Returns:
            Aggregated response
        """
        aggregated = {
            "query": user_query,
            "tasks_completed": len(results),
            "task_results": results,
            "final_answer": None
        }
        
        # Extract final answer from last task result
        if results:
            last_result = results[-1]
            if "output" in last_result:
                aggregated["final_answer"] = last_result["output"]
        
        return aggregated
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a task (implements BaseAgent interface).
        
        Args:
            task: Task dictionary
            context: Optional context
        
        Returns:
            Result dictionary
        """
        # Orchestrator doesn't process tasks directly
        # It delegates to other agents
        return {
            "status": "delegated",
            "message": "Orchestrator delegates tasks to specialized agents"
        }
    
    def _execute_query(self, query: str) -> None:
        """Execute SQL query."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark.sql(query)
        except Exception as e:
            logger.warning(f"Failed to execute query: {e}")


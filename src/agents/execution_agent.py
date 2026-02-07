"""
Execution Agent
===============

Controlled code execution agent.

Features:
- DANGEROUS AGENT - requires approval
- Executes SQL/PySpark/Python code
- RBAC-restricted execution
- Fully audited every action
- Dry-run first, then execute
- Returns execution results

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.governance.approval_workflow import ApprovalWorkflow
from src.governance.audit_logger import AuditLogger
from src.governance.rbac import RBACManager

logger = get_logger(__name__)


class ExecutionAgent(BaseAgent):
    """
    Code execution agent (requires approval).
    """
    
    def __init__(self):
        """Initialize ExecutionAgent."""
        super().__init__("ExecutionAgent")
        self.approval_workflow = ApprovalWorkflow()
        self.audit_logger = AuditLogger()
        self.rbac_manager = RBACManager()
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an execution task (requires approval).
        
        Args:
            task: Task dictionary with code to execute
            context: Context from previous agents
        
        Returns:
            Execution result dictionary
        """
        try:
            request_id = task.get("request_id")
            user_id = task.get("user_id")
            user_role = task.get("user_role", "viewer")
            code = task.get("code", "")
            
            logger.warning(f"ExecutionAgent received execution request {request_id}")
            
            # Check RBAC
            if not self.rbac_manager.check_permission(user_role, "execute_sql"):
                logger.warning(f"User {user_id} with role {user_role} denied execution")
                return {
                    "status": "denied",
                    "error": "Insufficient permissions for code execution"
                }
            
            # Check for approval
            approval_request_id = task.get("approval_request_id")
            if not approval_request_id:
                # Create approval request
                approval_request_id = self.approval_workflow.create_approval_request(
                    request_type="execution",
                    requester_agent="ExecutionAgent",
                    requester_user=user_id,
                    request_content={"code": code[:500]},
                    priority=10
                )
                
                return {
                    "status": "pending_approval",
                    "approval_request_id": approval_request_id,
                    "message": "Execution requires approval"
                }
            
            # Check approval status
            approval_status = self.approval_workflow.check_approval_status(approval_request_id)
            if approval_status != "approved":
                return {
                    "status": "pending_approval",
                    "approval_status": approval_status
                }
            
            # Log audit
            self.audit_logger.log(
                event_type="execution",
                actor=user_id,
                action="execute_code",
                resource_type="code",
                details={"code_preview": code[:100]}
            )
            
            # Dry-run first
            dry_run_result = self._dry_run(code)
            
            if not dry_run_result.get("safe", False):
                return {
                    "status": "rejected",
                    "error": "Code failed safety check",
                    "dry_run_result": dry_run_result
                }
            
            # Execute code
            execution_result = self._execute_code(code)
            
            result = {
                "status": "success",
                "execution_result": execution_result,
                "dry_run_passed": True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"ExecutionAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _dry_run(self, code: str) -> Dict[str, Any]:
        """
        Perform dry-run safety check.
        
        Args:
            code: Code to check
        
        Returns:
            Dry-run result
        """
        # Check for dangerous operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "SHUTDOWN"]
        code_upper = code.upper()
        
        for keyword in dangerous_keywords:
            if keyword in code_upper:
                return {
                    "safe": False,
                    "reason": f"Dangerous keyword detected: {keyword}"
                }
        
        return {
            "safe": True,
            "reason": "Code passed safety checks"
        }
    
    def _execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute code (simulated - in production use actual execution).
        
        Args:
            code: Code to execute
        
        Returns:
            Execution result
        """
        # In production, execute using Databricks SQL or Spark
        logger.warning("Executing code (simulated)")
        
        return {
            "rows_affected": 0,
            "execution_time_ms": 100,
            "success": True
        }


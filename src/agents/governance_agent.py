"""
Governance Agent
================

Approval authority agent.

Features:
- Enforces approval workflows
- Controls model promotion (dev → prod)
- Manages RBAC policies
- Approval timeout handling
- Auto-approve based on confidence threshold
- Returns approval decision

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.governance.approval_workflow import ApprovalWorkflow

logger = get_logger(__name__)


class GovernanceAgent(BaseAgent):
    """
    Governance and approval agent.
    """
    
    def __init__(self):
        """Initialize GovernanceAgent."""
        super().__init__("GovernanceAgent")
        self.approval_workflow = ApprovalWorkflow()
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a governance/approval task.
        
        Args:
            task: Task dictionary
            context: Context from previous agents
        
        Returns:
            Approval decision dictionary
        """
        try:
            request_type = task.get("request_type", "")
            request_id = task.get("request_id", "")
            approver_user = task.get("approver_user", "system")
            
            logger.info(f"GovernanceAgent processing {request_type} request {request_id}")
            
            if request_type == "approval":
                # Handle approval request
                action = task.get("action", "approve")
                
                if action == "approve":
                    success = self.approval_workflow.approve_request(
                        request_id=request_id,
                        approved_by=approver_user,
                        notes=task.get("notes", "")
                    )
                else:
                    success = self.approval_workflow.reject_request(
                        request_id=request_id,
                        rejected_by=approver_user,
                        reason=task.get("reason", "")
                    )
                
                return {
                    "status": "success" if success else "error",
                    "action": action,
                    "request_id": request_id
                }
            
            elif request_type == "retraining":
                # Create retraining approval request
                approval_id = self.approval_workflow.create_approval_request(
                    request_type="retraining",
                    requester_agent="OptimizerAgent",
                    requester_user=None,
                    request_content=task.get("content", {}),
                    priority=task.get("priority", 5)
                )
                
                return {
                    "status": "success",
                    "approval_request_id": approval_id,
                    "message": "Retraining approval request created"
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown request type: {request_type}"
                }
            
        except Exception as e:
            logger.error(f"GovernanceAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


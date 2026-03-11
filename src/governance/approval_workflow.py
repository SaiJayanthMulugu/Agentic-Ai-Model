"""
Approval Workflow
=================

Manages approval workflows for sensitive operations.

Features:
- Approval request creation
- Approval decision making
- Auto-approval based on confidence
- Timeout handling
- Approval history

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class ApprovalWorkflow:
    """
    Manages approval workflows.
    """
    
    def __init__(self):
        """Initialize ApprovalWorkflow."""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load("env.dev.yaml")
        self.auto_approve_threshold = self.config.get("security", {}).get("auto_approve_confidence_threshold", 0.95)
        self.approval_timeout_hours = 24
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.table_name = f"{self.catalog}.{self.schema}.approval_requests"
    
    def create_approval_request(
        self,
        request_type: str,
        requester_agent: str,
        requester_user: Optional[str],
        request_content: Dict[str, Any],
        priority: int = 5,
        confidence_score: Optional[float] = None
    ) -> str:
        """
        Create an approval request.
        
        Args:
            request_type: Type of request (execution, retraining, knowledge_add, model_promotion)
            requester_agent: Agent requesting approval
            requester_user: User ID (optional)
            request_content: Request content dictionary
            priority: Request priority (1-10)
            confidence_score: Confidence score for auto-approval
        
        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=self.approval_timeout_hours)
        
        # Check for auto-approval
        auto_approved = False
        status = "pending_approval"
        
        if confidence_score and confidence_score >= self.auto_approve_threshold:
            auto_approved = True
            status = "approved"
            logger.info(f"Request {request_id} auto-approved with confidence {confidence_score}")
        
        try:
            import json
            content_json = json.dumps(request_content)
            
            query = f"""
            INSERT INTO {self.table_name}
            (request_id, request_type, requester_agent, requester_user, request_content, status,
             priority, created_at, approved_at, expires_at, auto_approved, confidence_score)
            VALUES
            ('{request_id}', '{request_type}', '{requester_agent}', '{requester_user or ''}',
             '{content_json}', '{status}', {priority}, CURRENT_TIMESTAMP(),
             {'CURRENT_TIMESTAMP()' if auto_approved else 'NULL'},
             '{expires_at.isoformat()}', {str(auto_approved).lower()}, {confidence_score or 'NULL'})
            """
            
            self._execute_query(query)
            
            if auto_approved:
                self._log_approval_history(request_id, "approved", "system", "Auto-approved based on confidence threshold")
            
            logger.info(f"Created approval request {request_id} of type {request_type}")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            raise
    
    def approve_request(self, request_id: str, approved_by: str, notes: Optional[str] = None) -> bool:
        """
        Approve an approval request.
        
        Args:
            request_id: Request ID
            approved_by: User/agent approving the request
            notes: Optional approval notes
        
        Returns:
            True if approved successfully
        """
        try:
            query = f"""
            UPDATE {self.table_name}
            SET status = 'approved',
                approved_at = CURRENT_TIMESTAMP(),
                approved_by = '{approved_by}'
            WHERE request_id = '{request_id}'
              AND status = 'pending_approval'
            """
            
            self._execute_query(query)
            self._log_approval_history(request_id, "approved", approved_by, notes)
            
            logger.info(f"Request {request_id} approved by {approved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve request: {e}")
            return False
    
    def reject_request(self, request_id: str, rejected_by: str, reason: str) -> bool:
        """
        Reject an approval request.
        
        Args:
            request_id: Request ID
            rejected_by: User/agent rejecting the request
            reason: Rejection reason
        
        Returns:
            True if rejected successfully
        """
        try:
            query = f"""
            UPDATE {self.table_name}
            SET status = 'rejected',
                rejection_reason = '{reason}'
            WHERE request_id = '{request_id}'
              AND status = 'pending_approval'
            """
            
            self._execute_query(query)
            self._log_approval_history(request_id, "rejected", rejected_by, reason)
            
            logger.info(f"Request {request_id} rejected by {rejected_by}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reject request: {e}")
            return False
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get approval request by ID.
        
        Args:
            request_id: Request ID
        
        Returns:
            Request dictionary or None
        """
        try:
            query = f"""
            SELECT request_id, request_type, requester_agent, requester_user, request_content,
                   status, priority, created_at, approved_at, approved_by, rejection_reason,
                   expires_at, auto_approved, confidence_score
            FROM {self.table_name}
            WHERE request_id = '{request_id}'
            """
            
            results = self._execute_query(query, fetch=True)
            
            if results and len(results) > 0:
                row = results[0]
                import json
                return {
                    "request_id": row[0],
                    "request_type": row[1],
                    "requester_agent": row[2],
                    "requester_user": row[3],
                    "request_content": json.loads(row[4]) if isinstance(row[4], str) else row[4],
                    "status": row[5],
                    "priority": row[6],
                    "created_at": row[7],
                    "approved_at": row[8],
                    "approved_by": row[9],
                    "rejection_reason": row[10],
                    "expires_at": row[11],
                    "auto_approved": row[12],
                    "confidence_score": row[13]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get request: {e}")
            return None
    
    def check_approval_status(self, request_id: str) -> Optional[str]:
        """
        Check approval status.
        
        Args:
            request_id: Request ID
        
        Returns:
            Status string or None
        """
        request = self.get_request(request_id)
        return request.get("status") if request else None
    
    def _log_approval_history(self, request_id: str, action: str, actor: str, notes: Optional[str] = None) -> None:
        """Log approval history."""
        try:
            history_id = str(uuid.uuid4())
            history_table = f"{self.catalog}.{self.schema}.approval_history"
            
            query = f"""
            INSERT INTO {history_table}
            (history_id, request_id, action, actor, timestamp, notes)
            VALUES
            ('{history_id}', '{request_id}', '{action}', '{actor}', CURRENT_TIMESTAMP(), '{notes or ''}')
            """
            
            self._execute_query(query)
            
        except Exception as e:
            logger.warning(f"Failed to log approval history: {e}")
    
    def _execute_query(self, query: str, fetch: bool = False) -> Any:
        """Execute SQL query."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                if fetch:
                    return spark.sql(query).collect()
                else:
                    spark.sql(query)
                    return None
        except:
            pass
        
        logger.warning("No database connection available. Approval workflow operations may fail.")
        return None if not fetch else []


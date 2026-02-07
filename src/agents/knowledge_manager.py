"""
Knowledge Manager
=================

Knowledge lifecycle management agent.

Features:
- Knowledge base management
- Document lifecycle
- Quality control
- Approval workflows

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.governance.knowledge_quality_control import KnowledgeQualityControl
from src.governance.rag_approval_workflow import RAGApprovalWorkflow

logger = get_logger(__name__)


class KnowledgeManager(BaseAgent):
    """
    Knowledge lifecycle management agent.
    """
    
    def __init__(self):
        """Initialize KnowledgeManager."""
        super().__init__("KnowledgeManager")
        self.quality_control = KnowledgeQualityControl()
        self.approval_workflow = RAGApprovalWorkflow()
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a knowledge management task.
        
        Args:
            task: Task dictionary
            context: Context from previous agents
        
        Returns:
            Knowledge management result
        """
        try:
            operation = task.get("operation", "add")
            
            if operation == "add":
                # Add new document
                doc_id = task.get("doc_id")
                content = task.get("content")
                title = task.get("title", "")
                user_id = task.get("user_id", "")
                
                # Quality check
                quality_result = self.quality_control.evaluate_quality(content, title)
                
                if not quality_result.get("meets_threshold", False):
                    return {
                        "status": "rejected",
                        "error": "Document does not meet quality threshold",
                        "quality_result": quality_result
                    }
                
                # Create approval request
                approval_id = self.approval_workflow.create_document_approval_request(
                    doc_id=doc_id,
                    content=content,
                    requester_user=user_id,
                    confidence_score=quality_result.get("quality_score", 0.0)
                )
                
                return {
                    "status": "pending_approval",
                    "approval_request_id": approval_id,
                    "quality_result": quality_result
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            logger.error(f"KnowledgeManager failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


"""
RAG Approval Workflow
======================

Specialized approval workflow for RAG knowledge base operations.

Author: AI Ops Team
Version: 1.0.0
"""

from src.governance.approval_workflow import ApprovalWorkflow
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RAGApprovalWorkflow(ApprovalWorkflow):
    """Specialized approval workflow for RAG operations."""
    
    def create_document_approval_request(
        self,
        doc_id: str,
        content: str,
        requester_user: str,
        confidence_score: float = 0.0
    ) -> str:
        """
        Create approval request for new knowledge base document.
        
        Args:
            doc_id: Document ID
            content: Document content
            requester_user: User requesting approval
            confidence_score: Confidence score
        
        Returns:
            Request ID
        """
        request_content = {
            "doc_id": doc_id,
            "content": content[:500],  # Truncate for storage
            "action": "add_document"
        }
        
        return self.create_approval_request(
            request_type="knowledge_add",
            requester_agent="RAGAgent",
            requester_user=requester_user,
            request_content=request_content,
            confidence_score=confidence_score
        )


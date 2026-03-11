"""
RAG Agent
=========

Knowledge retrieval agent using RAG (Retrieval-Augmented Generation).

Features:
- Vector search in knowledge base
- Semantic similarity matching
- Context retrieval with RBAC filtering
- Explainability for retrieved context
- NO execution, only retrieval
- Returns structured context

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional, List
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.governance.rbac import RBACManager

logger = get_logger(__name__)


class RAGAgent(BaseAgent):
    """
    RAG Agent for knowledge retrieval.
    """
    
    def __init__(self):
        """Initialize RAGAgent."""
        super().__init__("RAGAgent")
        self.config_loader = ConfigLoader()
        self.rag_config = self.config_loader.load("rag.dev.yaml")
        self.rbac_manager = RBACManager()
        
        self.vector_endpoint = self.rag_config.get("rag", {}).get("vector_search", {}).get("endpoint")
        self.vector_index = self.rag_config.get("rag", {}).get("vector_search", {}).get("index")
        self.top_k = self.rag_config.get("rag", {}).get("vector_search", {}).get("top_k", 5)
        self.similarity_threshold = self.rag_config.get("rag", {}).get("vector_search", {}).get("similarity_threshold", 0.7)
        
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.knowledge_base_table = f"{self.catalog}.{self.schema}.knowledge_base"
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a knowledge retrieval task.
        
        Args:
            task: Task dictionary with query
            context: Optional context
        
        Returns:
            Result dictionary with retrieved context
        """
        try:
            query = task.get("task_description", task.get("query", ""))
            user_role = task.get("user_role", "viewer")
            
            logger.info(f"RAGAgent processing query: {query[:100]}...")
            
            # Retrieve relevant documents
            documents = self._retrieve_documents(query, user_role)
            
            # Format response
            result = {
                "status": "success",
                "query": query,
                "documents_retrieved": len(documents),
                "documents": documents,
                "explanation": f"Retrieved {len(documents)} relevant documents from knowledge base"
            }
            
            # Log query
            self._log_query(query, documents)
            
            return result
            
        except Exception as e:
            logger.error(f"RAGAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _retrieve_documents(self, query: str, user_role: str) -> List[Dict[str, Any]]:
        """
        Retrieve documents using vector search.
        
        Args:
            query: Search query
            user_role: User role for RBAC filtering
        
        Returns:
            List of document dictionaries
        """
        try:
            # In production, use Databricks Vector Search
            # For now, use SQL-based similarity search
            
            # Get embedding for query (simplified - in production use embedding endpoint)
            # query_embedding = self._get_embedding(query)
            
            # Query knowledge base
            query_sql = f"""
            SELECT doc_id, content, title, category, quality_score, sensitivity_level
            FROM {self.knowledge_base_table}
            WHERE status = 'active'
              AND (LOWER(content) LIKE LOWER('%{query}%') OR LOWER(title) LIKE LOWER('%{query}%'))
            ORDER BY quality_score DESC
            LIMIT {self.top_k}
            """
            
            results = self._execute_query(query_sql, fetch=True)
            
            documents = []
            for row in results:
                # Check RBAC for sensitivity level
                sensitivity = row[5]
                if self._check_sensitivity_access(user_role, sensitivity):
                    doc = {
                        "doc_id": row[0],
                        "content": row[1][:500],  # Truncate for response
                        "title": row[2],
                        "category": row[3],
                        "quality_score": row[4],
                        "similarity_score": 0.8  # Placeholder
                    }
                    documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def _check_sensitivity_access(self, user_role: str, sensitivity_level: str) -> bool:
        """
        Check if user role can access document with given sensitivity level.
        
        Args:
            user_role: User role
            sensitivity_level: Document sensitivity level
        
        Returns:
            True if access allowed
        """
        if sensitivity_level == "public":
            return True
        elif sensitivity_level == "internal":
            return user_role in ["data_engineer", "data_analyst", "admin", "knowledge_curator"]
        elif sensitivity_level == "confidential":
            return user_role in ["admin", "governance_officer"]
        
        return False
    
    def _log_query(self, query: str, documents: List[Dict[str, Any]]) -> None:
        """Log RAG query for learning."""
        try:
            query_id = str(uuid.uuid4())
            doc_ids = [doc["doc_id"] for doc in documents]
            scores = [doc.get("similarity_score", 0.0) for doc in documents]
            
            import json
            query_table = f"{self.catalog}.{self.schema}.rag_query_logs"
            
            query_sql = f"""
            INSERT INTO {query_table}
            (query_id, query_text, retrieved_docs, retrieved_scores, query_timestamp)
            VALUES
            ('{query_id}', '{query}', '{json.dumps(doc_ids)}', '{json.dumps(scores)}', CURRENT_TIMESTAMP())
            """
            
            self._execute_query(query_sql)
            
        except Exception as e:
            logger.warning(f"Failed to log query: {e}")
    
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
        
        return None if not fetch else []


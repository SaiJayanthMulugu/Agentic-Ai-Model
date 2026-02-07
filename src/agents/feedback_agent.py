"""
Feedback Agent
==============

Learning signal collection agent.

Features:
- Captures user ratings (thumbs up/down, 1-5 stars)
- Tracks failures and corrections
- Stores feedback in Delta tables
- Triggers learning signals
- Returns feedback ID

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class FeedbackAgent(BaseAgent):
    """
    Feedback collection agent.
    """
    
    def __init__(self):
        """Initialize FeedbackAgent."""
        super().__init__("FeedbackAgent")
        self.config_loader = ConfigLoader()
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.feedback_table = f"{self.catalog}.{self.schema}.rag_user_feedback"
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a feedback collection task.
        
        Args:
            task: Task dictionary with feedback data
            context: Context from previous agents
        
        Returns:
            Feedback result dictionary
        """
        try:
            query_id = task.get("query_id", "")
            user_id = task.get("user_id", "")
            feedback_type = task.get("feedback_type", "thumbs_up")
            rating_value = task.get("rating_value")
            feedback_text = task.get("feedback_text", "")
            correction_text = task.get("correction_text", "")
            
            logger.info(f"FeedbackAgent collecting feedback: {feedback_type}")
            
            # Store feedback
            feedback_id = self._store_feedback(
                query_id=query_id,
                user_id=user_id,
                feedback_type=feedback_type,
                rating_value=rating_value,
                feedback_text=feedback_text,
                correction_text=correction_text
            )
            
            # Trigger learning signal if negative feedback
            if feedback_type in ["thumbs_down", "rating"] and (rating_value is None or rating_value < 3):
                self.publish_event("learning_signal", {
                    "type": "negative_feedback",
                    "feedback_id": feedback_id,
                    "query_id": query_id
                })
            
            result = {
                "status": "success",
                "feedback_id": feedback_id,
                "message": "Feedback collected successfully"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"FeedbackAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _store_feedback(
        self,
        query_id: str,
        user_id: str,
        feedback_type: str,
        rating_value: Optional[int],
        feedback_text: str,
        correction_text: str
    ) -> str:
        """
        Store feedback in database.
        
        Args:
            query_id: Query ID
            user_id: User ID
            feedback_type: Type of feedback
            rating_value: Rating value (1-5)
            feedback_text: Feedback text
            correction_text: Correction text
        
        Returns:
            Feedback ID
        """
        feedback_id = str(uuid.uuid4())
        
        try:
            query = f"""
            INSERT INTO {self.feedback_table}
            (feedback_id, query_id, user_id, feedback_type, rating_value, feedback_text,
             correction_text, is_helpful, feedback_timestamp, processed)
            VALUES
            ('{feedback_id}', '{query_id}', '{user_id}', '{feedback_type}', {rating_value or 'NULL'},
             '{feedback_text}', '{correction_text}', {feedback_type == 'thumbs_up'}, CURRENT_TIMESTAMP(), false)
            """
            
            self._execute_query(query)
            logger.info(f"Stored feedback {feedback_id}")
            
            return feedback_id
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            raise
    
    def _execute_query(self, query: str) -> None:
        """Execute SQL query."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark.sql(query)
        except Exception as e:
            logger.warning(f"Failed to execute feedback query: {e}")


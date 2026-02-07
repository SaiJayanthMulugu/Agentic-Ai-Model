"""
Message Bus
===========

Event-driven message passing system for agent-to-agent communication.

Features:
- Delta table-based message bus
- Priority-based message handling
- Correlation ID tracking
- Message TTL and cleanup
- Polling-based message retrieval

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

try:
    from databricks import sql
    HAS_DATABRICKS_SQL = True
except ImportError:
    HAS_DATABRICKS_SQL = False

from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader
from src.utils.secrets_manager import SecretsManager

logger = get_logger(__name__)


class MessageBus:
    """
    Message bus for agent-to-agent communication using Delta tables.
    """
    
    def __init__(self, connection: Optional[Any] = None):
        """
        Initialize MessageBus.
        
        Args:
            connection: Databricks SQL connection (optional, will create if not provided)
        """
        self.config_loader = ConfigLoader()
        self.secrets_manager = SecretsManager()
        self.connection = connection
        self.config = self.config_loader.load("mas_config.yaml")
        self.table_name = self.config.get("mas", {}).get("message_bus", {}).get("table_name", "agent_messages")
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.full_table_name = f"{self.catalog}.{self.schema}.{self.table_name}"
    
    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        content: Dict[str, Any],
        message_type: str = "request",
        correlation_id: Optional[str] = None,
        priority: int = 5
    ) -> str:
        """
        Send a message to another agent.
        
        Args:
            from_agent: Sender agent name
            to_agent: Recipient agent name
            content: Message content (will be JSON serialized)
            message_type: Message type (request, response, event, notification)
            correlation_id: Correlation ID for tracking conversations
            priority: Message priority (1-10, 10 is highest)
        
        Returns:
            Message ID
        """
        message_id = str(uuid.uuid4())
        
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        
        message = {
            "message_id": message_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "priority": priority,
            "status": "pending"
        }
        
        try:
            # Insert message into Delta table
            import json
            content_json = json.dumps(content)
            
            query = f"""
            INSERT INTO {self.full_table_name}
            (message_id, from_agent, to_agent, message_type, content, timestamp, correlation_id, priority, status)
            VALUES
            ('{message_id}', '{from_agent}', '{to_agent}', '{message_type}', '{content_json}', 
             '{message["timestamp"]}', '{correlation_id}', {priority}, 'pending')
            """
            
            self._execute_query(query)
            
            logger.info(f"Message {message_id} sent from {from_agent} to {to_agent}")
            return message_id
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    def receive_messages(
        self,
        agent_name: str,
        message_type: Optional[str] = None,
        limit: int = 10,
        priority_threshold: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Receive messages for an agent.
        
        Args:
            agent_name: Agent name to receive messages for
            message_type: Filter by message type (optional)
            limit: Maximum number of messages to retrieve
            priority_threshold: Minimum priority (default: 0, gets all)
        
        Returns:
            List of messages
        """
        try:
            query = f"""
            SELECT message_id, from_agent, to_agent, message_type, content, timestamp, 
                   correlation_id, priority, status
            FROM {self.full_table_name}
            WHERE to_agent = '{agent_name}'
              AND status = 'pending'
              AND priority >= {priority_threshold}
            """
            
            if message_type:
                query += f" AND message_type = '{message_type}'"
            
            query += f" ORDER BY priority DESC, timestamp ASC LIMIT {limit}"
            
            results = self._execute_query(query, fetch=True)
            
            messages = []
            for row in results:
                import json
                message = {
                    "message_id": row[0],
                    "from_agent": row[1],
                    "to_agent": row[2],
                    "message_type": row[3],
                    "content": json.loads(row[4]) if isinstance(row[4], str) else row[4],
                    "timestamp": row[5],
                    "correlation_id": row[6],
                    "priority": row[7],
                    "status": row[8]
                }
                messages.append(message)
            
            logger.debug(f"Retrieved {len(messages)} messages for {agent_name}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to receive messages: {e}")
            return []
    
    def mark_message_processed(self, message_id: str, success: bool = True, error_message: Optional[str] = None) -> None:
        """
        Mark a message as processed.
        
        Args:
            message_id: Message ID
            success: Whether processing was successful
            error_message: Error message if processing failed
        """
        try:
            status = "processed" if success else "failed"
            error_clause = f", error_message = '{error_message}'" if error_message else ""
            
            query = f"""
            UPDATE {self.full_table_name}
            SET status = '{status}',
                processed_at = CURRENT_TIMESTAMP()
                {error_clause}
            WHERE message_id = '{message_id}'
            """
            
            self._execute_query(query)
            logger.debug(f"Marked message {message_id} as {status}")
            
        except Exception as e:
            logger.error(f"Failed to mark message as processed: {e}")
            raise
    
    def _execute_query(self, query: str, fetch: bool = False) -> Any:
        """
        Execute SQL query.
        
        Args:
            query: SQL query string
            fetch: Whether to fetch results
        
        Returns:
            Query results if fetch=True, None otherwise
        """
        # In Databricks notebooks, use spark.sql
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
        
        # Fallback: Use Databricks SQL connector if available
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            if fetch:
                return cursor.fetchall()
            cursor.close()
            return None
        
        # If no connection available, log warning
        logger.warning("No database connection available. Message bus operations may fail.")
        return None if not fetch else []


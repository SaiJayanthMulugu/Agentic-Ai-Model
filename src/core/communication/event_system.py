"""
Event System
============

Event-driven communication system for agents.

Features:
- Event publishing and subscription
- Event filtering by type
- Event TTL and cleanup
- Subscriber management

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class EventSystem:
    """
    Event system for event-driven agent communication.
    """
    
    def __init__(self):
        """Initialize EventSystem."""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load("mas_config.yaml")
        self.table_name = self.config.get("mas", {}).get("event_system", {}).get("table_name", "agent_events")
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.full_table_name = f"{self.catalog}.{self.schema}.{self.table_name}"
    
    def publish_event(
        self,
        event_type: str,
        source_agent: str,
        event_data: Dict[str, Any],
        subscribers: Optional[List[str]] = None
    ) -> str:
        """
        Publish an event.
        
        Args:
            event_type: Event type (task_completed, approval_needed, etc.)
            source_agent: Agent that published the event
            event_data: Event data dictionary
            subscribers: List of agent IDs subscribed to this event type
        
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        
        try:
            import json
            event_data_json = json.dumps(event_data)
            subscribers_json = json.dumps(subscribers or [])
            
            query = f"""
            INSERT INTO {self.full_table_name}
            (event_id, event_type, source_agent, event_data, timestamp, processed, subscribers)
            VALUES
            ('{event_id}', '{event_type}', '{source_agent}', '{event_data_json}', 
             '{datetime.utcnow().isoformat()}', false, '{subscribers_json}')
            """
            
            self._execute_query(query)
            
            logger.info(f"Event {event_id} of type {event_type} published by {source_agent}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise
    
    def subscribe_to_event(self, agent_id: str, event_type: str) -> None:
        """
        Subscribe an agent to an event type.
        
        Args:
            agent_id: Agent ID
            event_type: Event type to subscribe to
        """
        try:
            subscription_id = str(uuid.uuid4())
            table_name = f"{self.catalog}.{self.schema}.agent_event_subscriptions"
            
            query = f"""
            INSERT INTO {table_name}
            (subscription_id, agent_id, event_type, subscribed_at, active)
            VALUES
            ('{subscription_id}', '{agent_id}', '{event_type}', CURRENT_TIMESTAMP(), true)
            """
            
            self._execute_query(query)
            logger.info(f"Agent {agent_id} subscribed to event type {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to event: {e}")
            raise
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        source_agent: Optional[str] = None,
        processed: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get events matching criteria.
        
        Args:
            event_type: Filter by event type (optional)
            source_agent: Filter by source agent (optional)
            processed: Filter by processed status
            limit: Maximum number of events to retrieve
        
        Returns:
            List of events
        """
        try:
            query = f"""
            SELECT event_id, event_type, source_agent, event_data, timestamp, processed, subscribers
            FROM {self.full_table_name}
            WHERE processed = {str(processed).lower()}
            """
            
            if event_type:
                query += f" AND event_type = '{event_type}'"
            
            if source_agent:
                query += f" AND source_agent = '{source_agent}'"
            
            query += f" ORDER BY timestamp DESC LIMIT {limit}"
            
            results = self._execute_query(query, fetch=True)
            
            events = []
            for row in results:
                import json
                event = {
                    "event_id": row[0],
                    "event_type": row[1],
                    "source_agent": row[2],
                    "event_data": json.loads(row[3]) if isinstance(row[3], str) else row[3],
                    "timestamp": row[4],
                    "processed": row[5],
                    "subscribers": json.loads(row[6]) if isinstance(row[6], str) else row[6]
                }
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []
    
    def mark_event_processed(self, event_id: str) -> None:
        """
        Mark an event as processed.
        
        Args:
            event_id: Event ID
        """
        try:
            query = f"""
            UPDATE {self.full_table_name}
            SET processed = true, processed_at = CURRENT_TIMESTAMP()
            WHERE event_id = '{event_id}'
            """
            
            self._execute_query(query)
            logger.debug(f"Marked event {event_id} as processed")
            
        except Exception as e:
            logger.error(f"Failed to mark event as processed: {e}")
            raise
    
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
        
        logger.warning("No database connection available. Event system operations may fail.")
        return None if not fetch else []


"""
Agent Registry
==============

Manages agent registration and discovery.

Features:
- Agent registration
- Agent status tracking
- Agent discovery
- Heartbeat monitoring

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class AgentRegistry:
    """
    Registry for managing agent registration and discovery.
    """
    
    def __init__(self):
        """Initialize AgentRegistry."""
        self.config_loader = ConfigLoader()
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.table_name = f"{self.catalog}.{self.schema}.agent_registry"
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        version: str = "1.0.0",
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Register an agent in the registry.
        
        Args:
            agent_id: Unique agent ID
            agent_name: Agent name
            agent_type: Agent type/class
            capabilities: List of agent capabilities
            version: Agent version
            metadata: Optional metadata dictionary
        """
        try:
            import json
            capabilities_json = json.dumps(capabilities)
            metadata_json = json.dumps(metadata or {})
            
            query = f"""
            MERGE INTO {self.table_name} AS target
            USING (SELECT '{agent_id}' AS agent_id) AS source
            ON target.agent_id = source.agent_id
            WHEN MATCHED THEN
                UPDATE SET
                    agent_name = '{agent_name}',
                    agent_type = '{agent_type}',
                    status = 'active',
                    version = '{version}',
                    capabilities = '{capabilities_json}',
                    metadata = '{metadata_json}',
                    last_heartbeat = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (agent_id, agent_name, agent_type, status, version, capabilities, metadata, registered_at, last_heartbeat)
                VALUES ('{agent_id}', '{agent_name}', '{agent_type}', 'active', '{version}', 
                        '{capabilities_json}', '{metadata_json}', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
            """
            
            self._execute_query(query)
            logger.info(f"Registered agent: {agent_name} (ID: {agent_id})")
            
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    def update_heartbeat(self, agent_id: str) -> None:
        """
        Update agent heartbeat.
        
        Args:
            agent_id: Agent ID
        """
        try:
            query = f"""
            UPDATE {self.table_name}
            SET last_heartbeat = CURRENT_TIMESTAMP()
            WHERE agent_id = '{agent_id}'
            """
            
            self._execute_query(query)
            
        except Exception as e:
            logger.error(f"Failed to update heartbeat: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent dictionary or None
        """
        try:
            query = f"""
            SELECT agent_id, agent_name, agent_type, status, version, capabilities, metadata,
                   registered_at, last_heartbeat
            FROM {self.table_name}
            WHERE agent_id = '{agent_id}'
            """
            
            results = self._execute_query(query, fetch=True)
            
            if results and len(results) > 0:
                row = results[0]
                import json
                return {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "agent_type": row[2],
                    "status": row[3],
                    "version": row[4],
                    "capabilities": json.loads(row[5]) if isinstance(row[5], str) else row[5],
                    "metadata": json.loads(row[6]) if isinstance(row[6], str) else row[6],
                    "registered_at": row[7],
                    "last_heartbeat": row[8]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get agent: {e}")
            return None
    
    def get_agents_by_type(self, agent_type: str, status: str = "active") -> List[Dict[str, Any]]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Agent type
            status: Agent status filter
        
        Returns:
            List of agent dictionaries
        """
        try:
            query = f"""
            SELECT agent_id, agent_name, agent_type, status, version, capabilities, metadata,
                   registered_at, last_heartbeat
            FROM {self.table_name}
            WHERE agent_type = '{agent_type}' AND status = '{status}'
            """
            
            results = self._execute_query(query, fetch=True)
            
            agents = []
            for row in results:
                import json
                agent = {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "agent_type": row[2],
                    "status": row[3],
                    "version": row[4],
                    "capabilities": json.loads(row[5]) if isinstance(row[5], str) else row[5],
                    "metadata": json.loads(row[6]) if isinstance(row[6], str) else row[6],
                    "registered_at": row[7],
                    "last_heartbeat": row[8]
                }
                agents.append(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get agents by type: {e}")
            return []
    
    def get_all_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all registered agents.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of agent dictionaries
        """
        try:
            query = f"""
            SELECT agent_id, agent_name, agent_type, status, version, capabilities, metadata,
                   registered_at, last_heartbeat
            FROM {self.table_name}
            """
            
            if status:
                query += f" WHERE status = '{status}'"
            
            results = self._execute_query(query, fetch=True)
            
            agents = []
            for row in results:
                import json
                agent = {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "agent_type": row[2],
                    "status": row[3],
                    "version": row[4],
                    "capabilities": json.loads(row[5]) if isinstance(row[5], str) else row[5],
                    "metadata": json.loads(row[6]) if isinstance(row[6], str) else row[6],
                    "registered_at": row[7],
                    "last_heartbeat": row[8]
                }
                agents.append(agent)
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get all agents: {e}")
            return []
    
    def update_agent_status(self, agent_id: str, status: str, reason: Optional[str] = None) -> None:
        """
        Update agent status.
        
        Args:
            agent_id: Agent ID
            status: New status
            reason: Optional reason for status change
        """
        try:
            query = f"""
            UPDATE {self.table_name}
            SET status = '{status}'
            WHERE agent_id = '{agent_id}'
            """
            
            self._execute_query(query)
            
            # Log status change
            history_table = f"{self.catalog}.{self.schema}.agent_status_history"
            history_id = str(uuid.uuid4())
            
            history_query = f"""
            INSERT INTO {history_table}
            (status_id, agent_id, status, changed_at, reason)
            VALUES
            ('{history_id}', '{agent_id}', '{status}', CURRENT_TIMESTAMP(), '{reason or ''}')
            """
            
            self._execute_query(history_query)
            logger.info(f"Updated agent {agent_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
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
        
        logger.warning("No database connection available. Registry operations may fail.")
        return None if not fetch else []


"""
Agent Memory
============

Shared memory system for agents to share context.

Features:
- Key-value store in Delta table
- TTL-based expiration
- Access tracking
- Agent ownership

Author: AI Ops Team
Version: 1.0.0
"""

import json
from typing import Any, Optional
from datetime import datetime, timedelta
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class AgentMemory:
    """
    Shared memory system for agent context sharing.
    """
    
    def __init__(self):
        """Initialize AgentMemory."""
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load("mas_config.yaml")
        self.table_name = self.config.get("mas", {}).get("shared_memory", {}).get("table_name", "agent_shared_memory")
        self.default_ttl_hours = self.config.get("mas", {}).get("shared_memory", {}).get("ttl_hours", 24)
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.full_table_name = f"{self.catalog}.{self.schema}.{self.table_name}"
    
    def store(self, key: str, value: Any, agent_owner: str, ttl_hours: Optional[int] = None) -> None:
        """
        Store a value in shared memory.
        
        Args:
            key: Memory key
            value: Value to store (will be JSON serialized)
            agent_owner: Agent that owns this memory
            ttl_hours: Time to live in hours (defaults to configured TTL)
        """
        try:
            if ttl_hours is None:
                ttl_hours = self.default_ttl_hours
            
            expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            value_json = json.dumps(value)
            
            query = f"""
            INSERT INTO {self.full_table_name}
            (memory_key, memory_value, agent_owner, created_at, expires_at, access_count, last_accessed_at)
            VALUES
            ('{key}', '{value_json}', '{agent_owner}', CURRENT_TIMESTAMP(), 
             '{expires_at.isoformat()}', 0, CURRENT_TIMESTAMP())
            ON DUPLICATE KEY UPDATE
                memory_value = '{value_json}',
                agent_owner = '{agent_owner}',
                expires_at = '{expires_at.isoformat()}',
                access_count = access_count + 1,
                last_accessed_at = CURRENT_TIMESTAMP()
            """
            
            # For Databricks, use MERGE instead
            query = f"""
            MERGE INTO {self.full_table_name} AS target
            USING (SELECT '{key}' AS memory_key) AS source
            ON target.memory_key = source.memory_key
            WHEN MATCHED THEN
                UPDATE SET
                    memory_value = '{value_json}',
                    agent_owner = '{agent_owner}',
                    expires_at = '{expires_at.isoformat()}',
                    access_count = access_count + 1,
                    last_accessed_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (memory_key, memory_value, agent_owner, created_at, expires_at, access_count, last_accessed_at)
                VALUES ('{key}', '{value_json}', '{agent_owner}', CURRENT_TIMESTAMP(), 
                        '{expires_at.isoformat()}', 0, CURRENT_TIMESTAMP())
            """
            
            self._execute_query(query)
            logger.debug(f"Stored memory key: {key}")
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from shared memory.
        
        Args:
            key: Memory key
        
        Returns:
            Stored value or None if not found/expired
        """
        try:
            query = f"""
            SELECT memory_value, expires_at
            FROM {self.full_table_name}
            WHERE memory_key = '{key}'
              AND expires_at > CURRENT_TIMESTAMP()
            """
            
            results = self._execute_query(query, fetch=True)
            
            if results and len(results) > 0:
                value_json = results[0][0]
                # Update access count
                self._update_access_count(key)
                return json.loads(value_json) if isinstance(value_json, str) else value_json
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {e}")
            return None
    
    def delete(self, key: str) -> None:
        """
        Delete a memory key.
        
        Args:
            key: Memory key to delete
        """
        try:
            query = f"""
            DELETE FROM {self.full_table_name}
            WHERE memory_key = '{key}'
            """
            
            self._execute_query(query)
            logger.debug(f"Deleted memory key: {key}")
            
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            raise
    
    def _update_access_count(self, key: str) -> None:
        """Update access count for a memory key."""
        try:
            query = f"""
            UPDATE {self.full_table_name}
            SET access_count = access_count + 1,
                last_accessed_at = CURRENT_TIMESTAMP()
            WHERE memory_key = '{key}'
            """
            
            self._execute_query(query)
            
        except Exception as e:
            logger.debug(f"Failed to update access count: {e}")
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired memory entries.
        
        Returns:
            Number of entries deleted
        """
        try:
            query = f"""
            DELETE FROM {self.full_table_name}
            WHERE expires_at <= CURRENT_TIMESTAMP()
            """
            
            self._execute_query(query)
            logger.info("Cleaned up expired memory entries")
            return 0  # Delta doesn't return count directly
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired memory: {e}")
            return 0
    
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
        
        logger.warning("No database connection available. Memory operations may fail.")
        return None if not fetch else []


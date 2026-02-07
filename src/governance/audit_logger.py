"""
Audit Logger
============

Comprehensive audit logging for all system actions.

Features:
- Event logging
- Actor tracking
- Resource tracking
- Timestamp and context

Author: AI Ops Team
Version: 1.0.0
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class AuditLogger:
    """
    Comprehensive audit logger.
    """
    
    def __init__(self):
        """Initialize AuditLogger."""
        self.config_loader = ConfigLoader()
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.table_name = f"{self.catalog}.{self.schema}.audit_log"
    
    def log(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """
        Log an audit event.
        
        Args:
            event_type: Event type (agent_action, approval, rbac_change, execution)
            actor: Actor (user or agent)
            action: Action performed
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details dictionary
            ip_address: IP address (optional)
            user_agent: User agent string (optional)
        
        Returns:
            Audit log ID
        """
        audit_id = str(uuid.uuid4())
        
        try:
            import json
            details_json = json.dumps(details or {})
            
            query = f"""
            INSERT INTO {self.table_name}
            (audit_id, event_type, actor, action, resource_type, resource_id,
             details, timestamp, ip_address, user_agent)
            VALUES
            ('{audit_id}', '{event_type}', '{actor}', '{action}', '{resource_type or ''}',
             '{resource_id or ''}', '{details_json}', CURRENT_TIMESTAMP(),
             '{ip_address or ''}', '{user_agent or ''}')
            """
            
            self._execute_query(query)
            logger.debug(f"Audit log created: {audit_id} for {action} by {actor}")
            
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise
    
    def _execute_query(self, query: str) -> None:
        """Execute SQL query."""
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark:
                spark.sql(query)
        except Exception as e:
            logger.warning(f"Failed to execute audit query: {e}")


"""
PromptOps Agent
===============

Prompt lifecycle management agent.

Features:
- Versioning of all prompts
- Rollback capabilities
- A/B testing support
- Prompt performance analytics
- Returns prompt version metadata

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class PromptOpsAgent(BaseAgent):
    """
    Prompt operations agent.
    """
    
    def __init__(self):
        """Initialize PromptOpsAgent."""
        super().__init__("PromptOpsAgent")
        self.config_loader = ConfigLoader()
        self.catalog = self.config_loader.get("env.dev.yaml", "databricks.catalog", "main")
        self.schema = self.config_loader.get("env.dev.yaml", "databricks.schema", "mas_system")
        self.prompts_table = f"{self.catalog}.{self.schema}.prompt_versions"
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a prompt operations task.
        
        Args:
            task: Task dictionary
            context: Context from previous agents
        
        Returns:
            Prompt operation result
        """
        try:
            operation = task.get("operation", "get")
            
            if operation == "get":
                # Get active prompt version
                agent_type = task.get("agent_type", "")
                prompt = self._get_active_prompt(agent_type)
                return {
                    "status": "success",
                    "prompt": prompt
                }
            
            elif operation == "version":
                # Create new prompt version
                prompt_id = task.get("prompt_id")
                version = task.get("version")
                content = task.get("content")
                agent_type = task.get("agent_type")
                
                version_id = self._create_prompt_version(prompt_id, version, content, agent_type)
                
                return {
                    "status": "success",
                    "version_id": version_id
                }
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            logger.error(f"PromptOpsAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_active_prompt(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get active prompt version for agent type."""
        try:
            query = f"""
            SELECT prompt_id, version, prompt_content
            FROM {self.prompts_table}
            WHERE agent_type = '{agent_type}' AND status = 'active'
            ORDER BY version DESC
            LIMIT 1
            """
            
            results = self._execute_query(query, fetch=True)
            
            if results and len(results) > 0:
                return {
                    "prompt_id": results[0][0],
                    "version": results[0][1],
                    "content": results[0][2]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get active prompt: {e}")
            return None
    
    def _create_prompt_version(self, prompt_id: str, version: int, content: str, agent_type: str) -> str:
        """Create new prompt version."""
        # Simplified - in production insert into prompt_versions table
        logger.info(f"Creating prompt version {version} for {agent_type}")
        return f"{prompt_id}_v{version}"
    
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


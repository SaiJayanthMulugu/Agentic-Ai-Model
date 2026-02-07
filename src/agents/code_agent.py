"""
Code Agent
==========

Code generation agent for SQL/PySpark/Python.

Features:
- Generates SQL/PySpark/Python code
- Uses versioned prompts from PromptOpsAgent
- Validates code syntax
- NO EXECUTION - only generation
- Returns code with explanation

Author: AI Ops Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class CodeAgent(BaseAgent):
    """
    Code generation agent.
    """
    
    def __init__(self):
        """Initialize CodeAgent."""
        super().__init__("CodeAgent")
        self.config_loader = ConfigLoader()
    
    def process(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a code generation task.
        
        Args:
            task: Task dictionary
            context: Context from previous agents (e.g., RAG results)
        
        Returns:
            Result dictionary with generated code
        """
        try:
            task_description = task.get("task_description", "")
            user_query = task.get("user_query", task_description)
            
            logger.info(f"CodeAgent generating code for: {user_query[:100]}...")
            
            # Get context from RAG if available
            rag_context = ""
            if context:
                for key, value in context.items():
                    if isinstance(value, dict) and value.get("agent_type") == "RAGAgent":
                        docs = value.get("documents", [])
                        if docs:
                            rag_context = "\n".join([doc.get("content", "") for doc in docs[:3]])
            
            # Generate code (simplified - in production use LLM)
            code = self._generate_code(user_query, rag_context)
            
            # Validate code
            validation_result = self._validate_code(code)
            
            result = {
                "status": "success",
                "code": code,
                "code_type": self._detect_code_type(code),
                "explanation": f"Generated {self._detect_code_type(code)} code based on query and knowledge base context",
                "validation": validation_result,
                "context_used": bool(rag_context)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"CodeAgent failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _generate_code(self, query: str, context: str = "") -> str:
        """
        Generate code based on query and context.
        
        Args:
            query: User query
            context: RAG context
        
        Returns:
            Generated code string
        """
        # Simplified code generation - in production use LLM endpoint
        query_lower = query.lower()
        
        if "sql" in query_lower or "select" in query_lower:
            # Generate SQL
            if "top" in query_lower and "customer" in query_lower:
                return """-- Find top 10 customers by sales
SELECT 
    customer_id,
    customer_name,
    SUM(order_amount) AS total_sales
FROM orders
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC
LIMIT 10;"""
            else:
                return f"-- Generated SQL query\nSELECT * FROM table WHERE condition;"
        
        elif "pyspark" in query_lower or "spark" in query_lower:
            return """# Generated PySpark code
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Query").getOrCreate()
df = spark.sql("SELECT * FROM table")
df.show()"""
        
        else:
            return f"""# Generated Python code
# {query}
def process_data():
    # Implementation here
    pass"""
    
    def _detect_code_type(self, code: str) -> str:
        """
        Detect code type.
        
        Args:
            code: Code string
        
        Returns:
            Code type (sql, pyspark, python)
        """
        code_lower = code.lower()
        if "select" in code_lower or "from" in code_lower or "--" in code_lower:
            return "sql"
        elif "pyspark" in code_lower or "spark" in code_lower:
            return "pyspark"
        else:
            return "python"
    
    def _validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate code syntax.
        
        Args:
            code: Code string
        
        Returns:
            Validation result dictionary
        """
        # Simplified validation - in production use proper parsers
        issues = []
        
        if len(code.strip()) == 0:
            issues.append("Code is empty")
        
        # Basic SQL validation
        if code.strip().startswith("--") or "SELECT" in code.upper():
            if "FROM" not in code.upper():
                issues.append("SQL missing FROM clause")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


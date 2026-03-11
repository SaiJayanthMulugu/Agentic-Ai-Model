# Databricks notebook source
# MAGIC %md
# MAGIC # Chatbot Interface
# MAGIC 
# MAGIC Interactive chatbot UI for the MAS platform.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos")
from src.core.orchestrator import OrchestratorAgent

# COMMAND ----------

# MAGIC %md
# MAGIC ## User Input Widget

# COMMAND ----------

dbutils.widgets.text("user_query", "", "Enter your query:")
dbutils.widgets.text("user_id", "user_001", "User ID:")
dbutils.widgets.dropdown("user_role", "data_analyst", ["admin", "data_engineer", "data_analyst", "viewer"], "User Role:")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Process Request

# COMMAND ----------

# Get inputs
user_query = dbutils.widgets.get("user_query")
user_id = dbutils.widgets.get("user_id")
user_role = dbutils.widgets.get("user_role")

if user_query:
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Process request
    response = orchestrator.process_request(
        user_query=user_query,
        user_id=user_id,
        user_role=user_role
    )
    
    # Display results
    print("=" * 50)
    print("Response:")
    print("=" * 50)
    print(f"Status: {response.get('status')}")
    print(f"Intent: {response.get('intent')}")
    print(f"Duration: {response.get('duration_ms', 0):.2f}ms")
    print("\nExecution Plan:")
    for task in response.get('plan', []):
        print(f"  - {task.get('agent')}: {task.get('description')}")
    print("\nResults:")
    print(response.get('results', {}))
else:
    print("Please enter a query using the widget above.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feedback Collection

# COMMAND ----------

dbutils.widgets.dropdown("feedback", "thumbs_up", ["thumbs_up", "thumbs_down"], "Feedback:")

feedback = dbutils.widgets.get("feedback")
if feedback and user_query:
    # Collect feedback
    from src.agents.feedback_agent import FeedbackAgent
    feedback_agent = FeedbackAgent()
    feedback_result = feedback_agent.process({
        "query_id": response.get("request_id", ""),
        "user_id": user_id,
        "feedback_type": feedback
    })
    print(f"✓ Feedback collected: {feedback_result.get('feedback_id')}")


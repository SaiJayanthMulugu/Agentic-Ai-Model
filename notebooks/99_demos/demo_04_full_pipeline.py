# Databricks notebook source
# MAGIC %md
# MAGIC # Full Pipeline Demo
# MAGIC 
# MAGIC Complete end-to-end demonstration of the MAS platform.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup

# COMMAND ----------

import sys
import os

# Auto-detect repo path from notebook location
try:
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    repo_path = "/".join(notebook_path.split("/")[:4])  # Gets /Workspace/Repos/username/repo-name
    sys.path.append(repo_path)
    print(f"✓ Using repo path: {repo_path}")
except:
    # Fallback: manual path (update if needed)
    sys.path.append("/Workspace/Repos/your-username/aiops-agentic-mas-platform")
    print("⚠ Using fallback path - update if needed")

from src.core.orchestrator import OrchestratorAgent

# COMMAND ----------

# MAGIC %md
# MAGIC ## Demo: Generate SQL Query

# COMMAND ----------

# User query
user_query = "Generate SQL to find top 10 customers by sales"

print("=" * 70)
print("DEMO: Full Pipeline Execution")
print("=" * 70)
print(f"\nUser Query: {user_query}")
print(f"User Role: data_engineer")
print("\n" + "-" * 70)

# COMMAND ----------

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Process request
response = orchestrator.process_request(
    user_query=user_query,
    user_id="demo_user",
    user_role="data_engineer"
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Results

# COMMAND ----------

print("\n" + "=" * 70)
print("EXECUTION RESULTS")
print("=" * 70)

print(f"\nRequest ID: {response.get('request_id')}")
print(f"Status: {response.get('status')}")
print(f"Intent: {response.get('intent')}")
print(f"Duration: {response.get('duration_ms', 0):.2f}ms")

print("\nExecution Plan:")
for i, task in enumerate(response.get('plan', []), 1):
    print(f"  {i}. {task.get('agent')}: {task.get('description')}")

print("\nResults:")
results = response.get('results', {})
print(f"  Tasks Completed: {results.get('tasks_completed', 0)}")
print(f"  Final Answer: {results.get('final_answer', 'N/A')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Complete Trace

# COMMAND ----------

print("\n" + "=" * 70)
print("COMPLETE TRACE")
print("=" * 70)
print("\n1. OrchestratorAgent received request")
print("2. Intent detected: code_generation")
print("3. Execution plan created:")
for task in response.get('plan', []):
    print(f"   - {task.get('agent')}")
print("4. Tasks delegated via message bus")
print("5. Responses aggregated")
print("6. Final response returned")

# COMMAND ----------

print("\n" + "=" * 70)
print("DEMO COMPLETE")
print("=" * 70)


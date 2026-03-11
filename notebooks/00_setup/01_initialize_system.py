# Databricks notebook source
# MAGIC %md
# MAGIC # System Initialization
# MAGIC 
# MAGIC This notebook initializes the MAS platform system.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Execute SQL Schemas

# COMMAND ----------

import os
from pathlib import Path

# Get SQL files directory
# Update this path to match your Databricks Repos path
# Option 1: If using Databricks Repos
sql_dir = Path("/Workspace/Repos") / dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().get() / "aiops-agentic-mas-platform" / "sql"
# Option 2: If uploaded to workspace files, use:
# sql_dir = Path("/Workspace/aiops-agentic-mas-platform/sql")
# Option 3: If you know the exact path:
# sql_dir = Path("/Workspace/Repos/your-username/aiops-agentic-mas-platform/sql")

# SQL files in order
sql_files = [
    "00_create_schema.sql",
    "01_create_core_tables.sql",
    "02_create_governance_tables.sql",
    "03_rbac_grants.sql",
    "04_prompt_versioning_tables.sql",
    "05_memory_tables.sql",
    "06_tool_learning_tables.sql",
    "07_planning_tables.sql",
    "08_rag_knowledge_base.sql",
    "09_rag_query_logs.sql",
    "10_rag_feedback_system.sql",
    "11_rag_learning_pipeline.sql",
    "12_agent_communication.sql",
    "13_agent_metrics.sql"
]

# COMMAND ----------

# Execute each SQL file
for sql_file in sql_files:
    sql_path = sql_dir / sql_file
    if sql_path.exists():
        print(f"Executing {sql_file}...")
        with open(sql_path, "r") as f:
            sql_content = f.read()
            try:
                spark.sql(sql_content)
                print(f"✓ {sql_file} executed successfully")
            except Exception as e:
                print(f"✗ {sql_file} failed: {e}")
    else:
        print(f"⚠ {sql_file} not found")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Initial Knowledge Base

# COMMAND ----------

# Load sample documents
sample_docs = [
    {
        "doc_id": "doc_001",
        "title": "SQL Best Practices",
        "content": "When writing SQL queries, always use parameterized queries to prevent SQL injection. Use indexes for frequently queried columns.",
        "category": "best_practices",
        "quality_score": 0.9,
        "sensitivity_level": "public"
    },
    {
        "doc_id": "doc_002",
        "title": "PySpark Performance Tips",
        "content": "For better PySpark performance, use broadcast joins for small tables, cache frequently used DataFrames, and avoid unnecessary shuffles.",
        "category": "best_practices",
        "quality_score": 0.85,
        "sensitivity_level": "public"
    }
]

# COMMAND ----------

# Insert sample documents
for doc in sample_docs:
    spark.sql(f"""
    INSERT INTO main.mas_system.knowledge_base
    (doc_id, content, title, category, quality_score, usage_count, status, sensitivity_level, created_at)
    VALUES
    ('{doc['doc_id']}', '{doc['content']}', '{doc['title']}', '{doc['category']}',
     {doc['quality_score']}, 0, 'active', '{doc['sensitivity_level']}', CURRENT_TIMESTAMP())
    """)

print(f"✓ Loaded {len(sample_docs)} initial documents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Health Check

# COMMAND ----------

# Check table counts
tables = [
    "agent_registry",
    "knowledge_base",
    "agent_messages",
    "agent_shared_memory"
]

for table in tables:
    try:
        count = spark.sql(f"SELECT COUNT(*) FROM main.mas_system.{table}").collect()[0][0]
        print(f"✓ {table}: {count} records")
    except Exception as e:
        print(f"✗ {table}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Initialization Complete

# COMMAND ----------

print("=" * 50)
print("System Initialization Complete")
print("=" * 50)
print("All tables created and initialized.")
print("Proceed to agent setup.")


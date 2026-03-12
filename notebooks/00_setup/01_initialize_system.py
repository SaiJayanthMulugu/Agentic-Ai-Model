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

# SQL directory: try multiple methods (edit MANUAL_SQL_DIR if needed)
MANUAL_SQL_DIR = "/Workspace/Repos/saijayanthmulugu@gmail.com/Agentic-Ai-Model/sql"

candidates = [
    Path(MANUAL_SQL_DIR),
    (Path.cwd() / "sql").resolve(),           # cwd = repo root (Databricks Repos default)
    (Path.cwd() / ".." / "sql").resolve(),    # cwd = notebooks/00_setup
]
sql_dir = None
for c in candidates:
    if c and c.exists():
        sql_dir = c
        break
if sql_dir is None:
    try:
        notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
        parts = [p for p in notebook_path.rstrip("/").split("/") if p]
        if "Repos" in parts:
            idx = parts.index("Repos")
            repo_root = "/" + "/".join(parts[: idx + 3])
            sql_dir = Path(repo_root) / "sql"
    except Exception:
        sql_dir = Path(MANUAL_SQL_DIR)

print(f"SQL directory: {sql_dir}")
print(f"Exists: {sql_dir.exists()}")
print(f"Current working dir: {Path.cwd()}")

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

def split_sql_statements(sql_content):
    """Split SQL into individual statements. Spark.sql() accepts only one statement at a time."""
    statements = []
    for stmt in sql_content.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        # Skip comment-only blocks
        if all(line.strip().startswith('--') or not line.strip() for line in stmt.split('\n')):
            continue
        statements.append(stmt)
    return statements

# COMMAND ----------

# Execute each SQL file - run statements one at a time (Spark doesn't support multi-statement)
for sql_file in sql_files:
    sql_path = sql_dir / sql_file
    if sql_path.exists():
        print(f"[EXECUTING] {sql_file}...")
        with open(sql_path, "r") as f:
            sql_content = f.read()
        statements = split_sql_statements(sql_content)
        failed = False
        for i, stmt in enumerate(statements):
            try:
                spark.sql(stmt)
            except Exception as e:
                print(f"[ERROR] {sql_file} failed (statement {i+1}): {e}")
                failed = True
                break
        if not failed:
            print(f"[OK] {sql_file} executed successfully ({len(statements)} statements)")
    else:
        print(f"[NOT FOUND] {sql_file}")

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
    },
    {
        "doc_id": "doc_003",
        "title": "Python Unit Testing with Pytest",
        "content": "Use pytest for comprehensive testing. Write focused tests that cover edge cases and error conditions. Use fixtures for setup and teardown. Aim for at least 80% code coverage.",
        "category": "best_practices",
        "quality_score": 0.88,
        "sensitivity_level": "public"
    },
    {
        "doc_id": "doc_004",
        "title": "Azure Security Guidelines",
        "content": "Always use managed identities instead of service principals. Enable Azure RBAC for fine-grained access control. Use Azure Key Vault for secret management. Enable audit logging on all resources.",
        "category": "security",
        "quality_score": 0.92,
        "sensitivity_level": "internal"
    },
    {
        "doc_id": "doc_005",
        "title": "Databricks Cluster Performance Tuning",
        "content": "Configure auto-termination to reduce costs. Use instance pools for faster startup. Enable Photon for improved query performance. Monitor cluster metrics and adjust worker count based on workload.",
        "category": "best_practices",
        "quality_score": 0.87,
        "sensitivity_level": "public"
    },
    {
        "doc_id": "doc_006",
        "title": "API Design Standards",
        "content": "Use RESTful principles for API design. Return meaningful HTTP status codes. Include comprehensive error messages. Version your APIs. Document all endpoints with examples and expected payloads.",
        "category": "best_practices",
        "quality_score": 0.86,
        "sensitivity_level": "internal"
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
        print(f"[OK] {table}: {count} records")
    except Exception as e:
        err_msg = str(e).split("\n")[0] if "\n" in str(e) else str(e)
        if "TABLE_OR_VIEW_NOT_FOUND" in str(e) or "cannot be found" in str(e):
            print(f"[NOT FOUND] {table}: Table does not exist. Run 12_agent_communication.sql to create it.")
        else:
            print(f"[ERROR] {table}: {err_msg[:120]}...")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Initialization Complete

# COMMAND ----------

print("=" * 50)
print("System Initialization Complete")
print("=" * 50)
print("All tables created and initialized.")
print("Proceed to agent setup.")


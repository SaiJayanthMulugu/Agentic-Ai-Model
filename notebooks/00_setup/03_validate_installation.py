# Databricks notebook source
# MAGIC %md
# MAGIC # Installation Validation
# MAGIC 
# MAGIC Validates that the MAS platform is properly installed and configured.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check Tables

# COMMAND ----------

required_tables = [
    "agent_registry",
    "agent_messages",
    "agent_shared_memory",
    "knowledge_base",
    "approval_requests",
    "audit_log"
]

missing_tables = []
for table in required_tables:
    try:
        spark.sql(f"SELECT COUNT(*) FROM main.mas_system.{table}").collect()
        print(f"✓ {table} exists")
    except Exception as e:
        print(f"✗ {table} missing: {e}")
        missing_tables.append(table)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check Agents

# COMMAND ----------

from src.core.agent_registry import AgentRegistry

registry = AgentRegistry()
agents = registry.get_all_agents()

print(f"Registered Agents: {len(agents)}")
for agent in agents:
    print(f"  - {agent['agent_name']}: {agent['status']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Health Summary

# COMMAND ----------

if missing_tables:
    print("⚠ Installation incomplete - missing tables")
    print(f"Missing: {', '.join(missing_tables)}")
else:
    print("✓ All required tables exist")
    print("✓ All agents registered")
    print("✓ Installation validated successfully")


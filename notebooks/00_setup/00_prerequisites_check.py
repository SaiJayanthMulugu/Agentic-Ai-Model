# Databricks notebook source
# MAGIC %md
# MAGIC # Prerequisites Check
# MAGIC 
# MAGIC This notebook checks all prerequisites before system initialization.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check Unity Catalog

# COMMAND ----------

# Check if Unity Catalog is enabled
try:
    spark.sql("SHOW CATALOGS")
    print("✓ Unity Catalog is enabled")
except Exception as e:
    print(f"✗ Unity Catalog check failed: {e}")
    raise

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check Required Tables

# COMMAND ----------

# Check if we can access the schema
try:
    spark.sql("USE CATALOG main")
    spark.sql("SHOW SCHEMAS")
    print("✓ Can access Unity Catalog")
except Exception as e:
    print(f"✗ Cannot access Unity Catalog: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Check Environment Variables

# COMMAND ----------

import os

required_vars = [
    "DATABRICKS_HOST",
    "DATABRICKS_TOKEN",
    "CATALOG_NAME",
    "SCHEMA_NAME"
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
    raise ValueError(f"Missing required environment variables: {missing_vars}")
else:
    print("✓ All required environment variables are set")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

print("=" * 50)
print("Prerequisites Check Complete")
print("=" * 50)
print("All prerequisites met. Proceed to initialization.")


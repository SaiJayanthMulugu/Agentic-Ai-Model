# Databricks Setup Checklist

Use this checklist to ensure proper deployment.

## Pre-Deployment

- [ ] Databricks workspace access confirmed
- [ ] Unity Catalog enabled in workspace
- [ ] Personal Access Token created (for CLI/API access)
- [ ] Cluster created or existing cluster identified
- [ ] Vector Search enabled (for RAG functionality)

## Deployment Steps

### 1. Repository Setup
- [ ] Repository uploaded to Databricks Repos
- [ ] Repository path noted: `/Workspace/Repos/username/repo-name`
- [ ] All files uploaded successfully

### 2. Dependencies
- [ ] Requirements.txt reviewed
- [ ] Dependencies installed on cluster
- [ ] No installation errors

### 3. Configuration
- [ ] Environment variables set
- [ ] Databricks secrets configured (if using)
- [ ] Catalog name confirmed: `main` (or custom)
- [ ] Schema name confirmed: `mas_system`

### 4. Database Setup
- [ ] Unity Catalog catalog exists
- [ ] Schema `mas_system` created
- [ ] SQL files path updated in initialization notebook
- [ ] All 14 SQL schema files executed successfully
- [ ] Tables verified in Catalog Explorer

### 5. Agent Setup
- [ ] Python path updated in setup notebook
- [ ] All 11 agents imported successfully
- [ ] Agents registered in `agent_registry` table
- [ ] Agent status verified

### 6. Vector Search (for RAG)
- [ ] Vector Search endpoint created
- [ ] Vector index created
- [ ] Embedding model endpoint configured
- [ ] LLM endpoint configured

### 7. Testing
- [ ] Prerequisites check notebook passes
- [ ] System initialization completes
- [ ] Agent setup completes
- [ ] Demo notebook runs successfully
- [ ] Chatbot interface works

### 8. Jobs & Scheduling
- [ ] Job definitions imported
- [ ] Jobs scheduled correctly
- [ ] Job permissions set

## Post-Deployment

- [ ] Knowledge base populated with initial documents
- [ ] RBAC roles assigned to users
- [ ] Monitoring dashboards set up
- [ ] Team trained on usage
- [ ] Documentation shared

## Verification Commands

Run these in a Databricks notebook to verify:

```python
# Check tables
spark.sql("SHOW TABLES IN main.mas_system").show()

# Check agents
spark.sql("SELECT * FROM main.mas_system.agent_registry").show()

# Check configuration
from src.utils.config_loader import ConfigLoader
loader = ConfigLoader()
config = loader.load("mas_config.yaml")
print(config)
```

## Troubleshooting

If any step fails:
1. Check error messages in notebook output
2. Verify paths are correct
3. Check Unity Catalog permissions
4. Review logs in cluster driver logs
5. Refer to `docs/troubleshooting.md`

## Support Resources

- [Quick Start Guide](QUICK_START_DATABRICKS.md)
- [Full Deployment Guide](DEPLOYMENT_TO_DATABRICKS.md)
- [Troubleshooting](docs/troubleshooting.md)
- [User Guide](docs/user_guide.md)


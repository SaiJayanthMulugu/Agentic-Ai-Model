# Deploying MAS Platform to Databricks Workspace

## Method 1: Using Databricks Repos (Recommended)

### Step 1: Connect Repository to Databricks

1. **Open Databricks Workspace**
   - Navigate to your Databricks workspace
   - Go to **Repos** in the left sidebar

2. **Add Repository**
   - Click **Add Repo** button
   - Choose one of these options:
     - **GitHub**: If your code is in a GitHub repository
     - **GitLab**: If your code is in a GitLab repository
     - **Bitbucket**: If your code is in a Bitbucket repository
     - **Azure DevOps**: If your code is in Azure DevOps
     - **Workspace Files**: Upload directly from your local machine

3. **If Using Git Repository**
   - Provide repository URL
   - Select branch (usually `main` or `master`)
   - Choose a folder name (e.g., `aiops-agentic-mas-platform`)
   - Click **Create Repo**

4. **If Uploading from Local Machine**
   - Click **Upload** in Repos
   - Select your local `MAS MODEL` folder
   - The repository will be uploaded to `/Workspace/Repos/your-username/aiops-agentic-mas-platform`

### Step 2: Install Dependencies

1. **Create a Cluster or Use Existing**
   - Go to **Compute** → **Clusters**
   - Create a new cluster or use existing one
   - Recommended: **Databricks Runtime 13.3 LTS** or higher
   - Enable **Unity Catalog**

2. **Install Python Packages**
   - Attach the cluster to a notebook
   - Run this in a notebook cell:
   ```python
   %pip install -r /Workspace/Repos/your-username/aiops-agentic-mas-platform/requirements.txt
   ```
   - Or create an **init script** to install packages automatically

### Step 3: Configure Environment Variables

1. **Create a Secret Scope** (Recommended)
   - Go to **Settings** → **User Settings** → **Access Tokens**
   - Or use **Workspace Secrets** (Admin only)

2. **Set Environment Variables**
   - Create a notebook: `config/setup_env.py`
   ```python
   import os
   
   # Set environment variables
   os.environ['DATABRICKS_HOST'] = 'https://your-workspace.cloud.databricks.com'
   os.environ['DATABRICKS_TOKEN'] = dbutils.secrets.get(scope="mas-platform", key="databricks-token")
   os.environ['CATALOG_NAME'] = 'main'
   os.environ['SCHEMA_NAME'] = 'mas_system'
   os.environ['VECTOR_ENDPOINT'] = 'rag-vector-endpoint'
   os.environ['LLM_ENDPOINT'] = 'databricks-meta-llama-3-1-70b-instruct'
   os.environ['EMBEDDING_ENDPOINT'] = 'databricks-gte-large-en'
   ```

3. **Or Use Databricks Widgets** (for testing)
   - In notebooks, use widgets to set variables:
   ```python
   dbutils.widgets.text("DATABRICKS_HOST", "https://your-workspace.cloud.databricks.com")
   dbutils.widgets.text("CATALOG_NAME", "main")
   ```

### Step 4: Initialize System

1. **Run Prerequisites Check**
   - Open: `notebooks/00_setup/00_prerequisites_check.py`
   - Run all cells
   - Verify Unity Catalog is enabled

2. **Initialize Database Schema**
   - Open: `notebooks/00_setup/01_initialize_system.py`
   - **Update the SQL directory path** in the notebook:
   ```python
   # Update this line to match your repo path
   sql_dir = Path("/Workspace/Repos/your-username/aiops-agentic-mas-platform/sql")
   ```
   - Run all cells
   - Verify all tables are created

3. **Setup Agents**
   - Open: `notebooks/00_setup/02_setup_agents.py`
   - **Update the import path** if needed:
   ```python
   sys.path.append("/Workspace/Repos/your-username/aiops-agentic-mas-platform")
   ```
   - Run all cells
   - Verify all agents are registered

### Step 5: Test the System

1. **Run Demo**
   - Open: `notebooks/99_demos/demo_04_full_pipeline.py`
   - Run all cells
   - Verify end-to-end execution works

2. **Test Chatbot Interface**
   - Open: `notebooks/01_chatbot/01_chatbot_interface.py`
   - Enter a test query
   - Verify response

## Method 2: Using Databricks CLI

### Step 1: Install Databricks CLI

```bash
pip install databricks-cli
```

### Step 2: Configure CLI

```bash
databricks configure --token
# Enter your workspace URL and personal access token
```

### Step 3: Upload Files

```bash
# Upload entire repository
databricks workspace import-dir . /Workspace/Repos/aiops-agentic-mas-platform --overwrite

# Or upload specific directories
databricks workspace import-dir notebooks /Workspace/Repos/aiops-agentic-mas-platform/notebooks
databricks workspace import-dir src /Workspace/Repos/aiops-agentic-mas-platform/src
databricks workspace import-dir sql /Workspace/Repos/aiops-agentic-mas-platform/sql
```

### Step 4: Run Setup Notebooks

```bash
# Run initialization notebook
databricks runs submit --json-file jobs/initialize.json
```

## Method 3: Using Databricks Asset Bundles (DABs)

### Step 1: Create databricks.yml

```yaml
# databricks.yml
bundle:
  name: mas-platform

resources:
  jobs:
    initialize:
      name: Initialize MAS Platform
      tasks:
        - task_key: setup
          notebook_task:
            notebook_path: notebooks/00_setup/01_initialize_system
```

### Step 2: Deploy

```bash
databricks bundle deploy
databricks bundle run initialize
```

## Important Configuration Updates

### Update Notebook Paths

After uploading, update these paths in notebooks:

1. **In `notebooks/00_setup/01_initialize_system.py`**:
   ```python
   sql_dir = Path("/Workspace/Repos/your-username/aiops-agentic-mas-platform/sql")
   ```

2. **In `notebooks/00_setup/02_setup_agents.py`**:
   ```python
   sys.path.append("/Workspace/Repos/your-username/aiops-agentic-mas-platform")
   ```

3. **In all other notebooks**:
   ```python
   sys.path.append("/Workspace/Repos/your-username/aiops-agentic-mas-platform")
   ```

### Set Up Unity Catalog

1. **Enable Unity Catalog** (if not already enabled)
   - Go to **Catalog** in left sidebar
   - Create catalog: `main` (or use existing)
   - Create schema: `mas_system`

2. **Grant Permissions**
   - Grant appropriate permissions to users/roles
   - See `sql/03_rbac_grants.sql` for examples

### Set Up Vector Search

1. **Create Vector Search Endpoint**
   ```python
   from databricks.vector_search.client import VectorSearchClient
   
   client = VectorSearchClient()
   endpoint = client.create_endpoint(
       name="rag-vector-endpoint",
       endpoint_type="STANDARD"
   )
   ```

2. **Create Vector Index**
   - Use the RAG initialization notebook: `notebooks/09_rag_system/01_initialize_rag.py`

## Quick Start Checklist

- [ ] Repository uploaded to Databricks
- [ ] Dependencies installed on cluster
- [ ] Environment variables configured
- [ ] Unity Catalog enabled and schema created
- [ ] SQL schemas executed successfully
- [ ] Agents registered
- [ ] Demo notebook runs successfully
- [ ] Vector search endpoint created (for RAG)
- [ ] LLM endpoints configured

## Troubleshooting

### Issue: Module not found
**Solution**: Ensure `sys.path.append()` includes the repo path in all notebooks

### Issue: Tables not found
**Solution**: Run `notebooks/00_setup/01_initialize_system.py` to create all tables

### Issue: Agents not registered
**Solution**: Run `notebooks/00_setup/02_setup_agents.py` to register all agents

### Issue: Vector search not working
**Solution**: Ensure vector search endpoint is created and index is set up

## Next Steps

After successful deployment:

1. **Schedule Jobs**: Import job definitions from `jobs/` directory
2. **Configure Monitoring**: Set up dashboards using `notebooks/08_llmops_monitoring/`
3. **Load Knowledge Base**: Add documents to knowledge base
4. **Train Team**: Share user guide with team members

## Support

For issues, refer to:
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Deployment Guide](docs/deployment_guide.md)
- [User Guide](docs/user_guide.md)


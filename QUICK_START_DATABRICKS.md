# Quick Start: Deploy to Databricks (5 Minutes)

## Step-by-Step Guide

### 1. Upload Repository (2 minutes)

**Option A: Upload from Local Machine (No Git Required)**
1. Go to **Repos** in Databricks workspace
2. Click **Add Repo** button
3. **Uncheck** "Create repo by cloning a Git repository" checkbox
4. Look for **Upload** or **Create Folder** option
5. Or go to your **Home folder** and create a **Git folder** there
6. Upload your local `MAS MODEL` folder contents
7. Repository will be at: `/Workspace/Repos/your-username/aiops-agentic-mas-platform`

**Option B: Using Git Repository (If code is in Git)**
1. In the "Add Repo" dialog:
   - **Git repository URL**: Enter your repo URL (e.g., `https://github.com/username/repo.git`)
   - **Git provider**: Select from dropdown (GitHub, GitLab, Bitbucket, Azure DevOps, etc.)
   - **Repository name**: `aiops-agentic-mas-platform` (or your preferred name)
   - **Sparse checkout mode**: Leave unchecked
2. Click **Create Repo**
3. Databricks will clone your repository

**Option C: Create Git Folder in Home (New Feature)**
1. Go to your **Home folder** in Databricks
2. Click **Create** → **Git folder**
3. Upload your local files or connect to Git repository

### 2. Install Dependencies (1 minute)

Create a new notebook and run:
```python
%pip install -r /Workspace/Repos/your-username/aiops-agentic-mas-platform/requirements.txt
```

Or install on cluster:
- Go to **Compute** → Your Cluster → **Libraries** → **Install New**
- Upload `requirements.txt` or paste package names

### 3. Set Environment Variables (1 minute)

Create a notebook `config/setup_env.py`:
```python
import os

# Get from Databricks secrets or set directly
os.environ['DATABRICKS_HOST'] = 'https://your-workspace.cloud.databricks.com'
os.environ['CATALOG_NAME'] = 'main'
os.environ['SCHEMA_NAME'] = 'mas_system'
os.environ['VECTOR_ENDPOINT'] = 'rag-vector-endpoint'
os.environ['LLM_ENDPOINT'] = 'databricks-meta-llama-3-1-70b-instruct'
os.environ['EMBEDDING_ENDPOINT'] = 'databricks-gte-large-en'
```

### 4. Initialize System (1 minute)

1. Open `notebooks/00_setup/01_initialize_system.py`
2. **Update the SQL path** (line ~15):
   ```python
   sql_dir = Path("/Workspace/Repos/your-username/aiops-agentic-mas-platform/sql")
   ```
3. Run all cells
4. Verify: "✓ All tables created"

### 5. Setup Agents (30 seconds)

1. Open `notebooks/00_setup/02_setup_agents.py`
2. Run all cells
3. Verify: "✓ All agents registered"

### 6. Test (30 seconds)

1. Open `notebooks/99_demos/demo_04_full_pipeline.py`
2. Run all cells
3. Verify: "DEMO COMPLETE"

## ✅ Done!

Your MAS platform is now running in Databricks!

## Common Issues

**"Module not found"**
- Update `sys.path.append()` in notebooks to include your repo path

**"Table not found"**
- Run initialization notebook again

**"Agent not registered"**
- Run setup agents notebook again

## Next Steps

- Configure Vector Search endpoint
- Load knowledge base documents
- Set up scheduled jobs
- Customize for your use case


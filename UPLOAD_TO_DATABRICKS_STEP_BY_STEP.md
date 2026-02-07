# Step-by-Step: Upload to Databricks

## Method 1: Upload Local Files (No Git Required)

### Step 1: Navigate to Repos
1. In Databricks workspace, click **Repos** in the left sidebar
2. Click **Add Repo** button

### Step 2: Choose Upload Option
You have two ways to upload:

**Option A: Direct Upload (if available)**
- In the "Add Repo" dialog, **uncheck** "Create repo by cloning a Git repository"
- Look for an **Upload** button or option
- Select your local `MAS MODEL` folder
- Click **Create** or **Upload**

**Option B: Create Git Folder in Home (Recommended)**
1. **Close** the "Add Repo" dialog
2. Go to your **Home folder** (click your username in top right → Home)
3. Click **Create** button
4. Select **Git folder** (or **Folder** if Git folder not available)
5. Name it: `aiops-agentic-mas-platform`
6. Click **Create**
7. **Upload files** to this folder:
   - Click **Upload** button in the folder
   - Select all files from your local `MAS MODEL` folder
   - Or drag and drop files

### Step 3: Verify Upload
- Check that all folders are present:
  - `src/`
  - `notebooks/`
  - `sql/`
  - `config/`
  - `requirements.txt`
  - `README.md`

## Method 2: Use Git Repository

### Step 1: Push to Git (if not already done)
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/aiops-agentic-mas-platform.git
git push -u origin main
```

### Step 2: Connect in Databricks
1. In "Add Repo" dialog:
   - **Keep checked**: "Create repo by cloning a Git repository"
   - **Git repository URL**: `https://github.com/your-username/aiops-agentic-mas-platform.git`
   - **Git provider**: Select **GitHub** (or your provider)
   - **Repository name**: `aiops-agentic-mas-platform`
   - **Sparse checkout mode**: Leave **unchecked**
2. Click **Create Repo**

### Step 3: Authenticate
- If prompted, authenticate with your Git provider
- Grant Databricks access to your repository

## Method 3: Using Databricks CLI

If you prefer command line:

```bash
# Install Databricks CLI
pip install databricks-cli

# Configure
databricks configure --token
# Enter workspace URL and token

# Upload files
databricks workspace import-dir . /Workspace/Repos/aiops-agentic-mas-platform --overwrite
```

## After Upload

Once your files are in Databricks:

1. **Note the path**: `/Workspace/Repos/your-username/aiops-agentic-mas-platform`
   - Or if in Home: `/Users/your-email@domain.com/aiops-agentic-mas-platform`

2. **Update notebook paths** (if needed):
   - The notebooks now auto-detect paths, but verify they work

3. **Continue with Step 2** in `QUICK_START_DATABRICKS.md`

## Troubleshooting

**Can't find Upload option?**
- Use the Home folder method (Method 1, Option B)
- Or use Databricks CLI

**Git authentication fails?**
- Check your Git provider access token
- Ensure token has repository read permissions

**Files not showing?**
- Refresh the page
- Check folder permissions
- Verify files were uploaded completely


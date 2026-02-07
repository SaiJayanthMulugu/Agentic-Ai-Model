# Git Setup and Push Guide

## Step 1: Configure Git (Already Done ✅)

```bash
git config --global user.email "msaijayanth2@gmail.com"
git config --global user.name "SaiJayanthMulugu"
```

## Step 2: Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit: AIOps Agentic MAS Platform"
```

## Step 3: Create GitHub Repository

### Option A: Using GitHub Website
1. Go to https://github.com
2. Sign in with your account
3. Click **New repository** (or the **+** icon → **New repository**)
4. Repository name: `aiops-agentic-mas-platform`
5. Description: "Enterprise-grade Multi-Agent System with RAG capabilities on Databricks"
6. Choose **Public** or **Private**
7. **DO NOT** initialize with README, .gitignore, or license (we already have these)
8. Click **Create repository**

### Option B: Using GitHub CLI (if installed)
```bash
gh repo create aiops-agentic-mas-platform --public --description "Enterprise-grade Multi-Agent System with RAG capabilities on Databricks"
```

## Step 4: Connect and Push to GitHub

After creating the repository on GitHub, you'll get a URL like:
`https://github.com/SaiJayanthMulugu/aiops-agentic-mas-platform.git`

Then run:

```bash
# Add remote repository
git remote add origin https://github.com/SaiJayanthMulugu/aiops-agentic-mas-platform.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 5: Authenticate with GitHub

When you push, GitHub will ask for authentication:

**Option A: Personal Access Token (Recommended)**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token
5. When prompted for password, paste the token instead

**Option B: GitHub CLI**
```bash
gh auth login
```

## Complete Command Sequence

```bash
# 1. Configure Git (if not done)
git config --global user.email "msaijayanth2@gmail.com"
git config --global user.name "SaiJayanthMulugu"

# 2. Initialize and commit
git init
git add .
git commit -m "Initial commit: AIOps Agentic MAS Platform"

# 3. Create repository on GitHub (via website), then:
git remote add origin https://github.com/SaiJayanthMulugu/aiops-agentic-mas-platform.git
git branch -M main
git push -u origin main
```

## Troubleshooting

**"Repository not found"**
- Check repository name matches exactly
- Verify you have access to the repository

**"Authentication failed"**
- Use Personal Access Token instead of password
- Ensure token has `repo` scope

**"Large files"**
- If files are too large, GitHub may reject them
- Check `.gitignore` is working correctly
- Consider using Git LFS for large files

## After Pushing to GitHub

Once your code is on GitHub:

1. **In Databricks "Add Repo" dialog:**
   - Git repository URL: `https://github.com/SaiJayanthMulugu/aiops-agentic-mas-platform.git`
   - Git provider: **GitHub**
   - Repository name: `aiops-agentic-mas-platform`
   - Click **Create Repo**

2. Databricks will clone your repository automatically!


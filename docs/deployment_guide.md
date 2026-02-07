# Deployment Guide

## Prerequisites

- Databricks workspace with Unity Catalog
- Azure subscription
- Python 3.10+
- Databricks CLI

## Step 1: Infrastructure Deployment

```bash
cd infra
./deploy.sh
```

## Step 2: Environment Configuration

1. Copy `.env.example` to `.env`
2. Fill in Databricks credentials
3. Configure Unity Catalog settings

## Step 3: System Initialization

1. Run `notebooks/00_setup/00_prerequisites_check.py`
2. Run `notebooks/00_setup/01_initialize_system.py`
3. Run `notebooks/00_setup/02_setup_agents.py`

## Step 4: Verify Installation

Run `notebooks/99_demos/demo_04_full_pipeline.py` to verify end-to-end functionality.

## Step 5: Schedule Jobs

Import job definitions from `jobs/` directory into Databricks.

## Troubleshooting

See `docs/troubleshooting.md` for common issues.


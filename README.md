# AIOps Agentic MAS Platform

Enterprise-grade Multi-Agent System (MAS) with RAG capabilities built on Databricks.

## 🏗️ Architecture Overview

```
                ┌─────────────────┐
                │  User Request   │
                └────────┬────────┘
                         │
                ┌────────▼────────┐
                │  Orchestrator   │◄─── ReAct/ToT Planning
                │     Agent       │
                └────────┬────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     ┌────▼───┐    ┌────▼───┐    ┌────▼───┐
     │  RAG   │    │  Code  │    │ Test   │
     │ Agent  │    │ Agent  │    │ Agent  │
     └────┬───┘    └────┬───┘    └────┬───┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                ┌────────▼────────┐
                │  Message Bus    │
                │  (Delta Table)  │
                └─────────────────┘
```

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- Python 3.10+
- Databricks CLI configured
- Azure subscription (for infrastructure deployment)

### Step 1: Clone and Setup

```bash
git clone <repository-url>
cd aiops-agentic-mas-platform
pip install -r requirements.txt
pip install -e .
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your Databricks credentials
```

### Step 3: Initialize System

1. Open Databricks workspace
2. Navigate to `notebooks/00_setup/01_initialize_system.py`
3. Run all cells
4. Verify health report

### Step 4: Setup Agents

1. Run `notebooks/00_setup/02_setup_agents.py`
2. Verify all agents are registered

### Step 5: Test the System

1. Run `notebooks/99_demos/demo_04_full_pipeline.py`
2. Verify end-to-end execution

## 🤖 Agent Architecture

### 0. OrchestratorAgent (Master Controller)
- Receives user requests
- Intent detection using LLM
- Creates execution plans (ReAct/ToT)
- Delegates tasks via message bus
- Enforces RBAC
- Aggregates responses

### 1. RAGAgent (Knowledge Retrieval)
- Vector search in knowledge base
- Semantic similarity matching
- Context retrieval with RBAC filtering
- Explainability for retrieved context
- Returns structured context (NO execution)

### 2. CodeAgent (Code Generation)
- Generates SQL/PySpark/Python code
- Uses versioned prompts
- Validates code syntax
- Returns code with explanation (NO execution)

### 3. TestCaseAgent (QA Intelligence)
- Generates unit/integration tests
- Creates validation rules
- Persists test cases to Delta tables

### 4. PowerBIAgent (BI Validation)
- SQL reconciliation
- DAX formula validation
- Semantic model checks
- Data lineage verification

### 5. ExecutionAgent (Controlled Executor)
- **DANGEROUS AGENT** - requires approval
- Executes SQL/PySpark/Python code
- RBAC-restricted execution
- Fully audited actions
- Dry-run first, then execute

### 6. FeedbackAgent (Learning Collector)
- Captures user ratings
- Tracks failures and corrections
- Stores feedback in Delta tables
- Triggers learning signals

### 7. OptimizerAgent (Self-Healing)
- Detects knowledge gaps
- Analyzes performance degradation
- Creates retraining requests
- Sends to GovernanceAgent for approval

### 8. GovernanceAgent (Approval Authority)
- Enforces approval workflows
- Controls model promotion
- Manages RBAC policies
- Auto-approve based on confidence

### 9. PromptOpsAgent (Prompt Lifecycle)
- Versioning of all prompts
- Rollback capabilities
- A/B testing support
- Performance analytics

### 10. LLMOpsAgent (Observability)
- Latency monitoring per agent
- Token usage tracking
- Failure trend analysis
- Cost per request calculation
- Alert generation

## 📡 Communication Patterns

All agents communicate via **Message Bus** (Delta table: `agent_messages`):

```python
{
    "message_id": "uuid",
    "from_agent": "RAGAgent",
    "to_agent": "CodeAgent",
    "message_type": "request|response|event",
    "content": {...},
    "timestamp": "ISO8601",
    "correlation_id": "uuid",
    "priority": 1-10
}
```

**Shared Memory**: Delta table `agent_shared_memory` for context sharing (TTL: 24 hours)

**Event System**: Delta table `agent_events` for event-driven communication

## ⚙️ Configuration

### Environment Variables

See `.env.example` for required variables:

- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Personal access token
- `CATALOG_NAME`: Unity Catalog catalog name
- `SCHEMA_NAME`: Schema name for MAS system
- `VECTOR_ENDPOINT`: Vector search endpoint name
- `LLM_ENDPOINT`: LLM endpoint name

### Configuration Files

- `config/env.dev.yaml`: Development environment
- `config/env.prod.yaml`: Production environment
- `config/agents.yaml`: Agent configurations
- `config/mas_config.yaml`: MAS system config
- `config/rbac_roles.yaml`: RBAC definitions
- `config/rag.dev.yaml`: RAG system config

## 📊 Planning Strategies

### ReAct (Reasoning + Acting)
- Thought: Analyze what user wants
- Action: Choose agent
- Observation: Review agent output
- Repeat until goal achieved (max 10 iterations)

### Tree of Thoughts (ToT)
- Generate multiple thought branches
- Evaluate each branch
- Select best path
- Backtrack if needed

### Goal-Driven Execution Plans
Pre-defined workflows for common tasks (see `config/mas_config.yaml`)

## 🔍 RAG System

### Self-Learning Capabilities
- Automatic query logging
- Feedback collection
- Knowledge gap detection
- Auto-generate document candidates
- Human-in-the-loop approval
- Retraining triggers:
  - 10+ approved new documents
  - 20+ high-quality feedback items
  - Weekly scheduled retraining

### Vector Search
- Embedding model: `databricks-gte-large-en`
- LLM: `databricks-meta-llama-3-1-70b-instruct`
- Databricks Vector Search integration

## 🔐 Governance & RBAC

### Roles

- **admin**: All permissions
- **data_engineer**: Read knowledge, generate code, execute SQL (no delete/promote)
- **data_analyst**: Read knowledge, query RAG (no execute/code gen)
- **knowledge_curator**: Approve docs, manage knowledge

### Approval Workflows

- ExecutionAgent requests → GovernanceAgent approval → Execution
- OptimizerAgent retraining → GovernanceAgent approval → RAGAgent retrain
- New knowledge documents → Human review → GovernanceAgent approval → Knowledge base

## 📈 Monitoring & Observability

### Metrics Tracked
- Per-agent latency (p50, p95, p99)
- Success rate by agent
- Token usage and costs
- Knowledge base hit rate
- Approval workflow SLA
- Query patterns and trends

### Alerts
- Agent failure rate > 5%
- Response time > 5 seconds
- Knowledge gap detected
- Approval SLA breach
- Cost threshold exceeded

### Dashboards
See notebooks in `notebooks/08_llmops_monitoring/` for monitoring dashboards.

## 🚢 Deployment

### Infrastructure (Azure)

```bash
cd infra
./deploy.sh
```

This deploys:
- Databricks workspace
- Azure Key Vault
- Storage accounts
- Network security groups
- RBAC assignments

### Databricks Jobs

Scheduled jobs are defined in `jobs/`:
- `optimizer.job.json`: Daily knowledge gap detection
- `retraining.job.json`: Weekly model retraining
- `monitoring.job.json`: Hourly metrics collection
- `rag_learning.job.json`: Process pending feedback

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Agent Specifications](docs/agent_roles.md)
- [Governance Model](docs/governance_model.md)
- [MAS Design](docs/mas_design.md)
- [API Reference](docs/api_reference.md)
- [Deployment Guide](docs/deployment_guide.md)
- [User Guide](docs/user_guide.md)
- [Operations Runbook](docs/ops_runbook.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🧪 Testing

```bash
pytest tests/ -v --cov=src --cov-report=html
```

Target: 80%+ code coverage

## 📝 Usage Examples

### Simple Query
```python
from src.core.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()
response = orchestrator.process_request(
    user_query="What are the top 10 customers by sales?",
    user_role="data_analyst"
)
```

### Code Generation
```python
response = orchestrator.process_request(
    user_query="Generate SQL to find top 10 customers by sales",
    user_role="data_engineer"
)
# Returns: Generated SQL code with validation
```

### Full Pipeline with Execution
```python
response = orchestrator.process_request(
    user_query="Execute SQL to find top 10 customers and save to table",
    user_role="data_engineer"
)
# Requires approval → Executes → Returns results
```

## 🛠️ Development

### Adding a New Agent

1. Create agent class inheriting from `BaseAgent`
2. Implement required methods
3. Register in `agent_registry` table
4. Add configuration to `config/agents.yaml`
5. Update orchestrator planning logic

### Code Standards

- PEP 8 compliance
- Type hints on all functions
- Docstrings for all classes/functions
- Comprehensive error handling
- Logging at INFO, DEBUG, ERROR levels
- No hardcoded values (use config)

## 🐛 Troubleshooting

See [Troubleshooting Guide](docs/troubleshooting.md) for common issues.

## 📄 License

[Your License Here]

## 👥 Contributing

[Contributing Guidelines]

## 📞 Support

[Support Contact Information]


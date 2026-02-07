# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Setup
# MAGIC 
# MAGIC This notebook initializes and registers all agents.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Agent Classes

# COMMAND ----------

import sys
import os

# Add src to path
# Update this path to match your Databricks Repos path
# Option 1: Auto-detect from current notebook location
try:
    notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    repo_path = "/".join(notebook_path.split("/")[:4])  # Gets /Workspace/Repos/username/repo-name
    sys.path.append(repo_path)
    print(f"✓ Added to path: {repo_path}")
except:
    # Option 2: Manual path (update with your repo path)
    sys.path.append("/Workspace/Repos/your-username/aiops-agentic-mas-platform")
    print("⚠ Using manual path - please update if needed")
from src.core.agent_registry import AgentRegistry
from src.core.orchestrator import OrchestratorAgent
from src.agents.rag_agent import RAGAgent
from src.agents.code_agent import CodeAgent
from src.agents.testcase_agent import TestCaseAgent
from src.agents.powerbi_agent import PowerBIAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.feedback_agent import FeedbackAgent
from src.agents.optimizer_agent import OptimizerAgent
from src.agents.governance_agent import GovernanceAgent
from src.agents.promptops_agent import PromptOpsAgent
from src.agents.llmops_agent import LLMOpsAgent

# COMMAND ----------

# MAGIC %md
# MAGIC ## Initialize Agents

# COMMAND ----------

# Initialize all agents
agents = {
    "OrchestratorAgent": OrchestratorAgent(),
    "RAGAgent": RAGAgent(),
    "CodeAgent": CodeAgent(),
    "TestCaseAgent": TestCaseAgent(),
    "PowerBIAgent": PowerBIAgent(),
    "ExecutionAgent": ExecutionAgent(),
    "FeedbackAgent": FeedbackAgent(),
    "OptimizerAgent": OptimizerAgent(),
    "GovernanceAgent": GovernanceAgent(),
    "PromptOpsAgent": PromptOpsAgent(),
    "LLMOpsAgent": LLMOpsAgent()
}

print(f"✓ Initialized {len(agents)} agents")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Register Agents

# COMMAND ----------

registry = AgentRegistry()

for agent_name, agent in agents.items():
    try:
        registry.register_agent(
            agent_id=agent.agent_id,
            agent_name=agent_name,
            agent_type=agent_name,
            capabilities=["process", "handle_message"],
            version="1.0.0"
        )
        print(f"✓ Registered {agent_name}")
    except Exception as e:
        print(f"✗ Failed to register {agent_name}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Agent Communication

# COMMAND ----------

# Test message bus
orchestrator = agents["OrchestratorAgent"]
test_message_id = orchestrator.send_message(
    to_agent="RAGAgent",
    content={"test": "message"},
    message_type="request"
)
print(f"✓ Test message sent: {test_message_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Agent Status Report

# COMMAND ----------

# Get all registered agents
all_agents = registry.get_all_agents()
print(f"\nRegistered Agents: {len(all_agents)}")
for agent in all_agents:
    print(f"  - {agent['agent_name']}: {agent['status']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Complete

# COMMAND ----------

print("=" * 50)
print("Agent Setup Complete")
print("=" * 50)
print(f"All {len(agents)} agents initialized and registered.")
print("System is ready for use.")


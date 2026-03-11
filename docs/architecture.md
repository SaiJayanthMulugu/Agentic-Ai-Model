# System Architecture

## Overview

The AIOps Agentic MAS Platform is a Multi-Agent System (MAS) built on Databricks with RAG capabilities.

## Architecture Diagram

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

## Components

### Core Framework
- **BaseAgent**: Abstract base class for all agents
- **OrchestratorAgent**: Master controller
- **AgentRegistry**: Agent discovery and registration
- **AgentMemory**: Shared memory system
- **MessageBus**: Agent-to-agent communication
- **EventSystem**: Event-driven communication

### Planning Strategies
- **ReAct**: Reasoning + Acting loop
- **ToT**: Tree of Thoughts
- **Chain of Thought**: Sequential reasoning

### Agents
1. OrchestratorAgent
2. RAGAgent
3. CodeAgent
4. TestCaseAgent
5. PowerBIAgent
6. ExecutionAgent
7. FeedbackAgent
8. OptimizerAgent
9. GovernanceAgent
10. PromptOpsAgent
11. LLMOpsAgent

### Governance
- RBAC Manager
- Approval Workflows
- Audit Logging

### LLMOps
- Monitoring
- Alerting
- Metrics Collection

## Data Flow

1. User submits query
2. OrchestratorAgent detects intent
3. Creates execution plan
4. Delegates tasks via message bus
5. Agents process tasks
6. Responses aggregated
7. Final response returned


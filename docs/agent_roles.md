# Agent Roles and Specifications

## Agent Hierarchy

### 0. OrchestratorAgent
- **Role**: Master controller
- **Responsibilities**:
  - Receives user requests
  - Intent detection
  - Execution plan creation
  - Task delegation
  - RBAC enforcement
  - Response aggregation

### 1. RAGAgent
- **Role**: Knowledge retrieval
- **Capabilities**:
  - Vector search
  - Semantic similarity
  - Context retrieval
  - NO execution

### 2. CodeAgent
- **Role**: Code generation
- **Capabilities**:
  - SQL/PySpark/Python generation
  - Code validation
  - NO execution

### 3. TestCaseAgent
- **Role**: QA intelligence
- **Capabilities**:
  - Test generation
  - Validation rules

### 4. PowerBIAgent
- **Role**: BI validation
- **Capabilities**:
  - SQL reconciliation
  - DAX validation
  - Semantic model checks

### 5. ExecutionAgent
- **Role**: Controlled executor
- **DANGEROUS**: Requires approval
- **Capabilities**:
  - Code execution
  - Fully audited
  - Dry-run first

### 6. FeedbackAgent
- **Role**: Learning collector
- **Capabilities**:
  - Feedback collection
  - Learning signals

### 7. OptimizerAgent
- **Role**: Self-healing
- **Capabilities**:
  - Knowledge gap detection
  - Performance analysis
  - Retraining requests

### 8. GovernanceAgent
- **Role**: Approval authority
- **Capabilities**:
  - Approval workflows
  - Model promotion
  - RBAC management

### 9. PromptOpsAgent
- **Role**: Prompt lifecycle
- **Capabilities**:
  - Prompt versioning
  - A/B testing
  - Performance analytics

### 10. LLMOpsAgent
- **Role**: Observability
- **Capabilities**:
  - Latency monitoring
  - Token tracking
  - Cost calculation
  - Alert generation


# Governance Model

## RBAC Roles

### Admin
- All permissions
- Full system access

### Data Engineer
- Read knowledge
- Generate code
- Execute SQL/PySpark
- Generate tests
- Restrictions: No delete, no promote

### Data Analyst
- Read knowledge
- Query RAG
- View metrics
- Provide feedback
- Restrictions: No execute, no code generation

### Knowledge Curator
- Approve documents
- Manage knowledge base
- Approve retraining

### Governance Officer
- Approve execution
- Approve retraining
- Manage RBAC
- View audit logs

## Approval Workflows

### Execution Approval
1. ExecutionAgent creates request
2. GovernanceAgent reviews
3. Auto-approve if confidence > threshold
4. Manual approval if needed
5. Execute after approval

### Retraining Approval
1. OptimizerAgent detects need
2. Creates retraining request
3. GovernanceAgent approves
4. RAGAgent retrains model

### Knowledge Base Approval
1. New document added
2. Quality control check
3. Human review
4. GovernanceAgent approval
5. Document activated

## Audit Logging

All actions are logged to `audit_log` table with:
- Event type
- Actor (user/agent)
- Action
- Resource details
- Timestamp


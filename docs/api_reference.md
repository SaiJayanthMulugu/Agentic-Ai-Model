# API Reference

## OrchestratorAgent

### process_request()

```python
orchestrator.process_request(
    user_query: str,
    user_id: str,
    user_role: str = "viewer",
    planning_strategy: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

Process a user request end-to-end.

**Returns**:
- `request_id`: Unique request ID
- `status`: success/error/denied
- `intent`: Detected intent
- `plan`: Execution plan
- `results`: Aggregated results

## RAGAgent

### process()

```python
rag_agent.process(
    task: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

Retrieve knowledge from knowledge base.

**Returns**:
- `status`: success/error
- `documents`: Retrieved documents
- `explanation`: Retrieval explanation

## CodeAgent

### process()

```python
code_agent.process(
    task: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

Generate code based on query and context.

**Returns**:
- `status`: success/error
- `code`: Generated code
- `code_type`: sql/pyspark/python
- `validation`: Validation results

## Message Bus

### send_message()

```python
message_bus.send_message(
    from_agent: str,
    to_agent: str,
    content: Dict[str, Any],
    message_type: str = "request",
    correlation_id: Optional[str] = None,
    priority: int = 5
) -> str
```

Send a message to another agent.

## Approval Workflow

### create_approval_request()

```python
approval_workflow.create_approval_request(
    request_type: str,
    requester_agent: str,
    requester_user: Optional[str],
    request_content: Dict[str, Any],
    priority: int = 5,
    confidence_score: Optional[float] = None
) -> str
```

Create an approval request.


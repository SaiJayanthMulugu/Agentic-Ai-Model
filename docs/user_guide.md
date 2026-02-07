# User Guide

## Getting Started

### Basic Query

```python
from src.core.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()
response = orchestrator.process_request(
    user_query="What is SQL?",
    user_id="your_user_id",
    user_role="data_analyst"
)
```

### Code Generation

```python
response = orchestrator.process_request(
    user_query="Generate SQL to find top 10 customers by sales",
    user_id="your_user_id",
    user_role="data_engineer"
)
```

### Code Execution

```python
response = orchestrator.process_request(
    user_query="Execute SQL to find top 10 customers and save to table",
    user_id="your_user_id",
    user_role="data_engineer"
)
# Requires approval
```

## Using the Chatbot Interface

1. Open `notebooks/01_chatbot/01_chatbot_interface.py`
2. Enter your query in the widget
3. Select your role
4. Run the notebook
5. View results and provide feedback

## Feedback

Provide feedback using the feedback widget in the chatbot interface:
- Thumbs up/down
- Star rating (1-5)
- Correction text

## Permissions

Your role determines what you can do:
- **Viewer**: Read-only access
- **Data Analyst**: Query RAG, view metrics
- **Data Engineer**: Generate and execute code
- **Admin**: Full access


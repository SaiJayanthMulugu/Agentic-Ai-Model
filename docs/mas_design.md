# MAS Design

## Multi-Agent System Architecture

### Communication Patterns

**Message Bus**: All agents communicate via Delta table `agent_messages`
- No direct agent-to-agent calls
- Asynchronous message passing
- Priority-based message handling
- Correlation ID tracking

**Shared Memory**: Delta table `agent_shared_memory`
- Key-value store
- TTL: 24 hours
- Context sharing between agents

**Event System**: Delta table `agent_events`
- Event-driven communication
- Subscriber pattern
- Event types: task_completed, approval_needed, etc.

### Planning Strategies

1. **ReAct**: Thought-Action-Observation loop
2. **ToT**: Tree of Thoughts exploration
3. **Chain of Thought**: Sequential reasoning

### Agent Lifecycle

1. Registration in `agent_registry`
2. Heartbeat monitoring
3. Status tracking
4. Capability discovery

## Design Principles

- **Loose Coupling**: Agents communicate via message bus
- **Single Responsibility**: Each agent has one clear purpose
- **No Direct Calls**: All communication through message bus
- **Audit Everything**: All actions logged
- **RBAC First**: Permissions checked before actions


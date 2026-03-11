-- Agent Communication Tables
-- Message bus, event system for agent-to-agent communication

USE SCHEMA mas_system;

-- Message Bus: All agent-to-agent communication
CREATE TABLE IF NOT EXISTS agent_messages (
    message_id STRING NOT NULL,
    from_agent STRING NOT NULL,
    to_agent STRING NOT NULL,
    message_type STRING NOT NULL,
    content STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    correlation_id STRING,
    priority INT,
    status STRING NOT NULL,
    processed_at TIMESTAMP,
    error_message STRING
) USING DELTA
PARTITIONED BY (to_agent, message_type)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Event System: Event-driven communication
CREATE TABLE IF NOT EXISTS agent_events (
    event_id STRING NOT NULL,
    event_type STRING NOT NULL,
    source_agent STRING NOT NULL,
    event_data STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    processed BOOLEAN,
    processed_at TIMESTAMP,
    subscribers ARRAY<STRING>
) USING DELTA
PARTITIONED BY (event_type);

-- Event Subscriptions: Which agents subscribe to which events
CREATE TABLE IF NOT EXISTS agent_event_subscriptions (
    subscription_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    event_type STRING NOT NULL,
    subscribed_at TIMESTAMP NOT NULL,
    active BOOLEAN DEFAULT true,
    PRIMARY KEY (subscription_id)
) USING DELTA
PARTITIONED BY (agent_id);

-- Communication Metrics
CREATE TABLE IF NOT EXISTS communication_metrics (
    metric_id STRING NOT NULL,
    metric_date DATE NOT NULL,
    agent_id STRING,
    messages_sent INT,
    messages_received INT,
    avg_message_latency_ms FLOAT,
    failed_messages INT,
    events_published INT,
    events_processed INT,
    PRIMARY KEY (metric_id)
) USING DELTA
PARTITIONED BY (metric_date, agent_id);


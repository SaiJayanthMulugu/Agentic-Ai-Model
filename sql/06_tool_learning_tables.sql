-- Tool Learning Tables
-- Tracks tool usage patterns and learning

USE SCHEMA mas_system;

-- Tool Usage History
CREATE TABLE IF NOT EXISTS tool_usage_history (
    usage_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    tool_name STRING NOT NULL,
    tool_input MAP<STRING, STRING>,
    tool_output STRING,
    success BOOLEAN,
    execution_time_ms FLOAT,
    used_at TIMESTAMP NOT NULL,
    PRIMARY KEY (usage_id)
) USING DELTA
PARTITIONED BY (agent_id, DATE(used_at));

-- Tool Performance Metrics
CREATE TABLE IF NOT EXISTS tool_performance_metrics (
    metric_id STRING NOT NULL,
    tool_name STRING NOT NULL,
    agent_id STRING,
    metric_date DATE NOT NULL,
    success_count INT,
    failure_count INT,
    avg_execution_time_ms FLOAT,
    p50_execution_time_ms FLOAT,
    p95_execution_time_ms FLOAT,
    p99_execution_time_ms FLOAT,
    total_usage_count INT,
    PRIMARY KEY (metric_id)
) USING DELTA
PARTITIONED BY (tool_name, metric_date);


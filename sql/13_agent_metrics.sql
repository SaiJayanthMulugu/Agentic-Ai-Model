-- Agent Performance Metrics Tables
-- Tracks latency, success rates, token usage, costs

USE SCHEMA mas_system;

-- Agent Performance Metrics
CREATE TABLE IF NOT EXISTS agent_metrics (
    metric_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    metric_date DATE NOT NULL,
    metric_hour INT,  -- 0-23 for hourly aggregation
    total_requests INT,
    successful_requests INT,
    failed_requests INT,
    avg_latency_ms FLOAT,
    p50_latency_ms FLOAT,
    p95_latency_ms FLOAT,
    p99_latency_ms FLOAT,
    max_latency_ms FLOAT,
    min_latency_ms FLOAT,
    total_tokens_used BIGINT,
    total_cost_usd FLOAT,
    PRIMARY KEY (metric_id)
) USING DELTA
PARTITIONED BY (agent_id, metric_date);

-- Request Details (granular request-level metrics)
CREATE TABLE IF NOT EXISTS agent_request_details (
    request_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    user_id STRING,
    request_type STRING,
    status STRING NOT NULL,  -- success, failure, timeout
    latency_ms FLOAT,
    tokens_used INT,
    cost_usd FLOAT,
    error_message STRING,
    request_timestamp TIMESTAMP NOT NULL,
    PRIMARY KEY (request_id)
) USING DELTA
PARTITIONED BY (agent_id, DATE(request_timestamp));

-- Cost Tracking
CREATE TABLE IF NOT EXISTS agent_costs (
    cost_id STRING NOT NULL,
    agent_id STRING,
    cost_date DATE NOT NULL,
    total_tokens BIGINT,
    input_tokens BIGINT,
    output_tokens BIGINT,
    cost_usd FLOAT,
    cost_breakdown MAP<STRING, FLOAT>,  -- per-endpoint costs
    PRIMARY KEY (cost_id)
) USING DELTA
PARTITIONED BY (cost_date);

-- Alert History
CREATE TABLE IF NOT EXISTS agent_alerts (
    alert_id STRING NOT NULL,
    alert_type STRING NOT NULL,  -- failure_rate, latency, cost_threshold, knowledge_gap
    agent_id STRING,
    severity STRING NOT NULL,  -- low, medium, high, critical
    alert_message STRING NOT NULL,
    alert_data MAP<STRING, STRING>,
    status STRING NOT NULL,  -- active, acknowledged, resolved, dismissed
    created_at TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    acknowledged_by STRING,
    resolved_at TIMESTAMP,
    resolved_by STRING,
    PRIMARY KEY (alert_id)
) USING DELTA
PARTITIONED BY (alert_type, status, DATE(created_at));

-- System Health Summary
CREATE TABLE IF NOT EXISTS system_health_summary (
    summary_id STRING NOT NULL,
    summary_date DATE NOT NULL,
    summary_hour INT,
    total_requests INT,
    successful_requests INT,
    failed_requests INT,
    system_availability_pct FLOAT,
    avg_response_time_ms FLOAT,
    total_cost_usd FLOAT,
    active_agents_count INT,
    alerts_count INT,
    PRIMARY KEY (summary_id)
) USING DELTA
PARTITIONED BY (summary_date);


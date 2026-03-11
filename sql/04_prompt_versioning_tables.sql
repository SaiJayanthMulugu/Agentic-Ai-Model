-- Prompt Versioning Tables
-- Manages prompt lifecycle, versioning, A/B testing

USE SCHEMA mas_system;

-- Prompt Versions
CREATE TABLE IF NOT EXISTS prompt_versions (
    prompt_id STRING NOT NULL,
    version INT NOT NULL,
    prompt_name STRING NOT NULL,
    agent_type STRING NOT NULL,
    prompt_content STRING NOT NULL,
    variables MAP<STRING, STRING>,  -- Template variables
    status STRING NOT NULL,  -- draft, active, archived, deprecated
    created_at TIMESTAMP NOT NULL,
    created_by STRING,
    performance_metrics MAP<STRING, FLOAT>,  -- success_rate, avg_latency, etc.
    PRIMARY KEY (prompt_id, version)
) USING DELTA
PARTITIONED BY (agent_type, status);

-- Prompt A/B Tests
CREATE TABLE IF NOT EXISTS prompt_ab_tests (
    test_id STRING NOT NULL,
    prompt_id STRING NOT NULL,
    version_a INT NOT NULL,
    version_b INT NOT NULL,
    status STRING NOT NULL,  -- running, completed, cancelled
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    traffic_split FLOAT,  -- 0.0 to 1.0 for version_a
    metrics_a MAP<STRING, FLOAT>,
    metrics_b MAP<STRING, FLOAT>,
    winner_version INT,
    created_by STRING,
    PRIMARY KEY (test_id)
) USING DELTA;

-- Prompt Usage Log
CREATE TABLE IF NOT EXISTS prompt_usage_log (
    usage_id STRING NOT NULL,
    prompt_id STRING NOT NULL,
    version INT NOT NULL,
    agent_type STRING NOT NULL,
    request_id STRING,
    used_at TIMESTAMP NOT NULL,
    success BOOLEAN,
    latency_ms FLOAT,
    token_count INT,
    PRIMARY KEY (usage_id)
) USING DELTA
PARTITIONED BY (agent_type, DATE(used_at));


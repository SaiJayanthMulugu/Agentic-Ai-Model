-- Core System Tables
-- Idempotent: Uses CREATE TABLE IF NOT EXISTS

USE SCHEMA mas_system;

-- Agent Registry: Tracks all registered agents
CREATE TABLE IF NOT EXISTS agent_registry (
    agent_id STRING NOT NULL,
    agent_name STRING NOT NULL,
    agent_type STRING NOT NULL,
    status STRING NOT NULL,  -- active, inactive, maintenance
    version STRING,
    capabilities ARRAY<STRING>,
    registered_at TIMESTAMP NOT NULL,
    last_heartbeat TIMESTAMP,
    metadata MAP<STRING, STRING>,
    PRIMARY KEY (agent_id)
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Agent Status History
CREATE TABLE IF NOT EXISTS agent_status_history (
    status_id STRING NOT NULL,
    agent_id STRING NOT NULL,
    status STRING NOT NULL,
    changed_at TIMESTAMP NOT NULL,
    changed_by STRING,
    reason STRING,
    PRIMARY KEY (status_id)
) USING DELTA
PARTITIONED BY (agent_id);

-- System Configuration
CREATE TABLE IF NOT EXISTS system_config (
    config_key STRING NOT NULL,
    config_value STRING,
    config_type STRING,  -- string, int, float, bool, json
    environment STRING,  -- dev, prod
    updated_at TIMESTAMP NOT NULL,
    updated_by STRING,
    PRIMARY KEY (config_key, environment)
) USING DELTA;


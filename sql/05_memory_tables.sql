-- Shared Agent Memory Tables
-- TTL-based key-value store for context sharing

USE SCHEMA mas_system;

-- Shared Memory: Key-value store for agent context sharing
CREATE TABLE IF NOT EXISTS agent_shared_memory (
    memory_key STRING NOT NULL,
    memory_value STRING NOT NULL,  -- JSON string
    agent_owner STRING NOT NULL,  -- Agent that created this memory
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,  -- TTL: 24 hours default
    access_count INT,
    last_accessed_at TIMESTAMP,
    tags ARRAY<STRING>,
    PRIMARY KEY (memory_key)
) USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Memory Access Log
CREATE TABLE IF NOT EXISTS memory_access_log (
    access_id STRING NOT NULL,
    memory_key STRING NOT NULL,
    accessed_by_agent STRING NOT NULL,
    access_type STRING NOT NULL,  -- read, write, delete
    accessed_at TIMESTAMP NOT NULL,
    PRIMARY KEY (access_id)
) USING DELTA
PARTITIONED BY (DATE(accessed_at));


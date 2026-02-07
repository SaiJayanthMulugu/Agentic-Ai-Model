-- RAG Query Logging Tables
-- Tracks all RAG queries for learning and analytics

USE SCHEMA mas_system;

-- RAG Query Logs
CREATE TABLE IF NOT EXISTS rag_query_logs (
    query_id STRING NOT NULL,
    user_id STRING,
    query_text STRING NOT NULL,
    query_embedding ARRAY<FLOAT>,
    retrieved_docs ARRAY<STRING>,  -- Array of doc_ids
    retrieved_scores ARRAY<FLOAT>,  -- Similarity scores
    response_text STRING,
    response_quality_score FLOAT,
    query_timestamp TIMESTAMP NOT NULL,
    response_time_ms FLOAT,
    token_count INT,
    PRIMARY KEY (query_id)
) USING DELTA
PARTITIONED BY (DATE(query_timestamp))
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Query Patterns (for knowledge gap detection)
CREATE TABLE IF NOT EXISTS rag_query_patterns (
    pattern_id STRING NOT NULL,
    pattern_text STRING NOT NULL,
    frequency INT DEFAULT 1,
    first_seen_at TIMESTAMP NOT NULL,
    last_seen_at TIMESTAMP NOT NULL,
    knowledge_gap_detected BOOLEAN DEFAULT false,
    gap_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    PRIMARY KEY (pattern_id)
) USING DELTA;

-- Knowledge Gaps (detected from query patterns)
CREATE TABLE IF NOT EXISTS rag_knowledge_gaps (
    gap_id STRING NOT NULL,
    gap_description STRING NOT NULL,
    detected_from_queries ARRAY<STRING>,  -- Array of query_ids
    priority STRING,  -- low, medium, high, critical
    status STRING NOT NULL,  -- detected, under_review, resolved, ignored
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    resolved_by STRING,
    PRIMARY KEY (gap_id)
) USING DELTA
PARTITIONED BY (status);


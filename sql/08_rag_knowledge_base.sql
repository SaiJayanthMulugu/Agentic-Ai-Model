-- RAG Knowledge Base Tables
-- Stores documents, embeddings, metadata for RAG system

USE SCHEMA mas_system;

-- Knowledge Base: Main document store
CREATE TABLE IF NOT EXISTS knowledge_base (
    doc_id STRING NOT NULL,
    content STRING NOT NULL,
    title STRING,
    category STRING,
    quality_score FLOAT,
    usage_count BIGINT DEFAULT 0,
    status STRING NOT NULL,  -- active, archived, under_review, rejected
    sensitivity_level STRING NOT NULL,  -- public, internal, confidential
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    created_by STRING,
    approved_by STRING,
    approved_at TIMESTAMP,
    metadata MAP<STRING, STRING>,
    embedding_vector ARRAY<FLOAT>,  -- Optional: store embeddings
    PRIMARY KEY (doc_id)
) USING DELTA
PARTITIONED BY (category, status)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Knowledge Base Versions (for document updates)
CREATE TABLE IF NOT EXISTS knowledge_base_versions (
    version_id STRING NOT NULL,
    doc_id STRING NOT NULL,
    version_number INT NOT NULL,
    content STRING NOT NULL,
    changed_fields ARRAY<STRING>,
    created_at TIMESTAMP NOT NULL,
    created_by STRING,
    PRIMARY KEY (version_id)
) USING DELTA
PARTITIONED BY (doc_id);

-- Knowledge Base Tags
CREATE TABLE IF NOT EXISTS knowledge_base_tags (
    tag_id STRING NOT NULL,
    doc_id STRING NOT NULL,
    tag_name STRING NOT NULL,
    tag_value STRING,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (tag_id)
) USING DELTA
PARTITIONED BY (doc_id);

-- Knowledge Base Relationships (for document linking)
CREATE TABLE IF NOT EXISTS knowledge_base_relationships (
    relationship_id STRING NOT NULL,
    source_doc_id STRING NOT NULL,
    target_doc_id STRING NOT NULL,
    relationship_type STRING NOT NULL,  -- references, related_to, supersedes
    strength FLOAT,  -- 0.0 to 1.0
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (relationship_id)
) USING DELTA;


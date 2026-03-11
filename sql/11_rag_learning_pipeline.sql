-- RAG Learning Pipeline Tables
-- Tracks retraining, model versions, learning metrics

USE SCHEMA mas_system;

-- Retraining Requests
CREATE TABLE IF NOT EXISTS rag_retraining_requests (
    request_id STRING NOT NULL,
    trigger_type STRING NOT NULL,  -- threshold_docs, threshold_feedback, scheduled, manual
    trigger_details MAP<STRING, STRING>,
    status STRING NOT NULL,  -- pending_approval, approved, in_progress, completed, failed, rejected
    requested_at TIMESTAMP NOT NULL,
    requested_by STRING,
    approved_at TIMESTAMP,
    approved_by STRING,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    new_documents_count INT,
    new_feedback_count INT,
    PRIMARY KEY (request_id)
) USING DELTA
PARTITIONED BY (status);

-- Model Training History
CREATE TABLE IF NOT EXISTS rag_training_history (
    training_id STRING NOT NULL,
    request_id STRING,
    model_version STRING NOT NULL,
    training_date DATE NOT NULL,
    documents_used ARRAY<STRING>,  -- Array of doc_ids
    feedback_used ARRAY<STRING>,  -- Array of feedback_ids
    training_metrics MAP<STRING, FLOAT>,  -- loss, accuracy, etc.
    validation_metrics MAP<STRING, FLOAT>,
    status STRING NOT NULL,  -- training, completed, failed
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    deployed BOOLEAN DEFAULT false,
    deployed_at TIMESTAMP,
    PRIMARY KEY (training_id)
) USING DELTA
PARTITIONED BY (training_date);

-- Model Versions
CREATE TABLE IF NOT EXISTS rag_model_versions (
    model_version STRING NOT NULL,
    training_id STRING NOT NULL,
    status STRING NOT NULL,  -- dev, staging, prod, archived
    mlflow_run_id STRING,
    unity_catalog_path STRING,
    endpoint_name STRING,
    performance_metrics MAP<STRING, FLOAT>,
    created_at TIMESTAMP NOT NULL,
    promoted_to_prod_at TIMESTAMP,
    deprecated_at TIMESTAMP,
    PRIMARY KEY (model_version)
) USING DELTA
PARTITIONED BY (status);

-- Learning Metrics
CREATE TABLE IF NOT EXISTS rag_learning_metrics (
    metric_id STRING NOT NULL,
    metric_date DATE NOT NULL,
    total_queries INT,
    successful_queries INT,
    avg_response_quality FLOAT,
    knowledge_base_hit_rate FLOAT,
    avg_retrieval_time_ms FLOAT,
    avg_response_time_ms FLOAT,
    total_feedback_count INT,
    positive_feedback_rate FLOAT,
    PRIMARY KEY (metric_id)
) USING DELTA
PARTITIONED BY (metric_date);


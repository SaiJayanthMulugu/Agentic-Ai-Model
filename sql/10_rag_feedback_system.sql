-- RAG Feedback System Tables
-- Collects user feedback for continuous learning

USE SCHEMA mas_system;

-- User Feedback
CREATE TABLE IF NOT EXISTS rag_user_feedback (
    feedback_id STRING NOT NULL,
    query_id STRING NOT NULL,
    user_id STRING,
    feedback_type STRING NOT NULL,  -- thumbs_up, thumbs_down, rating, correction
    rating_value INT,  -- 1-5 for star ratings
    feedback_text STRING,
    correction_text STRING,  -- If user provides corrected answer
    is_helpful BOOLEAN,
    feedback_timestamp TIMESTAMP NOT NULL,
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMP,
    PRIMARY KEY (feedback_id)
) USING DELTA
PARTITIONED BY (feedback_type, DATE(feedback_timestamp));

-- Feedback Aggregation (for retraining triggers)
CREATE TABLE IF NOT EXISTS rag_feedback_aggregation (
    aggregation_id STRING NOT NULL,
    aggregation_date DATE NOT NULL,
    total_feedback_count INT,
    positive_feedback_count INT,
    negative_feedback_count INT,
    avg_rating FLOAT,
    high_quality_feedback_count INT,  -- Feedback with corrections or detailed text
    retraining_triggered BOOLEAN DEFAULT false,
    PRIMARY KEY (aggregation_id)
) USING DELTA
PARTITIONED BY (aggregation_date);

-- Document Candidates (auto-generated from feedback)
CREATE TABLE IF NOT EXISTS rag_document_candidates (
    candidate_id STRING NOT NULL,
    source_feedback_id STRING NOT NULL,
    candidate_content STRING NOT NULL,
    candidate_title STRING,
    category STRING,
    quality_score FLOAT,
    status STRING NOT NULL,  -- pending_review, approved, rejected
    created_at TIMESTAMP NOT NULL,
    reviewed_at TIMESTAMP,
    reviewed_by STRING,
    PRIMARY KEY (candidate_id)
) USING DELTA
PARTITIONED BY (status);


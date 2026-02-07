-- Task Planning Tables
-- Stores execution plans, task decomposition, planning history

USE SCHEMA mas_system;

-- Execution Plans
CREATE TABLE IF NOT EXISTS execution_plans (
    plan_id STRING NOT NULL,
    user_query STRING NOT NULL,
    intent STRING,
    planning_strategy STRING NOT NULL,  -- react, tot, chain_of_thought
    plan_steps ARRAY<STRUCT<
        step_id: STRING,
        agent_type: STRING,
        task_description: STRING,
        dependencies: ARRAY<STRING>,
        status: STRING,
        result: STRING
    >>,
    status STRING NOT NULL,  -- created, executing, completed, failed, cancelled
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by STRING,
    correlation_id STRING,  -- Track related requests
    PRIMARY KEY (plan_id)
) USING DELTA
PARTITIONED BY (planning_strategy, DATE(created_at));

-- Task Execution History
CREATE TABLE IF NOT EXISTS task_execution_history (
    task_id STRING NOT NULL,
    plan_id STRING NOT NULL,
    step_id STRING NOT NULL,
    agent_type STRING NOT NULL,
    task_description STRING,
    status STRING NOT NULL,  -- pending, executing, completed, failed, skipped
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_ms FLOAT,
    result STRING,  -- JSON string
    error_message STRING,
    retry_count INT,
    PRIMARY KEY (task_id)
) USING DELTA
PARTITIONED BY (plan_id, agent_type);

-- Planning Metrics
CREATE TABLE IF NOT EXISTS planning_metrics (
    metric_id STRING NOT NULL,
    planning_strategy STRING NOT NULL,
    metric_date DATE NOT NULL,
    total_plans INT,
    successful_plans INT,
    failed_plans INT,
    avg_planning_time_ms FLOAT,
    avg_execution_time_ms FLOAT,
    avg_steps_per_plan FLOAT,
    PRIMARY KEY (metric_id)
) USING DELTA
PARTITIONED BY (planning_strategy, metric_date);


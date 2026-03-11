-- Governance Tables
-- RBAC, Approval Workflows, Audit Logging

USE SCHEMA mas_system;

-- RBAC: User Roles
CREATE TABLE IF NOT EXISTS user_roles (
    user_id STRING NOT NULL,
    role STRING NOT NULL,
    assigned_at TIMESTAMP NOT NULL,
    assigned_by STRING,
    expires_at TIMESTAMP,
    PRIMARY KEY (user_id, role)
) USING DELTA
PARTITIONED BY (role);

-- RBAC: Role Permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    role STRING NOT NULL,
    permission STRING NOT NULL,
    granted_at TIMESTAMP NOT NULL,
    granted_by STRING,
    PRIMARY KEY (role, permission)
) USING DELTA
PARTITIONED BY (role);

-- Approval Requests
CREATE TABLE IF NOT EXISTS approval_requests (
    request_id STRING NOT NULL,
    request_type STRING NOT NULL,  -- execution, retraining, knowledge_add, model_promotion
    requester_agent STRING NOT NULL,
    requester_user STRING,
    request_content MAP<STRING, STRING>,  -- JSON-like structure
    status STRING NOT NULL,  -- pending, approved, rejected, expired
    priority INT,
    created_at TIMESTAMP NOT NULL,
    approved_at TIMESTAMP,
    approved_by STRING,
    rejection_reason STRING,
    expires_at TIMESTAMP,
    auto_approved BOOLEAN,
    confidence_score FLOAT,
    PRIMARY KEY (request_id)
) USING DELTA
PARTITIONED BY (request_type, status);

-- Approval History
CREATE TABLE IF NOT EXISTS approval_history (
    history_id STRING NOT NULL,
    request_id STRING NOT NULL,
    action STRING NOT NULL,  -- created, approved, rejected, expired
    actor STRING NOT NULL,  -- user or agent
    timestamp TIMESTAMP NOT NULL,
    notes STRING,
    PRIMARY KEY (history_id)
) USING DELTA
PARTITIONED BY (request_id);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id STRING NOT NULL,
    event_type STRING NOT NULL,  -- agent_action, approval, rbac_change, execution
    actor STRING NOT NULL,  -- user or agent
    action STRING NOT NULL,
    resource_type STRING,
    resource_id STRING,
    details MAP<STRING, STRING>,
    timestamp TIMESTAMP NOT NULL,
    ip_address STRING,
    user_agent STRING,
    PRIMARY KEY (audit_id)
) USING DELTA
PARTITIONED BY (event_type, DATE(timestamp));


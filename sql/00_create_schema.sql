-- Create Schema for MAS System
-- This script creates the Unity Catalog schema for the Multi-Agent System
-- Idempotent: Safe to run multiple times
-- Note: Skip CREATE CATALOG if "main" already exists in your workspace

USE CATALOG main;

CREATE SCHEMA IF NOT EXISTS mas_system
COMMENT 'Multi-Agent System (MAS) platform schema for AIOps';

USE SCHEMA mas_system;

-- Grant permissions (fully qualified schema for Unity Catalog)
GRANT USE SCHEMA ON SCHEMA main.mas_system TO `account users`;
GRANT USE SCHEMA ON SCHEMA main.mas_system TO `workspace users`;


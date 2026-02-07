-- Create Schema for MAS System
-- This script creates the Unity Catalog schema for the Multi-Agent System
-- Idempotent: Safe to run multiple times

CREATE CATALOG IF NOT EXISTS main;

USE CATALOG main;

CREATE SCHEMA IF NOT EXISTS mas_system
COMMENT 'Multi-Agent System (MAS) platform schema for AIOps';

USE SCHEMA mas_system;

-- Grant permissions
GRANT USE SCHEMA ON SCHEMA mas_system TO `account users`;
GRANT USE SCHEMA ON SCHEMA mas_system TO `workspace users`;


-- RBAC Grants
-- Grant appropriate permissions to roles

USE SCHEMA mas_system;

-- Note: In production, these grants should be managed through Unity Catalog
-- This is a template for manual execution

-- Grant SELECT on all tables to viewer role
-- GRANT SELECT ON ALL TABLES IN SCHEMA mas_system TO ROLE viewer;

-- Grant SELECT, INSERT, UPDATE on specific tables to data_analyst role
-- GRANT SELECT, INSERT, UPDATE ON TABLE agent_messages TO ROLE data_analyst;
-- GRANT SELECT, INSERT ON TABLE rag_user_feedback TO ROLE data_analyst;

-- Grant additional permissions to data_engineer role
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA mas_system TO ROLE data_engineer;
-- GRANT EXECUTE ON FUNCTION execute_sql TO ROLE data_engineer;

-- Grant all permissions to admin role
-- GRANT ALL PRIVILEGES ON SCHEMA mas_system TO ROLE admin;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA mas_system TO ROLE admin;

-- Grant knowledge management permissions to knowledge_curator role
-- GRANT SELECT, INSERT, UPDATE ON TABLE knowledge_base TO ROLE knowledge_curator;
-- GRANT SELECT, INSERT, UPDATE ON TABLE rag_approval_requests TO ROLE knowledge_curator;

-- Grant governance permissions to governance_officer role
-- GRANT SELECT, INSERT, UPDATE ON TABLE approval_requests TO ROLE governance_officer;
-- GRANT SELECT ON TABLE audit_log TO ROLE governance_officer;
-- GRANT SELECT, INSERT, UPDATE ON TABLE user_roles TO ROLE governance_officer;


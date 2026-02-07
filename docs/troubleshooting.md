# Troubleshooting Guide

## Common Issues

### Issue: Agents not registering
**Solution**: Check Unity Catalog permissions and agent_registry table exists.

### Issue: Message bus not working
**Solution**: Verify agent_messages table is created and accessible.

### Issue: RAG queries returning no results
**Solution**: Check knowledge_base table has documents and vector search is configured.

### Issue: Approval workflows not working
**Solution**: Verify approval_requests table exists and GovernanceAgent is registered.

## Debug Mode

Set `LOG_LEVEL=DEBUG` in environment variables for detailed logging.

## Health Checks

Run `notebooks/00_setup/03_validate_installation.py` for system health check.


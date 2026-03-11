"""
RBAC Manager
============

Role-Based Access Control manager.

Features:
- Permission checking
- Role management
- Permission definitions

Author: AI Ops Team
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)


class RBACManager:
    """
    Manages Role-Based Access Control.
    """
    
    def __init__(self):
        """Initialize RBACManager."""
        self.config_loader = ConfigLoader()
        self.rbac_config = self.config_loader.load("rbac_roles.yaml")
        self.roles = self.rbac_config.get("roles", {})
        self.permissions = self.rbac_config.get("permission_definitions", {})
    
    def check_permission(self, role: str, permission: str) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: Role name
            permission: Permission name
        
        Returns:
            True if role has permission, False otherwise
        """
        role_config = self.roles.get(role, {})
        role_permissions = role_config.get("permissions", [])
        
        # Check for "all" permission
        if "all" in role_permissions:
            return True
        
        # Check specific permission
        if permission in role_permissions:
            return True
        
        logger.debug(f"Role {role} does not have permission {permission}")
        return False
    
    def check_restriction(self, role: str, restriction: str) -> bool:
        """
        Check if a role has a specific restriction.
        
        Args:
            role: Role name
            restriction: Restriction name
        
        Returns:
            True if role has restriction, False otherwise
        """
        role_config = self.roles.get(role, {})
        restrictions = role_config.get("restrictions", [])
        
        return restriction in restrictions
    
    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get all permissions for a role.
        
        Args:
            role: Role name
        
        Returns:
            List of permission names
        """
        role_config = self.roles.get(role, {})
        return role_config.get("permissions", [])
    
    def get_role_restrictions(self, role: str) -> List[str]:
        """
        Get all restrictions for a role.
        
        Args:
            role: Role name
        
        Returns:
            List of restriction names
        """
        role_config = self.roles.get(role, {})
        return role_config.get("restrictions", [])
    
    def is_role_valid(self, role: str) -> bool:
        """
        Check if a role is valid.
        
        Args:
            role: Role name
        
        Returns:
            True if role exists, False otherwise
        """
        return role in self.roles


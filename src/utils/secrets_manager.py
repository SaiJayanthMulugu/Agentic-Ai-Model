"""
Secrets Manager
===============

Manages secrets from Azure Key Vault and environment variables.

Features:
- Azure Key Vault integration
- Environment variable fallback
- Secret caching
- Secure secret retrieval

Author: AI Ops Team
Version: 1.0.0
"""

import os
from typing import Optional, Dict, Any

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False
    DefaultAzureCredential = None
    SecretClient = None

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SecretsManager:
    """
    Manages secrets from Azure Key Vault with environment variable fallback.
    """
    
    def __init__(self, key_vault_name: Optional[str] = None):
        """
        Initialize SecretsManager.
        
        Args:
            key_vault_name: Azure Key Vault name. If None, uses AZURE_KEY_VAULT_NAME env var.
        """
        self.key_vault_name = key_vault_name or os.getenv("AZURE_KEY_VAULT_NAME")
        self._secret_client: Optional[SecretClient] = None
        self._cache: Dict[str, str] = {}
        
        # Initialize Key Vault client if name is provided
        if self.key_vault_name and HAS_AZURE:
            try:
                vault_url = f"https://{self.key_vault_name}.vault.azure.net/"
                credential = DefaultAzureCredential()
                self._secret_client = SecretClient(vault_url=vault_url, credential=credential)
                logger.info(f"Initialized Key Vault client for {self.key_vault_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Key Vault client: {e}. Using environment variables only.")
                self._secret_client = None
        else:
            if self.key_vault_name and not HAS_AZURE:
                logger.warning("Azure SDK not available. Using environment variables only.")
            self._secret_client = None
    
    def get_secret(self, secret_name: str, env_var_name: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret from Key Vault or environment variable.
        
        Priority:
        1. Key Vault
        2. Environment variable
        3. Default value
        
        Args:
            secret_name: Secret name in Key Vault
            env_var_name: Environment variable name (defaults to secret_name.upper())
            default: Default value if secret not found
        
        Returns:
            Secret value or None
        """
        # Check cache first
        if secret_name in self._cache:
            return self._cache[secret_name]
        
        # Try Key Vault first
        if self._secret_client:
            try:
                secret = self._secret_client.get_secret(secret_name)
                value = secret.value
                self._cache[secret_name] = value
                logger.debug(f"Retrieved secret {secret_name} from Key Vault")
                return value
            except Exception as e:
                logger.debug(f"Failed to get secret {secret_name} from Key Vault: {e}")
        
        # Fallback to environment variable
        env_name = env_var_name or secret_name.upper().replace("-", "_")
        value = os.getenv(env_name, default)
        
        if value:
            self._cache[secret_name] = value
            logger.debug(f"Retrieved secret {secret_name} from environment variable {env_name}")
        
        if value is None:
            logger.warning(f"Secret {secret_name} not found in Key Vault or environment variables")
        
        return value
    
    def get_databricks_token(self) -> Optional[str]:
        """
        Get Databricks token from secrets.
        
        Returns:
            Databricks token or None
        """
        return self.get_secret("databricks-token", "DATABRICKS_TOKEN")
    
    def get_databricks_host(self) -> Optional[str]:
        """
        Get Databricks host from secrets.
        
        Returns:
            Databricks host URL or None
        """
        return self.get_secret("databricks-host", "DATABRICKS_HOST")
    
    def clear_cache(self) -> None:
        """Clear secret cache."""
        self._cache.clear()
        logger.debug("Secret cache cleared")


"""
Configuration Loader
====================

Loads and merges configuration from YAML files and environment variables.

Features:
- YAML configuration loading
- Environment variable override
- Environment-specific configs (dev, prod)
- Configuration validation
- Type conversion

Author: AI Ops Team
Version: 1.0.0
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """
    Configuration loader that merges YAML configs with environment variables.
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize ConfigLoader.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def load(self, config_path: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file with environment variable overrides.
        
        Args:
            config_path: Path to YAML config file (relative to config_dir)
            environment: Environment name (dev, prod). If None, uses ENVIRONMENT env var.
        
        Returns:
            Merged configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        # Get environment
        if environment is None:
            environment = os.getenv("ENVIRONMENT", "dev")
        
        # Load base config
        base_config = self._load_yaml(config_path)
        
        # Load environment-specific config if exists
        env_config_path = config_path.replace(".yaml", f".{environment}.yaml")
        if not env_config_path.endswith(f".{environment}.yaml"):
            env_config_path = config_path.replace(".yaml", f".{environment}.yaml")
        
        env_config = {}
        if self._file_exists(env_config_path):
            env_config = self._load_yaml(env_config_path)
            logger.info(f"Loaded environment-specific config: {env_config_path}")
        
        # Merge configs (env-specific overrides base)
        merged_config = self._deep_merge(base_config, env_config)
        
        # Substitute environment variables
        resolved_config = self._substitute_env_vars(merged_config)
        
        # Validate required fields
        self._validate_config(resolved_config)
        
        logger.info(f"Loaded configuration from {config_path} for environment {environment}")
        return resolved_config
    
    def _load_yaml(self, config_path: str) -> Dict[str, Any]:
        """
        Load YAML file.
        
        Args:
            config_path: Path to YAML file (relative to config_dir)
        
        Returns:
            Parsed YAML dictionary
        """
        full_path = self.config_dir / config_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Config file not found: {full_path}")
        
        with open(full_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        return config or {}
    
    def _file_exists(self, config_path: str) -> bool:
        """Check if config file exists."""
        full_path = self.config_dir / config_path
        return full_path.exists()
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary
        
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """
        Recursively substitute environment variables in config.
        
        Supports ${VAR_NAME} and ${VAR_NAME:-default_value} syntax.
        
        Args:
            config: Configuration value (can be dict, list, or primitive)
        
        Returns:
            Configuration with environment variables substituted
        """
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Pattern: ${VAR_NAME} or ${VAR_NAME:-default}
            pattern = r'\$\{([^}:]+)(?::-([^}]*))?\}'
            
            def replace_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.lastindex >= 2 else None
                env_value = os.getenv(var_name)
                
                if env_value is not None:
                    return env_value
                elif default_value is not None:
                    return default_value
                else:
                    logger.warning(f"Environment variable {var_name} not found and no default provided")
                    return match.group(0)  # Return original if not found
            
            return re.sub(pattern, replace_var, config)
        else:
            return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration has required fields.
        
        Args:
            config: Configuration dictionary
        
        Raises:
            ValueError: If required fields are missing
        """
        # Basic validation - can be extended
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        logger.debug("Configuration validation passed")
    
    def get(self, config_path: str, key: str, default: Any = None, environment: Optional[str] = None) -> Any:
        """
        Get a specific configuration value.
        
        Args:
            config_path: Path to config file
            key: Configuration key (supports dot notation, e.g., "databricks.host")
            environment: Environment name
        
        Returns:
            Configuration value or default
        """
        config = self.load(config_path, environment)
        
        keys = key.split(".")
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


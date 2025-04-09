"""
Configuration module for the GCP AI Agent Framework.

This module provides utilities for managing application configuration,
including environment-specific settings, API credentials, and default values.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union


class Config:
    """
    Configuration manager for the GCP AI Agent Framework.
    
    Provides methods for loading, accessing, and updating configuration settings.
    Supports environment-specific configuration overrides.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default paths.
        """
        self._config = {}
        self._config_path = config_path
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Default configuration
        self._config = {
            'app': {
                'name': 'GCP AI Agent',
                'version': '1.0.0',
                'debug': False,
                'environment': 'development',
            },
            'api': {
                'base_url': 'http://localhost:8080',
                'timeout': 30,
                'retry_attempts': 3,
            },
            'agent': {
                'name': 'default_agent',
                'description': 'GCP AI Agent',
                'default_language_code': 'en',
            },
            'gcp': {
                'project_id': os.environ.get('GCP_PROJECT_ID', ''),
                'region': os.environ.get('GCP_REGION', 'us-central1'),
                'service_account': os.environ.get('GCP_SERVICE_ACCOUNT', ''),
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'log_to_cloud': False,
            },
            'security': {
                'enable_cors': True,
                'allowed_origins': ['*'],
                'enable_authentication': False,
                'authentication_header': 'X-API-Key',
            }
        }
        
        # Load from config file if provided
        if self._config_path and os.path.exists(self._config_path):
            self._load_from_file(self._config_path)
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file (YAML or JSON)
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.yaml' or ext == '.yml':
                with open(file_path, 'r') as f:
                    file_config = yaml.safe_load(f)
            elif ext == '.json':
                with open(file_path, 'r') as f:
                    file_config = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
            
            # Update config with file values
            self._update_nested_dict(self._config, file_config)
        
        except Exception as e:
            print(f"Error loading configuration from {file_path}: {str(e)}")
    
    def _load_from_env(self) -> None:
        """Load configuration overrides from environment variables."""
        prefix = "GCPAI_"  # GCP AI Agent prefix
        
        for env_key, env_value in os.environ.items():
            if env_key.startswith(prefix):
                # Convert environment variable name to config key path
                # e.g., GCPAI_API_TIMEOUT -> api.timeout
                key_path = env_key[len(prefix):].lower().replace('_', '.')
                self.set(key_path, self._convert_value(env_value))
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value in appropriate type
        """
        # Try to convert to appropriate type
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        elif value.lower() == 'null' or value.lower() == 'none':
            return None
        
        try:
            # Try to convert to int
            return int(value)
        except ValueError:
            pass
        
        try:
            # Try to convert to float
            return float(value)
        except ValueError:
            pass
        
        # Keep as string if no conversion applies
        return value
    
    def _update_nested_dict(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """
        Update nested dictionary recursively.
        
        Args:
            base_dict: Base dictionary to update
            update_dict: Dictionary with updates
        """
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._update_nested_dict(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Key path in dot notation (e.g., 'api.timeout')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Key path in dot notation (e.g., 'api.timeout')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        # Navigate to the nested dictionary
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get the full configuration as a dictionary.
        
        Returns:
            Full configuration dictionary
        """
        return self._config.copy()
    
    def save(self, file_path: Optional[str] = None) -> None:
        """
        Save current configuration to a file.
        
        Args:
            file_path: Path to save the configuration. If None, uses the original path.
        """
        save_path = file_path or self._config_path
        
        if not save_path:
            raise ValueError("No file path specified for saving configuration")
        
        try:
            ext = os.path.splitext(save_path)[1].lower()
            
            if ext == '.yaml' or ext == '.yml':
                with open(save_path, 'w') as f:
                    yaml.dump(self._config, f, default_flow_style=False)
            elif ext == '.json':
                with open(save_path, 'w') as f:
                    json.dump(self._config, f, indent=2)
            else:
                raise ValueError(f"Unsupported configuration file format: {ext}")
        
        except Exception as e:
            print(f"Error saving configuration to {save_path}: {str(e)}")


# Create a default instance for convenience
default_config = Config()

"""
Logger module for the GCP AI Agent Framework.

This module provides utilities for structured logging in GCP environments.
It supports both local logging and integration with Google Cloud Logging.

Example usage:
```python
# Get a logger
logger = get_logger("my_agent")

# Log messages at different levels
logger.info("Processing request", extra={"intent": "get_weather", "session_id": "123"})
logger.warning("Missing parameter", extra={"parameter": "location"})
logger.error("Error calling external API", extra={"api": "weather_api", "status_code": 500})

# Log exceptions
try:
    # Some code that might raise an exception
    result = api_client.get('/endpoint')
except Exception as e:
    logger.exception("Exception during API call", extra={"api": "example_api"})
```
"""

import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Try to import Google Cloud Logging, but provide fallbacks if not available
try:
    import google.cloud.logging
    from google.cloud.logging.handlers import CloudLoggingHandler
    from google.cloud.logging.handlers import setup_logging as setup_cloud_logging
    GCP_LOGGING_AVAILABLE = True
except ImportError:
    GCP_LOGGING_AVAILABLE = False

from ..config import default_config


class StructuredLogFormatter(logging.Formatter):
    """
    Formatter for structured logs in JSON format.
    
    This formatter outputs logs in a structured JSON format that is compatible
    with Google Cloud Logging and other log aggregation tools.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as a structured JSON object.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log message as JSON string
        """
        # Get the message
        if record.exc_info:
            # If there's an exception, include the traceback
            message = self.formatException(record.exc_info)
        else:
            message = record.getMessage()
        
        # Basic log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': message,
            'function': record.funcName,
            'module': record.module,
            'filename': record.filename,
            'lineno': record.lineno
        }
        
        # Add extra fields from kwargs
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        # Include all extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in log_entry and not key.startswith('_') and key != 'msg' and key != 'args':
                try:
                    # Try to serialize the value to JSON
                    json.dumps({key: value})
                    log_entry[key] = value
                except (TypeError, ValueError):
                    # If it can't be serialized, convert to string
                    log_entry[key] = str(value)
        
        return json.dumps(log_entry)


def setup_logging(log_level: str = 'INFO', use_cloud_logging: bool = None,
                project_id: Optional[str] = None) -> None:
    """
    Set up logging for the application.
    
    Args:
        log_level: Logging level
        use_cloud_logging: Whether to use Google Cloud Logging (if None, use config)
        project_id: Google Cloud project ID (if None, use config)
    """
    # Get configuration
    if use_cloud_logging is None:
        use_cloud_logging = default_config.get('logging.log_to_cloud', False)
    
    if project_id is None:
        project_id = default_config.get('gcp.project_id')
    
    # Convert log level string to logging level
    log_level_value = getattr(logging, log_level.upper(), logging.INFO)
    
    # Reset root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up root logger
    root_logger.setLevel(log_level_value)
    
    # Set up console logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredLogFormatter())
    root_logger.addHandler(console_handler)
    
    # Set up Google Cloud Logging if available and enabled
    if use_cloud_logging and GCP_LOGGING_AVAILABLE:
        try:
            # Initialize the logging client
            logging_client = google.cloud.logging.Client(project=project_id)
            
            # Create a cloud logging handler
            cloud_handler = CloudLoggingHandler(logging_client)
            
            # Add handler to the root logger
            root_logger.addHandler(cloud_handler)
            
            # Log that cloud logging is set up
            root_logger.info("Google Cloud Logging enabled")
        
        except Exception as e:
            # Fall back to console logging
            root_logger.warning(f"Failed to set up Google Cloud Logging: {str(e)}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Adapter for adding default context to logs.
    
    This adapter allows adding default fields to log records without
    having to specify them in every log call.
    """
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        """
        Initialize the adapter.
        
        Args:
            logger: Logger to adapt
            extra: Default fields to add to log records
        """
        super().__init__(logger, extra or {})
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process a log message, adding the extra context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments for the log call
            
        Returns:
            Tuple of (message, kwargs)
        """
        # Merge default extra fields with any extra fields in the kwargs
        if 'extra' in kwargs:
            kwargs['extra'] = {**self.extra, **kwargs['extra']}
        else:
            kwargs['extra'] = self.extra
        
        return msg, kwargs


def create_logger_with_context(name: str, context: Dict[str, Any]) -> logging.LoggerAdapter:
    """
    Create a logger with default context.
    
    Args:
        name: Logger name
        context: Default context fields for all log entries
        
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)

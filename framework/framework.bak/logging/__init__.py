"""
Logging module for the GCP AI Agent Framework.

This module provides utilities for logging and monitoring agent activities,
including integration with Google Cloud Logging, Error Reporting, and Monitoring.
It also provides utilities for creating structured logs and custom metrics.
"""

from .logger import get_logger, setup_logging
from .monitoring import create_metric, record_metric, record_latency

__all__ = [
    'get_logger',
    'setup_logging',
    'create_metric',
    'record_metric',
    'record_latency'
]

"""
Monitoring module for the GCP AI Agent Framework.

This module provides utilities for monitoring agent performance and behavior
using Google Cloud Monitoring (Cloud Operations Suite). It supports creating
custom metrics, recording metric values, and measuring latency.

It also provides fallbacks for local development environments where
Cloud Monitoring is not available.

Example usage:
```python
# Record a custom metric
record_metric("intent_triggered", 1, {"intent": "get_weather"})

# Measure and record function latency
@record_latency("api_call", {"service": "weather_api"})
def call_weather_api(location):
    # API call
    return result
```
"""

import functools
import logging
import time
from typing import Dict, Any, Optional, Union, Callable

# Try to import Google Cloud Monitoring, but provide fallbacks if not available
try:
    from google.cloud import monitoring_v3
    from google.api import metric_pb2, resource_pb2
    GCP_MONITORING_AVAILABLE = True
except ImportError:
    GCP_MONITORING_AVAILABLE = False

from ..config import default_config


# Create a logger for this module
logger = logging.getLogger("monitoring")


def create_metric(metric_type: str, metric_kind: str = 'GAUGE',
                value_type: str = 'INT64', description: str = '',
                project_id: Optional[str] = None) -> None:
    """
    Create a custom metric in Google Cloud Monitoring.
    
    Args:
        metric_type: Type of the metric (e.g., 'custom.googleapis.com/agent/requests')
        metric_kind: Kind of metric (GAUGE, DELTA, CUMULATIVE)
        value_type: Type of the value (INT64, DOUBLE, STRING, BOOL, DISTRIBUTION)
        description: Description of the metric
        project_id: Google Cloud project ID (if None, use config)
    """
    if not GCP_MONITORING_AVAILABLE:
        logger.warning("Google Cloud Monitoring not available, skipping metric creation")
        return
    
    # Get project ID from config if not provided
    if project_id is None:
        project_id = default_config.get('gcp.project_id')
    
    if not project_id:
        logger.warning("Project ID not specified, skipping metric creation")
        return
    
    try:
        # Create metric descriptor client
        client = monitoring_v3.MetricServiceClient()
        
        # Prepare project name
        project_name = f"projects/{project_id}"
        
        # Create metric descriptor
        descriptor = metric_pb2.MetricDescriptor()
        descriptor.type = metric_type
        descriptor.metric_kind = getattr(metric_pb2.MetricDescriptor.MetricKind, metric_kind)
        descriptor.value_type = getattr(metric_pb2.MetricDescriptor.ValueType, value_type)
        descriptor.description = description
        
        # Create the metric descriptor
        client.create_metric_descriptor(
            name=project_name,
            metric_descriptor=descriptor
        )
        
        logger.info(f"Created custom metric: {metric_type}")
    
    except Exception as e:
        logger.error(f"Failed to create metric: {str(e)}")


def record_metric(metric_type: str, value: Union[int, float, bool, str],
                labels: Optional[Dict[str, str]] = None,
                project_id: Optional[str] = None) -> None:
    """
    Record a metric value in Google Cloud Monitoring.
    
    Args:
        metric_type: Type of the metric (e.g., 'custom.googleapis.com/agent/requests')
        value: Value to record
        labels: Labels for the metric
        project_id: Google Cloud project ID (if None, use config)
    """
    if not GCP_MONITORING_AVAILABLE:
        # Log metric locally
        label_str = ", ".join(f"{k}={v}" for k, v in (labels or {}).items())
        logger.info(f"Local metric: {metric_type} = {value} {{{label_str}}}")
        return
    
    # Get project ID from config if not provided
    if project_id is None:
        project_id = default_config.get('gcp.project_id')
    
    if not project_id:
        logger.warning("Project ID not specified, skipping metric recording")
        return
    
    try:
        # Create metric client
        client = monitoring_v3.MetricServiceClient()
        
        # Prepare project name
        project_name = f"projects/{project_id}"
        
        # Prepare series
        series = monitoring_v3.TimeSeries()
        
        # Set metric type
        series.metric.type = metric_type
        
        # Set labels
        if labels:
            for key, value in labels.items():
                series.metric.labels[key] = value
        
        # Set resource type (global)
        series.resource.type = 'global'
        
        # Create a point
        point = series.points.add()
        
        # Set the time
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10**9)
        point.interval.end_time.seconds = seconds
        point.interval.end_time.nanos = nanos
        
        # Set the value
        if isinstance(value, bool):
            point.value.bool_value = value
        elif isinstance(value, int):
            point.value.int64_value = value
        elif isinstance(value, float):
            point.value.double_value = value
        elif isinstance(value, str):
            point.value.string_value = value
        
        # Record the metric
        client.create_time_series(
            name=project_name,
            time_series=[series]
        )
        
        logger.debug(f"Recorded metric: {metric_type} = {value}")
    
    except Exception as e:
        logger.error(f"Failed to record metric: {str(e)}")


def record_latency(metric_name: str, labels: Optional[Dict[str, str]] = None,
                 project_id: Optional[str] = None) -> Callable:
    """
    Decorator to record the latency of a function.
    
    Args:
        metric_name: Name of the metric (will be prefixed with 'custom.googleapis.com/agent/')
        labels: Labels for the metric
        project_id: Google Cloud project ID (if None, use config)
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Record start time
            start_time = time.time()
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Record success metric
                record_metric(
                    f"custom.googleapis.com/agent/{metric_name}/success",
                    1,
                    labels,
                    project_id
                )
                
                return result
            
            except Exception as e:
                # Record failure metric
                record_metric(
                    f"custom.googleapis.com/agent/{metric_name}/failure",
                    1,
                    labels,
                    project_id
                )
                
                # Re-raise the exception
                raise
            
            finally:
                # Record latency
                latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                record_metric(
                    f"custom.googleapis.com/agent/{metric_name}/latency",
                    latency,
                    labels,
                    project_id
                )
        
        return wrapper
    
    return decorator

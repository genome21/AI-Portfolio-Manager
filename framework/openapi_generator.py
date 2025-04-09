"""
OpenAPI Specification Generator

This module provides utilities for generating OpenAPI specification files that
can be used with Google's Agent Builder. It helps create consistent and valid
specifications for your agent's API.
"""

import yaml
import json
import os
from typing import Dict, Any, List, Optional, Union


def create_openapi_spec(
    title: str,
    description: str,
    version: str = "1.0.0",
    server_url: str = "https://example.com",
    paths: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a basic OpenAPI specification structure.
    
    Args:
        title: API title
        description: API description
        version: API version
        server_url: Server URL
        paths: API paths dictionary
        
    Returns:
        OpenAPI specification as a dictionary
    """
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "description": description,
            "version": version
        },
        "servers": [
            {
                "url": server_url,
                "description": f"{title} API endpoint"
            }
        ],
        "paths": paths or {}
    }
    
    return spec


def add_path(
    spec: Dict[str, Any],
    path: str,
    summary: str,
    description: str,
    operation_id: str,
    method: str = "get",
    parameters: Optional[List[Dict[str, Any]]] = None,
    request_body: Optional[Dict[str, Any]] = None,
    responses: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Add a path to an OpenAPI specification.
    
    Args:
        spec: OpenAPI specification dictionary
        path: API path (e.g., "/analyze_symbol")
        summary: Operation summary
        description: Operation description
        operation_id: Unique operation ID
        method: HTTP method (get, post, etc.)
        parameters: List of parameters
        request_body: Request body schema
        responses: Response schemas
        
    Returns:
        Updated OpenAPI specification
    """
    # Create path if it doesn't exist
    if path not in spec["paths"]:
        spec["paths"][path] = {}
    
    # Add method to path
    spec["paths"][path][method] = {
        "summary": summary,
        "description": description,
        "operationId": operation_id
    }
    
    # Add parameters if provided
    if parameters:
        spec["paths"][path][method]["parameters"] = parameters
    
    # Add request body if provided
    if request_body:
        spec["paths"][path][method]["requestBody"] = request_body
    
    # Add responses if provided
    if responses:
        spec["paths"][path][method]["responses"] = responses
    else:
        # Add default responses
        spec["paths"][path][method]["responses"] = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object"
                        }
                    }
                }
            },
            "400": {
                "description": "Bad request",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            },
            "500": {
                "description": "Internal server error",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {
                                    "type": "string"
                                }
                            }
                        }
                    }
                }
            }
        }
    
    return spec


def create_parameter(
    name: str,
    description: str,
    schema_type: str = "string",
    required: bool = False,
    location: str = "query",
    enum: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a parameter definition for an OpenAPI path.
    
    Args:
        name: Parameter name
        description: Parameter description
        schema_type: Parameter type (string, number, etc.)
        required: Whether the parameter is required
        location: Parameter location (query, path, etc.)
        enum: List of allowed values
        
    Returns:
        Parameter definition
    """
    param = {
        "name": name,
        "in": location,
        "description": description,
        "required": required,
        "schema": {
            "type": schema_type
        }
    }
    
    # Add enum if provided
    if enum:
        param["schema"]["enum"] = enum
    
    return param


def create_request_body(
    content_type: str = "application/json",
    schema: Dict[str, Any] = None,
    required: bool = True
) -> Dict[str, Any]:
    """
    Create a request body definition for an OpenAPI path.
    
    Args:
        content_type: Content type (application/json, etc.)
        schema: Request body schema
        required: Whether the request body is required
        
    Returns:
        Request body definition
    """
    return {
        "required": required,
        "content": {
            content_type: {
                "schema": schema or {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    }


def create_response(
    description: str,
    schema: Dict[str, Any] = None,
    content_type: str = "application/json"
) -> Dict[str, Any]:
    """
    Create a response definition for an OpenAPI path.
    
    Args:
        description: Response description
        schema: Response schema
        content_type: Content type
        
    Returns:
        Response definition
    """
    return {
        "description": description,
        "content": {
            content_type: {
                "schema": schema or {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    }


def save_openapi_spec(spec: Dict[str, Any], file_path: str, format: str = "yaml") -> str:
    """
    Save an OpenAPI specification to a file.
    
    Args:
        spec: OpenAPI specification dictionary
        file_path: Path to save the file
        format: File format (yaml or json)
        
    Returns:
        Path to the saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Save in the specified format
    if format.lower() == "yaml":
        with open(file_path, "w") as f:
            yaml.dump(spec, f, default_flow_style=False)
    else:
        with open(file_path, "w") as f:
            json.dump(spec, f, indent=2)
    
    return file_path

"""
Agent API Framework

This module provides a base framework for creating API handlers that can be 
integrated with Google's Agent Builder and DialogFlow. It includes utilities for:

1. Processing HTTP requests from Agent Builder
2. Routing to the appropriate handler functions
3. Formatting responses
4. Error handling

Based on the AI Portfolio Manager implementation pattern.
"""

import functions_framework
from flask import jsonify, Request
import json
import logging
from typing import Dict, Any, Callable, List, Optional


class AgentAPI:
    """
    Base class for creating an API that can be used with Agent Builder.
    
    This class provides a foundation for building API endpoints that can be
    integrated with Google's Agent Builder and DialogFlow.
    """
    
    def __init__(self, name: str):
        """
        Initialize the Agent API.
        
        Args:
            name: Name of the agent API (used for logging)
        """
        self.name = name
        self.handlers = {}
        self.logger = logging.getLogger(f"agent_api.{name}")
    
    def register_handler(self, path: str, handler: Callable):
        """
        Register a handler function for a specific API path.
        
        Args:
            path: API path/endpoint (e.g., 'analyze_symbol')
            handler: Handler function for this path
        """
        self.handlers[path] = handler
        self.logger.info(f"Registered handler for path: {path}")
    
    def handle_request(self, request: Request) -> Any:
        """
        Main entry point for handling API requests.
        
        Args:
            request: Flask request object from Cloud Functions
            
        Returns:
            Response for the API request
        """
        # Get the path from the request
        path = request.path.strip('/')
        
        # Route to the appropriate handler based on path
        if path in self.handlers:
            try:
                return self.handlers[path](request)
            except Exception as e:
                self.logger.error(f"Error in handler for {path}: {str(e)}")
                return jsonify({
                    'error': f"Error processing request: {str(e)}"
                }), 500
        else:
            # Default response for unknown paths
            return self.default_response(request)
    
    def default_response(self, request: Request) -> Any:
        """
        Default response handler for unknown paths.
        
        Args:
            request: Flask request object
            
        Returns:
            Default response (can be overridden by subclasses)
        """
        return jsonify({
            'name': f"{self.name} API",
            'version': '1.0.0',
            'endpoints': list(self.handlers.keys())
        })
    
    def create_cloud_function(self) -> Callable:
        """
        Create a Cloud Functions entry point function.
        
        Returns:
            Cloud Function handler
        """
        @functions_framework.http
        def cloud_function(request):
            return self.handle_request(request)
        
        return cloud_function


def validate_parameters(request: Request, required_params: List[str]) -> Optional[Dict[str, Any]]:
    """
    Validate that a request contains all required parameters.
    
    Args:
        request: Flask request object
        required_params: List of required parameter names
        
    Returns:
        Dictionary with error information if validation fails, None if successful
    """
    missing_params = []
    
    # Check if it's a GET request
    if request.method == 'GET':
        for param in required_params:
            if param not in request.args:
                missing_params.append(param)
        
        if missing_params:
            return {
                'error': f"Missing required parameters: {', '.join(missing_params)}"
            }
    
    # Check if it's a POST request with JSON body
    elif request.is_json:
        request_data = request.get_json()
        
        for param in required_params:
            if param not in request_data:
                missing_params.append(param)
        
        if missing_params:
            return {
                'error': f"Missing required parameters: {', '.join(missing_params)}"
            }
    
    # Not a valid request format
    else:
        return {
            'error': "Request must be either GET with query parameters or POST with JSON body"
        }
    
    # All required parameters are present
    return None


def create_error_response(message: str, status_code: int = 400) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    return jsonify({
        'error': message
    }), status_code


def create_success_response(data: Dict[str, Any]) -> Any:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        
    Returns:
        JSON response
    """
    return jsonify(data)

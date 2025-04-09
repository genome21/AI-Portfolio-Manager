"""
Exceptions module for the GCP AI Agent Framework.

This module defines custom exceptions used throughout the framework,
providing standardized error handling and messages.
"""

from typing import Optional, Dict, Any


class AgentFrameworkError(Exception):
    """Base exception for all GCP AI Agent Framework errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            code: Error code (for API responses)
            details: Additional details about the error
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ConfigError(AgentFrameworkError):
    """Exception raised for configuration-related errors."""
    pass


class ServiceError(AgentFrameworkError):
    """Exception raised for service-related errors."""
    pass


class DialogFlowError(AgentFrameworkError):
    """Exception raised for DialogFlow-related errors."""
    pass


class IntentHandlerError(AgentFrameworkError):
    """Exception raised for intent handler-related errors."""
    pass


class ValidationError(AgentFrameworkError):
    """Exception raised for validation errors."""
    pass


class APIError(AgentFrameworkError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the API exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            code: Error code
            details: Additional details about the error
        """
        self.status_code = status_code
        super().__init__(message, code, details)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary for API responses.
        
        Returns:
            Dictionary representation of the error
        """
        error_dict = {
            'error': {
                'message': self.message,
                'status_code': self.status_code
            }
        }
        
        if self.code:
            error_dict['error']['code'] = self.code
        
        if self.details:
            error_dict['error']['details'] = self.details
        
        return error_dict


class AuthenticationError(APIError):
    """Exception raised for authentication-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the authentication exception.
        
        Args:
            message: Error message
            code: Error code
            details: Additional details about the error
        """
        super().__init__(message, 401, code, details)


class AuthorizationError(APIError):
    """Exception raised for authorization-related errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the authorization exception.
        
        Args:
            message: Error message
            code: Error code
            details: Additional details about the error
        """
        super().__init__(message, 403, code, details)


class ExternalServiceError(ServiceError):
    """Exception raised for external service-related errors."""
    
    def __init__(self, service_name: str, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the external service exception.
        
        Args:
            service_name: Name of the external service
            message: Error message
            code: Error code
            details: Additional details about the error
        """
        self.service_name = service_name
        super().__init__(f"{service_name} error: {message}", code, details)

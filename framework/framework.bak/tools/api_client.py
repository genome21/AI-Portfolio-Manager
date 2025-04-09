"""
API Client module for the GCP AI Agent Framework.

This module provides a flexible API client for making HTTP requests to external
services and APIs. It includes support for authentication, request customization,
response parsing, and error handling.

Example usage:
```python
# Create an API client
client = APIClient("https://api.example.com", timeout=30)

# Add authentication
client.set_auth_header("Authorization", "Bearer YOUR_TOKEN")

# Make a request
response = client.get("/users", params={"limit": 10})

# Parse JSON response
data = response.json()
```
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Union, List, Tuple, Callable
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from ..config import default_config
from ..exceptions import ServiceError, ExternalServiceError


class APIResponse:
    """
    Wrapper for API responses.
    
    This class provides a consistent interface for handling API responses,
    regardless of the underlying HTTP library used.
    """
    
    def __init__(self, response: requests.Response):
        """
        Initialize the API response.
        
        Args:
            response: Requests library response object
        """
        self.response = response
        self.status_code = response.status_code
        self.headers = response.headers
        self.content = response.content
        self.text = response.text
        self._json = None
    
    def json(self) -> Dict[str, Any]:
        """
        Parse the response body as JSON.
        
        Returns:
            Parsed JSON data
            
        Raises:
            ValueError: If response body is not valid JSON
        """
        if self._json is None:
            try:
                self._json = self.response.json()
            except ValueError as e:
                raise ValueError(f"Failed to parse response as JSON: {str(e)}")
        
        return self._json
    
    def is_success(self) -> bool:
        """
        Check if the response indicates a successful request.
        
        Returns:
            True if status code is 2xx, False otherwise
        """
        return 200 <= self.status_code < 300
    
    def __str__(self) -> str:
        """
        Convert to a string representation.
        
        Returns:
            String representation of the response
        """
        return f"APIResponse(status_code={self.status_code}, content_length={len(self.content)})"


class APIClient:
    """
    HTTP client for making API requests.
    
    This class provides a flexible and reusable HTTP client for making
    requests to external APIs and services.
    """
    
    def __init__(self, base_url: str, timeout: int = 30, 
               max_retries: int = 3, logger: Optional[logging.Logger] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
            logger: Logger instance (creates a new one if None)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger or logging.getLogger("api_client")
        
        # Default headers
        self.default_headers = {
            'User-Agent': f"GCP-AI-Agent-Framework/{default_config.get('app.version')}",
            'Accept': 'application/json',
        }
        
        # Authentication headers
        self.auth_headers = {}
        
        # Create a requests session for connection pooling
        self.session = requests.Session()
        
        # Install a retry adapter
        self._configure_session()
    
    def _configure_session(self) -> None:
        """Configure the requests session with retries and other settings."""
        # Set default timeout for all requests
        self.session.request = lambda method, url, **kwargs: \
            super(requests.Session, self.session).request(
                method=method, url=url, timeout=self.timeout, **kwargs)
    
    def set_auth_header(self, header_name: str, header_value: str) -> None:
        """
        Set an authentication header.
        
        Args:
            header_name: Header name (e.g., 'Authorization')
            header_value: Header value (e.g., 'Bearer token123')
        """
        self.auth_headers[header_name] = header_value
    
    def clear_auth_headers(self) -> None:
        """Clear all authentication headers."""
        self.auth_headers = {}
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Prepare request headers by combining default, auth, and custom headers.
        
        Args:
            headers: Custom headers for the request
            
        Returns:
            Combined headers
        """
        # Start with default headers
        combined_headers = self.default_headers.copy()
        
        # Add authentication headers
        combined_headers.update(self.auth_headers)
        
        # Add custom headers
        if headers:
            combined_headers.update(headers)
        
        return combined_headers
    
    def _prepare_url(self, endpoint: str) -> str:
        """
        Prepare the full request URL.
        
        Args:
            endpoint: API endpoint (e.g., '/users')
            
        Returns:
            Full request URL
        """
        # Make sure the endpoint doesn't start with the base URL
        if endpoint.startswith(self.base_url):
            return endpoint
        
        # Join the base URL and endpoint
        return urljoin(self.base_url, endpoint.lstrip('/'))
    
    def _make_request(self, method: str, endpoint: str, 
                    headers: Optional[Dict[str, str]] = None,
                    params: Optional[Dict[str, Any]] = None,
                    data: Optional[Any] = None,
                    json_data: Optional[Dict[str, Any]] = None,
                    files: Optional[Dict[str, Any]] = None,
                    timeout: Optional[int] = None,
                    retry_codes: Optional[List[int]] = None) -> APIResponse:
        """
        Make an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            headers: Custom headers
            params: Query parameters
            data: Request body (for form data)
            json_data: Request body (for JSON data)
            files: Files to upload
            timeout: Request timeout (overrides default)
            retry_codes: Status codes to retry on
            
        Returns:
            API response
            
        Raises:
            ExternalServiceError: If the request fails
        """
        # Prepare request parameters
        url = self._prepare_url(endpoint)
        headers = self._prepare_headers(headers)
        timeout = timeout or self.timeout
        retry_codes = retry_codes or [429, 500, 502, 503, 504]
        
        # Debug logging
        self.logger.debug(f"Making {method} request to {url}")
        
        # Retry logic
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # Make the request
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_data,
                    files=files,
                    timeout=timeout
                )
                
                # Log response info
                self.logger.debug(f"Received response: {response.status_code}")
                
                # Check if we should retry based on status code
                if response.status_code in retry_codes and retries < self.max_retries:
                    # Exponential backoff
                    sleep_time = (2 ** retries) * 0.1
                    self.logger.warning(
                        f"Request failed with status {response.status_code}, "
                        f"retrying in {sleep_time:.2f} seconds (attempt {retries+1}/{self.max_retries})"
                    )
                    time.sleep(sleep_time)
                    retries += 1
                    continue
                
                # Return the response
                return APIResponse(response)
                
            except (ConnectionError, Timeout) as e:
                # Connection or timeout error
                last_error = e
                if retries < self.max_retries:
                    # Exponential backoff
                    sleep_time = (2 ** retries) * 0.1
                    self.logger.warning(
                        f"Request failed with error: {str(e)}, "
                        f"retrying in {sleep_time:.2f} seconds (attempt {retries+1}/{self.max_retries})"
                    )
                    time.sleep(sleep_time)
                    retries += 1
                else:
                    # Maximum retries reached
                    self.logger.error(f"Maximum retries reached, last error: {str(e)}")
                    raise ExternalServiceError(
                        service_name=self.base_url,
                        message=f"Request failed after {self.max_retries} retries: {str(e)}"
                    )
            
            except RequestException as e:
                # Other request error
                self.logger.error(f"Request error: {str(e)}")
                raise ExternalServiceError(
                    service_name=self.base_url,
                    message=f"Request error: {str(e)}"
                )
        
        # This should never happen, but just in case
        if last_error:
            raise ExternalServiceError(
                service_name=self.base_url,
                message=f"Request failed after {self.max_retries} retries: {str(last_error)}"
            )
        
        raise ExternalServiceError(
            service_name=self.base_url,
            message=f"Request failed for unknown reason"
        )
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        return self._make_request('GET', endpoint, headers=headers, params=params, timeout=timeout)
    
    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None,
           data: Optional[Any] = None, params: Optional[Dict[str, Any]] = None,
           headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON data for request body
            data: Form data for request body
            params: Query parameters
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        return self._make_request('POST', endpoint, headers=headers, params=params,
                               json_data=json_data, data=data, timeout=timeout)
    
    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None,
          data: Optional[Any] = None, params: Optional[Dict[str, Any]] = None,
          headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON data for request body
            data: Form data for request body
            params: Query parameters
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        return self._make_request('PUT', endpoint, headers=headers, params=params,
                               json_data=json_data, data=data, timeout=timeout)
    
    def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None,
            data: Optional[Any] = None, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """
        Make a PATCH request.
        
        Args:
            endpoint: API endpoint
            json_data: JSON data for request body
            data: Form data for request body
            params: Query parameters
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        return self._make_request('PATCH', endpoint, headers=headers, params=params,
                               json_data=json_data, data=data, timeout=timeout)
    
    def delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None, timeout: Optional[int] = None) -> APIResponse:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        return self._make_request('DELETE', endpoint, headers=headers, params=params, timeout=timeout)
    
    def upload_file(self, endpoint: str, file_path: str, file_key: str = 'file',
                  params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
                  timeout: Optional[int] = None) -> APIResponse:
        """
        Upload a file using a multipart/form-data POST request.
        
        Args:
            endpoint: API endpoint
            file_path: Path to the file to upload
            file_key: Form field name for the file
            params: Additional form data
            headers: Custom headers
            timeout: Request timeout
            
        Returns:
            API response
        """
        with open(file_path, 'rb') as f:
            files = {file_key: f}
            return self._make_request('POST', endpoint, headers=headers, params=params,
                                   files=files, timeout=timeout)

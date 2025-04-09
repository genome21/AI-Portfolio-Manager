"""
Webhook module for the GCP AI Agent Framework.

This module provides the WebhookHandler class for handling webhook requests from
DialogFlow Conversational Agents. This is the main entry point for Cloud Functions
that integrate with DialogFlow through webhooks.

Implementation Guide:
1. Create a subclass of WebhookHandler or use the default implementation
2. Register intent handlers using the intent registry
3. Deploy as a Cloud Function using the handle_request method as the entry point
"""

import json
import logging
import traceback
from typing import Dict, Any, Optional, Union, Callable

import functions_framework
from flask import Request, jsonify

from .agent import Agent, AgentRequest, AgentResponse
from .intent import IntentRegistry, IntentHandler
from ..exceptions import AgentFrameworkError, ValidationError


class WebhookHandler:
    """
    Handles webhook requests from DialogFlow.
    
    This class provides methods for parsing DialogFlow webhook requests,
    dispatching to appropriate intent handlers, and formatting responses.
    
    Typical usage:
    
    ```python
    # Create a webhook handler
    webhook = WebhookHandler("my-agent")
    
    # Register intent handlers
    webhook.registry.register(MyIntentHandler("my-intent"))
    
    # Create a Cloud Function
    @functions_framework.http
    def cloud_function_entry_point(request):
        return webhook.handle_request(request)
    ```
    """
    
    def __init__(self, agent_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the webhook handler.
        
        Args:
            agent_name: Name of the agent
            logger: Logger instance (creates a new one if None)
        """
        # Initialize the agent and intent registry
        self.agent = Agent(agent_name, logger)
        self.registry = IntentRegistry(logger)
        self.logger = logger or logging.getLogger(f"webhook.{agent_name}")
    
    def parse_request(self, request: Request) -> Dict[str, Any]:
        """
        Parse the webhook request.
        
        Args:
            request: Flask request object from Cloud Functions
            
        Returns:
            DialogFlow webhook request JSON
            
        Raises:
            ValidationError: If request is missing required fields
        """
        # Try to parse the request body as JSON
        if request.is_json:
            request_json = request.get_json(silent=True)
        else:
            # Try to parse the request data as JSON
            try:
                request_json = json.loads(request.data.decode('utf-8'))
            except json.JSONDecodeError:
                raise ValidationError("Request body is not valid JSON")
        
        # Validate the request
        if not request_json:
            raise ValidationError("Request body is empty")
        
        # Log the request for debugging
        self.logger.debug(f"Received webhook request: {json.dumps(request_json)}")
        
        return request_json
    
    def dispatch_request(self, request_json: Dict[str, Any]) -> AgentResponse:
        """
        Dispatch the request to the appropriate intent handler.
        
        Args:
            request_json: DialogFlow webhook request JSON
            
        Returns:
            Agent response
        """
        # Convert to AgentRequest
        agent_request = AgentRequest.from_dialogflow_request(request_json)
        
        # Log the intent being processed
        self.logger.info(f"Processing intent: {agent_request.intent_name}")
        
        # Dispatch to the registry
        return self.registry.dispatch(agent_request)
    
    def format_response(self, response: AgentResponse) -> Dict[str, Any]:
        """
        Format the agent response as a DialogFlow webhook response.
        
        Args:
            response: Agent response
            
        Returns:
            DialogFlow webhook response JSON
        """
        # Convert to DialogFlow response format
        return response.to_dialogflow_response()
    
    def handle_request(self, request: Request) -> Dict[str, Any]:
        """
        Handle a webhook request from DialogFlow.
        
        This is the main entry point for Cloud Functions that integrate with DialogFlow.
        
        Args:
            request: Flask request object from Cloud Functions
            
        Returns:
            DialogFlow webhook response JSON
        """
        try:
            # Parse the request
            request_json = self.parse_request(request)
            
            # Dispatch to the appropriate intent handler
            response = self.dispatch_request(request_json)
            
            # Format the response
            return jsonify(self.format_response(response))
        
        except ValidationError as e:
            # Handle validation errors
            self.logger.error(f"Validation error: {str(e)}")
            return jsonify({
                'fulfillmentText': f"Sorry, I couldn't understand your request: {str(e)}"
            })
        
        except AgentFrameworkError as e:
            # Handle framework errors
            self.logger.error(f"Agent framework error: {str(e)}")
            return jsonify({
                'fulfillmentText': f"Sorry, I encountered an error processing your request: {str(e)}"
            })
        
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.error(traceback.format_exc())
            return jsonify({
                'fulfillmentText': "Sorry, I encountered an unexpected error. Please try again later."
            })
    
    # Convenience methods for registering handlers
    
    def register_handler(self, handler: IntentHandler) -> None:
        """
        Register an intent handler.
        
        Args:
            handler: Intent handler to register
        """
        self.registry.register(handler)
    
    def register_function(self, intent_name: str) -> Callable[[Callable], Callable]:
        """
        Decorator for registering a function as an intent handler.
        
        Args:
            intent_name: Intent name
            
        Returns:
            Decorator function
            
        Example:
        ```python
        webhook = WebhookHandler("my-agent")
        
        @webhook.register_function("my-intent")
        def handle_my_intent(request):
            return AgentResponse(
                fulfillment_text="Hello from my intent!"
            )
        ```
        """
        def decorator(func):
            self.registry.register_function(func, intent_name)
            return func
        return decorator
    
    def fallback(self) -> Callable[[Callable], Callable]:
        """
        Decorator for registering a fallback handler.
        
        Returns:
            Decorator function
            
        Example:
        ```python
        webhook = WebhookHandler("my-agent")
        
        @webhook.fallback()
        def handle_fallback(request):
            return AgentResponse(
                fulfillment_text="I'm not sure how to handle that."
            )
        ```
        """
        def decorator(func):
            self.registry.set_fallback_handler(func)
            return func
        return decorator
    
    def default(self) -> Callable[[Callable], Callable]:
        """
        Decorator for registering a default handler.
        
        Returns:
            Decorator function
            
        Example:
        ```python
        webhook = WebhookHandler("my-agent")
        
        @webhook.default()
        def handle_default(request):
            return AgentResponse(
                fulfillment_text="How can I help you?"
            )
        ```
        """
        def decorator(func):
            self.registry.set_default_handler(func)
            return func
        return decorator

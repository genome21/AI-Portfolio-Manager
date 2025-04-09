"""
Intent module for the GCP AI Agent Framework.

This module provides classes and utilities for managing intents and intent handlers
for DialogFlow Conversational Agents.
"""

import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Type, Callable, Set, Union

from .agent import AgentRequest, AgentResponse
from ..exceptions import IntentHandlerError


@dataclass
class Intent:
    """
    Represents a DialogFlow intent.
    
    This class encapsulates information about a specific intent in DialogFlow.
    """
    
    name: str
    display_name: str
    description: Optional[str] = None
    training_phrases: List[str] = None
    parameters: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values after initialization."""
        if self.training_phrases is None:
            self.training_phrases = []
        
        if self.parameters is None:
            self.parameters = []


class IntentHandler(ABC):
    """
    Abstract base class for intent handlers.
    
    Intent handlers are responsible for processing specific intents
    and generating appropriate responses.
    """
    
    def __init__(self, intent_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the intent handler.
        
        Args:
            intent_name: Name of the intent this handler processes
            logger: Logger instance (creates a new one if None)
        """
        self.intent_name = intent_name
        self.logger = logger or logging.getLogger(f"intent.{intent_name}")
    
    @abstractmethod
    def handle(self, request: AgentRequest) -> AgentResponse:
        """
        Handle the intent request.
        
        Args:
            request: Agent request containing intent information
            
        Returns:
            Agent response
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any], required_params: List[str]) -> List[str]:
        """
        Validate that required parameters are present.
        
        Args:
            parameters: Parameters from the request
            required_params: List of required parameter names
            
        Returns:
            List of missing parameter names (empty if all required parameters are present)
        """
        missing_params = []
        
        for param in required_params:
            if param not in parameters or not parameters[param]:
                missing_params.append(param)
        
        return missing_params
    
    def extract_parameter(self, parameters: Dict[str, Any], param_name: str, 
                         default: Any = None, required: bool = False) -> Any:
        """
        Extract a parameter from the request parameters.
        
        Args:
            parameters: Parameters from the request
            param_name: Name of the parameter to extract
            default: Default value if parameter is not present
            required: Whether the parameter is required
            
        Returns:
            Parameter value or default
            
        Raises:
            IntentHandlerError: If parameter is required but not present
        """
        value = parameters.get(param_name, default)
        
        if required and (value is None or value == ''):
            raise IntentHandlerError(f"Required parameter '{param_name}' is missing")
        
        return value


class IntentRegistry:
    """
    Registry for intent handlers.
    
    This class provides a centralized registry for intent handlers and
    facilitates dispatching requests to the appropriate handler.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the intent registry.
        
        Args:
            logger: Logger instance (creates a new one if None)
        """
        self.handlers: Dict[str, IntentHandler] = {}
        self.logger = logger or logging.getLogger("intent_registry")
        self._fallback_handler: Optional[IntentHandler] = None
        self._default_handler: Optional[IntentHandler] = None
    
    def register(self, handler: IntentHandler) -> None:
        """
        Register an intent handler.
        
        Args:
            handler: Intent handler to register
        """
        self.handlers[handler.intent_name] = handler
        self.logger.debug(f"Registered handler for intent: {handler.intent_name}")
    
    def register_class(self, handler_class: Type[IntentHandler], intent_name: Optional[str] = None) -> None:
        """
        Register a handler class.
        
        Args:
            handler_class: Intent handler class to register
            intent_name: Intent name (uses class name if None)
        """
        # If intent_name not provided, use class name
        if intent_name is None:
            class_name = handler_class.__name__
            intent_name = class_name[:-7] if class_name.endswith('Handler') else class_name
        
        # Create instance and register
        handler = handler_class(intent_name)
        self.register(handler)
    
    def register_function(self, func: Callable[[AgentRequest], AgentResponse], intent_name: str) -> None:
        """
        Register a function as an intent handler.
        
        Args:
            func: Function that handles the intent
            intent_name: Intent name
        """
        # Create a function-based handler
        class FunctionHandler(IntentHandler):
            def handle(self, request: AgentRequest) -> AgentResponse:
                return func(request)
        
        # Register the handler
        handler = FunctionHandler(intent_name)
        self.register(handler)
    
    def set_fallback_handler(self, handler: Union[IntentHandler, Callable[[AgentRequest], AgentResponse]]) -> None:
        """
        Set the fallback handler for unrecognized intents.
        
        Args:
            handler: Fallback handler (IntentHandler instance or function)
        """
        if callable(handler) and not isinstance(handler, IntentHandler):
            # Create a function-based handler
            class FallbackHandler(IntentHandler):
                def handle(self, request: AgentRequest) -> AgentResponse:
                    return handler(request)
            
            self._fallback_handler = FallbackHandler("fallback")
        else:
            self._fallback_handler = handler
    
    def set_default_handler(self, handler: Union[IntentHandler, Callable[[AgentRequest], AgentResponse]]) -> None:
        """
        Set the default handler for when no intent is matched.
        
        Args:
            handler: Default handler (IntentHandler instance or function)
        """
        if callable(handler) and not isinstance(handler, IntentHandler):
            # Create a function-based handler
            class DefaultHandler(IntentHandler):
                def handle(self, request: AgentRequest) -> AgentResponse:
                    return handler(request)
            
            self._default_handler = DefaultHandler("default")
        else:
            self._default_handler = handler
    
    def get_handler(self, intent_name: str) -> Optional[IntentHandler]:
        """
        Get the handler for a specific intent.
        
        Args:
            intent_name: Intent name
            
        Returns:
            Intent handler or None if not found
        """
        return self.handlers.get(intent_name)
    
    def dispatch(self, request: AgentRequest) -> AgentResponse:
        """
        Dispatch a request to the appropriate handler.
        
        Args:
            request: Agent request containing intent information
            
        Returns:
            Agent response
        """
        intent_name = request.intent_name
        
        # Log the intent being processed
        self.logger.info(f"Processing intent: {intent_name}")
        
        # Default case - no intent specified
        if not intent_name and self._default_handler:
            self.logger.debug("No intent specified, using default handler")
            return self._default_handler.handle(request)
        
        # Try to find a handler for the intent
        handler = self.get_handler(intent_name)
        
        if handler:
            self.logger.debug(f"Found handler for intent: {intent_name}")
            try:
                return handler.handle(request)
            except Exception as e:
                self.logger.error(f"Error handling intent {intent_name}: {str(e)}")
                return AgentResponse(
                    fulfillment_text=f"Sorry, I encountered an error processing your request: {str(e)}"
                )
        
        # Use fallback handler if available
        if self._fallback_handler:
            self.logger.debug(f"No handler found for intent: {intent_name}, using fallback handler")
            return self._fallback_handler.handle(request)
        
        # No handler found
        self.logger.warning(f"No handler found for intent: {intent_name}")
        return AgentResponse(
            fulfillment_text=f"Sorry, I don't know how to handle the intent: {intent_name}"
        )
    
    def get_registered_intents(self) -> Set[str]:
        """
        Get the set of registered intent names.
        
        Returns:
            Set of registered intent names
        """
        return set(self.handlers.keys())
    
    def auto_register_handlers(self, module, base_class: Type[IntentHandler] = IntentHandler) -> None:
        """
        Automatically register handlers from a module.
        
        Args:
            module: Module containing handler classes
            base_class: Base class for handlers (default: IntentHandler)
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and issubclass(obj, base_class) and 
                obj != base_class and not inspect.isabstract(obj)):
                intent_name = name[:-7] if name.endswith('Handler') else name
                self.register_class(obj, intent_name)

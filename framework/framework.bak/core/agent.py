"""
Agent module for the GCP AI Agent Framework.

This module provides the core Agent class and related utilities for
managing conversational AI agents.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from ..config import default_config


@dataclass
class AgentRequest:
    """
    Represents a request to the agent from DialogFlow.
    
    This class encapsulates all the information contained in a webhook request
    from DialogFlow Conversational Agents.
    """
    
    session_id: str
    intent_name: str
    parameters: Dict[str, Any]
    query_text: str
    language_code: str
    fulfillment_text: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dialogflow_request(cls, request_json: Dict[str, Any]) -> 'AgentRequest':
        """
        Create an AgentRequest from a DialogFlow webhook request.
        
        Args:
            request_json: DialogFlow webhook request JSON
            
        Returns:
            AgentRequest instance
        """
        # Extract session ID
        session = request_json.get('session', '')
        session_id = session.split('/')[-1] if session else ''
        
        # Extract intent information
        query_result = request_json.get('queryResult', {})
        intent = query_result.get('intent', {})
        intent_name = intent.get('displayName', '')
        
        # Extract parameters
        parameters = query_result.get('parameters', {})
        
        # Extract query text
        query_text = query_result.get('queryText', '')
        
        # Extract language code
        language_code = query_result.get('languageCode', 'en')
        
        # Extract fulfillment text
        fulfillment_text = query_result.get('fulfillmentText', '')
        
        return cls(
            session_id=session_id,
            intent_name=intent_name,
            parameters=parameters,
            query_text=query_text,
            language_code=language_code,
            fulfillment_text=fulfillment_text,
            payload=request_json
        )


@dataclass
class AgentResponse:
    """
    Represents a response from the agent to DialogFlow.
    
    This class encapsulates all the information needed to respond to a webhook request
    from DialogFlow Conversational Agents.
    """
    
    fulfillment_text: str
    payload: Optional[Dict[str, Any]] = None
    output_contexts: List[Dict[str, Any]] = field(default_factory=list)
    followup_event: Optional[Dict[str, Any]] = None
    session_info: Optional[Dict[str, Any]] = None
    
    def to_dialogflow_response(self) -> Dict[str, Any]:
        """
        Convert to a DialogFlow webhook response.
        
        Returns:
            DialogFlow webhook response JSON
        """
        response = {
            'fulfillmentText': self.fulfillment_text
        }
        
        # Add payload if present
        if self.payload:
            response['payload'] = self.payload
        
        # Add output contexts if present
        if self.output_contexts:
            response['outputContexts'] = self.output_contexts
        
        # Add followup event if present
        if self.followup_event:
            response['followupEventInput'] = self.followup_event
        
        # Add session info if present
        if self.session_info:
            response['sessionInfo'] = self.session_info
        
        return response
    
    def __str__(self) -> str:
        """
        Convert to a string representation.
        
        Returns:
            String representation of the response
        """
        return json.dumps(self.to_dialogflow_response(), indent=2)


class Agent:
    """
    Core agent class for managing conversational AI agents.
    
    This class provides utilities for working with DialogFlow agents and handling
    webhook requests and responses.
    """
    
    def __init__(self, name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize the agent.
        
        Args:
            name: Agent name
            logger: Logger instance (creates a new one if None)
        """
        self.name = name
        self.logger = logger or logging.getLogger(name)
        self.config = default_config
        
        # Set up logging
        log_level = getattr(logging, self.config.get('logging.level', 'INFO'))
        self.logger.setLevel(log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.config.get('logging.format'))
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def process_request(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request to the agent.
        
        This method should be overridden by subclasses to implement
        custom processing logic.
        
        Args:
            request: Agent request
            
        Returns:
            Agent response
        """
        # Default implementation - return a simple response
        return AgentResponse(
            fulfillment_text=f"Agent {self.name} received request for intent {request.intent_name}."
        )
    
    def create_context(self, session_id: str, context_name: str, 
                     lifespan_count: int = 5, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an output context for DialogFlow.
        
        Args:
            session_id: DialogFlow session ID
            context_name: Context name
            lifespan_count: Context lifespan (number of turns)
            parameters: Context parameters
            
        Returns:
            DialogFlow output context
        """
        # Format context name to match DialogFlow expectations
        if not context_name.startswith('projects/'):
            # Ensure context name is fully qualified
            project_id = self.config.get('gcp.project_id')
            location = self.config.get('gcp.region', 'global')
            agent_id = self.config.get('agent.name', 'default_agent')
            
            context_name = f"projects/{project_id}/locations/{location}/agents/{agent_id}/sessions/{session_id}/contexts/{context_name}"
        
        context = {
            'name': context_name,
            'lifespanCount': lifespan_count
        }
        
        if parameters:
            context['parameters'] = parameters
        
        return context
    
    def create_followup_event(self, event_name: str, parameters: Optional[Dict[str, Any]] = None,
                            language_code: str = 'en') -> Dict[str, Any]:
        """
        Create a followup event for DialogFlow.
        
        Args:
            event_name: Event name
            parameters: Event parameters
            language_code: Language code
            
        Returns:
            DialogFlow followup event
        """
        event = {
            'name': event_name,
            'languageCode': language_code
        }
        
        if parameters:
            event['parameters'] = parameters
        
        return event

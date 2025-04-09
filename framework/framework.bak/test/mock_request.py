"""
Mock Request module for the GCP AI Agent Framework.

This module provides utilities for creating mock webhook requests that simulate
requests from DialogFlow for testing purposes. This makes it easier to test
intent handlers and agent logic without having to deploy to a live environment.

Example usage:
```python
# Create a mock intent request
mock_request = create_mock_intent_request(
    intent_name="get_weather",
    parameters={"location": "Seattle", "date": "2023-04-15"},
    session_id="test-session-123"
)

# Test an intent handler
handler = WeatherIntentHandler("get_weather")
response = handler.handle(AgentRequest.from_dialogflow_request(mock_request))

# Assert on the response
assert "Seattle" in response.fulfillment_text
```
"""

import json
import uuid
from typing import Dict, Any, Optional, List


def create_mock_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a mock Flask request with the given body.
    
    Args:
        body: Request body
        
    Returns:
        Mock request dictionary that can be passed to WebhookHandler.handle_request
    """
    return {
        "json": body,
        "get_json": lambda silent=False: body,
        "is_json": True,
        "data": json.dumps(body).encode('utf-8')
    }


def create_mock_intent_request(intent_name: str, parameters: Optional[Dict[str, Any]] = None,
                            session_id: Optional[str] = None, language_code: str = "en",
                            query_text: Optional[str] = None,
                            contexts: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Create a mock DialogFlow intent request.
    
    Args:
        intent_name: Name of the intent
        parameters: Intent parameters
        session_id: Session ID (generated if None)
        language_code: Language code
        query_text: Query text (uses intent name if None)
        contexts: Output contexts
        
    Returns:
        Mock DialogFlow webhook request JSON
    """
    # Generate a session ID if none provided
    if not session_id:
        session_id = f"test-session-{uuid.uuid4()}"
    
    # Use intent name for query text if none provided
    if not query_text:
        query_text = f"Trigger {intent_name} intent"
    
    # Create the request structure
    request = {
        "responseId": f"response-{uuid.uuid4()}",
        "session": f"projects/test-project/agent/sessions/{session_id}",
        "queryResult": {
            "queryText": query_text,
            "action": intent_name,
            "parameters": parameters or {},
            "allRequiredParamsPresent": True,
            "fulfillmentText": "",
            "fulfillmentMessages": [],
            "outputContexts": contexts or [],
            "intent": {
                "name": f"projects/test-project/agent/intents/{uuid.uuid4()}",
                "displayName": intent_name
            },
            "intentDetectionConfidence": 1.0,
            "languageCode": language_code
        },
        "originalDetectIntentRequest": {
            "source": "test",
            "payload": {}
        }
    }
    
    return request


def create_empty_event_request(event_name: str, parameters: Optional[Dict[str, Any]] = None,
                             session_id: Optional[str] = None, language_code: str = "en") -> Dict[str, Any]:
    """
    Create a mock DialogFlow event request with no detected intent.
    
    Args:
        event_name: Name of the event
        parameters: Event parameters
        session_id: Session ID (generated if None)
        language_code: Language code
        
    Returns:
        Mock DialogFlow webhook request JSON
    """
    # Generate a session ID if none provided
    if not session_id:
        session_id = f"test-session-{uuid.uuid4()}"
    
    # Create the request structure
    request = {
        "responseId": f"response-{uuid.uuid4()}",
        "session": f"projects/test-project/agent/sessions/{session_id}",
        "queryResult": {
            "queryText": "",
            "parameters": parameters or {},
            "allRequiredParamsPresent": True,
            "fulfillmentText": "",
            "fulfillmentMessages": [],
            "outputContexts": [],
            "languageCode": language_code
        },
        "originalDetectIntentRequest": {
            "source": "test",
            "payload": {}
        }
    }
    
    return request


def create_mock_context(name: str, lifespan_count: int = 5, 
                      parameters: Optional[Dict[str, Any]] = None, 
                      session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a mock DialogFlow context.
    
    Args:
        name: Context name
        lifespan_count: Context lifespan
        parameters: Context parameters
        session_id: Session ID (generated if None)
        
    Returns:
        Mock DialogFlow context
    """
    # Generate a session ID if none provided
    if not session_id:
        session_id = f"test-session-{uuid.uuid4()}"
    
    # Format the context name
    context_name = f"projects/test-project/agent/sessions/{session_id}/contexts/{name}"
    
    # Create the context
    context = {
        "name": context_name,
        "lifespanCount": lifespan_count
    }
    
    if parameters:
        context["parameters"] = parameters
    
    return context

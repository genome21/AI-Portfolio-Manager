"""
Test Validators module for the GCP AI Agent Framework.

This module provides utilities for validating agent responses in tests.
It includes functions for checking response structure, content, contexts,
and other aspects of agent behavior.

Example usage:
```python
# Validate a response
validation_errors = validate_response(
    response,
    expected_text="Hello, world!",
    expected_contexts=["greeting_context"],
    expected_payload_keys=["richContent"]
)

# Assert no validation errors
assert not validation_errors, f"Validation errors: {validation_errors}"

# Assert that a specific context exists
assert_contains_context(response, "user_info", {"name": "John"})
```
"""

from typing import Dict, Any, List, Optional, Union, Set
import re

from ..core.agent import AgentResponse


def validate_response(response: AgentResponse, expected_text: Optional[str] = None,
                    text_contains: Optional[List[str]] = None,
                    expected_contexts: Optional[List[str]] = None,
                    expected_payload_keys: Optional[List[str]] = None,
                    expected_event: Optional[str] = None) -> List[str]:
    """
    Validate an agent response against expected values.
    
    Args:
        response: Agent response to validate
        expected_text: Exact text expected in fulfillment_text (if None, not checked)
        text_contains: List of strings that should be in fulfillment_text
        expected_contexts: List of context names that should be present
        expected_payload_keys: List of keys that should be present in the payload
        expected_event: Name of the expected followup event
        
    Returns:
        List of validation error messages (empty if all validations pass)
    """
    errors = []
    
    # Validate fulfillment text
    if expected_text is not None and response.fulfillment_text != expected_text:
        errors.append(f"Expected text: '{expected_text}', got: '{response.fulfillment_text}'")
    
    # Validate text contains
    if text_contains:
        for text in text_contains:
            if text not in response.fulfillment_text:
                errors.append(f"Expected text to contain: '{text}'")
    
    # Validate contexts
    if expected_contexts:
        context_names = []
        
        for context in response.output_contexts:
            # Extract context name from the full context path
            match = re.search(r'/contexts/([^/]+)$', context.get('name', ''))
            if match:
                context_names.append(match.group(1))
        
        for expected_context in expected_contexts:
            if expected_context not in context_names:
                errors.append(f"Expected context: '{expected_context}' not found")
    
    # Validate payload keys
    if expected_payload_keys and response.payload:
        for key in expected_payload_keys:
            if key not in response.payload:
                errors.append(f"Expected payload key: '{key}' not found")
    
    # Validate followup event
    if expected_event and (not response.followup_event or 
                         response.followup_event.get('name') != expected_event):
        errors.append(f"Expected followup event: '{expected_event}', got: "
                     f"{response.followup_event.get('name') if response.followup_event else 'None'}")
    
    return errors


def assert_contains_context(response: AgentResponse, context_name: str, 
                          parameters: Optional[Dict[str, Any]] = None) -> bool:
    """
    Assert that a response contains a specific context with optional parameters.
    
    Args:
        response: Agent response to check
        context_name: Name of the context
        parameters: Expected parameter values
        
    Returns:
        True if context with matching parameters is found, False otherwise
    """
    if not response.output_contexts:
        return False
    
    for context in response.output_contexts:
        # Extract context name from the full context path
        match = re.search(r'/contexts/([^/]+)$', context.get('name', ''))
        if match and match.group(1) == context_name:
            # Context found, check parameters if specified
            if parameters is None:
                return True
            
            context_params = context.get('parameters', {})
            for key, expected_value in parameters.items():
                if key not in context_params or context_params[key] != expected_value:
                    return False
            
            return True
    
    return False


def assert_response_contains_rich_content(response: AgentResponse, 
                                        content_type: str) -> bool:
    """
    Assert that a response contains a specific type of rich content.
    
    Args:
        response: Agent response to check
        content_type: Type of rich content (e.g., "card", "image", "button")
        
    Returns:
        True if rich content of the specified type is found, False otherwise
    """
    if not response.payload or 'richContent' not in response.payload:
        return False
    
    rich_content = response.payload['richContent']
    
    # Iterate through all content groups
    for group in rich_content:
        # Iterate through all items in the group
        for item in group:
            if item.get('type') == content_type:
                return True
    
    return False


def assert_response_contains_suggestion_chips(response: AgentResponse, 
                                            expected_chips: List[str]) -> bool:
    """
    Assert that a response contains specific suggestion chips.
    
    Args:
        response: Agent response to check
        expected_chips: List of expected suggestion texts
        
    Returns:
        True if all expected suggestion chips are found, False otherwise
    """
    if not response.payload or 'richContent' not in response.payload:
        return False
    
    rich_content = response.payload['richContent']
    
    # Find suggestion chips
    found_chips = []
    
    # Iterate through all content groups
    for group in rich_content:
        # Iterate through all items in the group
        for item in group:
            if item.get('type') == 'chips':
                for chip in item.get('options', []):
                    found_chips.append(chip.get('text'))
    
    # Check that all expected chips are found
    return all(chip in found_chips for chip in expected_chips)


def assert_response_contains_button(response: AgentResponse, 
                                  button_text: str) -> bool:
    """
    Assert that a response contains a button with specific text.
    
    Args:
        response: Agent response to check
        button_text: Expected button text
        
    Returns:
        True if button with the specified text is found, False otherwise
    """
    if not response.payload or 'richContent' not in response.payload:
        return False
    
    rich_content = response.payload['richContent']
    
    # Iterate through all content groups
    for group in rich_content:
        # Iterate through all items in the group
        for item in group:
            # Check for button type
            if item.get('type') == 'button' and item.get('text') == button_text:
                return True
            
            # Check for card with action links
            if item.get('type') in ['info', 'card'] and 'actionLink' in item:
                for button in item['actionLink']:
                    if button.get('text') == button_text:
                        return True
    
    return False

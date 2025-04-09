"""
Response Formatters module for the GCP AI Agent Framework.

This module provides utilities for creating rich responses for DialogFlow agents,
including cards, carousels, suggestion chips, and other interactive elements.

The formatters follow the DialogFlow response format for the Conversational Agents
API, making it easy to create visually appealing and interactive responses.

Example usage:
```python
# Create a card response
card_response = create_card_response(
    title="Product Details",
    subtitle="Premium Widget",
    image_url="https://example.com/widget.jpg",
    buttons=[
        {"text": "Buy Now", "postback": "https://example.com/buy"},
        {"text": "Learn More", "postback": "learn_more_widgets"}
    ]
)

# Create suggestion chips
chips = create_suggestion_chips(["Yes", "No", "Maybe"])

# Combine into a response
response = AgentResponse(
    fulfillment_text="Here's the product you requested",
    payload={"richContent": [[card_response], [{"suggestions": chips}]]}
)
```
"""

from typing import Dict, Any, List, Optional, Union


def create_card_response(title: str, subtitle: Optional[str] = None,
                       image_url: Optional[str] = None,
                       buttons: Optional[List[Dict[str, str]]] = None,
                       text: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a card response for DialogFlow.
    
    Args:
        title: Card title
        subtitle: Card subtitle
        image_url: URL of the image to display
        buttons: List of button objects with 'text' and 'postback' properties
        text: Additional text content for the card
        
    Returns:
        Card response object
    """
    card = {
        "type": "info",
        "title": title
    }
    
    if subtitle:
        card["subtitle"] = subtitle
    
    if image_url:
        card["image"] = {
            "src": {
                "rawUrl": image_url
            }
        }
    
    if text:
        card["text"] = text
    
    if buttons:
        card["actionLink"] = buttons
    
    return card


def create_image_response(image_url: str, accessibility_text: str,
                        title: Optional[str] = None) -> Dict[str, Any]:
    """
    Create an image response for DialogFlow.
    
    Args:
        image_url: URL of the image to display
        accessibility_text: Alt text for the image
        title: Optional title for the image
        
    Returns:
        Image response object
    """
    image = {
        "type": "image",
        "rawUrl": image_url,
        "accessibilityText": accessibility_text
    }
    
    if title:
        image["title"] = title
    
    return image


def create_button_response(text: str, icon: Optional[str] = None,
                         link: Optional[str] = None,
                         event: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a button response for DialogFlow.
    
    Args:
        text: Button text
        icon: Optional icon for the button
        link: URL to open when button is clicked
        event: Event to trigger when button is clicked
        
    Returns:
        Button response object
    """
    button = {
        "type": "button",
        "text": text
    }
    
    if icon:
        button["icon"] = {
            "type": icon
        }
    
    if link:
        button["link"] = link
    
    if event:
        button["event"] = event
    
    return button


def create_carousel_response(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a carousel response for DialogFlow.
    
    Args:
        items: List of carousel item objects
        
    Returns:
        Carousel response object
    """
    carousel_items = []
    
    for item in items:
        carousel_item = {
            "type": "info",
            "title": item.get("title", "")
        }
        
        if "subtitle" in item:
            carousel_item["subtitle"] = item["subtitle"]
        
        if "image_url" in item:
            carousel_item["image"] = {
                "src": {
                    "rawUrl": item["image_url"]
                }
            }
        
        if "text" in item:
            carousel_item["text"] = item["text"]
        
        if "buttons" in item:
            carousel_item["actionLink"] = item["buttons"]
        
        carousel_items.append(carousel_item)
    
    return carousel_items


def create_suggestion_chips(suggestions: List[str]) -> List[Dict[str, str]]:
    """
    Create suggestion chips for DialogFlow.
    
    Args:
        suggestions: List of suggestion texts
        
    Returns:
        List of suggestion chip objects
    """
    return [{"title": suggestion} for suggestion in suggestions]


def create_list_response(title: str, items: List[Dict[str, Any]],
                       subtitle: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a list response for DialogFlow.
    
    Args:
        title: Title of the list
        items: List of item objects, each with 'key' and 'title' properties
        subtitle: Optional subtitle for the list
        
    Returns:
        List response object
    """
    list_response = {
        "type": "list",
        "title": title,
        "items": items
    }
    
    if subtitle:
        list_response["subtitle"] = subtitle
    
    return list_response


def create_accordion_response(title: str, subtitle: Optional[str] = None,
                            image_url: Optional[str] = None,
                            text: str = None) -> Dict[str, Any]:
    """
    Create an accordion response for DialogFlow.
    
    Args:
        title: Accordion title
        subtitle: Optional subtitle
        image_url: Optional image URL
        text: Text content for the accordion
        
    Returns:
        Accordion response object
    """
    accordion = {
        "type": "accordion",
        "title": title
    }
    
    if subtitle:
        accordion["subtitle"] = subtitle
    
    if image_url:
        accordion["image"] = {
            "src": {
                "rawUrl": image_url
            }
        }
    
    if text:
        accordion["text"] = text
    
    return accordion


def create_table_response(title: str, subtitle: Optional[str] = None,
                        headers: Optional[List[str]] = None,
                        rows: List[List[str]] = None) -> Dict[str, Any]:
    """
    Create a table response for DialogFlow.
    
    Args:
        title: Table title
        subtitle: Optional subtitle
        headers: List of column headers
        rows: 2D array of cell values
        
    Returns:
        Table response object
    """
    table = {
        "type": "table",
        "title": title,
        "rows": []
    }
    
    if subtitle:
        table["subtitle"] = subtitle
    
    if headers:
        table["columnProperties"] = [{"header": header} for header in headers]
    
    if rows:
        table["rows"] = [{"cells": [{"text": cell} for cell in row]} for row in rows]
    
    return table


def create_divider_response() -> Dict[str, str]:
    """
    Create a divider response for DialogFlow.
    
    Returns:
        Divider response object
    """
    return {"type": "divider"}


def create_rich_response(elements: List[Union[Dict[str, Any], List[Dict[str, Any]]]]) -> Dict[str, List[List[Dict[str, Any]]]]:
    """
    Create a rich response payload for DialogFlow, combining multiple UI elements.
    
    This follows the format required by the DialogFlow agent fulfillment payload.
    
    Args:
        elements: List of UI elements or groups of elements
        
    Returns:
        Rich response payload
    """
    rich_content = []
    
    for element in elements:
        if isinstance(element, list):
            # Element is already a group
            rich_content.append(element)
        else:
            # Single element, wrap in a group
            rich_content.append([element])
    
    return {"richContent": rich_content}

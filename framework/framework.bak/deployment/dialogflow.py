"""
DialogFlow deployment module for the GCP AI Agent Framework.

This module provides utilities for generating DialogFlow agent configuration files
that can be imported into the DialogFlow Console or used with the API.
It includes tools for defining intents, entities, and training phrases.

Example usage:
```python
# Generate DialogFlow configuration
generate_dialogflow_config(
    output_dir='./dialogflow',
    agent_name='Weather Bot',
    default_language='en',
    intents=[
        {
            'name': 'get_weather',
            'training_phrases': [
                'What\'s the weather in {location}',
                'Weather forecast for {location}',
                'How\'s the weather in {location} today'
            ],
            'parameters': [
                {'name': 'location', 'entity_type': '@sys.location', 'required': True}
            ]
        }
    ],
    entities=[
        {
            'name': 'weather_condition',
            'values': [
                {'value': 'sunny', 'synonyms': ['clear', 'fair', 'nice']},
                {'value': 'rainy', 'synonyms': ['rain', 'downpour', 'drizzle']},
                {'value': 'cloudy', 'synonyms': ['overcast', 'gray']}
            ]
        }
    ]
)
```
"""

import os
import json
import uuid
import zipfile
import textwrap
from typing import List, Dict, Any, Optional


def generate_dialogflow_config(output_dir: str, agent_name: str,
                             default_language: str = 'en',
                             intents: Optional[List[Dict[str, Any]]] = None,
                             entities: Optional[List[Dict[str, Any]]] = None,
                             webhook_url: Optional[str] = None) -> str:
    """
    Generate DialogFlow agent configuration files.
    
    Args:
        output_dir: Directory to write the configuration files
        agent_name: Name of the agent
        default_language: Default language code
        intents: List of intent definitions
        entities: List of entity definitions
        webhook_url: URL for the webhook
        
    Returns:
        Path to the output directory
    """
    # Create output directory structure
    os.makedirs(os.path.join(output_dir, 'intents'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'entities'), exist_ok=True)
    
    # Generate agent.json
    agent = {
        "description": f"{agent_name} - Created with GCP AI Agent Framework",
        "language": default_language,
        "shortDescription": agent_name,
        "examples": "",
        "linkToDocs": "",
        "displayName": agent_name,
        "disableInteractionLogs": False,
        "disableStackdriverLogs": False,
        "defaultTimezone": "America/Los_Angeles",
        "webhook": {
            "url": webhook_url or "",
            "available": bool(webhook_url),
            "useForDomains": False,
            "cloudFunctionsEnabled": True,
            "headers": {}
        },
        "isPrivate": True,
        "mlMinConfidence": 0.3,
        "customClassifierMode": "use.after.hybrid",
        "onePlatformApiVersion": "v2",
        "analyzeQueryTextSentiment": False,
        "enabledKnowledgeBaseNames": [],
        "knowledgeServiceConfidenceAdjustment": 0.0,
        "dialogBuilderMode": False,
        "baseActionPackagesUrl": ""
    }
    
    # Write agent.json
    with open(os.path.join(output_dir, 'agent.json'), 'w') as f:
        json.dump(agent, f, indent=2)
    
    # Generate package.json
    package = {
        "version": "1.0.0"
    }
    
    # Write package.json
    with open(os.path.join(output_dir, 'package.json'), 'w') as f:
        json.dump(package, f, indent=2)
    
    # Generate intents
    if intents:
        for intent in intents:
            generate_intent_files(os.path.join(output_dir, 'intents'), intent)
    
    # Generate default welcome intent
    generate_default_welcome_intent(os.path.join(output_dir, 'intents'))
    
    # Generate fallback intent
    generate_fallback_intent(os.path.join(output_dir, 'intents'))
    
    # Generate entities
    if entities:
        for entity in entities:
            generate_entity_files(os.path.join(output_dir, 'entities'), entity)
    
    # Generate README.md with instructions
    readme = f"""
    # {agent_name} DialogFlow Agent Configuration

    This directory contains configuration files for the {agent_name} DialogFlow agent.

    ## Import Instructions

    To import this agent:

    1. Go to the DialogFlow Console: https://dialogflow.cloud.google.com/
    2. Click "Create new agent"
    3. Click the gear icon to import
    4. Upload this directory as a zip file

    ## Structure

    - agent.json: Main agent configuration
    - package.json: Version information
    - intents/: Intent definitions
    - entities/: Entity definitions
    """
    
    # Write README.md
    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.write(textwrap.dedent(readme).strip())
    
    # Create zip file
    zip_path = f"{output_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), output_dir)
                )
    
    return output_dir


def generate_intent_files(intents_dir: str, intent: Dict[str, Any]) -> None:
    """
    Generate files for a DialogFlow intent.
    
    Args:
        intents_dir: Directory to write the intent files
        intent: Intent definition
    """
    intent_name = intent['name']
    intent_dir = os.path.join(intents_dir, f"{intent_name}.json")
    
    # Generate intent.json
    intent_json = {
        "id": str(uuid.uuid4()),
        "name": intent_name,
        "auto": True,
        "contexts": intent.get('input_contexts', []),
        "responses": [
            {
                "resetContexts": False,
                "affectedContexts": [
                    {"name": context, "lifespan": 5} 
                    for context in intent.get('output_contexts', [])
                ],
                "parameters": [
                    {
                        "id": str(uuid.uuid4()),
                        "required": param.get('required', False),
                        "dataType": param.get('entity_type', '@sys.any'),
                        "name": param['name'],
                        "value": f"${param['name']}",
                        "promptMessages": [],
                        "noMatchMessages": [],
                        "noInputMessages": [],
                        "outputDialogContexts": []
                    }
                    for param in intent.get('parameters', [])
                ],
                "messages": [
                    {
                        "type": 0,
                        "lang": "en",
                        "condition": "",
                        "speech": intent.get('responses', ["I'll handle that for you"])
                    }
                ],
                "defaultResponsePlatforms": {},
                "speech": []
            }
        ],
        "priority": 500000,
        "webhookUsed": True,
        "webhookForSlotFilling": False,
        "fallbackIntent": False,
        "events": intent.get('events', []),
        "conditionalResponses": [],
        "condition": "",
        "conditionalFollowupEvents": []
    }
    
    # Write intent.json
    with open(intent_dir, 'w') as f:
        json.dump(intent_json, f, indent=2)
    
    # Generate userSays JSON for training phrases
    user_says_dir = os.path.join(intents_dir, f"{intent_name}_usersays_en.json")
    
    user_says = []
    for phrase in intent.get('training_phrases', []):
        # Parse for parameters
        parts = []
        text = ""
        for part in phrase.split('{'):
            if '}' in part:
                param_part, rest = part.split('}', 1)
                param_name = param_part.strip()
                
                # Add parameter
                if text:
                    parts.append({"text": text, "userDefined": False})
                    text = ""
                
                # Find parameter definition
                param_def = next(
                    (p for p in intent.get('parameters', []) if p['name'] == param_name),
                    None
                )
                
                if param_def:
                    parts.append({
                        "text": param_name,
                        "alias": param_name,
                        "meta": param_def.get('entity_type', '@sys.any'),
                        "userDefined": True
                    })
                else:
                    parts.append({
                        "text": param_name,
                        "userDefined": False
                    })
                
                text = rest
            else:
                text += part
        
        if text:
            parts.append({"text": text, "userDefined": False})
        
        user_says.append({
            "id": str(uuid.uuid4()),
            "data": parts,
            "isTemplate": False,
            "count": 0,
            "updated": 0
        })
    
    # Write userSays.json
    if user_says:
        with open(user_says_dir, 'w') as f:
            json.dump(user_says, f, indent=2)


def generate_default_welcome_intent(intents_dir: str) -> None:
    """
    Generate the default welcome intent.
    
    Args:
        intents_dir: Directory to write the intent files
    """
    intent = {
        "name": "Default Welcome Intent",
        "responses": ["Welcome to our agent! How can I help you today?"],
        "events": ["WELCOME"]
    }
    
    generate_intent_files(intents_dir, intent)


def generate_fallback_intent(intents_dir: str) -> None:
    """
    Generate the default fallback intent.
    
    Args:
        intents_dir: Directory to write the intent files
    """
    intent_dir = os.path.join(intents_dir, "Default Fallback Intent.json")
    
    # Generate intent.json
    intent_json = {
        "id": str(uuid.uuid4()),
        "name": "Default Fallback Intent",
        "auto": True,
        "contexts": [],
        "responses": [
            {
                "resetContexts": False,
                "affectedContexts": [],
                "parameters": [],
                "messages": [
                    {
                        "type": 0,
                        "lang": "en",
                        "condition": "",
                        "speech": [
                            "I didn't get that. Can you say it again?",
                            "I missed what you said. What was that?",
                            "Sorry, could you say that again?",
                            "Sorry, can you say that again?",
                            "Can you say that again?",
                            "Sorry, I didn't get that. Can you rephrase?",
                            "Sorry, what was that?",
                            "One more time?",
                            "What was that?",
                            "Say that one more time?",
                            "I didn't get that. Can you repeat?",
                            "I missed that, say that again?"
                        ]
                    }
                ],
                "defaultResponsePlatforms": {},
                "speech": []
            }
        ],
        "priority": 500000,
        "webhookUsed": True,
        "webhookForSlotFilling": False,
        "fallbackIntent": True,
        "events": [],
        "conditionalResponses": [],
        "condition": "",
        "conditionalFollowupEvents": []
    }
    
    # Write intent.json
    with open(intent_dir, 'w') as f:
        json.dump(intent_json, f, indent=2)


def generate_entity_files(entities_dir: str, entity: Dict[str, Any]) -> None:
    """
    Generate files for a DialogFlow entity.
    
    Args:
        entities_dir: Directory to write the entity files
        entity: Entity definition
    """
    entity_name = entity['name']
    entity_dir = os.path.join(entities_dir, f"{entity_name}.json")
    
    # Generate entity.json
    entity_json = {
        "id": str(uuid.uuid4()),
        "name": entity_name,
        "isOverridable": True,
        "isEnum": False,
        "isRegexp": False,
        "automatedExpansion": True,
        "allowFuzzyExtraction": True
    }
    
    # Write entity.json
    with open(entity_dir, 'w') as f:
        json.dump(entity_json, f, indent=2)
    
    # Generate entries JSON
    entries_dir = os.path.join(entities_dir, f"{entity_name}_entries_en.json")
    
    entries = []
    for value in entity.get('values', []):
        entries.append({
            "value": value['value'],
            "synonyms": [value['value']] + value.get('synonyms', [])
        })
    
    # Write entries.json
    with open(entries_dir, 'w') as f:
        json.dump(entries, f, indent=2)

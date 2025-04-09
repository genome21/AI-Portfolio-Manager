# AI Agent Framework

A lightweight framework for building AI Agents using Google Cloud Platform's Agent Builder for DialogFlow, with integration to Cloud Functions.

## Overview

This framework provides a streamlined approach to building AI agents based on the AI Portfolio Manager pattern. It focuses on:

1. Creating a consistent API structure for handling agent requests
2. Providing tools for generating OpenAPI specifications
3. Including mock data generators for development and testing

## Components

The framework includes these key components:

- **agent_api.py**: Core API handling and routing
- **openapi_generator.py**: Utilities for creating OpenAPI specifications
- **mock_data.py**: Tools for generating mock data for testing
- **examples.py**: Example implementations

## Getting Started

### Installation

You can include this framework in your project by copying the `framework` directory to your project.

```bash
cp -r framework /path/to/your/project/
```

### Basic Usage

Here's a simple example of how to create an agent API:

```python
import functions_framework
from flask import Request
from framework.agent_api import AgentAPI, create_success_response

# Create an API
api = AgentAPI("my_agent")

# Define a handler
def greeting_handler(request: Request):
    name = request.args.get('name', 'there')
    return create_success_response({
        "message": f"Hello, {name}!"
    })

# Register the handler
api.register_handler('greeting', greeting_handler)

# Create a Cloud Function entry point
@functions_framework.http
def agent_function(request):
    return api.handle_request(request)
```

### Creating an OpenAPI Specification

Use the OpenAPI generator to create specifications for Agent Builder:

```python
from framework.openapi_generator import (
    create_openapi_spec,
    add_path,
    create_parameter,
    save_openapi_spec
)

# Create a basic specification
spec = create_openapi_spec(
    title="My Agent API",
    description="API for my conversational agent",
    server_url="https://us-central1-my-project.cloudfunctions.net/my_agent"
)

# Add a path
spec = add_path(
    spec,
    path="/greeting",
    summary="Get a greeting",
    description="Returns a personalized greeting",
    operation_id="getGreeting",
    method="get",
    parameters=[
        create_parameter(
            name="name",
            description="Name to greet",
            required=False
        )
    ]
)

# Save the specification
save_openapi_spec(spec, "openapi.yaml")
```

### Using Mock Data

The framework includes tools for generating mock data:

```python
from framework.mock_data import generate_stock_data

# Generate mock stock data
stock_data = generate_stock_data("AAPL", "Apple Inc.")
print(stock_data)
```

## Example: Portfolio Manager

The framework includes a complete example of a Portfolio Manager agent similar to the AI Portfolio Manager. To try it:

```python
from framework.examples import create_portfolio_manager_api

# Create the API
api = create_portfolio_manager_api()

# For local testing
from flask import Flask, request

app = Flask(__name__)

@app.route('/<path:path>', methods=['GET', 'POST'])
def api_route(path):
    return api.handle_request(request)

# Run the app
app.run(host='0.0.0.0', port=8080)
```

## Deployment

To deploy an agent API as a Cloud Function:

1. Create a `main.py` file:

```python
import functions_framework
from my_agent import create_api

# Create the API
api = create_api()

# Create Cloud Function entry point
@functions_framework.http
def agent_webhook(request):
    return api.handle_request(request)
```

2. Deploy the Cloud Function:

```bash
gcloud functions deploy agent_webhook \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated
```

3. Use the deployed URL in your Agent Builder/DialogFlow configuration.

## License

This framework is released under the same license as the AI Portfolio Manager project.

"""
Cloud Functions deployment module for the GCP AI Agent Framework.

This module provides utilities for generating code and configuration files
for deploying agent implementations as Google Cloud Functions. It includes
templates for main.py, requirements.txt, and helper functions.

Example usage:
```python
# Generate Cloud Function code
generate_cloud_function_code(
    output_dir='./function',
    function_name='agent_webhook',
    handler_module='my_agent.handlers',
    intents=['get_weather', 'get_forecast']
)

# Create requirements.txt
create_requirements_file(
    output_path='./function/requirements.txt',
    additional_requirements=['pandas', 'numpy']
)
```
"""

import os
import textwrap
from typing import List, Dict, Any, Optional


def generate_cloud_function_code(output_dir: str, function_name: str,
                               handler_module: str, intents: List[str],
                               memory: str = "256MB", timeout: str = "60s") -> str:
    """
    Generate code for a Cloud Function that serves as a webhook for a DialogFlow agent.
    
    Args:
        output_dir: Directory to write the generated code
        function_name: Name of the Cloud Function
        handler_module: Module containing intent handlers
        intents: List of intent names
        memory: Memory allocation for the function
        timeout: Timeout for the function
        
    Returns:
        Path to the generated main.py file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate main.py
    main_py = f"""
    import functions_framework
    from flask import jsonify

    # Import the agent framework
    from gcpai_framework.core import WebhookHandler
    from gcpai_framework.logging import setup_logging

    # Import intent handlers
    from {handler_module} import {', '.join([f"{intent}Handler" for intent in intents])}

    # Set up logging
    setup_logging(log_level='INFO', use_cloud_logging=True)

    # Create webhook handler
    webhook = WebhookHandler("{function_name}")

    # Register intent handlers
    {chr(10).join([f"webhook.register_handler({intent}Handler('{intent}'))" for intent in intents])}

    @functions_framework.http
    def {function_name}(request):
        \"\"\"
        Cloud Function entry point.
        
        Args:
            request: Flask request object
            
        Returns:
            Response for DialogFlow
        \"\"\"
        return webhook.handle_request(request)
    """
    
    # Write main.py
    main_py_path = os.path.join(output_dir, 'main.py')
    with open(main_py_path, 'w') as f:
        f.write(textwrap.dedent(main_py).strip())
    
    # Generate .gcloudignore
    gcloudignore = """
    .git
    .gitignore
    .gcloudignore
    .vscode/
    .idea/
    __pycache__/
    *.py[cod]
    *$py.class
    *.so
    .env
    .venv
    env/
    venv/
    ENV/
    """
    
    # Write .gcloudignore
    gcloudignore_path = os.path.join(output_dir, '.gcloudignore')
    with open(gcloudignore_path, 'w') as f:
        f.write(textwrap.dedent(gcloudignore).strip())
    
    # Generate README.md with deployment instructions
    readme = f"""
    # {function_name} Cloud Function

    This Cloud Function serves as a webhook for a DialogFlow agent.

    ## Deployment Instructions

    To deploy this function, run:

    ```bash
    gcloud functions deploy {function_name} \\
        --runtime python39 \\
        --trigger-http \\
        --allow-unauthenticated \\
        --memory {memory} \\
        --timeout {timeout} \\
        --entry-point {function_name}
    ```

    After deployment, you'll get a URL for the webhook. Use this URL in your DialogFlow agent's fulfillment settings.
    """
    
    # Write README.md
    readme_path = os.path.join(output_dir, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(textwrap.dedent(readme).strip())
    
    return main_py_path


def create_requirements_file(output_path: str, 
                           additional_requirements: Optional[List[str]] = None) -> str:
    """
    Create a requirements.txt file for a Cloud Function.
    
    Args:
        output_path: Path to write the requirements.txt file
        additional_requirements: Additional Python packages to include
        
    Returns:
        Path to the generated requirements.txt file
    """
    # Base requirements
    requirements = [
        "functions-framework==3.*",
        "google-cloud-logging>=2.7.0",
        "google-cloud-monitoring>=2.9.0",
        "google-cloud-storage>=2.5.0",
        "requests>=2.28.0"
    ]
    
    # Add additional requirements
    if additional_requirements:
        requirements.extend(additional_requirements)
    
    # Write requirements.txt
    with open(output_path, 'w') as f:
        f.write("\n".join(requirements))
    
    return output_path


def generate_deployment_script(output_dir: str, function_name: str,
                             project_id: str, region: str = "us-central1",
                             memory: str = "256MB", timeout: str = "60s") -> str:
    """
    Generate a deployment script for a Cloud Function.
    
    Args:
        output_dir: Directory to write the generated script
        function_name: Name of the Cloud Function
        project_id: Google Cloud project ID
        region: Google Cloud region
        memory: Memory allocation for the function
        timeout: Timeout for the function
        
    Returns:
        Path to the generated script
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate deploy.sh
    deploy_sh = f"""
    #!/bin/bash

    # Deploy Cloud Function
    gcloud functions deploy {function_name} \\
        --project={project_id} \\
        --region={region} \\
        --runtime=python39 \\
        --trigger-http \\
        --allow-unauthenticated \\
        --memory={memory} \\
        --timeout={timeout} \\
        --entry-point={function_name}

    # Get the deployed URL
    WEBHOOK_URL=$(gcloud functions describe {function_name} \\
        --project={project_id} \\
        --region={region} \\
        --format="value(httpsTrigger.url)")

    echo "Cloud Function deployed successfully!"
    echo "Webhook URL: $WEBHOOK_URL"
    echo ""
    echo "Use this URL in your DialogFlow agent's fulfillment settings."
    """
    
    # Write deploy.sh
    deploy_sh_path = os.path.join(output_dir, 'deploy.sh')
    with open(deploy_sh_path, 'w') as f:
        f.write(textwrap.dedent(deploy_sh).strip())
    
    # Make the script executable
    os.chmod(deploy_sh_path, 0o755)
    
    return deploy_sh_path

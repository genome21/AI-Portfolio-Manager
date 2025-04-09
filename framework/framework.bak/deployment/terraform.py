"""
Terraform deployment module for the GCP AI Agent Framework.

This module provides utilities for generating Terraform configuration files
for deploying agent implementations and associated infrastructure to Google Cloud Platform.
It includes templates for Cloud Functions, IAM, Storage, and other GCP resources.

Example usage:
```python
# Generate Terraform configuration
generate_terraform_config(
    output_dir='./terraform',
    project_id='my-project',
    region='us-central1',
    function_name='agent_webhook',
    source_dir='./function',
    bucket_name='agent-storage'
)
```
"""

import os
import textwrap
from typing import List, Dict, Any, Optional


def generate_terraform_config(output_dir: str, project_id: str, region: str,
                            function_name: str, source_dir: str,
                            bucket_name: Optional[str] = None,
                            memory: str = "256MiB", timeout: int = 60) -> str:
    """
    Generate Terraform configuration for deploying a Cloud Function.
    
    Args:
        output_dir: Directory to write the Terraform files
        project_id: Google Cloud project ID
        region: Google Cloud region
        function_name: Name of the Cloud Function
        source_dir: Directory containing the Cloud Function source code
        bucket_name: Name of the Cloud Storage bucket (generated if None)
        memory: Memory allocation for the function
        timeout: Timeout for the function in seconds
        
    Returns:
        Path to the generated Terraform files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate bucket name if not provided
    if not bucket_name:
        bucket_name = f"{project_id}-{function_name}-source"
    
    # Generate provider.tf
    provider_tf = """
    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 4.0"
        }
      }
    }

    provider "google" {
      project = var.project_id
      region  = var.region
    }
    """
    
    # Write provider.tf
    with open(os.path.join(output_dir, 'provider.tf'), 'w') as f:
        f.write(textwrap.dedent(provider_tf).strip())
    
    # Generate variables.tf
    variables_tf = f"""
    variable "project_id" {{
      description = "The ID of the Google Cloud project"
      type        = string
      default     = "{project_id}"
    }}

    variable "region" {{
      description = "The region to deploy to"
      type        = string
      default     = "{region}"
    }}

    variable "function_name" {{
      description = "The name of the Cloud Function"
      type        = string
      default     = "{function_name}"
    }}

    variable "source_dir" {{
      description = "The directory containing the Cloud Function source code"
      type        = string
      default     = "{source_dir}"
    }}

    variable "bucket_name" {{
      description = "The name of the Cloud Storage bucket for the function source"
      type        = string
      default     = "{bucket_name}"
    }}
    """
    
    # Write variables.tf
    with open(os.path.join(output_dir, 'variables.tf'), 'w') as f:
        f.write(textwrap.dedent(variables_tf).strip())
    
    # Generate storage.tf
    storage_tf = """
    # Create a bucket for the Cloud Function source code
    resource "google_storage_bucket" "function_bucket" {
      name     = var.bucket_name
      location = var.region
      force_destroy = true
      uniform_bucket_level_access = true
    }

    # Create a zip archive of the Cloud Function source code
    data "archive_file" "function_source" {
      type        = "zip"
      source_dir  = var.source_dir
      output_path = "${path.module}/function.zip"
    }

    # Upload the zip archive to the bucket
    resource "google_storage_bucket_object" "function_source" {
      name   = "function-${data.archive_file.function_source.output_md5}.zip"
      bucket = google_storage_bucket.function_bucket.name
      source = data.archive_file.function_source.output_path
    }
    """
    
    # Write storage.tf
    with open(os.path.join(output_dir, 'storage.tf'), 'w') as f:
        f.write(textwrap.dedent(storage_tf).strip())
    
    # Generate function.tf
    function_tf = f"""
    # Create the Cloud Function
    resource "google_cloudfunctions_function" "function" {{
      name        = var.function_name
      description = "Webhook for DialogFlow agent"
      runtime     = "python39"
      
      available_memory_mb   = {memory.replace('MiB', '')}
      source_archive_bucket = google_storage_bucket.function_bucket.name
      source_archive_object = google_storage_bucket_object.function_source.name
      trigger_http          = true
      timeout               = {timeout}
      entry_point           = var.function_name
      
      environment_variables = {{
        GCP_PROJECT = var.project_id
      }}
    }}

    # IAM entry for all users to invoke the function
    resource "google_cloudfunctions_function_iam_member" "invoker" {{
      project        = google_cloudfunctions_function.function.project
      region         = google_cloudfunctions_function.function.region
      cloud_function = google_cloudfunctions_function.function.name
      
      role   = "roles/cloudfunctions.invoker"
      member = "allUsers"
    }}
    """
    
    # Write function.tf
    with open(os.path.join(output_dir, 'function.tf'), 'w') as f:
        f.write(textwrap.dedent(function_tf).strip())
    
    # Generate outputs.tf
    outputs_tf = """
    output "function_url" {
      description = "The URL of the deployed Cloud Function"
      value       = google_cloudfunctions_function.function.https_trigger_url
    }

    output "function_name" {
      description = "The name of the deployed Cloud Function"
      value       = google_cloudfunctions_function.function.name
    }

    output "bucket_name" {
      description = "The name of the Cloud Storage bucket"
      value       = google_storage_bucket.function_bucket.name
    }
    """
    
    # Write outputs.tf
    with open(os.path.join(output_dir, 'outputs.tf'), 'w') as f:
        f.write(textwrap.dedent(outputs_tf).strip())
    
    # Generate README.md
    readme = f"""
    # Terraform Configuration for {function_name}

    This directory contains Terraform configuration files for deploying
    the {function_name} Cloud Function to Google Cloud Platform.

    ## Prerequisites

    - Terraform installed (https://www.terraform.io/downloads.html)
    - Google Cloud SDK installed (https://cloud.google.com/sdk/docs/install)
    - Google Cloud project with billing enabled

    ## Deployment Instructions

    1. Initialize Terraform:
    ```
    terraform init
    ```

    2. Review the deployment plan:
    ```
    terraform plan
    ```

    3. Apply the configuration:
    ```
    terraform apply
    ```

    4. After deployment, you'll see the URL for the webhook.
    Use this URL in your DialogFlow agent's fulfillment settings.

    ## Cleaning Up

    To remove all resources created by this configuration:
    ```
    terraform destroy
    ```
    """
    
    # Write README.md
    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.write(textwrap.dedent(readme).strip())
    
    return output_dir


def generate_complete_infrastructure(output_dir: str, project_id: str, region: str,
                                   agent_name: str, functions: List[Dict[str, Any]]) -> str:
    """
    Generate Terraform configuration for a complete agent infrastructure.
    
    Args:
        output_dir: Directory to write the Terraform files
        project_id: Google Cloud project ID
        region: Google Cloud region
        agent_name: Name of the DialogFlow agent
        functions: List of Cloud Function configurations
        
    Returns:
        Path to the generated Terraform files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate provider.tf
    provider_tf = """
    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 4.0"
        }
      }
    }

    provider "google" {
      project = var.project_id
      region  = var.region
    }
    """
    
    # Write provider.tf
    with open(os.path.join(output_dir, 'provider.tf'), 'w') as f:
        f.write(textwrap.dedent(provider_tf).strip())
    
    # Generate variables.tf
    variables_tf = f"""
    variable "project_id" {{
      description = "The ID of the Google Cloud project"
      type        = string
      default     = "{project_id}"
    }}

    variable "region" {{
      description = "The region to deploy to"
      type        = string
      default     = "{region}"
    }}

    variable "agent_name" {{
      description = "The name of the DialogFlow agent"
      type        = string
      default     = "{agent_name}"
    }}
    """
    
    # Write variables.tf
    with open(os.path.join(output_dir, 'variables.tf'), 'w') as f:
        f.write(textwrap.dedent(variables_tf).strip())
    
    # Generate storage.tf
    storage_tf = """
    # Create a bucket for the Cloud Function source code
    resource "google_storage_bucket" "function_bucket" {
      name     = "${var.project_id}-${var.agent_name}-functions"
      location = var.region
      force_destroy = true
      uniform_bucket_level_access = true
    }

    # Create a bucket for agent data storage
    resource "google_storage_bucket" "data_bucket" {
      name     = "${var.project_id}-${var.agent_name}-data"
      location = var.region
      force_destroy = true
      uniform_bucket_level_access = true
    }
    """
    
    # Write storage.tf
    with open(os.path.join(output_dir, 'storage.tf'), 'w') as f:
        f.write(textwrap.dedent(storage_tf).strip())
    
    # Generate functions.tf
    functions_tf = """
    # Cloud Functions
    """
    
    # Add each function
    for idx, function in enumerate(functions):
        name = function['name']
        source_dir = function.get('source_dir', f"./functions/{name}")
        memory = function.get('memory', '256MiB')
        timeout = function.get('timeout', 60)
        
        functions_tf += f"""
        # Function: {name}
        data "archive_file" "function_{idx}" {{
          type        = "zip"
          source_dir  = "{source_dir}"
          output_path = "${{path.module}}/function_{idx}.zip"
        }}

        resource "google_storage_bucket_object" "function_{idx}" {{
          name   = "{name}-${{data.archive_file.function_{idx}.output_md5}}.zip"
          bucket = google_storage_bucket.function_bucket.name
          source = data.archive_file.function_{idx}.output_path
        }}

        resource "google_cloudfunctions_function" "function_{idx}" {{
          name        = "{name}"
          description = "{function.get('description', f'Cloud Function for {agent_name}')}"
          runtime     = "python39"
          
          available_memory_mb   = {memory.replace('MiB', '')}
          source_archive_bucket = google_storage_bucket.function_bucket.name
          source_archive_object = google_storage_bucket_object.function_{idx}.name
          trigger_http          = true
          timeout               = {timeout}
          entry_point           = "{name}"
          
          environment_variables = {{
            GCP_PROJECT = var.project_id
            AGENT_NAME  = var.agent_name
          }}
        }}

        resource "google_cloudfunctions_function_iam_member" "invoker_{idx}" {{
          project        = google_cloudfunctions_function.function_{idx}.project
          region         = google_cloudfunctions_function.function_{idx}.region
          cloud_function = google_cloudfunctions_function.function_{idx}.name
          
          role   = "roles/cloudfunctions.invoker"
          member = "allUsers"
        }}
        """
    
    # Write functions.tf
    with open(os.path.join(output_dir, 'functions.tf'), 'w') as f:
        f.write(textwrap.dedent(functions_tf).strip())
    
    # Generate outputs.tf
    outputs_tf = """
    # Output the URLs of the deployed Cloud Functions
    """
    
    # Add outputs for each function
    for idx, function in enumerate(functions):
        name = function['name']
        outputs_tf += f"""
        output "{name}_url" {{
          description = "The URL of the deployed {name} function"
          value       = google_cloudfunctions_function.function_{idx}.https_trigger_url
        }}
        """
    
    # Add outputs for buckets
    outputs_tf += """
    output "function_bucket" {
      description = "The name of the Cloud Storage bucket for function source code"
      value       = google_storage_bucket.function_bucket.name
    }

    output "data_bucket" {
      description = "The name of the Cloud Storage bucket for agent data"
      value       = google_storage_bucket.data_bucket.name
    }
    """
    
    # Write outputs.tf
    with open(os.path.join(output_dir, 'outputs.tf'), 'w') as f:
        f.write(textwrap.dedent(outputs_tf).strip())
    
    # Generate README.md
    readme = f"""
    # Complete Terraform Configuration for {agent_name}

    This directory contains Terraform configuration files for deploying
    the complete infrastructure for the {agent_name} agent to Google Cloud Platform.

    ## Included Resources

    - Cloud Storage buckets for function source code and agent data
    - Cloud Functions for agent webhooks and processing
    - IAM permissions for invoking the functions

    ## Prerequisites

    - Terraform installed (https://www.terraform.io/downloads.html)
    - Google Cloud SDK installed (https://cloud.google.com/sdk/docs/install)
    - Google Cloud project with billing enabled
    - Required APIs enabled in your project:
      - Cloud Functions API
      - Cloud Storage API
      - Cloud Build API
      - DialogFlow API

    ## Deployment Instructions

    1. Initialize Terraform:
    ```
    terraform init
    ```

    2. Review the deployment plan:
    ```
    terraform plan
    ```

    3. Apply the configuration:
    ```
    terraform apply
    ```

    4. After deployment, you'll see the URLs for all the deployed functions.
    Use these URLs in your DialogFlow agent's fulfillment settings.

    ## Cleaning Up

    To remove all resources created by this configuration:
    ```
    terraform destroy
    ```
    """
    
    # Write README.md
    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.write(textwrap.dedent(readme).strip())
    
    return output_dir

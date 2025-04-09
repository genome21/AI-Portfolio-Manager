"""
Cloud Storage module for the GCP AI Agent Framework.

This module provides utilities for interacting with Google Cloud Storage,
making it easy to read, write, and manage files in GCS buckets.

In a production environment, this would utilize the Google Cloud Storage client
library, but for local development or environments without GCP access, it includes
a local file system fallback.

Example usage:
```python
# Create a Cloud Storage client
storage = CloudStorageClient("my-bucket")

# Upload a file
storage.upload_file("local/path/to/file.txt", "remote/path/to/file.txt")

# Read a file
content = storage.read_file("remote/path/to/file.txt")

# Check if a file exists
if storage.file_exists("remote/path/to/file.txt"):
    print("File exists!")
```
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, Optional, Union, List, BinaryIO, TextIO, cast

# Try to import GCS libraries, but provide fallbacks if not available
try:
    from google.cloud import storage
    from google.cloud.storage import Blob, Bucket
    from google.cloud.exceptions import NotFound
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from ..exceptions import ServiceError


class CloudStorageClient:
    """
    Client for interacting with Google Cloud Storage.
    
    This class provides a simple interface for common Cloud Storage operations
    like reading, writing, and listing files. It includes a fallback to local
    file system storage when GCS is not available.
    """
    
    def __init__(self, bucket_name: str, project_id: Optional[str] = None,
               use_local_fallback: bool = True, local_path: Optional[str] = None,
               logger: Optional[logging.Logger] = None):
        """
        Initialize the Cloud Storage client.
        
        Args:
            bucket_name: Name of the GCS bucket
            project_id: Google Cloud project ID (optional if already set in environment)
            use_local_fallback: Whether to use local file system fallback if GCS is not available
            local_path: Path for local file system fallback
            logger: Logger instance (creates a new one if None)
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.use_local_fallback = use_local_fallback
        self.local_path = local_path or os.path.join(tempfile.gettempdir(), "gcs_fallback", bucket_name)
        self.logger = logger or logging.getLogger("cloud_storage")
        
        # Initialize GCS client if available
        self.client = None
        self.bucket = None
        
        if GCS_AVAILABLE:
            try:
                # Create GCS client
                self.client = storage.Client(project=project_id) if project_id else storage.Client()
                
                # Get or create bucket
                try:
                    self.bucket = self.client.get_bucket(bucket_name)
                except NotFound:
                    self.logger.warning(f"Bucket {bucket_name} not found, attempting to create it")
                    self.bucket = self.client.create_bucket(bucket_name)
                
                self.logger.info(f"Using Google Cloud Storage bucket: {bucket_name}")
            
            except Exception as e:
                self.logger.warning(f"Failed to initialize Google Cloud Storage: {str(e)}")
                self.client = None
                self.bucket = None
        
        # If GCS is not available or initialization failed, set up local fallback
        if not self.client and self.use_local_fallback:
            self.logger.info(f"Using local file system fallback at: {self.local_path}")
            os.makedirs(self.local_path, exist_ok=True)
    
    def _get_local_path(self, blob_name: str) -> str:
        """
        Get the local file system path for a blob.
        
        Args:
            blob_name: Name of the blob (remote path in GCS)
            
        Returns:
            Local file system path
        """
        # Convert blob name to local path
        local_file_path = os.path.join(self.local_path, blob_name)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        
        return local_file_path
    
    def upload_file(self, local_file_path: str, blob_name: str,
                  content_type: Optional[str] = None,
                  metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload a file to Cloud Storage.
        
        Args:
            local_file_path: Path to the local file
            blob_name: Name for the blob in Cloud Storage
            content_type: MIME type for the file
            metadata: Custom metadata for the blob
            
        Returns:
            Public URL for the uploaded file
            
        Raises:
            ServiceError: If the upload fails
        """
        if self.bucket:
            try:
                # Upload to GCS
                blob = self.bucket.blob(blob_name)
                
                # Set content type if provided
                if content_type:
                    blob.content_type = content_type
                
                # Set metadata if provided
                if metadata:
                    blob.metadata = metadata
                
                # Upload the file
                blob.upload_from_filename(local_file_path)
                
                # Return the public URL
                return blob.public_url
            
            except Exception as e:
                self.logger.error(f"Failed to upload file to GCS: {str(e)}")
                raise ServiceError(f"Failed to upload file to Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get local path
                destination_path = self._get_local_path(blob_name)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                
                # Copy the file
                with open(local_file_path, 'rb') as source_file:
                    with open(destination_path, 'wb') as dest_file:
                        dest_file.write(source_file.read())
                
                # Store metadata if provided
                if metadata:
                    metadata_path = f"{destination_path}.metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump({
                            'content_type': content_type,
                            'metadata': metadata
                        }, f)
                
                # Return a fake URL
                return f"file://{destination_path}"
            
            except Exception as e:
                self.logger.error(f"Failed to copy file in local fallback: {str(e)}")
                raise ServiceError(f"Failed to copy file in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def download_file(self, blob_name: str, local_file_path: str) -> None:
        """
        Download a file from Cloud Storage.
        
        Args:
            blob_name: Name of the blob in Cloud Storage
            local_file_path: Path where the file should be saved locally
            
        Raises:
            ServiceError: If the download fails
        """
        if self.bucket:
            try:
                # Download from GCS
                blob = self.bucket.blob(blob_name)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Download the file
                blob.download_to_filename(local_file_path)
            
            except Exception as e:
                self.logger.error(f"Failed to download file from GCS: {str(e)}")
                raise ServiceError(f"Failed to download file from Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get local path
                source_path = self._get_local_path(blob_name)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                
                # Copy the file
                with open(source_path, 'rb') as source_file:
                    with open(local_file_path, 'wb') as dest_file:
                        dest_file.write(source_file.read())
            
            except Exception as e:
                self.logger.error(f"Failed to copy file in local fallback: {str(e)}")
                raise ServiceError(f"Failed to copy file in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def read_file(self, blob_name: str, binary_mode: bool = False) -> Union[str, bytes]:
        """
        Read the contents of a file from Cloud Storage.
        
        Args:
            blob_name: Name of the blob in Cloud Storage
            binary_mode: Whether to read in binary mode
            
        Returns:
            File contents as string (text mode) or bytes (binary mode)
            
        Raises:
            ServiceError: If the read fails
        """
        if self.bucket:
            try:
                # Read from GCS
                blob = self.bucket.blob(blob_name)
                
                if binary_mode:
                    # Read as bytes
                    return blob.download_as_bytes()
                else:
                    # Read as text
                    return blob.download_as_text()
            
            except Exception as e:
                self.logger.error(f"Failed to read file from GCS: {str(e)}")
                raise ServiceError(f"Failed to read file from Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get local path
                local_path = self._get_local_path(blob_name)
                
                # Read the file
                mode = 'rb' if binary_mode else 'r'
                with open(local_path, mode) as f:
                    return f.read()
            
            except Exception as e:
                self.logger.error(f"Failed to read file in local fallback: {str(e)}")
                raise ServiceError(f"Failed to read file in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def write_file(self, blob_name: str, content: Union[str, bytes],
                 content_type: Optional[str] = None,
                 metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Write content to a file in Cloud Storage.
        
        Args:
            blob_name: Name for the blob in Cloud Storage
            content: File content (string or bytes)
            content_type: MIME type for the file
            metadata: Custom metadata for the blob
            
        Returns:
            Public URL for the written file
            
        Raises:
            ServiceError: If the write fails
        """
        if self.bucket:
            try:
                # Write to GCS
                blob = self.bucket.blob(blob_name)
                
                # Set content type if provided
                if content_type:
                    blob.content_type = content_type
                
                # Set metadata if provided
                if metadata:
                    blob.metadata = metadata
                
                # Upload the content
                if isinstance(content, str):
                    blob.upload_from_string(content)
                else:
                    blob.upload_from_string(content, content_type=content_type or 'application/octet-stream')
                
                # Return the public URL
                return blob.public_url
            
            except Exception as e:
                self.logger.error(f"Failed to write file to GCS: {str(e)}")
                raise ServiceError(f"Failed to write file to Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get local path
                local_path = self._get_local_path(blob_name)
                
                # Create directory if needed
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # Write the file
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(local_path, mode) as f:
                    f.write(content)
                
                # Store metadata if provided
                if metadata:
                    metadata_path = f"{local_path}.metadata.json"
                    with open(metadata_path, 'w') as f:
                        json.dump({
                            'content_type': content_type,
                            'metadata': metadata
                        }, f)
                
                # Return a fake URL
                return f"file://{local_path}"
            
            except Exception as e:
                self.logger.error(f"Failed to write file in local fallback: {str(e)}")
                raise ServiceError(f"Failed to write file in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def delete_file(self, blob_name: str) -> None:
        """
        Delete a file from Cloud Storage.
        
        Args:
            blob_name: Name of the blob in Cloud Storage
            
        Raises:
            ServiceError: If the delete fails
        """
        if self.bucket:
            try:
                # Delete from GCS
                blob = self.bucket.blob(blob_name)
                blob.delete()
            
            except Exception as e:
                self.logger.error(f"Failed to delete file from GCS: {str(e)}")
                raise ServiceError(f"Failed to delete file from Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get local path
                local_path = self._get_local_path(blob_name)
                
                # Delete the file
                if os.path.exists(local_path):
                    os.remove(local_path)
                
                # Delete metadata file if it exists
                metadata_path = f"{local_path}.metadata.json"
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
            
            except Exception as e:
                self.logger.error(f"Failed to delete file in local fallback: {str(e)}")
                raise ServiceError(f"Failed to delete file in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Check if a file exists in Cloud Storage.
        
        Args:
            blob_name: Name of the blob in Cloud Storage
            
        Returns:
            True if the file exists, False otherwise
        """
        if self.bucket:
            try:
                # Check in GCS
                blob = self.bucket.blob(blob_name)
                return blob.exists()
            
            except Exception as e:
                self.logger.error(f"Failed to check if file exists in GCS: {str(e)}")
                return False
        
        elif self.use_local_fallback:
            try:
                # Get local path
                local_path = self._get_local_path(blob_name)
                
                # Check if file exists
                return os.path.exists(local_path)
            
            except Exception as e:
                self.logger.error(f"Failed to check if file exists in local fallback: {str(e)}")
                return False
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def list_files(self, prefix: Optional[str] = None) -> List[str]:
        """
        List files in Cloud Storage with an optional prefix.
        
        Args:
            prefix: Prefix to filter files by
            
        Returns:
            List of blob names
            
        Raises:
            ServiceError: If the list operation fails
        """
        if self.bucket:
            try:
                # List files in GCS
                blobs = self.bucket.list_blobs(prefix=prefix)
                return [blob.name for blob in blobs]
            
            except Exception as e:
                self.logger.error(f"Failed to list files in GCS: {str(e)}")
                raise ServiceError(f"Failed to list files in Cloud Storage: {str(e)}")
        
        elif self.use_local_fallback:
            try:
                # Get base path
                base_path = self.local_path
                if prefix:
                    base_path = os.path.join(base_path, prefix)
                
                # List files recursively
                result = []
                for root, _, files in os.walk(base_path):
                    for file in files:
                        # Skip metadata files
                        if file.endswith('.metadata.json'):
                            continue
                        
                        # Get relative path
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.local_path)
                        result.append(rel_path)
                
                return result
            
            except Exception as e:
                self.logger.error(f"Failed to list files in local fallback: {str(e)}")
                raise ServiceError(f"Failed to list files in local fallback: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")
    
    def get_signed_url(self, blob_name: str, expiration: int = 3600) -> str:
        """
        Generate a signed URL for temporary access to a file.
        
        Args:
            blob_name: Name of the blob in Cloud Storage
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Signed URL
            
        Raises:
            ServiceError: If URL generation fails
        """
        if self.bucket:
            try:
                # Generate signed URL in GCS
                blob = self.bucket.blob(blob_name)
                return blob.generate_signed_url(
                    version='v4',
                    expiration=datetime.timedelta(seconds=expiration),
                    method='GET'
                )
            
            except Exception as e:
                self.logger.error(f"Failed to generate signed URL in GCS: {str(e)}")
                raise ServiceError(f"Failed to generate signed URL: {str(e)}")
        
        elif self.use_local_fallback:
            # For local fallback, just return a file URL
            try:
                local_path = self._get_local_path(blob_name)
                return f"file://{local_path}"
            
            except Exception as e:
                self.logger.error(f"Failed to generate file URL in local fallback: {str(e)}")
                raise ServiceError(f"Failed to generate file URL: {str(e)}")
        
        else:
            raise ServiceError("Google Cloud Storage is not available and local fallback is disabled")

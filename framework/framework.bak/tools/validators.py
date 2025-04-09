"""
Validators module for the GCP AI Agent Framework.

This module provides utilities for validating input data, including webhook requests
and intent parameters. It helps ensure that incoming data meets expected formats
and contains required fields.

Example usage:
```python
# Validate webhook request
try:
    validate_request(request_json, required_fields=['queryResult', 'session'])
except ValidationError as e:
    # Handle validation error
    print(f"Validation error: {str(e)}")

# Validate parameters
parameters = request_json.get('queryResult', {}).get('parameters', {})
missing_params = validate_parameters(parameters, required_params=['date', 'amount'])
if missing_params:
    # Handle missing parameters
    print(f"Missing parameters: {', '.join(missing_params)}")
```
"""

from typing import Dict, Any, List, Optional, Union, Set

from ..exceptions import ValidationError


def validate_request(request_data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that a webhook request contains all required fields.
    
    Args:
        request_data: Request data to validate
        required_fields: List of required field names (can use dot notation for nested fields)
        
    Raises:
        ValidationError: If any required fields are missing
    """
    missing_fields = []
    
    for field in required_fields:
        # Handle nested fields with dot notation
        if '.' in field:
            parts = field.split('.')
            value = request_data
            
            for part in parts:
                if not isinstance(value, dict) or part not in value:
                    missing_fields.append(field)
                    break
                value = value[part]
        else:
            # Handle top-level fields
            if field not in request_data:
                missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(
            f"Request is missing required fields: {', '.join(missing_fields)}",
            code="missing_fields",
            details={"missing_fields": missing_fields}
        )


def validate_parameters(parameters: Dict[str, Any], required_params: List[str]) -> List[str]:
    """
    Validate that parameter dictionary contains all required parameters.
    
    Args:
        parameters: Parameters dictionary
        required_params: List of required parameter names
        
    Returns:
        List of missing parameter names (empty if all required parameters are present)
    """
    missing_params = []
    
    for param in required_params:
        if param not in parameters or parameters[param] is None or parameters[param] == '':
            missing_params.append(param)
    
    return missing_params


def validate_enum_value(value: str, allowed_values: Union[List[str], Set[str]], field_name: str) -> None:
    """
    Validate that a value is one of the allowed values.
    
    Args:
        value: Value to validate
        allowed_values: List or set of allowed values
        field_name: Name of the field being validated (for error message)
        
    Raises:
        ValidationError: If the value is not in the allowed values
    """
    if value not in allowed_values:
        raise ValidationError(
            f"Invalid value for {field_name}: '{value}'. Allowed values: {', '.join(sorted(allowed_values))}",
            code="invalid_enum_value",
            details={
                "field": field_name,
                "value": value,
                "allowed_values": sorted(allowed_values)
            }
        )


def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None,
                         max_value: Optional[Union[int, float]] = None, field_name: str = "value") -> None:
    """
    Validate that a numeric value is within the specified range.
    
    Args:
        value: Numeric value to validate
        min_value: Minimum allowed value (if None, no minimum)
        max_value: Maximum allowed value (if None, no maximum)
        field_name: Name of the field being validated (for error message)
        
    Raises:
        ValidationError: If the value is outside the allowed range
    """
    if min_value is not None and value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}, got {value}",
            code="value_too_low",
            details={"field": field_name, "value": value, "min_value": min_value}
        )
    
    if max_value is not None and value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}, got {value}",
            code="value_too_high",
            details={"field": field_name, "value": value, "max_value": max_value}
        )


def validate_string_length(value: str, min_length: Optional[int] = None,
                         max_length: Optional[int] = None, field_name: str = "string") -> None:
    """
    Validate that a string value has an acceptable length.
    
    Args:
        value: String value to validate
        min_length: Minimum allowed length (if None, no minimum)
        max_length: Maximum allowed length (if None, no maximum)
        field_name: Name of the field being validated (for error message)
        
    Raises:
        ValidationError: If the string length is outside the allowed range
    """
    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters, got {len(value)}",
            code="string_too_short",
            details={"field": field_name, "length": len(value), "min_length": min_length}
        )
    
    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters, got {len(value)}",
            code="string_too_long",
            details={"field": field_name, "length": len(value), "max_length": max_length}
        )


def validate_list_length(values: List[Any], min_length: Optional[int] = None,
                       max_length: Optional[int] = None, field_name: str = "list") -> None:
    """
    Validate that a list has an acceptable length.
    
    Args:
        values: List to validate
        min_length: Minimum allowed length (if None, no minimum)
        max_length: Maximum allowed length (if None, no maximum)
        field_name: Name of the field being validated (for error message)
        
    Raises:
        ValidationError: If the list length is outside the allowed range
    """
    if min_length is not None and len(values) < min_length:
        raise ValidationError(
            f"{field_name} must contain at least {min_length} items, got {len(values)}",
            code="list_too_short",
            details={"field": field_name, "length": len(values), "min_length": min_length}
        )
    
    if max_length is not None and len(values) > max_length:
        raise ValidationError(
            f"{field_name} must contain at most {max_length} items, got {len(values)}",
            code="list_too_long",
            details={"field": field_name, "length": len(values), "max_length": max_length}
        )

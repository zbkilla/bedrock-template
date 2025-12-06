"""
Amazon Bedrock Agent Action Handler

This Lambda function handles action group invocations from Bedrock Agents.
It processes requests based on the API path and returns formatted responses.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Input validation constants
MAX_RESOURCE_ID_LENGTH = 256
MAX_QUERY_LENGTH = 1000
MAX_LIMIT = 100
RESOURCE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def validate_resource_id(resource_id: Optional[str]) -> str:
    """
    Validate resource ID for security and correctness.

    Args:
        resource_id: The resource ID to validate

    Returns:
        The validated resource ID

    Raises:
        ValidationError: If validation fails
    """
    if not resource_id:
        raise ValidationError("resourceId is required")

    if len(resource_id) > MAX_RESOURCE_ID_LENGTH:
        raise ValidationError(f"resourceId exceeds maximum length of {MAX_RESOURCE_ID_LENGTH}")

    if not RESOURCE_ID_PATTERN.match(resource_id):
        raise ValidationError("resourceId contains invalid characters (only alphanumeric, underscore, hyphen allowed)")

    return resource_id


def validate_query(query: Optional[str]) -> str:
    """
    Validate search query for security and correctness.

    Args:
        query: The search query to validate

    Returns:
        The validated and sanitized query

    Raises:
        ValidationError: If validation fails
    """
    if not query:
        raise ValidationError("query is required")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValidationError(f"query exceeds maximum length of {MAX_QUERY_LENGTH}")

    # Sanitize: remove potential injection patterns
    sanitized = query.strip()

    return sanitized


def validate_limit(limit_str: Optional[str]) -> int:
    """
    Validate and convert limit parameter.

    Args:
        limit_str: The limit as a string

    Returns:
        The validated limit as an integer

    Raises:
        ValidationError: If validation fails
    """
    if not limit_str:
        return 10  # Default

    try:
        limit = int(limit_str)
    except ValueError:
        raise ValidationError("limit must be a valid integer")

    if limit < 1 or limit > MAX_LIMIT:
        raise ValidationError(f"limit must be between 1 and {MAX_LIMIT}")

    return limit


def validate_action(action: Optional[str]) -> str:
    """
    Validate action parameter.

    Args:
        action: The action to validate

    Returns:
        The validated action

    Raises:
        ValidationError: If validation fails
    """
    allowed_actions = {'start', 'stop', 'restart', 'update'}

    if not action:
        raise ValidationError("action is required")

    if action not in allowed_actions:
        raise ValidationError(f"action must be one of: {', '.join(allowed_actions)}")

    return action


def lambda_handler(event: dict, context: Any) -> dict:
    """
    Main handler for Bedrock Agent action group invocations.

    Args:
        event: The event from Bedrock Agent containing:
            - actionGroup: Name of the action group
            - apiPath: The API endpoint being called
            - httpMethod: HTTP method (GET, POST, etc.)
            - parameters: List of parameters with name/value pairs
            - requestBody: Request body for POST requests
        context: Lambda context object

    Returns:
        Formatted response for Bedrock Agent
    """
    logger.info(f"Received event: {json.dumps(event)}")

    action_group = event.get('actionGroup', '')
    api_path = event.get('apiPath', '')
    http_method = event.get('httpMethod', '')
    parameters = event.get('parameters', [])
    request_body = event.get('requestBody', {})

    # Route to appropriate handler
    try:
        if api_path == '/getStatus':
            result = handle_get_status(parameters)
        elif api_path == '/executeAction':
            result = handle_execute_action(request_body)
        elif api_path == '/search':
            result = handle_search(parameters)
        else:
            result = {"error": f"Unknown API path: {api_path}"}

    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        result = {"error": str(e)}

    except Exception as e:
        logger.error(f"Internal error handling request: {str(e)}")
        # Don't expose internal error details to client
        result = {"error": "An internal error occurred"}

    # Format response for Bedrock Agent
    return format_response(action_group, api_path, http_method, result)


def handle_get_status(parameters: List) -> Dict:
    """Handle getStatus API calls."""
    resource_id = get_parameter(parameters, 'resourceId')

    # Validate input
    resource_id = validate_resource_id(resource_id)

    # Implement your status lookup logic here
    return {
        "resourceId": resource_id,
        "status": "active",
        "lastUpdated": datetime.utcnow().isoformat()
    }


def handle_execute_action(request_body: Dict) -> Dict:
    """Handle executeAction API calls."""
    content = request_body.get('content', {})
    body = json.loads(content.get('application/json', {}).get('body', '{}'))

    resource_id = body.get('resourceId')
    action = body.get('action')
    params = body.get('parameters', {})

    # Validate inputs
    resource_id = validate_resource_id(resource_id)
    action = validate_action(action)

    # Implement your action execution logic here
    return {
        "success": True,
        "message": f"Action '{action}' executed on resource '{resource_id}'",
        "result": {
            "resourceId": resource_id,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


def handle_search(parameters: List) -> Dict:
    """Handle search API calls."""
    query = get_parameter(parameters, 'query')
    limit_str = get_parameter(parameters, 'limit', '10')

    # Validate inputs
    query = validate_query(query)
    limit = validate_limit(limit_str)

    # Implement your search logic here
    return {
        "results": [
            {"id": "1", "name": f"Result matching '{query}'", "score": 0.95},
            {"id": "2", "name": f"Another result for '{query}'", "score": 0.87},
        ],
        "total": 2,
        "limit": limit
    }


def get_parameter(parameters: list, name: str, default: str = None) -> str:
    """Extract a parameter value from the parameters list."""
    for param in parameters:
        if param.get('name') == name:
            return param.get('value', default)
    return default


def format_response(action_group: str, api_path: str, http_method: str, body: dict) -> dict:
    """Format the response for Bedrock Agent."""
    return {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': http_method,
            'httpStatusCode': 200 if 'error' not in body else 400,
            'responseBody': {
                'application/json': {
                    'body': json.dumps(body)
                }
            }
        }
    }

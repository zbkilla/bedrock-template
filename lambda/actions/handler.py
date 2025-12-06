"""
Amazon Bedrock Agent Action Handler

This Lambda function handles action group invocations from Bedrock Agents.
It processes requests based on the API path and returns formatted responses.
"""

import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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

    except Exception as e:
        logger.error(f"Error handling request: {str(e)}")
        result = {"error": str(e)}

    # Format response for Bedrock Agent
    return format_response(action_group, api_path, http_method, result)


def handle_get_status(parameters: list) -> dict:
    """Handle getStatus API calls."""
    resource_id = get_parameter(parameters, 'resourceId')

    if not resource_id:
        return {"error": "resourceId is required"}

    # Implement your status lookup logic here
    return {
        "resourceId": resource_id,
        "status": "active",
        "lastUpdated": datetime.utcnow().isoformat()
    }


def handle_execute_action(request_body: dict) -> dict:
    """Handle executeAction API calls."""
    content = request_body.get('content', {})
    body = json.loads(content.get('application/json', {}).get('body', '{}'))

    resource_id = body.get('resourceId')
    action = body.get('action')
    params = body.get('parameters', {})

    if not resource_id or not action:
        return {"error": "resourceId and action are required"}

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


def handle_search(parameters: list) -> dict:
    """Handle search API calls."""
    query = get_parameter(parameters, 'query')
    limit = int(get_parameter(parameters, 'limit', '10'))

    if not query:
        return {"error": "query is required"}

    # Implement your search logic here
    return {
        "results": [
            {"id": "1", "name": f"Result matching '{query}'", "score": 0.95},
            {"id": "2", "name": f"Another result for '{query}'", "score": 0.87},
        ],
        "total": 2
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

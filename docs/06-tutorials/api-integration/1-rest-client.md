# Tutorial: REST Client

**Time:** 20 minutes | **Level:** Beginner  
**Goal:** Build REST API clients for CORTEX

## Overview

The CORTEX REST API provides HTTP endpoints for all orchestrator operations. This tutorial covers basic client setup and common operations.

## Prerequisites

- Python 3.8+
- `requests` library installed
- CORTEX server running locally

## Step 1: Basic Setup

```python
import requests
from typing import Dict, Any

class CortexClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def execute_orchestrator(
        self,
        orchestrator: str,
        content: str,
        user_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute an orchestrator via REST API."""
        response = self.session.post(
            f"{self.base_url}/orchestrators/{orchestrator}/execute",
            json={
                "content": content,
                "user_id": user_id,
                **kwargs
            }
        )
        response.raise_for_status()
        return response.json()
```

## Step 2: Execute Orchestrator

```python
client = CortexClient()

response = client.execute_orchestrator(
    orchestrator="hello_world",
    content="Hello",
    user_id="alice"
)

print(f"Status: {response['status']}")
print(f"Content: {response['content']}")
```

## Step 3: Error Handling

```python
import logging

logger = logging.getLogger(__name__)

def execute_with_retry(client, orchestrator, content, user_id, max_retries=3):
    """Execute with retry logic."""
    for attempt in range(max_retries):
        try:
            return client.execute_orchestrator(
                orchestrator=orchestrator,
                content=content,
                user_id=user_id
            )
        except requests.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
        except requests.HTTPError as e:
            if e.response.status_code >= 500:
                logger.warning(f"Server error on attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    raise
            else:
                raise
```

## Step 4: Batch Requests

```python
def execute_batch(
    client,
    orchestrator: str,
    items: list,
    user_id: str
) -> list:
    """Execute multiple orchestrator calls."""
    results = []
    for item in items:
        response = client.execute_orchestrator(
            orchestrator=orchestrator,
            content=item,
            user_id=user_id
        )
        results.append(response)
    return results

# Usage
items = ["item1", "item2", "item3"]
results = execute_batch(
    client,
    "hello_world",
    items,
    "alice"
)
```

## Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orchestrators/{id}/execute` | POST | Execute orchestrator |
| `/orchestrators` | GET | List orchestrators |
| `/knowledge/query` | GET | Query Domain Brain |
| `/governance/check` | POST | Check governance |

## Authentication

For production:

```python
from requests.auth import HTTPBasicAuth

client = CortexClient()
client.session.auth = HTTPBasicAuth("username", "password")
```

## Next Steps

- [MCP Integration](2-mcp-integration.md) - JSON-RPC integration
- [REST API Reference](../../03-api-reference/rest-api/0-guide.md) - Full API docs

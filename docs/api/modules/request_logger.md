# request_logger

CORTEX Tier 1: Request Logger
Logs raw requests and responses

Task 1.6: Raw Request Logging
Duration: 30 minutes


## Table of Contents

### Classes
- [RequestLogger](#requestlogger)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, random, typing


## Classes

### RequestLogger

```python
class RequestLogger
```

Logs raw requests and responses to JSONL file

Responsibilities:
- Log user requests with timestamps
- Log system responses
- Track request/response pairs
- Support conversation association


**Methods:**

  #### `log_request`

  ```python
  log_request(self, request_text: str, conversation_id: Optional[str], intent: Optional[str], metadata: Optional[Dict]) -> str
  ```

  Log a user request

Args:
    request_text: The request text
    conversation_id: Associated conversation
    intent: Detected intent
    metadata: Additional metadata
    
Returns:
    request_id: Generated request ID

  **Parameters:**

  - `self`
  - `request_text` (str): The request text
  - `conversation_id` (Optional[str]) = `None`: Associated conversation
  - `intent` (Optional[str]) = `None`: Detected intent
  - `metadata` (Optional[Dict]) = `None`: Additional metadata


  **Returns:** str
    request_id: Generated request ID


  #### `log_response`

  ```python
  log_response(self, request_id: str, response_text: str, conversation_id: Optional[str], status: str, metadata: Optional[Dict])
  ```

  Log a system response

Args:
    request_id: Associated request ID
    response_text: The response text
    conversation_id: Associated conversation
    status: Response status (success, error, partial)
    metadata: Additional metadata

  **Parameters:**

  - `self`
  - `request_id` (str): Associated request ID
  - `response_text` (str): The response text
  - `conversation_id` (Optional[str]) = `None`: Associated conversation
  - `status` (str) = `'success'`: Response status (success, error, partial)
  - `metadata` (Optional[Dict]) = `None`: Additional metadata


  #### `log_error`

  ```python
  log_error(self, request_id: str, error_message: str, conversation_id: Optional[str], error_type: Optional[str], metadata: Optional[Dict])
  ```

  Log an error

Args:
    request_id: Associated request ID
    error_message: Error description
    conversation_id: Associated conversation
    error_type: Type of error
    metadata: Additional metadata

  **Parameters:**

  - `self`
  - `request_id` (str): Associated request ID
  - `error_message` (str): Error description
  - `conversation_id` (Optional[str]) = `None`: Associated conversation
  - `error_type` (Optional[str]) = `None`: Type of error
  - `metadata` (Optional[Dict]) = `None`: Additional metadata


  #### `get_recent_requests`

  ```python
  get_recent_requests(self, limit: int) -> list
  ```

  Get recent requests

Args:
    limit: Maximum number to retrieve
    
Returns:
    List of request entries

  **Parameters:**

  - `self`
  - `limit` (int) = `100`: Maximum number to retrieve


  **Returns:** list
    List of request entries


  #### `get_request_response_pair`

  ```python
  get_request_response_pair(self, request_id: str) -> Dict
  ```

  Get request and response for a request ID

Args:
    request_id: Request ID to find
    
Returns:
    Dictionary with request and response

  **Parameters:**

  - `self`
  - `request_id` (str): Request ID to find


  **Returns:** Dict
    Dictionary with request and response


  #### `get_conversation_requests`

  ```python
  get_conversation_requests(self, conversation_id: str) -> list
  ```

  Get all requests for a conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    List of request entries

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID


  **Returns:** list
    List of request entries


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict
  ```

  Get request logging statistics

Returns:
    Statistics dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict
    Statistics dictionary



---

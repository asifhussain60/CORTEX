# tier1_api

CORTEX Tier 1: API Wrapper
Unified API for Tier 1 Working Memory operations

Task 1.5: CRUD Operations API
Duration: 1.5 hours


## Table of Contents

### Classes
- [Tier1API](#tier1api)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** conversation_manager, datetime, entity_extractor, file_tracker, pathlib, request_logger, typing


## Classes

### Tier1API

```python
class Tier1API
```

Unified API for Tier 1 Working Memory

Provides high-level interface for:
- Conversation management
- Entity extraction
- File tracking
- Request logging


**Methods:**

  #### `start_conversation`

  ```python
  start_conversation(self, agent_id: str, goal: Optional[str], context: Optional[Dict]) -> str
  ```

  Start a new conversation with automatic entity extraction

Args:
    agent_id: Agent identifier
    goal: Conversation goal (optional)
    context: Additional context (optional)
    
Returns:
    conversation_id: New conversation ID

  **Parameters:**

  - `self`
  - `agent_id` (str): Agent identifier
  - `goal` (Optional[str]) = `None`: Conversation goal (optional)
  - `context` (Optional[Dict]) = `None`: Additional context (optional)


  **Returns:** str
    conversation_id: New conversation ID


  #### `process_message`

  ```python
  process_message(self, conversation_id: str, role: str, content: str, extract_entities: bool, track_files: bool, log_request: bool) -> Dict
  ```

  Process a message with automatic extraction and tracking

Args:
    conversation_id: Conversation ID
    role: Message role (user/assistant)
    content: Message content
    extract_entities: Extract entities from content
    track_files: Track file references
    log_request: Log to request log
    
Returns:
    Processing results with message_id and extracted data

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `role` (str): Message role (user/assistant)
  - `content` (str): Message content
  - `extract_entities` (bool) = `True`: Extract entities from content
  - `track_files` (bool) = `True`: Track file references
  - `log_request` (bool) = `True`: Log to request log


  **Returns:** Dict
    Processing results with message_id and extracted data


  #### `end_conversation`

  ```python
  end_conversation(self, conversation_id: str, outcome: Optional[str]) -> Dict
  ```

  End a conversation with summary

Args:
    conversation_id: Conversation ID
    outcome: Conversation outcome
    
Returns:
    Conversation summary

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `outcome` (Optional[str]) = `None`: Conversation outcome


  **Returns:** Dict
    Conversation summary


  #### `get_active_conversation`

  ```python
  get_active_conversation(self, agent_id: str) -> Optional[Dict]
  ```

  Get active conversation for agent

Args:
    agent_id: Agent identifier
    
Returns:
    Active conversation or None

  **Parameters:**

  - `self`
  - `agent_id` (str): Agent identifier


  **Returns:** Optional[Dict]
    Active conversation or None


  #### `get_conversation_history`

  ```python
  get_conversation_history(self, conversation_id: str, include_entities: bool, include_files: bool) -> Dict
  ```

  Get full conversation history

Args:
    conversation_id: Conversation ID
    include_entities: Include extracted entities
    include_files: Include file references
    
Returns:
    Complete conversation data

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `include_entities` (bool) = `True`: Include extracted entities
  - `include_files` (bool) = `True`: Include file references


  **Returns:** Dict
    Complete conversation data


  #### `search_conversations`

  ```python
  search_conversations(self, agent_id: Optional[str], start_date: Optional[datetime], end_date: Optional[datetime], has_goal: Optional[bool]) -> List[Dict]
  ```

  Search conversations by criteria

Args:
    agent_id: Filter by agent
    start_date: Start date filter
    end_date: End date filter
    has_goal: Filter by presence of goal
    
Returns:
    List of matching conversations

  **Parameters:**

  - `self`
  - `agent_id` (Optional[str]) = `None`: Filter by agent
  - `start_date` (Optional[datetime]) = `None`: Start date filter
  - `end_date` (Optional[datetime]) = `None`: End date filter
  - `has_goal` (Optional[bool]) = `None`: Filter by presence of goal


  **Returns:** List[Dict]
    List of matching conversations


  #### `extract_entities_from_text`

  ```python
  extract_entities_from_text(self, text: str) -> Dict
  ```

  Extract all entities from text

Args:
    text: Text to analyze
    
Returns:
    Dictionary of extracted entities by type

  **Parameters:**

  - `self`
  - `text` (str): Text to analyze


  **Returns:** Dict
    Dictionary of extracted entities by type


  #### `get_entity_frequency`

  ```python
  get_entity_frequency(self, conversation_id: str, entity_type: Optional[str]) -> Dict
  ```

  Get entity frequency for conversation

Args:
    conversation_id: Conversation ID
    entity_type: Filter by type (optional)
    
Returns:
    Entity frequency counts

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `entity_type` (Optional[str]) = `None`: Filter by type (optional)


  **Returns:** Dict
    Entity frequency counts


  #### `track_file_modification`

  ```python
  track_file_modification(self, conversation_id: str, file_path: str, operation: str)
  ```

  Track a file modification

Args:
    conversation_id: Conversation ID
    file_path: Path to file
    operation: Operation type (created, modified, deleted)

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `file_path` (str): Path to file
  - `operation` (str) = `'modified'`: Operation type (created, modified, deleted)


  #### `get_file_patterns`

  ```python
  get_file_patterns(self, conversation_id: str) -> Dict
  ```

  Get file patterns for conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    File patterns and statistics

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID


  **Returns:** Dict
    File patterns and statistics


  #### `log_response`

  ```python
  log_response(self, request_id: str, response_text: str, status: str)
  ```

  Log a response to a request

Args:
    request_id: Request ID
    response_text: Response content
    status: Response status

  **Parameters:**

  - `self`
  - `request_id` (str): Request ID
  - `response_text` (str): Response content
  - `status` (str) = `'success'`: Response status


  #### `log_error`

  ```python
  log_error(self, request_id: str, error_message: str, error_type: Optional[str])
  ```

  Log an error for a request

Args:
    request_id: Request ID
    error_message: Error description
    error_type: Error type

  **Parameters:**

  - `self`
  - `request_id` (str): Request ID
  - `error_message` (str): Error description
  - `error_type` (Optional[str]) = `None`: Error type


  #### `get_request_history`

  ```python
  get_request_history(self, conversation_id: Optional[str], limit: int) -> List[Dict]
  ```

  Get request history

Args:
    conversation_id: Filter by conversation (optional)
    limit: Maximum results
    
Returns:
    List of requests

  **Parameters:**

  - `self`
  - `conversation_id` (Optional[str]) = `None`: Filter by conversation (optional)
  - `limit` (int) = `100`: Maximum results


  **Returns:** List[Dict]
    List of requests


  #### `export_conversation_to_jsonl`

  ```python
  export_conversation_to_jsonl(self, conversation_id: str, output_path: Path)
  ```

  Export conversation to JSONL format

Args:
    conversation_id: Conversation ID
    output_path: Output file path

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID
  - `output_path` (Path): Output file path


  #### `get_tier1_statistics`

  ```python
  get_tier1_statistics(self) -> Dict
  ```

  Get comprehensive Tier 1 statistics

Returns:
    Statistics dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict
    Statistics dictionary



---

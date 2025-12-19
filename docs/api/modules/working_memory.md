# working_memory

CORTEX Tier 1: Working Memory (Modularized)
Short-term memory storage with FIFO queue (20 conversation limit).

This is a facade that coordinates between modular components while maintaining
backward compatibility with the original API.


## Table of Contents

### Classes
- [WorkingMemory](#workingmemory)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** cache_monitor, conversation_quality, conversations, datetime, entities, fifo, hashlib, json, lifecycle, messages, ml_context_optimizer, pathlib, random, session_correlation, sessions, sqlite3, src, time, token_metrics, traceback, typing


## Classes

### WorkingMemory

```python
class WorkingMemory
```

Tier 1: Working Memory (Short-Term Memory) - Modular Facade

Manages recent conversations with FIFO eviction when capacity (70) is reached.
Stores conversations, messages, and extracted entities in SQLite.

This class acts as a facade, delegating to specialized modules while
maintaining full backward compatibility with the original API.


**Methods:**

  #### `initialize`

  ```python
  initialize(self) -> bool
  ```

  Initialize the working memory system.

Returns:
    True if initialization successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if initialization successful, False otherwise


  #### `get_optimized_context`

  ```python
  get_optimized_context(self, conversation_id: Optional[str], pattern_context: Optional[List[Dict[str, Any]]], target_reduction: Optional[float]) -> Dict[str, Any]
  ```

  Get optimized context for a request (Phase 1.5 integration).

Retrieves conversation and pattern context, applies ML-based optimization
to reduce token usage while maintaining quality, and tracks metrics.

Args:
    conversation_id: Optional conversation to optimize. If None, uses active.
    pattern_context: Optional list of knowledge graph patterns to optimize.
    target_reduction: Optional target reduction ratio (0.0-1.0). Uses config default if None.

Returns:
    Dict with:
        - original_context: Original unoptimized context
        - optimized_context: ML-optimized context (if enabled)
        - optimization_stats: Metrics (token counts, reduction rate, quality score)
        - cache_health: Current cache health report

  **Parameters:**

  - `self`
  - `conversation_id` (Optional[str]) = `None`: Optional conversation to optimize. If None, uses active.
  - `pattern_context` (Optional[List[Dict[str, Any]]]) = `None`: Optional list of knowledge graph patterns to optimize.
  - `target_reduction` (Optional[float]) = `None`: Optional target reduction ratio (0.0-1.0). Uses config default if None.


  **Returns:** Dict[str, Any]
    Dict with: - original_context: Original unoptimized context - optimized_context: ML-optimized context (if enabled) - optimization_stats: Metrics (token counts, reduction rate, quality score) - cache_health: Current cache health report


  #### `get_token_metrics_summary`

  ```python
  get_token_metrics_summary(self) -> Dict[str, Any]
  ```

  Get current token optimization metrics summary (Phase 1.5).

Returns:
    Dict with session metrics, cost savings, and optimization performance.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with session metrics, cost savings, and optimization performance.


  #### `get_cache_health_report`

  ```python
  get_cache_health_report(self) -> Dict[str, Any]
  ```

  Get current cache health report (Phase 1.5).

Returns:
    Cache health report with token counts, limits, and recommendations.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Cache health report with token counts, limits, and recommendations.


  #### `add_conversation`

  ```python
  add_conversation(self, conversation_id: str, title: str, messages: List[Dict[str, str]], tags: Optional[List[str]]) -> Conversation
  ```

  Add a new conversation to working memory.

Args:
    conversation_id: Unique conversation identifier
    title: Conversation title
    messages: List of message dicts with 'role' and 'content'
    tags: Optional list of tags

Returns:
    Created Conversation object

  **Parameters:**

  - `self`
  - `conversation_id` (str): Unique conversation identifier
  - `title` (str): Conversation title
  - `messages` (List[Dict[str, str]]): List of message dicts with 'role' and 'content'
  - `tags` (Optional[List[str]]) = `None`: Optional list of tags


  **Returns:** Conversation
    Created Conversation object


  #### `get_conversation`

  ```python
  get_conversation(self, conversation_id: str) -> Optional[Conversation]
  ```

  Get a conversation by ID.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** Optional[Conversation]


  #### `get_recent_conversations`

  ```python
  get_recent_conversations(self, limit: int) -> List[Conversation]
  ```

  Get recent conversations ordered by creation date (newest first).

  **Parameters:**

  - `self`
  - `limit` (int) = `20`


  **Returns:** List[Conversation]


  #### `set_active_conversation`

  ```python
  set_active_conversation(self, conversation_id: str) -> None
  ```

  Mark a conversation as active.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** None


  #### `get_active_conversation`

  ```python
  get_active_conversation(self) -> Optional[Conversation]
  ```

  Get the currently active conversation.

  **Parameters:**

  - `self`


  **Returns:** Optional[Conversation]


  #### `update_conversation`

  ```python
  update_conversation(self, conversation_id: str, title: Optional[str], summary: Optional[str], tags: Optional[List[str]]) -> None
  ```

  Update conversation properties.

  **Parameters:**

  - `self`
  - `conversation_id` (str)
  - `title` (Optional[str]) = `None`
  - `summary` (Optional[str]) = `None`
  - `tags` (Optional[List[str]]) = `None`


  **Returns:** None


  #### `get_conversation_count`

  ```python
  get_conversation_count(self) -> int
  ```

  Get the total number of conversations in working memory.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `detect_or_create_session`

  ```python
  detect_or_create_session(self, workspace_path: str) -> Session
  ```

  Detect or create workspace session (CORTEX 3.0).

Creates new session if:
- No active session for workspace
- Idle gap exceeds threshold (default 2 hours)
- Previous session ended

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session object

  **Parameters:**

  - `self`
  - `workspace_path` (str): Absolute path to workspace


  **Returns:** Session
    Active Session object


  #### `get_active_session`

  ```python
  get_active_session(self, workspace_path: str) -> Optional[Session]
  ```

  Get active session for workspace.

  **Parameters:**

  - `self`
  - `workspace_path` (str)


  **Returns:** Optional[Session]


  #### `end_session`

  ```python
  end_session(self, session_id: str, reason: str) -> None
  ```

  End a workspace session.

Args:
    session_id: Session to end
    reason: Reason for ending (manual, idle_timeout, workspace_close)

  **Parameters:**

  - `self`
  - `session_id` (str): Session to end
  - `reason` (str) = `'manual'`: Reason for ending (manual, idle_timeout, workspace_close)


  **Returns:** None


  #### `get_session`

  ```python
  get_session(self, session_id: str) -> Optional[Session]
  ```

  Get session by ID.

  **Parameters:**

  - `self`
  - `session_id` (str)


  **Returns:** Optional[Session]


  #### `get_recent_sessions`

  ```python
  get_recent_sessions(self, workspace_path: Optional[str], limit: int) -> List[Session]
  ```

  Get recent sessions, optionally filtered by workspace.

  **Parameters:**

  - `self`
  - `workspace_path` (Optional[str]) = `None`
  - `limit` (int) = `10`


  **Returns:** List[Session]


  #### `handle_user_request`

  ```python
  handle_user_request(self, user_request: str, workspace_path: str, assistant_response: Optional[str], context: Optional[Dict[str, Any]]) -> Dict[str, Any]
  ```

  Handle user request with full session-based lifecycle management.

This is the primary entry point for CORTEX 3.0 session-based conversations.
Automatically:
- Detects or creates session
- Creates new conversation or continues existing
- Tracks workflow state progression
- Closes conversations when workflow complete
- Respects explicit user commands ("new conversation", "continue")

Args:
    user_request: User's message
    workspace_path: Absolute path to workspace
    assistant_response: Optional assistant's response
    context: Optional additional context

Returns:
    Dict with:
        - session_id: Active session ID
        - conversation_id: Active conversation ID
        - is_new_conversation: Whether conversation was just created
        - is_new_session: Whether session was just created
        - workflow_state: Current workflow state
        - lifecycle_event: Lifecycle event that occurred

  **Parameters:**

  - `self`
  - `user_request` (str): User's message
  - `workspace_path` (str): Absolute path to workspace
  - `assistant_response` (Optional[str]) = `None`: Optional assistant's response
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional additional context


  **Returns:** Dict[str, Any]
    Dict with: - session_id: Active session ID - conversation_id: Active conversation ID - is_new_conversation: Whether conversation was just created - is_new_session: Whether session was just created - workflow_state: Current workflow state - lifecycle_event: Lifecycle event that occurred


  #### `get_conversation_lifecycle_history`

  ```python
  get_conversation_lifecycle_history(self, conversation_id: str)
  ```

  Get lifecycle history for a conversation.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  #### `get_session_lifecycle_history`

  ```python
  get_session_lifecycle_history(self, session_id: str)
  ```

  Get all conversation lifecycle events for a session.

  **Parameters:**

  - `self`
  - `session_id` (str)


  #### `log_ambient_event`

  ```python
  log_ambient_event(self, session_id: str, event_type: str, file_path: Optional[str], pattern: Optional[str], score: Optional[int], summary: Optional[str], conversation_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> int
  ```

  Log ambient capture event linked to session.

Use this to record file changes, terminal commands, git operations
that occur during a development session.

Args:
    session_id: Active workspace session ID
    event_type: Type of event (file_change, terminal_command, git_operation)
    file_path: Path to affected file
    pattern: Detected pattern (FEATURE, BUGFIX, REFACTOR, etc.)
    score: Activity score (0-100)
    summary: Natural language summary
    conversation_id: Optional active conversation ID
    metadata: Additional event metadata
    
Returns:
    Event ID

  **Parameters:**

  - `self`
  - `session_id` (str): Active workspace session ID
  - `event_type` (str): Type of event (file_change, terminal_command, git_operation)
  - `file_path` (Optional[str]) = `None`: Path to affected file
  - `pattern` (Optional[str]) = `None`: Detected pattern (FEATURE, BUGFIX, REFACTOR, etc.)
  - `score` (Optional[int]) = `None`: Activity score (0-100)
  - `summary` (Optional[str]) = `None`: Natural language summary
  - `conversation_id` (Optional[str]) = `None`: Optional active conversation ID
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional event metadata


  **Returns:** int
    Event ID


  #### `get_session_events`

  ```python
  get_session_events(self, session_id: str, event_type: Optional[str], min_score: Optional[int]) -> List[Dict[str, Any]]
  ```

  Get all ambient events for a session.

Args:
    session_id: Session ID to query
    event_type: Optional filter by event type
    min_score: Optional minimum activity score
    
Returns:
    List of events with metadata

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID to query
  - `event_type` (Optional[str]) = `None`: Optional filter by event type
  - `min_score` (Optional[int]) = `None`: Optional minimum activity score


  **Returns:** List[Dict[str, Any]]
    List of events with metadata


  #### `get_conversation_events`

  ```python
  get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]
  ```

  Get all ambient events that occurred during a conversation.

This shows what actually happened (file changes, commands, git ops)
while the conversation was active.

Args:
    conversation_id: Conversation ID to query
    
Returns:
    List of events with metadata

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID to query


  **Returns:** List[Dict[str, Any]]
    List of events with metadata


  #### `generate_session_narrative`

  ```python
  generate_session_narrative(self, session_id: str) -> str
  ```

  Generate complete development narrative for a session.

Combines conversations + ambient events into a coherent story
of what happened during the development session.

Args:
    session_id: Session ID to narrate
    
Returns:
    Natural language narrative (Markdown format)

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID to narrate


  **Returns:** str
    Natural language narrative (Markdown format)


  #### `import_conversation`

  ```python
  import_conversation(self, conversation_turns: List[Dict[str, str]], import_source: str, workspace_path: Optional[str], import_date: Optional[datetime]) -> Dict[str, Any]
  ```

  Import a manually captured conversation to CORTEX brain.

Part of CORTEX 3.0's dual-channel memory system:
- Channel 1: Ambient daemon (execution-focused, automatic)
- Channel 2: Manual import (strategy-focused, user-driven)

Args:
    conversation_turns: List of conversation turns with 'user' and 'assistant' keys
    import_source: Source file path or identifier
    workspace_path: Optional workspace path to link conversation to session
    import_date: Optional import timestamp (defaults to now)
    
Returns:
    Dict with import results: {
        'success': bool,
        'conversation_id': str,
        'session_id': str,
        'quality_score': int,
        'quality_level': str,
        'semantic_elements': dict,
        'turns_imported': int
    }

  **Parameters:**

  - `self`
  - `conversation_turns` (List[Dict[str, str]]): List of conversation turns with 'user' and 'assistant' keys
  - `import_source` (str): Source file path or identifier
  - `workspace_path` (Optional[str]) = `None`: Optional workspace path to link conversation to session
  - `import_date` (Optional[datetime]) = `None`: Optional import timestamp (defaults to now)


  **Returns:** Dict[str, Any]
    Dict with import results: { 'success': bool, 'conversation_id': str, 'session_id': str, 'quality_score': int, 'quality_level': str, 'semantic_elements': dict, 'turns_imported': int }


  #### `get_messages`

  ```python
  get_messages(self, conversation_id: str) -> List[Dict[str, Any]]
  ```

  Get all messages for a conversation.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** List[Dict[str, Any]]


  #### `add_messages`

  ```python
  add_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> None
  ```

  Append new messages to an existing conversation.

  **Parameters:**

  - `self`
  - `conversation_id` (str)
  - `messages` (List[Dict[str, str]])


  **Returns:** None


  #### `extract_entities`

  ```python
  extract_entities(self, conversation_id: str) -> List[Entity]
  ```

  Extract entities from a conversation's messages.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** List[Entity]


  #### `get_conversation_entities`

  ```python
  get_conversation_entities(self, conversation_id: str) -> List[Entity]
  ```

  Get all entities associated with a conversation.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** List[Entity]


  #### `get_entity_statistics`

  ```python
  get_entity_statistics(self) -> List[Dict[str, Any]]
  ```

  Get statistics on entity usage.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]


  #### `search_conversations`

  ```python
  search_conversations(self, keyword: str) -> List[Conversation]
  ```

  Search conversations by keyword in title or messages.

  **Parameters:**

  - `self`
  - `keyword` (str)


  **Returns:** List[Conversation]


  #### `find_conversations_with_entity`

  ```python
  find_conversations_with_entity(self, entity_type: EntityType, entity_name: str) -> List[Conversation]
  ```

  Find conversations that mention a specific entity.

  **Parameters:**

  - `self`
  - `entity_type` (EntityType)
  - `entity_name` (str)


  **Returns:** List[Conversation]


  #### `get_conversations_by_date_range`

  ```python
  get_conversations_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Conversation]
  ```

  Get conversations within a date range.

  **Parameters:**

  - `self`
  - `start_date` (datetime)
  - `end_date` (datetime)


  **Returns:** List[Conversation]


  #### `get_eviction_log`

  ```python
  get_eviction_log(self) -> List[Dict[str, Any]]
  ```

  Get the eviction log.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]


  #### `store_conversation`

  ```python
  store_conversation(self, user_message: str, assistant_response: str, intent: str, context: Optional[Dict[str, Any]]) -> str
  ```

  Store a conversation with user message and assistant response.
Convenience method for external integrations (like conversation capture).

Args:
    user_message: User's message content
    assistant_response: Assistant's response content
    intent: Detected intent (EXECUTE, PLAN, FIX, etc.)
    context: Optional context metadata
    
Returns:
    Generated conversation ID

  **Parameters:**

  - `self`
  - `user_message` (str): User's message content
  - `assistant_response` (str): Assistant's response content
  - `intent` (str): Detected intent (EXECUTE, PLAN, FIX, etc.)
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context metadata


  **Returns:** str
    Generated conversation ID


  #### `close`

  ```python
  close(self) -> None
  ```

  Close any open connections (for cleanup in tests).

  **Parameters:**

  - `self`


  **Returns:** None


  #### `create_profile`

  ```python
  create_profile(self, interaction_mode: str, experience_level: str, tech_stack_preference: Optional[Dict[str, str]]) -> bool
  ```

  Create user profile with interaction preferences.

Args:
    interaction_mode: How user prefers to interact (autonomous/guided/educational/pair)
    experience_level: User's development experience (junior/mid/senior/expert)
    tech_stack_preference: Optional company tech stack context (not constraint)
        {
            "cloud_provider": "azure|aws|gcp|none",
            "container_platform": "kubernetes|docker|none",
            "architecture": "microservices|monolithic|hybrid",
            "ci_cd": "azure_devops|github_actions|jenkins|none",
            "iac": "terraform|arm|cloudformation|none"
        }
    
Returns:
    True if profile created successfully, False otherwise

  **Parameters:**

  - `self`
  - `interaction_mode` (str) = `'guided'`: How user prefers to interact (autonomous/guided/educational/pair)
  - `experience_level` (str) = `'mid'`: User's development experience (junior/mid/senior/expert)
  - `tech_stack_preference` (Optional[Dict[str, str]]) = `None`: Optional company tech stack context (not constraint) {


  **Returns:** bool
    True if profile created successfully, False otherwise


  #### `get_profile`

  ```python
  get_profile(self) -> Optional[Dict[str, Any]]
  ```

  Retrieve current user profile.

Returns:
    Profile dict with interaction_mode, experience_level, tech_stack_preference, created_at, last_updated
    None if no profile exists

  **Parameters:**

  - `self`


  **Returns:** Optional[Dict[str, Any]]
    Profile dict with interaction_mode, experience_level, tech_stack_preference, created_at, last_updated None if no profile exists


  #### `update_profile`

  ```python
  update_profile(self, interaction_mode: Optional[str], experience_level: Optional[str], tech_stack_preference: Optional[Dict[str, str]]) -> bool
  ```

  Update user profile (individual fields or multiple).

Args:
    interaction_mode: New interaction mode (optional)
    experience_level: New experience level (optional)
    tech_stack_preference: New tech stack preference, None to clear, omit to keep current
    
Returns:
    True if update successful, False otherwise

  **Parameters:**

  - `self`
  - `interaction_mode` (Optional[str]) = `None`: New interaction mode (optional)
  - `experience_level` (Optional[str]) = `None`: New experience level (optional)
  - `tech_stack_preference` (Optional[Dict[str, str]]) = `...`: New tech stack preference, None to clear, omit to keep current


  **Returns:** bool
    True if update successful, False otherwise


  #### `profile_exists`

  ```python
  profile_exists(self) -> bool
  ```

  Check if user profile exists.

Returns:
    True if profile exists, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if profile exists, False otherwise


  #### `delete_profile`

  ```python
  delete_profile(self) -> bool
  ```

  Delete user profile (clear all preferences).

Returns:
    True if deletion successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if deletion successful, False otherwise


  #### `store_application_name`

  ```python
  store_application_name(self, name: str) -> bool
  ```

  Store or update the application name in Tier 1.

Args:
    name: Application name to store

Returns:
    True if storage successful, False otherwise

  **Parameters:**

  - `self`
  - `name` (str): Application name to store


  **Returns:** bool
    True if storage successful, False otherwise


  #### `get_application_name`

  ```python
  get_application_name(self) -> Optional[str]
  ```

  Retrieve the stored application name from Tier 1.

Returns:
    Application name or None if not set

  **Parameters:**

  - `self`


  **Returns:** Optional[str]
    Application name or None if not set


  #### `store_swagger_context`

  ```python
  store_swagger_context(self, context_id: str, context_data: Dict[str, Any]) -> bool
  ```

  Store SWAGGER context for estimation workflow

Used when scope approval is required - preserves SWAGGER analysis
during handoff to planning workflow so it can be resumed later.

Args:
    context_id: Unique identifier (format: swagger-YYYYMMDD-HHMMSS)
    context_data: Dictionary with keys:
        - complexity: SWAGGER complexity score (0-100)
        - scope_boundary: ScopeBoundary dict or dataclass
        - team_size: Number of developers
        - velocity: Optional team velocity
        - status: 'awaiting_approval', 'approved', 'estimated'
        - created_at: ISO timestamp

Returns:
    True if storage successful, False otherwise

  **Parameters:**

  - `self`
  - `context_id` (str): Unique identifier (format: swagger-YYYYMMDD-HHMMSS)
  - `context_data` (Dict[str, Any]): Dictionary with keys:


  **Returns:** bool
    True if storage successful, False otherwise


  #### `retrieve_swagger_context`

  ```python
  retrieve_swagger_context(self, context_id: str) -> Optional[Dict[str, Any]]
  ```

  Retrieve stored SWAGGER context

Used when resuming estimation after user approves scope via
planning workflow or explicit approval command.

Args:
    context_id: Unique identifier to retrieve

Returns:
    Dictionary with SWAGGER context data or None if not found

  **Parameters:**

  - `self`
  - `context_id` (str): Unique identifier to retrieve


  **Returns:** Optional[Dict[str, Any]]
    Dictionary with SWAGGER context data or None if not found


  #### `update_swagger_context_status`

  ```python
  update_swagger_context_status(self, context_id: str, status: str) -> bool
  ```

  Update SWAGGER context status

Status transitions:
- awaiting_approval → approved (user approves scope)
- approved → estimated (estimate generated)

Args:
    context_id: Context to update
    status: New status value

Returns:
    True if update successful, False otherwise

  **Parameters:**

  - `self`
  - `context_id` (str): Context to update
  - `status` (str): New status value


  **Returns:** bool
    True if update successful, False otherwise


  #### `store_test_intent`

  ```python
  store_test_intent(self, feature_name: str, requirement: str, test_phase: str, edge_cases: List[str], metadata: Dict[str, Any]) -> bool
  ```

  Store test intent extracted during RED phase of TDD.

Part of Phase 3: Eliminates circular dependency on git commit messages
by capturing test requirements in real-time during RED phase.

Args:
    feature_name: Name of feature being tested
    requirement: Test requirement/behavior being validated
    test_phase: TDD phase (RED, GREEN, REFACTOR)
    edge_cases: List of edge cases being tested
    metadata: Additional context (file paths, test number, etc.)

Returns:
    True if stored successfully

  **Parameters:**

  - `self`
  - `feature_name` (str): Name of feature being tested
  - `requirement` (str): Test requirement/behavior being validated
  - `test_phase` (str) = `'RED'`: TDD phase (RED, GREEN, REFACTOR)
  - `edge_cases` (List[str]) = `None`: List of edge cases being tested
  - `metadata` (Dict[str, Any]) = `None`: Additional context (file paths, test number, etc.)


  **Returns:** bool
    True if stored successfully


  #### `get_recent_test_intents`

  ```python
  get_recent_test_intents(self, limit: int) -> List[Dict[str, Any]]
  ```

  Get recently captured test intents.

Returns:
    List of test intent dictionaries

  **Parameters:**

  - `self`
  - `limit` (int) = `10`


  **Returns:** List[Dict[str, Any]]
    List of test intent dictionaries


  #### `get_edge_cases_for_feature`

  ```python
  get_edge_cases_for_feature(self, feature_name: str) -> List[Dict[str, Any]]
  ```

  Get all edge cases for a specific feature.

Args:
    feature_name: Name of feature to retrieve edge cases for

Returns:
    List of edge case dictionaries with descriptions

  **Parameters:**

  - `self`
  - `feature_name` (str): Name of feature to retrieve edge cases for


  **Returns:** List[Dict[str, Any]]
    List of edge case dictionaries with descriptions


  #### `store_temp_context`

  ```python
  store_temp_context(self, key: str, value: Any, ttl_seconds: int, context_type: str, metadata: Optional[Dict[str, Any]]) -> bool
  ```

  Store temporary context with TTL expiration.

Args:
    key: Unique key for the context
    value: Context value (will be JSON serialized)
    ttl_seconds: Time-to-live in seconds
    context_type: Type of context (e.g., 'feature_work', 'conversation_work')
    metadata: Optional metadata dictionary

Returns:
    True if stored successfully, False otherwise

Example:
    working_memory.store_temp_context(
        key="current_feature",
        value={"feature": "user_auth", "status": "in_progress"},
        ttl_seconds=3600,  # 1 hour
        context_type="feature_work"
    )

  **Parameters:**

  - `self`
  - `key` (str): Unique key for the context
  - `value` (Any): Context value (will be JSON serialized)
  - `ttl_seconds` (int): Time-to-live in seconds
  - `context_type` (str): Type of context (e.g., 'feature_work', 'conversation_work')
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Optional metadata dictionary


  **Returns:** bool
    True if stored successfully, False otherwise


  #### `get_temp_context`

  ```python
  get_temp_context(self, key: str) -> Optional[Dict[str, Any]]
  ```

  Get temporary context by key (only if not expired).

Args:
    key: Context key to retrieve

Returns:
    Dictionary with 'value', 'context_type', 'created_at', 'expires_at', 'metadata'
    or None if not found or expired

  **Parameters:**

  - `self`
  - `key` (str): Context key to retrieve


  **Returns:** Optional[Dict[str, Any]]
    Dictionary with 'value', 'context_type', 'created_at', 'expires_at', 'metadata' or None if not found or expired


  #### `cleanup_expired_contexts`

  ```python
  cleanup_expired_contexts(self) -> int
  ```

  Remove all expired temporary contexts.

Returns:
    Number of contexts deleted

  **Parameters:**

  - `self`


  **Returns:** int
    Number of contexts deleted


  #### `list_active_contexts`

  ```python
  list_active_contexts(self, context_type: Optional[str]) -> List[Dict[str, Any]]
  ```

  List all active (non-expired) temporary contexts.

Args:
    context_type: Optional filter by context type

Returns:
    List of active context dictionaries

  **Parameters:**

  - `self`
  - `context_type` (Optional[str]) = `None`: Optional filter by context type


  **Returns:** List[Dict[str, Any]]
    List of active context dictionaries


  #### `list_conversations`

  ```python
  list_conversations(self, limit: Optional[int], include_inactive: bool) -> List[Dict[str, Any]]
  ```

  List conversations with optional limit.

Args:
    limit: Maximum number of conversations to return (None = all)
    include_inactive: Include inactive conversations

Returns:
    List of conversation dictionaries

  **Parameters:**

  - `self`
  - `limit` (Optional[int]) = `None`: Maximum number of conversations to return (None = all)
  - `include_inactive` (bool) = `True`: Include inactive conversations


  **Returns:** List[Dict[str, Any]]
    List of conversation dictionaries


  #### `mark_conversation_inactive`

  ```python
  mark_conversation_inactive(self, conversation_id: str) -> bool
  ```

  Mark a conversation as inactive (eligible for FIFO eviction).

Args:
    conversation_id: Conversation to mark inactive

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to mark inactive


  **Returns:** bool
    True if successful, False otherwise


  #### `archive_conversation_to_tier2`

  ```python
  archive_conversation_to_tier2(self, conversation_id: str, knowledge_graph: Any) -> bool
  ```

  Archive a conversation to Tier 2 (Knowledge Graph).

Args:
    conversation_id: Conversation to archive
    knowledge_graph: Tier 2 KnowledgeGraph instance

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to archive
  - `knowledge_graph` (Any): Tier 2 KnowledgeGraph instance


  **Returns:** bool
    True if successful, False otherwise


  #### `pin_conversation`

  ```python
  pin_conversation(self, conversation_id: str) -> bool
  ```

  Pin a conversation to prevent FIFO eviction.

Args:
    conversation_id: Conversation to pin

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to pin


  **Returns:** bool
    True if successful, False otherwise


  #### `unpin_conversation`

  ```python
  unpin_conversation(self, conversation_id: str) -> bool
  ```

  Unpin a conversation (allow FIFO eviction).

Args:
    conversation_id: Conversation to unpin

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to unpin


  **Returns:** bool
    True if successful, False otherwise


  #### `is_conversation_pinned`

  ```python
  is_conversation_pinned(self, conversation_id: str) -> bool
  ```

  Check if a conversation is pinned.

Args:
    conversation_id: Conversation to check

Returns:
    True if pinned, False otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to check


  **Returns:** bool
    True if pinned, False otherwise


  #### `list_pinned_conversations`

  ```python
  list_pinned_conversations(self) -> List[Dict[str, Any]]
  ```

  List all pinned conversations.

Returns:
    List of pinned conversation dictionaries

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of pinned conversation dictionaries



---

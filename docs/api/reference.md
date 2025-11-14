# CORTEX API Reference

**Auto-generated:** 2025-11-14 10:58:51
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## src.__init__

CORTEX Source Package

Core CORTEX components:
- router.py: Universal entry point router
- session_manager.py: Conversation session management
- context_injector.py: Tier 1-3 context injection
- workflows/: Workflow orchestrators (TDD, feature creation, bug fix)

Version: 1.0

---

## src.brain.tier1.__init__

CORTEX Brain - Tier 1 Package

Tier 1: Working Memory (Short-term Conversation History)

Purpose: Manage last 20 conversations with full message history
FIFO Queue: When conversation #21 starts, #1 gets deleted
Performance: <100ms read for active conversation + recent 19

Components:
- Tier1API: Unified high-level interface (RECOMMENDED)
- ConversationManager: Core CRUD operations for conversations
- EntityExtractor: Extract and link entities from messages
- FileTracker: Track file modifications per conversation
- RequestLogger: Log raw requests with privacy-aware redaction

Recommended Usage:
    from src.brain.tier1 import Tier1API
    
    api = Tier1API()  # Uses ConfigManager for tier-specific path
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix bug in auth.py",
        response="Fixed authentication issue"
    )

---

## src.brain.tier1.conversation_manager

CORTEX Brain - Tier 1: ConversationManager

Purpose: Core CRUD operations for managing conversations in SQLite database

Features:
- Create, read, update, delete conversations
- FIFO queue management (max 20 conversations)
- Message threading and sequencing
- Context resolution support
- Performance optimized (<100ms queries)

Database Tables:
- tier1_conversations: Conversation metadata
- tier1_messages: Individual messages within conversations
- tier1_conversations_fts: Full-text search index

Author: CORTEX Development Team
Version: 1.0.0

### ConversationManager

Manages conversations in the CORTEX Brain Tier 1 database.

Implements FIFO queue (max 20 conversations), message threading,
and context resolution for natural language continuity.

**Methods:**

#### `create_conversation(self, topic, intent, primary_entity)`

Create a new conversation and manage FIFO queue

Args:
    topic: Conversation topic (auto-generated from first message)
    intent: Primary intent (PLAN, EXECUTE, TEST, etc.)
    primary_entity: Main entity being discussed

Returns:
    conversation_id: UUID of created conversation

Raises:
    sqlite3.Error: If database operation fails

#### `get_conversation(self, conversation_id)`

Get conversation by ID

Args:
    conversation_id: Conversation UUID

Returns:
    Dictionary with conversation data, or None if not found

#### `get_active_conversation(self)`

Get the most recent active conversation

Returns:
    Dictionary with conversation data, or None if no active conversations

#### `get_recent_conversations(self, limit)`

Get recent conversations (FIFO queue)

Args:
    limit: Maximum number of conversations to return (default: 20)

Returns:
    List of conversation dictionaries, ordered by creation date (newest first)

#### `update_conversation(self, conversation_id, status, outcome, duration_seconds, related_files, associated_commits)`

Update conversation metadata

Args:
    conversation_id: Conversation UUID
    status: New status ('active', 'complete', 'archived')
    outcome: Outcome ('success', 'failure', 'cancelled')
    duration_seconds: Total conversation duration
    related_files: List of file paths
    associated_commits: List of commit metadata

Returns:
    True if updated, False if conversation not found

#### `delete_conversation(self, conversation_id)`

Delete conversation and all associated messages

Args:
    conversation_id: Conversation UUID

Returns:
    True if deleted, False if conversation not found

#### `add_message(self, conversation_id, role, content, intent_detected, resolved_references, agent_used, confidence)`

Add message to conversation

Args:
    conversation_id: Parent conversation UUID
    role: Message role ('user', 'assistant', 'system')
    content: Message text
    intent_detected: Detected intent for this message
    resolved_references: Dictionary of resolved references {"it": "FAB button"}
    agent_used: Which agent processed this message
    confidence: Confidence score (0.0-1.0)

Returns:
    message_id: UUID of created message

Raises:
    ValueError: If conversation not found or role invalid

#### `get_messages(self, conversation_id)`

Get all messages in conversation (ordered by sequence)

Args:
    conversation_id: Conversation UUID

Returns:
    List of message dictionaries, ordered by sequence_number

#### `get_recent_messages(self, conversation_id, limit)`

Get recent messages in conversation

Args:
    conversation_id: Conversation UUID
    limit: Maximum number of messages to return (default: 10)

Returns:
    List of message dictionaries, ordered by sequence_number (newest first)

#### `search_conversations(self, query, limit)`

Full-text search across conversations

Args:
    query: Search query (supports FTS5 syntax)
    limit: Maximum number of results (default: 10)

Returns:
    List of conversation dictionaries, ordered by relevance

#### `find_conversations_by_entity(self, entity)`

Find conversations that mention a specific entity

Args:
    entity: Entity name (file, feature, etc.)

Returns:
    List of conversation dictionaries

#### `get_queue_status(self)`

Get FIFO queue status

Returns:
    Dictionary with queue statistics

#### `get_context_for_resolution(self, conversation_id)`

Get context for resolving ambiguous references

Args:
    conversation_id: Conversation UUID

Returns:
    Dictionary with context information:
    - recent_messages: Last 5 messages
    - primary_entity: Main entity being discussed
    - related_files: Files modified in conversation

---

## src.brain.tier1.entity_extractor

CORTEX Brain - Tier 1: EntityExtractor

Purpose: Extract entities from conversation messages and link to conversations

Features:
- Extract file paths, features, components, services from messages
- Link entities to conversations for quick lookups
- Support fuzzy matching for entity resolution
- Track entity usage frequency
- Enable "Make it purple" style references

Entity Types:
- Files: Source files mentioned in conversation
- Features: Features being implemented/discussed
- Components: UI components, services, modules
- Concepts: Abstract concepts (dark mode, authentication, etc.)

Author: CORTEX Development Team
Version: 1.0.0

### EntityExtractor

Extracts and manages entities from conversation messages.

Supports multiple entity types and provides fuzzy matching
for resolving ambiguous references.

**Methods:**

#### `extract_entities(self, text)`

Extract all entities from text

Args:
    text: Message text to analyze

Returns:
    Dictionary with entity types as keys and lists of entities as values
    Example: {
        'files': ['HostControlPanel.razor', 'app.css'],
        'components': ['FABButton', 'UserPanel'],
        'features': ['dark mode', 'export to PDF']
    }

#### `extract_primary_entity(self, text)`

Extract the primary entity being discussed

Heuristic: First file, component, or feature mentioned

Args:
    text: Message text to analyze

Returns:
    Primary entity string, or None if no entities found

#### `resolve_reference(self, reference, context)`

Resolve ambiguous reference ("it", "that", "the button") to actual entity

Args:
    reference: Ambiguous reference from user message
    context: Context dictionary from ConversationManager
             Contains recent_messages, primary_entity, related_files

Returns:
    Resolved entity string, or None if cannot resolve

#### `extract_file_references(self, text)`

Extract only file references from text

Args:
    text: Message text to analyze

Returns:
    List of file paths mentioned

#### `deduplicate_entities(self, entities)`

Remove duplicate and similar entities

Args:
    entities: List of entity strings

Returns:
    Deduplicated list

#### `categorize_files(self, filepaths)`

Categorize files by type

Args:
    filepaths: List of file paths

Returns:
    Dictionary with categories: {
        'source': [...],
        'tests': [...],
        'config': [...],
        'documentation': [...]
    }

#### `build_entity_summary(self, entities)`

Build human-readable summary of extracted entities

Args:
    entities: Dictionary of entities by type

Returns:
    Summary string like "2 files, 3 components, 1 feature"

#### `extract_intents(self, text)`

Extract action intents from text

Args:
    text: Message text to analyze

Returns:
    List of detected intents (PLAN, EXECUTE, TEST, etc.)

---

## src.brain.tier1.file_tracker

CORTEX Brain - Tier 1: FileTracker

Purpose: Track file modifications per conversation and detect co-modification patterns

Features:
- Track which files are modified in each conversation
- Detect files frequently modified together (co-modification)
- Build file relationship graph for Tier 2 learning
- Support file categorization (source, tests, config, docs)
- Enable file-based conversation retrieval

Use Cases:
- "Show me conversations about HostControlPanel.razor"
- "What files are usually modified with this file?"
- "Which conversations touched the authentication system?"

Author: CORTEX Development Team
Version: 1.0.0

### FileTracker

Tracks file modifications and relationships across conversations.

Builds co-modification patterns for Tier 2 knowledge graph.

**Methods:**

#### `track_files(self, conversation_id, filepaths, categorize)`

Track files modified in a conversation

Args:
    conversation_id: Conversation UUID
    filepaths: List of file paths
    categorize: Whether to categorize files by type

Raises:
    ValueError: If conversation not found

#### `get_conversation_files(self, conversation_id)`

Get all files associated with a conversation

Args:
    conversation_id: Conversation UUID

Returns:
    List of file paths

#### `find_conversations_by_file(self, filepath)`

Find all conversations that modified a specific file

Args:
    filepath: File path to search for

Returns:
    List of conversation dictionaries

#### `detect_co_modifications(self, min_occurrences, min_confidence)`

Detect files frequently modified together

Args:
    min_occurrences: Minimum co-modification count to report
    min_confidence: Minimum confidence score (0.0-1.0)

Returns:
    List of co-modification patterns:
    [{
        'file_a': 'path/to/file1.py',
        'file_b': 'path/to/file2.py',
        'co_modification_count': 5,
        'confidence': 0.83,
        'conversations': ['conv-abc', 'conv-def', ...]
    }, ...]

#### `get_related_files(self, filepath, min_confidence, limit)`

Get files frequently modified with a specific file

Args:
    filepath: File path to find related files for
    min_confidence: Minimum confidence score
    limit: Maximum number of results

Returns:
    List of related files with confidence scores

#### `get_file_statistics(self)`

Get overall file tracking statistics

Returns:
    Dictionary with statistics:
    - total_files_tracked
    - total_conversations_with_files
    - most_modified_files (top 10)
    - file_categories

#### `get_file_modification_history(self, filepath)`

Get modification history for a specific file

Args:
    filepath: File path to get history for

Returns:
    List of conversation summaries that modified this file

#### `export_for_tier2(self)`

Export co-modification data for Tier 2 knowledge graph

Returns:
    Dictionary formatted for tier2_file_relationships table:
    {
        'relationships': [
            {
                'file_a': 'path/to/file1.py',
                'file_b': 'path/to/file2.py',
                'co_modification_count': 5,
                'co_modification_rate': 0.83,
                'last_seen': '2025-11-06T12:00:00Z'
            }, ...
        ]
    }

#### `sync_to_tier2(self, tier2_db_path)`

Sync file relationships to Tier 2 database

Args:
    tier2_db_path: Path to Tier 2 database (defaults to same as Tier 1)

Returns:
    Number of relationships synced

---

## src.brain.tier1.request_logger

Raw Request Logger
-----------------
Logs ALL raw user requests and agent responses for debugging and learning purposes.

This module provides privacy-aware logging that:
- Stores complete request/response pairs
- Redacts sensitive information (API keys, passwords, tokens)
- Enables replay for debugging
- Supports learning from user patterns
- Maintains separate log from conversation history (for raw data preservation)

Design Philosophy:
- Privacy First: Automatic redaction of sensitive data
- Debugging: Complete context for issue reproduction
- Learning: Identify user intent patterns and common tasks
- Separation: Raw logs separate from structured conversation history

Example Usage:
    from src.brain.tier1.request_logger import RequestLogger
    
    logger = RequestLogger()  # Uses ConfigManager for tier-specific path
    
    # Log raw request/response
    logger.log_raw_request(
        raw_request="Fix the auth bug using my API key abc123xyz",
        raw_response="Fixed authentication issue",
        agent_name="copilot",
        conversation_id="uuid-here"
    )
    # Stored as: "Fix the auth bug using my API key [REDACTED]"

### RequestLogger

Logger for raw user requests with privacy-aware redaction.

This class stores raw, unprocessed user input for debugging and learning,
while automatically redacting sensitive information.

Attributes:
    db_path: Path to SQLite database
    redaction_patterns: List of (pattern, replacement) tuples for sensitive data

**Methods:**

#### `redact_sensitive_data(self, text)`

Redact sensitive information from text.

Args:
    text: Input text that may contain sensitive data

Returns:
    Tuple of (redacted_text, was_redacted)

Example:
    >>> redacted, changed = logger.redact_sensitive_data(
    ...     "My API key is sk-abc123xyz456"
    ... )
    >>> print(redacted)
    "My API key is [REDACTED_API_KEY]"
    >>> print(changed)
    True

#### `log_raw_request(self, raw_request, raw_response, agent_name, conversation_id, metadata)`

Log a raw request/response pair with automatic redaction.

Args:
    raw_request: User's raw input (unprocessed)
    raw_response: Agent's raw output (unprocessed)
    agent_name: Name of agent (e.g., "copilot", "claude")
    conversation_id: Optional link to tier1_conversations
    metadata: Optional metadata dict

Returns:
    request_id: Integer ID of logged request

Example:
    req_id = logger.log_raw_request(
        raw_request="Fix bug using password=secret123",
        raw_response="Fixed the bug",
        agent_name="copilot",
        conversation_id="uuid-here"
    )

#### `get_raw_request(self, request_id)`

Get a raw request by ID.

Args:
    request_id: Integer ID of request

Returns:
    Dict with request data or None if not found

#### `get_conversation_raw_logs(self, conversation_id)`

Get all raw logs for a specific conversation.

Args:
    conversation_id: UUID of conversation

Returns:
    List of raw request dicts

#### `get_recent_raw_logs(self, limit, agent_name)`

Get recent raw logs (optionally filtered by agent).

Args:
    limit: Maximum results (default 50)
    agent_name: Optional agent name filter

Returns:
    List of raw request dicts

#### `get_redaction_stats(self)`

Get statistics about redaction activity.

Returns:
    Dict with total logs, redacted count, redaction rate

Example:
    stats = logger.get_redaction_stats()
    print(f"Redaction rate: {stats['redaction_rate']:.1%}")

### `get_request_logger(db_path)`

Convenience function to get a RequestLogger instance.

Args:
    db_path: Path to SQLite database (deprecated - use ConfigManager)

Returns:
    Initialized RequestLogger instance

Example:
    from src.brain.tier1.request_logger import get_request_logger
    
    logger = get_request_logger()
    logger.log_raw_request(...)

---

## src.brain.tier1.tier1_api

Tier 1 Unified API
-----------------
High-level wrapper combining all Tier 1 components (ConversationManager,
EntityExtractor, FileTracker) into a single, easy-to-use interface.

This is the PRIMARY entry point for CORTEX agents to interact with Tier 1 storage.

Design Philosophy:
- Single Responsibility: This class ONLY coordinates Tier 1 components
- Auto-extraction: Automatically extracts entities and tracks files from conversations
- Smart defaults: Reasonable defaults for all operations
- Performance: <100ms for common operations

Example Usage:
    from src.brain.tier1.tier1_api import Tier1API
    
    # Initialize
    api = Tier1API(db_path="cortex-brain/cortex-brain.db")
    
    # Log a conversation (auto-extracts entities and tracks files)
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix bug in auth.py",
        response="Fixed authentication issue",
        related_files=["src/auth.py"]
    )
    
    # Search conversations
    results = api.search("authentication bug")
    
    # Get co-modified files
    patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)

### Tier1API

Unified API for all Tier 1 operations.

This class provides a high-level interface that automatically:
- Extracts entities from conversations
- Tracks file relationships
- Manages FIFO queue (20 conversation limit)
- Provides search functionality
- Exports patterns to Tier 2

Attributes:
    conversation_manager: Handles conversation CRUD operations
    entity_extractor: Extracts entities and intents from text
    file_tracker: Tracks file modifications and patterns
    request_logger: Logs raw requests with privacy-aware redaction

**Methods:**

#### `log_conversation(self, agent_name, request, response, related_files, metadata, auto_extract)`

Log a complete conversation with automatic entity extraction and file tracking.

This is the PRIMARY method for logging agent conversations. It automatically:
1. Creates a conversation record
2. Adds request and response messages
3. Extracts entities (files, components, features)
4. Tracks file relationships
5. Enforces FIFO queue (deletes oldest if >20 conversations)

Args:
    agent_name: Name of agent (e.g., "copilot", "claude")
    request: User's request text
    response: Agent's response text
    related_files: Optional list of file paths
    metadata: Optional metadata (e.g., {"session_id": "abc123"})
    auto_extract: Whether to auto-extract entities (default True)

Returns:
    conversation_id: UUID of created conversation

Example:
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Add logging to database.py",
        response="Added logging statements to all methods",
        related_files=["src/database.py"]
    )

#### `add_message(self, conversation_id, role, content, auto_extract)`

Add a message to an existing conversation with auto-extraction.

Args:
    conversation_id: UUID of conversation
    role: "user" or "assistant"
    content: Message text
    auto_extract: Whether to auto-extract entities (default True)

Returns:
    message_id: Integer ID of created message

#### `search(self, query, limit, include_messages)`

Search conversations using full-text search.

This uses SQLite FTS5 for fast, relevant search results.

Args:
    query: Search query (supports AND, OR, NOT, quotes, *)
    limit: Maximum results (default 10)
    include_messages: Whether to include full message list (default True)

Returns:
    List of conversation dicts with relevance scores

Example:
    results = api.search("authentication bug", limit=5)
    for conv in results:
        print(f"Score: {conv['rank']}, Files: {conv['related_files']}")

#### `get_conversation(self, conversation_id, include_messages)`

Get a single conversation by ID.

Args:
    conversation_id: UUID of conversation
    include_messages: Whether to include message list (default True)

Returns:
    Conversation dict or None if not found

#### `get_recent_conversations(self, limit, include_messages)`

Get most recent conversations (ordered by created_at DESC).

Args:
    limit: Maximum results (default 20)
    include_messages: Whether to include message lists (default True)

Returns:
    List of conversation dicts

#### `get_file_patterns(self, file_path, min_confidence, limit)`

Get files frequently co-modified with the given file.

This is useful for predicting which other files might need changes
when modifying a specific file.

Args:
    file_path: Path to file (e.g., "src/auth.py")
    min_confidence: Minimum confidence score (0.0-1.0, default 0.2)
    limit: Maximum results (default 10)

Returns:
    List of {file_b, co_modifications, confidence, last_modified} dicts

Example:
    patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)
    for p in patterns:
        print(f"{p['file_b']}: {p['confidence']:.1%} confidence")

#### `export_patterns_to_tier2(self, min_confidence, limit)`

Export high-confidence file patterns to Tier 2 for pattern learning.

This is typically called periodically (e.g., once per day) to transfer
learned patterns from Tier 1 (conversation-based) to Tier 2 (knowledge graph).

Args:
    min_confidence: Minimum confidence to export (default 0.3)
    limit: Maximum patterns to export (default 100)

Returns:
    Number of patterns exported

Example:
    count = api.export_patterns_to_tier2(min_confidence=0.4)
    print(f"Exported {count} patterns to Tier 2")

#### `resolve_reference(self, reference, conversation_id)`

Resolve an ambiguous reference (e.g., "it", "that file") to a concrete entity.

This uses conversation context to resolve pronouns and vague references.

Args:
    reference: Ambiguous reference text
    conversation_id: UUID of conversation for context

Returns:
    Resolved entity or None if not resolvable

Example:
    # User: "Fix the bug in auth.py"
    # Agent: "Done"
    # User: "Now add tests for it"
    resolved = api.resolve_reference("it", conv_id)
    # Returns: "auth.py"

#### `get_conversation_summary(self, conversation_id)`

Get a brief summary of a conversation (first user message).

Args:
    conversation_id: UUID of conversation

Returns:
    Summary text or None if not found

#### `get_stats(self)`

Get Tier 1 statistics for monitoring and debugging.

Returns:
    Dict with conversation count, message count, file count, etc.

Example:
    stats = api.get_stats()
    print(f"Total conversations: {stats['total_conversations']}")
    print(f"Total messages: {stats['total_messages']}")
    print(f"Unique files tracked: {stats['unique_files']}")

#### `health_check(self)`

Perform health check on Tier 1 system.

Returns:
    Dict with status, warnings, and performance metrics

Example:
    health = api.health_check()
    if not health['healthy']:
        print(f"Warnings: {health['warnings']}")

### `get_tier1_api(db_path)`

Convenience function to get a Tier1API instance.

Args:
    db_path: Path to SQLite database (deprecated - use ConfigManager)

Returns:
    Initialized Tier1API instance

Example:
    from src.brain.tier1.tier1_api import get_tier1_api
    
    api = get_tier1_api()
    api.log_conversation(...)

---

## src.config

CORTEX Configuration Management

Handles cross-platform path resolution and configuration loading.
Supports development on multiple machines with different paths.

Machine Detection:
- Automatically detects current machine based on hostname or path
- Falls back to environment variables if cortex.config.json not found
- Uses relative paths as final fallback

Usage:
    from src.config import config
    
    # Get brain path (automatically resolved for current machine)
    brain_path = config.brain_path
    
    # Get project root
    root = config.root_path
    
    # Check if running in development mode
    if config.is_development:
        print("Development mode active")

### CortexConfig

CORTEX configuration manager.

Handles:
- Multi-machine path resolution
- Configuration file loading
- Environment variable fallbacks
- Relative path resolution

**Methods:**

#### `root_path(self)`

Get CORTEX root directory path.

#### `brain_path(self)`

Get cortex-brain directory path.

#### `src_path(self)`

Get CORTEX/src directory path.

#### `tests_path(self)`

Get CORTEX/tests directory path.

#### `hostname(self)`

Get current machine hostname.

#### `tier1_db_path(self)`

Get Tier 1 (Working Memory) database path.

#### `tier2_db_path(self)`

Get Tier 2 (Knowledge Graph) database path.

#### `tier3_db_path(self)`

Get Tier 3 (Development Context) database path.

#### `is_development(self)`

Check if running in development mode.

#### `get(self, key_path, default)`

Get configuration value using dot notation.

Args:
    key_path: Dot-separated key path (e.g., "application.name")
    default: Default value if key not found

Returns:
    Configuration value or default

Example:
    name = config.get("application.name")  # "CORTEX"
    threshold = config.get("governance.testQualityThreshold", 70)

#### `ensure_paths_exist(self)`

Create essential CORTEX directories if they don't exist.

Creates:
- cortex-brain/tier1
- cortex-brain/tier2
- cortex-brain/tier3
- cortex-brain/corpus-callosum

#### `get_machine_info(self)`

Get information about current machine configuration.

Returns:
    Dictionary with machine info

### `get_brain_path()`

Get cortex-brain path for current machine.

### `get_root_path()`

Get CORTEX root path for current machine.

---

## src.context_injector

CORTEX Context Injector

Injects relevant context from Tiers 1-3 into workflows:
- Tier 1: Recent conversations + entities (working memory)
- Tier 2: Patterns from knowledge graph
- Tier 3: Development activity and metrics

Performance Target: <200ms total injection time

Author: CORTEX Development Team
Version: 1.0

### ContextInjector

Inject context from Tiers 1-3 into workflows

Responsibilities:
- Load recent conversations (Tier 1)
- Load relevant patterns (Tier 2)
- Load development metrics (Tier 3)
- Selective tier inclusion
- Performance optimization (<200ms)

Performance Target: <200ms total

**Methods:**

#### `inject_context(self, user_request, conversation_id, current_file, include_tiers)`

Inject context from specified tiers

Args:
    user_request: User's request text
    conversation_id: Current conversation (if exists)
    current_file: Current file being worked on (for namespace detection)
    include_tiers: {'tier1': True, 'tier2': True, 'tier3': True}

Returns:
    {
        'tier1': {...},  # Recent conversations + entities
        'tier2': {...},  # Patterns (namespace-aware)
        'tier3': {...},  # Dev activity
        'injection_time_ms': 142.7
    }

#### `get_injection_stats(self)`

Get recent injection performance statistics

Returns:
    {
        'last_injection_ms': 142.7,
        'target_ms': 200,
        'performance_ok': True
    }

---

## src.core.plugin_processor

CORTEX 2.0 YAML Plugin Processor
Loads, validates, and executes machine-readable YAML plugins

### PluginProcessor

Process and execute YAML-based plugins

**Methods:**

#### `load_plugin(self, plugin_path)`

Load and validate a YAML plugin

Args:
    plugin_path: Path to .yaml plugin file (relative or absolute)
    
Returns:
    (plugin_config, error_message)

#### `execute_workflow(self, plugin, user_params)`

Execute a workflow plugin

Args:
    plugin: Loaded plugin configuration
    user_params: User-provided parameters
    
Returns:
    (success, error_message, result_data)

#### `get_plugin_info(self, plugin)`

Get plugin metadata and structure

---

## src.core.plugin_schema

CORTEX 2.0 Plugin Schema Definitions
Machine-readable plugin system using YAML with strict validation

### PluginType

Plugin categories

### StepType

Workflow step types

### Target

Target file or resource for plugin operations

### WorkflowStep

Single step in a workflow

### ValidationRule

Validation check definition

### Parameter

Plugin parameter definition

### PluginConfig

Complete plugin configuration

### `validate_plugin_schema(config)`

Validate plugin configuration against schema

Returns:
    (is_valid, error_message)

---

## src.cortex_agents.__init__

CORTEX Agents Package

This package contains all specialist agents for the CORTEX intelligence layer.
Each agent inherits from BaseAgent and implements specific capabilities.

Agent Types:
- Foundation: IntentRouter, WorkPlanner, HealthValidator
- Execution: CodeExecutor, TestGenerator, ErrorCorrector
- Advanced: SessionResumer, ScreenshotAnalyzer, ChangeGovernor, CommitHandler

Usage:
    from cortex_agents import IntentRouter, WorkPlanner
    from cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter(tier1_api, tier2_kg, tier3_context)
    request = AgentRequest(intent="plan", context={}, user_message="Build feature")
    response = router.execute(request)

---

## src.cortex_agents.agent_types

Agent Type Definitions and Enums

Defines common types and enumerations used across all CORTEX agents.

### AgentType

Categories of specialist agents

### IntentType

Common user intent categories

### Priority

Task priority levels

### ResponseStatus

Agent response status codes

### RiskLevel

Risk levels for change governance

### `get_agent_for_intent(intent)`

Map an intent to its primary agent type

### `get_intents_for_agent(agent_type)`

Get all intents handled by an agent type

---

## src.cortex_agents.base_agent

Base Agent Class and Core Data Structures

Provides abstract base class for all CORTEX specialist agents
and standard request/response formats.

### AgentRequest

Standard request format for all agents.

Attributes:
    intent: The classified user intent (e.g., "plan", "code", "test")
    context: Additional context information (files, settings, etc.)
    user_message: Original user message text
    conversation_id: Optional ID linking to Tier 1 conversation
    priority: Request priority level (default: NORMAL)
    metadata: Additional metadata for the request

Example:
    request = AgentRequest(
        intent="plan",
        context={"feature": "authentication"},
        user_message="Add user authentication"
    )

### AgentResponse

Standard response format for all agents.

Attributes:
    success: Whether the agent executed successfully
    result: The main result/output from the agent
    message: Human-readable message describing the outcome
    metadata: Additional metadata about the execution
    agent_name: Name of the agent that generated this response
    duration_ms: Execution time in milliseconds
    next_actions: Suggested follow-up actions

Example:
    response = AgentResponse(
        success=True,
        result={"tasks": ["Create auth model", "Add login route"]},
        message="Feature broken down into 2 tasks",
        agent_name="WorkPlanner"
    )

### AgentMessage

Message format for agent-to-agent communication in workflows.

Used for orchestrating multi-agent workflows like TDD cycle.

Attributes:
    from_agent: Name of the sending agent
    to_agent: Name of the receiving agent
    command: Command/action to perform
    payload: Data payload for the command
    correlation_id: Optional ID to correlate related messages

Example:
    message = AgentMessage(
        from_agent="workflow-orchestrator",
        to_agent="test-generator",
        command="create_test",
        payload={"task": "auth", "expect_failure": True}
    )

### BaseAgent

Abstract base class for all CORTEX specialist agents.

All agents must implement:
- can_handle(): Check if agent can process a request
- execute(): Perform the agent's primary function

Agents automatically receive:
- Tier 1 API (conversation/working memory)
- Tier 2 Knowledge Graph (patterns/learning)
- Tier 3 Context Intelligence (git/metrics)
- Logging infrastructure

Example:
    class MyAgent(BaseAgent):
        def can_handle(self, request: AgentRequest) -> bool:
            return request.intent == "my_intent"
        
        def execute(self, request: AgentRequest) -> AgentResponse:
            # Do work
            return AgentResponse(
                success=True,
                result=result,
                message="Work completed"
            )

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the given request.

Args:
    request: The agent request to evaluate

Returns:
    True if agent can handle this request, False otherwise

Example:
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent in ["plan", "feature"]

#### `execute(self, request)`

Execute the agent's primary function.

Args:
    request: The agent request to process

Returns:
    AgentResponse with results and status

Example:
    def execute(self, request: AgentRequest) -> AgentResponse:
        result = self._do_work(request)
        return AgentResponse(
            success=True,
            result=result,
            message="Work completed successfully"
        )

#### `log_request(self, request)`

Log incoming request (for debugging/auditing)

#### `log_response(self, response)`

Log outgoing response (for debugging/auditing)

---

## src.cortex_agents.change_governor

ChangeGovernor Agent

Enforces governance rules and performs risk assessment for changes.
Checks compliance with CORTEX governance rules before executing
potentially risky operations.

The ChangeGovernor ensures all changes follow project governance
policies and architectural standards.

### ChangeGovernor

Enforces governance rules and assesses change risk.

The ChangeGovernor validates proposed changes against governance
rules (documented in governance/rules.md) and performs risk
assessment to protect system integrity.

Features:
- Governance rule compliance checking
- Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Multi-rule validation
- Protected file detection
- Test requirement validation
- Change impact analysis

Example:
    governor = ChangeGovernor(name="Governor", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="check_governance",
        context={
            "files": ["src/core/database.py"],
            "operation": "delete"
        },
        user_message="Delete database module"
    )
    
    response = governor.execute(request)
    # Returns: {
    #   "allowed": False,
    #   "risk_level": "CRITICAL",
    #   "violations": ["Rule #3: Delete protected system file"],
    #   "requires_tests": True
    # }

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request to evaluate
    
Returns:
    True if intent is governance check, False otherwise

#### `execute(self, request)`

Check governance compliance and assess risk.

Args:
    request: Agent request with change details in context
    
Returns:
    AgentResponse with compliance check and risk assessment

---

## src.cortex_agents.code_executor.__init__

CodeExecutor agent for safe code execution.

---

## src.cortex_agents.code_executor.agent

CodeExecutor Agent - Coordinator.

### CodeExecutor

Executes code changes safely with validation and rollback.

The CodeExecutor performs code modifications including:
- File creation with template support
- File editing with backup/rollback
- File deletion with safety checks
- Syntax validation before applying changes
- Integration with HealthValidator

Features:
- Automatic backups before changes
- Rollback on validation failures
- Python syntax checking
- Operation logging to all tiers
- Batch operation support

Example:
    executor = CodeExecutor(name="Executor", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="execute_code",
        context={
            "operation": "create",
            "file_path": "/path/to/new_file.py",
            "content": "def hello(): pass"
        },
        user_message="Create a new Python file"
    )
    
    response = executor.execute(request)

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request

Returns:
    True if intent is code, implement, or file operations

#### `execute(self, request)`

Execute code changes safely.

Args:
    request: The agent request

Returns:
    AgentResponse with execution results

---

## src.cortex_agents.code_executor.backup.__init__

Backup management for CodeExecutor.

---

## src.cortex_agents.code_executor.backup.backup_manager

Backup manager for file operations.

### BackupManager

Manages file backups for safe operations.

**Methods:**

#### `create_backup_dir(self)`

Create a temporary backup directory.

Returns:
    Path to backup directory

#### `get_backup_dir(self)`

Get the current backup directory path.

Returns:
    Path to backup directory, or None if not created

#### `backup_file(self, file_path)`

Backup a file to the backup directory.

Args:
    file_path: Path to backup

Returns:
    Path to backup file, or None on failure

#### `restore_file(self, backup_path, original_path)`

Restore a file from backup.

Args:
    backup_path: Path to backup file
    original_path: Path to restore to

Returns:
    True if restore succeeded

#### `rollback_all(self)`

Rollback all changes from backup directory.

Note: This is a simplified implementation.
Real implementation would need to track original paths.

Returns:
    True if rollback information is available

#### `cleanup(self)`

Clean up backup directory.

---

## src.cortex_agents.code_executor.operations.__init__

File operations for CodeExecutor.

---

## src.cortex_agents.code_executor.operations.base_operation

Base operation interface for file operations.

### BaseOperation

Abstract base class for file operations.

**Methods:**

#### `execute(self, file_path, context)`

Execute the operation.

Args:
    file_path: Path to operate on
    context: Operation context (content, options, etc.)

Returns:
    Operation result dictionary with keys:
    - success: bool
    - message: str
    - file_path: str (optional)
    - operation: str (optional)
    - error: str (optional)

#### `get_operation_type(self)`

Get the operation type name.

Returns:
    Operation type (e.g., "create", "edit", "delete")

---

## src.cortex_agents.code_executor.operations.batch_operation

Batch file operations.

### BatchOperation

Operation for executing multiple file operations in batch.

**Methods:**

#### `get_operation_type(self)`

Get operation type.

#### `execute(self, file_path, context)`

Execute multiple operations in batch.

Args:
    file_path: Not used for batch operations
    context: Must contain 'operations' list

Returns:
    Batch operation results

---

## src.cortex_agents.code_executor.operations.create_operation

Create file operation.

### CreateOperation

Operation for creating new files.

**Methods:**

#### `get_operation_type(self)`

Get operation type.

#### `execute(self, file_path, context)`

Create a new file.

Args:
    file_path: Path to create
    context: Must contain 'content' key

Returns:
    Creation result

---

## src.cortex_agents.code_executor.operations.delete_operation

Delete file operation.

### DeleteOperation

Operation for deleting files.

**Methods:**

#### `get_operation_type(self)`

Get operation type.

#### `execute(self, file_path, context)`

Delete a file.

Args:
    file_path: Path to delete
    context: Must contain 'confirm' = True

Returns:
    Deletion result

---

## src.cortex_agents.code_executor.operations.edit_operation

Edit file operation.

### EditOperation

Operation for editing existing files.

**Methods:**

#### `get_operation_type(self)`

Get operation type.

#### `execute(self, file_path, context)`

Edit an existing file.

Args:
    file_path: Path to edit
    context: Must contain 'content' or 'old_string'/'new_string'

Returns:
    Edit result

---

## src.cortex_agents.code_executor.validators.__init__

Code validators for CodeExecutor.

---

## src.cortex_agents.code_executor.validators.syntax_validator

Syntax validation for code files.

### SyntaxValidator

Validates syntax of code files before execution.

**Methods:**

#### `should_validate(self, file_path)`

Check if file should have syntax validation.

Args:
    file_path: Path to check

Returns:
    True if syntax should be validated

#### `validate(self, content, file_path)`

Validate syntax of code content.

Args:
    content: Code content to validate
    file_path: File path (for determining language)

Returns:
    Tuple of (is_valid, error_message)

---

## src.cortex_agents.commit_handler

CommitHandler Agent

Manages git operations and generates conventional commit messages.
Handles commit message generation, staged file validation, and
git repository operations.

The CommitHandler automates git workflow and ensures consistent
commit message formatting following conventional commit standards.

### CommitHandler

Manages git operations and commit message generation.

The CommitHandler automates git commit workflow by generating
conventional commit messages, validating staged changes, and
executing git operations safely.

Features:
- Conventional commit message generation
- Staged file validation
- Git status checking
- Commit execution
- Pre-commit validation
- Commit message templates (feat, fix, docs, refactor, etc.)

Example:
    handler = CommitHandler(name="Committer", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="commit",
        context={
            "staged_files": ["src/feature.py", "tests/test_feature.py"],
            "type": "feat",
            "description": "Add user authentication"
        },
        user_message="Commit the authentication feature"
    )
    
    response = handler.execute(request)
    # Returns: {
    #   "committed": True,
    #   "message": "feat: Add user authentication",
    #   "files": 2,
    #   "commit_hash": "abc123"
    # }

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request to evaluate
    
Returns:
    True if intent is commit/git operation, False otherwise

#### `execute(self, request)`

Generate commit message and execute git commit.

Args:
    request: Agent request with commit details in context
    
Returns:
    AgentResponse with commit result

---

## src.cortex_agents.error_corrector

ErrorCorrector Agent

Automatically detects, parses, and corrects errors in code.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.

Handles:
- Pytest errors (assertion failures, import errors, type errors)
- Linter errors (undefined names, unused imports, formatting)
- Runtime errors (NameError, AttributeError, TypeError)
- Syntax errors (indentation, missing colons, invalid syntax)
- Import errors (missing modules, circular imports)

Uses Tier 2 knowledge base for known fix patterns.

### PatternStore

Placeholder for Tier 2 PatternStore.

**Methods:**

#### `search_patterns(self, query, pattern_type, min_confidence)`

Search for patterns. Currently returns empty list.

### ErrorCorrector

Agent that automatically corrects code errors.

ISOLATION: Fixes TARGET APPLICATION code only. NEVER modifies:
- CORTEX/tests/ (system health tests)
- CORTEX/src/cortex_agents/ (core agents)  
- cortex-brain/ (knowledge base)

**Methods:**

#### `can_handle(self, request)`

Can handle error correction requests.

Intents: FIX, DEBUG, fix_error, correct_code

#### `execute(self, request)`

Execute error correction.

Context expected:
- error_output: The error message/traceback
- file_path: Optional file where error occurred
- error_type: Optional type hint (pytest, linter, runtime, syntax)

---

## src.cortex_agents.error_corrector.__init__

ErrorCorrector Agent - Modular error correction with specialized parsers and strategies.

This module provides the ErrorCorrector agent that automatically detects, parses,
and corrects errors in code. The agent is organized into:

- Parsers: Extract structured error information from various error outputs
- Strategies: Apply specific fixes for different error types
- Validators: Ensure fixes are safe and paths are not protected

The agent only fixes TARGET APPLICATION code and never modifies CORTEX system files.

---

## src.cortex_agents.error_corrector.agent

ErrorCorrector Agent - Modular Version

Automatically detects, parses, and corrects errors in code.
This is the coordinator that delegates to specialized parsers, strategies, and validators.

ISOLATION NOTICE: This agent fixes errors in TARGET APPLICATION code only.
It NEVER modifies CORTEX/tests/ - those are protected system health tests.

### ErrorCorrector

Agent that automatically corrects code errors.

ISOLATION: Fixes TARGET APPLICATION code only. NEVER modifies:
- CORTEX/tests/ (system health tests)
- CORTEX/src/cortex_agents/ (core agents)  
- cortex-brain/ (knowledge base)

**Methods:**

#### `can_handle(self, request)`

Can handle error correction requests.

#### `execute(self, request)`

Execute error correction.

---

## src.cortex_agents.error_corrector.parsers.__init__

Error parsers for ErrorCorrector agent.

---

## src.cortex_agents.error_corrector.parsers.base_parser

Base error parser interface.

### BaseErrorParser

Abstract base class for error parsers.

**Methods:**

#### `can_parse(self, output)`

Check if this parser can handle the error output.

Args:
    output: Error output string
    
Returns:
    True if this parser can handle the output

#### `parse(self, output)`

Parse error output to extract structured information.

Args:
    output: Error output string
    
Returns:
    Parsed error dict with keys:
    - file: str (file path)
    - line: int (line number)
    - category: str (error category)
    - message: str (error message)
    - traceback: List[str] (traceback lines)
    - code_snippet: str (problematic code)
    - Additional parser-specific fields

---

## src.cortex_agents.error_corrector.parsers.import_parser

Parse import errors.

### ImportErrorParser

Parser for import errors.

**Methods:**

#### `can_parse(self, output)`

Check if output is import error.

#### `parse(self, output)`

Parse import error.

Returns:
    Dict with type, file, line, category, message, missing_module, missing_name

---

## src.cortex_agents.error_corrector.parsers.linter_parser

Parse linter errors (pylint, flake8, etc).

### LinterErrorParser

Parser for linter errors.

**Methods:**

#### `can_parse(self, output)`

Check if output is linter error.

#### `parse(self, output)`

Parse linter error (pylint, flake8, etc).

Returns:
    Dict with file, line, column, code, category, message

---

## src.cortex_agents.error_corrector.parsers.runtime_parser

Parse runtime errors (NameError, AttributeError, TypeError, etc).

### RuntimeErrorParser

Parser for Python runtime errors.

**Methods:**

#### `can_parse(self, output)`

Check if output is runtime error.

#### `parse(self, output)`

Parse runtime error (NameError, AttributeError, TypeError, etc).

Returns:
    Dict with file, line, category, message, traceback,
    and type-specific fields (undefined_name, missing_attribute, etc)

---

## src.cortex_agents.error_corrector.parsers.syntax_parser

Parse Python syntax errors.

### SyntaxErrorParser

Parser for Python syntax errors.

**Methods:**

#### `can_parse(self, output)`

Check if output is syntax error.

#### `parse(self, output)`

Parse Python syntax error.

Returns:
    Dict with type, file, line, category, message, code_snippet

---

## src.cortex_agents.error_corrector.parserstest_parser

Parse pytest error output.

### PytestErrorParser

Parser for pytest test failures.

**Methods:**

#### `can_parse(self, output)`

Check if output is pytest error.

#### `parse(self, output)`

Parse pytest error output.

Returns:
    Dict with type, file, test_name, line, category, message, traceback

---

## src.cortex_agents.error_corrector.strategies.__init__

Error fix strategies for ErrorCorrector agent.

---

## src.cortex_agents.error_corrector.strategies.base_strategy

Base fix strategy interface.

### BaseFixStrategy

Abstract base class for fix strategies.

**Methods:**

#### `can_fix(self, parsed_error, fix_pattern)`

Check if this strategy can fix the error.

Args:
    parsed_error: Parsed error information
    fix_pattern: Fix pattern from pattern store
    
Returns:
    True if this strategy can apply the fix

#### `apply_fix(self, parsed_error, fix_pattern, file_path)`

Apply the fix to the code.

Args:
    parsed_error: Parsed error information
    fix_pattern: Fix pattern to apply
    file_path: Optional file path to fix
    
Returns:
    Fix result dict with keys:
    - success: bool
    - message: str
    - changes: List[str] (description of changes)
    - fixed_content: Optional[str] (new file content)

---

## src.cortex_agents.error_corrector.strategies.import_strategy

Fix import-related errors.

### ImportFixStrategy

Strategy for fixing import errors.

**Methods:**

#### `can_fix(self, parsed_error, fix_pattern)`

Check if this is an import-related error.

#### `apply_fix(self, parsed_error, fix_pattern, file_path)`

Fix import errors by adding or removing imports.

Returns:
    Fix result with success, message, changes, import_statement

---

## src.cortex_agents.error_corrector.strategies.indentation_strategy

Fix indentation errors.

### IndentationFixStrategy

Strategy for fixing indentation errors.

**Methods:**

#### `can_fix(self, parsed_error, fix_pattern)`

Check if this is an indentation error.

#### `apply_fix(self, parsed_error, fix_pattern, file_path)`

Fix indentation errors by normalizing tabs to spaces.

Returns:
    Fix result with success, message, changes, fixed_content

---

## src.cortex_agents.error_corrector.strategies.package_strategy

Fix package-related errors.

### PackageFixStrategy

Strategy for suggesting package installations.

**Methods:**

#### `can_fix(self, parsed_error, fix_pattern)`

Check if this is a missing package error.

#### `apply_fix(self, parsed_error, fix_pattern, file_path)`

Suggest package installation.

Returns:
    Fix result with success, message, changes, command

---

## src.cortex_agents.error_corrector.strategies.syntax_strategy

Fix syntax errors.

### SyntaxFixStrategy

Strategy for fixing syntax errors.

**Methods:**

#### `can_fix(self, parsed_error, fix_pattern)`

Check if this is a syntax error.

#### `apply_fix(self, parsed_error, fix_pattern, file_path)`

Fix syntax errors like missing colons.

Returns:
    Fix result with success, message, changes, fixed_line

---

## src.cortex_agents.error_corrector.validators.__init__

Validators for ErrorCorrector agent.

---

## src.cortex_agents.error_corrector.validators.fix_validator

Validate error fixes before applying.

### FixValidator

Validator for error fixes.

**Methods:**

#### `validate(self, fix_result)`

Validate a fix result before applying.

Args:
    fix_result: Fix result from strategy
    
Returns:
    True if fix is valid and safe to apply

#### `is_safe(self, fix_result, parsed_error)`

Check if fix is safe to apply automatically.

Args:
    fix_result: Fix result from strategy
    parsed_error: Original parsed error
    
Returns:
    True if fix is safe for automatic application

---

## src.cortex_agents.error_corrector.validators.path_validator

Validate file paths for error correction.

### PathValidator

Validator for protected paths that should not be auto-fixed.

**Methods:**

#### `is_protected(self, file_path)`

Check if file path is in protected directory.

Protected paths:
- CORTEX/tests/ (system health tests)
- CORTEX/src/cortex_agents/ (core agents)
- cortex-brain/ (knowledge base)

Args:
    file_path: Path to check
    
Returns:
    True if path is protected and should not be auto-fixed

---

## src.cortex_agents.exceptions

Custom Exceptions for CORTEX Agents

Defines specific exception types for better error handling.

### CortexAgentError

Base exception for all CORTEX agent errors

### AgentNotFoundError

Raised when no agent can handle a request

### AgentExecutionError

Raised when agent execution fails

### InvalidRequestError

Raised when agent request is malformed or invalid

### TierConnectionError

Raised when connection to a tier (1, 2, or 3) fails

### AgentTimeoutError

Raised when agent execution exceeds timeout

### InsufficientContextError

Raised when agent lacks required context to proceed

### RuleViolationError

Raised when an operation would violate governance rules

---

## src.cortex_agents.health_validator.__init__

HealthValidator agent for system health checks.

---

## src.cortex_agents.health_validator.agent

HealthValidator Agent - Coordinator.

### HealthValidator

Validates system health before risky operations.

The HealthValidator performs comprehensive health checks including:
- Database integrity verification
- Test suite pass rate validation
- Git repository status
- Disk space availability
- Performance metric thresholds

Features:
- Multi-tier database checks
- Test execution and validation
- Git status monitoring
- Resource availability checks
- Risk level assessment

Example:
    validator = HealthValidator(name="Validator", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="health_check",
        context={},
        user_message="Check if system is ready for deployment"
    )
    
    response = validator.execute(request)

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request

Returns:
    True if intent is health_check or validate

#### `execute(self, request)`

Perform system health validation.

Args:
    request: The agent request

Returns:
    AgentResponse with health status and check results

---

## src.cortex_agents.health_validator.enhanced_validator

### EnhancedHealthValidator

Enhanced HealthValidator with investigation support for the Guided Deep Dive pattern.

Extends the existing HealthValidator with methods specifically for investigation
scenarios, providing detailed health analysis for entities under investigation.

**Methods:**

---

## src.cortex_agents.health_validator.reporting.__init__

Health report generation and analysis.

---

## src.cortex_agents.health_validator.reporting.analyzer

Health check result analyzer.

### ResultAnalyzer

Analyzes health check results to determine overall status and risk.

**Methods:**

#### `analyze_results(self, check_results)`

Analyze check results to determine overall status.

Args:
    check_results: Results from all checks

Returns:
    Tuple of (status, warnings, errors)

#### `calculate_risk(self, check_results, errors)`

Calculate overall risk level.

Args:
    check_results: Results from all checks
    errors: List of error messages

Returns:
    Risk level: "low", "medium", "high", or "critical"

---

## src.cortex_agents.health_validator.reporting.formatter

Health check report formatter.

### ReportFormatter

Formats health check results into user-friendly messages.

**Methods:**

#### `format_message(self, status, warnings, errors, check_results)`

Format health check results into a message.

Args:
    status: Overall health status
    warnings: List of warning messages
    errors: List of error messages
    check_results: Detailed results from all checks

Returns:
    Formatted message string

#### `suggest_actions(self, check_results, risk_level)`

Suggest remediation actions based on check results.

Args:
    check_results: Results from all checks
    risk_level: Overall risk level

Returns:
    List of suggested actions

---

## src.cortex_agents.health_validator.validators.__init__

Health check validators for HealthValidator agent.

---

## src.cortex_agents.health_validator.validators.base_validator

Base health validator interface.

### BaseHealthValidator

Abstract base class for health validators.

**Methods:**

#### `check(self)`

Perform health check.

Returns:
    Check result dict with keys:
    - status: str ("pass", "warn", "fail", "skip")
    - details: List[Dict] (check details)
    - errors: List[str] (error messages if any)
    - warnings: List[str] (warning messages if any)

#### `get_risk_level(self)`

Get risk level for this validator.

Returns:
    Risk level: "critical", "high", "medium", "low"

---

## src.cortex_agents.health_validator.validators.database_validator

Database health validator.

### DatabaseValidator

Validator for database integrity checks.

**Methods:**

#### `get_risk_level(self)`

Database failures are critical.

#### `check(self)`

Check all tier databases for integrity.

---

## src.cortex_agents.health_validator.validators.disk_validator

Disk space health validator.

### DiskValidator

Validator for available disk space (cross-platform).

**Methods:**

#### `get_risk_level(self)`

Low disk space is high risk.

#### `check(self)`

Check available disk space (cross-platform).

---

## src.cortex_agents.health_validator.validators.git_validator

Git repository health validator.

### GitValidator

Validator for git repository status.

**Methods:**

#### `get_risk_level(self)`

Git issues are medium risk.

#### `check(self)`

Check git repository status.

---

## src.cortex_agents.health_validator.validators.performance_validator

Performance metrics health validator.

### PerformanceValidator

Validator for performance metrics from Tier 3.

**Methods:**

#### `get_risk_level(self)`

Performance issues are low-medium risk.

#### `check(self)`

Check performance metrics from Tier 3.

---

## src.cortex_agents.health_validator.validators.test_validator

Test suite health validator.

### TestValidator

Validator for CORTEX internal test suite.

**Methods:**

#### `get_risk_level(self)`

Test failures are high risk.

#### `check(self)`

Check CORTEX internal test suite pass rate.

ISOLATION: This ONLY tests CORTEX's internal health, never the target
application's tests. Runs from CORTEX root with isolated environment.

---

## src.cortex_agents.intent_router

IntentRouter Agent

Routes user requests to appropriate specialist agents based on intent analysis.
Uses Tier 2 Knowledge Graph to find similar past intents and improve routing decisions.

The IntentRouter is the entry point for all user requests - it analyzes the intent,
checks for patterns in past requests, and routes to the most appropriate specialist agent.

### IntentRouter

Routes user requests to appropriate specialist agents.

The IntentRouter analyzes user messages to determine intent, queries
Tier 2 for similar past requests, and makes routing decisions to
send requests to the most appropriate specialist agent(s).

Features:
- Multi-keyword intent classification
- Pattern-based routing using Tier 2
- Support for multi-agent routing
- Fallback handling for unknown intents
- Confidence scoring for routing decisions

Example:
    router = IntentRouter(name="Router", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="unknown",  # Will be classified
        context={},
        user_message="Create a new authentication module with tests"
    )
    
    response = router.execute(request)
    # Returns: {
    #   "primary_agent": AgentType.EXECUTOR,
    #   "secondary_agents": [AgentType.TESTER],
    #   "confidence": 0.85
    # }

**Methods:**

#### `can_handle(self, request)`

IntentRouter can handle all requests (it's the entry point).

Args:
    request: The agent request

Returns:
    Always True (router handles everything)

#### `execute(self, request)`

Route the request to appropriate specialist agent(s).

Args:
    request: The agent request to route

Returns:
    AgentResponse with routing decision and metadata

---

## src.cortex_agents.investigation_router

### InvestigationPhase

Investigation phases with token budgets

### TokenBudget

Token budget allocation for investigation phases

**Methods:**

#### `is_exhausted(self)`

#### `consume(self, tokens)`

Consume tokens from budget. Returns True if budget allows.

### InvestigationContext

Context for investigation including target, relationships, and findings

**Methods:**

### InvestigationRouter

Routes and manages investigation commands with guided deep dive pattern.

Handles "Investigate why this view..." type requests by:
1. Intelligent scope detection from query
2. Phased investigation with token budgets
3. User checkpoints between phases
4. Relationship confidence scoring

**Methods:**

---

## src.cortex_agents.learning_capture_agent

CORTEX Learning Capture Agent

Automatically captures lessons from:
- Operation failures/successes
- Error patterns and resolutions
- Git commits and code changes
- Ambient daemon events (file changes, terminal errors, VS Code actions)
- SKULL protection violations

This agent ensures CORTEX learns from every mistake and success,
preventing repeated errors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### LearningEvent

Structured learning event for knowledge capture.

**Methods:**

#### `to_lesson_dict(self, lesson_id)`

Convert to lessons-learned.yaml format.

### LearningCaptureAgent

Agent that automatically captures lessons learned from various sources.

Sources:
- Operation execution results (success/failure patterns)
- Error traces and exceptions
- Git commit messages and diffs
- Ambient daemon events (file changes, terminal output, errors)
- SKULL protection violations

**Methods:**

#### `capture_from_operation_result(self, operation_name, result, context)`

Capture learning from operation execution result.

Args:
    operation_name: Name of operation executed
    result: Operation result object
    context: Execution context

Returns:
    LearningEvent if lesson extracted, None otherwise

#### `capture_from_exception(self, exception, context)`

Capture learning from exception.

Args:
    exception: Exception that occurred
    context: Context when exception occurred

Returns:
    LearningEvent if pattern recognized

#### `capture_from_ambient_events(self, lookback_minutes)`

Capture learning from recent ambient daemon events.

Args:
    lookback_minutes: How far back to analyze events

Returns:
    List of learning events from ambient monitoring

#### `capture_from_git_commit(self, commit_sha, commit_message, files_changed)`

Capture learning from git commit (fix commits especially).

Args:
    commit_sha: Git commit SHA
    commit_message: Commit message
    files_changed: List of files in commit

Returns:
    LearningEvent if fix pattern detected

#### `save_lesson(self, event)`

Save learning event to lessons-learned.yaml.

Args:
    event: Learning event to save

Returns:
    True if saved successfully

### `capture_operation_learning(operation_name, result, context, project_root)`

Quick function to capture learning from operation result.

Args:
    operation_name: Operation that executed
    result: Operation result
    context: Execution context
    project_root: Optional project root path

Returns:
    True if lesson captured

### `capture_exception_learning(exception, context, project_root)`

Quick function to capture learning from exception.

Args:
    exception: Exception that occurred
    context: Context when exception occurred
    project_root: Optional project root path

Returns:
    True if lesson captured

---

## src.cortex_agents.screenshot_analyzer

ScreenshotAnalyzer Agent

Analyzes UI screenshots to identify elements and suggest test IDs.
Helps with automated testing by providing Playwright selector suggestions
and element identification from visual inputs.

The ScreenshotAnalyzer uses basic image analysis techniques to assist
with test automation and UI element discovery.

### ScreenshotAnalyzer

Analyzes UI screenshots for test automation.

The ScreenshotAnalyzer processes screenshots to identify UI elements,
suggest Playwright/Selenium test IDs, and provide element descriptions
to assist with automated testing.

Features:
- UI element identification from screenshots
- Test ID/selector suggestions
- Element type classification (button, input, etc.)
- Accessibility label extraction
- Position-based element grouping

Note: This is a basic implementation. In production, this would
integrate with actual image recognition libraries (PIL, OpenCV, etc.)

Example:
    analyzer = ScreenshotAnalyzer(name="Analyzer", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="analyze_screenshot",
        context={"image_base64": "data:image/png;base64,..."},
        user_message="Find test IDs in this login page screenshot"
    )
    
    response = analyzer.execute(request)
    # Returns: {
    #   "elements": [
    #     {"type": "button", "label": "Login", "suggested_id": "btn-login"},
    #     {"type": "input", "label": "Email", "suggested_id": "input-email"}
    #   ],
    #   "recommendations": ["Use data-testid attributes", "Add ARIA labels"]
    # }

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request to evaluate
    
Returns:
    True if intent is screenshot analysis, False otherwise

#### `execute(self, request)`

Analyze screenshot to identify UI elements.

Args:
    request: Agent request with image data in context
    
Returns:
    AgentResponse with identified elements and test ID suggestions

---

## src.cortex_agents.session_resumer

SessionResumer Agent

Restores conversation context from Tier 1 working memory.
Reconstructs conversation history, context, and state to resume work
after interruptions or session changes.

The SessionResumer helps CORTEX overcome "amnesia" by retrieving and
reconstructing previous conversation context.

### SessionResumer

Restores conversation context from Tier 1 working memory.

The SessionResumer retrieves conversation history from Tier 1 and
reconstructs the full context needed to continue work seamlessly
after interruptions or session changes.

Features:
- Conversation history retrieval from Tier 1
- Context reconstruction from conversation messages
- File and entity extraction from conversation
- Timeline reconstruction for work resumption
- Multi-turn conversation support

Example:
    resumer = SessionResumer(name="Resumer", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="resume",
        context={"conversation_id": "conv-123"},
        user_message="Resume previous conversation about authentication"
    )
    
    response = resumer.execute(request)
    # Returns: {
    #   "conversation_id": "conv-123",
    #   "messages": [...],
    #   "summary": "Working on authentication feature",
    #   "files_discussed": ["auth.py", "user.py"],
    #   "entities": ["User", "Auth", "JWT"]
    # }

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: The agent request to evaluate
    
Returns:
    True if intent is resume/restore/continue, False otherwise

#### `execute(self, request)`

Restore conversation context from Tier 1.

Args:
    request: Agent request with conversation_id in context
    
Returns:
    AgentResponse with conversation history and reconstructed context

---

## src.cortex_agents.strategic.__init__

Strategic Agents Package

Contains agents responsible for strategic planning, architectural analysis, and routing:
- IntentRouter: Determines user intent and routes to appropriate workflow
- ArchitectAgent: Deep architectural analysis with automatic brain saving (CORTEX-BRAIN-001 fix)
- WorkPlanner: Creates multi-phase strategic plans
- ChangeGovernor: Protects system integrity

Key CORTEX-BRAIN-001 Fix:
- ArchitectAgent automatically saves architectural analysis to Tier 2 Knowledge Graph
- Namespace detection (e.g., ksessions_architecture, ksessions_features.etymology)
- User confirmation of brain saves to build confidence in memory system

---

## src.cortex_agents.strategic.architect

Architect Agent - Strategic architectural analysis with automatic brain saving.

Handles:
- System architecture analysis
- Routing system investigation  
- Component structure mapping
- View injection pattern analysis
- Feature architecture documentation
- Automatic saving of analysis to Tier 2 Knowledge Graph

This agent addresses CORTEX-BRAIN-001 incident by ensuring architectural
analysis is automatically persisted across sessions.

### ArchitectAgent

Strategic agent for architectural analysis with automatic brain saving.

Performs deep architectural analysis including:
- Shell structure analysis (layout, navigation, panels)
- Routing system mapping (states, URLs, templates)
- View injection pattern documentation
- Feature directory structure analysis
- Component interaction flows

Key Features:
- Automatic namespace detection (e.g., ksessions_architecture)
- Structured analysis data persistence
- Cross-session memory via Tier 2 Knowledge Graph
- User confirmation of brain saves

Example:
    architect = ArchitectAgent("Architect", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="analyze_architecture",
        context={"workspace_path": "/path/to/KSESSIONS"},
        user_message="crawl shell.html to understand KSESSIONS architecture"
    )
    
    response = architect.execute(request)
    # Analysis automatically saved to brain with namespace: ksessions_architecture

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Handles architectural analysis requests including:
- Architecture analysis ("understand", "analyze", "crawl")
- Routing analysis ("routing", "navigation", "flow")
- Structure analysis ("structure", "layout", "components")
- Feature analysis ("feature", "directory", "organization")

Args:
    request: The agent request

Returns:
    True if intent matches architectural analysis patterns

#### `execute(self, request)`

Perform architectural analysis with automatic brain saving.

Args:
    request: The agent request

Returns:
    AgentResponse with analysis results and brain save confirmation

---

## src.cortex_agents.strategic.intent_router

IntentRouter Agent

Routes user requests to appropriate specialist agents based on intent analysis.
Uses Tier 2 Knowledge Graph to find similar past intents and improve routing decisions.

The IntentRouter is the entry point for all user requests - it analyzes the intent,
checks for patterns in past requests, and routes to the most appropriate specialist agent.

### IntentRouter

Routes user requests to appropriate specialist agents.

The IntentRouter analyzes user messages to determine intent, queries
Tier 2 for similar past requests, and makes routing decisions to
send requests to the most appropriate specialist agent(s).

Features:
- Multi-keyword intent classification
- Pattern-based routing using Tier 2
- Support for multi-agent routing
- Fallback handling for unknown intents
- Confidence scoring for routing decisions

Example:
    router = IntentRouter(name="Router", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="unknown",  # Will be classified
        context={},
        user_message="Create a new authentication module with tests"
    )
    
    response = router.execute(request)
    # Returns: {
    #   "primary_agent": AgentType.EXECUTOR,
    #   "secondary_agents": [AgentType.TESTER],
    #   "confidence": 0.85
    # }

**Methods:**

#### `can_handle(self, request)`

IntentRouter can handle all requests (it's the entry point).

Args:
    request: The agent request

Returns:
    Always True (router handles everything)

#### `execute(self, request)`

Route the request to appropriate specialist agent(s).

Args:
    request: The agent request to route

Returns:
    AgentResponse with routing decision and metadata

---

## src.cortex_agents.strategic.interactive_planner

Interactive Planner Agent (CORTEX 2.1)

Collaborative planning through guided dialogue. Asks clarifying questions
to resolve ambiguous requirements before creating implementation plans.

This agent implements confidence-based routing:
- High confidence (>85%): Execute immediately (no questions)
- Medium confidence (60-85%): Confirm plan with user
- Low confidence (<60%): Interactive questioning mode

Part of CORTEX 2.1 Interactive Planning enhancement.

### PlanningState

States in the interactive planning state machine.

### QuestionType

Types of questions that can be asked.

### Question

Represents a clarifying question to ask the user.

Attributes:
    text: Question text to display
    type: Question category (multiple choice, yes/no, etc.)
    options: Available options for multiple choice
    default: Default answer if user skips
    priority: Question priority (1-5, 5 = critical)
    context: Additional context about the question
    id: Unique identifier for the question

**Methods:**

### Answer

Represents a user's answer to a question.

Attributes:
    question_id: ID of the question being answered
    value: The answer value
    skipped: Whether question was skipped (using default)
    timestamp: When answer was provided
    additional_context: Any extra info extracted from answer

### PlanningSession

Represents an interactive planning session.

Tracks state, questions, answers, and final plan.
Persisted to Tier 1 memory for resumption.

Attributes:
    session_id: Unique session identifier
    user_request: Original user request
    confidence: Initial confidence score (0-1)
    state: Current state in planning workflow
    questions: Questions to ask (or already asked)
    answers: User's answers so far
    final_plan: Generated implementation plan
    started_at: Session start time
    completed_at: Session completion time

### InteractivePlannerAgent

Interactive Planning Agent - CORTEX 2.1

Collaborative planning through guided dialogue. Detects ambiguity
in user requests, asks up to 5 clarifying questions, and creates
refined implementation plans based on answers.

Features:
- Confidence-based routing (auto-detect when to ask questions)
- Question budget (max 5 questions per session)
- User controls: skip, done, back, restart, abort
- Session persistence (can resume interrupted sessions)
- User preference learning (adapts over time)

Workflow:
1. Detect ambiguity in user request
2. If confidence < 60%, enter interactive mode
3. Ask up to 5 clarifying questions (one at a time)
4. Build refined plan from answers
5. Confirm plan with user
6. Execute or save for later

Example:
    planner = InteractivePlannerAgent("Planner", tier1, tier2, tier3)
    
    request = AgentRequest(
        intent="plan",
        context={},
        user_message="Refactor authentication"
    )
    
    response = planner.execute(request)
    # Returns session with questions to ask

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

Args:
    request: Agent request to evaluate

Returns:
    True if request is PLAN intent, False otherwise

#### `execute(self, request)`

Execute interactive planning workflow.

Analyzes ambiguity and routes based on confidence:
- High confidence (>85%): Execute immediately
- Medium confidence (60-85%): Confirm plan
- Low confidence (<60%): Interactive questioning

Args:
    request: Agent request containing user message

Returns:
    AgentResponse with session state and next steps

#### `detect_ambiguity(self, request, context)`

Detect ambiguity in user request and calculate confidence score.

Analyzes request for clarity, specificity, and completeness.
Lower scores indicate more ambiguity (need more questions).

Args:
    request: User's request text
    context: Additional context

Returns:
    Confidence score (0.0 - 1.0)
    - 1.0 = completely clear, no questions needed
    - 0.5 = moderate ambiguity, some questions helpful
    - 0.0 = completely unclear, many questions needed

#### `generate_questions(self, request, context)`

Generate clarifying questions based on request analysis.

Prioritizes questions by importance and generates up to MAX_QUESTIONS.
Questions are tailored to the specific ambiguities detected.

Args:
    request: User's request text
    context: Additional context

Returns:
    List of Question objects (up to MAX_QUESTIONS)

#### `process_answer(self, session, question, answer_text)`

Process user's answer and extract context.

Args:
    session: Current planning session
    question: Question that was answered
    answer_text: User's answer text

Returns:
    Answer object with parsed value and context

#### `build_refined_plan(self, session)`

Build implementation plan from collected answers.

Delegates to WorkPlanner for proper task breakdown after enriching
the request with collected answers and context.

Args:
    session: Planning session with answers

Returns:
    Implementation plan dictionary with phases and tasks

---

## src.cortex_agents.strategic.question_generator

Question Generator Utility (CORTEX 2.1)

Generates high-quality clarifying questions for interactive planning.
Prioritizes questions by importance and adapts to user expertise level.

Part of CORTEX 2.1 Interactive Planning enhancement.

### QuestionPriority

Question priority levels (1-5).

### QuestionCategory

Categories of questions.

### QuestionTemplate

Template for generating context-aware questions.

Templates adapt to detected keywords and context to generate
relevant, specific questions for the user's request.

**Methods:**

#### `matches(self, request)`

Check if request triggers this template.

#### `generate(self, context)`

Generate question from template.

### QuestionGenerator

Generates clarifying questions for interactive planning.

Features:
- Template-based question generation
- Context-aware question adaptation
- Priority-based question ordering
- Dependency-aware question filtering
- User expertise level adaptation

Example:
    generator = QuestionGenerator()
    questions = generator.generate(
        request="Refactor authentication",
        context={"expertise": "intermediate"},
        max_questions=5
    )

**Methods:**

#### `generate(self, request, context, max_questions)`

Generate clarifying questions for a request.

Args:
    request: User's request text
    context: Additional context (expertise, preferences, etc.)
    max_questions: Maximum number of questions to generate

Returns:
    List of Question objects, prioritized and filtered

### `generate_questions(request, context, max_questions)`

Convenience function to generate questions.

Args:
    request: User's request text
    context: Additional context
    max_questions: Maximum questions to generate

Returns:
    List of Question objects

---

## src.cortex_agents.tactical.__init__

Tactical Agents Package

Contains agents responsible for tactical execution:
- CodeExecutor: Implements code changes
- TestGenerator: Creates and runs tests
- ErrorCorrector: Fixes errors and warnings
- HealthValidator: Validates system health
- CommitHandler: Manages git commits

---

## src.cortex_agents.test_generator.__init__

TestGenerator - Modular test generation agent.

Exports the main TestGenerator agent class.

---

## src.cortex_agents.test_generator.agent

TestGenerator Agent - Modular Version

Analyzes code and generates pytest-compatible test cases.
Creates comprehensive test suites with fixtures, mocks, and edge cases.

### TestGenerator

Generates pytest-compatible test cases from code analysis.

Features:
- AST-based code analysis
- pytest-style test generation
- Mock/fixture templates
- Pattern learning from Tier 2
- Coverage-aware generation

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

#### `execute(self, request)`

Generate test cases for code.

---

## src.cortex_agents.test_generator.analyzers.__init__

Analyzers for code analysis.

---

## src.cortex_agents.test_generator.analyzers.class_analyzer

Class analysis for test generation.

### ClassAnalyzer

Analyzes class definitions for test generation.

**Methods:**

#### `analyze(self, node)`

Analyze a class definition.

Args:
    node: AST ClassDef node

Returns:
    Class analysis info

---

## src.cortex_agents.test_generator.analyzers.code_analyzer

Code analysis for test generation.

### CodeAnalyzer

Analyzes source code to identify testable components.

**Methods:**

#### `analyze(self, source_code, target)`

Analyze source code to identify testable components.

Args:
    source_code: Python source code to analyze
    target: Optional specific class/function to target

Returns:
    Analysis results with functions, classes, and scenarios

---

## src.cortex_agents.test_generator.analyzers.function_analyzer

Function analysis for test generation.

### FunctionAnalyzer

Analyzes function definitions for test generation.

**Methods:**

#### `analyze(self, node)`

Analyze a function definition.

Args:
    node: AST FunctionDef node

Returns:
    Function analysis info

---

## src.cortex_agents.test_generator.generators.__init__

Test generators.

---

## src.cortex_agents.test_generator.generators.class_test_generator

Class test generation.

### ClassTestGenerator

Generates test code for classes.

**Methods:**

#### `generate(self, class_info)`

Generate tests for a class.

---

## src.cortex_agents.test_generator.generators.function_test_generator

Function test generation.

### FunctionTestGenerator

Generates test code for functions.

**Methods:**

#### `generate(self, func_info)`

Generate tests for a function.

---

## src.cortex_agents.test_generator.pattern_learner

Pattern learning for test generation.

### PatternLearner

Learns and retrieves test patterns from Tier 2.

**Methods:**

#### `find_similar_patterns(self, analysis)`

Search Tier 2 for similar test patterns.

Args:
    analysis: Code analysis results

Returns:
    List of similar test patterns

#### `store_pattern(self, analysis, test_code, test_count)`

Store test pattern in Tier 2 for learning.

Args:
    analysis: Code analysis
    test_code: Generated test code
    test_count: Number of tests generated

---

## src.cortex_agents.test_generator.templates.__init__

Templates for test generation.

---

## src.cortex_agents.test_generator.templates.template_manager

Test code templates.

### TemplateManager

Manages test code templates for different scenarios.

**Methods:**

#### `basic_function(self, func_info)`

Template for basic function test.

#### `class_method(self, method_info)`

Template for class method test.

#### `edge_cases(self, func_info)`

Template for edge case tests.

#### `error_handling(self, func_info)`

Template for error handling tests.

#### `test_header(self, analysis)`

Generate test file header with imports.

#### `fixtures(self, analysis)`

Generate pytest fixtures for classes.

---

## src.cortex_agents.test_generator.test_counter

Test counting utilities.

### TestCounter

Counts test functions in generated code.

**Methods:**

#### `count(self, test_code)`

Count number of test functions in generated code.

Args:
    test_code: Generated test code

Returns:
    Number of test functions

---

## src.cortex_agents.utils

Utility Functions for CORTEX Agents

Common helper functions used across multiple agents.

### `extract_file_paths(text)`

Extract file paths from text.

Matches patterns like:
- /absolute/path/to/file.py
- relative/path/to/file.js
- C:\Windows\path\file.txt

Args:
    text: Text to search for file paths

Returns:
    List of extracted file paths

Example:
    >>> extract_file_paths("Edit /src/app.py and /tests/test_app.py")
    ['/src/app.py', '/tests/test_app.py']

### `extract_code_intent(text)`

Extract primary code intent from user message.

Looks for action verbs: create, edit, update, delete, fix, etc.

Args:
    text: User message text

Returns:
    Primary intent verb or None if not found

Example:
    >>> extract_code_intent("Create a new authentication module")
    'create'

### `parse_priority_keywords(text)`

Parse priority level from keywords in text.

Keywords:
- urgent, critical, asap -> CRITICAL (1)
- important, high, soon -> HIGH (2)
- normal, standard -> NORMAL (3)
- low, later, when possible -> LOW (4)

Args:
    text: Text to analyze for priority keywords

Returns:
    Priority level (1-5)

Example:
    >>> parse_priority_keywords("This is URGENT!")
    1

### `normalize_intent(intent)`

Normalize intent string to standard format.

Args:
    intent: Raw intent string

Returns:
    Normalized intent (lowercase, underscores)

Example:
    >>> normalize_intent("Create File")
    'create_file'

### `validate_context(context, required_keys)`

Validate that context contains required keys.

Args:
    context: Context dictionary to validate
    required_keys: List of required key names

Returns:
    True if all required keys present, False otherwise

Example:
    >>> validate_context({"file": "test.py"}, ["file", "line"])
    False

### `truncate_message(message, max_length)`

Truncate message to maximum length with ellipsis.

Args:
    message: Message to truncate
    max_length: Maximum length (default: 200)

Returns:
    Truncated message

Example:
    >>> truncate_message("A" * 300, 100)
    'A...A (truncated)'

### `format_duration(duration_ms)`

Format duration in human-readable string.

Args:
    duration_ms: Duration in milliseconds

Returns:
    Formatted duration string

Example:
    >>> format_duration(1234.56)
    '1.23s'
    >>> format_duration(45.2)
    '45ms'

### `safe_get(dictionary)`

Safely get nested dictionary value.

Args:
    dictionary: Dictionary to search
    *keys: Keys to traverse
    default: Default value if key not found

Returns:
    Value at keys path or default

Example:
    >>> safe_get({"a": {"b": {"c": 1}}}, "a", "b", "c")
    1
    >>> safe_get({"a": {"b": {}}}, "a", "b", "c", default=0)
    0

---

## src.cortex_agents.work_planner.__init__

WorkPlanner - Modular work planning agent.

Exports the main WorkPlanner agent class.

---

## src.cortex_agents.work_planner.agent

WorkPlanner Agent - Modular Version

Breaks down complex requests into actionable tasks with time estimates.
Uses Tier 2 Knowledge Graph to find similar workflow patterns and Tier 3 Context
Intelligence to inform velocity-aware time estimates.

### WorkPlanner

Breaks down complex requests into actionable tasks.

Features:
- Task decomposition based on complexity analysis
- Pattern-based task templates from Tier 2
- Velocity-aware time estimation using Tier 3
- Dependency identification and ordering
- Risk assessment for task execution

**Methods:**

#### `can_handle(self, request)`

Check if this agent can handle the request.

#### `execute(self, request)`

Generate task breakdown with time estimates.

---

## src.cortex_agents.work_planner.complexity_analyzer

Complexity analysis for work planning.

### ComplexityAnalyzer

Analyzes request complexity.

**Methods:**

#### `analyze(self, request)`

Analyze request complexity based on keywords and context.

Returns:
    Complexity level: "simple", "medium", or "complex"

---

## src.cortex_agents.work_planner.dependency_manager

Task dependency identification.

### DependencyManager

Identifies and manages task dependencies.

**Methods:**

#### `identify(self, tasks)`

Identify dependencies between tasks.

Args:
    tasks: List of tasks

Returns:
    Tasks with dependency information added

---

## src.cortex_agents.work_planner.estimator

Time estimation adjuster.

### Estimator

Adjusts task time estimates based on complexity and velocity.

**Methods:**

#### `adjust_estimates(self, tasks, complexity, velocity_data)`

Adjust task time estimates based on complexity and velocity.

Args:
    tasks: List of tasks with base_hours
    complexity: Complexity level
    velocity_data: Velocity metrics from Tier 3

Returns:
    Tasks with adjusted estimated_hours

---

## src.cortex_agents.work_planner.pattern_storage

Pattern storage for workflow learning.

### PatternStorage

Stores workflow patterns in Tier 2 for learning.

**Methods:**

#### `store(self, request_context, tasks, complexity, total_hours)`

Store workflow pattern in Tier 2 for learning.

Args:
    request_context: Original request context
    tasks: Generated task list
    complexity: Complexity level
    total_hours: Total estimated hours

---

## src.cortex_agents.work_planner.priority_calculator

Task priority calculation.

### PriorityCalculator

Calculates task priorities.

**Methods:**

#### `calculate(self, task, task_index, total_tasks)`

Calculate task priority based on position and characteristics.

Args:
    task: The task to prioritize
    task_index: Position in task list (0-based)
    total_tasks: Total number of tasks

Returns:
    Priority level

---

## src.cortex_agents.work_planner.risk_assessor

Risk assessment for tasks.

### RiskAssessor

Assesses execution risks for tasks.

**Methods:**

#### `assess(self, tasks, complexity, file_count)`

Assess risks for task execution.

Args:
    tasks: List of tasks
    complexity: Overall complexity level
    file_count: Number of files involved

Returns:
    Tasks with risk assessments added

---

## src.cortex_agents.work_planner.strategies.__init__

Task generation strategies.

---

## src.cortex_agents.work_planner.strategies.task_generator

Task templates and generation strategies.

### TaskGenerator

Generates tasks from templates and patterns.

**Methods:**

#### `match_template(self, request)`

Match request to a task template.

#### `create_generic_breakdown(self, request, complexity)`

Create generic task breakdown based on complexity.

---

## src.cortex_agents.work_planner.velocity_tracker

Velocity metrics tracker from Tier 3.

### VelocityTracker

Tracks development velocity metrics from Tier 3.

**Methods:**

#### `get_metrics(self)`

Get velocity/capacity metrics from Tier 3.

Returns:
    Velocity metrics dictionary or None if unavailable

---

## src.cortex_agents.work_planner.workflow_finder

Workflow pattern finder and extractor.

### WorkflowFinder

Finds similar workflow patterns from Tier 2.

**Methods:**

#### `find_similar(self, request, limit)`

Find similar workflow patterns from Tier 2.

Args:
    request: The agent request
    limit: Maximum number of patterns to return

Returns:
    List of similar workflow patterns

#### `extract_tasks(self, workflow)`

Extract tasks from a historical workflow pattern.

Args:
    workflow: Workflow pattern from Tier 2

Returns:
    List of tasks

---

## src.cortex_help

CORTEX Help System

Provides concise, bulletted command reference for easy memorization.
Shows entry point commands, slash commands, and natural language equivalents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### HelpFormat

Help display formats

### `show_help(format, category)`

Generate help text for CORTEX commands.

Args:
    format: Display format (concise, detailed, or category)
    category: Optional category filter

Returns:
    Formatted help text

Examples:
    >>> print(show_help())  # Quick bulletted list
    >>> print(show_help(HelpFormat.DETAILED))  # Full details
    >>> print(show_help(category=CommandCategory.PLATFORM))  # Platform commands only

### `get_quick_reference()`

Get ultra-concise quick reference - just the essentials.

Perfect for chat responses when user asks "what commands are available?"

Returns:
    Ultra-concise command list

### `handle_help_request(request)`

Handle help requests intelligently based on what user asks for.

Args:
    request: User's help request

Returns:
    Appropriate help text

Examples:
    "show help" → concise help
    "detailed help" → detailed help
    "platform commands" → platform category help
    "quick reference" → ultra-concise reference

### `cortex_help()`

Quick access to concise help.

---

## src.crawlers.__init__

CORTEX Crawler System

Unified crawler architecture for discovering and extracting knowledge from:
- UI components (React, Angular, Vue, etc.)
- REST APIs (endpoints, OpenAPI specs)
- Databases (Oracle, SQL Server, PostgreSQL, etc.)
- Development tools and configurations

Architecture:
- BaseCrawler: Abstract base class for all crawlers
- CrawlerOrchestrator: Manages crawler execution and dependencies
- Individual Crawlers: Specialized implementations for each domain

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.

---

## src.crawlers.base_crawler

Base Crawler Class for CORTEX

Provides abstract base class and common infrastructure for all CORTEX crawlers.
All crawlers (UI, API, Database, etc.) inherit from BaseCrawler.

Architecture:
- Standardized lifecycle (initialize → validate → crawl → store → cleanup)
- Error handling and retry logic
- Progress reporting
- Result standardization
- Knowledge graph integration

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.

### CrawlerStatus

Crawler execution status

### CrawlerPriority

Crawler execution priority

### CrawlerResult

Standardized result from crawler execution

**Methods:**

#### `to_dict(self)`

Convert result to dictionary

### BaseCrawler

Abstract base class for all CORTEX crawlers.

All crawlers must:
1. Inherit from BaseCrawler
2. Implement get_crawler_info() method
3. Implement validate() method
4. Implement crawl() method
5. Implement store_results() method

Lifecycle:
1. initialize() - Setup crawler (config, connections)
2. validate() - Check if crawler can run (dependencies, credentials)
3. crawl() - Execute discovery logic
4. store_results() - Save to knowledge graph
5. cleanup() - Release resources

Example:
```python
class UICrawler(BaseCrawler):
    def get_crawler_info(self) -> Dict[str, Any]:
        return {
            'crawler_id': 'ui_crawler',
            'name': 'UI Component Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.HIGH,
            'dependencies': ['tooling_crawler']
        }
    
    def validate(self) -> bool:
        return self.workspace_path.exists()
    
    def crawl(self) -> Dict[str, Any]:
        # Discover UI components
        return {'components': [...]}
    
    def store_results(self, data: Dict[str, Any]) -> int:
        # Store in knowledge graph
        return len(data['components'])
```

**Methods:**

#### `get_crawler_info(self)`

Get crawler metadata.

Returns:
    Dictionary with:
        - crawler_id: Unique identifier
        - name: Human-readable name
        - version: Semantic version
        - priority: CrawlerPriority enum
        - dependencies: List of crawler_ids this depends on
        - description: Brief description

#### `validate(self)`

Validate crawler can execute.

Checks:
- Required dependencies available
- Credentials present
- Target resources accessible

Returns:
    True if crawler can run, False otherwise

#### `crawl(self)`

Execute crawler discovery logic.

Returns:
    Dictionary with discovered items (format varies by crawler)

#### `store_results(self, data)`

Store crawled data in knowledge graph.

Args:
    data: Data returned from crawl()
    
Returns:
    Number of patterns stored

#### `initialize(self)`

Initialize crawler (setup connections, validate config).

Returns:
    True if initialization successful

#### `cleanup(self)`

Cleanup resources (close connections, release locks).

Called after crawler completes or fails.

#### `execute(self)`

Execute complete crawler lifecycle.

Lifecycle:
1. Initialize
2. Validate
3. Crawl
4. Store results
5. Cleanup

Returns:
    CrawlerResult with execution details

---

## src.crawlers.orchestrator

Crawler Orchestrator for CORTEX

Manages execution of multiple crawlers with:
- Dependency resolution
- Parallel/sequential execution
- Result aggregation
- Error handling and retries
- Progress reporting

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.

### OrchestrationResult

Result from orchestrator execution

**Methods:**

#### `to_dict(self)`

Convert to dictionary

### CrawlerOrchestrator

Orchestrates execution of multiple crawlers.

Features:
- Dependency resolution (run tooling crawler first)
- Priority-based execution
- Parallel execution for independent crawlers
- Conditional execution (skip DB crawlers if no connections)
- Result aggregation and reporting

Usage:
```python
from crawlers import CrawlerOrchestrator
from crawlers.tooling_crawler import ToolingCrawler
from crawlers.ui_crawler import UICrawler
from crawlers.api_crawler import APICrawler

orchestrator = CrawlerOrchestrator(
    workspace_path=Path.cwd(),
    knowledge_graph=kg
)

orchestrator.register(ToolingCrawler)
orchestrator.register(UICrawler)
orchestrator.register(APICrawler)

result = orchestrator.run_all()
print(f"Completed: {result.completed}/{result.total_crawlers}")
```

**Methods:**

#### `register(self, crawler_class)`

Register a crawler class.

Args:
    crawler_class: Class inheriting from BaseCrawler

#### `run_all(self, crawler_ids)`

Run all registered crawlers (or specified subset).

Args:
    crawler_ids: Optional list of specific crawler IDs to run
    
Returns:
    OrchestrationResult with execution details

#### `run_single(self, crawler_id)`

Run a single crawler by ID.

Args:
    crawler_id: ID of crawler to run
    
Returns:
    CrawlerResult

#### `get_results(self)`

Get all crawler results.

Returns:
    Dictionary mapping crawler_id to CrawlerResult

#### `get_summary(self)`

Get execution summary.

Returns:
    Dictionary with summary statistics

---

## src.crawlers.tooling_crawler

Tooling Crawler for CORTEX

Discovers available development tools and configurations:
- Database connections (Oracle, SQL Server, PostgreSQL, MySQL)
- API endpoints and specifications
- Build tools and frameworks
- Development environment setup

This crawler runs FIRST and its results determine which other crawlers to execute.

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.

### DatabaseConnection

Database connection configuration

### APIEndpoint

API endpoint configuration

### BuildTool

Build tool configuration

### ToolingCrawler

Crawler for discovering development tools and configurations.

Discovery Methods:
1. Environment variables (connection strings, API URLs)
2. Configuration files (tnsnames.ora, appsettings.json, .env)
3. Code scanning (connection strings in source files)
4. Package manifests (package.json, pom.xml, *.csproj)
5. OpenAPI specifications

Results are used by orchestrator to determine which crawlers to run next.

**Methods:**

#### `get_crawler_info(self)`

Get crawler metadata

#### `validate(self)`

Validate crawler can execute

#### `crawl(self)`

Execute tooling discovery.

Returns:
    Dictionary with:
        - database_connections: Dict[str, List[DatabaseConnection]]
        - api_endpoints: List[APIEndpoint]
        - build_tools: List[BuildTool]
        - frameworks: List[str]

#### `store_results(self, data)`

Store discovery results in knowledge graph.

Args:
    data: Discovery results from crawl()
    
Returns:
    Number of patterns stored

---

## src.crawlers.ui_crawler

UI Crawler for CORTEX

Discovers and analyzes UI components from various frameworks:
- React/JSX/TSX components
- Angular components
- Vue components
- HTML element IDs
- Routes and navigation
- Component dependencies

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.

### UIComponent

UI component representation

### UICrawler

Crawler for discovering UI components and structure.

Discovery Methods:
1. React components (.jsx, .tsx files)
2. Angular components (.component.ts files)
3. Vue components (.vue files)
4. HTML element IDs
5. Route configurations
6. Component dependencies (imports)

Used for:
- UI testing automation (finding element IDs)
- Component inventory
- Route mapping
- Dependency analysis

**Methods:**

#### `get_crawler_info(self)`

Get crawler metadata

#### `validate(self)`

Validate crawler can execute

#### `crawl(self)`

Execute UI component discovery.

Returns:
    Dictionary with:
        - components: List[UIComponent]
        - element_ids: Set[str]
        - routes: Set[str]
        - framework_detected: str

#### `store_results(self, data)`

Store UI discovery results in knowledge graph.

Args:
    data: Discovery results from crawl()
    
Returns:
    Number of patterns stored

---

## src.entry_point.__init__

CORTEX Entry Point Package

Provides unified interface for all CORTEX interactions.

Main Components:
- CortexEntry: Main entry point coordinator
- RequestParser: Natural language → AgentRequest
- ResponseFormatter: AgentResponse → user-friendly output

Usage:
    from src.entry_point import CortexEntry
    
    cortex = CortexEntry()
    response = cortex.process("Add tests for auth.py")
    print(response)

---

## src.entry_point.agent_executor

Agent Executor - Executes specific agents based on routing decisions

This module handles the actual execution of specialist agents after
the IntentRouter has determined which agents should handle a request.

Addresses CORTEX-BRAIN-001 incident by ensuring architectural analysis
requests are properly routed to and executed by the ArchitectAgent.

### AgentExecutor

Executes specific agents based on routing decisions.

This class takes routing decisions from IntentRouter and actually
instantiates and executes the appropriate specialist agents.

**Methods:**

#### `execute_routing_decision(self, routing_decision, request)`

Execute agents based on routing decision.

Args:
    routing_decision: Decision from IntentRouter
    request: Original user request
    
Returns:
    AgentResponse from executed agent(s)

---

## src.entry_point.cortex_entry

CORTEX Main Entry Point

This module provides the unified entry point for all CORTEX interactions.
It coordinates request parsing, agent routing, and response formatting.

Usage:
    from src.entry_point import CortexEntry
    
    entry = CortexEntry()
    response = entry.process("Add authentication to the login page")
    print(response)

CORTEX 2.0 Implementation Requirement:
    After completing any work (tests, features, refactoring), ALWAYS update:
    cortex-brain/cortex-2.0-design/IMPLEMENTATION-STATUS-CHECKLIST.md
    
    This is tracked automatically via _remind_checklist_update() method.

### CortexEntry

Main entry point for CORTEX system.

Coordinates all components:
- Request parsing (natural language → AgentRequest)
- Session management (conversation tracking)
- Agent routing (request → appropriate specialist)
- Response formatting (AgentResponse → user-friendly output)
- Tier integration (Tier 1, 2, 3 APIs)

Example:
    entry = CortexEntry()
    
    # Process single request
    response = entry.process("Create tests for auth.py")
    print(response)
    
    # Process with session continuity
    response = entry.process(
        "Make the button purple",
        resume_session=True  # References previous conversation
    )

**Methods:**

#### `process(self, user_message, resume_session, format_type, metadata)`

Process a user request through CORTEX.

Args:
    user_message: Natural language request from user
    resume_session: Whether to resume previous session
                   (uses 30-min boundary per Rule #11)
    format_type: Output format ("text", "json", "markdown")
    metadata: Optional additional metadata
    
Returns:
    Formatted response string

#### `process_batch(self, messages, resume_session, format_type)`

Process multiple requests in sequence.

Args:
    messages: List of user messages
    resume_session: Whether to use same session for all
    format_type: Output format
    
Returns:
    Formatted batch response

#### `get_session_info(self)`

Get information about current active session.

Returns:
    Session info dict or None if no active session

#### `end_session(self)`

Explicitly end current session.

Useful for starting fresh conversation.

#### `get_health_status(self)`

Get CORTEX system health status.

Returns:
    Health status dict with tier statuses

#### `setup(self, repo_path, verbose)`

Run CORTEX setup for a repository.

This command systematically:
1. Analyzes the repository structure
2. Installs all required tooling
3. Initializes the CORTEX brain (4-tier architecture)
4. Runs crawlers to feed the brain
5. Introduces CORTEX with links to documentation and story

Args:
    repo_path: Path to repository to setup (default: current directory)
    verbose: Show detailed progress output
    
Returns:
    Setup results dictionary
    
Example:
    entry = CortexEntry()
    results = entry.setup()
    
    # Or in a different repo
    results = entry.setup(repo_path="/path/to/project")

---

## src.entry_point.cortex_entry_workflows

CORTEX Entry Point Integration with Workflow Pipeline

Shows how to integrate the Workflow Pipeline System with the existing
CORTEX entry point and router.

Author: CORTEX Development Team
Version: 1.0

### CortexEntryWithWorkflows

Extended CORTEX entry point with workflow pipeline support

Backwards compatible - falls back to original routing if no workflow specified

**Methods:**

#### `process(self, user_message, resume_session, format_type, metadata, workflow_id)`

Process user request (with optional workflow)

Args:
    user_message: User's natural language request
    resume_session: Whether to resume previous session
    format_type: Output format ("text", "json", "markdown")
    metadata: Optional metadata
    workflow_id: Optional workflow to use (e.g., "secure_feature_creation")

Returns:
    Formatted response

### `process_with_workflow(user_message, workflow_id)`

Quick helper to process request with workflow

Args:
    user_message: User's request
    workflow_id: Optional workflow to use

Returns:
    Response string

Example:
    >>> result = process_with_workflow(
    ...     "Add authentication to login page",
    ...     workflow_id="secure_feature_creation"
    ... )
    >>> print(result)
    ✅ Workflow completed successfully
    Duration: 5.8s
    Stages: 8/8 succeeded
    ...

---

## src.entry_point.pagination

Pagination Manager for Chat Output

Provides simple persistence for paged outputs to avoid chat length limits.

Pages are stored per conversation under:
  cortex-brain/corpus-callosum/output_pages/{conversation_id}.json

Schema:
{
  "conversation_id": str,
  "continuation_id": str,
  "total": int,
  "current": int,   # 0-based index of last served page
  "pages": [str],
  "created": iso timestamp
}

### PaginationState

**Methods:**

#### `to_dict(self)`

### PaginationManager

Manage persisted paged outputs for a conversation.

**Methods:**

#### `create_pagination(self, conversation_id, pages)`

Create a pagination state and persist it; returns continuation_id.

#### `get_next(self, conversation_id)`

Return the next page content for a conversation, or None if no more.

---

## src.entry_point.request_parser

Request Parser for CORTEX Entry Point

Parses user messages into structured AgentRequest objects.
Extracts intent, context, priority, files, and other metadata
from natural language input.

### RequestParser

Parses user messages into structured agent requests.

The RequestParser analyzes natural language input to extract:
- Intent classification
- File paths and context
- Priority keywords
- Conversation ID for resumption
- Additional metadata

Example:
    parser = RequestParser()
    
    request = parser.parse(
        "Fix the bug in src/auth.py - this is urgent!",
        conversation_id="conv-123"
    )
    
    # Returns AgentRequest with:
    # - intent: "fix"
    # - context: {"files": ["src/auth.py"]}
    # - priority: CRITICAL (1)
    # - user_message: original message

**Methods:**

#### `parse(self, user_message, conversation_id, metadata)`

Parse user message into AgentRequest.

Args:
    user_message: The user's natural language message
    conversation_id: Optional conversation ID for resumption
    metadata: Optional additional metadata
    
Returns:
    Structured AgentRequest object

#### `parse_batch(self, messages, conversation_id)`

Parse multiple messages into requests.

Args:
    messages: List of user messages
    conversation_id: Optional conversation ID
    
Returns:
    List of AgentRequest objects

#### `extract_files_from_context(self, context)`

Extract file list from context.

Args:
    context: Context dictionary
    
Returns:
    List of file paths

#### `infer_agent_type(self, request)`

Infer which agent type should handle this request.

This is a helper for routing decisions.

Args:
    request: The parsed request
    
Returns:
    Suggested agent type name

#### `validate_request(self, request)`

Validate that request has required fields.

Args:
    request: The request to validate
    
Returns:
    Tuple of (is_valid, error_message)

---

## src.entry_point.response_formatter

Response Formatter for CORTEX Entry Point

Formats agent responses into user-friendly output with structured
metadata, success/error messages, and actionable context.

Supports 3 verbosity levels:
- concise: 50-150 words (default)
- detailed: 200-400 words
- expert: Full detail, no limit

Version 2.0: Integrated with Response Template System

### ResponseFormatter

Formats agent responses for user consumption with verbosity control.

The ResponseFormatter transforms AgentResponse objects into
human-readable formats with:
- Clear success/error messages
- Structured metadata
- Result data presentation
- Action summaries
- Recommendations and next steps
- Configurable verbosity levels

Verbosity Levels:
    - concise: Quick summary (50-150 words) - DEFAULT
    - detailed: Structured breakdown (200-400 words)
    - expert: Full technical detail (no limit)

Example:
    formatter = ResponseFormatter(default_verbosity="concise")
    
    response = AgentResponse(
        success=True,
        result={"files": ["src/auth.py"]},
        message="Task completed successfully",
        agent_name="CodeExecutor"
    )
    
    # Concise by default
    formatted = formatter.format(response)
    
    # Override per call
    detailed = formatter.format(response, verbosity="detailed")

**Methods:**

#### `format(self, response, verbosity, include_metadata, include_recommendations, format_type, conversation_id, enable_paging, max_chars)`

Format agent response into readable output with verbosity control.

Args:
    response: The AgentResponse to format
    verbosity: Override default verbosity ("concise"|"detailed"|"expert")
    include_metadata: Whether to include metadata (auto-set if None)
    include_recommendations: Whether to include recommendations (auto-set if None)
    format_type: Output format ("text", "json", "markdown")
    
Returns:
    Formatted response string (may be paged when exceeding max_chars)

#### `format_batch(self, responses, include_summary, format_type)`

Format multiple responses.

Args:
    responses: List of responses to format
    include_summary: Whether to include summary section
    format_type: Output format
    
Returns:
    Formatted batch output

#### `format_error(self, error, context)`

Format an error into a user-friendly message.

Args:
    error: The exception that occurred
    context: Optional context about the error
    
Returns:
    Formatted error message

#### `format_from_template(self, template_id, context, verbosity)`

Format response using a template (v2.0).

This is the new template-based approach that provides:
- Zero execution overhead for pre-defined templates
- Consistent formatting across all components
- Easy maintenance (edit YAML, not code)

Args:
    template_id: Template identifier
    context: Dictionary of values for placeholder substitution
    verbosity: Override template verbosity
    
Returns:
    Formatted response string
    
Example:
    formatter.format_from_template(
        "executor_success",
        context={"files_count": 3, "next_action": "Run tests"},
        verbosity="concise"
    )

#### `format_from_trigger(self, trigger, context, verbosity)`

Format response by finding template via trigger phrase.

Args:
    trigger: Trigger phrase (e.g., "help", "status")
    context: Dictionary of values for placeholder substitution
    verbosity: Override template verbosity
    
Returns:
    Formatted response string
    
Example:
    formatter.format_from_trigger("help")  # Returns help table

#### `register_plugin_templates(self, plugin_id, templates)`

Register templates from a plugin.

Args:
    plugin_id: Plugin identifier
    templates: List of Template objects from plugin

#### `list_available_templates(self, category)`

List all available template IDs.

Args:
    category: Optional category filter (system, agent, operation, error, plugin)
    
Returns:
    List of template IDs

#### `format_progress(self, current, total, message)`

Format progress indicator.

Args:
    current: Current step
    total: Total steps
    message: Optional progress message
    
Returns:
    Formatted progress string

---

## src.entry_point.setup_command

CORTEX Setup Command

This module implements the "setup" command that initializes CORTEX in a new repository.
It systematically:
1. Installs all required tooling
2. Initializes the CORTEX brain structure
3. Runs crawlers to feed the brain
4. Introduces CORTEX to the user with links to documentation

Usage:
    from CORTEX.src.entry_point.setup_command import CortexSetup
    
    setup = CortexSetup()
    setup.run()

### CortexSetup

CORTEX setup orchestrator that handles complete system initialization.

Phases:
1. Environment Analysis - Detect repo structure, language, frameworks
2. Tooling Installation - Install Python deps, Node.js deps, MkDocs
3. Brain Initialization - Create tier directories, schemas, initial data
4. Crawler Execution - Scan repo and populate knowledge graph
5. Welcome Introduction - Show "Awakening" story and quick start guide

**Methods:**

#### `run(self)`

Run complete CORTEX setup process.

Returns:
    Setup results dictionary with status of each phase

### `run_setup(repo_path, brain_path, verbose)`

Convenience function to run CORTEX setup.

Args:
    repo_path: Path to repository (default: current directory)
    brain_path: Path for CORTEX brain (default: repo/cortex-brain)
    verbose: Show detailed output
    
Returns:
    Setup results dictionary

---

## src.llm.__init__

---

## src.llm.adapters.__init__

---

## src.llm.adapters.anthropic_adapter

### AnthropicAdapter

**Methods:**

#### `detect_capabilities(self)`

#### `generate(self, prompt_text, generation, tools_schema, system_text)`

---

## src.llm.adapters.base

### LLMProviderAdapter

Abstract base for provider-specific LLM adapters.

**Methods:**

#### `detect_capabilities(self)`

Return the static/detected capabilities for this provider/model.

#### `generate(self, prompt_text, generation, tools_schema, system_text)`

Generate a response for the given prompt and settings.

---

## src.llm.adapters.local_adapter

### LocalAdapter

**Methods:**

#### `detect_capabilities(self)`

#### `generate(self, prompt_text, generation, tools_schema, system_text)`

---

## src.llm.adapters.openai_adapter

### OpenAIAdapter

**Methods:**

#### `detect_capabilities(self)`

#### `generate(self, prompt_text, generation, tools_schema, system_text)`

---

## src.llm.fallback_manager

### `resolve_fallback_chain(primary)`

Produce a fallback chain given a primary.
Simple heuristic: if primary is openai -> anthropic -> local; if anthropic -> openai -> local; else -> openai -> local.

---

## src.llm.memory_injector

### `build_memory_context(user_query, namespace, include_generic, limit)`

Return a list of memory snippets to inject into prompts.

Each snippet is a dict like {"title": ..., "content": ..., "source": ...}.
This is a stub; wire to Tier 2 KnowledgeGraph later.

---

## src.llm.orchestrator

### LLMOrchestrator

Selects appropriate adapter and applies fallback strategy.

**Methods:**

#### `capabilities(self, provider)`

#### `generate(self, prompt_text, generation, tools_schema, system_text)`

---

## src.llm.types

### SafetyLevel

### LLMGenerationSettings

### LLMCaps

### ToolCall

### LLMResponse

### LLMError

### RateLimitExceeded

### ContextTooLarge

### ToolSchemaUnsupported

### SafetyBlocked

### TransportFailure

### GracefulTimeout

---

## src.metrics.__init__

CORTEX Metrics Module

Provides user-facing metrics and analytics for brain performance,
token optimization, and system health.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.metrics.brain_metrics_collector

Brain Metrics Collector

Aggregates metrics from Tier 1, 2, 3 for user-facing brain performance reports.

Schema Version: 2.1.0 (must match response-templates.yaml)
Last Updated: 2025-11-13

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### BrainMetricsCollector

Collects comprehensive metrics from all brain tiers.

**Schema Versioning:**
- Declares SCHEMA_VERSION to match template expectations
- All metric keys must match template placeholders
- Breaking changes require version bump

Provides session-level insights about:
- Tier 1: Working memory usage, conversations, messages
- Tier 2: Knowledge graph patterns, relationships, learning rate
- Tier 3: Development context, git metrics, velocity
- Token optimization: Savings, overhead, efficiency

**Methods:**

#### `get_brain_performance_metrics(self)`

Get comprehensive brain performance metrics.

Returns:
    Dict with metrics from all tiers for template rendering
    
Schema Compatibility:
    - Includes 'schema_version' key for template validation
    - All keys match template placeholders in response-templates.yaml
    - Missing tiers return safe defaults (0, 'Unknown', etc.)

#### `get_token_optimization_metrics(self)`

Get token optimization and cost savings metrics.

Returns:
    Dict with token savings analysis for template rendering
    
Schema Compatibility:
    - Includes 'schema_version' key for template validation

#### `get_brain_health_diagnostics(self)`

Get comprehensive brain health diagnostics.

Returns:
    Dict with health status for all tiers

---

## src.migrations.run_all_migrations

CORTEX Master Migration Runner
Orchestrates all three tier migrations in sequence

Sub-Group 3A: Phase 0.5 - Migration Tools

### `run_command(cmd, description)`

Run a command and return success status

Args:
    cmd: Command to run as list
    description: Description of what's being done
    
Returns:
    True if successful, False otherwise

### `main()`

---

## src.migrations.test_migration

CORTEX End-to-End Migration Test
Tests all three tier migrations and validates results

Task 0.5.4: End-to-End Migration Test
Duration: 30-45 minutes

### MigrationValidator

Validates all tier migrations

**Methods:**

#### `validate_tier1(self)`

Validate Tier 1 migration

#### `validate_tier2(self)`

Validate Tier 2 migration

#### `validate_tier3(self)`

Validate Tier 3 migration

#### `run_all_validations(self)`

Run all tier validations

### `main()`

---

## src.operations.__init__

CORTEX Operations Package - Universal Command Execution

This package provides the universal operations system that powers ALL CORTEX commands:
    - Environment setup (/setup)
    - Story refresh (/CORTEX, refresh cortex story)
    - Workspace cleanup (/CORTEX, cleanup)
    - Documentation updates (/CORTEX, generate documentation)
    - And all future operations

Main API:
    execute_operation(operation_id_or_input, **kwargs) → OperationExecutionReport

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### `execute_operation(operation_id_or_input, profile, project_root)`

Execute a CORTEX operation.

This is the main entry point for the universal operations system.
Supports both operation IDs and natural language input.

Args:
    operation_id_or_input: Either:
        - Operation ID: 'refresh_cortex_story', 'workspace_cleanup'
        - Natural language: 'refresh story', 'cleanup workspace'
        - Slash command: '/CORTEX, refresh cortex story'
        - Help command: 'help', '/CORTEX help', '/help'
    profile: Profile to use (minimal/standard/full) - default 'standard'
    project_root: Project root path (auto-detected if None)
    **kwargs: Additional context to pass to operation

Returns:
    OperationExecutionReport with execution details

Examples:
    # Show help
    report = execute_operation('help')
    
    # By operation ID
    report = execute_operation('refresh_cortex_story')
    
    # By natural language
    report = execute_operation('refresh the story')
    
    # By slash command
    report = execute_operation('/CORTEX, refresh cortex story')
    
    # With profile
    report = execute_operation('environment_setup', profile='full')
    
    # With custom context
    report = execute_operation(
        'refresh_cortex_story',
        project_root=Path('/path/to/cortex'),
        dry_run=True
    )

### `list_operations()`

List all available operations with their metadata.

Returns:
    Dict mapping operation IDs to operation info

Example:
    ops = list_operations()
    for op_id, info in ops.items():
        print(f"{op_id}: {info['name']}")
        print(f"  Commands: {info['natural_language']}")
        print(f"  Modules: {len(info['modules'])}")

### `get_operation_modules(operation_id, profile)`

Get list of modules for an operation.

Args:
    operation_id: Operation identifier
    profile: Profile to use

Returns:
    List of module IDs

Example:
    modules = get_operation_modules('refresh_cortex_story')
    # ['load_story_template', 'apply_narrator_voice', 'save_story_markdown']

### `create_orchestrator(operation_id, profile, context)`

Create orchestrator without executing it.

Useful for:
    - Previewing execution order
    - Custom execution flow
    - Testing

Args:
    operation_id: Operation identifier
    profile: Profile to use
    context: Initial context

Returns:
    Configured orchestrator, or None if failed

Example:
    orchestrator = create_orchestrator('refresh_cortex_story')
    if orchestrator:
        # Preview execution order
        modules = orchestrator.get_module_execution_order()
        print(f"Will execute: {modules}")
        
        # Execute with custom context
        report = orchestrator.execute_operation({'dry_run': True})

### `show_help(format)`

Display CORTEX command help.

Shows all available operations with status, examples, and module info.

Args:
    format: Output format - 'table' (default), 'list', or 'detailed'

Returns:
    Formatted help text

Example:
    # Show quick reference table
    print(show_help())
    
    # Show detailed with categories
    print(show_help('detailed'))
    
    # Show simple list
    print(show_help('list'))

---

## src.operations.base_operation_module

Base Operation Module - Universal Abstract Interface

This module provides the abstract base class that ALL operation modules inherit from,
whether for setup, story refresh, documentation updates, cleanup, or any other CORTEX command.

Design Principles (SOLID):
    - Single Responsibility: Each module does ONE thing
    - Open/Closed: Add new modules without modifying orchestrator
    - Liskov Substitution: All modules are interchangeable
    - Interface Segregation: Minimal required interface
    - Dependency Inversion: Depend on abstractions, not concrete implementations

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### OperationPhase

Universal phases for operation execution.

All CORTEX operations follow these phases:
    PRE_VALIDATION: Validate prerequisites before starting
    PREPARATION: Prepare resources, load data, setup context
    ENVIRONMENT: Configure environment-specific settings
    DEPENDENCIES: Install/verify dependencies
    PROCESSING: Main processing logic
    FEATURES: Enable/configure features
    VALIDATION: Verify results
    FINALIZATION: Cleanup, reporting, completion

**Methods:**

#### `order(self)`

Get execution order for phase.

### ExecutionMode

Execution mode for operations.

### OperationStatus

Status of operation module execution.

### OperationResult

Result of operation module execution.

Universal across ALL operations (setup, cleanup, story refresh, etc.)

Attributes:
    success: Whether module executed successfully
    status: Current module status
    message: Human-readable result message
    data: Operation-specific data (file paths, counts, metrics, etc.)
    errors: List of error messages if failed
    warnings: List of warning messages
    duration_seconds: Execution time
    timestamp: When module completed
    execution_mode: Whether this was a dry-run or live execution
    formatted_header: Formatted header for Copilot Chat display
    formatted_footer: Formatted footer for Copilot Chat display

**Methods:**

### OperationModuleMetadata

Metadata describing an operation module.

Universal metadata applicable to ALL operations.

Attributes:
    module_id: Unique identifier (e.g., 'platform_detection', 'refresh_story')
    name: Human-readable name
    description: What the module does
    phase: Which phase this module runs in
    priority: Execution order within phase (lower = earlier)
    dependencies: Module IDs that must complete before this module
    optional: Whether module failure should stop operation
    version: Module version for compatibility tracking
    author: Module author for copyright attribution
    tags: Categorization tags (e.g., ['environment', 'required'])

### BaseOperationModule

Abstract base class for ALL CORTEX operation modules.

This interface is used by:
    - Setup modules (platform detection, vision API, etc.)
    - Story refresh modules (load story, transform voice, etc.)
    - Cleanup modules (scan files, remove old logs, etc.)
    - Documentation modules (build docs, validate links, etc.)
    - And any future operations

Key Methods:
    get_metadata(): Returns module metadata
    validate_prerequisites(): Checks if module can run
    execute(): Performs module's main work
    rollback(): Undoes changes if needed
    should_run(): Conditional execution check

Example Usage:
    class MyCustomModule(BaseOperationModule):
        def get_metadata(self):
            return OperationModuleMetadata(
                module_id="my_module",
                name="My Custom Module",
                description="Does something useful",
                phase=OperationPhase.PROCESSING
            )
        
        def execute(self, context):
            # Do work
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Work completed"
            )

**Methods:**

#### `metadata(self)`

Get cached metadata.

#### `execution_mode(self)`

Get current execution mode.

#### `execution_mode(self, mode)`

Set execution mode.

#### `is_dry_run(self)`

Check if module is in dry-run mode (deprecated - always returns False).

#### `get_metadata(self)`

Return metadata describing this module.

Returns:
    OperationModuleMetadata with module information

#### `validate_prerequisites(self, context)`

Validate that prerequisites for this module are met.

Override to add custom prerequisite checks (e.g., required files exist,
environment variables set, previous modules completed).

Args:
    context: Shared context dictionary with operation state

Returns:
    Tuple of (is_valid, issues_list)
        - is_valid: True if prerequisites met
        - issues_list: List of issue descriptions (empty if valid)

Example:
    def validate_prerequisites(self, context):
        issues = []
        if 'project_root' not in context:
            issues.append("project_root not set in context")
        if not Path(context.get('config_file', '')).exists():
            issues.append("Config file not found")
        return len(issues) == 0, issues

#### `execute(self, context)`

Execute the module's main work.

This is where the module performs its primary function:
    - Setup modules: Configure environment
    - Story modules: Transform documentation
    - Cleanup modules: Remove temporary files
    - Docs modules: Build documentation

Args:
    context: Shared context dictionary
        - Read context from previous modules
        - Write results for downstream modules
        - Access operation-wide configuration

Returns:
    OperationResult with execution status and data

Example:
    def execute(self, context):
        try:
            project_root = context['project_root']
            # Do work
            context['my_module_output'] = result_data
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Module completed successfully",
                data={'processed': 42}
            )
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Module failed: {e}",
                errors=[str(e)]
            )

#### `rollback(self, context)`

Rollback changes made by this module.

Called when:
    - This module failed and needs cleanup
    - A downstream module failed and operation is rolling back
    - User cancels operation mid-flight

Override to implement custom rollback logic:
    - Delete created files
    - Restore backups
    - Revert configuration changes
    - Undo database modifications

Args:
    context: Shared context dictionary (may contain rollback hints)

Returns:
    True if rollback successful, False if rollback failed

Example:
    def rollback(self, context):
        try:
            backup_file = context.get('my_module_backup')
            if backup_file:
                shutil.copy(backup_file, original_file)
            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

#### `should_run(self, context)`

Determine if this module should run based on context.

Override for conditional execution:
    - Skip if feature already configured
    - Skip if not needed on this platform
    - Skip if user preferences disable it

Args:
    context: Shared context dictionary

Returns:
    True if module should run, False to skip

Example:
    def should_run(self, context):
        # Only run on Windows
        return context.get('platform') == 'windows'
    
    def should_run(self, context):
        # Skip if already configured
        config = context.get('config', {})
        return not config.get('vision_api', {}).get('enabled', False)

#### `get_progress_message(self)`

Get progress message to show while module is running.

Returns:
    Human-readable progress message

Example:
    def get_progress_message(self):
        return f"Installing {self.package_count} Python packages..."

#### `log_info(self, message)`

Log info message (convenience wrapper).

#### `log_error(self, message)`

Log error message (convenience wrapper).

#### `log_warning(self, message)`

Log warning message (convenience wrapper).

#### `log_debug(self, message)`

Log debug message (convenience wrapper).

---

## src.operations.cleanup

Workspace Cleanup Operation
CORTEX 3.0 Phase 1.1 Week 3 - Monolithic MVP

Safely removes temporary files, old logs, and cache to free disk space.
Includes safety checks to never delete source code or critical files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### CleanupCategory

Categories of files that can be cleaned.

### CleanupResult

Result of cleanup operation.

**Methods:**

#### `add_file(self, path, size)`

Record file removal.

#### `add_directory(self, path, size)`

Record directory removal.

#### `add_error(self, message)`

Record error.

#### `add_skip(self, path, reason)`

Record skipped item.

#### `total_items_removed(self)`

Total files + directories removed.

#### `space_freed_mb(self)`

Space freed in MB.

### `is_safe_to_delete(path, project_root)`

Check if path is safe to delete.

NEVER deletes:
    - Source code (.py, .js, .ts, .java, .cpp, etc.)
    - Configuration files (.yaml, .json, .toml, .ini)
    - Documentation (.md, .rst, .txt)
    - Git repository (.git/)
    - Brain databases (cortex-brain/*.db)
    - Package manifests (requirements.txt, package.json, etc.)

Args:
    path: Path to check
    project_root: Project root directory

Returns:
    (is_safe, reason)

### `find_temp_files(project_root)`

Find temporary files in project.

Targets:
    - *.tmp, *.temp
    - __pycache__ directories
    - *.pyc, *.pyo, *.pyd files
    - .pytest_cache directories
    - *.log files in temp locations

Args:
    project_root: Project root directory

Returns:
    List of temporary file/directory paths

### `find_old_logs(project_root, days_old)`

Find log files older than specified days.

Args:
    project_root: Project root directory
    days_old: Consider files older than this many days

Returns:
    List of old log file paths

### `find_large_cache_files(project_root, min_size_mb)`

Find large cache files (>10MB by default).

Args:
    project_root: Project root directory
    min_size_mb: Minimum file size in MB

Returns:
    List of large cache file paths

### `get_size(path)`

Get total size of file or directory in bytes.

Args:
    path: File or directory path

Returns:
    Total size in bytes

### `cleanup_workspace(project_root, dry_run, categories, confirm)`

Clean workspace by removing temporary files, old logs, and cache.

Args:
    project_root: Project root directory (auto-detected if None)
    dry_run: If True, only show what would be deleted
    categories: List of cleanup categories (all by default)
    confirm: If True, prompt for confirmation before deleting

Returns:
    Dictionary with cleanup results

### `main()`

CLI entry point for cleanup operation.

---

## src.operations.crawlers.__init__

CORTEX Discovery Report Crawlers

This package contains crawlers that analyze different aspects of a project
to generate comprehensive discovery reports showcasing CORTEX intelligence.

Available Crawlers:
- FileScannerCrawler: Analyze file structure and technology stack
- GitAnalyzerCrawler: Extract development history and activity
- TestParserCrawler: Analyze test coverage and quality
- DocMapperCrawler: Map documentation structure
- BrainInspectorCrawler: Analyze CORTEX brain state (Tier 1/2/3)
- PluginRegistryCrawler: Inventory plugin ecosystem
- HealthAssessorCrawler: Evaluate project health and provide recommendations

---

## src.operations.crawlers.base_crawler

Base Crawler Class for Discovery Report System

All discovery crawlers inherit from this base class, which provides:
- Standard interface for crawling
- Error handling
- Logging
- Timeout management

### BaseCrawler

Abstract base class for all discovery crawlers.

Each crawler analyzes one aspect of the project (files, git, tests, etc.)
and returns structured data for report generation.

**Methods:**

#### `crawl(self)`

Execute crawler and return discovery data.

Returns:
    Dict containing crawler-specific discovery data
    
Example structure:
    {
        "success": True,
        "data": {...},
        "errors": [],
        "warnings": []
    }

#### `get_name(self)`

Return crawler name for logging and identification.

Returns:
    Human-readable crawler name (e.g., "File Scanner")

#### `execute(self)`

Execute crawler with error handling and timing.

This wraps the crawl() method with standard error handling,
logging, and performance tracking.

Returns:
    Dict containing:
        - success: bool
        - data: crawler-specific data
        - crawler_name: str
        - execution_time_ms: float
        - errors: list of error messages

#### `handle_error(self, error, execution_time)`

Standard error handling for all crawlers.

Args:
    error: Exception that occurred
    execution_time: Time spent before error (ms)
    
Returns:
    Dict with error information in standard format

#### `log_warning(self, message)`

Log a warning message.

#### `log_info(self, message)`

Log an info message.

#### `log_error(self, message)`

Log an error message.

---

## src.operations.crawlers.brain_inspector

Brain Inspector Crawler

Analyzes CORTEX brain state across all tiers (Tier 1, 2, 3).

### BrainInspectorCrawler

Inspects CORTEX brain to analyze:
- Tier 1: Conversation memory (working memory)
- Tier 2: Knowledge graph (learned patterns)
- Tier 3: Development context (project metrics)
- Brain health and protection rules

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Analyze CORTEX brain state across all tiers.

Returns:
    Dict containing brain analysis

---

## src.operations.crawlers.doc_mapper

Documentation Mapper Crawler

Maps documentation structure and assesses completeness.

### DocMapperCrawler

Maps documentation to analyze:
- Total documentation files
- Documentation types (user guides, API docs, design docs)
- Documentation coverage
- README quality
- Help system availability

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Map and analyze documentation structure.

Returns:
    Dict containing documentation analysis

---

## src.operations.crawlers.file_scanner

File Scanner Crawler

Analyzes project file structure and detects technology stack.

### FileScannerCrawler

Scans project files to analyze:
- Total files, directories, lines of code
- Programming languages (by extension)
- Framework indicators
- Project size classification

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Scan project files and analyze structure.

Returns:
    Dict containing file structure analysis

---

## src.operations.crawlers.git_analyzer

Git Analyzer Crawler

Extracts development history and activity patterns from Git.

### GitAnalyzerCrawler

Analyzes Git repository to extract:
- Total commits, branches, contributors
- Recent activity patterns
- Hot files (most changed)
- Branch health

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Analyze Git repository history and activity.

Returns:
    Dict containing Git analysis

---

## src.operations.crawlers.health_assessor

Health Assessor Crawler

Evaluates overall project health and provides recommendations.

### HealthAssessorCrawler

Evaluates project health based on data from other crawlers:
- Overall health score (0-10)
- Risk factors
- Opportunities for improvement
- Strengths
- Actionable recommendations

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Assess project health based on crawler data.

Returns:
    Dict containing health assessment

---

## src.operations.crawlers.plugin_registry

Plugin Registry Crawler

Inventories CORTEX plugin ecosystem and capabilities.

### PluginRegistryCrawler

Inventories CORTEX plugin system to analyze:
- Registered plugins (active/inactive)
- Natural language patterns
- Command registry entries
- Plugin health and initialization

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Inventory plugin ecosystem.

Returns:
    Dict containing plugin analysis

---

## src.operations.crawlers.test_parser

Test Parser Crawler

Analyzes test coverage and quality metrics.

### TestParserCrawler

Analyzes test suite to extract:
- Total tests (unit, integration, e2e)
- Test pass/fail rates
- Coverage percentage
- Untested modules

**Methods:**

#### `get_name(self)`

#### `crawl(self)`

Analyze test suite and coverage.

Returns:
    Dict containing test analysis

---

## src.operations.demo_discovery

Discovery Report Generator

Orchestrates crawlers and generates comprehensive project intelligence reports.

### DiscoveryReportGenerator

Orchestrates discovery crawlers and generates markdown reports.

This class:
1. Runs all crawlers in parallel
2. Aggregates results
3. Generates formatted markdown report
4. Saves to cortex-brain/discovery-reports/

**Methods:**

#### `generate(self)`

Generate discovery report.

Returns:
    Dict with:
        - success: bool
        - report_path: str (path to generated report)
        - execution_time_ms: float
        - summary: str

### `generate_discovery_report(project_root)`

Convenience function to generate discovery report.

Args:
    project_root: Project root directory (defaults to current directory)
    
Returns:
    Dict with generation results

---

## src.operations.environment_setup

CORTEX Environment Setup - Monolithic Script

Single-script implementation for environment setup operation.
Consolidates 11 modules into one cohesive workflow.

Design Philosophy (CORTEX 3.0):
- Monolithic-then-modular: Ship working MVP first
- User value over perfect architecture
- Refactor only when complexity warrants (>500 lines)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1)

### SetupResult

Result of environment setup operation.

**Methods:**

#### `to_dict(self)`

Convert to dictionary.

### EnvironmentSetup

Monolithic environment setup for CORTEX.

Consolidates functionality from 11 modules:
- project_validation
- platform_detection
- git_sync
- virtual_environment
- python_dependencies
- vision_api
- conversation_tracking
- brain_initialization
- brain_tests
- tooling_verification
- setup_completion

**Methods:**

#### `run(self, profile)`

Execute environment setup.

Args:
    profile: Setup profile (minimal, standard, full)
    
Returns:
    SetupResult with execution details

### `run_setup(profile, project_root)`

Run environment setup.

Args:
    profile: Setup profile (minimal, standard, full)
    project_root: Project root directory (default: current directory)
    
Returns:
    SetupResult with execution details

---

## src.operations.environment_setup_module

Environment Setup Operation - Module Wrapper
Integrates monolithic setup.py with CORTEX 2.0 operations system

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### EnvironmentSetupModule

Module wrapper for environment setup operation.

Bridges monolithic setup.py implementation with CORTEX 2.0
module-based operations architecture.

**Methods:**

#### `validate(self, context)`

Validate execution context.

Args:
    context: Execution context with optional 'profile' and 'project_root'

Returns:
    (is_valid, message)

#### `execute(self, context)`

Execute environment setup.

Args:
    context: {
        'profile': 'minimal' | 'standard' | 'full',
        'project_root': Optional[Path]
    }

Returns:
    OperationResult with setup details

#### `cleanup(self)`

Cleanup after execution (no-op for setup).

### `register()`

Register environment setup module with operations system.

---

## src.operations.header_formatter

CORTEX Orchestrator Header Formatter

Provides standardized headers for all CORTEX entry point orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### HeaderFormatter

Format headers for CORTEX orchestrators.

**Methods:**

#### `format_minimalist(operation_name, version, profile, mode, timestamp)`

Format minimalist header (Option C).

Used for: cleanup, optimization, design sync, story refresh, etc.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)

Returns:
    Formatted header string

#### `format_banner(operation_name, version, profile, mode, timestamp)`

Format banner-style header (Option D).

Used for: help module and other high-visibility entry points.

Args:
    operation_name: Name of the operation (e.g., "Help System")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "standard")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)

Returns:
    Formatted banner header string

#### `format_completion(success, duration_seconds, summary)`

Format completion footer.

Args:
    success: Whether operation succeeded
    duration_seconds: Total execution time
    summary: Optional summary message

Returns:
    Formatted completion footer

---

## src.operations.header_utils

CORTEX Orchestrator Header Utilities

Provides standardized copyright headers for all CORTEX entry point orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### `format_minimalist_header(operation_name, version, profile, mode, purpose)`

Format minimalist header (Option C) for orchestrators.

Returns the header as a string instead of printing.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode description (always "LIVE EXECUTION")
    purpose: Optional 1-2 line description of what will be accomplished

Returns:
    Formatted header string

### `print_minimalist_header(operation_name, version, profile, mode, purpose)`

Print minimalist header (Option C) for orchestrators.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode description (always "LIVE EXECUTION")
    purpose: Optional 1-2 line description of what will be accomplished

### `print_banner_header(operation_name, version, profile)`

Print banner-style header (Option D) for help module.

Args:
    operation_name: Name of the operation (e.g., "Help System")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile

### `format_completion_footer(operation_name, success, duration_seconds, summary, accomplishments)`

Format completion footer for orchestrators.

Returns the footer as a string instead of printing.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Execution duration
    summary: Optional summary message (single line)
    accomplishments: Optional list of bullet points showing what was done

Returns:
    Formatted footer string

### `print_completion_footer(operation_name, success, duration_seconds, summary, accomplishments)`

Print completion footer for orchestrators.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Execution duration
    summary: Optional summary message (single line)
    accomplishments: Optional list of bullet points showing what was done

---

## src.operations.help_command

CORTEX Help Command - Display Available Operations

Provides concise, user-friendly display of all CORTEX operations with:
    - Quick command reference
    - Natural language examples
    - Implementation status
    - Underlying orchestration modules

Author: Asif Hussain
Version: 1.0

### HelpCommand

Generate help text for CORTEX operations.

Displays:
    - Quick commands (shortest natural language phrase)
    - Natural language example (most common usage)
    - Orchestration module (operation_id)
    - Status (✅ ready, ⏸️ pending, 🎯 planned)

**Methods:**

#### `generate_help(self, format)`

Generate help text for all CORTEX operations.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

#### `get_operation_by_command(self, command)`

Find operation by quick command.

Args:
    command: Quick command string

Returns:
    Operation data dictionary

### `show_help(format)`

Convenience function to display CORTEX help.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

Example:
    print(show_help())
    print(show_help('detailed'))

### `find_command(command)`

Find operation by command.

Args:
    command: Command string to search for

Returns:
    Operation data dictionary

Example:
    op = find_command('setup')
    print(f"Operation: {op['operation_id']}")

---

## src.operations.modules.__init__

Operation Modules Package

All concrete operation modules implementing BaseOperationModule interface.
Each module handles ONE specific operation responsibility (SOLID Single Responsibility Principle).

Covers:
    - Setup operations (platform detection, dependencies, etc.)
    - Story refresh operations (load, transform, save, etc.)
    - Cleanup operations (temp files, logs, etc.)
    - Documentation operations (API docs, design docs, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.operations.modules.apply_narrator_voice_module

Apply Narrator Voice Module - Story Refresh Operation

This module transforms the CORTEX story by rebuilding it with current
architecture state, implementation metrics, and feature availability.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture - Live Transformation)

### ApplyNarratorVoiceModule

Transform story with current CORTEX architecture state.

This module rebuilds the CORTEX story from scratch using current implementation data:
- Module counts and completion percentages
- Response template statistics
- Natural language interface capabilities
- Test coverage and implementation status
- Feature availability and roadmap

What it does:
    1. Gathers current architecture state from multiple sources
    2. Rebuilds story sections with actual metrics
    3. Preserves narrative voice and engaging style
    4. Optimizes for 25-30 minute read time target
    5. Validates structure and content quality

Data Sources:
- cortex-operations.yaml - Module definitions and operations
- response-templates.yaml - Template count and coverage
- knowledge-graph.yaml - Learned patterns
- implementation status files - Actual progress metrics

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that story content is available.

Args:
    context: Must contain 'story_content'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Transform story with current CORTEX architecture state.

This is a LIVE transformation operation that rebuilds the story from scratch.

Steps:
1. Load current architecture state (modules, templates, features)
2. Extract key metrics and implementation status
3. Rebuild story sections with actual data
4. Preserve narrative voice and engaging style
5. Validate read time (25-30 minutes target)
6. Return transformed content

Args:
    context: Shared context dictionary
        - Input: story_content (str) - Original story template
        - Output: transformed_story (str) - Rebuilt story with current data

Returns:
    OperationResult with transformation status and metrics

#### `rollback(self, context)`

Rollback narrator voice transformation.

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds)

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True (always run for story refresh)

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.brain_initialization_module

Brain Initialization Setup Module

Initializes CORTEX brain databases (Tier 1, 2, 3) and knowledge graph.

SOLID Principles:
- Single Responsibility: Only handles brain initialization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### BrainInitializationModule

Setup module for initializing CORTEX brain.

Responsibilities:
1. Initialize Tier 1 (SQLite database for conversation history)
2. Initialize Tier 2 (YAML knowledge graph)
3. Initialize Tier 3 (Development context)
4. Create required directories
5. Verify brain health

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for brain initialization.

Checks:
1. Project root exists
2. cortex-brain directory exists or can be created
3. Required Python packages available (PyYAML, sqlite3)

#### `execute(self, context)`

Execute brain initialization.

Steps:
1. Initialize Tier 1 database
2. Initialize Tier 2 knowledge graph
3. Initialize Tier 3 context
4. Verify brain health
5. Update context

---

## src.operations.modules.brain_tests_module

Brain Tests Setup Module

Validates brain initialization with quick tests.

SOLID Principles:
- Single Responsibility: Only handles brain validation tests
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### BrainTestsModule

Setup module for brain validation tests.

Responsibilities:
1. Verify Tier 0 (brain protection rules loaded)
2. Verify Tier 1 (conversation history database)
3. Verify Tier 2 (knowledge graph)
4. Run quick validation queries
5. Report brain health status

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for brain tests.

Checks:
1. Brain initialized
2. Brain path exists

#### `execute(self, context)`

Execute brain validation tests.

Steps:
1. Test Tier 0 (brain protection rules)
2. Test Tier 1 (conversation history)
3. Test Tier 2 (knowledge graph)
4. Generate test summary

---

## src.operations.modules.build_consolidated_story_module

Build Consolidated Story Module - Story Refresh Operation

This module creates THE-AWAKENING-OF-CORTEX.md by merging all 9 chapter files
with the original introduction from the "Awakening Of CORTEX.md" file.

Mode-aware:
- generate-from-scratch: Regenerates entire consolidated story
- update-in-place: Updates only changed sections

Author: Asif Hussain
Version: 2.0 (Mode-aware with read-time optimization)

### BuildConsolidatedStoryModule

Build consolidated CORTEX story from individual chapters.

This module creates THE-AWAKENING-OF-CORTEX.md by:
1. Preserving the original introduction with Asif Codeinstein, 
   basement lab, Copilot as physical machine, and Wizard of Oz inspiration
2. Merging all 9 individual chapter files in sequence
3. Adding proper navigation and flow
4. Optimizing for read time (60-75 minutes target)
5. Enforcing 95% story / 5% technical ratio

What it does:
    1. Reads intro or generates it
    2. Reads all 9 chapter files (01-amnesia-problem.md through 09-awakening.md)
    3. Combines them into a single consolidated story
    4. Calculates read time and story:technical ratio
    5. Writes to THE-AWAKENING-OF-CORTEX.md

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that all chapter files exist.

Args:
    context: Must contain 'project_root'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Build consolidated story file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: consolidated_story (str), consolidated_path (Path)

Returns:
    OperationResult with consolidation status

#### `rollback(self, context)`

Rollback by removing consolidated file.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True (always run for story consolidation)

#### `get_progress_message(self)`

Get progress message.

#### `get_progress_message(self)`

Get progress message.

### `register()`

Register this module.

---

## src.operations.modules.build_documentation_module

Build documentation module for documentation generation.

Part of the Documentation Update operation - transforms docstrings into structured Markdown files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### BuildDocumentationModule

Build documentation from docstring index.

Transforms the docstring index from ScanDocstringsModule into:
- Markdown reference documentation
- Module hierarchy pages
- API reference index
- Search-friendly structure

Output format compatible with MkDocs, GitHub Pages, and static site generators.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute documentation building.

Args:
    context: Operation context with docstring_index from scan module
    
Returns:
    OperationResult with build status and file paths

---

## src.operations.modules.build_mkdocs_site_module

Build MkDocs site module for automated documentation.

Part of the Documentation Update operation - builds the documentation site using MkDocs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### BuildMkDocsSiteModule

Build documentation site with MkDocs.

Executes `mkdocs build` to generate static HTML documentation
from Markdown source files. Validates that MkDocs is installed
and handles build errors gracefully.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute MkDocs build.

Args:
    context: Operation context
    
Returns:
    OperationResult with build status

### `register()`

Register module for discovery.

---

## src.operations.modules.build_story_preview_module

Build Story Preview Module - Story Refresh Operation

This module builds an HTML preview of the refreshed CORTEX story using MkDocs.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### BuildStoryPreviewModule

Build HTML preview of story.

This module uses MkDocs to generate an HTML preview of the CORTEX story
for immediate viewing.

What it does:
    1. Runs `mkdocs build` to generate HTML
    2. Verifies site/ directory was created
    3. Checks for story HTML file
    4. Provides preview URL

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that story was saved and project root is available.

Args:
    context: Must contain 'story_file_path' and 'project_root'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Build story preview.

Args:
    context: Shared context dictionary
        - Input: story_file_path (Path), project_root (Path)
        - Output: preview_path (Path), preview_url (str)

Returns:
    OperationResult with build status

#### `rollback(self, context)`

Rollback preview build (no-op - site/ can be rebuilt anytime).

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds)

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True only for 'full' profile

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.cleanup.__init__

Cleanup module for CORTEX operations.

Provides comprehensive workspace cleanup functionality including:
- Backup file management with GitHub archival
- Root folder organization
- File reorganization
- MD file consolidation
- Bloat detection
- Automatic optimization integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

---

## src.operations.modules.cleanup.cleanup_orchestrator

Cleanup Orchestrator for CORTEX 2.0

Comprehensive workspace cleanup orchestrator that:
- Deletes all backup files and folders (with GitHub archival)
- Keeps root folder clean and organized
- Reorganizes misplaced files to correct locations
- Removes redundancies in MD files (consolidates duplicates)
- Runs bloat tests on entry points and orchestrators
- Automatically triggers optimization orchestrator after cleanup
- Git tracking for all changes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### CleanupMetrics

Metrics from cleanup operation

**Methods:**

#### `space_freed_mb(self)`

#### `space_freed_gb(self)`

#### `to_dict(self)`

### CleanupOrchestrator

Orchestrates comprehensive workspace cleanup with:
- Backup file management (GitHub archival before deletion)
- Root folder organization
- File reorganization to correct locations
- MD file consolidation (removes duplicates)
- Bloat detection for entry points/orchestrators
- Automatic optimization trigger after cleanup

**Methods:**

#### `get_metadata(self)`

Module metadata.

#### `check_prerequisites(self, context)`

Check if cleanup can run

#### `execute(self, context)`

Execute comprehensive cleanup workflow

---

## src.operations.modules.cleanup.remove_obsolete_tests_module

Remove Obsolete Tests Module

Detects and removes test files calling non-existent APIs (methods removed during refactoring).
This prevents false test failures from outdated tests testing old implementations.

Detection Strategy:
1. Parse test files for method calls (._method_name patterns)
2. Check if those methods exist in current implementation
3. Mark tests as obsolete if calling removed private methods
4. Remove obsolete test files (with Git tracking)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### RemoveObsoleteTestsModule

Detects and removes tests calling non-existent implementation methods.

**Methods:**

#### `get_metadata(self)`

#### `execute(self, context)`

Find and remove obsolete test files.

Args:
    context: Must contain 'dry_run' boolean
    
Returns:
    OperationResult with removed_tests list

---

## src.operations.modules.clear_python_cache_module

Clear Python Cache Module

Removes all __pycache__ directories in the workspace.

SOLID Principles:
- Single Responsibility: Only handles Python cache removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ClearPythonCacheModule

Cleanup module for removing Python cache directories.

Responsibilities:
1. Remove __pycache__ directories identified in scan
2. Track removal success/failure
3. Calculate space recovered
4. Report removal results

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for cache removal.

Checks:
1. Scan results available

#### `execute(self, context)`

Execute Python cache removal.

Steps:
1. Get cache directories from scan results
2. Remove each directory
3. Track success/failure
4. Calculate space recovered

---

## src.operations.modules.conversation_tracking_module

Conversation Tracking Setup Module

Enables ambient conversation capture for CORTEX.

SOLID Principles:
- Single Responsibility: Only handles conversation tracking setup
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ConversationTrackingModule

Setup module for conversation tracking (ambient capture).

Responsibilities:
1. Check if ambient capture daemon is available
2. Verify daemon dependencies installed
3. Start daemon if not running
4. Provide status and instructions

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for conversation tracking.

Checks:
1. Project root exists
2. Brain initialized (conversation database exists)

#### `execute(self, context)`

Execute conversation tracking setup.

Steps:
1. Check if daemon script exists
2. Check if daemon is already running
3. Start daemon if needed
4. Verify daemon started successfully

---

## src.operations.modules.deploy_docs_preview_module

Deploy documentation preview module.

Part of the Documentation Update operation - deploys or serves documentation preview.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### DeployDocsPreviewModule

Deploy documentation preview.

Starts a local MkDocs server for documentation preview,
or optionally deploys to GitHub Pages (if configured).

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute documentation preview deployment.

Args:
    context: Operation context
    
Returns:
    OperationResult with deployment status

### `register()`

Register module for discovery.

---

## src.operations.modules.design_sync.__init__

Design Sync Module

Handles synchronization of CORTEX design documents with actual implementation.
Supports multi-track development with race metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.operations.modules.design_sync.design_sync_orchestrator

CORTEX Design Synchronization Orchestrator

Resolves the critical problem of design-implementation drift by:
1. Discovering actual implementation state (modules, operations, tests, plugins)
2. Analyzing gaps between design documents and reality
3. Integrating optimization recommendations from optimize_cortex
4. Converting verbose MD documents to structured YAML schemas
5. Consolidating multiple status files into ONE coherent status document
6. Applying all changes with git tracking for audit trail

Always works on LATEST design version (auto-detects, currently CORTEX 2.0).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0

### ImplementationState

Current implementation reality.

### DesignState

Design document state.

### GapAnalysis

Gaps between design and implementation.

### SyncMetrics

Metrics collected during sync.

### DesignSyncOrchestrator

Design-Implementation Synchronization Orchestrator.

Resolves design drift through 6-phase workflow:

Phase 1: Live Implementation Discovery
    - Scan src/operations/modules/ for actual module files
    - Parse cortex-operations.yaml for operation definitions
    - Count tests in tests/ directory
    - Discover plugins in src/plugins/
    - Build accurate implementation state

Phase 2: Design Document Discovery
    - Auto-detect LATEST design version (scan cortex-brain/cortex-2.0-design/)
    - Find all status files (STATUS.md, CORTEX2-STATUS.MD, etc.)
    - Identify verbose MD documents (>500 lines)
    - Catalog YAML schemas already present

Phase 3: Gap Analysis
    - Compare design claims vs actual implementation
    - Identify overclaimed features (claimed complete but not implemented)
    - Identify underclaimed features (implemented but not documented)
    - Find inconsistent module/test counts
    - Detect redundant status files
    - Flag verbose MD documents for YAML conversion

Phase 4: Optimization Integration
    - Run optimize_cortex to get latest recommendations
    - Parse optimization output for architectural improvements
    - Integrate recommendations into design updates
    - Prioritize by impact and feasibility

Phase 5: Document Transformation
    - Convert verbose MD to YAML schemas (preserving critical info)
    - Update status files with accurate counts
    - **Auto-generate "Recent Updates" from git commit history**
    - **Add contextual timestamps (e.g., "design_sync + deployment updates")**
    - Consolidate multiple status files into ONE source of truth
    - Generate visual progress bars based on reality
    - Apply consistent formatting

Phase 6: Git Commit & Reporting
    - Commit all changes with detailed messages
    - Generate comprehensive sync report
    - Update Enhancement & Drift Log in 00-INDEX.md
    - Provide next action recommendations

Usage:
    orchestrator = DesignSyncOrchestrator(project_root=Path('/path/to/cortex'))
    result = orchestrator.execute(context={'profile': 'comprehensive'})

Profiles:
    - quick: Discovery and analysis only (no changes)
    - standard: Discovery, analysis, consolidation (safe updates)
    - comprehensive: Full sync with optimization + YAML conversion

**Methods:**

#### `get_metadata(self)`

Module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for design sync.

Checks:
- Project root exists
- Git repository present
- Design directory exists
- Operations YAML accessible

Args:
    context: Shared execution context

Returns:
    Tuple of (is_valid, issues_list)

#### `execute(self, context)`

Execute design synchronization workflow.

Args:
    context: Shared execution context with 'profile' key

Returns:
    OperationResult with sync metrics and git commits

---

## src.operations.modules.design_sync.track_config

CORTEX Multi-Track Configuration Module

Manages machine track assignments with automatic phase distribution,
fun naming, and race metrics tracking.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0

### TrackMetrics

Real-time metrics for a track.

**Methods:**

#### `completion_percentage(self)`

Calculate completion percentage.

#### `status_emoji(self)`

Get status emoji based on performance.

### MachineTrack

Configuration for a machine's work track.

**Methods:**

### MultiTrackConfig

Multi-track configuration for distributed development.

**Methods:**

#### `is_multi_track(self)`

Check if multi-track mode is enabled.

#### `get_track_for_machine(self, machine_name)`

Get the track assigned to a specific machine.

#### `get_leader(self)`

Get the track currently in the lead.

### TrackNameGenerator

Generates fun, deterministic track names based on machine names.

**Methods:**

#### `generate(machine_name, index)`

Generate track name from machine name.

Args:
    machine_name: Name of the machine
    index: Optional index for multiple tracks on same machine

Returns:
    Tuple of (full_name, emoji, color)

### PhaseDistributor

Intelligent phase distribution across tracks.

Ensures:
- No cross-track dependencies
- Balanced workload by estimated hours
- Logical grouping of related modules

**Methods:**

#### `distribute(cls, modules, num_tracks, track_names)`

Distribute phases across tracks intelligently.

Args:
    modules: Module definitions from cortex-operations.yaml
    num_tracks: Number of tracks to distribute across
    track_names: List of track IDs

Returns:
    Dict mapping track_id -> list of assigned phases

### TrackConfigManager

Manages multi-track configuration persistence and loading.

**Methods:**

#### `load_from_config(config_path)`

Load multi-track config from cortex.config.json.

#### `save_to_config(config, config_path)`

Save multi-track config to cortex.config.json.

#### `create_multi_track_config(machines, modules, config_path)`

Create new multi-track configuration.

Args:
    machines: List of machine names (from cortex.config.json)
    modules: Module definitions (from cortex-operations.yaml)
    config_path: Path to cortex.config.json

Returns:
    MultiTrackConfig ready to use

---

## src.operations.modules.design_sync.track_templates

CORTEX Multi-Track Design Document Templates

Templates for split and consolidated design documents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0

### TrackDocumentTemplates

Templates for multi-track design documents.

**Methods:**

#### `generate_race_dashboard(config)`

Generate race dashboard header for split design docs.

Args:
    config: Multi-track configuration with metrics

Returns:
    Markdown table with live race metrics

#### `generate_track_section(track, modules)`

Generate track-specific section for split design doc.

Args:
    track: Track configuration
    modules: Module definitions

Returns:
    Markdown section for this track

#### `generate_split_document(config, modules, version)`

Generate complete split design document with race dashboard.

Args:
    config: Multi-track configuration
    modules: Module definitions
    version: CORTEX version

Returns:
    Complete Markdown document

#### `generate_consolidated_document(config, modules, version)`

Generate consolidated single-track document after merge.

Args:
    config: Multi-track configuration (for archive reference)
    modules: Module definitions
    version: CORTEX version

Returns:
    Complete consolidated Markdown document

---

## src.operations.modules.evaluate_cortex_architecture_module

Evaluate CORTEX Architecture Module - Story Refresh Operation

This module evaluates the current CORTEX architecture state by loading
CORTEX-UNIFIED-ARCHITECTURE.yaml and extracting feature inventory,
implementation status, and architecture patterns.

Author: Asif Hussain
Version: 1.0

### EvaluateCortexArchitectureModule

Evaluate current CORTEX architecture from CORTEX-UNIFIED-ARCHITECTURE.yaml.

This module loads the unified architecture document and extracts:
- Feature inventory (all components, agents, operations, plugins)
- Implementation status (completion %, tests passing, metrics)
- Architecture patterns (SOLID, plugin system, etc.)
- Changes since last refresh (if timestamp provided)

What it does:
    1. Loads CORTEX-UNIFIED-ARCHITECTURE.yaml
    2. Extracts core components (tiers, agents, operations, plugins)
    3. Extracts implementation status (progress, tests, metrics)
    4. Extracts architecture patterns
    5. Compares with last refresh timestamp (optional)

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Evaluate CORTEX architecture with mode detection.

Args:
    context: Shared context dictionary
        - Input: project_root (Path), last_refresh_timestamp (optional datetime)
          refresh_mode (optional: 'auto' | 'generate-from-scratch' | 'update-in-place')
          change_magnitude_threshold (optional: float, default 0.20)
        - Output: feature_inventory, implementation_status, architecture_patterns, 
          changes_since_last_refresh, recommended_mode, change_magnitude, mode_rationale

Returns:
    OperationResult with architecture evaluation and mode recommendation

#### `rollback(self, context)`

Rollback architecture evaluation (no-op).

### `register()`

Register module with operation system.

---

## src.operations.modules.generate_api_docs_module

Generate API documentation module for automated documentation.

Part of the Documentation Update operation - creates API reference from docstrings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### GenerateAPIDocsModule

Generate API documentation from docstring index.

Takes the structured docstring index from scan_docstrings module
and generates Markdown API reference documentation organized by
module hierarchy.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute API documentation generation.

Args:
    context: Operation context with docstring_index
    
Returns:
    OperationResult with generated documentation info

### `register()`

Register module for discovery.

---

## src.operations.modules.generate_cleanup_report_module

Generate Cleanup Report Module

Creates comprehensive cleanup summary report.

SOLID Principles:
- Single Responsibility: Only handles report generation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### GenerateCleanupReportModule

Finalization module for generating cleanup report.

Responsibilities:
1. Collect cleanup results from all modules
2. Calculate total space recovered
3. Generate formatted report
4. Display summary

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for report generation.

Checks:
1. Context available

#### `execute(self, context)`

Execute cleanup report generation.

Steps:
1. Collect cleanup results
2. Calculate totals
3. Generate formatted report
4. Display summary

---

## src.operations.modules.generate_history_doc_module

Generate History Doc Module

### GenerateHistoryDocModule

**Methods:**

#### `get_metadata(self)`

#### `validate(self, context)`

#### `execute(self, context)`

#### `rollback(self, context)`

#### `should_run(self, context)`

#### `get_progress_message(self)`

### `register()`

---

## src.operations.modules.generate_image_prompts_doc_module

Generate Image Prompts Doc Module - Story Refresh Operation

This module generates Image-Prompts.md with Gemini-compatible system diagram
prompts for visualizing CORTEX architecture.

Author: Asif Hussain
Version: 2.0 (Architecture-driven prompt generation)

### GenerateImagePromptsDocModule

Generate Image-Prompts.md for CORTEX architecture visualization.

This module creates Gemini-compatible image generation prompts for:
- 4-tier brain architecture diagram
- 10 specialist agents (LEFT/RIGHT brain)
- Plugin system architecture
- Memory flow diagrams
- Agent coordination patterns

What it does:
    1. Extracts architecture structure from context
    2. Generates detailed Gemini prompts for each diagram
    3. Includes style guides and technical specifications
    4. Writes to Image-Prompts.md

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `validate(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Generate Image-Prompts.md.

#### `rollback(self, context)`

Rollback by removing generated file.

#### `should_run(self, context)`

Determine if module should run.

#### `get_progress_message(self)`

Get progress message.

### `register()`

Register this module.

---

## src.operations.modules.generate_image_prompts_module

Generate Image Prompts Module - Story Refresh Operation

This module generates Gemini-compatible image prompts for technical system diagrams
based on the CopilotRecommendedDiagrams.md specification.

Author: Asif Hussain
Version: 1.0

### GenerateImagePromptsModule

Generate Gemini-compatible image prompts for CORTEX system diagrams.

This module reads CopilotRecommendedDiagrams.md and generates single-paragraph
prompts that Gemini's image generator can use to create professional technical
diagrams (flowcharts, sequence diagrams, architecture diagrams).

What it does:
    1. Loads CopilotRecommendedDiagrams.md
    2. Generates 10 technical diagram prompts (single paragraph each)
    3. Saves to docs/story/CORTEX-STORY/Image-Prompts.md
    4. Validates output structure

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Generate image prompts file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: image_prompts_path (Path), prompts_generated (int)

#### `rollback(self, context)`

Rollback image prompts generation.

#### `should_run(self, context)`

Determine if module should run.

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.generate_story_chapters_module

Generate Story Chapters Module - Story Refresh Operation

This module generates 9+ detailed story chapters with engaging narrative
featuring Asif Codeinstein in NJ basement and Wizard of Oz references.

Supports two modes:
- generate-from-scratch: Regenerate ALL chapters from architecture
- update-in-place: Update only affected chapters, preserve existing narrative

Author: Asif Hussain
Version: 1.0

### GenerateStoryChaptersModule

Generate or update story chapter files with engaging narrative.

This module creates 9 detailed chapter files in docs/story/CORTEX-STORY/:
- 01-amnesia-problem.md - The intern with amnesia
- 02-first-memory.md - Tier 1 working memory
- 03-brain-architecture.md - Four-tier brain system
- 04-left-brain.md - Tactical agents
- 05-right-brain.md - Strategic agents
- 06-corpus-callosum.md - Agent coordination
- 07-knowledge-graph.md - Tier 2 learning system
- 08-protection-layer.md - SKULL rules, Tier 0
- 09-awakening.md - Token optimization, future

Narrative style:
- Asif Codeinstein character (mad scientist developer in NJ basement)
- Wizard of Oz references (Scarecrow wanting a brain)
- Funny, engaging tone (2 AM debugging, coffee addiction)
- 95% story / 5% technical ratio

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Generate story chapters.

Args:
    context: Shared context dictionary
        - Input: project_root, feature_inventory, recommended_mode, changes_since_last_refresh
        - Output: chapters_generated, chapters_updated, chapters_unchanged, backups_created

Returns:
    OperationResult with chapter generation status

#### `rollback(self, context)`

Rollback chapter generation by restoring from backups.

### `register()`

Register module with operation system.

---

## src.operations.modules.generate_technical_cortex_doc_module

Generate Technical CORTEX Doc Module - Story Refresh Operation

This module generates Technical-CORTEX.md with comprehensive technical details
extracted from CORTEX-UNIFIED-ARCHITECTURE.yaml.

Author: Asif Hussain
Version: 2.0 (Mode-aware with architecture-driven generation)

### GenerateTechnicalCortexDocModule

Generate Technical-CORTEX.md from architecture data.

This module creates comprehensive technical documentation covering:
- System architecture (4-tier brain)
- 10 specialist agents (LEFT/RIGHT brain)
- Plugin system
- Memory architecture
- Test coverage & metrics
- Development guide

What it does:
    1. Extracts all technical details from architecture evaluation context
    2. Generates sections for tiers, agents, plugins, metrics
    3. Adds code examples and configuration guidance
    4. Writes to Technical-CORTEX.md

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `validate(self, context)`

Validate prerequisites.

Args:
    context: Shared context dictionary

Returns:
    OperationResult indicating validation status

#### `execute(self, context)`

Generate Technical-CORTEX.md.

Args:
    context: Shared context dictionary

Returns:
    OperationResult with generation status

#### `rollback(self, context)`

Rollback by removing generated file.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if architecture data available

#### `get_progress_message(self)`

Get progress message.

### `register()`

Register this module.

---

## src.operations.modules.generate_technical_doc_module

Generate Technical Documentation Module - Story Refresh Operation

This module generates the Technical-CORTEX.md file with comprehensive technical
specifications extracted from CORTEX 2.0 design documents.

Author: Asif Hussain
Version: 1.0

### GenerateTechnicalDocModule

Generate Technical-CORTEX.md with comprehensive technical specifications.

Extracts and consolidates technical details from CORTEX 2.0 design documents
including architecture diagrams, API references, performance metrics, and
implementation status.

What it does:
    1. Loads CORTEX 2.0 design documents
    2. Extracts technical specifications
    3. Generates comprehensive Technical-CORTEX.md
    4. Includes architecture diagrams, APIs, metrics

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Generate Technical-CORTEX.md file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: technical_doc_path (Path), sections_generated (int)

#### `rollback(self, context)`

Rollback technical doc generation.

#### `should_run(self, context)`

Determine if module should run.

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.git_sync_module

Git Synchronization Setup Module

Synchronizes CORTEX project with remote repository.

SOLID Principles:
- Single Responsibility: Only handles git synchronization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### GitSyncModule

Setup module for git repository synchronization.

Responsibilities:
1. Verify git is installed and available
2. Check if project is a git repository
3. Fetch latest changes from remote
4. Pull changes if safe to do so
5. Report sync status

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for git sync.

Checks:
1. Project root exists
2. Git command available (not blocking)

#### `execute(self, context)`

Execute git synchronization.

Steps:
1. Check if git is installed
2. Verify project is a git repository
3. Check for uncommitted changes
4. Fetch remote changes
5. Pull if safe (no conflicts)

---

## src.operations.modules.load_protection_rules_module

Load protection rules module for brain protection validation.

Part of the Brain Protection operation - loads brain-protection-rules.yaml.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### LoadProtectionRulesModule

Load brain protection rules from YAML configuration.

Loads and validates the brain-protection-rules.yaml file that defines
SKULL protection rules and tier protection policies.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute protection rules loading.

Args:
    context: Operation context
    
Returns:
    OperationResult with loaded rules

### `register()`

Register module for discovery.

---

## src.operations.modules.load_story_template_module

Load Story Template Module - Story Refresh Operation

This module loads the CORTEX story template from prompts/shared/story.md
as the first step in the story refresh operation.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### LoadStoryTemplateModule

Load the CORTEX story template file.

This module is part of the refresh_cortex_story operation and demonstrates
how the universal operations architecture works for non-setup commands.

What it does:
    1. Validates story file exists at prompts/shared/story.md
    2. Loads story content
    3. Validates basic Markdown structure
    4. Stores story content in context for downstream modules

Example Usage:
    # Via operation
    result = execute_operation("refresh_cortex_story")
    
    # Direct
    module = LoadStoryTemplateModule()
    context = {'project_root': Path('/path/to/cortex')}
    result = module.execute(context)
    story_content = context['story_content']

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that story file exists.

Args:
    context: Must contain 'project_root'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Load story template file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: story_content (str), story_path (Path), story_line_count (int)

Returns:
    OperationResult with story loading status

#### `rollback(self, context)`

Rollback story loading (no-op for read operation).

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds for read-only operations)

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True (always run for story refresh)

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.optimization.__init__

CORTEX Optimization Operation Modules

This package contains all modules for the 'optimize' operation that performs
holistic CORTEX architecture review and executes optimizations.

Modules:
    - optimize_cortex_orchestrator: Main entry point that coordinates optimization workflow

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.operations.modules.optimization.hardcoded_data_cleaner_module

Hardcoded Data Cleaner Module

Aggressively scans for and eliminates:
- Hardcoded file paths (absolute paths, Windows/Unix specific paths)
- Mock data masquerading as real data
- Fallback mechanisms that return fake values
- Test fixtures with hardcoded values
- Placeholder data in production code
- Default values that should be configuration-driven

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0

### HardcodedViolation

Represents a single hardcoded data violation.

### HardcodedDataMetrics

Metrics for hardcoded data detection.

### HardcodedDataCleanerModule

Aggressively detects hardcoded paths, mock data, and fallback mechanisms.

Detection Rules:

1. HARDCODED PATHS (CRITICAL):
   - Absolute paths: C:\Users\..., /home/user/..., D:\PROJECTS\...
   - Platform-specific paths without Path() wrapper
   - Hardcoded directory separators (\, /) instead of Path.joinpath

2. MOCK DATA (HIGH):
   - unittest.mock imports in non-test files
   - @patch, @MagicMock in production code
   - Functions returning hardcoded dicts/lists without data source
   - Fake/dummy/stub data in production code

3. FALLBACK VALUES (HIGH):
   - try/except returning hardcoded values on failure
   - .get() with hardcoded defaults that mask missing config
   - if/else chains with hardcoded fallbacks
   - Default values that should come from config/environment

4. TEST FIXTURES (MEDIUM):
   - Hardcoded test data inside test functions
   - No use of @pytest.fixture for shared test data
   - Inline dictionaries/lists with test values

5. PLACEHOLDER DATA (MEDIUM):
   - TODO/FIXME comments with temporary hardcoded values
   - Obvious placeholder strings ('test', 'example', 'dummy', 'fake')
   - Hardcoded URLs, API keys, database connections

Usage:
    cleaner = HardcodedDataCleanerModule()
    result = cleaner.execute(context={
        'project_root': Path('/path/to/project'),
        'scan_paths': [Path('src'), Path('tests')],
        'exclude_patterns': ['__pycache__', '.git'],
        'fail_on_critical': True
    })

**Methods:**

#### `get_metadata(self)`

Module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites.

Args:
    context: Shared execution context (must contain 'project_root')

Returns:
    Tuple of (is_valid, issues_list)

#### `execute(self, context)`

Execute hardcoded data detection.

Args:
    context: Shared execution context with keys:
        - project_root: Root path to scan (REQUIRED)
        - scan_paths: List of paths to scan (default: ['src', 'tests'])
        - exclude_patterns: Patterns to exclude (default: ['__pycache__', '.git'])
        - fail_on_critical: Fail if critical violations found (default: True)
        - fix_automatically: Attempt to fix violations (default: False)

Returns:
    OperationResult with detected violations

#### `rollback(self, context)`

Rollback changes (no changes made during scan).

Args:
    context: Shared execution context

Returns:
    Always True (nothing to rollback)

### HardcodedDataVisitor

**Methods:**

#### `visit_Return(self, node)`

Check for functions returning hardcoded dicts/lists.

#### `visit_Assign(self, node)`

Check for large hardcoded assignments.

### `register()`

Register module with operation factory.

---

## src.operations.modules.optimization.optimize_cortex_orchestrator

CORTEX Optimization Orchestrator

Performs holistic review of CORTEX architecture and executes optimizations
with full git tracking and metrics collection.

This orchestrator:
1. Runs all SKULL tests (brain protection validation)
2. Analyzes CORTEX architecture, operation history, patterns learned
3. Generates optimization plan with prioritized actions
4. Executes optimizations with git commits for tracking
5. Collects metrics on improvements achieved

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0

### OptimizationMetrics

Metrics collected during optimization execution.

### OptimizeCortexOrchestrator

Entry point orchestrator for CORTEX optimization.

Coordinates:
- SKULL test execution (brain protection validation)
- Architecture analysis (holistic review)
- Pattern learning (knowledge graph insights)
- Optimization planning (prioritized action generation)
- Optimization execution (with git tracking)
- Metrics collection (improvement tracking)

Usage:
    orchestrator = OptimizeCortexOrchestrator(project_root=Path('/path/to/cortex'))
    result = orchestrator.execute(context={})
    
    # Result includes:
    # - metrics: OptimizationMetrics with full details
    # - git_commits: List of commit hashes for tracking
    # - optimizations_applied: List of applied improvements

**Methods:**

#### `get_metadata(self)`

Module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for optimization.

Checks:
- Project root exists
- Git repository present
- Test suite available
- Knowledge graph accessible

Args:
    context: Shared execution context

Returns:
    Tuple of (is_valid, issues_list)

#### `execute(self, context)`

Execute CORTEX optimization workflow.

Workflow:
1. Initialize metrics collection
2. Run SKULL tests (brain protection validation)
3. Analyze architecture (holistic review)
4. Generate optimization plan
5. Execute optimizations (with git commits)
6. Collect final metrics

Args:
    context: Shared execution context

Returns:
    OperationResult with optimization metrics and git commits

#### `rollback(self, context)`

Rollback optimization changes.

Uses git to revert commits if needed.

Args:
    context: Shared execution context

Returns:
    True if successful, False otherwise

### `register()`

Register module with operation factory.

---

## src.operations.modules.optimize.__init__

CORTEX Optimization Module

Performs comprehensive system health checks and optimization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.operations.modules.optimize.optimize_cortex_orchestrator

CORTEX Optimize Entry Point Orchestrator

Performs comprehensive system health scans to ensure CORTEX is fully operational.

This orchestrator:
1. Scans all tests and identifies obsolete ones (calling non-existent APIs)
2. Checks code coverage and identifies dead code
3. Validates brain tier integrity (Tier 0, 1, 2, 3)
4. Checks agent health and coordination
5. Validates plugin system integrity
6. Checks dependency health
7. Generates comprehensive health report
8. Marks obsolete tests for cleanup

Natural Language Triggers:
- "optimize cortex"
- "run health check"
- "system scan"
- "check cortex health"
- "optimize workspace"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Date: November 11, 2025

### HealthIssue

Represents a health issue found during scan

### ObsoleteTest

Represents a test file that should be deleted

### SystemHealthReport

Complete system health report

**Methods:**

#### `to_dict(self)`

### OptimizeCortexOrchestrator

Comprehensive CORTEX optimization and health check orchestrator.

Performs full system scan to ensure CORTEX is operational:
- Identifies obsolete tests calling non-existent APIs
- Checks code coverage and dead code
- Validates brain integrity
- Checks agent and plugin health
- Generates actionable health report

**Methods:**

#### `get_metadata(self)`

Module metadata

#### `check_prerequisites(self, context)`

Check if optimization can run

#### `execute(self, context)`

Execute comprehensive CORTEX optimization.

Args:
    context: Execution context with optional settings:
        - profile: 'quick' | 'standard' | 'deep' (default: standard)
        - scan_tests: bool (default: True)
        - scan_coverage: bool (default: True)
        - scan_brain: bool (default: True)
        - mark_obsolete: bool (default: True)

Returns:
    OperationResult with health report and recommendations

### `register()`

Register the optimize orchestrator module

---

## src.operations.modules.platform_detection_module

Platform Detection Setup Module

Detects current platform (Mac/Windows/Linux) and configures environment accordingly.

SOLID Principles:
- Single Responsibility: Only handles platform detection and basic config
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PlatformDetectionModule

Setup module for platform detection and configuration.

Responsibilities:
1. Detect current platform (Mac/Windows/Linux)
2. Determine platform-specific paths and commands
3. Configure environment variables
4. Update context with platform information

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for platform detection.

Checks:
1. Python sys module available
2. Platform module available
3. Project root exists

#### `execute(self, context)`

Execute platform detection.

Steps:
1. Detect platform using sys.platform
2. Determine platform-specific settings
3. Configure paths and commands
4. Update context

---

## src.operations.modules.project_validation_module

Project Validation Setup Module

Validates CORTEX project structure and required files.

SOLID Principles:
- Single Responsibility: Only handles project structure validation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ProjectValidationModule

Setup module for project structure validation.

Responsibilities:
1. Validate CORTEX project root directory
2. Check for required directories (cortex-brain/, src/, tests/, prompts/)
3. Verify essential configuration files
4. Ensure minimum project structure exists

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for project validation.

Minimal requirements:
1. Current working directory exists
2. Can read filesystem

#### `execute(self, context)`

Execute project structure validation.

Steps:
1. Determine project root (from context or discover)
2. Validate required directories exist
3. Check for required files (warnings only)
4. Verify brain structure
5. Update context with project paths

---

## src.operations.modules.publish_documentation_module

Publish documentation module for documentation deployment.

Part of the Documentation Update operation - deploys generated docs to MkDocs site.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### PublishDocumentationModule

Publish documentation to MkDocs site.

Handles:
- Copying generated API docs to MkDocs docs/ directory
- Updating mkdocs.yml navigation
- Building MkDocs site (optional)
- Deployment to GitHub Pages (optional)

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute documentation publishing.

Args:
    context: Operation context with build output info
    
Returns:
    OperationResult with publish status

---

## src.operations.modules.refresh_design_docs_module

Refresh design documentation module.

Part of the Documentation Update operation - updates design documentation files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### RefreshDesignDocsModule

Refresh design documentation.

Scans design documentation directory for outdated files,
updates indexes, and ensures documentation structure is current.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute design documentation refresh.

Args:
    context: Operation context
    
Returns:
    OperationResult with refresh status

### `register()`

Register module for discovery.

---

## src.operations.modules.relocate_story_files_module

Relocate Story Files Module - Story Refresh Operation

This module relocates Ancient-Rules.md and CORTEX-FEATURES.md to the story directory
to keep all story-related documentation together.

Author: Asif Hussain
Version: 2.0 (Intelligent file relocation)

### RelocateStoryFilesModule

Relocate story-related files to docs/story/CORTEX-STORY/.

This module moves:
- Ancient-Rules.md (from cortex-brain/ or docs/)
- CORTEX-FEATURES.md (from cortex-brain/ or docs/)

What it does:
    1. Searches for files in common locations
    2. Creates backups before moving
    3. Relocates files to story directory
    4. Updates any references in other docs (optional)
    5. Verifies successful relocation

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `validate(self, context)`

Validate prerequisites.

#### `execute(self, context)`

Relocate story files.

#### `rollback(self, context)`

Rollback by moving files back to original locations.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if files need relocation

#### `get_progress_message(self)`

Get progress message.

### `register()`

Register this module.

---

## src.operations.modules.remove_old_logs_module

Remove Old Logs Module

Deletes log files older than specified retention period.

SOLID Principles:
- Single Responsibility: Only handles old log removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### RemoveOldLogsModule

Cleanup module for removing old log files.

Responsibilities:
1. Remove log files identified in scan
2. Track removal success/failure
3. Calculate space recovered
4. Report removal results

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for log removal.

Checks:
1. Scan results available

#### `execute(self, context)`

Execute old log removal.

Steps:
1. Get old log files from scan results
2. Remove each file
3. Track success/failure
4. Calculate space recovered

---

## src.operations.modules.remove_orphaned_files_module

Remove Orphaned Files Module

Identifies and removes files not tracked by Git.

SOLID Principles:
- Single Responsibility: Only handles orphaned file removal
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### RemoveOrphanedFilesModule

Cleanup module for removing orphaned files.

Responsibilities:
1. Identify files not tracked by Git
2. Remove safe orphaned files
3. Track removal success/failure
4. Report removal results

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for orphaned file removal.

Checks:
1. Git available
2. Project is a Git repository

#### `execute(self, context)`

Execute orphaned file removal.

Steps:
1. Get untracked files from Git
2. Filter out safe files (.gitignore, etc.)
3. Remove orphaned files
4. Track success/failure

---

## src.operations.modules.save_story_markdown_module

Save Story Markdown Module - Story Refresh Operation

This module saves the transformed CORTEX story to the documentation directory.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### SaveStoryMarkdownModule

Save transformed story to file.

This module writes the transformed CORTEX story to docs/awakening-of-cortex.md
with backup of existing file.

What it does:
    1. Backs up existing story file (if it exists)
    2. Writes transformed story to docs/awakening-of-cortex.md
    3. Verifies file was written correctly
    4. Stores backup path in context for rollback

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that transformed story and project root are available.

Args:
    context: Must contain 'transformed_story' and 'project_root'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Save story to file.

Args:
    context: Shared context dictionary
        - Input: transformed_story (str), project_root (Path)
        - Output: story_file_path (Path), backup_path (Path or None)

Returns:
    OperationResult with save status

#### `rollback(self, context)`

Rollback story save by restoring backup.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    False if dry_run is True

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.scan_docstrings_module

Scan Python docstrings module for documentation generation.

Part of the Documentation Update operation - extracts docstrings from Python source files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### DocstringInfo

Information about a docstring.

### ScanDocstringsModule

Scan Python source files and extract docstrings.

Extracts docstrings from:
- Modules (file-level docstrings)
- Classes
- Functions
- Methods

Builds a structured index of all documentation strings in the codebase.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute docstring scanning.

Args:
    context: Operation context
    
Returns:
    OperationResult with docstring index

### `register()`

Register module for discovery.

---

## src.operations.modules.scan_temporary_files_module

Scan Temporary Files Module

Identifies temporary files for cleanup in CORTEX workspace.

SOLID Principles:
- Single Responsibility: Only handles temporary file scanning
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ScanTemporaryFilesModule

Cleanup module for scanning temporary files.

Responsibilities:
1. Scan for temporary files (*.tmp, *.cache, etc.)
2. Identify build artifacts
3. Find Python cache directories
4. Locate old log files
5. Track file locations and sizes

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for scanning.

Checks:
1. Project root exists

#### `execute(self, context)`

Execute temporary file scanning.

Steps:
1. Scan for temporary files by extension
2. Find Python cache directories
3. Identify old log files
4. Calculate total size
5. Store scan results in context

---

## src.operations.modules.setup_completion_module

Setup Completion Module

Generates comprehensive setup summary report.

SOLID Principles:
- Single Responsibility: Only handles setup completion and reporting
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### SetupCompletionModule

Setup module for generating completion summary.

Responsibilities:
1. Collect results from all setup modules
2. Generate human-readable summary
3. Identify any warnings or issues
4. Provide next steps
5. Output comprehensive setup report

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for setup completion.

Minimal requirements - can always run.

#### `execute(self, context)`

Execute setup completion and generate summary.

Steps:
1. Collect module execution results from context
2. Categorize results (success, warning, failure)
3. Generate summary report
4. Provide next steps

---

## src.operations.modules.story_length_manager_module

Story Length Manager Module

Validates and manages story content length to ensure 15-20 minute read time target.
Provides intelligent recommendations for content that falls outside the target range.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### StoryLengthManagerModule

Validates story length against 15-20 minute read time target.

Target Specifications:
- Read Speed: 200 words per minute (industry standard)
- Target Range: 15-20 minutes = 3,000-4,000 words
- Acceptable Range: 2,800-4,200 words (±7% tolerance)

Validation Levels:
- PASS: Within acceptable range (2,800-4,200 words)
- WARNING: Outside acceptable but within extended range (2,400-4,600 words)
- ERROR: Far outside target range (< 2,400 or > 4,600 words)

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `get_module_id(self)`

#### `get_description(self)`

#### `get_required_inputs(self)`

#### `get_output_keys(self)`

#### `execute(self, inputs)`

Validate story length and provide recommendations.

Args:
    inputs: Dict with 'story_content' key containing story text
    
Returns:
    ModuleResult with validation status and recommendations

### `create_module()`

Factory function for module creation.

---

## src.operations.modules.system.__init__

System-level optimization modules for CORTEX.

This package contains meta-level orchestrators that coordinate
multiple optimization operations across different system aspects.

---

## src.operations.modules.system.optimize_system_orchestrator

CORTEX System Optimizer - Meta-Level Orchestrator

Comprehensive system optimization from all angles:
1. Design-Implementation Synchronization (design_sync)
2. Code Health & Obsolete Tests (optimize_cortex)
3. Brain Tier Tuning & Knowledge Graph Optimization
4. Entry Point Alignment (orchestrator consistency)
5. Test Suite Optimization (SKULL-007 compliance)
6. Comprehensive Health Report

This meta-orchestrator coordinates ALL optimization operations to ensure:
- Maximum inbuilt tooling leverage
- Design-implementation alignment
- Brain protection layer integrity
- Knowledge graph quality
- Test suite health (100% pass rate)
- Entry point consistency

Natural Language Triggers:
- "optimize cortex system"
- "optimize everything"
- "run comprehensive optimization"
- "system health check comprehensive"
- "align all components"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 1.0.0
Date: November 12, 2025

### OptimizationMetrics

Comprehensive optimization metrics from all phases.

### SystemHealthReport

Comprehensive system health report.

**Methods:**

#### `to_dict(self)`

Convert to dictionary for JSON serialization.

### OptimizeSystemOrchestrator

Meta-level orchestrator for comprehensive CORTEX system optimization.

Coordinates 6 optimization phases:

Phase 1: Design Sync
    - Run design_sync_orchestrator
    - Resolve design-implementation drift
    - Consolidate status files
    - Update module counts

Phase 2: Code Health
    - Run optimize_cortex_orchestrator
    - Identify obsolete tests
    - Detect dead code
    - Analyze test coverage gaps

Phase 3: Brain Tuning
    - Validate tier boundaries (Tier 0, 1, 2, 3)
    - Prune low-confidence patterns (<0.50)
    - Detect and merge duplicate patterns
    - Validate brain protection rules (YAML)

Phase 4: Entry Point Alignment
    - Validate all orchestrator headers use HeaderFormatter
    - Sync command registry with natural language triggers
    - Update CORTEX.prompt.md with discovered commands
    - Ensure consistent copyright attribution

Phase 5: Test Suite Optimization
    - Execute obsolete test removal (from Phase 2)
    - Fix failing tests using recommendations
    - Validate 100% pass rate (SKULL-007 compliance)
    - Generate test coverage report

Phase 6: Comprehensive Report
    - Consolidate metrics from all phases
    - Calculate overall health score
    - Generate recommendations
    - Save to cortex-brain/system-optimization-report.md

Usage:
    orchestrator = OptimizeSystemOrchestrator(project_root=Path('/path/to/cortex'))
    result = orchestrator.execute(context={'profile': 'comprehensive', 'mode': 'live'})

**Methods:**

#### `get_metadata(self)`

Return metadata for this operation module.

#### `validate_prerequisites(self, context)`

Validate prerequisites for system optimization.

Checks:
- CORTEX project root exists
- Required orchestrators available
- Git repository initialized
- Python environment configured

Args:
    context: Execution context

Returns:
    OperationResult with validation status

#### `execute(self, context)`

Execute comprehensive system optimization.

Args:
    context: Execution context with keys:
        - profile: Optimization profile ('comprehensive', 'focused', 'minimal')
        - mode: Execution mode (always 'live')
        - skip_phases: Optional list of phases to skip

Returns:
    OperationResult with optimization status and metrics

### `register()`

Register this module with the operations system.

Returns:
    Instance of OptimizeSystemOrchestrator

---

## src.operations.modules.tooling_detection_module

Tooling Detection Module

Detects installed tooling on target machine (Python, Git, Node.js, pip, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ToolingDetector

Detect installed development tooling.

**Methods:**

#### `detect_all(self)`

Detect all required tooling.

#### `detect_python(self)`

Detect Python installation.

#### `detect_pip(self)`

Detect pip installation.

#### `detect_git(self)`

Detect Git installation.

#### `detect_node(self)`

Detect Node.js installation.

#### `detect_npm(self)`

Detect npm installation.

#### `detect_sqlite(self)`

Detect SQLite installation.

#### `detect_package_manager(self)`

Detect system package manager for automated installation.

#### `get_missing_required(self)`

Get list of missing required tools.

#### `print_report(self)`

Print detection report.

### `execute(context)`

Execute tooling detection.

---

## src.operations.modules.tooling_installer_module

Tooling Installer Module

Automatically installs missing development tooling (Python, Git, Node.js, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ToolingInstaller

Automated tooling installation.

**Methods:**

#### `install_python(self)`

Install Python.

#### `install_git(self)`

Install Git.

#### `install_node(self)`

Install Node.js (for Vision API).

#### `install_sqlite(self)`

Install SQLite.

#### `install_pip_packages(self, requirements_file)`

Install Python packages from requirements.txt.

#### `install_missing_tools(self, missing)`

Install all missing tools.

#### `print_install_report(self, results)`

Print installation report.

### VisionAPIInstaller

Install Vision API dependencies.

**Methods:**

#### `install(self, cortex_root)`

Install Vision API dependencies.

#### `configure_credentials(self, api_key)`

Configure Vision API credentials.

### `execute(context)`

Execute tooling installation.

---

## src.operations.modules.tooling_verification_module

Tooling Verification Setup Module

Verifies development tools are installed and configured.

SOLID Principles:
- Single Responsibility: Only handles tooling verification
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ToolingVerificationModule

Setup module for development tooling verification.

Responsibilities:
1. Verify git installation and version
2. Verify Python installation and version
3. Verify pytest installation (optional)
4. Verify other common dev tools
5. Report tool status summary

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for tooling verification.

Minimal requirements - can always run.

#### `execute(self, context)`

Execute tooling verification.

Steps:
1. Check required tools (git, python)
2. Check optional tools (pytest, pip)
3. Verify versions where applicable
4. Generate tool status report

---

## src.operations.modules.update_mkdocs_index_module

Update MkDocs Index Module - Story Refresh Operation

This module updates the MkDocs navigation to include the refreshed story.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### UpdateMkDocsIndexModule

Update MkDocs navigation with story.

This module ensures the CORTEX story is properly linked in the
MkDocs navigation structure.

What it does:
    1. Reads mkdocs.yml configuration
    2. Checks if story is in navigation
    3. Updates navigation if needed
    4. Writes back to mkdocs.yml

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that story was saved and project root is available.

Args:
    context: Must contain 'story_file_path' and 'project_root'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Update MkDocs navigation.

Args:
    context: Shared context dictionary
        - Input: story_file_path (Path), project_root (Path)
        - Output: mkdocs_updated (bool), navigation_entry (str)

Returns:
    OperationResult with update status

#### `rollback(self, context)`

Rollback MkDocs navigation update.

Note: This is a simplified rollback that doesn't restore the exact
previous state. For production, consider backing up mkdocs.yml.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if not in quick profile and not dry_run

#### `get_progress_message(self)`

Get progress message.

### `register()`

Register the module.

---

## src.operations.modules.vacuum_sqlite_databases_module

Vacuum SQLite Databases Module

Optimizes SQLite databases to recover space and improve performance.

SOLID Principles:
- Single Responsibility: Only handles SQLite optimization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### VacuumSQLiteDatabasesModule

Cleanup module for optimizing SQLite databases.

Responsibilities:
1. Vacuum CORTEX brain databases
2. Calculate space recovered
3. Report optimization results

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for database optimization.

Checks:
1. Project root available
2. Brain directory exists

#### `execute(self, context)`

Execute SQLite database optimization.

Steps:
1. Find all SQLite databases in cortex-brain
2. Get size before vacuum
3. Run VACUUM on each database
4. Calculate space recovered

---

## src.operations.modules.validate_doc_links_module

Validate documentation links module.

Part of the Documentation Update operation - checks for broken links in documentation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### ValidateDocLinksModule

Validate documentation links.

Scans Markdown documentation files for links and validates:
- Internal links (references to other docs files)
- Anchor links (references to headings)
- Optionally external links (HTTP/HTTPS URLs)

Reports broken or invalid links.

**Methods:**

#### `get_metadata(self)`

Get module metadata.

#### `execute(self, context)`

Execute link validation.

Args:
    context: Operation context
    
Returns:
    OperationResult with validation status

### `register()`

Register module for discovery.

---

## src.operations.modules.validate_story_structure_module

Validate Story Structure Module - Story Refresh Operation

This module validates the CORTEX story Markdown structure to ensure
it meets documentation standards.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### ValidateStoryStructureModule

Validate story Markdown structure.

This module ensures the CORTEX story has proper Markdown formatting
and meets documentation standards.

What it does:
    1. Validates Markdown syntax
    2. Checks for required sections
    3. Verifies heading hierarchy
    4. Checks for common issues

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate that transformed story is available.

Args:
    context: Must contain 'transformed_story'

Returns:
    (is_valid, issues_list)

#### `execute(self, context)`

Validate story structure.

Args:
    context: Shared context dictionary
        - Input: transformed_story (str)
        - Output: validation_results (dict), is_valid (bool)

Returns:
    OperationResult with validation status

#### `rollback(self, context)`

Rollback validation (no-op).

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds)

#### `should_run(self, context)`

Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if not in quick profile

#### `get_progress_message(self)`

Get progress message.

---

## src.operations.modules.virtual_environment_module

Virtual Environment Setup Module

Creates or activates Python virtual environment for CORTEX.

SOLID Principles:
- Single Responsibility: Only handles virtual environment management
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### VirtualEnvironmentModule

Setup module for Python virtual environment management.

Responsibilities:
1. Check if already running in venv
2. Detect existing venv in project
3. Create new venv if needed
4. Provide activation instructions
5. Validate venv is usable

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for virtual environment setup.

Checks:
1. Project root exists
2. Python command available
3. Platform information available

#### `execute(self, context)`

Execute virtual environment setup.

Steps:
1. Check if running in venv already
2. Look for existing venv
3. Create venv if needed
4. Validate venv
5. Provide activation instructions

---

## src.operations.modules.vision_api_module

Vision API Setup Module

Activates GitHub Copilot Vision API for screenshot analysis in CORTEX.

SOLID Principles:
- Single Responsibility: Only handles Vision API activation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### VisionAPIModule

Setup module for activating Vision API.

Responsibilities:
1. Verify cortex.config.json exists
2. Enable vision_api.enabled flag
3. Configure default settings if not present
4. Verify Pillow/PIL is installed (optional, for preprocessing)
5. Update context for downstream modules

Configuration (from YAML):
    config_file: Path to cortex.config.json
    config_path: JSON path to enable (e.g., "vision_api.enabled")
    max_tokens_per_image: Token budget per image
    cache_results: Whether to cache analysis results
    requires_copilot: Whether GitHub Copilot is required

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for Vision API activation.

Checks:
1. Project root exists in context
2. cortex.config.json exists
3. Config file is valid JSON

#### `execute(self, context)`

Execute Vision API activation.

Steps:
1. Load cortex.config.json
2. Enable vision_api.enabled = true
3. Set default configuration if missing
4. Save updated config
5. Update context

#### `rollback(self, context)`

Rollback Vision API activation.

Disables vision_api.enabled in config.

#### `should_run(self, context)`

Determine if Vision API setup should run.

Runs if:
- User explicitly requested full setup
- User included 'vision' in setup request

---

## src.operations.modulesthon_dependencies_module

Python Dependencies Setup Module

Installs required Python packages from requirements.txt.

SOLID Principles:
- Single Responsibility: Only handles Python package installation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PythonDependenciesModule

Setup module for installing Python dependencies.

Responsibilities:
1. Verify requirements.txt exists
2. Upgrade pip to latest version
3. Install packages from requirements.txt
4. Verify installations
5. Update context with installed packages

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for dependency installation.

Checks:
1. Project root exists
2. requirements.txt exists
3. Python command available

#### `execute(self, context)`

Execute Python dependency installation.

Steps:
1. Upgrade pip
2. Install from requirements.txt
3. Verify installations
4. Update context

---

## src.operations.operation_factory

Operation Factory - Load and Create Operations from YAML

This factory loads operation definitions from cortex-op                    # Convert snake_case to CamelCase, but preserve common acronyms
                    words = module_name.split('_')
                    # Preserve common acronyms in uppercase
                    acronyms = {'api': 'API', 'sql': 'SQL', 'sqlite': 'SQLite', 'html': 'HTML', 'css': 'CSS', 'json': 'JSON', 'yaml': 'YAML', 'mkdocs': 'MkDocs', 'pdf': 'PDF', 'cli': 'CLI'}
                    class_name = ''.join(
                        acronyms.get(word.lower(), word.capitalize()) 
                        for word in words
                    ).yaml and
instantiates orchestrators with the appropriate modules.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)

### OperationFactory

Factory for creating operation orchestrators from YAML configuration.

Loads cortex-operations.yaml and provides methods to:
    - Discover available operations
    - Load operation definitions
    - Instantiate module classes
    - Create orchestrators ready for execution

Example Usage:
    factory = OperationFactory()
    
    # Get available operations
    ops = factory.get_available_operations()
    # ['environment_setup', 'refresh_cortex_story', 'workspace_cleanup', ...]
    
    # Create orchestrator for an operation
    orchestrator = factory.create_operation('refresh_cortex_story')
    report = orchestrator.execute_operation(context={'project_root': Path('...')})

**Methods:**

#### `get_available_operations(self)`

Get list of available operation IDs.

Returns:
    List of operation IDs (e.g., ['environment_setup', 'refresh_cortex_story'])

#### `get_operation_info(self, operation_id)`

Get information about an operation.

Args:
    operation_id: Operation identifier

Returns:
    Operation configuration dict, or None if not found

#### `create_operation(self, operation_id, profile, context)`

Create orchestrator for an operation.

Args:
    operation_id: Operation identifier (e.g., 'refresh_cortex_story')
    profile: Profile to use (minimal/standard/full)
    context: Initial context dictionary

Returns:
    Configured orchestrator, or None if operation not found

Example:
    orchestrator = factory.create_operation('refresh_cortex_story')
    if orchestrator:
        report = orchestrator.execute_operation(context={'project_root': Path('.')})

#### `list_operation_modules(self, operation_id, profile)`

List modules for an operation without creating orchestrator.

Args:
    operation_id: Operation identifier
    profile: Profile name

Returns:
    List of module IDs

#### `get_natural_language_mappings(self)`

Get natural language → operation ID mappings.

Returns:
    Dict mapping natural language phrases to operation IDs

Example:
    {'refresh story': 'refresh_cortex_story',
     'cleanup': 'workspace_cleanup'}

#### `find_operation_by_input(self, user_input)`

Find operation ID by user input (natural language or slash command).

Args:
    user_input: User's input text

Returns:
    Operation ID if found, None otherwise

Example:
    factory.find_operation_by_input("refresh story") → 'refresh_cortex_story'
    factory.find_operation_by_input("/CORTEX, cleanup") → 'workspace_cleanup'

---

## src.operations.operation_header_formatter

CORTEX Operation Header Formatter

Provides standardized headers and footers for all CORTEX operation orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Consolidates functionality from header_formatter.py and header_utils.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### OperationHeaderFormatter

Format headers and footers for CORTEX operation orchestrators.

**Methods:**

#### `format_minimalist(operation_name, version, profile, mode, timestamp, purpose)`

Format minimalist header for operations.

Used for: cleanup, optimization, design sync, story refresh, etc.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)
    purpose: Optional 1-2 line description of operation purpose

Returns:
    Formatted header string

#### `format_banner(operation_name, version, profile, mode, timestamp)`

Format banner-style header with ASCII art logo.

Used for: help module and other high-visibility entry points.

Args:
    operation_name: Name of the operation (e.g., "Help System")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "standard")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)

Returns:
    Formatted banner header string

#### `format_completion(operation_name, success, duration_seconds, summary, accomplishments)`

Format completion footer.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Total execution time in seconds
    summary: Optional single-line summary message
    accomplishments: Optional list of bullet points showing what was done

Returns:
    Formatted completion footer

#### `print_minimalist(operation_name, version, profile, mode, timestamp, purpose)`

Print minimalist header directly to console.

#### `print_banner(operation_name, version, profile, mode, timestamp)`

Print banner header directly to console.

#### `print_completion(operation_name, success, duration_seconds, summary, accomplishments)`

Print completion footer directly to console.

---

## src.operations.operations_orchestrator

Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Parallel execution of independent modules
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 2.1 (Parallel Execution Optimization)

### OperationExecutionReport

Report of operation execution.

Universal report for ANY operation (setup, cleanup, story refresh, etc.)

Attributes:
    operation_id: Operation identifier (e.g., 'environment_setup')
    operation_name: Human-readable name
    success: Overall operation success
    modules_executed: List of module IDs that ran
    modules_succeeded: List of module IDs that succeeded
    modules_failed: List of module IDs that failed
    modules_skipped: List of module IDs that were skipped
    module_results: Detailed results for each module
    total_duration_seconds: Total execution time
    timestamp: When operation completed
    context: Final shared context dictionary
    errors: List of error messages
    parallel_execution_count: Number of modules executed in parallel
    parallel_groups_count: Number of parallel execution groups
    time_saved_seconds: Estimated time saved by parallel execution

**Methods:**

### OperationsOrchestrator

Universal orchestrator for ALL CORTEX operations.

Coordinates module execution for any operation defined in cortex-operations.yaml:
    - environment_setup (setup command)
    - refresh_cortex_story (story refresh command)
    - workspace_cleanup (cleanup command)
    - update_documentation (docs command)
    - And any future operations

Key Features:
    - Dependency resolution via topological sort
    - Phase-based execution (PRE_VALIDATION → FINALIZATION)
    - Priority ordering within phases
    - Error handling with rollback
    - Comprehensive reporting
    - Copyright header rendering

Example Usage:
    # Setup operation
    orchestrator = OperationsOrchestrator(
        operation_id="environment_setup",
        modules=[platform_mod, vision_mod, brain_mod]
    )
    report = orchestrator.execute_operation(
        context={'project_root': Path('...')}
    )
    
    # Cleanup operation
    orchestrator = OperationsOrchestrator(
        operation_id="workspace_cleanup",
        modules=[scan_mod, cleanup_mod]
    )
    report = orchestrator.execute_operation(
        context={'project_root': Path('...')}
    )

**Methods:**

#### `execute_operation(self, context)`

Execute the operation by running all modules in dependency-resolved order.

Args:
    context: Additional context to merge with initialization context

Returns:
    OperationExecutionReport with execution details

#### `get_module_execution_order(self)`

Get the execution order of modules without running them.

Returns:
    List of module IDs in execution order

---

## src.operations.response_formatter

CORTEX Response Formatter

Automatically formats operation results with appropriate copyright headers
based on execution context. This ensures consistent branding and legal
attribution without requiring user intervention.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ResponseFormatter

Intelligent response formatter that adapts headers based on context.

Header Strategy:
- First operation in session: Full header
- Help/documentation: Banner header (ASCII art)
- Regular operations: Minimal footer
- Error situations: No header (focus on problem)

**Methods:**

#### `format_operation_result(operation_name, result, context, is_help)`

Format operation result with appropriate header.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    result: OperationResult object
    context: Execution context
    is_help: Whether this is a help command
    
Returns:
    Formatted markdown string for Copilot Chat display

#### `reset_session()`

Reset session state (for testing or explicit session start).

### `format_for_copilot(operation_name, result, context)`

Convenience function to format operation results for Copilot Chat display.

Args:
    operation_name: Name of the operation
    result: OperationResult object
    context: Optional execution context
    
Returns:
    Formatted markdown string

---

## src.operations.setup

Environment Setup Operation - CORTEX 3.0 Phase 1.1
Monolithic MVP Implementation (~350 lines)

Detects platform, validates dependencies, creates virtual environment,
installs packages, initializes CORTEX brain databases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### Platform

Supported platforms.

### SetupResult

Result of setup operation.

**Methods:**

#### `add_error(self, message)`

Add error message.

#### `add_warning(self, message)`

Add warning message.

#### `to_dict(self)`

Convert to dictionary.

### `detect_platform()`

Detect current operating system platform.

Returns:
    Platform enum value

### `validate_python()`

Validate Python installation and version.

Returns:
    (is_valid, version_string)

### `validate_git()`

Validate Git installation.

Returns:
    (is_installed, version_string)

### `validate_vscode()`

Check if VS Code is installed.

Returns:
    True if VS Code found

### `create_virtual_environment(project_root)`

Create Python virtual environment if it doesn't exist.

Args:
    project_root: CORTEX project root directory

Returns:
    (success, message)

### `install_dependencies(project_root)`

Install Python dependencies from requirements.txt.

Args:
    project_root: CORTEX project root directory

Returns:
    (success, packages_installed, message)

### `initialize_brain_databases(project_root)`

Initialize CORTEX brain SQLite databases.

Creates:
    - cortex-brain/tier1/conversations.db
    - cortex-brain/tier2/knowledge-graph.db
    - cortex-brain/tier3/context-intelligence.db

Args:
    project_root: CORTEX project root directory

Returns:
    (success, message)

### `setup_environment(profile, project_root)`

Main setup operation - configures CORTEX development environment.

Steps:
    1. Detect platform (Windows/Mac/Linux)
    2. Validate dependencies (Python 3.9+, Git, VS Code)
    3. Create virtual environment
    4. Install Python packages from requirements.txt
    5. Initialize brain databases (Tier 1-3)
    6. Validate setup completion

Args:
    profile: Setup profile ('minimal', 'standard', 'full')
    project_root: Project root path (auto-detected if None)

Returns:
    Result dictionary with success status and details

---

## src.operations.update_documentation

CORTEX Documentation Generator - Monolithic Script

Single-script implementation for documentation update operation.
Auto-generates docs from code/YAML, validates links, updates MkDocs structure.

Design Philosophy (CORTEX 3.0):
- Monolithic-then-modular: Ship working MVP first
- User value over perfect architecture
- Refactor only when complexity warrants (>500 lines)

Features:
- API reference extraction from docstrings
- Operation documentation auto-generation
- Link validation system
- MkDocs navigation updates
- YAML-based configuration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1 Week 2)

### DocGenerationResult

Result of documentation generation operation.

**Methods:**

#### `to_dict(self)`

Convert to dictionary.

### DocumentationGenerator

CORTEX Documentation Generator.

Generates and updates documentation from source code and YAML files.

**Methods:**

#### `load_config(self)`

Load documentation generation configuration.

#### `discover_files(self)`

Discover all relevant files for documentation generation.

#### `extract_python_docstrings(self, file_path)`

Extract docstrings from Python file.

Args:
    file_path: Path to Python file
    
Returns:
    Dictionary with module, classes, functions, and their docstrings

#### `generate_api_reference(self, docstrings)`

Generate API reference markdown from docstrings.

Args:
    docstrings: List of docstring dictionaries
    
Returns:
    Markdown content

#### `generate_operations_docs(self)`

Generate documentation for all operations.

Returns:
    List of (filename, content) tuples

#### `validate_links(self, markdown_files)`

Validate links in markdown files.

Args:
    markdown_files: List of markdown files to validate
    
Returns:
    Tuple of (total_links, broken_links)

#### `update_mkdocs_nav(self, generated_docs)`

Update MkDocs navigation with generated documentation.

Args:
    generated_docs: List of generated documentation files
    
Returns:
    Success status

#### `execute(self)`

Execute documentation generation.

Returns:
    DocGenerationResult with execution details

### `main()`

Main entry point for documentation generator.

---

## src.plugins.base_plugin

Base Plugin System for CORTEX 2.0

Provides abstract base class and infrastructure for all CORTEX plugins.
Plugins extend CORTEX functionality without modifying core code.

Architecture:
- BasePlugin: Abstract class all plugins must inherit from
- PluginMetadata: Standardized plugin information
- Hook System: Lifecycle hooks for plugin execution
- Configuration: JSON schema validation for plugin settings

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PluginCategory

Plugin categories for organization

### PluginPriority

Plugin execution priority

### HookPoint

Lifecycle hooks for plugin execution

### PluginMetadata

Standardized metadata for all plugins

**Methods:**

### BasePlugin

Abstract base class for all CORTEX plugins.

All plugins must:
1. Inherit from BasePlugin
2. Implement _get_metadata() method
3. Implement initialize() method
4. Implement execute() method
5. Implement cleanup() method

Example:
```python
class MyPlugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="my_plugin",
            name="My Plugin",
            version="1.0.0",
            category=PluginCategory.WORKFLOW,
            priority=PluginPriority.MEDIUM,
            description="Does something useful",
            author="Your Name",
            dependencies=[],
            hooks=[HookPoint.ON_WORKFLOW_START.value],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        # Setup plugin resources
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Main plugin logic
        return {"success": True}
    
    def cleanup(self) -> bool:
        # Cleanup plugin resources
        return True
```

**Methods:**

#### `initialize(self)`

Initialize plugin resources.

Called once when plugin is loaded. Use this to:
- Verify dependencies
- Setup connections
- Load configuration
- Validate environment

Returns:
    True if initialization successful, False otherwise

#### `execute(self, context)`

Execute plugin main logic.

Args:
    context: Execution context with parameters
        - hook: Hook that triggered execution
        - Additional context-specific parameters

Returns:
    Dictionary with execution results:
        - success: bool (required)
        - Additional result data

#### `cleanup(self)`

Cleanup plugin resources.

Called when plugin is unloaded. Use this to:
- Close connections
- Release resources
- Save state

Returns:
    True if cleanup successful, False otherwise

#### `register_commands(self)`

Register plugin slash commands (optional).

Override this method to register commands for your plugin.
Commands provide shortcuts to plugin functionality.

Returns:
    List of CommandMetadata objects to register

Example:
    def register_commands(self) -> List[Any]:
        from .command_registry import CommandMetadata, CommandCategory
        
        return [
            CommandMetadata(
                command="/mac",
                natural_language_equivalent="switched to mac",
                plugin_id=self.metadata.plugin_id,
                description="Switch to macOS environment",
                category=CommandCategory.PLATFORM,
                aliases=["/macos"],
                examples=["@cortex /mac", "switched to mac"]
            )
        ]

#### `validate_config(self)`

Validate plugin configuration against schema.

Returns:
    True if configuration is valid, False otherwise

#### `get_info(self)`

Get plugin information.

Returns:
    Dictionary with plugin metadata

#### `enable(self)`

Enable plugin

#### `disable(self)`

Disable plugin

#### `is_enabled(self)`

Check if plugin is enabled

### PluginManager

Manages plugin lifecycle and execution.

Responsibilities:
- Plugin discovery and loading
- Hook registration and execution
- Plugin dependency resolution
- Configuration management

**Methods:**

#### `register_plugin(self, plugin)`

Register a plugin.

Args:
    plugin: Plugin instance to register

Returns:
    True if registration successful, False otherwise

#### `execute_hook(self, hook, context)`

Execute all plugins registered for a hook.

Args:
    hook: Hook to execute
    context: Context for plugin execution

Returns:
    List of results from all plugins

#### `get_plugin(self, plugin_id)`

Get plugin by ID

#### `list_plugins(self)`

List all registered plugins

#### `cleanup_all(self)`

Cleanup all plugins

---

## src.plugins.cleanup_orchestrator

Dynamic Cleanup Orchestrator for CORTEX 2.0

Performs fresh workspace scans on every execution using configurable YAML rules.
NO static lists - everything is discovered dynamically at runtime.

Features:
- YAML-based cleanup rules (cortex-brain/cleanup-rules.yaml)
- Fresh scanning on every execution
- Multiple action types (delete, archive, retain_recent, retain_days)
- Recursion protection for nested directories
- Safety validations (protected dirs, Git status, confirmations)
- Dry-run and live modes
- Rollback capability with manifests
- Comprehensive reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Date: November 11, 2025

### CleanupMode

Cleanup execution mode - always live

### CleanupAction

Types of cleanup actions

### RiskLevel

Risk levels for cleanup operations

### CleanupItem

Represents a file or directory to be cleaned

### CleanupStats

Statistics from cleanup execution

**Methods:**

#### `space_freed_mb(self)`

#### `space_freed_gb(self)`

### DynamicCleanupOrchestrator

Dynamic cleanup orchestrator that performs fresh scans on every execution.

Usage:
    orchestrator = DynamicCleanupOrchestrator(workspace_root)
    results = orchestrator.execute()

**Methods:**

#### `scan_category(self, category_name, category_config)`

Perform fresh scan for a specific cleanup category.

Args:
    category_name: Name of the category
    category_config: Category configuration from rules

Returns:
    List of CleanupItem objects found

#### `apply_retention_policy(self, items, category_config)`

Apply retention policy to filter items.

Args:
    items: List of CleanupItem objects
    category_config: Category configuration with retention rules

Returns:
    Filtered list of items to delete/archive

#### `execute(self, mode)`

Execute cleanup with fresh workspace scan.

Args:
    mode: Execution mode (LIVE only)

Returns:
    Dictionary with execution results and statistics

### `print_cleanup_report(report)`

Print formatted cleanup report to console

---

## src.plugins.cleanup_plugin

Cleanup Plugin for CORTEX 2.0

Comprehensive project cleanup and maintenance plugin with advanced features:
- Smart temp file removal with age-based filtering
- Duplicate file detection and removal
- Empty directory cleanup
- Log rotation and archival
- Large file detection and reporting
- Backup file cleanup (.bak, .old, etc.)
- Cache directory management
- Git-aware cleanup (respects .gitignore)
- Safe mode with dry-run capability
- Detailed reporting and statistics
- Rollback capability via backup
- File organization and structure enforcement
- Orphaned file detection (files not referenced anywhere)
- Compression of old archives
- Whitelist/blacklist pattern support

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### CleanupAction

Types of cleanup actions

### FileCategory

File categorization for cleanup

### CleanupStats

Statistics from cleanup operation

**Methods:**

#### `space_freed_mb(self)`

Space freed in megabytes

#### `space_freed_gb(self)`

Space freed in gigabytes

#### `to_dict(self)`

Convert to dictionary

### CleanupReport

Detailed cleanup report

**Methods:**

#### `to_dict(self)`

Convert to dictionary

#### `save(self, output_path)`

Save report to file

### Plugin

Comprehensive Cleanup Plugin for CORTEX

**Methods:**

#### `initialize(self, config)`

Initialize the plugin

#### `execute(self, context)`

Execute cleanup operations

#### `cleanup(self)`

Cleanup plugin resources

---

## src.plugins.code_review_plugin

Code Review Plugin for CORTEX 2.0

Automated pull request review with comprehensive code analysis:
- SOLID principle violation detection
- Security vulnerability scanning (secrets, SQL injection, XSS)
- Performance anti-pattern detection (N+1 queries, memory leaks)
- Test coverage regression detection
- Code style consistency checking
- Duplicate code detection
- Dependency vulnerability analysis
- Pattern violation checking (against Tier 2 knowledge)

Integration:
- Azure DevOps REST API
- GitHub REST API and GraphQL
- GitLab CI webhooks
- BitBucket Pipelines

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### ViolationSeverity

Severity levels for code violations

### ViolationType

Types of code violations

### CodeViolation

Represents a code review violation

**Methods:**

#### `to_dict(self)`

Convert to dictionary

### ReviewResult

Results from code review

**Methods:**

#### `critical_count(self)`

#### `high_count(self)`

#### `medium_count(self)`

#### `low_count(self)`

#### `to_dict(self)`

Convert to dictionary

### SOLIDAnalyzer

Analyzes code for SOLID principle violations

**Methods:**

#### `analyze(self, file_path, content, language)`

Analyze file for SOLID violations

Args:
    file_path: Path to the file
    content: File content
    language: Programming language (python, csharp, javascript, etc.)

Returns:
    List of violations found

### SecurityScanner

Scans code for security vulnerabilities

**Methods:**

#### `scan(self, file_path, content, language)`

Scan file for security vulnerabilities

Args:
    file_path: Path to the file
    content: File content
    language: Programming language

Returns:
    List of security violations found

### PerformanceAnalyzer

Analyzes code for performance anti-patterns

**Methods:**

#### `analyze(self, file_path, content, language)`

Analyze file for performance issues

Args:
    file_path: Path to the file
    content: File content
    language: Programming language

Returns:
    List of performance violations found

### CodeReviewPlugin

Automated code review plugin for pull requests

Features:
- SOLID principle violation detection
- Security vulnerability scanning
- Performance anti-pattern detection
- Test coverage regression checking
- Code style consistency validation
- Duplicate code detection
- Integration with Azure DevOps, GitHub, GitLab, BitBucket

**Methods:**

#### `initialize(self)`

Initialize plugin

#### `execute(self, context)`

Execute code review

Context parameters:
    - pr_id: Pull request ID
    - files: List of changed files
    - repository_path: Path to repository
    - platform: Integration platform (azure_devops, github, gitlab)

Returns:
    Review results

#### `cleanup(self)`

Cleanup plugin resources

---

## src.plugins.command_registry

CORTEX Plugin Command Registry

Extensible system for plugins to register slash commands and natural language aliases.
Enables /command shortcuts while maintaining natural language as primary interface.

Design Principles:
- Plugin-driven: Each plugin declares its own commands
- No conflicts: Automatic detection and resolution
- Discoverable: Auto-generated help and command listing
- Scalable: O(1) lookup performance even with 100+ commands

Architecture:
    Plugin → CommandMetadata → Registry → Router

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### CommandCategory

Command categories for organization and help display

### CommandMetadata

Metadata for a plugin command.

Example:
    CommandMetadata(
        command="/mac",
        natural_language_equivalent="switched to mac",
        plugin_id="platform_switch",
        description="Switch to macOS development environment",
        category=CommandCategory.PLATFORM,
        aliases=["/macos", "/darwin"],
        examples=["@cortex /mac", "switched to mac"],
        requires_online=False
    )

### PluginCommandRegistry

Central registry for all plugin commands.

Features:
- Automatic conflict detection
- O(1) command lookup
- Auto-generated help text
- Plugin discovery

Usage:
    registry = PluginCommandRegistry()
    
    # Plugin registers commands during initialization
    registry.register_command(CommandMetadata(
        command="/mac",
        natural_language_equivalent="switched to mac",
        plugin_id="platform_switch",
        ...
    ))
    
    # Router expands commands
    expanded = registry.expand_command("/mac")
    # → "switched to mac"

**Methods:**

#### `register_command(self, metadata)`

Register a plugin command.

Args:
    metadata: Command metadata from plugin

Returns:
    True if registered successfully, False if conflict detected

Raises:
    ValueError: If command format is invalid

#### `expand_command(self, user_input)`

Expand slash command to natural language.

Args:
    user_input: Raw user input (might be command or natural language)

Returns:
    Natural language equivalent, or None if not a command

Example:
    expand_command("/mac") → "switched to mac"
    expand_command("switched to mac") → None (already natural language)

#### `get_command_metadata(self, command)`

Get metadata for a command.

Args:
    command: Command string (e.g., "/mac")

Returns:
    CommandMetadata if found, None otherwise

#### `get_plugin_commands(self, plugin_id)`

Get all commands registered by a plugin.

Args:
    plugin_id: Plugin identifier

Returns:
    List of CommandMetadata objects

#### `get_all_commands(self)`

Get all registered commands.

Returns:
    List of all CommandMetadata objects (deduplicated)

#### `get_commands_by_category(self, category)`

Get commands in a category.

Args:
    category: CommandCategory enum value

Returns:
    List of CommandMetadata objects in that category

#### `generate_help_text(self, category)`

Generate formatted help text for commands.

Args:
    category: Optional category to filter by

Returns:
    Markdown-formatted help text

#### `is_command(self, user_input)`

Check if user input is a registered command.

Args:
    user_input: Raw user input

Returns:
    True if it's a registered command

#### `get_stats(self)`

Get registry statistics.

Returns:
    Dictionary with registry stats

### `get_command_registry()`

Get global command registry instance (singleton).

Returns:
    PluginCommandRegistry singleton

---

## src.plugins.configuration_wizard_plugin

Configuration Wizard Plugin

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

Provides post-setup incremental configuration with auto-discovery.

Features:
- Auto-discover Oracle/SQL Server/PostgreSQL connections
- Scan code for REST API endpoints
- Validate connections before saving
- Interactive guided configuration
- Non-blocking - runs AFTER basic setup

Usage:
    # Interactive wizard (all features)
    cortex config:wizard
    
    # Add single database
    cortex config:add-database --interactive
    
    # Add single API
    cortex config:add-api --interactive
    
    # Auto-discover only (no prompts)
    cortex config:discover --auto

### DatabaseConnection

Database connection configuration.

### APIEndpoint

REST API endpoint configuration.

### Plugin

Configuration Wizard Plugin

Provides incremental, post-setup configuration with intelligent
auto-discovery. Does NOT block initial setup.

Architecture:
- Phase 1: Auto-discovery (scan environment, files, code)
- Phase 2: User confirmation (review discovered items)
- Phase 3: Manual entry (fill gaps)
- Phase 4: Validation (test connections)
- Phase 5: Save to cortex.config.json

**Methods:**

#### `initialize(self)`

Initialize configuration wizard.

#### `execute(self, context)`

Run configuration wizard.

Args:
    context:
        mode: 'wizard' | 'add-database' | 'add-api' | 'discover'
        repo_path: Path to repository
        config_path: Path to cortex.config.json
        interactive: bool (prompt user or auto-only)
        
Returns:
    Result dictionary with discovered/configured items

---

## src.plugins.conversation_import_plugin

CORTEX 2.0 - Conversation Import Plugin

Purpose: Import manually copy-pasted Copilot conversations to enrich CORTEX learning.
Complements ambient daemon with strategic context and decision rationale.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### ConversationTurn

Represents one turn in a Copilot conversation.

### ParsedConversation

Parsed conversation with metadata.

### ConversationImportPlugin

Plugin for importing Copilot conversations to CORTEX brain.

Provides dual-channel learning:
- Channel 1: Ambient daemon (execution-focused)
- Channel 2: Manual conversations (strategy-focused)

**Methods:**

#### `register_commands(self)`

Register slash commands and natural language equivalents.

#### `initialize(self)`

Initialize conversation import plugin.

#### `execute(self, request, context)`

Execute conversation import operations.

Args:
    request: User request string
    context: Execution context
    
Returns:
    Result dictionary with status and data

#### `parse_conversation_file(self, file_path)`

Parse Copilot conversation markdown file.

Args:
    file_path: Path to conversation file
    
Returns:
    ParsedConversation or None if parsing fails

#### `store_to_tier1(self, parsed)`

Store parsed conversation to Tier 1 working memory.

Args:
    parsed: ParsedConversation object
    
Returns:
    True if successful

#### `cleanup(self)`

Cleanup plugin resources.

### `register()`

Plugin registration function.

---

## src.plugins.doc_refresh_plugin

Documentation Refresh Plugin

Automatically refreshes the 6 synchronized documentation files based on CORTEX 2.0 design:
- docs/story/CORTEX-STORY/Technical-CORTEX.md
- docs/story/CORTEX-STORY/Awakening Of CORTEX.md
- docs/story/CORTEX-STORY/Image-Prompts.md (TECHNICAL DIAGRAMS ONLY - no cartoons)
- docs/story/CORTEX-STORY/History.md
- docs/story/CORTEX-STORY/Ancient-Rules.md (The Rule Book - governance rules)
- docs/story/CORTEX-STORY/CORTEX-FEATURES.md (Simple feature list for humans)

Triggered by: 'Update Documentation' or 'Refresh documentation' commands at entry point

NOTE: Image-Prompts.md generates SYSTEM DIAGRAMS (flowcharts, sequence diagrams, 
architecture diagrams) that reveal CORTEX design - NOT cartoon characters or story 
illustrations. For story illustrations, see prompts/user/cortex-gemini-image-prompts.md

CRITICAL RULES (ABSOLUTE PROHIBITIONS):
1. **NEVER CREATE NEW FILES** - Only update existing documentation files
2. **FORBIDDEN:** Creating Quick Read, Summary, or variant versions
3. **FORBIDDEN:** Creating new files in docs/story/CORTEX-STORY/
4. If a file doesn't exist, FAIL with error - do not create it
5. If content exceeds target length, TRIM existing file - do not create alternatives

READ TIME ENFORCEMENT:
- "Awakening Of CORTEX.md" target: 60-75 minutes (epic full story)
- If Quick Read needed: UPDATE existing file to 15-20 min, don't create variant
- Plugin should TRIM content, not spawn new files
- Validate read time after updates, enforce constraints

PROGRESSIVE RECAP RULES (for multi-part stories):
1. Each PART should start with a quick, funny recap of previous parts
2. Part 2 recaps Part 1 (medium compression, ~150 tokens)
3. Part 3 recaps Part 2 + Part 1 (progressive compression: Part 1 high-level ~80 tokens, Part 2 medium ~120 tokens)
4. Recaps get progressively more compressed as you go back in time
5. Maintains humor, key milestones, and narrative flow
6. Insert recaps RIGHT AFTER the '# PART X:' heading, BEFORE the first interlude
7. Style: casual, funny, single-paragraph format like Lab Notebook

Example Pattern:
  # PART 2: THE EVOLUTION TO 2.0
  
  *[Quick funny recap of Part 1 achievements]*
  
  ## Interlude: The Whiteboard Archaeology
  
  # PART 3: THE EXTENSION ERA
  
  *[Quick funny recap of Part 2 (detailed) + Part 1 (high-level)]*
  
  ## Interlude: The Invoice That Haunts Him

### Plugin

Documentation Refresh Plugin for CORTEX 2.0

**Methods:**

#### `initialize(self)`

Initialize plugin - verify paths exist

#### `execute(self, context)`

Execute documentation refresh

#### `cleanup(self)`

Cleanup plugin resources

---

## src.plugins.extension_scaffold_plugin

Extension Scaffold Plugin for CORTEX 2.0

Generates complete VS Code extension project structure automatically.
This is the core implementation for Phase 3 (VS Code Extension).

Features:
- Complete TypeScript extension project generation
- Python ↔ TypeScript bridge setup
- package.json with all dependencies
- Chat participant (@cortex) implementation
- Lifecycle hooks (focus/blur, checkpoint)
- External monitoring (@copilot capture)
- Test infrastructure
- Build and package scripts

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### Plugin

Extension Scaffold Plugin - Generates VS Code extension project

**Methods:**

#### `initialize(self)`

Initialize plugin - verify templates exist

#### `execute(self, context)`

Execute extension scaffolding

#### `cleanup(self)`

Cleanup plugin resources

---

## src.plugins.hooks

Plugin Hook Definitions for CORTEX 2.0

Centralizes all plugin lifecycle hooks for consistency.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### HookPoint

Lifecycle hooks for plugin execution.

Plugins register for hooks to execute at specific points
in the CORTEX lifecycle.

---

## src.plugins.integrations.__init__

Integration modules for Code Review Plugin

Available integrations:
- Azure DevOps: REST API integration for Azure DevOps pull requests
- GitHub: REST API and GraphQL integration for GitHub pull requests
- GitLab: CI webhook integration (coming soon)
- BitBucket: Pipelines integration (coming soon)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.plugins.integrations.azure_devops_integration

Azure DevOps Integration for Code Review Plugin

Provides integration with Azure DevOps REST API for:
- Pull request retrieval
- Automated code review comments
- Review status updates
- Thread resolution
- Build policy integration

Documentation: https://learn.microsoft.com/en-us/rest/api/azure/devops/

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### AzureDevOpsConfig

Configuration for Azure DevOps integration

**Methods:**

#### `base_url(self)`

Get base API URL

#### `auth_header(self)`

Get authorization header

### AzureDevOpsIntegration

Azure DevOps integration for code reviews

Features:
- Fetch pull request details and file changes
- Post review comments on specific lines
- Update pull request status (approved/needs work)
- Create review threads
- Update build policies

**Methods:**

#### `get_pull_request(self, pr_id)`

Get pull request details

Args:
    pr_id: Pull request ID

Returns:
    Pull request details or None if error

#### `get_pr_files(self, pr_id)`

Get list of files changed in pull request

Args:
    pr_id: Pull request ID

Returns:
    List of file changes with paths and content

#### `create_review_thread(self, pr_id, file_path, line_number, comment, status)`

Create a review thread (comment) on specific line

Args:
    pr_id: Pull request ID
    file_path: File path relative to repository root
    line_number: Line number for comment
    comment: Comment text
    status: Thread status (active, fixed, closed)

Returns:
    True if successful, False otherwise

#### `post_review_summary(self, pr_id, summary, vote)`

Post overall review summary

Args:
    pr_id: Pull request ID
    summary: Summary comment
    vote: Vote (-10: reject, 0: no vote, 5: approved with suggestions,
          10: approved)

Returns:
    True if successful, False otherwise

#### `update_thread_status(self, pr_id, thread_id, status)`

Update status of review thread

Args:
    pr_id: Pull request ID
    thread_id: Thread ID
    status: New status (active, fixed, closed)

Returns:
    True if successful, False otherwise

#### `create_build_policy(self, pr_id, policy_name, status, description)`

Create or update build policy status

Args:
    pr_id: Pull request ID
    policy_name: Policy name (e.g., "Code Review Quality")
    status: Status (succeeded, failed, pending)
    description: Description of policy status

Returns:
    True if successful, False otherwise

#### `post_violations_to_pr(self, pr_id, violations, overall_score)`

Post code review violations to pull request

Args:
    pr_id: Pull request ID
    violations: List of violations from code review
    overall_score: Overall code quality score

Returns:
    True if successful, False otherwise

---

## src.plugins.integrations.github_integration

GitHub Integration for Code Review Plugin

Provides integration with GitHub REST API and GraphQL for:
- Pull request retrieval
- Automated code review comments
- Review status updates (approve, request changes, comment)
- Thread resolution
- Check runs and status checks

Documentation: https://docs.github.com/en/rest

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### GitHubConfig

Configuration for GitHub integration

**Methods:**

#### `base_url(self)`

Get base API URL

#### `auth_header(self)`

Get authorization headers

### GitHubIntegration

GitHub integration for code reviews

Features:
- Fetch pull request details and file changes
- Post review comments on specific lines
- Submit reviews (approve, request changes, comment)
- Create check runs
- Update commit statuses

**Methods:**

#### `get_pull_request(self, pr_number)`

Get pull request details

Args:
    pr_number: Pull request number

Returns:
    Pull request details or None if error

#### `get_pr_files(self, pr_number)`

Get list of files changed in pull request

Args:
    pr_number: Pull request number

Returns:
    List of file changes with paths and patches

#### `create_review_comment(self, pr_number, commit_sha, file_path, line, body, side)`

Create a review comment on specific line

Args:
    pr_number: Pull request number
    commit_sha: Commit SHA to comment on
    file_path: File path relative to repository root
    line: Line number for comment
    body: Comment body (supports Markdown)
    side: Side of diff (LEFT or RIGHT)

Returns:
    True if successful, False otherwise

#### `submit_review(self, pr_number, commit_sha, body, event, comments)`

Submit a pull request review

Args:
    pr_number: Pull request number
    commit_sha: Commit SHA being reviewed
    body: Review summary comment
    event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
    comments: List of review comments with positions

Returns:
    True if successful, False otherwise

#### `create_check_run(self, name, head_sha, status, conclusion, output)`

Create or update a check run

Args:
    name: Check run name
    head_sha: Commit SHA
    status: Status (queued, in_progress, completed)
    conclusion: Conclusion if completed (success, failure, neutral, etc.)
    output: Check run output with title, summary, annotations

Returns:
    True if successful, False otherwise

#### `create_commit_status(self, sha, state, context, description, target_url)`

Create commit status (simpler alternative to check runs)

Args:
    sha: Commit SHA
    state: State (error, failure, pending, success)
    context: Status context (e.g., "CORTEX/code-review")
    description: Status description
    target_url: Optional URL with more details

Returns:
    True if successful, False otherwise

#### `post_violations_to_pr(self, pr_number, commit_sha, violations, overall_score)`

Post code review violations to pull request

Args:
    pr_number: Pull request number
    commit_sha: Commit SHA being reviewed
    violations: List of violations from code review
    overall_score: Overall code quality score

Returns:
    True if successful, False otherwise

---

## src.plugins.investigation_html_id_mapping_plugin

Investigation HTML ID Mapping Plugin for CORTEX 3.0

Dedicated plugin for HTML element analysis, ID mapping, and accessibility improvements
during investigation phases.

Features:
- Element-to-ID mapping analysis
- Missing ID detection with intelligent suggestions
- Accessibility compliance checking
- Testability improvements
- Button caption to ID mapping (e.g., "Submit" → btnSubmit)
- Semantic element analysis
- ARIA attribute recommendations

Integration with InvestigationRouter:
- Token-efficient HTML parsing
- Actionable ID generation suggestions
- Accessibility recommendations
- Testing-friendly element identification

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ElementType

HTML element types for ID mapping

### AccessibilityIssueType

Types of accessibility issues

### IdMappingPriority

Priority levels for ID mapping suggestions

### ElementAnalysis

Analysis of an HTML element

**Methods:**

#### `to_dict(self)`

Convert to dictionary for investigation router

### IdMappingResult

Result of HTML ID mapping analysis

**Methods:**

#### `id_coverage_percentage(self)`

Calculate percentage of elements that have IDs

#### `to_dict(self)`

Convert to dictionary for investigation router

### IdGenerator

Intelligent ID generator for HTML elements

**Methods:**

#### `generate_id(self, element_analysis, context)`

Generate intelligent ID for an element

Args:
    element_analysis: Analysis of the element
    context: Additional context (page name, section, etc.)
    
Returns:
    Suggested ID

### HTMLElementAnalyzer

Analyzes HTML elements for ID mapping and accessibility

**Methods:**

#### `analyze_html_file(self, file_path, content)`

Comprehensive analysis of HTML file for ID mapping

Args:
    file_path: Path to HTML file
    content: HTML content
    
Returns:
    Complete ID mapping analysis

### InvestigationHtmlIdMappingPlugin

HTML element ID mapping plugin for investigation router

**Methods:**

#### `initialize(self)`

Initialize HTML ID mapping plugin

#### `execute(self, context)`

Execute HTML ID mapping analysis during investigation

Args:
    context: Investigation context
    
Returns:
    HTML analysis results

#### `cleanup(self)`

Cleanup HTML mapping plugin

### `register()`

Register the investigation HTML ID mapping plugin

---

## src.plugins.investigation_refactoring_plugin

Investigation Refactoring Plugin for CORTEX 3.0

Intelligent refactoring analysis plugin that integrates with InvestigationRouter
to identify code improvement opportunities without heavy AST parsing.

Features:
- SOLID principle violation detection
- Design pattern recommendations
- Code smell identification
- Complexity reduction suggestions
- Maintainability improvements
- Performance optimization opportunities
- Token-budget efficient analysis

Integration with InvestigationRouter:
- Lightweight pattern-based analysis
- Respects token budget constraints
- Provides actionable refactoring suggestions
- Prioritizes improvements by impact

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### RefactoringType

Types of refactoring opportunities

### RefactoringPriority

Priority levels for refactoring suggestions

### CodeSmell

Common code smells that indicate refactoring opportunities

### RefactoringSuggestion

A specific refactoring suggestion

**Methods:**

#### `to_dict(self)`

Convert to dictionary for investigation router

### CodeMetrics

Lightweight code metrics calculator

**Methods:**

#### `calculate_method_length(lines, start_line)`

Calculate method length starting from given line

#### `calculate_class_metrics(content, class_name)`

Calculate basic class metrics

#### `count_parameters(method_signature)`

Count parameters in method signature

### RefactoringPatternAnalyzer

Analyzes code patterns for refactoring opportunities

**Methods:**

#### `analyze_file(self, file_path, content)`

Analyze file for refactoring opportunities

### InvestigationRefactoringPlugin

Refactoring analysis plugin for investigation router

**Methods:**

#### `initialize(self)`

Initialize refactoring plugin

#### `execute(self, context)`

Execute refactoring analysis during investigation

Args:
    context: Investigation context
    
Returns:
    Refactoring analysis results

#### `cleanup(self)`

Cleanup refactoring plugin

### `register()`

Register the investigation refactoring plugin

---

## src.plugins.investigation_security_plugin

Investigation Security Plugin for CORTEX 3.0

Specialized security analysis plugin that integrates with InvestigationRouter
to provide security vulnerability detection during investigation phases.

Features:
- Vulnerability pattern scanning (OWASP Top 10)
- Dependency security analysis
- Code security best practices validation
- HTML security analysis (XSS, CSRF, etc.)
- Token-budget aware security scanning

Integration with InvestigationRouter:
- Hooks into analysis phase for detailed security scanning
- Respects token budget constraints
- Provides security-specific findings
- Generates actionable security recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### SecurityVulnerabilityType

OWASP Top 10 and common security vulnerabilities

### SecuritySeverity

Security vulnerability severity levels

### SecurityFinding

Security vulnerability finding

**Methods:**

#### `to_dict(self)`

Convert to dictionary for investigation router

### SecurityPatternDatabase

Database of security vulnerability patterns

**Methods:**

#### `get_patterns_for_language(self, language)`

Get security patterns for specific programming language

### HTMLSecurityAnalyzer

Analyzes HTML for security vulnerabilities and ID mapping

**Methods:**

#### `analyze_html_security(self, file_path, content)`

Analyze HTML content for security vulnerabilities

#### `analyze_html_id_mapping(self, file_path, content)`

Analyze HTML for element ID mapping and missing IDs

### InvestigationSecurityPlugin

Security analysis plugin for investigation router

**Methods:**

#### `initialize(self)`

Initialize security plugin

#### `execute(self, context)`

Execute security analysis during investigation

Args:
    context: Investigation context with target entity and budget info
    
Returns:
    Security analysis results

#### `cleanup(self)`

Cleanup security plugin

### `register()`

Register the investigation security plugin

---

## src.plugins.performance_telemetry_plugin

CORTEX Performance Telemetry Plugin

Collects comprehensive performance and business value metrics for team analytics.

Features:
- Performance: Execution times (avg, p50, p95, p99), success rates, error patterns
- Cost Savings: Token optimization, API cost avoidance, time saved
- Productivity: Commits, PRs, velocity, test coverage improvements
- Quality: Bug reduction, code review efficiency, test pass rates
- Copilot Enhancement: Context utilization, memory hits, suggestion quality
- Engineer Attribution: Name, email, machine config for multi-user comparison
- Platform Analysis: Windows vs Mac vs Linux performance differences

Business Value Metrics:
- ROI Calculator: Cost savings vs CORTEX investment
- Productivity Gains: Time saved per engineer per month
- Quality Improvements: Defect reduction, test coverage increase
- Executive Reporting: PowerPoint-ready dashboards

Use Case: Internal team analytics and executive ROI reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### PerformanceMetric

Individual performance measurement

### EngineerProfile

Engineer identification and machine config

### PerformanceTelemetryPlugin

Collects CORTEX performance and business value metrics for team analytics.

Tracked Metrics:
1. Performance: Latency, success rates, error patterns, trends
2. Cost Savings: Token optimization ($$$), API cost avoidance
3. Productivity: Commits, PRs, velocity, code quality
4. Copilot Enhancement: Memory hits, context utilization, suggestion quality
5. Quality: Bug reduction, test coverage, code review efficiency

Engineer Attribution:
- Name, email, machine hostname
- Machine specs (CPU, RAM, platform)
- Installation date, CORTEX version

Use Case: Internal team analytics and executive ROI reporting

**Methods:**

#### `initialize(self)`

Initialize telemetry database

#### `execute(self, context)`

Record performance metric with token tracking.

Args:
    context: Must contain:
        - capability_name: str (e.g., "test_generation")
        - duration_ms: float
        - success: bool
        - error_type: Optional[str] (if success=False)
        - tokens_saved: Optional[int] (CORTEX token optimization)
        - context_size_tokens: Optional[int] (context injected to Copilot)

Returns:
    Execution result

#### `cleanup(self)`

Cleanup resources

#### `export_performance_report(self, days)`

Generate comprehensive business value report for executive presentation.

Args:
    days: Number of days to aggregate (default 30)

Returns:
    Path to export file (YAML)

Raises:
    ValueError: If telemetry not enabled or engineer profile not setup

#### `setup_engineer_profile(self, engineer_name, engineer_email)`

Setup engineer profile for telemetry (one-time setup).

Args:
    engineer_name: Full name (e.g., "John Smith")
    engineer_email: Work email (e.g., "john.smith@company.com")

Returns:
    Confirmation with profile details

#### `disable_telemetry(self)`

Disable telemetry.

Returns:
    Confirmation message

#### `get_telemetry_status(self)`

Get current telemetry status.

Returns:
    Status information

#### `record_productivity_metrics(self, commits_count, prs_created, prs_merged, lines_added, lines_deleted, test_coverage_percent, bugs_fixed, code_reviews_completed)`

Record daily productivity metrics.

Call this at end of day or via automated git hook.

#### `record_cost_savings(self, tokens_saved_count, api_calls_avoided, time_saved_minutes)`

Record daily cost savings metrics.

Calculates estimated USD savings based on GPT-4 pricing.

#### `record_copilot_metrics(self, memory_hits, memory_misses, context_injections, avg_context_tokens, suggestions_accepted, suggestions_rejected)`

Record Copilot enhancement metrics.

Tracks how CORTEX improves GitHub Copilot performance.

### MEMORYSTATUSEX

### `register()`

Register plugin with CORTEX

---

## src.plugins.platform_switch_plugin

CORTEX Platform Switch Plugin

Handles automatic platform detection and configuration when switching between
development environments (Mac/Windows/Linux).

Features:
- Automatic platform detection on startup
- Stores last known platform to detect changes
- Auto-configures environment when platform changes
- Manual /setup command for forced reconfiguration

Usage:
    - Automatic: Opens CORTEX on different platform → auto-detects and configures
    - Manual: "setup environment" or /setup → forces reconfiguration

### Platform

Supported development platforms.

**Methods:**

#### `current()`

Detect current platform.

#### `display_name(self)`

Human-readable platform name.

### PlatformConfig

Platform-specific configuration.

**Methods:**

#### `for_platform(plat)`

Get configuration for a specific platform.

### PlatformSwitchPlugin

Handles platform switching for CORTEX development.

Automates:
1. Git pull latest code
2. Environment setup for platform
3. Brain tests validation
4. Tooling and dependencies verification

**Methods:**

#### `log(self, message)`

Log a message (stores for retrieval).

#### `get_logs(self)`

Get all logged messages.

#### `register_commands(self)`

Register platform commands.

Only /setup is exposed - platform detection is automatic.

Returns:
    List of CommandMetadata objects

#### `initialize(self)`

Initialize the plugin and check for platform changes.

#### `cleanup(self)`

Cleanup plugin resources (required by BasePlugin).

#### `can_handle(self, request)`

Check if this plugin should handle the request.

#### `execute(self, request, context)`

Execute manual platform setup/configuration.

Now delegates to the modular setup orchestrator system.

Note: Platform detection is automatic. This method only runs
when user explicitly requests setup/configuration.

#### `validate(self)`

Validate plugin configuration.

### `register()`

Register the platform switch plugin.

---

## src.plugins.plugin_registry

Plugin Registry

Central registry for CORTEX plugins. Manages plugin discovery, registration,
and lifecycle.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PluginRegistry

Central registry for plugin management.

Responsibilities:
- Plugin discovery and loading
- Plugin lifecycle management (init, execute, cleanup)
- Plugin metadata and capability tracking
- Natural language command routing

**Methods:**

#### `discover_plugins(self, plugins_dir)`

Discover and load plugins from plugins directory.

Args:
    plugins_dir: Path to plugins directory (defaults to src/plugins)
    
Returns:
    Number of plugins discovered

#### `register_plugin(self, plugin)`

Register a plugin instance.

Args:
    plugin: Plugin instance to register

#### `get_plugin(self, plugin_id)`

Get a plugin by ID.

Args:
    plugin_id: Plugin identifier
    
Returns:
    Plugin instance or None if not found

#### `list_plugins(self)`

List all registered plugins.

Returns:
    List of plugin metadata

#### `get_all_plugins(self)`

Get all registered plugin instances.

Returns:
    List of plugin instances

#### `get_plugin_by_natural_language(self, text)`

Find plugin that handles a natural language request.

Args:
    text: Natural language text
    
Returns:
    Best matching plugin or None

#### `initialize_all(self)`

Initialize all registered plugins.

Returns:
    Dict mapping plugin_id to initialization success

#### `cleanup_all(self)`

Clean up all registered plugins.

Returns:
    Dict mapping plugin_id to cleanup success

#### `is_initialized(self)`

Check if registry has been initialized.

#### `plugin_count(self)`

Get number of registered plugins.

### `get_registry()`

Get global plugin registry instance.

---

## src.plugins.sweeper_plugin

Aggressive File Sweeper Plugin for CORTEX 2.0

Scans workspace for unnecessary files and moves them to OS Recycle Bin.
Fully reversible - files can be restored from Recycle Bin/Trash.

Safety through INTELLIGENCE + OS-native reversibility:
- Smart classification rules (age, size, location, patterns)
- Whitelist protection (respects cleanup-rules.yaml)
- Recycle Bin instead of permanent deletion (uses send2trash)
- Minimal audit trail (JSON log for tracking only)

Target Files:
- *.md (reference docs, session reports, backups)
- *.log (logs)
- *.bak, *.backup (manual backups)
- *.tmp, *.temp (temporary files)
- *.pyc, __pycache__ (Python cache)
- *-BACKUP-*, *-OLD-* (backup patterns)
- *-REFERENCE.md, *-IMPLEMENTATION.md, *-QUICK-REFERENCE.md (reference docs)
- Dated duplicates (file.2024-11-10.md)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
Date: November 12, 2025

### FileCategory

Classification categories for files

### FileClassification

Classification result for a file

### SweeperStats

Statistics from sweeper execution

**Methods:**

#### `space_freed_mb(self)`

### SweeperPlugin

Aggressive file sweeper - moves clutter to Recycle Bin (reversible).

Usage:
    sweeper = SweeperPlugin()
    sweeper.initialize()
    results = sweeper.execute({"workspace_root": "/path/to/cortex"})

**Methods:**

#### `initialize(self)`

Initialize sweeper plugin

#### `execute(self, context)`

Execute file sweeping.

Args:
    context: Must contain 'workspace_root' key

Returns:
    Dictionary with execution results

#### `cleanup(self)`

Cleanup sweeper resources

### `register()`

Register sweeper plugin

---

## src.plugins.system_refactor_plugin

System Refactor Plugin - CORTEX Self-Review and Optimization

This plugin performs comprehensive critical review of CORTEX architecture,
identifies test coverage gaps, and executes automated refactoring.

Key Functions:
1. Critical faculty review (brain, plugins, modules, entry points)
2. Test coverage analysis and gap identification
3. Automated REFACTOR phase execution for edge case tests
4. Self-optimization and continuous improvement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### CoverageGap

Represents a test coverage gap.

### RefactorTask

Represents a refactoring task.

### ReviewReport

Comprehensive review report.

### SystemRefactorPlugin

Plugin for critical system review and automated refactoring.

Capabilities:
- Analyze test coverage across all layers
- Identify gaps in brain protection, plugins, modules
- Execute REFACTOR phase for tests in GREEN state
- Generate comprehensive review reports
- Automate gap-filling through test generation

**Methods:**

#### `register_commands(self)`

Register slash commands for this plugin.

#### `can_handle(self, request)`

Check if plugin can handle the request.

#### `initialize(self)`

Initialize plugin resources.

#### `execute(self, request, context)`

Execute refactor plugin workflow.

Workflow:
1. Critical faculty review
2. Gap analysis
3. REFACTOR phase execution
4. Report generation

#### `cleanup(self)`

Cleanup plugin resources.

### `register()`

Register plugin with CORTEX plugin system.

---

## src.response_templates.__init__

Response Template System for CORTEX.

This module provides a unified template-based response system for:
- Instant, zero-execution responses (help, status, etc.)
- Consistent formatting across agents, operations, and plugins
- Verbosity control (concise/detailed/expert)
- Easy maintenance (edit YAML, not code)

Author: Asif Hussain
Version: 1.0

---

## src.response_templates.template_loader

Template data structures and loader for CORTEX response templates.

This module handles loading and managing YAML-based response templates.

Author: Asif Hussain
Version: 1.0

### Template

Represents a single response template.

### TemplateLoader

Loads and manages response templates from YAML file.

**Methods:**

#### `load_templates(self)`

Load all templates from YAML file.

#### `load_template(self, template_id)`

Load a specific template by ID.

Args:
    template_id: The template identifier
    
Returns:
    Template object if found, None otherwise

#### `find_by_trigger(self, trigger)`

Find template by trigger phrase.

Args:
    trigger: The trigger phrase to search for
    
Returns:
    Template object if found, None otherwise

#### `list_templates(self, category)`

List all templates, optionally filtered by category.

Args:
    category: Optional category filter (e.g., 'agent', 'operation')
    
Returns:
    List of Template objects

#### `get_template_ids(self)`

Get all template IDs.

Returns:
    List of template IDs

#### `get_triggers(self)`

Get all registered triggers.

Returns:
    List of trigger phrases

---

## src.response_templates.template_registry

Template registry for CORTEX response templates.

This module provides a centralized registry for managing templates,
including plugin-registered templates.

Author: Asif Hussain
Version: 1.0

### TemplateRegistry

Central registry for all response templates.

**Methods:**

#### `register_template(self, template)`

Register a single template.

Args:
    template: Template object to register

#### `register_plugin_templates(self, plugin_id, templates)`

Register templates from a plugin.

Args:
    plugin_id: Plugin identifier
    templates: List of Template objects

#### `get_template(self, template_id)`

Get template by ID.

Args:
    template_id: Template identifier
    
Returns:
    Template object if found, None otherwise

#### `search_templates(self, query, category, plugin_id)`

Search templates by query.

Args:
    query: Search query (matches template_id, triggers, content)
    category: Optional category filter
    plugin_id: Optional plugin filter
    
Returns:
    List of matching Template objects

#### `list_templates(self, category, plugin_id)`

List all templates with optional filters.

Args:
    category: Optional category filter
    plugin_id: Optional plugin filter
    
Returns:
    List of Template objects

#### `get_categories(self)`

Get all registered categories.

Returns:
    List of category names

#### `get_plugins(self)`

Get all plugins that registered templates.

Returns:
    List of plugin IDs

#### `unregister_plugin_templates(self, plugin_id)`

Unregister all templates for a plugin.

Args:
    plugin_id: Plugin identifier
    
Returns:
    Number of templates unregistered

#### `get_template_count(self)`

Get total number of registered templates.

Returns:
    Template count

#### `clear(self)`

Clear all registered templates.

---

## src.response_templates.template_renderer

Template renderer for CORTEX response templates.

This module handles rendering templates with placeholders and verbosity control.

Author: Asif Hussain
Version: 1.0

### TemplateRenderer

Renders response templates with placeholder substitution and verbosity control.

**Methods:**

#### `render(self, template, context, verbosity)`

Render template with context and verbosity.

Args:
    template: Template object to render
    context: Dictionary of values for placeholder substitution
    verbosity: Override template verbosity (concise/detailed/expert)
    
Returns:
    Rendered template string

#### `render_with_placeholders(self, template)`

Render template with keyword arguments as placeholders.

Args:
    template: Template object to render
    **kwargs: Placeholder values
    
Returns:
    Rendered template string

#### `apply_verbosity(self, content, verbosity)`

Apply verbosity filtering to content.

Verbosity markers:
- [concise]...[/concise] - Only in concise mode
- [detailed]...[/detailed] - Only in detailed mode
- [expert]...[/expert] - Only in expert mode

Args:
    content: Template content
    verbosity: Target verbosity level
    
Returns:
    Filtered content

#### `convert_format(self, content, target_format)`

Convert content to target format.

Args:
    content: Template content
    target_format: Target format (text/markdown/json)
    
Returns:
    Converted content

---

## src.router

CORTEX Universal Router

Processes requests from cortex.md entry point with:
- Slash command expansion (optional shortcuts)
- Intent detection via Phase 4 agents
- Context injection from Tiers 1-3
- Workflow routing
- Session management
- Performance optimization (<100ms routing, <200ms context)

Author: CORTEX Development Team
Version: 1.1 (Added command support)

### CortexRouter

Universal router for cortex.md entry point

Responsibilities:
- Extract user request from cortex.md
- Detect intent via Phase 4 agents
- Inject context from Tiers 1-3
- Route to appropriate workflow
- Log interaction to Tier 1

Performance Targets:
- Intent detection: <100ms
- Context injection: <200ms
- Total routing: <300ms

**Methods:**

#### `process_request(self, user_request, conversation_id)`

Process request from cortex.md

Steps:
1. Expand slash commands (if present)
2. Detect intent (Phase 4: intent-router)
3. Inject context (Tiers 1-3)
4. Route to workflow
5. Log interaction (Tier 1)

Args:
    user_request: User's natural language request or slash command
    conversation_id: Optional existing conversation ID

Returns:
    {
        'intent': 'PLAN',
        'confidence': 0.95,
        'workflow': 'feature_creation',
        'context': {...},
        'conversation_id': 'uuid-here',
        'routing_time_ms': 85.3,
        'context_time_ms': 142.7,
        'total_time_ms': 228.0,
        'command_used': '/mac' or None,
        'next_step': 'Execute workflow...'
    }

#### `get_performance_stats(self)`

Get recent performance statistics

Returns:
    {
        'last_routing_ms': 85.3,
        'last_context_ms': 142.7,
        'routing_target_ms': 100,
        'context_target_ms': 200,
        'total_target_ms': 300
    }

---

## src.session_manager

CORTEX Session Manager

Manages conversation sessions and boundaries:
- Track active conversations
- Detect conversation boundaries (30-min idle per Rule #11)
- Coordinate with Tier 1 FIFO queue
- Session metadata (start, end, intent)

Author: CORTEX Development Team
Version: 1.0

### SessionManager

Manage conversation sessions

Responsibilities:
- Track active conversations
- Detect conversation boundaries (30-min idle per Rule #11)
- Coordinate with Tier 1 FIFO queue
- Session metadata (start, end, intent)

Conversation Boundary Rule:
- 30 minutes of inactivity = new conversation
- Active conversation never deleted (even if oldest)
- When 51st conversation starts, oldest completed deleted (FIFO)

**Methods:**

#### `start_session(self, intent, conversation_id)`

Start new conversation session

Args:
    intent: Detected intent (PLAN, EXECUTE, TEST, etc.)
    conversation_id: Optional conversation ID (generated if not provided)

Returns:
    conversation_id (UUID)

#### `end_session(self, conversation_id)`

End conversation session

Args:
    conversation_id: UUID of conversation to end

#### `get_active_session(self)`

Get active session if exists

Returns None if:
- No active session
- Last activity >30 min ago (conversation boundary per Rule #11)

Returns:
    conversation_id or None

#### `get_session_info(self, conversation_id)`

Get session metadata

Args:
    conversation_id: UUID of conversation

Returns:
    {
        'conversation_id': 'uuid',
        'start_time': 'ISO datetime',
        'end_time': 'ISO datetime' or None,
        'intent': 'PLAN',
        'status': 'active' or 'completed',
        'message_count': 5
    }

#### `get_all_sessions(self, limit)`

Get recent sessions (for monitoring/debugging)

Args:
    limit: Maximum number of sessions to return

Returns:
    List of session info dicts

---

## src.setup.__init__

CORTEX Setup System

Modular, extensible setup system using SOLID design principles.

Architecture:
    BaseSetupModule (abstract interface)
           ↓
    Concrete Modules (VisionAPIModule, PlatformDetectionModule, etc.)
           ↓
    SetupOrchestrator (coordinates execution)
           ↓
    Module Factory (YAML-driven configuration)

Usage:
    from src.setup import create_setup_orchestrator, run_setup
    
    # Quick setup
    result = run_setup(profile='standard')
    
    # Custom setup
    orchestrator = create_setup_orchestrator(profile='full')
    context = {'project_root': Path('/path/to/cortex')}
    report = orchestrator.execute_setup(context)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### `create_setup_orchestrator(profile, config_path)`

Create a configured SetupOrchestrator.

Args:
    profile: Setup profile (minimal, standard, full)
    config_path: Optional path to custom setup_modules.yaml

Returns:
    SetupOrchestrator ready to execute

### `run_setup(profile, project_root, context)`

Convenience function to run complete setup.

Args:
    profile: Setup profile to use
    project_root: Path to CORTEX project (default: auto-detect)
    context: Additional context to pass to modules

Returns:
    SetupExecutionReport with results

Example:
    # Standard setup
    report = run_setup()
    if report.overall_success:
        print("✅ Setup complete!")
    
    # Full setup with Vision API
    report = run_setup(profile='full')
    
    # Custom project path
    report = run_setup(project_root=Path('/custom/path'))

---

## src.setup.base_setup_module

Base Setup Module Interface

SOLID Design Principles:
- Single Responsibility: Each module handles ONE setup concern
- Open/Closed: Easy to add new modules without modifying orchestrator
- Liskov Substitution: All modules are interchangeable via base interface
- Interface Segregation: Minimal required interface
- Dependency Inversion: Modules depend on abstractions, not concrete implementations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### SetupPhase

Setup execution phases for ordering.

### SetupStatus

Module execution status.

### SetupResult

Result from a setup module execution.

Attributes:
    module_id: Unique module identifier
    status: Execution status
    message: Human-readable message
    details: Additional details (dict)
    errors: List of error messages
    warnings: List of warning messages
    duration_ms: Execution time in milliseconds

**Methods:**

#### `success(self)`

Check if execution was successful.

### SetupModuleMetadata

Metadata describing a setup module.

Attributes:
    module_id: Unique identifier (e.g., "platform_config", "vision_api")
    name: Display name
    description: What this module does
    phase: Which phase to run in
    priority: Order within phase (lower = earlier)
    dependencies: List of module_ids that must run first
    optional: Whether this module can be skipped on failure
    enabled_by_default: Whether to run by default

### BaseSetupModule

Abstract base class for all setup modules.

Each module must implement:
- get_metadata(): Return module metadata
- validate_prerequisites(): Check if module can run
- execute(): Perform setup tasks
- rollback(): Undo changes if possible

Example:
    class VisionAPISetupModule(BaseSetupModule):
        def get_metadata(self) -> SetupModuleMetadata:
            return SetupModuleMetadata(
                module_id="vision_api",
                name="Vision API Activation",
                description="Enable GitHub Copilot Vision API",
                phase=SetupPhase.FEATURES
            )
        
        def validate_prerequisites(self, context: Dict) -> Tuple[bool, List[str]]:
            # Check config file exists, etc.
            return True, []
        
        def execute(self, context: Dict) -> SetupResult:
            # Enable Vision API in config
            return SetupResult(...)
        
        def rollback(self, context: Dict) -> bool:
            # Disable Vision API if needed
            return True

**Methods:**

#### `metadata(self)`

Get module metadata (cached).

#### `get_metadata(self)`

Return module metadata.

Returns:
    SetupModuleMetadata describing this module

#### `validate_prerequisites(self, context)`

Validate that prerequisites are met before execution.

Args:
    context: Shared context dictionary with platform info, paths, etc.

Returns:
    (is_valid, list_of_issues)
    - is_valid: True if prerequisites met
    - list_of_issues: Error messages if validation failed

Example:
    def validate_prerequisites(self, context):
        issues = []
        if not context.get('project_root'):
            issues.append("Project root not found in context")
        return len(issues) == 0, issues

#### `execute(self, context)`

Execute setup tasks.

Args:
    context: Shared context dictionary
        - Can read: platform info, paths, previous results
        - Can write: Results for downstream modules

Returns:
    SetupResult with execution details

Example:
    def execute(self, context):
        try:
            # Perform setup
            result = self._enable_feature()
            
            # Update context for downstream modules
            context['vision_api_enabled'] = True
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message="Vision API enabled",
                details={'version': '1.0'}
            )
        except Exception as e:
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=str(e),
                errors=[str(e)]
            )

#### `rollback(self, context)`

Rollback changes if setup fails.

Optional: Override if rollback is possible.

Args:
    context: Shared context dictionary

Returns:
    True if rollback successful

#### `should_run(self, context)`

Determine if module should run based on context.

Override for conditional execution logic.

Args:
    context: Shared context dictionary

Returns:
    True if module should run

#### `log_info(self, message)`

Log info message.

#### `log_warning(self, message)`

Log warning message.

#### `log_error(self, message)`

Log error message.

---

## src.setup.module_factory

Setup Module Factory

Discovers and instantiates setup modules from YAML configuration.
Implements Factory pattern for module creation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### `register_module_class(module_id, module_class)`

Register a module class for factory instantiation.

Args:
    module_id: Unique module identifier
    module_class: Class implementing BaseSetupModule

### `load_setup_config(config_path)`

Load setup configuration from YAML.

Args:
    config_path: Path to setup_modules.yaml (default: auto-detect)

Returns:
    Dictionary with modules configuration

### `create_orchestrator_from_yaml(config_path, profile)`

Create a fully configured SetupOrchestrator from YAML config.

Args:
    config_path: Path to setup_modules.yaml
    profile: Profile to use (minimal, standard, full)

Returns:
    SetupOrchestrator with registered modules

---

## src.setup.modules.__init__

Setup Modules Package

All concrete setup modules implementing BaseSetupModule interface.
Each module handles ONE specific setup responsibility (SOLID Single Responsibility Principle).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## src.setup.modules.brain_initialization_module

Brain Initialization Setup Module

Initializes CORTEX brain databases (Tier 1, 2, 3) and knowledge graph.

SOLID Principles:
- Single Responsibility: Only handles brain initialization
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### BrainInitializationModule

Setup module for initializing CORTEX brain.

Responsibilities:
1. Initialize Tier 1 (SQLite database for conversation history)
2. Initialize Tier 2 (YAML knowledge graph)
3. Initialize Tier 3 (Development context)
4. Create required directories
5. Verify brain health

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for brain initialization.

Checks:
1. Project root exists
2. cortex-brain directory exists or can be created
3. Required Python packages available (PyYAML, sqlite3)

#### `execute(self, context)`

Execute brain initialization.

Steps:
1. Initialize Tier 1 database
2. Initialize Tier 2 knowledge graph
3. Initialize Tier 3 context
4. Verify brain health
5. Update context

---

## src.setup.modules.platform_detection_module

Platform Detection Setup Module

Detects current platform (Mac/Windows/Linux) and configures environment accordingly.

SOLID Principles:
- Single Responsibility: Only handles platform detection and basic config
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PlatformDetectionModule

Setup module for platform detection and configuration.

Responsibilities:
1. Detect current platform (Mac/Windows/Linux)
2. Determine platform-specific paths and commands
3. Configure environment variables
4. Update context with platform information

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for platform detection.

Checks:
1. Python sys module available
2. Platform module available
3. Project root exists

#### `execute(self, context)`

Execute platform detection.

Steps:
1. Detect platform using sys.platform
2. Determine platform-specific settings
3. Configure paths and commands
4. Update context

---

## src.setup.modules.refactoring_tools_module

Refactoring Tools Setup Module

Detects and optionally installs refactoring tools for user's tech stack.

ZERO-FOOTPRINT ARCHITECTURE:
- Detects existing tools (C#, JavaScript/TypeScript, SQL, Python)
- Does NOT force installations
- Provides guidance when tools missing
- Respects organizational firewalls

SOLID Principles:
- Single Responsibility: Only handles refactoring tool detection/setup
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Tech Stack Priority (based on user's organization):
1. C# / .NET Core (Roslyn analyzers, dotnet format)
2. Angular/React (ESLint, Prettier, TSLint)
3. SQL Server/Oracle (sqlfluff, SQL formatters)
4. Python (rope, black) - CORTEX dev only

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ToolInfo

Information about a detected tool.

### RefactoringToolsModule

Setup module for detecting and optionally installing refactoring tools.

Responsibilities:
1. Detect existing tools (dotnet, npm, eslint, etc.)
2. Check for tool versions
3. Optionally install missing tools (user consent required)
4. Provide guidance for blocked tools
5. Update context with detected tools

Zero-Footprint Design:
- NEVER installs by default
- Always asks for consent
- Provides fallback guidance
- Handles firewall restrictions gracefully

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for tool detection.

Checks:
1. Project root exists
2. Platform detected

NO FAILURES - This module is optional and always succeeds validation.

#### `execute(self, context)`

Execute tool detection and optional installation.

Steps:
1. Detect C# / .NET tools (highest priority)
2. Detect JavaScript/TypeScript tools
3. Detect SQL tools
4. Detect Python tools (lowest priority)
5. Provide guidance for missing tools
6. Optionally install (with consent)

---

## src.setup.modules.smart_refactoring_recommender

Smart Refactoring Tool Recommender Module

Analyzes the actual codebase from brain context and recommends
ONLY relevant refactoring tools based on detected languages.

Intelligence Sources:
- Tier 3 development context
- File extension analysis from Tier 1
- Language detection from actual code

SOLID Principles:
- Single Responsibility: Only recommends refactoring tools
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on abstractions (Tier 1, Tier 3)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### ToolPriority

Priority levels for tool recommendations.

### ToolRecommendation

Recommendation for a refactoring tool.

### SmartRefactoringRecommender

Intelligent refactoring tool recommender.

Analyzes actual codebase from brain context and recommends
only relevant tools based on detected languages.

Responsibilities:
1. Query Tier 3 for development context
2. Analyze file extensions to detect languages
3. Calculate language distribution percentages
4. Generate prioritized tool recommendations
5. Detect installed tools
6. Provide installation guidance

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for tool recommendation.

Checks:
1. Brain is initialized
2. Codebase has been crawled
3. File statistics available

#### `execute(self, context)`

Execute smart tool recommendation.

Steps:
1. Analyze codebase to detect languages
2. Calculate language distribution
3. Generate prioritized recommendations
4. Check what's already installed
5. Display recommendations

### `register()`

Register the smart refactoring recommender module.

---

## src.setup.modules.vision_api_module

Vision API Setup Module

Activates GitHub Copilot Vision API for screenshot analysis in CORTEX.

SOLID Principles:
- Single Responsibility: Only handles Vision API activation
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### VisionAPIModule

Setup module for activating Vision API.

Responsibilities:
1. Verify cortex.config.json exists
2. Enable vision_api.enabled flag
3. Configure default settings if not present
4. Verify Pillow/PIL is installed (optional, for preprocessing)
5. Update context for downstream modules

Configuration (from YAML):
    config_file: Path to cortex.config.json
    config_path: JSON path to enable (e.g., "vision_api.enabled")
    max_tokens_per_image: Token budget per image
    cache_results: Whether to cache analysis results
    requires_copilot: Whether GitHub Copilot is required

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for Vision API activation.

Checks:
1. Project root exists in context
2. cortex.config.json exists
3. Config file is valid JSON

#### `execute(self, context)`

Execute Vision API activation.

Steps:
1. Load cortex.config.json
2. Enable vision_api.enabled = true
3. Set default configuration if missing
4. Save updated config
5. Update context

#### `rollback(self, context)`

Rollback Vision API activation.

Disables vision_api.enabled in config.

#### `should_run(self, context)`

Determine if Vision API setup should run.

Runs if:
- User explicitly requested full setup
- User included 'vision' in setup request

---

## src.setup.modulesthon_dependencies_module

Python Dependencies Setup Module

Installs required Python packages from requirements.txt.

SOLID Principles:
- Single Responsibility: Only handles Python package installation
- Open/Closed: Extends BaseSetupModule without modifying it
- Dependency Inversion: Depends on BaseSetupModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### PythonDependenciesModule

Setup module for installing Python dependencies.

Responsibilities:
1. Verify requirements.txt exists
2. Upgrade pip to latest version
3. Install packages from requirements.txt
4. Verify installations
5. Update context with installed packages

**Methods:**

#### `get_metadata(self)`

Return module metadata.

#### `validate_prerequisites(self, context)`

Validate prerequisites for dependency installation.

Checks:
1. Project root exists
2. requirements.txt exists
3. Python command available

#### `execute(self, context)`

Execute Python dependency installation.

Steps:
1. Upgrade pip
2. Install from requirements.txt
3. Verify installations
4. Update context

---

## src.setup.setup_orchestrator

Setup Orchestrator - Coordinates all setup modules

SOLID Principles:
- Single Responsibility: Only orchestrates module execution
- Open/Closed: Add modules via registration, no code changes
- Dependency Inversion: Depends on BaseSetupModule abstraction

Responsibilities:
1. Discover and register setup modules
2. Resolve dependencies between modules
3. Execute modules in correct phase/priority order
4. Handle failures and rollback
5. Provide comprehensive setup report

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### SetupOrchestrator

Orchestrates execution of all setup modules.

Features:
- Automatic module discovery
- Dependency resolution
- Phase-based execution
- Failure handling with rollback
- Comprehensive reporting

Usage:
    orchestrator = SetupOrchestrator()
    
    # Register modules
    orchestrator.register_module(PlatformSetupModule())
    orchestrator.register_module(VisionAPISetupModule())
    
    # Execute setup
    context = {'project_root': Path('/path/to/project')}
    results = orchestrator.execute_setup(context)
    
    # Check results
    if results.overall_success:
        print("✅ Setup complete!")
    else:
        print(f"❌ Setup failed: {results.summary}")

**Methods:**

#### `register_module(self, module)`

Register a setup module.

Args:
    module: Instance of BaseSetupModule

Returns:
    True if registered successfully

#### `register_modules(self, modules)`

Register multiple modules.

Args:
    modules: List of module instances

Returns:
    Number of modules successfully registered

#### `get_module(self, module_id)`

Get a registered module by ID.

#### `get_all_modules(self)`

Get all registered modules.

#### `execute_setup(self, context, selected_modules)`

Execute setup with all registered modules.

Args:
    context: Shared context dictionary
        - Must include: project_root, platform info
        - Modules can add data for downstream modules
    selected_modules: Optional list of module IDs to run
        (if None, runs all enabled modules)

Returns:
    SetupExecutionReport with all results

#### `rollback(self, context)`

Rollback all executed modules in reverse order.

Args:
    context: Shared context

Returns:
    True if rollback successful

### SetupExecutionReport

Comprehensive report of setup execution.

Attributes:
    overall_success: Whether all modules succeeded
    context: Final context state
    results: List of all module results
    summary: Human-readable summary
    duration_ms: Total execution time
    failed_modules: List of failed module IDs

**Methods:**

#### `get_module_result(self, module_id)`

Get result for a specific module.

#### `get_successful_modules(self)`

Get list of successful module IDs.

#### `to_dict(self)`

Convert report to dictionary.

---

## src.tier0.__init__

CORTEX Tier 0: Instinct Layer - Immutable Governance

---

## src.tier0.brain_protector

CORTEX Brain Protector - Architectural Integrity Guardian

Implements 6 protection layers to prevent degradation of CORTEX intelligence:
1. Instinct Immutability - Tier 0 governance rules cannot be bypassed
2. Tier Boundary Protection - Data stored in correct tier
3. SOLID Compliance - No God Objects, proper separation
4. Hemisphere Specialization - Strategic vs tactical separation
5. Knowledge Quality - Pattern validation and confidence thresholds
6. Commit Integrity - Brain state files excluded from commits

Phase 3 Task 3.2: Brain Protector Automation
Duration: 2-3 hours
Date: November 6, 2025

Updated: November 8, 2025 - YAML-based configuration
Now loads rules from cortex-brain/brain-protection-rules.yaml

### Severity

Protection violation severity levels.

### ProtectionLayer

6 protection layers.

### Violation

A single protection violation.

### ModificationRequest

Request to modify CORTEX system.

### ProtectionResult

Result of protection analysis.

### Challenge

Protection challenge presented to user.

### BrainProtector

Automates architectural protection challenges.

Implements 6 protection layers from brain-protection-rules.yaml:
1. Instinct Immutability - Cannot disable TDD, skip DoD/DoR
2. Tier Boundary Protection - Application paths not in Tier 0
3. SOLID Compliance - No God Objects, no mode switches
4. Hemisphere Specialization - RIGHT plans, LEFT executes
5. Knowledge Quality - Min 3 occurrences, max 0.50 single-event confidence
6. Commit Integrity - Brain state files excluded from commits

**Methods:**

#### `analyze_request(self, request)`

Analyze modification request against all protection layers.

Args:
    request: Modification request to analyze

Returns:
    ProtectionResult with severity and violations

#### `generate_challenge(self, violations)`

Generate challenge with threat description, risks, and alternatives.

Args:
    violations: List of violations detected

Returns:
    Challenge object with formatted text and options

#### `log_event(self, challenge, user_decision, override_justification)`

Log protection event to corpus callosum.

Args:
    challenge: Protection challenge
    user_decision: User's decision (accept/different/override)
    override_justification: Justification if user overrode

---

## src.tier0.cleanup_hook

Tier 0: Smart Cleanup Hook (skeleton)

Purpose:
- Enforce CORTEX folder structure hygiene
- Auto-archive safe docs to Git (per Rule PHASE_GIT_CHECKPOINT & Rule #23 design)
- Require approval for potentially breaking moves/archives

Note: This is a skeleton; full implementation will be completed in later phases.

### ArchiveDecision

### CleanupAction

### SmartCleanupHook

Tier 0: Folder structure enforcement with Git-aware archival (skeleton).

**Methods:**

#### `enforce_structure(self)`

Detect and propose actions; do not execute destructive operations here.

#### `analyze_file(self, file_path)`

#### `archive_file(self, file_path)`

#### `move_with_reference_updates(self, src, dst)`

---

## src.tier0.context_optimizer

CORTEX Context Optimizer

Purpose: Optimize context injection for performance and token efficiency.
Achieves 30% token reduction through intelligent context management.

Features:
- Selective tier loading (only load what's needed)
- Pattern relevance scoring (best first)
- Context compression (30% reduction)
- Dynamic sizing (adjust to query)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization

### ContextOptimizer

Optimizes context injection for performance and token efficiency.

Reduces context size by 30% while maintaining quality through:
1. Selective tier loading
2. Pattern relevance scoring
3. Intelligent compression
4. Dynamic sizing

**Methods:**

#### `optimize_context(self, intent, query, available_tiers)`

Optimize context for given intent and query.

Args:
    intent: User intent (PLAN, EXECUTE, TEST, etc.)
    query: User query text
    available_tiers: Dict of available tier instances

Returns:
    Optimized context dict with reduced token count

### PatternRelevanceScorer

Scores patterns by relevance to current query.

Ranking factors:
1. Keyword match (40%)
2. Recency (30%)
3. Confidence (20%)
4. Usage frequency (10%)

**Methods:**

#### `score_patterns(self, patterns, query, limit)`

Score and rank patterns by relevance.

Args:
    patterns: List of pattern dicts
    query: Search query
    limit: Max patterns to return

Returns:
    Ranked list of patterns with scores

### ContextCompressor

Compresses context by removing redundancy and using references.

Compression techniques:
1. Summarize long content
2. Use references instead of full text
3. Remove duplicate information
4. Compress metadata

**Methods:**

#### `compress(self, context, target_reduction)`

Compress context by target percentage.

Args:
    context: Original context dict
    target_reduction: Target reduction (0.30 = 30%)

Returns:
    (compressed_context, compression_stats)

---

## src.tier0.coverage_reporter

CORTEX Test Coverage Reporter

Advanced coverage reporting with tier-specific analysis:
- Overall project coverage
- Tier-specific coverage (tier0, tier1, tier2, tier3)
- Plugin coverage
- HTML report generation
- Coverage threshold validation

Part of Test Execution Infrastructure
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11

### CoverageStatus

Coverage status levels.

### CoverageMetrics

Coverage metrics for a component.

### CoverageReport

Complete coverage report.

### CoverageReporter

Generates and analyzes test coverage reports.

Features:
- Runs pytest with coverage
- Generates HTML reports
- Tier-specific analysis
- Threshold validation
- Trend tracking

**Methods:**

#### `run_coverage(self, test_pattern, show_missing)`

Run tests with coverage analysis.

Args:
    test_pattern: Optional pytest pattern to filter tests
    show_missing: Whether to show missing lines

Returns:
    CoverageReport with results

#### `generate_markdown_report(self, report)`

Generate markdown-formatted coverage report.

### `run_coverage_analysis(test_pattern, threshold)`

Convenience function to run coverage analysis.

Args:
    test_pattern: Optional pytest pattern to filter tests
    threshold: Minimum acceptable coverage percentage

Returns:
    True if threshold passed

---

## src.tier0.git_isolation

CORTEX Git Isolation Enforcement
Prevents CORTEX source code from being committed to user application repositories.

This module:
1. Installs git hooks in user repos to block CORTEX code commits
2. Scans staged files for CORTEX paths
3. Provides clear error messages and alternatives

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file

### GitIsolationEnforcer

Enforces CORTEX code isolation from user application repositories.

Responsibilities:
- Install git hooks in user repos
- Scan commits for CORTEX code
- Block commits that violate isolation
- Provide clear error messages

**Methods:**

#### `install_hooks(self)`

Install git hooks to prevent CORTEX code commits.

Returns:
    True if hooks installed successfully

#### `check_staged_files(self)`

Check if any staged files contain CORTEX code.

Returns:
    (is_safe, violations) where is_safe=False if violations found

#### `uninstall_hooks(self)`

Remove CORTEX git hooks (for testing or uninstall).

Returns:
    True if hooks removed successfully

### `install_git_isolation_hooks(user_repo_path)`

Install git hooks to enforce CORTEX isolation.

This is called during 'cortex init' setup process.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    True if hooks installed successfully

### `check_git_isolation(user_repo_path)`

Check if staged files violate git isolation.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    (is_safe, violations) tuple

---

## src.tier0.governance_engine

CORTEX Tier 0: Governance Engine
Enforces immutable governance rules and protects system integrity.

### Severity

Rule severity levels

### ViolationType

Types of governance violations

### GovernanceEngine

Tier 0 Governance Engine

Responsibilities:
- Load and validate governance rules
- Check for rule violations
- Create challenges for risky changes
- Validate Definition of Done/Ready
- Enforce tier boundaries

**Methods:**

#### `get_rule(self, rule_id)`

Get a governance rule by ID.

Args:
    rule_id: Rule identifier (e.g., 'TEST_FIRST_TDD')

Returns:
    Rule dictionary or None if not found

#### `get_all_rules(self)`

Get all governance rules.

#### `get_rules_by_severity(self, severity)`

Get all rules of a specific severity.

Args:
    severity: Severity level to filter by

Returns:
    List of rules matching the severity

#### `check_tdd_violation(self, has_new_code, has_new_test, test_written_first)`

Check for TDD (Test-First Development) violations.

Args:
    has_new_code: Whether new production code was added
    has_new_test: Whether new test was added
    test_written_first: Whether test was written before code

Returns:
    Violation details or None if no violation

#### `validate_definition_of_done(self, compilation_clean, tests_pass, new_tests_created, tdd_cycle_complete, code_formatted, no_lint_violations, docs_updated, app_runs, no_exceptions, functionality_verified)`

Validate Definition of Done criteria.

Returns:
    Validation result with status and failed criteria

#### `validate_definition_of_ready(self, user_story_clear, acceptance_criteria_defined, testable_outcomes, scope_bounded, dependencies_identified, estimate_possible, files_known, architecture_clear, no_blocking_dependencies)`

Validate Definition of Ready criteria.

Returns:
    Validation result with status and failed criteria

#### `check_tier_boundary_violation(self, tier, data_type)`

Check if data is in the correct tier.

Args:
    tier: Tier number (0-3)
    data_type: Type of data (e.g., 'conversation', 'pattern', 'governance')

Returns:
    Violation details or None if no violation

#### `create_challenge(self, proposed_change, risks, alternatives)`

Create a challenge for a risky user-proposed change.

Args:
    proposed_change: Description of what user wants to change
    risks: List of identified risks
    alternatives: Optional list of safer alternatives

Returns:
    Challenge details to present to user

#### `get_violations(self, severity, limit)`

Get logged violations.

Args:
    severity: Filter by severity level
    limit: Maximum number of violations to return

Returns:
    List of violations

#### `clear_violations(self)`

Clear the violations log.

---

## src.tier0.integrity_checker

CORTEX Brain Integrity Checker

Detects and repairs corruption in brain data structures:
- Conversation history corruption
- Knowledge graph inconsistencies
- Development context staleness
- Cross-tier data leakage

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11

### IntegrityStatus

Integrity check status.

### IntegrityIssue

An integrity issue discovered.

### IntegrityReport

Integrity check report.

### IntegrityChecker

Checks and repairs brain data integrity.

Checks:
1. Data corruption (malformed JSON/YAML)
2. Schema violations (missing required fields)
3. Stale data (outdated timestamps)
4. Cross-tier leakage (data in wrong tier)
5. Orphaned references (broken links)

**Methods:**

#### `check_all(self)`

Run all integrity checks.

Returns:
    IntegrityReport with findings

#### `generate_report(self, integrity_report)`

Generate human-readable integrity report.

Args:
    integrity_report: Integrity check results

Returns:
    Formatted report string

### `check_brain_integrity(auto_repair)`

Convenience function to check brain integrity.

Args:
    auto_repair: Whether to automatically repair issues

Returns:
    True if brain is healthy

---

## src.tier0.optimized_context_loader

Optimized Context Loader

Purpose: Integration layer between CORTEX orchestrator and context optimizer.
Provides optimized context loading with 30% token reduction.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Phase: Phase 4.3 - Context Optimization

### OptimizedContextLoader

Loads and optimizes context for CORTEX orchestrator.

Features:
- Selective tier loading (only what's needed)
- Pattern relevance scoring (best matches first)
- Context compression (30% reduction)
- Dynamic sizing (adjust to query)

Usage:
    loader = OptimizedContextLoader(brain_dir)
    context = loader.load_optimized_context(
        intent="PLAN",
        query="refactor authentication module",
        available_tiers={
            "tier0": instinct_handler,
            "tier1": working_memory,
            "tier2": knowledge_graph,
            "tier3": dev_context
        }
    )

**Methods:**

#### `load_optimized_context(self, intent, query, available_tiers, compression_enabled)`

Load optimized context for given intent and query.

Args:
    intent: User intent (PLAN, EXECUTE, TEST, etc.)
    query: User query text
    available_tiers: Dict of available tier instances
    compression_enabled: Enable compression (default True)

Returns:
    Optimized context dict with metadata

#### `get_metrics(self)`

Get performance metrics

#### `reset_metrics(self)`

Reset performance metrics

---

## src.tier0.skull_protector

SKULL Protection Layer - Safety, Knowledge, Validation & Learning Layer

Prevents development violations by enforcing test validation requirements.

Created: 2025-11-09
Trigger: CSS + Vision API testing failures incident

### SkullRuleId

SKULL protection rule identifiers.

### EnforcementLevel

Enforcement levels for SKULL rules.

### SkullValidation

Result of SKULL validation check.

### FixValidationRequest

Request to validate a fix against SKULL rules.

### SkullProtector

SKULL Protection Layer - Enforces quality standards and test requirements.

The SKULL protects the CORTEX brain from untested changes, false claims,
and quality degradation.

**Methods:**

#### `validate_fix(self, request)`

Validate a fix against SKULL protection rules.

Args:
    request: Fix validation request with test info
    
Returns:
    SkullValidation result
    
Raises:
    SkullProtectionError: If BLOCKING rule violated

### SkullProtectionError

Raised when a BLOCKING SKULL rule is violated.

**Methods:**

### `enforce_skull(request)`

Convenience function to enforce SKULL protection.

Args:
    request: Fix validation request
    
Returns:
    SkullValidation result
    
Raises:
    SkullProtectionError: If BLOCKING rule violated

---

## src.tier0.test_analyzer

CORTEX Test Analyzer
=====================

Analyzes test suite for redundancy, coverage gaps, and optimization opportunities.

**Purpose:**
- Detect duplicate/redundant test cases
- Identify missing test scenarios
- Analyze test complexity and maintainability
- Generate actionable recommendations

**Integration:**
- Part of Tier 0 (Governance)
- Used by brain protector for test quality validation
- Supports SKULL protection enforcement

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Proprietary

### TestComplexity

Test complexity classification.

### RedundancyType

Types of test redundancy.

### TestCase

Represents a single test case.

**Methods:**

#### `line_count(self)`

Get number of lines in test.

#### `full_name(self)`

Get fully qualified test name.

### RedundancyIssue

Represents a detected redundancy.

### TestFileAnalysis

Analysis results for a single test file.

### TestSuiteAnalysis

Complete test suite analysis.

### TestAnalyzer

Analyzes test suite for quality, redundancy, and optimization opportunities.

**Features:**
- AST-based test parsing
- Redundancy detection (exact, semantic, coverage overlap)
- Complexity analysis
- Fixture usage tracking
- Coverage gap identification
- Actionable recommendations

**Methods:**

#### `analyze_suite(self, verbose)`

Perform complete test suite analysis.

Args:
    verbose: Print progress information
    
Returns:
    TestSuiteAnalysis with complete results

#### `generate_report(self, analysis, output_path)`

Generate human-readable analysis report.

Args:
    analysis: TestSuiteAnalysis to report on
    output_path: Optional file path to write report
    
Returns:
    Report as string

#### `export_json(self, analysis, output_path)`

Export analysis as JSON for programmatic processing.

### `main()`

CLI entry point for test analyzer.

---

## src.tier0.test_discovery

CORTEX Test Discovery System

Discovers and categorizes tests for intelligent test execution:
- Discovers tests by tier (tier0, tier1, tier2, tier3)
- Categorizes by plugin
- Identifies integration vs unit tests
- Builds test dependency graph

Part of Test Execution Infrastructure
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11

### TestCategory

Test category types.

### TestTier

CORTEX tier classification.

### TestNode

A discovered test.

### TestDiscoveryResult

Result of test discovery.

### TestDiscovery

Discovers and categorizes pytest tests.

Features:
- Automatic tier detection from file path
- Category inference from test name/markers
- Dependency analysis
- Duration estimation

**Methods:**

#### `discover_all(self)`

Discover all tests in test root.

Returns:
    TestDiscoveryResult with categorized tests

#### `filter_by_tier(self, result, tier)`

Get test node IDs for a specific tier.

Args:
    result: Discovery result
    tier: Tier to filter by

Returns:
    List of pytest node IDs

#### `filter_by_category(self, result, category)`

Get test node IDs for a specific category.

Args:
    result: Discovery result
    category: Category to filter by

Returns:
    List of pytest node IDs

#### `generate_report(self, result)`

Generate human-readable discovery report.

### `discover_tests(test_root)`

Convenience function to discover tests.

Args:
    test_root: Root directory for tests

Returns:
    TestDiscoveryResult

---

## src.tier0.tier_validator

CORTEX Tier Validator - Validates Brain Tier Integrity

Ensures data is stored in the correct tier and validates tier boundaries:
- Tier 0: Immutable governance rules (brain-protection-rules.yaml)
- Tier 1: Conversation history and working memory (SQLite)
- Tier 2: Knowledge graph and learned patterns (YAML)
- Tier 3: Development context and project health (YAML)

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11

### TierLevel

CORTEX tier levels.

### ValidationSeverity

Validation result severity levels.

### TierViolation

A tier boundary violation.

### TierValidationResult

Result of tier validation.

### TierValidator

Validates CORTEX brain tier integrity.

Ensures:
1. Tier 0 contains only immutable governance rules
2. Tier 1 contains only conversation data
3. Tier 2 contains only aggregated patterns
4. Tier 3 contains only development context
5. No cross-tier data leakage

**Methods:**

#### `validate_all_tiers(self)`

Validate all tiers for integrity.

Returns:
    Dictionary mapping tier to validation result

#### `validate_tier(self, tier)`

Validate a specific tier.

Args:
    tier: Tier to validate

Returns:
    TierValidationResult with violations and warnings

#### `generate_report(self, results)`

Generate human-readable validation report.

Args:
    results: Validation results for all tiers

Returns:
    Formatted report string

### `validate_brain_tiers()`

Convenience function to validate all brain tiers.

Returns:
    True if all tiers passed validation

---

## src.tier1.__init__

CORTEX Tier 1: Working Memory
Short-term storage for active conversations

Components:
- ConversationManager: CRUD operations for conversations
- EntityExtractor: Extract entities from text
- FileTracker: Track file modifications
- RequestLogger: Log raw requests/responses
- Tier1API: Unified API wrapper
- MLContextOptimizer: ML-powered context compression (Phase 1.5)
- CacheMonitor: Cache explosion prevention (Phase 1.5)
- TokenMetricsCollector: Token usage tracking (Phase 1.5)

---

## src.tier1.cache_monitor

CORTEX Tier 1: Cache Explosion Monitor
Monitor and prevent cache explosion in conversation history.

Inspired by Cortex Token Optimizer's cache-explosion prevention system.
Prevents runaway token growth that causes API failures.

### CacheMonitor

Monitor and prevent cache explosion in conversation history.

Prevents runaway token growth that causes API failures by implementing
soft and hard token limits with automatic cleanup mechanisms.

Key Features:
- Soft limit warning (40k tokens)
- Hard limit emergency trim (50k tokens)
- Automatic archival of old conversations
- Proactive cleanup recommendations
- 99.9% prevention of API failures

**Methods:**

#### `check_cache_health(self)`

Monitor conversation cache size and prevent explosion.

Returns:
    Health status dict with token counts and actions taken
    
Example:
    >>> monitor = CacheMonitor(working_memory)
    >>> status = monitor.check_cache_health()
    >>> if status['status'] == 'WARNING':
    ...     print(f"Cache at {status['total_tokens']} tokens")

#### `get_trim_recommendations(self)`

Suggest conversations to archive (proactive cleanup).

Returns:
    List of recommendations with conversation IDs and reasons
    
Example:
    >>> monitor = CacheMonitor(working_memory)
    >>> recs = monitor.get_trim_recommendations()
    >>> for rec in recs:
    ...     print(f"Archive {rec['conversation_id']}: {rec['reason']}")

#### `get_statistics(self)`

Get cache monitor statistics.

Returns:
    Dict with monitoring statistics

#### `reset_statistics(self)`

Reset monitoring statistics (useful for testing).

### CacheHealthReport

Comprehensive cache health report.

Provides detailed analysis of cache health including:
- Current token usage
- Trend analysis
- Recommendations

**Methods:**

#### `generate_report(self)`

Generate comprehensive cache health report.

Returns:
    Dict with detailed health information

---

## src.tier1.conversation_manager

CORTEX Tier 1: Conversation Manager
Manages conversation storage and retrieval in SQLite

Task 1.2: ConversationManager Class
Duration: 2 hours

### ConversationManager

Manages conversation data in Tier 1 Working Memory

Responsibilities:
- CRUD operations for conversations
- Message management
- Entity tracking
- File modification tracking
- Active conversation management
- FIFO queue enforcement (20 conversation limit)

**Methods:**

#### `create_conversation(self, agent_id, goal, context)`

Create a new conversation

Args:
    agent_id: Agent identifier
    goal: Conversation goal (optional)
    context: Additional context (optional)
    
Returns:
    conversation_id: Generated conversation ID

#### `add_message(self, conversation_id, role, content)`

Add a message to a conversation

Args:
    conversation_id: Conversation to add message to
    role: user, assistant, or system
    content: Message text
    
Returns:
    message_id: Generated message ID

#### `add_entity(self, conversation_id, entity_type, entity_value)`

Add an entity to a conversation

Args:
    conversation_id: Conversation to add entity to
    entity_type: Type of entity (file, intent, term, feature)
    entity_value: Entity value

#### `add_file(self, conversation_id, file_path, operation)`

Add a modified file to a conversation

Args:
    conversation_id: Conversation to add file to
    file_path: Path to modified file
    operation: Operation type (created, modified, deleted)

#### `end_conversation(self, conversation_id, outcome)`

Mark a conversation as ended

Args:
    conversation_id: Conversation to end
    outcome: Final outcome description

#### `get_conversation(self, conversation_id)`

Get conversation by ID

Args:
    conversation_id: Conversation ID
    
Returns:
    Conversation data with messages, entities, and files

#### `get_active_conversation(self, agent_id)`

Get the currently active conversation for an agent

Args:
    agent_id: Agent identifier
    
Returns:
    Active conversation data or None

#### `get_messages(self, conversation_id)`

Get all messages for a conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    List of messages

#### `get_entities(self, conversation_id, entity_type)`

Get entities for a conversation

Args:
    conversation_id: Conversation ID
    entity_type: Filter by entity type (optional)
    
Returns:
    List of entities

#### `get_files(self, conversation_id)`

Get files modified for a conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    List of files with operations

#### `get_statistics(self)`

Get conversation statistics

Returns:
    Statistics dictionary

#### `get_recent_conversations(self, limit)`

Get recent conversations (most recent first)

Args:
    limit: Maximum number to retrieve
    
Returns:
    List of conversation dictionaries

#### `search_conversations(self, agent_id, start_date, end_date, has_goal)`

Search conversations by criteria

Args:
    agent_id: Filter by agent
    start_date: Start date filter
    end_date: End date filter
    has_goal: Filter by presence of goal
    
Returns:
    List of matching conversations

#### `get_conversation_count(self)`

Get total number of conversations

#### `get_message_count(self, conversation_id)`

Get message count

Args:
    conversation_id: Specific conversation or None for all
    
Returns:
    Message count

#### `export_conversation_jsonl(self, conversation_id)`

Export conversation as JSONL line

Args:
    conversation_id: Conversation to export
    
Returns:
    JSON string

#### `export_to_jsonl(self, conversation_id, output_path)`

Export conversation to JSONL file

Args:
    conversation_id: Conversation to export
    output_path: Path to output file

#### `save_planning_session(self, session_data)`

Save interactive planning session to Tier 1.

Args:
    session_data: Session data including questions, answers, plan
    
Returns:
    True if saved successfully, False otherwise

#### `load_planning_session(self, session_id)`

Load interactive planning session from Tier 1.

Args:
    session_id: Session ID to load
    
Returns:
    Session data dictionary or None if not found

#### `list_planning_sessions(self, state, limit)`

List planning sessions.

Args:
    state: Filter by state (optional)
    limit: Maximum number to return
    
Returns:
    List of session summaries

---

## src.tier1.conversation_quality

CORTEX 3.0 - Conversation Quality Analyzer

Purpose: Semantic analysis of conversations to detect strategic value.
Scores conversations based on planning depth, reasoning, and decision rationale.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### SemanticElements

Detected semantic elements in a conversation.

### QualityScore

Conversation quality assessment.

### ConversationQualityAnalyzer

Analyzes conversation quality using CORTEX 3.0 semantic scoring.

Scoring Matrix (from HYBRID-CAPTURE-SIMULATION-REPORT.md):
- Multi-phase planning: 3 points per phase
- Challenge/Accept flow: 3 points
- Design decisions: 2 points
- File references: 1 point per file (max 3)
- Next steps provided: 2 points
- Code implementation: 1 point
- Architectural discussion: 2 points

Quality Thresholds:
- EXCELLENT: 10+ points (high strategic value)
- GOOD: 6-9 points (moderate strategic context)
- FAIR: 3-5 points (some strategic context)
- LOW: 0-2 points (minimal strategic content)

**Methods:**

#### `analyze_conversation(self, user_prompt, assistant_response)`

Analyze a single conversation turn for strategic value.

Args:
    user_prompt: User's input message
    assistant_response: CORTEX's response
    
Returns:
    QualityScore with semantic analysis and hint recommendation

#### `analyze_multi_turn_conversation(self, turns)`

Analyze a multi-turn conversation.

Args:
    turns: List of (user_prompt, assistant_response) tuples
    
Returns:
    Aggregated quality score for entire conversation

### `create_analyzer(config)`

Factory function to create analyzer with config.

Args:
    config: Optional configuration dict with 'hint_threshold' key
    
Returns:
    Configured ConversationQualityAnalyzer instance

---

## src.tier1.conversation_vault

CORTEX 3.0 - Conversation Vault Manager

Purpose: Manage conversation vault files for manual/automatic capture.
Creates structured markdown files with metadata for easy import to Tier 1.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### ConversationMetadata

Metadata for captured conversation.

### ConversationTurn

Single turn in a conversation.

### ConversationVaultManager

Manages conversation vault files for CORTEX 3.0 hybrid capture.

File Structure:
```
cortex-brain/conversation-vault/
├── 2025-11-13-implement-smart-hints.md
├── 2025-11-13-design-discussion.md
└── metadata/
    ├── conv-20251113-143045.json
    └── conv-20251113-145230.json
```

Each markdown file contains:
- Frontmatter with metadata (YAML)
- Conversation turns (formatted markdown)
- Quality assessment summary
- Import instructions

**Methods:**

#### `create_conversation_file(self, metadata, turns, filename)`

Create conversation file in vault.

Args:
    metadata: Conversation metadata
    turns: List of conversation turns
    filename: Suggested filename
    
Returns:
    Path to created file

#### `get_conversation_by_id(self, conv_id)`

Find conversation file by ID.

Args:
    conv_id: Conversation ID
    
Returns:
    Path to conversation file or None if not found

#### `list_conversations(self, quality_filter, limit)`

List captured conversations with optional filtering.

Args:
    quality_filter: Filter by quality level (EXCELLENT, GOOD, etc.)
    limit: Maximum number to return
    
Returns:
    List of conversation metadata dicts

#### `get_vault_stats(self)`

Get statistics about conversation vault.

### `create_vault_manager(config)`

Factory function to create vault manager with config.

Args:
    config: Optional configuration dict with 'vault_path' key
    
Returns:
    Configured ConversationVaultManager instance

---

## src.tier1.conversations.__init__

Conversation management module.

---

## src.tier1.conversations.conversation_manager

Conversation Manager - Handles conversation CRUD and lifecycle operations.

### Conversation

Represents a conversation in working memory.

### ConversationManager

Manages conversation CRUD operations and lifecycle.

**Methods:**

#### `add_conversation(self, conversation_id, title, message_count, tags)`

Add a new conversation.

Args:
    conversation_id: Unique conversation identifier
    title: Conversation title
    message_count: Initial message count
    tags: Optional list of tags

Returns:
    Created Conversation object

#### `get_conversation(self, conversation_id)`

Get a conversation by ID.

Args:
    conversation_id: Conversation identifier

Returns:
    Conversation object or None if not found

#### `get_recent_conversations(self, limit)`

Get recent conversations ordered by creation date (newest first).

Args:
    limit: Maximum number of conversations to return

Returns:
    List of Conversation objects

#### `set_active_conversation(self, conversation_id)`

Mark a conversation as active (deactivates all others).

Args:
    conversation_id: Conversation to mark as active

#### `get_active_conversation(self)`

Get the currently active conversation.

#### `update_conversation(self, conversation_id, title, summary, tags)`

Update conversation properties.

Args:
    conversation_id: Conversation to update
    title: New title (if provided)
    summary: New summary (if provided)
    tags: New tags (if provided)

#### `increment_message_count(self, conversation_id, count)`

Increment the message count for a conversation.

Args:
    conversation_id: Conversation to update
    count: Number to increment by

#### `get_conversation_count(self)`

Get the total number of conversations.

#### `delete_conversation(self, conversation_id)`

Delete a conversation and all related data.

Args:
    conversation_id: Conversation to delete

---

## src.tier1.conversations.conversation_search

Conversation Search - Handles conversation search operations.

### ConversationSearch

Handles conversation search functionality.

**Methods:**

#### `search_by_keyword(self, keyword)`

Search conversations by keyword in title or messages.

Args:
    keyword: Search keyword

Returns:
    List of matching Conversation objects

#### `search_by_date_range(self, start_date, end_date)`

Get conversations within a date range.

Args:
    start_date: Start of date range
    end_date: End of date range

Returns:
    List of Conversation objects

#### `search_by_entity(self, entity_type, entity_name)`

Find conversations that mention a specific entity.

Args:
    entity_type: Type of entity (file, class, method, etc.)
    entity_name: Name of entity

Returns:
    List of Conversation objects

---

## src.tier1.entities.__init__

Entity extraction module.

---

## src.tier1.entities.entity_extractor

Entity Extractor - Handles entity extraction from conversation content.

### EntityType

Types of entities that can be extracted.

### Entity

Represents an extracted entity.

### EntityExtractor

Extracts and manages entities from conversations.

**Methods:**

#### `extract_entities(self, conversation_id, text)`

Extract entities from text.

Args:
    conversation_id: Conversation to link entities to
    text: Text to extract entities from

Returns:
    List of extracted Entity objects

#### `get_conversation_entities(self, conversation_id)`

Get all entities associated with a conversation.

#### `get_entity_statistics(self)`

Get statistics on entity usage.

---

## src.tier1.entity_extractor

CORTEX Tier 1: Entity Extractor
Extracts entities from conversation text

Task 1.3: EntityExtractor
Duration: 1.5 hours

### EntityExtractor

Extracts meaningful entities from conversation text

Entity types:
- File paths (e.g., src/main.py, cortex-brain/knowledge-graph.yaml)
- Intent keywords (PLAN, EXECUTE, TEST, etc.)
- Technical terms (dashboard, FAB button, migration, etc.)
- Feature names (invoice export, dark mode, etc.)

**Methods:**

#### `extract_all(self, text)`

Extract all entity types from text

Args:
    text: Text to analyze
    
Returns:
    Dictionary with entity types and lists

#### `extract_files(self, text)`

Extract file paths from text

Examples:
- src/main.py
- cortex-brain/knowledge-graph.yaml
- CORTEX/src/tier1/conversation_manager.py

Args:
    text: Text to analyze
    
Returns:
    List of unique file paths

#### `extract_intents(self, text)`

Extract intent keywords from text

Examples:
- PLAN
- EXECUTE
- TEST

Args:
    text: Text to analyze
    
Returns:
    List of intent keywords found

#### `extract_technical_terms(self, text)`

Extract technical terms from text

Examples:
- dashboard
- migration
- pattern

Args:
    text: Text to analyze
    
Returns:
    List of dictionaries with term and frequency

#### `extract_features(self, text)`

Extract feature names from text

Examples:
- "invoice export"
- "dark mode"
- "FAB button"

Args:
    text: Text to analyze
    
Returns:
    List of feature names

#### `extract_entities_list(self, text)`

Extract all entities as a flat list (for backward compatibility)

Args:
    text: Text to analyze
    
Returns:
    Deduplicated list of all entities

#### `extract_from_messages(self, messages)`

Extract entities from a list of messages

Args:
    messages: List of message dictionaries with 'content' or 'text' field
    
Returns:
    Deduplicated list of all entities

#### `get_entity_frequency(self, text)`

Get entity frequency counts

Args:
    text: Text to analyze
    
Returns:
    Dictionary mapping entities to counts

---

## src.tier1.fifo.__init__

FIFO queue management module.

---

## src.tier1.fifo.queue_manager

Queue Manager - Handles FIFO queue enforcement for conversations.

### QueueManager

Manages FIFO queue enforcement (20-conversation limit).

**Methods:**

#### `enforce_fifo_limit(self)`

Enforce FIFO limit of 20 conversations.
Evicts oldest inactive conversation if at capacity.

#### `get_eviction_log(self)`

Get the eviction log.

#### `get_queue_status(self)`

Get current queue status.

Returns:
    Dict with queue statistics

---

## src.tier1.file_tracker

CORTEX Tier 1: File Tracker
Tracks file modifications during conversations

Task 1.4: FileTracker
Duration: 1 hour

### FileTracker

Tracks file modifications during conversations

Responsibilities:
- Extract file paths from text
- Normalize file paths
- Track file modification patterns
- Associate files with conversations

**Methods:**

#### `extract_files_from_text(self, text)`

Extract file paths from text

Args:
    text: Text to analyze
    
Returns:
    List of normalized file paths

#### `track_file_modifications(self, before_text, after_text)`

Compare two texts to find newly mentioned files

Args:
    before_text: Text before operation
    after_text: Text after operation
    
Returns:
    List of newly mentioned files

#### `get_file_patterns(self, files)`

Group files by type/pattern and directory

Args:
    files: List of file paths
    
Returns:
    Dictionary mapping patterns to file lists

#### `get_directory_hierarchy(self, files)`

Get directory modification counts

Args:
    files: List of file paths
    
Returns:
    Dictionary mapping directories to file counts

#### `get_file_statistics(self, files)`

Get statistics about files

Args:
    files: List of file paths
    
Returns:
    Statistics dictionary

#### `format_file_list(self, files, max_files)`

Format file list for display

Args:
    files: List of file paths
    max_files: Maximum files to display
    
Returns:
    Formatted string

---

## src.tier1.fusion_manager

CORTEX 3.0 Milestone 2 - Fusion Integration API

Simple integration layer that makes temporal correlation features
accessible through WorkingMemory and provides higher-level fusion
operations for the dual-channel memory system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### FusionManager

High-level API for CORTEX 3.0 dual-channel memory fusion operations.

Provides simple methods to correlate conversations with ambient events,
generate development narratives, and create unified timelines.

**Methods:**

#### `correlate_imported_conversation(self, conversation_id, auto_correlate)`

Correlate an imported conversation with ambient events.

Args:
    conversation_id: ID of imported conversation
    auto_correlate: If True, run correlation automatically
    
Returns:
    Correlation summary with results and statistics

#### `get_conversation_development_story(self, conversation_id)`

Generate complete development story for a conversation.

Combines conversation content with correlated ambient events
to create a narrative that shows both the planning (WHY) and
execution (WHAT) sides of development.

Args:
    conversation_id: ID of conversation to narrate
    
Returns:
    Development story with timeline and narrative

#### `get_fusion_insights(self, conversation_id, include_recommendations)`

Generate fusion insights for a conversation.

Analyzes correlation patterns to provide insights about
development effectiveness, plan execution, and areas for improvement.

Args:
    conversation_id: ID of conversation to analyze
    include_recommendations: If True, include actionable recommendations
    
Returns:
    Fusion insights and recommendations

---

## src.tier1.lifecycle.__init__

Conversation lifecycle management for CORTEX Tier 1.

Handles conversation creation, workflow state tracking, and closure.

---

## src.tier1.lifecycle.conversation_lifecycle_manager

Conversation Lifecycle Manager - Handles conversation creation, workflow tracking, and closure.

Implements CORTEX 3.0 session-based conversation lifecycle:
- Auto-creates conversations on session start
- Tracks workflow state progression
- Auto-closes conversations on workflow completion
- Detects explicit user commands (new conversation, continue)

### WorkflowState

Workflow states for conversation progression.

### ConversationLifecycleEvent

Represents a lifecycle event for a conversation.

### ConversationLifecycleManager

Manages conversation lifecycle within sessions.

**Methods:**

#### `detect_command_intent(self, user_request)`

Detect explicit command intent from user request.

Args:
    user_request: User's message

Returns:
    Tuple of (intent, confidence) where:
        intent: "new_conversation" | "continue" | "none"
        confidence: 0.0-1.0

#### `infer_workflow_state(self, user_request, current_state)`

Infer workflow state from user request.

Args:
    user_request: User's message
    current_state: Current workflow state (if any)

Returns:
    Inferred WorkflowState

#### `should_create_conversation(self, session_id, user_request, has_active_conversation)`

Determine if new conversation should be created.

Args:
    session_id: Current session ID
    user_request: User's message
    has_active_conversation: Whether session has active conversation

Returns:
    Tuple of (should_create, reason)

#### `should_close_conversation(self, conversation_id, current_state, user_request)`

Determine if conversation should be closed.

Args:
    conversation_id: Conversation to check
    current_state: Current workflow state
    user_request: Optional user message

Returns:
    Tuple of (should_close, reason)

#### `update_workflow_state(self, conversation_id, session_id, new_state, trigger)`

Update conversation workflow state.

Args:
    conversation_id: Conversation to update
    session_id: Associated session
    new_state: New workflow state
    trigger: What triggered the update

#### `close_conversation(self, conversation_id, session_id, reason, final_state)`

Close a conversation.

Args:
    conversation_id: Conversation to close
    session_id: Associated session
    reason: Reason for closure
    final_state: Final workflow state

#### `log_conversation_created(self, conversation_id, session_id, trigger, initial_state)`

Log conversation creation event.

Args:
    conversation_id: Created conversation
    session_id: Associated session
    trigger: What triggered creation
    initial_state: Initial workflow state

#### `get_conversation_history(self, conversation_id)`

Get lifecycle history for a conversation.

Args:
    conversation_id: Conversation to query

Returns:
    List of lifecycle events

#### `get_session_conversation_history(self, session_id)`

Get all conversation events for a session.

Args:
    session_id: Session to query

Returns:
    List of lifecycle events

---

## src.tier1.messages.__init__

Message storage module.

---

## src.tier1.messages.message_store

Message Store - Handles message storage and retrieval operations.

### MessageStore

Manages message storage and retrieval.

**Methods:**

#### `add_messages(self, conversation_id, messages)`

Add messages to a conversation.

Args:
    conversation_id: Conversation to add messages to
    messages: List of message dicts with 'role' and 'content'

#### `get_messages(self, conversation_id)`

Get all messages for a conversation.

Args:
    conversation_id: Conversation identifier

Returns:
    List of message dicts with role, content, timestamp

#### `get_message_count(self, conversation_id)`

Get the number of messages in a conversation.

Args:
    conversation_id: Conversation identifier

Returns:
    Number of messages

#### `delete_messages(self, conversation_id)`

Delete all messages for a conversation.

Args:
    conversation_id: Conversation identifier

---

## src.tier1.migrate_tier1

CORTEX Tier 1 Migration Script
Migrates conversation data from JSONL to SQLite

Task 0.5.1: Tier 1 Migration Script
Duration: 1-1.5 hours

### Tier1Migrator

Migrates Tier 1 conversation data from JSONL to SQLite

**Methods:**

#### `create_schema(self, conn)`

Create Tier 1 database schema

#### `migrate_conversation(self, conn, conv_data)`

Migrate a single conversation record

Args:
    conn: Database connection
    conv_data: Conversation data from JSONL
    
Returns:
    True if successful, False otherwise

#### `migrate(self)`

Execute migration from JSONL to SQLite

Returns:
    Migration statistics dictionary

### `main()`

---

## src.tier1.migration_add_conversation_import

CORTEX 3.0 - Tier 1 Migration: Add Conversation Import Support

Adds columns to support manual conversation import (Channel 2 of dual-channel memory):
- conversation_type: Distinguishes between live conversations and imported ones
- import_source: Tracks where imported conversation came from
- quality_score: Semantic quality rating (0-100)
- semantic_elements: JSON of extracted semantic elements

This enables CORTEX 3.0's dual-channel memory system:
- Channel 1: Ambient daemon (execution-focused, automatic)
- Channel 2: Manual conversation import (strategy-focused, user-driven)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### `migrate_add_conversation_import(db_path)`

Add conversation import support to Tier 1 database.

Args:
    db_path: Path to tier1-working-memory.db

### `verify_migration(db_path)`

Verify migration was applied correctly.

Args:
    db_path: Path to database
    
Returns:
    True if verified

---

## src.tier1.migration_add_sessions

Database migration: Add session support to Tier 1.

Adds session tracking tables and enhances conversations table with session metadata.
CORTEX 3.0 feature: Session-based conversation boundaries.

### `migrate_tier1_add_sessions(db_path)`

Add session support to existing Tier 1 database.

Changes:
- Add sessions table
- Add session_id, last_activity, workflow_state columns to conversations
- Add indexes for session queries
- Backfill existing conversations with default session

Args:
    db_path: Path to Tier 1 SQLite database

Returns:
    True if migration successful, False otherwise

### `main()`

Run migration from command line.

---

## src.tier1.ml_context_optimizer

CORTEX Tier 1: ML Context Optimizer
ML-powered context compression using TF-IDF relevance scoring.

Inspired by Cortex Token Optimizer's proven 76% token reduction success.
Achieves 50-70% token reduction while maintaining conversation quality.

### MLContextOptimizer

ML-powered context compression using TF-IDF relevance scoring.

Achieves 50-70% token reduction while maintaining conversation quality (>0.9).
Based on Cortex Token Optimizer's proven ML engine approach.

Key Features:
- TF-IDF vectorization for relevance scoring
- Conversation context compression (50-70% reduction)
- Pattern context compression
- Quality scoring (maintains >0.9 quality)
- Performance: <50ms optimization overhead

**Methods:**

#### `optimize_conversation_context(self, conversations, current_intent, min_conversations)`

Compress conversation history to most relevant content.

Args:
    conversations: List of conversation dicts with messages
    current_intent: Current user request for relevance scoring
    min_conversations: Minimum conversations to keep (default: 3)

Returns:
    Tuple of (optimized_conversations, metrics)
    
Example:
    >>> optimizer = MLContextOptimizer(target_reduction=0.6)
    >>> conversations = [
    ...     {"id": "1", "messages": [{"content": "Hello"}]},
    ...     {"id": "2", "messages": [{"content": "Debug error"}]},
    ... ]
    >>> optimized, metrics = optimizer.optimize_conversation_context(
    ...     conversations, "Fix the bug"
    ... )
    >>> print(f"Reduced by {metrics['reduction_percentage']:.1f}%")

#### `optimize_pattern_context(self, patterns, query, max_patterns)`

Compress knowledge graph patterns to most relevant subset.

Args:
    patterns: List of pattern dicts from Tier 2
    query: Current query for relevance scoring
    max_patterns: Maximum patterns to return (default: 20)

Returns:
    Tuple of (optimized_patterns, metrics)
    
Example:
    >>> optimizer = MLContextOptimizer()
    >>> patterns = [
    ...     {"description": "Error handling pattern", "confidence": 0.9},
    ...     {"description": "Testing pattern", "confidence": 0.8},
    ... ]
    >>> optimized, metrics = optimizer.optimize_pattern_context(
    ...     patterns, "Fix error handling", max_patterns=10
    ... )

#### `get_statistics(self)`

Get optimizer statistics.

Returns:
    Dict with optimization statistics

---

## src.tier1.narrative_intelligence

CORTEX 3.0 Narrative Intelligence Module
Advanced Fusion - Milestone 3

Enhanced story generation with contextual reasoning and development flow analysis.
Generates coherent narratives about development progress using conversation patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX

### StoryType

Types of stories the narrative intelligence can generate

### NarrativeStyle

Narrative styles for different audiences

### StoryElement

A single element or event in a development story

**Methods:**

### DevelopmentNarrative

A coherent narrative about development progress

**Methods:**

### NarrativeIntelligence

CORTEX 3.0 Narrative Intelligence Module

Generates coherent stories about development progress by analyzing conversation patterns,
file changes, and learning evolution. Provides contextual insights about project development.

**Methods:**

#### `add_story_element(self, element)`

Add a story element to the narrative database

#### `generate_development_story(self, time_range, story_type, narrative_style, focus_files)`

Generate a coherent narrative about development progress.

Args:
    time_range: Tuple of (start_time, end_time) for story scope
    story_type: Type of story to generate
    narrative_style: Style/audience for the narrative
    focus_files: Optional list of files to focus the story on
    
Returns:
    DevelopmentNarrative with generated story

#### `get_recent_narratives(self, limit)`

Get recently generated narratives

#### `get_narrative_statistics(self)`

Get statistics about narrative generation

#### `import_conversation_data(self, conversation_data)`

Import conversation data and create story elements

---

## src.tier1.pattern_learning_engine

CORTEX 3.0 Pattern Learning Engine
Advanced Fusion - Milestone 3

Learns from successful temporal correlations to improve future suggestions.
Core component of CORTEX's adaptive fusion layer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX

### PatternType

Types of patterns the learning engine can recognize and learn from

### CorrelationPattern

A learned pattern from successful correlations

**Methods:**

### LearningSession

A session where patterns were learned from correlations

**Methods:**

### PatternLearningEngine

CORTEX 3.0 Pattern Learning Engine

Learns from successful temporal correlations to improve future suggestions.
Builds patterns that help predict files, sequences, and optimal correlation windows.

**Methods:**

#### `learn_from_correlation(self, correlation_result)`

Learn patterns from a successful temporal correlation result.

Args:
    correlation_result: Result from TemporalCorrelator with correlation data
    
Returns:
    LearningSession with details of what was learned

#### `suggest_files_for_conversation(self, conversation_text, conversation_metadata)`

Predict likely implementation files based on conversation content using learned patterns.

Args:
    conversation_text: Text content of the conversation
    conversation_metadata: Optional metadata (timestamp, participants, etc.)
    
Returns:
    List of file suggestions with confidence scores

#### `boost_confidence_from_patterns(self, correlation_candidates)`

Use learned patterns to boost correlation confidence scores.

Args:
    correlation_candidates: List of potential correlations with base confidence
    
Returns:
    Same list with updated confidence scores based on patterns

#### `get_learning_statistics(self)`

Get statistics about pattern learning progress

#### `export_patterns(self, output_file)`

Export learned patterns to a JSON file for backup or analysis

---

## src.tier1.request_logger

CORTEX Tier 1: Request Logger
Logs raw requests and responses

Task 1.6: Raw Request Logging
Duration: 30 minutes

### RequestLogger

Logs raw requests and responses to JSONL file

Responsibilities:
- Log user requests with timestamps
- Log system responses
- Track request/response pairs
- Support conversation association

**Methods:**

#### `log_request(self, request_text, conversation_id, intent, metadata)`

Log a user request

Args:
    request_text: The request text
    conversation_id: Associated conversation
    intent: Detected intent
    metadata: Additional metadata
    
Returns:
    request_id: Generated request ID

#### `log_response(self, request_id, response_text, conversation_id, status, metadata)`

Log a system response

Args:
    request_id: Associated request ID
    response_text: The response text
    conversation_id: Associated conversation
    status: Response status (success, error, partial)
    metadata: Additional metadata

#### `log_error(self, request_id, error_message, conversation_id, error_type, metadata)`

Log an error

Args:
    request_id: Associated request ID
    error_message: Error description
    conversation_id: Associated conversation
    error_type: Type of error
    metadata: Additional metadata

#### `get_recent_requests(self, limit)`

Get recent requests

Args:
    limit: Maximum number to retrieve
    
Returns:
    List of request entries

#### `get_request_response_pair(self, request_id)`

Get request and response for a request ID

Args:
    request_id: Request ID to find
    
Returns:
    Dictionary with request and response

#### `get_conversation_requests(self, conversation_id)`

Get all requests for a conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    List of request entries

#### `get_statistics(self)`

Get request logging statistics

Returns:
    Statistics dictionary

---

## src.tier1.session_correlation

CORTEX 3.0 - Session-Ambient Correlation Layer

Links session-based conversations with ambient capture events to create
complete development narratives.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### SessionAmbientCorrelator

Correlates session-based conversations with ambient capture events.

**Methods:**

#### `log_ambient_event(self, session_id, event_type, file_path, pattern, score, summary, conversation_id, metadata)`

Log ambient capture event linked to session.

Args:
    session_id: Active workspace session ID
    event_type: Type of event (file_change, terminal_command, git_operation)
    file_path: Path to affected file
    pattern: Detected pattern (FEATURE, BUGFIX, etc.)
    score: Activity score (0-100)
    summary: Natural language summary
    conversation_id: Optional active conversation ID
    metadata: Additional event metadata
    
Returns:
    Event ID

#### `get_session_events(self, session_id, event_type, min_score)`

Get all ambient events for a session.

Args:
    session_id: Session ID to query
    event_type: Optional filter by event type
    min_score: Optional minimum activity score
    
Returns:
    List of events with metadata

#### `get_conversation_events(self, conversation_id)`

Get all ambient events that occurred during a conversation.

Args:
    conversation_id: Conversation ID to query
    
Returns:
    List of events with metadata

#### `generate_session_narrative(self, session_id)`

Generate complete development narrative for a session.

Combines conversations + ambient events into coherent story.

Args:
    session_id: Session ID to narrate
    
Returns:
    Natural language narrative

---

## src.tier1.session_token

CORTEX Tier 1: Session Token Manager
Provides persistent conversation IDs across chat restarts.

Purpose:
- Generate unique, persistent session tokens
- Store token associations with conversations
- Enable "continue" to resume the exact same conversation
- Track session lifecycle (active, paused, completed)
- Bridge chat restarts with continuous context

Usage:
    from src.tier1.session_token import SessionTokenManager
    
    stm = SessionTokenManager()
    
    # Start a new session
    token = stm.create_session("Implementing auth feature")
    print(f"Session Token: {token}")  # SESSION_20251108_143022_a7b3
    
    # Record conversation association
    stm.associate_conversation(token, "github_copilot_conv_12345")
    
    # Later (even after restart)
    session = stm.get_active_session()
    if session:
        print(f"Resume: {session.description}")
        print(f"Conversation ID: {session.conversation_id}")
    
    # End session
    stm.complete_session(token)

### SessionStatus

Status of a session.

### Session

Represents a persistent session.

**Methods:**

#### `to_dict(self)`

Convert to dictionary.

#### `is_stale(self, hours)`

Check if session is stale.

#### `age_hours(self)`

Get session age in hours.

### SessionTokenManager

Manages persistent session tokens for conversation continuity.

Features:
- Generate unique session tokens
- Track session lifecycle
- Associate with conversations and work sessions
- Auto-expire stale sessions
- Enable seamless resume across restarts

**Methods:**

#### `create_session(self, description, conversation_id, work_session_id, metadata)`

Create a new session token.

Args:
    description: Human-readable session description
    conversation_id: Optional conversation ID to associate
    work_session_id: Optional work session ID to link
    metadata: Additional context

Returns:
    token: Unique session token (e.g., SESSION_20251108_143022_a7b3)

#### `get_session(self, token)`

Retrieve session by token.

Args:
    token: Session token

Returns:
    Session if found, None otherwise

#### `get_active_session(self)`

Get the most recent active session.

Returns:
    Active Session if exists, None otherwise

#### `associate_conversation(self, token, conversation_id)`

Associate a conversation ID with a session token.

Args:
    token: Session token
    conversation_id: Conversation identifier from chat system

#### `associate_work_session(self, token, work_session_id)`

Associate a work session ID with a session token.

Args:
    token: Session token
    work_session_id: Work session identifier from WorkStateManager

#### `update_activity(self, token)`

Update last activity timestamp for a session.

Args:
    token: Session token

#### `pause_session(self, token)`

Pause a session (context switch).

Args:
    token: Session token

#### `resume_session(self, token)`

Resume a paused session.

Args:
    token: Session token

#### `complete_session(self, token)`

Mark session as completed.

Args:
    token: Session token

#### `expire_session(self, token)`

Mark session as expired (auto-cleanup).

Args:
    token: Session token

#### `get_all_active_sessions(self)`

Get all active sessions.

Returns:
    List of active Session objects

#### `cleanup_stale_sessions(self, hours)`

Expire stale sessions.

Args:
    hours: Consider sessions stale after this many hours

Returns:
    Number of sessions expired

#### `find_by_conversation(self, conversation_id)`

Find session by conversation ID.

Args:
    conversation_id: Conversation identifier

Returns:
    Session if found, None otherwise

#### `find_by_work_session(self, work_session_id)`

Find session by work session ID.

Args:
    work_session_id: Work session identifier

Returns:
    Session if found, None otherwise

#### `get_statistics(self)`

Get statistics about sessions.

Returns:
    Dictionary with counts and metrics

---

## src.tier1.sessions.__init__

Session management for CORTEX Tier 1 Working Memory.

Provides workspace session tracking and conversation boundary detection.

---

## src.tier1.sessions.session_manager

Session Manager - Handles workspace session lifecycle and boundary detection.

Implements session-based conversation boundaries for CORTEX 3.0 Tier 1.
Sessions map to workspace contexts and provide natural conversation segmentation.

### Session

Represents a workspace session.

### SessionManager

Manages workspace session lifecycle and boundaries.

**Methods:**

#### `detect_or_create_session(self, workspace_path)`

Detect existing active session or create new one.

Creates new session if:
- No active session exists for workspace
- Last activity exceeds idle threshold (>2 hours default)
- Previous session explicitly ended

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session object

#### `get_active_session(self, workspace_path)`

Get active session for workspace.

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session or None

#### `get_session(self, session_id)`

Get session by ID.

Args:
    session_id: Session identifier

Returns:
    Session object or None

#### `end_session(self, session_id, reason)`

End a session.

Args:
    session_id: Session to end
    reason: Reason for ending (manual, idle_timeout, workspace_close)

#### `increment_conversation_count(self, session_id)`

Increment conversation count for session.

Args:
    session_id: Session to update

#### `get_recent_sessions(self, workspace_path, limit)`

Get recent sessions.

Args:
    workspace_path: Optional filter by workspace
    limit: Maximum number of sessions

Returns:
    List of Session objects ordered by start time (newest first)

#### `cleanup_old_sessions(self, retention_days)`

Cleanup sessions older than retention period.

Args:
    retention_days: Number of days to retain sessions

Returns:
    Number of sessions deleted

---

## src.tier1.smart_hint_generator

CORTEX 3.0 - Smart Hint Generator

Purpose: Generate contextual hints for valuable conversation capture.
Shows hints only when quality threshold is met (reduces noise).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### SmartHint

Smart hint for conversation capture.

### SmartHintGenerator

Generates smart hints for conversation capture.

Based on CORTEX 3.0 Hybrid Capture design:
- Shows hints only for GOOD/EXCELLENT conversations
- Provides one-click capture suggestion
- Generates human-readable quality summary
- Stays in chat context (no context switching)

**Methods:**

#### `generate_hint(self, quality, user_prompt)`

Generate smart hint based on conversation quality.

Args:
    quality: Quality score from ConversationQualityAnalyzer
    user_prompt: User's original prompt (for filename generation)
    
Returns:
    SmartHint with conditional display and capture instructions

#### `generate_compact_hint(self, quality)`

Generate compact hint for inline display.

Args:
    quality: Quality assessment
    
Returns:
    One-line hint text or None if shouldn't show

### `create_hint_generator(config)`

Factory function to create hint generator with config.

Args:
    config: Optional configuration dict with 'vault_path' key
    
Returns:
    Configured SmartHintGenerator instance

---

## src.tier1.smart_hint_integration

CORTEX 3.0 - Smart Hint Integration

Purpose: Integration layer for conversation capture workflow.
Provides unified interface for quality analysis, hint generation, and vault storage.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### SmartHintSystem

Unified interface for CORTEX 3.0 smart hint conversation capture.

Workflow:
1. Analyze conversation quality (semantic scoring)
2. Generate hint if quality threshold met
3. On user request, capture to vault
4. Return hint text for display in response

Usage:
```python
system = SmartHintSystem()

# After generating response
hint = system.analyze_and_generate_hint(user_prompt, assistant_response)

if hint.should_show:
    print(hint.hint_text)  # Display to user

# When user says "capture conversation"
filepath = system.capture_conversation(
    user_prompt, 
    assistant_response,
    hint.conversation_id
)
```

**Methods:**

#### `analyze_and_generate_hint(self, user_prompt, assistant_response)`

Analyze conversation and generate hint if needed.

Args:
    user_prompt: User's input
    assistant_response: CORTEX's response
    
Returns:
    SmartHint with conditional display

#### `capture_conversation(self, user_prompt, assistant_response, conversation_id)`

Capture conversation to vault.

Args:
    user_prompt: User's input
    assistant_response: CORTEX's response
    conversation_id: Optional ID (uses current if not provided)
    
Returns:
    Tuple of (filepath, metadata)

#### `capture_multi_turn_conversation(self, turns, topic)`

Capture multi-turn conversation.

Args:
    turns: List of (user_prompt, assistant_response) tuples
    topic: Conversation topic/title
    
Returns:
    Tuple of (filepath, metadata)

#### `get_vault_stats(self)`

Get vault statistics.

#### `list_recent_conversations(self, limit)`

List recent captured conversations.

### `get_smart_hint_system(config)`

Get or create global SmartHintSystem instance.

Args:
    config: Optional configuration
    
Returns:
    SmartHintSystem instance

### `analyze_response_for_hint(user_prompt, assistant_response)`

Convenience function for use in response templates.

Returns hint text if should be shown, None otherwise.

Args:
    user_prompt: User's message
    assistant_response: Assistant's response
    
Returns:
    Hint text or None

### `capture_current_conversation(user_prompt, assistant_response)`

Convenience function to capture conversation.

Returns confirmation message.

Args:
    user_prompt: User's message
    assistant_response: Assistant's response
    
Returns:
    Confirmation message with filepath

---

## src.tier1.smart_recommendations

CORTEX 3.0 - Smart Recommendations API
Advanced Fusion Features - Milestone 3

Intelligent file prediction service that leverages learned patterns from the Pattern Learning Engine
to suggest relevant files based on conversation content and development context.

Features:
- Context-aware file suggestions based on conversation analysis
- Pattern-driven recommendations using learned correlations
- File grouping by relevance and development phase
- Adaptive learning from user interaction feedback
- Integration with both conversational and traditional memories

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Version: 3.0.0

### FileRecommendation

A recommended file with confidence score and reasoning

**Methods:**

### RecommendationContext

Context information for generating recommendations

**Methods:**

### RecommendationFeedback

User feedback on recommendation quality

### SmartRecommendations

Advanced file recommendation engine using pattern learning and context analysis.

This system learns from conversation patterns, file access history, and user feedback
to provide intelligent file suggestions that improve development workflow efficiency.

**Methods:**

#### `get_recommendations(self, context, max_results)`

Generate intelligent file recommendations based on conversation context.

Args:
    context: RecommendationContext with conversation details
    max_results: Maximum number of recommendations to return
    
Returns:
    List of FileRecommendation objects sorted by confidence score

#### `record_file_access(self, file_path, conversation_id, access_type, context)`

Record file access for learning and recommendations

#### `record_feedback(self, feedback)`

Record user feedback on recommendation quality

#### `get_recommendation_analytics(self, days)`

Get analytics on recommendation effectiveness and patterns

#### `optimize_recommendations(self)`

Optimize recommendation system based on collected data and feedback

---

## src.tier1.temporal_correlator

CORTEX 3.0 Milestone 2 - Temporal Correlation Layer

Implements the fusion layer that cross-references conversations with daemon events
to create complete development narratives. This is the core component of
dual-channel memory that links strategic discussions with tactical execution.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### CorrelationResult

Result of temporal correlation between conversation and event.

### ConversationTurn

Represents a single conversation turn for correlation.

### AmbientEvent

Represents an ambient daemon event for correlation.

### TemporalCorrelator

Core temporal correlation algorithm for CORTEX 3.0 dual-channel memory.

Matches conversation turns with ambient daemon events using:
1. Temporal proximity (±1 hour window)
2. File mention matching (backtick paths in conversations)
3. Plan verification (multi-phase tracking)

**Methods:**

#### `correlate_conversation(self, conversation_id, force_recalculate)`

Find temporal correlations for a conversation with ambient events.

Args:
    conversation_id: ID of imported conversation to correlate
    force_recalculate: If True, recalculate even if correlations exist
    
Returns:
    List of correlation results ordered by confidence score

#### `get_conversation_timeline(self, conversation_id)`

Generate a unified timeline of conversation turns and correlated events.

Args:
    conversation_id: ID of conversation to analyze
    
Returns:
    Timeline data with conversation turns and correlated events

---

## src.tier1.test_tier1

CORTEX Tier 1: Unit Tests
Comprehensive test suite for Tier 1 Working Memory

Task 1.7: Unit Testing
Duration: 1.5 hours
Target: 15 tests, 95% coverage

### `temp_dir()`

Create temporary directory for tests

### `db_path(temp_dir)`

Create temporary database path

### `log_path(temp_dir)`

Create temporary log path

### `conversation_manager(db_path)`

Create ConversationManager instance

### `entity_extractor()`

Create EntityExtractor instance

### `file_tracker()`

Create FileTracker instance

### `request_logger(log_path)`

Create RequestLogger instance

### `tier1_api(db_path, log_path)`

Create Tier1API instance

### `test_create_conversation(conversation_manager)`

Test creating a conversation

### `test_add_message(conversation_manager)`

Test adding messages to conversation

### `test_fifo_enforcement(conversation_manager)`

Test FIFO queue enforcement (20 conversation limit)

### `test_entity_tracking(conversation_manager)`

Test entity extraction and tracking

### `test_file_tracking(conversation_manager)`

Test file modification tracking

### `test_extract_file_paths(entity_extractor)`

Test file path extraction

### `test_extract_intents(entity_extractor)`

Test intent extraction

### `test_extract_technical_terms(entity_extractor)`

Test technical term extraction

### `test_file_pattern_detection(file_tracker)`

Test file pattern grouping

### `test_file_statistics(file_tracker)`

Test file statistics generation

### `test_log_request_response(request_logger)`

Test logging requests and responses

### `test_request_statistics(request_logger)`

Test request logging statistics

### `test_api_start_conversation(tier1_api)`

Test starting conversation via API

### `test_api_process_message(tier1_api)`

Test processing message with automatic extraction

### `test_api_conversation_history(tier1_api)`

Test getting conversation history

### `test_full_conversation_workflow(tier1_api)`

Test complete conversation workflow

---

## src.tier1.tier1_api

CORTEX Tier 1: API Wrapper
Unified API for Tier 1 Working Memory operations

Task 1.5: CRUD Operations API
Duration: 1.5 hours

### Tier1API

Unified API for Tier 1 Working Memory

Provides high-level interface for:
- Conversation management
- Entity extraction
- File tracking
- Request logging

**Methods:**

#### `start_conversation(self, agent_id, goal, context)`

Start a new conversation with automatic entity extraction

Args:
    agent_id: Agent identifier
    goal: Conversation goal (optional)
    context: Additional context (optional)
    
Returns:
    conversation_id: New conversation ID

#### `process_message(self, conversation_id, role, content, extract_entities, track_files, log_request)`

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

#### `end_conversation(self, conversation_id, outcome)`

End a conversation with summary

Args:
    conversation_id: Conversation ID
    outcome: Conversation outcome
    
Returns:
    Conversation summary

#### `get_active_conversation(self, agent_id)`

Get active conversation for agent

Args:
    agent_id: Agent identifier
    
Returns:
    Active conversation or None

#### `get_conversation_history(self, conversation_id, include_entities, include_files)`

Get full conversation history

Args:
    conversation_id: Conversation ID
    include_entities: Include extracted entities
    include_files: Include file references
    
Returns:
    Complete conversation data

#### `search_conversations(self, agent_id, start_date, end_date, has_goal)`

Search conversations by criteria

Args:
    agent_id: Filter by agent
    start_date: Start date filter
    end_date: End date filter
    has_goal: Filter by presence of goal
    
Returns:
    List of matching conversations

#### `extract_entities_from_text(self, text)`

Extract all entities from text

Args:
    text: Text to analyze
    
Returns:
    Dictionary of extracted entities by type

#### `get_entity_frequency(self, conversation_id, entity_type)`

Get entity frequency for conversation

Args:
    conversation_id: Conversation ID
    entity_type: Filter by type (optional)
    
Returns:
    Entity frequency counts

#### `track_file_modification(self, conversation_id, file_path, operation)`

Track a file modification

Args:
    conversation_id: Conversation ID
    file_path: Path to file
    operation: Operation type (created, modified, deleted)

#### `get_file_patterns(self, conversation_id)`

Get file patterns for conversation

Args:
    conversation_id: Conversation ID
    
Returns:
    File patterns and statistics

#### `log_response(self, request_id, response_text, status)`

Log a response to a request

Args:
    request_id: Request ID
    response_text: Response content
    status: Response status

#### `log_error(self, request_id, error_message, error_type)`

Log an error for a request

Args:
    request_id: Request ID
    error_message: Error description
    error_type: Error type

#### `get_request_history(self, conversation_id, limit)`

Get request history

Args:
    conversation_id: Filter by conversation (optional)
    limit: Maximum results
    
Returns:
    List of requests

#### `export_conversation_to_jsonl(self, conversation_id, output_path)`

Export conversation to JSONL format

Args:
    conversation_id: Conversation ID
    output_path: Output file path

#### `get_tier1_statistics(self)`

Get comprehensive Tier 1 statistics

Returns:
    Statistics dictionary

---

## src.tier1.token_metrics

CORTEX Tier 1: Token Metrics Collector
Collect and track token usage metrics for cost monitoring and optimization analysis.

Provides real-time visibility into token consumption, cost estimation,
and optimization effectiveness.

### TokenMetricsCollector

Collect token usage metrics for dashboard and monitoring.

Key Features:
- Session token tracking
- Cost estimation ($0.000003 per token)
- Optimization rate calculation
- Database size monitoring
- Real-time metrics for dashboard

**Methods:**

#### `record_request(self, original_tokens, optimized_tokens, optimization_method, quality_score)`

Record tokens for a single request.

Args:
    original_tokens: Token count before optimization
    optimized_tokens: Token count after optimization
    optimization_method: Method used for optimization
    quality_score: Optional quality score (0.0 to 1.0)
    
Example:
    >>> collector = TokenMetricsCollector(working_memory)
    >>> collector.record_request(
    ...     original_tokens=25000,
    ...     optimized_tokens=10000,
    ...     optimization_method="ml_context_compression",
    ...     quality_score=0.95
    ... )

#### `get_current_metrics(self, force_refresh)`

Get current token metrics for dashboard.

Args:
    force_refresh: Force refresh even if cache is valid

Returns:
    Dict with comprehensive metrics
    
Example:
    >>> collector = TokenMetricsCollector(working_memory)
    >>> metrics = collector.get_current_metrics()
    >>> print(f"Session cost: ${metrics['session_cost_usd']:.4f}")

#### `get_session_summary(self)`

Get session summary with detailed breakdown.

Returns:
    Dict with session summary

#### `get_request_history(self, limit)`

Get request history.

Args:
    limit: Optional limit on number of requests to return

Returns:
    List of request dicts

#### `export_session_data(self, output_path)`

Export session data to JSON file.

Args:
    output_path: Optional output file path

Returns:
    Path to exported file

#### `reset_session(self)`

Reset session metrics (start new session).

### TokenMetricsFormatter

Format token metrics for display.

**Methods:**

#### `format_tokens(token_count)`

Format token count with commas.

Args:
    token_count: Number of tokens

Returns:
    Formatted string

#### `format_cost(cost_usd)`

Format cost in USD.

Args:
    cost_usd: Cost in USD

Returns:
    Formatted string

#### `format_percentage(percentage)`

Format percentage.

Args:
    percentage: Percentage value

Returns:
    Formatted string

#### `format_filesize(bytes_count)`

Format file size in human-readable format.

Args:
    bytes_count: Size in bytes

Returns:
    Formatted string

#### `format_duration(seconds)`

Format duration in human-readable format.

Args:
    seconds: Duration in seconds

Returns:
    Formatted string

#### `format_metrics_summary(metrics)`

Format metrics as human-readable summary.

Args:
    metrics: Metrics dict from get_current_metrics()

Returns:
    Multi-line summary string

---

## src.tier1.vision_api

Vision API Integration for CORTEX

Provides image analysis capabilities using GitHub Copilot's built-in vision API.
Includes token budgeting, image preprocessing, and result caching.

Design Document: cortex-brain/cortex-2.0-design/31-vision-api-integration.md

### VisionAPI

GitHub Copilot Vision API integration with token management.

Features:
- Image preprocessing (downscale, compress)
- Token cost estimation
- Budget enforcement (500 token hard limit)
- Result caching (24 hour TTL)
- Graceful fallback on errors

Example:
    vision = VisionAPI(config)
    result = vision.analyze_image(
        image_data="data:image/png;base64,...",
        prompt="Extract button colors and labels"
    )
    
    if result['success']:
        print(f"Analysis: {result['analysis']}")
        print(f"Tokens used: {result['tokens_used']}")

**Methods:**

#### `analyze_image(self, image_data, prompt)`

Analyze image using GitHub Copilot vision API.

Args:
    image_data: Base64-encoded image (data URI format)
    prompt: Natural language analysis request
    
Returns:
    {
        'success': bool,
        'analysis': str,           # Natural language response
        'extracted_data': dict,    # Structured data
        'tokens_used': int,
        'processing_time_ms': int,
        'cached': bool,
        'error': str (if failed)
    }

#### `get_metrics(self)`

Get Vision API usage metrics.

#### `clear_cache(self)`

Clear cached results.

---

## src.tier1.work_state_manager

CORTEX Tier 1: Work State Manager
Tracks in-progress work to enable seamless "continue" functionality.

Purpose:
- Record current task being worked on
- Track files being modified
- Monitor last activity timestamp
- Persist state across sessions
- Enable proactive resume prompts

Usage:
    from src.tier1.work_state_manager import WorkStateManager
    
    wsm = WorkStateManager()
    
    # Start tracking a new task
    wsm.start_task("Implement user authentication", ["src/auth.py", "tests/test_auth.py"])
    
    # Update progress
    wsm.update_progress("Added login endpoint", files_touched=["src/auth.py"])
    
    # Check if there's incomplete work
    if wsm.has_incomplete_work():
        state = wsm.get_current_state()
        print(f"Resume: {state.task_description}")
    
    # Mark task complete
    wsm.complete_task()

### WorkStatus

Status of work session.

### WorkState

Represents the current state of in-progress work.

**Methods:**

#### `to_dict(self)`

Convert to dictionary for serialization.

#### `from_dict(cls, data)`

Create WorkState from dictionary.

#### `is_stale(self, hours)`

Check if work state is stale (no activity for N hours).

#### `duration_minutes(self)`

Calculate duration of work session in minutes.

### WorkStateManager

Manages work state tracking for seamless continuation.

Provides:
- Start/stop tracking work sessions
- Update progress with file changes
- Retrieve current state for resume
- Auto-detect stale sessions
- Integration with Tier 1 database

**Methods:**

#### `start_task(self, task_description, files, metadata)`

Start tracking a new work task.

Args:
    task_description: Human-readable description of the task
    files: Initial list of files being worked on
    metadata: Additional context (branch, conversation_id, etc.)

Returns:
    session_id: Unique identifier for this work session

#### `update_progress(self, progress_note, files_touched, session_id)`

Update progress on current work session.

Args:
    progress_note: Description of what was just done
    files_touched: Files modified in this progress step
    session_id: Specific session to update (defaults to current)

#### `complete_task(self, session_id)`

Mark current work session as completed.

Args:
    session_id: Specific session to complete (defaults to current)

#### `pause_task(self, session_id)`

Pause current work session (e.g., switching contexts).

Args:
    session_id: Specific session to pause (defaults to current)

#### `abandon_task(self, session_id, reason)`

Mark work session as abandoned (not completed).

Args:
    session_id: Specific session to abandon (defaults to current)
    reason: Optional reason for abandonment

#### `get_current_state(self)`

Get the current active work state.

Returns:
    WorkState if there's active work, None otherwise

#### `get_state(self, session_id)`

Get work state for a specific session.

Args:
    session_id: Session identifier

Returns:
    WorkState if found, None otherwise

#### `has_incomplete_work(self)`

Check if there's any incomplete work to resume.

Returns:
    True if there's in-progress or paused work

#### `get_incomplete_sessions(self, include_stale)`

Get all incomplete work sessions.

Args:
    include_stale: Include sessions with no activity in 24+ hours

Returns:
    List of WorkState objects for incomplete work

#### `cleanup_stale_sessions(self, hours)`

Mark stale sessions as abandoned.

Args:
    hours: Consider sessions stale after this many hours of inactivity

Returns:
    Number of sessions marked as abandoned

#### `get_recent_completed(self, limit)`

Get recently completed work sessions.

Args:
    limit: Maximum number of sessions to return

Returns:
    List of completed WorkState objects

#### `get_statistics(self)`

Get statistics about work sessions.

Returns:
    Dictionary with counts and metrics

---

## src.tier1.working_memory

CORTEX Tier 1: Working Memory (Modularized)
Short-term memory storage with FIFO queue (20 conversation limit).

This is a facade that coordinates between modular components while maintaining
backward compatibility with the original API.

### WorkingMemory

Tier 1: Working Memory (Short-Term Memory) - Modular Facade

Manages recent conversations with FIFO eviction when capacity (20) is reached.
Stores conversations, messages, and extracted entities in SQLite.

This class acts as a facade, delegating to specialized modules while
maintaining full backward compatibility with the original API.

**Methods:**

#### `get_optimized_context(self, conversation_id, pattern_context, target_reduction)`

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

#### `get_token_metrics_summary(self)`

Get current token optimization metrics summary (Phase 1.5).

Returns:
    Dict with session metrics, cost savings, and optimization performance.

#### `get_cache_health_report(self)`

Get current cache health report (Phase 1.5).

Returns:
    Cache health report with token counts, limits, and recommendations.

#### `add_conversation(self, conversation_id, title, messages, tags)`

Add a new conversation to working memory.

Args:
    conversation_id: Unique conversation identifier
    title: Conversation title
    messages: List of message dicts with 'role' and 'content'
    tags: Optional list of tags

Returns:
    Created Conversation object

#### `get_conversation(self, conversation_id)`

Get a conversation by ID.

#### `get_recent_conversations(self, limit)`

Get recent conversations ordered by creation date (newest first).

#### `set_active_conversation(self, conversation_id)`

Mark a conversation as active.

#### `get_active_conversation(self)`

Get the currently active conversation.

#### `update_conversation(self, conversation_id, title, summary, tags)`

Update conversation properties.

#### `get_conversation_count(self)`

Get the total number of conversations in working memory.

#### `detect_or_create_session(self, workspace_path)`

Detect or create workspace session (CORTEX 3.0).

Creates new session if:
- No active session for workspace
- Idle gap exceeds threshold (default 2 hours)
- Previous session ended

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session object

#### `get_active_session(self, workspace_path)`

Get active session for workspace.

#### `end_session(self, session_id, reason)`

End a workspace session.

Args:
    session_id: Session to end
    reason: Reason for ending (manual, idle_timeout, workspace_close)

#### `get_session(self, session_id)`

Get session by ID.

#### `get_recent_sessions(self, workspace_path, limit)`

Get recent sessions, optionally filtered by workspace.

#### `handle_user_request(self, user_request, workspace_path, assistant_response, context)`

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

#### `get_conversation_lifecycle_history(self, conversation_id)`

Get lifecycle history for a conversation.

#### `get_session_lifecycle_history(self, session_id)`

Get all conversation lifecycle events for a session.

#### `log_ambient_event(self, session_id, event_type, file_path, pattern, score, summary, conversation_id, metadata)`

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

#### `get_session_events(self, session_id, event_type, min_score)`

Get all ambient events for a session.

Args:
    session_id: Session ID to query
    event_type: Optional filter by event type
    min_score: Optional minimum activity score
    
Returns:
    List of events with metadata

#### `get_conversation_events(self, conversation_id)`

Get all ambient events that occurred during a conversation.

This shows what actually happened (file changes, commands, git ops)
while the conversation was active.

Args:
    conversation_id: Conversation ID to query
    
Returns:
    List of events with metadata

#### `generate_session_narrative(self, session_id)`

Generate complete development narrative for a session.

Combines conversations + ambient events into a coherent story
of what happened during the development session.

Args:
    session_id: Session ID to narrate
    
Returns:
    Natural language narrative (Markdown format)

#### `import_conversation(self, conversation_turns, import_source, workspace_path, import_date)`

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
        'conversation_id': str,
        'session_id': str,
        'quality_score': int,
        'quality_level': str,
        'semantic_elements': dict,
        'turns_imported': int
    }

#### `get_messages(self, conversation_id)`

Get all messages for a conversation.

#### `add_messages(self, conversation_id, messages)`

Append new messages to an existing conversation.

#### `extract_entities(self, conversation_id)`

Extract entities from a conversation's messages.

#### `get_conversation_entities(self, conversation_id)`

Get all entities associated with a conversation.

#### `get_entity_statistics(self)`

Get statistics on entity usage.

#### `search_conversations(self, keyword)`

Search conversations by keyword in title or messages.

#### `find_conversations_with_entity(self, entity_type, entity_name)`

Find conversations that mention a specific entity.

#### `get_conversations_by_date_range(self, start_date, end_date)`

Get conversations within a date range.

#### `get_eviction_log(self)`

Get the eviction log.

#### `close(self)`

Close any open connections (for cleanup in tests).

---

## src.tier1.working_memory_legacy

CORTEX Tier 1: Working Memory
Short-term memory storage with FIFO queue (20 conversation limit).

### EntityType

Types of entities that can be extracted.

### Conversation

Represents a conversation in working memory.

### Entity

Represents an extracted entity.

### WorkingMemory

Tier 1: Working Memory (Short-Term Memory)

Manages recent conversations with FIFO eviction when capacity (20) is reached.
Stores conversations, messages, and extracted entities in SQLite.

**Methods:**

#### `add_conversation(self, conversation_id, title, messages, tags)`

Add a new conversation to working memory.

Args:
    conversation_id: Unique conversation identifier
    title: Conversation title
    messages: List of message dicts with 'role' and 'content'
    tags: Optional list of tags

Returns:
    Created Conversation object

#### `get_conversation(self, conversation_id)`

Get a conversation by ID.

Args:
    conversation_id: Conversation identifier

Returns:
    Conversation object or None if not found

#### `get_recent_conversations(self, limit)`

Get recent conversations ordered by creation date (newest first).

Args:
    limit: Maximum number of conversations to return

Returns:
    List of Conversation objects

#### `set_active_conversation(self, conversation_id)`

Mark a conversation as active.

Args:
    conversation_id: Conversation to mark as active

#### `update_conversation(self, conversation_id, title, summary, tags)`

Update conversation properties.

Args:
    conversation_id: Conversation to update
    title: New title (if provided)
    summary: New summary (if provided)
    tags: New tags (if provided)

#### `get_conversation_count(self)`

Get the total number of conversations in working memory.

#### `get_eviction_log(self)`

Get the eviction log.

#### `get_active_conversation(self)`

Get the currently active conversation.

#### `extract_entities(self, conversation_id)`

Extract entities from a conversation's messages.

Args:
    conversation_id: Conversation to extract entities from

Returns:
    List of extracted Entity objects

#### `get_conversation_entities(self, conversation_id)`

Get all entities associated with a conversation.

#### `search_conversations(self, keyword)`

Search conversations by keyword in title or messages.

Args:
    keyword: Search keyword

Returns:
    List of matching Conversation objects

#### `find_conversations_with_entity(self, entity_type, entity_name)`

Find conversations that mention a specific entity.

Args:
    entity_type: Type of entity
    entity_name: Name of entity

Returns:
    List of Conversation objects

#### `get_conversations_by_date_range(self, start_date, end_date)`

Get conversations within a date range.

Args:
    start_date: Start of date range
    end_date: End of date range

Returns:
    List of Conversation objects

#### `get_entity_statistics(self)`

Get statistics on entity usage.

Returns:
    List of dicts with entity stats

#### `get_messages(self, conversation_id)`

Get all messages for a conversation.

Args:
    conversation_id: Conversation identifier

Returns:
    List of message dicts

#### `add_messages(self, conversation_id, messages)`

Append new messages to an existing conversation.

Args:
    conversation_id: Conversation to append to
    messages: List of message dicts with 'role' and 'content'

#### `close(self)`

Close any open connections (for cleanup in tests).

---

## src.tier2.__init__

CORTEX Tier 2: Knowledge Graph

Backward compatibility layer during Phase 1 modularization.

---

## src.tier2.amnesia

CORTEX Tier 2: Enhanced Amnesia System
Scope-aware selective memory deletion with safety protections.

Features:
- Namespace-scoped deletion (never touch CORTEX-core)
- Generic pattern protection (scope='generic' immune)
- Multi-namespace safety (only delete when all namespaces cleared)
- Confidence-based deletion with safeguards
- Comprehensive audit logging

### AmnesiaStats

Statistics from amnesia operations.

**Methods:**

### EnhancedAmnesia

Enhanced Amnesia System with scope and namespace protection.

CRITICAL SAFETY RULES:
1. NEVER delete scope='generic' patterns (CORTEX core intelligence)
2. NEVER delete patterns with 'CORTEX-core' in namespaces
3. For multi-namespace patterns, only delete when ALL namespaces cleared
4. Always require explicit confirmation for destructive operations
5. Log ALL deletions for audit trail and recovery

**Methods:**

#### `delete_by_namespace(self, namespace, require_confirmation, dry_run, bypass_safety)`

Delete all patterns in a specific namespace.

Safety protections:
- CORTEX-core namespace BLOCKED (cannot delete core intelligence)
- Generic patterns PROTECTED (even if namespace matches)
- Multi-namespace patterns only deleted if this is the LAST namespace
- Confirmation required if deleting >10 patterns

Args:
    namespace: Namespace to clear (e.g., 'KSESSIONS', 'NOOR')
    require_confirmation: If True, check deletion count threshold
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts and protected patterns

Raises:
    ValueError: If trying to delete CORTEX-core namespace
    RuntimeError: If deletion exceeds safety threshold without override

#### `delete_by_confidence(self, max_confidence, protect_generic, namespace, dry_run)`

Delete patterns with confidence below threshold.

Args:
    max_confidence: Delete patterns with confidence <= this value
    protect_generic: Never delete generic patterns (default: True)
    namespace: Limit to specific namespace (optional)
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

#### `delete_by_age(self, days_inactive, protect_generic, namespace, dry_run)`

Delete patterns not accessed in specified days.

Args:
    days_inactive: Delete patterns not accessed in this many days
    protect_generic: Never delete generic patterns (default: True)
    namespace: Limit to specific namespace (optional)
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

#### `clear_application_scope(self, confirmation_code, dry_run)`

Delete ALL application-specific patterns (DANGEROUS!).

This is a nuclear option that clears all application knowledge while
preserving CORTEX core intelligence.

Protections:
- Generic patterns IMMUNE (never deleted)
- CORTEX-core namespace IMMUNE
- Requires confirmation code: "DELETE_ALL_APPLICATIONS"
- Dry run available for safety testing

Args:
    confirmation_code: Must be "DELETE_ALL_APPLICATIONS" to proceed
    dry_run: If True, report what would be deleted without changes

Returns:
    AmnesiaStats with deletion counts

Raises:
    ValueError: If confirmation code is missing or incorrect

#### `get_deletion_preview(self, namespace, max_confidence, days_inactive)`

Preview what would be deleted without making changes.

Args:
    namespace: Preview namespace deletion
    max_confidence: Preview confidence threshold deletion
    days_inactive: Preview age-based deletion

Returns:
    Dict with deletion counts and sample patterns

#### `export_deletion_log(self, output_path)`

Export deletion log to JSON file for recovery.

Args:
    output_path: Path to save deletion log

Returns:
    True if successful, False otherwise

---

## src.tier2.knowledge_graph.__init__

CORTEX Tier 2: Knowledge Graph (Modular Architecture)

Long-term memory with FTS5 semantic search and pattern relationships.

PHASE 1 MIGRATION: This package is under active development.
For backward compatibility, we re-export from the legacy monolithic file.

New Structure (in progress):
- types.py: Shared data types (Pattern, PatternType, etc.) ✅
- database/: Database schema and connections ✅
- patterns/: Pattern storage, search, and decay logic (TODO)
- relationships/: Pattern relationship management (TODO)
- tags/: Tag-based organization (TODO)

Once modularization is complete, this will import from the new coordinator.

---

## src.tier2.knowledge_graph.database

Knowledge Graph Database Module

This module handles all database operations for the Knowledge Graph including:
- Database connection management
- Schema creation and migrations
- Transaction handling
- Connection pooling (future enhancement)

Responsibilities (Single Responsibility Principle):
    - Database schema initialization
    - Connection lifecycle management
    - Schema migrations and upgrades
    - Database health checks

Performance Target:
    - Connection establishment: <10ms
    - Schema creation: <50ms
    - Migration execution: <100ms

Example:
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> db = DatabaseConnection(db_path="cortex-brain/tier2/kg.db")
    >>> conn = db.get_connection()
    >>> cursor = conn.cursor()
    >>> # ... execute queries ...
    >>> db.close()

### DatabaseConnection

Manages SQLite database connections and schema for Knowledge Graph.

This class encapsulates all database-level operations, ensuring a clean
separation between data access and business logic.

Attributes:
    db_path (Path): Path to the SQLite database file
    _conn (sqlite3.Connection): Active database connection (cached)

Methods:
    get_connection: Retrieve (or create) database connection
    init_schema: Create all required tables with proper indexes
    migrate: Run schema migrations for upgrades
    close: Properly close database connection
    health_check: Verify database integrity

**Methods:**

#### `get_connection(self)`

Get database connection (creates if not exists).

Returns:
    Active SQLite connection with row factory enabled

Note:
    Connections are cached for performance. Call close() when done.

#### `init_schema(self)`

Create database schema if it doesn't exist.

This method is idempotent - safe to call multiple times.
Creates all tables, indexes, and triggers required by Knowledge Graph.

Tables Created:
    - patterns: Core pattern storage with FTS5 support
    - pattern_relationships: Graph edges between patterns
    - pattern_tags: Many-to-many tag associations
    - confidence_decay_log: Audit trail for confidence adjustments
    - schema_version: Track database version for migrations

Performance:
    - First run: ~50ms (creates all tables)
    - Subsequent runs: ~5ms (no-op if schema exists)

#### `migrate(self, target_version)`

Run schema migrations to upgrade database.

Args:
    target_version: Version to migrate to (default: latest)

Returns:
    Tuple of (old_version, new_version)

Raises:
    ValueError: If target_version is invalid
    sqlite3.DatabaseError: If migration fails

Example:
    >>> db = DatabaseConnection()
    >>> old, new = db.migrate()
    >>> print(f"Migrated from v{old} to v{new}")

#### `close(self)`

Close database connection if open.

Always call this when done with the database to ensure
proper cleanup and prevent file locking issues.

#### `health_check(self)`

Perform database health check.

Returns:
    Dictionary with health metrics:
        - status: "healthy" | "degraded" | "critical"
        - checks: Individual check results
        - metrics: Performance metrics

Checks Performed:
    1. Database file readable/writable
    2. Schema version matches expected
    3. No table corruption
    4. FTS5 indexes functional
    5. Referential integrity intact

Example:
    >>> db = DatabaseConnection()
    >>> health = db.health_check()
    >>> assert health['status'] == 'healthy'

---

## src.tier2.knowledge_graph.database.__init__

Knowledge Graph Database Package

Handles database schema and connections.

---

## src.tier2.knowledge_graph.database.connection

Knowledge Graph Database Connection

Manages database connections with connection pooling.

### ConnectionManager

Manages SQLite database connections.

Responsibilities:
- Create and manage database connections
- Connection pooling (if needed)
- Transaction management

**Methods:**

#### `get_connection(self)`

Get a database connection.

Returns:
    SQLite connection with row_factory set

#### `close(self)`

Close database connection if open.

#### `transaction(self)`

Context manager for transactional operations.

Yields:
    Database connection with transaction management

#### `health_check(self)`

Check database health.

Returns:
    Dictionary with status, timestamp, and optional error

#### `migrate(self, target_version)`

Apply database migration.

Args:
    target_version: Target migration version (defaults to SCHEMA_VERSION)
    
Returns:
    Tuple of (old_version, new_version)

#### `execute_query(self, query, params)`

Execute a SELECT query and return results.

Args:
    query: SQL SELECT query
    params: Query parameters
    
Returns:
    List of rows (as sqlite3.Row objects)

#### `execute_update(self, query, params)`

Execute an INSERT/UPDATE/DELETE query.

Args:
    query: SQL query
    params: Query parameters
    
Returns:
    Number of rows affected

#### `execute_many(self, query, params_list)`

Execute multiple queries in a transaction.

Args:
    query: SQL query
    params_list: List of parameter tuples
    
Returns:
    Total number of rows affected

---

## src.tier2.knowledge_graph.database.schema

Knowledge Graph Database Schema

Handles database initialization and schema management.

### DatabaseSchema

Manages Knowledge Graph database schema.

Responsibilities:
- Create tables (patterns, relationships, tags, decay log)
- Create FTS5 virtual table for search
- Set up triggers for FTS5 sync
- Create performance indexes

**Methods:**

#### `initialize(db_path)`

Initialize database schema with all tables, indexes, and triggers.

Args:
    db_path: Path to SQLite database file

---

## src.tier2.knowledge_graph.knowledge_graph

KnowledgeGraph Facade (Coordinator)

Provides a backward-compatible, high-level API aggregating modular components:
    - PatternStore (CRUD + confidence/access tracking)
    - PatternSearch (FTS5 BM25 ranked search + namespace boosting)
    - PatternDecay (scheduled confidence decay + audit trail)
    - RelationshipManager (graph edges CRUD + traversal)
    - TagManager (tag CRUD + queries)

Design Goals:
    - Keep each module <500 LOC (SOLID single responsibility)
    - Orchestrate operations without duplicating logic
    - Provide stable API while legacy code migrates off monolith
    - Allow eventual consolidation of database abstraction

NOTE:
    Two database abstractions currently exist (DatabaseConnection & ConnectionManager).
    This facade uses ConnectionManager for slimmer transactional helpers. A future
    consolidation can rename it to KGDatabase and remove DatabaseConnection.

### KnowledgeGraph

High-level orchestration for Knowledge Graph operations.

**Methods:**

#### `store_pattern(self)`

#### `learn_pattern(self, pattern, namespace, is_cortex_internal)`

Learn a new pattern with namespace protection.

Wrapper for store_pattern that accepts pattern dict and namespace separately.
Useful for cleaner test syntax.

#### `query(self, namespace_filter)`

Query patterns with namespace filtering.

Wrapper that provides namespace-based filtering on top of search.

#### `get_pattern(self, pattern_id)`

#### `update_pattern(self, pattern_id, updates)`

#### `delete_pattern(self, pattern_id)`

#### `list_patterns(self)`

#### `search_patterns(self, query)`

#### `search_patterns_with_namespace_priority(self, query)`

#### `get_cortex_patterns(self)`

#### `get_application_patterns(self, namespace)`

#### `apply_decay(self)`

#### `get_decay_candidates(self)`

#### `pin_pattern(self, pattern_id)`

#### `unpin_pattern(self, pattern_id)`

#### `get_decay_log(self)`

#### `create_relationship(self)`

#### `get_relationships(self, pattern_id, direction)`

#### `traverse_graph(self, start_pattern)`

#### `add_tag(self, pattern_id, tag)`

#### `remove_tag(self, pattern_id, tag)`

#### `get_tags(self, pattern_id)`

#### `get_patterns_by_tag(self, tag)`

#### `list_all_tags(self)`

#### `detect_analysis_namespace(self, request, context)`

Detect appropriate namespace for analysis based on request and context.

Args:
    request: User's request text
    context: Analysis context (files analyzed, workspace, etc.)

Returns:
    Namespace string (e.g., 'ksessions_architecture', 'workspace.features.etymology')

#### `save_architectural_analysis(self, namespace, analysis_data, metadata)`

Save architectural analysis to knowledge graph with proper namespace.

Args:
    namespace: Detected namespace for this analysis
    analysis_data: Structured analysis results
    metadata: Optional metadata about the analysis
    
Returns:
    Dict with save results and confirmation data

#### `health_check(self)`

#### `migrate(self, target_version)`

#### `close(self)`

---

## src.tier2.knowledge_graph.patterns.__init__

Pattern management modules for Knowledge Graph.

---

## src.tier2.knowledge_graph.patterns.pattern_decay

Pattern Decay Module

Implements confidence decay based on access patterns (Governance Rule #12).

Decay Logic:
    - Patterns unused for >60 days start decaying
    - Decay rate: 1% per day
    - Minimum confidence: 0.3 (delete below this)
    - Pinned patterns: immune to decay

Responsibilities:
    - Calculate decay for patterns
    - Apply decay adjustments
    - Delete low-confidence patterns
    - Log decay operations (audit trail)

Performance Targets:
    - Decay calculation: <5ms per pattern
    - Batch decay (1000 patterns): <500ms
    - Cleanup operation: <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_decay import PatternDecay
    >>> decay = PatternDecay(db)
    >>> results = decay.apply_decay()
    >>> print(f"Decayed: {results['decayed']}, Deleted: {results['deleted']}")

### PatternDecay

Manages confidence decay for patterns.

Implements time-based decay algorithm that reduces confidence
for patterns that haven't been accessed recently.

**Methods:**

#### `calculate_decay(self, pattern_id, as_of_date)`

Calculate decay for a single pattern (without applying it).

Args:
    pattern_id: Pattern to calculate decay for
    as_of_date: Date to calculate decay from (default: now)

Returns:
    Dictionary with:
        - pattern_id
        - current_confidence
        - days_since_access
        - decay_amount
        - new_confidence
        - should_delete

Performance: <5ms

#### `apply_decay(self)`

Apply decay to all eligible patterns.

Process:
1. Find patterns eligible for decay (not pinned, >60 days old)
2. Calculate decay for each
3. Update confidence or delete if below minimum
4. Log all operations

Returns:
    Dictionary with:
        - patterns_checked: Total patterns evaluated
        - patterns_decayed: Patterns with confidence reduced
        - patterns_deleted: Patterns removed (confidence < MIN_CONFIDENCE)
        - decay_log_entries: Audit trail records created

Performance: <500ms for 1000 patterns

#### `get_decay_candidates(self)`

Find patterns eligible for decay.

Criteria:
    - Not pinned
    - last_accessed > DECAY_THRESHOLD_DAYS ago
    - confidence > MIN_CONFIDENCE

Returns:
    List of pattern dictionaries with decay calculations

Performance: <50ms

#### `pin_pattern(self, pattern_id)`

Pin a pattern to protect it from confidence decay.

Args:
    pattern_id: Pattern to pin

Returns:
    True if pinned successfully, False if pattern not found

Performance: <10ms

#### `unpin_pattern(self, pattern_id)`

Unpin a pattern to allow confidence decay.

Args:
    pattern_id: Pattern to unpin

Returns:
    True if unpinned successfully, False if pattern not found

Performance: <10ms

#### `get_decay_log(self, pattern_id, limit)`

Get confidence decay audit trail.

Args:
    pattern_id: Filter by specific pattern (optional)
    limit: Maximum entries to return

Returns:
    List of decay log entries

Performance: <30ms

---

## src.tier2.knowledge_graph.patterns.pattern_search

Pattern Search Module

Handles semantic search across patterns using SQLite FTS5 (Full-Text Search).

Responsibilities:
    - FTS5 index management
    - BM25-ranked search queries
    - Namespace-aware search (boundary enforcement)
    - Multi-filter search (tags, confidence, scope)
    - Related pattern discovery

Performance Targets:
    - Simple search: <50ms
    - Complex search (multi-filter): <100ms
    - FTS5 ranking: <20ms overhead

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_search import PatternSearch
    >>> search = PatternSearch(db)
    >>> results = search.search("TDD workflow", min_confidence=0.8)
    >>> for result in results:
    ...     print(f"{result['title']}: {result['score']}")

### PatternSearch

Semantic pattern search using FTS5.

Implements BM25-ranked full-text search with namespace awareness
and confidence-based filtering.

**Methods:**

#### `search(self, query, min_confidence, scope, namespaces, limit)`

Search patterns using FTS5 semantic search with BM25 ranking.

Supports FTS5 query syntax:
- Simple keywords: "testing"
- Phrase search: '"test driven development"'
- Boolean operators: "testing AND refactoring"
- Prefix matching: "refactor*"
- NOT operator: "testing NOT manual"

Args:
    query: Search query string (FTS5 syntax)
    min_confidence: Minimum confidence threshold (0.0-1.0)
    scope: Filter by scope ('cortex' or 'application')
    namespaces: Filter by specific namespaces
    limit: Maximum results to return

Returns:
    List of patterns ranked by BM25 score (lower score = better match)

Performance: <50ms for simple queries

#### `search_with_namespace_priority(self, query, current_namespace, include_cortex, min_confidence, limit)`

Search patterns with namespace priority boosting.

Priority ranking:
1. Current namespace patterns (highest priority)
2. Cortex core patterns (if include_cortex=True)
3. Other namespace patterns (lowest priority)

Args:
    query: Search query (FTS5 syntax)
    current_namespace: Current application context (e.g., 'KSESSIONS')
    include_cortex: Include CORTEX-core patterns (default True)
    min_confidence: Minimum confidence threshold
    limit: Maximum results

Returns:
    List of patterns with namespace-boosted ranking

Performance: <100ms

#### `get_patterns_by_namespace(self, namespace, min_confidence, limit)`

Get all patterns in a specific namespace.

Args:
    namespace: Namespace to filter by
    min_confidence: Minimum confidence threshold
    limit: Maximum results

Returns:
    List of patterns in the namespace

Performance: <30ms

#### `get_cortex_patterns(self, min_confidence, limit)`

Get all CORTEX core patterns.

Args:
    min_confidence: Minimum confidence threshold
    limit: Maximum results

Returns:
    List of CORTEX-core patterns

#### `get_application_patterns(self, namespace, min_confidence, limit)`

Get application-specific patterns (non-CORTEX).

Args:
    namespace: Application namespace (e.g., 'KSESSIONS')
    min_confidence: Minimum confidence threshold
    limit: Maximum results

Returns:
    List of application patterns

---

## src.tier2.knowledge_graph.patterns.pattern_store

Pattern Store Module

Handles all pattern storage operations including:
- Pattern creation and persistence
- Pattern retrieval by ID
- Pattern updates
- Pattern deletion (with cascade)
- Batch operations

Responsibilities (Single Responsibility Principle):
    - CRUD operations for patterns
    - Confidence score management
    - Access tracking (last_accessed, access_count)
    - Pattern validation

Performance Targets:
    - Pattern storage: <20ms
    - Pattern retrieval by ID: <10ms
    - Batch insert (100 patterns): <200ms

Example:
    >>> from tier2.knowledge_graph.patterns.pattern_store import PatternStore
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> 
    >>> db = DatabaseConnection()
    >>> store = PatternStore(db)
    >>> 
    >>> pattern = store.store_pattern(
    ...     title="TDD Workflow",
    ...     content="Always write tests first",
    ...     pattern_type="workflow",
    ...     confidence=0.95
    ... )

### PatternType

Pattern classification types.

### PatternStore

Manages pattern storage operations for Knowledge Graph.

This class handles all CRUD operations for patterns, ensuring data
integrity and proper confidence score management.

Attributes:
    db: DatabaseConnection instance for database access

Methods:
    store_pattern: Create new pattern or update existing
    get_pattern: Retrieve pattern by ID
    update_pattern: Modify existing pattern
    delete_pattern: Remove pattern (with cascade)
    list_patterns: Query patterns with filters

**Methods:**

#### `store_pattern(self, pattern_id, title, content, pattern_type, confidence, source, metadata, is_pinned, scope, namespaces, is_cortex_internal)`

Store a new pattern in the Knowledge Graph with namespace protection.

Args:
    pattern_id: Unique identifier for the pattern
    title: Pattern title (human-readable)
    content: Pattern description/content
    pattern_type: Type of pattern (workflow, principle, etc.)
    confidence: Confidence score (0.0-1.0)
    source: Source of the pattern (optional)
    metadata: Additional metadata as dict (optional)
    is_pinned: Whether pattern is pinned (immune to decay)
    scope: 'cortex' or 'application' (boundary enforcement)
    namespaces: List of namespace tags (default: ["CORTEX-core"])
    is_cortex_internal: True if called from CORTEX framework code

Returns:
    Dictionary with stored pattern data including generated ID

Raises:
    ValueError: If validation fails or namespace protection violated
    sqlite3.IntegrityError: If pattern_id already exists

Performance: ~20ms

#### `get_pattern(self, pattern_id)`

Retrieve a pattern by ID.

Args:
    pattern_id: Pattern identifier

Returns:
    Pattern data as dictionary, or None if not found

Side Effects:
    - Updates last_accessed timestamp
    - Increments access_count

Performance: ~10ms

#### `update_pattern(self, pattern_id, updates)`

Update an existing pattern.

Args:
    pattern_id: Pattern to update
    updates: Dictionary of fields to update

Returns:
    True if updated, False if pattern not found

Allowed Updates:
    - title, content, confidence, metadata, is_pinned

Protected Fields (cannot update):
    - pattern_id, created_at, pattern_type

Performance: ~15ms

#### `delete_pattern(self, pattern_id)`

Delete a pattern (cascade deletes relationships and tags).

Args:
    pattern_id: Pattern to delete

Returns:
    True if deleted, False if pattern not found

Cascade Deletes:
    - pattern_relationships (both directions)
    - pattern_tags

Performance: ~25ms

#### `list_patterns(self, pattern_type, scope, min_confidence, limit)`

List patterns with optional filters.

Args:
    pattern_type: Filter by pattern type
    scope: Filter by scope ('cortex' or 'application')
    min_confidence: Minimum confidence threshold
    limit: Maximum number of results

Returns:
    List of pattern dictionaries

Performance: ~30ms for 100 patterns

---

## src.tier2.knowledge_graph.relationships.__init__

Relationship management modules for Knowledge Graph.

---

## src.tier2.knowledge_graph.relationships.relationship_manager

Relationship Manager Module

Manages pattern-to-pattern relationships (graph edges).

Relationship Types:
    - extends: Pattern B extends Pattern A
    - relates_to: General relationship
    - contradicts: Patterns conflict
    - supersedes: New pattern replaces old

Responsibilities:
    - Create relationships with validation
    - Query relationships (incoming/outgoing)
    - Update relationship strength
    - Delete relationships
    - Detect circular relationships

Performance Targets:
    - Create relationship: <15ms
    - Query relationships: <30ms
    - Graph traversal (depth=3): <150ms

Example:
    >>> from tier2.knowledge_graph.relationships.relationship_manager import RelationshipManager
    >>> rel_mgr = RelationshipManager(db)
    >>> rel_mgr.create_relationship(
    ...     from_pattern="tdd-basic",
    ...     to_pattern="tdd-advanced",
    ...     relationship_type="extends",
    ...     strength=0.9
    ... )

### RelationshipType

Pattern relationship types.

### RelationshipManager

Manages pattern relationships (graph edges).

Handles creation, retrieval, and validation of relationships
between patterns in the knowledge graph.

**Methods:**

#### `create_relationship(self, from_pattern, to_pattern, relationship_type, strength)`

Create a relationship between two patterns.

Args:
    from_pattern: Source pattern ID
    to_pattern: Target pattern ID
    relationship_type: Type of relationship
    strength: Relationship strength (0.0-1.0)

Returns:
    Dictionary with relationship data

Raises:
    ValueError: If validation fails
    sqlite3.IntegrityError: If relationship already exists

Validation:
    - Both patterns must exist
    - Cannot relate pattern to itself
    - Strength must be 0.0-1.0

Performance: <15ms

#### `get_relationships(self, pattern_id, direction)`

Get all relationships for a pattern.

Args:
    pattern_id: Pattern to query
    direction: "outgoing", "incoming", or "both"

Returns:
    List of relationship dictionaries

Performance: <30ms

#### `traverse_graph(self, start_pattern, max_depth, relationship_types)`

Traverse the pattern graph from a starting point.

Args:
    start_pattern: Starting pattern ID
    max_depth: Maximum traversal depth
    relationship_types: Filter by relationship types

Returns:
    Dictionary with:
        - nodes: List of pattern IDs reached
        - edges: List of relationships traversed
        - paths: List of paths from start to each node

Performance: <150ms for depth=3

---

## src.tier2.knowledge_graph.tags.__init__

Tag management modules for Knowledge Graph.

---

## src.tier2.knowledge_graph.tags.tag_manager

Tag Manager Module

Manages pattern tags for organization and filtering.

Tag Features:
    - Many-to-many pattern-tag associations
    - Tag-based filtering and search
    - Tag popularity tracking
    - Namespace-aware tag queries

Responsibilities:
    - Add/remove tags from patterns
    - Query patterns by tags
    - List all tags with counts
    - Tag validation and normalization

Performance Targets:
    - Add tag: <10ms
    - Query by tag: <40ms
    - List all tags: <30ms

Example:
    >>> from tier2.knowledge_graph.tags.tag_manager import TagManager
    >>> tag_mgr = TagManager(db)
    >>> tag_mgr.add_tag("tdd-pattern-001", "testing")
    >>> tag_mgr.add_tag("tdd-pattern-001", "best-practice")
    >>> patterns = tag_mgr.get_patterns_by_tag("testing")

### TagManager

Manages pattern tags for organization.

Provides tag-based organization and filtering for patterns
in the knowledge graph.

**Methods:**

#### `add_tag(self, pattern_id, tag)`

Add a tag to a pattern.

Args:
    pattern_id: Pattern to tag
    tag: Tag string (normalized to lowercase)

Returns:
    True if added, False if already exists

Tag Normalization:
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters

Performance: <10ms

#### `remove_tag(self, pattern_id, tag)`

Remove a tag from a pattern.

Args:
    pattern_id: Pattern to untag
    tag: Tag to remove

Returns:
    True if removed, False if tag didn't exist

Performance: <10ms

#### `get_tags(self, pattern_id)`

Get all tags for a pattern.

Args:
    pattern_id: Pattern to query

Returns:
    List of tag strings

Performance: <15ms

#### `get_patterns_by_tag(self, tag, min_confidence, limit)`

Find patterns with a specific tag.

Args:
    tag: Tag to search for
    min_confidence: Minimum confidence filter
    limit: Maximum results

Returns:
    List of pattern dictionaries

Performance: <40ms

#### `list_all_tags(self)`

List all tags with usage counts.

Returns:
    List of dictionaries with:
        - tag: Tag string
        - count: Number of patterns with this tag

Sorted by count (descending)

Performance: <30ms

---

## src.tier2.knowledge_graph.types

Knowledge Graph Shared Types

Contains common data types used across knowledge graph modules.

### PatternType

Pattern classification types.

### RelationshipType

Pattern relationship types.

### Pattern

Pattern data structure.

---

## src.tier2.knowledge_graph_legacy

CORTEX Tier 2: Knowledge Graph
Long-term memory with FTS5 semantic search and pattern relationships.

### PatternType

Pattern classification types.

### RelationshipType

Pattern relationship types.

### Pattern

Pattern data structure.

### KnowledgeGraph

Knowledge Graph (Tier 2): Long-term pattern storage with FTS5 search.

Features:
- SQLite + FTS5 for semantic search
- Pattern relationships (graph structure)
- Confidence decay based on access patterns
- Tag-based organization
- BM25 ranking for search results

Performance:
- Search queries: <150ms
- Pattern retrieval: <50ms
- Relationship traversal: <100ms

**Methods:**

#### `add_pattern(self, pattern_id, title, content, pattern_type, confidence, scope, namespaces, tags, source, metadata)`

Add a new pattern to the knowledge graph.

#### `get_pattern(self, pattern_id)`

Retrieve a pattern by ID and update access timestamp.

Args:
    pattern_id: Pattern identifier

Returns:
    Pattern object or None if not found

#### `update_pattern(self, pattern_id, title, content, confidence, metadata)`

Update pattern properties.

Args:
    pattern_id: Pattern to update
    title: New title (optional)
    content: New content (optional)
    confidence: New confidence (optional)
    metadata: New metadata (optional)

Returns:
    True if updated, False if pattern not found

#### `delete_pattern(self, pattern_id)`

Delete a pattern from the knowledge graph.

Args:
    pattern_id: Pattern to delete

Returns:
    True if deleted, False if not found

#### `get_patterns_by_type(self, pattern_type)`

Get all patterns of a specific type.

Args:
    pattern_type: Type to filter by

Returns:
    List of Pattern objects

#### `search_patterns(self, query, limit)`

Search patterns using FTS5 full-text search with BM25 ranking.

Supports:
- Simple keywords: "testing"
- Phrase search: '"test driven development"'
- Boolean: "testing AND refactoring"
- Prefix: "refactor*"
- NOT: "testing NOT manual"

Args:
    query: Search query (FTS5 syntax)
    limit: Maximum results to return

Returns:
    List of Pattern objects, ranked by relevance

#### `search_patterns_with_namespace(self, query, current_namespace, include_generic, limit)`

Search patterns with namespace boosting for context-aware results.

Priority ranking:
1. Current namespace patterns (weight 2.0)
2. Generic patterns (weight 1.5 if include_generic=True)
3. Other namespace patterns (weight 0.5)

Args:
    query: Search query (FTS5 syntax)
    current_namespace: Current application context (e.g., 'KSESSIONS')
    include_generic: Include generic CORTEX patterns (default True)
    limit: Maximum results to return

Returns:
    List of Pattern objects, ranked by relevance and namespace priority

#### `get_patterns_by_namespace(self, namespace)`

Get all patterns for a specific namespace.

Args:
    namespace: Namespace to filter by (e.g., 'KSESSIONS', 'CORTEX-core')

Returns:
    List of Pattern objects in the namespace

#### `get_generic_patterns(self)`

Get all generic (CORTEX core) patterns.

Returns:
    List of Pattern objects with scope='cortex'

#### `get_application_patterns(self)`

Get all application-specific patterns.

Returns:
    List of Pattern objects with scope='application'

#### `link_patterns(self, from_pattern, to_pattern, relationship_type, strength)`

Create a relationship between two patterns.

Args:
    from_pattern: Source pattern ID
    to_pattern: Target pattern ID
    relationship_type: Type of relationship
    strength: Relationship strength (0.0 to 1.0)

Returns:
    True if created, False if already exists

#### `get_related_patterns(self, pattern_id, max_depth, min_strength)`

Get patterns related to a given pattern (graph traversal).

Args:
    pattern_id: Starting pattern
    max_depth: Maximum traversal depth
    min_strength: Minimum relationship strength

Returns:
    List of related Pattern objects

#### `apply_confidence_decay(self)`

Apply confidence decay to patterns based on access patterns.

Implements Governance Rule #12: Confidence Decay
- Patterns decay 1% per day after 60 days of no access
- Patterns below 0.3 confidence are deleted
- Pinned patterns are protected from decay

Returns:
    Dict with 'decayed_count' and 'deleted_count'

#### `pin_pattern(self, pattern_id)`

Pin a pattern to protect it from confidence decay.

Args:
    pattern_id: Pattern to pin

Returns:
    True if pinned, False if not found

#### `get_decay_log(self, pattern_id, limit)`

Get confidence decay history.

Args:
    pattern_id: Filter by pattern (optional)
    limit: Maximum entries to return

Returns:
    List of decay log entries

#### `get_pattern_tags(self, pattern_id)`

Get all tags for a pattern.

Args:
    pattern_id: Pattern identifier

Returns:
    List of tag strings

#### `find_patterns_by_tag(self, tag)`

Find all patterns with a specific tag.

Args:
    tag: Tag to search for

Returns:
    List of Pattern objects

#### `get_tag_cloud(self, limit)`

Get tag frequency statistics (tag cloud).

Args:
    limit: Maximum tags to return

Returns:
    List of dicts with 'tag' and 'count'

#### `close(self)`

Close any open database connections.

---

## src.tier2.migrate_add_boundaries

CORTEX Tier 2: Schema Migration - Add Namespace/Scope Boundaries

This migration adds the knowledge boundary system to enforce impenetrable
separation between CORTEX core intelligence (generic) and application-specific
knowledge (KSESSIONS, NOOR, etc.).

Changes:
1. Add `scope` column: 'generic' (CORTEX) vs 'application' (apps)
2. Add `namespaces` column: JSON array supporting multi-app patterns
3. Create indexes for performance
4. Classify existing patterns based on content/source
5. Create rollback backup before migration

Usage:
    python CORTEX/src/tier2/migrate_add_boundaries.py [--dry-run] [--db-path PATH]

Args:
    --dry-run: Show what would be done without making changes
    --db-path: Path to database (default: cortex-brain/tier2/knowledge_graph.db)

### BoundaryMigration

Handles schema migration for namespace/scope boundaries.

**Methods:**

#### `create_backup(self)`

Create backup of database before migration.

Returns:
    Path to backup file

#### `classify_pattern(self, pattern_id, title, content, source)`

Classify pattern as generic or application-specific.

Rules:
1. Source from simulations/ → application, namespace from path
2. Contains application paths → application, extract namespace
3. Generic workflow/governance keywords → generic, CORTEX-core
4. Protection/tier patterns → generic, CORTEX-core
5. Default: generic if uncertain

Args:
    pattern_id: Pattern identifier
    title: Pattern title
    content: Pattern content
    source: Pattern source

Returns:
    Tuple of (scope, namespaces)
    - scope: 'generic' or 'application'
    - namespaces: List of namespace strings

#### `get_existing_patterns(self)`

Retrieve all existing patterns for classification.

Returns:
    List of pattern dicts with id, title, content, source

#### `execute_migration(self)`

Execute the migration.

Returns:
    Migration statistics

#### `print_summary(self, stats)`

Print migration summary.

### `main()`

Main migration entry point.

---

## src.tier2.migrate_tier2

CORTEX Tier 2 Migration Script
Migrates knowledge graph data from YAML to SQLite with FTS5

Task 0.5.2: Tier 2 Migration Script
Duration: 1-1.5 hours

### Tier2Migrator

Migrates Tier 2 knowledge graph from YAML to SQLite with FTS5

**Methods:**

#### `create_schema(self, conn)`

Create Tier 2 database schema with FTS5

#### `migrate_validation_insights(self, conn, insights)`

Migrate validation_insights section

#### `migrate_workflow_patterns(self, conn, workflows)`

Migrate workflow_patterns section

#### `migrate_intent_patterns(self, conn, intents)`

Migrate intent_patterns section

#### `migrate_file_relationships(self, conn, relationships)`

Migrate file_relationships section

#### `migrate(self)`

Execute migration from YAML to SQLite

Returns:
    Migration statistics dictionary

### `main()`

---

## src.tier2.oracle_crawler

Oracle Database Schema Crawler for CORTEX Knowledge Extraction

This crawler connects to Oracle databases, extracts schema metadata (tables, columns,
relationships, indexes), and stores them as knowledge patterns in Tier 2 knowledge graph.

CORTEX Tier 2 Integration:
- Scope: 'application' (database schemas are application-specific)
- Namespace: Database name (e.g., ['KSESSIONS_DB'])
- Pattern Title: "Oracle: {table_name} schema"
- Confidence: 0.95 (high confidence from direct schema introspection)

Usage:
    crawler = OracleCrawler(connection_string="user/pass@host:port/service")
    patterns = crawler.extract_schema()
    crawler.store_patterns(patterns, knowledge_graph)

### OracleTable

Represents an Oracle table with metadata.

### OracleColumn

Represents a table column.

### OracleIndex

Represents a table index.

### OracleConstraint

Represents a table constraint.

### OracleCrawler

Extracts schema metadata from Oracle databases.

Architecture:
- Uses oracledb (python-oracledb) for connectivity
- Queries data dictionary views (ALL_TABLES, ALL_TAB_COLUMNS, etc.)
- Converts metadata to CORTEX knowledge patterns
- Stores in Tier 2 with scope='application', namespace=[db_name]

**Methods:**

#### `connect(self)`

Establish connection to Oracle database.

#### `disconnect(self)`

Close Oracle connection.

#### `extract_schema(self, owners, include_system)`

Extract schema metadata from Oracle.

Args:
    owners: List of schema owners to extract (default: current user)
    include_system: Include Oracle system schemas (SYS, SYSTEM, etc.)

Returns:
    List of OracleTable objects with full metadata

#### `table_to_pattern(self, table)`

Convert OracleTable to CORTEX knowledge pattern.

Pattern Structure:
- Title: "Oracle: {owner}.{table_name} schema"
- Content: Detailed JSON with columns, indexes, constraints
- Scope: 'application' (database-specific)
- Namespace: [database_name]
- Tags: ['oracle', 'database', 'schema', owner, table_name]
- Confidence: 0.95 (high - direct introspection)

#### `store_patterns(self, tables, knowledge_graph)`

Store extracted schema as knowledge patterns in Tier 2.

Args:
    tables: List of OracleTable objects from extract_schema()
    knowledge_graph: KnowledgeGraph instance for storage

Returns:
    Number of patterns stored

---

## src.tier2.pattern_cleanup

CORTEX Tier 2: Pattern Cleanup System
Automated maintenance for knowledge graph patterns.

Features:
- Confidence decay for unused patterns
- Pattern consolidation (merge similar patterns)
- Scope-aware protection (never touch generic/CORTEX-core)
- Stale pattern detection and removal

### CleanupStats

Statistics from cleanup operations.

**Methods:**

### PatternCleanup

Pattern Cleanup System for automated knowledge graph maintenance.

Key Principles:
- NEVER modify scope='cortex' patterns (CORTEX core protection)
- NEVER modify patterns in CORTEX-core namespace
- Only affect application-specific patterns
- Respect confidence thresholds
- Log all cleanup actions for audit trail

**Methods:**

#### `apply_automatic_decay(self, protect_generic)`

    Apply confidence decay to application patterns only.
    
    Rules:
- Generic patterns (scope='cortex') NEVER decay
    - CORTEX-core namespace patterns NEVER decay
    - Application patterns decay 1% per day after 30 days
    - Patterns below 0.3 confidence are deleted
    - Pinned patterns are protected
    
    Args:
        protect_generic: If True, skip all scope='cortex' patterns (default: True)
    
    Returns:
        CleanupStats with decayed and deleted counts
    

#### `consolidate_similar_patterns(self, namespace, dry_run)`

Merge similar patterns to reduce duplication.

Rules:
- Only consolidate patterns with same scope and overlapping namespaces
- Never consolidate generic patterns (they're immutable)
- Preserve highest confidence and most recent evidence
- Combine access counts
- Keep all tags

Args:
    namespace: Limit consolidation to specific namespace (optional)
    dry_run: If True, report what would be consolidated without changes

Returns:
    CleanupStats with consolidated count

#### `remove_stale_patterns(self, stale_days, protect_generic)`

Remove patterns not accessed in a long time.

Args:
    stale_days: Days of inactivity to consider stale (default: 90)
    protect_generic: Never remove generic patterns (default: True)

Returns:
    CleanupStats with deleted count

#### `optimize_database(self)`

Optimize database performance.

- Run VACUUM to reclaim space
- Rebuild FTS5 index
- Analyze query performance

Returns:
    True if successful, False otherwise

#### `get_cleanup_recommendations(self)`

Analyze patterns and recommend cleanup actions.

Returns:
    Dict with recommendations for decay, consolidation, deletion

---

## src.tier2.personal_knowledge_archive

CORTEX Knowledge Archive - Personal Cross-Project Learning System

Your personal archive of proven solutions across all projects.

This module manages your knowledge archive - a persistent memory of:
- Successful patterns you've used
- Mistakes you've learned from (anti-patterns)
- PR decisions and their outcomes
- Solutions that worked (and didn't work)

Think of it as "collaborating with Future You" - capture knowledge once,
reuse it forever across all your projects.

### ArchivedPattern

Represents a proven pattern from your past work

**Methods:**

### ArchivedAntiPattern

Represents a mistake you've learned from (what NOT to do)

**Methods:**

### CortexKnowledgeArchive

Your Personal Knowledge Archive - Learn Once, Use Forever

Features:
- Archive successful patterns from your projects
- Remember mistakes you've made (anti-patterns)
- Search across all your past work
- Track what worked and what didn't
- Cross-project pattern reuse

Benefits:
- Never rediscover the same solution twice
- Avoid repeating past mistakes
- Build your personal "second brain"
- Accelerate future work with proven patterns

**Methods:**

#### `add_pattern(self, pattern)`

Archive a successful pattern for future reference

#### `add_antipattern(self, antipattern)`

Archive a mistake you've learned from

#### `search_patterns(self, query, pattern_type, limit)`

Search your archived patterns using full-text search.
Returns patterns sorted by relevance and confidence.

#### `get_pattern(self, pattern_id)`

Get a specific archived pattern by ID

#### `increment_pattern_usage(self, pattern_id, success)`

Track when you reuse a pattern (and whether it worked)

#### `get_archive_statistics(self)`

Get statistics about your knowledge archive

#### `add_project(self, project_id, project_name)`

Register a project in your archive

#### `update_project_stats(self, project_id)`

Update project statistics

---

## src.tier2.plan_models

### Meta

### Artifacts

### PlanLedgerEntry

**Methods:**

### PlanLedger

**Methods:**

### FeaturePlan

### ArchitecturePlan

### RefactorPlan

### ActivePlans

### Decision

**Methods:**

### DecisionGraph

### ReasoningChainEntry

**Methods:**

### RequiredTests

### TestAlignmentItem

### TestAlignment

### PlanForecast

**Methods:**

### MetricsForecast

---

## src.tier3.__init__

CORTEX Tier 3: Development Context Intelligence

Real-time project intelligence providing data-driven planning and proactive warnings.

---

## src.tier3.analysis.__init__

CORTEX Tier 3: Analysis Modules

---

## src.tier3.analysis.insight_generator

CORTEX Tier 3: Insight Generation
Generates actionable insights from collected metrics.

### InsightType

Types of insights that can be generated.

### Severity

Severity levels for insights.

### Insight

Generated insights and recommendations.

**Methods:**

### InsightGenerator

Generates insights from metrics.

Features:
- Velocity drop detection
- File hotspot identification
- Productivity pattern analysis
- Actionable recommendations

**Methods:**

#### `generate_insights(self)`

Generate insights from collected metrics.

Returns:
    List of Insight objects

#### `get_productivity_insights(self, days)`

Generate productivity-focused insights.

Args:
    days: Number of days to analyze
    
Returns:
    List of Insight objects focused on productivity

#### `get_file_health_insights(self)`

Generate file health insights.

Returns:
    List of Insight objects focused on file health

---

## src.tier3.analysis.velocity_analyzer

CORTEX Tier 3: Velocity Analysis
Analyzes commit velocity trends and detects productivity patterns.

### VelocityAnalyzer

Analyzes commit velocity trends and productivity patterns.

Features:
- Commit velocity calculation
- Trend analysis (increasing/stable/declining)
- Productivity pattern detection
- Historical comparisons

**Methods:**

#### `calculate_velocity(self, window_days)`

Calculate commit velocity trends.

Args:
    window_days: Number of days per window
    
Returns:
    Dictionary with velocity metrics and trend analysis

#### `get_productivity_summary(self, days)`

Get productivity summary for a period.

Args:
    days: Number of days to analyze
    
Returns:
    Dictionary with productivity metrics

#### `get_daily_breakdown(self, days)`

Get daily breakdown of commits.

Args:
    days: Number of days to include
    
Returns:
    List of dictionaries with daily metrics

---

## src.tier3.context_intelligence

CORTEX Tier 3: Development Context Intelligence
Part 1: Imports, Enums, and Data Classes

### InsightType

Types of insights that can be generated.

### Severity

Severity levels for insights.

### Stability

File stability classification.

### TestType

Types of tests tracked.

### IntentType

CORTEX intent types.

### GitMetric

Daily git activity metrics.

### FileHotspot

File churn analysis.

### TestMetric

Daily test execution metrics.

### FlakyTest

Flaky test tracking.

### BuildMetric

Daily build metrics.

### WorkPattern

Work session patterns.

### CortexUsage

CORTEX usage metrics.

### Correlation

Correlation between metrics.

### Insight

Generated insights and recommendations.

**Methods:**

### ContextIntelligence

Tier 3: Development Context Intelligence

Provides real-time project analytics including:
- Git activity tracking and commit velocity
- File hotspot detection and churn analysis
- Test metrics and flaky test detection
- Build health monitoring
- Work pattern analysis
- CORTEX usage effectiveness
- Correlation discovery and insights

Performance targets:
- Context queries: <10ms
- Database size: <50KB
- Update frequency: Delta updates (minimum 1 hour interval)

**Methods:**

#### `collect_git_metrics(self, repo_path, since, days)`

Collect git activity metrics with delta optimization.

Args:
    repo_path: Path to git repository (default: parent of cortex-brain)
    since: Only collect commits after this timestamp
    days: Number of days to collect (if since is None)
    
Returns:
    List of GitMetric objects

#### `save_git_metrics(self, metrics)`

Save git metrics to database.

#### `get_git_metrics(self, days, contributor)`

Retrieve git metrics from database.

Args:
    days: Number of days to retrieve
    contributor: Filter by contributor (None = all aggregated)
    
Returns:
    List of GitMetric objects

#### `analyze_file_hotspots(self, repo_path, days)`

Analyze file churn and identify unstable files with caching.

Cache TTL: 60 minutes (to avoid expensive git operations)

Args:
    repo_path: Path to git repository
    days: Analysis window in days
    
Returns:
    List of FileHotspot objects

#### `save_file_hotspots(self, hotspots)`

Save file hotspots to database.

#### `get_unstable_files(self, limit)`

Get most unstable files (highest churn rate).

Args:
    limit: Maximum number of files to return
    
Returns:
    List of FileHotspot objects

#### `calculate_commit_velocity(self, window_days)`

Calculate commit velocity trends.

Args:
    window_days: Number of days per window
    
Returns:
    Dictionary with velocity metrics and trend analysis

#### `generate_insights(self)`

Generate insights from collected metrics.

Returns:
    List of Insight objects

#### `get_context_summary(self)`

Get comprehensive context summary.

Returns:
    Dictionary with all context metrics

#### `update_all_metrics(self, repo_path, days)`

Update all metrics (git + file hotspots).

Args:
    repo_path: Path to git repository
    days: Number of days to analyze

---

## src.tier3.context_intelligence_legacy

CORTEX Tier 3: Development Context Intelligence
Part 1: Imports, Enums, and Data Classes

### InsightType

Types of insights that can be generated.

### Severity

Severity levels for insights.

### Stability

File stability classification.

### TestType

Types of tests tracked.

### IntentType

CORTEX intent types.

### GitMetric

Daily git activity metrics.

### FileHotspot

File churn analysis.

### TestMetric

Daily test execution metrics.

### FlakyTest

Flaky test tracking.

### BuildMetric

Daily build metrics.

### WorkPattern

Work session patterns.

### CortexUsage

CORTEX usage metrics.

### Correlation

Correlation between metrics.

### Insight

Generated insights and recommendations.

**Methods:**

### ContextIntelligence

Tier 3: Development Context Intelligence

Provides real-time project analytics including:
- Git activity tracking and commit velocity
- File hotspot detection and churn analysis
- Test metrics and flaky test detection
- Build health monitoring
- Work pattern analysis
- CORTEX usage effectiveness
- Correlation discovery and insights

Performance targets:
- Context queries: <10ms
- Database size: <50KB
- Update frequency: Delta updates (minimum 1 hour interval)

**Methods:**

#### `collect_git_metrics(self, repo_path, since, days)`

Collect git activity metrics with delta optimization.

Args:
    repo_path: Path to git repository (default: parent of cortex-brain)
    since: Only collect commits after this timestamp
    days: Number of days to collect (if since is None)
    
Returns:
    List of GitMetric objects

#### `save_git_metrics(self, metrics)`

Save git metrics to database.

#### `get_git_metrics(self, days, contributor)`

Retrieve git metrics from database.

Args:
    days: Number of days to retrieve
    contributor: Filter by contributor (None = all aggregated)
    
Returns:
    List of GitMetric objects

#### `analyze_file_hotspots(self, repo_path, days)`

Analyze file churn and identify unstable files.

Args:
    repo_path: Path to git repository
    days: Analysis window in days
    
Returns:
    List of FileHotspot objects

#### `save_file_hotspots(self, hotspots)`

Save file hotspots to database.

#### `get_unstable_files(self, limit)`

Get most unstable files (highest churn rate).

Args:
    limit: Maximum number of files to return
    
Returns:
    List of FileHotspot objects

#### `calculate_commit_velocity(self, window_days)`

Calculate commit velocity trends.

Args:
    window_days: Number of days per window
    
Returns:
    Dictionary with velocity metrics and trend analysis

#### `generate_insights(self)`

Generate insights from collected metrics.

Returns:
    List of Insight objects

#### `get_context_summary(self)`

Get comprehensive context summary.

Returns:
    Dictionary with all context metrics

#### `update_all_metrics(self, repo_path, days)`

Update all metrics (git + file hotspots).

Args:
    repo_path: Path to git repository
    days: Number of days to analyze

---

## src.tier3.metrics.__init__

CORTEX Tier 3: Metrics Collection Modules

---

## src.tier3.metrics.file_metrics

CORTEX Tier 3: File Metrics Analysis
Handles file hotspot detection and churn analysis.

### Stability

File stability classification.

### FileHotspot

File churn analysis.

### FileMetricsAnalyzer

Analyzes file churn and identifies unstable files.

Features:
- File edit frequency tracking
- Churn rate calculation
- Stability classification (STABLE/MODERATE/UNSTABLE)
- Hotspot detection

**Methods:**

#### `analyze_hotspots(self, repo_path, days)`

Analyze file churn and identify unstable files.

Args:
    repo_path: Path to git repository
    days: Analysis window in days
    
Returns:
    List of FileHotspot objects sorted by churn rate

#### `save_hotspots(self, hotspots)`

Save file hotspots to database.

Args:
    hotspots: List of FileHotspot objects to save

#### `get_hotspots(self, days, min_churn)`

Get file hotspots from database.

Args:
    days: Number of days to look back
    min_churn: Minimum churn rate to include
    
Returns:
    List of FileHotspot objects

#### `get_unstable_files(self, days)`

Get unstable files within time period.

Args:
    days: Number of days to look back
    
Returns:
    List of unstable FileHotspot objects

#### `get_hotspots_by_stability(self, stability, limit)`

Get files by stability classification.

Args:
    stability: Stability level to filter by
    limit: Maximum number of files to return
    
Returns:
    List of FileHotspot objects

---

## src.tier3.metrics.git_metrics

CORTEX Tier 3: Git Metrics Collection
Handles git activity tracking and commit velocity analysis.

### GitMetric

Daily git activity metrics.

### GitMetricsCollector

Collects git activity metrics with delta optimization.

Features:
- Collects commit counts, line changes, file modifications
- Per-contributor or aggregated metrics
- Delta updates (only collect new commits)
- Efficient subprocess-based git log parsing

**Methods:**

#### `collect_metrics(self, repo_path, since, days)`

Collect git activity metrics with delta optimization.

Args:
    repo_path: Path to git repository (default: workspace root)
    since: Only collect commits after this timestamp
    days: Number of days to collect (if since is None)
    
Returns:
    List of GitMetric objects

#### `save_metrics(self, metrics)`

Save git metrics to database.

Args:
    metrics: List of GitMetric objects to save

#### `get_metrics(self, days, contributor)`

Retrieve git metrics from database.

Args:
    days: Number of days to retrieve
    contributor: Filter by contributor (None = all aggregated)
    
Returns:
    List of GitMetric objects

---

## src.tier3.migrate_tier3

CORTEX Tier 3 Migration Script
Migrates development context from YAML to JSON (optimized structure)

Task 0.5.3: Tier 3 Migration Script
Duration: 30-45 minutes

### Tier3Migrator

Migrates Tier 3 development context from YAML to JSON

**Methods:**

#### `migrate(self)`

Execute migration from YAML to JSON

Returns:
    Migration statistics dictionary

### `main()`

---

## src.tier3.storage.__init__

CORTEX Tier 3: Storage Module

---

## src.tier3.storage.context_store

CORTEX Tier 3: Context Store
Handles database initialization and schema management.

### ContextStore

Manages context intelligence database schema and connections.

Features:
- Database initialization
- Schema creation and migration
- Index management
- Connection handling

**Methods:**

#### `get_connection(self)`

Get a database connection.

Returns:
    SQLite connection object

#### `vacuum(self)`

Vacuum the database to reclaim space and optimize performance.

#### `analyze(self)`

Analyze the database to update statistics for query optimization.

#### `get_database_size(self)`

Get database file size in bytes.

Returns:
    Size in bytes

#### `get_table_counts(self)`

Get row counts for all tables.

Returns:
    Dictionary of table names to row counts

---

## src.utils.incremental_test_runner

Incremental Test Runner for Large Test Suites

Runs pytest tests in small batches to provide visible progress feedback
and prevent apparent hangs with large test suites.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### IncrementalTestRunner

Runs pytest tests in batches with progress feedback.

**Methods:**

#### `collect_test_files(self)`

Collect all test files instead of individual tests.
This is simpler and faster than collecting individual test node IDs.

Returns:
    List of test file paths

#### `count_tests_in_files(self, files)`

Quick count of tests across files.

#### `run_batch(self, batch, batch_num, total_batches)`

Run a single batch of tests.

Args:
    batch: List of test node IDs to run
    batch_num: Current batch number (1-indexed)
    total_batches: Total number of batches
    
Returns:
    Dictionary with pass/fail/skip counts

#### `run_all(self)`

Run all tests in batches with progress feedback.
Works with test files as batches for simplicity.

Returns:
    Dictionary with total counts

#### `run_file_batch(self, files, batch_num, total_batches)`

Run a batch of test files, showing progress for each file.

Args:
    files: List of test file paths
    batch_num: Current batch number (1-indexed)
    total_batches: Total number of batches
    
Returns:
    Dictionary with pass/fail/skip counts

#### `get_summary_line(self)`

Get one-line summary for status updates.

### `main()`

CLI entry point for incremental test runner.

---

## src.utils.user_dictionary

CORTEX User Dictionary - Personalized Shortcut Management

Tracks user-defined shortcuts and abbreviations for natural conversation.

Features:
- Add new shortcuts with context
- Lookup shortcuts to expand
- List all shortcuts by category
- Track usage statistics
- Auto-save to YAML

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### UserDictionary

Manages user-defined shortcuts and abbreviations.

Example:
    >>> ud = UserDictionary()
    >>> ud.add_shortcut("EPM", "Entry Point Module", "architecture")
    >>> ud.lookup("EPM")
    "Entry Point Module"

**Methods:**

#### `add_shortcut(self, shortcut, full_term, category, description, context)`

Add a new shortcut to the dictionary.

Args:
    shortcut: The abbreviation (e.g., "EPM")
    full_term: The full term (e.g., "Entry Point Module")
    category: Category (architecture, operations, technical, user_specific)
    description: Optional description
    context: Optional usage context
    
Returns:
    True if added successfully, False if already exists

#### `lookup(self, shortcut, track_usage)`

Look up a shortcut and return the full term.

Args:
    shortcut: The abbreviation to look up
    track_usage: Whether to increment usage count
    
Returns:
    Full term if found, None otherwise

#### `get_details(self, shortcut)`

Get full details for a shortcut.

Args:
    shortcut: The abbreviation
    
Returns:
    Dictionary with all details, or None if not found

#### `list_shortcuts(self, category)`

List all shortcuts, optionally filtered by category.

Args:
    category: Optional category filter
    
Returns:
    List of (shortcut, full_term) tuples

#### `remove_shortcut(self, shortcut)`

Remove a shortcut from the dictionary.

Args:
    shortcut: The abbreviation to remove
    
Returns:
    True if removed, False if not found

#### `update_shortcut(self, shortcut, full_term, category, description, context)`

Update an existing shortcut.

Args:
    shortcut: The abbreviation to update
    full_term: New full term (optional)
    category: New category (optional)
    description: New description (optional)
    context: New context (optional)
    
Returns:
    True if updated, False if not found

#### `expand_text(self, text)`

Expand all shortcuts in a text string.

Args:
    text: Text containing shortcuts
    
Returns:
    Text with shortcuts expanded

#### `get_stats(self)`

Get usage statistics.

#### `print_summary(self)`

Print a formatted summary of the dictionary.

### `main()`

CLI entry point for testing.

---

## src.workflows.__init__

CORTEX Workflows Package

Workflow orchestrators:
- tdd_workflow.py: RED → GREEN → REFACTOR cycle
- feature_workflow.py: PLAN → EXECUTE → TEST
- bug_fix_workflow.py: DIAGNOSE → FIX → VERIFY (future)
- query_workflow.py: ANALYZE → SEARCH → RESPOND (future)

Version: 1.0

---

## src.workflows.checkpoint

CORTEX Workflow Checkpoint System

Provides checkpoint/resume capability for workflow execution,
allowing workflows to be resumed from last successful stage
after interruption or failure.

Author: CORTEX Development Team
Date: 2025-11-08
Version: 2.0.0

### CheckpointManager

Manages workflow checkpoints for resume capability

**Methods:**

#### `save(self, state)`

Save workflow state to checkpoint file

Args:
    state: Current workflow state
    
Returns:
    Path to checkpoint file

#### `load(self, workflow_id)`

Load workflow state from checkpoint

Args:
    workflow_id: Unique workflow identifier
    
Returns:
    Restored workflow state
    
Raises:
    FileNotFoundError: If checkpoint doesn't exist

#### `list_checkpoints(self)`

List all available checkpoints

Returns:
    List of checkpoint metadata dicts

#### `delete(self, workflow_id)`

Delete a checkpoint

Args:
    workflow_id: Workflow to delete
    
Returns:
    True if deleted, False if not found

#### `cleanup_old(self, days)`

Delete checkpoints older than specified days

Args:
    days: Age threshold in days
    
Returns:
    Number of checkpoints deleted

#### `get_resumable(self)`

Get list of checkpoints that can be resumed
(workflows that are incomplete)

Returns:
    List of resumable checkpoint metadata

### RollbackManager

Manages workflow rollback operations

**Methods:**

#### `rollback_to_stage(self, workflow_id, target_stage)`

Rollback workflow to a specific stage

Args:
    workflow_id: Workflow to rollback
    target_stage: Stage to rollback to
    
Returns:
    Modified workflow state ready to resume from target stage

#### `clear_failed_stages(self, workflow_id)`

Clear failed stages and reset to PENDING for retry

Args:
    workflow_id: Workflow to clear failures from
    
Returns:
    Modified workflow state

---

## src.workflows.feature_workflow

Feature Creation Workflow

Orchestrates complete feature creation:
- PLAN: Multi-phase breakdown via work-planner
- EXECUTE: Implement each phase with TDD
- TEST: Validate complete feature

Author: CORTEX Development Team
Version: 1.0

### FeatureCreationWorkflow

Feature Creation Workflow

Phases:
1. PLAN: Multi-phase breakdown (work-planner agent)
2. EXECUTE: Implement each phase with TDD
3. TEST: Validate complete feature

Integration:
- Uses work-planner (Phase 4: Strategic) for planning
- Uses TDD workflow for each phase execution
- Uses health-validator (Phase 4: Tactical) for validation

**Methods:**

#### `execute(self, feature_description, context)`

Execute feature creation workflow

Args:
    feature_description: User's feature request
    context: Injected context (Tiers 1-3)

Returns:
    {
        'status': 'success',
        'workflow': 'feature_creation',
        'plan': {
            'feature': 'Authentication',
            'phases': [
                {'phase': 1, 'name': 'User model', 'tasks': [...]},
                {'phase': 2, 'name': 'Login API', 'tasks': [...]}
            ],
            'estimated_hours': 8
        },
        'phases_completed': 2,
        'files_modified': ['path/to/file.py', ...],
        'tests_created': ['path/to/test.py', ...],
        'validation': {
            'passed': True,
            'checks': {...}
        }
    }

---

## src.workflows.stages.__init__

CORTEX Workflow Stages

Example stage implementations for testing and demonstration.

---

## src.workflows.stages.code_cleanup

Code Cleanup Stage

Performs code formatting, linting, and basic cleanup operations.

Author: CORTEX Development Team
Date: 2025-11-08

### CodeCleanup

Stage that performs code cleanup operations

Input Requirements:
    - state.stage_outputs['implement']: Implementation details with files
    OR
    - state.context: File paths to clean
    
Output:
    - files_cleaned: List of files cleaned
    - issues_fixed: List of issues fixed
    - cleanup_summary: Summary of cleanup operations

**Methods:**

#### `execute(self, state)`

Perform code cleanup

#### `validate_input(self, state)`

Validate input files or context available

---

## src.workflows.stages.doc_generator

Documentation Generator Stage

Generates or updates documentation based on implementation.

Author: CORTEX Development Team
Date: 2025-11-08

### DocGenerator

Stage that generates documentation

Input Requirements:
    - state.stage_outputs['implement']: Implementation details
    - state.user_request: Original request
    
Output:
    - documentation_files: List of documentation files created/updated
    - doc_sections: Sections added to documentation
    - doc_summary: Summary of documentation changes

**Methods:**

#### `execute(self, state)`

Generate documentation

#### `validate_input(self, state)`

Validate required inputs available

---

## src.workflows.stages.dod_dor_clarifier

DoD/DoR Clarification Stage

Clarifies Definition of Done and Definition of Ready with interactive prompts.

Author: CORTEX Development Team
Version: 1.0

### DoDCriteria

Definition of Done criteria

### DoRCriteria

Definition of Ready criteria

### DoDDoRClarifierStage

Clarify Definition of Done and Definition of Ready

Interactive stage that:
1. Presents DoD/DoR criteria to user
2. Asks for confirmation/clarification
3. Identifies missing information
4. Ensures work is "ready" before starting

**Methods:**

#### `execute(self, state)`

Execute DoD/DoR clarification

Args:
    state: Workflow state with user_request and threat model output

Returns:
    StageResult with clarified DoD/DoR

#### `validate_input(self, state)`

Validate state has user request

#### `on_failure(self, state, error)`

Log clarification failure

### `create_stage()`

Create DoD/DoR clarifier stage instance

---

## src.workflows.stages.threat_modeler

Threat Modeling Stage

Analyzes user request for security threats and risks using STRIDE model.

Author: CORTEX Development Team
Version: 1.0

### ThreatCategory

STRIDE threat categories

### Threat

Identified threat

**Methods:**

#### `risk_score(self)`

Calculate risk score (1-9)

### ThreatModelerStage

Threat modeling workflow stage

Analyzes user request for security threats using STRIDE:
- Spoofing: Authentication vulnerabilities
- Tampering: Data integrity issues
- Repudiation: Logging/audit gaps
- Information Disclosure: Data leakage
- Denial of Service: Resource exhaustion
- Elevation of Privilege: Access control issues

**Methods:**

#### `execute(self, state)`

Execute threat modeling

Args:
    state: Workflow state with user_request

Returns:
    StageResult with identified threats

#### `validate_input(self, state)`

Validate state has user request

#### `on_failure(self, state, error)`

Log threat modeling failure

### `create_stage()`

Create threat modeler stage instance

---

## src.workflows.tdd_workflow

TDD Workflow Orchestrator

Orchestrates RED → GREEN → REFACTOR TDD cycle (Rule #5):
- RED: Create failing test
- GREEN: Minimum implementation to pass
- REFACTOR: Improve code while keeping tests green

Author: CORTEX Development Team
Version: 1.0

### TDDWorkflow

TDD Workflow Orchestrator (Rule #5)

Orchestrates RED → GREEN → REFACTOR cycle

Phases:
1. RED: Create failing test
2. GREEN: Minimum implementation to pass
3. REFACTOR: Improve code while keeping tests green

Rule #5 Compliance:
- Tests MUST be written first (no implementation without tests)
- Tests MUST fail initially (RED phase validation)
- Implementation MUST make tests pass (GREEN phase validation)
- Refactoring MUST keep tests passing (REFACTOR phase validation)
- DoD MUST be validated (Rule #21)

**Methods:**

#### `execute(self, task, context)`

Execute TDD cycle for a task

Args:
    task: {
        'name': 'feature_name',
        'description': 'feature description',
        'files': ['path/to/file.py', ...] (optional)
    }
    context: Injected context from router (Tiers 1-3)

Returns:
    {
        'status': 'success',
        'cycle': 'RED → GREEN → REFACTOR',
        'phases': [
            {'phase': 'RED', 'status': 'RED', ...},
            {'phase': 'GREEN', 'status': 'GREEN', ...},
            {'phase': 'REFACTOR', 'status': 'REFACTORED', ...}
        ],
        'files_modified': [...],
        'tests_created': [...],
        'tests_passing': True,
        'dod_validated': True
    }

---

## src.workflows.workflow_engine

CORTEX Workflow Engine - DAG-based Workflow Orchestration

This module provides a declarative workflow pipeline system that allows
chaining tasks in any order with dependency management, state sharing,
checkpoint/resume, and context injection optimization.

Author: CORTEX Development Team
Date: 2025-11-08
Version: 2.0.0

### StageStatus

Status of a workflow stage

### StageResult

Result from executing a workflow stage

### WorkflowState

Shared state passed between workflow stages

**Methods:**

#### `get_stage_output(self, stage_id)`

Get output from a specific stage

#### `set_stage_output(self, stage_id, output)`

Set output for a specific stage

#### `set_stage_status(self, stage_id, status)`

Set status for a specific stage

#### `to_dict(self)`

Convert to dictionary for serialization

#### `from_dict(cls, data)`

Create WorkflowState from dictionary

### WorkflowStage

Protocol for workflow stages - defines the interface

**Methods:**

#### `execute(self, state)`

Execute the stage with given state

#### `validate_input(self, state)`

Validate inputs before execution

#### `on_failure(self, state, error)`

Handle stage failure

### StageDefinition

Definition of a workflow stage

### WorkflowDefinition

Definition of a complete workflow

**Methods:**

#### `from_yaml(cls, file_path)`

Load workflow definition from YAML file

#### `validate_dag(self)`

Validate workflow is a valid DAG (no cycles, all dependencies exist)

#### `get_execution_order(self)`

Get the order stages should be executed in

### WorkflowOrchestrator

Orchestrates workflow execution with DAG validation and state management

**Methods:**

#### `register_stage(self, stage_id, stage)`

Register a stage implementation

#### `execute(self, user_request, conversation_id, config)`

Execute the complete workflow

#### `resume(self, workflow_id)`

Resume a workflow from checkpoint

### BaseWorkflowStage

Base class for workflow stages with default implementations

**Methods:**

#### `execute(self, state)`

Override this in subclasses

#### `validate_input(self, state)`

Default: Always valid. Override if needed.

#### `on_failure(self, state, error)`

Default: Log error. Override if needed.

---

## src.workflows.workflow_pipeline

CORTEX Workflow Pipeline System

Orchestrates multi-stage workflows with:
- Declarative YAML definitions
- Dependency management (DAG validation)
- Shared state management
- Error recovery and retries
- Checkpoint/resume capability
- Context injection (Tier 1-3)

Author: CORTEX Development Team
Version: 1.0

### StageStatus

Stage execution status

### StageResult

Result from stage execution

### WorkflowState

Shared state passed between workflow stages

All stages read from and write to this state.
Persisted to disk for checkpoint/resume capability.

**Methods:**

#### `update_stage(self, result)`

Update state with stage result

#### `get_stage_output(self, stage_id)`

Get output from previous stage

#### `all_stages_before_completed(self, stage_id, dependencies)`

Check if all dependency stages completed successfully

### WorkflowStage

Interface that all workflow stages must implement

Each stage is a focused, single-responsibility script

**Methods:**

#### `execute(self, state)`

Execute this stage

Args:
    state: Shared workflow state

Returns:
    StageResult with outputs

#### `validate_input(self, state)`

Validate that state has required inputs for this stage

Returns:
    True if inputs valid

#### `on_failure(self, state, error)`

Handle stage failure (cleanup, logging)

Args:
    state: Current workflow state
    error: Exception that caused failure

### StageDefinition

Definition of a single stage in workflow

### WorkflowDefinition

Definition of complete workflow pipeline

**Methods:**

#### `from_yaml(cls, yaml_path)`

Load workflow definition from YAML file

#### `validate_dag(self)`

Validate workflow is a valid DAG (no cycles)

Returns:
    List of validation errors (empty if valid)

#### `get_execution_order(self)`

Get topological sort of stages (execution order)

Returns:
    List of stage IDs in execution order

### WorkflowOrchestrator

Orchestrates workflow execution with:
- Dependency management
- State persistence
- Error recovery
- Checkpoint/resume

**Methods:**

#### `register_stage(self, stage_id, stage_module)`

Register a stage implementation

#### `execute(self, user_request, conversation_id)`

Execute complete workflow pipeline

Args:
    user_request: User's original request
    conversation_id: Conversation UUID

Returns:
    Final workflow state

---

## tests.__init__

CORTEX Tests

---

## tests.agents.code_executor.__init__

Test package for code_executor modular components.

---

## tests.agents.error_corrector.__init__

Test package for modular ErrorCorrector agent.

---

## tests.agents.health_validator.__init__

Test package for health_validator modular components.

---

## tests.ambient.__init__

CORTEX 2.0 - Ambient Capture Tests

Test suite for ambient context capture daemon components.

Components tested:
- FileSystemWatcher: File change monitoring
- VSCodeMonitor: Editor state capture
- TerminalMonitor: Command detection
- GitMonitor: Git operation capture
- Debouncer: Event buffering and batching
- Integration: Full daemon lifecycle

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## tests.ambient.test_debouncer

CORTEX 2.0 - Debouncer Tests

Tests for event debouncing and batching.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestDebouncer

Test Debouncer component.

**Methods:**

#### `test_debouncer_initialization(self)`

Should initialize with default delay.

#### `test_custom_delay_initialization(self)`

Should initialize with custom delay.

#### `test_buffers_single_event(self)`

Should buffer events without immediate flush.

#### `test_buffers_multiple_events(self)`

Should buffer multiple events.

#### `test_resets_timer_on_new_event(self)`

Should reset timer when new event arrives.

#### `test_merges_duplicate_events(self)`

Should merge events for same file.

#### `test_does_not_merge_different_files(self)`

Should not merge events for different files.

#### `test_writes_to_tier1_on_flush(self, mock_wm_class)`

Should write events to Tier 1 on flush.

#### `test_concurrent_event_handling(self)`

Should handle concurrent events safely.

#### `test_clears_buffer_after_flush(self)`

Should clear buffer after successful flush.

---

## tests.ambient.test_file_watcher

CORTEX 2.0 - FileSystemWatcher Tests

Tests for file system monitoring component.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestFileSystemWatcher

Test FileSystemWatcher component.

**Methods:**

#### `temp_workspace(self)`

Create temporary workspace for testing.

#### `mock_callback(self)`

Create mock callback for event testing.

#### `test_watcher_initialization(self, temp_workspace, mock_callback)`

Should initialize watcher with valid workspace.

#### `test_rejects_invalid_workspace(self, mock_callback)`

Should reject non-existent workspace path.

#### `test_rejects_file_as_workspace(self, temp_workspace, mock_callback)`

Should reject file path (must be directory).

#### `test_detects_file_creation(self, temp_workspace, mock_callback)`

Should detect new file creation.

#### `test_detects_file_modification(self, temp_workspace, mock_callback)`

Should detect file modification.

#### `test_ignores_pycache_files(self, temp_workspace, mock_callback)`

Should ignore __pycache__ directory files.

#### `test_ignores_git_directory(self, temp_workspace, mock_callback)`

Should ignore .git directory files.

#### `test_only_watches_allowed_extensions(self, temp_workspace, mock_callback)`

Should only watch whitelisted file extensions.

#### `test_relative_paths_in_events(self, temp_workspace, mock_callback)`

Should use relative paths in event context.

#### `test_safe_path_validation(self, temp_workspace, mock_callback)`

Should validate paths are within workspace.

#### `test_event_contains_timestamp(self, temp_workspace, mock_callback)`

Should include timestamp in events.

### TestFileWatcherPatterns

Test pattern matching configuration.

**Methods:**

#### `test_watch_patterns_includes_common_extensions(self)`

Should watch common development file types.

#### `test_ignore_patterns_excludes_build_artifacts(self)`

Should ignore build artifacts and dependencies.

---

## tests.ambient.test_git_monitor

CORTEX 2.0 - GitMonitor Tests

Tests for git operation monitoring and hook installation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestGitMonitor

Test GitMonitor component.

**Methods:**

#### `git_repo(self, tmp_path)`

Create temporary git repository.

#### `mock_callback(self)`

Create mock callback for git events.

#### `test_monitor_initialization_with_git_repo(self, git_repo, mock_callback)`

Should initialize monitor with valid git repository.

#### `test_monitor_initialization_with_non_git_repo(self, tmp_path, mock_callback)`

Should handle non-git directory gracefully.

#### `test_rejects_non_existent_path(self, mock_callback)`

Should handle non-existent repository path gracefully.

#### `test_hook_types_whitelist(self, git_repo, mock_callback)`

Should only allow whitelisted hook types.

#### `test_installs_git_hooks(self, git_repo, mock_callback)`

Should install git hooks in .git/hooks directory.

#### `test_hook_script_uses_absolute_paths(self, git_repo, mock_callback)`

Should use absolute paths in hook scripts (prevent injection).

#### `test_backs_up_existing_hooks(self, git_repo, mock_callback)`

Should backup existing hooks before installing.

#### `test_skips_hook_install_if_capture_script_missing(self, git_repo, mock_callback)`

Should skip hook installation if capture script doesn't exist.

### TestGitHookSecurity

Test security aspects of git hook installation.

**Methods:**

#### `test_hook_permissions_are_restricted(self, tmp_path)`

Should set restrictive permissions on hooks (Unix-like).

#### `test_hook_script_has_no_variables(self, tmp_path)`

Should not use environment variables in hook script.

---

## tests.ambient.test_integration

CORTEX 2.0 - Ambient Capture Integration Tests

End-to-end tests for ambient capture daemon.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestAmbientCaptureDaemon

Test AmbientCaptureDaemon full lifecycle.

**Methods:**

#### `temp_workspace(self)`

Create temporary workspace with git repo.

#### `test_daemon_initialization(self, temp_workspace)`

Should initialize daemon with all components.

#### `test_git_hooks_installed_on_start(self, temp_workspace)`

Should install git hooks when daemon starts.

#### `test_captures_file_changes(self, mock_wm_class, temp_workspace)`

Should capture file changes to Tier 1.

#### `test_daemon_graceful_shutdown(self, temp_workspace)`

Should shutdown gracefully on signal.

#### `test_daemon_handles_missing_tier1_database(self, temp_workspace)`

Should handle missing Tier 1 database gracefully.

### TestVSCodeTasksIntegration

Test VS Code tasks.json integration.

**Methods:**

#### `test_tasks_json_contains_ambient_capture_task(self)`

Should have ambient capture task configured.

#### `test_stop_task_exists(self)`

Should have stop task configured.

### TestEndToEndCapture

Test end-to-end capture scenarios.

**Methods:**

#### `test_full_development_workflow_capture(self, mock_wm_class, tmp_path)`

Should capture multiple event types in realistic workflow.

#### `test_error_recovery_on_tier1_failure(self, tmp_path)`

Should continue working if Tier 1 write fails.

### TestPerformanceCharacteristics

Test performance characteristics of ambient capture.

**Methods:**

#### `test_debouncer_prevents_excessive_writes(self)`

Should batch events to prevent excessive Tier 1 writes.

#### `test_file_watcher_low_overhead(self, tmp_path)`

Should have minimal performance overhead.

---

## tests.ambient.test_terminal_monitor

CORTEX 2.0 - TerminalMonitor Tests

Tests for terminal command monitoring and sanitization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestTerminalMonitor

Test TerminalMonitor component.

**Methods:**

#### `mock_callback(self)`

Create mock callback for command testing.

#### `test_monitor_initialization(self, mock_callback)`

Should initialize monitor with callback.

#### `test_identifies_test_commands(self, mock_callback)`

Should identify test execution commands.

#### `test_identifies_build_commands(self, mock_callback)`

Should identify build commands.

#### `test_identifies_git_commands(self, mock_callback)`

Should identify git operations.

#### `test_sanitizes_passwords(self, mock_callback)`

Should redact passwords in commands.

#### `test_sanitizes_github_tokens(self, mock_callback)`

Should redact GitHub tokens.

#### `test_sanitizes_api_keys(self, mock_callback)`

Should redact API keys and tokens.

#### `test_blocks_malicious_rm_commands(self, mock_callback)`

Should block dangerous rm commands.

#### `test_blocks_eval_commands(self, mock_callback)`

Should block eval commands.

#### `test_blocks_fork_bombs(self, mock_callback)`

Should block fork bomb patterns.

#### `test_blocks_pipe_to_shell(self, mock_callback)`

Should block curl|sh and wget|bash patterns.

#### `test_allows_safe_commands(self, mock_callback)`

Should allow safe commands.

#### `test_rejects_oversized_commands(self, mock_callback)`

Should reject commands exceeding MAX_COMMAND_LENGTH.

#### `test_filters_meaningful_commands(self, mock_callback)`

Should only process meaningful commands.

### TestTerminalHistoryMonitoring

Test terminal history file monitoring.

**Methods:**

#### `test_validates_history_path_exists(self)`

Should validate history file exists.

#### `test_validates_history_path_is_file(self, tmp_path)`

Should validate history path is a file.

#### `test_validates_history_file_size(self, tmp_path)`

Should reject history files exceeding MAX_HISTORY_SIZE.

---

## tests.ambient.test_vscode_monitor

CORTEX 2.0 - VSCodeMonitor Tests

Tests for VS Code editor state monitoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestVSCodeMonitor

Test VSCodeMonitor component.

**Methods:**

#### `temp_workspace(self, tmp_path)`

Create temporary workspace with .vscode directory.

#### `test_monitor_initialization(self, temp_workspace)`

Should initialize monitor with valid workspace.

#### `test_get_open_files_with_valid_workspace(self, temp_workspace)`

Should parse workspace.json for open files.

#### `test_get_open_files_returns_empty_if_no_workspace(self, temp_workspace)`

Should return empty list if no workspace file.

#### `test_get_open_files_handles_invalid_json(self, temp_workspace)`

Should handle malformed JSON gracefully.

#### `test_get_open_files_limits_file_count(self, temp_workspace)`

Should limit number of files returned (max 100).

#### `test_rejects_oversized_workspace_file(self, temp_workspace)`

Should reject workspace files exceeding MAX_FILE_SIZE.

#### `test_sanitize_path_validates_workspace_boundary(self, temp_workspace)`

Should validate paths are within workspace.

#### `test_sanitize_path_handles_invalid_paths(self, temp_workspace)`

Should handle invalid path strings.

#### `test_get_active_file_returns_none(self, temp_workspace)`

Should return None (requires extension for full implementation).

### TestVSCodeStateValidation

Test VS Code state validation.

**Methods:**

#### `test_validates_json_structure(self, tmp_path)`

Should validate JSON has expected structure.

#### `test_validates_folder_entries(self, tmp_path)`

Should validate folder entries have 'path' property.

---

## tests.conftest

Pytest Configuration and Shared Fixtures

Provides common test fixtures for all CORTEX tests.

Copyright © 2024-2025 Asif Hussain. All rights reserved.

### MockAgent

Mock agent for testing BaseAgent functionality

**Methods:**

#### `can_handle(self, request)`

#### `execute(self, request)`

### MockTier1API

**Methods:**

#### `start_conversation(self, title)`

#### `process_message(self, conv_id, role, content)`

#### `get_conversation(self, conv_id)`

### MockKnowledgeGraph

**Methods:**

#### `search(self, query, limit)`

#### `add_pattern(self, pattern_type, title, content)`

#### `get_pattern(self, pattern_id)`

### MockContextIntelligence

**Methods:**

#### `get_context_summary(self)`

#### `update_all_metrics(self, days)`

#### `get_file_hotspots(self, limit)`

### `pytest_configure(config)`

Configure pytest with custom markers.

### `pytest_collection_modifyitems(config, items)`

Auto-skip tests based on missing dependencies.

### `sample_agent_request()`

Create a sample agent request for testing

### `sample_agent_response()`

Create a sample agent response for testing

### `mock_tier1_api()`

Mock Tier 1 API for agent testing

### `mock_tier2_kg()`

Mock Tier 2 Knowledge Graph for agent testing

### `mock_tier3_context()`

Mock Tier 3 Context Intelligence for agent testing

### `mock_tier_apis(mock_tier1_api, mock_tier2_kg, mock_tier3_context)`

Provide all three tier APIs together

### `mock_agent(mock_tier1_api, mock_tier2_kg, mock_tier3_context)`

Create a mock agent instance for testing

### `temp_db()`

Create a temporary database file with proper cleanup.

Uses in-memory database for parallel tests to avoid Windows file locking.
Falls back to temp file for tests that require file-based DB.

### `db_connection(temp_db)`

Create a SQLite database connection with proper cleanup.

### `in_memory_db()`

Create an in-memory database connection.

Preferred for unit tests to avoid file locking issues on Windows.

### `temp_brain(tmp_path)`

Create a temporary CORTEX brain directory structure.

Provides a complete brain directory with tier0/tier1/tier2/tier3 subdirs.
Used by integration tests that need full brain structure.

### `temp_workspace()`

Create a temporary workspace directory

### `sample_files(temp_workspace)`

Create sample files in workspace

### `monitor_test_performance(request)`

Monitor test execution time and warn on slow tests.

---

## tests.cortex-performance.generate-test-data

Generate realistic test data for sql.js performance benchmarking.

Creates a SQLite database with:
- 1000 conversations (simulating KDS conversation history)
- 3000 patterns (simulating extracted knowledge)
- Realistic data sizes and structures

Used in Phase -1 to validate sql.js performance assumptions.

### `create_schema(conn)`

Create CORTEX schema (Tier 1 + Tier 2).

### `generate_conversations(conn)`

Generate realistic conversation data.

### `generate_patterns(conn)`

Generate realistic pattern data.

### `generate_statistics(conn)`

Print database statistics.

### `main()`

Generate test database for sql.js benchmarking.

---

## tests.cortex_agents.strategic.test_interactive_planner

Unit Tests: Interactive Planner Agent Methods

Tests individual methods of InteractivePlannerAgent in isolation.
Part of CORTEX 2.1 Track B: Quality & Polish

### TestConfidenceDetection

Test confidence scoring algorithm.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_high_confidence_specific_request(self)`

Test that specific requests get high confidence.

#### `test_low_confidence_vague_request(self)`

Test that vague requests get low confidence.

#### `test_medium_confidence_moderate_request(self)`

Test that moderately specific requests get medium confidence.

#### `test_vague_terms_reduce_confidence(self)`

Test that vague terms reduce confidence score.

#### `test_specific_terms_increase_confidence(self)`

Test that technical terms increase confidence score.

#### `test_short_request_reduces_confidence(self)`

Test that very short requests get lower confidence.

#### `test_confidence_clamped_to_valid_range(self)`

Test that confidence is always in valid range.

### TestQuestionGeneration

Test question generation logic.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_generate_auth_questions(self)`

Test that authentication requests generate relevant questions.

#### `test_max_questions_limit(self)`

Test that question count is limited.

#### `test_questions_have_required_fields(self)`

Test that generated questions have all required fields.

### TestAnswerProcessing

Test answer processing logic.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_process_valid_answer(self)`

Test processing a valid answer.

#### `test_process_skipped_answer(self)`

Test processing a skipped answer.

#### `test_empty_string_not_treated_as_skip(self)`

Test that empty string answers are treated as valid (uses default).

### TestSessionManagement

Test session creation and management.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_create_session(self)`

Test session creation.

#### `test_session_timestamps(self)`

Test that session has proper timestamps.

### TestRoutingLogic

Test confidence-based routing decisions.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_high_confidence_routes_to_execute(self)`

Test that high confidence requests skip to execution.

#### `test_medium_confidence_routes_to_confirm(self)`

Test that medium confidence requests go to confirmation.

#### `test_low_confidence_routes_to_questioning(self)`

Test that low confidence requests trigger questions.

### TestAgentInterface

Test agent interface compliance.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_can_handle_plan_intent(self)`

Test that agent accepts PLAN intent.

#### `test_rejects_non_plan_intent(self)`

Test that agent rejects non-PLAN intents.

#### `test_execute_returns_agent_response(self)`

Test that execute returns proper AgentResponse.

---

## tests.cortex_brain_001.demo_fix_working

CORTEX-BRAIN-001 Fix Demo

Demonstrates the architectural analysis brain saving fix working end-to-end.
This simulates the KSESSIONS architecture analysis that was lost in the incident.

### `demonstrate_cortex_brain_001_fix()`

Demonstrate the CORTEX-BRAIN-001 architectural analysis brain saving fix.

---

## tests.cortex_brain_001.test_architecture_analysis_brain_saving

Test suite for CORTEX-BRAIN-001 fix: Architecture Analysis Brain Saving

Tests the complete workflow of architectural analysis with automatic brain saving:
1. Namespace detection logic
2. Automatic saving after analysis
3. User confirmation display
4. Cross-session recall

This addresses the critical incident where 30+ minutes of KSESSIONS architectural
analysis was lost due to missing automatic brain saving functionality.

### TestNamespaceDetection

Test namespace detection logic for architectural analysis.

**Methods:**

#### `knowledge_graph(self)`

Create a mock knowledge graph for testing.

#### `test_ksessions_architecture_detection(self, knowledge_graph)`

Test detection of KSESSIONS architecture namespace.

#### `test_ksessions_feature_detection(self, knowledge_graph)`

Test detection of KSESSIONS feature namespace.

#### `test_architectural_file_patterns(self, knowledge_graph)`

Test namespace detection based on architectural file patterns.

#### `test_generic_workspace_detection(self, knowledge_graph)`

Test detection for generic workspace (non-KSESSIONS).

#### `test_fallback_to_validation_insights(self, knowledge_graph)`

Test fallback to validation_insights when workspace unknown.

### TestArchitecturalAnalysisSaving

Test automatic saving of architectural analysis.

**Methods:**

#### `mock_kg(self)`

Create a mock knowledge graph with save functionality.

#### `architect_agent(self, mock_kg)`

Create ArchitectAgent with mocked dependencies.

#### `test_can_handle_architectural_requests(self, architect_agent)`

Test that ArchitectAgent recognizes architectural analysis requests.

#### `test_rejects_non_architectural_requests(self, architect_agent)`

Test that ArchitectAgent rejects non-architectural requests.

#### `test_automatic_brain_saving(self, architect_agent, mock_kg)`

Test that architectural analysis is automatically saved to brain.

#### `test_save_metadata_includes_request_context(self, architect_agent, mock_kg)`

Test that save metadata includes request context.

#### `test_handles_save_failure_gracefully(self, architect_agent, mock_kg)`

Test graceful handling when brain save fails.

### TestIntentRouting

Test that architectural analysis requests are properly routed.

**Methods:**

#### `test_architectural_keywords_route_to_architect(self)`

Test that architectural keywords route to ArchitectAgent.

### TestAgentExecutor

Test the AgentExecutor properly handles ArchitectAgent execution.

**Methods:**

#### `mock_tier2_kg(self)`

Mock Tier 2 Knowledge Graph.

#### `agent_executor(self, mock_tier2_kg)`

Create AgentExecutor with mocked dependencies.

#### `test_creates_architect_agent_on_demand(self, agent_executor)`

Test that AgentExecutor creates ArchitectAgent when needed.

#### `test_executes_architect_for_routing_decision(self, agent_executor, mock_tier2_kg)`

Test execution of ArchitectAgent based on routing decision.

### TestCrossSessionRecall

Test that architectural analysis can be recalled across sessions.

**Methods:**

#### `test_analysis_persisted_in_knowledge_graph(self)`

Test that analysis is properly stored for cross-session recall.

### TestEndToEndWorkflow

Integration tests for the complete CORTEX-BRAIN-001 fix workflow.

**Methods:**

#### `test_complete_architectural_analysis_workflow(self)`

Test the complete workflow from request to brain save.

#### `test_ksessions_specific_analysis(self)`

Test analysis of actual KSESSIONS architecture.

---

## tests.cortex_brain_001.test_namespace_detection

Unit tests for namespace detection functionality

Tests the core namespace detection logic added to fix CORTEX-BRAIN-001
without requiring full integration setup.

### TestNamespaceDetectionLogic

Test the namespace detection logic in isolation.

**Methods:**

#### `test_ksessions_architecture_patterns(self)`

Test KSESSIONS architecture detection patterns.

#### `test_file_pattern_detection(self)`

Test that architectural files trigger architecture namespace.

### TestSaveConfirmationFormatting

Test the save confirmation message formatting.

**Methods:**

#### `test_confirmation_message_structure(self)`

Test that confirmation messages have the right structure.

#### `test_different_namespace_formats(self)`

Test confirmation for different namespace formats.

---

## tests.docs.test_css_fixes

Tests for CSS styling fixes on documentation site.

Validates that:
1. Page title "Welcome to CORTEX" has proper dark color
2. No black bar appears on left sidebar
3. Styles persist after MkDocs rebuild

### TestCSSFixes

Test suite for MkDocs CSS styling fixes.

**Methods:**

#### `rebuild_docs()`

Force rebuild of documentation site.

#### `start_server()`

Start MkDocs server in background.

#### `test_page_title_color_is_dark(self)`

Verify 'Welcome to CORTEX' title has dark, visible color.

#### `test_sidebar_has_no_black_bar(self)`

Verify left sidebar has no dark header/black bar.

#### `test_css_file_contains_fixes(self)`

Verify custom.css contains the required style rules.

---

## tests.edge_cases.__init__

Edge case tests package

This package contains tests for edge cases and boundary conditions
across the CORTEX system.

Categories:
- test_empty_inputs.py: Empty/None/whitespace input handling
- test_malformed_data.py: Corrupted/invalid data resilience
- test_concurrent_access.py: Multi-user/parallel access scenarios
- test_resource_limits.py: Scalability and resource constraints

---

## tests.edge_cases.test_empty_inputs

Test edge cases for empty and missing inputs

These tests verify that CORTEX handles empty, None, and whitespace-only
inputs gracefully without crashing.

Test coverage:
- Empty string inputs
- None/null values
- Empty collections (lists, dicts)
- Whitespace-only strings

### TestEmptyInputs

Test system behavior with empty/missing inputs

**Methods:**

#### `test_empty_string_operation(self)`

Should gracefully handle empty string operation commands

#### `test_none_operation(self)`

Should handle None operation inputs without crashing

#### `test_empty_list_parameter(self)`

Should handle empty list parameters correctly

#### `test_empty_dict_config(self)`

Should handle empty configuration dictionaries

#### `test_whitespace_only_input(self)`

Should treat whitespace-only strings as empty

#### `test_empty_conversation_context(self)`

Should handle empty conversation context gracefully

#### `test_optional_parameters_omitted(self)`

Should handle omitted optional parameters correctly

#### `test_empty_file_path(self)`

Should reject empty file paths with clear error

---

## tests.edge_cases.test_malformed_data

Test edge cases for malformed and corrupted data

These tests verify that CORTEX handles invalid, corrupted, and malicious
data gracefully without crashing or exposing security vulnerabilities.

Test coverage:
- Invalid JSON configuration files
- Malformed YAML syntax
- Truncated/corrupted databases
- Invalid operation names
- Unparseable natural language
- SQL injection attempts
- Unicode edge cases
- Extremely long inputs (buffer overflow prevention)

### TestMalformedData

Test system resilience to corrupted/invalid data

**Methods:**

#### `test_invalid_json_config(self)`

Should detect and handle invalid JSON gracefully

#### `test_invalid_yaml_syntax(self)`

Should detect and report YAML syntax errors

#### `test_truncated_database(self)`

Should handle corrupted SQLite databases gracefully

#### `test_invalid_operation_name(self)`

Should reject invalid operation names with clear error

#### `test_malformed_natural_language(self)`

Should handle unparseable natural language requests

#### `test_special_characters_sql_injection(self)`

Should prevent SQL injection attacks

#### `test_unicode_edge_cases(self)`

Should handle various Unicode edge cases correctly

#### `test_extremely_long_input(self)`

Should handle extremely long inputs without buffer overflow

---

## tests.integration.test_component_wiring

CORTEX Component Wiring Integration Tests

Comprehensive tests to ensure all CORTEX modules, plugins, agents, and tiers
are correctly wired together and can communicate properly.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestPluginWiring

Test that all plugins are correctly wired

**Methods:**

#### `test_all_plugins_discoverable(self)`

Test that plugin registry can discover all plugins

#### `test_plugin_command_registration(self)`

Test that plugins can register commands

#### `test_platform_switch_plugin_integration(self)`

Test PlatformSwitchPlugin is wired correctly

### TestAgentWiring

Test that all agents are correctly wired

**Methods:**

#### `test_intent_router_wiring(self)`

Test IntentRouter is wired to all agents

#### `test_all_agents_have_base_methods(self)`

Test that all agents implement required base methods

### TestTierWiring

Test that all tiers are correctly wired together

**Methods:**

#### `test_tier0_brain_protector_integration(self)`

Test Tier 0 Brain Protector is wired

#### `test_tier1_conversation_manager_integration(self)`

Test Tier 1 Conversation Manager is wired

#### `test_tier2_knowledge_graph_integration(self)`

Test Tier 2 Knowledge Graph is wired

#### `test_tier3_metrics_integration(self)`

Test Tier 3 metrics are wired

### TestOperationsWiring

Test that operations orchestrators are wired correctly

**Methods:**

#### `test_operation_factory_wiring(self)`

Test OperationFactory can create operations

#### `test_cleanup_orchestrator_wiring(self)`

Test CleanupOrchestrator is wired

#### `test_design_sync_orchestrator_wiring(self)`

Test DesignSyncOrchestrator is wired

#### `test_optimize_system_orchestrator_wiring(self)`

Test OptimizeSystemOrchestrator is wired

### TestHeaderFormatterWiring

Test that header formatters are wired correctly after consolidation

**Methods:**

#### `test_operation_header_formatter_import(self)`

Test OperationHeaderFormatter can be imported

#### `test_backward_compatibility_imports(self)`

Test backward compatibility imports work

#### `test_orchestrators_use_new_formatter(self)`

Test that orchestrators import from consolidated formatter

#### `test_all_orchestrators_updated(self)`

Test all orchestrators use new formatter

### TestConfigWiring

Test configuration system is wired correctly

**Methods:**

#### `test_config_module_import(self)`

Test config module can be imported

#### `test_config_paths_accessible(self)`

Test config provides required paths

#### `test_tier_database_paths(self)`

Test tier database paths are configured

### TestTokenEfficiencyMetricsFileWiring

Test token-efficiency-metrics.yaml file is properly integrated

**Methods:**

#### `test_file_exists(self)`

Test token-efficiency-metrics.yaml exists

#### `test_file_is_valid_yaml(self)`

Test file contains valid YAML

#### `test_contains_token_efficiency_metrics(self)`

Test file contains token efficiency metrics

#### `test_old_file_removed(self)`

Test old efficiency-metrics.yaml is removed

#### `test_documentation_references_updated(self)`

Test documentation references new filename

### TestEndToEndWiring

End-to-end tests to verify complete system wiring

**Methods:**

#### `test_plugin_to_agent_communication(self)`

Test plugins can communicate with agents

#### `test_tier_to_tier_communication(self)`

Test tiers can communicate with each other

#### `test_operation_execution_flow(self)`

Test complete operation execution flow

---

## tests.integration.test_planning_integration

Integration Test: Interactive Planning Flow

Tests the complete flow from user request through interactive questioning
to task breakdown and plan generation.

Part of CORTEX 2.1 Track A: Quick Integration

### TestPlanningIntegration

Test complete planning flow from request to task breakdown.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_high_confidence_flow(self)`

Test that high confidence requests execute immediately without questions.

#### `test_low_confidence_flow(self)`

Test that ambiguous requests trigger interactive questioning.

#### `test_question_generation(self)`

Test that questions are generated appropriately for low confidence requests.

#### `test_workplanner_integration(self)`

Test that InteractivePlanner successfully delegates to WorkPlanner.

#### `test_confidence_detection(self)`

Test confidence scoring for different request types.

#### `test_fallback_plan_creation(self)`

Test that fallback plan works when WorkPlanner integration fails.

#### `test_answer_processing(self)`

Test that answers are correctly processed and stored.

### TestPlannerRouting

Test that planning requests are routed correctly.

**Methods:**

#### `test_plan_intent_keywords(self)`

Test that various planning keywords are recognized.

---

## tests.integration.test_publish_simulation

Integration Test: CORTEX Publish Simulation on ALIST Repository

Simulates the complete publish workflow:
1. Copy CORTEX to ALIST/cortex/
2. Verify all critical files present
3. Ensure no privacy leaks
4. Test onboarding workflow
5. Validate package integrity

Author: Asif Hussain
Created: 2025-11-12

### TestPublishSimulationALIST

Simulate CORTEX publish on ALIST repository

**Methods:**

#### `cortex_root(self)`

CORTEX repository root

#### `alist_simulation_dir(self, tmp_path)`

Create temporary ALIST-like directory structure

#### `published_cortex(self, cortex_root)`

Path to published CORTEX package

#### `test_published_package_exists(self, published_cortex)`

Verify publish/CORTEX exists before simulation

#### `test_critical_files_present_in_publish(self, published_cortex)`

Verify all critical files are in published package

These are ESSENTIAL for CORTEX to function in target application

#### `test_response_templates_included(self, published_cortex)`

Verify response-templates.yaml is included with all 13 new question templates

Added 2025-11-12 for intelligent question routing (CORTEX 3.0 foundation)

#### `test_simulate_copy_to_alist(self, published_cortex, alist_simulation_dir)`

Simulate copying CORTEX to ALIST repository

This is what users will do: cp -r publish/CORTEX /path/to/alist/cortex

#### `test_simulate_entry_point_copy(self, published_cortex, alist_simulation_dir)`

Simulate Module 1 of application_onboarding: copy_cortex_entry_points

This happens when user says "onboard this application"

#### `test_no_privacy_leaks_in_publish(self, published_cortex)`

SKULL-006: Verify no privacy leaks in published package

Check all text files for machine-specific paths

#### `test_no_excluded_directories_in_publish(self, published_cortex)`

Verify excluded directories are not in publish package

Directories like tests/, simulations/, cortex-2.0-design/ should NOT be published

#### `test_user_operations_only_in_publish(self, published_cortex)`

Verify only user-facing operations are in publish package

Admin operations like design_sync should be excluded

#### `test_package_size_reasonable(self, published_cortex)`

Verify published package is reasonably sized

Should be ~4-5 MB, not >10 MB

#### `test_simulate_brain_initialization(self, published_cortex, alist_simulation_dir, tmp_path)`

Simulate brain initialization in ALIST repository

This tests if the published package has everything needed to initialize

#### `test_cortex_3_0_design_docs_excluded(self, published_cortex)`

Verify CORTEX 3.0 design documents are NOT in publish package

These are internal design docs, not ready for public consumption

#### `test_all_python_modules_importable(self, published_cortex, tmp_path)`

Verify all Python modules in publish can be imported

This catches missing __init__.py files or broken imports

### TestPublishIntegrity

Test overall integrity of published package

**Methods:**

#### `published_cortex(self)`

#### `test_readme_not_truncated(self, published_cortex)`

Verify README.md is complete, not truncated

#### `test_requirements_not_empty(self, published_cortex)`

Verify requirements.txt has dependencies

#### `test_cortex_operations_valid_yaml(self, published_cortex)`

Verify cortex-operations.yaml is valid YAML

#### `test_brain_protection_rules_valid_yaml(self, published_cortex)`

Verify brain-protection-rules.yaml is valid YAML

---

## tests.integration.test_session_management

Integration tests for CORTEX session management and conversation tracking.

Tests conversation persistence, resume functionality, and context preservation across sessions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

### TestConversationPersistence

Test conversation data persistence to Tier 1 database.

**Methods:**

#### `temp_brain_root(self, tmp_path)`

Create temporary brain directory.

#### `conversation_memory(self, temp_brain_root)`

Create conversation memory instance.

#### `test_save_and_load_conversation(self, conversation_memory)`

Test saving and loading a complete conversation.

#### `test_save_multiple_conversations(self, conversation_memory)`

Test saving multiple conversations and retrieving them.

#### `test_conversation_retention_limit(self, conversation_memory)`

Test that only last 20 conversations are retained.

#### `test_conversation_with_context(self, conversation_memory)`

Test saving conversation with rich context.

### TestResumeWorkflow

Test resume functionality ('continue where I left off').

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `session_manager(self, temp_brain_root)`

Create session manager instance.

#### `test_resume_from_last_conversation(self, session_manager, temp_brain_root)`

Test resuming from the most recent conversation.

#### `test_resume_with_no_previous_conversation(self, session_manager)`

Test resume when there's no previous conversation.

#### `test_resume_specific_conversation_by_id(self, session_manager, temp_brain_root)`

Test resuming a specific conversation by ID.

### TestContextPreservation

Test that context is preserved across multiple turns.

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `test_pronoun_resolution_across_turns(self, temp_brain_root)`

Test that pronouns like 'it' are resolved using previous context.

#### `test_multi_turn_conversation_context(self, temp_brain_root)`

Test context accumulation over multiple turns.

### TestSessionStateManagement

Test session state tracking and management.

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `session_manager(self, temp_brain_root)`

#### `test_active_session_tracking(self, session_manager)`

Test tracking of active sessions.

#### `test_session_metadata_persistence(self, session_manager)`

Test that session metadata persists correctly.

#### `test_concurrent_sessions(self, session_manager)`

Test handling multiple concurrent sessions.

### TestConversationSearchAndRetrieval

Test searching and retrieving past conversations.

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `conversation_memory(self, temp_brain_root)`

#### `test_search_conversations_by_keyword(self, conversation_memory)`

Test searching conversations by keyword.

#### `test_get_conversations_by_date_range(self, conversation_memory)`

Test retrieving conversations within a date range.

#### `test_get_conversations_by_intent(self, conversation_memory)`

Test filtering conversations by intent type.

### TestSessionRecovery

Test recovery from interrupted or crashed sessions.

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `session_manager(self, temp_brain_root)`

#### `test_detect_interrupted_session(self, session_manager)`

Test detection of interrupted sessions (not properly closed).

#### `test_recover_interrupted_session(self, session_manager)`

Test recovering state from interrupted session.

### TestConversationContextWindow

Test conversation context window management (last 20 conversations).

**Methods:**

#### `temp_brain_root(self, tmp_path)`

#### `conversation_memory(self, temp_brain_root)`

#### `test_context_window_limit(self, conversation_memory)`

Test that context window respects the 20-conversation limit.

#### `test_context_window_chronological_order(self, conversation_memory)`

Test that context window is in chronological order.

---

## tests.operations.modules.optimization.test_hardcoded_data_cleaner_module

Tests for Hardcoded Data Cleaner Module

Validates aggressive detection of:
- Hardcoded paths
- Mock data in production
- Fallback mechanisms
- Placeholder values

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestHardcodedDataCleanerModule

Test suite for hardcoded data detection.

**Methods:**

#### `temp_project(self, tmp_path)`

Create temporary project structure.

#### `cleaner(self, temp_project)`

Create cleaner module instance.

#### `test_module_metadata(self, cleaner)`

Test module metadata is correct.

#### `test_detect_hardcoded_windows_path(self, temp_project, cleaner)`

Test detection of hardcoded Windows absolute paths.

#### `test_detect_hardcoded_unix_path(self, temp_project, cleaner)`

Test detection of hardcoded Unix absolute paths.

#### `test_detect_mock_in_production_code(self, temp_project, cleaner)`

Test detection of mock data in non-test files.

#### `test_allow_mock_in_test_files(self, temp_project, cleaner)`

Test that mocks are allowed in test files.

#### `test_detect_fallback_with_get(self, temp_project, cleaner)`

Test detection of .get() with hardcoded fallback values.

#### `test_detect_hardcoded_return_dict(self, temp_project, cleaner)`

Test detection of functions returning large hardcoded dicts.

#### `test_detect_placeholder_keywords(self, temp_project, cleaner)`

Test detection of placeholder keywords like 'test', 'dummy', 'fake'.

#### `test_exclude_paths_with_path_constructor(self, temp_project, cleaner)`

Test that paths using Path() are not flagged.

#### `test_fail_on_critical_violations(self, temp_project, cleaner)`

Test that fail_on_critical=True fails when critical violations found.

#### `test_no_violations_returns_success(self, temp_project, cleaner)`

Test that clean code returns success.

#### `test_exclude_patterns_work(self, temp_project, cleaner)`

Test that exclude patterns prevent scanning.

#### `test_multiple_violations_in_single_file(self, temp_project, cleaner)`

Test detection of multiple violations in one file.

#### `test_report_generation(self, temp_project, cleaner)`

Test that report is generated with violations.

#### `test_suggested_fixes_provided(self, temp_project, cleaner)`

Test that violations include suggested fixes.

#### `test_severity_categorization(self, temp_project, cleaner)`

Test that violations are categorized by severity correctly.

#### `test_prerequisite_validation(self, cleaner, temp_project)`

Test prerequisite validation.

#### `test_prerequisite_validation_failure(self)`

Test prerequisite validation with invalid project root.

#### `test_rollback_returns_true(self, cleaner)`

Test rollback (no-op for scanner).

### TestHardcodedPathPatterns

Test specific path pattern detection.

**Methods:**

#### `cleaner(self, tmp_path)`

#### `test_detect_project_path(self, tmp_path, cleaner)`

Test detection of hardcoded PROJECTS directory paths.

#### `test_ignore_relative_paths(self, tmp_path, cleaner)`

Test that relative paths are not flagged.

### TestEdgeCases

Test edge cases and error handling.

**Methods:**

#### `cleaner(self, tmp_path)`

#### `test_handle_syntax_error_file(self, tmp_path, cleaner)`

Test graceful handling of files with syntax errors.

#### `test_handle_empty_file(self, tmp_path, cleaner)`

Test handling of empty files.

#### `test_handle_nonexistent_scan_path(self, tmp_path, cleaner)`

Test handling of nonexistent scan paths.

---

## tests.operations.modules.optimize.__init__

Tests for CORTEX Optimization Module

---

## tests.operations.test_cleanup

Tests for Workspace Cleanup Operation
CORTEX 3.0 Phase 1.1 - BLOCKING Tests

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestSafetyChecks

BLOCKING: Safety checks are critical - never delete source code.

**Methods:**

#### `test_protects_python_source(self, tmp_path)`

Test protects .py files.

#### `test_protects_config_files(self, tmp_path)`

Test protects YAML/JSON config files.

#### `test_protects_documentation(self, tmp_path)`

Test protects markdown and text files.

#### `test_protects_git_directory(self, tmp_path)`

Test protects .git directory.

#### `test_protects_source_directory(self, tmp_path)`

Test protects src/ directory.

#### `test_protects_brain_databases(self, tmp_path)`

Test protects brain database files.

#### `test_allows_temp_files(self, tmp_path)`

Test allows deletion of .tmp files.

#### `test_allows_pycache(self, tmp_path)`

Test allows deletion of __pycache__ directories.

### TestTempFileDetection

BLOCKING: Temporary file detection.

**Methods:**

#### `test_finds_tmp_files(self, tmp_path)`

Test finds .tmp and .temp files.

#### `test_finds_pycache_dirs(self, tmp_path)`

Test finds __pycache__ directories.

#### `test_finds_pyc_files(self, tmp_path)`

Test finds .pyc compiled Python files.

#### `test_skips_protected_tmp_in_src(self, tmp_path)`

Test skips .tmp files in protected src/ directory.

### TestLogFileDetection

BLOCKING: Old log file detection.

**Methods:**

#### `test_finds_old_logs(self, tmp_path)`

Test finds log files older than 30 days.

#### `test_skips_recent_logs(self, tmp_path)`

Test skips recent log files.

#### `test_handles_missing_logs_dir(self, tmp_path)`

Test handles missing logs/ directory gracefully.

### TestCacheFileDetection

BLOCKING: Large cache file detection.

**Methods:**

#### `test_finds_large_cache_files(self, tmp_path)`

Test finds cache files larger than 10MB.

#### `test_skips_small_cache_files(self, tmp_path)`

Test skips cache files smaller than threshold.

### TestSizeCalculation

BLOCKING: Size calculation for cleanup reporting.

**Methods:**

#### `test_calculates_file_size(self, tmp_path)`

Test calculates individual file size.

#### `test_calculates_directory_size(self, tmp_path)`

Test calculates total directory size.

### TestCleanupOperation

BLOCKING: Complete cleanup operation.

**Methods:**

#### `test_dry_run_mode(self, tmp_path)`

Test dry-run mode doesn't delete anything.

#### `test_removes_temp_files(self, tmp_path)`

Test actually removes temp files.

#### `test_handles_empty_workspace(self, tmp_path)`

Test handles workspace with nothing to clean.

#### `test_reports_space_freed(self, tmp_path)`

Test reports space freed in MB.

### TestUserConfirmation

PRAGMATIC: User confirmation tests require manual testing.

**Methods:**

#### `test_user_can_cancel(self)`

Test user can cancel cleanup when prompted.

#### `test_no_confirm_flag_skips_prompt(self)`

Test --no-confirm flag skips confirmation.

---

## tests.operations.test_design_sync_orchestrator

Tests for design_sync_orchestrator module.

SKULL-001 compliance: These tests must pass BEFORE claiming design_sync is production-ready.

### TestStatusFileConsolidation

Test status file consolidation logic - CRITICAL for preventing content deletion.

**Methods:**

#### `test_consolidate_preserves_progress_bars(self, tmp_path)`

REGRESSION TEST: Ensure consolidation doesn't delete progress bars.

Bug: Regex r'\*Last Synchronized:.*?\*' was too greedy and deleted content.
Fix: Should only replace the timestamp line, not surrounding content.

#### `test_consolidate_preserves_file_size(self, tmp_path)`

Ensure consolidated file is not dramatically smaller (indicating content loss).

#### `test_consolidate_handles_multiple_asterisks(self, tmp_path)`

Ensure regex doesn't match beyond the timestamp line when multiple asterisks exist.

#### `test_consolidate_updates_metrics_correctly(self, tmp_path)`

Ensure metrics are updated without corrupting file structure.

#### `test_consolidate_first_time_adds_timestamp(self, tmp_path)`

Ensure first-time consolidation adds timestamp without corruption.

#### `test_consolidate_multiple_runs_idempotent(self, tmp_path)`

Ensure running consolidation multiple times doesn't corrupt file.

### TestDesignSyncIntegration

Integration tests for full design_sync operation.

**Methods:**

#### `test_design_sync_operation_completes(self, tmp_path)`

Smoke test: Ensure design_sync can run without crashing.

### TestProgressBarGeneration

Test visual progress bar generation - NEW FEATURE.

**Methods:**

#### `test_calculate_phase_progress_from_content(self)`

Test extraction of phase percentages from Current Focus section.

#### `test_generate_progress_bar_full(self)`

Test progress bar generation at 100%.

#### `test_generate_progress_bar_partial(self)`

Test progress bar generation at 50%.

#### `test_generate_progress_bar_empty(self)`

Test progress bar generation at 0%.

### TestExecutionOrderAndVisualGraphSync

CRITICAL: Tests to prevent visual progress graph from going out of sync.

This test suite enforces:
1. Visual graph percentages must match Current Focus percentages
2. Visual graph order must match Current Focus execution order
3. Active phases (mentioned in Current Focus) appear first
4. Completed phases (100%, not in Current Focus) appear next
5. Future phases (0%, not in Current Focus) appear last

SKULL-001: These tests MUST pass before claiming design_sync is production-ready.

**Methods:**

#### `test_execution_order_extraction_from_current_focus(self)`

Test that execution order is correctly extracted from Current Focus section.

#### `test_execution_order_completed_phases_grouped(self)`

Test that completed phases (100%) are grouped together after active phases.

#### `test_visual_graph_percentages_match_current_focus(self)`

CRITICAL: Ensure visual graph percentages exactly match Current Focus.

This test prevents the bug where hardcoded percentages override actual values.

#### `test_visual_graph_order_matches_current_focus_order(self)`

CRITICAL: Ensure visual graph shows phases in Current Focus order, not numerical.

This test prevents the bug where graph showed 0-11 regardless of execution sequence.

#### `test_visual_graph_sync_with_actual_file(self, tmp_path)`

INTEGRATION TEST: Verify visual graph stays in sync after consolidation.

This test simulates the full workflow:
1. Read CORTEX2-STATUS.MD with Current Focus
2. Extract percentages and execution order
3. Generate new visual progress bars
4. Verify bars match Current Focus exactly

#### `test_fallback_to_numerical_order_when_no_current_focus(self)`

Test that graph falls back to numerical order when Current Focus is missing.

#### `test_prevents_duplicate_phases_in_execution_order(self)`

Test that execution order doesn't contain duplicate phases.

#### `test_regression_phase_8_percentage_not_hardcoded_to_zero(self)`

REGRESSION TEST: Prevent Phase 8 from being hardcoded to 0%.

Original bug: _calculate_phase_progress had Phase 8 hardcoded to 0%,
which overrode the actual 25% from Current Focus.

#### `test_active_phases_always_appear_first_in_visual_graph(self)`

CRITICAL: Ensure active phases (in Current Focus) always appear first.

This is the core feature: visual graph should show what you're working on
at the top, not buried in numerical order.

---

## tests.operations.test_environment_setup

Tests for environment_setup.py monolithic script.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestSetupResult

Tests for SetupResult dataclass.

**Methods:**

#### `test_setup_result_creation(self)`

Test creating a SetupResult.

#### `test_setup_result_to_dict(self)`

Test converting SetupResult to dictionary.

### TestEnvironmentSetup

Tests for EnvironmentSetup class.

**Methods:**

#### `setup_instance(self, tmp_path)`

Create EnvironmentSetup instance with temp directory.

#### `mock_cortex_project(self, tmp_path)`

Create a mock CORTEX project structure.

#### `test_initialization(self, tmp_path)`

Test EnvironmentSetup initialization.

#### `test_initialization_default_path(self)`

Test EnvironmentSetup with default path.

#### `test_validate_project_success(self, mock_cortex_project)`

Test successful project validation.

#### `test_validate_project_missing_directory(self, tmp_path)`

Test project validation with missing directory.

#### `test_detect_platform(self, setup_instance)`

Test platform detection.

#### `test_initialize_brain_success(self, mock_cortex_project)`

Test successful brain initialization.

#### `test_initialize_brain_missing_directory(self, tmp_path)`

Test brain initialization with missing directory.

#### `test_initialize_brain_missing_files(self, tmp_path)`

Test brain initialization with missing essential files.

#### `test_sync_git_success(self, mock_run, mock_cortex_project)`

Test successful git sync.

#### `test_sync_git_uncommitted_changes(self, mock_run, mock_cortex_project)`

Test git sync with uncommitted changes.

#### `test_setup_virtualenv_already_active(self, setup_instance)`

Test virtual environment setup when already active.

#### `test_setup_virtualenv_exists(self, tmp_path)`

Test virtual environment setup when venv exists.

#### `test_install_dependencies_success(self, mock_run, mock_cortex_project)`

Test successful dependency installation.

#### `test_install_dependencies_missing_file(self, tmp_path)`

Test dependency installation without requirements.txt.

#### `test_install_dependencies_failure(self, mock_run, mock_cortex_project)`

Test failed dependency installation.

#### `test_configure_vision_api(self, setup_instance)`

Test Vision API configuration (intentionally skips for MVP).

#### `test_enable_conversation_tracking_exists(self, mock_cortex_project)`

Test conversation tracking with existing database.

#### `test_enable_conversation_tracking_missing(self, mock_cortex_project)`

Test conversation tracking without database.

#### `test_verify_tooling_all_available(self, mock_run, setup_instance)`

Test tooling verification with all tools available.

#### `test_verify_tooling_some_missing(self, mock_run, setup_instance)`

Test tooling verification with missing tools.

#### `test_complete_setup(self, mock_cortex_project)`

Test setup completion.

#### `test_run_minimal_profile_success(self, mock_complete, mock_brain, mock_deps, mock_venv, mock_platform, mock_validate, mock_cortex_project)`

Test running minimal profile successfully.

#### `test_run_validation_failure(self, mock_validate, mock_cortex_project)`

Test run with validation failure.

#### `test_run_dependency_failure(self, mock_deps, mock_venv, mock_platform, mock_validate, mock_cortex_project)`

Test run with dependency installation failure.

### TestRunSetupFunction

Tests for run_setup convenience function.

**Methods:**

#### `test_run_setup_default(self, mock_run)`

Test run_setup with defaults.

#### `test_run_setup_custom_profile(self, mock_run, tmp_path)`

Test run_setup with custom profile.

### TestIntegration

Integration tests for environment setup.

**Methods:**

#### `test_real_cortex_validation(self)`

Test validation against real CORTEX project.

#### `test_real_platform_detection(self)`

Test platform detection on real system.

---

## tests.operations.test_optimize_system_orchestrator

Tests for System Optimization Meta-Orchestrator.

These tests validate the meta-level orchestrator that coordinates
all CORTEX optimization operations.

SKULL-001 compliance: Tests must pass before claiming optimize_system is production-ready.

### TestOptimizeSystemOrchestrator

Test suite for System Optimization Meta-Orchestrator.

**Methods:**

#### `project_root(self, tmp_path)`

Create temporary project structure.

#### `orchestrator(self, project_root)`

Create orchestrator instance.

#### `test_orchestrator_initialization(self, orchestrator, project_root)`

Test orchestrator initializes correctly.

#### `test_metadata_properties(self, orchestrator)`

Test orchestrator metadata is correct.

#### `test_prerequisite_validation_success(self, orchestrator)`

Test prerequisite validation passes with valid setup.

#### `test_prerequisite_validation_failure_missing_directory(self, tmp_path)`

Test prerequisite validation fails with missing directories.

#### `test_prerequisite_validation_failure_missing_orchestrators(self, project_root)`

Test prerequisite validation fails with missing orchestrators.

#### `test_execute_live_mode(self, orchestrator, project_root)`

Test execution in live mode.

#### `test_calculate_total_improvements(self, orchestrator)`

Test improvement calculation.

#### `test_health_score_calculation(self, orchestrator)`

Test health score calculation.

#### `test_generate_health_report(self, orchestrator)`

Test health report generation.

#### `test_report_to_dict(self, orchestrator)`

Test health report serialization.

#### `test_save_report(self, orchestrator, project_root)`

Test report saving to file.

#### `test_phase_skipping(self, orchestrator)`

Test skipping specific phases.

#### `test_execution_time_tracking(self, orchestrator)`

Test execution time is tracked.

#### `test_formatted_header_in_result(self, orchestrator)`

Test formatted header is included in result (SKULL-006 compliance).

#### `test_formatted_footer_in_result(self, orchestrator)`

Test formatted footer is included in result (SKULL-006 compliance).

#### `test_error_handling(self, orchestrator, project_root)`

Test error handling during execution.

### TestOptimizationMetrics

Test OptimizationMetrics dataclass.

**Methods:**

#### `test_metrics_initialization(self)`

Test metrics initialize with correct defaults.

#### `test_metrics_modification(self)`

Test metrics can be modified.

### TestSystemHealthReport

Test SystemHealthReport dataclass.

**Methods:**

#### `test_report_initialization(self)`

Test report initializes correctly.

#### `test_report_serialization(self)`

Test report can be serialized to dict.

---

## tests.operations.test_parallel_execution

Tests for parallel module execution in operations orchestrator.

Validates that:
1. Independent modules execute in parallel
2. Dependent modules execute sequentially
3. Error handling works correctly in parallel execution
4. Performance improves with parallel execution
5. Context is properly shared between modules

Author: Asif Hussain
Version: 1.0

### SlowModule

Test module that takes some time to execute.

**Methods:**

#### `get_metadata(self)`

#### `execute(self, context)`

Execute with a delay to simulate work.

### FailingModule

Test module that fails.

**Methods:**

#### `get_metadata(self)`

#### `execute(self, context)`

Always fail.

### TestParallelExecution

Test suite for parallel module execution.

**Methods:**

#### `test_independent_modules_run_in_parallel(self)`

Independent modules should execute concurrently.

#### `test_dependent_modules_run_sequentially(self)`

Modules with dependencies should execute in order.

#### `test_mixed_parallel_and_sequential(self)`

Mix of independent and dependent modules.

#### `test_parallel_group_failure_handling(self)`

Failure in parallel group should be handled correctly.

#### `test_optional_module_failure_continues(self)`

Optional module failure should not stop execution.

#### `test_context_sharing_in_parallel(self)`

Context updates from parallel modules should be merged.

#### `test_max_workers_limit(self)`

Parallel execution should respect max_workers limit.

#### `test_performance_metrics_tracking(self)`

Performance metrics should be accurately tracked.

### TestParallelExecutionEdgeCases

Test edge cases in parallel execution.

**Methods:**

#### `test_single_module_no_parallel(self)`

Single module should not use parallel execution.

#### `test_empty_module_list(self)`

Empty module list should complete successfully.

#### `test_circular_dependency_handling(self)`

Circular dependencies should be detected and handled.

---

## tests.operations.test_setup

Tests for Environment Setup Operation
CORTEX 3.0 Phase 1.1 - BLOCKING Tests

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestPlatformDetection

BLOCKING: Platform detection is critical.

**Methods:**

#### `test_detects_windows(self)`

Test Windows platform detection.

#### `test_detects_mac(self)`

Test macOS platform detection.

#### `test_detects_linux(self)`

Test Linux platform detection.

#### `test_handles_unknown_platform(self)`

Test unknown platform detection.

### TestPythonValidation

BLOCKING: Python version validation is essential.

**Methods:**

#### `test_validates_python_39_or_higher(self)`

Test Python 3.9+ validation.

#### `test_validates_python_311(self)`

Test Python 3.11 validation.

#### `test_rejects_python_38(self)`

Test Python 3.8 rejection (too old).

#### `test_rejects_python_2(self)`

Test Python 2.x rejection.

### TestGitValidation

BLOCKING: Git validation for version control.

**Methods:**

#### `test_detects_git_installed(self, mock_run)`

Test Git installation detection.

#### `test_handles_git_not_found(self, mock_run)`

Test Git not found scenario.

### TestVirtualEnvironment

BLOCKING: Virtual environment creation.

**Methods:**

#### `test_creates_venv_if_missing(self, tmp_path)`

Test virtual environment creation.

#### `test_skips_if_venv_exists(self, tmp_path)`

Test skips creation if venv already exists.

### TestDependencyInstallation

BLOCKING: Dependency installation validation.

**Methods:**

#### `test_installs_from_requirements(self, tmp_path)`

Test dependency installation from requirements.txt.

#### `test_handles_missing_requirements(self, tmp_path)`

Test handles missing requirements.txt.

### TestBrainInitialization

BLOCKING: Brain database initialization.

**Methods:**

#### `test_creates_brain_databases(self, tmp_path)`

Test brain database creation.

#### `test_skips_if_databases_exist(self, tmp_path)`

Test skips creation if databases already exist.

### TestSetupOperation

BLOCKING: Complete setup operation validation.

**Methods:**

#### `test_minimal_profile_succeeds(self, tmp_path)`

Test minimal profile setup.

#### `test_standard_profile_creates_venv(self, mock_run, tmp_path)`

Test standard profile creates virtual environment.

#### `test_handles_invalid_project_root(self)`

Test handles invalid project root gracefully.

### TestCrossPlatform

WARNING: Platform-specific functionality requires target hardware.

**Methods:**

#### `test_setup_on_mac(self)`

Test setup on macOS.

#### `test_setup_on_linux(self)`

Test setup on Linux.

#### `test_creates_platform_specific_venv(self)`

Test platform-specific venv creation.

---

## tests.operations.test_update_documentation

Tests for CORTEX Documentation Generator

Comprehensive test suite for update_documentation operation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1 Week 2)

### TestDocGenerationResult

Test DocGenerationResult dataclass.

**Methods:**

#### `test_result_initialization(self)`

Test result object initialization.

#### `test_result_to_dict(self)`

Test conversion to dictionary.

### TestDocumentationGenerator

Test DocumentationGenerator class.

**Methods:**

#### `test_initialization(self, temp_cortex_root)`

Test generator initialization.

#### `test_load_config_creates_default(self, temp_cortex_root)`

Test config loading creates default if not exists.

#### `test_load_config_reads_existing(self, temp_cortex_root)`

Test config loading reads existing file.

#### `test_discover_files(self, temp_cortex_root)`

Test file discovery.

#### `test_discover_files_excludes_patterns(self, temp_cortex_root)`

Test file discovery excludes specified patterns.

#### `test_extract_python_docstrings(self, temp_cortex_root)`

Test docstring extraction from Python files.

#### `test_extract_function_args(self, temp_cortex_root)`

Test function argument extraction.

#### `test_generate_api_reference(self, temp_cortex_root)`

Test API reference generation.

#### `test_generate_operations_docs(self, temp_cortex_root)`

Test operations documentation generation.

#### `test_validate_links(self, temp_cortex_root)`

Test link validation.

#### `test_validate_links_disabled(self, temp_cortex_root)`

Test link validation when disabled.

#### `test_update_mkdocs_nav(self, temp_cortex_root)`

Test MkDocs navigation update.

#### `test_update_mkdocs_nav_disabled(self, temp_cortex_root)`

Test MkDocs navigation update when disabled.

#### `test_execute_full_workflow(self, temp_cortex_root)`

Test full documentation generation workflow.

#### `test_execute_handles_errors_gracefully(self, temp_cortex_root)`

Test error handling during execution.

### TestEdgeCases

Test edge cases and error conditions.

**Methods:**

#### `test_empty_directory(self, tmp_path)`

Test with empty directory.

#### `test_file_without_docstrings(self, temp_cortex_root)`

Test Python file without docstrings.

#### `test_malformed_python_file(self, temp_cortex_root)`

Test handling of malformed Python file.

#### `test_markdown_with_no_links(self, temp_cortex_root)`

Test markdown file with no links.

### TestIntegration

Integration tests with real CORTEX files.

**Methods:**

#### `test_real_cortex_documentation(self)`

Test documentation generation on real CORTEX codebase.

### `temp_cortex_root(tmp_path)`

Create temporary CORTEX structure for testing.

---

## tests.platform.__init__

Platform-specific tests package

This package contains tests for platform-specific behaviors
and edge cases, particularly for macOS.

Test files:
- test_macos_edge_cases.py: macOS-specific edge cases and quirks
- test_case_sensitivity.py: Filesystem case sensitivity handling
- test_path_separators.py: Unix vs Windows path handling
- test_python_detection.py: Multiple Python installation handling

---

## tests.plugins.test_cleanup_protection

Test cleanup plugin protection rules

Validates that cleanup_plugin properly respects CORTEX protection rules:
- Never deletes core CORTEX directories (src/, tests/, cortex-brain/, etc.)
- Never deletes essential configuration files
- Never deletes Python source files in src/
- Never deletes test files
- Never deletes database files
- Never deletes documentation in docs/

### TestCleanupProtection

Test that cleanup plugin respects protection rules

**Methods:**

#### `test_core_directories_protected(self, cleanup_plugin)`

Test that core CORTEX directories are protected

#### `test_tier_directories_protected(self, cleanup_plugin)`

Test that tier directories are protected

#### `test_agent_directories_protected(self, cleanup_plugin)`

Test that agent directories are protected

#### `test_config_files_protected(self, cleanup_plugin)`

Test that configuration files are protected

#### `test_essential_docs_protected(self, cleanup_plugin)`

Test that essential documentation files are protected

#### `test_python_source_files_protected(self, cleanup_plugin)`

Test that Python source files in src/ are protected

#### `test_test_files_protected(self, cleanup_plugin)`

Test that test files are protected

#### `test_database_files_protected(self, cleanup_plugin)`

Test that database files are protected

#### `test_documentation_protected(self, cleanup_plugin)`

Test that documentation in docs/ is protected

#### `test_brain_files_protected(self, cleanup_plugin)`

Test that cortex-brain files are protected

#### `test_safety_verification_passes(self, cleanup_plugin)`

Test that safety verification passes for core files

#### `test_temp_files_not_protected(self, cleanup_plugin)`

Test that temp files are NOT protected (should be cleanable)

#### `test_pycache_not_protected(self, cleanup_plugin)`

Test that __pycache__ directories are NOT protected

#### `test_backup_files_cleanable(self, cleanup_plugin)`

Test that backup files are cleanable (not protected)

### TestCleanupExecution

Test cleanup execution safety

**Methods:**

#### `test_dry_run_doesnt_modify_files(self, cleanup_plugin)`

Test that dry run doesn't actually modify files

#### `test_safety_check_runs_before_cleanup(self, cleanup_plugin)`

Test that safety check runs before any cleanup

#### `test_safety_violations_prevent_cleanup(self)`

Test that safety violations prevent cleanup execution

### `cleanup_plugin()`

Create a cleanup plugin instance for testing

---

## tests.plugins.test_command_expansion

CORTEX Router Command Expansion Tests

Tests for slash command expansion in the router before intent detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestRouterCommandExpansion

Test router command expansion integration.

**Methods:**

#### `mock_router(self)`

Create mock router with command registry.

#### `test_slash_command_expanded_before_routing(self, mock_router)`

Test that slash commands are expanded before intent detection.

#### `test_natural_language_passes_through(self, mock_router)`

Test that natural language bypasses command expansion.

#### `test_unknown_slash_command_passes_through(self, mock_router)`

Test that unknown slash commands pass through unchanged.

### TestCommandAliasExpansion

Test that command aliases expand correctly.

**Methods:**

#### `test_primary_and_alias_expand_identically(self)`

Test that primary command and alias expand to same natural language.

### TestPlatformCommandExpansion

Test platform switch command expansions.

**Methods:**

#### `test_mac_command_expansion(self)`

Test /mac expands correctly.

#### `test_windows_command_expansion(self)`

Test /windows expands correctly.

#### `test_setup_command_expansion(self)`

Test /setup expands correctly.

### TestCommandExpansionPerformance

Test that command expansion is fast.

**Methods:**

#### `test_expansion_is_fast(self)`

Test that command expansion meets performance target.

#### `test_is_command_is_fast(self)`

Test that command detection is O(1).

### TestCommandExpansionEdgeCases

Test edge cases in command expansion.

**Methods:**

#### `test_empty_string(self)`

Test expansion of empty string.

#### `test_whitespace_only(self)`

Test expansion of whitespace.

#### `test_slash_only(self)`

Test expansion of just slash.

#### `test_case_sensitivity(self)`

Test that commands are case-sensitive.

---

## tests.plugins.test_command_registry

CORTEX Plugin Command Registry Tests

Tests for the extensible command system that allows plugins to register
slash commands as shortcuts to natural language.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestCommandRegistryInitialization

Test registry initialization and singleton pattern.

**Methods:**

#### `test_registry_creation(self)`

Test basic registry creation.

#### `test_singleton_pattern(self)`

Test that get_command_registry returns singleton.

#### `test_core_commands_registered(self)`

Test that core commands are pre-registered.

#### `test_registry_stats_initial(self)`

Test initial registry statistics.

### TestCommandRegistration

Test command registration functionality.

**Methods:**

#### `test_register_valid_command(self)`

Test registering a valid command.

#### `test_register_command_with_aliases(self)`

Test registering command with aliases.

#### `test_command_conflict_detection(self)`

Test that conflicting commands are rejected.

#### `test_invalid_command_format(self)`

Test that invalid command formats are rejected.

### TestCommandExpansion

Test command expansion to natural language.

**Methods:**

#### `test_expand_registered_command(self)`

Test expanding a registered command.

#### `test_expand_alias(self)`

Test expanding an alias command.

#### `test_expand_non_command_returns_none(self)`

Test that non-commands return None.

#### `test_expand_with_whitespace(self)`

Test command expansion with whitespace.

### TestCommandQuery

Test querying commands from registry.

**Methods:**

#### `test_get_command_metadata(self)`

Test retrieving command metadata.

#### `test_get_plugin_commands(self)`

Test getting all commands for a plugin.

#### `test_get_commands_by_category(self)`

Test getting commands by category.

#### `test_get_all_commands(self)`

Test getting all commands.

### TestHelpGeneration

Test help text generation.

**Methods:**

#### `test_generate_help_all_commands(self)`

Test generating help for all commands.

#### `test_generate_help_by_category(self)`

Test generating help for specific category.

#### `test_help_includes_aliases(self)`

Test that help text shows aliases.

### TestIsCommand

Test command detection.

**Methods:**

#### `test_is_command_registered(self)`

Test detecting registered commands.

#### `test_is_command_not_registered(self)`

Test detecting non-commands.

#### `test_is_command_with_whitespace(self)`

Test command detection with whitespace.

### TestRegistryStats

Test registry statistics.

**Methods:**

#### `test_stats_after_registrations(self)`

Test stats reflect registrations.

### TestPlatformSwitchCommands

Test platform switch plugin commands (integration test).

**Methods:**

#### `test_platform_commands_registered(self)`

Test that platform commands are available.

---

## tests.plugins.test_narrative_flow_implicit_parts

Test Narrative Flow Detection - Implicit Part 1 Handling
Tests for the "Awakening of CORTEX" structure detection issue discovered during validation.

Issue: Plugin detected 2 explicit PART headers but 3 interludes, flagging false positive warning.
Root Cause: Story has implicit "Part 1" (unlabeled opening) followed by explicit "PART 2" and "PART 3".

This test suite ensures all structure detection logic correctly handles implicit parts.

### TestImplicitPartDetection

Test detection of implicit Part 1 in story structures.

**Methods:**

#### `plugin(self)`

Create plugin instance.

#### `test_detects_explicit_parts_only(self, plugin)`

Baseline: Story with only explicit PART headers.

#### `test_detects_implicit_part_1(self, plugin)`

Core issue: Story with implicit Part 1 (unlabeled) + explicit Parts 2 & 3.

#### `test_detects_implicit_part_with_interludes(self, plugin)`

Real CORTEX scenario: 3 interludes with implicit Part 1.

#### `test_no_implicit_part_when_starts_with_explicit(self, plugin)`

Should NOT detect implicit part if story starts with PART label.

#### `test_only_one_explicit_part_with_chapters_before(self, plugin)`

Edge case: Chapters before a single PART label.

### TestStructureClassification

Test story structure classification based on parts.

**Methods:**

#### `plugin(self)`

Create plugin instance.

#### `test_three_act_structure(self, plugin)`

Story with 3 parts = three-act structure.

#### `test_multi_part_structure(self, plugin)`

Story with 2 or 4+ parts = multi-part.

#### `test_single_narrative_no_parts(self, plugin)`

Story with no PART labels = single narrative.

#### `test_implicit_part_affects_structure_classification(self, plugin)`

Implicit Part 1 + 2 explicit parts should = three-act structure.

### TestInterludeToPartRatioValidation

Test validation of interlude/part ratios.

**Methods:**

#### `plugin(self)`

Create plugin instance.

#### `test_balanced_interludes_and_parts(self, plugin)`

One interlude per part = balanced, no warning.

#### `test_more_interludes_than_parts_warns(self, plugin)`

Too many interludes relative to parts should warn.

#### `test_implicit_part_prevents_false_positive_warning(self, plugin)`

The CORTEX story case: should NOT warn when implicit part exists.

### TestEdgeCases

Test edge cases and boundary conditions.

**Methods:**

#### `plugin(self)`

Create plugin instance.

#### `test_empty_story(self, plugin)`

Empty story should not crash.

#### `test_only_intro_no_chapters_or_parts(self, plugin)`

Story with just an intro, no structure.

#### `test_case_insensitive_part_detection(self, plugin)`

PART headers with different cases.

#### `test_part_in_middle_of_line(self, plugin)`

PART not at start of line shouldn't count as explicit part.

### TestRecommendedFix

Document the recommended implementation for implicit part detection.

**Methods:**

#### `plugin(self)`

Create plugin instance.

#### `test_recommended_implementation_pattern(self, plugin)`

This test documents how _analyze_narrative_flow SHOULD work.

Algorithm:
1. Count explicit "# PART " headers
2. Find position of first explicit PART
3. Check if chapters/interludes exist before first PART
4. If yes, implicit Part 1 exists → total_parts += 1
5. Return total parts (explicit + implicit)

---

## tests.plugins.test_platform_auto_detection

CORTEX Platform Auto-Detection Tests

Tests for automatic platform detection and configuration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestPlatformDetection

Test automatic platform detection.

**Methods:**

#### `test_detect_current_platform(self)`

Test that current platform is detected correctly.

#### `test_platform_display_names(self)`

Test platform display names.

#### `test_platform_config_creation(self)`

Test platform config is created correctly.

### TestAutomaticPlatformChange

Test automatic platform change detection.

**Methods:**

#### `temp_project(self)`

Create temporary project structure.

#### `test_first_time_setup_no_state_file(self, temp_project)`

Test first-time setup when no state file exists.

#### `test_save_and_load_platform_state(self, temp_project)`

Test saving and loading platform state.

#### `test_platform_change_detected(self, temp_project)`

Test that platform change is detected.

#### `test_no_change_same_platform(self, temp_project)`

Test that no change is detected when platform is same.

### TestAutoConfiguration

Test automatic configuration when platform changes.

**Methods:**

#### `mock_plugin(self, tmp_path)`

Create mock plugin with temp directory.

#### `test_auto_configure_runs_on_platform_change(self, mock_plugin)`

Test that auto-configure runs when platform changes.

#### `test_auto_configure_lightweight(self, mock_plugin)`

Test that auto-configure is lightweight (doesn't install).

### TestManualSetup

Test manual /setup command.

**Methods:**

#### `test_setup_command_registered(self)`

Test that /setup command is registered.

#### `test_no_platform_specific_commands(self)`

Test that /mac, /windows, /linux are NOT registered.

#### `test_setup_aliases_present(self)`

Test that /setup has useful aliases.

### TestPluginInitialization

Test plugin initialization with auto-detection.

**Methods:**

#### `temp_project(self)`

Create temporary project structure.

#### `test_initialize_checks_platform(self, temp_project)`

Test that initialize checks for platform changes.

### TestDependencyCheck

Test dependency checking (not installation).

**Methods:**

#### `test_check_dependencies_exist(self)`

Test quick dependency check.

---

## tests.plugins.test_platform_switch_plugin

Tests for Platform Switch Plugin

Validates platform switching functionality across Mac, Windows, and Linux.

### TestPlatformDetection

Test platform detection logic.

**Methods:**

#### `test_detects_current_platform(self)`

Test that current platform is detected correctly.

#### `test_platform_display_names(self)`

Test platform display names.

#### `test_mac_detection_from_request(self)`

Test detecting Mac from user request.

#### `test_windows_detection_from_request(self)`

Test detecting Windows from user request.

#### `test_linux_detection_from_request(self)`

Test detecting Linux from user request.

### TestPlatformConfig

Test platform configuration.

**Methods:**

#### `test_mac_config(self)`

Test macOS configuration.

#### `test_windows_config(self)`

Test Windows configuration.

#### `test_linux_config(self)`

Test Linux configuration.

### TestPluginInitialization

Test plugin initialization.

**Methods:**

#### `test_plugin_creates_successfully(self)`

Test plugin can be instantiated.

#### `test_plugin_finds_project_root(self)`

Test plugin finds CORTEX project root.

#### `test_plugin_has_triggers(self)`

Test plugin has proper triggers.

### TestTriggerDetection

Test trigger detection.

**Methods:**

#### `test_can_handle_mac_requests(self)`

Test plugin handles Mac-related requests.

#### `test_can_handle_windows_requests(self)`

Test plugin handles Windows-related requests.

#### `test_does_not_handle_unrelated_requests(self)`

Test plugin ignores unrelated requests.

### TestGitOperations

Test Git-related operations.

**Methods:**

#### `test_git_pull_success(self, mock_run)`

Test successful git pull.

#### `test_git_pull_failure(self, mock_run)`

Test git pull failure handling.

#### `test_count_git_changes(self)`

Test parsing git output for file changes.

### TestEnvironmentConfiguration

Test environment configuration.

**Methods:**

#### `test_configures_mac_environment(self, mock_run)`

Test Mac environment configuration.

#### `test_creates_venv_if_missing(self, mock_run)`

Test virtual environment creation when missing.

### TestDependencyVerification

Test dependency verification.

**Methods:**

#### `test_verifies_installed_packages(self, mock_run)`

Test verification of installed packages.

#### `test_get_venv_python_mac(self)`

Test getting venv Python path on Mac.

#### `test_get_venv_python_windows(self)`

Test getting venv Python path on Windows.

### TestBrainTests

Test brain test execution.

**Methods:**

#### `test_runs_brain_tests(self, mock_run)`

Test running brain tests.

#### `test_handles_test_failures(self, mock_run)`

Test handling of test failures.

### TestToolingVerification

Test tooling verification.

**Methods:**

#### `test_verifies_git(self, mock_run)`

Test Git verification.

### TestEndToEnd

End-to-end integration tests.

**Methods:**

#### `test_plugin_validates(self)`

Test plugin validation.

#### `test_full_execution_flow(self, mock_run)`

Test full execution flow (mocked).

#### `test_generates_summary(self)`

Test summary generation.

---

## tests.plugins.test_sweeper_plugin

Tests for Aggressive File Sweeper Plugin (Recycle Bin Mode)

Tests file classification, Recycle Bin execution, whitelist protection,
and integration with cleanup orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestSweeperPlugin

Test sweeper plugin functionality

**Methods:**

#### `temp_workspace(self)`

Create temporary workspace for testing

#### `sweeper(self)`

Create sweeper plugin instance

#### `test_plugin_metadata(self, sweeper)`

Test plugin metadata is correct

#### `test_classification_backup_files(self, sweeper, temp_workspace)`

Test classification of backup files

#### `test_classification_dated_duplicates(self, sweeper, temp_workspace)`

Test classification of dated duplicate files

#### `test_classification_session_reports(self, sweeper, temp_workspace)`

Test classification of session reports

#### `test_classification_reference_docs(self, sweeper, temp_workspace)`

Test classification of reference documentation

#### `test_classification_temp_files(self, sweeper, temp_workspace)`

Test classification of temporary files

#### `test_protected_directories(self, sweeper, temp_workspace)`

Test that protected directories are respected

#### `test_protected_patterns(self, sweeper, temp_workspace)`

Test that protected patterns are respected

#### `test_deletion_execution(self, mock_send2trash, sweeper, temp_workspace)`

Test Recycle Bin execution

#### `test_audit_log_creation(self, mock_send2trash, sweeper, temp_workspace)`

Test that audit log is created with Recycle Bin info

#### `test_full_execution(self, mock_send2trash, sweeper, temp_workspace)`

Test full sweeper execution with Recycle Bin

#### `test_no_backup_creation(self, sweeper, temp_workspace)`

Test that no backup/manifest files are created

#### `test_error_handling(self, mock_send2trash, sweeper, temp_workspace)`

Test error handling for inaccessible files

#### `test_scan_and_classify(self, sweeper, temp_workspace)`

Test full workspace scanning and classification

### TestSweeperIntegration

Integration tests with cleanup orchestrator

**Methods:**

#### `test_plugin_registration(self)`

Test that sweeper can be registered

#### `test_plugin_initialization(self)`

Test plugin can be initialized

#### `test_plugin_cleanup(self)`

Test plugin cleanup

---

## tests.plugins.test_system_refactor_plugin

Tests for System Refactor Plugin

Validates critical review, gap analysis, and automated refactoring functionality.

### TestPluginInitialization

Test plugin initialization and metadata.

**Methods:**

#### `test_plugin_creates_successfully(self)`

Test plugin can be instantiated.

#### `test_plugin_has_correct_metadata(self)`

Test plugin metadata is correct.

#### `test_plugin_registers_commands(self)`

Test plugin registers slash commands.

#### `test_plugin_handles_refactor_requests(self)`

Test plugin handles refactor-related requests.

#### `test_plugin_ignores_unrelated_requests(self)`

Test plugin ignores unrelated requests.

### TestCriticalReview

Test critical review functionality.

**Methods:**

#### `test_review_analyzes_test_suite(self)`

Test review analyzes test suite metrics.

#### `test_review_assesses_system_health(self)`

Test system health assessment logic.

#### `test_review_analyzes_test_categories(self)`

Test category-based test analysis.

### TestGapAnalysis

Test coverage gap analysis.

**Methods:**

#### `test_gap_analysis_checks_plugin_coverage(self)`

Test plugin coverage gap detection.

#### `test_gap_analysis_checks_entry_point_coverage(self)`

Test entry point coverage gap detection.

#### `test_gap_analysis_checks_refactor_phase(self)`

Test REFACTOR phase gap detection.

#### `test_gap_analysis_checks_module_coverage(self)`

Test module integration coverage gap detection.

#### `test_gap_analysis_checks_performance_coverage(self)`

Test performance test coverage gap detection.

### TestRefactorPhaseExecution

Test REFACTOR phase execution.

**Methods:**

#### `test_refactor_parses_tasks_from_test_files(self)`

Test parsing REFACTOR tasks from test files.

#### `test_refactor_identifies_pending_tasks(self)`

Test identification of pending REFACTOR tasks.

### TestRecommendations

Test recommendation generation.

**Methods:**

#### `test_recommendations_for_critical_health(self)`

Test recommendations for critical system health.

#### `test_recommendations_for_coverage_gaps(self)`

Test recommendations for coverage gaps.

#### `test_recommendations_for_refactor_tasks(self)`

Test recommendations for pending REFACTOR tasks.

### TestReporting

Test report generation and formatting.

**Methods:**

#### `test_report_saves_to_brain(self)`

Test report saving to brain directory.

#### `test_report_formats_as_markdown(self)`

Test markdown formatting of report.

#### `test_summary_formats_correctly(self)`

Test summary formatting.

### TestPluginExecution

Test full plugin execution workflow.

**Methods:**

#### `test_plugin_executes_full_workflow(self)`

Test complete plugin execution.

#### `test_plugin_handles_execution_errors(self)`

Test error handling during execution.

### TestPluginCleanup

Test plugin cleanup.

**Methods:**

#### `test_plugin_cleans_up_successfully(self)`

Test plugin cleanup.

### TestPluginIntegration

Test plugin integration with CORTEX.

**Methods:**

#### `test_plugin_registers_successfully(self)`

Test plugin registration.

#### `test_plugin_works_with_command_registry(self)`

Test plugin command registration.

---

## tests.response_templates.__init__

Tests for CORTEX Response Template System.

---

## tests.scripts.test_plan_cli

### `test_create_feature_plan_creates_yaml_file()`

---

## tests.staleness.__init__

Staleness Test Suite

Detects when documentation, templates, or configuration
becomes stale relative to actual implementation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

---

## tests.staleness.test_template_schema_validation

Template Schema Validation Tests

Ensures response templates stay synchronized with metric collectors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestTemplateSchemaValidation

Validate template placeholders match collector output.

**Methods:**

#### `templates(self)`

Load response templates.

#### `collector(self)`

Create metrics collector.

#### `test_schema_version_matches(self, templates)`

Verify global schema version is defined.

#### `test_brain_performance_placeholders(self, templates, collector)`

Verify brain_performance_session template placeholders exist in collector output.

#### `test_token_optimization_placeholders(self, templates, collector)`

Verify token_optimization_session template placeholders exist in collector output.

#### `test_all_template_placeholders_documented(self, templates)`

Verify all templates with context_needed=true declare required_fields.

#### `test_collector_includes_schema_version(self, collector)`

Verify collector returns schema_version in all metric methods.

#### `test_fallback_template_exists(self, templates)`

Verify fallback template exists for schema mismatches.

#### `test_no_orphaned_placeholders(self, templates, collector)`

Detect placeholders in templates that don't exist in any collector.

### TestDocumentationStaleness

Detect stale documentation that doesn't match implementation.

**Methods:**

#### `templates(self)`

Load response templates.

#### `test_entry_point_schema_version(self)`

Verify entry point mentions current schema version.

#### `test_template_last_updated_recent(self, templates)`

Verify templates have been updated recently (within 90 days).

#### `test_no_hardcoded_counts_in_templates(self, templates)`

Verify templates don't contain hardcoded module counts.

---

## tests.test_ambient_security

CORTEX 2.0 - Ambient Capture Security Tests

Purpose: Validate all security protections in the ambient capture daemon.

Tests cover:
- Path traversal prevention
- Command injection blocking
- Malicious pattern detection
- Input validation (sizes, lengths, formats)
- Symlink resolution
- File extension whitelisting
- Workspace boundary enforcement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestPathTraversalProtection

Test path traversal attack prevention.

**Methods:**

#### `test_blocks_parent_directory_traversal(self, tmp_path)`

Should block attempts to access parent directories.

#### `test_blocks_absolute_path_outside_workspace(self, tmp_path)`

Should block absolute paths outside workspace.

#### `test_allows_valid_workspace_paths(self, tmp_path)`

Should allow valid paths within workspace.

#### `test_resolves_symlinks_and_validates(self, tmp_path)`

Should resolve symlinks and validate target is in workspace.

### TestCommandInjectionPrevention

Test command injection attack prevention.

**Methods:**

#### `test_git_hook_type_whitelist(self, tmp_path)`

Should only allow whitelisted git hook types.

#### `test_git_hook_script_uses_absolute_paths(self, tmp_path)`

Should use absolute paths in hook scripts (no injection).

#### `test_subprocess_uses_list_args(self)`

Should use list arguments for subprocess (no shell injection).

### TestMaliciousPatternDetection

Test malicious command pattern detection.

**Methods:**

#### `terminal_monitor(self, tmp_path)`

Create terminal monitor for testing.

#### `test_blocks_rm_rf_commands(self, terminal_monitor)`

Should block rm -rf commands.

#### `test_blocks_eval_commands(self, terminal_monitor)`

Should block eval commands.

#### `test_blocks_curl_pipe_sh(self, terminal_monitor)`

Should block curl|sh patterns.

#### `test_blocks_fork_bombs(self, terminal_monitor)`

Should block fork bomb patterns.

#### `test_sanitizes_passwords_in_commands(self, terminal_monitor)`

Should redact passwords in command logging.

#### `test_sanitizes_tokens_in_commands(self, terminal_monitor)`

Should redact tokens in command logging.

#### `test_allows_safe_commands(self, terminal_monitor)`

Should allow safe commands.

### TestInputValidation

Test input validation and size limits.

**Methods:**

#### `test_rejects_oversized_files(self, tmp_path)`

Should reject files larger than MAX_FILE_SIZE.

#### `test_rejects_long_commands(self, tmp_path)`

Should reject commands exceeding MAX_COMMAND_LENGTH.

#### `test_validates_file_extensions(self, tmp_path)`

Should only process whitelisted file extensions.

#### `test_limits_vscode_file_list(self, tmp_path)`

Should limit number of files returned from VS Code.

#### `test_validates_json_structure(self, tmp_path)`

Should validate JSON structure in VS Code state.

### TestWorkspaceBoundaryEnforcement

Test workspace boundary enforcement.

**Methods:**

#### `test_terminal_history_must_be_in_workspace(self, tmp_path)`

Should validate terminal history file path exists.

#### `test_git_repo_must_be_valid_directory(self, tmp_path)`

Should validate git repository is a valid directory.

#### `test_file_watcher_only_monitors_workspace(self, tmp_path)`

Should only monitor files within workspace.

### TestSecureErrorHandling

Test secure error handling and logging.

**Methods:**

#### `test_does_not_expose_paths_in_errors(self, tmp_path)`

Should not expose file paths in error messages.

#### `test_git_hook_failures_are_silent(self, tmp_path)`

Git hook failures should not break git operations.

### TestSecurityConstants

Test security constants are properly defined.

**Methods:**

#### `test_file_size_limit_defined(self)`

MAX_FILE_SIZE should be defined and reasonable.

#### `test_command_length_limit_defined(self)`

MAX_COMMAND_LENGTH should be defined and reasonable.

#### `test_dangerous_patterns_defined(self)`

DANGEROUS_PATTERNS should contain common attack patterns.

---

## tests.test_css_browser_loading

Test to verify CSS can be loaded in a browser and renders correctly.

This helps debug browser caching and CSS application issues.

### TestCSSCacheBusting

Test CSS file integrity and cache-busting.

**Methods:**

#### `test_css_file_hash(self)`

Generate hash of CSS file to detect changes.

#### `test_css_specificity_check(self)`

Check that our selectors are specific enough.

#### `test_css_load_order(self)`

Verify custom.css loads after Material theme CSS.

### TestVisualDebugging

Generate debugging info for visual inspection.

**Methods:**

#### `test_generate_css_snippet(self)`

Generate a CSS snippet to test in browser DevTools.

---

## tests.test_css_styles

Tests to verify CSS styles are correctly applied to the documentation site.

This test suite validates:
1. Custom CSS file exists in built site
2. Color styles are present in the CSS
3. Navigation styles are defined
4. Main title gradient is configured
5. Code block styles use dark grey

### TestCSSStyles

Test suite for verifying CSS styles in the built documentation.

**Methods:**

#### `site_css_path(self)`

Path to the built custom CSS file.

#### `css_content(self, site_css_path)`

Load the CSS file content.

#### `test_css_file_exists(self, site_css_path)`

Verify custom.css was copied to the built site.

#### `test_sidebar_gradient_background(self, css_content)`

Verify sidebar has gradient background.

#### `test_navigation_link_color(self, css_content)`

Verify navigation links use dark grey (#374151).

#### `test_active_link_purple_gradient(self, css_content)`

Verify active navigation items have purple gradient background.

#### `test_main_title_gradient(self, css_content)`

Verify main title has colorful gradient.

#### `test_brain_emoji_in_title(self, css_content)`

Verify brain emoji is added to title.

#### `test_code_block_dark_grey(self, css_content)`

Verify code blocks use dark grey (#1F2937) instead of black.

#### `test_hover_effect_purple(self, css_content)`

Verify hover effects use purple accent color.

#### `test_navigation_title_style(self, css_content)`

Verify navigation titles have colorful styling.

#### `test_no_pure_black_in_navigation(self, css_content)`

Verify navigation doesn't use pure black (#000000).

### TestHTMLIntegration

Test suite for verifying HTML includes CSS correctly.

**Methods:**

#### `index_html_path(self)`

Path to the built index.html file.

#### `html_content(self, index_html_path)`

Load the HTML file content.

#### `test_html_file_exists(self, index_html_path)`

Verify index.html was built.

#### `test_custom_css_linked(self, html_content)`

Verify custom.css is linked in the HTML.

#### `test_google_fonts_loaded(self, html_content)`

Verify Google Fonts are loaded for ancient rules styling.

### TestColorConsistency

Test suite for verifying color consistency across the site.

**Methods:**

#### `css_content(self)`

Load the CSS file content.

#### `test_cortex_primary_color_defined(self, css_content)`

Verify CORTEX primary brand color is defined.

#### `test_cortex_accent_color_defined(self, css_content)`

Verify CORTEX accent color is defined.

#### `test_color_variables_used(self, css_content)`

Verify CSS color variables are actually used.

---

## tests.test_planning_triggers

Test Planning Trigger Detection

Tests that all documented planning trigger phrases correctly activate
the planning system via the IntentRouter.

Author: Asif Hussain
Date: 2025-11-13

### TestPlanningTriggers

Test planning trigger phrase detection

**Methods:**

#### `intent_router(self)`

Create IntentRouter instance for testing

#### `test_direct_planning_triggers(self, intent_router, trigger_phrase)`

Test direct planning request triggers

#### `test_feature_specific_triggers(self, intent_router, trigger_phrase)`

Test feature-specific planning triggers

#### `test_question_form_triggers(self, intent_router, trigger_phrase)`

Test question-form planning triggers

#### `test_collaborative_triggers(self, intent_router, trigger_phrase)`

Test collaborative planning triggers

#### `test_implicit_planning_triggers(self, intent_router, trigger_phrase)`

Test implicit planning triggers

#### `test_planning_routes_to_work_planner(self, intent_router)`

Test that PLAN intent routes to WorkPlanner agent

#### `test_all_triggers_count(self)`

Verify we have comprehensive trigger coverage

#### `test_case_insensitive_triggers(self, intent_router)`

Test that triggers work regardless of case

#### `test_trigger_in_longer_sentence(self, intent_router)`

Test that triggers work when embedded in longer sentences

#### `test_non_planning_triggers_not_detected(self, intent_router)`

Test that non-planning phrases don't trigger PLAN intent

#### `test_confidence_scoring(self, intent_router)`

Test confidence scoring for planning requests

---

## tests.test_yaml_conversion

YAML Conversion Tests - Phase 5.5.4

Tests for validating YAML conversion accuracy, performance, and token reduction.
Created: 2025-11-10
Machine: Mac (Asifs-MacBook-Pro.local)

### TestYAMLConversion

Tests for Phase 5.5 YAML conversion validation.

**Methods:**

#### `brain_path(self)`

Get path to cortex-brain directory.

#### `root_path(self)`

Get path to CORTEX root directory.

#### `operations_config(self, brain_path)`

Load operations-config.yaml

#### `slash_commands_guide(self, brain_path)`

Load slash-commands-guide.yaml

#### `cortex_operations(self, root_path)`

Load cortex-operations.yaml (in root directory)

#### `test_operations_config_structure(self, operations_config)`

Verify operations-config.yaml has correct structure.

#### `test_slash_commands_structure(self, slash_commands_guide)`

Verify slash-commands-guide.yaml has correct structure.

#### `test_cortex_operations_structure(self, cortex_operations)`

Verify cortex-operations.yaml has correct structure.

#### `test_operations_config_data_integrity(self, operations_config)`

Verify all operations have required fields.

#### `test_no_duplicate_operation_ids(self, operations_config)`

Ensure no duplicate operation IDs.

#### `test_no_duplicate_commands(self, slash_commands_guide)`

Ensure no duplicate slash commands.

#### `test_aliases_reference_valid_commands(self, slash_commands_guide)`

Verify aliases point to valid commands.

#### `test_operations_config_load_performance(self, brain_path)`

Verify operations-config.yaml loads quickly.

#### `test_slash_commands_load_performance(self, brain_path)`

Verify slash-commands-guide.yaml loads quickly (<200ms).

#### `test_cortex_operations_load_performance(self, root_path)`

Verify cortex-operations.yaml loads quickly (<300ms).

#### `test_all_yaml_files_load_together(self, brain_path, root_path)`

Verify all YAML files load together quickly.

#### `test_operations_match_yaml_definitions(self, operations_config, cortex_operations)`

Verify operations-config.yaml matches cortex-operations.yaml.

#### `test_commands_have_operation_mapping(self, slash_commands_guide, operations_config)`

Verify slash commands map to operations.

#### `test_yaml_contains_all_legacy_operations(self, cortex_operations)`

Ensure YAML includes all operations from legacy system.

#### `test_yaml_files_are_valid_yaml(self, brain_path, root_path)`

Verify all YAML files parse without errors.

#### `test_operations_have_module_structure(self, cortex_operations)`

Verify operations define proper module structure.

### TestTokenReductionPreliminary

Preliminary token reduction validation.

**Methods:**

#### `brain_path(self)`

Get path to cortex-brain directory.

#### `root_path(self)`

Get path to CORTEX root directory.

#### `test_yaml_files_exist(self, brain_path, root_path)`

Verify new YAML files were created.

#### `test_yaml_files_not_empty(self, brain_path, root_path)`

Verify YAML files have content.

### `pytest_configure(config)`

Configure pytest markers.

---

## tests.test_yaml_loading

YAML Loading Tests

Validates YAML file loading, schema validation, and error handling for CORTEX 2.0.
Tests all major YAML configuration files to ensure proper structure and content.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestYAMLLoading

Test suite for YAML file loading and validation.

**Methods:**

#### `cortex_root(self)`

Get CORTEX project root.

#### `test_brain_protection_rules_loads(self, cortex_root)`

Test that brain-protection-rules.yaml loads successfully.

#### `test_brain_protection_rules_structure(self, cortex_root)`

Test brain protection rules have required structure.

#### `test_brain_protection_rules_content(self, cortex_root)`

Test brain protection rules have valid content.

#### `test_operations_config_loads(self, cortex_root)`

Test that cortex-operations.yaml loads successfully.

#### `test_operations_config_structure(self, cortex_root)`

Test operations config has required structure.

#### `test_operations_config_content(self, cortex_root)`

Test operations config has valid content.

#### `test_operations_config_profiles(self, cortex_root)`

Test operations have valid profile configurations.

#### `test_module_definitions_loads(self, cortex_root)`

Test that module-definitions.yaml loads successfully.

#### `test_module_definitions_structure(self, cortex_root)`

Test module definitions have required structure.

#### `test_module_definitions_content(self, cortex_root)`

Test module definitions have valid content.

#### `test_module_definitions_statistics(self, cortex_root)`

Test module definitions have valid statistics.

#### `test_design_metadata_loads(self, cortex_root)`

Test that design-metadata.yaml loads successfully.

#### `test_design_metadata_structure(self, cortex_root)`

Test design metadata has required structure.

#### `test_design_metadata_phases(self, cortex_root)`

Test design metadata phases have valid content.

#### `test_yaml_handles_missing_file(self, cortex_root)`

Test YAML loading handles missing files gracefully.

#### `test_yaml_handles_malformed_content(self, tmp_path)`

Test YAML loading handles malformed content.

#### `test_yaml_handles_empty_file(self, tmp_path)`

Test YAML loading handles empty files.

#### `test_yaml_loading_performance(self, cortex_root)`

Test YAML files load within acceptable time limits.

#### `test_all_yaml_files_consistent(self, cortex_root)`

Test that related YAML files have consistent data.

#### `test_module_dependencies_valid(self, cortex_root)`

Test that module dependencies reference valid modules.

### TestYAMLTokenOptimization

Test suite for YAML token optimization metrics.

**Methods:**

#### `test_yaml_file_sizes(self, tmp_path)`

Test that YAML files are reasonably sized.

#### `test_yaml_token_estimation(self)`

Test YAML token count estimation.

---

## tests.tier0.__init__

CORTEX Tier 0 Tests

---

## tests.tier0.test_active_narrator_voice

Tests for Active Narrator Voice Enforcement

Validates that the doc refresh plugin correctly:
1. Detects passive narrator voice
2. Allows active narrator voice
3. Preserves third-person perspective
4. Applies correct transformations

### TestPassiveVoiceDetection

Test detection of passive/clinical narrator voice

**Methods:**

#### `test_detects_passive_designed(self)`

Should detect 'Asif Codeinstein designed'

#### `test_detects_passive_created(self)`

Should detect 'Asif Codeinstein created'

#### `test_detects_passive_wrote(self)`

Should detect 'He wrote routines'

#### `test_detects_passive_implemented(self)`

Should detect 'He implemented'

#### `test_detects_documentary_one_evening_while(self)`

Should detect 'One evening, while'

#### `test_detects_documentary_after_completing(self)`

Should detect 'After completing'

#### `test_detects_documentary_while_reviewing(self)`

Should detect ', while reviewing'

### TestActiveVoiceAllowed

Test that active narrator voice is allowed

**Methods:**

#### `test_allows_so_asif_built(self)`

Should allow 'So Asif built'

#### `test_allows_he_grabbed(self)`

Should allow 'He grabbed'

#### `test_allows_that_evening(self)`

Should allow 'That evening, knee-deep in'

#### `test_allows_three_hours_later(self)`

Should allow time markers with energy

#### `test_allows_asif_stared_and_decided(self)`

Should allow action-oriented decisions

### TestThirdPersonPreserved

Test that third-person perspective is preserved

**Methods:**

#### `test_allows_asif_codeinstein_name(self)`

Third-person character name should be allowed

#### `test_allows_he_his_him(self)`

Third-person pronouns should be allowed

#### `test_rejects_first_person_i(self)`

First-person 'I' should not be used in story

### TestTransformationPatterns

Test transformation pattern mappings

**Methods:**

#### `test_transformation_designed_to_built(self)`

'designed a system' → 'So Asif built a system'

#### `test_transformation_wrote_routines_to_grabbed(self)`

'wrote routines for' → 'grabbed keyboard and coded'

#### `test_transformation_one_evening_while_to_that_evening(self)`

'One evening, while' → 'That evening, knee-deep in'

#### `test_transformation_after_completing_to_complete(self)`

'After completing X, he' → 'X complete, Asif leaned back'

### TestStoryConsistency

Test story consistency validation

**Methods:**

#### `test_feature_not_mentioned_before_introduction(self)`

Features shouldn't be mentioned before their chapter

#### `test_no_deprecated_kds_references(self)`

Story should not mention deprecated 'KDS' term

#### `test_no_deprecated_monolithic_references(self)`

Story should not mention deprecated monolithic architecture

### TestNarratorVoiceAnalysis

Test narrator voice analysis functionality

**Methods:**

#### `test_calculates_violation_rate(self)`

Should calculate percentage of lines with violations

#### `test_identifies_passive_vs_documentary(self)`

Should categorize violations correctly

### TestFeatureInventory

Test feature inventory extraction

**Methods:**

#### `test_extracts_implemented_features(self)`

Should identify implemented features

#### `test_extracts_designed_features(self)`

Should identify designed but not implemented features

#### `test_maps_features_to_chapters(self)`

Should map features to correct story phases

### TestDeprecatedSectionDetection

Test detection of deprecated content

**Methods:**

#### `test_detects_kds_reference(self)`

Should detect deprecated KDS terminology

#### `test_suggests_replacement(self)`

Should suggest replacement for deprecated terms

---

## tests.tier0.test_brain_protector

CORTEX Brain Protector Tests
Phase 3 Task 3.4: Testing

Updated: November 8, 2025
Tests now validate YAML-based configuration instead of hardcoded rules.
Configuration: cortex-brain/brain-protection-rules.yaml

### TestYAMLConfiguration

Test that YAML configuration loads correctly.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_loads_yaml_configuration(self, protector)`

Verify YAML rules are loaded successfully.

#### `test_has_all_protection_layers(self, protector)`

Verify all 10 protection layers are configured.

#### `test_critical_paths_loaded(self, protector)`

Verify critical paths loaded from YAML.

#### `test_application_paths_loaded(self, protector)`

Verify application paths loaded from YAML.

#### `test_brain_state_files_loaded(self, protector)`

Verify brain state files loaded from YAML.

### TestInstinctImmutability

Test Layer 1: Instinct Immutability protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_tdd_bypass_attempt(self, protector, src_path)`

Verify BLOCKS code implementation without tests.

#### `test_detects_dod_bypass_attempt(self, protector, src_path)`

Verify BLOCKS attempts to skip Definition of Done.

#### `test_allows_compliant_changes(self, protector, src_path)`

Verify allows TDD-compliant modifications.

### TestTierBoundaryProtection

Test Layer 2: Tier Boundary protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_application_data_in_tier0(self, protector, brain_path)`

Verify BLOCKS application paths in Tier 0.

#### `test_warns_conversation_data_in_tier2(self, protector, brain_path)`

Verify WARNS on conversation data in Tier 2.

### TestSOLIDCompliance

Test Layer 3: SOLID Compliance protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_god_object_pattern(self, protector)`

Verify WARNS on God Object patterns.

#### `test_detects_hardcoded_dependencies(self, protector, src_path)`

Verify WARNS on hardcoded paths.

### TestHemisphereSpecialization

Test Layer 4: Hemisphere Specialization protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_strategic_logic_in_left_brain(self, protector)`

Verify WARNS on planning logic in tactical agents.

#### `test_detects_tactical_logic_in_right_brain(self, protector)`

Verify WARNS on execution logic in strategic agents.

### TestKnowledgeQuality

Test Layer 5: Knowledge Quality protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_high_confidence_single_event(self, protector, brain_path)`

Verify WARNS on high confidence with single occurrence.

### TestCommitIntegrity

Test Layer 6: Commit Integrity protection.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_brain_state_commit_attempt(self, protector, brain_path)`

Verify WARNS on committing brain state files.

### TestChallengeGeneration

Test challenge generation and formatting.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_generates_challenge_with_alternatives(self, protector)`

Verify challenge includes safe alternatives.

#### `test_challenge_includes_severity(self, protector)`

Verify challenge displays severity correctly.

### TestEventLogging

Test protection event logging to corpus callosum.

**Methods:**

#### `protector(self)`

Create BrainProtector with temp log file.

#### `test_logs_protection_event(self, protector)`

Verify events are logged correctly.

#### `test_log_contains_alternatives(self, protector)`

Verify logged events include suggested alternatives.

### TestMultipleViolations

Test handling of multiple simultaneous violations.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_combines_multiple_violations(self, protector)`

Verify multiple violations are detected together.

#### `test_blocked_severity_overrides_warning(self, protector, src_path)`

Verify BLOCKED takes precedence over WARNING.

### `project_root()`

Get project root path (cross-platform).

### `src_path(project_root)`

Get src directory path.

### `brain_path(project_root)`

Get cortex-brain directory path.

---

## tests.tier0.test_brain_protector_conversation_tracking

CORTEX Brain Protector: Conversation Tracking Validation

This test ensures the CRITICAL brain function of conversation tracking works correctly.
Without this, CORTEX has amnesia - the core problem we're solving.

Protection Level: TIER 0 (Core Instinct)
Rule: #24 - Conversation Memory Must Work

Tests:
1. CortexEntry.process() logs messages to Tier 1
2. conversation-history.jsonl receives updates (backward compat)
3. SQLite conversations.db is updated correctly
4. FIFO queue enforcement (20 conversation limit)
5. Session continuity across multiple messages
6. No data loss between Python invocations

### TestConversationTrackingProtection

Brain Protector: Conversation Tracking

CRITICAL: These tests must ALWAYS pass. If they fail, CORTEX has amnesia.

**Methods:**

#### `test_process_logs_to_tier1_sqlite(self, cortex_entry, temp_brain)`

CRITICAL: CortexEntry.process() MUST log messages to SQLite

Failure Impact: ❌ Complete amnesia - no conversation memory

#### `test_session_continuity_across_messages(self, cortex_entry, temp_brain)`

CRITICAL: Multiple messages in same session MUST share conversation_id

Failure Impact: ❌ Context lost between messages ("Make it purple" fails)

#### `test_fifo_queue_enforcement(self, cortex_entry, temp_brain)`

CRITICAL: FIFO queue MUST delete oldest conversation when limit reached

Failure Impact: ❌ Unbounded storage growth, performance degradation

#### `test_no_data_loss_between_invocations(self, temp_brain)`

CRITICAL: Data MUST persist between Python invocations

Failure Impact: ❌ Amnesia between Copilot Chat sessions

#### `test_backward_compatibility_with_jsonl(self, cortex_entry, temp_brain)`

OPTIONAL: Verify backward compatibility with conversation-history.jsonl

Note: Primary storage is now SQLite, but JSONL may be used for exports

#### `test_cortex_capture_script_integration(self, temp_brain)`

CRITICAL: cortex-capture.ps1 MUST successfully invoke Python tracking

Failure Impact: ❌ Copilot Chat → CORTEX bridge broken

### TestConversationTrackingHealth

Health checks for conversation tracking system

**Methods:**

#### `test_database_schema_integrity(self, temp_brain)`

Verify database schema is correct

#### `test_performance_under_load(self, cortex_entry)`

Verify tracking doesn't significantly slow down responses

### `temp_brain()`

Create temporary brain directory for testing

### `cortex_entry(temp_brain)`

Initialize CortexEntry with temp brain

---

## tests.tier0.test_brain_protector_new_rules

Brain Protection Tests - New Rules Coverage

Tests for rules added after initial brain protector implementation.
Ensures comprehensive coverage of all 31 CORTEX rules.

Created: November 9, 2025
Priority: HIGH (risk mitigation)
Phase: Phase 5 - Testing & Validation

Related:
- QA-CRITICAL-QUESTIONS-2025-11-09.md (Gap analysis)
- docs/human-readable/CORTEX-RULEBOOK.md (Rule definitions)
- cortex-brain/brain-protection-rules.yaml (Configuration)
- cortex-brain/cortex-2.0-design/34-brain-protection-test-enhancements.md (Specification)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestMachineReadableFormatEnforcement

Test Rule 5: Machine-Readable Formats

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_structured_table_in_markdown(self, protector)`

Verify WARNS when structured configuration data added to Markdown.

Scenario: Adding configuration table to Markdown instead of YAML
Expected: WARNING with suggestion to use YAML

#### `test_detects_structured_list_in_markdown(self, protector)`

Verify WARNS when structured task data added to Markdown.

Scenario: Adding task list with dependencies to Markdown
Expected: WARNING with suggestion to use YAML

#### `test_allows_narrative_markdown(self, protector)`

Verify ALLOWS narrative content in Markdown.

Scenario: Adding story/narrative to Markdown
Expected: SAFE (no violation)

### TestDefinitionOfReadyValidation

Test Rule 3: Definition of READY

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_implementation_without_dor(self, protector)`

Verify BLOCKS implementation without DoR document.

Scenario: Creating implementation file without DoR checklist
Expected: BLOCKED with suggestion to create DoR

#### `test_allows_implementation_with_dor(self, protector)`

Verify ALLOWS implementation when DoR exists.

Scenario: Implementation with corresponding DoR document
Expected: SAFE (or WARNING if other rules trigger)

#### `test_allows_bug_fix_without_dor(self, protector)`

Verify ALLOWS bug fixes without DoR requirement.

Scenario: Bug fix (modification, not new feature)
Expected: SAFE

### TestModularFileStructureLimits

Test Rule 26: Modular File Structure

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_warns_file_exceeds_soft_limit(self, protector)`

Verify WARNS when file exceeds 500 line soft limit.

Scenario: File grows to 650 lines
Expected: WARNING to consider splitting

#### `test_blocks_file_exceeds_hard_limit(self, protector)`

Verify BLOCKS when file exceeds 1000 line hard limit.

Scenario: File grows to 1200 lines
Expected: BLOCKED with suggestion to split

#### `test_allows_small_files(self, protector)`

Verify ALLOWS files within limits.

Scenario: File with 150 lines
Expected: SAFE

### TestHemisphereSeparationStrict

Test Rule 27: Hemisphere Separation

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_strategic_logic_in_left_brain(self, protector)`

Verify WARNS/BLOCKS strategic logic in left hemisphere.

Scenario: Adding architecture analysis to execution agent
Expected: WARNING/BLOCKED with suggestion to move to right brain

#### `test_detects_tactical_logic_in_right_brain(self, protector)`

Verify WARNS/BLOCKS tactical logic in right hemisphere.

Scenario: Adding code execution to architect agent
Expected: WARNING/BLOCKED with suggestion to move to left brain

#### `test_allows_corpus_callosum_coordination(self, protector)`

Verify ALLOWS coordination logic in corpus callosum.

Scenario: Adding coordination between hemispheres
Expected: SAFE (or WARNING if keywords trigger existing rules)

### TestPluginArchitectureEnforcement

Test Rule 28: Plugin Architecture

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_detects_feature_added_to_core(self, protector)`

Verify WARNS/BLOCKS new features added to core.

Scenario: Adding export feature directly to core
Expected: WARNING/BLOCKED with suggestion to use plugin

#### `test_allows_plugin_implementation(self, protector)`

Verify ALLOWS features implemented as plugins.

Scenario: Creating new plugin for feature
Expected: SAFE

#### `test_allows_core_bug_fixes(self, protector)`

Verify ALLOWS bug fixes to core without plugin requirement.

Scenario: Fixing bug in core code
Expected: SAFE

### TestStoryTechnicalRatioValidation

Test Rule 31: Story/Technical Ratio

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_warns_too_much_technical_content(self, protector)`

Verify WARNS when human-readable doc has too much technical content.

Scenario: Adding code blocks and tables to story document
Expected: WARNING to maintain 95/5 ratio

#### `test_allows_proper_story_ratio(self, protector)`

Verify ALLOWS human-readable docs with proper ratio.

Scenario: Adding narrative content with minimal technical
Expected: SAFE

#### `test_ignores_ratio_for_technical_docs(self, protector)`

Verify ratio check not applied to technical documentation.

Scenario: Adding technical content to technical doc
Expected: SAFE (ratio check only for human-readable/)

### TestIntegrationWithExistingTests

Ensure new tests integrate with existing test suite.

**Methods:**

#### `protector(self)`

Create BrainProtector instance.

#### `test_yaml_configuration_loads(self, protector)`

Verify YAML configuration loads successfully.

#### `test_all_protection_layers_active(self, protector)`

Verify all protection layers are active.

#### `test_compatible_with_existing_workflow(self, protector)`

Verify new tests don't break existing workflow.

---

## tests.tier0.test_conversation_tracking_integration

CORTEX Brain Protector: Conversation Tracking Integration Test

Tests the complete conversation tracking pipeline:
1. cortex-capture.ps1 → Python CLI → CortexEntry → SQLite
2. Validates Rule #24 (Conversation Memory Must Work)

This test runs as a standalone integration test to avoid import issues.

### `test_cortex_cli_tracks_conversations()`

CRITICAL: cortex_cli.py MUST track conversations to SQLite

Tests:
- Python CLI can be invoked
- Message is processed
- Conversation is logged to database
- Data persists

### `test_validation_command()`

Test that cortex_cli.py --validate works

### `test_powershell_capture_script()`

Test that cortex-capture.ps1 exists and has correct structure

### `main()`

Run all integration tests

---

## tests.tier0.test_entry_point_bloat

CORTEX Entry Point Bloat Prevention Test Harness

This SKULL test harness enforces strict token budget limits on the CORTEX entry point
to prevent regression back to bloated monolithic architecture.

SKULL Rule Enforced: SKULL-001 (Test Before Claim)
Protection Layer: Layer 2 (Token Budget Enforcement)

Token Limits:
- HARD LIMIT: 5,000 tokens (BLOCKING - tests fail if exceeded)
- WARNING LIMIT: 4,000 tokens (WARNING - generates alert)
- TARGET: 3,500 tokens (IDEAL - optimal performance)

Architecture Validation:
- Modular structure with #file: references
- No inline documentation (must be in shared modules)
- Response templates externalized to YAML
- Plugin documentation in separate files

Author: Asif Hussain
Created: 2025-11-10
CORTEX Version: 5.2

### TestEntryPointBloat

Test suite for CORTEX entry point bloat prevention.

**Methods:**

#### `entry_point_path(self)`

Get path to CORTEX entry point.

#### `entry_point_content(self, entry_point_path)`

Read entry point file content.

#### `calculate_tokens(self, text)`

Calculate approximate token count.

#### `test_entry_point_exists(self, entry_point_path)`

SKULL-001: Entry point file must exist.

#### `test_token_count_hard_limit(self, entry_point_content)`

SKULL-001: Entry point MUST NOT exceed hard token limit (BLOCKING).

#### `test_token_count_warning(self, entry_point_content)`

SKULL-001: Entry point should stay below warning threshold.

#### `test_token_count_target(self, entry_point_content)`

SKULL-001: Entry point should aim for target token count (IDEAL).

#### `test_line_count_limit(self, entry_point_content)`

SKULL-001: Entry point should not exceed line count limit.

#### `test_references_valid_files(self, entry_point_content, entry_point_path)`

SKULL-001: All #file: references must point to existing files.

#### `test_no_excessive_inline_docs(self, entry_point_content)`

SKULL-001: Excessive inline documentation should be modularized.

#### `test_modular_architecture_present(self, entry_point_content)`

SKULL-001: Entry point must use modular architecture (#file: references).

#### `test_response_templates_externalized(self, entry_point_content)`

SKULL-001: Response templates must be externalized to YAML.

#### `test_no_python_execution_for_help(self, entry_point_content)`

SKULL-001: Help command should use templates, not Python execution.

#### `test_version_documented(self, entry_point_content)`

SKULL-001: Entry point must document version number.

#### `test_status_documented(self, entry_point_content)`

SKULL-001: Entry point must document production status.

#### `test_copyright_present(self, entry_point_content)`

SKULL-001: Entry point must include copyright notice.

#### `test_performance_metrics(self, entry_point_content)`

SKULL-001: Log performance metrics for tracking.

### TestEntryPointArchitecture

Test suite for entry point architecture validation.

**Methods:**

#### `entry_point_path(self)`

Get path to CORTEX entry point.

#### `entry_point_content(self, entry_point_path)`

Read entry point file content.

#### `test_quick_start_section(self, entry_point_content)`

Entry point must have Quick Start section.

#### `test_help_command_documented(self, entry_point_content)`

Entry point must document help command.

#### `test_slash_commands_documented(self, entry_point_content)`

Entry point must document available slash commands.

#### `test_plugin_system_referenced(self, entry_point_content)`

Entry point must reference plugin system.

#### `test_tracking_system_referenced(self, entry_point_content)`

Entry point must reference conversation tracking.

#### `test_brain_architecture_referenced(self, entry_point_content)`

Entry point must reference brain tier architecture.

---

## tests.tier0.test_publish_faculties

SKULL-007: CORTEX Faculty Integrity Test

Ensures published CORTEX package contains ALL essential components for full operation.
This test verifies that no critical faculties are lost during publish process.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestCORTEXFaculties

Test that all CORTEX essential faculties exist in publish package.

**Methods:**

#### `publish_cortex(self)`

Path to published CORTEX package.

#### `test_publish_folder_exists(self, publish_cortex)`

Verify publish/CORTEX folder exists.

#### `test_tier0_brain_protection_exists(self, publish_cortex)`

Tier 0: Brain protection rules and protector.

#### `test_tier1_conversation_memory_exists(self, publish_cortex)`

Tier 1: Conversation memory system.

#### `test_tier2_knowledge_graph_exists(self, publish_cortex)`

Tier 2: Knowledge graph and pattern storage.

#### `test_tier3_development_context_exists(self, publish_cortex)`

Tier 3: Development context and project intelligence.

#### `test_specialist_agents_exist(self, publish_cortex)`

Specialist agents: modular architecture with strategic/tactical split.

#### `test_operations_framework_exists(self, publish_cortex)`

Operations framework and orchestrator.

#### `test_user_operations_exist(self, publish_cortex)`

User-facing operations (setup, cleanup, onboarding, etc.).

#### `test_admin_operations_excluded(self, publish_cortex)`

Admin operations should NOT exist in user package.

#### `test_plugin_system_exists(self, publish_cortex)`

Plugin system for extensibility.

#### `test_entry_points_exist(self, publish_cortex)`

CORTEX entry points for GitHub Copilot.

#### `test_documentation_exists(self, publish_cortex)`

User documentation modules.

#### `test_configuration_exists(self, publish_cortex)`

Configuration files and templates.

#### `test_setup_guide_exists(self, publish_cortex)`

SETUP-FOR-COPILOT.md inside CORTEX folder.

#### `test_legal_files_exist(self, publish_cortex)`

Legal and README files.

#### `test_no_machine_specific_config(self, publish_cortex)`

Ensure cortex.config.json (with machine paths) is NOT published.

#### `test_no_dev_artifacts(self, publish_cortex)`

Ensure development artifacts are excluded.

#### `test_cortex_fully_operational(self, publish_cortex)`

Comprehensive check: all faculties present.

---

## tests.tier0.test_publish_privacy

Tests for SKULL-006: Privacy Protection

Ensures publish script NEVER includes files with:
- Machine-specific paths (C:\, D:\, /home/, AHHOME)
- Coverage reports with machine names
- Log files with absolute paths
- Health reports with diagnostic data
- Development artifacts

Author: CORTEX SKULL Protection Layer
Created: 2025-11-12

### TestPublishPrivacy

SKULL-006: Privacy Protection Tests

**Methods:**

#### `publish_cortex_path(self)`

Get path to publish/CORTEX folder

#### `privacy_patterns(self)`

Patterns that indicate privacy leaks

#### `excluded_file_patterns(self)`

File patterns that should NEVER be published

#### `test_no_coverage_files_published(self, publish_cortex_path)`

SKULL-006: Verify no .coverage.* files in publish package

Coverage files contain machine names like .coverage.AHHOME.12345

#### `test_no_log_files_published(self, publish_cortex_path)`

SKULL-006: Verify no .log files in publish package

Log files contain absolute paths and machine-specific data

#### `test_no_health_reports_published(self, publish_cortex_path)`

SKULL-006: Verify no health-reports/ folder in publish package

Health reports contain diagnostic data for development only

#### `test_no_logs_folder_published(self, publish_cortex_path)`

SKULL-006: Verify no logs/ folder in publish package

#### `test_no_pycache_published(self, publish_cortex_path)`

SKULL-006: Verify no __pycache__ folders in publish package

#### `test_config_uses_template_not_real_paths(self, publish_cortex_path)`

SKULL-006: Verify cortex.config.template.json is used (not cortex.config.json)

The publish package should use the template file with placeholders,
not the developer's actual config with machine names.

#### `scan_file_for_privacy_leaks(self, file_path, privacy_patterns)`

Scan a file for privacy-leaking patterns

Returns:
    List of (pattern_name, matched_text) tuples

#### `test_no_absolute_paths_in_text_files(self, publish_cortex_path, privacy_patterns)`

SKULL-006: Scan all text files for machine-specific absolute paths

Checks .py, .md, .json, .yaml files for privacy leaks

Excludes documentation files that legitimately contain examples:
- brain-protection-rules.yaml (contains SKULL-006 example)
- setup-guide.md (contains example paths)
- Governance/rule files that document violations

#### `test_exclude_patterns_comprehensive(self)`

SKULL-006: Verify publish script has comprehensive exclusion patterns

#### `test_publish_script_imports_correctly(self)`

Verify publish script can be imported for testing

#### `test_no_admin_documentation_published(self, publish_cortex_path)`

SKULL-006 (CORTEX 3.0): Verify no admin documentation in publish package

Admin content that should be excluded:
- docs/images/system-design-prompts/ → Image generation prompts
- docs/images/system-design-prompts/narrative/ → PR narratives
- docs/architecture/ → Architecture diagrams
- docs/development/ → Development guides

#### `test_no_image_prompt_narratives_published(self, publish_cortex_path)`

SKULL-006 (CORTEX 3.0): Verify no image prompt narratives in publish

Specifically checks for:
- docs/images/system-design-prompts/narrative/*.md
- Any files matching *-narrative.md pattern

#### `test_no_design_documents_published(self, publish_cortex_path)`

SKULL-006 (CORTEX 3.0): Verify no design documents in publish

Checks for:
- cortex-brain/cortex-2.0-design/
- cortex-brain/cortex-3.0-design/
- Any PHASE-*.md, SESSION-*.md files

#### `test_publish_config_yaml_exists(self, publish_cortex_path)`

SKULL-006 (CORTEX 3.0): Verify publish-config.yaml exists and is valid

#### `test_no_admin_operations_published(self, publish_cortex_path)`

SKULL-006 (CORTEX 3.0): Verify no admin operation modules in publish

Admin operations that should be excluded:
- design_sync
- interactive_planning (if implemented)
- system_refactor

---

## tests.tier0.test_skull_ascii_headers

SKULL Protection Test: Banner Images and Headers in Response Templates

Tests that CORTEX banner image appears correctly in help templates ONLY.
All orchestrator operations use minimalist headers for cleaner output.

Design Decision:
- Help entry point: Banner image + minimalist header (visual impact for discovery)
- Operation orchestrators: Minimalist header with ━ characters (clean, professional)

SKULL Rules Tested:
- SKULL-006: Help templates must include banner image for visual consistency
- SKULL-007: Orchestrator templates must use minimalist headers (not ASCII art)
- SKULL-008: Banner images must be properly referenced for display

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestSKULLBannerImages

Test banner images and headers in response templates

**Methods:**

#### `response_templates_path(self)`

Path to response templates YAML

#### `response_templates(self, response_templates_path)`

Load response templates

#### `test_help_table_has_banner_image(self, response_templates)`

SKULL-006: Help table response must include CORTEX banner image

#### `test_help_detailed_has_banner_image(self, response_templates)`

SKULL-006: Detailed help must include banner image

#### `test_operation_started_has_ascii_banner(self, response_templates)`

SKULL-006: Operation start messages should have ASCII art

#### `test_orchestrator_header_has_full_banner(self, response_templates)`

SKULL-006: Orchestrator header uses minimalist style (not ASCII banner)

#### `test_banner_image_properly_formatted(self, response_templates)`

SKULL-007: Banner image must be properly referenced

#### `test_copyright_in_all_headers(self, response_templates)`

SKULL-006: All headers must include copyright notice

#### `test_ascii_banner_visual_consistency(self, response_templates)`

SKULL-007: ASCII banners should only appear in help templates

#### `test_structured_response_format(self, response_templates)`

SKULL-008: Response templates must follow structured format.

Validates:
- Header configured appropriately
- User request reflected back (📝 Your Request:)
- Understanding section (🎯 Understanding:)
- Response section (💬 Response:)
- Optional: Challenges section (⚠️ Considerations:)
- Next steps section (🔮 Next Steps:)

### TestSKULLASCIIBannerContent

Test specific ASCII banner content

**Methods:**

#### `response_templates_path(self)`

Path to response templates YAML

#### `response_templates(self, response_templates_path)`

Load response templates

#### `test_ascii_logo_structure(self, response_templates)`

SKULL-006: ASCII logo should form recognizable CORTEX letters

#### `test_banner_metadata_complete(self, response_templates)`

SKULL-006: Banner must include version, mode, timestamp placeholders

---

## tests.tier0.test_test_analyzer

CORTEX Test Analyzer Tests
===========================

Tests for test suite analysis and redundancy detection.

**Author:** Asif Hussain
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
**License:** Proprietary

### TestTestAnalyzerInitialization

Test TestAnalyzer initialization.

**Methods:**

#### `test_create_analyzer(self, temp_test_project)`

Test basic analyzer creation.

#### `test_default_test_dir(self, tmp_path)`

Test default test directory is project_root/tests.

### TestFileAnalysis

Test individual file analysis.

**Methods:**

#### `test_analyze_simple_file(self, temp_test_project)`

Test analysis of simple test file.

#### `test_extract_test_cases(self, temp_test_project)`

Test test case extraction.

#### `test_extract_fixtures(self, temp_test_project)`

Test fixture extraction.

#### `test_fixture_usage_tracking(self, temp_test_project)`

Test that fixture usage is tracked in test cases.

### TestComplexityAnalysis

Test complexity classification.

**Methods:**

#### `test_trivial_complexity(self, temp_test_project)`

Test trivial complexity classification.

#### `test_complex_classification(self, temp_test_project)`

Test complex test classification.

#### `test_complexity_distribution(self, temp_test_project)`

Test complexity distribution calculation.

### TestRedundancyDetection

Test redundancy detection algorithms.

**Methods:**

#### `test_detect_exact_duplicates(self, temp_test_project)`

Test exact duplicate detection.

#### `test_no_duplicates_in_simple_file(self, temp_test_project)`

Test that unique tests don't trigger exact duplicate detection.

#### `test_detect_semantic_duplicates(self, temp_test_project)`

Test semantic duplicate detection.

#### `test_detect_overlapping_coverage(self, temp_test_project)`

Test overlapping coverage detection.

#### `test_detect_fixture_redundancy(self, temp_test_project)`

Test fixture redundancy detection.

### TestSuiteAnalysis

Test complete suite analysis.

**Methods:**

#### `test_analyze_full_suite(self, temp_test_project)`

Test complete suite analysis.

#### `test_analysis_includes_redundancies(self, temp_test_project)`

Test that analysis detects redundancies.

#### `test_analysis_generates_recommendations(self, temp_test_project)`

Test that analysis generates recommendations.

### TestReportGeneration

Test report generation.

**Methods:**

#### `test_generate_text_report(self, temp_test_project)`

Test text report generation.

#### `test_write_report_to_file(self, temp_test_project, tmp_path)`

Test writing report to file.

#### `test_export_json(self, temp_test_project, tmp_path)`

Test JSON export.

### TestEdgeCases

Test edge cases and error handling.

**Methods:**

#### `test_empty_test_directory(self, tmp_path)`

Test analyzer with empty test directory.

#### `test_malformed_python_file(self, tmp_path)`

Test handling of malformed Python file.

#### `test_test_without_assertions(self, tmp_path)`

Test handling of test without assertions.

### TestCLIInterface

Test CLI interface.

**Methods:**

#### `test_main_function_exists(self)`

Test that main function exists for CLI.

#### `test_run_analyzer_programmatically(self, temp_test_project)`

Test running analyzer programmatically.

### TestIntegrationWithBrainProtector

Test integration points with brain protector.

**Methods:**

#### `test_can_be_imported_by_brain_protector(self)`

Test that TestAnalyzer can be imported.

#### `test_redundancy_severity_levels(self, temp_test_project)`

Test that severity levels match brain protector expectations.

#### `test_provides_actionable_recommendations(self, temp_test_project)`

Test that recommendations are actionable.

### `temp_test_project(tmp_path)`

Create a temporary test project structure.

---

## tests.tier0.test_tier_validator

Tests for Tier Validator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11

### TestTierValidatorInitialization

Test TierValidator initialization.

**Methods:**

#### `test_initializes_with_default_paths(self)`

Verify validator initializes with default paths.

#### `test_initializes_with_custom_brain_root(self, temp_brain_dir)`

Verify validator accepts custom brain root.

### TestTier0Validation

Test Tier 0 validation.

**Methods:**

#### `test_detects_missing_tier0_file(self, validator)`

Verify warning when Tier 0 file missing.

#### `test_validates_correct_tier0_structure(self, temp_brain_dir, validator)`

Verify Tier 0 with correct structure passes.

#### `test_detects_application_data_in_tier0(self, temp_brain_dir, validator)`

Verify critical violation for application data in Tier 0.

### TestTier1Validation

Test Tier 1 validation.

**Methods:**

#### `test_detects_missing_tier1_file(self, validator)`

Verify warning when Tier 1 file missing.

#### `test_validates_correct_jsonl_format(self, temp_brain_dir, validator)`

Verify Tier 1 JSONL with correct format passes.

#### `test_detects_malformed_json_in_tier1(self, temp_brain_dir, validator)`

Verify error for malformed JSON in Tier 1.

### TestTier2Validation

Test Tier 2 validation.

**Methods:**

#### `test_detects_missing_tier2_file(self, validator)`

Verify warning when Tier 2 file missing.

#### `test_validates_correct_knowledge_graph(self, temp_brain_dir, validator)`

Verify Tier 2 with correct structure passes.

#### `test_detects_raw_conversation_in_tier2(self, temp_brain_dir, validator)`

Verify critical violation for raw conversation data in Tier 2.

### TestTier3Validation

Test Tier 3 validation.

**Methods:**

#### `test_detects_missing_tier3_file(self, validator)`

Verify warning when Tier 3 file missing.

#### `test_validates_correct_dev_context(self, temp_brain_dir, validator)`

Verify Tier 3 with correct structure passes.

### TestAllTiersValidation

Test validation of all tiers.

**Methods:**

#### `test_validates_all_tiers(self, validator)`

Verify validate_all_tiers checks all tiers.

### TestReportGeneration

Test report generation.

**Methods:**

#### `test_generates_readable_report(self, validator)`

Verify report generation produces readable output.

### `temp_brain_dir(tmp_path)`

Create temporary brain directory structure.

### `validator(temp_brain_dir)`

Create TierValidator with temp brain directory.

---

## tests.tier1.__init__

CORTEX Tier 1: Working Memory (STM) Tests

---

## tests.tier1.conversations.__init__

Tests for conversation modules.

---

## tests.tier1.entities.__init__

Tests for entity modules.

---

## tests.tier1.fifo.__init__

Tests for FIFO modules.

---

## tests.tier1.messages.__init__

Tests for message modules.

---

## tests.tier1.test_conversation_import

Tests for CORTEX 3.0 Conversation Import Feature

Tests the dual-channel memory system's manual conversation import capability.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestConversationImport

Test conversation import functionality.

**Methods:**

#### `temp_db(self, tmp_path)`

Create temporary database for testing.

#### `test_import_basic_conversation(self, temp_db)`

Should import a basic conversation successfully.

#### `test_import_high_quality_conversation(self, temp_db)`

Should recognize high-quality strategic conversation.

#### `test_import_stores_quality_metadata(self, temp_db)`

Should store quality scores in database.

#### `test_import_without_workspace(self, temp_db)`

Should import conversation without workspace context.

#### `test_import_links_to_existing_session(self, temp_db)`

Should link imported conversation to existing active session.

#### `test_import_preserves_message_order(self, temp_db)`

Should preserve the order of conversation turns.

#### `test_import_detects_file_references(self, temp_db)`

Should detect and count file references in conversations.

#### `test_import_empty_conversation(self, temp_db)`

Should handle empty conversation gracefully.

### TestImportedConversationRetrieval

Test retrieving and querying imported conversations.

**Methods:**

#### `temp_db_with_imports(self, tmp_path)`

Create database with pre-imported conversations.

#### `test_retrieve_imported_conversations(self, temp_db_with_imports)`

Should retrieve all imported conversations.

#### `test_filter_by_quality_level(self, temp_db_with_imports)`

Should filter conversations by quality score.

---

## tests.tier1.test_conversation_quality

Tests for CORTEX 3.0 Conversation Quality Analyzer

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestConversationQualityAnalyzer

Test conversation quality analysis.

**Methods:**

#### `test_excellent_quality_multi_phase(self)`

Test EXCELLENT quality detection with multi-phase planning.

#### `test_good_quality_with_design(self)`

Test GOOD quality detection with design decisions.

#### `test_fair_quality_simple_task(self)`

Test FAIR quality detection for simple tasks.

#### `test_low_quality_minimal_content(self)`

Test LOW quality detection.

#### `test_challenge_flow_detection(self)`

Test challenge/accept flow detection.

#### `test_file_reference_counting(self)`

Test file reference detection and capping.

#### `test_architectural_discussion(self)`

Test architectural discussion detection.

#### `test_code_implementation_detection(self)`

Test code implementation detection.

#### `test_hint_threshold_excellent_only(self)`

Test hint threshold set to EXCELLENT only.

#### `test_multi_turn_aggregation(self)`

Test multi-turn conversation aggregation.

#### `test_reasoning_generation(self)`

Test quality reasoning text generation.

#### `test_factory_function_with_config(self)`

Test factory function with configuration.

#### `test_factory_function_defaults(self)`

Test factory function with defaults.

#### `test_score_calculation_accuracy(self)`

Test score calculation matches design.

### TestSemanticElements

Test SemanticElements dataclass.

**Methods:**

#### `test_default_initialization(self)`

Test default values.

#### `test_custom_initialization(self)`

Test custom values.

### TestQualityScore

Test QualityScore dataclass.

**Methods:**

#### `test_quality_score_structure(self)`

Test QualityScore contains expected fields.

---

## tests.tier1.test_conversation_vault

Tests for CORTEX 3.0 Conversation Vault

Tests vault storage, archival, and retrieval functionality.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestConversationVault

Test conversation vault functionality.

**Methods:**

#### `temp_vault(self, tmp_path)`

Create temporary vault for testing.

#### `test_vault_initialization(self, temp_vault)`

Should create vault directories.

#### `test_create_conversation_file(self, temp_vault)`

Should create conversation file with metadata.

#### `test_metadata_saved_separately(self, temp_vault)`

Should save metadata as JSON file.

#### `test_get_conversation_by_id(self, temp_vault)`

Should retrieve conversation file by ID.

#### `test_list_conversations(self, temp_vault)`

Should list all conversations in vault.

#### `test_quality_filtering(self, temp_vault)`

Should filter conversations by quality level.

#### `test_vault_stats(self, temp_vault)`

Should compute vault statistics.

#### `test_create_vault_manager_factory(self, tmp_path)`

Should create vault manager via factory function.

### TestVaultIntegration

Test vault integration with Tier 1 import.

**Methods:**

#### `test_vault_workflow(self, tmp_path)`

Should handle complete capture → import → archive workflow.

---

## tests.tier1.test_e2e_conversation_import

End-to-End Validation: Real Conversation Import

Tests the complete import workflow with the actual Milestone 1 completion conversation.

Author: Asif Hussain
Copyright: © 2024-2025

### `test_e2e_milestone_1_conversation_import(tmp_path)`

E2E test with real Milestone 1 completion conversation.

This validates the entire system works end-to-end.

### `test_e2e_quick_fix_conversation(tmp_path)`

E2E test with a simple low-quality conversation for contrast.

Validates that quality scoring correctly identifies quick fixes.

---

## tests.tier1.test_fusion_manager

CORTEX 3.0 Milestone 2 - Fusion Manager Tests

Test suite for the FusionManager integration API that provides
high-level fusion operations for dual-channel memory.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### TestFusionManager

Test the FusionManager integration API.

**Methods:**

#### `temp_db(self)`

Create temporary database for testing.

#### `fusion_manager(self, temp_db)`

Create FusionManager instance.

#### `sample_conversation_with_events(self, temp_db)`

Create sample conversation and correlated ambient events.

#### `test_fusion_manager_initialization(self, temp_db)`

Test FusionManager initialization.

#### `test_correlate_imported_conversation_success(self, fusion_manager, sample_conversation_with_events)`

Test successful conversation correlation.

#### `test_correlate_imported_conversation_disabled(self, fusion_manager, sample_conversation_with_events)`

Test correlation with auto_correlate disabled.

#### `test_get_conversation_development_story(self, fusion_manager, sample_conversation_with_events)`

Test development story generation.

#### `test_get_fusion_insights_with_correlations(self, fusion_manager, sample_conversation_with_events)`

Test fusion insights generation with good correlations.

#### `test_get_fusion_insights_no_recommendations(self, fusion_manager, sample_conversation_with_events)`

Test fusion insights without recommendations.

#### `test_empty_conversation_correlation(self, fusion_manager, temp_db)`

Test correlation with conversation that has no correlations.

#### `test_empty_conversation_story(self, fusion_manager, temp_db)`

Test story generation for conversation with no events.

#### `test_empty_conversation_insights(self, fusion_manager, temp_db)`

Test insights for conversation with no correlations.

#### `test_correlation_statistics_calculation(self, fusion_manager)`

Test internal correlation statistics calculation.

#### `test_correlation_summary_generation(self, fusion_manager)`

Test correlation summary text generation.

### TestFusionManagerIntegration

Test FusionManager integration with WorkingMemory.

**Methods:**

#### `temp_db(self)`

Create temporary database.

#### `test_end_to_end_fusion_workflow(self, temp_db)`

Test complete fusion workflow from import to insights.

---

## tests.tier1.test_lifecycle_manager

Tests for ConversationLifecycleManager - CORTEX 3.0 conversation lifecycle.

### TestConversationLifecycleManager

Test suite for ConversationLifecycleManager.

**Methods:**

#### `test_init_creates_schema(self, temp_db)`

Test that initializing creates lifecycle events table.

#### `test_detect_new_conversation_command(self, lifecycle_manager)`

Test detection of 'new conversation' commands.

#### `test_infer_workflow_state(self, lifecycle_manager)`

Test workflow state inference from user requests.

#### `test_workflow_state_progression(self, lifecycle_manager)`

Test default workflow state progression.

#### `test_should_create_conversation_no_active(self, lifecycle_manager)`

Test should create conversation when none active.

#### `test_should_create_conversation_explicit_new(self, lifecycle_manager)`

Test should create when user says 'new conversation'.

#### `test_should_not_create_conversation_explicit_continue(self, lifecycle_manager)`

Test should not create when user says 'continue'.

#### `test_should_not_create_conversation_default_continuation(self, lifecycle_manager)`

Test default behavior is to continue existing conversation.

#### `test_should_close_conversation_workflow_complete(self, lifecycle_manager)`

Test conversation closes when workflow complete.

#### `test_should_close_conversation_new_requested(self, lifecycle_manager)`

Test conversation closes when new conversation requested.

#### `test_log_conversation_created(self, lifecycle_manager, temp_db)`

Test logging conversation creation.

#### `test_get_conversation_history(self, working_memory)`

Test retrieving conversation lifecycle history.

### TestWorkingMemoryIntegration

Integration tests for WorkingMemory with lifecycle management.

**Methods:**

#### `test_handle_user_request_creates_session_and_conversation(self, working_memory)`

Test that handle_user_request creates session and conversation.

#### `test_handle_user_request_continues_conversation(self, working_memory)`

Test that subsequent requests continue same conversation.

#### `test_handle_user_request_explicit_new_conversation(self, working_memory)`

Test explicit 'new conversation' command creates new conversation.

#### `test_handle_user_request_workflow_progression(self, working_memory)`

Test workflow state progression through lifecycle.

#### `test_handle_user_request_with_assistant_response(self, working_memory)`

Test storing assistant response.

### `temp_db()`

Create temporary database for testing.

### `lifecycle_manager(temp_db)`

Create ConversationLifecycleManager instance.

### `working_memory(temp_db)`

Create WorkingMemory instance for integration tests.

---

## tests.tier1.test_narrative_intelligence

Tests for CORTEX 3.0 Narrative Intelligence Module
Advanced Fusion - Milestone 3

Tests story generation, contextual reasoning, and development flow analysis capabilities.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX

### TestNarrativeIntelligence

Test suite for Narrative Intelligence module

**Methods:**

#### `setUp(self)`

Set up test environment with temporary database

#### `tearDown(self)`

Clean up test environment

#### `test_initialization(self)`

Test NarrativeIntelligence initialization and database setup

#### `test_add_story_element(self)`

Test adding story elements to the database

#### `test_add_multiple_story_elements(self)`

Test adding multiple story elements

#### `test_gather_story_elements_time_range(self)`

Test gathering story elements within a time range

#### `test_gather_story_elements_file_filter(self)`

Test gathering story elements with file filtering

#### `test_analyze_story_elements(self)`

Test story element analysis functionality

#### `test_extract_themes(self)`

Test theme extraction from content

#### `test_identify_development_phases(self)`

Test development phase identification

#### `test_classify_development_phase(self)`

Test development phase classification

#### `test_detect_complexity_indicators(self)`

Test complexity indicator detection

#### `test_detect_collaboration_signals(self)`

Test collaboration signal detection

#### `test_identify_technical_discoveries(self)`

Test technical discovery identification

#### `test_generate_development_story_technical_style(self)`

Test development story generation with technical narrative style

#### `test_generate_development_story_executive_style(self)`

Test development story generation with executive narrative style

#### `test_generate_development_story_storytelling_style(self)`

Test development story generation with storytelling narrative style

#### `test_generate_story_title(self)`

Test story title generation

#### `test_calculate_narrative_confidence(self)`

Test narrative confidence calculation

#### `test_create_empty_narrative(self)`

Test empty narrative creation when no elements found

#### `test_store_and_retrieve_narrative(self)`

Test storing and retrieving narratives

#### `test_get_narrative_statistics(self)`

Test narrative statistics collection

#### `test_import_conversation_data(self)`

Test importing conversation data to create story elements

#### `test_extract_files_from_content(self)`

Test file extraction from conversation content

#### `test_extract_context_tags_from_content(self)`

Test context tag extraction from conversation content

#### `test_generate_story_with_focus_files(self)`

Test generating story with focus on specific files

---

## tests.tier1.test_pattern_learning_engine

Tests for CORTEX 3.0 Pattern Learning Engine
Advanced Fusion - Milestone 3

Tests pattern learning capabilities, file suggestion algorithms,
confidence boosting, and learning session management.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX

### TestPatternLearningEngine

Test suite for Pattern Learning Engine

**Methods:**

#### `setUp(self)`

Set up test environment with temporary database

#### `tearDown(self)`

Clean up temporary database

#### `test_initialization(self)`

Test pattern learning engine initialization

#### `test_file_mention_pattern_learning(self)`

Test learning patterns from file mentions

#### `test_context_pattern_learning(self)`

Test learning patterns from conversation context

#### `test_temporal_pattern_learning(self)`

Test learning temporal patterns from correlations

#### `test_plan_sequence_pattern_learning(self)`

Test learning patterns from plan sequences

#### `test_file_suggestion_based_on_patterns(self)`

Test file suggestion using learned patterns

#### `test_file_mention_suggestions(self)`

Test file suggestions based on file mention patterns

#### `test_confidence_boosting_from_patterns(self)`

Test correlation confidence boosting using patterns

#### `test_learning_statistics(self)`

Test learning statistics collection

#### `test_pattern_export(self)`

Test exporting learned patterns to JSON

#### `test_keyword_extraction(self)`

Test keyword extraction from conversation text

#### `test_file_mention_extraction(self)`

Test file mention extraction from text

#### `test_pattern_merging_and_similarity(self)`

Test that similar patterns get merged instead of duplicated

#### `test_empty_correlation_handling(self)`

Test handling of empty or minimal correlation data

#### `test_pattern_confidence_evolution(self)`

Test that pattern confidence evolves with usage

---

## tests.tier1.test_session_correlation

Tests for Session-Ambient Correlation (CORTEX 3.0 Phase 3)

### TestSessionAmbientCorrelation

Test session-ambient event correlation.

**Methods:**

#### `memory(self)`

Create temporary working memory instance.

#### `test_log_ambient_event(self, memory)`

Test logging ambient events linked to sessions.

#### `test_get_session_events(self, memory)`

Test retrieving all events for a session.

#### `test_filter_events_by_type(self, memory)`

Test filtering session events by type.

#### `test_filter_events_by_score(self, memory)`

Test filtering session events by minimum score.

#### `test_get_conversation_events(self, memory)`

Test getting events that occurred during a specific conversation.

#### `test_generate_session_narrative(self, memory)`

Test generating complete session narrative.

#### `test_narrative_groups_by_pattern(self, memory)`

Test that narrative groups events by pattern.

### TestSessionCorrelationIntegration

Integration tests for session correlation with handle_user_request.

**Methods:**

#### `memory(self)`

Create temporary working memory instance.

#### `test_workflow_with_ambient_events(self, memory)`

Test complete workflow: conversation + ambient events + narrative.

---

## tests.tier1.test_session_manager

Tests for SessionManager - CORTEX 3.0 session-based conversation boundaries.

### TestSessionManager

Test suite for SessionManager.

**Methods:**

#### `test_init_creates_schema(self, temp_db)`

Test that initializing SessionManager creates schema.

#### `test_create_new_session(self, session_manager)`

Test creating a new session.

#### `test_detect_existing_active_session(self, session_manager)`

Test detecting existing active session.

#### `test_idle_threshold_creates_new_session(self, session_manager, temp_db)`

Test that idle threshold triggers new session creation.

#### `test_get_active_session(self, session_manager)`

Test getting active session.

#### `test_end_session(self, session_manager)`

Test ending a session.

#### `test_increment_conversation_count(self, session_manager)`

Test incrementing conversation count.

#### `test_get_recent_sessions(self, session_manager)`

Test getting recent sessions.

#### `test_cleanup_old_sessions(self, session_manager)`

Test cleanup of old sessions.

#### `test_multiple_workspaces_independent_sessions(self, session_manager)`

Test that different workspaces have independent sessions.

#### `test_session_last_activity_updates(self, session_manager)`

Test that last_activity updates on session detection.

### `temp_db()`

Create temporary database for testing.

### `session_manager(temp_db)`

Create SessionManager instance with temp database.

---

## tests.tier1.test_smart_recommendations

Test Suite for Smart Recommendations API
CORTEX 3.0 - Advanced Fusion Features

Comprehensive testing of intelligent file prediction service with pattern-based
recommendations, context analysis, and user feedback integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0

### TestSmartRecommendations

Test suite for Smart Recommendations API

**Methods:**

#### `setUp(self)`

Set up test fixtures

#### `tearDown(self)`

Clean up test fixtures

#### `test_database_initialization(self)`

Test that database tables are created correctly

#### `test_file_recommendation_creation(self)`

Test FileRecommendation dataclass creation and serialization

#### `test_recommendation_context_creation(self)`

Test RecommendationContext dataclass creation

#### `test_pattern_based_recommendations(self)`

Test pattern-based recommendation generation

#### `test_context_similarity_recommendations(self)`

Test context-based similarity recommendations

#### `test_development_flow_recommendations(self)`

Test development phase-aware recommendations

#### `test_frequency_based_recommendations(self)`

Test frequency-based recommendations

#### `test_recency_based_recommendations(self)`

Test recency-based recommendations

#### `test_recommendation_merging(self)`

Test merging multiple recommendations for same file

#### `test_intent_boost_calculation(self)`

Test intent-based confidence boosting

#### `test_phase_boost_calculation(self)`

Test development phase-based confidence boosting

#### `test_keyword_extraction(self)`

Test keyword extraction from conversation text

#### `test_context_similarity_calculation(self)`

Test context similarity calculation

#### `test_file_type_scoring(self)`

Test file type appropriateness scoring

#### `test_get_recommendations_integration(self)`

Test complete recommendation generation flow

#### `test_file_access_recording(self)`

Test recording file access for learning

#### `test_feedback_recording(self)`

Test recording user feedback on recommendations

#### `test_analytics_generation(self)`

Test recommendation analytics generation

#### `test_optimization(self)`

Test recommendation system optimization

#### `test_cache_refresh(self)`

Test pattern cache refresh functionality

#### `test_file_types_for_phase(self)`

Test getting appropriate file types for development phase

#### `test_development_flow_score(self)`

Test development flow appropriateness scoring

---

## tests.tier1.test_temporal_correlator

CORTEX 3.0 Milestone 2 - Temporal Correlation Tests

Comprehensive test suite for the temporal correlation layer that verifies
all fusion capabilities: temporal matching, file mention correlation,
plan verification, and timeline generation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### TestTemporalCorrelator

Test the temporal correlation algorithm.

**Methods:**

#### `temp_db(self)`

Create temporary database for testing.

#### `correlator(self, temp_db)`

Create TemporalCorrelator instance.

#### `sample_conversation(self, temp_db)`

Create sample conversation for testing.

#### `sample_events(self, temp_db)`

Create sample ambient events for testing.

#### `test_correlator_initialization(self, temp_db)`

Test correlator initialization and schema setup.

#### `test_extract_file_mentions(self, correlator)`

Test file mention extraction from conversation content.

#### `test_extract_phase_mentions(self, correlator)`

Test phase mention extraction from conversation content.

#### `test_get_conversation_turns(self, correlator, sample_conversation)`

Test conversation turn extraction.

#### `test_get_ambient_events_in_window(self, correlator, sample_events)`

Test ambient event retrieval within time window.

#### `test_temporal_correlation_calculation(self, correlator)`

Test temporal correlation scoring algorithm.

#### `test_file_mention_correlation_exact_match(self, correlator)`

Test file mention correlation with exact path match.

#### `test_file_mention_correlation_filename_match(self, correlator)`

Test file mention correlation with filename-only match.

#### `test_plan_verification_correlation(self, correlator)`

Test plan verification correlation scoring.

#### `test_full_conversation_correlation(self, correlator, sample_conversation, sample_events)`

Test complete conversation correlation workflow.

#### `test_correlation_persistence(self, correlator, sample_conversation, sample_events)`

Test that correlations are stored and retrieved correctly.

#### `test_force_recalculation(self, correlator, sample_conversation, sample_events)`

Test force recalculation of existing correlations.

#### `test_conversation_timeline_generation(self, correlator, sample_conversation, sample_events)`

Test unified timeline generation.

#### `test_custom_time_window(self, temp_db)`

Test correlator with custom time window.

#### `test_no_correlations_case(self, correlator, temp_db)`

Test behavior when no correlations are found.

### TestIntegrationWithWorkingMemory

Test integration between TemporalCorrelator and WorkingMemory.

**Methods:**

#### `temp_db(self)`

Create temporary database.

#### `test_working_memory_temporal_correlation_integration(self, temp_db)`

Test that WorkingMemory can use temporal correlation features.

#### `test_temporal_correlation_api_extension(self, temp_db)`

Test potential API extension for WorkingMemory temporal features.

---

## tests.tier2.__init__

CORTEX Tier 2 Tests Package

---

## tests.tier2.knowledge_graph.__init__

Tests for Knowledge Graph modular components.

---

## tests.tier2.test_namespace_protection

Comprehensive tests for namespace-based knowledge boundary protection.

Tests namespace isolation, write protection, and correct storage routing.
Ensures CORTEX framework patterns stay separate from workspace patterns.

CRITICAL: These tests validate SKULL protection against knowledge contamination.

### TestNamespaceWriteProtection

Test that cortex.* namespace is write-protected from user code.

**Methods:**

#### `temp_kg(self, tmp_path)`

Create temporary knowledge graph for testing.

#### `test_cortex_namespace_blocked_from_user_code(self, temp_kg)`

CRITICAL: User code CANNOT write to cortex.* namespace.

This prevents workspace patterns from contaminating framework knowledge.

#### `test_cortex_namespace_allowed_from_framework_code(self, temp_kg)`

CORTEX framework code CAN write to cortex.* namespace.

Framework must be able to store its own patterns.

#### `test_workspace_namespace_always_allowed(self, temp_kg)`

User code CAN write to workspace.* namespace freely.

This is the designated space for user application patterns.

#### `test_namespace_required_on_write(self, temp_kg)`

All patterns MUST have a namespace when written.

No more ambiguous storage without clear boundaries.

### TestNamespaceIsolation

Test that namespaces isolate patterns correctly.

**Methods:**

#### `populated_kg(self, tmp_path)`

Knowledge graph with patterns in multiple namespaces.

#### `test_query_cortex_namespace_only(self, populated_kg)`

Query cortex.* should return ONLY framework patterns.

No workspace contamination in results.

#### `test_query_workspace_namespace_only(self, populated_kg)`

Query workspace.app1.* should return ONLY app1 patterns.

No CORTEX or other workspace contamination.

#### `test_query_specific_namespace(self, populated_kg)`

Query exact namespace returns only matching patterns.

#### `test_query_all_namespaces_with_wildcard(self, populated_kg)`

Query with * wildcard returns all patterns (admin use case).

#### `test_cross_workspace_isolation(self, populated_kg)`

workspace.app1.* CANNOT see workspace.app2.* patterns.

Critical for multi-project CORTEX usage.

### TestCorrectStorageRouting

Test that patterns are stored in the correct namespace automatically.

**Methods:**

#### `temp_kg(self, tmp_path)`

Create temporary knowledge graph.

#### `test_cortex_pattern_routed_to_cortex_namespace(self, temp_kg)`

When CORTEX framework learns a pattern, it goes to cortex.* namespace.

#### `test_workspace_pattern_routed_to_workspace_namespace(self, temp_kg)`

When user's workspace learns a pattern, it goes to workspace.* namespace.

#### `test_auto_namespace_detection_from_source(self, temp_kg)`

FUTURE: Knowledge graph auto-detects namespace from pattern source.

Example: If source is "tests/fixtures/mock-project/...", 
namespace should be "workspace.mock-project.*"

### TestNamespacePriorityBoosting

Test that namespace priority boosting works correctly (already implemented).

**Methods:**

#### `populated_kg(self, tmp_path)`

Knowledge graph with patterns of varying relevance.

#### `test_current_workspace_gets_highest_priority(self, populated_kg)`

When working on workspace.myapp, its patterns get 2.0x boost.

Even if other patterns have higher confidence, current workspace wins.

#### `test_cortex_patterns_get_medium_priority(self, populated_kg)`

CORTEX patterns get 1.5x boost (second priority after current workspace).

#### `test_other_workspaces_get_lowest_priority(self, populated_kg)`

Other workspace patterns get 0.5x boost (lowest priority).

### TestNamespaceProtectionRules

Test brain protection rules for namespace violations.

**Methods:**

#### `test_brain_protector_detects_namespace_violation(self)`

Brain Protector should detect attempts to write to cortex.* namespace.

This tests integration with brain-protection-rules.yaml Layer 6.

#### `test_namespace_mixing_blocked(self)`

A pattern CANNOT belong to multiple namespaces.

Cross-namespace references must use explicit links, not multi-namespace.

### TestMigrationScenarios

Test migration of existing patterns to namespaces.

**Methods:**

#### `test_detect_cortex_patterns_for_migration(self)`

Migration script must correctly identify CORTEX framework patterns.

Patterns like "validation_insights", "workflow_patterns" → cortex.*

#### `test_migration_preserves_pattern_data(self)`

Migration adds namespace prefix WITHOUT losing pattern data.

### TestNamespaceProtectionIntegration

End-to-end test of namespace protection system.

**Methods:**

#### `full_kg(self, tmp_path)`

Fully configured knowledge graph with namespace protection.

#### `test_complete_namespace_workflow(self, full_kg)`

Test complete workflow: write protection, isolation, correct routing.

This is the ultimate validation of namespace-based boundaries.

---

## tests.tier2.test_oracle_crawler

Tests for Oracle Database Schema Crawler

Test Strategy:
- Mock oracledb module to avoid requiring actual Oracle instance
- Test metadata extraction logic (tables, columns, indexes, constraints)
- Validate pattern conversion (Oracle schema -> CORTEX knowledge pattern)
- Verify Tier 2 integration (scope='application', namespace handling)
- Test error handling (connection failures, missing metadata)

Run: python -m pytest CORTEX/tests/tier2/test_oracle_crawler.py -v

### TestOracleCrawlerInit

Test Oracle crawler initialization.

**Methods:**

#### `test_initializes_with_connection_params(self)`

Should store connection parameters.

#### `test_extracts_namespace_from_dsn(self)`

Should extract database name from DSN for namespace.

#### `test_accepts_custom_namespace(self)`

Should allow custom namespace override.

### TestOracleConnection

Test Oracle database connection handling.

**Methods:**

#### `test_connects_to_oracle(self, mock_oracledb)`

Should establish Oracle connection.

#### `test_handles_connection_failure(self, mock_oracledb)`

Should raise ConnectionError on failure.

#### `test_disconnects_from_oracle(self, mock_oracledb)`

Should close Oracle connection.

### TestSchemaExtraction

Test Oracle schema metadata extraction.

**Methods:**

#### `test_extracts_tables_for_current_user(self, mock_oracledb)`

Should extract tables for current user by default.

#### `test_extracts_columns_with_metadata(self, mock_oracledb)`

Should extract column metadata including types and comments.

#### `test_extracts_indexes_with_columns(self, mock_oracledb)`

Should extract indexes with column information.

#### `test_extracts_foreign_key_constraints(self, mock_oracledb)`

Should extract FK constraints with referenced table info.

### TestPatternConversion

Test conversion of Oracle schema to CORTEX patterns.

**Methods:**

#### `test_converts_table_to_pattern(self)`

Should convert OracleTable to knowledge pattern.

#### `test_pattern_includes_foreign_key_references(self)`

Should include FK reference information in pattern.

### TestTier2Integration

Test integration with CORTEX Tier 2 knowledge graph.

**Methods:**

#### `test_stores_patterns_in_knowledge_graph(self)`

Should store patterns with correct scope and namespace.

#### `test_handles_multiple_tables(self)`

Should store multiple table schemas as separate patterns.

#### `test_uses_custom_namespace(self)`

Should use custom namespace when provided.

### TestErrorHandling

Test error handling and edge cases.

**Methods:**

#### `test_requires_connection_before_extract(self)`

Should raise error if extracting without connection.

#### `test_handles_empty_schema(self, mock_oracledb)`

Should handle schema with no tables gracefully.

#### `test_handles_storage_failure(self)`

Should continue storing even if one pattern fails.

### TestOracleIntegration

Integration tests with real Oracle database.

**Methods:**

#### `test_real_oracle_connection(self)`

Test with actual Oracle instance.

---

## tests.tier2.test_pattern_detector

Tests for Change Pattern Detector (Phase 4.4)

Tests pattern detection for different file changes.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### TestChangePatternDetector

Test suite for ChangePatternDetector.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `teardown_method(self)`

Clean up test fixtures.

#### `test_detect_documentation_pattern(self)`

Should detect documentation changes.

#### `test_detect_rst_documentation(self)`

Should detect .rst documentation.

#### `test_detect_config_json(self)`

Should detect JSON configuration changes.

#### `test_detect_config_yaml(self)`

Should detect YAML configuration changes.

#### `test_detect_config_env(self)`

Should detect environment file changes.

#### `test_detect_feature_created(self)`

Should detect new file creation as feature.

#### `test_detect_refactor_deleted(self)`

Should detect file deletion as refactor.

#### `test_detect_bugfix_small_change(self)`

Should detect small changes as bug fix.

#### `test_detect_refactor_balanced_changes(self)`

Should detect balanced add/delete as refactor.

#### `test_detect_feature_many_additions(self)`

Should detect many additions as feature.

#### `test_detect_unknown_no_diff(self)`

Should return unknown when no diff available.

#### `test_cache_git_diff(self)`

Should cache git diff results.

#### `test_cache_size_limit(self)`

Should limit cache size to 100 entries.

#### `test_handle_git_not_available(self)`

Should handle when git is not available.

#### `test_handle_git_timeout(self)`

Should handle git command timeout.

#### `test_handle_malformed_event(self)`

Should handle malformed events gracefully.

#### `test_clear_cache(self)`

Should clear diff cache.

### TestPatternDetectorIntegration

Integration tests for pattern detector.

**Methods:**

#### `test_pattern_types_defined(self)`

Should define all pattern types.

#### `test_all_patterns_are_strings(self)`

All pattern constants should be strings.

---

## tests.tier2.test_scorer_summarizer

Tests for Activity Scorer and Auto-Summarizer (Phase 4.4)

Tests activity scoring and summarization components.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### TestActivityScorer

Test suite for ActivityScorer.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_score_python_file(self)`

Should give high score to Python source files.

#### `test_score_typescript_file(self)`

Should give high score to TypeScript files.

#### `test_score_config_file(self)`

Should give medium score to config files.

#### `test_score_documentation(self)`

Should give lower score to documentation.

#### `test_score_created_file(self)`

Should give high magnitude score to created files.

#### `test_score_deleted_file(self)`

Should give significant score to deleted files.

#### `test_score_modified_file(self)`

Should give moderate score to modified files.

#### `test_score_feature_pattern(self)`

Should give highest pattern score to features.

#### `test_score_bugfix_pattern(self)`

Should give medium-high pattern score to bug fixes.

#### `test_score_core_source(self)`

Should give highest importance to core source.

#### `test_score_test_files(self)`

Should give high importance to test files.

#### `test_score_scripts(self)`

Should give moderate importance to scripts.

#### `test_score_docs_path(self)`

Should give lower importance to docs directory.

#### `test_score_high_priority_change(self)`

Should give 80+ score to high-priority changes.

#### `test_score_low_priority_change(self)`

Should give <50 score to low-priority changes.

#### `test_score_capped_at_100(self)`

Should cap scores at 100.

#### `test_score_unknown_pattern(self)`

Should handle unknown patterns.

#### `test_score_unknown_file_type(self)`

Should handle unknown file types.

#### `test_score_malformed_event(self)`

Should handle malformed events gracefully.

### TestAutoSummarizer

Test suite for AutoSummarizer.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `test_summarize_created_event(self)`

Should summarize file creation.

#### `test_summarize_modified_event(self)`

Should summarize file modification.

#### `test_summarize_deleted_event(self)`

Should summarize file deletion.

#### `test_summarize_high_priority_event(self)`

Should mark high-priority events.

#### `test_summarize_normal_priority_event(self)`

Should not mark normal-priority events.

#### `test_summarize_empty_batch(self)`

Should handle empty batch.

#### `test_summarize_single_event_batch(self)`

Should summarize single-event batch.

#### `test_summarize_multi_event_batch(self)`

Should summarize multiple events.

#### `test_batch_summary_includes_avg_score(self)`

Should include average score in batch summary.

#### `test_summarize_session(self)`

Should summarize work session.

#### `test_session_summary_includes_high_priority(self)`

Should mention high-priority changes in session.

#### `test_session_summary_includes_top_files(self)`

Should list most active files.

#### `test_summarize_malformed_event(self)`

Should handle malformed events gracefully.

#### `test_summarize_long_filenames(self)`

Should handle long filenames.

### TestScorerSummarizerIntegration

Integration tests for scorer and summarizer.

**Methods:**

#### `test_score_and_summarize_flow(self)`

Should score and summarize events in sequence.

---

## tests.tier2.test_smart_filter

Tests for Smart File Filter (Phase 4.4)

Tests intelligent noise filtering for ambient capture.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

### TestSmartFileFilter

Test suite for SmartFileFilter.

**Methods:**

#### `setup_method(self)`

Set up test fixtures.

#### `teardown_method(self)`

Clean up test fixtures.

#### `test_filter_pycache(self)`

Should filter __pycache__ files.

#### `test_filter_pyc_files(self)`

Should filter .pyc files.

#### `test_filter_node_modules(self)`

Should filter node_modules directory.

#### `test_filter_dist_build(self)`

Should filter dist/ and build/ directories.

#### `test_filter_temp_files(self)`

Should filter .tmp and .temp files.

#### `test_filter_swap_files(self)`

Should filter .swp files (Vim).

#### `test_filter_ds_store(self)`

Should filter .DS_Store files (macOS).

#### `test_filter_generated_marker(self)`

Should filter files with @generated marker.

#### `test_filter_autogenerated_marker(self)`

Should filter files with autogenerated marker.

#### `test_filter_generated_directory(self)`

Should filter files in generated/ directory.

#### `test_filter_git_directory(self)`

Should filter .git directory files.

#### `test_filter_vscode_files(self)`

Should filter .vscode directory files.

#### `test_filter_idea_files(self)`

Should filter .idea directory files.

#### `test_filter_large_files(self)`

Should filter files larger than max size.

#### `test_filter_empty_files(self)`

Should filter empty files.

#### `test_allow_normal_size_files(self)`

Should allow files within size limit.

#### `test_filter_binary_files(self)`

Should filter binary files.

#### `test_allow_python_source(self)`

Should allow Python source files.

#### `test_allow_markdown_docs(self)`

Should allow Markdown documentation.

#### `test_allow_json_config(self)`

Should allow JSON configuration files.

#### `test_allow_yaml_files(self)`

Should allow YAML files.

#### `test_cache_generated_marker_check(self)`

Should cache generated marker checks.

#### `test_cache_size_limit(self)`

Should limit cache size.

#### `test_filtering_performance(self)`

Should filter files quickly (<5ms per file).

#### `test_handle_nonexistent_file(self)`

Should handle nonexistent files gracefully.

#### `test_handle_permission_error(self)`

Should handle permission errors gracefully.

#### `test_handle_unicode_filename(self)`

Should handle Unicode filenames.

### TestSmartFilterIntegration

Integration tests for SmartFileFilter.

**Methods:**

#### `test_filter_stats(self)`

Should return filter statistics.

---

## tests.tier3.__init__

CORTEX Tier 3 Tests Initialization

---

## tests.tier3.analysis.__init__

Tier 3 analysis tests.

---

## tests.tier3.metrics.__init__

Tier 3 metrics tests.

---

## tests.tier3.metrics.test_brain_metrics_collector

Tests for Brain Metrics Collector

Ensures that the brain metrics collector properly aggregates metrics from
Tier 1, 2, and 3, and calculates token efficiency correctly.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

### TestBrainMetricsCollector

Test suite for BrainMetricsCollector

**Methods:**

#### `temp_brain_dir(self)`

Create temporary cortex-brain directory structure

#### `mock_tier1_db(self, temp_brain_dir)`

Create mock Tier 1 database

#### `mock_tier2_db(self, temp_brain_dir)`

Create mock Tier 2 database

#### `collector(self, mock_tier1_db, mock_tier2_db, temp_brain_dir)`

Create BrainMetricsCollector with mocked config

#### `test_schema_version(self, collector)`

Test that schema version is correctly declared

#### `test_get_brain_performance_metrics(self, collector)`

Test comprehensive brain performance metrics retrieval

#### `test_get_token_optimization_metrics(self, collector)`

Test token efficiency metric calculations

#### `test_get_brain_health_diagnostics(self, collector)`

Test brain health diagnostic reporting

#### `test_tier1_metrics_accuracy(self, collector)`

Test accuracy of Tier 1 metric extraction

#### `test_tier2_metrics_accuracy(self, collector)`

Test accuracy of Tier 2 metric extraction

#### `test_derived_metrics_calculation(self, collector)`

Test derived metrics are correctly calculated

#### `test_token_efficiency_terminology(self, collector)`

Test that all metrics use 'token-efficiency' terminology

#### `test_health_warnings_generation(self, collector)`

Test health warning generation

#### `test_health_recommendations_generation(self, collector)`

Test health recommendation generation

#### `test_missing_tier3_db_handled_gracefully(self, collector)`

Test that missing Tier 3 DB doesn't break collection

#### `test_corrupted_db_error_handling(self, temp_brain_dir)`

Test error handling for corrupted database

#### `test_metrics_match_template_schema(self, collector)`

Test that metrics keys match response-templates.yaml expectations

#### `test_token_efficiency_calculations(self, collector)`

Test token efficiency percentage calculations

#### `test_concurrent_access_safety(self, collector)`

Test that metrics collector is safe for concurrent access

#### `test_wiring_to_tier_apis(self, mock_tier1_db, mock_tier2_db)`

Test that collector is correctly wired to Tier APIs

#### `test_integration_with_response_templates(self, collector)`

Test integration point with response templates

### TestTokenEfficiencyMetricsFile

Test the renamed token-efficiency-metrics.yaml file

**Methods:**

#### `test_token_efficiency_metrics_file_exists(self)`

Test that token-efficiency-metrics.yaml exists

#### `test_old_efficiency_metrics_removed(self)`

Test that old efficiency-metrics.yaml no longer exists

### TestOperationHeaderFormatter

Test the consolidated operation_header_formatter.py

**Methods:**

#### `test_operation_header_formatter_exists(self)`

Test that operation_header_formatter.py exists

#### `test_can_import_operation_header_formatter(self)`

Test that OperationHeaderFormatter can be imported

#### `test_backward_compatibility_aliases(self)`

Test backward compatibility aliases

#### `test_format_minimalist_header(self)`

Test minimalist header formatting

#### `test_format_completion_footer(self)`

Test completion footer formatting

---

## tests.tier3.storage.__init__

Tier 3 storage tests.

---

## tests.workflows.__init__

CORTEX Workflow Tests

Unit and integration tests for workflow orchestration system.

---

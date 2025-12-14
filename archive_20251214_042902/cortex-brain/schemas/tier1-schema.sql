-- ============================================================================
-- CORTEX Tier 1: Working Memory Schema
-- Short-term memory with FIFO queue management
-- ============================================================================
-- 
-- Schema Version: 7.1.0
-- Last Updated: December 2, 2025
-- Author: Asif Hussain
-- Phase: Phase 7.1 - Tier 1 Schema Completion
--
-- Purpose: Complete schema documentation for Tier 1 working memory including
--          all tables, indexes, and relationships
--
-- Tables:
--   1. conversations - Conversation history with workflow state tracking
--   2. messages - Individual messages within conversations
--   3. entities - Named entity tracking (files, functions, projects)
--   4. conversation_entities - Entity-conversation relationships
--   5. user_profile - User interaction preferences
--   6. working_memory - TTL-based temporary context storage (NEW in Phase 7.1)
--   7. sessions - Session tracking for conversation boundaries
--   8. ambient_events - Background activity capture
--   9. application - Application name requirement
--  10. swagger_contexts - Scope approval gate contexts
--  11. eviction_log - FIFO eviction tracking
--  12. conversation_lifecycle_events - Conversation state transitions
--
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Table: conversations
-- Purpose: Store conversation history with FIFO queue management
-- FIFO: 70-conversation limit (Phase 7.5), oldest evicted to Tier 2
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 0,
    summary TEXT,
    tags TEXT,
    session_id TEXT,
    last_activity TIMESTAMP,
    workflow_state TEXT,
    conversation_type TEXT DEFAULT 'interactive',
    import_source TEXT,
    quality_score REAL DEFAULT 0.0,
    semantic_elements TEXT DEFAULT '{}'
);

-- Performance indexes for conversations
CREATE INDEX IF NOT EXISTS idx_conversations_created 
ON conversations(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_active 
ON conversations(is_active);

CREATE INDEX IF NOT EXISTS idx_conversations_session 
ON conversations(session_id);

CREATE INDEX IF NOT EXISTS idx_conversations_last_activity 
ON conversations(last_activity DESC);

-- ----------------------------------------------------------------------------
-- Table: messages
-- Purpose: Store individual messages within conversations
-- Relationship: N messages : 1 conversation
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Performance index for messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation 
ON messages(conversation_id);

-- ----------------------------------------------------------------------------
-- Table: entities
-- Purpose: Track named entities (files, functions, classes, projects)
-- Used for: Entity extraction, access tracking, relevance scoring
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    file_path TEXT,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 1,
    UNIQUE(entity_type, entity_name, file_path)
);

-- Performance indexes for entities
CREATE INDEX IF NOT EXISTS idx_entities_type 
ON entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_entities_accessed 
ON entities(last_accessed DESC);

-- ----------------------------------------------------------------------------
-- Table: conversation_entities
-- Purpose: Many-to-many relationship between conversations and entities
-- Relationship: N conversations : M entities
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_entities (
    conversation_id TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    relevance_score REAL DEFAULT 1.0,
    PRIMARY KEY (conversation_id, entity_id),
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
    FOREIGN KEY (entity_id) REFERENCES entities(id)
);

-- ----------------------------------------------------------------------------
-- Table: user_profile
-- Purpose: Store user interaction preferences (CORTEX 3.2.1)
-- Singleton: Only one profile per user (id = 1)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
    experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
    response_detail TEXT NOT NULL CHECK(response_detail IN ('concise', 'balanced', 'verbose')) DEFAULT 'balanced',
    tech_stack_preference TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    persistent_flag BOOLEAN NOT NULL DEFAULT 1
);

-- Enforce single profile
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id);

-- ----------------------------------------------------------------------------
-- Table: working_memory (NEW in Phase 7.1)
-- Purpose: TTL-based temporary context storage for active work
-- TTL: Expires after specified duration, auto-cleanup
-- Use Cases: Feature work in progress, temporary state, session context
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS working_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    context_type TEXT NOT NULL,
    metadata TEXT
);

-- Performance indexes for working_memory
CREATE INDEX IF NOT EXISTS idx_working_memory_expires 
ON working_memory(expires_at);

CREATE INDEX IF NOT EXISTS idx_working_memory_type 
ON working_memory(context_type);

CREATE INDEX IF NOT EXISTS idx_working_memory_key 
ON working_memory(key);

-- ----------------------------------------------------------------------------
-- Table: sessions
-- Purpose: Session boundary tracking for conversation grouping
-- Used for: Idle gap detection, session-based context
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    conversation_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1
);

-- ----------------------------------------------------------------------------
-- Table: ambient_events
-- Purpose: Capture background activity for context awareness
-- Used for: Ambient conversation capture, activity correlation
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ambient_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT
);

-- ----------------------------------------------------------------------------
-- Table: application
-- Purpose: Store application name requirement (Phase 1.3)
-- Singleton: Only one application per workspace (id = 1)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS application (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Enforce single application
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_application ON application(id);

-- ----------------------------------------------------------------------------
-- Table: swagger_contexts
-- Purpose: Scope approval gate contexts (CORTEX 3.2.1)
-- Used for: Complexity tracking, scope boundary management
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS swagger_contexts (
    context_id TEXT PRIMARY KEY,
    complexity REAL NOT NULL,
    scope_boundary TEXT NOT NULL,
    team_size INTEGER DEFAULT 1,
    velocity REAL,
    status TEXT NOT NULL DEFAULT 'awaiting_approval',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- Table: eviction_log
-- Purpose: Track FIFO evictions for audit and analytics
-- Used for: FIFO queue management, eviction history
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS eviction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT
);

-- ----------------------------------------------------------------------------
-- Table: conversation_lifecycle_events
-- Purpose: Track conversation state transitions
-- Used for: Workflow state tracking, lifecycle analytics
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS conversation_lifecycle_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    from_state TEXT,
    to_state TEXT NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- ----------------------------------------------------------------------------
-- Table: test_intents (Phase 3: TDD Workflow Enhancement)
-- Purpose: Store test requirements and edge cases during RED phase
-- Source: tdd_red_phase (validates no git dependency)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS test_intents (
    intent_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    requirement TEXT NOT NULL,
    edge_cases_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source TEXT DEFAULT 'tdd_red_phase'
);

-- Performance index for test_intents
CREATE INDEX IF NOT EXISTS idx_test_intents_feature 
ON test_intents(feature_name);

CREATE INDEX IF NOT EXISTS idx_test_intents_source 
ON test_intents(source);

-- ============================================================================
-- Schema Version Tracking (Phase 7.1: Migration System)
-- ============================================================================

-- Table: schema_migrations
-- Purpose: Track applied database migrations for zero-downtime evolution
-- Managed by: src/tier1/schema_migrations.py (MigrationManager)
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL CHECK(status IN ('applied', 'rolled_back', 'failed')),
    error_message TEXT,
    execution_time_ms INTEGER
);

-- Performance indexes for schema_migrations
CREATE INDEX IF NOT EXISTS idx_migrations_version 
ON schema_migrations(version);

CREATE INDEX IF NOT EXISTS idx_migrations_status 
ON schema_migrations(status);

-- ============================================================================
-- Performance Notes
-- ============================================================================
--
-- Query Performance Targets:
--   - Recent conversations: <100ms (FIFO with 70 limit)
--   - Entity lookups: <50ms (indexed by type and access time)
--   - Message retrieval: <75ms (indexed by conversation_id)
--   - Working memory: <25ms (indexed by key and expiration)
--   - Session queries: <50ms (indexed by session_id)
--
-- Storage Estimates:
--   - 70 conversations: ~5MB (with messages)
--   - Entities: ~1MB (typical project)
--   - Working memory: ~500KB (active contexts)
--   - Total: ~7MB typical, <100MB maximum
--
-- Maintenance:
--   - FIFO eviction: Automatic when conversation count > 70
--   - Working memory cleanup: Automatic on expiration
--   - Vacuum: Recommended monthly for optimal performance
--
-- ============================================================================

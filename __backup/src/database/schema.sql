-- ==============================================================================
-- CORTEX 6.0 StateManager Database Schema
-- ==============================================================================
-- Purpose: SQLite schema for state management with WAL mode and optimistic locking
-- Author: Asif Hussain
-- Version: 6.0.0
-- Created: 2026-01-07
-- 
-- Features:
--   - WAL mode for concurrent read/write
--   - Optimistic locking via version column
--   - Checkpoint/resume functionality
--   - Comprehensive indexing for performance
-- ==============================================================================

-- Enable WAL mode (must be executed separately via PRAGMA)
-- PRAGMA journal_mode=WAL;
-- PRAGMA synchronous=NORMAL;

-- ==============================================================================
-- CORE STATE TABLES
-- ==============================================================================

-- Generic key-value state storage with versioning
CREATE TABLE IF NOT EXISTS state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,                    -- JSON serialized value
    version INTEGER NOT NULL DEFAULT 1,     -- Optimistic locking version
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    expires_at TEXT,                        -- Optional TTL
    metadata TEXT                           -- JSON metadata
);

-- TODO items for execution tracking
CREATE TABLE IF NOT EXISTS todo_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT NOT NULL UNIQUE,           -- External identifier (e.g., "task-2.1")
    feature_id TEXT NOT NULL,               -- Feature this belongs to
    phase_id INTEGER NOT NULL,              -- Phase number
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'NOT_STARTED', -- NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED, SKIPPED
    priority TEXT NOT NULL DEFAULT 'P1_HIGH',   -- P0_CRITICAL, P1_HIGH, P2_MEDIUM, P3_LOW
    version INTEGER NOT NULL DEFAULT 1,     -- Optimistic locking
    tdd_phase TEXT,                         -- RED, GREEN, REFACTOR
    estimated_minutes INTEGER,
    actual_minutes INTEGER,
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    dependencies TEXT,                      -- JSON array of item_ids
    validation_result TEXT,                 -- JSON validation details
    metadata TEXT                           -- JSON metadata
);

-- Execution state for orchestrators and workflows
CREATE TABLE IF NOT EXISTS execution_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL UNIQUE,      -- Correlation ID
    orchestrator TEXT NOT NULL,             -- Orchestrator name
    workflow_type TEXT,                     -- Type of workflow
    status TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    version INTEGER NOT NULL DEFAULT 1,     -- Optimistic locking
    phase TEXT,                             -- Current phase
    step INTEGER DEFAULT 0,                 -- Current step in phase
    context TEXT,                           -- JSON execution context
    result TEXT,                            -- JSON result data
    error TEXT,                             -- Error message if failed
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    metadata TEXT                           -- JSON metadata
);

-- ==============================================================================
-- CHECKPOINT TABLES
-- ==============================================================================

-- Checkpoints for resume functionality
CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    checkpoint_type TEXT NOT NULL DEFAULT 'MANUAL', -- MANUAL, AUTO, PHASE_COMPLETE
    state_snapshot TEXT NOT NULL,           -- JSON snapshot of relevant state
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    created_by TEXT,                        -- Who/what created the checkpoint
    tags TEXT,                              -- JSON array of tags
    metadata TEXT                           -- JSON metadata
);

-- Checkpoint references - links checkpoints to specific state entries
CREATE TABLE IF NOT EXISTS checkpoint_refs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id TEXT NOT NULL,
    ref_type TEXT NOT NULL,                 -- 'state', 'todo_item', 'execution_state'
    ref_id TEXT NOT NULL,                   -- ID in the referenced table
    ref_version INTEGER NOT NULL,           -- Version at checkpoint time
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(checkpoint_id) ON DELETE CASCADE
);

-- ==============================================================================
-- AUDIT & TRACKING TABLES
-- ==============================================================================

-- State change history for audit trail
CREATE TABLE IF NOT EXISTS state_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,               -- Which table was modified
    record_id TEXT NOT NULL,                -- ID of modified record
    operation TEXT NOT NULL,                -- INSERT, UPDATE, DELETE
    old_value TEXT,                         -- JSON of old record (for UPDATE/DELETE)
    new_value TEXT,                         -- JSON of new record (for INSERT/UPDATE)
    version_before INTEGER,
    version_after INTEGER,
    changed_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    changed_by TEXT,                        -- Correlation ID or user
    correlation_id TEXT                     -- Links to execution context
);

-- Lock tracking for debugging (not actual locks)
CREATE TABLE IF NOT EXISTS lock_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    operation TEXT NOT NULL,                -- 'ACQUIRE', 'RELEASE', 'CONFLICT'
    version_attempted INTEGER,
    version_actual INTEGER,
    success BOOLEAN NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
    correlation_id TEXT
);

-- ==============================================================================
-- INDEXES
-- ==============================================================================

-- State table indexes
CREATE INDEX IF NOT EXISTS idx_state_key ON state(key);
CREATE INDEX IF NOT EXISTS idx_state_expires ON state(expires_at) WHERE expires_at IS NOT NULL;

-- Todo items indexes
CREATE INDEX IF NOT EXISTS idx_todo_feature ON todo_items(feature_id);
CREATE INDEX IF NOT EXISTS idx_todo_phase ON todo_items(phase_id);
CREATE INDEX IF NOT EXISTS idx_todo_status ON todo_items(status);
CREATE INDEX IF NOT EXISTS idx_todo_priority ON todo_items(priority);
CREATE INDEX IF NOT EXISTS idx_todo_item_id ON todo_items(item_id);

-- Execution state indexes
CREATE INDEX IF NOT EXISTS idx_execution_status ON execution_state(status);
CREATE INDEX IF NOT EXISTS idx_execution_orchestrator ON execution_state(orchestrator);
CREATE INDEX IF NOT EXISTS idx_execution_id ON execution_state(execution_id);

-- Checkpoint indexes
CREATE INDEX IF NOT EXISTS idx_checkpoint_type ON checkpoints(checkpoint_type);
CREATE INDEX IF NOT EXISTS idx_checkpoint_created ON checkpoints(created_at);

-- Checkpoint refs indexes
CREATE INDEX IF NOT EXISTS idx_checkpoint_ref_checkpoint ON checkpoint_refs(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_checkpoint_ref_type ON checkpoint_refs(ref_type, ref_id);

-- History indexes
CREATE INDEX IF NOT EXISTS idx_history_table ON state_history(table_name);
CREATE INDEX IF NOT EXISTS idx_history_record ON state_history(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_history_correlation ON state_history(correlation_id);
CREATE INDEX IF NOT EXISTS idx_history_changed ON state_history(changed_at);

-- Lock history indexes
CREATE INDEX IF NOT EXISTS idx_lock_key ON lock_history(key);
CREATE INDEX IF NOT EXISTS idx_lock_correlation ON lock_history(correlation_id);

-- ==============================================================================
-- VIEWS
-- ==============================================================================

-- Active TODO items view
CREATE VIEW IF NOT EXISTS v_active_todos AS
SELECT 
    item_id,
    feature_id,
    phase_id,
    name,
    status,
    priority,
    tdd_phase,
    estimated_minutes,
    started_at,
    version
FROM todo_items
WHERE status IN ('NOT_STARTED', 'IN_PROGRESS')
ORDER BY 
    CASE priority 
        WHEN 'P0_CRITICAL' THEN 0 
        WHEN 'P1_HIGH' THEN 1 
        WHEN 'P2_MEDIUM' THEN 2 
        WHEN 'P3_LOW' THEN 3 
    END,
    phase_id,
    id;

-- Recent checkpoints view
CREATE VIEW IF NOT EXISTS v_recent_checkpoints AS
SELECT 
    checkpoint_id,
    name,
    checkpoint_type,
    created_at,
    created_by,
    (SELECT COUNT(*) FROM checkpoint_refs WHERE checkpoint_refs.checkpoint_id = checkpoints.checkpoint_id) as ref_count
FROM checkpoints
ORDER BY created_at DESC
LIMIT 10;

-- Execution summary view
CREATE VIEW IF NOT EXISTS v_execution_summary AS
SELECT 
    orchestrator,
    status,
    COUNT(*) as count,
    AVG(CAST((julianday(completed_at) - julianday(started_at)) * 86400 AS INTEGER)) as avg_duration_seconds
FROM execution_state
WHERE started_at IS NOT NULL
GROUP BY orchestrator, status;

-- ==============================================================================
-- TRIGGERS FOR AUTOMATIC VERSION INCREMENT
-- ==============================================================================

-- Auto-increment version on state update
CREATE TRIGGER IF NOT EXISTS trg_state_version
AFTER UPDATE ON state
FOR EACH ROW
WHEN NEW.version = OLD.version
BEGIN
    UPDATE state SET version = OLD.version + 1, updated_at = datetime('now', 'utc')
    WHERE id = NEW.id;
END;

-- Auto-increment version on todo_items update
CREATE TRIGGER IF NOT EXISTS trg_todo_version
AFTER UPDATE ON todo_items
FOR EACH ROW
WHEN NEW.version = OLD.version
BEGIN
    UPDATE todo_items SET version = OLD.version + 1, updated_at = datetime('now', 'utc')
    WHERE id = NEW.id;
END;

-- Auto-increment version on execution_state update
CREATE TRIGGER IF NOT EXISTS trg_execution_version
AFTER UPDATE ON execution_state
FOR EACH ROW
WHEN NEW.version = OLD.version
BEGIN
    UPDATE execution_state SET version = OLD.version + 1, updated_at = datetime('now', 'utc')
    WHERE id = NEW.id;
END;

-- ==============================================================================
-- INITIALIZATION
-- ==============================================================================

-- Insert schema version
INSERT OR REPLACE INTO state (key, value, version) 
VALUES ('__schema_version__', '"6.0.0"', 1);

INSERT OR REPLACE INTO state (key, value, version)
VALUES ('__schema_created__', '"2026-01-07"', 1);

-- ============================================================================
-- CORTEX-6 Database Schema (Greenfield)
-- SQLite with WAL Mode, Optimistic Locking, Full Audit Trail
-- Generated: 2026-01-07T17:10:00Z
-- ============================================================================

-- Purpose: Complete database schema for CORTEX-6 from scratch
-- Database: SQLite 3.35+ (WAL mode required)
-- Features: Optimistic locking, audit logs, state management, TODO graphs
-- Author: Asif Hussain
-- Copyright © 2025-2026 Asif Hussain. All rights reserved.

-- ============================================================================
-- DATABASE CONFIGURATION
-- ============================================================================

-- Enable WAL mode (concurrent reads during writes)
PRAGMA journal_mode=WAL;

-- Synchronous mode (NORMAL is safe with WAL)
PRAGMA synchronous=NORMAL;

-- Busy timeout (5 seconds)
PRAGMA busy_timeout=5000;

-- Foreign keys enforcement
PRAGMA foreign_keys=ON;

-- Cache size (64MB)
PRAGMA cache_size=-64000;

-- Page size (4KB, optimal for most workloads)
PRAGMA page_size=4096;

-- Auto vacuum (incremental, prevents fragmentation)
PRAGMA auto_vacuum=INCREMENTAL;

-- ============================================================================
-- TABLE: schema_version
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    migration_file TEXT NOT NULL,
    rollback_file TEXT
);

-- Initial schema version
INSERT INTO schema_version (version, description, migration_file, rollback_file)
VALUES (1, 'Initial schema', '001_initial_schema.sql', '001_rollback_initial_schema.sql');

-- ============================================================================
-- TABLE: states (Orchestrator State Management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS states (
    state_id TEXT PRIMARY KEY,
    state_type TEXT NOT NULL CHECK(state_type IN ('planning', 'execution', 'validation', 'coordination')),
    workflow_id TEXT,
    orchestrator_id TEXT,
    data TEXT NOT NULL,  -- JSON blob
    version INTEGER NOT NULL DEFAULT 1,  -- Optimistic locking
    status TEXT NOT NULL CHECK(status IN ('active', 'completed', 'failed', 'deleted')) DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_states_workflow ON states(workflow_id) WHERE status != 'deleted';
CREATE INDEX idx_states_orchestrator ON states(orchestrator_id) WHERE status != 'deleted';
CREATE INDEX idx_states_type ON states(state_type) WHERE status != 'deleted';
CREATE INDEX idx_states_status ON states(status);

-- Trigger: Update updated_at on state changes
CREATE TRIGGER update_states_timestamp
    AFTER UPDATE ON states
    FOR EACH ROW
BEGIN
    UPDATE states SET updated_at = CURRENT_TIMESTAMP WHERE state_id = NEW.state_id;
END;

-- ============================================================================
-- TABLE: workflows (Workflow Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflows (
    workflow_id TEXT PRIMARY KEY,
    workflow_type TEXT NOT NULL,  -- e.g., 'planning', 'tdd', 'review'
    orchestrator_id TEXT NOT NULL,
    request_text TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    metadata TEXT,  -- JSON blob
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_orchestrator ON workflows(orchestrator_id);
CREATE INDEX idx_workflows_created ON workflows(created_at);

-- Trigger: Update updated_at on workflow changes
CREATE TRIGGER update_workflows_timestamp
    AFTER UPDATE ON workflows
    FOR EACH ROW
BEGIN
    UPDATE workflows SET updated_at = CURRENT_TIMESTAMP WHERE workflow_id = NEW.workflow_id;
END;

-- ============================================================================
-- TABLE: todo_tasks (DAG Work Tracking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS todo_tasks (
    task_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    orchestrator_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'ready', 'in_progress', 'completed', 'failed', 'blocked')) DEFAULT 'pending',
    estimated_effort_hours INTEGER,
    actual_effort_hours INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    metadata TEXT,  -- JSON blob
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_todo_tasks_workflow ON todo_tasks(workflow_id);
CREATE INDEX idx_todo_tasks_status ON todo_tasks(status);
CREATE INDEX idx_todo_tasks_orchestrator ON todo_tasks(orchestrator_id);

-- Trigger: Update updated_at on task changes
CREATE TRIGGER update_todo_tasks_timestamp
    AFTER UPDATE ON todo_tasks
    FOR EACH ROW
BEGIN
    UPDATE todo_tasks SET updated_at = CURRENT_TIMESTAMP WHERE task_id = NEW.task_id;
END;

-- ============================================================================
-- TABLE: todo_dependencies (DAG Edges)
-- ============================================================================

CREATE TABLE IF NOT EXISTS todo_dependencies (
    from_task_id TEXT NOT NULL,
    to_task_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL CHECK(dependency_type IN ('hard', 'soft')) DEFAULT 'hard',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_task_id, to_task_id),
    FOREIGN KEY (from_task_id) REFERENCES todo_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (to_task_id) REFERENCES todo_tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX idx_todo_deps_from ON todo_dependencies(from_task_id);
CREATE INDEX idx_todo_deps_to ON todo_dependencies(to_task_id);

-- Check constraint: Prevent self-referencing dependencies
CREATE TRIGGER prevent_self_dependency
    BEFORE INSERT ON todo_dependencies
    FOR EACH ROW
    WHEN NEW.from_task_id = NEW.to_task_id
BEGIN
    SELECT RAISE(ABORT, 'Task cannot depend on itself');
END;

-- ============================================================================
-- TABLE: audit_logs (Mandatory Audit Trail)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL CHECK(category IN ('governance', 'orchestration', 'state_management', 'knowledge', 'system')),
    level TEXT NOT NULL CHECK(level IN ('debug', 'info', 'warning', 'error', 'critical')),
    workflow_id TEXT,
    orchestrator_id TEXT,
    task_id TEXT,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata TEXT,  -- JSON blob
    stack_trace TEXT,
    user_id TEXT,
    session_id TEXT
);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_category ON audit_logs(category);
CREATE INDEX idx_audit_logs_level ON audit_logs(level);
CREATE INDEX idx_audit_logs_workflow ON audit_logs(workflow_id);
CREATE INDEX idx_audit_logs_orchestrator ON audit_logs(orchestrator_id);
CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);

-- ============================================================================
-- TABLE: governance_violations (SKULL Rule Violations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS governance_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'blocked', 'critical')),
    workflow_id TEXT,
    orchestrator_id TEXT,
    file_path TEXT,
    line_number INTEGER,
    violation_message TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'fixed', 'ignored', 'false_positive')) DEFAULT 'active',
    fix_commit TEXT,
    reviewer TEXT,
    reviewed_at TIMESTAMP,
    metadata TEXT  -- JSON blob
);

CREATE INDEX idx_gov_violations_timestamp ON governance_violations(timestamp);
CREATE INDEX idx_gov_violations_rule ON governance_violations(rule_id);
CREATE INDEX idx_gov_violations_severity ON governance_violations(severity);
CREATE INDEX idx_gov_violations_status ON governance_violations(status);
CREATE INDEX idx_gov_violations_workflow ON governance_violations(workflow_id);

-- ============================================================================
-- TABLE: knowledge_cache (3-Tier Knowledge Merge Cache)
-- ============================================================================

CREATE TABLE IF NOT EXISTS knowledge_cache (
    cache_key TEXT PRIMARY KEY,
    tier TEXT NOT NULL CHECK(tier IN ('cortex', 'company', 'project', 'merged')),
    knowledge_data TEXT NOT NULL,  -- JSON blob
    conflicts TEXT,  -- JSON blob of conflict resolutions
    cache_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER NOT NULL DEFAULT 3600,  -- 1 hour default TTL
    hit_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_knowledge_cache_tier ON knowledge_cache(tier);
CREATE INDEX idx_knowledge_cache_timestamp ON knowledge_cache(cache_timestamp);

-- Trigger: Auto-expire cache entries
CREATE TRIGGER expire_knowledge_cache
    AFTER INSERT ON knowledge_cache
    FOR EACH ROW
BEGIN
    DELETE FROM knowledge_cache
    WHERE cache_timestamp < datetime('now', '-' || ttl_seconds || ' seconds');
END;

-- ============================================================================
-- TABLE: performance_metrics (Performance Benchmarking)
-- ============================================================================

CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metric_type TEXT NOT NULL,  -- e.g., 'routing_latency', 'knowledge_merge_latency'
    metric_value REAL NOT NULL,
    unit TEXT NOT NULL,  -- e.g., 'ms', 'seconds', 'ops/sec'
    context TEXT,  -- JSON blob (workflow_id, orchestrator_id, etc.)
    sla_target REAL,
    sla_met BOOLEAN
);

CREATE INDEX idx_perf_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX idx_perf_metrics_type ON performance_metrics(metric_type);
CREATE INDEX idx_perf_metrics_sla_met ON performance_metrics(sla_met);

-- ============================================================================
-- TABLE: checkpoints (State Checkpoints for Rollback)
-- ============================================================================

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    orchestrator_id TEXT NOT NULL,
    checkpoint_type TEXT NOT NULL CHECK(checkpoint_type IN ('phase_start', 'phase_end', 'task_complete', 'manual')),
    state_snapshot TEXT NOT NULL,  -- JSON blob of full state
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_checkpoints_workflow ON checkpoints(workflow_id);
CREATE INDEX idx_checkpoints_created ON checkpoints(created_at);

-- ============================================================================
-- TABLE: mcp_tool_calls (MCP Server Invocations)
-- ============================================================================

CREATE TABLE IF NOT EXISTS mcp_tool_calls (
    call_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tool_name TEXT NOT NULL,
    arguments TEXT NOT NULL,  -- JSON blob
    result TEXT,  -- JSON blob
    error TEXT,
    duration_ms REAL,
    client_info TEXT  -- JSON blob (GitHub Copilot version, etc.)
);

CREATE INDEX idx_mcp_calls_timestamp ON mcp_tool_calls(timestamp);
CREATE INDEX idx_mcp_calls_tool_name ON mcp_tool_calls(tool_name);
CREATE INDEX idx_mcp_calls_error ON mcp_tool_calls(error) WHERE error IS NOT NULL;

-- ============================================================================
-- TABLE: team_knowledge (Team Learning Aggregation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS team_knowledge (
    learning_id TEXT PRIMARY KEY,
    pattern_name TEXT NOT NULL,
    category TEXT NOT NULL,
    learning_text TEXT NOT NULL,
    evidence TEXT,  -- JSON blob (workflow_ids, file paths, code snippets)
    confidence_score REAL NOT NULL CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    validation_status TEXT NOT NULL CHECK(validation_status IN ('pending', 'validated', 'rejected')) DEFAULT 'pending',
    contributor TEXT,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_team_knowledge_category ON team_knowledge(category);
CREATE INDEX idx_team_knowledge_confidence ON team_knowledge(confidence_score);
CREATE INDEX idx_team_knowledge_validation ON team_knowledge(validation_status);
CREATE INDEX idx_team_knowledge_usage ON team_knowledge(usage_count);

-- Trigger: Update updated_at on team knowledge changes
CREATE TRIGGER update_team_knowledge_timestamp
    AFTER UPDATE ON team_knowledge
    FOR EACH ROW
BEGIN
    UPDATE team_knowledge SET updated_at = CURRENT_TIMESTAMP WHERE learning_id = NEW.learning_id;
END;

-- ============================================================================
-- VIEWS (Convenience Queries)
-- ============================================================================

-- View: Active workflows with progress
CREATE VIEW IF NOT EXISTS v_active_workflows AS
SELECT
    w.workflow_id,
    w.workflow_type,
    w.orchestrator_id,
    w.status AS workflow_status,
    w.start_time,
    COUNT(t.task_id) AS total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) / COUNT(t.task_id), 2) AS progress_percentage,
    SUM(t.estimated_effort_hours) AS total_estimated_hours,
    SUM(t.actual_effort_hours) AS total_actual_hours
FROM workflows w
LEFT JOIN todo_tasks t ON w.workflow_id = t.workflow_id
WHERE w.status IN ('pending', 'in_progress')
GROUP BY w.workflow_id;

-- View: Governance violations summary
CREATE VIEW IF NOT EXISTS v_governance_summary AS
SELECT
    rule_id,
    severity,
    COUNT(*) AS violation_count,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_count,
    SUM(CASE WHEN status = 'fixed' THEN 1 ELSE 0 END) AS fixed_count,
    MIN(timestamp) AS first_occurrence,
    MAX(timestamp) AS last_occurrence
FROM governance_violations
GROUP BY rule_id, severity
ORDER BY severity DESC, violation_count DESC;

-- View: Performance metrics summary (last 24 hours)
CREATE VIEW IF NOT EXISTS v_performance_summary AS
SELECT
    metric_type,
    COUNT(*) AS sample_count,
    ROUND(AVG(metric_value), 2) AS avg_value,
    ROUND(MIN(metric_value), 2) AS min_value,
    ROUND(MAX(metric_value), 2) AS max_value,
    ROUND(AVG(CASE WHEN sla_met THEN 1.0 ELSE 0.0 END) * 100, 2) AS sla_compliance_percentage,
    unit
FROM performance_metrics
WHERE timestamp > datetime('now', '-24 hours')
GROUP BY metric_type, unit
ORDER BY metric_type;

-- View: TODO task dependency graph (for cycle detection)
CREATE VIEW IF NOT EXISTS v_todo_dependency_graph AS
SELECT
    d.from_task_id,
    t1.task_name AS from_task_name,
    t1.status AS from_status,
    d.to_task_id,
    t2.task_name AS to_task_name,
    t2.status AS to_status,
    d.dependency_type,
    t1.workflow_id
FROM todo_dependencies d
JOIN todo_tasks t1 ON d.from_task_id = t1.task_id
JOIN todo_tasks t2 ON d.to_task_id = t2.task_id;

-- ============================================================================
-- FUNCTIONS (Via Application Layer)
-- ============================================================================

-- Note: SQLite doesn't support user-defined functions in SQL.
-- These are implemented in Python (src/database/functions.py):
--
-- - detect_circular_dependencies(workflow_id) -> List[List[task_id]]
-- - get_ready_tasks(workflow_id) -> List[task_id]
-- - calculate_critical_path(workflow_id) -> (duration_hours, [task_ids])
-- - backup_database() -> backup_file_path
-- - restore_from_backup(backup_file_path) -> bool
-- - run_migrations(target_version) -> bool
-- - rollback_migration(from_version) -> bool

-- ============================================================================
-- MIGRATION TRACKING
-- ============================================================================

-- All schema changes MUST be tracked in schema_version table
-- Migration files: cortex-brain/database/migrations/XXX_description.sql
-- Rollback files: cortex-brain/database/migrations/XXX_rollback_description.sql

-- Example future migration:
-- INSERT INTO schema_version (version, description, migration_file, rollback_file)
-- VALUES (2, 'Add distributed tracing support', '002_add_tracing.sql', '002_rollback_add_tracing.sql');

-- ============================================================================
-- PERFORMANCE NOTES
-- ============================================================================

-- 1. WAL mode enables concurrent reads during writes
-- 2. Indexes created for all common query patterns
-- 3. Foreign keys ensure referential integrity
-- 4. Triggers auto-update timestamps (no application logic needed)
-- 5. Views provide convenient query interfaces
-- 6. Optimistic locking via version column (minimal contention)
-- 7. JSON blobs allow flexibility without schema changes
-- 8. Checkpoints enable instant rollback without complex logic

-- ============================================================================
-- BACKUP & RESTORE COMMANDS
-- ============================================================================

-- Backup (from application):
-- sqlite3 cortex-brain/database/cortex-state.db ".backup 'cortex-brain/database/backups/cortex-state-20260107.db'"

-- Restore (from application):
-- sqlite3 cortex-brain/database/cortex-state.db ".restore 'cortex-brain/database/backups/cortex-state-20260107.db'"

-- ============================================================================
-- INTEGRITY CHECKS
-- ============================================================================

-- Run integrity check on startup:
PRAGMA integrity_check;

-- Run foreign key check:
PRAGMA foreign_key_check;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Schema Version: 1.0.0
-- Generated: 2026-01-07T17:10:00Z
-- Author: Asif Hussain
-- Status: ✅ PRODUCTION-READY

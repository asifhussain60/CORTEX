-- CORTEX Audit Database Schema
-- Authority: AC-GOLDEN-E2E-001
-- Created: 2026-02-17
-- Purpose: Centralized audit logging for orchestrator workflows

-- Core audit log table (already exists in governance.db)
-- Documenting existing structure for reference
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    ac_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    component TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata TEXT,  -- JSON blob
    entry_hash TEXT,
    previous_hash TEXT,
    
    -- Indexes for performance
    CONSTRAINT valid_level CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'AUDIT'))
);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_ac_id ON audit_log(ac_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);

-- Orchestrator-specific audit events table
-- NEW: Structured logging for orchestrator workflows
CREATE TABLE IF NOT EXISTS orchestrator_audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Temporal tracking
    timestamp TEXT NOT NULL,
    
    -- Orchestrator identity
    orchestrator_name TEXT NOT NULL,
    orchestrator_version TEXT DEFAULT '1.0',
    
    -- Workflow tracking
    workflow_stage TEXT NOT NULL,  -- INTERACTION, INTENT, INTELLIGENCE, EXECUTION
    activity TEXT NOT NULL,  -- CLASSIFY_INTENT, GENERATE_TESTS, etc.
    
    -- Correlation and tracing
    correlation_id TEXT NOT NULL,
    parent_trace_id TEXT,
    session_id TEXT,
    
    -- Input/Output capture
    input_parameters TEXT,  -- JSON blob
    output_results TEXT,    -- JSON blob
    
    -- Status and decision tracking
    status TEXT NOT NULL,  -- STARTED, COMPLETED, FAILED
    decision_point TEXT,   -- JSON blob for key decisions
    reasoning TEXT,        -- Human-readable reasoning
    
    -- Performance metrics
    duration_ms INTEGER,
    
    -- AC tracking
    ac_id TEXT,
    
    -- Hash chain integrity (links to audit_log)
    parent_audit_id INTEGER,
    
    FOREIGN KEY (parent_audit_id) REFERENCES audit_log(id),
    CONSTRAINT valid_status CHECK (status IN ('STARTED', 'COMPLETED', 'FAILED', 'SKIPPED'))
);

-- Indexes for golden test queries
CREATE INDEX IF NOT EXISTS idx_orch_events_correlation ON orchestrator_audit_events(correlation_id);
CREATE INDEX IF NOT EXISTS idx_orch_events_orchestrator ON orchestrator_audit_events(orchestrator_name);
CREATE INDEX IF NOT EXISTS idx_orch_events_workflow_stage ON orchestrator_audit_events(workflow_stage);
CREATE INDEX IF NOT EXISTS idx_orch_events_timestamp ON orchestrator_audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_orch_events_session ON orchestrator_audit_events(session_id);

-- View for golden test assertions
-- Simplifies audit log queries in tests
CREATE VIEW IF NOT EXISTS v_golden_test_audit_trail AS
SELECT 
    oae.id,
    oae.timestamp,
    oae.orchestrator_name,
    oae.workflow_stage,
    oae.activity,
    oae.correlation_id,
    oae.status,
    oae.input_parameters,
    oae.output_results,
    oae.duration_ms,
    oae.reasoning,
    al.ac_id,
    al.message
FROM orchestrator_audit_events oae
LEFT JOIN audit_log al ON oae.parent_audit_id = al.id
ORDER BY oae.timestamp ASC;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL
);

INSERT OR IGNORE INTO schema_migrations (version, applied_at, description)
VALUES (1, datetime('now'), 'Initial schema documentation');

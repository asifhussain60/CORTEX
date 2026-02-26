-- Migration 001: Add orchestrator audit events table
-- Authority: AC-GOLDEN-E2E-002
-- Created: 2026-02-17

-- Check if migration already applied
-- This migration is idempotent

BEGIN TRANSACTION;

-- Create schema_migrations table if not exists
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT NOT NULL
);

-- Create orchestrator_audit_events table if not exists
CREATE TABLE IF NOT EXISTS orchestrator_audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    orchestrator_name TEXT NOT NULL,
    orchestrator_version TEXT DEFAULT '1.0',
    workflow_stage TEXT NOT NULL,
    activity TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    parent_trace_id TEXT,
    session_id TEXT,
    input_parameters TEXT,
    output_results TEXT,
    status TEXT NOT NULL,
    decision_point TEXT,
    reasoning TEXT,
    duration_ms INTEGER,
    ac_id TEXT,
    parent_audit_id INTEGER,
    FOREIGN KEY (parent_audit_id) REFERENCES audit_log(id),
    CONSTRAINT valid_status CHECK (status IN ('STARTED', 'COMPLETED', 'FAILED', 'SKIPPED'))
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_orch_events_correlation ON orchestrator_audit_events(correlation_id);
CREATE INDEX IF NOT EXISTS idx_orch_events_orchestrator ON orchestrator_audit_events(orchestrator_name);
CREATE INDEX IF NOT EXISTS idx_orch_events_workflow_stage ON orchestrator_audit_events(workflow_stage);
CREATE INDEX IF NOT EXISTS idx_orch_events_timestamp ON orchestrator_audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_orch_events_session ON orchestrator_audit_events(session_id);

-- Create view
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

-- Record migration
INSERT OR IGNORE INTO schema_migrations (version, applied_at, description)
VALUES (2, datetime('now'), 'Add orchestrator_audit_events table and indexes');

COMMIT;

-- Planning State Database Schema
-- Single source of truth for all planning execution state
-- Version: 1.0.0
-- Author: Asif Hussain
-- Copyright © 2025-2026 Asif Hussain. All rights reserved.

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL
);

-- Plans: High-level planning metadata
CREATE TABLE IF NOT EXISTS plans (
    plan_id TEXT PRIMARY KEY,
    feature_name TEXT NOT NULL,
    complexity_tier INTEGER CHECK (complexity_tier BETWEEN 1 AND 5),
    strategy TEXT,
    status TEXT CHECK (status IN ('not_started', 'in_progress', 'completed', 'failed', 'paused')) DEFAULT 'not_started',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration_days REAL,
    actual_duration_seconds REAL,
    error_message TEXT,
    metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);
CREATE INDEX IF NOT EXISTS idx_plans_created_at ON plans(created_at);

-- Phases: Individual execution phases within plans
CREATE TABLE IF NOT EXISTS phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT CHECK (status IN ('not_started', 'in_progress', 'completed', 'failed', 'skipped')) DEFAULT 'not_started',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    error_message TEXT,
    config JSON,
    result JSON,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    UNIQUE (plan_id, phase_number)
);

CREATE INDEX IF NOT EXISTS idx_phases_plan_status ON phases(plan_id, status);
CREATE INDEX IF NOT EXISTS idx_phases_status ON phases(status);

-- Tasks: Granular tasks within phases
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    task_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT CHECK (status IN ('not_started', 'in_progress', 'completed', 'failed', 'skipped')) DEFAULT 'not_started',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    error_message TEXT,
    result JSON,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    UNIQUE (phase_id, task_number)
);

CREATE INDEX IF NOT EXISTS idx_tasks_phase_status ON tasks(phase_id, status);
CREATE INDEX IF NOT EXISTS idx_tasks_plan_status ON tasks(plan_id, status);

-- Artifacts: Registry of generated files and outputs
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    task_id TEXT,
    path TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('plan', 'report', 'code', 'test', 'config', 'documentation', 'other')),
    size_bytes INTEGER,
    checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE SET NULL,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_artifacts_plan ON artifacts(plan_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type);
CREATE INDEX IF NOT EXISTS idx_artifacts_path ON artifacts(path);

-- Validations: Checkpoint validation results
CREATE TABLE IF NOT EXISTS validations (
    validation_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT NOT NULL,
    validation_type TEXT NOT NULL CHECK (validation_type IN ('test', 'lint', 'format', 'security', 'custom')),
    status TEXT CHECK (status IN ('passed', 'failed', 'skipped', 'error')) DEFAULT 'passed',
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds REAL,
    passed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    skipped_count INTEGER DEFAULT 0,
    error_message TEXT,
    details JSON,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_validations_plan_phase ON validations(plan_id, phase_id);
CREATE INDEX IF NOT EXISTS idx_validations_status ON validations(status);

-- State Snapshots: Point-in-time state captures for rollback
CREATE TABLE IF NOT EXISTS state_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    snapshot_type TEXT CHECK (snapshot_type IN ('checkpoint', 'auto', 'manual')) DEFAULT 'checkpoint',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    state_data JSON NOT NULL,
    artifact_refs JSON,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_plan ON state_snapshots(plan_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_created ON state_snapshots(created_at);

-- Execution Log: Detailed execution trace
CREATE TABLE IF NOT EXISTS execution_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    task_id TEXT,
    level TEXT CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')) DEFAULT 'INFO',
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context JSON,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_log_plan_timestamp ON execution_log(plan_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_log_level ON execution_log(level);

-- Metrics: Performance and resource tracking
CREATE TABLE IF NOT EXISTS metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    unit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_metrics_plan_name ON metrics(plan_id, metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON metrics(recorded_at);

-- Orchestrator Execution Log: Track orchestrator lifecycle events (for StateManager)
CREATE TABLE IF NOT EXISTS orchestrator_execution_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    orchestrator_id TEXT NOT NULL,
    status TEXT CHECK (status IN ('started', 'in_progress', 'completed', 'failed')) NOT NULL,
    parameters TEXT,
    result TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orch_exec_log_orchestrator ON orchestrator_execution_log(orchestrator_id);
CREATE INDEX IF NOT EXISTS idx_orch_exec_log_status ON orchestrator_execution_log(status);
CREATE INDEX IF NOT EXISTS idx_orch_exec_log_timestamp ON orchestrator_execution_log(timestamp);

-- Initial schema version
INSERT OR IGNORE INTO schema_migrations (version, description)
VALUES (1, 'Initial schema: plans, phases, tasks, artifacts, validations, snapshots, logs, metrics, orchestrator_execution_log');


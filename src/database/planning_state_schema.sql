-- Planning State Database Schema
-- CORTEX Planning System State Management
-- Author: Asif Hussain
-- Copyright © 2025-2026 Asif Hussain. All rights reserved.

-- Plans table: Master plan records
CREATE TABLE IF NOT EXISTS plans (
    plan_id TEXT PRIMARY KEY,
    plan_name TEXT NOT NULL UNIQUE,
    plan_type TEXT NOT NULL,  -- 'feature', 'epic', 'phase', 'sub-plan'
    status TEXT NOT NULL,  -- 'draft', 'approved', 'in_progress', 'complete', 'archived'
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    metadata TEXT  -- JSON
);

-- Phases table: Plan phases
CREATE TABLE IF NOT EXISTS phases (
    phase_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_number INTEGER NOT NULL,
    phase_name TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'pending', 'in_progress', 'complete', 'failed', 'skipped'
    started_at INTEGER,
    completed_at INTEGER,
    metadata TEXT,  -- JSON
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    UNIQUE(plan_id, phase_number)
);

-- Tasks table: Phase tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'pending', 'in_progress', 'complete', 'failed'
    created_at INTEGER NOT NULL,
    completed_at INTEGER,
    metadata TEXT,  -- JSON
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

-- Artifacts table: Generated artifacts
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,  -- 'file', 'folder', 'report', 'config'
    artifact_path TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    metadata TEXT,  -- JSON
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

-- Validations table: Validation results
CREATE TABLE IF NOT EXISTS validations (
    validation_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    phase_id TEXT,
    validation_type TEXT NOT NULL,  -- 'schema', 'dor', 'dod', 'acceptance'
    passed BOOLEAN NOT NULL,
    created_at INTEGER NOT NULL,
    errors TEXT,  -- JSON array
    warnings TEXT,  -- JSON array
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE,
    FOREIGN KEY (phase_id) REFERENCES phases(phase_id) ON DELETE CASCADE
);

-- Snapshots table: State snapshots
CREATE TABLE IF NOT EXISTS snapshots (
    snapshot_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,  -- 'checkpoint', 'backup', 'rollback'
    created_at INTEGER NOT NULL,
    state_data TEXT NOT NULL,  -- JSON
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id) ON DELETE CASCADE
);

-- Indices for performance
CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);
CREATE INDEX IF NOT EXISTS idx_phases_plan_id ON phases(plan_id);
CREATE INDEX IF NOT EXISTS idx_phases_status ON phases(status);
CREATE INDEX IF NOT EXISTS idx_tasks_phase_id ON tasks(phase_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_artifacts_plan_id ON artifacts(plan_id);
CREATE INDEX IF NOT EXISTS idx_validations_plan_id ON validations(plan_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_plan_id ON snapshots(plan_id);

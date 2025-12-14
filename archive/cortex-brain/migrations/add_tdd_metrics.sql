-- Migration: Add TDD Metrics Tracking
-- Version: 1.0.0
-- Author: Asif Hussain
-- Date: 2025-11-25
-- Description: Adds timestamp and metrics columns to TDD workflow tracking

-- Add columns to tdd_sessions table (if it exists)
-- If table doesn't exist, this migration will create it

CREATE TABLE IF NOT EXISTS tdd_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'in-progress',
    project_path TEXT NOT NULL,
    feature_name TEXT
);

-- Add new metrics columns
ALTER TABLE tdd_sessions ADD COLUMN IF NOT EXISTS session_start_time TIMESTAMP;
ALTER TABLE tdd_sessions ADD COLUMN IF NOT EXISTS session_end_time TIMESTAMP;
ALTER TABLE tdd_sessions ADD COLUMN IF NOT EXISTS session_duration_seconds REAL;
ALTER TABLE tdd_sessions ADD COLUMN IF NOT EXISTS total_phases_completed INTEGER DEFAULT 0;

-- Create tdd_phases table for phase-level tracking
CREATE TABLE IF NOT EXISTS tdd_phases (
    phase_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    phase_name TEXT NOT NULL, -- RED, GREEN, REFACTOR, COMPLETE
    phase_start_time TIMESTAMP NOT NULL,
    phase_end_time TIMESTAMP,
    phase_duration_seconds REAL,
    git_commit_sha TEXT,
    git_commit_message TEXT,
    metrics_before TEXT, -- JSON blob
    metrics_after TEXT,  -- JSON blob
    status TEXT DEFAULT 'in-progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES tdd_sessions(session_id)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_tdd_phases_session_id ON tdd_phases(session_id);
CREATE INDEX IF NOT EXISTS idx_tdd_phases_phase_name ON tdd_phases(phase_name);
CREATE INDEX IF NOT EXISTS idx_tdd_phases_git_commit_sha ON tdd_phases(git_commit_sha);
CREATE INDEX IF NOT EXISTS idx_tdd_phases_phase_start_time ON tdd_phases(phase_start_time);

-- Create tdd_metrics table for detailed metrics tracking
CREATE TABLE IF NOT EXISTS tdd_metrics (
    metric_id TEXT PRIMARY KEY,
    phase_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metric_unit TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phase_id) REFERENCES tdd_phases(phase_id)
);

CREATE INDEX IF NOT EXISTS idx_tdd_metrics_phase_id ON tdd_metrics(phase_id);
CREATE INDEX IF NOT EXISTS idx_tdd_metrics_metric_name ON tdd_metrics(metric_name);

-- Migration complete
-- Version: 1.0.0

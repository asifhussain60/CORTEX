-- Tier Enforcement Schema for governance.db (AC-REM-002-06/07)
-- Adds per-turn tier access logging and TIER-0 immutability constraints
--
-- Purpose: Track tier access per turn and enforce TIER-0 rule immutability
--          through database constraints (triggers + checks)
--
-- Author: Asif Hussain
-- Copyright © 2025-2026 Asif Hussain. All rights reserved.

-- ============================================================================
-- Table: governance_rules (if not already exists)
-- ============================================================================
-- This table may be created by phase initialization code
-- We create a minimal version here for tier enforcement compatibility

CREATE TABLE IF NOT EXISTS governance_rules (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL UNIQUE,
    name TEXT,
    description TEXT,
    tier INTEGER DEFAULT 1,
    category TEXT,
    severity TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- Table: tier_access_log
-- ============================================================================
-- Tracks per-turn tier access for all orchestrators
-- Enables enforcement of:
-- 1. Undeclared tier access detection
-- 2. TIER-0 immutability verification
-- 3. Per-turn governance audit trail

CREATE TABLE IF NOT EXISTS tier_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_number INTEGER NOT NULL,
    orchestrator_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    access_type TEXT NOT NULL CHECK(access_type IN ('DECLARE', 'ACCESS', 'ATTEMPT_VIOLATION')),
    decision TEXT NOT NULL CHECK(decision IN ('ALLOWED', 'DENIED')),
    violation_reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(turn_number, orchestrator_id, rule_id)
);

-- ============================================================================
-- Indexes for performance optimization
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_tier_access_turn ON tier_access_log(turn_number);

CREATE INDEX IF NOT EXISTS idx_tier_access_orchestrator ON tier_access_log(orchestrator_id);

CREATE INDEX IF NOT EXISTS idx_tier_access_rule ON tier_access_log(rule_id);

CREATE INDEX IF NOT EXISTS idx_tier_access_timestamp ON tier_access_log(timestamp);

-- ============================================================================
-- Trigger: tier0_immutability_check
-- ============================================================================
-- Prevents modification of TIER-0 rules after first access
-- Raises error if attempt to update TIER-0 rule with existing access log entries

CREATE TRIGGER IF NOT EXISTS tier0_immutability_check
BEFORE UPDATE ON governance_rules
WHEN NEW.tier = 0 AND (SELECT COUNT(*) FROM tier_access_log WHERE rule_id=NEW.rule_id) > 0
BEGIN
    SELECT RAISE(ABORT, 'TIER-0 rule immutability violation: Rule cannot be modified after first access (per-turn enforcement)');
END;

-- ============================================================================
-- View: tier_access_summary
-- ============================================================================
-- Summary of tier access patterns for analysis and debugging

CREATE VIEW IF NOT EXISTS tier_access_summary AS
SELECT
    turn_number,
    orchestrator_id,
    COUNT(*) as total_accesses,
    SUM(CASE WHEN decision = 'ALLOWED' THEN 1 ELSE 0 END) as allowed_count,
    SUM(CASE WHEN decision = 'DENIED' THEN 1 ELSE 0 END) as denied_count,
    SUM(CASE WHEN access_type = 'DECLARE' THEN 1 ELSE 0 END) as declarations,
    SUM(CASE WHEN access_type = 'ACCESS' THEN 1 ELSE 0 END) as accesses,
    SUM(CASE WHEN access_type = 'ATTEMPT_VIOLATION' THEN 1 ELSE 0 END) as violations,
    MIN(timestamp) as first_access,
    MAX(timestamp) as last_access
FROM tier_access_log
GROUP BY turn_number, orchestrator_id;

-- ============================================================================
-- View: tier0_immutability_violations
-- ============================================================================
-- Tracks attempts to violate TIER-0 immutability

CREATE VIEW IF NOT EXISTS tier0_immutability_violations AS
SELECT
    turn_number,
    orchestrator_id,
    rule_id,
    violation_reason,
    timestamp
FROM tier_access_log
WHERE access_type = 'ATTEMPT_VIOLATION'
    AND decision = 'DENIED'
ORDER BY timestamp DESC;

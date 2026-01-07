-- ============================================================================
-- CORTEX Compliance Tracking Database Schema
-- ============================================================================
-- Purpose: Track governance compliance, rule violations, and acknowledgments
-- Sprint: 2 (Active Compliance Dashboard) - Prepared in Sprint 1
-- Created: November 28, 2025
-- Author: Asif Hussain
-- Version: 1.0
-- ============================================================================

-- Compliance Events Table
-- Tracks all governance-related events (violations, warnings, acknowledgments)
CREATE TABLE IF NOT EXISTS compliance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL CHECK(event_type IN ('violation', 'warning', 'acknowledgment', 'info')),
    rule_id TEXT,              -- SKULL rule identifier (e.g., 'SKULL-01', 'DEV-03')
    rule_category TEXT CHECK(rule_category IN ('brain_protection', 'development', 'quality', 'security', 'documentation')),
    severity TEXT NOT NULL CHECK(severity IN ('critical', 'warning', 'info')),
    description TEXT NOT NULL,
    context TEXT,              -- JSON: {file, line, operation, user_input, stack_trace}
    user_response TEXT,        -- How user handled event (ignored, fixed, acknowledged)
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT,
    resolution_notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Rulebook Acknowledgments Table
-- Tracks when users acknowledge reading the rulebook
CREATE TABLE IF NOT EXISTS rulebook_acknowledgments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,              -- From user profile (email or unique identifier)
    acknowledged_at TEXT NOT NULL DEFAULT (datetime('now')),
    cortex_version TEXT NOT NULL,
    rulebook_version TEXT DEFAULT '1.0',
    acknowledgment_method TEXT CHECK(acknowledgment_method IN ('onboarding', 'manual', 'pre_flight'))
);

-- Rule Views Table
-- Tracks when users view rule documentation
CREATE TABLE IF NOT EXISTS rule_views (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    viewed_at TEXT NOT NULL DEFAULT (datetime('now')),
    view_context TEXT CHECK(view_context IN ('help', 'violation', 'search', 'dashboard', 'explorer')),
    view_duration_seconds INTEGER,
    user_action TEXT          -- 'acknowledged', 'dismissed', 'searched_more'
);

-- Compliance Summary View
-- Pre-aggregated view for dashboard performance
CREATE VIEW IF NOT EXISTS compliance_summary AS
SELECT 
    DATE(timestamp) as date,
    rule_category,
    severity,
    COUNT(*) as event_count,
    SUM(CASE WHEN resolved_at IS NOT NULL THEN 1 ELSE 0 END) as resolved_count,
    AVG(CASE WHEN resolved_at IS NOT NULL 
        THEN (julianday(resolved_at) - julianday(timestamp)) * 24 * 60 
        ELSE NULL END) as avg_resolution_time_minutes
FROM compliance_events
WHERE event_type IN ('violation', 'warning')
GROUP BY DATE(timestamp), rule_category, severity;

-- User Compliance Score View
-- Calculate compliance score per user (for future multi-user support)
CREATE VIEW IF NOT EXISTS user_compliance_scores AS
SELECT 
    COALESCE(user_id, 'default_user') as user_id,
    COUNT(DISTINCT ra.id) as acknowledgments,
    (SELECT COUNT(*) FROM compliance_events ce 
     WHERE ce.event_type = 'violation' 
     AND ce.severity = 'critical') as critical_violations,
    (SELECT COUNT(*) FROM compliance_events ce 
     WHERE ce.event_type = 'violation' 
     AND ce.severity = 'warning') as warnings,
    (SELECT COUNT(*) FROM compliance_events ce 
     WHERE ce.resolved_at IS NOT NULL) as resolved_events,
    -- Compliance score: 100 - (criticals*10 + warnings*2) + (resolved*1)
    100 - 
    (SELECT COUNT(*) * 10 FROM compliance_events WHERE event_type = 'violation' AND severity = 'critical') -
    (SELECT COUNT(*) * 2 FROM compliance_events WHERE event_type = 'violation' AND severity = 'warning') +
    (SELECT COUNT(*) FROM compliance_events WHERE resolved_at IS NOT NULL)
    as compliance_score
FROM rulebook_acknowledgments ra
GROUP BY user_id;

-- Recent Events View (for dashboard)
-- Last 50 events for quick dashboard loading
CREATE VIEW IF NOT EXISTS recent_compliance_events AS
SELECT 
    id,
    event_type,
    rule_id,
    rule_category,
    severity,
    description,
    timestamp,
    resolved_at,
    CASE 
        WHEN resolved_at IS NOT NULL THEN 'resolved'
        WHEN event_type = 'acknowledgment' THEN 'acknowledged'
        ELSE 'open'
    END as status
FROM compliance_events
ORDER BY timestamp DESC
LIMIT 50;

-- ============================================================================
-- Performance Indexes
-- ============================================================================

-- Compliance events indexes
CREATE INDEX IF NOT EXISTS idx_compliance_timestamp 
    ON compliance_events(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_compliance_rule 
    ON compliance_events(rule_id);

CREATE INDEX IF NOT EXISTS idx_compliance_severity 
    ON compliance_events(severity);

CREATE INDEX IF NOT EXISTS idx_compliance_type 
    ON compliance_events(event_type);

CREATE INDEX IF NOT EXISTS idx_compliance_category 
    ON compliance_events(rule_category);

CREATE INDEX IF NOT EXISTS idx_compliance_resolved 
    ON compliance_events(resolved_at);

-- Rulebook acknowledgments indexes
CREATE INDEX IF NOT EXISTS idx_acknowledgment_user 
    ON rulebook_acknowledgments(user_id);

CREATE INDEX IF NOT EXISTS idx_acknowledgment_timestamp 
    ON rulebook_acknowledgments(acknowledged_at DESC);

-- Rule views indexes
CREATE INDEX IF NOT EXISTS idx_rule_views_rule 
    ON rule_views(rule_id);

CREATE INDEX IF NOT EXISTS idx_rule_views_timestamp 
    ON rule_views(viewed_at DESC);

CREATE INDEX IF NOT EXISTS idx_rule_views_context 
    ON rule_views(view_context);

-- ============================================================================
-- Sample Queries (for testing)
-- ============================================================================

-- Query 1: Get compliance events from last 7 days
-- SELECT * FROM compliance_events 
-- WHERE timestamp >= datetime('now', '-7 days')
-- ORDER BY timestamp DESC;

-- Query 2: Get unresolved critical violations
-- SELECT * FROM compliance_events 
-- WHERE event_type = 'violation' 
-- AND severity = 'critical' 
-- AND resolved_at IS NULL;

-- Query 3: Get compliance summary for dashboard
-- SELECT * FROM compliance_summary 
-- WHERE date >= DATE('now', '-30 days')
-- ORDER BY date DESC;

-- Query 4: Check if user acknowledged rulebook
-- SELECT COUNT(*) FROM rulebook_acknowledgments 
-- WHERE user_id = 'user@example.com';

-- Query 5: Most viewed rules (popularity)
-- SELECT rule_id, COUNT(*) as views 
-- FROM rule_views 
-- GROUP BY rule_id 
-- ORDER BY views DESC 
-- LIMIT 10;

-- ============================================================================
-- Database Initialization
-- ============================================================================

-- Insert sample compliance event (for testing schema)
INSERT INTO compliance_events (
    event_type, rule_id, rule_category, severity, description, context
) VALUES (
    'info', 
    'SYSTEM', 
    'development', 
    'info', 
    'Compliance tracking database initialized',
    '{"version": "1.0", "sprint": 1}'
);

-- ============================================================================
-- Schema Version Tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) 
VALUES ('1.0', 'Initial compliance tracking schema for Option B Dashboard');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

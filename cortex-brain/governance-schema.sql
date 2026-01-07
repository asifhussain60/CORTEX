-- ============================================================================
-- CORTEX Governance Database Schema v3.0
-- ============================================================================
-- Purpose: Replace brain-protection-rules.yaml with relational database
-- Features: Schema enforcement, versioning, querying, FTS, transactions
-- Author: CORTEX Development Team
-- Date: January 4, 2026
-- ============================================================================

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) 
VALUES (3, 'SQLite governance migration - replaces YAML');

-- ============================================================================
-- Core Governance Tables
-- ============================================================================

-- Protection layers (high-level groupings)
CREATE TABLE IF NOT EXISTS protection_layers (
    layer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    priority INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main rules table
CREATE TABLE IF NOT EXISTS governance_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('blocked', 'warning', 'info')),
    description TEXT NOT NULL,
    layer_id TEXT NOT NULL,
    minimum_coverage INTEGER DEFAULT 0 CHECK (minimum_coverage >= 0 AND minimum_coverage <= 100),
    version INTEGER NOT NULL DEFAULT 1,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (layer_id) REFERENCES protection_layers(layer_id)
);

-- Detection keywords and scopes
CREATE TABLE IF NOT EXISTS rule_detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    keyword_group TEXT,  -- e.g., 'planning_triggers', 'tdd_keywords'
    keyword TEXT NOT NULL,
    scope TEXT,  -- e.g., 'intent', 'code_generation', 'file_operations'
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Validation criteria
CREATE TABLE IF NOT EXISTS rule_validation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    validation_criterion TEXT NOT NULL,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Alternative solutions
CREATE TABLE IF NOT EXISTS rule_alternatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    alternative TEXT NOT NULL,
    display_order INTEGER DEFAULT 0,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Test requirements
CREATE TABLE IF NOT EXISTS rule_test_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    test_name TEXT NOT NULL,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Documentation (external references)
CREATE TABLE IF NOT EXISTS rule_documentation (
    rule_id TEXT PRIMARY KEY,
    evidence_template TEXT,
    rationale TEXT,
    examples_path TEXT,  -- Path to examples directory
    documentation_path TEXT,  -- Path to full .md documentation
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- ============================================================================
-- Tier 0 Configuration
-- ============================================================================

-- Tier 0 instincts (immutable core rules)
CREATE TABLE IF NOT EXISTS tier0_instincts (
    instinct_id TEXT PRIMARY KEY,
    display_order INTEGER NOT NULL,
    description TEXT
);

-- Critical paths protected by governance
CREATE TABLE IF NOT EXISTS critical_paths (
    path TEXT PRIMARY KEY,
    description TEXT,
    protection_level TEXT DEFAULT 'high' CHECK (protection_level IN ('high', 'medium', 'low'))
);

-- Application-specific paths (for isolation rules)
CREATE TABLE IF NOT EXISTS application_paths (
    path TEXT PRIMARY KEY,
    description TEXT
);

-- Brain state files (protected from commits)
CREATE TABLE IF NOT EXISTS brain_state_files (
    filename TEXT PRIMARY KEY,
    description TEXT
);

-- ============================================================================
-- Full-Text Search
-- ============================================================================

-- FTS5 virtual table for fast rule search
CREATE VIRTUAL TABLE IF NOT EXISTS rules_fts USING fts5(
    rule_id UNINDEXED,
    name,
    description,
    keywords,
    content='governance_rules',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS rules_fts_insert AFTER INSERT ON governance_rules BEGIN
    INSERT INTO rules_fts(rule_id, name, description, keywords)
    SELECT NEW.rule_id, NEW.name, NEW.description, 
           (SELECT GROUP_CONCAT(keyword, ' ') FROM rule_detection WHERE rule_id = NEW.rule_id);
END;

CREATE TRIGGER IF NOT EXISTS rules_fts_update AFTER UPDATE ON governance_rules BEGIN
    DELETE FROM rules_fts WHERE rule_id = OLD.rule_id;
    INSERT INTO rules_fts(rule_id, name, description, keywords)
    SELECT NEW.rule_id, NEW.name, NEW.description,
           (SELECT GROUP_CONCAT(keyword, ' ') FROM rule_detection WHERE rule_id = NEW.rule_id);
END;

CREATE TRIGGER IF NOT EXISTS rules_fts_delete AFTER DELETE ON governance_rules BEGIN
    DELETE FROM rules_fts WHERE rule_id = OLD.rule_id;
END;

-- ============================================================================
-- Performance Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_rules_severity ON governance_rules(severity);
CREATE INDEX IF NOT EXISTS idx_rules_layer ON governance_rules(layer_id);
CREATE INDEX IF NOT EXISTS idx_rules_enabled ON governance_rules(enabled);
CREATE INDEX IF NOT EXISTS idx_rules_version ON governance_rules(version);

CREATE INDEX IF NOT EXISTS idx_detection_rule ON rule_detection(rule_id);
CREATE INDEX IF NOT EXISTS idx_detection_keyword ON rule_detection(keyword);
CREATE INDEX IF NOT EXISTS idx_detection_scope ON rule_detection(scope);

CREATE INDEX IF NOT EXISTS idx_validation_rule ON rule_validation(rule_id);
CREATE INDEX IF NOT EXISTS idx_alternatives_rule ON rule_alternatives(rule_id);
CREATE INDEX IF NOT EXISTS idx_test_reqs_rule ON rule_test_requirements(rule_id);

-- ============================================================================
-- Audit & Change Tracking
-- ============================================================================

-- Rule change history
CREATE TABLE IF NOT EXISTS rule_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    changed_by TEXT DEFAULT 'system',
    change_type TEXT NOT NULL CHECK (change_type IN ('created', 'updated', 'deleted', 'enabled', 'disabled')),
    previous_version INTEGER,
    new_version INTEGER,
    changes TEXT,  -- JSON describing what changed
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rule usage statistics (when rules are triggered)
CREATE TABLE IF NOT EXISTS rule_usage_stats (
    rule_id TEXT NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,  -- What triggered the rule
    outcome TEXT,  -- 'blocked', 'warned', 'passed'
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id)
);

CREATE INDEX IF NOT EXISTS idx_usage_rule ON rule_usage_stats(rule_id);
CREATE INDEX IF NOT EXISTS idx_usage_date ON rule_usage_stats(triggered_at);

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- Active rules with layer info
CREATE VIEW IF NOT EXISTS active_rules AS
SELECT 
    r.rule_id,
    r.name,
    r.severity,
    r.description,
    r.layer_id,
    l.name as layer_name,
    l.priority as layer_priority,
    r.minimum_coverage,
    r.version,
    r.enabled
FROM governance_rules r
JOIN protection_layers l ON r.layer_id = l.layer_id
WHERE r.enabled = 1
ORDER BY l.priority, r.rule_id;

-- Rules with detection keywords
CREATE VIEW IF NOT EXISTS rules_with_detection AS
SELECT 
    r.rule_id,
    r.name,
    r.severity,
    GROUP_CONCAT(DISTINCT d.keyword, ', ') as keywords,
    GROUP_CONCAT(DISTINCT d.scope, ', ') as scopes
FROM governance_rules r
LEFT JOIN rule_detection d ON r.rule_id = d.rule_id
WHERE r.enabled = 1
GROUP BY r.rule_id, r.name, r.severity;

-- Rule usage summary
CREATE VIEW IF NOT EXISTS rule_usage_summary AS
SELECT 
    r.rule_id,
    r.name,
    r.severity,
    COUNT(u.rule_id) as trigger_count,
    SUM(CASE WHEN u.outcome = 'blocked' THEN 1 ELSE 0 END) as blocked_count,
    SUM(CASE WHEN u.outcome = 'warned' THEN 1 ELSE 0 END) as warned_count,
    MAX(u.triggered_at) as last_triggered
FROM governance_rules r
LEFT JOIN rule_usage_stats u ON r.rule_id = u.rule_id
GROUP BY r.rule_id, r.name, r.severity;

-- ============================================================================
-- Helper Functions (Triggers for auto-updates)
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS rules_updated_at AFTER UPDATE ON governance_rules BEGIN
    UPDATE governance_rules SET updated_at = CURRENT_TIMESTAMP WHERE rule_id = NEW.rule_id;
END;

CREATE TRIGGER IF NOT EXISTS layers_updated_at AFTER UPDATE ON protection_layers BEGIN
    UPDATE protection_layers SET updated_at = CURRENT_TIMESTAMP WHERE layer_id = NEW.layer_id;
END;

-- Track rule changes in history
CREATE TRIGGER IF NOT EXISTS rules_track_changes AFTER UPDATE ON governance_rules BEGIN
    INSERT INTO rule_history (rule_id, change_type, previous_version, new_version, changes)
    VALUES (
        NEW.rule_id,
        'updated',
        OLD.version,
        NEW.version,
        json_object(
            'name_changed', OLD.name != NEW.name,
            'severity_changed', OLD.severity != NEW.severity,
            'description_changed', OLD.description != NEW.description,
            'enabled_changed', OLD.enabled != NEW.enabled
        )
    );
END;

-- ============================================================================
-- Migration Metadata
-- ============================================================================

-- Track migration from YAML
CREATE TABLE IF NOT EXISTS migration_metadata (
    migration_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_format TEXT NOT NULL,  -- 'yaml'
    source_file TEXT NOT NULL,  -- 'brain-protection-rules.yaml'
    target_format TEXT NOT NULL,  -- 'sqlite'
    target_file TEXT NOT NULL,  -- 'governance.db'
    rules_migrated INTEGER NOT NULL,
    layers_migrated INTEGER NOT NULL,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    migration_status TEXT NOT NULL CHECK (migration_status IN ('success', 'partial', 'failed')),
    migration_notes TEXT
);

-- ============================================================================
-- End of Schema
-- ============================================================================

-- Verify schema
SELECT 'Schema v3.0 applied successfully' as status;

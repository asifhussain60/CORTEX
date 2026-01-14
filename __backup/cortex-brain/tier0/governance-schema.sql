-- CORTEX Brain Protection Rules - SQLite Schema v1.0
-- Purpose: Replace brain-protection-rules.yaml with relational database
-- Author: CORTEX AI Assistant
-- Date: 2026-01-04

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description) 
VALUES (1, 'Initial governance schema - migrated from YAML');

-- Protection layers (24 layers)
CREATE TABLE IF NOT EXISTS protection_layers (
    layer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    priority INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_layer_priority ON protection_layers(priority);

-- Governance rules (61+ rules)
CREATE TABLE IF NOT EXISTS governance_rules (
    rule_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('blocked', 'warning', 'info')),
    description TEXT NOT NULL,
    layer_id TEXT NOT NULL,
    minimum_coverage INTEGER DEFAULT 0,
    version INTEGER NOT NULL DEFAULT 1,
    enabled BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (layer_id) REFERENCES protection_layers(layer_id) ON DELETE CASCADE
);

CREATE INDEX idx_rule_severity ON governance_rules(severity);
CREATE INDEX idx_rule_enabled ON governance_rules(enabled);
CREATE INDEX idx_rule_layer ON governance_rules(layer_id);

-- Detection patterns (keywords, scopes, logic)
CREATE TABLE IF NOT EXISTS rule_detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    detection_type TEXT NOT NULL CHECK (detection_type IN ('keyword', 'scope', 'combined')),
    keyword TEXT,
    scope TEXT,
    logic TEXT CHECK (logic IN ('AND', 'OR', NULL)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_detection_rule ON rule_detection(rule_id);
CREATE INDEX idx_detection_keyword ON rule_detection(keyword);

-- Test requirements
CREATE TABLE IF NOT EXISTS rule_test_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    test_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_test_rule ON rule_test_requirements(rule_id);

-- Alternatives (what to do instead)
CREATE TABLE IF NOT EXISTS rule_alternatives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    alternative TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_alt_rule ON rule_alternatives(rule_id);

-- Documentation (evidence templates, rationale, examples)
CREATE TABLE IF NOT EXISTS rule_documentation (
    rule_id TEXT PRIMARY KEY,
    evidence_template TEXT,
    rationale TEXT,
    examples_path TEXT,
    documentation_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Tier 0 instincts (61 immutable rules)
CREATE TABLE IF NOT EXISTS tier0_instincts (
    instinct_id TEXT PRIMARY KEY,
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instinct_order ON tier0_instincts(display_order);

-- Critical paths (protected file paths)
CREATE TABLE IF NOT EXISTS critical_paths (
    path TEXT PRIMARY KEY,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application paths (user application-specific)
CREATE TABLE IF NOT EXISTS application_paths (
    path TEXT PRIMARY KEY,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Brain state files (protected state files)
CREATE TABLE IF NOT EXISTS brain_state_files (
    file_path TEXT PRIMARY KEY,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rule violations log (track when rules are triggered)
CREATE TABLE IF NOT EXISTS rule_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    violation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    resolved BOOLEAN DEFAULT 0,
    resolution_notes TEXT,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id)
);

CREATE INDEX idx_violation_rule ON rule_violations(rule_id);
CREATE INDEX idx_violation_timestamp ON rule_violations(violation_timestamp);
CREATE INDEX idx_violation_resolved ON rule_violations(resolved);

-- Rule usage statistics
CREATE TABLE IF NOT EXISTS rule_usage_stats (
    rule_id TEXT PRIMARY KEY,
    trigger_count INTEGER DEFAULT 0,
    last_triggered TIMESTAMP,
    blocked_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

-- Full-text search for rules
CREATE VIRTUAL TABLE IF NOT EXISTS rules_fts USING fts5(
    rule_id UNINDEXED,
    name,
    description,
    rationale,
    content='governance_rules',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS rules_fts_insert AFTER INSERT ON governance_rules BEGIN
    INSERT INTO rules_fts(rowid, rule_id, name, description, rationale)
    SELECT 
        NEW.rowid,
        NEW.rule_id,
        NEW.name,
        NEW.description,
        (SELECT rationale FROM rule_documentation WHERE rule_id = NEW.rule_id)
    ;
END;

CREATE TRIGGER IF NOT EXISTS rules_fts_update AFTER UPDATE ON governance_rules BEGIN
    UPDATE rules_fts 
    SET 
        name = NEW.name,
        description = NEW.description,
        rationale = (SELECT rationale FROM rule_documentation WHERE rule_id = NEW.rule_id)
    WHERE rowid = NEW.rowid;
END;

CREATE TRIGGER IF NOT EXISTS rules_fts_delete AFTER DELETE ON governance_rules BEGIN
    DELETE FROM rules_fts WHERE rowid = OLD.rowid;
END;

-- Views for common queries

-- All rules with their layers
CREATE VIEW IF NOT EXISTS v_rules_full AS
SELECT 
    r.rule_id,
    r.name,
    r.severity,
    r.description,
    r.layer_id,
    l.name AS layer_name,
    l.priority AS layer_priority,
    r.minimum_coverage,
    r.enabled,
    r.version,
    r.created_at,
    r.updated_at
FROM governance_rules r
JOIN protection_layers l ON r.layer_id = l.layer_id
ORDER BY l.priority, r.rule_id;

-- Rules with usage statistics
CREATE VIEW IF NOT EXISTS v_rules_stats AS
SELECT 
    r.rule_id,
    r.name,
    r.severity,
    r.enabled,
    COALESCE(s.trigger_count, 0) AS trigger_count,
    COALESCE(s.blocked_count, 0) AS blocked_count,
    COALESCE(s.warning_count, 0) AS warning_count,
    s.last_triggered
FROM governance_rules r
LEFT JOIN rule_usage_stats s ON r.rule_id = s.rule_id
ORDER BY trigger_count DESC;

-- Active violations
CREATE VIEW IF NOT EXISTS v_active_violations AS
SELECT 
    v.id,
    v.rule_id,
    r.name AS rule_name,
    r.severity,
    v.violation_timestamp,
    v.context
FROM rule_violations v
JOIN governance_rules r ON v.rule_id = r.rule_id
WHERE v.resolved = 0
ORDER BY v.violation_timestamp DESC;

-- Metadata table for configuration
CREATE TABLE IF NOT EXISTS governance_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO governance_metadata (key, value) VALUES
    ('version', '2.4'),
    ('type', 'governance'),
    ('name', 'Brain Protection Rules'),
    ('enforcement', 'automated via Brain Protector agent'),
    ('total_rule_count', '61'),
    ('total_layers', '24'),
    ('migrated_from', 'brain-protection-rules.yaml'),
    ('migration_date', datetime('now'));

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rules_enabled_severity ON governance_rules(enabled, severity);
CREATE INDEX IF NOT EXISTS idx_violations_rule_resolved ON rule_violations(rule_id, resolved);

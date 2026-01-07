-- ============================================================================
-- CORTEX Brain Governance Schema (SQLite)
-- Version: 5.0.0
-- Purpose: Replace 7,057-line YAML with professional relational database
-- Benefits: <10ms queries, schema validation, zero parse errors, analytics
-- ============================================================================

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    rollback_sql TEXT
);

INSERT INTO schema_version (version, description) VALUES 
('5.0.0', 'Initial SQLite governance migration from brain-protection-rules.yaml');

-- ============================================================================
-- PROTECTION LAYERS (Top-level governance categories)
-- ============================================================================
CREATE TABLE IF NOT EXISTS protection_layers (
    layer_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL CHECK(priority >= 1 AND priority <= 100),
    enforcement_mode TEXT NOT NULL CHECK(enforcement_mode IN ('BLOCKING', 'WARNING', 'ADVISORY')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_layers_priority ON protection_layers(priority);
CREATE INDEX idx_layers_enforcement ON protection_layers(enforcement_mode);

-- ============================================================================
-- TIER0 INSTINCTS (Core unbreakable principles)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tier0_instincts (
    instinct_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    principle TEXT NOT NULL,
    rationale TEXT NOT NULL,
    priority INTEGER NOT NULL CHECK(priority >= 1 AND priority <= 100),
    applies_to TEXT, -- JSON array of contexts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instincts_priority ON tier0_instincts(priority);

-- ============================================================================
-- GOVERNANCE RULES (Main rule definitions)
-- ============================================================================
CREATE TABLE IF NOT EXISTS governance_rules (
    rule_id TEXT PRIMARY KEY,
    layer_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('BLOCKED', 'ERROR', 'WARNING', 'INFO')),
    enabled BOOLEAN NOT NULL DEFAULT 1,
    trigger_conditions TEXT, -- JSON array
    version TEXT DEFAULT '1.0.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (layer_id) REFERENCES protection_layers(layer_id) ON DELETE CASCADE
);

CREATE INDEX idx_rules_layer ON governance_rules(layer_id);
CREATE INDEX idx_rules_severity ON governance_rules(severity);
CREATE INDEX idx_rules_enabled ON governance_rules(enabled);
CREATE INDEX idx_rules_name ON governance_rules(name);

-- ============================================================================
-- DETECTION PATTERNS (What triggers a rule)
-- ============================================================================
CREATE TABLE IF NOT EXISTS detection_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL CHECK(pattern_type IN ('FILE', 'CODE', 'COMMAND', 'BEHAVIOR', 'STATE')),
    pattern TEXT NOT NULL,
    match_mode TEXT NOT NULL CHECK(match_mode IN ('EXACT', 'REGEX', 'CONTAINS', 'STARTS_WITH', 'ENDS_WITH')),
    case_sensitive BOOLEAN NOT NULL DEFAULT 1,
    priority INTEGER NOT NULL DEFAULT 50,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_patterns_rule ON detection_patterns(rule_id);
CREATE INDEX idx_patterns_type ON detection_patterns(pattern_type);

-- ============================================================================
-- VALIDATION CHECKS (How to verify rule compliance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS validation_checks (
    check_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    check_type TEXT NOT NULL CHECK(check_type IN ('FILE_EXISTS', 'FILE_CONTENT', 'DIRECTORY_STRUCTURE', 'GIT_STATUS', 'TEST_RESULT', 'CUSTOM_SCRIPT')),
    check_config TEXT NOT NULL, -- JSON configuration
    pass_criteria TEXT NOT NULL,
    fail_message TEXT NOT NULL,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_checks_rule ON validation_checks(rule_id);
CREATE INDEX idx_checks_type ON validation_checks(check_type);

-- ============================================================================
-- ALTERNATIVES (Allowed exceptions or workarounds)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rule_alternatives (
    alternative_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    description TEXT NOT NULL,
    when_allowed TEXT NOT NULL,
    approval_required BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_alternatives_rule ON rule_alternatives(rule_id);

-- ============================================================================
-- EVIDENCE TEMPLATES (What proof is needed for compliance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS evidence_templates (
    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL CHECK(evidence_type IN ('FILE', 'SCREENSHOT', 'LOG', 'TEST_OUTPUT', 'CODE_SNIPPET', 'DOCUMENT')),
    required BOOLEAN NOT NULL DEFAULT 1,
    description TEXT NOT NULL,
    format TEXT, -- Expected format (e.g., 'JSON', 'PNG', 'TXT')
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_evidence_rule ON evidence_templates(rule_id);
CREATE INDEX idx_evidence_required ON evidence_templates(required);

-- ============================================================================
-- RULE DEPENDENCIES (Rules that depend on other rules)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rule_dependencies (
    dependency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    depends_on_rule_id TEXT NOT NULL,
    dependency_type TEXT NOT NULL CHECK(dependency_type IN ('REQUIRES', 'CONFLICTS_WITH', 'SUPERSEDES')),
    description TEXT,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE,
    FOREIGN KEY (depends_on_rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE,
    UNIQUE(rule_id, depends_on_rule_id, dependency_type)
);

CREATE INDEX idx_deps_rule ON rule_dependencies(rule_id);
CREATE INDEX idx_deps_depends_on ON rule_dependencies(depends_on_rule_id);
CREATE INDEX idx_deps_type ON rule_dependencies(dependency_type);

-- ============================================================================
-- CRITICAL PATHS (Protected file paths and directories)
-- ============================================================================
CREATE TABLE IF NOT EXISTS critical_paths (
    path_id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    protection_level TEXT NOT NULL CHECK(protection_level IN ('READ_ONLY', 'MANUAL_COMMIT', 'ADMIN_ONLY', 'VERSIONED')),
    description TEXT NOT NULL,
    associated_rule_id TEXT,
    FOREIGN KEY (associated_rule_id) REFERENCES governance_rules(rule_id) ON DELETE SET NULL
);

CREATE INDEX idx_paths_protection ON critical_paths(protection_level);
CREATE INDEX idx_paths_rule ON critical_paths(associated_rule_id);

-- ============================================================================
-- RULE VIOLATIONS (Track when rules are violated)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rule_violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT, -- JSON context (file, line, user, etc.)
    severity TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT 0,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE
);

CREATE INDEX idx_violations_rule ON rule_violations(rule_id);
CREATE INDEX idx_violations_detected ON rule_violations(detected_at);
CREATE INDEX idx_violations_resolved ON rule_violations(resolved);

-- ============================================================================
-- RULE USAGE ANALYTICS (Track how often rules are checked)
-- ============================================================================
CREATE TABLE IF NOT EXISTS rule_usage_stats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT NOT NULL,
    check_date DATE NOT NULL,
    check_count INTEGER NOT NULL DEFAULT 0,
    violation_count INTEGER NOT NULL DEFAULT 0,
    avg_check_time_ms REAL,
    FOREIGN KEY (rule_id) REFERENCES governance_rules(rule_id) ON DELETE CASCADE,
    UNIQUE(rule_id, check_date)
);

CREATE INDEX idx_stats_rule ON rule_usage_stats(rule_id);
CREATE INDEX idx_stats_date ON rule_usage_stats(check_date);

-- ============================================================================
-- MIGRATION TRACKING (Track YAML to SQLite migration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS migration_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,
    migration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rules_migrated INTEGER NOT NULL,
    duplicates_removed INTEGER NOT NULL DEFAULT 0,
    errors_encountered INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

-- Rule coverage by layer
CREATE VIEW IF NOT EXISTS v_layer_coverage AS
SELECT 
    pl.layer_id,
    pl.name AS layer_name,
    pl.priority,
    COUNT(gr.rule_id) AS total_rules,
    SUM(CASE WHEN gr.enabled = 1 THEN 1 ELSE 0 END) AS enabled_rules,
    SUM(CASE WHEN gr.severity = 'BLOCKED' THEN 1 ELSE 0 END) AS blocking_rules
FROM protection_layers pl
LEFT JOIN governance_rules gr ON pl.layer_id = gr.layer_id
GROUP BY pl.layer_id, pl.name, pl.priority
ORDER BY pl.priority;

-- Rules with no detection patterns (incomplete)
CREATE VIEW IF NOT EXISTS v_incomplete_rules AS
SELECT 
    gr.rule_id,
    gr.name,
    gr.severity,
    gr.layer_id
FROM governance_rules gr
LEFT JOIN detection_patterns dp ON gr.rule_id = dp.rule_id
WHERE dp.pattern_id IS NULL
ORDER BY gr.severity DESC, gr.name;

-- Rule conflict detection
CREATE VIEW IF NOT EXISTS v_rule_conflicts AS
SELECT 
    rd.rule_id AS rule1,
    gr1.name AS rule1_name,
    rd.depends_on_rule_id AS rule2,
    gr2.name AS rule2_name,
    rd.dependency_type
FROM rule_dependencies rd
JOIN governance_rules gr1 ON rd.rule_id = gr1.rule_id
JOIN governance_rules gr2 ON rd.depends_on_rule_id = gr2.rule_id
WHERE rd.dependency_type = 'CONFLICTS_WITH';

-- Recent violations summary
CREATE VIEW IF NOT EXISTS v_recent_violations AS
SELECT 
    rv.violation_id,
    rv.rule_id,
    gr.name AS rule_name,
    gr.severity,
    rv.detected_at,
    rv.resolved,
    rv.resolved_at
FROM rule_violations rv
JOIN governance_rules gr ON rv.rule_id = gr.rule_id
WHERE rv.detected_at >= datetime('now', '-30 days')
ORDER BY rv.detected_at DESC;

-- Rule performance metrics
CREATE VIEW IF NOT EXISTS v_rule_performance AS
SELECT 
    rus.rule_id,
    gr.name AS rule_name,
    SUM(rus.check_count) AS total_checks,
    SUM(rus.violation_count) AS total_violations,
    ROUND(AVG(rus.avg_check_time_ms), 2) AS avg_check_time_ms,
    ROUND(100.0 * SUM(rus.violation_count) / NULLIF(SUM(rus.check_count), 0), 2) AS violation_rate_pct
FROM rule_usage_stats rus
JOIN governance_rules gr ON rus.rule_id = gr.rule_id
GROUP BY rus.rule_id, gr.name
ORDER BY total_checks DESC;

-- ============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS trg_rules_updated_at
AFTER UPDATE ON governance_rules
BEGIN
    UPDATE governance_rules SET updated_at = CURRENT_TIMESTAMP WHERE rule_id = NEW.rule_id;
END;

-- Prevent deletion of rules with unresolved violations
CREATE TRIGGER IF NOT EXISTS trg_prevent_rule_deletion
BEFORE DELETE ON governance_rules
BEGIN
    SELECT RAISE(ABORT, 'Cannot delete rule with unresolved violations')
    WHERE EXISTS (
        SELECT 1 FROM rule_violations 
        WHERE rule_id = OLD.rule_id AND resolved = 0
    );
END;

-- Log rule violations when detected
CREATE TRIGGER IF NOT EXISTS trg_log_violation
AFTER INSERT ON rule_violations
BEGIN
    UPDATE rule_usage_stats
    SET violation_count = violation_count + 1
    WHERE rule_id = NEW.rule_id AND check_date = DATE('now');
END;

-- ============================================================================
-- INDEXES FOR PERFORMANCE (<10ms query target)
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_rules_layer_severity ON governance_rules(layer_id, severity);
CREATE INDEX IF NOT EXISTS idx_violations_rule_resolved ON rule_violations(rule_id, resolved);
CREATE INDEX IF NOT EXISTS idx_patterns_rule_type ON detection_patterns(rule_id, pattern_type);

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- CORTEX Analytics Database Schema
-- Per-Application Metrics Storage
-- 
-- This schema defines 11 tables for comprehensive feedback analytics:
--   1. feedback_reports - Master report registry
--   2. application_metrics - Project size, tech stack
--   3. crawler_performance - Discovery statistics
--   4. cortex_performance - Operation timings
--   5. knowledge_graphs - Entity counts, density
--   6. development_hygiene - Code quality, security
--   7. tdd_mastery - Test coverage, test-first
--   8. commit_metrics - Build success, deployments
--   9. velocity_metrics - Sprint velocity, cycle time
--   10. trend_analysis - Time-series trends
--   11. issues_reported - Issue tracking
--
-- Author: Asif Hussain
-- Version: 1.0
-- Date: 2025-11-24

-- ========================================
-- 1. Master Report Registry
-- ========================================
CREATE TABLE IF NOT EXISTS feedback_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT NOT NULL,
    report_timestamp TIMESTAMP NOT NULL,
    report_hash TEXT UNIQUE NOT NULL,  -- SHA256 of report content (prevent duplicates)
    gist_url TEXT,
    privacy_level TEXT CHECK(privacy_level IN ('full', 'medium', 'minimal')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_from_gist BOOLEAN DEFAULT 0,
    validation_status TEXT CHECK(validation_status IN ('valid', 'warning', 'error')),
    validation_errors TEXT,  -- JSON array of validation issues
    UNIQUE(app_name, report_timestamp)
);

CREATE INDEX idx_feedback_reports_app ON feedback_reports(app_name);
CREATE INDEX idx_feedback_reports_timestamp ON feedback_reports(report_timestamp);
CREATE INDEX idx_feedback_reports_hash ON feedback_reports(report_hash);

-- ========================================
-- 2. Application Metrics
-- ========================================
CREATE TABLE IF NOT EXISTS application_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    project_size_mb REAL,
    lines_of_code INTEGER,
    file_count INTEGER,
    tech_stack TEXT,  -- JSON array
    test_coverage REAL,
    complexity_score REAL,
    dependency_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_app_metrics_report ON application_metrics(report_id);
CREATE INDEX idx_app_metrics_coverage ON application_metrics(test_coverage);

-- ========================================
-- 3. Crawler Performance
-- ========================================
CREATE TABLE IF NOT EXISTS crawler_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    discovery_runs INTEGER,
    success_rate REAL,
    cache_hit_rate REAL,
    avg_discovery_time REAL,
    elements_discovered INTEGER,
    error_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_crawler_perf_report ON crawler_performance(report_id);
CREATE INDEX idx_crawler_perf_success ON crawler_performance(success_rate);

-- ========================================
-- 4. CORTEX Performance
-- ========================================
CREATE TABLE IF NOT EXISTS cortex_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    avg_operation_time REAL,
    brain_db_size_mb REAL,
    tier1_size_mb REAL,
    tier2_size_mb REAL,
    tier3_size_mb REAL,
    token_efficiency REAL,
    memory_usage_mb REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_cortex_perf_report ON cortex_performance(report_id);
CREATE INDEX idx_cortex_perf_time ON cortex_performance(avg_operation_time);

-- ========================================
-- 5. Knowledge Graphs
-- ========================================
CREATE TABLE IF NOT EXISTS knowledge_graphs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    entity_count INTEGER,
    relationship_count INTEGER,
    graph_density REAL,
    update_frequency REAL,  -- Updates per day
    unique_patterns INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_kg_report ON knowledge_graphs(report_id);
CREATE INDEX idx_kg_density ON knowledge_graphs(graph_density);

-- ========================================
-- 6. Development Hygiene
-- ========================================
CREATE TABLE IF NOT EXISTS development_hygiene (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    clean_commit_rate REAL,
    branch_strategy_score REAL,
    security_vulnerabilities INTEGER,
    code_review_coverage REAL,
    documentation_coverage REAL,
    linting_pass_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_dev_hygiene_report ON development_hygiene(report_id);
CREATE INDEX idx_dev_hygiene_security ON development_hygiene(security_vulnerabilities);

-- ========================================
-- 7. TDD Mastery
-- ========================================
CREATE TABLE IF NOT EXISTS tdd_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    test_coverage REAL,
    test_first_adherence REAL,
    first_run_success_rate REAL,
    coverage_trend TEXT CHECK(coverage_trend IN ('improving', 'stable', 'declining', 'unknown')),
    test_count INTEGER,
    assertion_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_tdd_report ON tdd_mastery(report_id);
CREATE INDEX idx_tdd_coverage ON tdd_mastery(test_coverage);

-- ========================================
-- 8. Commit Metrics
-- ========================================
CREATE TABLE IF NOT EXISTS commit_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    build_success_rate REAL,
    deployment_frequency REAL,  -- Deployments per week
    rollback_rate REAL,
    mttr_hours REAL,  -- Mean time to recovery
    commit_count INTEGER,
    avg_commit_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_commit_metrics_report ON commit_metrics(report_id);
CREATE INDEX idx_commit_metrics_build ON commit_metrics(build_success_rate);

-- ========================================
-- 9. Velocity Metrics
-- ========================================
CREATE TABLE IF NOT EXISTS velocity_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    sprint_velocity REAL,
    cycle_time_days REAL,
    estimate_accuracy REAL,
    lead_time_days REAL,
    throughput REAL,
    wip_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_velocity_report ON velocity_metrics(report_id);
CREATE INDEX idx_velocity_sprint ON velocity_metrics(sprint_velocity);

-- ========================================
-- 10. Trend Analysis
-- ========================================
CREATE TABLE IF NOT EXISTS trend_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name TEXT NOT NULL,
    metric_category TEXT NOT NULL,  -- e.g., 'tdd_mastery', 'velocity_metrics'
    metric_name TEXT NOT NULL,      -- e.g., 'test_coverage', 'sprint_velocity'
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    trend_direction TEXT CHECK(trend_direction IN ('improving', 'stable', 'declining', 'insufficient_data')),
    change_percent REAL,
    first_value REAL,
    last_value REAL,
    average_value REAL,
    values_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(app_name, metric_category, metric_name, period_start)
);

CREATE INDEX idx_trend_app ON trend_analysis(app_name);
CREATE INDEX idx_trend_metric ON trend_analysis(metric_category, metric_name);
CREATE INDEX idx_trend_period ON trend_analysis(period_start, period_end);

-- ========================================
-- 11. Issues Reported
-- ========================================
CREATE TABLE IF NOT EXISTS issues_reported (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    app_name TEXT NOT NULL,
    issue_type TEXT NOT NULL,  -- 'security', 'build_failure', 'low_coverage', 'performance', etc.
    severity TEXT CHECK(severity IN ('critical', 'high', 'medium', 'low')),
    message TEXT NOT NULL,
    metric_value REAL,
    threshold_value REAL,
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES feedback_reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_issues_report ON issues_reported(report_id);
CREATE INDEX idx_issues_app ON issues_reported(app_name);
CREATE INDEX idx_issues_severity ON issues_reported(severity);
CREATE INDEX idx_issues_type ON issues_reported(issue_type);
CREATE INDEX idx_issues_resolved ON issues_reported(resolved_at);

-- ========================================
-- Views for Common Queries
-- ========================================

-- Latest metrics per application
CREATE VIEW IF NOT EXISTS latest_metrics AS
SELECT 
    fr.app_name,
    fr.report_timestamp,
    am.test_coverage as app_test_coverage,
    am.complexity_score,
    cp.success_rate as crawler_success_rate,
    cop.avg_operation_time,
    kg.graph_density,
    dh.security_vulnerabilities,
    tm.test_coverage as tdd_coverage,
    cm.build_success_rate,
    vm.sprint_velocity
FROM feedback_reports fr
LEFT JOIN application_metrics am ON fr.id = am.report_id
LEFT JOIN crawler_performance cp ON fr.id = cp.report_id
LEFT JOIN cortex_performance cop ON fr.id = cop.report_id
LEFT JOIN knowledge_graphs kg ON fr.id = kg.report_id
LEFT JOIN development_hygiene dh ON fr.id = dh.report_id
LEFT JOIN tdd_mastery tm ON fr.id = tm.report_id
LEFT JOIN commit_metrics cm ON fr.id = cm.report_id
LEFT JOIN velocity_metrics vm ON fr.id = vm.report_id
WHERE fr.id IN (
    SELECT MAX(id) FROM feedback_reports GROUP BY app_name
);

-- Critical issues summary
CREATE VIEW IF NOT EXISTS critical_issues_summary AS
SELECT 
    app_name,
    issue_type,
    COUNT(*) as issue_count,
    MAX(detected_at) as last_detected
FROM issues_reported
WHERE severity = 'critical' AND resolved_at IS NULL
GROUP BY app_name, issue_type
ORDER BY issue_count DESC, last_detected DESC;

-- Application health score (0-100)
CREATE VIEW IF NOT EXISTS application_health_scores AS
SELECT 
    fr.app_name,
    fr.report_timestamp,
    -- Weighted health score (0-100)
    ROUND(
        COALESCE(tm.test_coverage, 0) * 0.25 +                    -- 25% weight
        COALESCE(cm.build_success_rate, 0) * 0.20 +              -- 20% weight
        COALESCE(cp.success_rate, 0) * 0.15 +                    -- 15% weight
        COALESCE((100 - dh.security_vulnerabilities * 10), 0) * 0.15 +  -- 15% weight
        COALESCE(vm.sprint_velocity / 50 * 100, 0) * 0.15 +      -- 15% weight
        COALESCE(kg.graph_density * 100, 0) * 0.10,              -- 10% weight
        0
    ) as health_score
FROM feedback_reports fr
LEFT JOIN tdd_mastery tm ON fr.id = tm.report_id
LEFT JOIN commit_metrics cm ON fr.id = cm.report_id
LEFT JOIN crawler_performance cp ON fr.id = cp.report_id
LEFT JOIN development_hygiene dh ON fr.id = dh.report_id
LEFT JOIN velocity_metrics vm ON fr.id = vm.report_id
LEFT JOIN knowledge_graphs kg ON fr.id = kg.report_id
WHERE fr.id IN (
    SELECT MAX(id) FROM feedback_reports GROUP BY app_name
);

-- ========================================
-- Cleanup and Maintenance
-- ========================================

-- Trigger to auto-delete old resolved issues (keep 90 days)
CREATE TRIGGER IF NOT EXISTS cleanup_old_resolved_issues
AFTER UPDATE ON issues_reported
WHEN NEW.resolved_at IS NOT NULL 
    AND datetime(NEW.resolved_at) < datetime('now', '-90 days')
BEGIN
    DELETE FROM issues_reported 
    WHERE id = NEW.id;
END;

-- ========================================
-- Schema Version and Metadata
-- ========================================
CREATE TABLE IF NOT EXISTS schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO schema_metadata (key, value) VALUES ('version', '1.0');
INSERT OR REPLACE INTO schema_metadata (key, value) VALUES ('created_at', datetime('now'));
INSERT OR REPLACE INTO schema_metadata (key, value) VALUES ('description', 'CORTEX Analytics Database Schema - Per-Application Metrics');

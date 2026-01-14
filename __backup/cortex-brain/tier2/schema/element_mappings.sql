-- Element Mappings Schema - Issue #3 Fix (P1)
-- Purpose: Store discovered element IDs and navigation flows for test generation
-- Created: 2025-11-23
-- Author: Asif Hussain
-- Part of: TDD View Discovery Phase implementation

-- ============================================================================
-- Element Mappings: Discovered UI elements from Razor/Blazor views
-- ============================================================================

CREATE TABLE IF NOT EXISTS tier2_element_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Project context
    project_name TEXT NOT NULL,            -- Project identifier
    component_path TEXT NOT NULL,          -- Relative path to Razor/Blazor file
    
    -- Element identification
    element_id TEXT,                       -- HTML id attribute value
    element_type TEXT NOT NULL,            -- 'button', 'input', 'select', 'div', etc.
    data_testid TEXT,                      -- data-testid attribute value
    css_classes TEXT,                      -- JSON array of CSS classes
    
    -- Selector strategy
    selector_strategy TEXT NOT NULL,       -- Recommended selector: '#id' or '[data-testid="x"]'
    selector_priority INTEGER NOT NULL,    -- 1=ID, 2=data-testid, 3=class, 4=text
    
    -- User-facing information
    user_facing_text TEXT,                 -- Button text or input label
    line_number INTEGER,                   -- Line number in source file
    
    -- Timestamps
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified TIMESTAMP,               -- Last time element was verified to exist
    last_used_in_test TIMESTAMP,           -- Last time used in test generation
    
    -- Metadata
    attributes TEXT,                       -- JSON: all element attributes
    notes TEXT,                            -- Optional notes (e.g., "requires auth")
    
    -- Uniqueness constraint
    UNIQUE(project_name, component_path, element_id, selector_strategy)
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_element_mappings_project 
    ON tier2_element_mappings(project_name);
    
CREATE INDEX IF NOT EXISTS idx_element_mappings_component 
    ON tier2_element_mappings(component_path);
    
CREATE INDEX IF NOT EXISTS idx_element_mappings_element_id 
    ON tier2_element_mappings(element_id);
    
CREATE INDEX IF NOT EXISTS idx_element_mappings_selector 
    ON tier2_element_mappings(selector_strategy);
    
CREATE INDEX IF NOT EXISTS idx_element_mappings_priority 
    ON tier2_element_mappings(selector_priority);

-- ============================================================================
-- Navigation Flows: Complete user workflows (multi-step actions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tier2_navigation_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Flow identification
    project_name TEXT NOT NULL,
    flow_name TEXT NOT NULL,               -- 'Session Creation Workflow', 'Login Flow'
    description TEXT,                      -- Human-readable description
    
    -- Flow steps (ordered)
    steps TEXT NOT NULL,                   -- JSON array of navigation steps
    
    -- Metadata
    requires_auth INTEGER DEFAULT 0,       -- 1 if flow requires authentication
    route_path TEXT,                       -- URL route (@page directive)
    entry_point TEXT,                      -- Starting component path
    
    -- Usage tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 1.0,         -- Calculated: success/total
    
    -- Uniqueness
    UNIQUE(project_name, flow_name)
);

CREATE INDEX IF NOT EXISTS idx_navigation_flows_project 
    ON tier2_navigation_flows(project_name);
    
CREATE INDEX IF NOT EXISTS idx_navigation_flows_route 
    ON tier2_navigation_flows(route_path);
    
CREATE INDEX IF NOT EXISTS idx_navigation_flows_success_rate 
    ON tier2_navigation_flows(success_rate DESC);

-- ============================================================================
-- Element Discovery History: Track discovery runs for change detection
-- ============================================================================

CREATE TABLE IF NOT EXISTS tier2_discovery_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Run metadata
    project_name TEXT NOT NULL,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discovery_type TEXT NOT NULL,          -- 'full', 'incremental', 'single_file'
    
    -- Results
    files_scanned INTEGER DEFAULT 0,
    elements_discovered INTEGER DEFAULT 0,
    elements_added INTEGER DEFAULT 0,      -- New elements
    elements_updated INTEGER DEFAULT 0,    -- Changed elements
    elements_removed INTEGER DEFAULT 0,    -- Deleted elements
    
    -- Performance
    duration_ms INTEGER,
    
    -- Notes
    warnings TEXT,                         -- JSON array of warnings
    errors TEXT                            -- JSON array of errors
);

CREATE INDEX IF NOT EXISTS idx_discovery_runs_project 
    ON tier2_discovery_runs(project_name);
    
CREATE INDEX IF NOT EXISTS idx_discovery_runs_timestamp 
    ON tier2_discovery_runs(run_timestamp DESC);

-- ============================================================================
-- Element Changes: Track when elements are added/removed (change detection)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tier2_element_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Change metadata
    project_name TEXT NOT NULL,
    component_path TEXT NOT NULL,
    change_type TEXT NOT NULL,             -- 'added', 'removed', 'modified'
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Element details
    element_id TEXT,
    selector_strategy TEXT,
    old_value TEXT,                        -- For modifications: old selector/text
    new_value TEXT,                        -- For modifications: new selector/text
    
    -- Discovery run reference
    discovery_run_id INTEGER,
    
    FOREIGN KEY (discovery_run_id) REFERENCES tier2_discovery_runs(id)
);

CREATE INDEX IF NOT EXISTS idx_element_changes_project 
    ON tier2_element_changes(project_name);
    
CREATE INDEX IF NOT EXISTS idx_element_changes_type 
    ON tier2_element_changes(change_type);
    
CREATE INDEX IF NOT EXISTS idx_element_changes_timestamp 
    ON tier2_element_changes(change_timestamp DESC);

-- ============================================================================
-- VIEWS: Convenient queries
-- ============================================================================

-- View: Elements without IDs (need improvement)
CREATE VIEW IF NOT EXISTS view_elements_without_ids AS
SELECT 
    project_name,
    component_path,
    element_type,
    user_facing_text,
    selector_strategy,
    line_number,
    discovered_at
FROM tier2_element_mappings
WHERE element_id IS NULL 
  AND data_testid IS NULL
  AND selector_priority > 2  -- Only class or text-based selectors
ORDER BY component_path, line_number;

-- View: Recently discovered elements (last 7 days)
CREATE VIEW IF NOT EXISTS view_recent_discoveries AS
SELECT 
    project_name,
    component_path,
    element_id,
    element_type,
    selector_strategy,
    discovered_at
FROM tier2_element_mappings
WHERE discovered_at >= datetime('now', '-7 days')
ORDER BY discovered_at DESC;

-- View: Most used elements in tests
CREATE VIEW IF NOT EXISTS view_popular_elements AS
SELECT 
    project_name,
    element_id,
    element_type,
    selector_strategy,
    user_facing_text,
    last_used_in_test,
    (JULIANDAY('now') - JULIANDAY(last_used_in_test)) as days_since_use
FROM tier2_element_mappings
WHERE last_used_in_test IS NOT NULL
ORDER BY last_used_in_test DESC
LIMIT 50;

-- View: Navigation flow success rates
CREATE VIEW IF NOT EXISTS view_flow_success_rates AS
SELECT 
    project_name,
    flow_name,
    usage_count,
    success_count,
    failure_count,
    ROUND(success_rate * 100, 1) as success_rate_pct,
    last_used
FROM tier2_navigation_flows
WHERE usage_count > 0
ORDER BY success_rate DESC, usage_count DESC;

-- ============================================================================
-- Schema Version
-- ============================================================================

INSERT OR IGNORE INTO schema_version (version, description) VALUES
    ('1.2.0', 'Added Tier 2 Element Mappings for TDD View Discovery (Issue #3 Fix)');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
-- Tables Created: 4 (element_mappings, navigation_flows, discovery_runs, element_changes)
-- Indexes Created: 14
-- Views Created: 4
-- Purpose: Enable TDD workflow to discover element IDs before test generation

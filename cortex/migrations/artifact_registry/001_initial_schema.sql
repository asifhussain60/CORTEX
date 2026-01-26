-- Migration 001: Initial Artifact Registry Schema
--
-- Creates 3 core tables for federated artifact registry:
-- 1. artifact_registry - Central metadata for all generated artifacts
-- 2. artifact_version_log - Version history and migration tracking
-- 3. artifact_cleanup_queue - Garbage collection scheduler
--
-- Authority: CORE-035 (Single Canonical Source)
-- Date: 2026-01-26
-- Version: 1.0

-- ============================================================================
-- TABLE 1: artifact_registry
-- Central metadata store for all generated artifacts (viewers, reports, docs)
-- ============================================================================

CREATE TABLE IF NOT EXISTS artifact_registry (
    -- Primary Key & Relationships
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL,
    
    -- Artifact Type & Classification
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('viewer', 'report', 'documentation', 'other')),
    artifact_subtype TEXT,  -- e.g., 'html-5-glassmorphism', 'pdf-report', 'markdown-guide'
    
    -- Physical Location (ephemeral - regenerated on access)
    artifact_path TEXT NOT NULL,  -- Relative to .cortex/cache/ or CDN path
    artifact_hash TEXT UNIQUE,  -- MD5 of artifact content for dedup
    
    -- Capability-Based Versioning (no version field - uses capabilities)
    capability_generated_under TEXT NOT NULL,  -- e.g., "artifact:viewer-v1", "artifact:report-v2"
    capabilities_required TEXT,  -- JSON array of capabilities needed for compatibility
    
    -- Implicit Multi-Tenancy Namespacing
    workspace_id TEXT,  -- Implicit namespace (dev team, org, etc)
    environment TEXT CHECK (environment IN ('dev', 'staging', 'prod')),  -- Deployment environment
    
    -- Metadata & Audit
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_by TEXT,  -- Orchestrator name or service
    expires_at DATETIME,  -- Lazy cleanup scheduled time
    
    -- Content Tracking
    size_bytes INTEGER,  -- File size in bytes
    mime_type TEXT,  -- e.g., 'text/html', 'application/pdf'
    encoding TEXT DEFAULT 'utf-8',
    
    -- Relationship to Plan
    plan_phase_id INTEGER,  -- Which phase of plan generated this
    
    -- Status & Flags
    is_cached BOOLEAN DEFAULT true,  -- In-memory or filesystem cache?
    is_published BOOLEAN DEFAULT false,  -- Available for external consumption?
    is_deprecated BOOLEAN DEFAULT false,  -- Marked for cleanup
    
    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Metadata (extensible JSON)
    metadata JSON,  -- { "source": "planning_orchestrator", "format_version": "1.0", ... }
    
    FOREIGN KEY (plan_id) REFERENCES plan_registry(plan_id) ON DELETE CASCADE
);

-- Indexes for efficient queries
CREATE INDEX idx_artifact_plan ON artifact_registry(plan_id);
CREATE INDEX idx_artifact_type ON artifact_registry(artifact_type);
CREATE INDEX idx_artifact_capability ON artifact_registry(capability_generated_under);
CREATE INDEX idx_artifact_workspace ON artifact_registry(workspace_id, environment);
CREATE INDEX idx_artifact_expires ON artifact_registry(expires_at);
CREATE INDEX idx_artifact_deprecated ON artifact_registry(is_deprecated);


-- ============================================================================
-- TABLE 2: artifact_version_log
-- Version history and migration tracking for forward/backward compatibility
-- ============================================================================

CREATE TABLE IF NOT EXISTS artifact_version_log (
    -- Primary Key
    version_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    
    -- Version Identity (capability-based, not numeric)
    capability_version TEXT NOT NULL,  -- e.g., "artifact:viewer-capability-v1"
    migration_status TEXT CHECK (migration_status IN ('pending', 'applied', 'reverted', 'failed')),
    
    -- Change Tracking
    change_reason TEXT,  -- Why this version was created
    change_description TEXT,  -- Human-readable description
    
    -- Migration Details
    migration_type TEXT CHECK (migration_type IN ('schema', 'format', 'capability', 'content')),
    breaking_change BOOLEAN DEFAULT false,  -- Requires special handling?
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    reverted_at DATETIME,
    
    -- Audit Trail
    created_by TEXT,  -- Orchestrator or user
    applied_by TEXT,
    
    -- Forward/Backward Compatibility Info
    compatible_with TEXT,  -- JSON array of previous versions it's compatible with
    incompatible_with TEXT,  -- JSON array of incompatible versions
    
    FOREIGN KEY (artifact_id) REFERENCES artifact_registry(artifact_id) ON DELETE CASCADE
);

-- Indexes for migration queries
CREATE INDEX idx_version_artifact ON artifact_version_log(artifact_id);
CREATE INDEX idx_version_capability ON artifact_version_log(capability_version);
CREATE INDEX idx_version_status ON artifact_version_log(migration_status);
CREATE INDEX idx_version_applied ON artifact_version_log(applied_at);


-- ============================================================================
-- TABLE 3: artifact_cleanup_queue
-- Garbage collection scheduler (lazy ephemeral lifecycle)
-- ============================================================================

CREATE TABLE IF NOT EXISTS artifact_cleanup_queue (
    -- Primary Key
    cleanup_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL UNIQUE,
    
    -- Cleanup Scheduling
    scheduled_deletion_time DATETIME NOT NULL,
    cleanup_reason TEXT CHECK (cleanup_reason IN ('expired', 'deprecated', 'plan_deleted', 'manual', 'storage_limit')),
    
    -- Status Tracking
    status TEXT CHECK (status IN ('scheduled', 'in_progress', 'completed', 'failed', 'cancelled')) DEFAULT 'scheduled',
    
    -- Retry Logic
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    last_attempt_at DATETIME,
    last_error TEXT,
    
    -- Metadata
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    
    -- Safety Flags
    requires_confirmation BOOLEAN DEFAULT false,  -- Manual approval needed?
    confirmed_by TEXT,  -- Who approved the deletion?
    
    FOREIGN KEY (artifact_id) REFERENCES artifact_registry(artifact_id) ON DELETE CASCADE
);

-- Indexes for cleanup scheduling
CREATE INDEX idx_cleanup_scheduled ON artifact_cleanup_queue(scheduled_deletion_time);
CREATE INDEX idx_cleanup_status ON artifact_cleanup_queue(status);
CREATE INDEX idx_cleanup_artifact ON artifact_cleanup_queue(artifact_id);


-- ============================================================================
-- VIEW: active_artifacts
-- Shows currently active (non-deprecated, non-expired) artifacts
-- ============================================================================

CREATE VIEW IF NOT EXISTS active_artifacts AS
SELECT 
    artifact_id,
    plan_id,
    artifact_type,
    artifact_path,
    capability_generated_under,
    workspace_id,
    environment,
    generated_at,
    expires_at
FROM artifact_registry
WHERE is_deprecated = false
  AND is_cached = true
  AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP);


-- ============================================================================
-- VIEW: artifact_statistics
-- Aggregated statistics for monitoring and reporting
-- ============================================================================

CREATE VIEW IF NOT EXISTS artifact_statistics AS
SELECT 
    artifact_type,
    COUNT(*) AS total_count,
    COUNT(CASE WHEN is_deprecated = false THEN 1 END) AS active_count,
    SUM(size_bytes) AS total_size_bytes,
    AVG(size_bytes) AS avg_size_bytes,
    MAX(generated_at) AS latest_generated
FROM artifact_registry
GROUP BY artifact_type;


-- ============================================================================
-- Metadata: Schema Version
-- ============================================================================

INSERT OR IGNORE INTO metadata (key, value, version)
VALUES ('artifact_registry_schema_version', '1.0', 1);

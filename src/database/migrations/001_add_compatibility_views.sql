-- CORTEX Database Compatibility Views
-- Version: 1.0.0
-- Purpose: Create views to maintain backward compatibility during schema transition
-- Date: 2026-01-05

-- ============================================================================
-- VIEW: tier2_patterns (maps to patterns table)
-- ============================================================================
-- This view provides backward compatibility for code expecting tier2_patterns
-- Maps new schema (patterns: title, content) to old schema (tier2_patterns: name, description)

CREATE VIEW IF NOT EXISTS tier2_patterns AS
SELECT 
    id,
    pattern_id,
    title AS name,                      -- Map title → name
    content AS description,             -- Map content → description
    pattern_type AS category,           -- Map pattern_type → category
    confidence,
    created_at,
    last_accessed,
    access_count,
    source AS source_conversation_id,   -- Map source → source_conversation_id
    metadata AS context,                -- Map metadata → context
    is_pinned,
    scope,
    namespaces,
    usage_count,
    last_used
FROM patterns;

-- ============================================================================
-- Verification Query (uncomment to test after applying migration)
-- ============================================================================
-- SELECT COUNT(*) as total_patterns FROM tier2_patterns;
-- SELECT name, description, category FROM tier2_patterns LIMIT 5;

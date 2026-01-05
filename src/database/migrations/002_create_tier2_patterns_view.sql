-- Migration 002: Create tier2_patterns compatibility view
-- Database: tier2/knowledge_graph.db
-- Purpose: Map old tier2_patterns API to new patterns table schema
-- Author: Asif Hussain
-- Date: 2026-01-05
-- Note: FTS tables cannot be views, so code must use patterns/patterns_fts directly

-- Drop existing view if present
DROP VIEW IF EXISTS tier2_patterns;

-- Create view mapping old API (name, description, category) to new schema (title, content, pattern_type)
CREATE VIEW tier2_patterns AS 
    SELECT 
        pattern_id,
        title AS name,
        content AS description,
        pattern_type AS category,
        confidence,
        created_at,
        last_accessed,
        access_count,
        '' AS source_conversation_id,  -- deprecated field (no longer used)
        metadata AS context,
        is_pinned,
        scope,
        namespaces,
        usage_count,
        last_used
    FROM patterns;

-- Validation: Ensure view works
SELECT name, description FROM tier2_patterns LIMIT 1;

-- Migration: Add missing columns to patterns table
-- This aligns the patterns table with the schema in src/tier2/knowledge_graph/database/schema.py

-- Add missing columns to patterns table
ALTER TABLE patterns ADD COLUMN last_used TIMESTAMP;
ALTER TABLE patterns ADD COLUMN last_accessed TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE patterns ADD COLUMN access_count INTEGER DEFAULT 0;
ALTER TABLE patterns ADD COLUMN usage_count INTEGER DEFAULT 0;
ALTER TABLE patterns ADD COLUMN source TEXT;
ALTER TABLE patterns ADD COLUMN metadata TEXT;
ALTER TABLE patterns ADD COLUMN is_pinned INTEGER DEFAULT 0;
ALTER TABLE patterns ADD COLUMN scope TEXT DEFAULT 'cortex' CHECK (scope IN ('cortex', 'application'));
ALTER TABLE patterns ADD COLUMN namespaces TEXT DEFAULT '["CORTEX-core"]';
ALTER TABLE patterns ADD COLUMN id INTEGER;
ALTER TABLE patterns ADD COLUMN title TEXT;
ALTER TABLE patterns ADD COLUMN content TEXT;

-- Update existing rows with default values
UPDATE patterns SET last_accessed = created_at WHERE last_accessed IS NULL;
UPDATE patterns SET title = name WHERE title IS NULL;
UPDATE patterns SET content = context WHERE content IS NULL;

-- Record migration
INSERT OR IGNORE INTO schema_migrations (version, description)
VALUES (2, 'Add missing columns to patterns table for CORTEX 4.0 compatibility');

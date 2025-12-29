-- Add indexes for better query performance

-- Conversations indexes
CREATE INDEX IF NOT EXISTS idx_conversations_namespace 
    ON conversations(namespace);

CREATE INDEX IF NOT EXISTS idx_conversations_quality 
    ON conversations(quality DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_captured_at 
    ON conversations(captured_at DESC);

-- Patterns indexes
CREATE INDEX IF NOT EXISTS idx_patterns_namespace 
    ON patterns(namespace);

CREATE INDEX IF NOT EXISTS idx_patterns_confidence 
    ON patterns(confidence DESC);

CREATE INDEX IF NOT EXISTS idx_patterns_type 
    ON patterns(pattern_type);

-- Context items indexes
CREATE INDEX IF NOT EXISTS idx_context_items_tier 
    ON context_items(tier);

CREATE INDEX IF NOT EXISTS idx_context_items_relevance 
    ON context_items(relevance_score DESC);

CREATE INDEX IF NOT EXISTS idx_context_items_namespace 
    ON context_items(namespace);

-- Record migration
INSERT OR IGNORE INTO schema_migrations (version, description)
VALUES (2, 'Add performance indexes');

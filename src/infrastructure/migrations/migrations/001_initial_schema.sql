-- Initial database schema for CORTEX
-- Creates tables for Tier 1, Tier 2, and Tier 3 data

-- Tier 1: Working Memory - Conversations
CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    quality REAL NOT NULL CHECK (quality >= 0.0 AND quality <= 1.0),
    participant_count INTEGER NOT NULL DEFAULT 0,
    entity_count INTEGER NOT NULL DEFAULT 0,
    captured_at TIMESTAMP NOT NULL,
    namespace TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tier 2: Knowledge Graph - Patterns
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    context TEXT NOT NULL,
    confidence REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    namespace TEXT NOT NULL,
    examples TEXT,  -- JSON array
    related_patterns TEXT,  -- JSON array
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Tier 1-3: Context Items
CREATE TABLE IF NOT EXISTS context_items (
    context_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    relevance_score REAL NOT NULL CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    namespace TEXT NOT NULL,
    tier INTEGER NOT NULL CHECK (tier IN (1, 2, 3)),
    source_id TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Metadata table for migration tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL
);

-- Insert initial migration record
INSERT OR IGNORE INTO schema_migrations (version, description)
VALUES (1, 'Initial schema - conversations, patterns, context_items');

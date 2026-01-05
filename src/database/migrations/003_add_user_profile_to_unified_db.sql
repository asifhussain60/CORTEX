-- Migration 003: Add user_profile to unified cortex-brain.db
-- Database: cortex-brain.db
-- Purpose: Ensure user_profile exists in unified database for backward compatibility
-- Author: Asif Hussain
-- Date: 2026-01-05

CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
    experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
    response_detail TEXT NOT NULL CHECK(response_detail IN ('concise', 'balanced', 'verbose')) DEFAULT 'balanced',
    tech_stack_preference TEXT DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    persistent_flag BOOLEAN NOT NULL DEFAULT 1
);

-- Create unique index to enforce singleton pattern
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id);

-- Insert default profile if not exists (expert autonomous user with concise responses)
INSERT OR IGNORE INTO user_profile (id, interaction_mode, experience_level, response_detail)
VALUES (1, 'autonomous', 'expert', 'concise');

-- Validation: Ensure profile exists with response_detail
SELECT response_detail FROM user_profile WHERE id = 1;

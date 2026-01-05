-- Migration 001: Add response_detail to user_profile
-- Database: tier1/working_memory.db
-- Purpose: Add missing response_detail column for user preference tracking
-- Author: Asif Hussain
-- Date: 2026-01-05

-- Add response_detail column if it doesn't exist
ALTER TABLE user_profile ADD COLUMN response_detail TEXT DEFAULT 'balanced' 
    CHECK(response_detail IN ('concise', 'balanced', 'verbose'));

-- Set default value for existing records
UPDATE user_profile 
SET response_detail = 'concise' 
WHERE response_detail IS NULL;

-- Validation: Ensure column exists and has valid values
SELECT response_detail FROM user_profile LIMIT 1;

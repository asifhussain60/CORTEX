-- ═══════════════════════════════════════════════════════════════════════
-- Context Efficiency Audit Queries (ENH-046 Phase 1.6)
-- ═══════════════════════════════════════════════════════════════════════
-- Purpose: Evidence-based validation of EXIT GATE performance
-- Database: cortex_brain/state/governance.db
-- Author: CORTEX Architect
-- Date: 2026-02-06
-- ═══════════════════════════════════════════════════════════════════════

-- Query 1: Context Synthesis Events (Last 24h)
-- Shows all context synthesis operations with token counts and timing
SELECT 
    timestamp,
    operation,
    ac_id,
    json_extract(details, '$.tokens') as tokens,
    json_extract(details, '$.initial_tokens') as initial_tokens,
    json_extract(details, '$.incremental_tokens') as incremental_tokens,
    json_extract(details, '$.intent') as intent,
    json_extract(details, '$.synthesis_time_ms') as synthesis_ms,
    json_extract(details, '$.cache_hit') as cache_hit,
    json_extract(details, '$.cache_hit_rate') as cache_hit_rate,
    status
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-24 hours')
ORDER BY timestamp DESC
LIMIT 100;

-- Query 2: Budget Violations (Exceeding Thresholds)
-- Identifies operations that exceeded context budget limits
SELECT 
    timestamp,
    ac_id,
    json_extract(details, '$.tokens') as total_tokens,
    json_extract(details, '$.initial_tokens') as initial_tokens,
    json_extract(details, '$.incremental_tokens') as incremental_tokens,
    json_extract(details, '$.budget_remaining') as budget_remaining,
    json_extract(details, '$.intent') as intent,
    CASE 
        WHEN CAST(json_extract(details, '$.initial_tokens') AS INTEGER) > 250 THEN 'INITIAL_BUDGET_EXCEEDED'
        WHEN CAST(json_extract(details, '$.incremental_tokens') AS INTEGER) > 500 THEN 'INCREMENTAL_BUDGET_EXCEEDED'
        WHEN CAST(json_extract(details, '$.tokens') AS INTEGER) > 2000 THEN 'SESSION_BUDGET_EXCEEDED'
    END as violation_type
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-24 hours')
  AND (
      CAST(json_extract(details, '$.initial_tokens') AS INTEGER) > 250
      OR CAST(json_extract(details, '$.incremental_tokens') AS INTEGER) > 500
      OR CAST(json_extract(details, '$.tokens') AS INTEGER) > 2000
  )
ORDER BY timestamp DESC;

-- Query 3: Cache Performance Metrics (7-Day Trend)
-- Aggregates cache hit rates and synthesis times by day
SELECT 
    date(timestamp) as date,
    COUNT(*) as total_syntheses,
    SUM(CASE WHEN json_extract(details, '$.cache_hit') = 'true' THEN 1 ELSE 0 END) as cache_hits,
    ROUND(AVG(CASE WHEN json_extract(details, '$.cache_hit') = 'true' THEN 1.0 ELSE 0.0 END) * 100, 2) as cache_hit_rate_pct,
    ROUND(AVG(CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)), 2) as avg_synthesis_ms,
    ROUND(AVG(CAST(json_extract(details, '$.tokens') AS REAL)), 0) as avg_tokens,
    MAX(CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)) as max_synthesis_ms,
    MAX(CAST(json_extract(details, '$.tokens') AS REAL)) as max_tokens
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-7 days')
GROUP BY date(timestamp)
ORDER BY date DESC;

-- Query 4: Intent-Specific Token Consumption
-- Analyzes token usage patterns by request intent
SELECT 
    json_extract(details, '$.intent') as intent,
    COUNT(*) as request_count,
    ROUND(AVG(CAST(json_extract(details, '$.tokens') AS REAL)), 0) as avg_total_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.initial_tokens') AS REAL)), 0) as avg_initial_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.incremental_tokens') AS REAL)), 0) as avg_incremental_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)), 2) as avg_synthesis_ms,
    MAX(CAST(json_extract(details, '$.tokens') AS REAL)) as max_tokens,
    SUM(CASE WHEN CAST(json_extract(details, '$.tokens') AS REAL) > 2000 THEN 1 ELSE 0 END) as budget_violations,
    ROUND(AVG(CAST(json_extract(details, '$.cache_hit_rate') AS REAL)) * 100, 2) as avg_cache_hit_rate_pct
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-7 days')
  AND json_extract(details, '$.intent') IS NOT NULL
GROUP BY json_extract(details, '$.intent')
ORDER BY avg_total_tokens DESC;

-- Query 5: Synthesis Performance Distribution (P50, P95, P99)
-- Calculates percentiles for synthesis time and token consumption
WITH ranked_data AS (
    SELECT 
        CAST(json_extract(details, '$.synthesis_time_ms') AS REAL) as synthesis_ms,
        CAST(json_extract(details, '$.tokens') AS REAL) as tokens,
        ROW_NUMBER() OVER (ORDER BY CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)) as time_rank,
        ROW_NUMBER() OVER (ORDER BY CAST(json_extract(details, '$.tokens') AS REAL)) as token_rank,
        COUNT(*) OVER () as total_count
    FROM audit_log
    WHERE operation LIKE '%context_synthesis%'
      AND timestamp >= datetime('now', '-7 days')
)
SELECT 
    'P50 (Median)' as percentile,
    (SELECT ROUND(synthesis_ms, 2) FROM ranked_data WHERE time_rank = CAST(total_count * 0.50 AS INTEGER) LIMIT 1) as synthesis_ms,
    (SELECT ROUND(tokens, 0) FROM ranked_data WHERE token_rank = CAST(total_count * 0.50 AS INTEGER) LIMIT 1) as tokens
UNION ALL
SELECT 
    'P95',
    (SELECT ROUND(synthesis_ms, 2) FROM ranked_data WHERE time_rank = CAST(total_count * 0.95 AS INTEGER) LIMIT 1),
    (SELECT ROUND(tokens, 0) FROM ranked_data WHERE token_rank = CAST(total_count * 0.95 AS INTEGER) LIMIT 1)
UNION ALL
SELECT 
    'P99',
    (SELECT ROUND(synthesis_ms, 2) FROM ranked_data WHERE time_rank = CAST(total_count * 0.99 AS INTEGER) LIMIT 1),
    (SELECT ROUND(tokens, 0) FROM ranked_data WHERE token_rank = CAST(total_count * 0.99 AS INTEGER) LIMIT 1);

-- Query 6: Hourly Synthesis Activity (Last 24h)
-- Shows synthesis activity patterns by hour
SELECT 
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    COUNT(*) as synthesis_count,
    ROUND(AVG(CAST(json_extract(details, '$.tokens') AS REAL)), 0) as avg_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)), 2) as avg_time_ms,
    SUM(CASE WHEN CAST(json_extract(details, '$.tokens') AS REAL) > 2000 THEN 1 ELSE 0 END) as violations
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-24 hours')
GROUP BY strftime('%Y-%m-%d %H:00', timestamp)
ORDER BY hour DESC;

-- Query 7: Summary Statistics (Overall Health Check)
-- Provides a quick health overview of context synthesis performance
SELECT 
    COUNT(*) as total_syntheses,
    ROUND(AVG(CAST(json_extract(details, '$.tokens') AS REAL)), 0) as avg_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.initial_tokens') AS REAL)), 0) as avg_initial_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.incremental_tokens') AS REAL)), 0) as avg_incremental_tokens,
    ROUND(AVG(CAST(json_extract(details, '$.synthesis_time_ms') AS REAL)), 2) as avg_synthesis_ms,
    MAX(CAST(json_extract(details, '$.tokens') AS REAL)) as max_tokens,
    MIN(CAST(json_extract(details, '$.tokens') AS REAL)) as min_tokens,
    SUM(CASE WHEN CAST(json_extract(details, '$.initial_tokens') AS REAL) > 250 THEN 1 ELSE 0 END) as initial_budget_violations,
    SUM(CASE WHEN CAST(json_extract(details, '$.incremental_tokens') AS REAL) > 500 THEN 1 ELSE 0 END) as incremental_budget_violations,
    SUM(CASE WHEN CAST(json_extract(details, '$.tokens') AS REAL) > 2000 THEN 1 ELSE 0 END) as session_budget_violations,
    ROUND(AVG(CASE WHEN json_extract(details, '$.cache_hit') = 'true' THEN 1.0 ELSE 0.0 END) * 100, 2) as overall_cache_hit_rate_pct,
    MIN(timestamp) as first_synthesis,
    MAX(timestamp) as last_synthesis
FROM audit_log
WHERE operation LIKE '%context_synthesis%'
  AND timestamp >= datetime('now', '-7 days');

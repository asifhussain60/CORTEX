# Tier 3: Development Context Design

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** 🏗️ DESIGN SPECIFICATION  
**Purpose:** Real-time project intelligence providing data-driven planning and proactive warnings

---

## 🎯 Overview

**Tier 3 = DEVELOPMENT CONTEXT** - Copilot's "balcony view" of your entire project.

**Purpose:**
- Track git activity and commit velocity patterns
- Monitor code health metrics and file stability
- Analyze testing activity and detect flaky tests
- Measure KDS/CORTEX usage effectiveness
- Identify work patterns and productive time slots
- Generate proactive warnings and data-driven insights
- Provide holistic project understanding for planning

**Storage:** SQLite (`cortex-brain.db`)  
**Size Target:** <50 KB (efficient time-series compression)  
**Performance Target:** <10ms for context queries  
**Update Frequency:** Delta updates (last N days), throttled to 1 hour minimum

**Key Differentiator from Other Tiers:**
- **Tier 0:** Immutable rules and governance
- **Tier 1:** Recent conversations (last 20)
- **Tier 2:** Learned patterns (permanent knowledge)
- **Tier 3:** Development metrics (time-series analytics)

---

## 📊 SQLite Schema

### Table: `context_git_metrics`

```sql
CREATE TABLE context_git_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,              -- Date of metric snapshot (YYYY-MM-DD)
    commits_count INTEGER NOT NULL DEFAULT 0, -- Commits on this date
    lines_added INTEGER NOT NULL DEFAULT 0,  -- Total lines added
    lines_deleted INTEGER NOT NULL DEFAULT 0, -- Total lines deleted
    net_growth INTEGER NOT NULL DEFAULT 0,   -- Net lines (added - deleted)
    files_changed INTEGER NOT NULL DEFAULT 0, -- Unique files modified
    contributor TEXT,                        -- Contributor name (NULL for aggregate)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, contributor)
);

-- Indexes
CREATE INDEX idx_git_date ON context_git_metrics(metric_date DESC);
CREATE INDEX idx_git_contributor ON context_git_metrics(contributor);
CREATE INDEX idx_git_commits ON context_git_metrics(commits_count DESC);

-- Materialized view for velocity calculations
CREATE VIEW git_velocity AS
SELECT 
    date(metric_date, '-' || (strftime('%w', metric_date)) || ' days') AS week_start,
    SUM(commits_count) AS commits_per_week,
    SUM(lines_added) AS lines_added_per_week,
    SUM(lines_deleted) AS lines_deleted_per_week,
    SUM(net_growth) AS net_growth_per_week,
    COUNT(DISTINCT metric_date) AS days_with_activity
FROM context_git_metrics
WHERE metric_date >= date('now', '-30 days')
    AND contributor IS NULL  -- Aggregate only
GROUP BY week_start
ORDER BY week_start DESC;
```

### Table: `context_file_hotspots`

```sql
CREATE TABLE context_file_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,                -- Relative file path
    period_start DATE NOT NULL,             -- Start of measurement period (30-day window)
    period_end DATE NOT NULL,               -- End of measurement period
    total_commits INTEGER NOT NULL DEFAULT 0, -- Total commits in project during period
    file_edits INTEGER NOT NULL DEFAULT 0,   -- How many commits modified this file
    churn_rate REAL NOT NULL CHECK(churn_rate >= 0.0 AND churn_rate <= 1.0), -- file_edits / total_commits
    stability TEXT NOT NULL CHECK(stability IN ('STABLE', 'MODERATE', 'UNSTABLE')),
    last_modified TIMESTAMP,                -- Last modification timestamp
    lines_changed INTEGER NOT NULL DEFAULT 0, -- Total lines changed in period
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_path, period_start, period_end)
);

-- Indexes
CREATE INDEX idx_hotspot_file ON context_file_hotspots(file_path);
CREATE INDEX idx_hotspot_churn ON context_file_hotspots(churn_rate DESC);
CREATE INDEX idx_hotspot_stability ON context_file_hotspots(stability);
CREATE INDEX idx_hotspot_period ON context_file_hotspots(period_start, period_end);

-- Stability classification trigger
CREATE TRIGGER classify_file_stability
BEFORE INSERT ON context_file_hotspots
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.churn_rate < 0.10 THEN 'STABLE'
        WHEN NEW.churn_rate < 0.20 THEN 'MODERATE'
        ELSE 'UNSTABLE'
    END INTO NEW.stability;
END;
```

### Table: `context_test_metrics`

```sql
CREATE TABLE context_test_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,              -- Date of test run
    test_type TEXT NOT NULL CHECK(test_type IN ('ui', 'unit', 'integration', 'e2e')),
    tests_discovered INTEGER NOT NULL DEFAULT 0, -- Total tests found
    tests_run INTEGER NOT NULL DEFAULT 0,    -- Tests executed
    tests_passed INTEGER NOT NULL DEFAULT 0, -- Successful tests
    tests_failed INTEGER NOT NULL DEFAULT 0, -- Failed tests
    tests_skipped INTEGER NOT NULL DEFAULT 0, -- Skipped tests
    pass_rate REAL CHECK(pass_rate >= 0.0 AND pass_rate <= 1.0), -- tests_passed / tests_run
    coverage_percentage REAL CHECK(coverage_percentage >= 0.0 AND coverage_percentage <= 1.0),
    avg_duration_seconds REAL,              -- Average test execution time
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, test_type)
);

-- Indexes
CREATE INDEX idx_test_date ON context_test_metrics(metric_date DESC);
CREATE INDEX idx_test_type ON context_test_metrics(test_type);
CREATE INDEX idx_test_pass_rate ON context_test_metrics(pass_rate DESC);
CREATE INDEX idx_test_coverage ON context_test_metrics(coverage_percentage DESC);
```

### Table: `context_flaky_tests`

```sql
CREATE TABLE context_flaky_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,                -- Full test name/path
    test_type TEXT NOT NULL CHECK(test_type IN ('ui', 'unit', 'integration', 'e2e')),
    first_detected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_runs INTEGER NOT NULL DEFAULT 0,  -- Total times test was executed
    failure_count INTEGER NOT NULL DEFAULT 0, -- How many times it failed
    failure_rate REAL NOT NULL CHECK(failure_rate >= 0.0 AND failure_rate <= 1.0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'FIXED', 'IGNORED')),
    failure_pattern TEXT,                   -- JSON array of failure reasons
    resolution_notes TEXT,                  -- How it was fixed (if fixed)
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_name)
);

-- Indexes
CREATE INDEX idx_flaky_name ON context_flaky_tests(test_name);
CREATE INDEX idx_flaky_rate ON context_flaky_tests(failure_rate DESC);
CREATE INDEX idx_flaky_status ON context_flaky_tests(status);
CREATE INDEX idx_flaky_last_seen ON context_flaky_tests(last_seen DESC);

-- Auto-mark as FIXED if no failures in 30 days
CREATE TRIGGER auto_fix_flaky_tests
AFTER UPDATE OF last_seen ON context_flaky_tests
WHEN NEW.status = 'ACTIVE'
    AND (julianday('now') - julianday(NEW.last_seen)) > 30
BEGIN
    UPDATE context_flaky_tests
    SET status = 'FIXED',
        resolution_notes = 'Auto-resolved: No failures in 30 days'
    WHERE id = NEW.id;
END;
```

### Table: `context_build_metrics`

```sql
CREATE TABLE context_build_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,              -- Date of build
    builds_total INTEGER NOT NULL DEFAULT 0, -- Total build attempts
    builds_successful INTEGER NOT NULL DEFAULT 0, -- Successful builds
    builds_failed INTEGER NOT NULL DEFAULT 0, -- Failed builds
    success_rate REAL CHECK(success_rate >= 0.0 AND success_rate <= 1.0),
    avg_build_time_seconds REAL,           -- Average build duration
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date)
);

-- Indexes
CREATE INDEX idx_build_date ON context_build_metrics(metric_date DESC);
CREATE INDEX idx_build_success_rate ON context_build_metrics(success_rate DESC);
```

### Table: `context_work_patterns`

```sql
CREATE TABLE context_work_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_date DATE NOT NULL,             -- Date of work session
    time_slot TEXT NOT NULL CHECK(time_slot IN (
        '00-02', '02-04', '04-06', '06-08', '08-10', '10-12',
        '12-14', '14-16', '16-18', '18-20', '20-22', '22-24'
    )),
    sessions_count INTEGER NOT NULL DEFAULT 0, -- Sessions in this time slot
    sessions_successful INTEGER NOT NULL DEFAULT 0, -- Successfully completed
    success_rate REAL CHECK(success_rate >= 0.0 AND success_rate <= 1.0),
    avg_duration_minutes INTEGER,          -- Average session length
    avg_focus_duration_minutes INTEGER,    -- Average uninterrupted time
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pattern_date, time_slot)
);

-- Indexes
CREATE INDEX idx_work_date ON context_work_patterns(pattern_date DESC);
CREATE INDEX idx_work_slot ON context_work_patterns(time_slot);
CREATE INDEX idx_work_success ON context_work_patterns(success_rate DESC);

-- Materialized view for best productivity times
CREATE VIEW best_work_times AS
SELECT 
    time_slot,
    SUM(sessions_count) AS total_sessions,
    SUM(sessions_successful) AS total_successful,
    AVG(success_rate) AS avg_success_rate,
    AVG(avg_duration_minutes) AS avg_duration
FROM context_work_patterns
WHERE pattern_date >= date('now', '-30 days')
GROUP BY time_slot
HAVING total_sessions >= 3  -- Minimum 3 sessions for statistical significance
ORDER BY avg_success_rate DESC;
```

### Table: `context_cortex_usage`

```sql
CREATE TABLE context_cortex_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date DATE NOT NULL,              -- Date of usage
    intent_type TEXT NOT NULL CHECK(intent_type IN ('PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'CORRECT', 'RESUME', 'ASK')),
    requests_count INTEGER NOT NULL DEFAULT 0, -- How many requests of this intent
    successful_count INTEGER NOT NULL DEFAULT 0, -- Successfully completed
    failed_count INTEGER NOT NULL DEFAULT 0,  -- Failed or abandoned
    avg_response_time_seconds REAL,        -- Average time to complete
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, intent_type)
);

-- Indexes
CREATE INDEX idx_cortex_date ON context_cortex_usage(metric_date DESC);
CREATE INDEX idx_cortex_intent ON context_cortex_usage(intent_type);
CREATE INDEX idx_cortex_success ON context_cortex_usage((CAST(successful_count AS REAL) / requests_count) DESC);
```

### Table: `context_correlations`

```sql
CREATE TABLE context_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_name TEXT NOT NULL UNIQUE,  -- e.g., "commit_size_vs_success"
    description TEXT NOT NULL,              -- Human-readable explanation
    metric_a TEXT NOT NULL,                 -- First metric being compared
    metric_b TEXT NOT NULL,                 -- Second metric being compared
    correlation_coefficient REAL NOT NULL CHECK(correlation_coefficient >= -1.0 AND correlation_coefficient <= 1.0),
    sample_size INTEGER NOT NULL,           -- How many data points used
    confidence_level REAL NOT NULL CHECK(confidence_level >= 0.0 AND confidence_level <= 1.0),
    insight TEXT,                           -- Generated insight text
    last_calculated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                           -- JSON for additional correlation data
);

-- Indexes
CREATE INDEX idx_corr_name ON context_correlations(correlation_name);
CREATE INDEX idx_corr_coefficient ON context_correlations(ABS(correlation_coefficient) DESC);
CREATE INDEX idx_corr_confidence ON context_correlations(confidence_level DESC);

-- Pre-defined correlations to track
INSERT INTO context_correlations (correlation_name, description, metric_a, metric_b, correlation_coefficient, sample_size, confidence_level, insight) VALUES
('commit_size_vs_success', 'Correlation between commit size and success rate', 'lines_changed', 'success_rate', -0.72, 0, 0.0, 'Pending calculation'),
('test_first_vs_rework', 'Correlation between TDD and rework rate', 'test_first_flag', 'rework_rate', -0.85, 0, 0.0, 'Pending calculation'),
('cortex_usage_vs_velocity', 'Correlation between CORTEX usage and commit velocity', 'cortex_usage_rate', 'velocity', 0.79, 0, 0.0, 'Pending calculation'),
('session_duration_vs_quality', 'Correlation between session length and success rate', 'session_duration', 'success_rate', -0.34, 0, 0.0, 'Pending calculation');
```

### Table: `context_insights`

```sql
CREATE TABLE context_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK(insight_type IN (
        'velocity_drop',                    -- Commit velocity decreased
        'file_hotspot',                     -- High-churn file warning
        'flaky_test',                       -- Unreliable test detected
        'build_health',                     -- Build success rate issue
        'test_coverage',                    -- Coverage trend warning
        'productivity_time',                -- Best time slot recommendation
        'session_duration',                 -- Session length recommendation
        'correlation_discovery'             -- New correlation found
    )),
    severity TEXT NOT NULL DEFAULT 'INFO' CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    title TEXT NOT NULL,                    -- Short insight title
    description TEXT NOT NULL,              -- Detailed explanation
    recommendation TEXT,                    -- Suggested action
    related_entity TEXT,                    -- File, test, or metric affected
    data_snapshot TEXT,                     -- JSON snapshot of relevant data
    acknowledged BOOLEAN NOT NULL DEFAULT 0, -- User has seen this insight
    acknowledged_at TIMESTAMP,              -- When user acknowledged
    dismissed BOOLEAN NOT NULL DEFAULT 0,   -- User dismissed this insight
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP                    -- When insight becomes stale
);

-- Indexes
CREATE INDEX idx_insight_type ON context_insights(insight_type);
CREATE INDEX idx_insight_severity ON context_insights(severity);
CREATE INDEX idx_insight_entity ON context_insights(related_entity);
CREATE INDEX idx_insight_active ON context_insights(acknowledged, dismissed);
CREATE INDEX idx_insight_created ON context_insights(created_at DESC);
```

### Table: `context_collection_log`

```sql
CREATE TABLE context_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    collector_name TEXT NOT NULL,           -- e.g., "GitMetricsCollector"
    collection_type TEXT NOT NULL CHECK(collection_type IN ('full', 'delta')),
    records_processed INTEGER NOT NULL DEFAULT 0,
    duration_seconds REAL NOT NULL,
    success BOOLEAN NOT NULL DEFAULT 1,
    error_message TEXT,                     -- NULL if successful
    metadata TEXT                           -- JSON with collection details
);

-- Indexes
CREATE INDEX idx_collection_timestamp ON context_collection_log(collection_timestamp DESC);
CREATE INDEX idx_collection_name ON context_collection_log(collector_name);
CREATE INDEX idx_collection_success ON context_collection_log(success);
```

---

## 🔄 Data Collection Strategy

### Delta Collection (Efficiency Optimization)

**Problem:** Full repository scans (git log, test discovery) take 2-5 minutes on large projects.

**Solution:** Delta collection - only process NEW data since last collection.

**Implementation:**

```python
class GitMetricsCollector:
    def collect(self, since: Optional[datetime] = None) -> List[GitMetric]:
        """
        Collect git metrics with delta optimization.
        
        Args:
            since: Only collect commits after this timestamp (delta mode)
                   If None, uses last_collection_time from database (default)
                   
        Returns:
            List of GitMetric objects
        """
        if since is None:
            # Auto-detect delta: get last collection time
            since = self._get_last_collection_time()
        
        if since is None:
            # First run: collect last 30 days
            since = datetime.now() - timedelta(days=30)
        
        # Only query commits since last collection
        commits = self._query_git_log(since=since)
        
        # Process and aggregate by date
        metrics = self._aggregate_by_date(commits)
        
        # Record collection timestamp
        self._record_collection_time()
        
        return metrics
    
    def _get_last_collection_time(self) -> Optional[datetime]:
        """Get timestamp of last successful collection."""
        result = db.query("""
            SELECT MAX(collection_timestamp) 
            FROM context_collection_log
            WHERE collector_name = 'GitMetricsCollector'
              AND success = 1
        """)
        return result[0] if result else None
```

### Collection Throttling (1-Hour Minimum)

**Problem:** BRAIN updates trigger after every 50 events. Tier 3 collection is expensive (2-5 min for full scan).

**Solution:** Only collect if >1 hour since last collection.

**Implementation:**

```python
class CollectorOrchestrator:
    def should_collect(self) -> bool:
        """
        Check if collection should run (throttling logic).
        
        Returns:
            True if >= 1 hour since last collection OR force flag set
        """
        last_collection = self._get_last_collection_time()
        
        if last_collection is None:
            return True  # First run
        
        hours_since = (datetime.now() - last_collection).total_seconds() / 3600
        
        return hours_since >= 1.0
    
    def collect_all(self, force: bool = False) -> CollectionResult:
        """
        Run all collectors with throttling.
        
        Args:
            force: Skip throttling check (for manual collection)
            
        Returns:
            CollectionResult with success/failure details
        """
        if not force and not self.should_collect():
            return CollectionResult(
                skipped=True,
                reason="Throttled: Last collection < 1 hour ago"
            )
        
        # Run collectors in sequence
        collectors = [
            GitMetricsCollector(),
            FileHotspotCollector(),
            TestMetricsCollector(),
            BuildMetricsCollector(),
            WorkPatternCollector()
        ]
        
        results = []
        for collector in collectors:
            try:
                result = collector.collect()  # Auto delta mode
                results.append(result)
            except Exception as e:
                # Log error but continue with other collectors
                logger.error(f"{collector.__class__.__name__} failed: {e}")
                results.append(CollectorResult(success=False, error=str(e)))
        
        return CollectionResult(results=results)
```

### Collection Triggers

**Automatic Triggers:**
1. **Brain Update Cycle** - When `brain-updater.md` processes events (if > 1 hour since last collection)
2. **Scheduled** - Every 6 hours via cron/task scheduler (delta collection)
3. **Post-Commit Hook** - After git commits (lightweight metrics only)

**Manual Triggers:**
1. **Force Collection** - User requests immediate collection (skip throttle)
2. **Setup/Migration** - Initial setup or migration (full collection)

**Priority:**
- **High Priority:** Git metrics (fast with delta)
- **Medium Priority:** Test metrics (if tests run recently)
- **Low Priority:** Build metrics (if builds happened)
- **On-Demand:** Correlation recalculation (only when needed)

---

## 📊 Query Performance Targets

### Fast Queries (<10ms)

```sql
-- Current velocity (last 7 days)
SELECT AVG(commits_count) * 7 AS commits_per_week
FROM context_git_metrics
WHERE metric_date >= date('now', '-7 days')
  AND contributor IS NULL;

-- File stability lookup
SELECT stability, churn_rate
FROM context_file_hotspots
WHERE file_path = ?
ORDER BY period_end DESC
LIMIT 1;

-- Best productivity time
SELECT time_slot, avg_success_rate
FROM best_work_times
LIMIT 1;

-- Active insights
SELECT * FROM context_insights
WHERE acknowledged = 0
  AND dismissed = 0
  AND (expires_at IS NULL OR expires_at > datetime('now'))
ORDER BY severity DESC, created_at DESC
LIMIT 10;
```

### Medium Queries (<50ms)

```sql
-- Velocity trend (last 30 days)
SELECT week_start, commits_per_week
FROM git_velocity
ORDER BY week_start DESC;

-- Top 10 hotspots
SELECT file_path, churn_rate, stability
FROM context_file_hotspots
WHERE period_end >= date('now', '-30 days')
ORDER BY churn_rate DESC
LIMIT 10;

-- Flaky tests summary
SELECT test_name, failure_rate, last_seen
FROM context_flaky_tests
WHERE status = 'ACTIVE'
ORDER BY failure_rate DESC;
```

### Complex Queries (<100ms)

```sql
-- Velocity forecast (linear regression)
WITH velocity_data AS (
    SELECT 
        julianday(week_start) - julianday('2024-01-01') AS x,
        commits_per_week AS y
    FROM git_velocity
    WHERE week_start >= date('now', '-90 days')
),
regression AS (
    SELECT 
        COUNT(*) AS n,
        SUM(x) AS sum_x,
        SUM(y) AS sum_y,
        SUM(x * x) AS sum_xx,
        SUM(x * y) AS sum_xy
    FROM velocity_data
)
SELECT 
    (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x) AS slope,
    (sum_y - slope * sum_x) / n AS intercept,
    slope * julianday('now', '+7 days') + intercept AS forecast_next_week
FROM regression;

-- Correlation calculation (commit size vs success)
WITH commit_data AS (
    SELECT 
        metric_date,
        lines_added + lines_deleted AS commit_size,
        (SELECT success_rate FROM context_work_patterns 
         WHERE pattern_date = context_git_metrics.metric_date 
         ORDER BY sessions_successful DESC LIMIT 1) AS success_rate
    FROM context_git_metrics
    WHERE metric_date >= date('now', '-30 days')
      AND contributor IS NULL
)
SELECT 
    (COUNT(*) * SUM(commit_size * success_rate) - SUM(commit_size) * SUM(success_rate)) /
    (SQRT(COUNT(*) * SUM(commit_size * commit_size) - SUM(commit_size) * SUM(commit_size)) *
     SQRT(COUNT(*) * SUM(success_rate * success_rate) - SUM(success_rate) * SUM(success_rate)))
    AS correlation_coefficient
FROM commit_data
WHERE success_rate IS NOT NULL;
```

---

## 🚨 Proactive Insight Generation

### Insight Generator Architecture

```python
class InsightGenerator:
    """
    Analyzes Tier 3 data and generates proactive warnings/recommendations.
    Runs after each collection cycle.
    """
    
    def generate_insights(self) -> List[Insight]:
        """Generate all insights from current context data."""
        insights = []
        
        # Check each insight type
        insights.extend(self._check_velocity_drop())
        insights.extend(self._check_file_hotspots())
        insights.extend(self._check_flaky_tests())
        insights.extend(self._check_build_health())
        insights.extend(self._check_test_coverage())
        insights.extend(self._check_productivity_patterns())
        insights.extend(self._check_new_correlations())
        
        # Save to database
        self._save_insights(insights)
        
        return insights
    
    def _check_velocity_drop(self) -> List[Insight]:
        """Detect significant velocity decreases."""
        baseline = self._get_baseline_velocity()  # 30-day average
        current_week = self._get_current_week_velocity()
        
        drop_percent = (baseline - current_week) / baseline
        
        if drop_percent >= 0.30:  # 30%+ drop
            return [Insight(
                insight_type='velocity_drop',
                severity='WARNING' if drop_percent < 0.50 else 'ERROR',
                title=f"Velocity dropped {drop_percent:.0%} this week",
                description=f"Baseline: {baseline:.0f} commits/week. Current: {current_week:.0f} commits/week.",
                recommendation="Consider smaller commits, more frequent tests, or address blockers",
                data_snapshot=json.dumps({
                    'baseline': baseline,
                    'current': current_week,
                    'drop_percent': drop_percent
                })
            )]
        
        return []
    
    def _check_file_hotspots(self) -> List[Insight]:
        """Warn about high-churn files."""
        hotspots = self._query_unstable_files()
        
        insights = []
        for hotspot in hotspots:
            if hotspot.churn_rate >= 0.20:  # 20%+ churn
                insights.append(Insight(
                    insight_type='file_hotspot',
                    severity='WARNING',
                    title=f"{hotspot.file_path} is a hotspot ({hotspot.churn_rate:.0%} churn)",
                    description=f"This file modified in {hotspot.file_edits} of last {hotspot.total_commits} commits",
                    recommendation="Add extra testing - file is unstable",
                    related_entity=hotspot.file_path,
                    data_snapshot=json.dumps({
                        'churn_rate': hotspot.churn_rate,
                        'edits': hotspot.file_edits,
                        'stability': hotspot.stability
                    })
                ))
        
        return insights
    
    def _check_flaky_tests(self) -> List[Insight]:
        """Alert on unreliable tests."""
        flaky = self._query_flaky_tests()
        
        insights = []
        for test in flaky:
            if test.failure_rate >= 0.10:  # 10%+ failure rate
                insights.append(Insight(
                    insight_type='flaky_test',
                    severity='WARNING',
                    title=f"{test.test_name} fails {test.failure_rate:.0%} of the time",
                    description="Test has inconsistent results",
                    recommendation="Investigate and stabilize (add waits, fix race conditions)",
                    related_entity=test.test_name,
                    data_snapshot=json.dumps({
                        'failure_rate': test.failure_rate,
                        'total_runs': test.total_runs,
                        'failures': test.failure_count
                    })
                ))
        
        return insights
```

### Insight Display Integration

**In WorkPlanner (before creating plan):**

```python
def create_plan(request: str) -> Plan:
    # Step 1: Generate insights for this request
    insights = insight_generator.get_relevant_insights(request)
    
    # Step 2: Display insights to user
    if insights:
        display_insights(insights)
    
    # Step 3: Create plan (insights influence planning)
    plan = planner.create(request, context_insights=insights)
    
    return plan

def display_insights(insights: List[Insight]):
    print("🧠 CORTEX Insights:")
    print("─" * 60)
    
    for insight in insights:
        icon = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }[insight.severity]
        
        print(f"{icon} {insight.title}")
        print(f"   💡 {insight.recommendation}")
        print()
```

**Example Output:**

```
🧠 CORTEX Insights:
────────────────────────────────────────────────────────────
⚠️ HostControlPanel.razor is a hotspot (28% churn)
   💡 Add extra testing - file is unstable

✅ Test-first approach has 96% success rate
   💡 Continue TDD workflow

⚠️ Velocity dropped 35% this week
   💡 Consider smaller commits, more frequent tests
────────────────────────────────────────────────────────────

Routing to WorkPlanner...
```

---

## 🎯 Migration from KDS v8

### Data Migration Script

```python
class Tier3Migrator:
    """Migrate KDS v8 development-context.yaml to CORTEX SQLite."""
    
    def migrate(self, kds_yaml_path: str):
        """
        Main migration entry point.
        
        Args:
            kds_yaml_path: Path to KDS development-context.yaml
        """
        # Load KDS data
        kds_data = self._load_kds_yaml(kds_yaml_path)
        
        # Migrate each category
        self._migrate_git_metrics(kds_data['git_activity'])
        self._migrate_file_hotspots(kds_data['file_hotspots'])
        self._migrate_test_metrics(kds_data['test_activity'])
        self._migrate_build_metrics(kds_data['build_health'])
        self._migrate_work_patterns(kds_data['work_patterns'])
        self._migrate_correlations(kds_data['correlations'])
        
        # Generate initial insights
        self._generate_initial_insights()
        
        print("✅ Tier 3 migration complete")
    
    def _migrate_git_metrics(self, git_data: dict):
        """Migrate git activity snapshot to time-series."""
        # KDS stores snapshot, CORTEX needs time-series
        # Generate last 30 days from current snapshot
        
        commits_30d = git_data['commits_30d']
        velocity_weekly = git_data.get('velocity_per_week', [])
        
        if velocity_weekly:
            # Backfill 4 weeks
            for i, week_commits in enumerate(velocity_weekly):
                week_start = date.today() - timedelta(weeks=i+1)
                
                # Distribute commits across week
                for day in range(7):
                    metric_date = week_start + timedelta(days=day)
                    commits_per_day = week_commits / 7  # Rough distribution
                    
                    db.insert('context_git_metrics', {
                        'metric_date': metric_date,
                        'commits_count': int(commits_per_day),
                        'lines_added': 0,  # Not available in KDS
                        'lines_deleted': 0,
                        'net_growth': 0,
                        'contributor': None  # Aggregate
                    })
        else:
            # Fallback: distribute commits evenly
            avg_per_day = commits_30d / 30
            for i in range(30):
                metric_date = date.today() - timedelta(days=i)
                
                db.insert('context_git_metrics', {
                    'metric_date': metric_date,
                    'commits_count': int(avg_per_day),
                    'contributor': None
                })
    
    def _migrate_file_hotspots(self, hotspots: list):
        """Migrate file hotspot data."""
        period_start = date.today() - timedelta(days=30)
        period_end = date.today()
        
        # Get total commits for churn calculation
        total_commits = db.query("""
            SELECT SUM(commits_count) 
            FROM context_git_metrics 
            WHERE metric_date >= ?
        """, [period_start])[0]
        
        for hotspot in hotspots:
            db.insert('context_file_hotspots', {
                'file_path': hotspot['file'],
                'period_start': period_start,
                'period_end': period_end,
                'total_commits': total_commits,
                'file_edits': hotspot['edits_30d'],
                'churn_rate': hotspot['churn_rate'],
                'stability': hotspot['status'].upper(),
                'last_modified': hotspot['last_modified']
            })
    
    def _migrate_correlations(self, correlations: dict):
        """Migrate correlation data."""
        for corr_name, corr_data in correlations.items():
            db.update('context_correlations', 
                where={'correlation_name': corr_name},
                values={
                    'correlation_coefficient': corr_data['correlation_coefficient'],
                    'insight': corr_data.get('insight'),
                    'sample_size': corr_data.get('sample_size', 0),
                    'confidence_level': 0.80,  # Assume moderate confidence
                    'last_calculated': datetime.now()
                }
            )
```

### Validation Tests

```python
def test_tier3_migration_velocity():
    """Verify git velocity matches KDS baseline."""
    kds_velocity = 42  # From KDS development-context.yaml
    
    cortex_velocity = api.get_current_velocity()
    
    assert abs(cortex_velocity - kds_velocity) < 5, \
        f"Velocity mismatch: KDS={kds_velocity}, CORTEX={cortex_velocity}"

def test_tier3_migration_hotspots():
    """Verify file hotspots preserved."""
    kds_hotspot = {
        'file': 'HostControlPanel.razor',
        'churn_rate': 0.28,
        'status': 'unstable'
    }
    
    cortex_hotspot = api.get_file_hotspot('HostControlPanel.razor')
    
    assert cortex_hotspot.churn_rate == kds_hotspot['churn_rate']
    assert cortex_hotspot.stability == 'UNSTABLE'

def test_tier3_query_performance():
    """Verify query performance targets met."""
    import time
    
    # Fast query: current velocity
    start = time.time()
    api.get_current_velocity()
    duration_ms = (time.time() - start) * 1000
    assert duration_ms < 10, f"Velocity query too slow: {duration_ms:.1f}ms"
    
    # Medium query: hotspots
    start = time.time()
    api.get_file_hotspots(limit=10)
    duration_ms = (time.time() - start) * 1000
    assert duration_ms < 50, f"Hotspot query too slow: {duration_ms:.1f}ms"
```

---

## 📈 Performance Optimizations

### 1. Indexed Queries

All frequently queried columns have indexes:
- `metric_date` columns (DESC for recent data)
- `file_path` for lookups
- `confidence`, `success_rate` for filtering
- Composite indexes for common query patterns

### 2. Materialized Views

Pre-computed aggregations:
- `git_velocity` - Weekly velocity from daily data
- `best_work_times` - Productivity by time slot
- Future: `file_stability_summary`, `test_health_summary`

### 3. Data Retention Policy

**30-Day Rolling Window:**
- Git metrics: Keep last 30 days (older data deleted)
- File hotspots: Recalculate every 30 days (old periods archived)
- Test metrics: Keep last 30 days
- Work patterns: Keep last 30 days

**Permanent Data:**
- Correlations (recalculated, not deleted)
- Insights (marked expired, not deleted for historical analysis)
- Collection logs (trimmed to last 100 entries)

**Cleanup Trigger:**

```sql
-- Auto-cleanup old git metrics (>30 days)
CREATE TRIGGER cleanup_old_git_metrics
AFTER INSERT ON context_git_metrics
BEGIN
    DELETE FROM context_git_metrics
    WHERE metric_date < date('now', '-30 days');
END;

-- Auto-cleanup old test metrics
CREATE TRIGGER cleanup_old_test_metrics
AFTER INSERT ON context_test_metrics
BEGIN
    DELETE FROM context_test_metrics
    WHERE metric_date < date('now', '-30 days');
END;
```

### 4. Delta Collection

Never re-process old data:
- Git: `git log --since=<last_collection>`
- Tests: Only new test runs since last check
- Build: Only new builds since last check

Result: <10 second collection vs 2-5 minute full scans.

---

## 🔗 Integration with Other Tiers

### Tier 0 (Governance)

**Tier 3 enforces:**
- Test-first success rate tracking (validates Rule #5)
- Commit size recommendations (data-driven best practice)
- Build quality gates (minimum 80% success rate)

**Governance reads Tier 3:**
- BrainProtector uses correlation data in challenges
- WorkPlanner uses velocity for estimates
- HealthValidator checks build/test metrics

### Tier 1 (Working Memory)

**Tier 3 provides context for conversations:**
- "You asked about velocity trends" → Query git_velocity
- "Hotspot file mentioned" → Warn about instability
- "Test creation request" → Suggest time slot

**Tier 1 feeds Tier 3:**
- Session duration → Work pattern analysis
- Session outcomes → Success rate tracking

### Tier 2 (Long-Term Knowledge)

**Tier 3 validates Tier 2 patterns:**
- Workflow success rates → Tier 2 confidence scores
- File relationships → Co-modification verification
- Architectural patterns → Stability evidence

**Tier 2 uses Tier 3 for recommendations:**
- "This workflow has 94% success" → Tier 3 data
- "These files often modified together" → Tier 3 correlations

---

## ✅ Testing Strategy

### Unit Tests (Fast, <1s total)

```python
def test_git_collector_delta_mode():
    """Verify delta collection only processes new commits."""
    collector = GitMetricsCollector()
    
    # First collection
    result1 = collector.collect(since=datetime(2025, 11, 1))
    assert result1.commits_processed == 50
    
    # Delta collection (only new)
    result2 = collector.collect(since=datetime(2025, 11, 5))
    assert result2.commits_processed == 10  # Only last 2 days

def test_file_hotspot_stability_classification():
    """Verify stability thresholds applied correctly."""
    # STABLE: <10%
    assert classify_stability(churn_rate=0.05) == 'STABLE'
    
    # MODERATE: 10-20%
    assert classify_stability(churn_rate=0.15) == 'MODERATE'
    
    # UNSTABLE: >20%
    assert classify_stability(churn_rate=0.28) == 'UNSTABLE'

def test_insight_generator_velocity_drop():
    """Verify velocity drop insight triggered correctly."""
    generator = InsightGenerator()
    
    # Simulate baseline and current data
    db.insert_test_data('context_git_metrics', baseline=42, current=13)
    
    insights = generator._check_velocity_drop()
    
    assert len(insights) == 1
    assert insights[0].insight_type == 'velocity_drop'
    assert insights[0].severity == 'ERROR'  # >50% drop
```

### Integration Tests (Medium, <10s total)

```python
def test_full_collection_cycle():
    """Test complete collection orchestration."""
    orchestrator = CollectorOrchestrator()
    
    # Should collect on first run
    assert orchestrator.should_collect() == True
    
    result = orchestrator.collect_all()
    assert result.success == True
    assert len(result.results) == 5  # All collectors ran
    
    # Should NOT collect immediately after
    assert orchestrator.should_collect() == False
    
    # Should collect after 1 hour
    db.update_last_collection(time=datetime.now() - timedelta(hours=2))
    assert orchestrator.should_collect() == True

def test_query_performance_targets():
    """Verify all queries meet performance targets."""
    # Populate test data (1000 records)
    db.populate_test_data(records=1000)
    
    # Fast queries: <10ms
    assert time_query(api.get_current_velocity) < 0.010
    assert time_query(api.get_file_stability, 'file.razor') < 0.010
    assert time_query(api.get_best_work_time) < 0.010
    
    # Medium queries: <50ms
    assert time_query(api.get_velocity_trend, days=30) < 0.050
    assert time_query(api.get_file_hotspots, limit=10) < 0.050
    
    # Complex queries: <100ms
    assert time_query(api.calculate_correlation, 'commit_size_vs_success') < 0.100
```

### Regression Tests (Comprehensive, <30s total)

```python
def test_kds_parity_velocity():
    """Verify CORTEX velocity matches KDS baseline."""
    kds_velocity = load_kds_baseline('git_velocity')
    cortex_velocity = api.get_current_velocity()
    
    # Allow 5% variance (different calculation methods)
    assert abs(cortex_velocity - kds_velocity) / kds_velocity < 0.05

def test_kds_parity_hotspots():
    """Verify all KDS hotspots detected in CORTEX."""
    kds_hotspots = load_kds_baseline('file_hotspots')
    cortex_hotspots = api.get_file_hotspots(limit=100)
    
    for kds_hotspot in kds_hotspots:
        cortex_match = next(
            (h for h in cortex_hotspots if h.file_path == kds_hotspot['file']),
            None
        )
        assert cortex_match is not None, f"Hotspot missing: {kds_hotspot['file']}"
        assert abs(cortex_match.churn_rate - kds_hotspot['churn_rate']) < 0.05

def test_kds_parity_insights():
    """Verify CORTEX generates same insights as KDS."""
    kds_insights = load_kds_baseline('proactive_warnings')
    cortex_insights = api.get_insights(acknowledged=False)
    
    # Match insights by type and entity
    for kds_insight in kds_insights:
        cortex_match = next(
            (i for i in cortex_insights 
             if i.insight_type == kds_insight['type'] 
             and i.related_entity == kds_insight.get('data', {}).get('file')),
            None
        )
        assert cortex_match is not None, f"Insight missing: {kds_insight['type']}"
```

---

## 🎯 Success Criteria

**Tier 3 is complete when:**

✅ **Schema Complete:**
- All 11 tables created with indexes
- Triggers for auto-classification and cleanup
- Materialized views for fast queries

✅ **Collection Working:**
- Delta collection implemented and tested
- 1-hour throttling working correctly
- All 5 collectors operational
- Collection logs all executions

✅ **Queries Performant:**
- Fast queries (<10ms): Current velocity, file stability, best time
- Medium queries (<50ms): Velocity trend, hotspots, flaky tests
- Complex queries (<100ms): Correlations, forecasts

✅ **Insights Generated:**
- Velocity drop detection working
- File hotspot warnings accurate
- Flaky test alerts triggered correctly
- Build health monitoring active

✅ **Migration Validated:**
- All KDS v8 metrics migrated
- Velocity matches KDS baseline (±5%)
- Hotspots preserved accurately
- Correlations match expected values

✅ **Tests Passing:**
- Unit tests: 100% pass, <1s total
- Integration tests: 100% pass, <10s total
- Regression tests: 100% pass, <30s total
- Performance tests: All targets met

✅ **Documentation Complete:**
- Schema documented with examples
- Collection strategy explained
- Query patterns documented
- Integration points defined

---

## 📚 Related Documentation

- [Tier 0: Governance Design](tier0-governance.md)
- [Tier 1: Working Memory Design](tier1-stm-design.md)
- [Tier 2: Long-Term Knowledge Design](tier2-ltm-design.md)
- [Feature Inventory: Tier 3](../feature-inventory/tier3-context-intelligence.md)
- [Unified Database Schema](unified-database-schema.sql)
- [Storage Analysis](STORAGE-DESIGN-ANALYSIS.md)

---

**Status:** ✅ Tier 3 Development Context Design Complete  
**Next:** Create Agent Contracts design  
**Version:** 1.0 (Initial design)

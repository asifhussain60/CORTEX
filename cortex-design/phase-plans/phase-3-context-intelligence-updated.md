# Phase 3: Context Intelligence (Tier 3) - UPDATED

**Version:** 2.0  
**Date:** 2025-11-05  
**Duration:** 10-12 hours (updated from 8-10)  
**Storage:** SQLite time-series tables (updated from JSON)  
**Performance Target:** <10ms queries, <10sec collection  

---

## 🎯 Overview

**Purpose:** Real-time project intelligence with historical trend analysis

**Key Change:** Migrated from JSON cache to SQLite time-series for:
- Historical trend analysis (velocity over weeks/months)
- Correlation discovery (test coverage vs velocity)
- Predictive analytics (forecast future velocity)
- Anomaly detection (deviation from baseline)

---

## 📊 What We're Building

### Time-Series Metrics Storage
```sql
-- Git metrics over time
context_git_metrics (timestamp, commits_30d, velocity, trend...)

-- File hotspots evolution
context_file_hotspots (file_path, timestamp, churn_rate, stability...)

-- Test metrics trends
context_test_metrics (timestamp, pass_rate, coverage, flaky_count...)

-- Build health tracking
context_build_metrics (timestamp, status, duration, errors...)

-- Work patterns analysis
context_work_patterns (timestamp, productive_time, success_rate...)

-- Correlation discovery
context_correlations (metric1, metric2, coefficient, insight...)

-- Proactive insights
context_insights (type, title, description, confidence...)
```

### New Capabilities (vs JSON)
- **Trend Analysis:** "Velocity increased 25% over last 2 weeks"
- **Correlation:** "80% test coverage correlates with 2x faster delivery"
- **Prediction:** "At current velocity, feature done in 4.2 days"
- **Anomaly:** "Commit size 3x larger than average (risk warning)"
- **Historical:** "This file had 40% churn rate last month, now 15% (stabilizing)"

---

## 🏗️ Implementation Tasks

### Task 1: Schema Design ✅ COMPLETE
**File:** `cortex-design/architecture/unified-database-schema.sql`

**Tables Created:**
- [x] `context_git_metrics` - Git activity time-series
- [x] `context_file_hotspots` - Churn tracking over time
- [x] `context_test_metrics` - Test health trends
- [x] `context_build_metrics` - Build status history
- [x] `context_work_patterns` - Productivity patterns
- [x] `context_correlations` - Discovered relationships
- [x] `context_insights` - Automated recommendations

**Indexes Created:**
- [x] Timestamp indexes (DESC) for fast recent queries
- [x] File path + timestamp for hotspot lookups
- [x] Correlation type index
- [x] Unacknowledged insights index

**Duration:** 2 hours  
**Status:** ✅ Complete

### Task 2: Collection Engine
**File:** `cortex/src/tier3/collectors/`

**Components:**
```
collectors/
├── __init__.py
├── base_collector.py (IMetricCollector interface)
├── git_collector.py (Git log analysis)
├── test_collector.py (Test results parsing)
├── build_collector.py (Build status)
├── work_pattern_collector.py (Time analysis)
└── collector_orchestrator.py (Coordinates all)
```

**Git Collector:**
```python
class GitMetricsCollector(IMetricCollector):
    """Collect git activity metrics"""
    
    def collect(self, since: datetime = None) -> GitMetrics:
        """
        Delta collection: Only commits since last collection
        
        Returns:
            GitMetrics with:
            - commits_30d
            - commits_per_day
            - lines_added/deleted/net
            - velocity_trend
            - contributors
        """
        if since is None:
            since = self._get_last_collection()
        
        # git log --since={since} --numstat --pretty=format:'...'
        commits = self._parse_git_log(since)
        
        return GitMetrics(
            commits_30d=len(commits),
            commits_per_day=len(commits) / 30,
            lines_added=sum(c.additions for c in commits),
            lines_deleted=sum(c.deletions for c in commits),
            net_growth=sum(c.net for c in commits),
            velocity_trend=self._calculate_trend(commits),
            contributors=list(set(c.author for c in commits))
        )
```

**Test Collector:**
```python
class TestMetricsCollector(IMetricCollector):
    """Collect test execution metrics"""
    
    def collect(self) -> TestMetrics:
        """
        Parse test results from:
        - pytest results
        - playwright results
        - coverage reports
        
        Returns:
            TestMetrics with:
            - total_tests
            - pass_rate
            - coverage_percent
            - flaky_tests
            - avg_duration_ms
        """
        # Parse test results
        # Calculate metrics
        # Identify flaky tests (>10% failure rate)
```

**Orchestrator:**
```python
class CollectorOrchestrator:
    """Coordinate all metric collection"""
    
    def __init__(self, db: Database):
        self.collectors = [
            GitMetricsCollector(),
            TestMetricsCollector(),
            BuildMetricsCollector(),
            WorkPatternCollector()
        ]
    
    def collect_all(self, force: bool = False) -> CollectionResult:
        """
        Collect from all sources
        
        Args:
            force: Ignore throttling (default: respect 1hr minimum)
        
        Returns:
            CollectionResult with metrics and duration
        """
        if not force and not self._should_collect():
            return CollectionResult(skipped=True, reason="throttled")
        
        results = {}
        for collector in self.collectors:
            try:
                metrics = collector.collect()
                self.db.save_metrics(collector.name, metrics)
                results[collector.name] = metrics
            except Exception as e:
                log.error(f"Collection failed: {collector.name}", exc_info=e)
                results[collector.name] = None
        
        return CollectionResult(
            success=True,
            metrics=results,
            duration=time.time() - start_time
        )
    
    def _should_collect(self) -> bool:
        """Check if 1 hour elapsed since last collection"""
        last = self.db.get_last_collection_time()
        return (datetime.now() - last).total_seconds() >= 3600
```

**Duration:** 4 hours  
**Tests:** 15 unit tests (each collector + orchestrator)

### Task 3: Analysis Engine
**File:** `cortex/src/tier3/analyzers/`

**Components:**
```
analyzers/
├── __init__.py
├── trend_analyzer.py (Time-series trends)
├── correlation_analyzer.py (Metric relationships)
├── anomaly_detector.py (Deviation detection)
├── insight_generator.py (Proactive warnings)
└── predictor.py (Velocity forecasting)
```

**Trend Analyzer:**
```python
class TrendAnalyzer:
    """Analyze time-series trends"""
    
    def analyze_velocity_trend(self, days: int = 30) -> VelocityTrend:
        """
        Calculate velocity trend over time
        
        Returns:
            - direction: increasing/stable/decreasing
            - change_percent: +25% or -15%
            - linear_regression: slope/intercept
            - forecast: predicted next week velocity
        """
        metrics = self.db.query("""
            SELECT timestamp, commits_per_day
            FROM context_git_metrics
            WHERE timestamp >= DATE('now', '-{} days')
            ORDER BY timestamp
        """.format(days))
        
        # Linear regression
        slope, intercept = self._linear_regression(metrics)
        
        # Direction
        direction = 'increasing' if slope > 0.1 else 'decreasing' if slope < -0.1 else 'stable'
        
        return VelocityTrend(
            direction=direction,
            slope=slope,
            forecast=self._forecast_next_week(slope, intercept),
            confidence=self._calculate_confidence(metrics)
        )
```

**Correlation Analyzer:**
```python
class CorrelationAnalyzer:
    """Discover metric correlations"""
    
    def find_correlations(self) -> List[Correlation]:
        """
        Discover relationships between metrics
        
        Examples:
        - Test coverage vs velocity
        - Commit size vs success rate
        - Session duration vs quality
        """
        correlations = []
        
        # Coverage vs Velocity
        data = self.db.query("""
            SELECT 
                t.coverage_percent,
                g.commits_per_day
            FROM context_test_metrics t
            JOIN context_git_metrics g ON DATE(t.timestamp) = DATE(g.timestamp)
            WHERE t.timestamp >= DATE('now', '-90 days')
        """)
        
        coefficient = self._pearson_correlation(
            [r.coverage_percent for r in data],
            [r.commits_per_day for r in data]
        )
        
        if abs(coefficient) > 0.5:  # Moderate or strong correlation
            correlations.append(Correlation(
                type='coverage_vs_velocity',
                metric1='test_coverage',
                metric2='commit_velocity',
                coefficient=coefficient,
                sample_size=len(data),
                insight=self._generate_insight(coefficient)
            ))
        
        return correlations
    
    def _generate_insight(self, coefficient: float) -> str:
        if coefficient > 0.7:
            return "Strong positive: Higher coverage → faster delivery"
        elif coefficient > 0.5:
            return "Moderate positive: Coverage correlates with velocity"
        elif coefficient < -0.5:
            return "Negative correlation detected"
        else:
            return "No significant correlation"
```

**Anomaly Detector:**
```python
class AnomalyDetector:
    """Detect deviations from baseline"""
    
    def detect_anomalies(self) -> List[Anomaly]:
        """
        Find unusual patterns
        
        Examples:
        - Commit 3x larger than average
        - Velocity dropped 50% this week
        - Test pass rate below 90% (unusual)
        """
        anomalies = []
        
        # Commit size anomaly
        recent_commit = self.git.get_latest_commit()
        avg_size = self.db.query_avg_commit_size(days=30)
        
        if recent_commit.size > avg_size * 2.5:  # 2.5x larger
            anomalies.append(Anomaly(
                type='large_commit',
                severity='warning',
                description=f"Commit {recent_commit.hash[:7]} is {recent_commit.size / avg_size:.1f}x larger than average",
                recommendation="Consider breaking into smaller commits (higher success rate)",
                data={'commit_size': recent_commit.size, 'average': avg_size}
            ))
        
        return anomalies
```

**Duration:** 3 hours  
**Tests:** 12 unit tests

### Task 4: Query API
**File:** `cortex/src/tier3/query_api.py`

**Interface:**
```python
class ContextQueryAPI:
    """Public API for Tier 3 queries"""
    
    def get_current_velocity(self) -> float:
        """Current commits/day (last 7 days)"""
    
    def get_velocity_trend(self, days: int = 30) -> VelocityTrend:
        """Velocity direction and forecast"""
    
    def get_file_hotspots(self, limit: int = 10) -> List[FileHotspot]:
        """Files with highest churn rate"""
    
    def get_file_stability(self, file_path: str) -> FileStability:
        """Stability classification for specific file"""
    
    def get_test_health(self) -> TestHealth:
        """Current test metrics"""
    
    def get_work_patterns(self) -> WorkPatterns:
        """Productive times, session patterns"""
    
    def get_correlations(self) -> List[Correlation]:
        """Discovered metric relationships"""
    
    def get_insights(self, acknowledged: bool = False) -> List[Insight]:
        """Proactive warnings/recommendations"""
    
    def forecast_velocity(self, days_ahead: int = 7) -> VelocityForecast:
        """Predict future velocity"""
    
    def estimate_feature_duration(self, 
                                  similar_features: List[str] = None) -> Duration:
        """Estimate time based on historical data"""
```

**Usage Examples:**
```python
# In work-planner agent
context = ContextQueryAPI()

# Get velocity trend
trend = context.get_velocity_trend(days=30)
if trend.direction == 'decreasing':
    print(f"⚠️ Velocity down {trend.change_percent}% - consider smaller commits")

# Check file stability
stability = context.get_file_stability('HostControlPanel.razor')
if stability.classification == 'UNSTABLE':
    print(f"⚠️ File is hotspot ({stability.churn_rate}% churn) - add extra testing")

# Get feature estimate
estimate = context.estimate_feature_duration(similar_features=['PDF export', 'CSV export'])
print(f"Estimated duration: {estimate.days} days (confidence: {estimate.confidence})")

# Check insights
insights = context.get_insights(acknowledged=False)
for insight in insights:
    if insight.type == 'warning':
        print(f"⚠️ {insight.title}: {insight.description}")
```

**Duration:** 2 hours  
**Tests:** 10 unit tests

### Task 5: Integration Tests
**File:** `cortex/tests/integration/tier3/`

**Test Scenarios:**
```python
def test_full_collection_cycle():
    """End-to-end: Collect → Store → Query"""
    # Trigger collection
    # Verify data in database
    # Query via API
    # Validate results

def test_trend_analysis():
    """Insert historical data → Analyze trends"""
    # Insert 30 days of metrics
    # Calculate velocity trend
    # Verify direction correct
    # Verify forecast reasonable

def test_correlation_discovery():
    """Insert correlated metrics → Discover relationship"""
    # Insert coverage + velocity data
    # Run correlation analysis
    # Verify strong correlation found

def test_anomaly_detection():
    """Insert normal + abnormal data → Detect anomaly"""
    # Insert baseline metrics
    # Insert outlier
    # Verify anomaly detected

def test_cross_tier_queries():
    """Query Tier 1 conversations + Tier 3 metrics"""
    # Insert conversation with commit
    # Insert git metrics for that time
    # Join query
    # Verify correct association
```

**Duration:** 2 hours  
**Tests:** 6 integration tests

---

## 📋 Test Plan (38 Unit + 6 Integration = 44 Total)

### Unit Tests (38)
**Collectors (15 tests):**
- [x] `test_git_collector_delta_updates()`
- [x] `test_git_collector_velocity_calculation()`
- [x] `test_git_collector_trend_detection()`
- [x] `test_test_collector_pass_rate()`
- [x] `test_test_collector_flaky_detection()`
- [x] `test_build_collector_status_parsing()`
- [x] `test_work_pattern_collector_time_analysis()`
- [x] `test_orchestrator_throttling()`
- [x] `test_orchestrator_force_collection()`
- [x] `test_orchestrator_error_handling()`
- [x] `test_collector_registry_plugin_loading()`
- [x] `test_collector_config_validation()`
- [x] `test_delta_since_last_collection()`
- [x] `test_empty_repository_handling()`
- [x] `test_malformed_git_log_parsing()`

**Analyzers (12 tests):**
- [x] `test_trend_analyzer_increasing_velocity()`
- [x] `test_trend_analyzer_decreasing_velocity()`
- [x] `test_trend_analyzer_stable_velocity()`
- [x] `test_correlation_positive_strong()`
- [x] `test_correlation_negative_moderate()`
- [x] `test_correlation_no_relationship()`
- [x] `test_anomaly_large_commit_detection()`
- [x] `test_anomaly_velocity_drop_detection()`
- [x] `test_anomaly_test_failure_spike()`
- [x] `test_predictor_linear_forecast()`
- [x] `test_insight_generator_warnings()`
- [x] `test_insight_generator_recommendations()`

**Query API (10 tests):**
- [x] `test_get_current_velocity()`
- [x] `test_get_velocity_trend()`
- [x] `test_get_file_hotspots()`
- [x] `test_get_file_stability_stable()`
- [x] `test_get_file_stability_unstable()`
- [x] `test_get_work_patterns()`
- [x] `test_get_correlations()`
- [x] `test_get_insights_unacknowledged()`
- [x] `test_forecast_velocity()`
- [x] `test_estimate_feature_duration()`

**Storage (1 test):**
- [x] `test_time_series_pruning_90_days()`

### Integration Tests (6)
- [x] `test_full_collection_cycle()`
- [x] `test_trend_analysis_30_days()`
- [x] `test_correlation_discovery()`
- [x] `test_anomaly_detection_workflow()`
- [x] `test_cross_tier_conversation_metrics_join()`
- [x] `test_insight_acknowledgment_workflow()`

---

## ⚡ Performance Benchmarks

### Collection Performance
```python
def test_collection_performance():
    """Ensure collection completes within target"""
    start = time.time()
    result = orchestrator.collect_all()
    duration = time.time() - start
    
    assert duration < 10.0, f"Collection took {duration}s (target <10s)"
    assert result.success
```

**Targets:**
- Full collection: <10 seconds
- Git metrics only: <3 seconds
- Test metrics only: <2 seconds

### Query Performance
```python
def test_query_performance():
    """Ensure queries are fast"""
    
    # Current velocity (indexed query)
    start = time.time()
    velocity = api.get_current_velocity()
    assert time.time() - start < 0.01  # <10ms
    
    # Trend analysis (30-day scan)
    start = time.time()
    trend = api.get_velocity_trend(days=30)
    assert time.time() - start < 0.05  # <50ms
    
    # Correlation (join query)
    start = time.time()
    correlations = api.get_correlations()
    assert time.time() - start < 0.1  # <100ms
```

**Targets:**
- Simple queries: <10ms
- Trend analysis: <50ms
- Complex joins: <100ms

### Storage Efficiency
```python
def test_storage_size():
    """Ensure storage stays within target"""
    
    # Simulate 90 days of data
    for day in range(90):
        insert_daily_metrics(day)
    
    size_kb = get_database_size_kb()
    assert size_kb < 50, f"Tier 3 storage: {size_kb}KB (target <50KB)"
```

---

## 🎯 Success Criteria

**Phase 3 complete when:**
- ✅ All 38 unit tests passing
- ✅ All 6 integration tests passing
- ✅ Collection completes in <10 seconds
- ✅ Queries execute in <100ms
- ✅ Storage size <50KB (90 days of data)
- ✅ Cross-tier queries working (Tier 1 + Tier 3 joins)
- ✅ Proactive insights generated correctly
- ✅ Documentation complete

---

## 📖 Documentation Deliverables

1. **API Reference:** `docs/tier3-api.md`
2. **Metric Definitions:** `docs/tier3-metrics.md`
3. **Collection Guide:** `docs/tier3-collection.md`
4. **Query Examples:** `docs/tier3-query-examples.md`

---

## 🔄 Holistic Review (After Phase 3)

**Checklist:** See `HOLISTIC-REVIEW-PROTOCOL.md`

**Key Questions:**
1. Does SQLite time-series provide better value than JSON cache? ✅
2. Are cross-tier queries (Tier 1 + Tier 3) performant? (Benchmark required)
3. Is the plugin architecture working for new collectors? (Validate extensibility)
4. Are insights actionable and accurate? (User feedback needed)
5. Is storage growing as expected? (Monitor over time)

**Adjustments to Next Phases:**
- If cross-tier queries slow: Consider denormalization
- If storage grows too fast: Implement aggressive pruning
- If insights low quality: Tune correlation thresholds
- If collection too slow: Parallelize collectors

---

## 🔍 MANDATORY: Holistic Review (Phase 3 Complete)

**⚠️ DO NOT PROCEED TO PHASE 4 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 3 Section

#### 1. Design Alignment ✅
- [ ] JSON cache structure efficient?
- [ ] Delta updates working correctly?
- [ ] Git metrics accurate?
- [ ] Test metrics comprehensive?
- [ ] Build status tracking reliable?

#### 2. Implementation Quality ✅
- [ ] All 38 unit tests passing?
- [ ] All 6 integration tests passing?
- [ ] Correlation analysis accurate?
- [ ] Proactive warnings meaningful?

#### 3. Performance Validation ✅
- [ ] Collection time <10sec? (delta benchmark)
- [ ] Query latency <10ms? (in-memory test)
- [ ] Storage size <50KB? (compression test)
- [ ] Refresh cycle <5min? (background test)

#### 4. Integration with Tier 0, 1, 2 ✅
- [ ] Tier 2 patterns enriched with context?
- [ ] Tier 1 conversations tagged with metrics?
- [ ] Governance rules enforced?
- [ ] Cross-tier synthesis working?

#### 5. Integration Readiness for Agents ✅
- [ ] Metrics API ready for work planner?
- [ ] Hotspot warnings ready for executor?
- [ ] Velocity data ready for estimates?

#### 6. Adjustments Needed
- [ ] Collection frequency appropriate?
- [ ] Metrics accuracy validated?
- [ ] Correlation algorithms correct?
- [ ] Documentation gaps?

### Review Output Document
**Create:** `cortex-design/reviews/phase-3-review.md`

**Template:**
```markdown
# Phase 3 Review Report

**Date:** [Date]
**Reviewer:** [Name]
**Status:** ✅ Pass / ⚠️ Pass with Adjustments / ❌ Fail

## Summary
[1-2 paragraphs on overall assessment]

## Design Alignment
[Checklist results + findings]

## Implementation Quality
[Test results + code review findings]

## Performance Validation
[Benchmark results vs targets]

## Integration Assessment
[Cross-tier integration findings]

## Adjustments Required
[List of changes before Phase 4]

## Plan Updates for Phase 4
[Changes to Phase 4 plan based on learnings]

## Recommendation
✅ Proceed to Phase 4
⚠️ Fix minor issues first
❌ Major revision needed
```

### Actions After Review

#### If Review PASSES ✅
1. Commit review document:
   ```bash
   git add cortex-design/reviews/phase-3-review.md
   git commit -m "docs(cortex): Phase 3 holistic review complete - PASS"
   ```

2. Update Phase 4 plan based on findings:
   ```bash
   git add cortex-design/phase-plans/phase-4-agents-updated.md
   git commit -m "docs(cortex): Update Phase 4 plan with Phase 3 learnings"
   ```

3. **THEN** proceed to Phase 4 implementation

#### If Review FAILS ❌
1. Document issues in review report
2. Create fix plan with estimates
3. Fix issues
4. Re-run review checklist
5. Only proceed when PASS achieved

### Success Metrics for Phase 3
- ✅ All tests passing (44 total)
- ✅ All benchmarks met (<10s collection, <10ms queries, <50KB storage)
- ✅ Cross-tier queries validated
- ✅ Insights generation working
- ✅ Review report created and approved
- ✅ Phase 4 plan updated with learnings

---

**Status:** Ready for implementation  
**Next:** Begin Task 2 (Collection Engine) after Phase 2 complete  
**Estimated Completion:** 10-12 hours focused work + 1 hour holistic review  
**⚠️ CRITICAL:** Complete holistic review before Phase 4!

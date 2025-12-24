# CORTEX Healthcheck Enhancement Plan

**Purpose:** Comprehensive system health diagnostics with brain, knowledge graph, and feature usage analytics  
**Version:** 2.0  
**Status:** PLANNED  
**Author:** Asif Hussain  
**Date:** November 26, 2025

---

## 🎯 Current State Analysis

### Existing Healthcheck Operation

**Location:** `src/operations/healthcheck_operation.py`

**Current Capabilities:**
- ✅ System resource monitoring (CPU, memory, disk)
- ✅ Database integrity checks (Tier 1, Tier 2)
- ✅ Brain directory validation
- ✅ Performance metrics (YAML cache stats)
- ✅ Health scoring (0-100)

**Missing Capabilities:**
- ❌ Knowledge graph analytics (pattern counts, confidence distribution)
- ❌ Feature usage tracking (which CORTEX features used vs unused)
- ❌ Brain tier statistics (conversation counts, entity extraction)
- ❌ Entry point module effectiveness (which commands used most)
- ❌ Agent performance metrics (execution times, success rates)
- ❌ Workflow health (TDD, Planning, Feedback completion rates)

---

## 📊 Enhancement Goals

### 1. Brain Health Analytics

**Tier 1 (Working Memory):**
- Conversation count and retention rate
- Active vs archived conversations
- Token usage trends
- Entity extraction statistics
- Context quality scores

**Tier 2 (Knowledge Graph):**
- Total patterns stored
- Confidence score distribution
- Pattern decay detection
- Duplicate pattern identification
- Cross-reference integrity

**Tier 3 (Development Context):**
- Code metrics (hotspots, churn rate)
- Git activity analysis
- Project insights
- Developer patterns

### 2. Feature Usage Analytics

**Entry Point Modules:**
- Command invocation frequency
- Success/failure rates per command
- Average execution time per operation
- Most/least used features
- Orphaned features (wired but never used)

**Workflow Tracking:**
- TDD workflow completion rate
- Planning sessions (active, approved, abandoned)
- Feedback reports generated
- Upgrade success rate
- View discovery utilization

**Agent Performance:**
- Strategic agents (Intent Router, Work Planner, Health Validator)
- Tactical agents (Executor, Tester, Documenter)
- Execution time distribution
- Success rate by agent type

### 3. System Performance Metrics

**Optimization Impact:**
- Space saved by cleanup operations
- Cache hit rates (YAML, validation, alignment)
- Database vacuum effectiveness
- Query performance (p50, p95, p99)

**Governance Compliance:**
- Brain protection rule violations
- Document organization compliance
- Test isolation adherence
- SKULL rule enforcement rates

---

## 🏗️ Implementation Plan

### Phase 1: Brain Analytics Module (3-4 hours)

**Tasks:**
1. Create `BrainAnalyticsCollector` class
   - Query Tier 1 for conversation stats
   - Query Tier 2 for pattern analytics
   - Query Tier 3 for dev context metrics
   
2. Implement metrics collection methods:
   ```python
   def get_tier1_stats() -> Dict[str, Any]
   def get_tier2_stats() -> Dict[str, Any]
   def get_tier3_stats() -> Dict[str, Any]
   def get_brain_health_score() -> float
   ```

3. Add brain health section to healthcheck report

**Output Example:**
```markdown
## 🧠 Brain Health

### Tier 1: Working Memory
- Total conversations: 1,247
- Active sessions: 15
- Token budget usage: 67% (2.1M / 3M)
- Context quality: 8.7/10
- Retention rate: 94%

### Tier 2: Knowledge Graph
- Total patterns: 3,458
- High confidence (>0.80): 2,341 (68%)
- Medium confidence (0.50-0.80): 892 (26%)
- Low confidence (<0.50): 225 (6%)
- Duplicate patterns: 12 identified
- Pattern decay: 3% (last 30 days)

### Tier 3: Development Context
- Code hotspots: 87 files
- Churn rate: 12%
- Git activity: 156 commits (last 7 days)
- Project insights: 42 patterns learned
```

### Phase 2: Feature Usage Tracking (2-3 hours)

**Tasks:**
1. Create `FeatureUsageTracker` class
   - Track command invocations
   - Record execution times
   - Store success/failure results

2. Integrate with existing operations:
   - Add tracking to BaseOperationModule
   - Store metrics in Tier 3 database
   - Add usage table schema

3. Implement usage analytics:
   ```python
   def get_command_usage_stats() -> Dict[str, Any]
   def get_workflow_completion_rates() -> Dict[str, float]
   def identify_orphaned_features() -> List[str]
   ```

**Output Example:**
```markdown
## 📈 Feature Usage Analytics

### Top 5 Commands (Last 30 Days)
1. healthcheck (247 uses, 98% success)
2. optimize (189 uses, 100% success)
3. plan feature (156 uses, 94% success)
4. discover views (134 uses, 97% success)
5. feedback (89 uses, 100% success)

### Workflow Completion Rates
- TDD: 87% (RED→GREEN→REFACTOR)
- Planning: 78% (DoR→Approval→Implementation)
- Feedback: 94% (Report→Upload→Acknowledgment)

### Unused Features (Potential Deprecation)
- Feature X: 0 uses in 90 days
- Feature Y: 2 uses in 90 days (last use: 67 days ago)
```

### Phase 3: Performance Metrics Dashboard (2 hours)

**Tasks:**
1. Create `PerformanceMetricsDashboard` class
   - Cache effectiveness metrics
   - Database query performance
   - Optimization impact tracking

2. Add performance visualization:
   ```python
   def get_cache_effectiveness() -> Dict[str, Any]
   def get_query_performance() -> Dict[str, Any]
   def get_optimization_impact() -> Dict[str, Any]
   ```

**Output Example:**
```markdown
## ⚡ Performance Metrics

### Cache Effectiveness
- Overall hit rate: 76% (saved ~8.3s per healthcheck)
- YAML cache: 85% hit rate (12 entries)
- Validation cache: 68% hit rate (optimize: 100%, align: 45%)
- Governance cache: 82% hit rate (5 entries)

### Query Performance (p50/p95/p99)
- Tier 1 queries: 12ms / 45ms / 89ms
- Tier 2 queries: 23ms / 78ms / 156ms
- FTS5 searches: 34ms / 112ms / 234ms

### Optimization Impact (Last 30 Days)
- Space reclaimed: 1.2 GB
- Cleanup runs: 12
- Average time saved: 18s per run
```

### Phase 4: Integration & Testing (2 hours)

**Tasks:**
1. Integrate all modules into `HealthCheckOperation.execute()`
2. Add detailed/summary report modes
3. Create comprehensive test suite
4. Update documentation and examples

---

## 🎯 Enhanced Healthcheck Output Structure

### Summary Mode (Default)
```markdown
# CORTEX Health Check Report

**Status:** ✅ HEALTHY (Score: 92/100)
**Generated:** 2025-11-26 14:30:15

## Quick Overview
- Brain: ✅ Healthy (3.4k patterns, 94% retention)
- Performance: ✅ Excellent (76% cache hit rate)
- Features: ⚠️ 2 unused features detected
- System: ✅ Healthy (45% CPU, 67% RAM, 58% disk)

[Run 'healthcheck --detailed' for complete diagnostics]
```

### Detailed Mode
```markdown
# CORTEX Comprehensive Health Check

[Full report with all sections:]
1. System Resources
2. Brain Health (Tier 1, 2, 3)
3. Feature Usage Analytics
4. Performance Metrics
5. Governance Compliance
6. Recommendations
7. Next Actions
```

---

## 🔗 Integration with Optimize & Align

### Question: Should optimize/align run healthcheck first?

**Analysis:**

**Optimize Operation:**
- **Current behavior:** Runs governance drift check, EPMO health check (cached)
- **Recommendation:** ⚠️ **NO** - Don't add full healthcheck
  - Reason: Optimize already does targeted health checks
  - Impact: Would add 2-3s overhead for full healthcheck
  - Alternative: Use cached results from recent healthcheck if available

**Align Operation:**
- **Current behavior:** Validates integration depth, deployment readiness
- **Recommendation:** ✅ **YES** - Run lightweight healthcheck first
  - Reason: Alignment should validate brain integrity before analyzing features
  - Impact: Minimal (0.5-1s with caching)
  - Implementation: Check brain database accessibility, verify tier boundaries

**Proposed Integration:**

```python
# In OptimizeSystemOrchestrator.execute()
def execute(self, context: Dict[str, Any]) -> OperationResult:
    # Use cached healthcheck results if recent (<5 min)
    cache = get_cache()
    health_status = cache.get('healthcheck', 'status')
    
    if health_status and health_status['timestamp'] > 5_minutes_ago:
        logger.info(f"✅ Using cached health status (score: {health_status['score']})")
    else:
        # Run quick health check (system + brain only, skip features)
        health_check = HealthCheckOperation()
        result = health_check.execute({'component': 'brain', 'quick': True})
        
        if not result.success:
            logger.warning(f"⚠️ Health check warning: {result.message}")
    
    # Continue with optimize phases...

# In SystemAlignmentOrchestrator.execute()
def execute(self, context: Dict[str, Any]) -> OperationResult:
    # Always run lightweight brain validation
    brain_check = self._validate_brain_accessibility()
    
    if not brain_check['healthy']:
        return OperationResult(
            success=False,
            message=f"Brain validation failed: {brain_check['issues']}"
        )
    
    # Continue with alignment validation...
```

**Benefits:**
- ✅ Prevents operations on unhealthy systems
- ✅ Uses caching to minimize overhead
- ✅ Provides early warning of brain issues
- ✅ Lightweight checks (no full feature analysis)

**Trade-offs:**
- ⚠️ Adds 0.5-1s to optimize/align when cache cold
- ⚠️ Increases complexity slightly
- ✅ But prevents cascading failures from corrupted brain state

---

## 📝 API Changes

### New HealthCheckOperation Methods

```python
class HealthCheckOperation(BaseOperationModule):
    def execute(self, **kwargs) -> OperationResult:
        """
        Args:
            detailed: Include detailed diagnostics (default: False)
            component: Specific component ('system', 'brain', 'features', 'all')
            quick: Skip expensive operations (default: False)
        """
    
    # NEW METHODS
    def _check_brain_analytics(self) -> Dict[str, Any]:
        """Comprehensive brain health analytics."""
    
    def _check_feature_usage(self) -> Dict[str, Any]:
        """Feature usage tracking and analytics."""
    
    def _check_workflow_health(self) -> Dict[str, Any]:
        """Workflow completion rates and effectiveness."""
    
    def _check_agent_performance(self) -> Dict[str, Any]:
        """Agent execution metrics and success rates."""
    
    def _get_recommendations(self, health_data: Dict) -> List[str]:
        """Generate actionable recommendations."""
```

### New Database Schema (Tier 3)

```sql
-- Feature usage tracking
CREATE TABLE IF NOT EXISTS feature_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT NOT NULL,
    invocation_timestamp REAL NOT NULL,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT,
    context TEXT  -- JSON blob
);

CREATE INDEX idx_feature_usage_name ON feature_usage(feature_name);
CREATE INDEX idx_feature_usage_timestamp ON feature_usage(invocation_timestamp);

-- Workflow tracking
CREATE TABLE IF NOT EXISTS workflow_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_type TEXT NOT NULL,  -- 'tdd', 'planning', 'feedback'
    session_id TEXT UNIQUE NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL,
    completed BOOLEAN,
    phases_completed TEXT,  -- JSON array
    final_status TEXT
);
```

---

## 🎯 Success Criteria

### Healthcheck Enhancement Complete When:

1. ✅ Brain analytics module implemented and tested
2. ✅ Feature usage tracking integrated into BaseOperationModule
3. ✅ Performance dashboard shows cache/query metrics
4. ✅ Comprehensive report generation (summary + detailed modes)
5. ✅ Lightweight healthcheck integration in optimize/align operations
6. ✅ Database schema updated with usage tracking tables
7. ✅ Documentation updated with new metrics and examples
8. ✅ Test coverage >80% for new healthcheck components

### Key Metrics to Validate:

- Healthcheck execution time: <2s (summary), <5s (detailed)
- Cache effectiveness: >70% hit rate
- Report accuracy: All metrics correct and current
- Zero performance regression in optimize/align operations

---

## 📋 Next Actions

1. **Phase 1 (Brain Analytics):** Create BrainAnalyticsCollector class
2. **Phase 2 (Feature Tracking):** Implement FeatureUsageTracker integration
3. **Phase 3 (Performance Dashboard):** Add cache/query metrics
4. **Phase 4 (Integration):** Wire into optimize/align with caching
5. **Testing:** Write comprehensive test suite
6. **Documentation:** Update CORTEX.prompt.md with new healthcheck capabilities

---

## 🔗 Related Files

- Implementation: `src/operations/healthcheck_operation.py`
- Tests: `tests/operations/test_healthcheck_operation.py`
- Documentation: `.github/prompts/modules/healthcheck-guide.md` (to be created)
- Database schema: `cortex-brain/tier3/schema.sql`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

# Tier 3: Development Context Intelligence

**Status:** ✅ COMPLETE  
**Tests:** 13/13 passing  
**Implementation Date:** November 6, 2025

## Overview

Tier 3 provides real-time project intelligence with data-driven planning and proactive warnings. It tracks git activity, file hotspots, and generates insights to help you understand project health and productivity patterns.

## Features

### ✅ Git Metrics Collection
- Daily commit tracking with contributor attribution
- Lines added/deleted/net growth analysis
- Files changed tracking
- Delta collection optimization (only new data)
- Automatic aggregation across contributors

### ✅ File Hotspot Analysis
- Churn rate calculation (edits / total commits)
- Stability classification:
  - **STABLE**: <10% churn rate
  - **MODERATE**: 10-20% churn rate
  - **UNSTABLE**: >20% churn rate
- Period-based analysis (default: 30 days)
- Automatic unstable file detection

### ✅ Velocity Analysis
- Commit velocity trend detection
- Window-based comparison (default: 7 days)
- Trend classification:
  - **Increasing**: >30% velocity increase
  - **Declining**: >30% velocity decrease
  - **Stable**: Within 30% range

### ✅ Insight Generation
- Automatic velocity drop warnings
- High-churn file alerts
- Data-driven recommendations
- Severity classification (INFO, WARNING, ERROR, CRITICAL)

## Usage

### Basic Usage

```python
from CORTEX.src.tier3 import ContextIntelligence

# Initialize
context = ContextIntelligence()

# Update all metrics (git + file hotspots)
context.update_all_metrics(days=30)

# Get comprehensive summary
summary = context.get_context_summary()
print(summary)
```

### Git Metrics

```python
# Collect git metrics for last 30 days
metrics = context.collect_git_metrics(days=30)

# Save to database
context.save_git_metrics(metrics)

# Retrieve metrics
all_metrics = context.get_git_metrics(days=30)
user_metrics = context.get_git_metrics(days=30, contributor="user_name")
```

### File Hotspot Analysis

```python
# Analyze file churn
hotspots = context.analyze_file_hotspots(days=30)

# Save to database
context.save_file_hotspots(hotspots)

# Get unstable files
unstable = context.get_unstable_files(limit=10)
for file in unstable:
    print(f"{file.file_path}: {file.churn_rate*100:.1f}% churn")
```

### Velocity Analysis

```python
# Calculate commit velocity
velocity = context.calculate_commit_velocity(window_days=7)
print(f"Trend: {velocity['trend']}")
print(f"Change: {velocity['change_percent']:.1f}%")
```

### Insights

```python
# Generate insights
insights = context.generate_insights()

for insight in insights:
    print(f"[{insight.severity.value}] {insight.title}")
    print(f"  {insight.description}")
    if insight.recommendation:
        print(f"  Recommendation: {insight.recommendation}")
```

## Database Schema

### Tables

1. **context_git_metrics** - Daily git activity
2. **context_file_hotspots** - File churn analysis

### Indexes

- `idx_git_date` - Git metrics by date (DESC)
- `idx_git_contributor` - Git metrics by contributor
- `idx_hotspot_file` - Hotspots by file path
- `idx_hotspot_churn` - Hotspots by churn rate (DESC)

## Performance Targets

- ✅ Context queries: <10ms
- ✅ Database size: <50KB (typical project)
- ✅ Update frequency: Delta updates (1 hour minimum)

## Data Classes

### GitMetric
```python
@dataclass
class GitMetric:
    metric_date: date
    commits_count: int
    lines_added: int
    lines_deleted: int
    net_growth: int
    files_changed: int
    contributor: Optional[str] = None
```

### FileHotspot
```python
@dataclass
class FileHotspot:
    file_path: str
    period_start: date
    period_end: date
    total_commits: int
    file_edits: int
    churn_rate: float
    stability: Stability
    last_modified: Optional[datetime] = None
    lines_changed: int = 0
```

### Insight
```python
@dataclass
class Insight:
    insight_type: InsightType
    severity: Severity
    title: str
    description: str
    recommendation: Optional[str] = None
    related_entity: Optional[str] = None
    data_snapshot: Optional[Dict[str, Any]] = None
```

## Testing

Run tests:
```bash
pytest CORTEX/tests/tier3/test_context_intelligence.py -v
```

Test coverage:
- Database initialization: 3 tests
- Git metrics collection: 3 tests
- File hotspot analysis: 2 tests
- Velocity analysis: 2 tests
- Insight generation: 2 tests
- Context summary: 1 test

**Total: 13 tests, all passing ✅**

## Integration

### With Other Tiers

- **Tier 1 (Conversations)**: Context enriches conversation history with project metrics
- **Tier 2 (Knowledge Graph)**: Insights feed pattern learning
- **Tier 0 (Governance)**: Velocity trends inform governance decisions

### With Agents

- **WorkPlanner**: Uses velocity trends for task estimation
- **ChangeGovernor**: Uses file hotspots for risk assessment
- **HealthValidator**: Uses build metrics for quality validation

## Future Enhancements

The following features are designed but not yet implemented:

- Test metrics tracking (TestMetric)
- Flaky test detection (FlakyTest)
- Build metrics monitoring (BuildMetric)
- Work pattern analysis (WorkPattern)
- CORTEX usage tracking (CortexUsage)
- Correlation discovery (Correlation)
- Extended insight types

## File Structure

```
CORTEX/src/tier3/
├── __init__.py                      # Public API
├── context_intelligence.py          # Main implementation
└── migrate_tier3.py                 # Migration script

CORTEX/tests/tier3/
├── __init__.py
└── test_context_intelligence.py     # 13 tests
```

## Notes

- Tier 3 requires git repository for full functionality
- Delta collection minimizes performance impact
- Database automatically created on first use
- All timestamps in UTC
- Metrics aggregated daily for efficiency

---

**Last Updated:** November 6, 2025  
**Version:** 1.0  
**Maintainer:** CORTEX Team

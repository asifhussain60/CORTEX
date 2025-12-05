# CORTEX 3.7.x Path A: Manager Metrics Quick Start

**Version:** 3.7.2 (Path A Implementation)  
**Status:** ✅ Production Ready  
**Author:** Asif Hussain  
**Implementation Date:** December 5, 2025

---

## 🎯 Overview

Path A adds manager-level metrics tracking to CORTEX 3.7.x by leveraging existing Tier 3 infrastructure. This implementation provides immediate value with minimal disruption while establishing the foundation for CORTEX 4.0's comprehensive Manager Metrics System.

### What's New in Path A

1. **Coverage Integration** - Automatic test coverage tracking during TDD workflow
2. **Git Metrics Enhancement** - Task attribution in git commits with time-to-phase tracking
3. **Manager Report Command** - Executive reports with velocity, coverage, and insights

---

## 🚀 Quick Start

### 1. Run Tests with Coverage

```python
from pathlib import Path
from src.tier3.coverage_tracker import CoverageTracker

# Initialize tracker
cortex_root = Path("d:/PROJECTS/CORTEX")
tracker = CoverageTracker(db_path=cortex_root / "cortex-brain/tier3/development_context.db")

# Run tests with coverage
result = tracker.run_tests_with_coverage(
    test_path="tests/",
    project_root=cortex_root,
    test_suite="cortex-internal"
)

print(f"Coverage: {result['coverage_percentage']}%")
print(f"Tests Passed: {result['passed_tests']}/{result['total_tests']}")
```

### 2. Create Task-Attributed Commits

```python
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator

# Initialize orchestrator
orchestrator = GitCheckpointOrchestrator(project_root=cortex_root)

# Create checkpoint with task attribution
result = orchestrator.create_checkpoint(
    session_id="session-20251205",
    checkpoint_type="phase-GREEN",
    message="Implemented manager metrics Path A",
    metadata={
        "task_id": "CORTEX-842",
        "feature_name": "Manager Metrics",
        "work_item_id": "ADO-12345"
    }
)

print(f"Checkpoint created: {result['checkpoint_id']}")
```

### 3. Generate Manager Report

```bash
# Weekly report (default)
python src/orchestrators/manager_report_orchestrator.py --period weekly

# Monthly report
python src/orchestrators/manager_report_orchestrator.py --period monthly

# Custom output path
python src/orchestrators/manager_report_orchestrator.py \
  --period weekly \
  --output cortex-brain/documents/reports/sprint-23.md
```

---

## 📊 Manager Report Features

### Report Sections

1. **Executive Summary**
   - Tasks completed
   - Average task duration
   - Test coverage percentage + trend
   - Critical hotspots
   - Action items

2. **Task Velocity**
   - Tasks per week/month
   - Average duration per task
   - TDD cycle counts
   - Phase durations (RED → GREEN → REFACTOR)

3. **Test Coverage Trends**
   - Coverage percentage over time
   - Total tests tracked
   - Pass rates
   - Coverage delta

4. **Code Hotspots**
   - Files with high churn rates
   - Stability classification (STABLE/MODERATE/UNSTABLE)
   - Edit frequency

5. **Insights & Recommendations**
   - Velocity drops
   - Coverage declines
   - Flaky tests
   - Build health issues

### Sample Report Output

```markdown
# 📊 CORTEX Manager Report

**Report Period:** Weekly
**Generated:** December 5, 2025 at 2:30 PM
**Coverage:** Last 7 days

---

## 🎯 Executive Summary

- **Tasks Completed:** 12
- **Average Task Duration:** 4.2 hours
- **Total Commits:** 48
- **Lines Changed:** 2,847
- **Test Coverage:** 87.3% (improving)
- **Critical Hotspots:** 2
- **Action Items:** 1

## 🚀 Task Velocity

| Period | Tasks | Avg Duration | Cycles | RED → GREEN | GREEN → REFACTOR |
|--------|-------|--------------|--------|-------------|------------------|
| 2025-12-01 | 3 | 4.1h | 12 | 8.3m | 12.1m |
| 2025-12-02 | 4 | 3.8h | 15 | 7.9m | 11.5m |
| 2025-12-03 | 5 | 4.5h | 18 | 9.1m | 13.2m |
```

---

## 🔧 Integration with TDD Workflow

### Automatic Coverage Tracking

Coverage is now automatically collected during TDD workflow when using the enhanced test runner:

```python
# In TDD orchestrator
from src.tier3.coverage_tracker import CoverageTracker

def run_green_phase_tests(self):
    """Run tests with automatic coverage collection."""
    tracker = CoverageTracker(db_path=self.tier3_db)
    
    result = tracker.run_tests_with_coverage(
        test_path=self.test_path,
        project_root=self.project_root,
        test_suite=self.current_feature
    )
    
    # Coverage automatically stored in tier3_test_activity
    return result
```

### Task Attribution in Commits

All TDD checkpoints can now include task metadata:

```python
# RED phase checkpoint
checkpoint_result = self.git_checkpoint.create_checkpoint(
    session_id=self.session_id,
    checkpoint_type="phase-RED",
    message="Test fails as expected for user authentication",
    metadata={
        "task_id": "AUTH-101",
        "feature_name": "User Authentication",
        "work_item_id": "ADO-5678"
    }
)
```

This creates git commits like:

```
CORTEX-TDD: phase-RED

Session: session-20251205-143022
Checkpoint: ckpt-a7b3f8e2
Message: Test fails as expected for user authentication
Timestamp: 2025-12-05T14:30:45+00:00
Task-ID: AUTH-101
Feature: User Authentication
Work-Item: ADO-5678
```

---

## 📈 Metrics Extraction

### Coverage Trends

```python
from src.tier3.coverage_tracker import CoverageTracker

tracker = CoverageTracker(db_path=tier3_db)

# Get last 30 days of coverage
trends = tracker.get_coverage_trends(days=30)

for trend in trends:
    print(f"{trend['timestamp']}: {trend['coverage_percentage']}%")

# Get latest coverage
latest = tracker.get_latest_coverage()
print(f"Current coverage: {latest['coverage_percentage']}%")
```

### Task Velocity

```python
from src.tier3.context_intelligence import ContextIntelligence

intelligence = ContextIntelligence(db_path=tier3_db)

# Extract task metrics from git history
task_metrics = intelligence.extract_task_metrics_from_git(days=30)

for task in task_metrics:
    print(f"Task: {task['task_id']}")
    print(f"  Duration: {task['total_duration_seconds'] / 3600:.1f} hours")
    print(f"  RED time: {task['red_time']:.1f}s")
    print(f"  GREEN time: {task['green_time']:.1f}s")

# Calculate velocity by week
velocity = intelligence.calculate_task_velocity(days=30, group_by="week")

for week in velocity:
    print(f"Week {week['period']}: {week['tasks_completed']} tasks")
```

---

## 🎯 Usage Scenarios

### Scenario 1: Sprint Retrospective

**Goal:** Review team velocity and quality for past sprint (2 weeks)

```bash
# Generate 2-week report
python src/orchestrators/manager_report_orchestrator.py \
  --period weekly \
  --output cortex-brain/documents/reports/sprint-23-retro.md

# Open report
code cortex-brain/documents/reports/sprint-23-retro.md
```

**What to look for:**
- Velocity trend (increasing/stable/declining)
- Coverage trend (should be improving or stable)
- Critical hotspots (files needing refactoring)
- Phase duration anomalies (RED or GREEN taking too long)

### Scenario 2: Monthly Executive Review

**Goal:** Provide high-level metrics to leadership

```bash
# Generate monthly report
python src/orchestrators/manager_report_orchestrator.py \
  --period monthly \
  --output cortex-brain/documents/reports/monthly-november-2025.md
```

**Key sections to present:**
- Executive Summary (1-slide summary)
- Task velocity trends (show progress)
- Coverage improvements (quality focus)
- Critical insights (action items)

### Scenario 3: Feature Development Tracking

**Goal:** Track specific feature from start to completion

```python
# Extract metrics for specific feature
intelligence = ContextIntelligence(db_path=tier3_db)
tasks = intelligence.extract_task_metrics_from_git(days=90)

# Filter by feature name
feature_tasks = [t for t in tasks if t['feature_name'] == 'User Authentication']

total_duration = sum(t['total_duration_seconds'] for t in feature_tasks)
print(f"Feature took {total_duration / 3600:.1f} hours")
```

---

## 🔍 Troubleshooting

### Coverage Not Recording

**Symptom:** `coverage_percentage` is NULL in `tier3_test_activity`

**Solutions:**
1. Ensure pytest-cov is installed: `pip install pytest-cov`
2. Check coverage XML is being generated: `ls -la .coverage_temp/`
3. Verify database path is correct
4. Check file permissions on `cortex-brain/tier3/development_context.db`

### Task Attribution Not Working

**Symptom:** No `Task-ID` field in commit messages

**Solutions:**
1. Verify metadata dict is passed to `create_checkpoint()`
2. Check git commit messages: `git log --grep="CORTEX-TDD" -1`
3. Ensure checkpoint orchestrator is v3.7.2+

### Report Generation Fails

**Symptom:** Manager report script exits with error

**Solutions:**
1. Check database exists: `cortex-brain/tier3/development_context.db`
2. Verify Python path includes `src/`: `echo $PYTHONPATH`
3. Check dependencies: `pip install -r requirements.txt`
4. Run with verbose: `python -v src/orchestrators/manager_report_orchestrator.py`

---

## 📚 API Reference

### CoverageTracker

```python
class CoverageTracker:
    """Test coverage tracking and storage."""
    
    def __init__(self, db_path: Path):
        """Initialize with Tier 3 database path."""
        
    def run_tests_with_coverage(
        self,
        test_path: str,
        project_root: Path,
        test_suite: str = "default",
        additional_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run pytest with coverage collection.
        
        Returns:
            {
                "success": bool,
                "test_run_id": str,
                "coverage_percentage": float,
                "total_tests": int,
                "passed_tests": int,
                "failed_tests": int,
                "skipped_tests": int,
                "duration_seconds": float
            }
        """
        
    def get_coverage_trends(
        self,
        test_suite: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get coverage trends over time."""
        
    def get_latest_coverage(
        self,
        test_suite: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get most recent coverage data."""
```

### GitCheckpointOrchestrator (Enhanced)

```python
class GitCheckpointOrchestrator:
    """Git checkpoint creation with task attribution."""
    
    def create_checkpoint(
        self,
        session_id: str,
        checkpoint_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create git checkpoint with optional task attribution.
        
        Metadata keys:
            - task_id: str (e.g., "CORTEX-842")
            - feature_name: str (e.g., "User Authentication")
            - work_item_id: str (e.g., "ADO-12345")
        
        Returns:
            {
                "success": bool,
                "checkpoint_id": str,
                "commit_sha": str,
                "session_id": str,
                "checkpoint_type": str,
                "timestamp": str
            }
        """
```

### ContextIntelligence (Enhanced)

```python
class ContextIntelligence:
    """Development context intelligence with task tracking."""
    
    def extract_task_metrics_from_git(
        self,
        days: int = 30,
        repo_path: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract task-level metrics from git commits.
        
        Returns list of:
            {
                "task_id": str,
                "feature_name": str,
                "work_item_id": str,
                "session_id": str,
                "checkpoints": List[dict],
                "red_time": float (seconds),
                "green_time": float (seconds),
                "refactor_time": float (seconds),
                "completion_time": datetime,
                "cycle_count": int,
                "total_duration_seconds": float
            }
        """
        
    def calculate_task_velocity(
        self,
        days: int = 30,
        group_by: str = "week"
    ) -> List[Dict[str, Any]]:
        """
        Calculate task completion velocity over time.
        
        Args:
            days: Lookback period
            group_by: "day", "week", or "month"
        
        Returns list of:
            {
                "period": str (ISO date),
                "tasks_completed": int,
                "total_duration": float,
                "total_cycles": int,
                "avg_red_time": float,
                "avg_green_time": float,
                "avg_refactor_time": float
            }
        """
```

### ManagerReportOrchestrator

```python
class ManagerReportOrchestrator:
    """Manager report generation."""
    
    def __init__(self, cortex_root: Path):
        """Initialize with CORTEX root directory."""
        
    def generate_report(
        self,
        period: str = "weekly",
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive manager report.
        
        Args:
            period: "daily", "weekly", "monthly", "quarterly"
            output_path: Optional custom output path
        
        Returns:
            {
                "success": bool,
                "report_path": str,
                "period": str,
                "days_covered": int,
                "summary": {
                    "tasks_completed": int,
                    "avg_task_duration_hours": float,
                    "total_commits": int,
                    "total_lines_changed": int,
                    "current_coverage": float,
                    "coverage_trend": str,
                    "critical_hotspots": int,
                    "critical_insights": int
                }
            }
        """
```

---

## 🔄 Migration to CORTEX 4.0

Path A is designed as a stepping stone to CORTEX 4.0. When upgrading:

### Data Preservation

All Path A data will be preserved and migrated:
- ✅ Coverage data in `tier3_test_activity` (already uses 4.0 schema)
- ✅ Task attribution in git commits (format compatible)
- ✅ Historical velocity calculations (will be re-processed)

### Schema Compatibility

Path A uses a subset of CORTEX 4.0's schema:
- `tier3_test_activity.coverage_percentage` - ✅ Already in 4.0 schema
- Git commit format - ✅ Compatible with 4.0 attribution engine
- Task velocity calculations - ✅ Will be enhanced in 4.0

### What Changes in 4.0

- **Task Registry:** Dedicated `tier3_task_registry` table (not in Path A)
- **Manager Portal:** Web UI replaces markdown reports
- **ML Attribution:** Advanced attribution engine vs Path A's simple parser
- **External Sync:** ADO/Jira integration (not in Path A)
- **Forecasting:** Predictive analytics (not in Path A)

### Upgrade Path

```bash
# When CORTEX 4.0 is released
python src/orchestrators/upgrade_orchestrator.py --upgrade

# Migration script will:
# 1. Preserve all Path A data
# 2. Backfill historical commits to task registry
# 3. Generate coverage baselines
# 4. Initialize ML models
# 5. Launch manager portal
```

---

## 📝 Feedback & Iteration

Path A is designed for rapid feedback. If you encounter issues or have suggestions:

1. **Generate diagnostic report:**
   ```bash
   python src/orchestrators/manager_report_orchestrator.py \
     --period weekly \
     --output diagnostic.md
   ```

2. **Check data quality:**
   ```python
   from src.tier3.context_intelligence import ContextIntelligence
   
   intel = ContextIntelligence(db_path=tier3_db)
   metrics = intel.extract_task_metrics_from_git(days=7)
   
   # Validate attribution
   attributed = [m for m in metrics if m['task_id']]
   print(f"Attribution rate: {len(attributed)/len(metrics)*100:.1f}%")
   ```

3. **Report issues:**
   - Document what you expected vs what happened
   - Include sample report output
   - Share diagnostic data (anonymized)

---

**Path A Status:** ✅ Production Ready  
**Next Milestone:** CORTEX 4.0 Phase 1 (Task Registry) - Q1 2025  
**Documentation Updated:** December 5, 2025

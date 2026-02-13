## 🚀 Phase 52 S7 Continuation Guide

**Status:** Ready to Begin | **Token Budget:** ~40% remaining | **Estimated Duration:** 6-8 hours

---

## S7: MCP Tools & Dashboard Integration (15 tests)

### Overview
Wrap S4-S6 orchestrators as MCP tools and integrate with CORTEX dashboard.

### Test Specifications Needed

#### Category 1: MCP Tool Registration (5 tests)
- `test_register_migration_mcp_tool` - cortex_migrate tool registration
- `test_register_performance_mcp_tool` - cortex_profile_perf tool
- `test_register_loadtest_mcp_tool` - cortex_load_test tool
- `test_tool_descriptions_and_parameters` - Tool metadata
- `test_mcp_tools_callable_from_chat` - Tool accessibility

#### Category 2: Dashboard Widget Integration (5 tests)
- `test_migration_progress_widget` - Real-time migration tracking
- `test_performance_trend_widget` - Performance over time
- `test_loadtest_results_widget` - Load test result display
- `test_regression_alert_widget` - Regression notification
- `test_dashboard_data_refresh` - Widget refresh/update

#### Category 3: GitHub Actions Integration (3 tests)
- `test_generate_github_action_workflow` - Workflow file creation
- `test_workflow_triggers_on_pr` - PR trigger configuration
- `test_workflow_blocks_on_regression` - Regression blocking logic

#### Category 4: End-to-End Integration (2 tests)
- `test_full_workflow_migration_to_dashboard` - Complete flow
- `test_mcp_tool_to_github_action_pipeline` - Tool → GitHub → Dashboard

---

## File Structure

### Files to Create
```
tests/unit/orchestrators/enterprise/test_mcp_tools_s7.py (500+ lines)
cortex/orchestrators/enterprise/mcp_integration.py (300+ lines)
cortex/orchestrators/enterprise/dashboard_widgets.py (250+ lines)
deployment/github-actions-templates.yaml (200+ lines)
```

### Files to Update
```
cortex/orchestrators/__init__.py - Register S4-S6 orchestrators
cortex/mcp/tools.py - Add S7 MCP tool definitions
cortex-registry/_cortex-master/index.yaml - Mark S7 complete
```

---

## Quick Start Commands

**1. Create S7 test file:**
```bash
touch tests/unit/orchestrators/enterprise/test_mcp_tools_s7.py
```

**2. Run S7 tests (will fail - RED phase):**
```bash
pytest tests/unit/orchestrators/enterprise/test_mcp_tools_s7.py -v
```

**3. Implement S7 classes (GREEN phase):**
- MCP tool wrapper classes
- Dashboard widget classes
- GitHub Actions generator

**4. Commit progress:**
```bash
git add -A && git commit -m "Phase 52 S7: MCP Tools & Dashboard - RED Phase (15/15 tests)"
```

---

## Key Classes to Implement

### MCP Tool Wrappers
```python
class MigrationMCPTool:
    """Wrap MigrationOrchestrator for MCP"""
    def execute(self, target_framework, source_language)
    
class PerformanceMCPTool:
    """Wrap PerformanceOrchestrator for MCP"""
    def profile_code(self, file_path, function_name)
    
class LoadTestMCPTool:
    """Wrap LoadTestOrchestrator for MCP"""
    def run_load_test(self, scenario_name, baseline_version)
```

### Dashboard Widgets
```python
class MigrationProgressWidget:
    def render_migration_progress(self, orchestrator)
    
class PerformanceTrendWidget:
    def render_performance_chart(self, baselines)
    
class LoadTestResultsWidget:
    def render_test_results(self, run)
    
class RegressionAlertWidget:
    def render_alerts(self, analysis)
```

### GitHub Actions Integration
```python
class GitHubActionsGenerator:
    def generate_workflow(self, orchestrator_type)
    def configure_pr_trigger(self, workflow)
    def configure_regression_blocking(self, workflow)
```

---

## Acceptance Criteria (AC) Matrix

| AC | Test | Description |
|----|------|-------------|
| AC-PHASE52-S7-001 | MCP Tool Registration | All 3 orchestrators registered as MCP tools |
| AC-PHASE52-S7-002 | Dashboard Widgets | All 4 widgets render correctly |
| AC-PHASE52-S7-003 | GitHub Actions | Workflows trigger on PR + block on regression |

---

## Registry Updates Needed

Update `cortex-registry/_cortex-master/index.yaml`:
```yaml
current_stage: "S7"
stage_progress: "All stages complete (109/165 tests)"
stages_complete: "7/7"
progress_percent: "100%"
status: "completed"
```

---

## Quick Reference: Key Classes from S4-S6

### From S4 (Migration)
```python
from cortex.orchestrators.enterprise.migration_execution import (
    MigrationExecutor, MigrationStep, MigrationExecutionPlan
)
```

### From S5 (Performance)
```python
from cortex.orchestrators.enterprise.performance import (
    PerformanceOrchestrator, ProfilerCapture, Bottleneck
)
```

### From S6 (LoadTest)
```python
from cortex.orchestrators.enterprise.loadtest import (
    LoadTestOrchestrator, K6TestGenerator, RegressionDetector
)
```

---

## Silent Autonomous Protocol

**Trigger:** "continue" → Auto-execute S7 RED phase
**Pattern:**
1. Create test file with 15 test specifications
2. Run tests (will fail - RED phase)
3. Implement classes to pass tests (GREEN phase)
4. Refactor for quality (REFACTOR phase)
5. Update registry and commit

**Progress Reporting:**
- ASCII progress bars (no narration)
- Report on completion/error only
- Commit after each stage

---

## Success Criteria

✅ All 15 S7 tests passing
✅ 109/165 total tests passing (Phase 52 at 100%)
✅ Production code: MCP tools + dashboard widgets
✅ GitHub Actions templates in deployment/
✅ Registry updated to mark Phase 52 complete
✅ Comprehensive AC coverage

---

**Ready to Begin:** YES
**User Command:** "continue" (to start S7 RED phase)


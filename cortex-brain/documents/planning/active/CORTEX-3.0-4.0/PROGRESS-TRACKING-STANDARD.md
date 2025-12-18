# CORTEX 4.0 Progress Tracking Standard

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Status:** 🟢 APPROVED - Core CORTEX 4.0 Pattern

---

## 📋 Executive Summary

**Visual progress tracking with automated orchestrator updates is now a CORTEX 4.0 standard practice.** All master plans, orchestrators, and worker plans MUST include:

1. **Visual Status Tracker** - ASCII progress bars showing real-time completion
2. **Automated Updates** - Orchestrators update tracker on phase completion
3. **Milestone Tracking** - Checkboxes for key achievements
4. **Metrics Dashboard** - Quantifiable outcomes (tests, docs, LOC reduced)

**Rationale:** Observable, self-documenting systems align with CORTEX 4.0 architecture principles of transparency, measurability, and continuous feedback.

---

## 🎯 Standard Components

### 1. Visual Status Tracker (Master Plans)

**ALL master plans MUST include this at the top:**

```markdown
## 📊 [OPERATION] PROGRESS TRACKER

**Last Updated:** [Date] | **Current Phase:** [Phase X] | **Week:** [N] | **Overall:** [X]% Complete

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: [Name]                                           [████████████] 100% │
│ Week 0: [Description]                                     ✅ COMPLETE        │
├─────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: [Name]                                           [███░░░░░░░░░]  25% │
│ Week 1: [Description]                                     [███░░]  60%  ⏳ ACTIVE│
│ Week 2: [Description]                                     [░░░░░]  0%         │
└─────────────────────────────────────────────────────────────────────────────┘

🎯 MILESTONES
├─ ✅ [Completed Milestone]
├─ ⏳ [In-Progress Milestone]
└─ ☐ [Pending Milestone]

📈 METRICS
├─ [Metric 1]: X/Y (Z%)
├─ [Metric 2]: Description
└─ [Metric 3]: Value (Target: Goal)
```

**🔄 AUTO-UPDATE INSTRUCTIONS:**

```python
from src.core.progress_tracker import update_master_plan_progress

update_master_plan_progress(
    phase="1",
    week="1",
    completion_percentage=60,
    metrics={...}
)
```
```

---

### 2. BaseOrchestrator Integration (Foundation)

**Standard Pattern (Phase 1, Week 1, Days 2-3):**

```python
# src/orchestrators/base/base_orchestrator.py
from src.core.progress_tracker import update_master_plan_progress
from abc import ABC, abstractmethod

class BaseOrchestrator(ABC):
    """Base class for all CORTEX 4.0 orchestrators with progress tracking."""
    
    def __init__(self, 
                 config: Dict[str, Any],
                 phase_number: str = None,
                 week_number: str = None):
        self.config = config
        self.phase_number = phase_number  # NEW: For progress tracking
        self.week_number = week_number    # NEW: For progress tracking
        self.logger = setup_logger(self.__class__.__name__)
        self.brain = BrainInterface()
        self.template_manager = TemplateManager()
    
    @abstractmethod
    def _execute_implementation(self, **kwargs) -> OrchestratorResult:
        """Subclasses implement actual logic here."""
        pass
    
    def execute(self, **kwargs) -> OrchestratorResult:
        """Execute orchestrator with automatic progress tracking."""
        try:
            result = self._execute_implementation(**kwargs)
            
            # AUTO-UPDATE: Track progress on completion
            if result.is_complete and self.phase_number:
                self._update_progress(result)
            
            return result
        except Exception as e:
            self.handle_error(e)
            raise
    
    def _update_progress(self, result: OrchestratorResult):
        """Update MASTER-PLAN progress tracker."""
        update_master_plan_progress(
            phase=self.phase_number,
            week=self.week_number,
            completion_percentage=self.calculate_phase_completion(),
            metrics=self._extract_metrics(result)
        )
    
    def _extract_metrics(self, result: OrchestratorResult) -> Dict:
        """Extract metrics from orchestrator result."""
        return {
            "orchestrators_migrated": getattr(result, "orchestrators_count", 0),
            "test_coverage": getattr(result, "coverage_percentage", "N/A"),
            "docs_generated": getattr(result, "docs_count", 0),
            "lines_reduced": getattr(result, "loc_delta", 0)
        }
    
    def calculate_phase_completion(self) -> int:
        """Calculate phase completion percentage (override in subclasses)."""
        return 100 if hasattr(self, "_is_complete") and self._is_complete else 0
```

**Why This Pattern?**
- ✅ **Automatic** - No manual tracker calls in subclasses
- ✅ **Consistent** - All orchestrators report progress the same way
- ✅ **Observable** - Real-time visibility into operation status
- ✅ **Testable** - Mock `update_master_plan_progress` in tests

---

### 3. PhaseManager Integration (Phase Transitions)

**Standard Pattern (Phase 1, Week 1, Days 2-3):**

```python
# src/orchestrators/base/phase_manager.py
from src.core.progress_tracker import update_master_plan_progress

class PhaseManager:
    """Manages orchestrator phases with progress tracking."""
    
    def __init__(self, orchestrator_name: str, phase_number: str, week_number: str):
        self.orchestrator_name = orchestrator_name
        self.phase_number = phase_number
        self.week_number = week_number
        self.phases = {}
        self.current_phase = None
    
    def transition(self, from_phase: str, to_phase: str) -> bool:
        """Transition between phases with progress update."""
        logger.info(f"🎭 Phase transition: {from_phase} → {to_phase}")
        
        # Update progress tracker on phase completion
        if from_phase and self._is_phase_complete(from_phase):
            self._update_phase_progress(from_phase)
        
        self.current_phase = to_phase
        return True
    
    def _update_phase_progress(self, completed_phase: str):
        """Update progress after phase completion."""
        completion = self.calculate_overall_completion()
        
        update_master_plan_progress(
            phase=self.phase_number,
            week=self.week_number,
            completion_percentage=completion
        )
    
    def calculate_overall_completion(self) -> int:
        """Calculate overall orchestrator completion."""
        total_phases = len(self.phases)
        completed_phases = sum(1 for p in self.phases.values() if p.is_complete)
        return int((completed_phases / total_phases) * 100) if total_phases > 0 else 0
```

**Why This Pattern?**
- ✅ **Granular** - Track progress at phase level (not just orchestrator)
- ✅ **Visual Feedback** - `🎭` hints show phase transitions in logs
- ✅ **Incremental** - Progress updates as work proceeds, not just at end

---

### 4. Validation Script Integration (Milestones)

**Standard Pattern (Phase 1, Week 3, Day 5):**

```python
# scripts/validate_cortex_4_foundation.py
from src.core.progress_tracker import update_master_plan_progress

def run_validation() -> bool:
    """Run foundation validation with progress tracking."""
    
    # ... validation logic ...
    
    if all_prerequisites_passing:
        # Update milestone on 100% pass
        update_master_plan_progress(
            phase="1",
            completion_percentage=100,
            milestone_completed="Foundation Validation"  # Updates 🎯 MILESTONES
        )
        
        print("✅ PHASE 1 FOUNDATION COMPLETE!")
        return True
    else:
        print("❌ Validation failed")
        return False
```

**Why This Pattern?**
- ✅ **Automated Milestones** - No manual checkbox updates
- ✅ **Gate Enforcement** - Validation must pass to proceed
- ✅ **Audit Trail** - Milestone completion timestamped in tracker

---

### 5. Worker Plan Template (Orchestrator-Specific)

**ALL worker plans MUST follow this template:**

```markdown
# [Orchestrator Name] Migration Plan

**Master Plan:** MASTER-PLAN.md  
**Phase:** X | **Week:** Y | **Duration:** Z days  
**Status:** [Status] | **Progress:** X%

---

## 📊 PROGRESS TRACKER

**Last Updated:** [Date] | **Overall:** X% Complete

```
┌─────────────────────────────────────────────────────────────┐
│ DAY 1: [Task]                           [███░░]  60%  ⏳ ACTIVE│
│ DAY 2: [Task]                           [░░░░░]   0%         │
│ DAY 3: [Task]                           [░░░░░]   0%         │
└─────────────────────────────────────────────────────────────┘

🎯 OBJECTIVES
├─ ✅ [Completed Objective]
├─ ⏳ [In-Progress Objective]
└─ ☐ [Pending Objective]

📈 METRICS
├─ Tests Written: X/Y
├─ Coverage: Z%
└─ LOC Reduced: -N
```

**🔄 AUTO-UPDATE:**

```python
# Update after each day's work
update_worker_plan_progress(
    plan_file="[ORCHESTRATOR]-MIGRATION-PLAN.md",
    day="1",
    completion_percentage=60
)
```
```

**Example: ExecutionOrchestrator Migration Plan**

```markdown
# ExecutionOrchestrator Migration Plan

**Master Plan:** MASTER-PLAN.md  
**Phase:** 3 | **Week:** 9 | **Duration:** 3 days  
**Status:** ⏳ ACTIVE | **Progress:** 33%

---

## 📊 PROGRESS TRACKER

**Last Updated:** December 18, 2025 | **Overall:** 33% Complete

```
┌─────────────────────────────────────────────────────────────┐
│ DAY 1: Design & Stub Implementation    [█████]  100%  ✅ COMPLETE│
│ DAY 2: Core Logic & DI Integration     [███░░]   60%  ⏳ ACTIVE│
│ DAY 3: Testing & Validation            [░░░░░]    0%         │
└─────────────────────────────────────────────────────────────┘

🎯 OBJECTIVES
├─ ✅ Create base structure
├─ ✅ Integrate with BaseOrchestrator
├─ ⏳ Write 20 unit tests
├─ ☐ Achieve 95%+ coverage
└─ ☐ Update MASTER-PLAN metrics

📈 METRICS
├─ Tests Written: 12/20 (60%)
├─ Coverage: 87%
└─ LOC Reduced: -340 (from consolidation)
```

**🔄 AUTO-UPDATE (Day 2 Complete):**

```python
from src.core.progress_tracker import update_master_plan_progress

# Update MASTER-PLAN.md after Day 2
update_master_plan_progress(
    phase="3",
    week="9",
    completion_percentage=8,  # 1/13 orchestrators = 7.7%
    metrics={
        "orchestrators_migrated": 1,
        "test_coverage": "87% (ExecutionOrchestrator)",
        "lines_reduced": -340
    }
)

# Mark milestone
update_master_plan_progress(
    phase="3",
    milestone_completed="First Orchestrator Migrated"
)
```
```

---

## 📋 Implementation Checklist

### Phase 1: Foundation (Week 1)

- [x] Create `src/core/progress_tracker.py` (204 lines)
- [x] Add visual tracker to MASTER-PLAN.md
- [x] Create PROGRESS-TRACKER-USAGE.md guide
- [ ] **Integrate `update_master_plan_progress()` in BaseOrchestrator**
- [ ] **Integrate progress tracking in PhaseManager**
- [ ] **Update validation script to track milestones**
- [ ] Test progress tracker with Phase 1 completion

### Phase 1.5: Documentation Framework (Week 3)

- [ ] Documentation orchestrator tracks `docs_generated` metric
- [ ] Auto-update after each doc batch generation
- [ ] Report to MASTER-PLAN metrics dashboard

### Phase 2: Brain Enhancement (Weeks 4-8)

- [ ] Brain migration orchestrator tracks tier completion
- [ ] RAG implementation tracks guideline store progress
- [ ] Update milestone on RAG integration live

### Phase 3: Orchestrator Migration (Weeks 9-13)

- [ ] **EVERY orchestrator migration updates `orchestrators_migrated` count**
- [ ] Track test coverage percentage per orchestrator
- [ ] Report lines reduced from consolidation
- [ ] Update MASTER-PLAN after each orchestrator completes
- [ ] Create worker plan for each orchestrator with embedded tracker

### Phase 4: Operations Simplification (Weeks 14-16)

- [ ] MCP Gateway tracks server registrations
- [ ] DI container tracks auto-discovered components
- [ ] Manifest reduction tracks file count decrease

### Phase 5: Testing & Validation (Weeks 17-19)

- [ ] Test suite tracks coverage percentage
- [ ] Performance benchmarks track regression metrics
- [ ] Quality gates update go/no-go status

### Phase 6: Documentation Finalization (Week 20)

- [ ] Final documentation orchestrator updates `docs_generated`
- [ ] Completion triggers `# 🎉 CONGRATULATIONS` template
- [ ] All milestones marked ✅ COMPLETE

---

## 🚨 Enforcement & Validation

### Pre-Commit Hook (Phase 1, Week 3)

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Validate progress tracker updates
python scripts/validate_progress_tracking.py

if [ $? -ne 0 ]; then
    echo "❌ Progress tracking validation failed!"
    echo "   Orchestrator completed but progress tracker not updated."
    exit 1
fi
```

### CI/CD Integration (Phase 5, Week 17)

```yaml
# .github/workflows/progress-tracking-audit.yml
name: Progress Tracking Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate Progress Tracking
        run: python scripts/validate_progress_tracking.py
      - name: Generate Progress Report
        run: python scripts/generate_progress_report.py
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: progress-report
          path: reports/progress-tracking-audit.md
```

---

## 📊 Metrics & Success Criteria

### Phase 1 Success Criteria

- ✅ `progress_tracker.py` tested and operational
- ✅ MASTER-PLAN.md visual tracker present and updating
- ✅ BaseOrchestrator integrates progress tracking
- ✅ PhaseManager tracks phase transitions
- ✅ Validation script updates milestones

### Phase 3 Success Criteria

- ✅ 13/13 orchestrators migrated with progress tracking
- ✅ Each orchestrator has worker plan with embedded tracker
- ✅ MASTER-PLAN metrics accurate (orchestrators_migrated, test_coverage, lines_reduced)
- ✅ All milestones marked ✅ COMPLETE

### Overall CORTEX 4.0 Success Criteria

- ✅ 100% of phases tracked with visual progress bars
- ✅ 100% of orchestrators auto-update progress on completion
- ✅ 100% of milestones automatically marked on achievement
- ✅ Progress tracking standard documented and enforced

---

## 🎓 Training & Adoption

### Developer Onboarding (Phase 1, Week 1)

**Required Reading:**
1. This document (PROGRESS-TRACKING-STANDARD.md)
2. `cortex-brain/documents/implementation-guides/PROGRESS-TRACKER-USAGE.md`
3. MASTER-PLAN.md progress tracker section

**Hands-On Exercise:**
```python
# Exercise: Create a simple orchestrator with progress tracking
from src.orchestrators.base import BaseOrchestrator

class HelloWorldOrchestrator(BaseOrchestrator):
    def __init__(self):
        super().__init__(
            config={},
            phase_number="1",
            week_number="1"
        )
    
    def _execute_implementation(self, **kwargs):
        print("Hello, CORTEX 4.0!")
        return OrchestratorResult(is_complete=True)

# Run and verify MASTER-PLAN.md updates
orchestrator = HelloWorldOrchestrator()
result = orchestrator.execute()

# Check: MASTER-PLAN.md Phase 1 should show progress update
```

### Code Review Checklist

**ALL orchestrator PRs MUST include:**
- [ ] Worker plan with embedded progress tracker
- [ ] `update_master_plan_progress()` call on completion
- [ ] Metrics extraction (tests, coverage, LOC)
- [ ] Milestone update (if applicable)
- [ ] Progress tracker tested in unit tests

---

## 🔮 Future Enhancements

### Planned (Phase 5, Week 19)

1. **Real-Time Dashboard**
   - Web UI showing live progress from MASTER-PLAN.md
   - Websocket updates on orchestrator completion
   - Historical progress charts

2. **Slack/Teams Integration**
   - Notify channel on milestone achievement
   - Daily progress summaries
   - Alert on blockers or failures

3. **Rollback Support**
   - Revert progress on orchestrator failure
   - Restore previous state from checkpoint
   - Auto-retry with progress preservation

4. **Multi-Repository Tracking**
   - Aggregate progress across CORTEX repos
   - Cross-project dependencies visualization
   - Unified progress dashboard

---

## 📚 References

- **Implementation:** `src/core/progress_tracker.py`
- **Usage Guide:** `cortex-brain/documents/implementation-guides/PROGRESS-TRACKER-USAGE.md`
- **Master Plan:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md`
- **Base Orchestrator:** `src/orchestrators/base/base_orchestrator.py`
- **Phase Manager:** `src/orchestrators/base/phase_manager.py`

---

**Approved:** December 18, 2025  
**Status:** 🟢 CORE CORTEX 4.0 STANDARD  
**Enforcement:** MANDATORY for all Phase 1+ work

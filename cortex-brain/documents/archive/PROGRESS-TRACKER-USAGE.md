# Progress Tracker Usage Guide

**Purpose:** Automated updates to MASTER-PLAN.md status visualization from orchestrators.

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025

---

## Quick Start

### From Orchestrator Code

```python
from src.core.progress_tracker import update_master_plan_progress

# After completing a phase or week
update_master_plan_progress(
    phase="1",                # Phase number (0, 1, 1.5, 2, 3, 4, 5, 6)
    week="1",                 # Week number (optional)
    completion_percentage=60, # Phase completion % (0-100)
    week_completion=60,       # Week completion % (optional)
    milestone_completed=None, # Milestone name if achieved (optional)
    metrics={                 # Optional metrics update
        "orchestrators_migrated": 0,
        "test_coverage": "10/10 foundation prerequisites passing",
        "docs_generated": 0,
        "lines_reduced": 0
    }
)
```

### From Command Line

```bash
# Test update
python src/core/progress_tracker.py

# From custom script
from src.core.progress_tracker import update_master_plan_progress
update_master_plan_progress(phase="1", completion_percentage=80)
```

---

## Parameters Reference

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `phase` | str | ✅ | Phase number | "1", "1.5", "2" |
| `week` | str | ❌ | Week number within phase | "1", "2" |
| `completion_percentage` | int | ✅ | Phase completion (0-100) | 60 |
| `week_completion` | int | ❌ | Week completion (0-100) | 80 |
| `milestone_completed` | str | ❌ | Milestone name if achieved | "Foundation Validation" |
| `metrics` | dict | ❌ | Metrics dictionary (see below) | {...} |

### Metrics Dictionary

```python
metrics = {
    "orchestrators_migrated": int,  # Number of orchestrators migrated (0-13)
    "test_coverage": str,           # Coverage description or percentage
    "docs_generated": int,          # Number of docs generated (0-200+)
    "lines_reduced": int            # Net lines reduced (can be negative)
}
```

---

## Usage Examples

### Example 1: Phase Completion

```python
# Phase 1 fully complete
update_master_plan_progress(
    phase="1",
    completion_percentage=100,
    milestone_completed="Foundation Validation",
    metrics={
        "orchestrators_migrated": 0,
        "test_coverage": "90%+ (foundation complete)",
        "docs_generated": 10,
        "lines_reduced": -500  # Reduced 500 lines
    }
)
```

Result:
```
│ PHASE 1: Foundation                                       [████████████] 100% │
├─ ✅ Foundation Validation (Week 3) - 10/10 prerequisites passing
├─ Test Coverage: 90%+ (foundation complete)
```

---

### Example 2: Week Progress

```python
# Week 1 at 60% progress
update_master_plan_progress(
    phase="1",
    week="1",
    completion_percentage=25,  # Overall phase 1 is 25% done
    week_completion=60         # Week 1 is 60% done
)
```

Result:
```
│ PHASE 1: Foundation                                       [███░░░░░░░░░]  25% │
│ Week 1: Base Orchestrator & Brain                        [███░░]  60%  ⏳ ACTIVE│
```

---

### Example 3: Orchestrator Migration

```python
# After migrating 5 orchestrators in Phase 3
update_master_plan_progress(
    phase="3",
    completion_percentage=40,
    metrics={
        "orchestrators_migrated": 5,
        "test_coverage": "85% (5 orchestrators)",
        "docs_generated": 50,
        "lines_reduced": -2000
    }
)
```

Result:
```
├─ Orchestrators Migrated: 5/13 (38%)
├─ Test Coverage: 85% (5 orchestrators)
├─ Documentation: 50/200+ docs generated
└─ Lines Reduced: -2000 (Target: -40% bloat)
```

---

### Example 4: Milestone Achievement

```python
# RAG integration complete
update_master_plan_progress(
    phase="2",
    week="8",
    completion_percentage=100,
    week_completion=100,
    milestone_completed="RAG Integration Live"
)
```

Result:
```
│ PHASE 2: Brain Enhancement + RAG                          [████████████] 100% │
├─ ✅ RAG Integration Live (Week 8)
```

---

## Integration Patterns

### BaseOrchestrator Integration

```python
class MyOrchestrator(BaseOrchestrator):
    def _execute_implementation(self, **kwargs) -> OrchestratorResult:
        # ... orchestrator work ...
        
        # Update progress on completion
        if self.is_complete():
            update_master_plan_progress(
                phase=self.phase_number,
                week=self.week_number,
                completion_percentage=self.calculate_phase_completion(),
                week_completion=100
            )
        
        return result
```

---

### PhaseManager Integration

```python
class MyPhaseManager(PhaseManager):
    def on_phase_complete(self, phase_name: str):
        # Update tracker after each phase
        update_master_plan_progress(
            phase=self.current_phase_number,
            completion_percentage=self.get_overall_completion()
        )
```

---

## Manual Updates (Emergency)

If automated updates fail, edit `MASTER-PLAN.md` directly:

1. **Update progress bars:**
   ```
   [████░░░░]  # 50% (4 filled, 4 empty out of 8 chars)
   [███░░]     # 60% (3 filled, 2 empty out of 5 chars)
   ```

2. **Update status icons:**
   ```
   ✅ COMPLETE   # 100% done
   ⏳ ACTIVE     # In progress (>0%, <100%)
   ☐ PENDING    # Not started (0%)
   ```

3. **Update timestamp:**
   ```markdown
   **Last Updated:** December 18, 2025 | ...
   ```

4. **Update metrics:**
   ```markdown
   ├─ Orchestrators Migrated: 5/13 (38%)
   ├─ Test Coverage: 85%
   └─ Lines Reduced: -2000 (Target: -40% bloat)
   ```

---

## Progress Bar Encoding

**12-character bars (phases):**
- 1 char = 8.33% completion
- Example: 60% = 7.2 chars filled → `[███████░░░░░]`

**5-character bars (weeks):**
- 1 char = 20% completion
- Example: 60% = 3 chars filled → `[███░░]`

**Formula:**
```python
filled = int((percentage / 100) * bar_width)
bar = f"[{'█' * filled}{'░' * (bar_width - filled)}]"
```

---

## Troubleshooting

### Issue: Update Not Reflecting

**Check:**
1. MASTER-PLAN.md path correct? (relative to project root)
2. File has write permissions?
3. Regex patterns matching? (phase/week numbers exact)

**Solution:**
```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)
update_master_plan_progress(...)
```

---

### Issue: Unicode Encoding Error

**Windows Console Issue:**
```python
# progress_tracker.py uses Unicode box characters (│ ├ └)
# Ensure file saved as UTF-8 with BOM
```

**Solution:**
```python
# Read/write with explicit encoding
content = path.read_text(encoding="utf-8")
path.write_text(content, encoding="utf-8")
```

---

## Testing

```python
# Test all scenarios
from src.core.progress_tracker import update_master_plan_progress

# Test 1: Phase update
update_master_plan_progress(phase="1", completion_percentage=50)

# Test 2: Week update
update_master_plan_progress(phase="1", week="2", week_completion=80)

# Test 3: Milestone
update_master_plan_progress(phase="3", milestone_completed="First Orchestrator Migrated")

# Test 4: Metrics
update_master_plan_progress(
    phase="5",
    completion_percentage=90,
    metrics={"test_coverage": "95%", "orchestrators_migrated": 13}
)
```

---

## Best Practices

1. **Update Frequency:**
   - ✅ After each week completion
   - ✅ After each phase completion
   - ✅ On milestone achievement
   - ❌ NOT on every task (too granular)

2. **Consistency:**
   - Always update `completion_percentage` AND `week_completion` together
   - Ensure phase % matches week progress (Week 1 = 33%, Week 2 = 66%, Week 3 = 100%)

3. **Metrics:**
   - Only update metrics that changed
   - Use descriptive test coverage strings ("85% - 5 orchestrators tested")
   - Lines reduced can be negative (reduction is positive outcome)

4. **Error Handling:**
   ```python
   success = update_master_plan_progress(...)
   if not success:
       logger.warning("Failed to update MASTER-PLAN.md progress tracker")
   ```

---

## Future Enhancements

- [ ] Automated rollback on orchestrator failure
- [ ] Progress snapshots (git checkpoints)
- [ ] Historical progress charting
- [ ] Slack/email notifications on milestone achievement
- [ ] Integration with CI/CD pipeline

---

**Questions?** See `src/core/progress_tracker.py` source code or contact Asif Hussain.

# 🚀 Quick Start Guide

## Invocation

**Standard (autonomous - all phases):**
```bash
system maintenance
```

**Specific phases only:**
```bash
system maintenance --phases 1,2,5
```

**Dry-run (no changes):**
```bash
system maintenance --dry-run
```

---

## What Happens During Maintenance

### Autonomous Execution
1. **NO user interaction** required between phases
2. **Auto-repair** ALL detected issues immediately
3. **Auto-commit** changes after each phase
4. **Visual progress tracker** shows completion status
5. **Final consolidated report** generated at end

### Duration
- **Full maintenance:** 15-30 minutes (typical)
- **Single phase:** 1-5 minutes per phase

---

## Common Scenarios

### Scenario 1: After Major Code Changes
```bash
# Run full maintenance to ensure system health
system maintenance
```

### Scenario 2: Fix Wiring Issues Only
```bash
# Run Phase 5 (Wiring) only
system maintenance --phases 5
```

### Scenario 3: Validate Templates
```bash
# Run Phase 2 (Template Validation) only
system maintenance --phases 2
```

### Scenario 4: Check Before Committing
```bash
# Dry-run to see what would be fixed
system maintenance --dry-run
```

---

## Expected Output

```
🧹 Phase 0: Executing Cleanup Orchestrator...
✅ Phase 0 complete: Space freed 245 MB

🔍 Phase 1: Holistic System Discovery...
✅ Phase 1 complete: 12 issues found

🗑️ Phase 2: Template Validation...
✅ Phase 2 complete: 3 broken references fixed

⛔ Phase 3: Data Preservation Validation...
✅ Phase 3 complete: All protected data intact

🔧 Phase 4: Scaffolding Verification...
✅ Phase 4 complete: 2 generators created

🔌 Phase 5: Component Wiring...
✅ Phase 5 complete: 100% wiring coverage achieved

🧪 Phase 6: Test Suite Execution...
✅ Phase 6 complete: 147/147 tests passing

📚 Phase 7: Knowledge Library Sync...
✅ Phase 7 complete: 3 broken refs fixed

🗂️ Phase 8: Report Organization...
✅ Phase 8 complete: 8 reports archived

🔀 Phase 9: Intent Router Validation...
✅ Phase 9 complete: All routes functional

📝 Phase 10: Prompt Optimization...
✅ Phase 10 complete: 4 prompts optimized

✅ Phase 11: Final Health Verification...
✅ Phase 11 complete: Health score 98%

---

# 🩺 CORTEX Maintenance Report

**Overall Progress:** ████████████████████ 100% ✅ HEALTHY

📊 Issues Found: 12 | Auto-Fixed: 12 | Health: 98%

[... detailed report follows ...]
```

---

## Frequency Recommendations

| Trigger | Action |
|---------|--------|
| **After major refactor** | Run full maintenance |
| **After adding new orchestrator/agent** | Run phases 4-5 (Scaffolding + Wiring) |
| **After template changes** | Run phase 2 (Template Validation) |
| **Monthly schedule** | Run full maintenance |
| **Before major release** | Run full maintenance + validation |

---

## Next Steps

- **Troubleshooting:** See `troubleshooting.md`
- **Customization:** See `customization.md`
- **Full Details:** See `../metadata/FULL-IMPLEMENTATION-REFERENCE.md`

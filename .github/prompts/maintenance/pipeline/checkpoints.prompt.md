# 🔒 Execution Checkpoints (Auto-Validated)

**At each phase transition, auto-validate:**

| Checkpoint | Validation | On Failure |
|------------|------------|------------|
| Phase 0→1 | Cleanup completed | Retry cleanup |
| Phase 1→2 | Discovery report exists | Regenerate |
| Phase 2→3 | Templates valid | Re-validate |
| Phase 3→4 | Protected data verified | **STOP maintenance** |
| Phase 4→5 | Scaffolds verified | Create missing |
| Phase 5→6 | 100% wiring coverage | Re-wire |
| Phase 6→7 | Tests passing | Fix failures |
| Phase 7→8 | Knowledge synced | Re-sync |
| Phase 8→9 | Reports organized | Re-organize |
| Phase 9→10 | Routes functional | Re-route |
| Phase 10→11 | Prompts optimized | Re-optimize |
| Phase 11→END | Health ≥95% | Escalate |

---

## Checkpoint Behavior

**Auto-Validation:**
- Runs IMMEDIATELY after each phase completes
- NO user interaction required
- Failures trigger auto-repair OR skip with warning
- Only Phase 3→4 checkpoint can STOP maintenance (data protection)

**Failure Handling:**

```python
def checkpoint_validation(from_phase, to_phase, result):
    """Auto-validate checkpoint between phases."""
    
    checkpoint = get_checkpoint_rule(from_phase, to_phase)
    
    if checkpoint.validate(result):
        log(f"✅ Checkpoint {from_phase}→{to_phase}: PASS")
        return True
    else:
        log(f"⚠️ Checkpoint {from_phase}→{to_phase}: FAIL")
        
        if checkpoint.action == "STOP":
            log("🛑 Critical checkpoint failed - stopping maintenance")
            generate_emergency_report(result)
            return False
        
        elif checkpoint.action == "RETRY":
            log(f"🔄 Retrying Phase {from_phase}...")
            retry_phase(from_phase)
            return checkpoint_validation(from_phase, to_phase, result)
        
        elif checkpoint.action == "FIX":
            log(f"🔧 Auto-repairing...")
            fix_result = auto_repair(result.issues)
            return True  # Continue with warning
        
        return True  # Skip with warning, continue
```

---

**Critical Checkpoint: Phase 3→4**

**Purpose:** Ensure data preservation rules enforced BEFORE any destructive operations

**Validation:**
- All protected data paths exist
- No critical files in cleanup targets
- Brain databases (.db files) intact
- User-added content preserved

**On Failure:**
- **STOP maintenance immediately**
- Generate emergency report
- Notify user of data protection violation
- Require manual intervention

---

**For phase-specific details, see `phases/phase-{00-11}-*.prompt.md`**

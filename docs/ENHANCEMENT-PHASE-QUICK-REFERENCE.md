# Enhancement Phase Gating - Quick Reference (2026-01-18)

## Property Update Summary

| Aspect | Old | New |
|--------|-----|-----|
| Property Name | `enhancement_only_when_ready` | `implement_when_ready` |
| Condition | Vague "when ready" | `locked: false` + all others `locked: true` |
| Primary Gate | All mandatory phases done | `locked` status visibility |
| Decision Logic | Generic pseudo-code | Explicit boolean checks |

## The New Rule

```
Phases can be implemented with implement_when_ready: true ONLY when:

1. locked: false (this phase)
2. locked: true (ALL other phases)
3. No other phases have implement_when_ready: true
```

## Phase Status in cortex-master.yaml

### PHASE-15-NEURAL-OBSERVATORY (Enhancement)
```yaml
status: "ENHANCEMENT_READY"
locked: false
enhancement_phase: true
implement_when_ready: true  ← NEW PROPERTY
```

### PHASE-DEPLOYMENT (Deployment)
```yaml
status: "NOT_STARTED"
locked: false
enhancement_phase: true
implement_when_ready: true  ← NEW PROPERTY
```

### ALL OTHER PHASES
```yaml
locked: true  ← Must be true for enhancement phases to activate
```

## Decision Tree for cortex-builder

```
Is there a phase with locked: false?
├─ NO → All locked, system complete
└─ YES → Check implement_when_ready
    ├─ not set (or false) → Mandatory phase, proceed with it
    └─ true → Check if ONLY this one
        ├─ YES + ALL others locked: true → Implement this enhancement
        └─ NO → Wait, other mandatory work pending
```

## Real-World Example

**Current State (2026-01-18):**
- PHASE-01 through PHASE-22: `locked: true` ✅
- PHASE-15-NEURAL-OBSERVATORY: `locked: false`, `implement_when_ready: true` 🔓
- PHASE-DEPLOYMENT: `locked: false`, `implement_when_ready: true` 🔓

**What cortex-builder should do:**
```
1. Find phases with locked: false
   → Found 2: PHASE-15, PHASE-DEPLOYMENT
2. Check implement_when_ready
   → PHASE-15: implement_when_ready: true
   → PHASE-DEPLOYMENT: implement_when_ready: true
3. Check if only ONE
   → Found 2, but check order
   → PHASE-15 comes first in roadmap
4. Check if ALL others locked: true
   → YES ✅
5. Action: Can implement PHASE-15 enhancement

6. After PHASE-15 complete:
   - Set PHASE-15: locked: true
   - Now only PHASE-DEPLOYMENT has locked: false
   - Check: implement_when_ready: true? YES
   - Check: All others locked: true? YES
   - Action: Can implement PHASE-DEPLOYMENT
```

## Implementation Pseudocode

```python
def can_implement_enhancement_phase(phase_tracker):
    """Check if an enhancement phase is ready for implementation"""
    
    unlocked_phases = [p for p in phase_tracker if p.locked == False]
    
    if len(unlocked_phases) != 1:
        return False, "Must have exactly one unlocked phase"
    
    phase = unlocked_phases[0]
    
    if phase.implement_when_ready != True:
        return False, "Phase is not marked as implement_when_ready"
    
    # Check all OTHER phases are locked
    for other_phase in phase_tracker:
        if other_phase.name != phase.name and other_phase.locked != True:
            return False, f"Other phase {other_phase.name} is not locked"
    
    return True, f"Phase {phase.name} is ready for implementation"
```

## Files Modified

1. `_workspaces/roadmap/cortex-master.yaml`
   - PHASE-15: `enhancement_only_when_ready` → `implement_when_ready`
   - PHASE-DEPLOYMENT: `enhancement_only_when_ready` → `implement_when_ready`
   - Both: Updated `implementation_prerequisite` text

2. `.github/prompts/cortex-builder.prompt.md`
   - Section: "Enhancement Phases (Optional Refinement Phases)"
   - Updated conditions and decision logic
   - New pseudocode for phase selection

3. `docs/ENHANCEMENT-PHASE-PROPERTY-UPDATE-2026-01-18.md`
   - Detailed explanation of changes
   - Rationale and benefits
   - Migration guidance

## Key Benefits

✅ **Explicit Status** - `locked` status is the single source of truth  
✅ **Simple Logic** - One boolean check: "Is this the only unlocked phase?"  
✅ **Scalable** - Supports multiple enhancement phases in future  
✅ **Transparent** - Anyone can see readiness at a glance  
✅ **Reversible** - Easy to set `locked: true` to prevent implementation  

## Migration Checklist

- ✅ Property renamed in cortex-master.yaml
- ✅ Implementation prerequisites updated
- ✅ Gating logic documented in cortex-builder.prompt.md
- ✅ Decision pseudocode provided
- ✅ Examples with new logic provided
- ✅ PHASE-15 updated
- ✅ PHASE-DEPLOYMENT updated
- ⏳ cortex-builder agent must use new decision logic

## Next Steps

1. **For cortex-builder agent**: Update phase selection logic to use `implement_when_ready` property
2. **For users**: Check `locked` status in phase_tracker to see enhancement readiness
3. **For future phases**: Use same pattern for other enhancement/deployment phases

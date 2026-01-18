# Property Update Complete: enhancement_only_when_ready → implement_when_ready (2026-01-18)

## What Changed

**Property Name:**
- ❌ OLD: `enhancement_only_when_ready: true`
- ✅ NEW: `implement_when_ready: true`

**Gating Logic:**
- ❌ OLD: Vague conditions like "all mandatory phases completed"
- ✅ NEW: Explicit locked-status-based conditions

## The New Gating Rule

### Condition in YAML
```yaml
implement_when_ready: true
```

### Meaning
"This phase can be implemented ONLY when ALL OTHER phases have `locked: true`"

### Validation Logic
```python
can_implement = (
    this_phase.locked == False AND
    this_phase.implement_when_ready == True AND
    all(other_phase.locked == True for other_phase in all_phases)
)
```

## Files Updated

### 1. cortex-master.yaml (phase_tracker)

**PHASE-15-NEURAL-OBSERVATORY:**
```diff
  - enhancement_phase: true
-   enhancement_only_when_ready: true
+   implement_when_ready: true
  - implementation_prerequisite: |
      cortex-builder.prompt.md MUST implement this phase ONLY when:
      - ALL OTHER phases in phase_tracker have: locked: true
      - This phase is the ONLY phase with: locked: false AND implement_when_ready: true
      ...
```

**PHASE-DEPLOYMENT:**
```diff
  - enhancement_phase: true
-   enhancement_only_when_ready: true
+   implement_when_ready: true
  - implementation_prerequisite: |
      cortex-builder.prompt.md MUST implement this deployment phase ONLY when:
      - ALL OTHER phases in phase_tracker have: locked: true
      - This phase is the ONLY phase with: locked: false AND implement_when_ready: true
      ...
```

### 2. cortex-builder.prompt.md

**Section: Enhancement Phases (Optional Refinement Phases)**

```diff
  ### When to Use Enhancement Phases
  Enhancement phases are **ONLY** considered for implementation when:
- 1. ✅ ALL mandatory phases from `cortex-master.yaml` phase_tracker are COMPLETED and LOCKED
- 2. ✅ ALL AC-IDs in the roadmap have been successfully implemented
- 3. ✅ NO other pending work exists
- 4. ✅ Complete audit trail verification has been performed
- 5. ✅ System is in a stable, production-ready state

+ 1. ✅ ALL OTHER phases in phase_tracker have: `locked: true`
+ 2. ✅ This phase is the ONLY phase with: `locked: false` AND `implement_when_ready: true`
+ 3. ✅ ALL mandatory phases from `cortex-master.yaml` phase_tracker are COMPLETED
+ 4. ✅ NO other pending work exists in phase_tracker
+ 5. ✅ System is in a stable, production-ready state
```

### 3. Documentation Files Created

- `docs/ENHANCEMENT-PHASE-PROPERTY-UPDATE-2026-01-18.md` - Detailed changes
- `docs/ENHANCEMENT-PHASE-QUICK-REFERENCE.md` - Quick reference guide

## Phase Current Status

### Locked Phases (locked: true)
- PHASE-01 through PHASE-14 ✅
- PHASE-16 through PHASE-22 ✅
- All remediation phases (RM-01 through RM-06) ✅
- **Result: 22+ phases with `locked: true`**

### Enhancement Phases (locked: false)
- PHASE-15-NEURAL-OBSERVATORY: `locked: false`, `implement_when_ready: true` 🔓
- PHASE-DEPLOYMENT: `locked: false`, `implement_when_ready: true` 🔓
- **Result: 2 phases with `locked: false` + `implement_when_ready: true`**

## Decision Logic (for cortex-builder)

```
While phases exist:
  1. Find all phases with locked: false
  2. If count != 1:
     → Skip enhancement phases, implement mandatory phases
  3. If found phase has implement_when_ready != true:
     → Skip, implement this mandatory phase
  4. If all OTHER phases have locked: true:
     → IMPLEMENT THIS ENHANCEMENT PHASE
  5. Else:
     → Wait for other phases to complete
```

## Examples

### Scenario 1: All phases locked except PHASE-15
```yaml
PHASE-01 through PHASE-14: locked: true ✅
PHASE-15-NEURAL-OBSERVATORY: locked: false, implement_when_ready: true 🟢 READY
PHASE-16 through PHASE-22: locked: true ✅

Result: cortex-builder IMPLEMENTS PHASE-15 ✅
```

### Scenario 2: Multiple phases unlocked
```yaml
PHASE-01 through PHASE-13: locked: true ✅
PHASE-14: locked: false, implement_when_ready: false ⏳ MANDATORY
PHASE-15-NEURAL-OBSERVATORY: locked: false, implement_when_ready: true 🔴 NOT READY
PHASE-16 through PHASE-22: locked: true ✅

Result: cortex-builder SKIPS PHASE-15, IMPLEMENTS PHASE-14 (mandatory)
```

### Scenario 3: Only PHASE-DEPLOYMENT waiting
```yaml
PHASE-01 through PHASE-14: locked: true ✅
PHASE-15-NEURAL-OBSERVATORY: locked: true ✅ (completed)
PHASE-16 through PHASE-21: locked: true ✅
PHASE-DEPLOYMENT: locked: false, implement_when_ready: true 🟢 READY

Result: cortex-builder IMPLEMENTS PHASE-DEPLOYMENT ✅
```

## Validation

✅ All references to `enhancement_only_when_ready` replaced with `implement_when_ready`  
✅ PHASE-15 updated with new property and gating conditions  
✅ PHASE-DEPLOYMENT updated with new property and gating conditions  
✅ cortex-builder.prompt.md updated with new decision logic  
✅ Implementation prerequisites clearly documented  
✅ Pseudocode and examples provided  
✅ Quick reference guide created for easy lookup  

## Benefits

| Aspect | Benefit |
|--------|---------|
| **Clarity** | Property name directly indicates gating condition |
| **Simplicity** | Single boolean check: locked status of all phases |
| **Visibility** | User can see readiness at a glance in cortex-master.yaml |
| **Scalability** | Supports multiple enhancement/deployment phases |
| **Reversibility** | Setting `locked: true` immediately prevents implementation |
| **Auditability** | Clear locked/unlocked status visible in phase_tracker |

## Migration Path for Agents

### Old Logic (DEPRECATED)
```python
if phase.enhancement_only_when_ready == True:
    if all_mandatory_phases_complete:
        implement(phase)
```

### New Logic (REQUIRED)
```python
if phase.implement_when_ready == True:
    if phase.locked == False:
        if all_other_phases_locked:
            implement(phase)
```

## Next Action

**Pending:** cortex-builder agent must update to use new `implement_when_ready` property name and locked-status-based decision logic.

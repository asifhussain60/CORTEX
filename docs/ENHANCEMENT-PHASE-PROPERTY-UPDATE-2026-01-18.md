# Enhancement Phase Property Update (2026-01-18)

## Summary of Changes

User Request: Change `enhancement_only_when_ready` to `implement_when_ready:true` with clearer gating logic based on locked phase status.

## Changes Made

### 1. Property Name Update
**Old:** `enhancement_only_when_ready: true`  
**New:** `implement_when_ready: true`

### 2. Gating Logic - CLEARER and MORE SPECIFIC

#### Previous Approach
- Generic conditions about "all mandatory phases completed"
- Vague about what "ready" means

#### New Approach (2026-01-18)
**cortex-builder.prompt.md MUST implement these phases ONLY when:**

```yaml
implementation_prerequisite: |
  cortex-builder.prompt.md MUST implement this phase ONLY when:
  - ALL OTHER phases in phase_tracker have: locked: true
  - This phase is the ONLY phase with: locked: false AND implement_when_ready: true
  - ALL mandatory phases (PHASE-01 through PHASE-22) are COMPLETED and LOCKED
  - System audit trail is fully verified and unbroken
  - Production baseline is established and stable
  
  Gating Logic:
    PHASE_READY = (ALL other phases have locked: true) AND
                  (NO other phases have implement_when_ready: true) AND
                  (This is ONLY enhancement phase ready)
    IF PHASE_READY: implement this phase
    ELSE: skip to next mandatory locked: true phase
```

### 3. Phases Updated

**PHASE-15-NEURAL-OBSERVATORY:**
- ✅ Changed `enhancement_only_when_ready: true` → `implement_when_ready: true`
- ✅ Updated `implementation_prerequisite` with new gating logic
- ✅ Locked status: `false` (ready for enhancement)

**PHASE-DEPLOYMENT:**
- ✅ Changed `enhancement_only_when_ready: true` → `implement_when_ready: true`
- ✅ Updated `implementation_prerequisite` with new gating logic
- ✅ Locked status: `false` (ready for deployment)

### 4. cortex-builder.prompt.md Updated

**Section: Enhancement Phases (Optional Refinement Phases)**

Updated documentation to reflect:
1. New property name: `implement_when_ready: true`
2. Clear gating conditions based on `locked` status
3. Explicit pseudocode for phase selection logic
4. All OTHER phases must have `locked: true`
5. This phase must be the ONLY one with `locked: false` + `implement_when_ready: true`

## Decision Logic Summary

```yaml
When cortex-builder evaluates phases:

1. Check all phases in phase_tracker
2. Find phases with locked: false
3. Count them
4. If count == 1 AND that phase has implement_when_ready: true:
   - Check if ALL OTHER phases have locked: true
   - If YES: This phase is ready for implementation
   - If NO: Wait - other mandatory phases still pending
5. If count > 1 OR other phases have locked: false:
   - Mandatory phases still pending
   - Skip enhancement phases
   - Continue with mandatory work
6. If count == 0:
   - All phases locked
   - System complete
```

## Key Benefit

**Clear Visibility:**
- One look at `locked` status in phase_tracker reveals whether enhancement phases are ready
- No ambiguity about "when ready" - it's explicit in the yaml: `locked: false` + `implement_when_ready: true`
- Prevents accidental premature implementation of enhancement/deployment phases

## Implementation Impact

### For cortex-builder Agent
- Simplified decision logic based on `locked` status
- Clear boolean check: "Are all OTHER phases `locked: true`?"
- Implementation proceeds only when gating conditions verified

### For cortext-master.yaml
- PHASE-15-NEURAL-OBSERVATORY: `locked: false`, `implement_when_ready: true`
- PHASE-DEPLOYMENT: `locked: false`, `implement_when_ready: true`
- All other phases: `locked: true` (or will be after completion)

### For Users
- Transparent readiness status in YAML
- No guessing about "when is the system ready?"
- Can see at a glance: `locked: false` means enhancement/deployment available when all others are `locked: true`

## Files Modified

1. `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml`
   - PHASE-15-NEURAL-OBSERVATORY: property update + implementation_prerequisite
   - PHASE-DEPLOYMENT: property update + implementation_prerequisite

2. `/Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-builder.prompt.md`
   - Section: "Enhancement Phases (Optional Refinement Phases)"
   - Updated when-to-use conditions
   - New decision logic pseudocode
   - Clearer implementation pattern

## Backwards Compatibility

⚠️ **Breaking Change:** Agents must update decision logic
- Old property: `enhancement_only_when_ready`
- New property: `implement_when_ready`
- Old agents looking for `enhancement_only_when_ready` will not find these phases

✅ **Migration Path:**
- cortex-builder.prompt.md updated with new logic
- All references in cortex-master.yaml updated
- Clear pseudocode for new decision logic provided

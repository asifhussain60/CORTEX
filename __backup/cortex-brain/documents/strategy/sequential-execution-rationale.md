# Sequential Execution Strategy - Decision Record

**Date:** 2026-01-11  
**Decision:** Switch from snowball to sequential phase execution  
**Status:** Active  

---

## Decision

CORTEX 6.0 will execute phases **sequentially** with 100% completion gates between phases.

## Context

Original plan used "snowball" strategy where:
- Phase 1 must complete 100% (foundation)
- Phase 2+ could overlap after Phase 1 done
- Allowed parallel finishing work (~15-20% time savings)

User challenged: "Should we proceed phase-by-phase instead?"

## Analysis

### Technical Dependency Reality
- **Sparse dependencies** between phases (not dense)
- Most Phase 2 work has ZERO Phase 1 dependencies
- Only 3-4 AC-IDs in Phase 2 require Phase 1 completion

### Tracking Complexity: Identical
Both approaches need same tracker structure:
```json
"phase_1_progress": "97%",
"phase_2_progress": "47%"
```

### Timeline Impact
- **Snowball:** ~21 days (with 15% parallelism advantage)
- **Sequential:** ~26.75 days (strict serial)
- **Difference:** ~5 days (15-20% slower)

### Risk Profile
- **Snowball:** Higher risk (context-switching, parallel state updates)
- **Sequential:** Lower risk (single focus, no concurrency hazards)

## Decision Rationale

**Chose Sequential because:**

1. **Cleaner mental model** - Single active phase at a time
2. **Easier tracking** - No ambiguity about "current state"
3. **Zero concurrency hazards** - No race conditions on progress-tracker.json
4. **Quality over speed** - 5-day timeline cost acceptable for risk reduction
5. **Current implementation only 5%** - Early enough to pivot without rework

**Trade-offs accepted:**
- 15-20% longer timeline (~5 days)
- Less parallelism efficiency
- Some idle time during phase transitions

## Implementation Changes

### Files Updated:
1. `.github/copilot-instructions.md` - Removed snowball strategy, added sequential gates
2. `.github/prompts/CORTEX.prompt.md` - Added 100% phase completion gate logic
3. `cortex-brain/tier1/tracking/progress-tracker.json` - Added execution_strategy field

### Key Changes:
- **Execution loop:** Check phase completion before selecting next AC-ID
- **Phase gates:** Stop at 100%, require user approval for next phase
- **Failure modes:** Removed "Concurrency Hazards" section
- **Strategy field:** `"execution_strategy": "SEQUENTIAL"`

## Monitoring

**Success criteria:**
- No context-switching confusion
- Phase transitions are clear events
- Progress tracking remains linear
- No parallel state corruption

**Failure signals:**
- Team feels blocked waiting for phases
- Timeline slippage exceeds 20%
- Quality doesn't improve vs. parallel approach

## Rollback Plan

If sequential proves too slow:
1. Re-enable snowball strategy (original design)
2. Add file locking for progress-tracker.json (fcntl/msvcrt)
3. Update prompts to allow Phase 2+ overlap
4. Accept 15% speed gain with concurrency risk mitigation

---

**Approved by:** Asif Hussain  
**Effective:** 2026-01-11  
**Review date:** 2026-01-25 (after Phase 1 complete)

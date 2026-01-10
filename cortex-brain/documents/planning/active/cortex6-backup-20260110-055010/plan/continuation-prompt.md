# CORTEX 6.0 Upgrade Plan - Continuation Context

## Current Status
**Plan Created:** 2026-01-09  
**Status:** ACTIVE - EXECUTION READY  
**DOR Achievement:** 100% (18/18 decisions, zero ambiguity)

## Quick Access

### Source Documents
- **Requirements:** `../acceptance-criteria/requirements/CX6-requirements.yaml`
- **Acceptance Criteria:** `../acceptance-criteria/CX6-acceptance-criteria.yaml`
- **Master Plan:** `../artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml`
- **Dashboard Plan:** `../artifacts/PLAN-VIEWER-DASHBOARD-PLAN.yaml`

### Plan Structure
- **Configuration:** `config.yaml` (execution settings)
- **Progress Tracking:** `../tracking/progress-tracker.json`
- **Phase Details:** `phases/` (will be created during execution)

## Execution Commands

### Start Stage 1 (Foundation)
```bash
# Via CORTEX orchestrator
python3 -m src.main "continue cortex 6 upgrade plan from stage 1"

# Or via TDD-Master (recommended for implementation)
python3 -m src.main "tdd implement audit logger from cortex6 plan"
```

### Check Progress
```bash
python3 -m src.main "epic review cortex6"
```

### View Dashboard (After Stage 3 Phase 3.7)
```bash
python3 cortex6/dashboard/serve.py
# Opens localhost:8000
```

## Key Decisions Summary

### DoR Session 1-3 (Q1-Q16)
- **Q3:** No backward compatibility (clean SKULL deletion)
- **Q4:** Manual housekeeping (user decides when to run)
- **Q5:** Clone + PATH deployment (no global install)
- **Q6:** 50MB audit log rotation + daily fallback
- **Q7:** Audit logs prove execution (not duplicate tests)
- **Q12:** bin/cortex shell script (standard Unix)
- **Q13:** Check cortex-brain/ folder (workspace detection)
- **Q14:** Store plans in CORTEX only (git isolation)
- **Q15:** Import-time lazy loading (<500ms startup)
- **Q16:** README + setup.sh (convenience + control)

### DoR Session 4 - Dashboard (Q17-Q20)
- **Q17:** Generate HTML once (WebSocket handles updates)
- **Q18:** Manual launch default (--dashboard-launch optional)
- **Q19:** Foreground server (--daemon optional)
- **Q20:** WebSocket push (no polling, <100ms latency)

## Next Steps

### Immediate (Stage 1 - Foundation)
1. **Phase 1.1:** Audit Logger Infrastructure (16-20h)
   - SQLite database + JSONL dual storage
   - <5ms latency target
   - Bootstrap self-audit validation
   
2. **Phase 1.2:** SKULL → CORE Migration (8-12h)
   - Delete brain-protection-rules.yaml
   - Create governance/core-rules.yaml
   - 61 rules preserved, new structure

3. **Phase 1.3:** AC Traceability (8-10h)
   - @pytest.mark.ac_id() decorators
   - 390+ AC coverage tracking
   - Dual validation (test + audit)

4. **Phase 1.4:** Housekeeping Orchestrator (12-16h)
   - Manual on-demand execution
   - Self-cleanup capability
   - Health report generation

### Progress Tracking
All progress tracked in:
- `../tracking/progress-tracker.json` (machine-readable)
- `../tracking/TODO.md` (human-readable)
- Audit logs in `../../../audit-logs/` (evidence trail)

### Architecture Compliance
All implementation must comply with:
- **CORE Rules:** 61 governance rules in cortex-brain/tier0/governance/
- **TDD Enforcement:** RED→GREEN→REFACTOR mandatory (CORE-019)
- **Audit Evidence:** All operations logged with AC-ID tags
- **Holistic Validation:** Architecture compliance verified continuously

## References

### Planning System
- **Planning v5:** Current (manual plans working)
- **Planning v6:** Target (with DoR workflow, fixed in Stage 3)
- **Planner v1:** Plan continuation/modification orchestrator

### Test Framework
- **pytest:** With AC-ID markers (@pytest.mark.ac_id('AC-XXX-001'))
- **Coverage Target:** ≥85% toolkit, 100% orchestrators
- **Validation:** Test execution + audit evidence required

### Dashboard (Stage 3 Phase 3.7)
- **Tech Stack:** FastAPI + WebSocket + Tailwind CSS
- **Theme:** Glassmorphism dark (dark blue gradient)
- **Features:** Real-time progress, audit logs, test coverage
- **Performance:** <2s load, <100ms WebSocket, <200MB memory

---

**To resume work:** Check `../tracking/TODO.md` for current phase and tasks.

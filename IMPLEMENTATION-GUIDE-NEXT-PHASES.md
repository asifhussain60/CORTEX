# Implementation Guide: Next 9 Unlocked Phases

**Status**: ✅ Ready for implementation  
**Date**: 2026-01-18  
**Framework**: cortex-builder.prompt.md (Unified Phase Mode)  
**Total AC-IDs**: 71 across 9 phases  

---

## Summary: What to Implement

### 🎯 Immediate Priority (Blocking Critical Path)
```
PHASE-03 (6 ACs)    → Production Reliability & Observability
PHASE-04 (12 ACs)   → Production Hardening & Security
PHASE-05 (17 ACs)   → Brittleness Fixes & Stabilization
PHASE-PARALLEL (3 ACs) → Folder Migration (parallel, must complete before PHASE-05)
```
**Why**: Foundation for all higher phases. PHASE-02 is locked and ready. These unblock everything else.

### 📚 Secondary Priority (Advanced Features)
```
PHASE-21 (8 ACs)    → Intelligent Knowledge Protocol
PHASE-22 (8 ACs)    → MCP Protocol Compliance  
PHASE-23 (4 ACs)    → Complexity-Aware Confirmation Gate
PHASE-DEPLOYMENT (10 ACs) → Universal Deployment & Multi-Repo
```
**Why**: Enhanced capabilities. Can start after PHASE-20 (delivered). Enables production deployment.

### 🔧 Maintenance Priority (Gap Remediation)
```
PHASE-REMEDIATION-07 (3 ACs) → MCP Tool Exposure Gap
```
**Why**: Fixes identified gap. Can run in parallel. Requires PHASE-REMEDIATION-06 (locked).

---

## Implementation Workflow (cortex-builder.prompt.md)

### Updated: Load Phase Context

**Single Source of Truth (SSOT)**:
- Location: `_workspaces/roadmap/cortex-master.yaml`
- Section: `phase_tracker:`
- Canonical: YES (no separate files needed)

**What you get**:
- Title, description, status, locked flag ✓
- All AC-IDs with specs ✓  
- Testing requirements ✓
- Governance rules ✓
- Success criteria ✓
- Dependencies ✓

### Updated: Implement AC-IDs

**For each phase in `phase_tracker.PHASE-XX.acceptance_criteria` section**:

1. **Read the AC specification**:
   ```yaml
   phases.PHASE-XX.acceptance_criteria:
     - ac_id: AC-XXX-XX-01
       title: "AC Title"
       description: "..."
       estimated_hours: 2
       test_count: 10
       status: NOT_STARTED
   ```

2. **Write tests first (TDD)**:
   - Create test file: `tests/unit/test_ac_xxx_xx_01.py`
   - Write RED tests covering all acceptance criteria
   - Expected test count: from `test_count` field

3. **Implement code**:
   - Write minimal implementation to pass tests
   - Follow CORE-001: Keep functions <500 lines
   - Include CORE-011: Type hints mandatory
   - Include CORE-012: Google-style docstrings

4. **Update AC Status**:
   ```yaml
   # Edit cortex-master.yaml → phase_tracker.PHASE-XX.acceptance_criteria
   - ac_id: AC-XXX-XX-01
     status: COMPLETED  ← Updated
     completed_date: 2026-01-18
     verified: true
     tests_passing: 10  ← All tests passing
   ```

5. **All tests pass?** → Update Phase Status:
   ```yaml
   # When all ACs in PHASE-XX are COMPLETED:
   phase_tracker.PHASE-XX:
     status: COMPLETED
     locked: true  ← Lock when all ACs done
   ```

### Updated: Validate & Commit

**Before every commit**:
```bash
# Validation runs automatically (pre-commit hook)
python3 scripts/validate_phase_sync.py

# If passes:
git add _workspaces/roadmap/cortex-master.yaml
git commit -m "phase-XX: AC-XXX-XX-01 COMPLETED"

# Pre-commit hook automatically:
# - Validates phase sync
# - Updates metadata counts if needed
# - Checks AC naming conventions (AC-DOMAIN-NNN-NN)
# - Prevents broken states
```

---

## Phase Details: Load Before Starting

### PHASE-03: Safety, Reliability & Observability (6 ACs)

**Overview**: Production Reliability, Graceful Degradation, Circuit Breaker Patterns, OpenTelemetry Metrics Integration

**AC Breakdown**:
- AC-??-001-01: Production Reliability Framework
- AC-??-001-02: Graceful Degradation Strategy
- AC-??-002-01: Circuit Breaker Patterns Implementation
- AC-??-002-02: Fallback Mechanisms
- AC-??-003-01: OpenTelemetry Metrics Integration
- AC-??-003-02: Observability Dashboard

**Dependencies**: PHASE-02 (COMPLETED & LOCKED) ✓

**Next Phase Blocker**: PHASE-04 cannot start until PHASE-03 complete

**Load Details**:
```bash
grep -A 150 "PHASE-03:" _workspaces/roadmap/cortex-master.yaml | grep -A 200 "acceptance_criteria:"
```

---

### PHASE-04: Production Hardening & Security (12 ACs)

**Overview**: Security Hardening, Secret Redaction, Hash Verification, Cross-File Coherence Validation

**AC Breakdown**: 12 acceptance criteria across:
- Security Hardening (4 ACs)
- Secret Redaction (3 ACs)
- Hash Verification (3 ACs)
- Cross-File Coherence (2 ACs)

**Dependencies**: PHASE-03 (must complete)

**Next Phase Blocker**: PHASE-05 cannot start until PHASE-04 complete

**Load Details**:
```bash
grep -A 150 "PHASE-04:" _workspaces/roadmap/cortex-master.yaml | grep -A 400 "acceptance_criteria:"
```

---

### PHASE-05: Brittleness Fixes & Stabilization (17 ACs)

**Overview**: Import Path Resolution, Cross-Platform Compatibility, Test Stabilization, Final Verification

**AC Breakdown**: 17 acceptance criteria across:
- Import Path Resolution (4 ACs)
- Cross-Platform Compatibility (5 ACs)
- Test Stabilization (5 ACs)
- Final Verification (3 ACs)

**Dependencies**: PHASE-04 (must complete) + PHASE-PARALLEL (must complete)

**Parallel Constraint**: PHASE-PARALLEL must complete before PHASE-05 starts

**Load Details**:
```bash
grep -A 150 "PHASE-05:" _workspaces/roadmap/cortex-master.yaml | grep -A 400 "acceptance_criteria:"
```

---

### PHASE-PARALLEL: Folder Migration & Organization (3 ACs)

**Overview**: Nested Folder Structure Organization, Import Updates, Non-Blocking Parallel Execution

**AC Breakdown**: 3 acceptance criteria
- AC-??-001-01: Folder Structure Planning & Design
- AC-??-001-02: Migration Script Implementation
- AC-??-001-03: Import Path Updates & Verification

**Parallel Execution**: 
- Can start: After PHASE-01 (COMPLETED & LOCKED) ✓
- Runs alongside: PHASE-02, PHASE-03, PHASE-04
- Must complete: Before PHASE-05 starts ✓

**Non-Blocking**: `blocking: false` (will not halt other phases)

**Load Details**:
```bash
grep -A 100 "PHASE-PARALLEL:" _workspaces/roadmap/cortex-master.yaml | grep -A 150 "acceptance_criteria:"
```

---

### PHASE-21: Intelligent Knowledge Protocol (8 ACs)

**Overview**: Unified knowledge access layer, intelligent routing, bulk ingestion pipeline

**AC Breakdown**: 8 acceptance criteria across:
- Knowledge Provider Protocol (2 ACs)
- Intelligent Knowledge Router (2 ACs)  
- Change Detection Service (2 ACs)
- Bulk Ingestion Pipeline & Refinement Engine (2 ACs)

**Dependencies**: PHASE-20-TEMPLATE-CONTENT (available) ✓

**Load Details**:
```bash
grep -A 300 "PHASE-21-INTELLIGENT-KNOWLEDGE-PROTOCOL:" _workspaces/roadmap/cortex-master.yaml | grep -A 400 "acceptance_criteria:"
```

---

### PHASE-22: MCP Protocol Compliance (8 ACs)

**Overview**: Proper Model Context Protocol compliance, tool standardization

**AC Breakdown**: 8 acceptance criteria (see phase_tracker details)

**Dependencies**: PHASE-21 (must complete)

**Load Details**:
```bash
grep -A 300 "PHASE-22-MCP-PROTOCOL-COMPLIANCE:" _workspaces/roadmap/cortex-master.yaml | grep -A 400 "acceptance_criteria:"
```

---

### PHASE-23: Complexity-Aware Confirmation Gate (4 ACs)

**Overview**: Intelligent confirmation gate, complexity-aware user prompts

**AC Breakdown**: 4 acceptance criteria
- AC-CONF-001-01: Complexity Analyzer
- AC-CONF-002-01: Confirmation Gate Logic
- AC-CONF-003-01: User Prompt Generation
- AC-CONF-004-01: Integration & Testing

**Dependencies**: PHASE-22 (must complete)

**Load Details**:
```bash
grep -A 200 "PHASE-23-COMPLEXITY-AWARE-CONFIRMATION-GATE:" _workspaces/roadmap/cortex-master.yaml | grep -A 300 "acceptance_criteria:"
```

---

### PHASE-DEPLOYMENT: Universal Deployment & Multi-Repo Distribution (10 ACs)

**Overview**: Single-command installation, multi-repo deployment, upgrade capability

**AC Breakdown**: 10 acceptance criteria across sections:
- Section A: Installation & Bootstrap (3 ACs)
- Section B: Multi-Repo Architecture (3 ACs)
- Section C: Upgrade & Distribution (2 ACs)
- Section D: Production Readiness (2 ACs)

**Dependencies**: PHASE-22-MCP-PROTOCOL-COMPLIANCE (must complete)

**Load Details**:
```bash
grep -A 300 "PHASE-DEPLOYMENT:" _workspaces/roadmap/cortex-master.yaml | head -400
```

---

### PHASE-REMEDIATION-07: MCP Tool Exposure Gap (3 ACs)

**Overview**: Add @mcp_tool decorator, expose domain orchestrator operations, /list-tools endpoint

**AC Breakdown**: 3 acceptance criteria
- AC-MCP-EXPOSURE-001: @mcp_tool decorator on get_relevant_business_knowledge_for_operation()
- AC-MCP-EXPOSURE-002: Expose domain orchestrator operations as MCP tools (15+ methods)
- AC-MCP-EXPOSURE-003: Add /list-tools MCP endpoint for tool discovery

**Dependencies**: PHASE-REMEDIATION-06 (COMPLETED & LOCKED) ✓

**Can Run**: In parallel with other phases (non-blocking)

**Load Details**:
```bash
grep -A 100 "PHASE-REMEDIATION-07:" _workspaces/roadmap/cortex-master.yaml
```

---

## Governance Compliance (Mandatory for all ACs)

✅ **CORE-001**: Incremental Execution - Functions <500 lines  
✅ **CORE-008**: TDD Pattern - Tests first, RED → GREEN  
✅ **CORE-011**: Type Hints - Mandatory on all functions  
✅ **CORE-012**: Docstrings - Google-style mandatory  
✅ **CORE-013**: Exception Handling - Specific types, no bare except  
✅ **CORE-024**: Audit Logging - AC lifecycle tracked  
✅ **CORE-027**: Audit Trail - START/EXECUTE/COMPLETE per AC  
✅ **CORE-028**: Portable Paths - Use Path(__file__).parent, no hardcoded /Users/  

---

## Pre-Implementation Checklist

- [ ] Read cortex-builder.prompt.md (already done)
- [ ] Verify PHASE-02 is locked: `locked: true` ✅
- [ ] Verify prerequisite phases complete: `status: COMPLETED` ✅
- [ ] Run validator: `python3 scripts/validate_phase_sync.py` 
- [ ] Install pre-commit hook: `.git/hooks/pre-commit` exists ✅
- [ ] Create feature branch: `git checkout -b next-phases`
- [ ] Load first phase: Read PHASE-03 acceptance_criteria section
- [ ] Write tests first (TDD): RED → GREEN pattern
- [ ] Implement code: One AC at a time
- [ ] Update phase_tracker: Each AC marked COMPLETED when tests pass
- [ ] Validate before commit: Pre-commit hook prevents broken states
- [ ] Commit: `git commit -m "phase-XX: AC-XXX-XX-01 COMPLETED"`

---

## Testing Strategy

**Test Placement**: One test file per AC-ID
```
tests/unit/test_ac_xxx_xx_01.py
tests/unit/test_ac_xxx_xx_02.py
```

**Test Count**: From phase_tracker `test_count` field per AC

**TDD Cycle**:
1. Write test (RED - should fail)
2. Run test: `pytest tests/unit/test_ac_xxx_xx_01.py -v`
3. Implement minimal code to pass
4. Run test again: `pytest tests/unit/test_ac_xxx_xx_01.py -v`
5. All tests passing (GREEN)
6. Refactor if needed
7. Mark AC as COMPLETED in phase_tracker

---

## File Locations & References

| Item | Location |
|------|----------|
| Master Plan | `_workspaces/roadmap/cortex-master.yaml` |
| Phase Specs | `phase_tracker: → PHASE-XX:` section |
| Scripts | `scripts/` |
| Tests | `tests/` |
| Source | `src/`, `cortex-brain/` |
| Validators | `scripts/validate_phase_sync.py` |
| Pre-commit Hook | `.git/hooks/pre-commit` |
| Documentation | `docs/` |

---

## Next Steps

1. ✅ Load this implementation guide
2. ✅ Understand cortex-builder.prompt.md workflow
3. ➡️ **START**: Begin with PHASE-03 implementation
   ```bash
   # Load PHASE-03 details
   grep -A 150 "PHASE-03:" _workspaces/roadmap/cortex-master.yaml | grep -A 200 "acceptance_criteria:"
   
   # Create branch
   git checkout -b phase-03-implementation
   
   # For each AC:
   # 1. Write tests (RED)
   # 2. Implement code (GREEN)
   # 3. Update phase_tracker
   # 4. Commit with validation
   ```

---

## Quick Reference: cortex-builder.prompt.md Commands

```bash
# Load phase from SSOT
grep -A 200 "PHASE-XX:" _workspaces/roadmap/cortex-master.yaml

# Validate before commit
python3 scripts/validate_phase_sync.py

# Run tests
pytest tests/unit/test_ac_xxx_xx_01.py -v

# Commit with validation
git add _workspaces/roadmap/cortex-master.yaml
git commit -m "phase-XX: AC-XXX-XX-01 COMPLETED"

# Check phase status
python3 -c "
import yaml
with open('_workspaces/roadmap/cortex-master.yaml') as f:
    data = yaml.safe_load(f)
    pt = data['phase_tracker']
    phase = pt['PHASE-XX']
    print(f\"Status: {phase['status']}, Locked: {phase['locked']}\")
"
```

---

**Ready to begin implementation!** Follow cortex-builder.prompt.md workflow for each phase.

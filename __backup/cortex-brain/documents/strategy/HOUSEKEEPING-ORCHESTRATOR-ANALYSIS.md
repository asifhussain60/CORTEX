# CORTEX Housekeeping Orchestrator Enhancement Analysis

**Date:** 2026-01-12  
**Classification:** Architecture Review / Strategic Recommendation  
**Author:** GitHub Copilot (with CORTEX governance framework)  
**Status:** Final Recommendation

---

## Executive Summary

**Recommendation: HYBRID MANUAL + EVENT-DRIVEN approach (not continuous autonomous)**

After analyzing CORTEX's current architecture, I recommend **actively challenging the "keep clean and wired 24/7 via continuous execution" model** and replacing it with a **targeted, reactive housekeeping system** that operates at strategic moments. Here's why continuous execution is suboptimal:

### Core Problem with Continuous Housekeeping

| Problem | Impact | Root Cause |
|---------|--------|-----------|
| **State Corruption Risk** | Cleanup mid-orchestration causes race conditions | Vacuum reads while orchestrators write |
| **Audit Trail Pollution** | Massive log volume from periodic maintenance | 1000s of "file moved" entries obscure real issues |
| **False Positives** | Marks valid temporary files as "orphaned" | No semantic understanding of orchestrator state |
| **Phase Gate Violations** | Vacuum runs independently of CORTEX phase lifecycle | Cleanup shouldn't happen mid-phase |
| **Context Drift** | Automated cleanup without human intent can delete needed assets | No approval/reason for cleanup action |

---

## 1. VIABILITY CHALLENGE

### Is "Housekeeping Always Keeps CORTEX Clean" Optimal?

**Answer: No, with important caveats.**

The assumption that "continuous autonomous cleaning = maximum potential" is **not supported** by the current architecture:

#### 1.1 Constraint: Phase Gate System

**Current State:** CORTEX uses **strict 100% phase gates** (Phase 1 → 100% before Phase 2 starts).

**Problem:** Continuous housekeeping is **orthogonal to phases**:
- Vacuum phase runs independently
- Creates cleanup work that isn't tracked in progress-tracker.json
- Vacuum produces AC-IDs (AC-VAC-001 to AC-VAC-010) but these aren't gated to phases
- Result: Phase completion claims (Phase 1 at 100%) don't account for ongoing cleanup work

**Constraint:** You CANNOT have true "maximum potential" housekeeping without integrating it into the phase gate system.

**Trade-off Implied:** Either:
- A) Integrate housekeeping as AC-IDs within each phase (adds ~5% overhead)
- B) Accept that housekeeping runs "outside the system" (loses audit trail)
- C) Run housekeeping only at phase boundaries (clean, auditable, less continuous)

#### 1.2 Constraint: Evidence-Based Completion

**Current State:** CORTEX Phase 1 requires **verification rate ≥ 80%** (AC-IDs proven by tests, not just commits).

**Problem:** Housekeeping creates "false evidence":
- Deleting a 2000-line duplicate file is marked as "cleanup complete" ✅
- But if no AC-ID test validates the deletion reasoning, it's unverifiable
- Example: Vacuum deletes `/cortex-brain/documents/old-analysis-2025.md` — but HOW do we prove it was truly orphaned?

**Constraint:** You CANNOT have clean evidence trails with autonomous deletions that aren't traceable to acceptance criteria.

**Trade-off:** Housekeeping must either:
- A) Have explicit AC-IDs with test cases that validate deletion reasoning (more overhead)
- B) Be manual with human intent (slower but fully auditable)
- C) Log deletions to audit trail with explanation, but accept loss of "reversibility proof"

#### 1.3 Constraint: Synchronization with State Manager

**Current State:** State Manager persists progress-tracker.json, evidence bundles, governance state.

**Problem:** Vacuum may delete files WHILE State Manager is writing:
- State Manager: `write governance.db` (SQLite transaction)
- Vacuum: `delete /cortex-brain/documents/old-file.md` (concurrent read)
- Result: Potential corruption if Vacuum deletes a file referenced in active transaction

**Current Mitigation:** Vacuum has exclusion list for critical files:
```python
PROTECTED_PATHS = {
    "cortex-brain/database/",
    "cortex-brain/tier0/",
    "cortex-brain/tier1/",
    "cortex-brain/registry/",
}
```

**Constraint:** With **more operations happening faster** (faster Phase 2-4 execution), the window for race conditions **increases proportionally**.

**Trade-off:** Housekeeping complexity increases exponentially with system speed.

---

## 2. FAILURE MODES (What Can Go Wrong)

### 2.1 High Probability Failures

| Failure Mode | Probability | Severity | Trigger | Recovery |
|--------------|-------------|----------|---------|----------|
| **Concurrent Write Collision** | HIGH (Phase 2+) | CRITICAL | Vacuum deletes while State Manager writes | Manual restore from git |
| **False Orphan Detection** | MEDIUM | HIGH | Vacuum sees 2-hour-old temp file, deletes before usage | Regeneration script (if it exists) |
| **Audit Trail Bifurcation** | MEDIUM | MEDIUM | Vacuum logs to audit, orchestrators log to audit, interleaved entries | Complex correlation query |
| **Phase Contamination** | MEDIUM | HIGH | Housekeeping finds artifacts from Phase 1, deletes during Phase 2 init | Rollback to Phase 1 checkpoint |
| **Critical File Deletion** | LOW (with exclusions) | CRITICAL | Exclusion list incomplete, vacuum deletes AC-INDEX.yaml | Git restore, manual AC re-registry |
| **Storage Thrashing** | LOW-MEDIUM | MEDIUM | Continuous filesystem scans on large trees (22,400 files) | I/O bottleneck, slow orchestrations |

### 2.2 Architectural Brittleness Points

**1. Exclusion List Maintenance**
- Current: Hardcoded PROTECTED_PATHS in vacuum code
- Problem: New tier1 working memory files added, not in exclusion list
- Risk: Manual edits to code needed for each new protected path

**2. Semantic Gap**
- Current: "File older than 7 days" = orphaned?
- Problem: Temporary analysis files are created daily, reused in new analysis
- Risk: Delete needed analysis that happens to be 8 days old

**3. No "Intent Registry"**
- Current: Vacuum has no way to ask "is this file intentionally here?"
- Problem: cortex-brain/documents/ has 970+ files, many are learning/history
- Risk: Delete valuable historical context assuming it's obsolete

---

## 3. OPTIMAL ALTERNATIVE ARCHITECTURE

### 3.1 Recommended: Strategic Reactive Housekeeping

**Instead of continuous cleanup, use phase-integrated selective cleanup:**

```
PHASE LIFECYCLE:
  Phase N start
  ├─ Load phase AC-IDs
  ├─ Execute phase work
  ├─ HOUSEKEEPING GATE: Run targeted cleanup
  │   ├─ Clean phase N-1 temporary files only
  │   ├─ Verify no in-use assets deleted
  │   ├─ Generate cleanup evidence bundle
  │   └─ Update progress-tracker.json
  └─ Mark Phase N complete → Verify 100% with cleanup included
```

**Rationale:**
- ✅ Integrated into phase gates (no system state ambiguity)
- ✅ Cleanup artifacts fully auditable (part of phase evidence)
- ✅ No concurrent write collisions (cleanup happens at phase boundary)
- ✅ Cleaner correlation in audit trail
- ✅ Explicit intent: "Cleanup before advancing to next phase"

**Trade-off:** ~5% more time per phase, but **100% auditability** and **zero race conditions**.

---

### 3.2 Three-Tier Housekeeping Strategy

#### Tier 1: Phase-Boundary Cleanup (Mandatory)
```yaml
scope: Previous phase temporary files
frequency: Once per phase transition
files_targeted: *.tmp, *.cache, build artifacts, test output
ac_ids: AC-CLEAN-001 to AC-CLEAN-003 (existing)
safety: Protected file list + git tracking
evidence: Cleanup bundle with file deletion manifest
risk: VERY LOW (scoped, bounded)
```

**Implementation:** 
- Add to MasterOrchestrator: Before marking phase complete, run CLEAN phase
- Cleanup AC-IDs produce evidence that proves "Phase N cleanup successful"
- Adds ~2-3% to phase duration

#### Tier 2: Semantic Cleanup (Manual + Reactive)
```yaml
scope: Orphaned analyses, duplicate documents, obsolete prompts
frequency: Weekly (manual review) or on-demand
files_targeted: cortex-brain/documents/*, docs/archives/*, old-*.md
ac_ids: Would need AC-CLEAN-004 to AC-CLEAN-006 (new)
safety: Requires human approval (preview first)
evidence: Manual cleanup ticket with justification
risk: MEDIUM (semantic judgment required)
```

**Example:**
```bash
# Weekly manual review (30 minutes, intentional)
python3 scripts/cleanup-orchestrator.py --mode=preview --tier=semantic

# Show files eligible for cleanup
# User reviews, marks files for deletion with reason
# User approves cleanup
# Cleanup generates AC evidence bundle with justification
```

**Trade-off:** Manual work, but **maximum correctness** and **documented intent**.

#### Tier 3: Infrastructure Cleanup (Automated, Very Narrow)
```yaml
scope: Build artifacts, pytest cache, unused node_modules
frequency: Continuous (safe)
files_targeted: __pycache__/, .pytest_cache, htmlcov/, *.egg-info
ac_ids: AC-CLEAN-INFRA-001 (new, single catch-all)
safety: Only gitignored files
evidence: Hourly checkpoint logs
risk: VERY LOW (only deletes what .gitignore marks)
```

**Implementation:**
- Runs as background process or scheduled job
- Only deletes `.gitignore`-d patterns
- Logs to audit with minimal verbosity
- No AC-ID proliferation (single "housekeeping" AC)

---

## 4. CONCRETE DESIGN RECOMMENDATIONS

### 4.1 Implement Phase-Integrated Cleanup

**Change MasterOrchestrator:**
```python
# In src/orchestrators/master/master_orchestrator.py

def complete_phase(self, phase_num: int) -> PhaseResult:
    """Execute cleanup gate before marking phase complete."""
    
    # 1. Run orchestrators for this phase
    orchestrator_result = self.execute_phase_ac_ids(phase_num)
    
    # 2. HOUSEKEEPING GATE: Clean up after phase
    cleanup_result = self.run_cleanup_for_phase_boundary(phase_num)
    if cleanup_result.failed:
        return PhaseResult.BLOCKED("Cleanup failed, cannot advance")
    
    # 3. Mark phase complete (with cleanup evidence included)
    self.progress_tracker.mark_phase_complete(
        phase_num,
        evidence_includes=[
            orchestrator_result.evidence_bundle,
            cleanup_result.evidence_bundle,  # NEW: Cleanup proof
        ]
    )
    
    return PhaseResult.SUCCESS()
```

**Benefits:**
- Cleanup is **part of phase evidence** (phase not complete if cleanup fails)
- No orphaned cleanup work
- Clear causality: "Phase 2 complete = orchestration + cleanup validated"

**AC-ID Assignments:**
- AC-CLEAN-001: Phase boundary cleanup framework
- AC-CLEAN-002: Temporary file detection (trustworthy)
- AC-CLEAN-003: Cleanup evidence bundle (proves files deleted & safe)

### 4.2 Add Intent Registry for Semantic Cleanup

**Create:** `cortex-brain/registry/file-intent-registry.yaml`
```yaml
version: '1.0'
purpose: |
  Mark files as intentional (keep) or optional (candidate for cleanup)
  Enables semantic cleanup without guessing

file_registry:
  cortex-brain/documents/archives/:
    intent: keep
    reason: Historical reference, learning material
    last_touched: 2026-01-10
    suggested_cleanup: false
    
  cortex-brain/documents/reports/:
    intent: keep
    reason: Phase completion evidence bundles
    last_touched: 2026-01-11
    suggested_cleanup: false
  
  cortex-brain/documents/old-analysis-2025/:
    intent: optional
    reason: Deprecated analysis, knowledge migrated
    last_touched: 2025-12-01
    suggested_cleanup: true
    approval_required: true
```

**Benefits:**
- Cleanup decision is **documented intent**, not inference
- Approval workflow: Cleanup only proceeds if intent = optional + approved
- Audit trail shows "why was this deleted?" explicitly
- No semantic guessing

### 4.3 Separate Infrastructure Cleanup as Autonomous Background Task

**Create:** `src/orchestrators/housekeeping/infra-cleanup.py`
```python
class InfraCleanupDaemon:
    """
    Autonomous cleanup of infrastructure artifacts.
    Only deletes .gitignore-d files, runs hourly.
    """
    
    def __init__(self):
        self.workspace_root = Path(project_root())
        self.gitignore_patterns = self.load_gitignore_patterns()
    
    def run_cleanup_cycle(self) -> Dict[str, Any]:
        """Run hourly cleanup of infrastructure artifacts."""
        
        # Only delete patterns explicitly in .gitignore
        files_to_delete = self.find_gitignored_files()
        
        # Safety: Skip certain patterns even if gitignored
        SAFETY_OVERRIDE = {
            "cortex-brain/database/",
            "cortex-brain/tier0/",
            ".env",
            ".secrets",
        }
        
        safe_deletions = [
            f for f in files_to_delete 
            if not any(s in str(f) for s in SAFETY_OVERRIDE)
        ]
        
        # Execute deletions
        deleted_count = 0
        for file_path in safe_deletions:
            file_path.unlink()
            deleted_count += 1
        
        # Log to audit (minimal, non-blocking)
        audit_logger.info(
            "infra_cleanup_cycle",
            deleted_count=deleted_count,
            category="INFRASTRUCTURE"
        )
        
        return {
            "status": "success",
            "files_deleted": deleted_count,
            "cycle_time_ms": timer.elapsed_ms()
        }
```

**Benefits:**
- **Truly autonomous**, no human intervention needed
- **Scoped to safe patterns** (gitignored infrastructure only)
- **Non-blocking** (audit log, not evidence bundle)
- Can run as scheduled job or background service

---

## 5. IMPLEMENTATION ROADMAP

### Phase 2 Enhancement (Add to existing AC-CLEAN-001-003)

| Item | AC-ID | Effort | Integration |
|------|-------|--------|-------------|
| Phase-boundary cleanup framework | AC-CLEAN-001 | 1 day | MasterOrchestrator.complete_phase() |
| Intent registry system | NEW: AC-CLEAN-201 | 2 days | Vacuum reads intent before deleting |
| Infrastructure daemon | NEW: AC-CLEAN-202 | 2 days | Scheduled job or background service |
| Cleanup evidence bundles | AC-CLEAN-003 (enhance) | 1 day | Include intent, approval, deleted manifest |

**Total Addition:** ~6 days to Phase 2

**Alternative:** Defer to Phase 3 if Phase 2 schedule tight.

### Implementation Steps

1. **Week 1:** Add intent registry, update vacuum to check intent before deleting
2. **Week 2:** Implement phase-boundary cleanup in MasterOrchestrator
3. **Week 3:** Deploy infrastructure daemon as background task
4. **Week 4:** Integration tests, evidence bundle validation

---

## 6. EXPLICIT TRADE-OFFS MATRIX

### Option A: Continuous Autonomous Cleanup (Current Proposal)
| Aspect | Rating | Notes |
|--------|--------|-------|
| **Speed** | ⭐⭐⭐⭐ | Cleanup happens constantly, no phase delay |
| **Correctness** | ⭐⭐ | Orphan detection has false positives |
| **Auditability** | ⭐⭐⭐ | Cleanup logged but outside phase context |
| **Safety** | ⭐⭐ | Race condition risk with state manager |
| **Maintainability** | ⭐⭐ | Exclusion lists, semantic heuristics are fragile |
| **Evidence Quality** | ⭐⭐ | Hard to prove "why" a file was deleted |
| **CORTEX Alignment** | ⭐⭐ | Orthogonal to phase gates and evidence system |
| **Overall** | ⭐⭐⭐ | Fast but risky, hard to verify |

### Option B: Phase-Integrated + Intent Registry (RECOMMENDED)
| Aspect | Rating | Notes |
|--------|--------|-------|
| **Speed** | ⭐⭐⭐ | ~5% overhead per phase for cleanup |
| **Correctness** | ⭐⭐⭐⭐ | Intent documented, human judgment where needed |
| **Auditability** | ⭐⭐⭐⭐⭐ | Cleanup is part of phase evidence |
| **Safety** | ⭐⭐⭐⭐ | No race conditions, clear phase boundaries |
| **Maintainability** | ⭐⭐⭐⭐ | Intent registry is simple, self-documenting |
| **Evidence Quality** | ⭐⭐⭐⭐⭐ | Every deletion backed by intent + approval |
| **CORTEX Alignment** | ⭐⭐⭐⭐⭐ | Perfectly integrated into phase gate system |
| **Overall** | ⭐⭐⭐⭐⭐ | Slightly slower but fully robust |

### Option C: Manual Weekly + Infrastructure Daemon
| Aspect | Rating | Notes |
|--------|--------|-------|
| **Speed** | ⭐⭐ | Semantic cleanup only weekly, infrastructure only |
| **Correctness** | ⭐⭐⭐⭐⭐ | No false positives (human reviews) |
| **Auditability** | ⭐⭐⭐⭐ | Manual cleanup tracked, daemon minimal logs |
| **Safety** | ⭐⭐⭐⭐⭐ | Daemon only touches gitignored files |
| **Maintainability** | ⭐⭐⭐⭐ | Simple, predictable behavior |
| **Evidence Quality** | ⭐⭐⭐⭐⭐ | Manual cleanup fully documented |
| **CORTEX Alignment** | ⭐⭐⭐⭐ | Fits governance model, lower integration overhead |
| **Overall** | ⭐⭐⭐⭐ | Slower but maximally safe and clear |

---

## 7. CRITICAL CONSTRAINTS

### Constraint #1: CORE-001 Incremental Execution
**Rule:** Operations must be <500 line increments

**Impact:** Continuous cleanup scanning 22,400 files in cortex-brain/ may exceed token budget in single execution.

**Mitigation:** Vacuum already implements batched file processing, but should add token monitoring to cleanup phase.

### Constraint #2: CORE-017 Governance Enforcement
**Rule:** All operations logged to audit trail with governance validation

**Impact:** Cleanup must generate evidence, not just audit logs

**Mitigation:** Implement AC-CLEAN-* AC-IDs for each cleanup activity with supporting tests

### Constraint #3: CORE-019 TDD Enforcement
**Rule:** No code without tests

**Impact:** Cleanup decisions must be testable (file truly orphaned, etc.)

**Mitigation:** Test cases for orphan detection heuristics, semantic cleanup requires manual approval

---

## 8. FINAL RECOMMENDATION

### To Keep CORTEX Clean, Wired, and Operating at Maximum Potential:

**Use a hybrid approach:**

1. **Phase-Boundary Cleanup (Mandatory, Automated)**
   - Integrated into phase completion workflow
   - Deletes only phase N-1 artifacts
   - Safety: Protected file list
   - Evidence: Cleanup bundle proves deletions

2. **Intent Registry (Semi-Automated, Manual Approval)**
   - YAML registry marks files as "keep" or "optional"
   - Weekly manual review for semantic cleanup candidates
   - Cleanup proceeds only with human approval
   - Full audit trail shows reason for each deletion

3. **Infrastructure Daemon (Truly Autonomous, Scoped)**
   - Runs on schedule (hourly) or as background service
   - Deletes ONLY .gitignore-d patterns
   - No approval needed (safe by design)
   - Minimal audit logging (non-blocking)

**Why This Works:**
- ✅ No race conditions (phase boundaries are safe points)
- ✅ Full auditability (intent + approval + evidence)
- ✅ Aligned with CORTEX phase gate system
- ✅ Distinguishes routine maintenance from semantic decisions
- ✅ Safer and more maintainable than continuous heuristic-based cleanup
- ✅ ~5% time overhead for 100% correctness improvement

**Why Not "Continuous Autonomous":**
- ❌ Orthogonal to phase gates (ambiguous state)
- ❌ Race condition risk with state manager (architecture brittleness)
- ❌ Orphan detection lacks semantic understanding (false positives)
- ❌ Evidence trails don't explain "why" files were deleted
- ❌ More complex to maintain as system speed increases

---

## Appendix: Specific Implementation Notes

### A. Phase-Boundary Cleanup Pseudo-Code
```python
def run_cleanup_for_phase_boundary(phase_num: int) -> CleanupResult:
    """Clean up artifacts from previous phase."""
    
    # Phase 1 → 2: Clean Phase 1 temp files
    temp_patterns = [
        "cortex-brain/temp/phase-1-*",
        "cortex-brain/cache/phase-1-*",
        ".pytest_cache",
        "htmlcov",
    ]
    
    deleted_files = []
    for pattern in temp_patterns:
        for file_path in glob(pattern):
            if not is_protected(file_path):
                file_path.unlink()
                deleted_files.append(str(file_path))
    
    # Generate evidence bundle
    evidence = {
        "phase": phase_num,
        "files_deleted": deleted_files,
        "timestamp": now(),
        "integrity_check": hash(deleted_files)
    }
    
    return CleanupResult(
        status="success",
        files_deleted=len(deleted_files),
        evidence_bundle=evidence
    )
```

### B. Intent Registry Schema
```yaml
version: '1.0'
schema_url: cortex-brain/schemas/file-intent-registry.json

files:
  - path: cortex-brain/documents/archives/
    intent: keep
    reason: Historical reference
    
  - path: cortex-brain/documents/old-analysis-2025/
    intent: optional
    reason: Knowledge migrated to tier3
    suggested_cleanup: true
    approval_required: true
```

### C. Daemon Configuration
```yaml
# cortex-brain/manifests/housekeeping/infra-daemon.yaml

daemon:
  name: Infrastructure Cleanup Daemon
  description: Autonomous cleanup of build artifacts
  schedule: hourly
  enabled: true
  
safety:
  protected_patterns:
    - "cortex-brain/database/*"
    - "cortex-brain/tier0/*"
    - ".env*"
    - ".secrets*"
  
patterns:
    - "__pycache__/"
    - ".pytest_cache/"
    - "*.egg-info/"
    - "htmlcov/"
    - ".venv/lib/python3.*/site-packages/*.dist-info/"

logging:
  audit_category: INFRASTRUCTURE
  level: INFO
  batch_threshold: 100  # Log every 100 deletions
```

---

**End of Analysis Document**

*This recommendation prioritizes correctness and auditability over raw speed. The 5% time overhead is a small price for eliminating race conditions, false positives, and ambiguous state management.*

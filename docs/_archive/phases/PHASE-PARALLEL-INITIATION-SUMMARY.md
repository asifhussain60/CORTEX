# PHASE-02-CODEBASE-COHERENCE: Codebase Coherence & Import Foundation
**Initiation Summary - 2026-01-18**

**[PHASE PROMOTED & RENAMED]** From: PHASE-PARALLEL → To: PHASE-02-CODEBASE-COHERENCE (Position 2 in execution sequence)

## Executive Summary
PHASE-02-CODEBASE-COHERENCE is now a foundational phase that establishes critical import coherence and folder structure *before* all core architecture work. This strategic promotion ensures maximum downstream stability by validating coherent imports early, reducing technical debt propagation, and improving maintainability at the foundation level.

**Phase Dependency Chain (New Sequence):**
- ✅ **PHASE-01**: Governance Foundation (completed)
- 🚀 **PHASE-02-CODEBASE-COHERENCE**: Import Foundation (current - NOT_STARTED)
- ✅ **PHASE-03-CORE-ARCHITECTURE**: Orchestrator Core (blocks on this phase)
- ✅ **PHASE-04-SAFETY-RELIABILITY**: Safety & Reliability (downstream)
- ✅ **PHASE-05-PRODUCTION-HARDENING**: Production Hardening (downstream)
- ✅ **PHASE-06-BRITTLENESS**: Brittleness Fixes (downstream)
- ✅ **PHASE-07-ECOSYSTEM**: Orchestrator Plugins (downstream)

---

## Phase Specification (from cortex-master.yaml)

### Metadata
```yaml
id: PHASE-02-CODEBASE-COHERENCE
status: NOT_STARTED
locked: false
priority: P0
blocking: true
requires: PHASE-01
must_complete_before: PHASE-03-CORE-ARCHITECTURE
estimated_hours: 35
```

### Strategic Rationale
**Why Promote to Position 2?**
1. **Highest-Risk Foundation**: Import coherence failures cascade through entire system
2. **Early Validation**: Establish clean codebase foundation before architecture complexity multiplies
3. **Unblock Parallel Velocity**: All downstream phases execute with confidence on stable imports
4. **Preventive Over Reactive**: Fix import risks in Week 1, not Week 4-5
5. **Governance Alignment**: Directly supports CORE-004 (Organization) and CORE-028 (Portable Paths)

### Acceptance Criteria (3 ACs)

#### AC-AR-010-01: Nested Folder Structure Planning & Design
- **Status**: NOT_STARTED
- **Description**: Design comprehensive nested folder structure; Document organization rationale; Create migration plan
- **Success Criteria**:
  - Structure designed
  - Rationale documented
  - Plan comprehensive
- **Testing**: 5 unit tests + 2 integration tests expected
- **Dependencies**: AR-010 (Architecture Decision)

#### AC-AR-010-02: Automated Folder Migration Script
- **Status**: NOT_STARTED
- **Description**: Create automated migration script; Verify file integrity; Generate migration report
- **Success Criteria**:
  - Script works reliably
  - Integrity verified
  - Report generated
- **Testing**: 10 unit tests + 4 integration tests expected

#### AC-AR-010-03: Import Path Update & Validation
- **Status**: NOT_STARTED
- **Description**: Update all import paths after migration; Validate no broken imports; Run full test suite
- **Success Criteria**:
  - All imports updated
  - No broken imports
  - Tests pass 100%
- **Testing**: 8 unit tests + 6 integration tests expected

---

## Current Status Analysis

### Phase Readiness: ✅ READY TO START
- ✅ Blocker PHASE-01 is COMPLETED and LOCKED
- ✅ Phase specification loaded from cortex-master.yaml phases: section
- ✅ All 3 ACs defined with success criteria
- ✅ Testing expectations documented
- ✅ Governance compliance framework ready

### Governance Alignment
This phase aligns with:
- **CORE-001**: Single Source of Truth (phase spec in phases: section)
- **CORE-004**: Codebase Organization (primary focus)
- **CORE-028**: Portable paths (AC-AR-010-03 requirement)
- **AR-010**: Nested Folder Organization (architecture decision)

---

## Implementation Roadmap

### Phase 1: Folder Structure Design (AC-AR-010-01)
1. Analyze current CORTEX codebase structure
2. Design comprehensive nested folder hierarchy
3. Document organization rationale and benefits
4. Create detailed migration plan with risk assessment
5. Get governance approval
6. Implement comprehensive unit + integration tests

### Phase 2: Migration Automation (AC-AR-010-02)
1. Create automated migration script with safety checks
2. Implement file integrity verification (checksums/hashing)
3. Add dry-run capability for validation
4. Generate migration report with before/after comparison
5. Test on staging environment
6. Implement comprehensive testing suite

### Phase 3: Import Path Updates (AC-AR-010-03)
1. Identify all import statements affected by migration
2. Create automated import path updater
3. Validate all imports resolve correctly
4. Run full test suite to catch any broken imports
5. Verify no runtime path resolution issues
6. Add comprehensive integration tests

---

## Success Metrics
- **All 3 ACs**: NOT_STARTED → COMPLETED
- **Test Pass Rate**: 100% (35 tests expected)
- **Code Quality**: Governance compliance across all CORE rules
- **No Regressions**: Existing tests continue to pass

---

## Timeline & Sequencing
- **Total Estimated Hours**: ~35 hours
- **Suggested Duration**: 5-7 days
- **Blocker**: Must complete before PHASE-03-CORE-ARCHITECTURE starts
- **Priority Signal**: P0 (Foundational - highest priority for resource allocation)

---

## Next Steps
1. ✅ Load phase spec from cortex-master.yaml phases: section ✓
2. 📋 Begin AC-AR-010-01: Folder Structure Planning & Design
3. ✅ Follow new SSOT workflow (edit cortex-master.yaml phases: section only)
4. 🧪 Implement tests first (TDD: RED → GREEN → REFACTOR)
5. ✅ Maintain governance compliance (CORE rules)
6. ✅ Lock phase when all 3 ACs complete

---

## Key Advantages of Nested Folder Structure
1. **Organization**: Logical grouping of related functionality
2. **Maintainability**: Easier to navigate and understand codebase
3. **Scalability**: Clear structure supports growth
4. **Import Clarity**: Well-defined import paths reduce confusion
5. **Testing**: Modular structure simplifies unit testing

---

**Initiated**: 2026-01-18 (Promoted & Prioritized)
**Initiated By**: cortex-builder (Strategic Phase Prioritization)
**Authority**: cortex-builder.prompt.md (SSOT workflow) + Strategic Value Analysis
**Tracking**: cortex-master.yaml phase_tracker section (PHASE-02-CODEBASE-COHERENCE)

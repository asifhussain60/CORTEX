# CORTEX Implementation Plan: Phases 03-05 & Beyond (71 AC-IDs)

**Date**: 2026-01-18  
**Plan Status**: ✅ READY FOR EXECUTION  
**Total AC-IDs**: 71 across 9 phases  
**Estimated Duration**: 5-6 weeks  
**Source of Truth**: `_workspaces/roadmap/cortex-master.yaml` (Consolidated SSOT)

---

## 🎯 Overview

This document outlines the comprehensive implementation plan for the next 71 AC-IDs across 9 critical phases. All phase specifications have been consolidated into `cortex-master.yaml` following the Single Source of Truth (SSOT) pattern documented in `cortex-builder.prompt.md`.

### Key Principle: Single Source of Truth
- ✅ **All phase details in ONE place**: `cortex-master.yaml` → `phases:` section
- ✅ **Phase YAML files**: Archived reference only (read-only)
- ✅ **Validator**: Prevents sync drift automatically
- ✅ **Pre-commit hook**: Enforces validation before commit

---

## 📊 Phase Roadmap

```
┌─────────────────────────────────────────────────────────────┐
│ WEEK 1: Foundation (42 ACs)                                │
├─────────────────────────────────────────────────────────────┤
│ PHASE-03: Safety & Observability (6 ACs)                   │
│ PHASE-PARALLEL: Folder Migration (3 ACs) ⬜ PARALLEL      │
│ PHASE-04: Production Hardening (12 ACs)                    │
│ PHASE-05: Brittleness Fixes (17 ACs)                       │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ WEEK 2: Advanced Features (12 ACs)                         │
├─────────────────────────────────────────────────────────────┤
│ PHASE-REMEDIATION-07: MCP Tool Exposure (3 ACs)            │
│ PHASE-21: Intelligent Knowledge Protocol (8 ACs)           │
│ PHASE-22: MCP Protocol Compliance (8 ACs)                  │
└─────────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│ WEEK 3: Production Ready (14 ACs)                          │
├─────────────────────────────────────────────────────────────┤
│ PHASE-23: Complexity-Aware Confirmation (4 ACs)            │
│ PHASE-DEPLOYMENT: Universal Deployment (10 ACs)           │
└─────────────────────────────────────────────────────────────┘

Total: 71 ACs in 9 phases → Production Ready
```

---

## 📋 Phase Details & Execution Plan

### PHASE-03: Safety, Reliability & Observability (6 ACs)

**Status**: NOT_STARTED  
**Requires**: PHASE-02 ✅ (LOCKED & COMPLETE)  
**Blocks**: PHASE-04  
**Estimated Hours**: 28 + 6 (buffer)  
**Test Coverage**: 57 unit tests + 24 integration tests = 81 tests

#### AC-IDs to Implement

| AC-ID | Title | Hours | Tests | Description |
|-------|-------|-------|-------|-------------|
| AC-NFR-002-01 | Graceful Degradation Framework | 4 | 17 | Handle component failures gracefully |
| AC-NFR-002-02 | Automatic Retry with Exponential Backoff | 3 | 14 | Retry handler with backoff strategies |
| AC-NFR-002-03 | Circuit Breaker Pattern | 4 | 20 | Implement circuit breaker (Closed/Open/Half-Open) |
| AC-NFR-004-01 | OpenTelemetry Metrics Integration | 5 | 17 | Production metrics export |
| AC-NFR-004-02 | Real-Time Progress Dashboard | 4 | 14 | Live metrics visualization |
| AC-NFR-004-03 | Alert Management & Thresholds | 3 | 16 | Alerting system with configurable triggers |

**Day-by-Day Breakdown**:
- **Day 1**: AC-NFR-002-01 (Graceful Degradation)
- **Day 2**: AC-NFR-002-02 & AC-NFR-002-03 (Retry & Circuit Breaker)
- **Day 3**: AC-NFR-004-01 (OpenTelemetry Integration)
- **Day 4**: AC-NFR-004-02 (Dashboard Service)
- **Day 5**: AC-NFR-004-03 (Alert Manager) + Integration testing

**Test Strategy**:
- Unit tests: Focus on individual components
- Integration tests: Focus on cross-component interactions
- End-to-end: Verify observable behavior

**Success Criteria**:
- ✅ All 6 AC-IDs implemented
- ✅ 81/81 tests passing (100%)
- ✅ Zero test regressions
- ✅ Governance compliance verified
- ✅ Ready to block on PHASE-04

---

### PHASE-04: Production Hardening & Security (12 ACs)

**Status**: NOT_STARTED  
**Requires**: PHASE-03 (must complete)  
**Blocks**: PHASE-05  
**Estimated Hours**: 32 + 7 (buffer)  
**Test Coverage**: 117 unit tests + 38 integration tests = 155 tests

#### AC-ID Groups

**Security Hardening (3 ACs)**:
| AC-ID | Title | Focus |
|-------|-------|-------|
| AC-NFR-003-01 | Security Hardening Framework | Input validation, output encoding, OWASP Top 10 |
| AC-NFR-003-02 | Secret Detection & Redaction | Credential leak prevention |
| AC-NFR-003-03 | Credential Protection | Secure storage, encryption, key rotation |

**Coherence Validation (4 ACs)**:
| AC-ID | Title | Focus |
|-------|-------|-------|
| AC-COHERENCE-001 | Cross-File Import Validation | Detect circular deps, ensure consistency |
| AC-COHERENCE-002 | Type Consistency Across Modules | Protocol compliance, interface alignment |
| AC-COHERENCE-003 | State Consistency Verification | Invariant maintenance, anomaly detection |
| AC-COHERENCE-004 | Configuration Coherence | Config validation, conflict detection |

**Explainability & Audit (5 ACs)**:
| AC-ID | Title | Focus |
|-------|-------|-------|
| AC-EXPLAIN-001 | Response Coherence Logging | Decision trace chains |
| AC-EXPLAIN-002 | Context Awareness | Context inclusion, confusion prevention |
| AC-EXPLAIN-003 | Output Consistency Checks | Coherence validation before output |
| AC-EXPLAIN-004 | Coherence Failure Fallbacks | Graceful degradation on check failure |
| AC-EXPLAIN-005 | Validation Test Suite | Comprehensive edge case coverage |

**Day-by-Day Breakdown**:
- **Day 1**: AC-NFR-003-01 (Security Framework)
- **Day 2**: AC-NFR-003-02 & AC-NFR-003-03 (Secrets)
- **Day 3**: AC-COHERENCE-001 through AC-COHERENCE-004
- **Day 4**: AC-EXPLAIN-001 through AC-EXPLAIN-003
- **Day 5**: AC-EXPLAIN-004 & AC-EXPLAIN-005 + Integration

**Success Criteria**:
- ✅ All 12 AC-IDs implemented
- ✅ 155/155 tests passing
- ✅ No security vulnerabilities
- ✅ Coherence validated across all modules
- ✅ Ready for PHASE-05

---

### PHASE-PARALLEL: Folder Structure Migration (3 ACs)

**Status**: NOT_STARTED  
**Requires**: PHASE-01 ✅  
**Must Complete Before**: PHASE-05  
**Can Run In Parallel With**: PHASE-02, PHASE-03, PHASE-04  
**Estimated Hours**: 16 + 3 (buffer)  
**Test Coverage**: 23 unit tests + 12 integration tests = 35 tests

#### AC-IDs

| AC-ID | Title | Hours | Tests | Deliverables |
|-------|-------|-------|-------|--------------|
| AC-AR-010-01 | Folder Structure Planning | 2 | 5+2 | Design doc + rationale + migration plan |
| AC-AR-010-02 | Automated Migration Script | 6 | 10+4 | Migration script + integrity checks |
| AC-AR-010-03 | Import Path Update & Validation | 5 | 8+6 | Updated imports + validation suite |

**Execution Strategy**:
- **Can start**: After PHASE-01 completion
- **Must finish**: Before PHASE-05 starts
- **Non-blocking**: Won't delay PHASE-04
- **Impact**: Affects all subsequent phases

**Success Criteria**:
- ✅ New folder structure implemented
- ✅ All files migrated successfully
- ✅ All imports updated
- ✅ 35/35 tests passing
- ✅ No broken imports in codebase

---

### PHASE-05: Brittleness Fixes & Stabilization (17 ACs)

**Status**: NOT_STARTED  
**Requires**: PHASE-04 + PHASE-PARALLEL (both must complete)  
**Blocks**: None (foundation complete)  
**Estimated Hours**: 36 + 8 (buffer)  
**Test Coverage**: 167 unit tests + 65 integration tests = 232 tests

#### AC-ID Groups

**Maintainability (3 ACs)**:
| AC-ID | Focus | Tests |
|-------|-------|-------|
| AC-NFR-001-01 | Code audit & refactoring | 15+5 |
| AC-NFR-001-02 | Style & consistency enforcement | 10+3 |
| AC-NFR-001-03 | Type annotation coverage (100%) | 12+4 |

**Import Resolution (4 ACs)**:
| AC-ID | Focus | Tests |
|-------|-------|-------|
| AC-BRITTLE-001 | Import path resolution framework | 20+8 |
| AC-BRITTLE-002 | Portable path abstraction | 18+6 |
| AC-BRITTLE-003 | Windows path compatibility | 12+4 |
| AC-BRITTLE-004 | macOS path compatibility | 10+3 |

**Platform Compatibility (3 ACs)**:
| AC-ID | Focus | Tests |
|-------|-------|-------|
| AC-BRITTLE-005 | Linux path compatibility | 10+3 |
| AC-BRITTLE-006 | Test flakiness audit | 8+2 |
| AC-BRITTLE-007 | Test isolation & cleanup | 14+5 |

**Test Stabilization (7 ACs)**:
| AC-ID | Focus | Tests |
|-------|-------|-------|
| AC-BRITTLE-008 | Timing-dependent tests | 16+4 |
| AC-BRITTLE-009 | Database state management | 12+6 |
| AC-BRITTLE-010 | Mock & stub management | 10+3 |
| AC-BRITTLE-011 | Coverage gap analysis | 6+2 |
| AC-BRITTLE-012 | Smoke test suite | 8+8 |
| AC-BRITTLE-013 | Production readiness validation | 12+8 |
| AC-BRITTLE-014 | CI/CD pipeline stabilization | 8+4 |

**Week Breakdown**:
- **Days 1-2**: Maintainability (AC-NFR-001-01 through 03)
- **Days 3-4**: Import resolution (AC-BRITTLE-001 through 004)
- **Days 5-6**: Platform compatibility (AC-BRITTLE-005 through 007)
- **Days 7-10**: Test stabilization (AC-BRITTLE-008 through 014)
- **Days 11-12**: Comprehensive validation + lock

**Success Criteria**:
- ✅ All 17 AC-IDs implemented
- ✅ 232/232 tests passing (100%)
- ✅ Zero flaky tests
- ✅ Cross-platform verified (Windows/macOS/Linux)
- ✅ Type annotations 100% coverage
- ✅ Production readiness verified
- ✅ Phase-05 locked ✅

---

## 🚀 Advanced Phases (Beyond Foundation)

### PHASE-21: Intelligent Knowledge Protocol (8 ACs)

**After**: PHASE-20-TEMPLATE-CONTENT  
**Estimated**: 39 hours + 150 tests  
**Focus**: Unified knowledge access layer with intelligent routing

**Key AC-IDs**:
- AC-IKP-001-01/02: KnowledgeProvider Protocol
- AC-IKP-002-01/02: IntelligentKnowledgeRouter
- AC-IKP-003-01/02: Change Detection Service
- AC-IKP-004-01/02: Ingestion & Refinement
- AC-IKP-005-01: Unified Facade

---

### PHASE-22: MCP Protocol Compliance (8 ACs)

**After**: PHASE-21 or PHASE-02  
**Estimated**: 48 hours + 140 tests  
**Priority**: P0 (CRITICAL)  
**Focus**: Full Model Context Protocol compliance

**Key AC-IDs**:
- AC-MCP-COMPLIANCE-001: Full protocol implementation
- AC-MCP-COMPLIANCE-002: Tool standardization
- AC-MCP-COMPLIANCE-003/004: Registry & discovery
- AC-MCP-COMPLIANCE-005/006: Tool execution & errors
- AC-MCP-COMPLIANCE-007: Input validation
- AC-MCP-COMPLIANCE-008: Integration tests

---

### PHASE-23: Complexity-Aware Confirmation (4 ACs)

**After**: PHASE-22  
**Estimated**: 23 hours + 30 tests  
**Focus**: Intelligent confirmation gate with complexity analysis

**Key AC-IDs**:
- AC-CONF-001-01: Complexity assessment engine
- AC-CONF-002-01: Approval gate logic
- AC-CONF-003-01: Master orchestrator integration
- AC-CONF-004-01: Governance & audit rules

---

### PHASE-DEPLOYMENT: Universal Deployment (10 ACs)

**After**: PHASE-22  
**Estimated**: 80 hours + 117 tests  
**Priority**: P0 (CRITICAL)  
**Focus**: Production-ready deployment system

**Key AC-ID Groups**:
- Installation & Bootstrap (3 ACs)
- Multi-Repo Architecture (3 ACs)
- Upgrade & Monitoring (2 ACs)
- Production Readiness (2 ACs)

---

### PHASE-REMEDIATION-07: MCP Tool Exposure (3 ACs)

**After**: PHASE-REMEDIATION-06 ✅  
**Estimated**: 8 hours + 19 tests  
**Can Run**: In parallel with other phases  
**Focus**: Expose domain orchestrator operations as MCP tools

**Key AC-IDs**:
- AC-MCP-EXPOSURE-001: @mcp_tool decorator
- AC-MCP-EXPOSURE-002: Domain operations exposure (15+ methods)
- AC-MCP-EXPOSURE-003: /list-tools endpoint

---

## ✅ Implementation Checklist

### Pre-Implementation

- [ ] Read `cortex-builder.prompt.md` fully
- [ ] Review `cortex-master.yaml` phases section
- [ ] Ensure `scripts/validate_phase_sync.py` exists
- [ ] Pre-commit hook installed: `.git/hooks/pre-commit`
- [ ] Phase files archived: `_workspaces/roadmap/_archives/phase-yamls-v1/`

### For Each Phase

- [ ] Load phase details from `cortex-master.yaml` → `phases.PHASE-XX`
- [ ] All AC-ID specs in ONE place (no file splitting)
- [ ] Implement AC-IDs following TDD pattern
- [ ] Run tests: `pytest tests/` (expect 100% pass)
- [ ] Validate sync: `python3 scripts/validate_phase_sync.py`
- [ ] Commit with: `git commit -m "phase-XX: AC-XXX-XX-01 COMPLETED"`
- [ ] Pre-commit hook validates automatically
- [ ] When complete: `locked: true` → phase lock
- [ ] Commit final lock: `git commit -m "phase-XX: COMPLETED - all XX ACs verified"`

### Testing Requirements

For each AC-ID:
1. **Unit tests** (individual component testing)
2. **Integration tests** (cross-component interactions)
3. **Governance compliance** (CORE-008 through CORE-028)
4. **Regression testing** (verify no breakage)

**All tests pass** before phase lock.

---

## 🔧 Technical Standards

### Governance Compliance (REQUIRED)

- ✅ **CORE-008**: TDD pattern (tests first, 100% pass)
- ✅ **CORE-011**: Type hints on all functions
- ✅ **CORE-012**: Google-style docstrings
- ✅ **CORE-013**: Specific exception handling
- ✅ **CORE-026**: Git checkpoints at phase completion
- ✅ **CORE-028**: Portable paths (`Path(__file__).parent`)
- ✅ **CORE-024**: Audit logging for all changes

### File Organization

- **Source code**: `src/`, `cortex-brain/tierX/`
- **Tests**: `tests/unit/`, `tests/integration/`
- **Utilities**: `src/mcp/utilities/`
- **Analysis tools**: `src/mcp/tools/analysis/`
- **Documentation**: `docs/` or `_workspaces/roadmap/reports/`

### Naming Conventions

- **AC-ID Format**: `AC-DOMAIN-NNN-NN` (e.g., `AC-NFR-002-01`)
- **Module Names**: kebab-case, <25 characters
- **Functions**: snake_case, descriptive
- **Classes**: PascalCase, descriptive

---

## 📈 Progress Tracking

### Current State
- **Locked Phases**: 13 (PHASE-01 through PHASE-13)
- **Completed ACs**: 125
- **Completion %**: 63.8%

### After Implementation
- **All Phases**: 22
- **Completed ACs**: 196
- **Completion %**: 100%
- **Production Ready**: ✅ YES

### Velocity Metrics
- **Target**: 5-6 weeks for all 9 phases
- **Buffer**: 20% contingency
- **Actual**: Track weekly

---

## 🚨 Risk Mitigation

### Known Risks

| Risk | Probability | Severity | Mitigation |
|------|-------------|----------|-----------|
| Import path issues across platforms | HIGH | HIGH | Early focus on PHASE-PARALLEL + PHASE-05 |
| Test flakiness delays phases | MEDIUM | MEDIUM | Dedicated flakiness AC (AC-BRITTLE-006) |
| Sync drift in cortex-master.yaml | LOW | HIGH | Validator + pre-commit hook |
| Governance rule violations | LOW | MEDIUM | Strict enforcement mode |

### Contingency Plans

1. **If sync drift occurs**: Run `python3 scripts/validate_phase_sync.py --fix`
2. **If tests fail**: Review governance checklist (CORE rules)
3. **If phase blocks**: Skip to parallel phase (see roadmap)
4. **If critical issue**: Rollback: `git checkout cortex-master.yaml`

---

## 📞 Support & Questions

### Common Issues

**Q: Where do I find phase details?**  
A: `_workspaces/roadmap/cortex-master.yaml` → `phases.PHASE-XX` section (ALL details in one place)

**Q: How do I validate my changes?**  
A: `python3 scripts/validate_phase_sync.py` (runs automatically on commit)

**Q: How do I mark an AC-ID complete?**  
A: Update `status: COMPLETED` in cortex-master.yaml → commit with pre-commit hook validation

**Q: Can I run phases in parallel?**  
A: Yes! PHASE-PARALLEL can run with PHASE-02/03/04, but must finish before PHASE-05

---

## 🎓 Learning Resources

- **Single Source of Truth**: `cortex-builder.prompt.md` (sections on SSOT)
- **Validator**: `scripts/validate_phase_sync.py` (auto-fixes, prevention)
- **Governance**: `cortex-brain/tier0/governance/core-rules.yaml`
- **Phase YAML Archive**: `_workspaces/roadmap/_archives/phase-yamls-v1/` (read-only reference)

---

## ✨ Success Definition

✅ **Implementation Complete When**:

1. All 71 AC-IDs implemented
2. All 316+ tests passing (100%)
3. cortex-master.yaml in sync
4. All 9 phases locked
5. Zero governance violations
6. Production readiness verified
7. Deployment ready

**Expected Timeline**: 5-6 weeks  
**Current Status**: ✅ Ready to start

---

**Next Step**: Start with PHASE-03 (Safety & Observability)  
Follow `cortex-builder.prompt.md` workflow for each AC-ID.

# 🚀 CORTEX Implementation: Consolidated Roadmap (71 AC-IDs)

**Effective Date**: 2026-01-18  
**Status**: ✅ READY FOR EXECUTION  
**Total Pending**: 71 AC-IDs across 9 phases  
**Execution Model**: Single Source of Truth (SSOT) in `cortex-master.yaml`

---

## 📊 Executive Summary

This document provides a consolidated view of the next 71 AC-IDs to implement across 9 critical phases. All phase specifications have been **consolidated into `cortex-master.yaml`** following the SSOT pattern from `cortex-builder.prompt.md`.

### Key Changes (From Previous Model)
- ✅ **OLD**: Separate phase YAML files (27 files) + cortex-master.yaml splits
- ✅ **NEW**: Single `cortex-master.yaml` → `phases:` section (all specs in one place)
- ✅ **Benefit**: Eliminated 2-source-of-truth sync issues
- ✅ **Prevention**: Validator auto-prevents drift; pre-commit hook auto-validates

---

## 🎯 Implementation Roadmap (6-Week Timeline)

```
WEEK 1
├─ PHASE-03: Safety & Observability (6 ACs) ..................... 28 hrs
├─ PHASE-PARALLEL: Folder Migration (3 ACs) [⬜ PARALLEL] ....... 16 hrs
├─ PHASE-04: Production Hardening (12 ACs) ..................... 32 hrs
└─ PHASE-05: Brittleness Fixes (17 ACs) ........................ 36 hrs
   SUBTOTAL: 38 ACs, 112 hours

WEEK 2
├─ PHASE-21: Intelligent Knowledge (8 ACs) ..................... 39 hrs
├─ PHASE-22: MCP Compliance (8 ACs) [P0 CRITICAL] .............. 48 hrs
├─ PHASE-23: Complexity Gate (4 ACs) ........................... 23 hrs
└─ PHASE-REMEDIATION-07: MCP Tools (3 ACs) [⬜ PARALLEL] ........ 8 hrs
   SUBTOTAL: 23 ACs, 118 hours

WEEK 3+
└─ PHASE-DEPLOYMENT: Universal Deploy (10 ACs) [P0] ............ 80 hrs
   SUBTOTAL: 10 ACs, 80 hours

TOTAL: 71 ACs, 310+ hours (with contingency)
Timeline: 5-6 weeks at standard velocity
```

---

## 📋 Phase-by-Phase Summary

### ✅ FOUNDATION PHASES (CRITICAL BLOCKERS)

#### PHASE-03: Safety, Reliability & Observability (6 ACs)
**Duration**: 5 days | **Tests**: 81 | **Hours**: 28  
**Status**: NOT_STARTED | **Requires**: PHASE-02 ✅ | **Blocks**: PHASE-04

| AC-ID | Title | Priority |
|-------|-------|----------|
| AC-NFR-002-01 | Graceful Degradation Framework | P0 |
| AC-NFR-002-02 | Automatic Retry + Exponential Backoff | P0 |
| AC-NFR-002-03 | Circuit Breaker Pattern | P0 |
| AC-NFR-004-01 | OpenTelemetry Metrics Integration | P0 |
| AC-NFR-004-02 | Real-Time Progress Dashboard | P0 |
| AC-NFR-004-03 | Alert Management & Thresholds | P0 |

**Key Deliverables**:
- GracefulDegradationHandler with FallbackStrategy
- RetryHandler with ExponentialBackoffPolicy
- CircuitBreaker (Closed/Open/Half-Open states)
- TelemetryProvider + MetricsExporter (OTEL)
- DashboardService + ProgressAggregator
- AlertManager + ThresholdMonitor

**Success Criteria**:
- ✅ 81/81 tests passing
- ✅ All infrastructure components stable
- ✅ PHASE-04 unblocked

---

#### PHASE-04: Production Hardening & Security (12 ACs)
**Duration**: 8 days | **Tests**: 155 | **Hours**: 32  
**Status**: NOT_STARTED | **Requires**: PHASE-03 | **Blocks**: PHASE-05

| Category | AC-IDs | Count |
|----------|--------|-------|
| Security | AC-NFR-003-01/02/03 | 3 |
| Coherence | AC-COHERENCE-001/002/003/004 | 4 |
| Explainability | AC-EXPLAIN-001/002/003/004/005 | 5 |

**Key Deliverables**:
- SecurityHardeningFramework (OWASP Top 10)
- SecretDetectionEngine + RedactionSystem
- CredentialProtectionVault (encryption, rotation)
- ImportCoherenceValidator (circular deps, consistency)
- TypeConsistencyChecker (across modules)
- StateConsistencyValidator (invariants)
- ConfigurationCoherenceValidator (conflicts)
- ResponseCoherenceLogger (decision traces)
- ContextAwarenessEngine (context inclusion)
- ConsistencyCheckValidator (pre-output checks)
- FallbackMechanisms (coherence failures)
- ComprehensiveTestSuite (edge cases)

**Success Criteria**:
- ✅ 155/155 tests passing
- ✅ All security hardening complete
- ✅ Cross-module coherence validated
- ✅ PHASE-05 unblocked

---

#### PHASE-05: Brittleness Fixes & Stabilization (17 ACs)
**Duration**: 12 days | **Tests**: 232 | **Hours**: 36  
**Status**: NOT_STARTED | **Requires**: PHASE-04 + PHASE-PARALLEL | **Blocks**: None

| Category | AC-IDs | Count |
|----------|--------|-------|
| Maintainability | AC-NFR-001-01/02/03 | 3 |
| Import Resolution | AC-BRITTLE-001/002/003/004 | 4 |
| Platform Compat | AC-BRITTLE-005/006/007 | 3 |
| Test Stabilization | AC-BRITTLE-008→014 | 7 |

**Key Deliverables**:
- CodeMaintainabilityAudit + RefactoringPlan
- CodeStyleEnforcer (Black, isort, flake8)
- TypeAnnotationValidator (100% coverage + mypy)
- ImportPathResolutionFramework
- PortablePathAbstractionLayer (pathlib)
- WindowsPathCompatibility (drive letters, UNC)
- macOSPathCompatibility (bundles, symlinks)
- LinuxPathCompatibility (containers)
- TestFlakynessAuditReport
- TestIsolationManager (fixtures, cleanup)
- TimingDependentTestFixer (async/await)
- DatabaseStateManager (transactions, rollback)
- MockStubFactory (centralized mocks)
- TestCoverageAnalyzer (gaps report)
- SmokeSuite (rapid feedback <30s)
- ProductionReadinessValidator
- CI/CDPipelineStabilizer

**Success Criteria**:
- ✅ 232/232 tests passing (100%)
- ✅ Zero flaky tests in CI
- ✅ Cross-platform verified (Win/macOS/Linux)
- ✅ Type annotations 100%
- ✅ Production ready ✅

---

#### PHASE-PARALLEL: Folder Structure Migration (3 ACs)
**Duration**: 3 days | **Tests**: 35 | **Hours**: 16  
**Status**: NOT_STARTED | **Requires**: PHASE-01 ✅ | **Must Complete**: Before PHASE-05  
**Execution**: ⬜ Can run parallel with PHASE-02/03/04 (non-blocking)

| AC-ID | Title | Hours | Tests |
|-------|-------|-------|-------|
| AC-AR-010-01 | Folder Structure Planning | 2 | 7 |
| AC-AR-010-02 | Migration Script | 6 | 14 |
| AC-AR-010-03 | Import Updates & Validation | 5 | 14 |

**Key Deliverables**:
- FolderStructureDesign (nested hierarchy)
- MigrationScript (automated file movement)
- ImportPathUpdateScript (all imports updated)
- MigrationValidationReport

**Success Criteria**:
- ✅ All files migrated successfully
- ✅ 35/35 tests passing
- ✅ No broken imports
- ✅ Complete before PHASE-05

---

### 🚀 ADVANCED PHASES (P1 FEATURES + CRITICAL INFRASTRUCTURE)

#### PHASE-21: Intelligent Knowledge Protocol (8 ACs)
**Estimated**: 39 hours + 150 tests  
**Requires**: PHASE-20-TEMPLATE-CONTENT ✅  
**Priority**: P1 | **Focus**: Unified knowledge access + intelligent routing

**AC-ID Groups**:
- AC-IKP-001-01/02: KnowledgeProvider Protocol (typing.Protocol)
- AC-IKP-002-01/02: IntelligentKnowledgeRouter (query-aware routing)
- AC-IKP-003-01/02: ChangeDetectionService (schema drift monitoring)
- AC-IKP-004-01/02: IngestionPipeline (extensible with plugins)
- AC-IKP-005-01: UnifiedKnowledgeServiceFacade (single entry point)

**Deliverables**:
- KnowledgeProviderProtocol (interface definition)
- IntelligentRouter (confidence scoring, aggregation)
- ChangeDetector (anomaly detection, alerts)
- IngestionEngine (extensible pipeline)
- RefinementEngine (entity extraction, dedup)
- UnifiedFacade (simplified client API)

---

#### PHASE-22: MCP Protocol Compliance (8 ACs)
**Estimated**: 48 hours + 140 tests  
**Requires**: PHASE-21 or PHASE-02 (minimum)  
**Priority**: P0 CRITICAL | **Focus**: Full MCP protocol implementation

**AC-ID Groups**:
- AC-MCP-COMPLIANCE-001: Protocol Full Implementation
- AC-MCP-COMPLIANCE-002: Tool Standardization
- AC-MCP-COMPLIANCE-003: Tool Registry
- AC-MCP-COMPLIANCE-004: Tool Discovery
- AC-MCP-COMPLIANCE-005: Tool Execution Framework
- AC-MCP-COMPLIANCE-006: Error Handling
- AC-MCP-COMPLIANCE-007: Input Validation
- AC-MCP-COMPLIANCE-008: Integration Tests

**Deliverables**:
- MCPProtocolImplementation (full spec compliance)
- ToolStandardization (naming, documentation)
- ToolRegistry (registration, versioning)
- ToolDiscoveryAPI (dynamic tool exposure)
- ToolExecutor (reliable execution, timeouts)
- ErrorHandler (MCP-compliant error codes)
- InputValidator (parameter validation)

**Impact**:
- MCP tool count: 16 → 32+ tools
- Tool discovery: Programmatic ✅
- Protocol compliance: 100% ✅

---

#### PHASE-23: Complexity-Aware Confirmation Gate (4 ACs)
**Estimated**: 23 hours + 30 tests  
**Requires**: PHASE-22  
**Priority**: P1 | **Focus**: Intelligent approval gate

**AC-ID Groups**:
- AC-CONF-001-01: Complexity Assessment Engine (5-level scale)
- AC-CONF-002-01: Approval Gate Logic (auto-approval matrix)
- AC-CONF-003-01: Master Orchestrator Integration (Stage 2.5)
- AC-CONF-004-01: Governance & Audit (5 rules + trails)

**Deliverables**:
- ComplexityAssessmentEngine (aggregate LENS confidence)
- ApprovalGate (confidence-based decisions)
- ConversationProtocolIntegration (Stage 2.5 insertion)
- GovernanceRules (5 audit-enabled rules)

---

#### PHASE-DEPLOYMENT: Universal Deployment System (10 ACs)
**Estimated**: 80 hours + 117 tests  
**Requires**: PHASE-22  
**Priority**: P0 CRITICAL | **Focus**: Production deployment

**AC-ID Groups**:
- Installation & Bootstrap (3 ACs): Config mgmt, Blue-Green, MCP registration
- Multi-Repo Architecture (3 ACs): CI/CD, Rollback, Context switching
- Upgrade & Monitoring (2 ACs): Production monitoring, Health checks
- Production Readiness (2 ACs): Documentation, Training materials

**Deliverables**:
- EnvironmentConfigurations (dev/staging/prod)
- BlueGreenDeployment (zero-downtime updates)
- MCPToolRegistration (client-side)
- CI/CDPipeline (automated, parallel)
- RollbackMechanism (point-in-time recovery)
- ContextSwitcher (multi-repo isolation)
- ProductionMonitoring (alerting, dashboards)
- HealthChecks (readiness probes, LB integration)
- ReleaseNotes (generated)
- TrainingMaterials (user onboarding)

---

#### PHASE-REMEDIATION-07: MCP Tool Exposure Gap (3 ACs)
**Estimated**: 8 hours + 19 tests  
**Requires**: PHASE-REMEDIATION-06 ✅  
**Priority**: P1 | **Parallel Capable**: Yes ⬜

**AC-IDs**:
- AC-MCP-EXPOSURE-001: @mcp_tool decorator (knowledge operations)
- AC-MCP-EXPOSURE-002: Domain orchestrator tools (15+ methods)
- AC-MCP-EXPOSURE-003: /list-tools endpoint (discovery)

**Impact**:
- MCP tools: +16 additional tools exposed
- Discovery: Programmatic tool listing enabled
- Domain operations: All available as MCP tools

---

## 🔧 Consolidated Phase Structure in cortex-master.yaml

All phase details now in **single location**:

```yaml
phases:
  phase_03:
    id: PHASE-03
    title: Safety, Reliability & Observability
    description: "..."
    status: NOT_STARTED
    locked: false
    requires: PHASE-02
    blocks: PHASE-04
    ac_ids:
      AC-NFR-002-01:
        title: "..."
        description: "..."
        status: NOT_STARTED
        testing:
          unit_tests_expected: 12
          integration_tests_expected: 5
        success_criteria:
          - "..."
          - "..."
      AC-NFR-002-02:
        ...
```

**Benefits**:
- ✅ No file splits (single source)
- ✅ Validator prevents drift
- ✅ Pre-commit hook auto-validates
- ✅ Atomic updates (one file to edit)
- ✅ Git history cleaner

---

## ✅ Workflow for Each AC-ID

### Standard TDD Pattern (per cortex-builder.prompt.md)

1. **Load Phase Context**
   ```bash
   grep -A 20 "PHASE-03:" _workspaces/roadmap/cortex-master.yaml | head -50
   ```

2. **For Each AC-ID**:
   ```bash
   # 1. Read specs from cortex-master.yaml
   # 2. Write tests first (TDD pattern)
   # 3. Implement code until tests pass
   # 4. Update status: COMPLETED
   # 5. Validate: python3 scripts/validate_phase_sync.py
   # 6. Commit: git commit -m "phase-XX: AC-YYY-YY-ZZ COMPLETED"
   ```

3. **Pre-commit Hook Validation** (automatic)
   - Checks AC-ID naming (AC-DOMAIN-NNN-NN)
   - Validates governance rules
   - Prevents sync drift
   - Runs validator

4. **Phase Lock** (when all ACs complete)
   ```yaml
   phase_03:
     status: COMPLETED
     locked: true
   ```

---

## 📊 Metrics & Tracking

### Current State (2026-01-18)
- **Completed Phases**: 13 (PHASE-01 through PHASE-13)
- **Completed AC-IDs**: 125
- **Total AC-IDs**: 196 (after this plan)
- **Completion %**: 63.8%

### After Implementation (Target: 2026-02-28)
- **Completed Phases**: 22
- **Completed AC-IDs**: 196 (100%)
- **Total Tests**: 316+
- **Production Ready**: ✅ YES
- **Completion %**: 100%

### Velocity Target
- **Weeks**: 6 (with contingency)
- **ACs/Week**: ~12 ACs
- **Tests/Week**: ~50 tests
- **Hours/Day**: 5-6 effective hours

---

## 🛡️ Governance & Quality Assurance

### Mandatory Compliance (CORE-008 through CORE-028)

**For ALL code**:
- ✅ **CORE-008**: TDD methodology (tests first, 100% pass)
- ✅ **CORE-011**: Type hints on ALL functions
- ✅ **CORE-012**: Google-style docstrings
- ✅ **CORE-013**: Specific exception handling (no bare except)
- ✅ **CORE-026**: Git checkpoints at phase completion
- ✅ **CORE-028**: Portable paths (`Path(__file__).parent`)
- ✅ **CORE-024**: Audit logging for all changes

### Testing Requirements

| Test Type | Scope | Target |
|-----------|-------|--------|
| Unit Tests | Individual components | >80% coverage |
| Integration | Cross-component | All interfaces |
| End-to-End | Full workflows | Critical paths |
| Regression | No breakage | 100% pass rate |
| Smoke | Rapid feedback | <30s execution |

### Validation & Prevention

- **Validator**: `scripts/validate_phase_sync.py`
  - Prevents sync drift
  - Auto-fixes common issues
  - Checks AC-ID naming
  - Validates governance rules

- **Pre-commit Hook**: Automatic on commit
  - Runs validator
  - Checks governance
  - Prevents broken states
  - Blocks bad commits

---

## 🚨 Critical Path & Blockers

### Blocking Dependencies

```
PHASE-01 ✅ COMPLETED
   ↓
PHASE-02 ✅ COMPLETED
   ↓
PHASE-03 (6 ACs) ← START HERE
   ↓
PHASE-04 (12 ACs)
   ↓
PHASE-PARALLEL (3 ACs, can start after PHASE-01)
+
PHASE-05 (17 ACs) [requires PHASE-04 + PHASE-PARALLEL]
   ↓
PHASE-21 (8 ACs)
PHASE-22 (8 ACs) [P0, can start after PHASE-21 or PHASE-02]
   ↓
PHASE-23 (4 ACs) [requires PHASE-22]
   ↓
PHASE-DEPLOYMENT (10 ACs) [P0, requires PHASE-22]

PHASE-REMEDIATION-07 (3 ACs) ⬜ Can run parallel (non-blocking)
```

### Critical Path (Minimum)
1. PHASE-03 (5 days)
2. PHASE-04 (8 days)
3. PHASE-05 (12 days)
4. PHASE-21 (5 days)
5. PHASE-22 (6 days)
6. PHASE-23 (3 days)
7. PHASE-DEPLOYMENT (8 days)

**Total**: ~47 days (~6-7 weeks)  
**Parallel Opportunities**: PHASE-PARALLEL, PHASE-REMEDIATION-07

---

## 📞 Quick Reference

### Load Phase Details
```bash
# View PHASE-03 details
grep -A 200 "phase_03:" _workspaces/roadmap/cortex-master.yaml

# View specific AC-ID
grep "AC-NFR-002-01:" -A 10 _workspaces/roadmap/cortex-master.yaml
```

### Validation & Commit
```bash
# Pre-validation
python3 scripts/validate_phase_sync.py

# Run tests
pytest tests/ -k "phase_03" -v

# Commit per AC-ID
git commit -m "phase-03: AC-NFR-002-01 COMPLETED"
```

### Monitor Progress
```bash
# Check phase status
grep "phase_03:" -A 5 _workspaces/roadmap/cortex-master.yaml | grep -E "status|locked"

# Count completed ACs
grep "status: COMPLETED" _workspaces/roadmap/cortex-master.yaml | wc -l
```

---

## 📚 Resources

| Resource | Purpose | Location |
|----------|---------|----------|
| Phase Specs | Single source of truth | `cortex-master.yaml` → `phases:` section |
| Builder Prompt | Implementation workflow | `.github/prompts/cortex-builder.prompt.md` |
| Validator | Sync prevention | `scripts/validate_phase_sync.py` |
| Governance | Quality rules | `cortex_brain/tier0/governance/core-rules.yaml` |
| Detailed Plan | Full breakdown | `IMPLEMENTATION-PLAN-PHASES-03-05-AND-BEYOND.md` |
| Quick Start | Day-by-day guide | `QUICK-START-PHASE-03.md` |

---

## ✨ Success Metrics

### Definition of Done (Per Phase)

✅ **All AC-IDs implemented**  
✅ **All tests passing** (100% pass rate)  
✅ **Governance compliant** (CORE-008 through CORE-028)  
✅ **cortex-master.yaml in sync** (validator passes)  
✅ **Phase locked** (`locked: true`)  
✅ **Next phase unblocked** (ready to proceed)  

### Definition of Project Complete

✅ **All 71 AC-IDs implemented**  
✅ **316+ tests passing** (100% pass rate)  
✅ **All 9 phases locked** ✅  
✅ **Zero governance violations**  
✅ **Production ready** ✅  
✅ **Documentation complete**  
✅ **Deployment ready**  

---

## 🚀 Next Steps

**Immediate (Today)**:
1. ✅ Read this document completely
2. ✅ Review `cortex-builder.prompt.md`
3. ✅ Verify validator exists: `ls scripts/validate_phase_sync.py`
4. ✅ Verify pre-commit hook: `ls .git/hooks/pre-commit`

**Today/Tomorrow**:
1. ✅ Start PHASE-03 (Day 1: AC-NFR-002-01)
2. ✅ Follow `QUICK-START-PHASE-03.md`
3. ✅ Implement, test, validate, commit

**Expected Timeline**:
- Week 1: PHASE-03/04/05/PARALLEL (38 ACs)
- Week 2: PHASE-21/22/23/REMEDIATION-07 (23 ACs)
- Week 3+: PHASE-DEPLOYMENT (10 ACs)
- **Target**: 2026-02-28 (6 weeks)

---

**Status**: ✅ READY FOR EXECUTION  
**Confidence**: HIGH (all blockers cleared)  
**Quality**: PRODUCTION GRADE (governance enforced)  
**Timeline**: 6 weeks to completion

**Begin now with PHASE-03 → Follow cortex-builder.prompt.md workflow → Proceed to PHASE-04 when complete**

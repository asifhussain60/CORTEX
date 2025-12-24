# Orchestrator Extensibility Enhancement

**Feature Plan ID:** FEAT-CORTEX-EXT-001  
**Planning System:** 2.0  
**Complexity:** HIGH (Incremental Phasing Required)  
**Created:** 2025-12-10  
**Author:** CORTEX Planning System  
**Status:** 🟡 APPROVED - Ready for Execution

---

## 📋 Executive Summary

**Goal:** Enhance all CORTEX 3.0 orchestrators to achieve 4+/5⭐ extensibility ratings through systematic registry patterns, plugin architectures, and intelligent scope management.

**Current State:**
- ✅ Execution Orchestrator: 5⭐ (Full registry pattern)
- 🟡 Planning Orchestrator: 3⭐ (Hardcoded phases)
- 🔴 TDD Orchestrator: 2⭐ (Limited by design)
- 🟡 Scaffolding Orchestrator: 3⭐ (Missing pipeline pattern)
- ⚪ Others: Not rated

**Target State:** All 10 orchestrators rated 4+/5⭐ (average ≥4.0)

**Innovation:** AST-powered intelligent scope management to prevent context overflow in large C# monoliths while preserving architectural completeness.

---

## 🎯 Problem Statement

### Challenge 1: Extensibility Gaps
Current orchestrators lack systematic extensibility mechanisms:
- **Planning/Scaffolding:** Hardcoded phases/strategies limit customization
- **TDD:** No plugin system for quality gates or test frameworks
- **Others:** Varying levels of extensibility without consistent patterns

### Challenge 2: Context Overflow in Large Codebases
When analyzing large C# monoliths (50,000+ LOC), Copilot loses focus:
- **Symptom:** "Getting lost" during scope identification
- **Impact:** Misses critical dependencies, suggests incomplete solutions
- **Root Cause:** No semantic boundary detection, entire namespace loaded

**User Requirement:** "Intelligently limit scope (use AST?) but not restrict" - get as much scope as needed across all layers without context drift.

---

## 🏗️ Solution Architecture

### Core Components

#### 1. **Registry Pattern System** (Execution model)
**Purpose:** Enable runtime orchestrator/phase/strategy registration

**Implementation:**
- Phase Registry (Planning, Scaffolding)
- Orchestrator Registry (already exists in Execution)
- Strategy Registry (Scaffolding refactoring approaches)

#### 2. **Plugin Architecture** (TDD)
**Purpose:** Extensible quality gates and test frameworks

**Implementation:**
- Plugin interface definition
- Plugin discovery mechanism
- Lifecycle hooks (pre-test, post-test, coverage validation)

#### 3. **Intelligent Scope Management** (NEW)
**Purpose:** Prevent context overflow while maintaining architectural completeness

**Implementation:**
```
Scope Analyzer (Scaffolding)
├── AST Parser (Roslyn/Tree-sitter)
├── Dependency Tracer (DAG)
├── Coupling Calculator (HIGH/MEDIUM/LOW)
└── Boundary Detector (semantic limits)

Context Optimizer (Intelligence)
├── Token Counter
├── Relevance Ranker
└── Window Manager (80% target)
```

**Algorithm:** 4-Phase Scope Expansion
1. **Entry Point** (50 LOC): Requested method
2. **Layer 1** (200 LOC): Direct dependencies (coupling score ≥0.5)
3. **Layer 2** (400 LOC): Interfaces, validation, schema
4. **Boundary Detection**: STOP at async events, external APIs, context limit

**Coupling Scores:**
- HIGH (1.0): Direct method calls within same namespace
- MEDIUM (0.5): Interface implementations, shared DTOs
- LOW (0.1): Async events, external API calls

**Expected Benefit:** 80% reduction in context overflow, >0.9 relevance score

---

## ✅ Acceptance Criteria

### AC-1: Phase Registry System (Planning 3⭐→4⭐)
**User Story:** As a developer, I want to add custom planning phases without modifying core orchestrator code.

**Acceptance Tests:**
- [ ] Phase registry configuration file exists (`planning-phases.yaml`)
- [ ] `register_phase()` method implemented in Planning Orchestrator
- [ ] Custom phase loaded at runtime and executed in sequence
- [ ] Phase metadata (name, description, dependencies) validated
- [ ] Documentation shows example custom phase implementation

**Definition of Ready:**
- [ ] Planning Orchestrator source code analyzed
- [ ] Phase execution flow documented
- [ ] Registry interface designed (follows Execution model)

**Definition of Done:**
- [ ] Code implemented and unit tested (≥90% coverage)
- [ ] Integration test validates custom phase execution
- [ ] Documentation updated with extension guide
- [ ] No breaking changes to existing phase execution

---

### AC-2: TDD Methodology Extensions (TDD 2⭐→4⭐)
**User Story:** As a QA engineer, I want to add custom quality gates (performance tests, security scans) to TDD workflow.

**Acceptance Tests:**
- [ ] Plugin interface defined (`ITDDPlugin`)
- [ ] Plugin discovery mechanism implemented (scan `plugins/` directory)
- [ ] Lifecycle hooks functional (pre-test, post-test, coverage-validation)
- [ ] Example plugin implemented (performance threshold validation)
- [ ] Plugin execution logged and reportable

**Definition of Ready:**
- [ ] TDD Orchestrator plugin requirements gathered
- [ ] Execution Orchestrator plugin pattern reviewed
- [ ] Plugin lifecycle documented

**Definition of Done:**
- [ ] Plugin interface implemented with ≥3 lifecycle hooks
- [ ] Example plugin functional (performance or security)
- [ ] Plugin execution integrated in TDD workflow
- [ ] Documentation shows plugin development guide
- [ ] Zero impact on existing TDD tests (35/35 passing)

---

### AC-3: Scaffolding Pipeline Pattern (Scaffolding 3⭐→4+⭐)
**User Story:** As a developer, I want to add custom refactoring strategies (e.g., Strangler Fig, Feature Toggle) to scaffolding workflow.

**Acceptance Tests:**
- [ ] Strategy registry implemented (`scaffolding-strategies.yaml`)
- [ ] `register_strategy()` method functional
- [ ] Custom strategy loaded and executable
- [ ] Strategy metadata (approach, prerequisites, risks) validated
- [ ] Multiple strategies selectable per project

**Definition of Ready:**
- [ ] Scaffolding Orchestrator refactoring strategies analyzed
- [ ] Current strategy execution flow documented
- [ ] Strategy interface designed

**Definition of Done:**
- [ ] Strategy registry implemented with ≥3 built-in strategies
- [ ] Custom strategy registration tested
- [ ] Strategy selection UI/CLI functional
- [ ] Documentation includes strategy development guide
- [ ] Backward compatibility maintained (existing scaffolding works)

---

### AC-4: Extensibility Assessment (All ≥4⭐)
**User Story:** As a product owner, I want verification that all orchestrators meet 4+ star extensibility rating.

**Acceptance Tests:**
- [ ] Extensibility audit report generated
- [ ] All 10 orchestrators rated (score 1-5)
- [ ] Average rating ≥4.0
- [ ] No orchestrator rated <4 stars
- [ ] Audit methodology documented

**Definition of Ready:**
- [ ] Extensibility rating criteria defined (registry, plugin, configuration)
- [ ] Audit script designed
- [ ] Baseline ratings documented (current state)

**Definition of Done:**
- [ ] Audit script implemented (`scripts/audit_extensibility.py`)
- [ ] Report generated showing all ratings ≥4.0
- [ ] Report includes remediation recommendations (if any)
- [ ] Report published to `cortex-brain/documents/analysis/`

---

### AC-5: Documentation & Developer Guides
**User Story:** As a new developer, I want clear examples of extending each orchestrator.

**Acceptance Tests:**
- [ ] Extension guide created for Planning (phase registration)
- [ ] Extension guide created for TDD (plugin development)
- [ ] Extension guide created for Scaffolding (strategy registration)
- [ ] Code examples functional (copy-paste ready)
- [ ] Troubleshooting section included

**Definition of Ready:**
- [ ] Documentation template designed
- [ ] Example scenarios identified (3 per orchestrator)

**Definition of Done:**
- [ ] 3 extension guides published to `cortex-brain/documents/implementation-guides/`
- [ ] Code examples tested and validated
- [ ] Guides reviewed by 1 engineer (peer review)
- [ ] Guides linked from main README

---

### AC-6: Backward Compatibility
**User Story:** As an existing user, I want zero breaking changes to current orchestrator usage.

**Acceptance Tests:**
- [ ] All existing smoke tests pass (35/35)
- [ ] No changes to public method signatures
- [ ] Default behavior unchanged (extensibility opt-in)
- [ ] Migration guide created (if any API changes)

**Definition of Ready:**
- [ ] Current public API documented
- [ ] Smoke test suite reviewed (baseline)

**Definition of Done:**
- [ ] 35/35 smoke tests passing
- [ ] No breaking changes detected by compatibility scan
- [ ] Migration guide published (empty if no changes needed)
- [ ] Regression test suite expanded (coverage ≥current baseline)

---

### AC-7: Intelligent Scope Management (NEW)
**User Story:** As a developer working in large C# monoliths, I want Copilot to analyze manageable scope without losing architectural context.

**Acceptance Tests:**
- [ ] Scope analyzer integrated in Scaffolding Orchestrator
- [ ] AST parser functional (Roslyn for C#, Tree-sitter for others)
- [ ] Dependency tracer builds DAG with coupling scores
- [ ] Boundary detection stops at semantic limits (async, external APIs)
- [ ] Context optimizer targets 80% token window utilization
- [ ] Validated on small (5K LOC), medium (20K LOC), large (50K LOC) codebases

**Scope Expansion Algorithm:**
```
Entry Point (50 LOC)
  └─> Layer 1 (200 LOC): Direct dependencies (score ≥0.5)
       └─> Layer 2 (400 LOC): Interfaces, validation, schema
            └─> BOUNDARY: Stop at LOW coupling (<0.1), context limit
```

**Coupling Score Calculation:**
- **HIGH (1.0):** Direct method calls within same namespace
- **MEDIUM (0.5):** Interface implementations, shared DTOs
- **LOW (0.1):** Async events, message queues, external API calls

**Definition of Ready:**
- [ ] Roslyn API integration researched (C# AST parsing)
- [ ] Tree-sitter fallback designed (multi-language support)
- [ ] Dependency graph algorithm designed (DAG with scores)
- [ ] Integration point identified (Scaffolding + Intelligence orchestrators)

**Definition of Done:**
- [ ] Scope analyzer implemented (`scaffolding/scope_analyzer.py`, 400 LOC)
- [ ] Context optimizer implemented (`intelligence/context_optimizer.py`, 300 LOC)
- [ ] Coupling calculator utility (`shared/coupling_calculator.py`, 200 LOC)
- [ ] Algorithm tested on 3 codebase sizes (small/medium/large)
- [ ] Precision metrics: >0.9 relevance score, <10% false negatives
- [ ] Performance: <2s for 50K LOC codebase analysis
- [ ] Documentation: Algorithm explainer + tuning guide
- [ ] Integration: Scaffolding calls scope analyzer, Intelligence optimizes context

---

## 📅 Implementation Plan

### Phase 1: Foundation (Days 1-5)
**Focus:** Registry patterns + AST infrastructure

**Tasks:**
- [ ] Design phase registry interface (Planning, Scaffolding)
- [ ] Implement `register_phase()` methods
- [ ] Create `planning-phases.yaml` configuration
- [ ] **AST Integration:** Research Roslyn API, setup Tree-sitter parser
- [ ] **Scope Analyzer Skeleton:** Create `scope_analyzer.py` with parser interface
- [ ] Unit tests for registry logic (TDD: RED→GREEN→REFACTOR)
- [ ] Documentation: Phase registry guide

**Deliverables:**
- Phase registry functional in Planning/Scaffolding
- AST parser functional (C#, Python, JavaScript)
- Unit tests passing (≥90% coverage)

**DoD Gate:** Custom phase executable, AST parsing 50 LOC C# method

---

### Phase 2: Plugins + Scope Algorithm (Days 6-10)
**Focus:** TDD plugins + Intelligent scope algorithm

**Tasks:**
- [ ] Define `ITDDPlugin` interface
- [ ] Implement plugin discovery (scan `plugins/` directory)
- [ ] Create example plugin (performance threshold validator)
- [ ] Lifecycle hooks: pre-test, post-test, coverage-validation
- [ ] **Dependency Tracer:** Build DAG from AST with method call relationships
- [ ] **Coupling Calculator:** Implement scoring algorithm (HIGH/MEDIUM/LOW)
- [ ] **Scope Expansion:** 4-phase algorithm (Entry → L1 → L2 → Boundary)
- [ ] Integration tests (custom plugin + scope analyzer)

**Deliverables:**
- TDD plugin system functional
- Scope analyzer produces DAG with coupling scores
- Example plugin working (performance validation)
- Scope expansion tested on 5K LOC codebase

**DoD Gate:** Plugin executes in TDD workflow, scope analyzer returns 650 LOC for test case

---

### Phase 3: Remaining Orchestrators + Integration (Days 11-15)
**Focus:** Scaffolding strategy registry + Scope integration

**Tasks:**
- [ ] Implement `register_strategy()` in Scaffolding
- [ ] Create `scaffolding-strategies.yaml` with 3 built-in strategies
- [ ] Strategy selection CLI/UI
- [ ] **Context Optimizer:** Implement in Intelligence Orchestrator
- [ ] **Scope Integration:** Scaffolding calls scope_analyzer, Intelligence optimizes tokens
- [ ] **Window Manager:** Target 80% token utilization, rank by relevance
- [ ] Audit remaining 6 orchestrators (rate extensibility)
- [ ] Apply registry patterns where needed

**Deliverables:**
- Scaffolding strategy registry functional
- Context optimizer integrated with scope analyzer
- 6/10 orchestrators audited and rated
- Scope management working end-to-end (Scaffolding → Intelligence)

**DoD Gate:** Custom strategy executable, context optimizer reduces 50K LOC to 650 LOC with >0.9 relevance

---

### Phase 4: Testing + Documentation + Audit (Days 16-20)
**Focus:** Validation, documentation, extensibility audit

**Tasks:**
- [ ] Comprehensive testing (35/35 smoke tests + new tests)
- [ ] **C# Monolith Validation:** Test scope analyzer on real 50K+ LOC codebase
- [ ] **Precision Metrics:** Measure relevance score, false negative rate
- [ ] Extension guides (Planning, TDD, Scaffolding, Scope Management)
- [ ] Code examples (copy-paste ready)
- [ ] Extensibility audit script (`scripts/audit_extensibility.py`)
- [ ] Run audit, generate report (all ≥4.0 stars)
- [ ] Backward compatibility verification

**Deliverables:**
- 3 extension guides + scope management tuning guide
- Extensibility audit report (all 10 orchestrators ≥4⭐)
- 100% smoke tests passing
- C# monolith validation report (80% context reduction achieved)

**DoD Gate:** All tests passing, audit shows average ≥4.0, documentation complete

---

## 📊 Success Metrics

### Extensibility
- ✅ All 10 orchestrators rated 4+/5⭐
- ✅ Average rating ≥4.0
- ✅ Extension guides published (3 guides)
- ✅ Audit report validates compliance

### Intelligent Scope Management
- ✅ Context overflow reduced by ≥80% in large codebases
- ✅ Copilot relevance score >0.9 (semantic accuracy)
- ✅ Architectural completeness preserved (cross-layer dependencies included)
- ✅ Performance: <2s analysis for 50K LOC
- ✅ False negative rate <10% (critical dependencies not missed)

### Quality
- ✅ Zero breaking changes (35/35 tests passing)
- ✅ Unit test coverage ≥90% (new code)
- ✅ Performance overhead <5ms per phase
- ✅ All DoR/DoD gates passed

### Adoption
- ✅ Example plugins/phases/strategies functional
- ✅ Documentation peer-reviewed
- ✅ Real-world validation (C# monolith tested)

---

## 🔒 Risk Management

### Risk 1: Breaking Changes
**Probability:** LOW  
**Impact:** HIGH  
**Mitigation:** 
- Smoke test suite runs after every change
- Public API frozen (extensibility via new methods)
- Feature flags for experimental features

### Risk 2: AST Parser Accuracy
**Probability:** MEDIUM  
**Impact:** MEDIUM  
**Mitigation:**
- Roslyn API for C# (high accuracy)
- Tree-sitter fallback for other languages
- Manual validation on 3 test codebases
- Tunable coupling score thresholds

### Risk 3: Complexity Creep
**Probability:** MEDIUM  
**Impact:** MEDIUM  
**Mitigation:**
- Incremental phases with DoD gates
- Registry patterns follow Execution model (proven)
- Code reviews at each phase boundary

### Risk 4: Context Optimizer Over-Pruning
**Probability:** MEDIUM  
**Impact:** HIGH  
**Mitigation:**
- Conservative boundary detection (include borderline dependencies)
- User feedback loop (report missing context)
- Adjustable relevance thresholds (HIGH/MEDIUM/LOW)
- Validation: Measure false negative rate <10%

---

## 🎯 Team & Effort

**Estimated Duration:** 20 days (15 base + 5 for scope management)  
**Team Size:** 2 engineers  
**Roles:**
- **Engineer 1:** Registry patterns, TDD plugins, Scaffolding strategies
- **Engineer 2:** AST integration, Scope analyzer, Context optimizer

**Total Effort:** 40 person-days (~320 hours)

**Breakdown:**
- Phase 1: 10 person-days (registry + AST foundation)
- Phase 2: 10 person-days (plugins + scope algorithm)
- Phase 3: 10 person-days (remaining orchestrators + integration)
- Phase 4: 10 person-days (testing + documentation + audit)

---

## 🔗 Dependencies

### External
- **Roslyn API:** C# AST parsing (NuGet package)
- **Tree-sitter:** Multi-language parsing (Python bindings)
- **PyYAML:** Configuration parsing

### Internal
- **Execution Orchestrator:** Registry pattern reference
- **Scaffolding Orchestrator:** Scope analyzer integration
- **Intelligence Orchestrator:** Context optimizer integration
- **TDD Orchestrator:** Plugin system integration

---

## 📚 References

### Documentation
- `cortex-brain/documents/reports/phase-2-orchestrators-completion.md` (Current extensibility ratings)
- `cortex-brain/manifests/orchestrators/planning-system-2.0-manifest.yaml` (DoR/DoD requirements)
- `src/orchestration_3_0/orchestrators/execution/orchestrator_registry.py` (Registry pattern example)

### Research
- Roslyn API Documentation: https://learn.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/
- Tree-sitter: https://tree-sitter.github.io/tree-sitter/
- Coupling Metrics: Martin, R. C. (2017). Clean Architecture

---

## 🚀 Execution Mode

**Method:** Planning System 2.0 Autonomous Execution  
**Approach:** Incremental phasing with DoD gates  
**Interaction:** Interactive (user approval at phase boundaries)

**Next Action:** Review and approve this plan, then say "execute all phases autonomously" to begin Phase 1.

---

**Plan Status:** 🟡 APPROVED - Awaiting Autonomous Execution Command  
**Created:** 2025-12-10 | **Last Updated:** 2025-12-10

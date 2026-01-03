# Sanitization Orchestrator v2 Migration - Master Plan

**Plan ID:** sanitization-v2-migration  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.4)  
**Feature:** Pure Autonomous Sanitization with Transactional Safety  
**Created:** January 3, 2026  
**Complexity:** TIER 4 (ARCHITECTURAL - High-risk transformations require transactional safety)  
**Strategy:** Engine-based architecture with progressive analysis and dual-mode support  
**Estimated Duration:** 2 days (16 hours)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `███░░░░░░░░░░░░░░░░░` **20%** ⏳ IN PROGRESS

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| 0 | Foundation & Analysis | `██████████` | 2h | ✅ Complete |
| 0.5 | **Holistic Review #1** | `██████████` | **1h** | ✅ **Complete** |
| 1 | Design Architecture | `██░░░░░░░░` | 2h | ⏳ In Progress |
| 1.5 | **Holistic Review #2** | `░░░░░░░░░░` | **0.5h** | ⏸️ Not Started |
| 2 | Implement Core Orchestrator | `░░░░░░░░░░` | 3h | ⏸️ Not Started |
| 3 | Implement Engines | `░░░░░░░░░░` | 4h | ⏸️ Not Started |
| 3.5 | **Holistic Review #3** | `░░░░░░░░░░` | **0.5h** | ⏸️ Not Started |
| 4 | Configuration & Templates | `░░░░░░░░░░` | 1.5h | ⏸️ Not Started |
| 5 | Testing & Validation | `░░░░░░░░░░` | 3h | ⏸️ Not Started |
| 5.5 | **Holistic Review #4** | `░░░░░░░░░░` | **0.5h** | ⏸️ Not Started |
| 6 | Master Orchestrator Integration | `░░░░░░░░░░` | 1h | ⏸️ Not Started |
| 7 | Documentation & Completion | `░░░░░░░░░░` | 1h | ⏸️ Not Started |
| 7.5 | **Holistic Review #5** | `░░░░░░░░░░` | **1h** | ⏸️ Not Started |
| 8 | REFACTOR & Cleanup | `░░░░░░░░░░` | 1h | ⏸️ Not Started |

**Total Duration:** 19 hours (includes 3.5 hours holistic reviews)  
**Current Phase:** 1 (Design Architecture)

---

## 🎯 Executive Summary

### The Transformation

Migrate Sanitization from **prompt-based GUIDED orchestrator** (manifest instructions) to **pure autonomous Python implementation (v2)** with comprehensive safety guarantees, transactional operations, and Master Orchestrator integration.

### Why Autonomous?

**Current State (v1 - GUIDED):**
- Prompt-based execution via `code-sanitization-manifest.yaml`
- Manual approval workflow through LLM interpretation
- Limited rollback capability
- Not Master Orchestrator integrated

**Target State (v2 - AUTONOMOUS):**
- ✅ Pure Python implementation (zero prompt interpretation)
- ✅ Transactional operations with atomic rollback
- ✅ Progressive AST analysis for performance
- ✅ 5-level risk classification (SAFE → CRITICAL)
- ✅ Dry-run mode by default
- ✅ State persistence in PlanningStateDB
- ✅ Master Orchestrator integrated (priority 57)
- ✅ BaseOrchestrator v4.1 compliant

### Holistic Review Integration 🆕

Based on learnings from ADO v2, Cleanup v2, and Vacuum v2 migrations:

**Key Architectural Decisions:**
1. ✅ **Engine-based architecture** (5 specialized engines - proven pattern)
2. ✅ **Transactional operations** (checkpoint → transform → validate → commit/rollback)
3. ✅ **Progressive analysis** (quick scan → AST parsing → deep analysis)
4. ⚠️ **Dual-mode architecture** (evaluate autonomous vs wizard modes)
5. ✅ **45% code reuse** from existing utilities (mapping_engine, validator, report_generator)

**See:** `architecture/holistic-review-01.md` for full analysis

---

## 🏗️ Architecture Overview

### 5-Engine Modular Design

```
sanitization_orchestrator_v2.py (600-700 lines)
├── code_analyzer_engine.py (400-500 lines)
│   ├── File scanning & categorization
│   ├── AST parsing (cached)
│   ├── Domain terminology extraction
│   └── Sensitive data detection
│
├── transformer_engine.py (500-600 lines)
│   ├── AST-based code transformation
│   ├── File/directory renaming
│   ├── TransformationTransaction (atomic ops)
│   └── Checkpoint creation & rollback
│
├── validator_engine.py (300-400 lines)
│   ├── Build system detection
│   ├── Test execution & comparison
│   ├── Functionality parity verification
│   └── Rollback trigger on failure
│
├── mapping_engine.py (300-400 lines) [REUSE 70%]
│   ├── Domain→generic mapping generation
│   ├── Conflict detection & resolution
│   ├── Mapping persistence (JSON)
│   └── Interactive approval workflow
│
└── report_generator_engine.py (200-300 lines) [REUSE 60%]
    ├── Audit report generation
    ├── Transformation metrics
    ├── Diff summaries
    └── Mapping documentation
```

**Total:** ~2,300-2,900 lines (production) + ~1,500-2,000 lines (tests)

### 5-Phase Workflow

```
PHASE 1: ANALYZE
├── Scan file structure
├── Parse AST (progressive)
├── Extract domain terminology
├── Classify transformation risk
└── Generate analysis report

PHASE 2: MAPPING
├── Generate domain→generic mappings
├── Detect naming conflicts
├── Present preview to user
├── Collect approval (wizard mode) or auto-approve (autonomous mode)
└── Persist approved mappings

PHASE 3: TRANSFORM
├── Create checkpoint backup
├── Begin TransformationTransaction
├── Apply AST transformations
├── Rename files/directories
├── Verify transformations (SHA256)
└── Commit transaction

PHASE 4: VALIDATE
├── Detect build system
├── Execute build
├── Run test suite
├── Compare test results
└── Rollback if validation fails

PHASE 5: COMPLETE
├── Generate audit report
├── Save mapping artifacts
├── Clean up checkpoint (if validation passed)
└── Update state database
```

---

## 📋 Phase Breakdown

### Phase 0: Foundation & Analysis ✅ COMPLETE
**Duration:** 2 hours  
**Status:** ✅ Complete

**Deliverables:**
- ✅ Migration plan structure created
- ✅ Existing v1 sanitization analyzed
- ✅ Reusable components identified:
  - `src/operations/utilities/sanitization/code_analyzer.py` (296 lines - 50% reusable)
  - `src/operations/utilities/sanitization/transformer.py` (reusable AST patterns)
  - `src/operations/utilities/sanitization/validator.py` (build validation logic)
  - `src/operations/utilities/sanitization/report_generator.py` (60% reusable)
  - `src/operations/utilities/sanitization/mapping_engine.py` (70% reusable)

---

### Phase 0.5: Holistic Review #1 - Before Design ✅ COMPLETE
**Duration:** 1 hour  
**Status:** ✅ Complete

**Deliverables:**
- ✅ `architecture/holistic-review-01.md` (12 sections, 400+ lines)
- ✅ Pattern analysis (ADO v2, Cleanup v2, Vacuum v2)
- ✅ Architecture recommendations (engine-based, transactional, progressive)
- ✅ Code reuse strategy (~45% reuse potential)
- ✅ Complexity estimate (4,000-5,000 lines total)

**Key Insights:**
1. Engine-based architecture is proven (3 successful migrations)
2. Transactional operations critical for code transformation safety
3. Progressive analysis optimizes performance (like Vacuum's 3-phase hashing)
4. Dual-mode architecture evaluation needed (autonomous vs wizard)
5. 45% code reuse achievable from existing utilities

---

### Phase 1: Design Architecture ⏳ IN PROGRESS
**Duration:** 2 hours  
**Status:** ⏳ In Progress (20% complete)

**Tasks:**
1. ⏳ Create detailed architecture diagram
2. ⏸️ Define TransformationTransaction interface
3. ⏸️ Specify 5-level risk classification rules
4. ⏸️ Design progressive analysis pipeline
5. ⏸️ Evaluate dual-mode architecture (cost/benefit)
6. ⏸️ Document component interfaces
7. ⏸️ Define YAML configuration structure

**Deliverables:**
- `architecture/component-design.md` - Detailed component specifications
- `architecture/workflow-diagram.md` - Visual workflow representation
- `architecture/risk-classification.md` - 5-level risk taxonomy
- `architecture/transaction-model.md` - Transactional operation design
- `architecture/dual-mode-evaluation.md` - Autonomous vs wizard analysis

---

### Phase 1.5: Holistic Review #2 - Before Implementation ⏸️ NOT STARTED
**Duration:** 0.5 hours  
**Status:** ⏸️ Not Started

**Purpose:**
- Review design decisions against Cleanup v2/Vacuum v2 implementations
- Identify code reuse opportunities (which components to import vs adapt)
- Validate transactional model design
- Confirm engine interfaces
- Document any architectural adjustments

**Deliverable:**
- `architecture/holistic-review-02.md`

---

### Phase 2: Implement Core Orchestrator ⏸️ NOT STARTED
**Duration:** 3 hours  
**Status:** ⏸️ Not Started

**Tasks:**
1. Create `src/orchestrators/sanitization/sanitization_orchestrator_v2.py`
2. Inherit from BaseOrchestrator v4.1
3. Implement 5-phase workflow methods
4. Add state persistence (PlanningStateDB)
5. Implement dry-run mode
6. Add error handling & recovery

**Deliverables:**
- `sanitization_orchestrator_v2.py` (600-700 lines)
- Phase execution framework
- State management integration
- Error recovery logic

**Success Criteria:**
- ✅ BaseOrchestrator v4.1 compliant
- ✅ All 5 phases callable
- ✅ State persists correctly
- ✅ Dry-run mode functional
- ✅ Unit tests passing (orchestrator level)

---

### Phase 3: Implement Engines ⏸️ NOT STARTED
**Duration:** 4 hours  
**Status:** ⏸️ Not Started

**Tasks:**
1. **CodeAnalyzerEngine** (400-500 lines)
   - File scanning with exclusions
   - Progressive AST parsing
   - Domain term extraction
   - Risk classification

2. **TransformerEngine** (500-600 lines)
   - TransformationTransaction class
   - AST-based transformations
   - File/directory renaming
   - Checkpoint creation & rollback

3. **ValidatorEngine** (300-400 lines)
   - Build system detection
   - Test execution
   - Result comparison
   - Rollback triggering

4. **MappingEngine** (300-400 lines) [ADAPT EXISTING]
   - Reuse `src/operations/utilities/sanitization/mapping_engine.py`
   - Add conflict detection
   - Implement approval workflow
   - Add mapping persistence

5. **ReportGeneratorEngine** (200-300 lines) [ADAPT EXISTING]
   - Reuse `src/operations/utilities/sanitization/report_generator.py`
   - Add transformation metrics
   - Generate diff summaries
   - Create audit reports

**Deliverables:**
- 5 engine files (~2,000-2,400 lines total)
- Engine unit tests (~1,200 lines)
- Component integration tests

**Success Criteria:**
- ✅ Each engine independently testable
- ✅ Transactional operations atomic
- ✅ Rollback works correctly
- ✅ Progressive analysis optimized
- ✅ 95%+ test coverage per engine

---

### Phase 3.5: Holistic Review #3 - Before Configuration ⏸️ NOT STARTED
**Duration:** 0.5 hours  
**Status:** ⏸️ Not Started

**Purpose:**
- Review code quality and architectural consistency
- Identify common configuration patterns across orchestrators
- Validate test coverage completeness
- Recommend manifest structure improvements
- Document any implementation adjustments

**Deliverable:**
- `architecture/holistic-review-03.md`

---

### Phase 4: Configuration & Templates ⏸️ NOT STARTED
**Duration:** 1.5 hours  
**Status:** ⏸️ Not Started

**Tasks:**
1. Create `cortex-brain/manifests/orchestrators/sanitization-v2.yaml`
   - Sanitization patterns (domain terms, generic mappings)
   - Risk classification rules
   - Protected file types
   - Transformation rules
   - Validation thresholds

2. Create Jinja2 templates:
   - `sanitization_phase_1_analyze.jinja2`
   - `sanitization_phase_2_mapping.jinja2`
   - `sanitization_phase_3_transform.jinja2`
   - `sanitization_phase_4_validate.jinja2`
   - `sanitization_phase_5_complete.jinja2`

3. Create default mapping templates:
   - `default-sanitization-mappings.json`
   - `terminology-categories.yaml`

**Deliverables:**
- `sanitization-v2.yaml` (300-400 lines)
- 5 Jinja2 templates (~50 lines each)
- Default configuration files

**Success Criteria:**
- ✅ YAML validates against schema
- ✅ Templates render correctly
- ✅ Configuration covers all edge cases
- ✅ Protected paths include CORTEX brain

---

### Phase 5: Testing & Validation ⏸️ NOT STARTED
**Duration:** 3 hours  
**Status:** ⏸️ Not Started

**Tasks:**
1. **Unit Tests** (per engine)
   - CodeAnalyzerEngine: AST parsing, term extraction
   - TransformerEngine: Transaction logic, rollback
   - ValidatorEngine: Build detection, test execution
   - MappingEngine: Conflict resolution, approval
   - ReportGeneratorEngine: Report generation

2. **Integration Tests**
   - End-to-end workflow (all 5 phases)
   - Rollback scenarios
   - Dry-run mode validation
   - Multi-file transformation

3. **Edge Case Tests**
   - Empty project
   - No domain terms found
   - Build failure triggers rollback
   - Test failure triggers rollback
   - Mapping conflicts

**Deliverables:**
- `tests/orchestrators/sanitization/test_sanitization_orchestrator_v2.py`
- `tests/orchestrators/sanitization/test_code_analyzer_engine.py`
- `tests/orchestrators/sanitization/test_transformer_engine.py`
- `tests/orchestrators/sanitization/test_validator_engine.py`
- `tests/orchestrators/sanitization/test_mapping_engine_v2.py`
- `tests/orchestrators/sanitization/test_report_generator_engine.py`
- `tests/orchestrators/sanitization/test_sanitization_e2e.py`

**Test Count:** ~80-100 tests  
**Test Coverage Target:** 95%+

**Success Criteria:**
- ✅ All tests passing
- ✅ 95%+ coverage
- ✅ Rollback scenarios validated
- ✅ Edge cases handled
- ✅ Performance acceptable (<10s for typical project)

---

### Phase 5.5: Holistic Review #4 - Before Integration ⏸️ NOT STARTED
**Duration:** 0.5 hours  
**Status:** ⏸️ Not Started

**Purpose:**
- Analyze test coverage and implementation completeness
- Review Master Orchestrator routing patterns across all v2 orchestrators
- Identify routing optimization opportunities
- Validate pattern priority assignments
- Document integration recommendations

**Deliverable:**
- `architecture/holistic-review-04.md`

---

### Phase 6: Master Orchestrator Integration ⏸️ NOT STARTED
**Duration:** 1 hour  
**Status:** ⏸️ Not Started

**Tasks:**
1. Add routing patterns to `cortex-brain/config/master-orchestrator.yaml`:
   ```yaml
   sanitization_v2:
     orchestrator: sanitization_orchestrator_v2
     priority: 57
     patterns:
       - "^sanitize .*$"
       - "^clean code.*$"
       - "^anonymize .*$"
       - "^make.*generic$"
     handler: src.orchestrators.sanitization.sanitization_orchestrator_v2:SanitizationOrchestratorV2
   ```

2. Update pattern router
3. Validate routing works correctly
4. Test pattern precedence

**Deliverables:**
- Updated `master-orchestrator.yaml`
- Routing validation tests
- Pattern priority documentation

**Success Criteria:**
- ✅ All sanitization patterns route correctly
- ✅ Priority 57 doesn't conflict with other orchestrators
- ✅ Pattern router tests passing
- ✅ Master Orchestrator integration tests passing

---

### Phase 7: Documentation & Completion ⏸️ NOT STARTED
**Duration:** 1 hour  
**Status:** ⏸️ Not Started

**Tasks:**
1. Create completion report
2. Update CONTINUATION-PROMPT-PHASE-6-5.md
3. Create migration guide
4. Document architecture decisions
5. Generate metrics report

**Deliverables:**
- `reports/completion-report.md`
- `reports/migration-guide.md`
- `reports/architecture-decisions.md`
- `reports/metrics-report.md`
- `CONTINUATION-PROMPT-PHASE-6-5.md`

---

### Phase 7.5: Holistic Review #5 - Final Architecture Review ⏸️ NOT STARTED
**Duration:** 1 hour  
**Status:** ⏸️ Not Started

**Purpose:**
- Conduct comprehensive review of ALL Phase 6 migrations (ADO, Cleanup, Vacuum, Sanitization)
- Identify system-wide architectural improvements
- Extract reusable patterns for future orchestrators
- Document technical debt
- Generate recommendations for remaining phases (Debug v2, Phase 8-10)

**Deliverable:**
- `reports/final-holistic-review.md` (comprehensive analysis)

---

### Phase 8: REFACTOR & Cleanup ⏸️ NOT STARTED
**Duration:** 1 hour  
**Status:** ⏸️ Not Started

**SKULL Brain Protection Rules:**
1. ✅ Remove all debug print statements
2. ✅ Standardize docstrings (Google style)
3. ✅ Optimize imports (remove unused)
4. ✅ Validate test coverage (95%+)
5. ✅ PEP 8 compliance
6. ✅ Type hints comprehensive
7. ✅ Error messages descriptive
8. ✅ Implement recommendations from final holistic review

**Tasks:**
- Run `black` formatter
- Run `isort` for imports
- Run `mypy` for type checking
- Run `pylint` for code quality
- Apply final holistic review recommendations

**Success Criteria:**
- ✅ All linters passing
- ✅ Type hints complete
- ✅ No TODO/FIXME comments
- ✅ Documentation complete
- ✅ Holistic review recommendations implemented

---

## 🎯 Success Criteria

### Architecture
- ✅ BaseOrchestrator v4.1 compliant
- ✅ 5 specialized engines (modular design)
- ✅ Transactional operations with rollback
- ✅ State persistence in PlanningStateDB
- ✅ Dry-run mode by default

### Safety
- ✅ 5-level risk classification (SAFE → CRITICAL)
- ✅ CORTEX brain protection enforced
- ✅ Checkpoint/rollback system operational
- ✅ Build/test validation triggers rollback on failure

### Quality
- ✅ ~2,300-2,900 lines production code
- ✅ ~1,500-2,000 lines test code
- ✅ 95%+ test coverage
- ✅ All linters passing
- ✅ Type hints comprehensive

### Integration
- ✅ Master Orchestrator routing (priority 57)
- ✅ Pattern-based request detection
- ✅ Template-driven reporting
- ✅ Cross-session context compatible

### Documentation
- ✅ Completion report
- ✅ Migration guide
- ✅ Architecture documentation
- ✅ 5 holistic review documents
- ✅ Continuation prompt updated

---

## 📦 Deliverables Summary

### Production Code
- `src/orchestrators/sanitization/sanitization_orchestrator_v2.py` (600-700 lines)
- `src/orchestrators/sanitization/code_analyzer_engine.py` (400-500 lines)
- `src/orchestrators/sanitization/transformer_engine.py` (500-600 lines)
- `src/orchestrators/sanitization/validator_engine.py` (300-400 lines)
- `src/orchestrators/sanitization/mapping_engine.py` (300-400 lines)
- `src/orchestrators/sanitization/report_generator_engine.py` (200-300 lines)

### Configuration
- `cortex-brain/manifests/orchestrators/sanitization-v2.yaml`
- `cortex-brain/templates/sanitization/` (5 Jinja2 templates)
- `cortex-brain/config/master-orchestrator.yaml` (routing patterns)

### Testing
- 7 test files (~1,500-2,000 lines)
- 80-100 test cases
- 95%+ coverage

### Documentation
- 5 holistic review documents (`architecture/holistic-review-01.md` through `reports/final-holistic-review.md`)
- Completion report
- Migration guide
- Architecture documentation
- Metrics report

---

## 🔄 Holistic Review Schedule

| Review | Trigger | Duration | Purpose |
|--------|---------|----------|---------|
| **#1** | Before Design | 1h | ✅ Pattern analysis, architecture recommendations |
| **#2** | Before Implementation | 0.5h | Code reuse strategy, interface validation |
| **#3** | Before Configuration | 0.5h | Implementation quality, config patterns |
| **#4** | Before Integration | 0.5h | Routing optimization, test coverage analysis |
| **#5** | Before REFACTOR | 1h | System-wide review, future recommendations |

**Total Review Time:** 3.5 hours (18% of project duration)  
**Benefit:** Continuous improvement, pattern extraction, architectural consistency

---

## 🚀 Next Steps

**Current Status:** Phase 1 (Design Architecture) in progress  
**Next Milestone:** Complete design documents, then proceed to Holistic Review #2

**Immediate Actions:**
1. ✅ Complete architecture diagram
2. ✅ Define TransformationTransaction interface
3. ✅ Specify risk classification rules
4. ✅ Design progressive analysis pipeline
5. ⚠️ Evaluate dual-mode architecture
6. ✅ Document component interfaces
7. ✅ Define YAML configuration structure

Then proceed to **Holistic Review #2** before implementation begins.

---

**Plan Status:** ⏳ Active (20% complete)  
**Estimated Completion:** January 3, 2026 (end of day) + January 4, 2026 (morning)  
**Risk Level:** MEDIUM (mitigated by transactional safety and proven patterns)  
**Parent Plan Progress Impact:** +4% (Phase 6.4 completion moves overall from 48% → 52%)

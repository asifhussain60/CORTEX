# CORTEX5 Snowball

**Plan ID:** plan-c34db247-f34d-44d3-8f3d-4da3487227b9  
**Created:** 2026-01-06  
**Updated:** 2026-01-06  
**Status:** ✅ ACTIVE  
**Orchestrator:** Planning v5  
**Architecture:** Hierarchical Goals v1.0 (70% maintenance reduction)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Name | Progress | Status |
|-------|------|----------|--------|
| 0 | Planning Complete | `██████████` | ✅ Complete |
| 1 | Intelligent Goal Detection | `░░░░░░░░░░` | ⏸️ Not Started |
| 2 | Goal Inheritance Resolver | `░░░░░░░░░░` | ⏸️ Not Started |
| 3 | Planning v5 Integration | `░░░░░░░░░░` | ⏸️ Not Started |
| 4 | Cross-Plan Learning | `░░░░░░░░░░` | ⏸️ Not Started |
| 5 | Validation & Testing | `░░░░░░░░░░` | ⏸️ Not Started |

---

## 🎯 Executive Summary

### The Goal
CORTEX 5.0 Remediation with maximum snowball effect - progressive system activation with parallel execution tracks for 36% faster completion (11 weeks → 8 weeks).

### Epic-Level Goals (Auto-Inherit to ALL Phases)

**🔴 Mandatory Goals (Blocked if violated):**
- **G001:** Track all audit log paths - Every orchestrator logs audit trail with decision capture
- **G002:** Ensure atomic operations - All database ops atomic with rollback
- **G003:** Validate governance compliance - Every phase validates brain-protection-rules.yaml

**🟡 Recommended Goals (Warning if violated):**
- **G004:** Verify brittleness checks - No false positives (Phase -2 validation)
- **G005:** Maintain backward compatibility - All changes support existing workflows

**📋 Note:** Phases auto-inherit these goals - no re-declaration needed! Only add phase-specific goals below.

### Success Criteria
- ✅ Implementation complete
- ✅ Tests passing (100% coverage)
- ✅ Documentation updated
- ✅ Code reviewed
- ✅ All Epic-level goals validated (G001-G005)

---

## 🏗️ Implementation Phases

### Phase 0: Planning (COMPLETE)
**Duration:** 1h  
**Status:** ✅ Complete

**Deliverables:**
- Master plan document
- Folder structure
- Progress tracker

### Phase 1: Intelligent Goal Detection
**Duration:** 1 week  
**Status:** ⏸️ Not Started  
**Inherits:** G001 (audit logs), G002 (atomic ops), G003 (governance), G004 (brittleness), G005 (compatibility)

**Phase-Specific Goals:**
- P001: Keyword detection from natural language requests
- P002: Auto-create Epic goals from user prompts
- P003: Real-time goal validation during feature requests

**Feature:** Every new feature request automatically checked against learned goals for maximum efficiency

**Tasks:**
1. Create goal pattern library (20 common goals)
   - Audit logging, brittleness checks, atomic operations
   - Threat modeling, compliance mapping, governance validation
   - TDD enforcement, backward compatibility
2. Implement keyword scanner in Planning v5
   - Scan user request: "plan user auth with audit logging"
   - Extract keywords: ["audit logging", "user auth"]
   - Map to goals: G001 (Track Audit Paths)
3. Auto-suggest goals during plan creation
   - User prompt → keyword detection → goal extraction
   - Confirmation dialog: "Add G001: Track Audit Paths?"
   - One-click acceptance or customization

**Deliverables:**
- `src/orchestrators/planning/intelligence/goal_keyword_detector.py`
- `cortex-brain/config/goal-pattern-library.yaml` (20 common goals)
- `src/orchestrators/planning/intelligence/goal_suggester.py`

**Goal Validation:**
- ✅ Audit logs created (G001)
- ✅ Operations atomic (G002)
- ✅ Governance validated (G003)
- ✅ Brittleness checks passed (G004)

**Acceptance Criteria:**
- User says "plan OAuth2 with audit logging" → G001 auto-suggested
- User confirms → G001 added as Epic goal
- All future phases auto-inherit G001

---

### Phase 1.5: Script Consolidation Governance ⚡ URGENT
**Duration:** 3 days  
**Status:** ⏸️ Not Started  
**Inherits:** G001 (audit logs), G002 (atomic ops), G003 (governance), G004 (brittleness), G005 (compatibility)

**Phase-Specific Goals:**
- P1.5-001: Catalog all utility scripts via Cortex Toolkit Orchestrator
- P1.5-002: Detect and eliminate duplicate functionality scripts
- P1.5-003: Consolidate similar scripts into unified modules

**Problem:** Multiple *.py files in `src/orchestrators/planning/` doing similar tasks (duplicate_detector.py, orphan_detector.py, similarity_checker.py, etc.) causing code duplication, maintenance burden, and discovery failures.

**Solution:** Enforce `SCRIPT_ORGANIZATION_ENFORCEMENT` governance rule (brain-protection-rules.yaml)

**Tasks:**
1. Create Cortex Toolkit Orchestrator with child orchestrators
   - Scanner child: Duplicate script detection
   - Consolidator child: Merge similar scripts
   - Cataloger child: Register scripts in central catalog
2. Scan `src/orchestrators/planning/` for duplicate functionality
   - AST-based similarity detection
   - Function signature matching
   - Purpose overlap analysis
3. Consolidate duplicate scripts
   - Merge duplicate_detector.py + orphan_detector.py → unified code_analyzer.py
   - Archive unused scripts to cortex-brain/archives/scripts/
   - Update imports across codebase
4. Create script catalog registry
   - `cortex-brain/toolkit/script-catalog.yaml`
   - Document each script: purpose, owner, dependencies
   - Enforce registration for new scripts

**Deliverables:**
- `src/orchestrators/toolkit/cortex_toolkit_orchestrator.py` (Master)
- `src/orchestrators/toolkit/duplicate_script_detector.py` (Child)
- `src/orchestrators/toolkit/script_consolidator.py` (Child)
- `src/orchestrators/toolkit/script_cataloger.py` (Child)
- `cortex-brain/toolkit/script-catalog.yaml` (Registry)
- `cortex-brain/documents/reports/script-consolidation-2026-01-06.md` (Report)

**Goal Validation:**
- ✅ Audit logs created (G001) - Track all consolidation actions
- ✅ Operations atomic (G002) - Consolidation with rollback
- ✅ Governance validated (G003) - SCRIPT_ORGANIZATION_ENFORCEMENT rule enforced

**Acceptance Criteria:**
- <10 scripts in src/orchestrators/planning/ (down from 15+)
- Zero duplicate functionality detected
- All scripts registered in catalog
- SCRIPT_ORGANIZATION_ENFORCEMENT rule active

---

### Phase 2: Goal Inheritance Resolver
**Duration:** 2 weeks  
**Status:** ⏸️ Not Started  
**Inherits:** G001, G002, G003, G004, G005

**Phase-Specific Goals:**
- P004: Implement cascading inheritance (Epic → Feature → Phase)
- P005: Circular dependency detection
- P006: Goal conflict resolution

**Tasks:**
1. Create `GoalInheritanceResolver` class
   - Based on `ManifestInheritanceResolver` pattern
   - Recursive goal resolution (Epic → Feature → Phase → Task)
   - Inheritance type enforcement (mandatory/recommended/optional)
2. Implement goal validation middleware
   - Validate mandatory goals before phase transitions
   - Warning for skipped recommended goals (justification required)
   - Exemption workflow for special cases
3. Integration with GovernanceCheckpoint
   - Connect to existing governance middleware
   - Goal completion tracking per phase

**Deliverables:**
- `src/orchestrators/planning/intelligence/goal_inheritance_resolver.py`
- `cortex-brain/schemas/hierarchical-goals-schema.yaml`
- Unit tests for goal resolution logic

**Goal Validation:**
- ✅ Audit logs created (G001)
- ✅ Operations atomic (G002)
- ✅ Governance validated (G003)

**Acceptance Criteria:**
- Epic goal G001 auto-inherits to all phases
- Phase can opt-out of recommended goals with justification
- Mandatory goal violation = blocked phase transition

---

### Phase 3: Planning v5 Integration
**Duration:** 2 weeks  
**Status:** ⏸️ Not Started  
**Inherits:** G001, G002, G003, G004

**Phase-Specific Goals:**
- P007: Auto-inject inherited goals during plan generation
- P008: Real-time goal compliance reporting
- P009: One-click goal inheritance from similar plans

**Tasks:**
1. Update Planning v5 plan generation
   - Auto-inject inherited goals into phase definitions
   - No manual YAML editing required
   - Goal validation before each phase start
2. Implement goal compliance dashboard
   - Epic → Feature → Phase breakdown
   - Goal completion percentage per phase
   - Violations report (blocked/warning/info)
3. Similar plan detection
   - "This plan is similar to cortex5-remediation"
   - "Inherit G001-G005 from that plan?"
   - One-click goal inheritance

**Deliverables:**
- Enhanced `PlanningOrchestratorV5.generate_plan()` method
- `src/orchestrators/planning/intelligence/goal_compliance_reporter.py`
- `src/orchestrators/planning/intelligence/similar_plan_detector.py`

**Goal Validation:**
- ✅ Audit logs created (G001)
- ✅ Governance validated (G003)
- ✅ Brittleness checks passed (G004)

**Acceptance Criteria:**
- Plan generation auto-injects inherited goals (no manual work)
- Goal compliance report generated per phase
- Similar plan detection suggests goal inheritance

---

### Phase 4: Cross-Plan Learning
**Duration:** 1 week  
**Status:** ⏸️ Not Started  
**Inherits:** G001, G003

**Phase-Specific Goals:**
- P010: Track goal frequency across all plans
- P011: Auto-promote repeated goals to Epic level
- P012: Smart suggestions based on patterns

**Feature:** CORTEX learns from repeated goal patterns and suggests Epic-level promotion

**Tasks:**
1. Implement goal frequency tracker
   - Store goal mentions in Tier 2 knowledge graph
   - Track: goal_id, plan_id, phase_id, timestamp
   - Calculate frequency: mentions across plans
2. Auto-promotion logic
   - Goal mentioned 3+ times → suggest Epic promotion
   - Goal mentioned 10+ times → auto-promote (with confirmation)
   - "Audit logging appears in 8/10 plans - make it global?"
3. Context-aware suggestions
   - Database feature → suggest "atomic operations"
   - Security feature → suggest "threat modeling" + "audit logs"
   - User data feature → suggest "compliance mapping" + "audit logs"

**Deliverables:**
- `src/orchestrators/planning/intelligence/goal_frequency_tracker.py`
- Tier 2 knowledge graph schema extension (goal tracking)
- `src/orchestrators/planning/intelligence/goal_promotion_suggester.py`

**Goal Validation:**
- ✅ Audit logs created (G001)
- ✅ Governance validated (G003)

**Acceptance Criteria:**
- Goal mentioned 3+ times triggers promotion suggestion
- Context-aware suggestions based on feature type
- Goal frequency data persisted in knowledge graph

### Phase 5: Validation & Testing
**Duration:** 1 week  
**Status:** ⏸️ Not Started  
**Inherits:** G001, G003, G004

**Phase-Specific Goals:**
- P013: 100% test coverage for goal system
- P014: End-to-end validation with cortex5-remediation plan
- P015: Performance benchmarking (goal detection <100ms)

**Tasks:**
1. Unit tests for all components
   - GoalKeywordDetector tests (20 patterns)
   - GoalInheritanceResolver tests (inheritance chains)
   - GoalFrequencyTracker tests (cross-plan learning)
2. Integration tests
   - Full workflow: prompt → detection → inheritance → validation
   - Similar plan detection accuracy
   - Goal promotion logic validation
3. End-to-end testing
   - Migrate cortex5-remediation plan to new system
   - Validate 70% maintenance reduction claim
   - User acceptance testing
4. Performance optimization
   - Goal detection <100ms per request
   - Inheritance resolution <50ms
   - Knowledge graph queries <200ms

**Deliverables:**
- `tests/orchestrators/planning/intelligence/test_goal_*.py` (5 test files)
- End-to-end test suite
- Performance benchmark report
- Migration guide for existing plans

**Goal Validation:**
- ✅ Audit logs created (G001)
- ✅ Governance validated (G003)
- ✅ Test brittleness prevented (G004)

**Acceptance Criteria:**
- 100% test coverage achieved
- Goal detection <100ms (performance requirement)
- cortex5-remediation plan migrated successfully
- 70% maintenance reduction validated

---

## � Efficiency Multiplier: Automatic Goal Validation

**How It Works:**

Every time a new feature is requested, CORTEX automatically:
1. ✅ Scans request for goal keywords ("audit", "atomic", "brittle", "threat", "compliance")
2. ✅ Extracts relevant goals from pattern library
3. ✅ Suggests Epic-level goals: "Add G001: Track Audit Paths?"
4. ✅ Auto-inherits goals to all phases (no manual work)
5. ✅ Validates goal completion before phase transitions
6. ✅ Learns patterns: "Audit logging in 8/10 plans - make it global?"

**Example Workflow:**

```
You: "plan payment processing with PCI-DSS compliance"

CORTEX: "🔍 Detected 3 goals from your request:
         - G001: Audit logging (PCI-DSS 10.0) [mandatory]
         - G002: Encryption (PCI-DSS 3.0) [mandatory]
         - G003: Access control (PCI-DSS 7.0) [mandatory]
         
         Add these as Epic goals?"

You: "yes"

CORTEX: "✅ 3 Epic goals created
         ✅ Auto-inherited to all 5 phases
         ✅ Validation gates enabled
         ✅ Plan ready for execution"
```

**Efficiency Gains:**

| Action | Before (Manual) | After (Automatic) | Time Saved |
|--------|----------------|-------------------|------------|
| **Create Epic Goals** | 15 min (manual YAML editing) | 30 sec (one confirmation) | **14.5 min** |
| **Inherit to Phases** | 10 min (copy-paste × 5 phases) | 0 sec (automatic) | **10 min** |
| **Update Goals** | 20 min (edit 5 phases) | 2 min (update Epic) | **18 min** |
| **Check Compliance** | 30 min (manual review) | 5 sec (automatic validation) | **29.9 min** |
| **Learn Patterns** | Never (manual analysis) | Real-time (cross-plan tracking) | **∞ gain** |

**Total Time Saved per Plan:** **72.4 minutes** (>1 hour!)

---

## 📝 Next Steps

1. Begin Phase 1: Intelligent Goal Detection (Week 1)
   - Create goal pattern library (20 common goals)
   - Implement keyword scanner
   - Auto-suggest workflow

2. Phase 2: Goal Inheritance Resolver (Week 2-3)
   - Implement cascading inheritance
   - Goal validation middleware

3. Phase 3: Planning v5 Integration (Week 4-5)
   - Auto-inject inherited goals
   - Goal compliance reporting

4. Phase 4: Cross-Plan Learning (Week 6)
   - Track goal frequency
   - Auto-promotion suggestions

5. Phase 5: Validation & Testing (Week 7)
   - End-to-end testing
   - Performance benchmarking

**Total Duration:** 7 weeks  
**ROI:** 70% plan maintenance reduction + 72 minutes saved per plan

---

**Generated by:** Planning Orchestrator v5  
**Database:** `plan_id="plan-c34db247-f34d-44d3-8f3d-4da3487227b9"`  
**Enhancement:** Intelligent Goal Detection v1.0 (auto-validates every feature request)

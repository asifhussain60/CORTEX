# Phase 38 S11-S12: Final Stages Implementation Plan
**Authority:** TDDOrchestrator | **Status:** KICKOFF | **Scope:** 47 tests across 2 stages | **Duration:** ~2 days

---

## 🎯 Implementation Objective

Complete Phase 38's final 2 stages (S11-S12):
- **S11:** VacuumOrchestrator Enhancement (File Relocation + Recataloging) — 37 tests, 4 days planned
- **S12:** cortex-architect AUDIT Mode Integration — 10 tests, 2 days planned

**Result:** 57/57 phases complete (100%) → Ready for production launch

---

## 📋 Stage 11: VacuumOrchestrator Enhancement (37 tests)

### Scope

Extend VacuumOrchestrator beyond markdown cleanup to handle file governance:

1. **FileRelocationEngine** (12 tests)
   - Detect files violating placement rules
   - Generate relocation plan (source → destination)
   - Update all references (imports, wiring.yaml, registry)
   - Git mv with history preservation

2. **ScreamingCaseDetector** (10 tests)
   - Detect SCREAMING_CASE files (violates CORE-028)
   - Generate kebab-case alternatives
   - Bulk rename with reference updates

3. **RecataloingEngine** (8 tests)
   - Update wiring.yaml orchestrator paths
   - Update cortex-registry index.yaml references
   - Update Python import statements
   - Update documentation links

4. **OptimalFolderStateValidator** (7 tests)
   - No files in root (except allowed: README, Makefile, etc.)
   - All .py files in cortex/, tests/
   - All .md files in docs/, .github/
   - All orchestrators in cortex/orchestrators/

### Acceptance Criteria (TDD Format)

```
AC-PHASE38-030: FileRelocationEngine tests (12)
├── Test: Detect_files_violating_placement_rules
├── Test: Generate_relocation_plan_with_path_mapping
├── Test: Update_imports_in_python_files
├── Test: Update_wiring_yaml_references
├── Test: Update_registry_references
├── Test: Preserve_git_history_on_move
├── Test: Handle_nested_directory_relocations
├── Test: Validate_destination_path_available
├── Test: Rollback_on_reference_update_failure
├── Test: Batch_relocate_multiple_files
├── Test: Detect_circular_import_after_relocation
└── Test: Update_relative_imports_correctly

AC-PHASE38-031: ScreamingCaseDetector tests (10)
├── Test: Detect_SCREAMING_CASE_files
├── Test: Generate_kebab_case_alternatives
├── Test: Map_all_violations_in_codebase
├── Test: Generate_migration_plan
├── Test: Preserve_file_history_on_rename
├── Test: Update_imports_after_rename
├── Test: Update_documentation_references
├── Test: Handle_test_file_renames
├── Test: Validate_kebab_case_naming_compliance
└── Test: Batch_rename_multiple_files

AC-PHASE38-032: RecataloingEngine tests (8)
├── Test: Update_wiring_yaml_paths_after_relocation
├── Test: Update_index_yaml_references
├── Test: Update_python_imports
├── Test: Update_markdown_links
├── Test: Maintain_wiring_integrity_post_update
├── Test: Validate_no_broken_references
├── Test: Generate_recatalog_report
└── Test: Rollback_catalog_updates_on_failure

AC-PHASE38-033: OptimalFolderStateValidator tests (7)
├── Test: Detect_py_files_in_root
├── Test: Detect_md_files_outside_docs_github
├── Test: Validate_all_orchestrators_in_cortex_orchestrators
├── Test: Validate_tests_in_tests_directory
├── Test: Detect_placement_violations
├── Test: Generate_placement_audit_report
└── Test: Provide_placement_remediation_plan
```

### File Deliverables (S11)

```
New Files:
├── cortex/orchestrators/support/file_relocation_engine.py (200 LOC)
├── cortex/orchestrators/support/recataloging_engine.py (180 LOC)
├── cortex/orchestrators/support/screaming_case_detector.py (150 LOC)
├── cortex/orchestrators/support/file_governance_validator.py (120 LOC)
├── tests/unit/orchestrators/support/test_file_relocation.py (120 tests)
└── tests/unit/orchestrators/support/test_recataloging.py (80 tests)

Modified Files:
└── cortex/orchestrators/support/vacuum_orchestrator.py (+200 LOC integration)
```

### Implementation Strategy (TDD Cycle)

**Cycle 1: FileRelocationEngine (Day 1 AM)**
- RED: Write 12 tests for file detection + path mapping
- GREEN: Implement minimal FileRelocationEngine
- REFACTOR: Add error handling, logging, performance optimization

**Cycle 2: ScreamingCaseDetector (Day 1 PM)**
- RED: Write 10 tests for case detection + migration
- GREEN: Implement detector + kebab-case generator
- REFACTOR: Add batch processing, dry-run mode

**Cycle 3: RecataloingEngine (Day 2 AM)**
- RED: Write 8 tests for wiring/registry/import updates
- GREEN: Implement update logic (order: wiring → registry → imports → docs)
- REFACTOR: Add rollback capability, validation gates

**Cycle 4: OptimalFolderStateValidator (Day 2 AM)**
- RED: Write 7 tests for folder structure validation
- GREEN: Implement validator checks
- REFACTOR: Add reporting, remediation suggestions

---

## 📋 Stage 12: cortex-architect AUDIT Mode Integration (10 tests)

### Scope

Update cortex-architect.prompt.md to audit ALL Phase 38 enhancements:
1. MCP Toolkit Completeness (100% coverage)
2. Central Brain Health (multi-user capable)
3. SaaS/MCP Deployment Ready (load tests pass)
4. Regression Safety Net (no broken functionality)
5. File Placement Governance (kebab-case, optimal folders)

### Acceptance Criteria (TDD Format)

```
AC-PHASE38-034: cortex-architect.prompt.md Phase 38 checks (5)
├── Test: P1.5-006 MCP Toolkit audit is present
├── Test: P1.5-007 Central Brain audit is present
├── Test: P1.5-008 SaaS/MCP Deployment audit is present
├── Test: P1.5-009 Regression Safety audit is present
└── Test: P1.5-010 File Placement audit is present

AC-PHASE38-035: AUDIT mode workflow integration (3)
├── Test: AUDIT_MODE includes Phase 38 validation checks
├── Test: AUDIT output includes P1.5-006 through P1.5-010 results
└── Test: AUDIT failure if Phase 38 checks fail

AC-PHASE38-036: Documentation updates (2)
├── Test: docs/architecture/phase-38-brain-cohesion.md created
└── Test: cortex-registry audit-checklist.yaml P1.5 category added
```

### File Deliverables (S12)

```
Modified Files:
├── .github/prompts/cortex-architect.prompt.md (+150 LOC for P1.5 checks)
├── cortex-registry/_cortex-master/governance/audit-checklist.yaml (+40 lines P1.5 category)
└── cortex/orchestrators/support/vacuum_orchestrator.py (refactor to use Phase 38 tools)

New Files:
├── tests/unit/governance/test_phase_38_audit_integration.py (50 tests)
├── docs/architecture/phase-38-brain-cohesion.md (reference guide)
└── cortex-registry/_cortex-master/governance/p1.5-checks.yaml (detailed checks)
```

### Implementation Strategy (TDD Cycle)

**Cycle 1: cortex-architect.prompt.md Updates (Half Day)**
- RED: Write 5 tests verifying P1.5-006 through P1.5-010 in prompt
- GREEN: Add P1.5 check section to cortex-architect.prompt.md
- REFACTOR: Integrate with AUDIT mode workflow

**Cycle 2: AUDIT Workflow Integration (Half Day)**
- RED: Write 3 tests for AUDIT mode including Phase 38 checks
- GREEN: Implement Phase 38 checks in AUDIT mode
- REFACTOR: Add reporting, pass/fail logic

**Cycle 3: Documentation + Checklist (Half Day)**
- RED: Write 2 tests for documentation/checklist updates
- GREEN: Create reference docs + audit checklist
- REFACTOR: Add examples, remediation steps

---

## 🔄 Implementation Timeline

### Day 1: Stage 11 - File Relocation & Governance (24h)

| Time | Task | Tests | Duration |
|------|------|-------|----------|
| 9:00-12:00 | FileRelocationEngine (RED-GREEN-REFACTOR) | 12 | 3h |
| 12:00-13:00 | Lunch & Review | — | 1h |
| 13:00-16:00 | ScreamingCaseDetector (RED-GREEN-REFACTOR) | 10 | 3h |
| 16:00-19:00 | RecataloingEngine (RED-GREEN-REFACTOR) | 8 | 3h |
| **Subtotal S11** | **3 implementations complete** | **30/37** | **10h** |

### Day 2: Stage 11 Part 2 + Stage 12 (24h)

| Time | Task | Tests | Duration |
|------|------|-------|----------|
| 9:00-11:00 | OptimalFolderStateValidator (RED-GREEN-REFACTOR) | 7 | 2h |
| 11:00-12:00 | VacuumOrchestrator integration | — | 1h |
| 12:00-13:00 | Lunch & Regression Test Run | 37/37 ✅ | 1h |
| 13:00-15:00 | cortex-architect.prompt.md updates (RED-GREEN-REFACTOR) | 5 | 2h |
| 15:00-17:00 | AUDIT workflow integration (RED-GREEN-REFACTOR) | 3 | 2h |
| 17:00-18:00 | Documentation + checklist (RED-GREEN-REFACTOR) | 2 | 1h |
| 18:00-19:00 | Full Phase 38 validation + commit | 47/47 ✅ | 1h |
| **Total (Days 1-2)** | **Phase 38 S11-S12 Complete** | **47/47** | **18h** |

---

## ✅ Pre-Implementation Checklist

- [ ] Phase 38 S1-S10 verified complete (220/220 tests passing)
- [ ] No blockers in registry (all dependencies met)
- [ ] VacuumOrchestrator current implementation reviewed
- [ ] wiring.yaml integrity validated
- [ ] cortex-registry index.yaml structure understood
- [ ] Test infrastructure ready (pytest, test fixtures)
- [ ] Git history preservation (git mv) understood
- [ ] AUDIT mode flow in cortex-architect.prompt.md reviewed

---

## 🚀 Success Criteria

### Stage 11 Success
- ✅ All 37 tests passing
- ✅ FileRelocationEngine handles 100+ path updates
- ✅ ScreamingCaseDetector finds all violations
- ✅ RecataloingEngine maintains zero broken references
- ✅ OptimalFolderStateValidator passes full codebase scan
- ✅ VacuumOrchestrator extended with new capabilities
- ✅ Zero regressions (existing 220 tests still passing)

### Stage 12 Success
- ✅ All 10 tests passing
- ✅ P1.5 checks integrated in cortex-architect.prompt.md
- ✅ AUDIT mode includes Phase 38 validation
- ✅ Documentation complete
- ✅ Zero regressions (47 Stage 11 tests still passing)

### Phase 38 Final Success
- ✅ All 260 tests passing (220 S1-S10 + 40 S11-S12)
- ✅ 100% coverage of governance gaps
- ✅ Zero regressions (515+ baseline suite maintained)
- ✅ Production ready (all 57 phases complete)

---

## 🎯 Post-Implementation

### Upon Completion
1. **Registry Update**: Mark Phase 38 as "completed" (will be automatic via TDD framework)
2. **Production Readiness**: All 57 phases complete (54/54 previous + 1 Phase 38)
3. **Decision Point**: Launch to production or proceed with Phase 61+ planning

### Production Launch Preparation
- [ ] Run full regression suite (933+ tests)
- [ ] Performance benchmarking
- [ ] Deployment validation (SaaS + MCP)
- [ ] Documentation review
- [ ] Team onboarding

---

## 📞 Next Action

**Ready to kick off Phase 38 S11-S12 implementation?**

Awaiting confirmation to begin TDD cycles:
1. Confirm understanding of FileRelocationEngine scope
2. Begin RED phase for S11 (12 tests)
3. Proceed through REFACTOR cycle

**Estimated Completion:** 2 days (18 hours active development)
**Result:** 57/57 phases complete + Production ready 🚀

---

*Implementation Plan: Ready for TDD Orchestrator Execution*
*Authority: cortex-architect.prompt.md § TDD MANDATORY*
*Token Budget: ~41K/200K used this session, ~159K remaining (79% available)*

# Phase 1.5: Toolkit Orchestration & Script Consolidation

**Phase ID:** P001.5 | **Duration:** 2 weeks | **Status:** ⏸️ NOT STARTED | **Priority:** ⚡ URGENT

---

## 🎯 Phase Objective

Reduce 17+ scripts to <10 via intelligent consolidation using master toolkit orchestrator with 3 child agents. Achieve 41% script reduction with zero duplication.

---

## 📦 Features Included

| Feature ID | Name | Status | Priority |
|------------|------|--------|----------|
| **F003** | Toolkit Orchestration | ⏸️ Pending | ⚡ URGENT |
| **F002** | Governance Rules (Rule #7) | 🟡 Partial | 🔥 HIGH |

---

## ✅ Acceptance Criteria

### F003: Toolkit Orchestration
- [ ] Master orchestrator created (`src/orchestrators/toolkit_orchestrator.py`)
- [ ] Scanner child agent: AST-based duplicate detection
- [ ] Consolidator child agent: Script merge logic
- [ ] Cataloger child agent: `script-catalog.yaml` registration
- [ ] 17 scripts → <10 scripts (≥41% reduction)
- [ ] Zero functional regression
- [ ] All scripts cataloged in `script-catalog.yaml`

### F002: Rule #7 Enforcement
- [ ] SCRIPT_ORGANIZATION_ENFORCEMENT rule activated
- [ ] Pre-commit hook: Validate no duplicates
- [ ] CI/CD pipeline: Check script catalog compliance
- [ ] Documentation: Script consolidation guidelines

---

## 🔗 Dependencies

**Requires:**
- Phase 0 (Foundation) complete
- F002 (Governance Rules) documented

**Enables:**
- Phase 4 (Response Templates) - cleaner template application
- Phase 7 (Script Orchestration Testing)

---

## 📋 Implementation Tasks

### Week 1: Orchestrator Architecture
1. **Design Master Orchestrator**
   - Create `toolkit_orchestrator.py` skeleton
   - Define child agent interfaces
   - Implement orchestration logic (discovery → consolidation → cataloging)

2. **Scanner Child Agent**
   - AST-based script analysis
   - Similarity detection (≥80% similarity = duplicate)
   - Dependency mapping
   - Conflict detection

3. **Testing**
   - Unit tests for scanner (5 tests)
   - Test with sample duplicate scripts

### Week 2: Consolidation & Cataloging
1. **Consolidator Child Agent**
   - Merge similar scripts
   - Preserve all functionality
   - Update import paths
   - Generate consolidated scripts

2. **Cataloger Child Agent**
   - Register scripts in `script-catalog.yaml`
   - Generate metadata (purpose, inputs, outputs)
   - Create deprecation warnings for old scripts
   - Update documentation

3. **Rule #7 Enforcement**
   - Pre-commit hook setup
   - CI/CD validation pipeline
   - Documentation updates

4. **Testing**
   - Integration tests (orchestrator + 3 children)
   - Regression testing (all scripts still work)
   - Performance testing (consolidation speed)

---

## 🧪 Testing Requirements

- **Unit Tests:** 12 tests (4 per child agent)
- **Integration Tests:** 5 tests (full orchestration flow)
- **Regression Tests:** 17 tests (1 per original script)
- **Coverage Target:** ≥90%

---

## 📈 Success Metrics

- **Script Reduction:** 17 → <10 (≥41%)
- **Duplication Eliminated:** 100%
- **Catalog Coverage:** 100% of remaining scripts
- **Regression Rate:** 0%
- **Consolidation Accuracy:** ≥95%

---

## 📁 Expected Output Structure

```
src/orchestrators/
├── toolkit_orchestrator.py          # Master orchestrator
├── toolkit_scanner_child.py         # Duplicate detection
├── toolkit_consolidator_child.py    # Script merging
└── toolkit_cataloger_child.py       # Catalog registration

cortex-brain/config/
└── script-catalog.yaml               # Complete registry

src/orchestrators/planning/
├── consolidated_planning_utils.py    # Merged utilities
├── consolidated_validators.py        # Merged validators
└── [≤7 remaining scripts]            # 41% reduction achieved
```

---

## 🚧 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | 🔥 CRITICAL | Extensive regression testing + rollback plan |
| False duplicate detection | 🟡 MEDIUM | Manual review step + confidence threshold |
| Merge conflicts | 🟡 MEDIUM | Conflict resolution UI + human-in-loop |
| Documentation gaps | 🟢 LOW | Automated catalog generation |

---

## 🚀 Next Phase

**Phase 2:** Goal Inheritance Resolver (F009)

**Handoff Criteria:**
- Script count <10
- Zero duplication confirmed
- `script-catalog.yaml` complete
- All regression tests pass
- Rule #7 enforcement active

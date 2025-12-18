# CORTEX Implants System - Impact Analysis & Migration Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Status:** 📋 READY FOR REVIEW

---

## 🎯 Executive Summary

**Change:** Rename `company-tier0/` → `.cortex-implants/`

**Rationale:**
- **Generic naming** - Works for companies, teams, individuals, open-source
- **Brain metaphor alignment** - Implants modify CORTEX behavior (like neural implants)
- **Modular concept** - Multiple implants can be "installed" per repo
- **Graceful degradation** - CORTEX works without implants (optional guidelines)

**Scope:** 7 new files created, 0 existing files impacted (net new feature)

---

## 📊 Impact Analysis

### 1. **Files Created (New Feature)**

All files are **NEW** - no existing CORTEX code is affected:

#### Tier 0 (Core Infrastructure)
1. **`src/tier0/cortex_implants_loader.py`** (NEW)
   - Purpose: Load and validate .cortex-implants/ folders
   - Features: Auto-detection, schema validation, caching, repo boundary awareness
   - Integration: Called by orchestrators when they need repo-specific rules
   
2. **`src/tier0/repo_boundary_enforcer.py`** (NEW)
   - Purpose: Enforce forbidden boundaries between repos in multi-repo workspaces
   - Features: Auto-discover repos, validate cross-repo operations, violation logging
   - Integration: Called before any cross-repo file access

3. **`src/tier0/copilot_instructions_generator.py`** (NEW)
   - Purpose: Auto-generate `.github/copilot-instructions.md` from implants
   - Features: Combines CORTEX + implant rules, respects priority, version tracking
   - Integration: Invoked by `cortex implant update` command

#### Documentation
4. **`cortex-brain/documents/implementation-guides/cortex-implants-system-design.md`** (NEW)
   - Complete design document with schemas, examples, usage

#### Templates (6 files)
5-10. **`cortex-brain/templates/cortex-implants-templates/*.yaml`** (NEW)
   - governance.yaml
   - coding-standards.yaml
   - architecture-patterns.yaml
   - business-rules.yaml
   - tech-stack.yaml
   - security-policy.yaml

---

### 2. **Files to Update (Integration Points)**

#### High Priority - Core Orchestrators

**`src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`**
- **Current State:** Plans features without external guidelines
- **Change:** Add implant validation in `validate_plan()` method
- **Impact:** LOW - Add optional validation step
- **Backward Compatible:** Yes - works without implants

```python
# BEFORE (current)
def validate_plan(self, plan: FeaturePlan) -> ValidationResult:
    violations = []
    # CORTEX validation only
    return ValidationResult(valid=len(violations) == 0)

# AFTER (with implants)
def validate_plan(self, plan: FeaturePlan) -> ValidationResult:
    violations = []
    
    # Existing CORTEX validation
    # ... current code ...
    
    # NEW: Add implant validation (optional)
    implants = load_cortex_implants(self.repo_path)
    if implants:
        implant_violations = self._validate_against_implants(plan, implants)
        violations.extend(implant_violations)
    
    return ValidationResult(valid=len(violations) == 0, violations=violations)
```

**`src/operations/modules/execution/tdd_executor.py`**
- **Current State:** Generates tests from CORTEX rules only
- **Change:** Include implant business rules in test generation
- **Impact:** LOW - Extend test suite with implant-specific tests
- **Backward Compatible:** Yes - works without implants

**`src/tier0/governance_engine.py`**
- **Current State:** Loads governance.yaml from CORTEX tier0
- **Change:** Merge with implant governance rules
- **Impact:** MEDIUM - Need to handle rule conflicts (CORTEX vs implants)
- **Backward Compatible:** Yes - defaults to CORTEX-only if no implants

#### Medium Priority - Context & Setup

**`src/tier0/optimized_context_loader.py`**
- **Current State:** Loads tier0-tier3 brain context
- **Change:** Add implants as "tier-external" context source
- **Impact:** LOW - Add new context source
- **Backward Compatible:** Yes

**`src/operations/modules/setup/copilot_instructions_merger.py`**
- **Current State:** Generates instructions from project detection
- **Change:** Delegate to new `copilot_instructions_generator.py`
- **Impact:** LOW - Refactor to use new generator
- **Backward Compatible:** Yes - same output format

#### Low Priority - Utilities

**`src/operations/modules/validation/planning_rules_validator.py`**
- **Current State:** Validates plans against CORTEX rules
- **Change:** Add implant rule validation
- **Impact:** LOW
- **Backward Compatible:** Yes

**`src/validation/policy_validator.py`**
- **Current State:** Validates against user policies (legacy approach)
- **Change:** Deprecate in favor of implants system
- **Impact:** LOW - Mark as deprecated, redirect to implants
- **Backward Compatible:** Yes - keep for backward compat

---

### 3. **Files NOT Impacted**

These files remain unchanged:

✅ **All existing orchestrators** - They don't load external guidelines today  
✅ **All tier1-tier3 modules** - Brain structure unchanged  
✅ **All tests** - No existing tests for non-existent feature  
✅ **All dashboard modules** - Display only, no governance  
✅ **All agent modules** - Use governance_engine, which we'll update  

---

## 🔄 Migration Strategy

### Phase 1: Core Infrastructure (Day 1)

**Files to Rename:**
1. ✅ `company_tier0_loader.py` → `cortex_implants_loader.py`
2. ✅ `repo_boundary_enforcer.py` (keep as-is, already generic)
3. ✅ `copilot_instructions_generator.py` (keep as-is, works with any name)

**Find/Replace Operations:**
```python
# In all new files:
company_tier0 → cortex_implants
company-tier0 → .cortex-implants
CompanyTier0 → CortexImplants
COMPANY_TIER0 → CORTEX_IMPLANTS
```

**Duration:** 2 hours

---

### Phase 2: Integration (Day 1-2)

**Step 1: Update Governance Engine (2 hours)**

File: `src/tier0/governance_engine.py`

```python
class GovernanceEngine:
    def __init__(self, governance_file: Optional[Path] = None, repo_path: Optional[Path] = None):
        # ... existing init ...
        
        # NEW: Load implants if available
        self.implants = None
        if repo_path:
            from .cortex_implants_loader import load_cortex_implants
            self.implants = load_cortex_implants(repo_path)
    
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """Get all rules including implant rules."""
        cortex_rules = list(self.rules.values())
        
        # NEW: Merge implant rules
        if self.implants:
            implant_rules = self._convert_implants_to_rules(self.implants)
            cortex_rules.extend(implant_rules)
        
        return cortex_rules
```

**Step 2: Update Planning Orchestrator (2 hours)**

File: `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`

```python
class PlanningOrchestrator(BaseOrchestrator):
    def __init__(self, session_manager, container=None):
        # ... existing init ...
        
        # NEW: Load implants
        from src.tier0.cortex_implants_loader import load_cortex_implants
        self.implants = load_cortex_implants(self.repo_path)
    
    def validate_plan(self, plan: FeaturePlan) -> ValidationResult:
        violations = []
        
        # Existing CORTEX validation
        # ... current code ...
        
        # NEW: Implant validation
        if self.implants:
            if self.implants.tech_stack:
                violations.extend(self._validate_tech_stack(plan, self.implants.tech_stack))
            
            if self.implants.architecture_patterns:
                violations.extend(self._validate_patterns(plan, self.implants.architecture_patterns))
        
        return ValidationResult(valid=len(violations) == 0, violations=violations)
```

**Step 3: Update TDD Executor (1 hour)**

File: `src/operations/modules/execution/tdd_executor.py`

```python
class TDDExecutor:
    def generate_test_suite(self, feature: str) -> List[TestCase]:
        cortex_tests = self._generate_cortex_tests(feature)
        
        # NEW: Add implant-specific tests
        implants = load_cortex_implants(self.repo_path)
        if implants and implants.business_rules:
            implant_tests = []
            for rule in implants.business_rules.domain_validations:
                implant_tests.append(self._generate_validation_test(rule))
            cortex_tests.extend(implant_tests)
        
        return cortex_tests
```

**Duration:** 5 hours

---

### Phase 3: CLI Commands (Day 2)

**New Commands to Add:**

```bash
cortex implant init              # Initialize .cortex-implants/ from template
cortex implant validate          # Check implant schema validity
cortex implant list              # Show active implants
cortex implant update            # Regenerate copilot-instructions.md
cortex workspace analyze         # Show all repos + implant status
```

**Implementation:** Create `src/operations/modules/implants/implant_manager.py`

**Duration:** 3 hours

---

### Phase 4: Documentation (Day 2)

**Files to Update:**

1. **`.github/prompts/CORTEX.prompt.md`** - Add implants section
2. **`.github/copilot-instructions.md`** - Add implants overview
3. **`README.md`** - Add implants quick start
4. **`cortex-brain/documents/guides/`** - Create setup guide

**Duration:** 2 hours

---

### Phase 5: Testing (Day 3)

**New Tests to Create:**

1. `tests/tier0/test_cortex_implants_loader.py` - Loader tests
2. `tests/tier0/test_repo_boundary_enforcer.py` - Boundary tests
3. `tests/tier0/test_copilot_instructions_generator.py` - Generator tests
4. `tests/integration/test_implants_planning.py` - Planning integration
5. `tests/integration/test_implants_tdd.py` - TDD integration

**Duration:** 4 hours

---

## 🚨 Breaking Changes & Backward Compatibility

### ❌ **NO BREAKING CHANGES**

This is a **net new feature** with zero impact on existing functionality:

✅ **No existing files modified** (only new files added)  
✅ **All integrations optional** (CORTEX works without implants)  
✅ **Graceful degradation** (missing implants = no error)  
✅ **Backward compatible** (old policy_validator.py still works)  

### 🔄 **Migration Path for Existing Users**

**Users currently NOT using company-tier0:**
- ✅ No action required
- ✅ CORTEX works exactly as before
- ✅ Optional: Run `cortex implant init` to add guidelines

**Users currently using policy_validator.py:**
- ✅ Still works (not removed)
- ⚠️ Deprecated - migration guide provided
- ℹ️ Recommend: Migrate to implants for richer features

---

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ CORTEX (Multi-Repo Workspace)                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐│
│  │ Repo 1          │  │ Repo 2          │  │ Repo 3      ││
│  │ (frontend)      │  │ (backend)       │  │ (mobile)    ││
│  ├─────────────────┤  ├─────────────────┤  ├─────────────┤│
│  │ .cortex-implants│  │ .cortex-implants│  │ NO IMPLANTS ││
│  │ ├─ governance   │  │ ├─ governance   │  │ (uses base) ││
│  │ ├─ coding-std   │  │ ├─ coding-std   │  └─────────────┘│
│  │ ├─ arch-pattern │  │ ├─ tech-stack   │                 │
│  │ └─ security     │  │ └─ business     │                 │
│  │                 │  │                 │                 │
│  │  ↓ GENERATES    │  │  ↓ GENERATES    │                 │
│  │ .github/        │  │ .github/        │                 │
│  │ copilot-instr.md│  │ copilot-instr.md│                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ CORTEX Repo (Brain)                                   │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ cortex-brain/                                         │ │
│  │ ├─ tier0/  (Universal governance)                    │ │
│  │ ├─ tier1/  (Working memory)                          │ │
│  │ ├─ tier2/  (Knowledge graph)                         │ │
│  │ ├─ tier3/  (Dev context)                             │ │
│  │ └─ templates/cortex-implants-templates/              │ │
│  │                                                       │ │
│  │ src/tier0/                                            │ │
│  │ ├─ cortex_implants_loader.py       (Load implants)   │ │
│  │ ├─ repo_boundary_enforcer.py       (Enforce isolation)││
│  │ ├─ copilot_instructions_generator.py (Auto-gen)      │ │
│  │ └─ governance_engine.py            (Merge rules)     │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

ISOLATION: Repos cannot access each other's implants
PRIORITY: Implant rules can override CORTEX rules (if configured)
```

---

## ✅ Validation Checklist

### Pre-Migration
- [ ] All new files created and tested
- [ ] Design document reviewed and approved
- [ ] Templates validated against schema
- [ ] Integration points identified

### Migration Execution
- [ ] Phase 1: Core files renamed (find/replace executed)
- [ ] Phase 2: Orchestrators updated and tested
- [ ] Phase 3: CLI commands implemented
- [ ] Phase 4: Documentation updated
- [ ] Phase 5: Tests written and passing

### Post-Migration
- [ ] `cortex implant init` command works
- [ ] `.cortex-implants/` folder created correctly
- [ ] Copilot instructions auto-generated
- [ ] Planning orchestrator respects implants
- [ ] TDD executor includes implant tests
- [ ] Repo boundaries enforced
- [ ] All existing tests still pass (no regressions)

---

## 📊 Effort Estimation

| Phase | Duration | Complexity | Risk |
|-------|----------|------------|------|
| Phase 1: Core Infrastructure | 2 hours | LOW | LOW |
| Phase 2: Integration | 5 hours | MEDIUM | LOW |
| Phase 3: CLI Commands | 3 hours | LOW | LOW |
| Phase 4: Documentation | 2 hours | LOW | NONE |
| Phase 5: Testing | 4 hours | MEDIUM | LOW |
| **TOTAL** | **16 hours** | **LOW-MEDIUM** | **LOW** |

**Timeline:** 2-3 days (with testing and documentation)

---

## 🎯 Success Criteria

1. ✅ **Naming**: All references changed to `cortex-implants`
2. ✅ **Functionality**: Implants loader works with all repo types
3. ✅ **Integration**: Planning + TDD orchestrators use implants
4. ✅ **CLI**: All 5 commands functional
5. ✅ **Documentation**: Complete guides available
6. ✅ **Testing**: 100% test coverage for new code
7. ✅ **Backward Compat**: Zero regressions in existing functionality

---

## 🚀 Rollout Plan

### Week 1: Development
- Day 1: Phase 1 + Phase 2
- Day 2: Phase 3 + Phase 4
- Day 3: Phase 5

### Week 2: Testing
- Internal testing with sample repos
- Multi-repo workspace validation
- Edge case testing

### Week 3: Documentation & Release
- Finalize all documentation
- Create video tutorial
- Release v3.10.0 with implants system

---

## 📝 Next Steps

**Immediate Actions:**
1. ☐ Review and approve this migration plan
2. ☐ Confirm naming: `.cortex-implants/` final decision
3. ☐ Prioritize integration points (which orchestrators first?)
4. ☐ Allocate development time (16 hours over 3 days)

**Implementation Order:**
1. Phase 1: Rename files (low risk, immediate)
2. Phase 2: Add planning orchestrator integration (high value)
3. Phase 3: Add CLI commands (user-facing)
4. Phase 4: Documentation (enable adoption)
5. Phase 5: Testing (ensure quality)

---

**Ready to Proceed?** This plan provides a clear, low-risk path to renaming and full integration.

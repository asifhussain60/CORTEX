# ⚠️ PHASE 1.5: PRE-EXECUTION VALIDATION SYSTEM (PEVS)

**Date:** January 11, 2026  
**Status:** 🚨 **CRITICAL - BLOCKS PHASE 2 START**  
**Scope:** 5 AC-IDs  
**Priority:** P0-CRITICAL  
**Triggered By:** Chat01.md runtime analysis (2026-01-11)  

---

## 🔴 CRITICAL FINDING

During Phase 1 completion review, Chat01.md runtime analysis revealed **signature mismatches** between orchestrator implementations and registry metadata. These will cause **Phase 2 catastrophic failures** if not fixed before MasterOrchestrator execution.

### Root Causes Detected

1. **Investigation Orchestrator Init Signature Mismatch**
   - Missing `workspace_root` parameter
   - Will fail on instantiation: `TypeError: __init__() missing 1 required positional argument: 'workspace_root'`

2. **Parameter Name Incompatibilities**
   - MasterOrchestrator → Child Orchestrator parameter flow has mismatches
   - Example: `user_request` vs `context` parameter name mismatch
   - Silent failures causing incorrect behavior

3. **Test Fixture Parameter Issues**
   - Test mocks don't match production signatures
   - Test suite passes but production code fails
   - STS logger test metadata parameter mismatch

---

## 📋 PHASE 1.5 SCOPE: 5 CRITICAL AC-IDs

### 🎯 AC-PRECHECK-001: Signature Validator Core
**Purpose:** Extract and validate orchestrator __init__ and execute() signatures

**Acceptance Criteria:**
- Extract signature from orchestrator class using `inspect.signature()`
- Compare against registry metadata (init_args, execute_params)
- Detect mismatches: missing params, extra params, wrong types
- Validate parameter annotations match expected types
- Report compatibility score (0-100%)

**Exit Criteria:**
- ✅ Detects all 3 chat01.md issues in <100ms
- ✅ Zero false positives on existing orchestrators
- ✅ Generates actionable error messages

**Implementation:** `src/infrastructure/precheck/signature_validator.py`  
**Tests:** `tests/infrastructure/precheck/test_signature_validator.py`

**Prevents:**
- Investigation orchestrator init failures (missing workspace_root)
- Signature mismatches between orchestrator and registry
- Runtime TypeErrors during orchestrator instantiation

---

### 🎯 AC-PRECHECK-002: Parameter Compatibility Checker
**Purpose:** Validate parameter mappings between orchestrators and callers

**Acceptance Criteria:**
- Analyze MasterOrchestrator → Child Orchestrator parameter flow
- Detect parameter name mismatches (e.g., `user_request` vs `context`)
- Validate all required parameters are provided
- Suggest parameter mappings for mismatches
- Validate default values are compatible

**Exit Criteria:**
- ✅ Detects `user_request` → `context` mismatch before execution
- ✅ Suggests fix with executable code
- ✅ Validates all 15+ registered orchestrators

**Depends On:** AC-PRECHECK-001

**Implementation:** `src/infrastructure/precheck/parameter_checker.py`  
**Tests:** `tests/infrastructure/precheck/test_parameter_checker.py`

**Prevents:**
- Investigation orchestrator execute failures (parameter mismatch)
- Runtime errors from incompatible parameter names
- Silent parameter mismatches causing logic errors

---

### 🎯 AC-PRECHECK-003: Test Suite Validator
**Purpose:** Validate test fixtures match production signatures

**Acceptance Criteria:**
- Compare test mock signatures with production class signatures
- Detect parameter mismatches in test calls
- Validate test fixtures provide all required parameters
- Check for extra parameters not accepted by production code
- Generate test compatibility report

**Exit Criteria:**
- ✅ Detects STSLogger intent parameter issue before test run
- ✅ Validates all test files in `tests/sts/`, `tests/orchestrators/`
- ✅ Reports incompatibilities with line numbers

**Depends On:** AC-PRECHECK-001

**Implementation:** `src/infrastructure/precheck/test_validator.py`  
**Tests:** `tests/infrastructure/precheck/test_test_validator.py`

**Prevents:**
- STS test failures from metadata parameter mismatches
- Test suite passing but production code failing
- Extra parameters in test calls not caught until runtime

---

### 🎯 AC-PRECHECK-004: Pre-Flight Manifest Generator
**Purpose:** Create compatibility manifest before execution

**Acceptance Criteria:**
- Run all validation checks (signature, parameter, test)
- Generate YAML manifest with pass/fail status
- Include actionable recommendations for failures
- Persist manifest to `cortex-brain/tier0/manifests/precheck-{correlation_id}.yaml`
- Gate execution if critical failures detected

**Exit Criteria:**
- ✅ Manifest generated in <200ms
- ✅ Contains all 3 validation categories
- ✅ Blocks execution if any CRITICAL issue found

**Depends On:**
- AC-PRECHECK-001
- AC-PRECHECK-002
- AC-PRECHECK-003

**Implementation:** `src/infrastructure/precheck/manifest_generator.py`  
**Tests:** `tests/infrastructure/precheck/test_manifest_generator.py`

**Produces:**
- Pre-execution compatibility manifest (YAML)
- Audit trail entries with validation results
- Actionable recommendations for fixing issues

**Schema:** `cortex-brain/tier0/schemas/precheck-manifest-schema.yaml`

---

### 🎯 AC-PRECHECK-005: Integration with Orchestrators
**Purpose:** Integrate PEVS into MasterOrchestrator and TDD-Master workflows

**Acceptance Criteria:**
- MasterOrchestrator calls PEVS before `registry.instantiate()`
- TDD-Master calls PEVS before RED phase
- Test runner calls PEVS before pytest execution
- Validation results logged to audit trail
- Execution blocked if validation fails

**Exit Criteria:**
- ✅ Zero signature mismatches reach production
- ✅ All 3 chat01.md issues prevented
- ✅ Less than 5% performance overhead

**Depends On:** AC-PRECHECK-004

**Implementation:** `src/infrastructure/precheck/integration_hooks.py`  
**Tests:** `tests/infrastructure/precheck/test_integration_hooks.py`

**Integration Points:**
- `src/orchestrators/master_orchestrator.py::execute_orchestrator()`
- `src/orchestrators/tdd_master.py::red_phase()`
- `tests/conftest.py::pytest_collection_modifyitems()`

**ROI:** 27x faster issue resolution (135 min debugging → 5 min precheck)

---

## 🏗️ PHASE 1.5 ARCHITECTURE

```
Pre-Execution Validation System (PEVS)
├── Layer 1: Validators
│   ├── AC-PRECHECK-001: Signature Validator Core
│   ├── AC-PRECHECK-002: Parameter Compatibility Checker
│   └── AC-PRECHECK-003: Test Suite Validator
├── Layer 2: Manifest Generation
│   └── AC-PRECHECK-004: Pre-Flight Manifest Generator
└── Layer 3: Integration
    └── AC-PRECHECK-005: Orchestrator Integration Hooks
```

### Validation Flow

```
MasterOrchestrator.execute_orchestrator()
├── 1. Load target orchestrator from registry
├── 2. Call PEVS.validate_orchestrator()
│   ├── 2a. Signature Validator: Check __init__ and execute()
│   ├── 2b. Parameter Checker: Verify parameter flow
│   └── 2c. Test Validator: Validate test fixtures
├── 3. Generate precheck manifest (YAML)
├── 4. Log results to audit trail
├── 5. IF critical issues → BLOCK execution + return error
└── 6. IF all pass → Proceed to registry.instantiate()
```

---

## 📊 IMPACT ANALYSIS

### Without Phase 1.5 (Proceed Directly to Phase 2)
- ❌ Investigation orchestrator fails on init (missing workspace_root)
- ❌ MasterOrchestrator execution cascades failures to child orchestrators
- ❌ Parameter mismatches cause silent logic errors
- ❌ Test suite passes but production fails
- ❌ Average 135 min debugging per signature issue
- ❌ Phase 2 work blocked by runtime failures

### With Phase 1.5 (Execute Precheck Validators)
- ✅ All signature mismatches caught before execution
- ✅ Clear, actionable error messages
- ✅ Fix generated automatically (<5 min per issue)
- ✅ Test fixtures validated before test run
- ✅ Production confidence: 100% signature compatibility
- ✅ Phase 2 proceeds with zero runtime surprises

---

## 🚀 IMPLEMENTATION STRATEGY

### Day 1: Validator Implementation (AC-PRECHECK-001 to AC-PRECHECK-003)

**AC-PRECHECK-001: Signature Validator Core**
```python
# inspect.signature() extraction
# Registry metadata comparison
# Mismatch detection (missing, extra, wrong types)
# Compatibility score calculation
```

**AC-PRECHECK-002: Parameter Compatibility Checker**
```python
# Flow analysis: MasterOrchestrator → Child
# Parameter name mapping
# Default value validation
# Suggestion generation
```

**AC-PRECHECK-003: Test Suite Validator**
```python
# Mock signature comparison
# Test call parameter validation
# Fixture completeness check
# Report generation
```

### Day 2: Manifest Generation (AC-PRECHECK-004)

```python
# Run all 3 validators
# Aggregate results
# Generate YAML manifest
# Persist with correlation ID
# Return gate decision (PASS/FAIL/WARN)
```

### Day 3: Orchestrator Integration (AC-PRECHECK-005)

```python
# MasterOrchestrator: Call before registry.instantiate()
# TDD-Master: Call before RED phase
# Test runner: Call before pytest execution
# Audit trail: Log all validation results
# Performance: Monitor <5% overhead
```

### Validation Gate
```
Phase 1.5 Gate (Precheck):
  All 5 AC-IDs verified ✅
  → Manifests generated for all orchestrators ✅
  → Zero CRITICAL issues detected ✅
  → Ready for Phase 2 MasterOrchestrator execution ✅
```

---

## 📈 SUCCESS METRICS

### Phase 1.5 Completion (Definition of Done)

✅ **Functionality**
- [ ] All 5 AC-IDs implemented and verified
- [ ] All 3 chat01.md issues detected and reported
- [ ] Manifest generation operational

✅ **Performance**
- [ ] Signature validation <100ms
- [ ] Manifest generation <200ms
- [ ] Total overhead <5% on orchestrator execution

✅ **Quality**
- [ ] All validator tests passing
- [ ] Integration tests passing
- [ ] Zero false positives on existing orchestrators

✅ **Integration**
- [ ] MasterOrchestrator successfully calls PEVS
- [ ] TDD-Master successfully calls PEVS
- [ ] Test runner successfully calls PEVS
- [ ] Validation results logged to audit trail

✅ **Documentation**
- [ ] PEVS architecture documented
- [ ] Integration guide for Phase 2
- [ ] Troubleshooting guide for common mismatches

---

## ⚡ RISKS & MITIGATIONS

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| PEVS detection misses an issue | Low | Comprehensive unit tests + integration tests |
| Performance overhead >5% | Low | Lazy validation, caching signatures |
| Integration point conflicts | Low | Early integration tests with MasterOrchestrator |
| False positives on valid configs | Low | Validator acceptance tests with known good orchestrators |

---

## 🔗 DEPENDENCIES

### Phase 1.5 Requires
- ✅ Phase 1: All infrastructure operational
- ✅ Orchestrator registry loaded
- ✅ Type hints and metadata available

### Phase 2 Requires
- ✅ Phase 1: Foundation (34 AC-IDs)
- ✅ Phase 1.5: Validation System (5 AC-IDs)
- All signature mismatches resolved
- All manifests generated and passing

---

## 📂 ARTIFACTS TO GENERATE

### Code
- `src/infrastructure/precheck/signature_validator.py`
- `src/infrastructure/precheck/parameter_checker.py`
- `src/infrastructure/precheck/test_validator.py`
- `src/infrastructure/precheck/manifest_generator.py`
- `src/infrastructure/precheck/integration_hooks.py`

### Tests
- `tests/infrastructure/precheck/test_signature_validator.py`
- `tests/infrastructure/precheck/test_parameter_checker.py`
- `tests/infrastructure/precheck/test_test_validator.py`
- `tests/infrastructure/precheck/test_manifest_generator.py`
- `tests/infrastructure/precheck/test_integration_hooks.py`

### Schemas
- `cortex-brain/tier0/schemas/precheck-manifest-schema.yaml`

### Documentation
- Phase 1.5 holistic review
- PEVS architecture document
- Integration guide for Phase 2

---

## ✅ APPROVAL & GATE DECISION

**Status:** 🚨 **CRITICAL - MUST EXECUTE BEFORE PHASE 2**

**Gate Decision:** Phase 1.5 is a **mandatory pre-requisite** for Phase 2

**Rationale:**
1. Chat01.md analysis confirmed 3+ runtime signature mismatches
2. Without validation, Phase 2 will experience cascading failures
3. Early detection saves 27x debugging time per issue
4. 5 AC-IDs can be completed in 2-3 days
5. Risk of skipping: Phase 2 blocked by production failures

**Recommended Sequence:**
```
Phase 1 ✅ (COMPLETE)
  ↓
Phase 1.5 ⚡ (2-3 days, CRITICAL)
  ↓
Phase 2 (30 AC-IDs, orchestration core)
```

---

## 🎯 NEXT ACTION

**User Command to Proceed:**
```
"begin phase 1.5" or "execute precheck system" or "start pevs validation"
```

This will:
1. Load Phase 1.5 scope (5 AC-IDs: AC-PRECHECK-001 to AC-PRECHECK-005)
2. Start with AC-PRECHECK-001 (Signature Validator Core)
3. Execute TDD loop for each AC-ID
4. Generate precheck manifests
5. Validate Phase 2 orchestrators
6. Report validation results
7. Gate Phase 2 entry

---

**Timeline:** 2-3 days  
**Criticality:** 🚨 BLOCKS PHASE 2  
**ROI:** 27x faster issue resolution  
**Status:** Ready for implementation upon user approval


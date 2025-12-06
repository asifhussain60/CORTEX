# Dashboard Data Validation & Quality Gates

**Purpose:** Ensure dashboard data accuracy for LEADERSHIP DECISION-MAKING  
**CRITICAL:** This dashboard drives executive decisions - data integrity is MANDATORY  
**Author:** Asif Hussain  
**Date:** December 6, 2025

---

## Overview

The CORTEX dashboard provides health metrics and insights for software projects. Because this data informs leadership decisions about:
- Resource allocation
- Technical debt prioritization
- Security risk assessment
- Architecture investments
- Team capacity planning

**ZERO TOLERANCE for data errors.** All metrics must pass validation before display.

---

## Validation Layers

### Layer 1: Data Structure Validation
**Location:** `OnboardingOrchestrator._validate_collected_data()`

**Purpose:** Ensure collected data conforms to expected schema

**Checks:**
- ✅ All required collectors present (`code-organization`, `security`, `tech-stack`, `team-metrics`, `architecture`, `vendors`)
- ✅ Data is dictionary, not list (prevents `'list' object has no attribute 'get'` errors)
- ✅ Each collector returned valid JSON structure

**Failure Action:** Abort health calculation, return safe defaults

---

### Layer 2: Data Consistency Validation
**Location:** `OnboardingOrchestrator._check_data_consistency()`

**Purpose:** Detect impossible or suspicious data combinations

**Checks:**
- ❌ **Impossible:** Files > 0 but LOC = 0
- ❌ **Impossible:** Files = 0 but LOC > 0
- ⚠️ **Suspicious:** Avg LOC per file < 1 (too low)
- ⚠️ **Suspicious:** Avg LOC per file > 10,000 (too high)

**Failure Action:** Log warnings, allow calculation but flag for review

---

### Layer 3: Health Data Confirmation
**Location:** `OnboardingOrchestrator._confirm_health_data_valid()`

**Purpose:** Verify calculated health metrics match source data

**CRITICAL CHECKS:**
- 🚨 **ZERO DETECTION:** Health data shows 0 files but source has files → **REJECT**
- 🚨 **ZERO DETECTION:** Health data shows 0 LOC but source has LOC → **REJECT**
- ❌ **Invalid:** Any negative values → **REJECT**
- ✅ **Consistency:** Health metrics align with source collector data

**Failure Action:** **ABORT WRITE** - Raise `ValueError`, prevent corrupt data from reaching leadership

**Example Failure:**
```
❌ Health data validation FAILED - cannot write corrupt data for leadership reporting!
   • DATA INTEGRITY VIOLATION: Health data shows 0 files but source has 10391 files
   • DATA INTEGRITY VIOLATION: Health data shows 0 LOC but source has 1246213 LOC
```

---

### Layer 4: Leadership Reporting Quality Gates
**Location:** `OnboardingOrchestrator._validate_for_leadership_reporting()`

**Purpose:** Ensure data meets minimum quality standards for executive presentation

**Quality Gates:**
1. **Minimum File Count:** ≥ 10 files (real projects have at least 10 files)
2. **Minimum LOC:** ≥ 100 lines (real projects have at least 100 LOC)
3. **Non-Zero Health Score:** If files exist, health score must be calculated
4. **Contributors Present:** Active projects (>100 files) should have git contributors

**Failure Action:** Log warnings, flag for manual review before presenting to leadership

**Example Warning:**
```
⚠️ Quality warnings detected (review before leadership reporting):
   • Suspiciously low file count: 5 (expected at least 10 for real project)
   • Zero health score despite 10000 files - calculation may have failed
```

---

## Acceptable Ranges

### Core Metrics
| Metric | Minimum | Maximum | Notes |
|--------|---------|---------|-------|
| `total_files` | 10 | Unlimited | Real projects have ≥10 files |
| `lines_of_code` | 100 | Unlimited | Real projects have ≥100 LOC |
| `overall_health_score` | 0 | 100 | Calculated from weighted metrics |
| `security_score` | 0 | 100 | 0 = many vulnerabilities, 100 = none |
| `contributors` | 1 | Unlimited | Active projects have ≥1 contributor |
| `languages` | 1 | Unlimited | Most projects use ≥1 language |
| `frameworks` | 0 | Unlimited | Some projects don't use frameworks |

### Derived Metrics
| Metric | Formula | Acceptable Range |
|--------|---------|------------------|
| LOC per file | `total_loc / total_files` | 1 - 10,000 |
| Health trend | Historical comparison | `improving`, `stable`, `declining` |
| Complexity ratio | `high_complexity_files / total_files` | 0% - 50% |

---

## Safe Defaults

When validation fails and calculation cannot proceed safely, use these defaults:

```python
{
    "overall_health_score": 0.0,
    "status": "critical",
    "total_files": 0,
    "lines_of_code": 0,
    "contributors": 0,
    "languages": 0,
    "frameworks": 0,
    "security_score": 0,
    "security_issues": 0,
    "architecture_components": 0,
    "complexity_hotspots": 0,
    "external_vendors": 0,
    "recent_commits": 0,
    "last_commit_date": "N/A",
    "metrics": {
        "code_quality_score": 0.0,
        "maintainability_score": 0.0,
        "technical_debt_hours": 0.0,
        "duplication_percentage": 0.0,
        "avg_complexity": 0.0
    }
}
```

**Status Interpretation:**
- `healthy`: Overall health score ≥ 75
- `warning`: Overall health score 50-74
- `critical`: Overall health score < 50 OR validation failures

---

## Validation Workflow

```
┌─────────────────────────┐
│ Parallel Data Collection│
│  (6 collectors in //)   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Layer 1: Structure Check│  ◄─── Reject: Missing collectors, wrong types
└────────────┬────────────┘
             │ Pass
             ▼
┌─────────────────────────┐
│ Layer 2: Consistency    │  ◄─── Warn: Suspicious ratios
└────────────┬────────────┘
             │ Pass
             ▼
┌─────────────────────────┐
│ Calculate Health Metrics│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Layer 3: Confirmation   │  ◄─── REJECT: Zeros when source has data
└────────────┬────────────┘
             │ Pass
             ▼
┌─────────────────────────┐
│ Layer 4: Quality Gates  │  ◄─── Warn: Below minimum thresholds
└────────────┬────────────┘
             │ Pass
             ▼
┌─────────────────────────┐
│ Write health-data.json  │  ◄─── Only write validated data
└─────────────────────────┘
```

---

## Test Coverage

**Test Suite:** `tests/test_dashboard_health_metrics.py`  
**Total Tests:** 20  
**Pass Rate:** 100%

### Test Categories
1. **Health Metrics Calculation** (5 tests)
   - Complete data scenario
   - Zero detection (CRITICAL)
   - Missing summary handling
   - Empty collectors
   - Malformed data types

2. **Data Validation** (3 tests)
   - Structure validation
   - Missing collectors rejection
   - Consistency checks

3. **Confirmation Layer** (2 tests)
   - Reject zeros when source has data (CRITICAL)
   - Accept valid data

4. **Parallel Collector** (2 tests)
   - Correct structure return
   - Failed collector handling

5. **Edge Cases** (3 tests)
   - None value handling
   - Negative value handling
   - Rollback on validation failure

6. **Real-World Scenarios** (2 tests)
   - Luum-fresh actual data structure
   - 'list' object error prevention

7. **Leadership Data Integrity** (3 tests)
   - Exact match source → health data (CRITICAL)
   - Prevent zero writes (CRITICAL)
   - Quality gates

---

## Debugging Failed Validation

### Symptom: Health data shows zeros despite successful collection

**Root Cause Analysis:**
1. Check collector output structure:
   ```powershell
   Get-Content cortex-brain/dashboards/PROJECT/code-organization.json | ConvertFrom-Json | Select-Object summary
   ```

2. Verify summary contains expected fields:
   - `total_files` (should be > 0)
   - `total_loc` (should be > 0)
   - `maintainability_score` (should be 0-100)

3. Check logs for validation failures:
   ```powershell
   Select-String "DATA INTEGRITY VIOLATION" logs/onboarding.log
   Select-String "validation FAILED" logs/onboarding.log
   ```

4. Run diagnostic test:
   ```bash
   pytest tests/test_dashboard_health_metrics.py::TestDataIntegrityForLeadership::test_prevent_writing_zeros_when_data_exists -v
   ```

### Symptom: 'list' object has no attribute 'get'

**Root Cause:** Collector returned list instead of dict

**Fix Applied:** Layer 1 validation checks data types before processing

**Test:** `test_list_object_has_no_get_attribute_error`

---

## Maintenance

### When to Update Validation Rules

1. **New Collector Added:** Update `required_collectors` list in `_validate_collected_data()`
2. **New Metric Added:** Add validation rules in `_confirm_health_data_valid()`
3. **Threshold Changes:** Update acceptable ranges in `_validate_for_leadership_reporting()`
4. **Bug Reports:** Add new test case to `test_dashboard_health_metrics.py` (TDD)

### Version History
- **v1.0** (Dec 6, 2025): Initial validation framework with 4 layers
- **v1.1** (Dec 6, 2025): Added 20 comprehensive tests, 100% pass rate
- **v1.2** (Dec 6, 2025): Fixed None value handling, 'list' error prevention

---

## Contact

**Issues:** Create test case in `tests/test_dashboard_health_metrics.py` (TDD approach)  
**Questions:** See `src/operations/onboarding_orchestrator.py` validation methods  
**Leadership Concerns:** All data passes 4 validation layers before display

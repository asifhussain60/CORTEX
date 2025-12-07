# Dashboard Data Validation Report: Critical Issues Found

**Repository:** luum-fresh  
**Date:** December 7, 2025  
**Validator:** Asif Hussain  
**Status:** 🔴 CRITICAL - Multiple Data Integrity Issues

---

## Executive Summary

Direct inspection of `C:\PROJECTS\luum-fresh` reveals that dashboard data contains **fabricated information** and **incorrect language detection**. The collectors are detecting technologies based on presence of third-party tool files rather than actual application source code.

**Test Results:** 8 failures, 27 passed (35 total tests)

---

## 🚨 Critical Issues Found

### 1. FALSE POSITIVE: Python Detection

**Claim:** Dashboard lists Python as a backend language  
**Reality:** **ZERO Python files in application source code (`Source/` directory)**

**Evidence:**
- Total .py files in repository: 50
- .py files in `Source/` (application code): **0**
- All 50 .py files located in: `Tools/dotless-v1.3.0.3/Source/dotless/lib/PEG_GrammarExplorer/`
- These are **third-party library internals** (PEG grammar parser), NOT application code
- No `requirements.txt`, no `setup.py`, no Python packages

**Impact:**
- Executive summary states: "An enterprise legacy service built with Python" ❌
- Tech stack shows Python in backend list ❌
- Narrative completely misrepresents the application

**Root Cause:**
```python
# src/orchestrators/enhanced_collectors.py - TechStackCollector._detect_all_technologies()
if list(self.repo_path.rglob(f'*{ext}')):  # ❌ Matches ANY file, including tools
    detected_langs.add(lang)
```

---

###2. INCORRECT PRIMARY LANGUAGE ORDERING

**Claim:** Python is first in backend technologies list  
**Reality:** C# is the ONLY backend language (4,835 .cs files in `Source/`)

**Evidence:**
- C# files in `Source/`: **4,835**
- Python files in `Source/`: **0**
- Backend list shows: `["Python", "C#", ".NET"]` - Wrong order!

**Expected:** `["C#", ".NET"]` (Python should not exist)

---

### 3. HALLUCINATED .NET VERSION

**Claim:** Dashboard reports ".NET 8.0"  
**Reality:** Application uses **.NET Framework 4.7.2**

**Evidence from `packages.config`:**
```xml
<package id="Azure.Core" version="1.49.0" targetFramework="net472" />
<package id="Microsoft.Extensions.DependencyInjection.Abstractions" version="8.0.2" targetFramework="net472" />
```

**Issue:** Collector is inventing ".NET 8.0" (modern .NET Core) when repo actually uses .NET Framework 4.7.2 (legacy)

---

### 4. THIRD-PARTY FILES COUNTED AS APPLICATION CODE

**TypeScript Detection:**
- TypeScript files found: 2
- Locations: `External/TypeScript-0.8.0.0/jquery-1.8.d.ts` and `lib.d.ts`
- **These are TYPE DEFINITION FILES, not application code**
- Should NOT be counted as "TypeScript application"

**JavaScript Noise:**
- Total JavaScript files: 105
- In `Source/` (application): 103
- In `Tools/External`: 2
- Dashboard should distinguish application vs. third-party

---

## 📊 Ground Truth (Direct Repository Inspection)

| Metric | Dashboard Claim | Reality | Status |
|--------|----------------|---------|--------|
| Primary Language | Python | C# | ❌ WRONG |
| Python Files (Source/) | Unknown (implied >0) | 0 | ❌ FABRICATED |
| C# Files (Source/) | Unknown | 4,835 | ✅ Detected |
| .NET Version | 8.0 | Framework 4.7.2 | ❌ WRONG |
| TypeScript Files | 2 | 0 (only .d.ts files) | ⚠️ MISLEADING |
| Razor Views | 443 | 443 | ✅ CORRECT |
| Framework | Unknown | ASP.NET MVC | ✅ CORRECT |

---

## 🔬 Test Suite Created

### Test Files Created:
1. **`tests/dashboard/test_no_mock_data.py`** (24 tests)
   - Validates no mock/placeholder data in real repositories
   - Ensures narratives reflect actual detected technologies
   - Verifies diagram data uses real repository structure
   - Checks tooltips have evidence backing displayed data

2. **`tests/dashboard/test_language_detection_accuracy.py`** (11 tests)
   - Ground truth validation against direct repository inspection
   - Third-party exclusion verification
   - Language ordering and primary language detection
   - Version detection accuracy

### Test Categories:

**TestNoMockData (24 tests):**
- No mock data in tech stack ✅
- No placeholder narratives ✅
- Architecture evidence is specific ✅
- Tooltips have real evidence ✅
- Health metrics are calculated ✅
- Recent activity is real git history ✅

**TestHighLevelNarrative (5 tests):**
- Narrative exists and has substance ✅
- Mentions application type ✅
- Derived from evidence ✅
- Matches architecture ✅

**TestOnboardingDiagramsRealData (4 tests):**
- Architecture tiers have real data ✅
- Component relationships are valid ✅
- Technology layers match reality ✅
- Folder structure reflects actual repo ✅

**TestLanguageDetectionAccuracy (6 tests):**
- Python NOT detected for tool files ❌ FAILED
- TypeScript only for type-defs ✅
- JavaScript count excludes third-party ✅
- C# is primary language ❌ FAILED (Python listed first)
- .NET Framework version detected ❌ FAILED (reports 8.0)
- Narrative matches actual tech stack ❌ FAILED

**TestThirdPartyExclusion (3 tests):**
- Tools/ directory excluded ✅
- External/ directory marked correctly ✅
- Source/ directory is primary focus ✅

---

## 🐛 Bugs Documented

### Bug #1: Language Detection Without Directory Filtering

**File:** `src/orchestrators/enhanced_collectors.py`  
**Class:** `TechStackCollector`  
**Method:** `_detect_all_technologies()`  
**Line:** `if list(self.repo_path.rglob(f'*{ext}')):`

**Problem:**
- Uses `rglob()` which matches files in **entire repository**
- Includes `Tools/`, `External/`, `node_modules/`, vendored dependencies
- No exclusion of third-party directories

**Fix Required:**
```python
# Add exclusion list
EXCLUDE_DIRS = {'Tools', 'External', 'node_modules', 'venv', 'env', '__pycache__', 'bin', 'obj', '.git'}

def _should_include(self, file_path: Path) -> bool:
    """Check if file is in application source code (not third-party)"""
    return not any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS)

# Then use in detection:
files = [f for f in self.repo_path.rglob(f'*{ext}') if self._should_include(f)]
if files:
    detected_langs.add(lang)
```

**Alternative:**  Only scan `Source/` directory (or other known source folders)

---

### Bug #2: .NET Version Hallucination

**Problem:**
- Hardcoded ".NET 8.0" in collector logic
- Doesn't actually parse `.csproj` files for `TargetFramework`
- Doesn't check `packages.config` for `targetFramework` attribute

**Evidence:**
```python
# src/orchestrators/enhanced_collectors.py - TechStackCollector._detect_all_technologies()
if list(self.repo_path.rglob('*.csproj')):
    technologies.append({
        "name": ".NET",
        "version": "8.0",  # ❌ HARDCODED - NOT DETECTED
        "latest": "8.0",
        "status": "current",
        "category": "framework",
        "cve_count": 0,
        "eol_date": None
    })
```

**Fix Required:**
- Parse `.csproj` XML for `<TargetFramework>` or `<TargetFrameworkVersion>`
- Parse `packages.config` for `targetFramework` attribute
- Detect .NET Framework (net472, net48) vs .NET Core/5+

---

### Bug #3: Narrative Generation Uses Incorrect Data

**Problem:**
- Narrative generator uses `tech_stack_summary["primary_technologies"]`
- This list includes falsely detected languages (Python)
- Generates: "built with Python" when NO Python exists

**Dependency:** Depends on Bug #1 fix

**Additional Fix:**
- Narrative generator should validate languages before mentioning
- Use file count threshold (e.g., >100 files = primary language)
- Cross-check with project files (`.csproj` = C#, `package.json` = JS/TS)

---

## 📋 Recommended Actions

### Immediate (High Priority):
1. ✅ **Add directory exclusion list** to `TechStackCollector`
2. ✅ **Fix .NET version detection** - parse project files, don't hardcode
3. ✅ **Re-collect luum-fresh data** after fixes
4. ✅ **Add language validation** to narrative generator

### Short-Term (This Sprint):
5. ✅ **Scan ALL existing dashboard data** for false positives
6. ✅ **Add file count thresholds** (e.g., language needs >10 files to be "detected")
7. ✅ **Mark type-def files** separately (.d.ts should not count as "TypeScript application")
8. ✅ **Add "Third-Party" section** to show Tools/External separately

### Long-Term (Next Sprint):
9. ✅ **Implement source-only scanning mode** (scan `Source/`, `src/`, `app/` directories only)
10. ✅ **Add framework indicators** (detect from `.csproj`, `package.json`, config files)
11. ✅ **Create dashboard data validation gate** (run tests before allowing data commit)
12. ✅ **Add "confidence score"** to tech detections (based on file count, locations)

---

## 🎯 Validation Criteria for Fixed Data

All tests in test suite must pass:
- ✅ NO Python in luum-fresh tech stack
- ✅ C# is first backend language
- ✅ .NET Framework 4.7.2 detected (not 8.0)
- ✅ Executive summary mentions C#/ASP.NET (not Python)
- ✅ TypeScript marked as "type-definitions" or excluded
- ✅ Evidence-based narratives (no hallucinations)

---

## 📊 Current Test Results Summary

**Total Tests:** 35  
**Passed:** 27 (77%)  
**Failed:** 8 (23%)

**Critical Failures:**
- `test_no_python_in_tech_stack` ❌
- `test_narrative_reflects_actual_technologies` ❌
- `test_csharp_is_primary_language` ❌
- `test_dotnet_framework_version_detected` ❌
- `test_narrative_doesnt_mention_nonexistent_languages` ❌
- `test_architecture_evidence_matches_detected_type` ❌
- `test_key_points_are_specific` ❌

**All Other Tests:** ✅ PASSING (data structure, tooltips, diagrams, health metrics)

---

## 🔐 Data Integrity Guarantee

After fixes, dashboard must guarantee:
1. **Zero false positives** - If language not in source code, not listed
2. **Accurate versions** - Detected from project files, not hardcoded
3. **Evidence-based narratives** - Every claim backed by file scan results
4. **Third-party separation** - Tools/External clearly marked
5. **Clickable evidence** - Every technology shows files/locations in tooltip

---

**Next Steps:** Fix collectors, re-run data collection, validate all tests pass.

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Test Files:**
- `tests/dashboard/test_no_mock_data.py`
- `tests/dashboard/test_language_detection_accuracy.py`

# Overview Tab Metric Definitions

**Version:** 1.0  
**Last Updated:** 2025-12-06  
**Purpose:** Detailed definitions and calculation formulas for all Overview tab metrics

---

## Overall Health Score

### Definition
Composite metric (0-100) representing overall codebase health based on weighted combination of four categories.

### Calculation Formula

```
Overall Health Score = (
    Code Quality Score × 0.35 +
    Security Score × 0.30 +
    Test Score × 0.25 +
    Documentation Score × 0.10
)
```

### Weighting Rationale

| Category | Weight | Justification |
|----------|--------|---------------|
| Code Quality | 35% | Highest impact on maintainability and developer velocity |
| Security | 30% | Critical for production readiness and compliance |
| Tests | 25% | Essential for confidence in changes and refactoring |
| Documentation | 10% | Important but lower immediate impact than code/security/tests |

### Score Interpretation

| Range | Status | Badge Color | Meaning |
|-------|--------|-------------|---------|
| 80-100 | ✅ Healthy | Green | Production-ready, best practices followed |
| 60-79 | ⚠️ Warning | Yellow | Acceptable with improvements needed |
| 40-59 | 🚨 Critical | Orange | Significant issues, action required |
| 0-39 | ⛔ Severe | Red | Major problems, immediate attention needed |

### Example Calculation

```
Code Quality: 85 × 0.35 = 29.75
Security: 95 × 0.30 = 28.50
Tests: 78 × 0.25 = 19.50
Documentation: 70 × 0.10 = 7.00
-----------------------------------
Overall Health Score = 84.75 → 85 (rounded)
Status: ✅ Healthy
```

---

## Key Metrics

### 1. Total Files

**Definition:** Count of all source code files in repository

**Calculation:**
```python
total_files = len([
    f for f in repo_path.rglob("*") 
    if f.is_file() and f.suffix in CODE_EXTENSIONS
])
```

**Included extensions:**
- Programming: `.py`, `.js`, `.ts`, `.java`, `.cs`, `.cpp`, `.go`, `.rb`, `.php`
- Markup: `.html`, `.css`, `.scss`, `.xml`, `.json`, `.yaml`
- Configuration: `.config`, `.ini`, `.toml`

**Excluded:**
- Binaries: `.exe`, `.dll`, `.so`
- Media: `.jpg`, `.png`, `.mp4`
- Archives: `.zip`, `.tar`, `.gz`
- Build outputs: `dist/`, `build/`, `node_modules/`, `__pycache__/`

**Typical ranges:**
- Small project: 10-100 files
- Medium project: 100-1000 files
- Large project: 1000-10,000 files
- Enterprise: 10,000+ files

---

### 2. Total LOC (Lines of Code)

**Definition:** Sum of non-blank, non-comment source code lines across all files

**Calculation:**
```python
def count_loc(file_path: Path) -> int:
    """Count lines of code (exclude blanks and comments)"""
    loc = 0
    with open(file_path, 'r') as f:
        for line in f:
            stripped = line.strip()
            # Skip blank lines
            if not stripped:
                continue
            # Skip comment-only lines (language-specific)
            if is_comment_line(stripped, file_path.suffix):
                continue
            loc += 1
    return loc

total_loc = sum(count_loc(f) for f in all_code_files)
```

**Comment detection by language:**
```python
COMMENT_PATTERNS = {
    '.py': ['#'],
    '.js': ['//', '/*', '*/'],
    '.java': ['//', '/*', '*/'],
    '.cs': ['//', '/*', '*/'],
    '.html': ['<!--', '-->'],
    '.css': ['/*', '*/']
}
```

**Typical ranges:**
- Small project: 1K-10K LOC
- Medium project: 10K-100K LOC
- Large project: 100K-1M LOC
- Enterprise: 1M+ LOC

**Industry benchmarks:**
- Developer productivity: 10-50 LOC/day (net after refactoring)
- Code density: 30-50 LOC per file (average)
- Optimal file size: <500 LOC per file

---

### 3. Test Coverage

**Definition:** Percentage of code lines executed by automated test suite

**Calculation:**
```python
test_coverage = (lines_covered_by_tests / total_lines_in_source) × 100
```

**Data sources:**
1. **Python:** `coverage.py` output (`coverage.json` or `.coverage` file)
2. **JavaScript:** Istanbul/NYC coverage reports (`coverage/coverage-summary.json`)
3. **Java:** JaCoCo XML reports
4. **.NET:** OpenCover or Coverlet reports

**Coverage types:**
- **Line coverage:** Percentage of lines executed (used in Overview tab)
- **Branch coverage:** Percentage of decision branches taken
- **Function coverage:** Percentage of functions called
- **Statement coverage:** Percentage of statements executed

**Target ranges:**
- Excellent: >80%
- Good: 60-80%
- Acceptable: 40-60%
- Poor: <40%

**Interpretation:**
- **100%:** Potentially over-testing or trivial code
- **80-95%:** Ideal range for most projects
- **60-80%:** Acceptable, focus on critical paths
- **<60%:** High risk, insufficient testing

**Exemptions (not counted in coverage):**
- Configuration files
- Migration scripts
- Generated code
- UI layout files (e.g., `.aspx`, `.xaml`)

---

### 4. Maintainability Index

**Definition:** Microsoft metric (0-100) measuring code maintainability based on complexity, LOC, and Halstead volume

**Calculation:**
```
MI = max(0, 171 - 5.2 × ln(HV) - 0.23 × CC - 16.2 × ln(LOC)) × 100 / 171

Where:
- HV = Halstead Volume (complexity based on operators/operands)
- CC = Cyclomatic Complexity (number of independent code paths)
- LOC = Lines of Code per module
- ln = Natural logarithm
```

**Halstead Volume:**
```
HV = N × log₂(n)

Where:
- N = Total operators + operands
- n = Unique operators + unique operands
```

**Cyclomatic Complexity:**
```
CC = E - N + 2P

Where:
- E = Number of edges in control flow graph
- N = Number of nodes
- P = Number of connected components (usually 1)
```

**Simplified approximation:**
```
CC ≈ 1 + (number of decision points: if, while, for, case, &&, ||)
```

**Interpretation:**

| MI Score | Maintainability | Action |
|----------|-----------------|--------|
| 85-100 | ✅ Excellent | Easy to maintain, no action needed |
| 70-84 | ✅ Good | Acceptable, minor improvements beneficial |
| 50-69 | ⚠️ Moderate | Refactoring recommended |
| 20-49 | 🚨 Difficult | Refactoring required |
| 0-19 | ⛔ Unmaintainable | Immediate refactoring or rewrite |

**Example calculation:**

```python
# File: user_service.py (200 LOC, CC=15, HV=800)
MI = max(0, 171 - 5.2 × ln(800) - 0.23 × 15 - 16.2 × ln(200)) × 100 / 171
   = max(0, 171 - 34.9 - 3.45 - 85.8) × 100 / 171
   = max(0, 46.85) × 100 / 171
   = 27.4

Result: MI = 27.4 → Difficult to maintain, refactoring required
```

---

### 5. Technical Debt (Hours)

**Definition:** Estimated time (hours) required to fix all code quality issues

**Calculation:**
```python
technical_debt_hours = sum(
    issue.severity_weight × issue.fix_time_estimate
    for issue in all_code_issues
)
```

**Issue categories and fix times:**

| Issue Type | Severity Weight | Avg Fix Time | Example |
|------------|----------------|--------------|---------|
| Long file (>500 LOC) | 0.5 | 2 hours | Split into modules |
| High complexity (CC>10) | 1.0 | 3 hours | Refactor method |
| Code duplication | 0.7 | 1 hour | Extract common code |
| Long method (>50 LOC) | 0.3 | 0.5 hours | Extract submethods |
| Too many parameters (>5) | 0.2 | 0.5 hours | Introduce parameter object |
| God class (>1000 LOC) | 1.5 | 8 hours | Split into smaller classes |
| Circular dependency | 1.2 | 4 hours | Refactor dependencies |
| Magic numbers | 0.1 | 0.25 hours | Extract constants |
| Dead code | 0.2 | 0.1 hours | Remove unused code |

**Example calculation:**

```
Project has:
- 3 long files (>500 LOC): 3 × 0.5 × 2 = 3 hours
- 5 high complexity methods: 5 × 1.0 × 3 = 15 hours
- 2 code duplication instances: 2 × 0.7 × 1 = 1.4 hours
- 10 long methods: 10 × 0.3 × 0.5 = 1.5 hours
-------------------------------------------------------
Total Technical Debt = 20.9 hours
```

**Interpretation:**

| Debt Hours | Status | Project Size Context |
|------------|--------|---------------------|
| 0-10 | ✅ Excellent | Small project or well-maintained |
| 10-30 | ✅ Good | Medium project, manageable |
| 30-60 | ⚠️ Moderate | Large project or needs attention |
| 60-100 | 🚨 High | Significant refactoring needed |
| 100+ | ⛔ Critical | Major technical debt, plan sprint |

**Debt velocity tracking:**
```
Debt Velocity = (Debt Today - Debt Last Month) / Days

Positive velocity = Debt growing (bad)
Negative velocity = Debt shrinking (good)
Zero velocity = Debt stable (monitor)
```

---

## Health Categories

### 1. Code Quality Score

**Definition:** Composite score (0-100) based on code cleanliness metrics

**Calculation:**
```python
code_quality_score = (
    (1 - long_files_ratio) × 30 +
    (1 - high_complexity_ratio) × 40 +
    (1 - code_duplication_ratio) × 20 +
    (maintainability_index / 100) × 10
)

Where:
- long_files_ratio = files_over_500_loc / total_files
- high_complexity_ratio = functions_with_cc_over_10 / total_functions
- code_duplication_ratio = duplicated_loc / total_loc
```

**Scoring breakdown:**

| Component | Weight | Calculation |
|-----------|--------|-------------|
| File length | 30% | `(1 - files>500LOC / total_files) × 30` |
| Complexity | 40% | `(1 - functions_CC>10 / total_functions) × 40` |
| Duplication | 20% | `(1 - duplicated_LOC / total_LOC) × 20` |
| Maintainability | 10% | `(maintainability_index / 100) × 10` |

**Example:**

```
Project stats:
- Total files: 100, Long files (>500 LOC): 5
- Total functions: 500, High complexity (CC>10): 25
- Total LOC: 50,000, Duplicated LOC: 2,500
- Maintainability index: 85

Calculations:
- File length: (1 - 5/100) × 30 = 28.5
- Complexity: (1 - 25/500) × 40 = 38.0
- Duplication: (1 - 2500/50000) × 20 = 19.0
- Maintainability: (85/100) × 10 = 8.5
-------------------------------------------
Code Quality Score = 94.0 → 94 (Excellent)
```

---

### 2. Security Score

**Definition:** Score (0-100) based on known vulnerabilities in dependencies

**Calculation:**
```python
security_score = 100 - min(100, (
    critical_cve_count × 20 +
    high_cve_count × 10 +
    medium_cve_count × 5 +
    low_cve_count × 1
))
```

**CVE (Common Vulnerabilities and Exposures) severity:**

| Severity | Point Deduction | Max Acceptable | Example |
|----------|----------------|----------------|---------|
| Critical (CVSS 9.0-10.0) | -20 per CVE | 0 | Remote code execution |
| High (CVSS 7.0-8.9) | -10 per CVE | 1-2 | SQL injection |
| Medium (CVSS 4.0-6.9) | -5 per CVE | <5 | XSS vulnerability |
| Low (CVSS 0.1-3.9) | -1 per CVE | <10 | Information disclosure |

**Example:**

```
Project dependencies:
- Critical CVEs: 0
- High CVEs: 1 (lodash 4.17.15, CVE-2020-8203)
- Medium CVEs: 2
- Low CVEs: 5

Calculation:
Score = 100 - (0×20 + 1×10 + 2×5 + 5×1)
      = 100 - (0 + 10 + 10 + 5)
      = 100 - 25
      = 75

Result: Security Score = 75 (Warning status)
Action: Upgrade lodash to 4.17.21+
```

**Data sources:**
- **Node.js:** `npm audit` or `yarn audit`
- **Python:** `safety check` or `pip-audit`
- **.NET:** NuGet vulnerability scanning
- **Java:** OWASP Dependency Check

---

### 3. Test Score

**Definition:** Score (0-100) combining test coverage and test quality

**Calculation:**
```python
test_score = (
    test_coverage × 0.70 +
    test_quality_score × 0.30
)

Where test_quality_score = (
    (1 - failing_tests_ratio) × 50 +
    (test_code_ratio) × 30 +
    (assertion_density) × 20
)
```

**Components:**

| Component | Weight | Calculation |
|-----------|--------|-------------|
| Test coverage | 70% | Direct coverage percentage |
| Failing tests | 15% | `(1 - failing/total) × 50` |
| Test code ratio | 9% | `(test_LOC / source_LOC) × 30` |
| Assertion density | 6% | `(assertions / tests) × 20` |

**Example:**

```
Project stats:
- Test coverage: 78%
- Failing tests: 0 / 250 (0%)
- Source LOC: 50,000, Test LOC: 15,000
- Total tests: 250, Total assertions: 750

Test quality calculations:
- Failing tests: (1 - 0/250) × 50 = 50.0
- Test code ratio: (15000/50000) × 30 = 9.0
- Assertion density: (750/250) × 20 = 60.0 (capped at 20)
Test quality score = 50 + 9 + 20 = 79

Final test score = 78 × 0.70 + 79 × 0.30
                 = 54.6 + 23.7
                 = 78.3 → 78 (Good)
```

---

### 4. Documentation Score

**Definition:** Score (0-100) based on documentation completeness

**Calculation:**
```python
documentation_score = (
    readme_quality_score × 0.40 +
    api_documentation_coverage × 0.35 +
    inline_comment_ratio × 0.25
)
```

**README quality scoring:**
```python
readme_score = 0
if readme_exists: readme_score += 20
if has_overview_section: readme_score += 20
if has_installation_instructions: readme_score += 20
if has_usage_examples: readme_score += 20
if has_contributing_guide: readme_score += 10
if has_license: readme_score += 10
# Max: 100
```

**API documentation coverage:**
```python
api_doc_coverage = (documented_public_apis / total_public_apis) × 100
```

**Inline comment ratio:**
```python
comment_ratio = min(30, (comment_lines / code_lines) × 100)
# Target: 10-20% comments (too many = code smell)
```

**Example:**

```
Project stats:
- README: Exists with overview, installation, usage (60/100)
- Public APIs: 100, Documented: 75 (75%)
- Code lines: 50,000, Comment lines: 8,000 (16%)

Calculations:
- README quality: 60 × 0.40 = 24.0
- API coverage: 75 × 0.35 = 26.25
- Comment ratio: 16 × 0.25 = 4.0
--------------------------------------------
Documentation Score = 54.25 → 54 (Moderate)
```

---

## Composition Metrics

### Language Percentage

**Definition:** Percentage of codebase written in each language

**Calculation:**
```python
language_percentage = (language_loc / total_loc) × 100

Where:
- language_loc = Sum of LOC in files with language extension
- total_loc = Sum of all LOC across all languages
```

**Language detection:**
```python
LANGUAGE_EXTENSIONS = {
    'Python': ['.py'],
    'JavaScript': ['.js', '.jsx'],
    'TypeScript': ['.ts', '.tsx'],
    'C#': ['.cs'],
    'Java': ['.java'],
    'Go': ['.go'],
    'Ruby': ['.rb'],
    'PHP': ['.php'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass'],
    'YAML': ['.yaml', '.yml'],
    'Markdown': ['.md']
}
```

**Example:**

```
Project LOC breakdown:
- Python: 34,340 LOC (.py files)
- JavaScript: 7,219 LOC (.js files)
- YAML: 2,421 LOC (.yaml/.yml files)
- Markdown: 1,698 LOC (.md files)
Total: 45,678 LOC

Calculations:
- Python: (34340 / 45678) × 100 = 75.2%
- JavaScript: (7219 / 45678) × 100 = 15.8%
- YAML: (2421 / 45678) × 100 = 5.3%
- Markdown: (1698 / 45678) × 100 = 3.7%
Total: 100.0%
```

---

## Trends

### Health Trend

**Definition:** Direction of health score change over time

**Calculation:**
```python
health_trend = classify_trend(
    current_score=current_health_score,
    previous_score=previous_health_score
)

def classify_trend(current, previous):
    delta = current - previous
    if delta > 5:
        return "improving"
    elif delta < -5:
        return "declining"
    else:
        return "stable"
```

**Threshold rationale:**
- ±5 points: Significant change (not noise)
- Prevents trend flapping from minor fluctuations

**Example:**

```
Current scan: 85
Previous scan: 78
Delta: +7

Trend: "improving" (delta > 5)
```

---

## Formulas Summary

| Metric | Formula | Range |
|--------|---------|-------|
| Overall Health | `(Quality×0.35 + Security×0.30 + Tests×0.25 + Docs×0.10)` | 0-100 |
| Total Files | `count(code_files excluding binaries/media)` | 0-∞ |
| Total LOC | `sum(non_blank_non_comment_lines)` | 0-∞ |
| Test Coverage | `(covered_lines / total_lines) × 100` | 0-100% |
| Maintainability Index | `max(0, 171 - 5.2×ln(HV) - 0.23×CC - 16.2×ln(LOC)) × 100/171` | 0-100 |
| Technical Debt | `sum(issue_severity × fix_time)` | 0-∞ hours |
| Code Quality | `(1-long_files)×30 + (1-high_cc)×40 + (1-dup)×20 + MI×10` | 0-100 |
| Security | `100 - min(100, critical×20 + high×10 + med×5 + low×1)` | 0-100 |
| Test Score | `coverage×0.70 + test_quality×0.30` | 0-100 |
| Documentation | `readme×0.40 + api_docs×0.35 + comments×0.25` | 0-100 |
| Language % | `(lang_loc / total_loc) × 100` | 0-100% |

---

## References

1. **Maintainability Index:** Microsoft Visual Studio documentation
2. **Cyclomatic Complexity:** Thomas J. McCabe (1976)
3. **Halstead Metrics:** Maurice H. Halstead (1977)
4. **CVE Scoring:** NIST CVSS v3.1 specification
5. **Test Coverage:** IEEE 829-2008 standard

---

**Last updated:** 2025-12-06 | **Version:** 1.0 | **Maintainer:** CORTEX Team

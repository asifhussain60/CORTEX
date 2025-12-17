# Dashboard Reconciliation Engine Implementation Plan

**Plan ID:** DASH-RECONCILE-2025-001  
**Created:** December 7, 2025  
**Status:** 🟢 Ready for Implementation  
**Author:** Asif Hussain  
**Priority:** High - Data Integrity & Accuracy

---

## 📋 Executive Summary

**Objective:** Create a comprehensive reconciliation engine that analyzes ALL dashboard data holistically to ensure accuracy, consistency, and alignment with industry standards (CVSS, OWASP, ISO 27001, SOC 2).

**Problem Statement:**
Current dashboard collectors operate independently without cross-validation:
- Security scores and quality scores can both be low, yet overall health shows "healthy"
- No validation that security vulnerabilities properly impact overall scores
- Missing industry-standard severity mappings (CVSS v3.1/v4.0)
- No enforcement of logical constraints (e.g., critical vulnerabilities should cap overall score)
- Inconsistent scoring algorithms across collectors (0-100 vs 0-10 scales)

**Solution:**
Build a reconciliation engine that:
1. Normalizes all scores to industry standards
2. Validates cross-tab dependencies and constraints
3. Applies weighted scoring with security/quality guardrails
4. Detects anomalies and flags inconsistencies
5. Produces auditable reconciliation reports

---

## 🎯 Success Criteria

**Must Have (Blockers):**
- ✅ All scores normalized to 0-100 scale with industry mapping
- ✅ Security vulnerabilities (Critical/High) properly cap overall scores
- ✅ Cross-tab validation rules enforced (15+ validation rules)
- ✅ Reconciliation runs after every data collection
- ✅ Detailed audit trail with before/after comparisons
- ✅ 100% test coverage for reconciliation logic

**Should Have (Targets):**
- ✅ Weighted scoring with configurable weights
- ✅ Anomaly detection with statistical analysis
- ✅ Compliance score alignment with SOC 2/ISO 27001
- ✅ Performance < 500ms for full reconciliation

**Nice to Have (Optimizations):**
- ✅ Machine learning for scoring refinement
- ✅ Historical trend analysis
- ✅ Predictive score forecasting

---

## 📊 Current State Analysis

### Existing Scoring Mechanisms (Inconsistencies Found)

#### 1. Health Collector (`enhanced_collectors.py`)
```python
# Lines 258-265
def _calculate_health_score(self, complexity: Dict, smells: List, maintainability: float) -> float:
    complexity_score = max(0, 100 - (complexity["average_cyclomatic"] * 3))
    smell_score = max(0, 100 - (len(smells) * 0.5))
    return round((complexity_score + smell_score + maintainability) / 3, 1)
```
- **Scale:** 0-100
- **Algorithm:** Simple average of 3 components
- **Issue:** No weighting, no security factor

#### 2. Security Collector (`security_collector.py`)
```python
# Lines 90-103
def _calculate_overall_score(categories_dict, vuln_data):
    # Uses category scores and vulnerability counts
    # No clear algorithm visible in excerpt
```
- **Scale:** 0-100 (assumed)
- **Algorithm:** Unknown (needs investigation)
- **Issue:** Vulnerabilities may not properly impact score

#### 3. Complexity Scoring
```python
# Lines 293-296
def _calculate_complexity_score(self, complexity: Dict) -> float:
    avg = complexity["average_cyclomatic"]
    return max(0, min(100, 100 - (avg - 5) * 10))
```
- **Scale:** 0-100
- **Algorithm:** Linear penalty from baseline of 5
- **Issue:** Arbitrary penalty factor (10x)

### Industry Standards (Must Align With)

#### CVSS v3.1/v4.0 (Common Vulnerability Scoring System)
**Source:** NIST NVD (https://nvd.nist.gov/vuln-metrics/cvss)

| CVSS Score | Severity | Score Range |
|------------|----------|-------------|
| 0.0 | None | 0.0 |
| 0.1-3.9 | Low | 1-39 (normalized) |
| 4.0-6.9 | Medium | 40-69 (normalized) |
| 7.0-8.9 | High | 70-89 (normalized) |
| 9.0-10.0 | Critical | 90-100 (normalized) |

**Mapping Formula:**
```
normalized_score = (cvss_score / 10.0) * 100
severity_weight = {
    'critical': 1.0,  # Full impact
    'high': 0.7,      # 70% impact
    'medium': 0.4,    # 40% impact
    'low': 0.1        # 10% impact
}
```

#### OWASP Top 10 2025
**Source:** https://owasp.org/www-project-top-ten/

11 Categories (A01-A11):
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)
- A11: Insecure AI/ML Model Deployment (NEW in 2025)

**Compliance Scoring:**
```
owasp_compliance = (categories_passed / 11) * 100
penalty_per_category = 100 / 11 ≈ 9.09 points
```

#### ISO 27001 / SOC 2 Alignment
**Control Categories:**
- Access Control
- Cryptography
- Physical Security
- Operations Security
- Communications Security
- System Acquisition/Development
- Supplier Relationships
- Incident Management
- Business Continuity
- Compliance

**Scoring:**
```
compliance_score = weighted_average([
    security_controls * 0.40,    # 40% weight
    vulnerability_mgmt * 0.30,   # 30% weight
    incident_response * 0.15,    # 15% weight
    audit_logging * 0.15         # 15% weight
])
```

---

## 🏗️ Reconciliation Engine Architecture

### Component Design

```
src/dashboard/reconciliation/
├── __init__.py
├── reconciliation_engine.py       # Main orchestrator
├── normalizers/
│   ├── __init__.py
│   ├── score_normalizer.py        # 0-100 normalization
│   ├── cvss_normalizer.py         # CVSS to 0-100
│   └── severity_normalizer.py     # Severity string to numeric
├── validators/
│   ├── __init__.py
│   ├── cross_tab_validator.py     # Cross-tab consistency
│   ├── constraint_validator.py    # Business rule enforcement
│   └── anomaly_detector.py        # Statistical outlier detection
├── scorers/
│   ├── __init__.py
│   ├── weighted_scorer.py         # Weighted score calculation
│   ├── security_scorer.py         # Security-specific scoring
│   └── quality_scorer.py          # Code quality scoring
├── rules/
│   ├── __init__.py
│   ├── validation_rules.py        # Rule definitions
│   └── scoring_rules.py           # Scoring formulas
└── reports/
    ├── __init__.py
    └── reconciliation_report.py   # Audit trail generator
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Data Collection (Existing Collectors)                        │
│    - HealthDataCollector                                         │
│    - SecurityCollector                                           │
│    - TechStackCollector                                          │
│    - ArchitectureCollector                                       │
│    - CodeOrganizationCollector                                   │
│    - VendorCollector                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Reconciliation Engine Input                                  │
│    {                                                             │
│      'health': {...},                                            │
│      'security': {...},                                          │
│      'tech-stack': {...},                                        │
│      'architecture': {...},                                      │
│      'code-organization': {...},                                 │
│      'vendors': {...}                                            │
│    }                                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Phase 1: Normalization                                       │
│    - Convert all scores to 0-100 scale                          │
│    - Map CVSS scores (0-10) to 0-100                            │
│    - Normalize severity strings (critical/high/medium/low)      │
│    - Standardize vulnerability counts                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Phase 2: Validation                                          │
│    - Rule 1: Critical vulns (≥1) → cap overall at 40            │
│    - Rule 2: High vulns (≥5) → cap overall at 60                │
│    - Rule 3: Security < 50 → overall cannot exceed 70           │
│    - Rule 4: Quality < 40 → overall cannot exceed 60            │
│    - Rule 5: Both Security & Quality < 50 → overall max 50      │
│    - ... (15+ validation rules)                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Phase 3: Weighted Scoring                                    │
│    overall_score = weighted_average([                            │
│      security_score * 0.35,        # 35% weight                 │
│      quality_score * 0.25,         # 25% weight                 │
│      maintainability_score * 0.15, # 15% weight                 │
│      architecture_score * 0.15,    # 15% weight                 │
│      test_coverage_score * 0.10    # 10% weight                 │
│    ])                                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Phase 4: Anomaly Detection                                   │
│    - Statistical outlier detection (z-score > 2)                │
│    - Score delta validation (max 20 point swing)                │
│    - Trend analysis (historical comparison)                     │
│    - Flag inconsistencies for manual review                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Reconciliation Output                                        │
│    {                                                             │
│      'reconciled_data': {normalized + validated scores},         │
│      'violations': [{rule, severity, message}],                  │
│      'anomalies': [{type, confidence, recommendation}],          │
│      'audit_trail': {before, after, changes},                    │
│      'metrics': {total_adjustments, rules_triggered}             │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📐 Validation Rules & Constraints

### Critical Validation Rules (15 Core Rules)

#### Security Impact Rules (Highest Priority)

**R1: Critical Vulnerability Cap**
```python
if vulnerability_counts['critical'] >= 1:
    overall_score = min(overall_score, 40)
    violations.append({
        'rule': 'R1_CRITICAL_VULN_CAP',
        'severity': 'blocker',
        'message': f"{vulnerability_counts['critical']} critical vulnerabilities found",
        'adjustment': original_score - 40,
        'rationale': 'Critical vulnerabilities pose immediate risk'
    })
```

**R2: High Vulnerability Cap**
```python
if vulnerability_counts['high'] >= 5:
    overall_score = min(overall_score, 60)
elif vulnerability_counts['high'] >= 3:
    overall_score = min(overall_score, 70)
```

**R3: Security Score Threshold**
```python
if security_score < 50:
    overall_score = min(overall_score, 70)
if security_score < 30:
    overall_score = min(overall_score, 50)
```

**R4: OWASP Compliance Minimum**
```python
owasp_passing = sum(1 for cat in owasp_top_10 if cat['compliant'])
if owasp_passing < 8:  # Must pass 8/11 categories
    security_score = min(security_score, 60)
```

#### Quality Impact Rules

**R5: Code Quality Floor**
```python
if quality_score < 40:
    overall_score = min(overall_score, 60)
```

**R6: Complexity Penalty**
```python
if avg_cyclomatic_complexity > 20:
    maintainability_score = min(maintainability_score, 40)
if avg_cyclomatic_complexity > 15:
    maintainability_score = min(maintainability_score, 60)
```

**R7: Test Coverage Minimum**
```python
if test_coverage < 50:
    quality_score *= 0.8  # 20% penalty
if test_coverage < 30:
    quality_score *= 0.6  # 40% penalty
```

#### Cross-Tab Consistency Rules

**R8: Security-Quality Correlation**
```python
if security_score < 50 and quality_score < 50:
    overall_score = min(overall_score, 50)  # Both low = system at risk
```

**R9: Architecture-Security Alignment**
```python
if security_score < 40 and architecture_score > 80:
    anomalies.append({
        'type': 'score_mismatch',
        'confidence': 0.9,
        'message': 'High architecture score inconsistent with low security'
    })
```

**R10: Maintainability-Complexity Inverse**
```python
if avg_complexity > 15 and maintainability_score > 80:
    # High complexity should reduce maintainability
    maintainability_score = min(maintainability_score, 70)
```

#### Dependency & Supply Chain Rules

**R11: Outdated Dependencies Penalty**
```python
outdated_critical_deps = count_outdated_deps(severity='critical')
if outdated_critical_deps > 10:
    vendor_score = min(vendor_score, 50)
    security_score = min(security_score, 60)
```

**R12: Unmaintained Dependencies Flag**
```python
unmaintained_count = count_unmaintained_deps(years=2)
if unmaintained_count > 5:
    risk_score = 'high'
    security_score = min(security_score, 70)
```

#### Configuration & Deployment Rules

**R13: Production Configuration Violations**
```python
if 'debug=true' in prod_config or 'customErrors=Off' in prod_config:
    security_score = min(security_score, 50)
    violations.append({
        'rule': 'R13_PROD_CONFIG_VIOLATION',
        'severity': 'high',
        'message': 'Debug mode or error disclosure enabled in production'
    })
```

**R14: Hardcoded Secrets Impact**
```python
secret_severity_map = {'critical': 30, 'high': 20, 'medium': 10}
for secret in hardcoded_secrets:
    security_score -= secret_severity_map[secret['severity']]
security_score = max(security_score, 0)  # Floor at 0
```

**R15: Missing Security Headers**
```python
missing_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'CSP']
if len(missing_critical_headers) >= 2:
    security_score = min(security_score, 70)
```

### Weighting Configuration

```python
SCORING_WEIGHTS = {
    'security': 0.35,        # 35% - Highest priority
    'quality': 0.25,         # 25% - Code health
    'maintainability': 0.15, # 15% - Long-term sustainability
    'architecture': 0.15,    # 15% - Structural integrity
    'test_coverage': 0.10    # 10% - Verification confidence
}

VULNERABILITY_IMPACT_WEIGHTS = {
    'critical': 1.0,   # 100% impact on security score
    'high': 0.7,       # 70% impact
    'medium': 0.4,     # 40% impact
    'low': 0.1         # 10% impact
}

CVSS_TO_NORMALIZED_SCORE = {
    (9.0, 10.0): (90, 100),  # Critical
    (7.0, 8.9): (70, 89),    # High
    (4.0, 6.9): (40, 69),    # Medium
    (0.1, 3.9): (1, 39),     # Low
    (0.0, 0.0): (0, 0)       # None
}
```

---

## 🔧 Implementation Phases

### Phase 1: Core Engine Foundation (Days 1-2)

**Deliverables:**
- `reconciliation_engine.py` - Main orchestrator class
- `score_normalizer.py` - 0-100 normalization
- `cvss_normalizer.py` - CVSS to 0-100 mapping
- Base test suite (30 tests)

**TDD Approach:**
1. **RED:** Write tests for score normalization (CVSS 0-10 → 0-100)
2. **GREEN:** Implement normalization functions
3. **REFACTOR:** Optimize with lookup tables

**Acceptance Criteria:**
- [ ] All scores normalized to 0-100 scale
- [ ] CVSS scores correctly mapped per NIST standards
- [ ] Severity strings converted to numeric scores
- [ ] 100% test coverage for normalizers

### Phase 2: Validation Rules Engine (Days 3-4)

**Deliverables:**
- `cross_tab_validator.py` - Cross-tab consistency checks
- `constraint_validator.py` - Business rule enforcement
- `validation_rules.py` - Rule definitions
- Validation test suite (50 tests)

**TDD Approach:**
1. **RED:** Write tests for each of 15 validation rules
2. **GREEN:** Implement rule logic
3. **REFACTOR:** Extract common validation patterns

**Acceptance Criteria:**
- [ ] All 15 validation rules implemented
- [ ] Rule violations properly logged with severity
- [ ] Score adjustments applied correctly
- [ ] No false positives in validation

### Phase 3: Weighted Scoring System (Days 5-6)

**Deliverables:**
- `weighted_scorer.py` - Weighted average calculation
- `security_scorer.py` - Security-specific scoring
- `quality_scorer.py` - Quality scoring
- Scoring test suite (40 tests)

**TDD Approach:**
1. **RED:** Write tests for weighted calculations
2. **GREEN:** Implement weighted scoring formulas
3. **REFACTOR:** Make weights configurable

**Acceptance Criteria:**
- [ ] Weighted scores calculated correctly
- [ ] Security/quality factors properly applied
- [ ] Edge cases handled (all zeros, missing data)
- [ ] Weights sum to 1.0

### Phase 4: Anomaly Detection (Days 7-8)

**Deliverables:**
- `anomaly_detector.py` - Statistical analysis
- Z-score calculation for outliers
- Trend analysis (historical comparison)
- Anomaly test suite (30 tests)

**TDD Approach:**
1. **RED:** Write tests for anomaly detection algorithms
2. **GREEN:** Implement statistical detection
3. **REFACTOR:** Optimize for performance

**Acceptance Criteria:**
- [ ] Outliers detected with >95% accuracy
- [ ] Anomalies flagged with confidence scores
- [ ] Historical trends compared correctly
- [ ] False positive rate < 5%

### Phase 5: Audit Trail & Reporting (Days 9-10)

**Deliverables:**
- `reconciliation_report.py` - Report generator
- Before/after comparison
- Violation details
- JSON export format
- Report test suite (25 tests)

**TDD Approach:**
1. **RED:** Write tests for report generation
2. **GREEN:** Implement report formatting
3. **REFACTOR:** Add export formats (JSON, HTML, PDF)

**Acceptance Criteria:**
- [ ] Complete audit trail generated
- [ ] Before/after scores tracked
- [ ] All violations documented
- [ ] Report exports successfully

### Phase 6: Integration & Performance (Days 11-12)

**Deliverables:**
- Integration with `dashboard_collector.py`
- Performance optimization (<500ms target)
- Caching layer for repeated calculations
- End-to-end integration tests (20 tests)

**TDD Approach:**
1. **RED:** Write integration tests with real collector data
2. **GREEN:** Hook reconciliation into data pipeline
3. **REFACTOR:** Add caching and optimization

**Acceptance Criteria:**
- [ ] Reconciliation runs automatically after collection
- [ ] Performance < 500ms for typical dataset
- [ ] Integration tests pass with real data
- [ ] No regression in existing functionality

---

## 🧪 Test Strategy

### Test Pyramid

```
              ▲
             /E2E\           10 tests (Integration)
            /─────\
           /Unit   \         175 tests (Component)
          /_________\
         /  Contract \       20 tests (API)
        /─────────────\
       Total: 205 Tests
```

### Test Categories

**1. Unit Tests (175 tests)**
- Score normalization (30 tests)
- CVSS mapping (20 tests)
- Validation rules (50 tests)
- Weighted scoring (40 tests)
- Anomaly detection (30 tests)
- Report generation (5 tests)

**2. Integration Tests (20 tests)**
- End-to-end reconciliation flow (5 tests)
- Real collector data processing (10 tests)
- Multi-tab validation (5 tests)

**3. Contract Tests (10 tests)**
- Input schema validation (5 tests)
- Output schema validation (5 tests)

### Test Data Sets

**Dataset 1: Perfect Score Scenario**
```json
{
  "security_score": 95,
  "quality_score": 92,
  "vulnerabilities": {"critical": 0, "high": 0, "medium": 1, "low": 3},
  "test_coverage": 88,
  "complexity": 7.2,
  "expected_overall": 93
}
```

**Dataset 2: Critical Vulnerability Scenario**
```json
{
  "security_score": 75,
  "quality_score": 80,
  "vulnerabilities": {"critical": 2, "high": 5, "medium": 10, "low": 15},
  "test_coverage": 85,
  "complexity": 8.5,
  "expected_overall": 40,  # Capped due to critical vulns
  "expected_violations": ["R1_CRITICAL_VULN_CAP"]
}
```

**Dataset 3: Low Quality + Low Security**
```json
{
  "security_score": 35,
  "quality_score": 40,
  "vulnerabilities": {"critical": 0, "high": 8, "medium": 15, "low": 20},
  "test_coverage": 25,
  "complexity": 18.5,
  "expected_overall": 50,  # Capped due to R8
  "expected_violations": ["R2_HIGH_VULN_CAP", "R3_SECURITY_THRESHOLD", "R8_SECURITY_QUALITY_CORRELATION"]
}
```

**Dataset 4: Anomaly Detection**
```json
{
  "security_score": 25,
  "architecture_score": 95,  # Anomaly: arch high, security low
  "quality_score": 85,
  "vulnerabilities": {"critical": 3, "high": 12, "medium": 20, "low": 30},
  "expected_anomalies": ["R9_ARCHITECTURE_SECURITY_MISMATCH"]
}
```

---

## 📊 Integration Points

### 1. Dashboard Collector Integration

**File:** `src/orchestrators/dashboard_collector.py`

**Modification Point:** After `collect_all()` method (line ~200)

```python
# BEFORE (current)
results = {}
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(func): name for name, func in collectors.items()}
    for future in as_completed(futures):
        name = futures[future]
        try:
            results[name] = future.result()
        except Exception as e:
            logger.error(f"Failed to collect {name}: {e}")

# Save results
self._save_results(results)

# AFTER (with reconciliation)
results = {}
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(func): name for name, func in collectors.items()}
    for future in as_completed(futures):
        name = futures[future]
        try:
            results[name] = future.result()
        except Exception as e:
            logger.error(f"Failed to collect {name}: {e}")

# NEW: Reconciliation step
from src.dashboard.reconciliation.reconciliation_engine import ReconciliationEngine
reconciliation_engine = ReconciliationEngine()
reconciliation_result = reconciliation_engine.reconcile(results)

# Save reconciled results + audit trail
self._save_results(reconciliation_result['reconciled_data'])
self._save_reconciliation_report(reconciliation_result)
```

### 2. Dashboard Data Loader Integration

**File:** `cortex-brain/dashboards/ui/data-loader.js`

**Modification Point:** After data load

```javascript
// BEFORE (current)
async function loadDashboardData(repoName) {
    const data = await fetch(`data/${repoName}/overview.json`);
    return await data.json();
}

// AFTER (with reconciliation awareness)
async function loadDashboardData(repoName) {
    const data = await fetch(`data/${repoName}/overview.json`);
    const jsonData = await data.json();
    
    // Check for reconciliation metadata
    if (jsonData.reconciliation) {
        displayReconciliationBadge(jsonData.reconciliation);
    }
    
    return jsonData;
}

function displayReconciliationBadge(reconciliation) {
    const badge = document.createElement('div');
    badge.className = 'reconciliation-badge';
    badge.innerHTML = `
        <span class="badge-icon">✓</span>
        <span>Reconciled</span>
        <span class="badge-detail">${reconciliation.rules_triggered} rules applied</span>
    `;
    document.querySelector('.dashboard-header').appendChild(badge);
}
```

### 3. Score Display Components

**All Tab Components:** Add reconciliation metadata display

```javascript
// Example: Security tab
function renderSecurityScore(score, reconciliation) {
    const container = document.createElement('div');
    container.className = 'score-container';
    
    // Original score (if adjusted)
    if (reconciliation && reconciliation.adjustments.security) {
        const original = reconciliation.adjustments.security.original;
        container.innerHTML += `
            <div class="score-adjusted">
                <span class="original-score">${original}</span>
                <span class="arrow">→</span>
                <span class="final-score">${score}</span>
                <span class="adjustment-reason" title="${reconciliation.adjustments.security.reason}">
                    ⓘ
                </span>
            </div>
        `;
    } else {
        container.innerHTML = `<div class="score-final">${score}</div>`;
    }
    
    return container;
}
```

---

## 📁 File Structure

```
src/dashboard/reconciliation/
├── __init__.py                         # Package exports
├── reconciliation_engine.py            # Main orchestrator (350 lines)
│   └── class ReconciliationEngine:
│       ├── reconcile(data) -> ReconciliationResult
│       ├── _normalize_phase(data)
│       ├── _validation_phase(data)
│       ├── _scoring_phase(data)
│       └── _anomaly_phase(data)
│
├── normalizers/
│   ├── __init__.py
│   ├── score_normalizer.py             # Base normalizer (150 lines)
│   │   └── class ScoreNormalizer:
│   │       ├── normalize_to_100(value, scale)
│   │       ├── normalize_percentage(value)
│   │       └── normalize_severity(severity_str)
│   │
│   ├── cvss_normalizer.py              # CVSS converter (100 lines)
│   │   └── class CVSSNormalizer:
│   │       ├── cvss_to_100(cvss_score)
│   │       ├── severity_to_cvss(severity)
│   │       └── get_severity_range(cvss)
│   │
│   └── severity_normalizer.py          # Severity mapper (80 lines)
│       └── class SeverityNormalizer:
│           ├── severity_to_numeric(severity)
│           ├── numeric_to_severity(score)
│           └── get_severity_weight(severity)
│
├── validators/
│   ├── __init__.py
│   ├── cross_tab_validator.py          # Cross-tab checks (250 lines)
│   │   └── class CrossTabValidator:
│   │       ├── validate_security_quality_correlation(data)
│   │       ├── validate_architecture_security_alignment(data)
│   │       ├── validate_maintainability_complexity_inverse(data)
│   │       └── validate_all(data) -> List[Violation]
│   │
│   ├── constraint_validator.py         # Business rules (300 lines)
│   │   └── class ConstraintValidator:
│   │       ├── apply_critical_vuln_cap(data)
│   │       ├── apply_high_vuln_cap(data)
│   │       ├── apply_security_threshold(data)
│   │       ├── apply_quality_floor(data)
│   │       └── apply_all_constraints(data) -> List[Violation]
│   │
│   └── anomaly_detector.py             # Statistical analysis (200 lines)
│       └── class AnomalyDetector:
│           ├── detect_outliers(scores, threshold=2.0)
│           ├── detect_score_inconsistencies(data)
│           ├── detect_trend_anomalies(historical, current)
│           └── detect_all(data) -> List[Anomaly]
│
├── scorers/
│   ├── __init__.py
│   ├── weighted_scorer.py              # Weighted calc (180 lines)
│   │   └── class WeightedScorer:
│   │       ├── calculate_weighted_average(scores, weights)
│   │       ├── calculate_overall_score(data)
│   │       └── apply_vulnerability_impact(score, vulns)
│   │
│   ├── security_scorer.py              # Security logic (220 lines)
│   │   └── class SecurityScorer:
│   │       ├── calculate_security_score(vulns, config, secrets)
│   │       ├── apply_cvss_weights(vulns)
│   │       ├── calculate_owasp_compliance(categories)
│   │       └── apply_hardcoded_secret_penalty(score, secrets)
│   │
│   └── quality_scorer.py               # Quality logic (180 lines)
│       └── class QualityScorer:
│           ├── calculate_quality_score(complexity, coverage, smells)
│           ├── apply_complexity_penalty(score, complexity)
│           ├── apply_coverage_penalty(score, coverage)
│           └── apply_code_smell_penalty(score, smells)
│
├── rules/
│   ├── __init__.py
│   ├── validation_rules.py             # Rule definitions (400 lines)
│   │   └── VALIDATION_RULES = [
│   │       Rule('R1_CRITICAL_VULN_CAP', ...),
│   │       Rule('R2_HIGH_VULN_CAP', ...),
│   │       ... (15 rules)
│   │   ]
│   │
│   └── scoring_rules.py                # Scoring formulas (300 lines)
│       └── SCORING_CONFIG = {
│           'weights': {...},
│           'thresholds': {...},
│           'penalties': {...}
│       }
│
├── reports/
│   ├── __init__.py
│   └── reconciliation_report.py        # Report generator (250 lines)
│       └── class ReconciliationReport:
│           ├── generate_report(reconciliation_result)
│           ├── generate_audit_trail(before, after)
│           ├── generate_violation_summary(violations)
│           ├── export_json(report)
│           ├── export_html(report)
│           └── export_pdf(report)
│
└── models/
    ├── __init__.py
    ├── reconciliation_result.py        # Result model (120 lines)
    │   └── @dataclass ReconciliationResult:
    │       ├── reconciled_data: Dict
    │       ├── violations: List[Violation]
    │       ├── anomalies: List[Anomaly]
    │       ├── audit_trail: AuditTrail
    │       └── metrics: ReconciliationMetrics
    │
    ├── violation.py                    # Violation model (80 lines)
    │   └── @dataclass Violation:
    │       ├── rule_id: str
    │       ├── severity: str
    │       ├── message: str
    │       ├── adjustment: float
    │       └── rationale: str
    │
    └── anomaly.py                      # Anomaly model (80 lines)
        └── @dataclass Anomaly:
            ├── type: str
            ├── confidence: float
            ├── message: str
            └── recommendation: str
```

**Total Estimated Lines:** ~3,000 lines (including tests)

---

## ⚙️ Configuration

### Reconciliation Configuration File

**Location:** `cortex-brain/reconciliation-config.yaml`

```yaml
# Reconciliation Engine Configuration
# Version: 1.0.0

scoring:
  weights:
    security: 0.35
    quality: 0.25
    maintainability: 0.15
    architecture: 0.15
    test_coverage: 0.10
  
  vulnerability_impact:
    critical: 1.0
    high: 0.7
    medium: 0.4
    low: 0.1

validation:
  rules_enabled:
    - R1_CRITICAL_VULN_CAP
    - R2_HIGH_VULN_CAP
    - R3_SECURITY_THRESHOLD
    - R4_OWASP_COMPLIANCE
    - R5_CODE_QUALITY_FLOOR
    - R6_COMPLEXITY_PENALTY
    - R7_TEST_COVERAGE_MINIMUM
    - R8_SECURITY_QUALITY_CORRELATION
    - R9_ARCHITECTURE_SECURITY_ALIGNMENT
    - R10_MAINTAINABILITY_COMPLEXITY_INVERSE
    - R11_OUTDATED_DEPS_PENALTY
    - R12_UNMAINTAINED_DEPS_FLAG
    - R13_PROD_CONFIG_VIOLATION
    - R14_HARDCODED_SECRETS_IMPACT
    - R15_MISSING_SECURITY_HEADERS
  
  thresholds:
    critical_vuln_overall_cap: 40
    high_vuln_overall_cap: 60
    security_low_threshold: 50
    security_critical_threshold: 30
    quality_floor: 40
    owasp_min_passing: 8
    test_coverage_penalty_threshold: 50
    complexity_high_threshold: 15
    complexity_critical_threshold: 20

anomaly_detection:
  enabled: true
  z_score_threshold: 2.0
  confidence_threshold: 0.75
  max_score_delta: 20
  historical_lookback_days: 30

reporting:
  generate_audit_trail: true
  generate_violation_summary: true
  generate_anomaly_report: true
  export_formats:
    - json
    - html
  save_path: "cortex-brain/dashboards/reports/reconciliation/"

performance:
  max_execution_time_ms: 500
  enable_caching: true
  cache_ttl_seconds: 300
```

---

## 📊 Expected Output Format

### Reconciliation Result Structure

```json
{
  "reconciliation_timestamp": "2025-12-07T15:30:45.123Z",
  "reconciliation_version": "1.0.0",
  "repository": "my-project",
  "execution_time_ms": 347,
  
  "reconciled_data": {
    "overall_score": 72,
    "security": {
      "score": 65,
      "original_score": 75,
      "adjusted": true,
      "adjustment_reason": "High vulnerability cap applied (R2)",
      "vulnerabilities": {
        "critical": 0,
        "high": 6,
        "medium": 12,
        "low": 8
      },
      "owasp_compliance": {
        "passed": 9,
        "failed": 2,
        "compliance_score": 82
      }
    },
    "quality": {
      "score": 78,
      "original_score": 78,
      "adjusted": false,
      "code_smells": 23,
      "complexity_score": 72,
      "documentation_score": 85
    },
    "maintainability": {
      "score": 70,
      "original_score": 75,
      "adjusted": true,
      "adjustment_reason": "Complexity penalty applied (R6)",
      "complexity_avg": 16.5
    },
    "architecture": {
      "score": 82,
      "adjusted": false
    },
    "test_coverage": {
      "score": 85,
      "coverage_percent": 85,
      "adjusted": false
    }
  },
  
  "violations": [
    {
      "rule_id": "R2_HIGH_VULN_CAP",
      "severity": "high",
      "category": "security",
      "message": "6 high-severity vulnerabilities found, capping overall score at 60",
      "original_score": 75,
      "adjusted_score": 60,
      "adjustment": -15,
      "rationale": "High-severity vulnerabilities pose significant risk and require remediation"
    },
    {
      "rule_id": "R6_COMPLEXITY_PENALTY",
      "severity": "medium",
      "category": "maintainability",
      "message": "Average cyclomatic complexity 16.5 exceeds threshold of 15",
      "original_score": 75,
      "adjusted_score": 70,
      "adjustment": -5,
      "rationale": "High complexity reduces maintainability and increases bug risk"
    }
  ],
  
  "anomalies": [
    {
      "type": "score_inconsistency",
      "confidence": 0.85,
      "category": "architecture_security",
      "message": "Architecture score (82) is high despite low security score (65)",
      "recommendation": "Review architecture for security design patterns",
      "z_score": 2.3
    }
  ],
  
  "audit_trail": {
    "changes": [
      {
        "category": "security",
        "field": "score",
        "before": 75,
        "after": 65,
        "reason": "R2_HIGH_VULN_CAP applied"
      },
      {
        "category": "maintainability",
        "field": "score",
        "before": 75,
        "after": 70,
        "reason": "R6_COMPLEXITY_PENALTY applied"
      },
      {
        "category": "overall",
        "field": "score",
        "before": 78,
        "after": 72,
        "reason": "Weighted recalculation with adjusted component scores"
      }
    ],
    "rules_triggered": 2,
    "anomalies_detected": 1
  },
  
  "metrics": {
    "total_adjustments": 3,
    "total_score_delta": -6,
    "rules_triggered": 2,
    "violations_count": 2,
    "anomalies_count": 1,
    "confidence_average": 0.85
  }
}
```

---

## 🧪 Test Execution Strategy

### Test Phases

**Phase 1: Unit Tests (Days 1-6)**
- Run tests continuously during development
- 100% pass rate required before moving to next component
- Code coverage target: 100% for business logic, 90% overall

**Phase 2: Integration Tests (Days 7-10)**
- Test with real collector data from sample projects
- Validate end-to-end reconciliation flow
- Performance benchmarking (<500ms target)

**Phase 3: Regression Tests (Days 11-12)**
- Run full dashboard test suite
- Ensure no breaking changes to existing functionality
- Validate backward compatibility

### Continuous Testing

```bash
# Run unit tests with coverage
pytest tests/dashboard/reconciliation/ --cov=src/dashboard/reconciliation --cov-report=html

# Run specific test category
pytest tests/dashboard/reconciliation/test_normalizers.py -v

# Run integration tests
pytest tests/dashboard/reconciliation/integration/ -v

# Run performance tests
pytest tests/dashboard/reconciliation/test_performance.py --benchmark

# Run all tests with full report
pytest tests/dashboard/reconciliation/ -v --cov=src/dashboard/reconciliation --cov-report=term-missing --cov-report=html
```

---

## 📈 Success Metrics

### Quantitative Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥ 95% | pytest --cov |
| Test Pass Rate | 100% | CI/CD pipeline |
| Performance | < 500ms | Reconciliation execution time |
| False Positive Rate | < 5% | Anomaly detection accuracy |
| Rule Accuracy | ≥ 98% | Validation rule correctness |
| Integration Success | 100% | Dashboard compatibility |

### Qualitative Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| Score Accuracy | Aligned with industry standards | Manual audit vs CVSS/OWASP |
| Data Consistency | Zero cross-tab conflicts | Validation rule coverage |
| Audit Trail Completeness | 100% of changes tracked | Before/after comparison |
| Developer Experience | Seamless integration | Zero breaking changes |

---

## 🚀 Deployment Strategy

### Phase 1: Development & Testing (Days 1-12)
- Implement all components with TDD
- Run comprehensive test suites
- Performance benchmarking
- Code review and refinement

### Phase 2: Staging Deployment (Days 13-14)
- Deploy to staging environment
- Run reconciliation on historical dashboard data
- Compare before/after scores manually
- Validate audit trails
- Fix any edge cases discovered

### Phase 3: Production Rollout (Day 15+)
- **Stage 1:** Silent mode - Reconciliation runs but doesn't modify scores (observation only)
- **Stage 2:** Partial enforcement - Apply only critical rules (R1-R4)
- **Stage 3:** Full enforcement - All 15 rules active
- **Stage 4:** Enable anomaly detection and reporting

### Rollback Plan

If critical issues discovered:
1. Disable reconciliation engine (feature flag)
2. Revert to original collector scores
3. Investigate and fix issues in staging
4. Redeploy with fixes

---

## 📚 Documentation Deliverables

1. **Technical Documentation**
   - API reference for all reconciliation classes
   - Validation rule definitions and rationale
   - Scoring algorithm documentation
   - Integration guide for new collectors

2. **User Documentation**
   - Reconciliation report interpretation guide
   - Violation severity guide
   - Anomaly detection explanation
   - FAQ for score adjustments

3. **Developer Documentation**
   - Architecture decision records (ADRs)
   - Test strategy and coverage
   - Performance optimization guide
   - Contribution guidelines

4. **Compliance Documentation**
   - CVSS alignment certification
   - OWASP compliance mapping
   - ISO 27001 / SOC 2 alignment matrix
   - Audit trail specifications

---

## 🎯 Next Steps

### Immediate Actions (This Week)

1. **Approve Plan:** Review and approve this implementation plan
2. **Setup Environment:** Create reconciliation module structure
3. **Kickoff TDD:** Start with Phase 1 normalizer tests

### Implementation Timeline (2 Weeks)

| Week | Days | Phase | Deliverable |
|------|------|-------|-------------|
| 1 | 1-2 | Phase 1 | Core engine + normalizers |
| 1 | 3-4 | Phase 2 | Validation rules |
| 1 | 5-6 | Phase 3 | Weighted scoring |
| 2 | 7-8 | Phase 4 | Anomaly detection |
| 2 | 9-10 | Phase 5 | Reporting |
| 2 | 11-12 | Phase 6 | Integration + performance |

### Post-Implementation (Week 3+)

1. Staging validation (2 days)
2. Production rollout (phased, 5 days)
3. Monitoring and refinement (ongoing)
4. Documentation finalization (3 days)

---

## 🔒 Risk Assessment

### Technical Risks

**Risk:** Performance degradation on large datasets
- **Mitigation:** Implement caching, optimize algorithms, add performance tests
- **Severity:** Medium
- **Likelihood:** Low

**Risk:** False positives in anomaly detection
- **Mitigation:** Tune thresholds with real data, add confidence scoring
- **Severity:** Medium
- **Likelihood:** Medium

**Risk:** Breaking changes to existing dashboard
- **Mitigation:** Comprehensive integration tests, backward compatibility checks
- **Severity:** High
- **Likelihood:** Low

### Business Risks

**Risk:** Score changes confuse users
- **Mitigation:** Clear documentation, audit trail, gradual rollout
- **Severity:** Medium
- **Likelihood:** Medium

**Risk:** Industry standards change (new CVSS version)
- **Mitigation:** Modular design, configurable mappings, version tracking
- **Severity:** Low
- **Likelihood:** Low

---

## ✅ Acceptance Criteria Summary

### Core Functionality
- [ ] All 15 validation rules implemented and tested
- [ ] Score normalization aligned with CVSS v3.1/v4.0
- [ ] Weighted scoring produces accurate overall scores
- [ ] Anomaly detection flags inconsistencies with >95% accuracy
- [ ] Audit trail tracks all score adjustments

### Quality Standards
- [ ] 95%+ test coverage
- [ ] 100% test pass rate
- [ ] <500ms reconciliation performance
- [ ] Zero breaking changes to existing dashboard
- [ ] Complete API documentation

### Integration Requirements
- [ ] Seamless integration with dashboard_collector.py
- [ ] Compatible with all 6 existing collectors
- [ ] JSON output format matches schema
- [ ] Dashboard UI displays reconciliation metadata

### Compliance & Standards
- [ ] CVSS scoring aligned with NIST standards
- [ ] OWASP Top 10 2025 compliance checks implemented
- [ ] ISO 27001 / SOC 2 alignment documented
- [ ] Industry-standard severity mappings

---

**Plan Status:** 🟢 Ready for Implementation  
**Estimated Effort:** 12 development days (2.5 weeks)  
**Risk Level:** Medium  
**Business Value:** High - Ensures data accuracy and trustworthiness

**Approval Required:** Yes  
**Approver:** Asif Hussain  
**Approval Date:** _Pending_

---

**End of Plan Document**

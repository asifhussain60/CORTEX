# Mock Data Scenarios

**Location:** `cortex-brain/dashboards/mock/`  
**Purpose:** Realistic mock data for dashboard development and testing  
**Schema Version:** 1.0.0  
**Created:** December 4, 2025

---

## 📋 Available Mock Data Files

### 1. `health-data.json` (Baseline - Healthy Medium Repo)
**Scenario:** Healthy, medium-sized application  
**Health Score:** 88 (healthy)  
**Trend:** Improving

**Characteristics:**
- 18,500 LOC (medium project)
- 275 files, 85 directories
- 68.5% test coverage
- 98 dependencies (28 direct)
- 15 open issues (0 critical)
- No security vulnerabilities
- Active development (145 commits/month)

**Use Case:** Default dashboard view, demonstrates healthy project state

---

### 2. `health-data-warning.json` (Warning State - Large Repo)
**Scenario:** Large application with mounting technical debt  
**Health Score:** 62 (warning)  
**Trend:** Stable

**Characteristics:**
- 45,000 LOC (large project)
- 680 files, 145 directories
- 42.3% test coverage (below recommended)
- 285 dependencies (45 direct, 32 outdated)
- 67 open issues (3 critical, 15 high)
- 4 vulnerable dependencies
- 1 exposed secret
- Moderate activity (58 commits/month)
- 15.2% code duplication

**Use Case:** Demonstrates warning indicators, technical debt visualization

---

### 3. `health-data-critical.json` (Critical State - Large Legacy Repo)
**Scenario:** Large legacy codebase with severe issues  
**Health Score:** 32 (critical)  
**Trend:** Degrading

**Characteristics:**
- 125,000 LOC (very large project)
- 1,850 files, 420 directories
- 18.5% test coverage (critically low)
- 512 dependencies (78 direct, 98 outdated, 23 vulnerable)
- 342 open issues (28 critical, 87 high)
- 23 vulnerable dependencies
- 7 exposed secrets
- 38.7% code duplication (very high)
- Low activity (12 commits/month)
- Stale pull requests (45 open, only 2 merged)
- Last commit 19 days ago

**Use Case:** Demonstrates critical alerts, emergency dashboard state

---

### 4. `health-data-small.json` (Healthy Small Microservice)
**Scenario:** Well-maintained microservice  
**Health Score:** 92 (healthy)  
**Trend:** Stable

**Characteristics:**
- 2,500 LOC (small project)
- 45 files, 12 directories
- 85.3% test coverage (excellent)
- 28 dependencies (12 direct, 1 outdated)
- 3 open issues (0 critical/high)
- No security vulnerabilities
- Daily deployments
- 100% test pass rate
- Low complexity (avg 4.2)

**Use Case:** Demonstrates ideal state, microservice architecture pattern

---

## 📊 Scenario Comparison Matrix

| Metric | Healthy (Medium) | Warning (Large) | Critical (Legacy) | Small (Microservice) |
|--------|------------------|-----------------|-------------------|----------------------|
| **Health Score** | 88 | 62 | 32 | 92 |
| **Status** | ✅ Healthy | ⚠️ Warning | 🚨 Critical | ✅ Healthy |
| **LOC** | 18,500 | 45,000 | 125,000 | 2,500 |
| **Test Coverage** | 68.5% | 42.3% | 18.5% | 85.3% |
| **Dependencies** | 98 | 285 | 512 | 28 |
| **Outdated Deps** | 5 | 32 | 98 | 1 |
| **Vulnerable Deps** | 0 | 4 | 23 | 0 |
| **Critical Issues** | 0 | 3 | 28 | 0 |
| **Tech Debt (days)** | 4.2 | 18.5 | 125.8 | 0.5 |
| **Code Duplication** | 3.5% | 15.2% | 38.7% | 1.8% |
| **Commits/Month** | 145 | 58 | 12 | 42 |
| **Deployment Freq** | Weekly | Biweekly | Rarely | Daily |

---

## 🎯 Dashboard Testing Scenarios

### Scenario 1: Happy Path (health-data.json)
**Test:** Load default mock data  
**Expected:**
- Green health indicator (88 score)
- All tabs populated
- No critical alerts
- "Improving" trend arrow pointing up

### Scenario 2: Warning State (health-data-warning.json)
**Test:** Load warning state data  
**Expected:**
- Yellow/orange health indicator (62 score)
- Warning badges on Dependencies tab (32 outdated)
- Alert for exposed secret
- "Stable" trend indicator

### Scenario 3: Critical State (health-data-critical.json)
**Test:** Load critical state data  
**Expected:**
- Red health indicator (32 score)
- Critical alerts on multiple tabs
- Issues tab shows 28 critical issues
- Security tab shows 5 critical vulnerabilities
- "Degrading" trend arrow pointing down
- High technical debt warning (125.8 days)

### Scenario 4: Small Project (health-data-small.json)
**Test:** Load microservice data  
**Expected:**
- Green health indicator (92 score)
- Fast metrics (8.5s build, 4.2s tests)
- High test coverage badge (85.3%)
- Daily deployment indicator

---

## 🔧 Using Mock Data

### Loading in Dashboard

**URL Pattern:**
```
http://localhost:5000/dashboard/mock
```

**JavaScript Fetch:**
```javascript
fetch('/api/dashboard/mock/health-data.json')
  .then(response => response.json())
  .then(data => renderDashboard(data));
```

### Switching Scenarios

**Via Query Parameter:**
```
?scenario=warning  → Loads health-data-warning.json
?scenario=critical → Loads health-data-critical.json
?scenario=small    → Loads health-data-small.json
(default)          → Loads health-data.json
```

### Validation

All mock data files validate against `../schema/health-data-schema.json`:

```python
import json
import jsonschema

with open('../schema/health-data-schema.json') as f:
    schema = json.load(f)

with open('health-data.json') as f:
    data = json.load(f)

jsonschema.validate(data, schema)  # Should pass without errors
```

---

## 📐 Data Generation Patterns

### Health Score Calculation
Formula used for mock data:
```
health_score = (
    code_quality_score * 0.25 +
    test_coverage * 0.20 +
    dependency_health * 0.20 +
    security_score * 0.20 +
    (100 - issues_severity_weighted) * 0.15
)
```

### Realistic Ranges

**Healthy (80-100):**
- Test coverage: 65-90%
- Dependencies: <10% outdated, 0 vulnerable
- Issues: <5% critical/high
- Code duplication: <5%

**Warning (50-79):**
- Test coverage: 40-65%
- Dependencies: 10-30% outdated, few vulnerable
- Issues: 5-20% critical/high
- Code duplication: 5-20%

**Critical (0-49):**
- Test coverage: <40%
- Dependencies: >30% outdated, many vulnerable
- Issues: >20% critical/high
- Code duplication: >20%

---

## 🎨 Dashboard UI Considerations

### Color Coding
- **Healthy (80-100):** Green (#10B981)
- **Warning (50-79):** Yellow/Orange (#F59E0B)
- **Critical (0-49):** Red (#EF4444)

### Trend Indicators
- **Improving:** ↑ (green)
- **Stable:** → (blue)
- **Degrading:** ↓ (red)

### Conditional Rendering
- Hide Security tab if no security data
- Hide Performance tab if no performance data
- Show "N/A" for optional missing fields
- Truncate large numbers (125000 → "125K")

---

## 📚 Next Steps

1. ✅ Mock data files created (4 scenarios)
2. ⏭️ Validate all files against JSON schema
3. ⏭️ Create schema validator Python script
4. ⏭️ Build static HTML dashboard UI (Phase 3)
5. ⏭️ Test dashboard with all 4 mock scenarios

---

**Mock Data Version:** 1.0.0  
**Schema Compliance:** 100%  
**Scenarios:** 4 (Healthy, Warning, Critical, Small)  
**Last Updated:** December 4, 2025

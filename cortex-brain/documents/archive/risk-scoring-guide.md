# Risk Scoring Guide

**Tech Stack Enhancement Dashboard Suite - Risk Scoring Reference**  
**Version:** 1.0.0  
**Last Updated:** December 6, 2025  
**Author:** Asif Hussain

---

## Overview

This guide explains the mathematical formulas, thresholds, and factor weights used across all three dashboards. Understanding these calculations helps you:

- Interpret risk scores accurately
- Customize thresholds for your team's needs
- Validate scoring against business priorities
- Explain scoring decisions to stakeholders

---

## 1. Migration Priority Score

**Dashboard:** Migration Roadmap Generator  
**Purpose:** Rank technologies by urgency for migration

### Formula

```
Priority Score = (Risk Score × 0.5) + (Complexity Factor × 0.3) + (EOL Urgency × 0.2)
```

### Factor Breakdown

#### Risk Score (50% weight)

**Rationale:** Security vulnerabilities and outdated versions are the primary drivers for migration.

**Calculation:**
```
Risk = (CVE_Count × 10) + (Versions_Behind × 5) + (EOL_Proximity × 15)

Where:
- CVE_Count: Number of known vulnerabilities
- Versions_Behind: Major versions behind current stable
- EOL_Proximity: Months until end-of-life (inverted: 0 months = 100, 12+ months = 0)
```

**Example:**
```
Technology: .NET 5
- CVE_Count: 8 → 8 × 10 = 80
- Versions_Behind: 3 (.NET 5 → .NET 8) → 3 × 5 = 15
- EOL_Proximity: 0 months (already EOL) → 100
- Risk Score: 80 + 15 + 100 = 195
```

#### Complexity Factor (30% weight)

**Rationale:** Migration effort impacts timeline and resource allocation.

**Components:**
```
Complexity = (Lines_of_Code / 10000) + (Dependencies_Count / 100) + Breaking_Changes_Flag

Where:
- Lines_of_Code: Codebase size using technology
- Dependencies_Count: Number of packages/libraries
- Breaking_Changes_Flag: 0 (minor update) or 50 (major breaking changes)
```

**Example:**
```
Technology: Angular 12 → Angular 17
- Lines_of_Code: 45,000 → 45,000 / 10,000 = 4.5
- Dependencies_Count: 120 → 120 / 100 = 1.2
- Breaking_Changes: Major (signals removed, standalone default) → 50
- Complexity Factor: 4.5 + 1.2 + 50 = 55.7
```

#### EOL Urgency (20% weight)

**Rationale:** Post-EOL technologies lose security patches and support.

**Thresholds:**
```
0 months (already EOL):   100
1-3 months:               80
4-6 months:               60
7-12 months:              40
13-24 months:             20
25+ months:               0
```

**Example:**
```
Technology: Ubuntu 18.04 LTS
- EOL: May 2023 (already passed)
- EOL Urgency: 100
```

### Priority Score Interpretation

```
90-100:  CRITICAL - Immediate action required (within 1 sprint)
70-89:   HIGH - Prioritize in next quarter
50-69:   MEDIUM - Plan within 6 months
30-49:   LOW - Monitor for changes
0-29:    MINIMAL - Stable, no action needed
```

### Phase Assignment Logic

**Phase 1 (Critical):**
- Priority Score ≥ 70
- Technologies with active CVEs
- Already past EOL

**Phase 2 (High):**
- Priority Score 50-69
- EOL within 6 months
- Major version updates available

**Phase 3 (Medium):**
- Priority Score 30-49
- Minor version updates
- Dependency chain blockers resolved

**Phase 4 (Low Priority):**
- Priority Score < 30
- Optimization opportunities
- Technical debt reduction

---

## 2. Framework Health Score

**Dashboard:** Framework Health Heatmap  
**Purpose:** Assess overall health of each technology/framework

### Formula

```
Health Score = (Version Currency × 0.25) + (CVE Score × 0.30) + (EOL Status × 0.25) + (Community Activity × 0.20)
```

### Factor Breakdown

#### Version Currency (25% weight)

**Rationale:** Recent versions receive security patches and new features.

**Calculation:**
```
Version Currency = 100 - (Versions_Behind × 20)

Capped at 0 (minimum) and 100 (maximum)
```

**Example:**
```
Framework: React
- Current Version: 18.2.0
- Latest Version: 18.2.0
- Versions Behind: 0
- Version Currency: 100 - (0 × 20) = 100
```

#### CVE Score (30% weight - HIGHEST)

**Rationale:** Security vulnerabilities pose the greatest risk to production systems.

**Calculation:**
```
CVE Score = 100 - (Critical_CVEs × 20) - (High_CVEs × 10) - (Medium_CVEs × 5)

Capped at 0 (minimum)
```

**Severity Weights:**
- Critical CVEs: -20 points each (e.g., remote code execution)
- High CVEs: -10 points each (e.g., SQL injection)
- Medium CVEs: -5 points each (e.g., XSS vulnerabilities)
- Low CVEs: Not counted (informational only)

**Example:**
```
Framework: Node.js 14.x
- Critical CVEs: 2 → 2 × 20 = 40
- High CVEs: 5 → 5 × 10 = 50
- Medium CVEs: 3 → 3 × 5 = 15
- CVE Score: 100 - 40 - 50 - 15 = -5 → Capped at 0
```

#### EOL Status (25% weight)

**Rationale:** End-of-life technologies lose vendor support and community contributions.

**Calculation:**
```
EOL Status = Months_Until_EOL × 4.17

Where:
- Already EOL: 0 points
- 12+ months: 50 points
- 24+ months: 100 points (capped)

Formula: (Months / 24) × 100
```

**Example:**
```
Framework: .NET 6 (LTS)
- EOL Date: November 2024
- Current Date: December 2025
- Months Until EOL: -1 (already EOL)
- EOL Status: 0 points
```

#### Community Activity (20% weight)

**Rationale:** Active communities provide support, plugins, and long-term viability.

**Metrics:**
```
Community Activity = (GitHub_Stars / 1000) + (Weekly_Downloads / 100000) + (Recent_Commits / 10)

Capped at 100
```

**Components:**
- GitHub Stars: Popularity indicator
- Weekly Downloads: Active usage (npm, NuGet, PyPI)
- Recent Commits: Development activity (last 90 days)

**Example:**
```
Framework: Vue.js 3
- GitHub Stars: 42,000 → 42,000 / 1000 = 42
- Weekly Downloads: 5,000,000 → 5,000,000 / 100,000 = 50
- Recent Commits: 85 → 85 / 10 = 8.5
- Community Activity: 42 + 50 + 8.5 = 100.5 → Capped at 100
```

### Health Score Interpretation

```
80-100:  EXCELLENT - Healthy, well-maintained
60-79:   GOOD - Minor concerns, monitor
40-59:   FAIR - Plan upgrades, review alternatives
20-39:   POOR - Urgent action needed
0-19:    CRITICAL - Immediate replacement required
```

### Color Coding

```css
Green (#27AE60):    70-100 (Healthy)
Yellow (#F39C12):   50-69  (Warning)
Orange (#E67E22):   30-49  (Attention)
Red (#E74C3C):      0-29   (Critical)
```

---

## 3. Dependency Bloat Score

**Dashboard:** Dependency Bloat Analyzer  
**Purpose:** Identify solutions with excessive package dependencies

### Formula (Z-Score)

```
Bloat Score = (Package_Count - Mean) / Standard_Deviation

Where:
- Package_Count: Number of packages in solution
- Mean: Average package count across all solutions
- Standard_Deviation: Spread of package counts
```

### Statistical Concepts

#### Z-Score Interpretation

**Standard Deviations from Mean:**
```
+3σ:   Extreme outlier (99.7th percentile)
+2σ:   High outlier (97.7th percentile)
+1σ:   Above average (84th percentile)
0σ:    Average (50th percentile)
-1σ:   Below average (16th percentile)
```

**Example:**
```
Dataset:
- Solution A: 20 packages
- Solution B: 35 packages
- Solution C: 40 packages
- Solution D: 45 packages
- Solution E: 200 packages (outlier)

Mean: (20 + 35 + 40 + 45 + 200) / 5 = 68 packages
Std Dev: 72.5

Bloat Scores:
- Solution A: (20 - 68) / 72.5 = -0.66 (below average)
- Solution B: (35 - 68) / 72.5 = -0.46 (below average)
- Solution C: (40 - 68) / 72.5 = -0.39 (below average)
- Solution D: (45 - 68) / 72.5 = -0.32 (below average)
- Solution E: (200 - 68) / 72.5 = 1.82 (warning)
```

### Category Thresholds

```
CRITICAL:  Bloat Score ≥ 2.0  (>95th percentile)
WARNING:   Bloat Score 1.0-1.99 (84th-95th percentile)
NORMAL:    Bloat Score < 1.0  (<84th percentile)
```

**Actions by Category:**
- **CRITICAL**: Immediate review required, split solution, remove unused packages
- **WARNING**: Schedule refactoring, analyze dependencies, consolidate packages
- **NORMAL**: No action needed, maintain current approach

### Outlier Detection (IQR Method)

**Tukey's Fences Formula:**
```
Outlier Threshold = Q3 + (1.5 × IQR)

Where:
- Q1 (25th percentile): First quartile
- Q3 (75th percentile): Third quartile
- IQR: Interquartile Range = Q3 - Q1
```

**Example:**
```
Dataset: [20, 25, 30, 35, 40, 45, 50, 120]

Sorted: [20, 25, 30, 35, 40, 45, 50, 120]
Q1 (25th): 27.5 (average of 25 and 30)
Q3 (75th): 47.5 (average of 45 and 50)
IQR: 47.5 - 27.5 = 20

Outlier Threshold: 47.5 + (1.5 × 20) = 77.5

Result: 120 packages is an outlier (>77.5)
```

### Histogram Bins

**5-Bin Distribution:**
```
Bin 1:  0-50 packages    (Lean)
Bin 2:  51-100 packages  (Moderate)
Bin 3:  101-150 packages (Heavy)
Bin 4:  151-200 packages (Very Heavy)
Bin 5:  200+ packages    (Extreme)
```

**Interpretation:**
- **Bin 1 (0-50)**: Microservices, focused solutions
- **Bin 2 (51-100)**: Standard web applications
- **Bin 3 (101-150)**: Large enterprise applications
- **Bin 4 (151-200)**: Monolithic systems
- **Bin 5 (200+)**: Legacy systems, potential over-engineering

---

## 4. Customizing Thresholds

### When to Adjust

1. **Team Context**: Startup vs enterprise (different risk tolerances)
2. **Industry**: Healthcare/finance (stricter) vs gaming (lenient)
3. **Project Phase**: Greenfield (aggressive updates) vs maintenance (conservative)

### Migration Priority Adjustments

**Conservative (Large Enterprise):**
```python
CRITICAL_THRESHOLD = 80  # Higher bar
HIGH_THRESHOLD = 65
MEDIUM_THRESHOLD = 45
```

**Aggressive (Startup):**
```python
CRITICAL_THRESHOLD = 60  # Lower bar, faster action
HIGH_THRESHOLD = 40
MEDIUM_THRESHOLD = 25
```

### Health Score Adjustments

**Security-Critical Industry (Healthcare, Finance):**
```python
CVE_WEIGHT = 0.40  # Increase from 0.30
VERSION_WEIGHT = 0.30  # Increase from 0.25
COMMUNITY_WEIGHT = 0.10  # Decrease from 0.20
```

**Cutting-Edge Tech Company:**
```python
VERSION_WEIGHT = 0.35  # Prefer latest versions
COMMUNITY_WEIGHT = 0.25  # Value ecosystem
CVE_WEIGHT = 0.25  # Tolerate some risk
```

### Bloat Score Adjustments

**Microservices Architecture:**
```python
CRITICAL_THRESHOLD = 1.5  # Stricter (expect fewer packages)
WARNING_THRESHOLD = 0.8
```

**Monolithic Applications:**
```python
CRITICAL_THRESHOLD = 2.5  # More lenient
WARNING_THRESHOLD = 1.5
```

---

## 5. Real-World Examples

### Example 1: Critical Migration (Angular 12)

**Scenario:** Large enterprise web app on Angular 12 (EOL May 2023)

**Scores:**
```
Risk Score: 85
- CVEs: 3 critical, 5 high → (3×20) + (5×10) = 110
- Versions Behind: 5 (Angular 12 → 17) → 5×5 = 25
- EOL: Already passed → 100
- Subtotal: 110 + 25 + 100 = 235 → Capped at 100

Complexity: 62
- Lines of Code: 120,000 → 120,000 / 10,000 = 12
- Dependencies: 180 → 180 / 100 = 1.8
- Breaking Changes: Major (signals removed) → 50
- Subtotal: 12 + 1.8 + 50 = 63.8

EOL Urgency: 100 (already EOL)

Priority Score: (100 × 0.5) + (62 × 0.3) + (100 × 0.2)
              = 50 + 18.6 + 20 = 88.6 → CRITICAL
```

**Recommendation:** Phase 1 (immediate), allocate 320 hours, 8-week timeline

### Example 2: Healthy Framework (React 18)

**Scenario:** Modern SPA with React 18.2.0

**Scores:**
```
Version Currency: 100 (on latest)
CVE Score: 100 (no known vulnerabilities)
EOL Status: 100 (24+ months until EOL)
Community Activity: 100 (very active)

Health Score: (100 × 0.25) + (100 × 0.30) + (100 × 0.25) + (100 × 0.20)
            = 25 + 30 + 25 + 20 = 100 → EXCELLENT
```

**Recommendation:** No action, monitor quarterly

### Example 3: Dependency Bloat (Legacy API)

**Scenario:** .NET API with 250 packages (mean: 65, std dev: 55)

**Scores:**
```
Bloat Score: (250 - 65) / 55 = 3.36 → CRITICAL (>2.0)

Outlier Detection:
- Dataset Q3: 85 packages
- IQR: 45
- Threshold: 85 + (1.5 × 45) = 152.5
- Result: 250 > 152.5 → Outlier confirmed
```

**Recommendation:**
1. Remove unused packages (estimated 40% reduction)
2. Consolidate overlapping dependencies (Newtonsoft.Json + System.Text.Json)
3. Split into microservices (target: 80-100 packages per service)

---

## 6. Validation & Testing

### Manual Validation

**Steps:**
1. Calculate score manually with spreadsheet
2. Compare against dashboard output
3. Verify thresholds trigger correct categories
4. Test edge cases (0 packages, single solution)

**Example Spreadsheet:**
```
| Technology | Risk | Complexity | EOL | Priority | Phase |
|-----------|------|------------|-----|----------|-------|
| .NET 5    | 100  | 45         | 100 | 88.5     | 1     |
| Node 14   | 75   | 30         | 80  | 63.5     | 2     |
```

### Automated Testing

**Unit Tests:**
```python
def test_priority_calculation():
    risk, complexity, eol = 85, 62, 100
    priority = (risk * 0.5) + (complexity * 0.3) + (eol * 0.2)
    assert priority == 88.6
    assert get_phase(priority) == "Phase 1"
```

**Integration Tests:**
```python
def test_health_score_consistency():
    analyzer = FrameworkHealthAnalyzer()
    score1 = analyzer.calculate_health(react_data)
    score2 = analyzer.calculate_health(react_data)  # Same data
    assert score1 == score2  # Deterministic
```

---

## 7. Troubleshooting Scores

### Issue: Score Seems Too High/Low

**Checklist:**
1. Verify input data accuracy (CVE counts, version numbers)
2. Check for formula typos (wrong weights)
3. Validate capping logic (scores should be 0-100)
4. Review recent updates (EOL dates change)

**Example Debug:**
```
Expected Health: 75
Actual Health: 45

Investigation:
- Version Currency: 100 ✓
- CVE Score: 20 ✗ (found 4 critical CVEs, expected 0)
- EOL Status: 50 ✓
- Community: 80 ✓

Root Cause: Recent CVE disclosure (not in cache)
Solution: Update CVE database, re-calculate
```

### Issue: Inconsistent Phase Assignments

**Symptoms:**
- Lower priority score in Phase 1
- Higher priority score in Phase 3

**Causes:**
1. Manual phase overrides
2. Dependency chains (blocking tasks)
3. Large tasks (>160h get dedicated phase)

**Solution:** Review `assignPhases()` logic, check dependency graph

---

**Questions or customization needs?**  
Contact: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

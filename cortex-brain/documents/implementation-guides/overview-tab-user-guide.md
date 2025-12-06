# Overview Tab User Guide

**Version:** 1.0  
**Last Updated:** 2025-12-06  
**Purpose:** Help users understand and interpret the Overview tab metrics

---

## Quick Start

The **Overview tab** provides a high-level health snapshot of your codebase in seconds. It answers:
- **Is my codebase healthy?** (Overall health score + status)
- **What needs attention?** (Critical issues alerts)
- **What's it made of?** (Language composition breakdown)
- **How is it trending?** (Improving, stable, or declining)

**Time to comprehension:** <30 seconds for critical issues, <3 minutes for full overview

---

## Dashboard Sections

### 1. Health Score Hero

**Location:** Top center of Overview tab  
**Purpose:** Single-number health assessment

**What you see:**
- **Large circular gauge** (0-100 scale)
- **Health score** (e.g., 92)
- **Status badge** (Healthy / Warning / Critical)
- **Trend indicator** (↗ Improving / → Stable / ↘ Declining)

**How to interpret:**

| Score Range | Status | Meaning | Action |
|-------------|--------|---------|--------|
| 80-100 | ✅ Healthy | Codebase in excellent condition | Maintain current practices |
| 60-79 | ⚠️ Warning | Some issues need attention | Review warnings, plan improvements |
| 0-59 | 🚨 Critical | Significant issues present | Immediate action required |

**Trend meanings:**
- **↗ Improving:** Recent changes increased health (good!)
- **→ Stable:** Health unchanged from last scan
- **↘ Declining:** Recent changes decreased health (investigate)

**Example interpretation:**
```
Score: 92 ✅ Healthy ↗ Improving
```
"Your codebase is in excellent condition and getting better with recent changes."

---

### 2. Key Metrics Cards

**Location:** Below health gauge  
**Purpose:** Essential codebase statistics

**Metrics explained:**

#### Total Files
**What:** Number of code files in repository  
**Typical range:** 50-5000 (varies by project size)  
**Watch for:** Sudden increases (mass file additions) or decreases (deletions)

#### Total LOC (Lines of Code)
**What:** Sum of all code lines across all files  
**Typical range:** 1K-500K+ (varies by project)  
**Watch for:** Rapid growth without corresponding tests = technical debt

#### Test Coverage
**What:** Percentage of code covered by automated tests  
**Target:** >80% (excellent), 60-80% (good), <60% (needs improvement)  
**Watch for:** Coverage dropping below 70% = test debt accumulating

#### Maintainability Index
**What:** Code maintainability score (0-100)  
**Calculation:** Based on cyclomatic complexity, LOC, Halstead volume  
**Target:** >85 (excellent), 70-85 (good), <70 (hard to maintain)  
**Watch for:** Scores <70 = refactoring needed

#### Technical Debt (Hours)
**What:** Estimated hours to fix all code issues  
**Typical range:** 5-50 hours (varies by project size)  
**Watch for:** Debt growing faster than codebase = quality declining

**Example interpretation:**
```
Total Files: 994  
Total LOC: 45,678  
Test Coverage: 78.5%  
Maintainability Index: 85  
Technical Debt: 12.5 hours
```

**Assessment:** Healthy codebase with good maintainability. Test coverage is decent but could improve. Technical debt is manageable (~12 hours to fix all issues).

---

### 3. Health Categories Breakdown

**Location:** Left side, below key metrics  
**Purpose:** Detailed health by category

**Categories explained:**

#### Code Quality
**What:** Code cleanliness, complexity, duplication  
**Healthy when:** Few long files, low complexity, minimal duplication  
**Issues:** Long files (>500 lines), high complexity (>10 cyclomatic), duplicate code

#### Security
**What:** Known vulnerabilities in dependencies  
**Healthy when:** Zero CVEs, all dependencies current  
**Issues:** High-severity CVEs, outdated dependencies with known exploits

#### Tests
**What:** Test coverage and quality  
**Healthy when:** >80% coverage, all tests passing  
**Issues:** Low coverage (<60%), failing tests, no tests for critical code

#### Documentation
**What:** Code documentation completeness  
**Healthy when:** >80% of public APIs documented  
**Issues:** Missing README, undocumented APIs, outdated docs

**How to prioritize:**
1. Fix 🚨 Critical categories first (security vulnerabilities)
2. Address ⚠️ Warning categories next (low test coverage)
3. Maintain ✅ Healthy categories (keep code quality high)

---

### 4. Composition Pie Chart

**Location:** Right side, below key metrics  
**Purpose:** Language distribution visualization

**What you see:**
- **Pie chart** with colored segments per language
- **Language legend** with percentages
- **LOC (Lines of Code)** per language

**How to interpret:**

**Balanced composition:**
```
Python: 75.2% (34,340 LOC)
JavaScript: 15.8% (7,219 LOC)
YAML: 5.3% (2,421 LOC)
Markdown: 3.7% (1,698 LOC)
```
"Python backend with JavaScript frontend, YAML configs, Markdown docs. Typical full-stack application."

**Single-language dominance:**
```
C#: 98.5% (450,000 LOC)
XML: 1.5% (7,000 LOC)
```
".NET application with minimal configuration. Monolithic architecture."

**Fragmented composition:**
```
10+ languages, each <15%
```
"Polyglot codebase. May indicate microservices or integration complexity."

**Watch for:**
- **Unexpected languages:** Shell scripts in frontend project = deployment complexity
- **Test file languages:** TypeScript tests for JavaScript app = good practice
- **Config file bloat:** >10% YAML/JSON = over-configuration

---

### 5. Critical Issues Alert

**Location:** Bottom of Overview tab  
**Purpose:** Immediate attention items

**What you see:**
- **Red alert banner** (if critical issues exist)
- **Issue list** with severity, category, message, count

**Issue structure:**
```
[HIGH] Documentation: Documentation coverage below recommended threshold (1 issue)
```

**Severity levels:**
- **HIGH:** Fix within 1 sprint (security, blocking bugs)
- **MEDIUM:** Fix within 1-2 months (code quality, performance)
- **LOW:** Fix when convenient (cosmetic, minor improvements)

**Categories:**
- **security:** Vulnerabilities, exposed secrets, weak crypto
- **quality:** Code smells, complexity, duplication
- **tests:** Low coverage, failing tests, missing tests
- **documentation:** Missing docs, outdated docs, broken links
- **performance:** Slow queries, memory leaks, inefficient algorithms

**How to respond:**

| Category | Response |
|----------|----------|
| Security (HIGH) | Drop everything, patch immediately |
| Quality (HIGH) | Schedule refactoring sprint |
| Tests (HIGH) | Add tests before next deployment |
| Documentation (MEDIUM) | Update docs in next sprint |
| Performance (MEDIUM) | Profile and optimize bottlenecks |

---

## Common Scenarios

### Scenario 1: New project onboarding

**You see:**
```
Score: 45 🚨 Critical
Test Coverage: 15%
Critical Issues: 8 (5 high-severity)
```

**What it means:**  
Legacy project with technical debt. Needs investment before active development.

**Action plan:**
1. Week 1: Fix high-severity security issues
2. Week 2-3: Add tests for critical paths (target 50% coverage)
3. Week 4: Refactor highest-complexity files
4. Month 2: Increase coverage to 70%+

---

### Scenario 2: Post-release health check

**You see:**
```
Score: 88 ✅ Healthy → Stable
Test Coverage: 82% (↑ from 78%)
Technical Debt: 8 hours (↓ from 15 hours)
```

**What it means:**  
Release went well, team paid down debt, improved tests.

**Action:**  
Maintain current velocity. Celebrate wins with team.

---

### Scenario 3: Declining health trend

**You see:**
```
Score: 72 ⚠️ Warning ↘ Declining (was 85 last week)
New Issues: 12 code quality warnings
Maintainability: 68 (was 82)
```

**What it means:**  
Recent code additions decreased quality. Rushed implementation?

**Action:**
1. Review recent commits (identify culprits)
2. Refactor new code (apply SOLID principles)
3. Add code reviews (prevent future decline)
4. Target: Return to 80+ within 2 sprints

---

## Tips for Decision-Makers

### For Engineering Managers

**Weekly ritual:**
1. Check health score trend (improving/stable/declining?)
2. Review critical issues (any blockers?)
3. Monitor test coverage (staying above 70%?)
4. Track technical debt (growing or shrinking?)

**Red flags:**
- Health declining for 3+ weeks → Schedule tech debt sprint
- Critical issues growing → Adjust sprint priorities
- Test coverage <60% → Implement testing mandate

### For Product Owners

**Pre-release checklist:**
1. Health score >70? (Good to ship)
2. Zero high-severity security issues? (Must fix before ship)
3. Test coverage >60%? (Acceptable risk)
4. Technical debt <30 hours? (Manageable)

**Trade-offs:**
- Ship with score 65-75: Acceptable if no security issues
- Ship with coverage 50-60%: Risky, add monitoring
- Ship with 20+ hours debt: Plan debt paydown sprint

### For Developers

**Daily workflow:**
1. Before coding: Check current health baseline
2. After changes: Run tests, verify coverage maintained
3. Before PR: Ensure health score unchanged or improved
4. After merge: Confirm Overview tab reflects improvements

**Best practices:**
- Add tests BEFORE implementation (TDD)
- Refactor when maintainability <75
- Document public APIs immediately
- Fix security issues same day

---

## Glossary

**Health Score:** Composite score (0-100) based on code quality, security, tests, documentation.

**LOC (Lines of Code):** Count of non-blank, non-comment source code lines.

**Test Coverage:** Percentage of code lines executed by automated tests.

**Maintainability Index:** Microsoft metric (0-100) measuring code maintainability.

**Technical Debt:** Estimated hours to fix all code issues (complexity, duplication, smells).

**Cyclomatic Complexity:** Count of independent code paths (>10 = hard to test).

**CVE (Common Vulnerabilities and Exposures):** Publicly disclosed security vulnerabilities.

**Code Smell:** Symptom of deeper problem (long methods, large classes, duplicate code).

---

## Frequently Asked Questions

**Q: Why is my health score 45 even though tests pass?**  
A: Health considers more than tests: code quality, security, documentation. Low maintainability (complex code) or missing docs can lower the score.

**Q: What's a "good" health score?**  
A: 80+ is excellent, 60-79 is acceptable, <60 needs improvement. Context matters: greenfield project vs legacy system.

**Q: How often does Overview tab update?**  
A: Data refreshes on each repository scan. Trigger manually with "Scan Now" or automatic on git push.

**Q: Can I customize health score weights?**  
A: Not yet. Planned for Phase 9 (Tech Stack Enhancements). Currently uses standard weights: Quality 35%, Security 30%, Tests 25%, Docs 10%.

**Q: Why is test coverage different from CI/CD?**  
A: Coverage calculation may differ. Overview uses file-based coverage, CI/CD may use branch coverage. Verify tool settings match.

**Q: What does "Trend: Improving" mean?**  
A: Health score increased since last scan. Indicates positive changes (more tests, refactoring, bug fixes).

---

## Troubleshooting

**Issue:** Overview tab shows "No data available"  
**Solution:** Run collector: `python -m src.dashboard.data.overview_collector --path /repo/path`

**Issue:** Health score seems inaccurate  
**Solution:** Check last scan date. Re-scan if >1 week old.

**Issue:** Composition chart missing languages  
**Solution:** Verify code files have recognized extensions (.py, .js, etc.)

**Issue:** Critical issues count differs from IDE  
**Solution:** Overview uses automated static analysis. IDE may have different linter rules.

---

## Next Steps

1. **Review health categories:** Identify weakest area
2. **Check critical issues:** Prioritize high-severity fixes
3. **Track trends:** Bookmark Overview tab, check weekly
4. **Set team goals:** Target 80+ health, 75+ coverage
5. **Integrate with workflow:** Add health checks to CI/CD

**Related documentation:**
- Developer Guide: Extending Overview components
- Metric Definitions: Detailed calculation formulas
- Dashboard Launcher: How to run dashboard locally

---

**Questions or feedback?** Open an issue at github.com/asifhussain60/CORTEX

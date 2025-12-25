# STS Validation Application

**Purpose:** Deliberately flawed e-commerce application for validating CORTEX 4.0 capabilities

**Status:** 🚧 Phase 13B - Week 1 Day 1 (Application Structure)

**Score:** 25/100 (F grade) → Target: 90+/100 (A grade)

---

## 📋 Overview

This application contains **61 documented flaws** across 6 categories, designed to test CORTEX 4.0's ability to detect, diagnose, and remediate real-world code issues.

**Philosophy:** "Sharpen The Saw" (Stephen Covey's 7th Habit) - Continuous improvement through deliberate practice

---

## 🏗️ Architecture

### 4-Layer Structure

```
src/
├── api/          # HTTP endpoints, authentication, routing
├── business/     # Core business logic, rules, workflows  
├── data/         # Database access, caching, models
└── utils/        # Helpers, validators, formatters
```

### Technology Stack (Deliberately Outdated)

- **Framework:** Flask 1.1.2 (vulnerable version)
- **Database:** SQLite with raw SQL (SQL injection prone)
- **ORM:** SQLAlchemy 1.x (outdated)
- **Testing:** pytest with 15% coverage
- **Documentation:** Minimal, outdated

---

## 🐛 Documented Flaws (61 Total)

### Security Vulnerabilities (12)
| ID | Location | Severity | Description |
|----|----------|----------|-------------|
| SEC-01 | `auth.py:15` | CRITICAL | Hardcoded JWT secret |
| SEC-02 | `auth.py:42` | CRITICAL | No password hashing |
| SEC-03 | `database.py:28` | CRITICAL | SQL injection (f-strings) |
| SEC-04 | `products.py:67` | CRITICAL | SQL injection (string concat) |
| SEC-05 | `app.py:10` | HIGH | Debug mode enabled in prod |
| SEC-06 | `auth.py:89` | HIGH | Weak JWT algorithm (HS256) |
| SEC-07 | `users.py:134` | MEDIUM | No rate limiting |
| SEC-08 | `.env` | CRITICAL | Secrets in version control |
| SEC-09 | `requirements.txt` | HIGH | Vulnerable Flask 1.1.2 |
| SEC-10 | `setup.sh:22` | MEDIUM | Shell injection risk |
| SEC-11 | `cache.py:45` | HIGH | Pickle deserialization |
| SEC-12 | `app.py:78` | MEDIUM | CORS allow all origins |

### SOLID Principle Violations (15)
| ID | Principle | Violation | Complexity |
|----|-----------|-----------|------------|
| SOL-01 | SRP | God class `users.py` (auth + CRUD + validation + email) | High |
| SOL-02 | SRP | 500+ line `helpers.py` with 20+ functions | High |
| SOL-03 | OCP | Hard-coded pricing rules (not extensible) | Medium |
| SOL-04 | OCP | If/else chains for payment processors | Medium |
| SOL-05 | LSP | Child classes throw NotImplementedError | Medium |
| ... | ... | ... | ... |

### Code Quality Issues (20)
| ID | Type | Location | Complexity | Impact |
|----|------|----------|------------|--------|
| CQ-01 | High Complexity | `orders.py:create_order()` | 87 | Critical |
| CQ-02 | High Complexity | `users.py:validate_user()` | 45 | High |
| CQ-03 | Duplication | `payment.py` (3 similar methods, 80% same code) | - | Medium |
| ... | ... | ... | ... | ... |

### Performance Issues (8)
### Testing Gaps (3)
### Documentation Issues (8)

**Full Details:** See `docs/FLAW-CATALOG.md`

---

## 🎯 Validation Scenarios

### 1. Code Sanitization
**Test:** Can CORTEX remove all 5 hardcoded secrets?
**Expected:** 5/5 secrets sanitized, tests still pass

### 2. Planning System 2.0
**Test:** Can CORTEX detect HIGH complexity and create incremental plan?
**Expected:** Complexity detected, 4-phase plan, DoR/DoD compliance

### 3. TDD Mastery
**Test:** Can CORTEX achieve RED→GREEN→REFACTOR cycle?
**Expected:** 15% → 90%+ test coverage, complexity reduced

### 4. System Maintenance
**Test:** Can CORTEX run 7-phase maintenance without errors?
**Expected:** 0 critical issues after completion

### 5. System Refinement  
**Test:** Can CORTEX resolve 35+ SOLID/quality violations?
**Expected:** All violations resolved, 60%+ coverage

### 6. Architectural Review
**Test:** Can CORTEX score 25 → 90+ accurately?
**Expected:** Accurate scoring, 20+ actionable recommendations

### 7. ADO Operations
**Test:** Can CORTEX generate valid ADO work items?
**Expected:** Valid ADO format, complete hierarchy

### 8. Holistic Discovery
**Test:** Can CORTEX find duplicates and dead code with 100% accuracy?
**Expected:** 0 false positives, all issues found

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip
- SQLite3

### Installation

```bash
# Install dependencies (deliberately vulnerable)
pip install -r requirements.txt

# Setup database
python scripts/setup.sh

# Run application (will fail due to bugs)
python src/app.py
```

### Running Tests

```bash
# Run minimal test suite (15% coverage)
pytest tests/

# Expected: Many tests skipped/failing
```

---

## 📊 Baseline Metrics

| Metric | Current | Target | Transformation |
|--------|---------|--------|----------------|
| Overall Score | 25/100 (F) | 90+/100 (A) | **+260%** |
| Security Vulnerabilities | 12 | 0 | **-100%** |
| Test Coverage | 15% | 90%+ | **+500%** |
| Avg Complexity | 68 | <15 | **-78%** |
| SOLID Violations | 15 | 0 | **-100%** |
| Code Quality Issues | 20 | 0 | **-100%** |
| Performance Issues | 8 | 0 | **-100%** |
| Documentation Score | 20/100 | 85+/100 | **+325%** |

---

## 📈 Transformation Roadmap

### Week 1-2: Application Creation
- ✅ Directory structure
- ⏳ Implement 4 layers with deliberate flaws
- ⏳ Create minimal documentation
- ⏳ Seed database with test data

### Week 3-4: Capabilities 1-4
- ⏳ Code Sanitization validation
- ⏳ Planning System 2.0 validation
- ⏳ TDD Mastery validation
- ⏳ System Maintenance validation

### Week 5-6: Capabilities 5-8
- ⏳ System Refinement validation
- ⏳ Architectural Review validation
- ⏳ ADO Operations validation
- ⏳ Holistic Discovery validation

### Week 7: Final Measurement
- ⏳ Re-measure all metrics
- ⏳ Generate transformation dashboard
- ⏳ Create capability certification matrix

---

## 📚 Documentation

- `docs/ARCHITECTURE.md` - System design (outdated, contradictory)
- `docs/API.md` - API endpoints (missing endpoints)
- `docs/DEPLOYMENT.md` - Deployment guide (obsolete)
- `docs/FLAW-CATALOG.md` - Complete list of 61 deliberate flaws

---

## 🎓 Learning Objectives

**For CORTEX 4.0:**
- Validate detection accuracy (can it find all 61 flaws?)
- Measure remediation effectiveness (can it fix them?)
- Test production readiness (does it work end-to-end?)

**For Developers:**
- See CORTEX capabilities in action
- Learn code quality best practices
- Understand transformation process

---

## ⚠️ Warnings

**DO NOT USE IN PRODUCTION**
- This application is deliberately insecure
- Contains 12 critical security vulnerabilities
- SQL injection, authentication bypass, data leaks
- For validation purposes ONLY

---

## 📄 License

MIT License - For CORTEX validation purposes only

**Author:** Asif Hussain  
**Created:** December 25, 2025  
**Phase:** 13B - STS Validation  
**Version:** 0.1.0 (Baseline - Deliberately Flawed)

# STS Validation Application - Technical Overview

**Purpose:** Deliberately flawed e-commerce application for CORTEX 4.0 validation  
**Status:** 🔴 BASELINE (F Grade: 25/100)  
**Location:** `cortex-sample-apps/sts-validation-app/`  
**Author:** Asif Hussain

---

## 🎯 Application Purpose

The STS (Sharpen The Saw) Validation Application is a **real-world e-commerce system** intentionally designed with 65 documented flaws across 7 categories. It serves as the ultimate test for CORTEX 4.0's transformation capabilities.

**Philosophy:** Based on Stephen Covey's 7th Habit - "Sharpen The Saw" - continuous renewal through deliberate practice.

---

## 🏗️ Architecture

### 4-Layer Structure

```
src/
├── api/          # REST API layer
│   ├── auth.py           # Authentication (SEC-01, SEC-06)
│   ├── users.py          # User management (SOL-01, god class 654 LOC)
│   ├── orders.py         # Order processing (CQ-01, complexity 87)
│   └── products.py       # Product catalog (SEC-04, SQL injection)
│
├── business/     # Business logic layer
│   ├── pricing.py        # Pricing rules (SOL-03, hardcoded logic)
│   ├── payment.py        # Payment processing (SOL-04, if/else chains)
│   ├── shipping.py       # Shipping calculation (CQ-04, arrow anti-pattern)
│   └── inventory.py      # Stock management (SOL-15, concrete dependency)
│
├── data/         # Data access layer
│   ├── database.py       # DB connection (SEC-03, SQL injection, PERF-08)
│   ├── repositories.py   # Repository pattern (SOL-05, LSP violation)
│   ├── models.py         # Data models (SOL-06, signature changes)
│   └── cache.py          # Caching layer (SEC-11, pickle, PERF-02)
│
└── utils/        # Utility layer
    ├── helpers.py        # God object (SOL-02, 23 functions, 587 LOC)
    ├── validators.py     # Lazy class (CQ-10, only 45 LOC)
    ├── formatters.py     # Utility functions
    └── legacy_api.py     # Dead code (CQ-11, unused 6 months)
```

### Technology Stack (Deliberately Outdated)

| Component | Version | Issue | Flaw ID |
|-----------|---------|-------|---------|
| **Framework** | Flask 1.1.2 | Vulnerable (CVE-2021-45382) | SEC-09 |
| **Database** | SQLite | Raw SQL (injection prone) | SEC-03, SEC-04 |
| **ORM** | SQLAlchemy 1.x | Outdated, no async | PERF-04 |
| **Testing** | pytest | 15% coverage | TEST-01 to TEST-08 |
| **Documentation** | Minimal | Outdated, contradictory | DOC-01 to DOC-07 |

---

## 🐛 The 65 Documented Flaws

### Category Breakdown

```
┌──────────────────────────────────────────────────┐
│  FLAW DISTRIBUTION                               │
│  ══════════════════════════════════════════      │
│                                                  │
│  Security (12):        ████████████ CRITICAL    │
│  SOLID (15):           ███████████████          │
│  Code Quality (20):    ████████████████████     │
│  Performance (8):      ████████                 │
│  Testing (8):          ████████                 │
│  Documentation (7):    ███████                  │
│  UI/Visual (4):        ████                     │
│                                                  │
│  TOTAL: 65 FLAWS                                │
└──────────────────────────────────────────────────┘
```

### Security Vulnerabilities (12) - OWASP Top 10:2021

| ID | OWASP | CWE | Location | Severity | Description |
|----|-------|-----|----------|----------|-------------|
| SEC-01 | A02 | CWE-798 | `auth.py:23` | 🔴 CRITICAL | Hardcoded JWT secret |
| SEC-02 | A02 | CWE-916 | `auth.py:42` | 🔴 CRITICAL | Plaintext passwords |
| SEC-03 | A03 | CWE-89 | `database.py:75` | 🔴 CRITICAL | SQL injection (f-strings) |
| SEC-04 | A03 | CWE-89 | `products.py:67` | 🔴 CRITICAL | SQL injection (concat) |
| SEC-05 | A05 | CWE-489 | `app.py:10` | 🟡 HIGH | Debug mode enabled |
| SEC-06 | A02 | CWE-327 | `auth.py:89` | 🟡 HIGH | Weak crypto (HS256) |
| SEC-07 | A04 | CWE-770 | `users.py:134` | 🟠 MEDIUM | No rate limiting |
| SEC-08 | A02 | CWE-798 | `.env` | 🔴 CRITICAL | Secrets in version control |
| SEC-09 | A06 | CWE-1104 | `requirements.txt` | 🟡 HIGH | Vulnerable Flask 1.1.2 |
| SEC-10 | A03 | CWE-78 | `setup.sh:22` | 🟠 MEDIUM | OS command injection |
| SEC-11 | A08 | CWE-502 | `cache.py:45` | 🟡 HIGH | Insecure pickle |
| SEC-12 | A05 | CWE-942 | `app.py:78` | 🟠 MEDIUM | Permissive CORS |

### SOLID Violations (15)

| ID | Principle | Violation | Location | Metrics |
|----|-----------|-----------|----------|---------|
| SOL-01 | SRP | God class | `users.py` | 32 methods, 654 LOC |
| SOL-02 | SRP | God object | `helpers.py` | 23 functions, 587 LOC |
| SOL-03 | OCP | Hardcoded rules | `pricing.py:45` | 15 if/elif branches |
| SOL-04 | OCP | If/else chains | `payment.py:89` | 8 payment types |
| SOL-05 | LSP | NotImplementedError | `repositories.py:123` | 3 broken methods |
| SOL-06 | LSP | Signature changes | `models.py:67` | Type mismatches |
| SOL-07 | ISP | Fat interface | `IRepository` | 18 methods |
| SOL-08 | ISP | Unused methods | `product_service.py` | 18 depend, 4 used |
| SOL-09 | DIP | Direct instantiation | `orders.py:34` | 7 `new` calls |
| SOL-10 | DIP | Wrong direction | `business/` → `data/` | 12 direct imports |
| SOL-11 | SRP | 4 responsibilities | `order_manager.py` | Low cohesion |
| SOL-12 | OCP | Modification needed | `shipping.py` | 3 change points |
| SOL-13 | LSP | Precondition | `premium_user.py:89` | Extra validation |
| SOL-14 | ISP | Mixed concerns | `IRepository` | Cache + CRUD |
| SOL-15 | DIP | Business instantiates DB | `inventory.py:23` | `db = Database()` |

### Code Quality Issues (20)

| ID | Anti-Pattern | Location | Metrics |
|----|--------------|----------|---------|
| CQ-01 | Monster Method | `create_order()` | Complexity 87, 245 LOC |
| CQ-02 | Complex Conditional | `validate_user()` | Complexity 45, 18 conditions |
| CQ-03 | Copy-Paste | `payment.py` | 80% duplicate |
| CQ-04 | Arrow Anti-Pattern | `calculate_cost()` | Nesting depth 7 |
| CQ-05 | Magic Numbers | `pricing.py` | 23 hardcoded constants |
| CQ-06 | Long Parameter List | `create_user()` | 9 parameters |
| CQ-07 | Data Clumps | Address fields | 5 fields × 8 repeats |
| CQ-08 | Feature Envy | `order_service.py:123` | 8 Product methods |
| CQ-09 | Inappropriate Intimacy | `User` ↔ `Order` | Bidirectional coupling |
| CQ-10 | Lazy Class | `validators.py` | 3 methods, 45 LOC |
| CQ-11 | Dead Code | `legacy_api.py` | Unused 6 months |
| CQ-12 | Speculative Generality | `base_processor.py` | No subclasses |
| CQ-13 | Primitive Obsession | String status | 15 string literals |
| CQ-14 | Switch Statements | `process_payment()` | 8 payment types |
| CQ-15 | Temporary Field | `temp_total` | Set/unset pattern |
| CQ-16 | Middle Man | `order_facade.py` | Delegates everything |
| CQ-17 | Message Chains | User→Order→Product | 4-level chain |
| CQ-18 | Refused Bequest | BasicUser extends Admin | Wrong hierarchy |
| CQ-19 | Comments | Commented code | 150+ LOC |
| CQ-20 | TODO Comments | 34 unresolved TODOs | 2 years old |

### Performance Bottlenecks (8)

| ID | Issue | Location | Impact |
|----|-------|----------|--------|
| PERF-01 | N+1 Queries | `get_orders_with_products()` | 23 queries vs 2 |
| PERF-02 | Memory Leak | `OrderCache` | +500MB/hour |
| PERF-03 | No Pagination | `load_all_products()` | 50K products at once |
| PERF-04 | Blocking I/O | API calls | 5s wait time |
| PERF-05 | No Caching | All DB queries | 10x slower |
| PERF-06 | Inefficient Sort | `rank_products()` | O(n²) bubble sort |
| PERF-07 | File Loading | CSV import | 500MB in memory |
| PERF-08 | No Connection Pool | DB connections | New per request |

### Testing Gaps (8)

| ID | Issue | Current | Target |
|----|-------|---------|--------|
| TEST-01 | Low Coverage | 15% | 90% |
| TEST-02 | Zero Coverage | PaymentService 0% | 90% |
| TEST-03 | No Integration Tests | 0 tests | 10+ tests |
| TEST-04 | Flaky Tests | 30% failure rate | 0% |
| TEST-05 | Mock Hell | 12 dependencies | 3 max |
| TEST-06 | No Fixtures | Hardcoded data | Fixtures |
| TEST-07 | Implementation Tests | Breaks on refactor | Stable |
| TEST-08 | No Negative Tests | Only happy path | Complete |

### Documentation Issues (7)

| ID | Issue | Problem |
|----|-------|---------|
| DOC-01 | Outdated README | References removed features |
| DOC-02 | No API Docs | No OpenAPI spec |
| DOC-03 | Contradictory Comments | Code does opposite |
| DOC-04 | No Architecture Diagram | Design undocumented |
| DOC-05 | Copy-Paste Docstrings | Same text 8 times |
| DOC-06 | No Inline Comments | Complex algorithms unexplained |
| DOC-07 | No CHANGELOG | No version history |

### UI/Visual Issues (4) 🆕

| ID | Issue | WCAG Violation |
|----|-------|----------------|
| UI-01 | Faded Images | SC 1.4.3 (30% opacity) |
| UI-02 | Missing Test IDs | N/A (brittle tests) |
| UI-03 | Inconsistent Spacing | N/A (8-24px random) |
| UI-04 | Poor Contrast | SC 1.4.3 (2.8:1 ratio) |

---

## 📊 Baseline Metrics

### Overall Score: F (25/100)

| Category | Score | Grade | Status |
|----------|-------|-------|--------|
| Security | 15/100 | F 🔴 | CRITICAL |
| SOLID | 20/100 | F 🔴 | POOR |
| Code Quality | 20/100 | F 🔴 | POOR |
| Performance | 30/100 | F 🔴 | SLOW |
| Testing | 15/100 | F 🔴 | INADEQUATE |
| Documentation | 20/100 | F 🔴 | POOR |
| UI/Visual | 25/100 | F 🔴 | ISSUES |
| **AVERAGE** | **25/100** | **F 🔴** | **NOT READY** |

### Code Metrics

```
Total Lines of Code:   8,457 LOC
Duplicated Code:       3,383 LOC (40%)
Dead Code:             300+ LOC
Cyclomatic Complexity: 68 (avg)
Test Coverage:         15%
Documentation:         Outdated/contradictory
```

---

## 🎯 Transformation Target: A (90+/100)

### Expected Outcomes After CORTEX 4.0

| Category | Before | After | Improvement |
|----------|--------|-------|-------------|
| Security | 15/100 | 95/100 | +533% |
| SOLID | 20/100 | 92/100 | +360% |
| Code Quality | 20/100 | 90/100 | +350% |
| Performance | 30/100 | 88/100 | +193% |
| Testing | 15/100 | 95/100 | +533% |
| Documentation | 20/100 | 90/100 | +350% |
| UI/Visual | 25/100 | 90/100 | +260% |
| **AVERAGE** | **25/100** | **90+/100** | **+260%** |

---

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
PostgreSQL 14+ (or SQLite for dev)
Node.js 18+ (for UI mockups)
```

### Installation
```bash
cd cortex-sample-apps/sts-validation-app
pip install -r requirements.txt
cp .env.example .env  # Configure environment
python setup_database.py
```

### Running
```bash
python src/main.py  # Starts on http://localhost:8000
```

⚠️ **WARNING:** Do NOT deploy to production. Contains deliberate vulnerabilities.

---

## 📁 Key Files

| File | Purpose | Flaws |
|------|---------|-------|
| `src/api/auth.py` | Authentication | SEC-01, SEC-02, SEC-06 |
| `src/api/users.py` | User management | SOL-01 (god class 654 LOC) |
| `src/api/orders.py` | Order processing | CQ-01 (complexity 87) |
| `src/business/pricing.py` | Pricing rules | SOL-03 (hardcoded) |
| `src/data/database.py` | DB connection | SEC-03, PERF-08 |
| `src/utils/helpers.py` | Utilities | SOL-02 (god object 587 LOC) |
| `.mapping.json` | Sanitization audit | 5 secrets documented |
| `STS-MANIFEST.json` | Flaw catalog | All 65 flaws mapped |

---

## 🎭 CORTEX Validation Journey

This application will undergo transformation through 9 CORTEX capabilities:

1. **Code Sanitization** → Remove 5 hardcoded secrets
2. **Planning System** → Generate refactoring plan for god classes
3. **TDD Mastery** → Achieve 90%+ test coverage
4. **System Maintenance** → Remove dead code, fix memory leaks
5. **System Refinement** → Fix 15 SOLID violations
6. **Architectural Review** → Generate 20+ recommendations
7. **ADO Operations** → Create business tracking hierarchy
8. **Holistic Discovery** → Complete codebase inventory
9. **Vision API** → Analyze UI mockups for accessibility

**Expected Result:** F→A transformation (25→90+, 260% improvement)

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Copyright:** © 2025 Asif Hussain. All rights reserved.

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

### Security Vulnerabilities (12) - OWASP Top 10:2021 Mapped

| ID | OWASP | CWE | Location | Severity | Description | Detection Pattern |
|----|-------|-----|----------|----------|-------------|-------------------|
| SEC-01 | A02:2021 | CWE-798 | `auth.py:15` | CRITICAL | Hardcoded JWT secret key | `pattern: "SECRET.*=.*['\"]"` |
| SEC-02 | A02:2021 | CWE-916 | `auth.py:42` | CRITICAL | No password hashing (plaintext storage) | `pattern: "password.*==.*password"` |
| SEC-03 | A03:2021 | CWE-89 | `database.py:28` | CRITICAL | SQL injection via f-strings | `pattern: "f['\"].*{.*}.*['\"]"` |
| SEC-04 | A03:2021 | CWE-89 | `products.py:67` | CRITICAL | SQL injection via string concatenation | `pattern: ".*\\+.*request\\..*\\+.*"` |
| SEC-05 | A05:2021 | CWE-489 | `app.py:10` | HIGH | Debug mode enabled in production | `pattern: "debug.*=.*True"` |
| SEC-06 | A02:2021 | CWE-327 | `auth.py:89` | HIGH | Weak cryptographic algorithm (HS256) | `pattern: "algorithm.*HS256"` |
| SEC-07 | A04:2021 | CWE-770 | `users.py:134` | MEDIUM | Missing rate limiting (DoS risk) | `pattern: "@app\\.route.*def.*\\(.*request"` |
| SEC-08 | A02:2021 | CWE-798 | `.env` | CRITICAL | Secrets committed to version control | `git ls-files | grep "\\.env$"` |
| SEC-09 | A06:2021 | CWE-1104 | `requirements.txt` | HIGH | Vulnerable dependency (Flask 1.1.2) | `pattern: "Flask==1\\.1\\.2"` |
| SEC-10 | A03:2021 | CWE-78 | `setup.sh:22` | MEDIUM | OS command injection via shell | `pattern: "os\\.system.*\\+.*input"` |
| SEC-11 | A08:2021 | CWE-502 | `cache.py:45` | HIGH | Insecure deserialization (pickle) | `pattern: "pickle\\.loads"` |
| SEC-12 | A05:2021 | CWE-942 | `app.py:78` | MEDIUM | Permissive CORS (allow all origins) | `pattern: "Access-Control-Allow-Origin.*\\*"` |

**Knowledge Source:** `cortex-brain/knowledge/security/owasp-top-10.yaml`

### SOLID Principle Violations (15) - Measurable Heuristics

| ID | Principle | Violation | Location | Metrics | Detection Heuristic |
|----|-----------|-----------|----------|---------|---------------------|
| SOL-01 | SRP | God class (auth + CRUD + validation + email) | `users.py` | 32 methods, 654 LOC | `methods > 20, LOC > 500` |
| SOL-02 | SRP | God object with 23 unrelated functions | `helpers.py` | 23 functions, 587 LOC | `functions > 15, LOC > 400` |
| SOL-03 | OCP | Hard-coded pricing rules (not extensible) | `pricing.py:45` | 15 if/elif branches | `if.*elif.*elif count > 10` |
| SOL-04 | OCP | Payment processor if/else chains | `payment.py:89` | 8 if/elif processors | `if.*elif.*elif count > 5` |
| SOL-05 | LSP | Subclass throws NotImplementedError | `repositories.py:123` | 3 broken methods | `raise NotImplementedError` |
| SOL-06 | LSP | Subclass changes method signatures | `models.py:67` | Type mismatches | Signature comparison |
| SOL-07 | ISP | Fat interface with 18 methods | `IRepository` | 18 methods (6 used) | `interface_methods > 10` |
| SOL-08 | ISP | Client forced to depend on unused methods | `product_service.py` | Depends on 18, uses 4 | `usage_ratio < 0.3` |
| SOL-09 | DIP | Direct instantiation of concrete classes | `orders.py:34` | 7 direct `new` calls | `pattern: "= \\w+\\("` |
| SOL-10 | DIP | High-level module depends on low-level | `business/` → `data/` | 12 direct imports | Import graph analysis |
| SOL-11 | SRP | Class has 4 distinct responsibilities | `order_manager.py` | 4 responsibility groups | Cohesion analysis |
| SOL-12 | OCP | Modification required to add new feature | `shipping.py` | Change in 3 places | Extension point missing |
| SOL-13 | LSP | Precondition strengthening in subclass | `premium_user.py:89` | Extra validation | Contract violation |
| SOL-14 | ISP | Repository interface includes caching | `IRepository` | Cache + CRUD mixed | Single responsibility |
| SOL-15 | DIP | Business logic instantiates database | `inventory.py:23` | `db = Database()` | Concrete dependency |

**Knowledge Source:** `cortex-brain/knowledge/engineering/solid-principles.yaml`

### Code Quality Issues (20) - Anti-Patterns & Code Smells

| ID | Anti-Pattern | Location | Metrics | Detection | Refactoring Path |
|----|--------------|----------|---------|-----------|------------------|
| CQ-01 | Monster Method | `orders.py:create_order()` | Complexity: 87, LOC: 245 | `complexity > 20` | Extract Method (refactor_001) |
| CQ-02 | Complex Conditional | `users.py:validate_user()` | Complexity: 45, 18 conditions | `complexity > 15` | Decompose Conditional (refactor_003) |
| CQ-03 | Copy-Paste Programming | `payment.py` | 3 methods, 80% duplicate | `duplicate > 5%` | Extract Method (refactor_001) |
| CQ-04 | Arrow Anti-Pattern | `shipping.py:calculate_cost()` | Nesting depth: 7 | `nesting > 4` | Replace Nested Conditional (refactor_004) |
| CQ-05 | Magic Numbers | `pricing.py` | 23 hardcoded constants | `pattern: "\\d+\\.\\d+"` | Replace Magic Number with Symbolic Constant |
| CQ-06 | Long Parameter List | `create_user()` | 9 parameters | `params > 3` | Introduce Parameter Object (refactor_045) |
| CQ-07 | Data Clumps | `address fields` | 5 fields repeated 8x | Grouping analysis | Extract Class (refactor_013) |
| CQ-08 | Feature Envy | `order_service.py:123` | Uses 8 Product methods | Method-class affinity | Move Method (refactor_011) |
| CQ-09 | Inappropriate Intimacy | `User` ↔ `Order` | Bidirectional coupling | Coupling analysis | Change Bidirectional to Unidirectional |
| CQ-10 | Lazy Class | `validators.py` | 3 methods, 45 LOC | `LOC < 100, methods < 5` | Inline Class (refactor_002) |
| CQ-11 | Dead Code | `legacy_api.py` | Unused 6 months | Call graph analysis | Remove Dead Code |
| CQ-12 | Speculative Generality | `base_processor.py` | No subclasses | Inheritance check | Collapse Hierarchy (refactor_056) |
| CQ-13 | Primitive Obsession | String-based status | 15 string literals | Type analysis | Replace Type Code with Class (refactor_019) |
| CQ-14 | Message Chains | `order.user.address.city` | 4-level chain | `chain_depth > 3` | Hide Delegate (refactor_012) |
| CQ-15 | Middle Man | `order_facade.py` | 90% delegation | Delegation ratio | Remove Middle Man (refactor_014) |
| CQ-16 | Comments Explaining Bad Code | `auth.py` | 45% comment ratio | `comment_ratio > 0.30` | Extract Method + Rename |
| CQ-17 | Anemic Domain Model | `models.py` | Only getters/setters | Behavior analysis | Move Method from Service to Model |
| CQ-18 | Divergent Change | `database.py` | Modified for 4 reasons | Change history | Extract Class by Responsibility |
| CQ-19 | Shotgun Surgery | Add payment type | 8 files modified | Impact analysis | Move Method/Field to centralize |
| CQ-20 | Parallel Inheritance | `User` + `UserValidator` | Mirrored hierarchies | Inheritance analysis | Collapse Hierarchies |

**Knowledge Sources:** 
- `cortex-brain/knowledge/engineering/anti-patterns.yaml`
- `cortex-brain/knowledge/engineering/refactoring.yaml`

### Performance Issues (8) - Optimization Techniques Mapped

| ID | Issue | Location | Current | Target | Detection | Optimization Technique |
|----|-------|----------|---------|--------|-----------|------------------------|
| PERF-01 | N+1 Query Problem | `orders.py:get_with_items()` | O(n) queries | O(1) query | Query count analysis | Use JOIN/eager loading |
| PERF-02 | Naive Fibonacci | `utils.py:fibonacci()` | O(2ⁿ) time | O(n) time | Complexity analysis | Dynamic programming/memoization |
| PERF-03 | Quadratic String Concat | `report.py:generate()` | O(n²) time | O(n) time | `+= in loop` pattern | Use StringBuilder/join() |
| PERF-04 | Missing Database Index | `products` table | Full table scan | Index scan | Query plan analysis | Add index on `category_id` |
| PERF-05 | Memory Leak | `cache.py:_cache` | Unbounded growth | Bounded LRU | Memory profiling | Implement LRU eviction |
| PERF-06 | Synchronous I/O | `email.py:send_batch()` | Sequential, blocking | Parallel | I/O wait analysis | Use async/await or ThreadPool |
| PERF-07 | No Response Caching | `api/products.py` | DB hit every request | Cache hit 95% | Cache-Control headers | Add Redis/Memcached layer |
| PERF-08 | Inefficient Sort | `search.py:rank_results()` | Bubble sort O(n²) | O(n log n) | Algorithm analysis | Use Timsort/Mergesort |

**Baseline Metrics:**
- Avg Response Time: 2,340ms (Target: <200ms)
- Database Queries per Request: 47 (Target: <5)
- Memory Usage: 1.2GB (Target: <256MB)
- Cache Hit Rate: 12% (Target: >90%)

**Knowledge Source:** `cortex-brain/knowledge/performance/optimization-techniques.yaml`

### Testing Gaps (3) - TDD Best Practices Violations

| ID | Gap | Current | Target | Detection | Best Practice |
|----|-----|---------|--------|-----------|---------------|
| TEST-01 | Low Coverage | 15% code coverage | 90%+ coverage | Coverage report | RED→GREEN→REFACTOR cycle |
| TEST-02 | No Unit Tests | Only 12 integration tests | Unit + Integration + E2E | Test pyramid analysis | Follow testing pyramid |
| TEST-03 | Brittle Tests | 40% tests fail on refactor | <5% fragile tests | Refactoring impact | Use test doubles, avoid implementation details |

**Knowledge Source:** `cortex-brain/knowledge/testing/tdd-best-practices.yaml`

### Documentation Issues (8)

| ID | Issue | Location | Impact | Detection |
|----|-------|----------|--------|-----------|
| DOC-01 | Outdated README | `README.md` | Setup instructions wrong | Last updated 2 years ago |
| DOC-02 | Missing API Docs | `api/` endpoints | No Swagger/OpenAPI | No spec file |
| DOC-03 | No Architecture Diagram | `docs/` | Hard to onboard | No diagrams |
| DOC-04 | Contradictory Docs | `setup.md` vs `deploy.md` | Python 3.6 vs 3.8 | Version conflicts |
| DOC-05 | No Code Comments | Business logic | Intent unclear | Comment ratio < 2% |
| DOC-06 | Incomplete Changelog | `CHANGELOG.md` | Missing 6 months | Gap detection |
| DOC-07 | Dead Links | External references | 12 broken links | Link checker |
| DOC-08 | No Error Handling Guide | Exception patterns | Inconsistent handling | Pattern analysis |

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

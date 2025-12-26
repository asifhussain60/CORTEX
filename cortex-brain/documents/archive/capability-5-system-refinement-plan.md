# Phase 13B Capability 5: System Refinement Validation Plan

**Capability:** System Refinement - SOLID Violation Resolution & Quality Improvement  
**Status:** ⏳ READY FOR VALIDATION  
**Date:** December 26, 2025  
**Duration:** 5 hours estimated

---

## 🎯 Validation Objective

Validate System Refinement's ability to identify and resolve code quality issues:

1. **SOLID Violations:** Detect and fix 35 principle violations (SRP, OCP, LSP, ISP, DIP)
2. **Code Smells:** Identify and remediate 20 anti-patterns
3. **Test Coverage:** Improve from 15% → 60%+ (45% increase minimum)
4. **Code Quality:** Improve pylint scores from 6.5 → 9.0+ average
5. **Complexity:** Reduce cyclomatic complexity from 68 avg → <15

**Target:** STS validation app with 35 SOLID violations, 20 code smells, 15% coverage

---

## 📊 STS Application Current State (Pre-Refinement)

### Deliberate Flaws (55 total targeting refinement)

#### SOLID Principle Violations (15)

| ID | Principle | Violation | Location | Metrics | Refactoring |
|----|-----------|-----------|----------|---------|-------------|
| **SOL-01** | SRP | God class (auth + CRUD + validation + email) | `users.py` | 32 methods, 654 LOC | Extract UserAuth, UserEmail, UserValidator |
| **SOL-02** | SRP | God object with 23 unrelated functions | `helpers.py` | 23 functions, 587 LOC | Extract DateHelpers, StringHelpers, MathHelpers |
| **SOL-03** | OCP | Hard-coded pricing rules (not extensible) | `pricing.py:45` | 15 if/elif branches | Strategy pattern (PricingStrategy) |
| **SOL-04** | OCP | Payment processor if/else chains | `payment.py:89` | 8 if/elif processors | Strategy pattern (PaymentProcessor) |
| **SOL-05** | LSP | Subclass throws NotImplementedError | `repositories.py:123` | 3 broken methods | Remove LSP violation, proper inheritance |
| **SOL-06** | LSP | Subclass changes method signatures | `models.py:67` | Type mismatches | Fix signature consistency |
| **SOL-07** | ISP | Fat interface with 18 methods | `IRepository` | 18 methods (6 used) | Split into IReader, IWriter, ICache |
| **SOL-08** | ISP | Client forced to depend on unused methods | `product_service.py` | Depends on 18, uses 4 | Interface segregation |
| **SOL-09** | DIP | Direct instantiation of concrete classes | `orders.py:34` | 7 direct `new` calls | Dependency injection |
| **SOL-10** | DIP | High-level module depends on low-level | `business/` → `data/` | 12 direct imports | Inversion via interfaces |
| **SOL-11** | SRP | Class has 4 distinct responsibilities | `order_manager.py` | 4 responsibility groups | Extract OrderValidator, OrderNotifier |
| **SOL-12** | OCP | Modification required to add new feature | `shipping.py` | Change in 3 places | Template Method pattern |
| **SOL-13** | LSP | Precondition strengthening in subclass | `premium_user.py:89` | Extra validation | Remove precondition violation |
| **SOL-14** | ISP | Repository interface includes caching | `IRepository` | Cache + CRUD mixed | Separate concerns |
| **SOL-15** | DIP | Business logic instantiates database | `inventory.py:23` | `db = Database()` | Inject dependency |

#### Code Quality Issues (20)

| ID | Anti-Pattern | Location | Metrics | Detection | Refactoring |
|----|--------------|----------|---------|-----------|-------------|
| **CQ-01** | Monster Method | `orders.py:create_order()` | Complexity: 87, LOC: 245 | `complexity > 20` | Extract Method |
| **CQ-02** | Complex Conditional | `users.py:validate_user()` | Complexity: 45, 18 conditions | `complexity > 15` | Decompose Conditional |
| **CQ-03** | Copy-Paste Programming | `payment.py` | 3 methods, 80% duplicate | `duplicate > 5%` | Extract Method |
| **CQ-04** | Arrow Anti-Pattern | `shipping.py:calculate_cost()` | Nesting depth: 7 | `nesting > 4` | Replace Nested Conditional |
| **CQ-05** | Magic Numbers | `pricing.py` | 23 hardcoded constants | `pattern: "\\d+\\.\\d+"` | Named Constants |
| **CQ-06** | Long Parameter List | `create_user()` | 9 parameters | `params > 3` | Parameter Object |
| **CQ-07** | Data Clumps | `address fields` | 5 fields repeated 8x | Grouping analysis | Extract Class (Address) |
| **CQ-08** | Feature Envy | `order_service.py:123` | Uses 8 Product methods | Method-class affinity | Move Method |
| **CQ-09** | Inappropriate Intimacy | `User` ↔ `Order` | Bidirectional coupling | Coupling analysis | Unidirectional |
| **CQ-10** | Lazy Class | `validators.py` | 3 methods, 45 LOC | `LOC < 100` | Inline Class |
| **CQ-11** | Dead Code | `legacy_api.py` | Unused 6 months | Call graph | Remove |
| **CQ-12** | Speculative Generality | `base_processor.py` | No subclasses | Inheritance check | Collapse Hierarchy |
| **CQ-13** | Primitive Obsession | String-based status | 15 string literals | Type analysis | Enum/Class |
| **CQ-14** | Long Method | `process_payment()` | 187 LOC | `LOC > 50` | Extract Method |
| **CQ-15** | Shotgun Surgery | Status change | 12 files modified | Change impact | Encapsulate |
| **CQ-16** | Divergent Change | `User` class | 5 change reasons | Cohesion analysis | Split class |
| **CQ-17** | Message Chains | `order.user.address.city` | 4-level chain | Law of Demeter | Hide Delegate |
| **CQ-18** | Middle Man | `UserService` | 8 methods delegate | Delegation % | Remove Middle Man |
| **CQ-19** | Comments | Obsolete comments | 47 outdated comments | Comment analysis | Update/Remove |
| **CQ-20** | Inconsistent Names | Variable naming | 34 inconsistencies | Naming convention | Standardize |

#### Test Coverage Gaps (10)

| ID | Gap | Location | Coverage | Target |
|----|-----|----------|----------|--------|
| **TEST-01** | No business logic tests | `business/` | 0% | 80%+ |
| **TEST-02** | API endpoints untested | `api/` | 15% | 70%+ |
| **TEST-03** | Edge cases missing | `validators.py` | 0% | 90%+ |
| **TEST-04** | Integration tests absent | `tests/integration/` | 0 tests | 20+ tests |
| **TEST-05** | No error path tests | All modules | 5% | 60%+ |
| **TEST-06** | Mock-heavy tests | `tests/` | 90% mocked | 50% real |
| **TEST-07** | No performance tests | `tests/` | 0 tests | 10+ tests |
| **TEST-08** | Security tests missing | `tests/security/` | 0 tests | 15+ tests |
| **TEST-09** | No regression tests | `tests/` | 0 tests | 10+ tests |
| **TEST-10** | Test data hard-coded | `tests/` | 100% hard-coded | Fixtures |

**Summary:**
- **SOLID Violations:** 15 (SRP: 3, OCP: 3, LSP: 3, ISP: 3, DIP: 3)
- **Code Smells:** 20 anti-patterns
- **Test Coverage:** 15% → 60%+ target (45% increase)
- **Code Quality:** 6.5 avg → 9.0+ target
- **Complexity:** 68 avg → <15 target

**Health Baseline:** 25/100 (F grade)

---

## 🎯 Refinement Validation Plan

### Phase 1: SOLID Violation Detection (60 minutes)

**Objective:** Detect all 15 SOLID violations with 100% accuracy

**Detection Strategy:**

1. **SRP Violations (3):**
```python
# Detection heuristics
def detect_srp_violations(file_path):
    """Detect Single Responsibility Principle violations."""
    violations = []
    
    # God class heuristic: >20 methods OR >500 LOC
    if method_count > 20 or line_count > 500:
        violations.append({
            "type": "god_class",
            "severity": "high",
            "location": file_path,
            "metrics": {"methods": method_count, "loc": line_count},
            "recommendation": "Extract classes by responsibility"
        })
    
    # Cohesion analysis: LCOM > 0.8 (Low Cohesion of Methods)
    lcom = calculate_lcom(class_ast)
    if lcom > 0.8:
        violations.append({
            "type": "low_cohesion",
            "severity": "medium",
            "location": file_path,
            "metrics": {"lcom": lcom},
            "recommendation": "Group related methods into separate classes"
        })
    
    return violations
```

2. **OCP Violations (3):**
```python
def detect_ocp_violations(file_path):
    """Detect Open/Closed Principle violations."""
    violations = []
    
    # Long if/elif chain heuristic: >5 branches
    for method in methods:
        if_elif_count = count_if_elif_branches(method)
        if if_elif_count > 5:
            violations.append({
                "type": "if_elif_chain",
                "severity": "high",
                "location": f"{file_path}:{method.lineno}",
                "metrics": {"branches": if_elif_count},
                "recommendation": "Use Strategy pattern"
            })
    
    # Hard-coded rules heuristic: >10 literals in decision logic
    if literal_count_in_decisions > 10:
        violations.append({
            "type": "hard_coded_rules",
            "severity": "medium",
            "recommendation": "Extract rules to configuration/strategy"
        })
    
    return violations
```

3. **LSP Violations (3):**
```python
def detect_lsp_violations(file_path):
    """Detect Liskov Substitution Principle violations."""
    violations = []
    
    # NotImplementedError heuristic
    for method in methods:
        if raises_not_implemented_error(method):
            violations.append({
                "type": "not_implemented",
                "severity": "critical",
                "location": f"{file_path}:{method.lineno}",
                "recommendation": "Remove method or implement properly"
            })
    
    # Signature change heuristic: subclass changes param types
    if signature_differs_from_parent(method, parent_method):
        violations.append({
            "type": "signature_mismatch",
            "severity": "high",
            "recommendation": "Match parent method signature"
        })
    
    return violations
```

4. **ISP Violations (3):**
```python
def detect_isp_violations(file_path):
    """Detect Interface Segregation Principle violations."""
    violations = []
    
    # Fat interface heuristic: >10 methods
    if interface_method_count > 10:
        violations.append({
            "type": "fat_interface",
            "severity": "medium",
            "metrics": {"methods": interface_method_count},
            "recommendation": "Split into smaller interfaces"
        })
    
    # Unused methods heuristic: client uses <30% of interface
    usage_ratio = used_methods / total_methods
    if usage_ratio < 0.3:
        violations.append({
            "type": "unused_methods",
            "severity": "medium",
            "metrics": {"usage_ratio": usage_ratio},
            "recommendation": "Segregate interface by client needs"
        })
    
    return violations
```

5. **DIP Violations (3):**
```python
def detect_dip_violations(file_path):
    """Detect Dependency Inversion Principle violations."""
    violations = []
    
    # Direct instantiation heuristic: `= ConcreteClass()`
    for assignment in assignments:
        if is_concrete_instantiation(assignment):
            violations.append({
                "type": "direct_instantiation",
                "severity": "high",
                "location": f"{file_path}:{assignment.lineno}",
                "recommendation": "Use dependency injection"
            })
    
    # High-level depends on low-level heuristic: business imports data layer
    if "business" in file_path and imports_data_layer(file_path):
        violations.append({
            "type": "wrong_dependency_direction",
            "severity": "high",
            "recommendation": "Depend on abstractions, not concretions"
        })
    
    return violations
```

**Expected Detection:**
- **SRP:** 3/3 (god classes, low cohesion)
- **OCP:** 3/3 (if/elif chains, hard-coded rules)
- **LSP:** 3/3 (NotImplementedError, signature mismatches)
- **ISP:** 3/3 (fat interfaces, unused methods)
- **DIP:** 3/3 (direct instantiation, wrong dependency direction)

**Total:** 15/15 violations detected (100% accuracy)

**Validation Criteria:**
- ✅ All 15 SOLID violations detected
- ✅ 0 false positives (no incorrect violations)
- ✅ Actionable recommendations for each
- ✅ Severity levels assigned correctly

---

### Phase 2: Code Smell Detection (45 minutes)

**Objective:** Detect 20 code smells with 95%+ accuracy

**Detection Tools:**
1. **Radon:** Cyclomatic complexity, maintainability index
2. **Pylint:** Code quality, naming conventions
3. **Bandit:** Security issues
4. **Duplicate:** Copy-paste detection
5. **AST Analysis:** Custom smell detection

**Target Smells:**
- Monster Method (complexity >20): 2 instances
- Long Parameter List (>3 params): 3 instances
- Magic Numbers (hardcoded): 23 instances
- Data Clumps (repeated fields): 5 fields × 8 locations
- Feature Envy (uses other class methods): 3 instances
- Dead Code (unused functions): 5 instances
- Primitive Obsession (strings for enums): 15 instances

**Validation Criteria:**
- ✅ 19+/20 code smells detected (95% accuracy)
- ✅ <2 false positives (<10%)
- ✅ Refactoring recommendations provided
- ✅ Priority ranking (critical → low)

---

### Phase 3: Automated Refactoring (90 minutes)

**Objective:** Apply automated refactorings with 100% test pass rate

**Refactoring Catalog (Fowler's patterns):**

1. **Extract Method** (CQ-01, CQ-03, CQ-14):
```python
# BEFORE
def create_order(customer_id, items, discount, shipping):
    # 245 lines of logic...
    # Validation (50 lines)
    # Calculation (80 lines)
    # Database (60 lines)
    # Email (55 lines)
    pass

# AFTER
def create_order(customer_id, items, discount, shipping):
    self._validate_order(customer_id, items)  # 50 lines
    total = self._calculate_total(items, discount)  # 80 lines
    order = self._save_order(customer_id, items, total)  # 60 lines
    self._send_confirmation(order)  # 55 lines
    return order  # 5 lines (from 245 → 5)
```

2. **Introduce Parameter Object** (CQ-06, CQ-07):
```python
# BEFORE
def create_user(name, email, street, city, state, zip, country, phone, age):
    pass  # 9 parameters

# AFTER
@dataclass
class Address:
    street: str
    city: str
    state: str
    zip: str
    country: str

@dataclass
class ContactInfo:
    email: str
    phone: str

def create_user(name: str, address: Address, contact: ContactInfo, age: int):
    pass  # 4 parameters
```

3. **Replace Type Code with Enum** (CQ-13):
```python
# BEFORE
status = "pending"  # 15 string literals scattered

# AFTER
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

status = OrderStatus.PENDING
```

4. **Strategy Pattern** (SOL-03, SOL-04):
```python
# BEFORE (OCP violation)
def calculate_price(item, customer_type):
    if customer_type == "regular":
        return item.price
    elif customer_type == "premium":
        return item.price * 0.9
    elif customer_type == "vip":
        return item.price * 0.8
    # ... 15 branches

# AFTER (OCP compliant)
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, item): pass

class RegularPricing(PricingStrategy):
    def calculate_price(self, item):
        return item.price

class PremiumPricing(PricingStrategy):
    def calculate_price(self, item):
        return item.price * 0.9

class VIPPricing(PricingStrategy):
    def calculate_price(self, item):
        return item.price * 0.8

def calculate_price(item, strategy: PricingStrategy):
    return strategy.calculate_price(item)
```

5. **Dependency Injection** (SOL-09, SOL-15):
```python
# BEFORE (DIP violation)
class OrderService:
    def __init__(self):
        self.db = Database()  # Direct instantiation
        self.cache = RedisCache()  # Concrete dependency

# AFTER (DIP compliant)
from abc import ABC, abstractmethod

class IDatabase(ABC):
    @abstractmethod
    def save(self, data): pass

class ICache(ABC):
    @abstractmethod
    def get(self, key): pass

class OrderService:
    def __init__(self, db: IDatabase, cache: ICache):
        self.db = db  # Injected abstraction
        self.cache = cache  # Injected abstraction
```

**Refactoring Execution:**
```python
refactorings = [
    ("Extract Method", ["CQ-01", "CQ-03", "CQ-14"], 3),
    ("Parameter Object", ["CQ-06", "CQ-07"], 2),
    ("Replace Type Code", ["CQ-13"], 1),
    ("Strategy Pattern", ["SOL-03", "SOL-04"], 2),
    ("Dependency Injection", ["SOL-09", "SOL-15"], 2),
    ("Interface Segregation", ["SOL-07", "SOL-08"], 2),
    ("Hide Delegate", ["CQ-17"], 1),
    ("Remove Middle Man", ["CQ-18"], 1),
    ("Inline Class", ["CQ-10"], 1),
    ("Decompose Conditional", ["CQ-02", "CQ-04"], 2)
]

# Total: 17 refactorings applied
```

**Validation Criteria:**
- ✅ 15+ refactorings applied successfully
- ✅ 100% test pass rate after each refactoring
- ✅ No regressions (existing functionality preserved)
- ✅ Complexity reduced (68 → <15 average)
- ✅ SOLID violations resolved (15 → 0)

---

### Phase 4: Test Coverage Improvement (60 minutes)

**Objective:** Increase coverage from 15% → 60%+ (45% minimum increase)

**Coverage Strategy:**

1. **Business Logic (0% → 80%):**
```python
# Target: business/ directory
# Tests needed: 45 tests

# Order processing
test_create_order_success()
test_create_order_invalid_customer()
test_create_order_empty_items()
test_calculate_total_with_tax()
test_calculate_total_with_discount()
# ... 40 more

# Payment processing
test_process_payment_success()
test_process_payment_insufficient_funds()
test_process_payment_invalid_card()
# ... 15 more

# Inventory management
test_reserve_stock_success()
test_reserve_stock_insufficient()
test_release_reservation()
# ... 12 more
```

2. **API Endpoints (15% → 70%):**
```python
# Target: api/ directory
# Tests needed: 35 tests

# User endpoints
test_create_user_success()
test_create_user_duplicate_email()
test_get_user_by_id()
test_update_user_profile()
test_delete_user()
# ... 20 more

# Product endpoints
test_list_products()
test_get_product_by_id()
test_search_products()
# ... 10 more
```

3. **Edge Cases (0% → 90%):**
```python
# Target: validators.py, utils/
# Tests needed: 25 tests

# Boundary conditions
test_validate_min_quantity()
test_validate_max_quantity()
test_validate_zero_quantity()
test_validate_negative_quantity()
# ... 10 more

# Extreme values
test_calculate_with_max_float()
test_calculate_with_min_float()
test_calculate_with_overflow()
# ... 8 more

# Error paths
test_handle_database_error()
test_handle_network_timeout()
test_handle_invalid_input()
# ... 7 more
```

**Expected Coverage:**
- **Business Logic:** 0% → 80% (+80%)
- **API Endpoints:** 15% → 70% (+55%)
- **Validators/Utils:** 0% → 90% (+90%)
- **Overall:** 15% → 62% (+47%, exceeds 45% target)

**Validation Criteria:**
- ✅ Coverage increase ≥45% (target: 60%+)
- ✅ 100+ tests added
- ✅ All tests passing (100% pass rate)
- ✅ Edge cases covered (90%+)
- ✅ Error paths tested (60%+)

---

### Phase 5: Code Quality Validation (45 minutes)

**Objective:** Verify quality improvements across all metrics

**Quality Metrics:**

| Metric | Baseline | Target | Validation |
|--------|----------|--------|------------|
| **Pylint Score** | 6.5/10 | 9.0+/10 | Run pylint on all files |
| **Cyclomatic Complexity** | 68 avg | <15 avg | Run radon cc |
| **Maintainability Index** | 42 | 75+ | Run radon mi |
| **SOLID Violations** | 15 | 0 | Re-run detection |
| **Code Smells** | 20 | <3 | Re-run detection |
| **Test Coverage** | 15% | 60%+ | Run pytest --cov |
| **Duplication** | 12% | <5% | Run duplicate |

**Validation Commands:**
```bash
# Pylint
pylint src/ --rcfile=.pylintrc --output-format=json

# Radon complexity
radon cc src/ -a -s

# Radon maintainability
radon mi src/ -s

# Coverage
pytest tests/ --cov=src --cov-report=term-missing

# Duplication
duplicate --min-lines=5 src/
```

**Expected Results:**
```
Pylint: 9.2/10 (improved from 6.5)
Complexity: 12 avg (improved from 68)
Maintainability: 78 (improved from 42)
SOLID Violations: 0 (improved from 15)
Code Smells: 2 (improved from 20)
Coverage: 62% (improved from 15%)
Duplication: 3% (improved from 12%)
```

**Validation Criteria:**
- ✅ Pylint score ≥9.0/10
- ✅ Complexity avg <15
- ✅ Maintainability ≥75
- ✅ SOLID violations = 0
- ✅ Code smells <3
- ✅ Coverage ≥60%
- ✅ Duplication <5%

---

## 📊 Success Criteria Matrix

| Phase | Criteria | Target | Validation Method |
|-------|----------|--------|-------------------|
| **SOLID Detection** | Violations detected | 15/15 | Detection report |
| | False positives | 0 | Manual review |
| | Recommendations | 15/15 | Quality check |
| **Code Smell Detection** | Smells detected | 19+/20 | Detection report |
| | False positives | <2 | Manual review |
| **Automated Refactoring** | Refactorings applied | 15+ | Git diff |
| | Test pass rate | 100% | pytest |
| | No regressions | 100% | Integration tests |
| **Test Coverage** | Coverage increase | 45%+ | pytest --cov |
| | Tests added | 100+ | Test count |
| | Pass rate | 100% | pytest |
| **Code Quality** | Pylint score | 9.0+ | pylint |
| | Complexity | <15 avg | radon cc |
| | SOLID violations | 0 | Re-detection |
| | Code smells | <3 | Re-detection |

---

## 🔄 Execution Timeline

### Day 1 (5 hours total)

**Hour 1: SOLID Detection**
- Run detection heuristics (30 min)
- Validate results (15 min)
- Generate recommendations (15 min)

**Hour 2: Code Smell Detection**
- Run analysis tools (20 min)
- Review findings (15 min)
- Prioritize remediation (10 min)

**Hour 3: Automated Refactoring (Part 1)**
- Apply 8 refactorings (50 min)
- Run tests after each (10 min)

**Hour 4: Automated Refactoring (Part 2) + Testing**
- Apply 7 more refactorings (30 min)
- Add 50 tests (30 min)

**Hour 5: Test Coverage + Quality Validation**
- Add 50 more tests (20 min)
- Run quality metrics (20 min)
- Generate report (20 min)

---

## 📝 Validation Report Template

```markdown
# System Refinement Validation Report

## Executive Summary
- **Overall Result:** ✅ PASS / ❌ FAIL
- **SOLID Violations:** 15 → 0 (100% resolved)
- **Code Smells:** 20 → 2 (90% resolved)
- **Test Coverage:** 15% → 62% (+47%)
- **Code Quality:** 6.5 → 9.2 pylint score
- **Duration:** 5 hours

## Phase Results

### SOLID Detection ✅
- **Detected:** 15/15 (100%)
- **False Positives:** 0
- **Recommendations:** 15/15

### Code Smell Detection ✅
- **Detected:** 19/20 (95%)
- **False Positives:** 1
- **Actionable:** 19/19

### Automated Refactoring ✅
- **Applied:** 17 refactorings
- **Test Pass Rate:** 100%
- **Regressions:** 0

### Test Coverage ✅
- **Baseline:** 15%
- **Final:** 62%
- **Increase:** +47% (exceeds 45% target)
- **Tests Added:** 105

### Code Quality ✅
- **Pylint:** 6.5 → 9.2/10 ✅
- **Complexity:** 68 → 12 avg ✅
- **SOLID:** 15 → 0 violations ✅
- **Smells:** 20 → 2 remaining ✅

## Overall Validation

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| SOLID Detection | 100% | 100% | ✅ PASS |
| Refactorings | 15+ | 17 | ✅ PASS |
| Coverage Increase | 45%+ | 47% | ✅ PASS |
| Pylint Score | 9.0+ | 9.2 | ✅ PASS |
| Complexity | <15 | 12 | ✅ PASS |

**Verdict:** ✅ **SYSTEM REFINEMENT VALIDATED**
```

---

## 🎯 Next Steps After Validation

1. **Capability 6: Architectural Review** - Overall architecture score (25 → 90)
2. **Return to TDD Mastery:** Complete Cycles 2-8 (90%+ coverage)
3. **Full STS App:** Apply all capabilities end-to-end

---

**Plan Created:** December 26, 2025  
**Status:** ⏳ READY FOR VALIDATION  
**Duration:** 5 hours estimated  
**Target:** 0 SOLID violations, 60%+ coverage, 9.0+ pylint

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

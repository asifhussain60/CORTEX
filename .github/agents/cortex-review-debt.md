# CORTEX Review Agent: Technical Debt Analysis
## Code Quality, Patterns & Maintenance Issues

**Purpose:** Identify technical debt that increases maintenance burden, reduces quality, or hides real problems.

---

## CHECKS PERFORMED

### 1. Code Duplication

**What to look for:**
- Same logic in 3+ places
- Copy-paste code patterns
- Similar class implementations
- Repeated error handling

**Search patterns:**
```bash
# Find similar function signatures
grep -rn "def " cortex/ --include="*.py" | sort | uniq -c | sort -rn | head -20

# Find repeated patterns
grep -rn "for.*in\|while.*:\|try:" cortex/ --include="*.py" | sort | uniq -c | sort -rn | head -10

# Find copy-paste comments
grep -rn "TODO\|FIXME\|NOTE" cortex/ --include="*.py" | cut -d: -f1 | sort | uniq -c | sort -rn
```

**Examples:**
```python
# Pattern 1: Validation code repeated 3x
if not user_input or len(user_input) > 100:
    raise ValueError(...)

# Pattern 2: Same validation elsewhere
if not config or len(config) > 100:
    raise ValueError(...)

# Pattern 3: Yet again
if not request or len(request) > 100:
    raise ValueError(...)

# ← Should be: def validate_input(data, max_len=100): ...
```

---

### 2. Over-Engineering

**What to look for:**
- Complex abstraction for simple problem
- Inheritance hierarchies that don't simplify
- Design patterns used unnecessarily
- Over-parameterized functions

**Examples:**
```python
# Over-engineered: Factory pattern for single implementation
class DatabaseFactory:
    @staticmethod
    def create_connection():
        return PostgresConnection()

# Over-engineered: Inheritance for slight variation
class BaseHandler:
    def process(self): ...

class SpecialHandler(BaseHandler):
    def process(self):
        return super().process() + "special"

# Should be: Simple function with parameter
def handle(data, special=False):
    result = process(data)
    if special:
        result += "special"
    return result
```

---

### 3. Under-Engineering

**What to look for:**
- Shortcuts taken for speed
- Hardcoded values that should be parameterized
- Quick fixes that should be proper patterns
- Band-aid solutions

**Examples:**
```python
# Under-engineered: Hardcoded retry count
for i in range(3):  # ← Magic number, should be configurable
    try:
        result = api.call()
        break
    except:
        pass

# Under-engineered: Direct state manipulation
class Store:
    def __init__(self):
        self.state = {}  # ← Public, anyone can modify
    
# Better:
class Store:
    def __init__(self):
        self._state = {}  # ← Private, controlled access
    
    def set_state(self, key, value):
        # Can add validation, logging, etc.
        self._state[key] = value
```

---

### 4. Deprecated Pattern Usage

**What to look for:**
- Old async patterns instead of modern ones
- String formatting instead of f-strings
- Classes instead of dataclasses
- Old exception handling patterns

**Search patterns:**
```bash
# Old string formatting
grep -rn "\.format(\|%s\|%d" cortex/ --include="*.py" | grep -v "f\"" | head -10

# Old exception handling
grep -rn "except.*as e:\s*print" cortex/ --include="*.py"

# Classes that should be dataclasses
grep -rn "class.*:\s*$" cortex/ --include="*.py" -A 5 | grep "__init__.*self," | head -10

# Collections usage
grep -rn "from collections import\|import collections" cortex/ --include="*.py"
```

**Examples:**
```python
# Old pattern
name = "{}".format(user)  # ← Use f-string instead
message = "User: %s" % user  # ← Use f-string instead

# Modern pattern
name = f"{user}"
message = f"User: {user}"

# Old: Manual class for data storage
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

# Modern: Dataclass
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
```

---

### 5. Missing Abstractions

**What to look for:**
- Same logic in 3+ classes
- Similar interfaces not unified
- Code that could be parameterized
- Repeated conditional branches

**Examples:**
```python
# Missing abstraction: Three similar handlers
class UserHandler:
    def handle(self, user):
        validate_user(user)
        save_user(user)
        notify_user(user)

class ProductHandler:
    def handle(self, product):
        validate_product(product)
        save_product(product)
        notify_product(product)

class OrderHandler:
    def handle(self, order):
        validate_order(order)
        save_order(order)
        notify_order(order)

# Better: Abstract handler
from abc import ABC, abstractmethod

class BaseHandler(ABC):
    def handle(self, entity):
        self.validate(entity)
        self.save(entity)
        self.notify(entity)
    
    @abstractmethod
    def validate(self, entity): ...
    @abstractmethod
    def save(self, entity): ...
    @abstractmethod
    def notify(self, entity): ...
```

---

### 6. Documentation vs Implementation Gaps

**What to look for:**
- Docstring doesn't match implementation
- README outdated vs actual code
- Configuration docs missing
- Error messages don't match code

**Verify:**
```bash
# Check if README matches actual CLI
cortex --help > /tmp/help.txt
grep -E "usage:|command" docs/README.md | diff - /tmp/help.txt

# Find modules without docs
find cortex -name "*.py" -exec grep -L "\"\"\"" {} \; | head -10
```

---

### 7. Integration Test Gaps

**What to look for:**
- Only unit tests, no integration tests
- Happy-path tests missing edge cases
- No cross-module testing
- No test of actual persistence/APIs

**Check:**
```bash
# Count integration tests
find tests -name "test_integration*" | wc -l

# Count unit tests
find tests -name "test_unit*" | wc -l

# Coverage
pytest --cov=cortex --cov-report=term-missing | grep "TOTAL"
```

**Issues:**
```python
# Unit test (mock): Happy path only
def test_save_user():
    user = User(name="John")
    repo.save(user)  # ← Mocked
    assert repo.get(user.id) == user  # ← Mocked, not real

# Missing: Integration test with real DB
def test_save_user_integration():
    db = PostgreSQL()
    user = User(name="John")
    db.execute("TRUNCATE users")  # ← Real setup
    repo = UserRepository(db)
    repo.save(user)
    
    # Read from DB without mock
    result = db.query("SELECT * FROM users WHERE name='John'")
    assert result[0]['name'] == "John"
```

---

### 8. Performance Anti-Patterns

**What to look for:**
- N+1 query problems
- Inefficient algorithms
- Polling instead of event-driven
- Unnecessary data copies

**Search patterns:**
```bash
# N+1 patterns
grep -rn "for.*in.*:" cortex/ --include="*.py" -A 5 | grep "query\|select\|get" | head -10

# Polling patterns
grep -rn "while.*True\|sleep" cortex/ --include="*.py"

# Inefficient sorts
grep -rn "sort\|sorted" cortex/ --include="*.py"
```

**Examples:**
```python
# N+1 query problem
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id=?", user.id)  # ← Repeated query!
    process(orders)

# Better: JOIN
users_with_orders = db.query("""
    SELECT u.*, o.* FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
""")

# Polling instead of events
while True:
    new_data = api.check_for_updates()
    if new_data:
        process(new_data)
    sleep(5)

# Better: Event-driven
def on_update(data):
    process(data)
api.subscribe(on_update)
```

---

## OUTPUT FORMAT

Create: `_workspaces/roadmap/issues/findings-debt-YYYYMMDD.yaml`

```yaml
debt_findings:
  metadata:
    review_date: "YYYYMMDD"
    total_debt_items: X
    by_category:
      duplication: Y
      over_engineering: Z
      under_engineering: A
      deprecated: B
      abstraction_gaps: C
      documentation_gaps: D
      integration_gaps: E
      performance: F
    
  high_priority_debt:
    - debt_id: "DEBT-001"
      category: "DUPLICATION"
      severity: "HIGH"
      description: "Validation logic repeated 7 times"
      locations:
        - "cortex/api/endpoints/users.py:45"
        - "cortex/api/endpoints/products.py:123"
        - "cortex/api/endpoints/orders.py:89"
      impact: "Bug in validation requires 7 fixes; 7x maintenance burden"
      remediation: "Extract to cortex/common/validation.py"
      effort: "2 hours"
      
    - debt_id: "DEBT-002"
      category: "INTEGRATION_GAPS"
      severity: "HIGH"
      description: "No integration tests for database operations"
      evidence:
        - "Only 23 unit tests with mocks"
        - "Zero integration tests"
        - "Coverage: 45% (real operations untested)"
      impact: "DB migrations fail in production; undetected in tests"
      remediation: "Add 15-20 integration tests with real DB"
      effort: "3 days"
      
    - debt_id: "DEBT-003"
      category: "PERFORMANCE"
      severity: "MEDIUM"
      description: "N+1 query in audit log retrieval"
      location: "cortex/infrastructure/audit_logger.py:150"
      evidence: "For each AC, queries entries (1 + N queries for N ACs)"
      impact: "Audit retrieval O(N²) instead of O(N); slow for large audits"
      remediation: "Use JOIN to fetch all entries in single query"
      effort: "1 hour"
      
  recommendations:
    - "Extract all validation logic to shared module (reduce duplication by 80%)"
    - "Add integration test suite (2-3 days effort, 40% coverage improvement)"
    - "Refactor N+1 queries (5-10 queries identified, quick wins)"
    - "Replace polling with event-driven architecture (resource intensive operations)"
    - "Consolidate 3 similar handlers into single abstraction"
```

---

## DECISION TREE

```
For each debt item:

Q1: Is code duplicated 3+ times?
  → YES: HIGH debt (maintenance burden * 3)
  
Q2: Does it affect performance?
  → YES: MEDIUM or HIGH (depends on frequency)
  
Q3: Is there no test coverage?
  → YES: HIGH debt (undetectable bugs)
  
Q4: Is it using deprecated patterns?
  → YES: LOW to MEDIUM (maintenance burden, readability)
```

---

## VALIDATION

Before finalizing findings:
- [ ] Duplication pattern is exact (not just similar)
- [ ] Performance impact is quantifiable (not speculative)
- [ ] Effort estimate is realistic
- [ ] Remediation is actionable
- [ ] Business impact is clear

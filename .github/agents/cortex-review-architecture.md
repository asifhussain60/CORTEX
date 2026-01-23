# CORTEX Review Agent: Architecture & Design Pattern Flaws

## Structural Anti-Patterns, SOLID Violations & Design Defects

**Purpose:** Identify architectural defects, design pattern misuse, SOLID principle violations, and structural choices that create brittleness, tight coupling, or poor testability.

**Why Critical:** Architectural flaws multiply across the entire codebase. A single bad design pattern choice used in 10 places creates 10 instances of brittleness.

---

## CHECKS PERFORMED

### 1. SOLID Principle Violations

#### 1A: Single Responsibility (SRP)

**What to look for:**
- God objects (class does too much)
- Classes with multiple reasons to change
- Mixed concerns (business logic + I/O + logging + error handling)
- Classes with >500 lines

**Search patterns:**
```bash
# Find large classes
wc -l cortex/**/*.py | sort -n | tail -20

# Find classes with multiple concerns
grep -rn "class.*:" cortex/ --include="*.py" | head -20
grep -rn "self\._[a-z]*_manager\|self\._[a-z]*_handler" cortex/ --include="*.py"

# Find mixed concerns
grep -rn "db\.query\|requests\.get\|logger\.\|open(" cortex/ --include="*.py" | grep -B5 "def "
```

**Red Flags:**
```python
# ❌ GOD OBJECT: UserManager does everything
class UserManager:
    def create_user(self): ...
    def send_email(self): ...
    def log_activity(self): ...
    def validate_payment(self): ...
    def update_cache(self): ...
    def sync_with_ldap(self): ...
    # Now has 6 reasons to change!

# ✅ FIX: Separate concerns
class UserRepository:
    def create_user(self): ...

class EmailService:
    def send_email(self): ...

class AuditLogger:
    def log_activity(self): ...
```

#### 1B: Open/Closed (OCP)

**What to look for:**
- Hard-coded if/else chains for new types
- Switch statements that need modification when new types added
- Tight coupling to concrete classes instead of abstractions

**Search patterns:**
```bash
# Find switch statements and if/else chains
grep -rn "if.*==" cortex/ --include="*.py" | grep "\.type\|\.kind\|\.mode" | head -20

# Find hard-coded class names
grep -rn "if.*isinstance\(" cortex/ --include="*.py" | head -20

# Find missing abstractions
grep -rn "class.*:" cortex/ --include="*.py" | grep -v "ABC\|Protocol\|abstract"
```

**Red Flags:**
```python
# ❌ CLOSED TO EXTENSION: Hard-coded handler selection
def process(self, request_type):
    if request_type == "user":
        return UserHandler().process(request)
    elif request_type == "order":
        return OrderHandler().process(request)
    elif request_type == "payment":
        return PaymentHandler().process(request)
    # Adding new type requires modifying this method!

# ✅ FIX: Use abstraction
class RequestProcessor(ABC):
    @abstractmethod
    def process(self, request): ...

processor_registry = {
    "user": UserProcessor(),
    "order": OrderProcessor(),
    "payment": PaymentProcessor(),
}

def process(self, request_type, request):
    processor = processor_registry.get(request_type)
    return processor.process(request)  # Adding new type = add to registry
```

#### 1C: Liskov Substitution (LSP)

**What to look for:**
- Subclass breaks contract of parent
- Subclass narrows exception handling
- Subclass changes preconditions/postconditions
- Incomplete method implementations in subclass

**Search patterns:**
```bash
# Find inheritance relationships
grep -rn "class.*\(.*\):" cortex/ --include="*.py" | grep -v "object\|ABC"

# Find method overrides
grep -rn "def.*:" cortex/ --include="*.py" | sort | uniq -c | sort -rn | grep -v "^      1"

# Find incomplete implementations
grep -rn "raise NotImplementedError\|pass$" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ LSP VIOLATION: Subclass breaks contract
class PaymentProcessor:
    def process(self, amount: float) -> bool:
        """Process payment. Always throws on invalid amount."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return self._do_payment(amount)

class MockPaymentProcessor(PaymentProcessor):
    def process(self, amount: float) -> bool:
        """Returns False instead of raising - breaks contract!"""
        if amount <= 0:
            return False  # ❌ Violates LSP
        return True

# ✅ FIX: Maintain contract
class MockPaymentProcessor(PaymentProcessor):
    def process(self, amount: float) -> bool:
        if amount <= 0:
            raise ValueError("Amount must be positive")  # Same as parent
        return True
```

#### 1D: Interface Segregation (ISP)

**What to look for:**
- Fat interfaces (clients don't use all methods)
- Classes forced to implement unused methods
- Interface with >5 methods often too large

**Search patterns:**
```bash
# Find classes with many methods
grep -rn "def " cortex/ --include="*.py" | grep -v "__\|_private" | cut -d: -f1 | sort | uniq -c | sort -rn | head -20

# Find unused method implementations
# This requires cross-referencing usage
```

**Red Flags:**
```python
# ❌ FAT INTERFACE: Worker must implement all methods
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    
    @abstractmethod
    def manage_others(self): ...  # Not all workers manage!
    
    @abstractmethod
    def conduct_interviews(self): ...  # Not all workers interview!

class Programmer(Worker):
    def work(self): ...
    def manage_others(self): pass  # Forced to implement
    def conduct_interviews(self): pass  # Forced to implement

# ✅ FIX: Segregate interfaces
class Worker(ABC):
    @abstractmethod
    def work(self): ...

class Manager(Worker):
    @abstractmethod
    def manage_others(self): ...

class InterviewConductor(ABC):
    @abstractmethod
    def conduct_interviews(self): ...

class SeniorProgrammer(Worker, Manager, InterviewConductor):
    # Only implements what it needs
```

#### 1E: Dependency Inversion (DIP)

**What to look for:**
- High-level modules depend on low-level modules
- Concrete dependencies instead of abstractions
- Hard-coded dependencies
- Tight coupling to implementations

**Search patterns:**
```bash
# Find direct instantiation of concrete classes
grep -rn "= [A-Z][a-zA-Z]*(" cortex/ --include="*.py" | grep -v "Error\|Exception"

# Find hard-coded import of concrete classes
grep -rn "from.*import.*Repository\|from.*import.*Service" cortex/ --include="*.py"

# Find missing dependency injection
grep -rn "def __init__.*:" cortex/ --include="*.py" | wc -l
grep -rn "self\._.*=.*(" cortex/ --include="*.py" | wc -l
```

**Red Flags:**
```python
# ❌ DIP VIOLATION: High-level depends on low-level
class OrderService:
    def __init__(self):
        self.database = PostgresDatabase()  # Hard-coded!
        self.payment = StripePaymentProcessor()  # Hard-coded!
    
    def process_order(self, order):
        self.database.save(order)
        self.payment.process(order.total)

# ✅ FIX: Inject dependencies
class OrderService:
    def __init__(self, database: Database, payment: PaymentProcessor):
        self.database = database
        self.payment = payment
    
    def process_order(self, order):
        self.database.save(order)
        self.payment.process(order.total)

# Usage
service = OrderService(
    database=PostgresDatabase(),
    payment=StripePaymentProcessor()
)
```

---

### 2. Coupling Anti-Patterns

**What to look for:**
- Feature envy (object using too many methods from another)
- Law of Demeter violations (deep object chaining)
- Circular dependencies
- Hidden dependencies

**Search patterns:**
```bash
# Find deep object chaining (Law of Demeter)
grep -rn "\.\w\+\.\w\+\.\w\+\.\w\+" cortex/ --include="*.py"

# Find circular imports
python3 -m py_compile cortex/**/*.py 2>&1 | grep "circular"

# Find feature envy
grep -rn "other_object\.[a-z_]\+\|dependency\.[a-z_]\+" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ LAW OF DEMETER: Deep chaining
total = order.customer.account.balance.current

# ✅ FIX: Delegate to intermediate objects
total = order.get_customer_balance()

# ❌ FEATURE ENVY: Method overly interested in another object
def calculate_discount(user):
    if user.account.tier == "gold":
        return user.account.purchase_history.total * 0.1
    return 0

# ✅ FIX: Move logic to appropriate object
def get_discount(self):  # In User class
    if self.account.tier == "gold":
        return self.account.purchase_history.total * 0.1
    return 0

discount = user.get_discount()
```

---

### 3. Inheritance Misuse

**What to look for:**
- Inheritance used for code reuse instead of "is-a"
- Deep inheritance hierarchies (>3 levels)
- Base classes that are too general
- Parallel class hierarchies

**Search patterns:**
```bash
# Find deep hierarchies
grep -rn "class.*\([A-Z]" cortex/ --include="*.py" | head -20

# Find multiple inheritance
grep -rn "class.*(.*, .*)" cortex/ --include="*.py"

# Find inheritance from concrete classes
grep -rn "class.*\([^)]" cortex/ --include="*.py" | grep -v "ABC\|Exception"
```

**Red Flags:**
```python
# ❌ INHERITANCE MISUSE: Should use composition
class Dog(Animal):
    def bark(self): ...

class Car(Machine):
    def honk(self): ...

class RobotDog(Dog, Car):  # Doesn't make sense!
    pass

# ✅ FIX: Use composition
class RobotDog:
    def __init__(self):
        self.dog_behavior = DogBehavior()
        self.machine_behavior = MachineBehavior()
    
    def bark(self):
        return self.dog_behavior.bark()
```

---

### 4. Abstraction Failures

**What to look for:**
- Missing abstractions (same logic in 3+ places)
- Over-abstraction (abstraction not used)
- Leaky abstractions (implementation details exposed)
- Wrong level of abstraction

**Search patterns:**
```bash
# Find potential missing abstractions (repeated patterns)
grep -rn "for.*in\|try:.*except" cortex/ --include="*.py" | head -30

# Find unused abstractions
grep -rn "class [A-Z]" cortex/ --include="*.py" > /tmp/classes.txt
grep -rn "[A-Z][a-zA-Z]*(" cortex/ --include="*.py" | cut -d'(' -f1 > /tmp/usages.txt
comm -23 /tmp/classes.txt /tmp/usages.txt
```

**Red Flags:**
```python
# ❌ MISSING ABSTRACTION: Same pattern repeated
# In order_service.py
for item in items:
    try:
        process(item)
    except Exception as e:
        logger.error(f"Failed: {e}")

# In user_service.py
for item in items:
    try:
        process(item)
    except Exception as e:
        logger.error(f"Failed: {e}")

# ✅ FIX: Extract abstraction
def process_items_safely(items):
    for item in items:
        try:
            process(item)
        except Exception as e:
            logger.error(f"Failed: {e}")
```

---

### 5. Pattern Misuse

**What to look for:**
- Singleton pattern used incorrectly
- Factory pattern for single implementation
- Decorator pattern used instead of direct composition
- Observer pattern without cleanup (memory leaks)

**Search patterns:**
```bash
# Find singleton patterns
grep -rn "class.*Singleton\|_instance\|_shared" cortex/ --include="*.py"

# Find decorators
grep -rn "@\|decorator\|Decorator" cortex/ --include="*.py"

# Find observer patterns
grep -rn "register\|unregister\|listen\|subscribe" cortex/ --include="*.py"
```

**Red Flags:**
```python
# ❌ SINGLETON MISUSE: Thread-unsafe
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:  # Race condition!
            cls._instance = super().__new__(cls)
        return cls._instance

# ✅ FIX: Thread-safe singleton (or use dependency injection)
class Database:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

# ❌ OBSERVER MISUSE: Memory leak from unregistered observers
class Observable:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    # Missing detach()!

# ✅ FIX: Ensure cleanup
class Observable:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def detach(self, observer):
        self.observers.remove(observer)
    
    def notify(self):
        for observer in self.observers[:]:  # Copy list
            observer.update(self)
```

---

## OUTPUT FORMAT

**Create YAML report:** `_workspaces/roadmap/issues/Findings-ARCH-YYYYMMDD.yaml`

```yaml
architecture_findings:
  metadata:
    agent: "ARCHITECTURE_AND_DESIGN_PATTERNS"
    timestamp: "2026-01-23T14:30:00Z"
    confidence_grades: ["A", "B"]
    evidence_locations: ["cortex/api/", "cortex/orchestrators/", "cortex/infrastructure/"]

  srp_violations:
    - finding_id: "SRP-001"
      severity: "HIGH"
      component: "cortex/orchestrators/orchestrator.py"
      issue: "Orchestrator class handles scheduling, execution, logging, and persistence"
      line_count: 850
      concerns_count: 4
      evidence_grade: "A"
      evidence_text: "Lines 1-200: scheduling logic. 201-500: execution. 501-800: logging. 801-850: DB persistence."
      affected_ac_ids: ["AC-ORCH-001"]
      fix_complexity: "HIGH"

  ocp_violations:
    - finding_id: "OCP-001"
      severity: "MEDIUM"
      component: "cortex/brain/processor.py"
      issue: "Hard-coded if/elif chain for processor types"
      lines: [45, 65]
      evidence_grade: "A"
      new_type_count: 3
      would_require_modification: true
      affected_ac_ids: ["AC-BRAIN-002"]

  dependency_inversions:
    - finding_id: "DIP-001"
      severity: "HIGH"
      component: "cortex/execution/executor.py"
      issue: "Hard-coded dependencies instead of injection"
      hard_coded_instantiations: 12
      evidence_grade: "A"
      affected_ac_ids: ["AC-EXEC-001"]
      fix_complexity: "MEDIUM"

  coupling_issues:
    - finding_id: "COUP-001"
      severity: "MEDIUM"
      component: "cortex/api/handlers.py"
      issue: "Deep object chaining violates Law of Demeter"
      max_chain_depth: 5
      example: "request.user.account.permissions.list[0].access_level"
      evidence_grade: "A"
      affected_ac_ids: ["AC-API-003"]

  summary:
    critical_findings: 0
    high_findings: 3
    medium_findings: 5
    total_arch_issues: 8
    recommendation: "Refactor high-priority modules for better architecture"
```

---

## DECISION LOGIC

```yaml
decision_tree:
  found_solid_violations:
    finding: "Multiple SRP/OCP/DIP violations"
    severity: "HIGH"
    action: "Plan refactoring phase"
    complexity: "MEDIUM-HIGH"
    
  found_god_objects:
    finding: "Class with >500 lines and multiple concerns"
    severity: "HIGH"
    action: "Break into smaller, focused classes"
    timeline: "Next phase"
    
  found_tight_coupling:
    finding: "Hard-coded dependencies throughout"
    severity: "MEDIUM"
    action: "Introduce dependency injection"
    timeline: "Phase 2 remediation"
```

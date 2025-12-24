# 💉 Dependency Injection in CORTEX

**Estimated Time:** 15 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Understanding of classes, constructors, and [SOLID Principles](./solid-principles.md)  
**Last Reviewed:** December 6, 2025

---

## 🎯 What You'll Learn

- What dependency injection (DI) is and why it matters
- Constructor injection pattern (CORTEX's preferred approach)
- Service lifetimes (when to use what)
- How DI makes testing easier
- Common DI mistakes and how to avoid them

---

## 📚 What is Dependency Injection?

**Simple Definition:** Instead of creating dependencies inside a class, pass them in from outside.

**Why?**
- **Testability:** Inject mock dependencies for testing
- **Flexibility:** Swap implementations without changing code
- **Loose Coupling:** Classes don't know about concrete implementations

### Without DI (❌ Tight Coupling)
```python
class ProfileAgent:
    def __init__(self):
        # Creates dependency internally - tightly coupled!
        self.database = SQLiteDatabase("/path/to/db")
        self.logger = FileLogger("/path/to/log")
    
    def update_profile(self, user_id, data):
        self.logger.log("Updating profile")
        self.database.save(user_id, data)
```

**Problems:**
- Can't test without real database/file system
- Hard-coded paths make it inflexible
- Can't swap SQLite for PostgreSQL without changing code
- Creates new dependencies every time (wasteful)

### With DI (✅ Loose Coupling)
```python
class ProfileAgent:
    def __init__(self, database, logger):
        # Dependencies injected - loosely coupled!
        self.database = database
        self.logger = logger
    
    def update_profile(self, user_id, data):
        self.logger.log("Updating profile")
        self.database.save(user_id, data)

# Production: Inject real implementations
agent = ProfileAgent(
    database=SQLiteDatabase("/path/to/db"),
    logger=FileLogger("/path/to/log")
)

# Testing: Inject mocks
agent = ProfileAgent(
    database=MockDatabase(),
    logger=MockLogger()
)
```

**Benefits:**
- Easy to test (inject mocks)
- Flexible (swap implementations)
- No hard-coded dependencies
- Reuse existing instances

---

## 🏗️ Types of Dependency Injection

### 1. Constructor Injection (Recommended)

**Pattern:** Pass dependencies through constructor

```python
class UserService:
    def __init__(self, repository, logger):
        """Dependencies injected via constructor"""
        self.repository = repository
        self.logger = logger
```

**When to Use:** Always (CORTEX default)

**Pros:**
- Dependencies explicit and required
- Immutable after construction
- Easy to test
- Clear what class needs

**Cons:**
- Constructor can get long (but that's a code smell - class doing too much!)

### 2. Property Injection (Not Recommended)

**Pattern:** Set dependencies after construction

```python
class UserService:
    def __init__(self):
        self.repository = None  # ❌ Optional dependencies are code smell
        self.logger = None

service = UserService()
service.repository = SQLiteRepository()  # Set after construction
service.logger = FileLogger()
```

**When to Use:** Rarely - only for truly optional dependencies

**Cons:**
- Dependencies might be None (NullReferenceError risk)
- Not obvious what's required
- Harder to test

### 3. Method Injection (Special Cases)

**Pattern:** Pass dependency to specific method

```python
class ReportGenerator:
    def generate(self, data, formatter):
        """Formatter injected per method call"""
        formatted = formatter.format(data)
        return formatted

generator = ReportGenerator()
pdf_report = generator.generate(data, PDFFormatter())
json_report = generator.generate(data, JSONFormatter())
```

**When to Use:** When dependency varies per method call

---

## 🔧 CORTEX Dependency Injection Patterns

### Pattern 1: Agent Constructor Injection

```python
class ProfileAgent(BaseAgent):
    def __init__(
        self, 
        name: str = "ProfileAgent",
        db_path: Optional[str] = None,
        tier1_api=None,      # Injected brain tier
        tier2_kg=None,       # Injected brain tier
        tier3_context=None   # Injected brain tier
    ):
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Create UserProfileManager with injected db_path
        self.profile_manager = UserProfileManager(db_path)
```

**What's Injected:**
- `tier1_api`, `tier2_kg`, `tier3_context` - Brain tier dependencies
- `db_path` - Configuration (optional, has default)

**Why This Works:**
- Testing: Inject mock brain tiers
- Flexibility: Use different databases per environment
- Clear dependencies: Everything needed is in constructor

### Pattern 2: Setup Module Dependency Injection

```python
class VisionAPIModule(BaseSetupModule):
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """Context acts as a dependency container"""
        
        # Extract injected dependencies from context
        project_root = context['project_root']
        brain_path = context['brain_path']
        platform_info = context.get('platform_info', {})
        
        # Use dependencies
        api_key = self._get_api_key(platform_info)
```

**What's Injected:**
- Entire `context` dictionary acts as service locator
- Modules extract what they need

**Why This Works:**
- Modules are decoupled from orchestrator
- Easy to add new context data
- Each module gets only what it needs

### Pattern 3: Optional Dependencies with Defaults

```python
class WorkingMemory:
    def __init__(self, db_path: Optional[str] = None):
        """db_path is optional - has sensible default"""
        
        if db_path is None:
            # Default to standard location
            db_path = self._get_default_db_path()
        
        self.db_path = db_path
        self._init_database()
```

**When to Use:**
- Configuration values with sensible defaults
- Optional features (logging, caching)

---

## 🧪 Testing with Dependency Injection

### Without DI - Hard to Test
```python
class EmailService:
    def __init__(self):
        self.smtp_client = SMTPClient("smtp.gmail.com", 587)  # ❌ Hard-coded
    
    def send_email(self, to, subject, body):
        self.smtp_client.send(to, subject, body)

# Test - ACTUALLY SENDS EMAIL! 😱
def test_send_email():
    service = EmailService()
    service.send_email("user@example.com", "Test", "Body")  # Sends real email!
```

### With DI - Easy to Test
```python
class EmailService:
    def __init__(self, smtp_client):
        self.smtp_client = smtp_client  # ✅ Injected
    
    def send_email(self, to, subject, body):
        self.smtp_client.send(to, subject, body)

# Test - Uses mock
def test_send_email():
    mock_client = MockSMTPClient()
    service = EmailService(mock_client)
    
    service.send_email("user@example.com", "Test", "Body")
    
    # Verify mock was called correctly
    assert mock_client.send_called
    assert mock_client.last_to == "user@example.com"
```

### CORTEX Real Test Example
```python
def test_profile_agent_update():
    """Test ProfileAgent with mocked dependencies"""
    
    # Create mock dependencies
    mock_tier1 = MockTier1API()
    mock_db = MockDatabase()
    
    # Inject mocks
    agent = ProfileAgent(
        name="TestAgent",
        db_path=":memory:",  # In-memory DB for testing
        tier1_api=mock_tier1
    )
    
    # Test without touching real database
    request = AgentRequest(
        user_message="set experience to junior",
        intent=IntentType.UPDATE_PROFILE
    )
    
    response = agent.execute(request)
    
    assert response.success
    assert "junior" in response.message
```

---

## 📊 Service Lifetimes (When Using DI Containers)

**Note:** Python doesn't have built-in DI containers like C#/.NET, but understanding lifetimes helps when designing object creation.

### Transient (New instance every time)
```python
# Every call creates new instance
agent1 = ProfileAgent(db_path="/path/to/db")
agent2 = ProfileAgent(db_path="/path/to/db")  # Different instance
```

**When to Use:** Lightweight, stateless objects

### Singleton (One instance shared)
```python
# Shared instance
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

db1 = DatabaseConnection()
db2 = DatabaseConnection()  # Same instance as db1
```

**When to Use:** Expensive resources (database connections, file handles)

### Scoped (One per request/session)
```python
# In web frameworks - one instance per HTTP request
# Not applicable to CORTEX CLI
```

---

## ⚠️ Common DI Mistakes

### Mistake 1: Service Locator Anti-Pattern
```python
# ❌ BAD - Hidden dependencies
class ProfileAgent:
    def update_profile(self):
        # Dependencies hidden in service locator
        database = ServiceLocator.get("database")
        logger = ServiceLocator.get("logger")
        database.save(...)

# ✅ GOOD - Explicit dependencies
class ProfileAgent:
    def __init__(self, database, logger):
        self.database = database  # Clear what's needed
        self.logger = logger
```

### Mistake 2: Injecting Too Many Dependencies
```python
# ❌ BAD - Too many dependencies (code smell!)
class UserService:
    def __init__(self, repo, logger, email, sms, cache, metrics, audit, validator):
        # 8 dependencies = class doing too much!
        pass

# ✅ GOOD - Refactor into smaller classes
class UserService:
    def __init__(self, repo, logger, notification_service):
        # 3 dependencies = manageable
        self.notification_service = notification_service  # Hides email/sms complexity
```

### Mistake 3: Circular Dependencies
```python
# ❌ BAD - A depends on B, B depends on A
class ServiceA:
    def __init__(self, service_b):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a  # Circular!

# ✅ GOOD - Introduce interface/abstraction
class IServiceA(ABC):
    @abstractmethod
    def do_something(self): pass

class ServiceA(IServiceA):
    def __init__(self, service_b):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a: IServiceA):  # Depends on abstraction
        self.service_a = service_a
```

---

## 🎥 Video Resources

- [Dependency Injection (8 min)](https://www.youtube.com/watch?v=0yc2UANSDiw) - Christopher Okhravi - Clear explanation
- [Dependency Injection Explained (10 min)](https://www.youtube.com/watch?v=IKD2-MAkXyQ) - ArjanCodes - Python-specific
- [SOLID: Dependency Inversion (12 min)](https://www.youtube.com/watch?v=9oHY5TllWaU) - Christopher Okhravi

---

## 📖 Further Reading

- [Dependency Injection (Martin Fowler)](https://martinfowler.com/articles/injection.html)
- [Python Dependency Injection](https://python-dependency-injector.ets-labs.org/)
- [Inversion of Control Containers](https://martinfowler.com/articles/injection.html)

---

## ✅ Quick Checklist

Before writing a class, ask:

- [ ] Are dependencies passed via constructor? (Not created internally)
- [ ] Can I easily mock dependencies for testing?
- [ ] Are dependencies abstractions, not concrete classes?
- [ ] Do I have fewer than 5 constructor parameters?
- [ ] Are optional dependencies truly optional?

---

## 🚀 Next Steps

1. **Practice:** Review CORTEX agents - spot constructor injection pattern
2. **Apply:** Refactor one of your classes to use constructor injection
3. **Test:** Write a test using mocked dependencies
4. **Deep Dive:** Learn [Testing Strategies](./testing-strategies.md) to master mocking

---

**Questions?** Ask CORTEX: `"explain dependency injection in [specific code]"` for custom examples.

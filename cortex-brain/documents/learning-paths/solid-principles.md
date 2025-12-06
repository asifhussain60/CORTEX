# 🏛️ SOLID Principles in CORTEX

**Estimated Time:** 20 minutes  
**Difficulty:** Beginner  
**Prerequisites:** Basic understanding of classes and objects  
**Last Reviewed:** December 6, 2025

---

## 🎯 What You'll Learn

By the end of this guide, you'll understand:
- The 5 SOLID principles (SRP, OCP, LSP, ISP, DIP)
- How CORTEX applies each principle
- Why SOLID code is easier to test and maintain
- Common violations and how to fix them

---

## 📚 The Five Principles

### 1. Single Responsibility Principle (SRP)

**Definition:** A class should have one, and only one, reason to change.

**Why It Matters:**
- Easier to understand (one job per class)
- Easier to test (fewer dependencies)
- Easier to maintain (changes are isolated)

**CORTEX Example:**

```python
# ❌ BAD - Multiple responsibilities
class UserManager:
    def create_user(self, name, email):
        # Creates user
        user = {"name": name, "email": email}
        
        # Validates email
        if "@" not in email:
            raise ValueError("Invalid email")
        
        # Saves to database
        db.save(user)
        
        # Sends welcome email
        email_service.send(email, "Welcome!")
        
        return user

# ✅ GOOD - Single responsibility per class
class UserValidator:
    def validate_email(self, email):
        if "@" not in email:
            raise ValueError("Invalid email")

class UserRepository:
    def save(self, user):
        db.save(user)

class EmailService:
    def send_welcome(self, email):
        email_service.send(email, "Welcome!")

class UserManager:
    def __init__(self, validator, repository, email_service):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
    
    def create_user(self, name, email):
        self.validator.validate_email(email)
        user = {"name": name, "email": email}
        self.repository.save(user)
        self.email_service.send_welcome(email)
        return user
```

**CORTEX Real Example:**
```python
# ProfileAgent - ONLY routes profile update requests
class ProfileAgent(BaseAgent):
    def execute(self, request: AgentRequest) -> AgentResponse:
        updates = self._parse_update_request(request.user_message)
        # Delegates actual storage to UserProfileManager
        return self.profile_manager.update_profile(updates)

# UserProfileManager - ONLY handles database operations
class UserProfileManager:
    def update_profile(self, updates: Dict) -> bool:
        # Only responsible for data persistence
        return self._execute_update(updates)
```

**Why This Works:**
- ProfileAgent changes only if routing logic changes
- UserProfileManager changes only if storage logic changes
- Each class has ONE reason to change

---

### 2. Open/Closed Principle (OCP)

**Definition:** Software entities should be open for extension, but closed for modification.

**Why It Matters:**
- Add new features without changing existing code
- Reduces risk of breaking working functionality
- Supports plugin architectures

**CORTEX Example:**

```python
# ❌ BAD - Must modify class to add new agent types
class AgentFactory:
    def create_agent(self, agent_type: str):
        if agent_type == "profile":
            return ProfileAgent()
        elif agent_type == "planning":
            return PlanningAgent()
        elif agent_type == "tdd":
            return TDDAgent()
        # Adding new agent requires modifying this method!

# ✅ GOOD - Extend via registration, no modification needed
class AgentFactory:
    def __init__(self):
        self._registry = {}
    
    def register_agent(self, agent_type: str, agent_class):
        """Extend by registering new agents"""
        self._registry[agent_type] = agent_class
    
    def create_agent(self, agent_type: str):
        """Closed for modification"""
        agent_class = self._registry.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_class()

# Extend without modifying AgentFactory
factory = AgentFactory()
factory.register_agent("profile", ProfileAgent)
factory.register_agent("planning", PlanningAgent)
factory.register_agent("new_type", NewAgent)  # Extension, no modification!
```

**CORTEX Real Example:**
```python
# Setup modules extend via BaseSetupModule, no orchestrator changes needed
class VisionAPIModule(BaseSetupModule):
    def execute(self, context):
        # New module added without modifying SetupOrchestrator
        pass

# SetupOrchestrator is closed for modification
class SetupOrchestrator:
    def register_module(self, module: BaseSetupModule):
        # Accepts ANY module implementing BaseSetupModule
        self._modules[module.metadata.module_id] = module
```

---

### 3. Liskov Substitution Principle (LSP)

**Definition:** Subtypes must be substitutable for their base types without altering program correctness.

**Why It Matters:**
- Polymorphism works correctly
- Base class references can use subclasses safely
- Prevents unexpected behavior

**CORTEX Example:**

```python
# ✅ GOOD - All agents are substitutable for BaseAgent
class BaseAgent:
    def can_handle(self, request: AgentRequest) -> bool:
        """Returns True if this agent can handle the request"""
        raise NotImplementedError
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent's logic"""
        raise NotImplementedError

class ProfileAgent(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == IntentType.UPDATE_PROFILE  # ✅ Returns bool
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # ✅ Returns AgentResponse
        return AgentResponse(success=True, result={})

class PlanningAgent(BaseAgent):
    def can_handle(self, request: AgentRequest) -> bool:
        return request.intent == IntentType.PLAN_FEATURE  # ✅ Returns bool
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        # ✅ Returns AgentResponse
        return AgentResponse(success=True, result={})

# All agents are substitutable - orchestrator doesn't care which subclass
for agent in [ProfileAgent(), PlanningAgent(), TDDAgent()]:
    if agent.can_handle(request):  # Works for all subclasses
        response = agent.execute(request)  # Works for all subclasses
```

---

### 4. Interface Segregation Principle (ISP)

**Definition:** Clients should not be forced to depend on interfaces they don't use.

**Why It Matters:**
- Reduces coupling
- Smaller, focused interfaces
- Easier to implement

**Python Note:** Python doesn't have formal interfaces, but we use abstract base classes (ABC).

**CORTEX Example:**

```python
# ❌ BAD - Fat interface, not all agents need all methods
class BaseAgent:
    def can_handle(self, request): pass
    def execute(self, request): pass
    def validate_syntax(self, code): pass  # Only TDD agents need this
    def generate_diagram(self, data): pass  # Only planning agents need this
    def send_email(self, user): pass  # Only notification agents need this

# ✅ GOOD - Segregated interfaces
class BaseAgent(ABC):
    """Core agent interface - all agents need these"""
    @abstractmethod
    def can_handle(self, request): pass
    
    @abstractmethod
    def execute(self, request): pass

class CodeValidatorMixin:
    """Only for agents that validate code"""
    def validate_syntax(self, code): pass

class DiagramGeneratorMixin:
    """Only for agents that generate diagrams"""
    def generate_diagram(self, data): pass

# Agents implement only what they need
class TDDAgent(BaseAgent, CodeValidatorMixin):
    def can_handle(self, request): return request.intent == IntentType.TDD
    def execute(self, request): pass
    def validate_syntax(self, code): pass  # Only TDD agents implement this

class PlanningAgent(BaseAgent, DiagramGeneratorMixin):
    def can_handle(self, request): return request.intent == IntentType.PLAN
    def execute(self, request): pass
    def generate_diagram(self, data): pass  # Only planning agents implement this
```

---

### 5. Dependency Inversion Principle (DIP)

**Definition:** High-level modules should not depend on low-level modules. Both should depend on abstractions.

**Why It Matters:**
- Reduces coupling between layers
- Makes code testable (inject mocks)
- Supports multiple implementations

**CORTEX Example:**

```python
# ❌ BAD - High-level depends on low-level concrete class
class ProfileAgent:
    def __init__(self):
        # Depends on concrete SQLite implementation
        self.profile_manager = SQLiteUserProfileManager()

# ✅ GOOD - Depends on abstraction
class IUserProfileManager(ABC):
    """Abstraction - defines contract"""
    @abstractmethod
    def update_profile(self, updates): pass

class SQLiteUserProfileManager(IUserProfileManager):
    """Concrete implementation"""
    def update_profile(self, updates):
        # SQLite-specific logic
        pass

class InMemoryUserProfileManager(IUserProfileManager):
    """Alternative implementation for testing"""
    def update_profile(self, updates):
        # In-memory logic
        pass

class ProfileAgent:
    def __init__(self, profile_manager: IUserProfileManager):
        # Depends on abstraction, not concrete class
        self.profile_manager = profile_manager

# Production: Inject SQLite implementation
agent = ProfileAgent(SQLiteUserProfileManager())

# Testing: Inject mock implementation
agent = ProfileAgent(InMemoryUserProfileManager())
```

**CORTEX Real Example:**
```python
class BaseAgent:
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        # Depends on abstractions (interfaces), not concrete implementations
        self.tier1_api = tier1_api  # Could be any tier1 implementation
        self.tier2_kg = tier2_kg    # Could be any tier2 implementation
        self.tier3_context = tier3_context  # Could be any tier3 implementation
```

---

## 🎥 Video Resources

- [SOLID Principles (10 min)](https://www.youtube.com/watch?v=pTB30aXS77U) - Fireship - Quick, visual overview
- [SOLID Principles Explained (7 min)](https://www.youtube.com/watch?v=_jDNAf3CzeY) - Christopher Okhravi - Deep dive
- [SOLID Design Principles (15 min)](https://www.youtube.com/watch?v=yxf2spbpTSw) - Mosh Hamedani - Practical examples

---

## 📖 Further Reading

- [SOLID Principles (DigitalOcean)](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Clean Code JavaScript](https://github.com/ryanmcdermott/clean-code-javascript#solid) - Principles apply to Python
- [Real Python: SOLID Principles](https://realpython.com/solid-principles-python/)

---

## 🔍 Common Violations in Practice

### Violation: God Classes
**Symptom:** One class does everything (1000+ lines)  
**Fix:** Split into multiple classes following SRP

### Violation: Tight Coupling
**Symptom:** Changing one class breaks five others  
**Fix:** Apply DIP - depend on abstractions

### Violation: Framework Lock-In
**Symptom:** Can't swap database/framework without rewriting  
**Fix:** Apply DIP - wrap framework behind abstraction

---

## ✅ Quick Checklist

Before committing code, ask yourself:

- [ ] Does each class have ONE reason to change? (SRP)
- [ ] Can I add features without modifying existing code? (OCP)
- [ ] Can I swap subclasses without breaking code? (LSP)
- [ ] Do classes implement only methods they need? (ISP)
- [ ] Do high-level modules depend on abstractions? (DIP)

---

## 🚀 Next Steps

1. **Practice:** Review code CORTEX generates - identify SOLID principles in action
2. **Deep Dive:** Learn [Dependency Injection](./dependency-injection.md) - DIP in practice
3. **Apply:** Refactor one of your classes using SOLID principles

---

**Questions?** Ask CORTEX: `"explain SOLID principles in [specific code]"` for custom examples.

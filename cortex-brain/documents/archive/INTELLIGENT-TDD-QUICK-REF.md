# 🧬 Intelligent TDD Enforcement - Quick Reference

**Version:** 3.8.5 | **Last Updated:** 2025-01-08

---

## 🎯 One-Line Summary

**CORTEX automatically enforces TDD only for high-value production code (controllers, services, repositories with logic) and skips simple data structures (entities, DTOs, POCOs).**

---

## ⚡ Quick Decision Matrix

| Code Type | Complexity | TDD Required? | Reason |
|-----------|------------|---------------|---------|
| Controller | Any | ✅ YES | HTTP logic critical |
| Service | Any | ✅ YES | Business logic critical |
| Repository | ≥30/100 | ✅ YES | Data access with logic |
| Middleware | Any | ✅ YES | Pipeline logic critical |
| Validator | Any | ✅ YES | Validation logic critical |
| Orchestrator | Any | ✅ YES | Workflow coordination critical |
| **Entity** | **<30/100** | **❌ NO** | **Simple properties only** |
| **DTO** | **<30/100** | **❌ NO** | **Data carrier only** |
| **Configuration** | **<30/100** | **❌ NO** | **Settings only** |
| **Constants** | **Any** | **❌ NO** | **Readonly values** |

---

## 🔍 How It Works

### 1. Code Type Detection (Triple Pattern Matching)

```python
# File Path Pattern
"**/Controllers/**/*Controller.cs" → CONTROLLER
"**/Entities/**/*.cs" → ENTITY
"**/DTOs/**/*Dto.cs" → DTO

# Code Content Pattern
"public class UserController : ControllerBase" → CONTROLLER
"public class User { get; set; }" → ENTITY
"public class UserDto { get; set; }" → DTO

# Intent Keywords
"Create user controller" → CONTROLLER
"Create user entity" → ENTITY
"Create user DTO" → DTO
```

### 2. Complexity Calculation (0-100 Scale)

```python
complexity_score = (
    method_count * 15 +        # Methods indicate logic
    conditionals * 15 +        # If/else branches
    loops * 15 +               # For/while/foreach
    dependency_count * 10      # Injected services
) capped at 100
```

**Examples:**
- Entity with 5 properties, 0 methods → **5/100**
- Repository with 3 methods, 2 dependencies → **65/100**
- Service with 4 methods, 3 conditionals, 2 dependencies → **80/100**

### 3. TDD Decision Logic

```python
TDD_COMPLEXITY_THRESHOLD = 30

if code_type in [CONTROLLER, SERVICE, MIDDLEWARE, VALIDATOR, ORCHESTRATOR]:
    return TDD_REQUIRED  # Always enforce for these types
elif code_type in [ENTITY, DTO, CONFIGURATION, CONSTANTS]:
    if complexity_score >= 30:
        return TDD_REQUIRED  # Complex entity with business logic
    else:
        return TDD_OPTIONAL  # Simple data structure
else:
    return TDD_REQUIRED  # Unknown type, err on safe side
```

---

## 🚀 Usage Examples

### Example 1: Create Simple Entity (TDD Skipped)

```csharp
// User creates FundingInvoice.cs
public class FundingInvoice
{
    public int Id { get; set; }
    public string InvoiceNumber { get; set; }
    public decimal Amount { get; set; }
    public DateTime CreatedDate { get; set; }
}

// CORTEX Analysis:
// - Code Type: ENTITY (file path + properties pattern)
// - Complexity: 8/100 (4 properties, 0 methods)
// - Decision: TDD OPTIONAL
// - Rationale: "Simple entity - properties only, no business logic"
// - Action: Creates entity WITHOUT tests

// Log Output:
// ⏭️  TDD OPTIONAL: Simple entity - properties only
//    Exemption: Entity has 0 methods, complexity 8/100 (threshold 30)
//    Properties: 4
```

### Example 2: Create Controller (TDD Enforced)

```csharp
// User creates FundingInvoicesController.cs
public class FundingInvoicesController : ControllerBase
{
    private readonly IFundingInvoiceService _service;
    
    [HttpGet]
    public async Task<IActionResult> GetAll() { ... }
    
    [HttpPost]
    public async Task<IActionResult> Create(CreateInvoiceDto dto) { ... }
}

// CORTEX Analysis:
// - Code Type: CONTROLLER (file path + [ApiController] pattern)
// - Complexity: 70/100 (2 methods, 1 dependency, HTTP attributes)
// - Decision: TDD MANDATORY
// - Rationale: "Controller with API endpoints - HTTP logic critical"
// - Action: ENFORCES RED→GREEN→REFACTOR

// Log Output:
// 🔴 TDD MANDATORY: Controller with API endpoints
//    Code Type: CONTROLLER
//    Complexity: 70/100
//    Methods: 2
//
// ❌ RED_PHASE_VALIDATION: Cannot proceed without tests
//    Challenge: Write failing tests FIRST for FundingInvoicesController
```

### Example 3: Create Service with Validation (TDD Enforced)

```csharp
// User creates FundingInvoiceService.cs
public class FundingInvoiceService : IFundingInvoiceService
{
    private readonly IFundingInvoiceRepository _repository;
    private readonly IValidator<CreateInvoiceDto> _validator;
    
    public async Task<Invoice> CreateAsync(CreateInvoiceDto dto)
    {
        var validationResult = await _validator.ValidateAsync(dto);
        if (!validationResult.IsValid)
            throw new ValidationException(validationResult.Errors);
        
        // ... business logic ...
    }
}

// CORTEX Analysis:
// - Code Type: SERVICE (file path + IService pattern)
// - Complexity: 65/100 (1 method, 2 dependencies, conditional, validation)
// - Decision: TDD MANDATORY
// - Rationale: "Service with business logic and validation - high business value"
// - Action: ENFORCES RED→GREEN→REFACTOR

// Log Output:
// 🔴 TDD MANDATORY: Service with business logic
//    Code Type: SERVICE
//    Complexity: 65/100
//    Methods: 1 | Dependencies: 2 | Conditionals: 2
```

---

## 🛠️ Developer Workflow

### Automatic Enforcement (Planning System)

```bash
# User runs planning command
> plan RA Funding Invoices Feature

# CORTEX Planning System analyzes phases:
Phase 1: Create Entity Models
  → Detection: ENTITY, complexity 5-10/100
  → Decision: TDD OPTIONAL
  → DoR: "⏭️  TDD OPTIONAL for: Phase 1 - Entity Models"

Phase 2: Create Repositories
  → Detection: REPOSITORY, complexity 50-60/100
  → Decision: TDD MANDATORY
  → DoR: "🧬 TDD MANDATORY for: Phase 2 - Repositories"

Phase 3: Create Controllers
  → Detection: CONTROLLER, complexity 70-80/100
  → Decision: TDD MANDATORY
  → DoR: "🧬 TDD MANDATORY for: Phase 3 - Controllers"
```

### Manual Check (Python API)

```python
from src.orchestrators.tdd_intelligence import get_tdd_intelligence

tdd_intel = get_tdd_intelligence()

# Analyze code before creating
code = """
public class UserDto
{
    public string Name { get; set; }
    public string Email { get; set; }
}
"""

decision = tdd_intel.analyze_code_for_tdd(
    code_content=code,
    file_path="src/DTOs/UserDto.cs",
    intent="Create user DTO for API requests"
)

print(decision.tdd_required)       # False
print(decision.code_type.value)    # "DTO"
print(decision.complexity_score)   # 3
print(decision.exemption_reason)   # "DTO with 0 methods, complexity 3/100"
```

---

## 📊 Brain Protection Integration

### SKULL Rule: TDD_ENFORCEMENT

```yaml
TDD_ENFORCEMENT:
  combined_keywords:
    high_value_code:
      - controller
      - service
      - business logic
      - repository method
      - validation
      - authorization
      - workflow
    
    low_value_exemptions:
      - entity
      - DTO
      - POCO
      - configuration
      - constants
  
  complexity_threshold:
    methods_with_logic: true
    cyclomatic_complexity: "> 1"
  
  intelligent_enforcement:
    - HIGH-VALUE code (controllers, services, repositories) → TDD MANDATORY
    - LOW-VALUE code (entities, DTOs, POCOs) → TDD OPTIONAL
    - Threshold: 30/100 complexity score
```

### Challenge Messages

**TDD Mandatory (Blocked):**
```
❌ RED_PHASE_VALIDATION violation: Test files missing
   Brain Protector: TDD_ENFORCEMENT requires test-first.
   
   Analysis:
   - Code Type: CONTROLLER
   - Complexity: 75/100
   - Rationale: Controller with API endpoints - HTTP logic critical
   
   Action Required:
   1. Create test file: FundingInvoicesControllerTests.cs
   2. Write failing test (RED phase)
   3. Run tests (verify failure)
   4. Then implement controller (GREEN phase)
```

**TDD Optional (Allowed):**
```
⏭️  TDD OPTIONAL: Simple entity - properties only
   Exemption: Entity with 0 methods, complexity 8/100 (threshold 30)
   Evidence: 4 properties, 0 dependencies
   
   Proceeding WITHOUT tests (low business value code).
```

---

## 🎯 Configuration

### Threshold Tuning (Advanced)

**File:** `src/orchestrators/tdd_intelligence.py`

```python
# Adjust complexity threshold (default: 30/100)
TDD_COMPLEXITY_THRESHOLD = 30  # Lower = stricter, Higher = more lenient

# Adjust complexity weights
method_count * 15        # Default: 15 points per method
conditionals * 15        # Default: 15 points per if/else
loops * 15               # Default: 15 points per loop
dependencies * 10        # Default: 10 points per injected service
```

### Adding Custom Code Types

```python
# src/orchestrators/tdd_intelligence.py

class CodeType(Enum):
    # ... existing types ...
    CUSTOM_HANDLER = "custom_handler"  # Add new type

# Update TDD_MANDATORY_TYPES or TDD_OPTIONAL_TYPES
TDD_MANDATORY_TYPES = {
    CodeType.CONTROLLER,
    CodeType.SERVICE,
    CodeType.CUSTOM_HANDLER  # Include new type
}

# Add detection patterns in _detect_code_type()
if "handler" in file_path.lower() or "Handler" in code_content:
    return CodeType.CUSTOM_HANDLER
```

---

## 🔍 Debugging TDD Decisions

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run TDD analysis
decision = tdd_intel.analyze_code_for_tdd(...)

# Output will show:
# DEBUG: Analyzing code for TDD requirement
# DEBUG: File path: src/Entities/User.cs
# DEBUG: Intent: Create user entity
# DEBUG: Detected code type: ENTITY
# DEBUG: Calculated complexity: 8/100
# DEBUG: Evidence: {'method_count': 0, 'property_count': 4, ...}
# INFO:  TDD OPTIONAL: Simple entity - properties only
```

### Inspect TDDDecision Object

```python
decision = tdd_intel.analyze_code_for_tdd(...)

print(f"Required: {decision.tdd_required}")
print(f"Code Type: {decision.code_type.value}")
print(f"Complexity: {decision.complexity_score}/100")
print(f"Rationale: {decision.rationale}")
print(f"Evidence: {decision.evidence}")
print(f"Exemption: {decision.exemption_reason}")

# Output:
# Required: False
# Code Type: ENTITY
# Complexity: 8/100
# Rationale: Simple entity - properties only, no business logic
# Evidence: {'method_count': 0, 'property_count': 4, 'conditional_count': 0, ...}
# Exemption: Entity with 0 methods, complexity 8/100 (threshold 30)
```

---

## 📚 Related Documentation

- **Full Report:** `cortex-brain/documents/reports/TDD-INTELLIGENCE-INTEGRATION-REPORT.md`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **CORTEX Instructions:** `.github/prompts/CORTEX.prompt.md`
- **TDD Orchestrator:** `src/orchestrators/tdd_implementation_orchestrator.py`
- **Planning Orchestrator:** `src/orchestrators/planning_orchestrator.py`

---

## 🚨 Common Issues

### Issue 1: TDD Enforced on Simple Entity

**Symptom:** Entity with only properties triggers TDD requirement

**Cause:** File path not matching ENTITY pattern (e.g., in `/Models/` instead of `/Entities/`)

**Fix:** 
```python
# Check file path detection
decision = tdd_intel.analyze_code_for_tdd(
    code_content=entity_code,
    file_path="src/Entities/User.cs",  # Use correct path pattern
    intent="Create user entity"
)
```

### Issue 2: TDD Skipped on Repository

**Symptom:** Repository with methods NOT enforcing TDD

**Cause:** Complexity score below 30 (too few methods/dependencies detected)

**Fix:** Lower threshold or add explicit enforcement:
```python
# Option 1: Lower threshold (global change)
TDD_COMPLEXITY_THRESHOLD = 20

# Option 2: Force TDD for specific file
if "Repository" in file_path:
    return TDDDecision(tdd_required=True, ...)
```

### Issue 3: Unknown Code Type

**Symptom:** Code classified as UNKNOWN, defaults to TDD_REQUIRED

**Cause:** No matching patterns in file path, content, or intent

**Fix:** Add detection pattern:
```python
# In _detect_code_type() method
if "custom_pattern" in file_path.lower():
    return CodeType.CUSTOM_TYPE
```

---

**Last Updated:** 2025-01-08  
**Maintainer:** CORTEX Team  
**Status:** ✅ Active

# Phase P01.4: Python Best Practices Validator

**Epic:** cortex5-enhancement-epic-v2  
**Phase:** P01.4 (Bonus Enhancement - Inserts after Phase 1)  
**Track:** Track 1 (Core Intelligence)  
**Duration:** 6 hours  
**Dependencies:** Phase 1 (Knowledge Extension Layer)  
**Status:** 🟢 RECOMMENDED (Addresses ARCH-004 Critical Issue)  
**Priority:** P1 (HIGH)

---

## 🎯 Phase Objective

**Goal:** Enforce Python coding standards, SOLID principles, and CORTEX-specific architecture patterns through automated middleware validation BEFORE code execution.

**Why This Matters:**  
The CORTEX review (2026-01-07) identified **ARCH-004** as a CRITICAL issue: "Python best practices NOT enforced in Master Orchestrator." While comprehensive best practices documentation now exists (python-style-guide.md, python-architecture-patterns.md, solid-principles.md), there's **NO enforcement mechanism** to prevent non-compliant code from executing.

**Problem Examples:**
- Orchestrators with inconsistent `__init__` signatures (caused INT-001)
- Missing type hints on public APIs
- SOLID principle violations (fat interfaces, tight coupling)
- Cyclomatic complexity >10 (unmaintainable code)
- Missing docstrings on critical classes

---

## 📋 Deliverables

### 1. PythonBestPracticesValidator Middleware

**File:** `src/middleware/python_best_practices_validator.py`

**Class:** `PythonBestPracticesValidator`

**Validation Categories:**

#### A. PEP 8 Compliance
```python
def validate_pep8(self, file_path: str) -> ValidationResult:
    """Validate PEP 8 compliance using black + isort.
    
    Checks:
    - Indentation (4 spaces, no tabs)
    - Line length (≤100 characters)
    - Naming conventions (PascalCase, snake_case, SCREAMING_SNAKE_CASE)
    - Import organization (stdlib → third-party → local)
    - Whitespace consistency
    
    Returns:
        ValidationResult with errors/warnings
    """
```

#### B. Type Hints (PEP 484)
```python
def validate_type_hints(self, file_path: str) -> ValidationResult:
    """Validate type hints using mypy.
    
    Checks:
    - All public functions have return type annotations
    - All function parameters have type annotations
    - Class attributes have type annotations
    - No use of `Any` without justification
    - Complex types use proper generics (Dict, List, Optional)
    
    Returns:
        ValidationResult with missing type hints
    """
```

#### C. Docstrings (PEP 257 + Google Style)
```python
def validate_docstrings(self, file_path: str) -> ValidationResult:
    """Validate docstring completeness.
    
    Checks:
    - All public classes have docstrings
    - All public functions/methods have docstrings
    - Docstrings include Args, Returns, Raises, Example
    - Performance characteristics documented (O(n) complexity)
    - Side effects documented (modifies database, etc.)
    
    Returns:
        ValidationResult with missing/incomplete docstrings
    """
```

#### D. SOLID Principles
```python
def validate_solid_principles(self, file_path: str) -> ValidationResult:
    """Validate SOLID principle adherence using AST analysis.
    
    Checks:
    - Single Responsibility: Class has ≤3 public methods (excluding __init__)
    - Open/Closed: Uses inheritance/composition, not if/elif chains
    - Liskov Substitution: Subclasses don't strengthen preconditions
    - Interface Segregation: Protocols have ≤5 methods
    - Dependency Inversion: Depends on ABC/Protocol, not concrete classes
    
    Returns:
        ValidationResult with SOLID violations
    """
```

#### E. Code Quality
```python
def validate_code_quality(self, file_path: str) -> ValidationResult:
    """Validate code quality metrics.
    
    Checks:
    - Cyclomatic complexity ≤10 per function
    - Function length ≤50 lines
    - Class length ≤300 lines
    - Module length ≤500 lines
    - Nesting depth ≤4 levels
    - Parameter count ≤5 per function
    - Code duplication ≤5 consecutive lines
    
    Returns:
        ValidationResult with quality violations
    """
```

#### F. CORTEX Architecture Patterns
```python
def validate_cortex_patterns(self, file_path: str) -> ValidationResult:
    """Validate CORTEX-specific architecture patterns.
    
    Checks:
    - Orchestrators implement OrchestratorInterface protocol
    - Orchestrators have consistent __init__ signature
    - State management uses StateStore abstraction (not direct SQLite)
    - Middleware uses Chain of Responsibility pattern
    - Execution modes use Strategy pattern
    
    Returns:
        ValidationResult with pattern violations
    """
```

---

### 2. Validation Result Schema

**File:** `src/middleware/validation_result.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any

class ValidationSeverity(Enum):
    """Validation error severity."""
    ERROR = "error"      # Blocks execution
    WARNING = "warning"  # Logs but allows execution
    INFO = "info"        # Informational only

@dataclass
class ValidationError:
    """Individual validation error."""
    severity: ValidationSeverity
    category: str  # "pep8", "type_hints", "docstrings", etc.
    rule: str      # "PEP8-001", "SOLID-SRP-001", etc.
    file_path: str
    line_number: int
    message: str
    fix_suggestion: str  # How to fix the error

@dataclass
class ValidationResult:
    """Validation result for a file or module."""
    file_path: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    info: List[ValidationError]
    
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Validation {'PASSED' if self.is_valid else 'FAILED'}: "
            f"{len(self.errors)} errors, {len(self.warnings)} warnings, "
            f"{len(self.info)} info"
        )
```

---

### 3. Integration with Master Orchestrator

**Modified File:** `src/orchestrators/master_orchestrator.py`

```python
from src.middleware.python_best_practices_validator import PythonBestPracticesValidator

class MasterOrchestrator:
    """Master orchestrator with validation middleware."""
    
    def __init__(
        self,
        registry: OrchestratorRegistry,
        router: PatternRouter,
        executor: ExecutionEngine,
        validator: PythonBestPracticesValidator  # NEW
    ):
        self.registry = registry
        self.router = router
        self.executor = executor
        self.validator = validator  # NEW
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Route and execute request with validation."""
        # 1. Pattern matching
        match = self.router.match_pattern(request)
        
        # 2. Load orchestrator
        orchestrator = self.registry.get(match.orchestrator_id)
        
        # 3. VALIDATE ORCHESTRATOR CODE (NEW)
        orchestrator_file = inspect.getfile(orchestrator.__class__)
        validation_result = self.validator.validate_file(orchestrator_file)
        
        if not validation_result.is_valid:
            return {
                "status": "validation_failed",
                "errors": [error.message for error in validation_result.errors],
                "fix_suggestions": [error.fix_suggestion for error in validation_result.errors]
            }
        
        # 4. Execute (only if validation passes)
        result = self.executor.execute(orchestrator, request)
        
        return result
```

---

### 4. Knowledge Library Integration

**Reference Files:**
- `cortex-brain/knowledge-library/standards/python-style-guide.md` (validation rules source)
- `cortex-brain/knowledge-library/architecture/python-architecture-patterns.md` (pattern rules)
- `cortex-brain/knowledge-library/design-patterns/solid-principles.md` (SOLID rules)

**Validation Rules Config:**  
**File:** `cortex-brain/config/validation-rules.yaml`

```yaml
validation_rules:
  pep8:
    enabled: true
    severity: error
    rules:
      - id: PEP8-001
        name: "Indentation must be 4 spaces"
        check: black
      - id: PEP8-002
        name: "Line length ≤100 characters"
        check: black
      - id: PEP8-003
        name: "Import organization (stdlib → third-party → local)"
        check: isort
  
  type_hints:
    enabled: true
    severity: error
    rules:
      - id: TYPE-001
        name: "Public functions must have return type"
        check: mypy
      - id: TYPE-002
        name: "Function parameters must have type annotations"
        check: mypy
  
  docstrings:
    enabled: true
    severity: warning  # Don't block execution, but warn
    rules:
      - id: DOC-001
        name: "Public classes must have docstrings"
        check: pydocstyle
      - id: DOC-002
        name: "Public functions must have docstrings"
        check: pydocstyle
  
  solid:
    enabled: true
    severity: error
    rules:
      - id: SOLID-SRP-001
        name: "Class has ≤3 public methods (SRP)"
        check: ast_analysis
      - id: SOLID-OCP-001
        name: "No if/elif chains >3 for type switching (OCP)"
        check: ast_analysis
      - id: SOLID-LSP-001
        name: "Subclass return type matches parent (LSP)"
        check: mypy
      - id: SOLID-ISP-001
        name: "Protocol has ≤5 methods (ISP)"
        check: ast_analysis
      - id: SOLID-DIP-001
        name: "Depends on ABC/Protocol, not concrete (DIP)"
        check: ast_analysis
  
  code_quality:
    enabled: true
    severity: error
    rules:
      - id: QUALITY-001
        name: "Cyclomatic complexity ≤10"
        check: radon
      - id: QUALITY-002
        name: "Function length ≤50 lines"
        check: ast_analysis
      - id: QUALITY-003
        name: "Class length ≤300 lines"
        check: ast_analysis
  
  cortex_patterns:
    enabled: true
    severity: error
    rules:
      - id: CORTEX-001
        name: "Orchestrators implement OrchestratorInterface"
        check: ast_analysis
      - id: CORTEX-002
        name: "Orchestrators have consistent __init__ signature"
        check: signature_analysis
      - id: CORTEX-003
        name: "State management uses StateStore abstraction"
        check: import_analysis
```

---

## 🚀 Implementation Steps

### Step 1: Create Validation Infrastructure (2 hours)

**Tasks:**
1. Create `src/middleware/` directory
2. Create `validation_result.py` (dataclasses, enums)
3. Create `validation_rules.yaml` config
4. Write unit tests for ValidationResult

**Validation:**
```bash
pytest tests/test_validation_result.py -v
```

---

### Step 2: Implement PEP 8 + Type Hints Validators (2 hours)

**Tasks:**
1. Create `python_best_practices_validator.py`
2. Implement `validate_pep8()` using `black`, `isort`
3. Implement `validate_type_hints()` using `mypy`
4. Write tests with intentionally non-compliant code

**Test Cases:**
- File with tabs → PEP8-001 error
- File with line >100 chars → PEP8-002 error
- Function without return type → TYPE-001 error
- Function with `Any` type → TYPE-002 warning

**Validation:**
```bash
pytest tests/test_pep8_validation.py -v
pytest tests/test_type_hints_validation.py -v
```

---

### Step 3: Implement SOLID + Code Quality Validators (1.5 hours)

**Tasks:**
1. Implement `validate_solid_principles()` using AST analysis
2. Implement `validate_code_quality()` using `radon`
3. Write tests with SOLID violations

**Test Cases:**
- Class with 10 public methods → SOLID-SRP-001 error
- 15 if/elif chain → SOLID-OCP-001 error
- Function with complexity 15 → QUALITY-001 error
- Function with 80 lines → QUALITY-002 error

**Validation:**
```bash
pytest tests/test_solid_validation.py -v
pytest tests/test_quality_validation.py -v
```

---

### Step 4: Implement CORTEX Pattern Validator (1 hour)

**Tasks:**
1. Implement `validate_cortex_patterns()` using import + signature analysis
2. Write tests with pattern violations

**Test Cases:**
- Orchestrator without OrchestratorInterface → CORTEX-001 error
- Orchestrator with inconsistent `__init__` → CORTEX-002 error
- Direct `sqlite3.connect()` usage → CORTEX-003 error

**Validation:**
```bash
pytest tests/test_cortex_patterns_validation.py -v
```

---

### Step 5: Integrate with Master Orchestrator (0.5 hours)

**Tasks:**
1. Update `MasterOrchestrator.__init__()` to accept validator
2. Add validation check before orchestrator execution
3. Test end-to-end (invoke orchestrator with validation)

**Test:**
```bash
python -m src.main "plan API" --validate
```

**Expected Output:**
```
✅ Validation PASSED for planning_v5:
  - PEP 8: 0 errors
  - Type Hints: 0 errors
  - Docstrings: 2 warnings (acceptable)
  - SOLID: 0 errors
  - Code Quality: 0 errors
  - CORTEX Patterns: 0 errors

Executing planning_v5...
```

---

## 📊 Success Criteria

**Must achieve all 6 for phase completion:**

1. ✅ **PEP 8 validator operational** - detects indentation, line length, naming violations
2. ✅ **Type hints validator operational** - detects missing type annotations
3. ✅ **SOLID validator operational** - detects SRP, OCP, LSP, ISP, DIP violations
4. ✅ **Code quality validator operational** - detects complexity, length violations
5. ✅ **CORTEX pattern validator operational** - detects architecture pattern violations
6. ✅ **Integration tested** - Master Orchestrator validates before execution

**Validation Command:**
```bash
python -m pytest tests/test_phase_p01_4_integration.py -v
```

---

## ⚠️ Risks & Mitigations

### Risk 1: Validation overhead slows execution

**Impact:** Orchestrator startup time >1s (unacceptable)  
**Mitigation:** Cache validation results per file (invalidate on file change)  
**Contingency:** Make validation optional via `--skip-validation` flag

### Risk 2: False positives block valid code

**Impact:** Orchestrators fail validation despite being correct  
**Mitigation:** Add exemption mechanism (per-file or per-rule)  
**Contingency:** Downgrade severity to WARNING for problematic rules

### Risk 3: Validation rules conflict with company standards

**Impact:** Company ABC allows 120-char lines, validator enforces 100  
**Mitigation:** Make validation-rules.yaml company-specific (company-knowledge/company_abc/validation-rules.yaml)  
**Contingency:** Global override via environment variable

---

## 📚 References

**Knowledge Library (Validation Sources):**
- `cortex-brain/knowledge-library/standards/python-style-guide.md` (Created 2026-01-07)
- `cortex-brain/knowledge-library/architecture/python-architecture-patterns.md` (Created 2026-01-07)
- `cortex-brain/knowledge-library/design-patterns/solid-principles.md` (Created 2026-01-07)

**Review Documentation:**
- `cortex-brain/documents/planning/active/cortex5-enhancement-epic/reports/cortex-review/20260107_051434_comprehensive_review.yaml`
- Critical Issue ARCH-004: "Python best practices NOT enforced" (line 50)

**Tools:**
- `black` - PEP 8 formatting
- `isort` - Import organization
- `mypy` - Type checking
- `pydocstyle` - Docstring validation
- `radon` - Cyclomatic complexity
- `pylint` - General linting

---

## 🎉 Phase Completion Checklist

Before marking this phase complete, verify:

- [ ] PythonBestPracticesValidator class implemented with all 6 validators
- [ ] ValidationResult dataclass created with severity levels
- [ ] validation-rules.yaml config file created (20+ rules)
- [ ] Integration with MasterOrchestrator complete
- [ ] Unit tests pass (>90% coverage for each validator)
- [ ] Integration tests pass (end-to-end validation workflow)
- [ ] Performance acceptable (<100ms validation overhead)
- [ ] Knowledge library references correct (python-style-guide.md, etc.)
- [ ] Exemption mechanism implemented (for edge cases)
- [ ] Documentation updated (architecture docs, best practices enforcement)

**Approval:** Phase P01.4 complete when all checkboxes ✅

---

## 📈 Impact on Epic Score

**CORTEX Review Score Impact:**

| Metric | Before P01.4 | After P01.4 | Improvement |
|--------|--------------|-------------|-------------|
| **Overall Score** | 72/100 (AT_RISK) | 78/100 (GOOD) | +6 points |
| **ARCH-004 (Critical Issue)** | ❌ Not Enforced | ✅ RESOLVED | Critical → Fixed |
| **Best Practices (Phase 7)** | 70/100 (AT_RISK) | 85/100 (EXCELLENT) | +15 points |
| **Code Quality** | 75/100 (GOOD) | 90/100 (EXCELLENT) | +15 points |

**Prevents Future Issues:**
- INT-001 (Orchestrator instantiation failures) - prevented by CORTEX-002 rule
- ARCH-001 (State management issues) - prevented by CORTEX-003 rule
- MAINT-001 (Interface contract violations) - prevented by CORTEX-001 rule

---

**Phase Owner:** CORTEX Planning System v5  
**Created:** 2026-01-07  
**Status:** 🟢 RECOMMENDED  
**Next:** Phase 2 (Orchestrator Registry System)

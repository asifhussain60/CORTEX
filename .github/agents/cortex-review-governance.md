# CORTEX Review Agent: Governance Compliance
## CORE Rule Verification & Audit Trail Integrity

**Purpose:** Verify compliance with CORE governance rules and detect violations.

---

## CORE RULES CHECKLIST

### CORE-008: Test-Driven Development
**Requirement:** Tests written before code implementation

**Verification:**
```bash
# Find files without tests
find cortex/ -name "*.py" -not -path "*/test*" | while read f; do
  class_name=$(basename "$f" .py)
  test_file="tests/test_$class_name.py"
  if [ ! -f "$test_file" ]; then
    echo "NO TEST: $f"
  fi
done

# Check test timestamps are older than implementation
for test in tests/test_*.py; do
  impl="cortex/$(basename $test test_)"
  if [ -f "$impl" ]; then
    test_date=$(stat -f%Sm -t"%Y%m%d" "$test")
    impl_date=$(stat -f%Sm -t"%Y%m%d" "$impl")
    if [ $test_date -gt $impl_date ]; then
      echo "TEST AFTER CODE: $test"
    fi
  fi
done
```

**What violates CORE-008:**
- Implementation file exists without test file
- Test written after implementation completed
- Tests only cover happy path (not error cases)

---

### CORE-011: Type Hints (100%)
**Requirement:** All function signatures must have type hints

**Verification:**
```bash
# Find functions without type hints
grep -rn "def " cortex/ --include="*.py" | grep -v " -> \|def __" | head -20
```

**What violates CORE-011:**
```python
def process_data(input):  # ← No types!
    return result

def calculate(x, y) -> int:  # ← Parameters untyped
    return x + y
```

**Required format:**
```python
def process_data(input: str) -> Dict[str, Any]:
    return result

def calculate(x: int, y: int) -> int:
    return x + y
```

---

### CORE-012: Docstrings (100% on public APIs)
**Requirement:** All public functions have Google-style docstrings

**Verification:**
```bash
# Find public methods without docstrings
grep -rn "^\s*def [^_]" cortex/ --include="*.py" | grep -v "\"\"\"" | head -20
```

**What violates CORE-012:**
```python
def public_method(self, x: int) -> str:
    return str(x)  # ← No docstring!
```

**Required format:**
```python
def public_method(self, x: int) -> str:
    """Convert integer to string representation.
    
    Args:
        x: Integer value to convert
        
    Returns:
        String representation of the integer
    """
    return str(x)
```

---

### CORE-013: Error Handling
**Requirement:** No bare `except:` clauses; all exceptions must be specific

**Verification:**
```bash
# Find bare except clauses
grep -rn "except:" cortex/ --include="*.py" | grep -v "except.*Error\|except.*Exception"
```

**What violates CORE-013:**
```python
try:
    risky_operation()
except:  # ← Bare except!
    pass
```

**Required format:**
```python
try:
    risky_operation()
except ConnectionError:
    logger.error("Connection failed")
except TimeoutError:
    logger.error("Operation timed out")
```

---

### CORE-025: Hash Chain Integrity
**Requirement:** Cryptographic linkage of audit entries (tamper-evidence)

**Verification:**
```bash
# Check audit logger implementation
grep -rn "previous_hash\|hash_chain" cortex/ --include="*.py"

# Verify test passes
pytest tests/test_audit_trail_integrity.py::test_hash_chain_integrity -v
```

**What violates CORE-025:**
- Audit entries not linked by hash
- No verification of chain on read
- Hash calculation missing or incorrect

---

### CORE-027: Audit Trail Completeness
**Requirement:** All AC activities logged as AC_START → AC_EXECUTE → AC_COMPLETE

**Verification:**
```bash
# Check for all three lifecycle states in tests
grep -rn "AC_START\|AC_EXECUTE\|AC_COMPLETE" tests/ --include="*.py" | wc -l

# Should be balanced: count(START) == count(EXECUTE) == count(COMPLETE)
```

**What violates CORE-027:**
- AC_START logged but no AC_EXECUTE
- AC_EXECUTE without corresponding AC_START
- Missing AC_COMPLETE on success

---

### CORE-028: Naming Conventions
**Requirement:** Kebab-case for file/function names, ≤25 chars

**Verification:**
```bash
# Find snake_case function names (should be kebab)
grep -rn "def .*_.*_.*_.*(" cortex/ --include="*.py" | grep -v "__"

# Find names > 25 characters
find cortex/ -name "*.py" | while read f; do
  len=${#f}
  if [ $len -gt 25 ]; then
    echo "LONG NAME ($len): $f"
  fi
done
```

**What violates CORE-028:**
```python
def process_governance_rule_evaluation_engine_instance():  # ← Too long!
    pass

def process_rule_engine(self):  # ← Snake case (should be kebab elsewhere)
    pass
```

---

## OUTPUT FORMAT

Create: `_workspaces/roadmap/issues/findings-governance-YYYYMMDD.yaml`

```yaml
governance_findings:
  metadata:
    review_date: "YYYYMMDD"
    total_violations: X
    by_core_rule:
      core_008: Y
      core_011: Z
      core_012: A
      core_013: B
      core_025: C
      core_027: D
      core_028: E
    
  critical_violations:
    - violation_id: "GOV-001"
      core_rule: "CORE-008"
      severity: "CRITICAL"
      description: "Module without tests"
      location: "cortex/infrastructure/graceful_degradation.py"
      evidence: "File exists but no test_graceful_degradation.py found"
      impact: "No TDD verification; implementation untested"
      remediation: "Create tests/test_graceful_degradation.py with full coverage"
      
    - violation_id: "GOV-002"
      core_rule: "CORE-011"
      severity: "HIGH"
      description: "Untyped function parameters"
      location: "cortex/brain/tier2/resilience/__init__.py:1000"
      evidence: "def send_alert(message, severity): ← No type hints"
      impact: "Type checking disabled; potential runtime errors"
      remediation: "Add type hints: def send_alert(message: str, severity: AlertSeverity):"
      
    - violation_id: "GOV-003"
      core_rule: "CORE-013"
      severity: "CRITICAL"
      description: "Bare except clause swallowing errors"
      location: "cortex/infrastructure/crash_recovery.py:220"
      evidence: "except:\n    pass"
      impact: "Silent failures; errors undetectable"
      remediation: "Catch specific exceptions; add error logging"
      
    - violation_id: "GOV-004"
      core_rule: "CORE-025"
      severity: "CRITICAL"
      description: "Hash chain test failing"
      location: "cortex/infrastructure/audit_hash_chain.py"
      evidence: "pytest test_hash_chain_integrity.py FAILED"
      impact: "Tamper-evidence broken; audit trail compromised"
      remediation: "Fix hash calculation; verify linkage algorithm"
      
  compliance_summary:
    total_rules: 29
    fully_compliant: X
    partially_compliant: Y
    non_compliant: Z
    compliance_percentage: "X%"
    
  recommendations:
    - "Enable static type checking with mypy (CORE-011 enforcement)"
    - "Add pre-commit hook for docstring validation (CORE-012)"
    - "Scan for bare except clauses before commit (CORE-013)"
    - "Run hash chain integrity test in CI/CD (CORE-025)"
    - "Audit lifecycle test for completeness (CORE-027)"
```

---

## DECISION TREE

```
For each governance check:

Q1: Is code written without test?
  → YES: CRITICAL - CORE-008 violation
  
Q2: Are function parameters untyped?
  → YES: HIGH - CORE-011 violation
  
Q3: Are public APIs undocumented?
  → YES: MEDIUM - CORE-012 violation
  
Q4: Are exceptions caught without type?
  → YES: CRITICAL - CORE-013 violation
  
Q5: Is audit trail incomplete?
  → YES: CRITICAL - CORE-027 violation
  
Q6: Is hash chain broken?
  → YES: CRITICAL - CORE-025 violation (tamper-evidence violated)
```

---

## VALIDATION

Before finalizing findings:
- [ ] Each violation has specific file:line reference
- [ ] Evidence is direct code inspection (not speculation)
- [ ] Remediation includes specific code changes
- [ ] Severity matches impact (CRITICAL = system broken)
- [ ] Rule reference is to actual CORE rule (not made up)

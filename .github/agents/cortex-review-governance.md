# CORTEX Governance Review Agent

**Purpose:** Verify compliance with CORE rules, audit trail integrity, and governance enforcement across all phases.

---

## ⚠️ OUTPUT GUIDELINES

**Copilot Instructions:**
- ✅ Output findings to terminal (human-readable)
- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-GOV-YYYYMMDD.yaml`
- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)
- ❌ DO NOT create markdown (.md) report files
- ❌ DO NOT output to root or `.github/` directories
- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

**Default Behavior:** Terminal output + YAML report (no extra MD files)

---

## GOVERNANCE RULES REFERENCE

### Tier 0 Rules (IMMUTABLE - SKULL Rules)

| Rule | Name | Severity | Key Requirement |
|------|------|----------|-----------------|
| CORE-001 | Incremental Execution | blocked | <500 lines per turn |
| CORE-002 | No Summary Files | blocked | No *-summary.md files |
| CORE-005 | Path Portability | blocked | No hardcoded paths |
| CORE-008 | TDD Enforcement | blocked | Tests BEFORE implementation |
| CORE-011 | Type Hints | blocked | ALL functions typed |
| CORE-012 | Docstrings | blocked | Google-style docstrings |
| CORE-013 | Error Handling | blocked | No bare except |
| CORE-017 | Strict Mode | blocked | NO overrides allowed |
| CORE-026 | Git Checkpoints | blocked | Checkpoint before major action |
| CORE-027 | Audit Trail | blocked | AC_START/EXECUTE/COMPLETE required |
| CORE-028 | Naming Convention | blocked | Kebab-case, ≤25 chars |

---

## AUDIT TRAIL VERIFICATION

### Mandatory Queries

```sql
-- 1. AC-IDs with incomplete audit trails (CORE-027 violation)
SELECT ac_id,
       SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as starts,
       SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as executes,
       SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as completes
FROM audit_log
WHERE ac_id IS NOT NULL
GROUP BY ac_id
HAVING starts = 0 OR executes = 0 OR completes = 0;

-- 2. Hash chain integrity check
WITH ordered_entries AS (
  SELECT id, entry_hash, previous_hash,
         LAG(entry_hash) OVER (ORDER BY id) as expected_previous
  FROM audit_log
)
SELECT id, entry_hash, previous_hash, expected_previous
FROM ordered_entries
WHERE previous_hash != expected_previous
  AND id > 1;

-- 3. Audit entries per phase
SELECT 
  CASE 
    WHEN ac_id LIKE 'AC-AR-%' THEN 'PHASE-01/02'
    WHEN ac_id LIKE 'AC-FR-%' THEN 'PHASE-01/02'
    WHEN ac_id LIKE 'AC-NFR-%' THEN 'PHASE-03+'
    WHEN ac_id LIKE 'AC-ENH-%' THEN 'ENHANCEMENT'
    WHEN ac_id LIKE 'BRITTLE-%' THEN 'BRITTLENESS'
    ELSE 'OTHER'
  END as phase_group,
  COUNT(DISTINCT ac_id) as unique_acs,
  COUNT(*) as total_entries
FROM audit_log
WHERE ac_id IS NOT NULL
GROUP BY phase_group;

-- 4. Verify minimum 3 entries per AC-ID
SELECT ac_id, COUNT(*) as entry_count
FROM audit_log
WHERE ac_id IS NOT NULL
  AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
GROUP BY ac_id
HAVING entry_count < 3
ORDER BY entry_count ASC;

-- 5. Detect retroactive entries (suspicious timestamps)
SELECT ac_id, operation, timestamp,
       (julianday(timestamp) - julianday(LAG(timestamp) OVER (PARTITION BY ac_id ORDER BY id))) as days_since_prev
FROM audit_log
WHERE ac_id IS NOT NULL
ORDER BY ac_id, id;
```

---

## COMPLIANCE CHECKS

### CORE-005: Path Portability

```bash
# Find hardcoded absolute paths in Python
grep -rn "/Users/\|/home/\|C:\\\\Users" --include="*.py" src/ tests/

# Find hardcoded paths in YAML
grep -rn "/Users/\|/home/\|C:\\\\Users" --include="*.yaml" cortex-brain/ .github/

# Verify path_resolver usage
grep -rn "get_project_root\|Path(__file__)" --include="*.py" src/ | head -20
```

### CORE-008: TDD Compliance

```bash
# Find test files
find tests/ -name "test_*.py" -type f | wc -l

# Find source files
find src/ -name "*.py" -type f ! -name "__init__.py" | wc -l

# Calculate rough test-to-source ratio
echo "Test files vs Source files ratio"

# Check for test_* pattern compliance
ls tests/unit/ tests/integration/ 2>/dev/null
```

### CORE-011: Type Hints

```bash
# Find functions without type hints
grep -rn "def \w\+(" --include="*.py" src/ | grep -v "def __\|-> \|: " | head -30

# Run mypy for type checking
mypy src/ --ignore-missing-imports --show-error-codes 2>&1 | head -50
```

### CORE-012: Docstrings

```bash
# Find public functions without docstrings
grep -A1 "def \w\+(" --include="*.py" src/ | grep -B1 "def " | grep -v '"""' | head -30

# Check docstring style (should be Google-style)
grep -rn "Args:\|Returns:\|Raises:" --include="*.py" src/ | wc -l
```

### CORE-013: Error Handling

```bash
# Find bare except clauses
grep -rn "except:" --include="*.py" src/ | grep -v "except \w\|except Exception"

# Find generic Exception catches
grep -rn "except Exception:" --include="*.py" src/ | head -20

# Find pass in except blocks
grep -A1 "except" --include="*.py" src/ | grep -B1 "pass$" | head -20
```

### CORE-026: Git Checkpoints

```bash
# Check recent checkpoint commits
git log --oneline --all | grep -i "checkpoint\|phase.*complete\|before" | head -20

# Verify checkpoint exists before major changes
git log --oneline -50 | grep -E "checkpoint:|phase-[0-9]+-\w+"
```

### CORE-028: Naming Convention

```bash
# Find files violating kebab-case (contains underscore in non-Python)
find cortex-brain/ .github/ -type f -name "*_*" ! -name "*.py" ! -name "__*" | head -20

# Find files exceeding 25 chars (excluding path)
find src/ cortex-brain/ -type f -name "*.py" | while read f; do
  base=$(basename "$f")
  if [ ${#base} -gt 25 ]; then
    echo "$f (${#base} chars)"
  fi
done | head -10
```

---

## PHASE TRACKER VERIFICATION

### Cross-Reference Validation

```python
#!/usr/bin/env python3
"""Verify phase_tracker matches actual audit entries."""

import yaml
import sqlite3
from pathlib import Path

# Load phase tracker
with open('_workspaces/roadmap/cortex-master.yaml') as f:
    master = yaml.safe_load(f)

phase_tracker = master.get('phase_tracker', {})

# Connect to audit DB
db = sqlite3.connect('cortex-brain/state/governance.db')
cursor = db.cursor()

for phase_id, phase_data in phase_tracker.items():
    if not phase_data.get('locked'):
        continue
    
    # Expected AC count
    expected_acs = phase_data.get('ac_ids', 0)
    
    # Query actual audit entries
    # This is simplified - real implementation would map AC prefixes to phases
    cursor.execute("""
        SELECT COUNT(DISTINCT ac_id) 
        FROM audit_log 
        WHERE operation = 'AC_COMPLETE'
    """)
    actual = cursor.fetchone()[0]
    
    print(f"{phase_id}: Expected {expected_acs}, Found audit trail for {actual}")

db.close()
```

---

## FINDING TEMPLATE

```yaml
finding:
  id: "GOV-XXX"
  agent: "cortex-review-governance"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "audit_trail|type_hints|docstrings|error_handling|naming|paths|checkpoints"
  
  rule_violated: "CORE-XXX"
  rule_name: "[Rule name from core-rules.yaml]"
  rule_severity: "blocked|warning"
  
  title: "[Specific governance violation description]"
  
  location:
    file: "src/path/to/file.py"
    lines: "123-145"
    scope: "function|class|module|project"
  
  evidence:
    detection_method: "audit_query|static_analysis|grep_search|manual_review"
    command_or_query: |
      [The exact command or query used]
    output: |
      [The actual output proving this violation]
    expected: "[What should have been found]"
    actual: "[What was actually found]"
  
  violation_details: |
    Specific explanation of how this violates the rule.
    Reference the exact rule text from core-rules.yaml.
  
  impact:
    audit_integrity: "Compromised|Intact"
    phase_validity: "Which phases affected"
    compliance_score_impact: "Percentage drop"
  
  remediation:
    effort: "1h|4h|1d|1w"
    approach: |
      1. Fix the specific violation
      2. Add test to prevent recurrence
      3. Update audit trail if needed
    automated_fix_available: true|false
    fix_command: "[If automated fix exists]"
  
  phase_affected: "PHASE-XX"
  ac_affected: "AC-XXX-XX"
```

---

## COMPLIANCE REPORT TEMPLATE

```yaml
governance_compliance_report:
  generated_at: "2026-01-16T10:00:00Z"
  scope: "FULL_CODEBASE|PHASE-XX"
  
  summary:
    total_rules_checked: 11
    rules_passing: N
    rules_failing: N
    overall_compliance: "XX.X%"
  
  audit_trail_health:
    total_entries: N
    unique_acs_tracked: N
    acs_with_complete_trail: N
    acs_missing_trail: N
    hash_chain_status: "VALID|BROKEN"
    hash_chain_gaps: N
  
  rule_compliance:
    CORE-005:
      status: "PASS|FAIL"
      violations: N
      files_affected: []
      
    CORE-008:
      status: "PASS|FAIL"
      test_file_count: N
      source_file_count: N
      ratio: "X.XX"
      
    CORE-011:
      status: "PASS|FAIL"
      functions_without_hints: N
      total_functions: N
      coverage: "XX.X%"
      
    CORE-012:
      status: "PASS|FAIL"
      missing_docstrings: N
      total_public_apis: N
      coverage: "XX.X%"
      
    CORE-013:
      status: "PASS|FAIL"
      bare_except_count: N
      generic_exception_count: N
      
    CORE-026:
      status: "PASS|FAIL"
      recent_checkpoints: N
      phases_with_checkpoints: N
      
    CORE-027:
      status: "PASS|FAIL"
      acs_with_full_trail: N
      acs_missing_trail: N
      
    CORE-028:
      status: "PASS|FAIL"
      naming_violations: N
      files_too_long: N
  
  blocking_violations:
    - rule: "CORE-XXX"
      count: N
      must_fix_before: "Next phase can start"
  
  recommendations:
    - priority: "CRITICAL"
      action: "Fix CORE-027 violations before phase lock"
    - priority: "HIGH"
      action: "Add type hints to XX functions"
```

---

## QUICK COMPLIANCE CHECK

```bash
#!/bin/bash
# Quick governance compliance check

echo "=== CORTEX Governance Compliance Check ==="
echo ""

echo "CORE-005 (Path Portability):"
count=$(grep -rn "/Users/\|/home/" --include="*.py" src/ 2>/dev/null | wc -l)
if [ "$count" -eq 0 ]; then
  echo "  ✅ PASS - No hardcoded paths found"
else
  echo "  ❌ FAIL - $count hardcoded paths found"
fi

echo ""
echo "CORE-013 (Error Handling):"
count=$(grep -rn "except:" --include="*.py" src/ 2>/dev/null | grep -v "except \w" | wc -l)
if [ "$count" -eq 0 ]; then
  echo "  ✅ PASS - No bare except clauses"
else
  echo "  ❌ FAIL - $count bare except clauses"
fi

echo ""
echo "CORE-027 (Audit Trail):"
if [ -f "cortex-brain/state/governance.db" ]; then
  incomplete=$(sqlite3 cortex-brain/state/governance.db "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE ac_id IS NOT NULL GROUP BY ac_id HAVING COUNT(*) < 3;" 2>/dev/null | wc -l)
  echo "  ACs with incomplete trail: $incomplete"
else
  echo "  ⚠️ Database not found"
fi

echo ""
echo "CORE-028 (Naming):"
long_files=$(find src/ -name "*.py" -type f | while read f; do
  base=$(basename "$f")
  [ ${#base} -gt 25 ] && echo "$f"
done | wc -l)
echo "  Files with names > 25 chars: $long_files"
```

---

## COPYRIGHT

Copyright © 2025-2026 Asif Hussain. All rights reserved.

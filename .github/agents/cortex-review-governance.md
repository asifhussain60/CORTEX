# CORTEX Governance Review Agent# CORTEX Governance Review Agent



**Purpose:** Verify compliance with CORE rules, audit trail integrity, and governance enforcement across all phases.**Purpose:** Verify compliance with CORE rules, audit trail integrity, and governance enforcement across all phases.



**SSOT Source**: `_workspaces/roadmap/cortex-impl-map.yaml` (ONLY implementation map)---



---## ⚠️ OUTPUT GUIDELINES



## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)**Copilot Instructions:**

- ✅ Output findings to terminal (human-readable)

**Unified policy enforced across ALL review agents:**- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-GOV-YYYYMMDD.yaml`

- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)

### Forbidden File Patterns (NO EXCEPTIONS)- ❌ DO NOT create markdown (.md) report files

| What | Why | Action |- ❌ DO NOT output to root or `.github/` directories

|------|-----|--------|- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

| `.md` report files outside `docs/` | SSOT conflict | DELETE IMMEDIATELY |

| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

| Multiple cortex-*.yaml files | Truth conflict | DELETE extra files |

| `.py` scripts in root | Pollution | DELETE at end of session |**Default Behavior:** Terminal output + YAML report (no extra MD files)

| Governance reports as `.md` | Authority confusion | Use YAML only |

---

### ✅ Correct Findings Output Locations

- Primary: `_workspaces/roadmap/issues/Findings-GOV-YYYYMMDD.yaml` (YAML only)## GOVERNANCE RULES REFERENCE

- Documentation: `docs/FILENAME.md` (only if needed for execution)

- Terminal: Default (human-readable compliance report)### Tier 0 Rules (IMMUTABLE - SKULL Rules)



---| Rule | Name | Severity | Key Requirement |

|------|------|----------|-----------------|

## 🎯 VALIDATION CHECKLIST - Before Each Output| CORE-001 | Incremental Execution | blocked | <500 lines per turn |

| CORE-002 | No Summary Files | blocked | No *-summary.md files |

```| CORE-005 | Path Portability | blocked | No hardcoded paths |

BEFORE creating governance findings:| CORE-008 | TDD Enforcement | blocked | Tests BEFORE implementation |

[ ] Creating .md report? → STOP - Use YAML + terminal instead| CORE-011 | Type Hints | blocked | ALL functions typed |

[ ] Creating docs_md/? → STOP - FORBIDDEN| CORE-012 | Docstrings | blocked | Google-style docstrings |

[ ] Multiple cortex-*.yaml? → STOP - SSOT violation| CORE-013 | Error Handling | blocked | No bare except |

[ ] Wrong output locations? → STOP - FIX paths| CORE-017 | Strict Mode | blocked | NO overrides allowed |

[ ] .py files in root? → DELETE before commit| CORE-026 | Git Checkpoints | blocked | Checkpoint before major action |

[ ] Reading from v1/v2/archived YAML? → STOP - Use cortex-impl-map.yaml ONLY| CORE-027 | Audit Trail | blocked | AC_START/EXECUTE/COMPLETE required |

```| CORE-028 | Naming Convention | blocked | Kebab-case, ≤25 chars |



**Red Flag 🚩 = IMMEDIATE ACTION**---

- `.md` governance reports outside `docs/`

- `docs_md/` folder## AUDIT TRAIL VERIFICATION

- Multiple cortex-*.yaml files

- Stray files in root### Mandatory Queries

- References to archived versions

```sql

----- 1. AC-IDs with incomplete audit trails (CORE-027 violation)

SELECT ac_id,

## ⚠️ OUTPUT GUIDELINES       SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as starts,

       SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as executes,

**Copilot Instructions:**       SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as completes

- ✅ Output compliance findings to terminal (human-readable, default)FROM audit_log

- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-GOV-YYYYMMDD.yaml`WHERE ac_id IS NOT NULL

- ✅ Create MD documentation to `docs/` (only if absolutely required)GROUP BY ac_id

- ❌ DO NOT create markdown (.md) report filesHAVING starts = 0 OR executes = 0 OR completes = 0;

- ❌ DO NOT output to root or `.github/` directories

- ❌ DO NOT create `docs_md/` folder-- 2. Hash chain integrity check

- ❌ NEVER leave `.py` scripts in rootWITH ordered_entries AS (

- ❌ NEVER read from archived/old YAML versions  SELECT id, entry_hash, previous_hash,

         LAG(entry_hash) OVER (ORDER BY id) as expected_previous

**Default Behavior:** Terminal output + optional YAML findings  FROM audit_log

)

---SELECT id, entry_hash, previous_hash, expected_previous

FROM ordered_entries

## GOVERNANCE RULES REFERENCEWHERE previous_hash != expected_previous

  AND id > 1;

### Tier 0 Rules (IMMUTABLE - Non-Negotiable)

-- 3. Audit entries per phase

| Rule | Name | Severity | Key Requirement |SELECT 

|------|------|----------|-----------------|  CASE 

| CORE-001 | Incremental Execution | blocked | <500 lines per turn |    WHEN ac_id LIKE 'AC-AR-%' THEN 'PHASE-01/02'

| CORE-002 | No Summary Files | blocked | No *-summary.md files |    WHEN ac_id LIKE 'AC-FR-%' THEN 'PHASE-01/02'

| CORE-005 | Path Portability | blocked | No hardcoded paths |    WHEN ac_id LIKE 'AC-NFR-%' THEN 'PHASE-03+'

| CORE-008 | TDD Enforcement | blocked | Tests BEFORE implementation |    WHEN ac_id LIKE 'AC-ENH-%' THEN 'ENHANCEMENT'

| CORE-011 | Type Hints | blocked | ALL functions typed |    WHEN ac_id LIKE 'BRITTLE-%' THEN 'BRITTLENESS'

| CORE-012 | Docstrings | blocked | Google-style docstrings |    ELSE 'OTHER'

| CORE-013 | Error Handling | blocked | No bare except |  END as phase_group,

| CORE-017 | Strict Mode | blocked | NO overrides allowed |  COUNT(DISTINCT ac_id) as unique_acs,

| CORE-026 | Git Checkpoints | blocked | Checkpoint before major action |  COUNT(*) as total_entries

| CORE-027 | Audit Trail | blocked | AC_START/EXECUTE/COMPLETE required |FROM audit_log

| CORE-028 | Naming Convention | blocked | Kebab-case, ≤25 chars |WHERE ac_id IS NOT NULL

GROUP BY phase_group;

---

-- 4. Verify minimum 3 entries per AC-ID

## AUDIT TRAIL VERIFICATIONSELECT ac_id, COUNT(*) as entry_count

FROM audit_log

### Mandatory QueriesWHERE ac_id IS NOT NULL

  AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')

```sqlGROUP BY ac_id

-- 1. AC-IDs with incomplete audit trails (CORE-027 violation)HAVING entry_count < 3

SELECT ac_id,ORDER BY entry_count ASC;

       SUM(CASE WHEN operation = 'AC_START' THEN 1 ELSE 0 END) as starts,

       SUM(CASE WHEN operation = 'AC_EXECUTE' THEN 1 ELSE 0 END) as executes,-- 5. Detect retroactive entries (suspicious timestamps)

       SUM(CASE WHEN operation = 'AC_COMPLETE' THEN 1 ELSE 0 END) as completesSELECT ac_id, operation, timestamp,

FROM audit_log       (julianday(timestamp) - julianday(LAG(timestamp) OVER (PARTITION BY ac_id ORDER BY id))) as days_since_prev

WHERE ac_id IS NOT NULLFROM audit_log

GROUP BY ac_idWHERE ac_id IS NOT NULL

HAVING starts = 0 OR executes = 0 OR completes = 0;ORDER BY ac_id, id;

```

-- 2. Hash chain integrity check

WITH ordered_entries AS (---

  SELECT id, entry_hash, previous_hash,

         LAG(entry_hash) OVER (ORDER BY id) as expected_previous## COMPLIANCE CHECKS

  FROM audit_log

)### CORE-005: Path Portability

SELECT id, entry_hash, previous_hash, expected_previous

FROM ordered_entries```bash

WHERE previous_hash != expected_previous# Find hardcoded absolute paths in Python

  AND id > 1;grep -rn "/Users/\|/home/\|C:\\\\Users" --include="*.py" src/ tests/



-- 3. Audit entries per phase# Find hardcoded paths in YAML

SELECT grep -rn "/Users/\|/home/\|C:\\\\Users" --include="*.yaml" cortex_brain/ .github/

  CASE 

    WHEN ac_id LIKE 'AC-AR-%' THEN 'PHASE-01/02'# Verify path_resolver usage

    WHEN ac_id LIKE 'AC-FR-%' THEN 'PHASE-01/02'grep -rn "get_project_root\|Path(__file__)" --include="*.py" src/ | head -20

    WHEN ac_id LIKE 'AC-NFR-%' THEN 'PHASE-03+'```

    WHEN ac_id LIKE 'AC-ENH-%' THEN 'ENHANCEMENT'

    WHEN ac_id LIKE 'BRITTLE-%' THEN 'BRITTLENESS'### CORE-008: TDD Compliance

    ELSE 'OTHER'

  END as phase_group,```bash

  COUNT(DISTINCT ac_id) as unique_acs,# Find test files

  COUNT(*) as total_entriesfind tests/ -name "test_*.py" -type f | wc -l

FROM audit_log

WHERE ac_id IS NOT NULL# Find source files

GROUP BY phase_group;find src/ -name "*.py" -type f ! -name "__init__.py" | wc -l



-- 4. Verify minimum 3 entries per AC-ID# Calculate rough test-to-source ratio

SELECT ac_id, COUNT(*) as entry_countecho "Test files vs Source files ratio"

FROM audit_log

WHERE ac_id IS NOT NULL# Check for test_* pattern compliance

  AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')ls tests/unit/ tests/integration/ 2>/dev/null

GROUP BY ac_id```

HAVING entry_count < 3

ORDER BY entry_count ASC;### CORE-011: Type Hints



-- 5. Detect retroactive entries (suspicious timestamps)```bash

SELECT ac_id, operation, timestamp,# Find functions without type hints

       (julianday(timestamp) - julianday(LAG(timestamp) OVER (PARTITION BY ac_id ORDER BY id))) as days_since_prevgrep -rn "def \w\+(" --include="*.py" src/ | grep -v "def __\|-> \|: " | head -30

FROM audit_log

WHERE ac_id IS NOT NULL# Run mypy for type checking

ORDER BY ac_id, id;mypy src/ --ignore-missing-imports --show-error-codes 2>&1 | head -50

``````



---### CORE-012: Docstrings



## COMPLIANCE CHECK PROCEDURES```bash

# Find public functions without docstrings

### Procedure 1: Phase Governance Statusgrep -A1 "def \w\+(" --include="*.py" src/ | grep -B1 "def " | grep -v '"""' | head -30



1. Query `phase_tracker` from `_workspaces/roadmap/cortex-impl-map.yaml`# Check docstring style (should be Google-style)

2. For each phase, verify:grep -rn "Args:\|Returns:\|Raises:" --include="*.py" src/ | wc -l

   - All AC-IDs marked COMPLETED```

   - Audit trail has 3+ entries per AC

   - No CORE rule violations in implementation### CORE-013: Error Handling

3. Generate compliance % per phase

```bash

### Procedure 2: CORE Rule Enforcement# Find bare except clauses

grep -rn "except:" --include="*.py" src/ | grep -v "except \w\|except Exception"

1. Load `cortex_brain/tier0/governance/core-rules.yaml` (28 rules)

2. For each active phase, verify:# Find generic Exception catches

   - Relevant CORE rules enforcedgrep -rn "except Exception:" --include="*.py" src/ | head -20

   - No violations in implemented code

   - Audit log documents rule checks# Find pass in except blocks

3. List violations by severitygrep -A1 "except" --include="*.py" src/ | grep -B1 "pass$" | head -20

```

### Procedure 3: AC-ID Validation

### CORE-026: Git Checkpoints

1. For each unlocked AC-ID:

   - Verify implementation code exists```bash

   - Check test coverage > 90%# Check recent checkpoint commits

   - Verify docstrings (CORE-012)git log --oneline --all | grep -i "checkpoint\|phase.*complete\|before" | head -20

   - Verify type hints (CORE-011)

   - Verify error handling (CORE-013)# Verify checkpoint exists before major changes

   - Check audit trail (CORE-027)git log --oneline -50 | grep -E "checkpoint:|phase-[0-9]+-\w+"

2. Generate AC completion report```



---### CORE-028: Naming Convention



## Governance Severity Levels```bash

# Find files violating kebab-case (contains underscore in non-Python)

| Level | Definition | Action |find cortex_brain/ .github/ -type f -name "*_*" ! -name "*.py" ! -name "__*" | head -20

|-------|-----------|--------|

| BLOCKED | CORE rule violation | Immediate escalation |# Find files exceeding 25 chars (excluding path)

| CRITICAL | Governance failure | Fix before next phase |find src/ cortex_brain/ -type f -name "*.py" | while read f; do

| HIGH | Compliance gap | Fix in this phase |  base=$(basename "$f")

| MEDIUM | Minor violation | Address when possible |  if [ ${#base} -gt 25 ]; then

| LOW | Best practice gap | Monitor for trends |    echo "$f (${#base} chars)"

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
with open('_workspaces/roadmap/cortex-impl-map.yaml') as f:
    master = yaml.safe_load(f)

phase_tracker = master.get('phase_tracker', {})

# Connect to audit DB
db = sqlite3.connect('cortex_brain/state/governance.db')
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
if [ -f "cortex_brain/state/governance.db" ]; then
  incomplete=$(sqlite3 cortex_brain/state/governance.db "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE ac_id IS NOT NULL GROUP BY ac_id HAVING COUNT(*) < 3;" 2>/dev/null | wc -l)
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

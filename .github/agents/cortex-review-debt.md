# CORTEX Technical Debt Review Agent# CORTEX Technical Debt Review Agent



**Purpose:** Identify accumulated technical debt, deferred decisions, duplicated patterns, and opportunities for simplification.**Purpose:** Identify accumulated technical debt, deferred decisions, duplicated patterns, and opportunities for simplification.



**SSOT Source**: `_workspaces/roadmap/cortex-impl-map.yaml` (ONLY implementation map)---



---## ⚠️ OUTPUT GUIDELINES



## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT SSOT CONFLICTS)**Copilot Instructions:**

- ✅ Output findings to terminal (human-readable)

**Unified policy enforced across ALL review agents:**- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-DEBT-YYYYMMDD.yaml`

- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)

### Forbidden File Patterns (ZERO TOLERANCE)- ❌ DO NOT create markdown (.md) report files

| What | Why | Action |- ❌ DO NOT output to root or `.github/` directories

|------|-----|--------|- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

| `.md` report files outside `docs/` | SSOT conflict | DELETE IMMEDIATELY |

| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

| Multiple cortex-*.yaml files | Truth conflict | DELETE extra files |

| `.py` scripts in root | Pollution | DELETE at end of session |**Default Behavior:** Terminal output + YAML report (no extra MD files)

| Mixed YAML/MD findings | Authority confusion | Use YAML only for reports |

---

### ✅ Correct Findings Output Locations

- Primary: `_workspaces/roadmap/issues/Findings-DEBT-YYYYMMDD.yaml` (YAML only)## DEBT CATEGORIES

- Documentation: `docs/FILENAME.md` (only if needed for execution)

- Terminal: Default (human-readable analysis)### Category 1: Code Duplication



---**Detection Commands:**

```bash

## 🎯 VALIDATION CHECKLIST - Before Each Output# Find similar function names (potential duplication)

grep -rh "def \w\+" --include="*.py" src/ | sort | uniq -c | sort -rn | head -20

```

BEFORE creating debt findings:# Find copy-paste patterns (identical blocks)

[ ] Creating .md report? → STOP - Use YAML + terminal instead# Use a proper tool like jscpd or pylint

[ ] Creating docs_md/? → STOP - FORBIDDENpylint --disable=all --enable=duplicate-code src/ 2>&1 | head -50

[ ] Multiple cortex-*.yaml? → STOP - SSOT violation

[ ] Wrong output locations? → STOP - FIX paths# Find multiple implementations of same interface

[ ] .py scripts in root? → DELETE before commitgrep -rn "class.*IAudit\|class.*Logger\|class.*Handler" --include="*.py" src/

``````



**Red Flag 🚩 = FIX IMMEDIATELY****What to Flag:**

- `.md` findings outside `docs/`- Same logic in multiple files — HIGH

- `docs_md/` folder created- Copy-paste with minor variations — MEDIUM

- Multiple cortex-*.yaml in use- Multiple implementations without interface — HIGH

- Stray files in root- Redundant utility functions — LOW



---### Category 2: Missing Abstractions



## ⚠️ OUTPUT GUIDELINES**Detection Commands:**

```bash

**Copilot Instructions:**# Find long functions (>50 lines)

- ✅ Output findings to terminal (human-readable, default)grep -n "def " --include="*.py" src/ | while read line; do

- ✅ Create YAML findings to `_workspaces/roadmap/issues/Findings-DEBT-YYYYMMDD.yaml`  file=$(echo $line | cut -d: -f1)

- ✅ Create MD documentation to `docs/` (only if absolutely required)  linenum=$(echo $line | cut -d: -f2)

- ❌ DO NOT create markdown (.md) report files  # Complex to detect, use static analysis tools

- ❌ DO NOT output to root or `.github/` directoriesdone

- ❌ DO NOT create `docs_md/` folder

- ❌ NEVER leave `.py` scripts in root# Find repeated parameter patterns

grep -rn "def .*db_path.*config" --include="*.py" src/

**Default Behavior:** Terminal output + optional YAML findings

# Find God classes (too many methods)

---grep -c "def " src/**/*.py 2>/dev/null | awk -F: '$2 > 20 {print}'

```

## DEBT CATEGORIES

**What to Flag:**

### Category 1: Code Duplication- Functions over 50 lines — MEDIUM

- Classes with 20+ methods — HIGH

**Detection Commands:**- Repeated parameter groups — MEDIUM

```bash- No clear separation of concerns — HIGH

# Find similar function names (potential duplication)

grep -rh "def \w\+" --include="*.py" src/ | sort | uniq -c | sort -rn | head -20### Category 3: Deprecated Patterns



# Find copy-paste patterns (identical blocks)**Detection Commands:**

# Use a proper tool like jscpd or pylint```bash

pylint --disable=all --enable=duplicate-code src/ 2>&1 | head -50# Find TODO/FIXME/HACK/XXX comments

grep -rn "TODO\|FIXME\|HACK\|XXX\|DEPRECATED" --include="*.py" src/

# Find multiple implementations of same interface

grep -rn "class.*IAudit\|class.*Logger\|class.*Handler" --include="*.py" src/# Find old-style string formatting

```grep -rn "% s\|%d\|%f\|\.format(" --include="*.py" src/ | grep -v "logging\|f\"" | head -20



**What to Flag:**# Find deprecated stdlib usage

- Same logic in multiple files — HIGHgrep -rn "optparse\|imp\.\|asyncore\|asynchat" --include="*.py" src/

- Copy-paste with minor variations — MEDIUM```

- Multiple implementations without interface — HIGH

- Redundant utility functions — LOW**What to Flag:**

- TODO comments over 30 days old — MEDIUM

### Category 2: Missing Abstractions- FIXME without issue reference — MEDIUM

- HACK comments (known shortcuts) — HIGH

**Detection Commands:**- Deprecated stdlib modules — HIGH

```bash

# Find long functions (>50 lines)### Category 4: Over-Engineering

grep -n "def " --include="*.py" src/ | while read line; do

  file=$(echo $line | cut -d: -f1)**Detection Commands:**

  linenum=$(echo $line | cut -d: -f2)```bash

  # Complex to detect, use static analysis tools# Find unnecessary abstractions (1 implementation)

done# Interfaces with single implementor

grep -rn "class I[A-Z]\w\+\|Protocol\):" --include="*.py" src/ | while read interface; do

# Find repeated parameter patterns  name=$(echo $interface | grep -o "I[A-Z]\w\+\|class \w\+Protocol" | head -1)

grep -rn "def .*db_path.*config" --include="*.py" src/  # Check for implementations

done

# Find God classes (too many methods)

grep -c "def " src/**/*.py 2>/dev/null | awk -F: '$2 > 20 {print}'# Find deeply nested code

```# Use complexity analysis tools

radon cc src/ -a -nc 2>&1 | head -30

**What to Flag:**

- Functions over 50 lines — MEDIUM# Find unused parameters

- Classes with 20+ methods — HIGHpylint --disable=all --enable=unused-argument src/ 2>&1 | head -30

- Repeated parameter groups — MEDIUM```

- No clear separation of concerns — HIGH

**What to Flag:**

### Category 3: Deprecated Patterns- Abstract classes with single implementation — LOW

- Cyclomatic complexity > 10 — HIGH

**Detection Commands:**- Inheritance depth > 3 — MEDIUM

```bash- Unused parameters — LOW

# Find TODO/FIXME/HACK/XXX comments

grep -rn "TODO\|FIXME\|HACK\|XXX\|DEPRECATED" --include="*.py" src/### Category 5: Under-Engineering



# Find old-style string formatting**Detection Commands:**

grep -rn "% s\|%d\|%f\|\.format(" --include="*.py" src/ | grep -v "logging\|f\"" | head -20```bash

# Find magic numbers

# Find deprecated stdlib usagegrep -rn "[^a-zA-Z_][0-9]\{3,\}[^a-zA-Z_]" --include="*.py" src/ | grep -v "test\|0x\|port\|version"

grep -rn "optparse\|imp\.\|asyncore\|asynchat" --include="*.py" src/

```# Find hardcoded strings (should be constants)

grep -rn '"\w\{10,\}"' --include="*.py" src/ | grep -v "docstring\|import\|test"

**What to Flag:**

- TODO comments over 30 days old — MEDIUM# Find missing validation

- FIXME without issue reference — MEDIUMgrep -rn "def \w\+(.*:" --include="*.py" src/ | head -50

- HACK comments (known shortcuts) — HIGH# Then check which lack input validation

- Deprecated stdlib modules — HIGH```



### Category 4: Over-Engineering**What to Flag:**

- Magic numbers without names — MEDIUM

**Detection Commands:**- Hardcoded strings that should be configurable — MEDIUM

```bash- Missing input validation — HIGH

# Find unnecessary abstractions (1 implementation)- No error messages (just raise) — LOW

# Interfaces with single implementor

grep -rn "class I[A-Z]\w\+\|Protocol\):" --include="*.py" src/ | while read interface; do### Category 6: Documentation Drift

  name=$(echo $interface | grep -o "I[A-Z]\w\+\|class \w\+Protocol" | head -1)

  # Check for implementations**Detection Commands:**

done```bash

# Compare docstrings to implementation

# Find unused dependencies# Complex - use tools or manual review

grep -rn "^import\|^from" --include="*.py" src/ > /tmp/imports.txt

grep -o "^[a-z_]*" /tmp/imports.txt | sort -u > /tmp/imported_modules.txt# Find outdated comments

git log --oneline --all --follow src/ | head -20

# Find unused classes/functions# Then compare comment dates to code change dates

grep -rn "^class\|^def" --include="*.py" src/ > /tmp/definitions.txt

```# Find README inconsistencies

diff <(grep "## " README.md) <(ls -1 src/)

**What to Flag:**```

- Interfaces with single implementation — MEDIUM

- Unused imports — LOW**What to Flag:**

- Unused functions/classes — MEDIUM- Docstrings mentioning removed parameters — HIGH

- Excessive inheritance hierarchies — HIGH- README features not implemented — HIGH

- Comments describing old behavior — MEDIUM

### Category 5: Configuration Debt- Missing changelog entries — LOW



**Detection Commands:**### Category 7: Test Debt

```bash

# Find hardcoded values that should be config**Detection Commands:**

grep -rn "=['\"].*['\"]" --include="*.py" src/ | grep -E "path|url|host|port|key" | head -30```bash

# Find untested code paths

# Find inconsistent config patternspytest --cov=src --cov-report=term-missing 2>&1 | grep "TOTAL\|Missing"

grep -rn "os.getenv\|os.environ\|config\[" --include="*.py" src/ | head -20

# Find tests without assertions

# Find missing config docsgrep -rn "def test_" --include="*.py" tests/ | while read test; do

ls -la *.ini *.yaml *.json *.toml 2>/dev/null  file=$(echo $test | cut -d: -f1)

```  linenum=$(echo $test | cut -d: -f2)

  # Check for assert in next 50 lines

**What to Flag:**done

- Hardcoded paths/URLs — MEDIUM

- Inconsistent config access — MEDIUM# Find skipped tests

- Missing config documentation — LOWgrep -rn "@pytest.mark.skip\|pytest.skip\|@unittest.skip" --include="*.py" tests/

- Config not validated — MEDIUM```



### Category 6: Documentation Debt**What to Flag:**

- Coverage below 80% — HIGH

**Detection Commands:**- Tests without assertions — CRITICAL

```bash- Permanently skipped tests — MEDIUM

# Find missing docstrings (CORE-012 violation)- Flaky tests — HIGH

grep -rn "^def\|^class" --include="*.py" src/ | wc -l

grep -rn "\"\"\"" --include="*.py" src/ | wc -l---



# Find outdated documentation## FINDING TEMPLATE

grep -rn "TODO\|FIXME\|XXX" docs/ | head -20

```yaml

# Find missing type hints (CORE-011 violation)finding:

grep -rn "def.*:" --include="*.py" src/ | grep -v " ->" | head -20  id: "DEBT-XXX"

```  agent: "cortex-review-debt"

  severity: "CRITICAL|HIGH|MEDIUM|LOW"

**What to Flag:**  category: "duplication|abstraction|deprecated|over_engineering|under_engineering|documentation|test"

- Missing docstrings — HIGH  

- Outdated docs — MEDIUM  title: "[Specific technical debt description]"

- Missing type hints — HIGH  

- Inconsistent doc format — MEDIUM  location:

    files: 

---      - "src/path/to/file1.py"

      - "src/path/to/file2.py"

## Debt Severity Levels    scope: "function|class|module|pattern"

  

| Level | Definition | Impact |  evidence:

|-------|-----------|--------|    detection_method: "static_analysis|code_review|test_coverage|git_history"

| CRITICAL | Blocks future development | Fix immediately |    tool_used: "pylint|radon|pytest-cov|manual"

| HIGH | Increases maintenance cost | Fix in next phase |    output: |

| MEDIUM | Reduces code clarity | Fix when convenient |      [Tool output or code snippets]

| LOW | Minor inconsistency | Monitor and address later |  

  debt_description: |
    What the debt is.
    When it was introduced (if known).
    Why it exists (historical reason).
  
  debt_cost:
    maintenance_overhead: "Hours per month spent working around this"
    bug_risk: "Likelihood of bugs from this debt"
    onboarding_impact: "How this affects new developers"
  
  interest_accumulation: |
    How this debt grows worse over time.
    What becomes harder the longer it exists.
  
  refactoring_opportunity: |
    What clean solution would look like.
    What patterns should be applied.
  
  remediation:
    effort: "1h|4h|1d|1w|2w"
    approach: |
      1. Create abstraction for [pattern]
      2. Consolidate duplicates into [location]
      3. Add tests for [coverage gap]
      4. Update documentation
    dependencies: "Must complete [other work] first"
    risk: "Breaking changes to [components]"
  
  priority_factors:
    affects_critical_path: true|false
    blocks_new_features: true|false
    causes_recurring_bugs: true|false
    developer_pain_point: true|false
```

---

## DEBT METRICS DASHBOARD

```yaml
technical_debt_summary:
  generated_at: "2026-01-16T10:00:00Z"
  
  code_quality_metrics:
    test_coverage: "XX%"
    cyclomatic_complexity_avg: X.X
    maintainability_index: XX
    duplicate_code_percentage: "X%"
  
  debt_by_category:
    duplication:
      findings: N
      estimated_fix_hours: N
    abstraction:
      findings: N
      estimated_fix_hours: N
    deprecated:
      findings: N
      estimated_fix_hours: N
    test_debt:
      findings: N
      estimated_fix_hours: N
  
  debt_velocity:
    new_debt_this_month: N
    debt_paid_this_month: N
    net_debt_change: "+N or -N"
  
  quick_wins:
    - description: "Remove 5 TODO comments with fixes"
      effort: "2h"
      impact: "Removes 5 MEDIUM findings"
    - description: "Consolidate 3 duplicate utilities"
      effort: "4h"
      impact: "Removes 3 HIGH findings"
  
  recommended_focus_areas:
    - area: "Test coverage for src/orchestrators/"
      current: "65%"
      target: "80%"
      effort: "8h"
```

---

## QUICK DEBT AUDIT SCRIPT

```python
#!/usr/bin/env python3
"""Quick technical debt audit for CORTEX."""

import subprocess
import os
from pathlib import Path

def count_todo_fixme():
    """Count TODO/FIXME comments."""
    result = subprocess.run(
        ["grep", "-rn", "TODO\\|FIXME\\|HACK\\|XXX", "--include=*.py", "src/"],
        capture_output=True, text=True
    )
    lines = [l for l in result.stdout.split('\n') if l]
    
    by_type = {
        "TODO": len([l for l in lines if "TODO" in l]),
        "FIXME": len([l for l in lines if "FIXME" in l]),
        "HACK": len([l for l in lines if "HACK" in l]),
        "XXX": len([l for l in lines if "XXX" in l]),
    }
    
    return {
        "check": "todo_fixme",
        "total": len(lines),
        "by_type": by_type,
        "details": lines[:10]
    }

def check_function_length():
    """Estimate long functions (rough heuristic)."""
    long_functions = []
    for pyfile in Path("src").rglob("*.py"):
        try:
            content = pyfile.read_text()
            lines = content.split('\n')
            current_func = None
            func_start = 0
            
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    if current_func and (i - func_start) > 50:
                        long_functions.append({
                            "file": str(pyfile),
                            "function": current_func,
                            "lines": i - func_start
                        })
                    current_func = line.strip().split("(")[0].replace("def ", "")
                    func_start = i
        except Exception:
            pass
    
    return {
        "check": "long_functions",
        "functions_over_50_lines": len(long_functions),
        "details": long_functions[:10]
    }

def check_test_skips():
    """Find skipped tests."""
    result = subprocess.run(
        ["grep", "-rn", "@pytest.mark.skip\\|pytest.skip\\|@skip", "--include=*.py", "tests/"],
        capture_output=True, text=True
    )
    lines = [l for l in result.stdout.split('\n') if l]
    
    return {
        "check": "skipped_tests",
        "count": len(lines),
        "details": lines[:10]
    }

if __name__ == "__main__":
    import json
    
    checks = [
        count_todo_fixme(),
        check_function_length(),
        check_test_skips(),
    ]
    
    print(json.dumps({"debt_audit": checks}, indent=2))
```

---

## DEBT PRIORITIZATION MATRIX

| Factor | Weight | Description |
|--------|--------|-------------|
| Bug Risk | 3x | Debt that causes/enables bugs |
| Feature Block | 3x | Debt that blocks new features |
| Developer Pain | 2x | Debt that slows daily work |
| Maintenance Cost | 2x | Debt that increases ongoing work |
| Code Clarity | 1x | Debt that makes code hard to understand |

**Priority Score = Σ(Factor Weight × Factor Score)**

- Score 15+: CRITICAL — Fix in current sprint
- Score 10-14: HIGH — Fix within 2 weeks
- Score 5-9: MEDIUM — Plan for next quarter
- Score 1-4: LOW — Track, fix opportunistically

---

## COPYRIGHT

Copyright © 2025-2026 Asif Hussain. All rights reserved.

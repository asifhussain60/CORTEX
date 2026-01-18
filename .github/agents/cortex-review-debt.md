# CORTEX Technical Debt Review Agent

**Purpose:** Identify accumulated technical debt, deferred decisions, duplicated patterns, and opportunities for simplification.

---

## ⚠️ OUTPUT GUIDELINES

**Copilot Instructions:**
- ✅ Output findings to terminal (human-readable)
- ✅ Create YAML report to `_workspaces/roadmap/issues/Findings-DEBT-YYYYMMDD.yaml`
- ✅ If creating MD documentation, path MUST be: `docs/FILENAME.md` (only if absolutely required)
- ❌ DO NOT create markdown (.md) report files
- ❌ DO NOT output to root or `.github/` directories
- ❌ DO NOT create `docs_md/` folder (FORBIDDEN - all docs go to `docs/`)

**CRITICAL:** If you see code creating `docs_md/` folder: STOP and FIX IMMEDIATELY

**Default Behavior:** Terminal output + YAML report (no extra MD files)

---

## DEBT CATEGORIES

### Category 1: Code Duplication

**Detection Commands:**
```bash
# Find similar function names (potential duplication)
grep -rh "def \w\+" --include="*.py" src/ | sort | uniq -c | sort -rn | head -20

# Find copy-paste patterns (identical blocks)
# Use a proper tool like jscpd or pylint
pylint --disable=all --enable=duplicate-code src/ 2>&1 | head -50

# Find multiple implementations of same interface
grep -rn "class.*IAudit\|class.*Logger\|class.*Handler" --include="*.py" src/
```

**What to Flag:**
- Same logic in multiple files — HIGH
- Copy-paste with minor variations — MEDIUM
- Multiple implementations without interface — HIGH
- Redundant utility functions — LOW

### Category 2: Missing Abstractions

**Detection Commands:**
```bash
# Find long functions (>50 lines)
grep -n "def " --include="*.py" src/ | while read line; do
  file=$(echo $line | cut -d: -f1)
  linenum=$(echo $line | cut -d: -f2)
  # Complex to detect, use static analysis tools
done

# Find repeated parameter patterns
grep -rn "def .*db_path.*config" --include="*.py" src/

# Find God classes (too many methods)
grep -c "def " src/**/*.py 2>/dev/null | awk -F: '$2 > 20 {print}'
```

**What to Flag:**
- Functions over 50 lines — MEDIUM
- Classes with 20+ methods — HIGH
- Repeated parameter groups — MEDIUM
- No clear separation of concerns — HIGH

### Category 3: Deprecated Patterns

**Detection Commands:**
```bash
# Find TODO/FIXME/HACK/XXX comments
grep -rn "TODO\|FIXME\|HACK\|XXX\|DEPRECATED" --include="*.py" src/

# Find old-style string formatting
grep -rn "% s\|%d\|%f\|\.format(" --include="*.py" src/ | grep -v "logging\|f\"" | head -20

# Find deprecated stdlib usage
grep -rn "optparse\|imp\.\|asyncore\|asynchat" --include="*.py" src/
```

**What to Flag:**
- TODO comments over 30 days old — MEDIUM
- FIXME without issue reference — MEDIUM
- HACK comments (known shortcuts) — HIGH
- Deprecated stdlib modules — HIGH

### Category 4: Over-Engineering

**Detection Commands:**
```bash
# Find unnecessary abstractions (1 implementation)
# Interfaces with single implementor
grep -rn "class I[A-Z]\w\+\|Protocol\):" --include="*.py" src/ | while read interface; do
  name=$(echo $interface | grep -o "I[A-Z]\w\+\|class \w\+Protocol" | head -1)
  # Check for implementations
done

# Find deeply nested code
# Use complexity analysis tools
radon cc src/ -a -nc 2>&1 | head -30

# Find unused parameters
pylint --disable=all --enable=unused-argument src/ 2>&1 | head -30
```

**What to Flag:**
- Abstract classes with single implementation — LOW
- Cyclomatic complexity > 10 — HIGH
- Inheritance depth > 3 — MEDIUM
- Unused parameters — LOW

### Category 5: Under-Engineering

**Detection Commands:**
```bash
# Find magic numbers
grep -rn "[^a-zA-Z_][0-9]\{3,\}[^a-zA-Z_]" --include="*.py" src/ | grep -v "test\|0x\|port\|version"

# Find hardcoded strings (should be constants)
grep -rn '"\w\{10,\}"' --include="*.py" src/ | grep -v "docstring\|import\|test"

# Find missing validation
grep -rn "def \w\+(.*:" --include="*.py" src/ | head -50
# Then check which lack input validation
```

**What to Flag:**
- Magic numbers without names — MEDIUM
- Hardcoded strings that should be configurable — MEDIUM
- Missing input validation — HIGH
- No error messages (just raise) — LOW

### Category 6: Documentation Drift

**Detection Commands:**
```bash
# Compare docstrings to implementation
# Complex - use tools or manual review

# Find outdated comments
git log --oneline --all --follow src/ | head -20
# Then compare comment dates to code change dates

# Find README inconsistencies
diff <(grep "## " README.md) <(ls -1 src/)
```

**What to Flag:**
- Docstrings mentioning removed parameters — HIGH
- README features not implemented — HIGH
- Comments describing old behavior — MEDIUM
- Missing changelog entries — LOW

### Category 7: Test Debt

**Detection Commands:**
```bash
# Find untested code paths
pytest --cov=src --cov-report=term-missing 2>&1 | grep "TOTAL\|Missing"

# Find tests without assertions
grep -rn "def test_" --include="*.py" tests/ | while read test; do
  file=$(echo $test | cut -d: -f1)
  linenum=$(echo $test | cut -d: -f2)
  # Check for assert in next 50 lines
done

# Find skipped tests
grep -rn "@pytest.mark.skip\|pytest.skip\|@unittest.skip" --include="*.py" tests/
```

**What to Flag:**
- Coverage below 80% — HIGH
- Tests without assertions — CRITICAL
- Permanently skipped tests — MEDIUM
- Flaky tests — HIGH

---

## FINDING TEMPLATE

```yaml
finding:
  id: "DEBT-XXX"
  agent: "cortex-review-debt"
  severity: "CRITICAL|HIGH|MEDIUM|LOW"
  category: "duplication|abstraction|deprecated|over_engineering|under_engineering|documentation|test"
  
  title: "[Specific technical debt description]"
  
  location:
    files: 
      - "src/path/to/file1.py"
      - "src/path/to/file2.py"
    scope: "function|class|module|pattern"
  
  evidence:
    detection_method: "static_analysis|code_review|test_coverage|git_history"
    tool_used: "pylint|radon|pytest-cov|manual"
    output: |
      [Tool output or code snippets]
  
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

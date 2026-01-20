---
# PHASE EXECUTION CHECKLIST WITH AUDIT LOGGING
# Quick reference for engineers executing any phase with proper test validation

metadata:
  title: "Phase Execution Checklist - Test-Driven Audit Trail"
  version: "1.0"
  date: "2026-01-20"
  applies_to: "All phases in _workspaces/roadmap/phases/"
  reference_docs:
    - "AUDIT-LOGGING-STANDARD.md"
    - "PHASE-E-STUB-PREVENTION.md"
    - "cortex-builder.prompt.md § CORE-027"

---

## BEFORE YOU START A PHASE

### Pre-Execution Checklist

```
☐ Phase YAML file exists in _workspaces/roadmap/phases/[phase-name].yaml
☐ Phase YAML has "audit_and_validation" section (if not, see "Adding Audit Logging" below)
☐ You've read the phase's "acceptance_criteria" section completely
☐ You understand all test files referenced in the phase
☐ You've created git branch: git checkout -b [phase-name]
☐ You've read AUDIT-LOGGING-STANDARD.md § PART 3 (Implementation Guidance)
☐ You've read PHASE-E-STUB-PREVENTION.md (if this is Phase E or implementation phase)
☐ You understand governance rules: CORE-008, CORE-011, CORE-012, CORE-013
```

---

## FOR EACH ACCEPTANCE CRITERION (AC)

### STEP 1: AC_START EVENT - Record the beginning

**When:** Before you start working on this AC

**Commands to run:**
```bash
# 1. Record baseline for this AC
cd /Users/asifhussain/PROJECTS/CORTEX

# 2. See what tests exist for this AC (if known)
pytest --collect-only -q | grep -i "[ac-specific-module]" | wc -l

# 3. Run test (expect FAILURES - this is RED phase)
pytest tests/unit/[module-path]/ -v

# 4. Record output:
# - Test count
# - Number of failures
# - Error messages
# - Time: YYYY-MM-DD HH:MM:SS
```

**What to record in YAML:**
```yaml
# In phase YAML file, under audit_trail.ac_start_events, add:
- ac_id: "AC-PHASE-001"
  ac_title: "[Title from acceptance_criteria]"
  started: "YYYY-MM-DD HH:MM:SS"
  started_by: "[Your name]"
  test_command: "pytest tests/unit/[path]/ -v"
  baseline_test_count: N
  baseline_failures: M
```

**Git record:**
```bash
git add _workspaces/roadmap/phases/[phase-name].yaml
git commit -m "AC-PHASE-001: START - Record baseline for [AC title]"
```

---

### STEP 2: AC_EXECUTE EVENT - Work and track progress

**During implementation:**

After every significant change (not every keystroke - maybe every 30 mins):

```bash
# 1. Run the test again
pytest tests/unit/[module-path]/ -v > /tmp/test_output.txt

# 2. Check if tests pass
if grep "passed" /tmp/test_output.txt; then
  echo "✅ Tests passing!"
fi

# 3. Record current timestamp and status
date "+%Y-%m-%d %H:%M:%S"

# 4. Count: how many pass, how many fail
grep -E "PASSED|FAILED" /tmp/test_output.txt | wc -l
```

**What to record in YAML (ongoing):**
```yaml
# In phase YAML, under audit_trail.ac_execute_events, add:
- ac_id: "AC-PHASE-001"
  execution_timestamp: "YYYY-MM-DD HH:MM:SS"  # When tests ran
  test_output: "N passed, M failed"
  pytest_output_snippet: |
    [Paste last 20 lines of pytest output]
    test_function_1 PASSED
    test_function_2 FAILED
    ... N passed in X.XXs
  pass_percentage: "[N/(N+M) * 100]%"
  verified_by: "[Your name]"
```

**When all tests pass:**
```bash
# 1. Run final test
pytest tests/unit/[module-path]/ -v

# 2. Capture the output
pytest tests/unit/[module-path]/ -v --tb=short > /tmp/final_test.txt

# 3. Verify: should show "N passed, 0 failed"
grep "passed" /tmp/final_test.txt

# 4. Commit with test count
git add cortex/[module-path]
git commit -m "Module: [name] - Implement [what you did]; N tests passing"
```

---

### STEP 3: AC_COMPLETE EVENT - Finalize and verify

**When:** All tests for this AC are passing

**Final verification commands:**
```bash
# 1. Run tests ONE MORE TIME to confirm they still pass
pytest tests/unit/[module-path]/ -v

# 2. Check type hints (if implementation phase)
mypy cortex/[module-path]/ --strict

# 3. Check docstrings (if implementation phase)
pydocstyle cortex/[module-path]/

# 4. Verify no bare except clauses (governance rule CORE-013)
grep -n "except:" cortex/[module-path]/*.py | grep -v "except [A-Z]"
```

**Record in YAML:**
```yaml
# In phase YAML, under audit_trail.ac_complete_events, add:
- ac_id: "AC-PHASE-001"
  ac_title: "[AC title]"
  completion_timestamp: "YYYY-MM-DD HH:MM:SS"
  completion_status: "✅ COMPLETE"
  evidence:
    - "All tests passing: N/N passed (from execute_events)"
    - "Git commit: [hash] - Module: [name]"
    - "Type hints: [0 errors or 100% coverage]"
    - "Docstrings: [100% coverage]"
    - "No bare except clauses: ✅ verified"
  completed_by: "[Your name]"
```

**Final git commit:**
```bash
git add _workspaces/roadmap/phases/[phase-name].yaml
git commit -m "AC-PHASE-001: COMPLETE - [What was implemented]; N tests passing"
```

---

## WHEN ALL ACS ARE COMPLETE

### Create the Phase Audit Report

**File:** `_workspaces/roadmap/reports/[PHASE-ID]-AUDIT-COMPLETE.yaml`

**Template to use:** See AUDIT-LOGGING-STANDARD.md § PART 2

**Commands to gather data:**
```bash
# 1. Get all tests that passed
pytest tests/unit/[phase-modules]/ -v 2>&1 | grep "passed"

# 2. Get git log for this phase
git log --oneline | grep "[phase-name]" | head -20

# 3. Get line count of what you implemented
find cortex/[phase-modules]/ -name "*.py" -exec wc -l {} + | tail -1

# 4. Get type checking result
mypy cortex/[phase-modules]/ --strict 2>&1 | tail -5

# 5. Get docstring coverage
pydocstyle cortex/[phase-modules]/ 2>&1 | tail -5
```

**Create the report:**
```yaml
---
# [PHASE-ID]-AUDIT-COMPLETE.yaml

metadata:
  phase_id: "[PHASE-ID]"
  completion_date: "YYYY-MM-DD"
  status: "✅ COMPLETE"

executive_summary: |
  [What was accomplished]
  
  Starting: X errors, Y tests
  Ending: 0 errors (or X errors), Z tests passing

acceptance_criteria_matrix:
  ac_count: N
  complete_count: N
  pass_rate: "100%"
  
  details:
    - ac_id: "AC-PHASE-001"
      status: "✅ COMPLETE"
      tests_passed: "N/N"
      git_commit: "[hash]"

test_execution:
  total_tests_passed: Z
  pass_rate: "100%"
  pytest_output: |
    [Paste actual pytest summary]
    Z passed in X.XXs

validation_results:
  pytest_collection:
    result: "[N tests collected, 0 errors]"
  pytest_execution:
    result: "[N passed, 0 failed]"
  type_checking:
    result: "0 errors"
  docstring_coverage:
    result: "100%"

metrics:
  error_reduction: "[Baseline → Final]"
  code_coverage: "[Module count and test references]"
  implementation_velocity: "[N modules/day, M LOC/day]"

sign_off:
  phase_complete: true
  all_acceptance_criteria: "✅ MET"
```

**Commit the report:**
```bash
git add _workspaces/roadmap/reports/[PHASE-ID]-AUDIT-COMPLETE.yaml
git commit -m "Phase [ID]: Final audit report - All ACs verified, 100% pass rate"
```

---

## QUICK COMMAND REFERENCE

### Before each AC
```bash
# Create git branch for this AC (optional but recommended)
git checkout -b ac-phase-001

# Run baseline test to see what fails
pytest tests/unit/[module]/ -v
```

### During implementation
```bash
# Quick test run
pytest tests/unit/[module]/ -v -x  # Stop on first failure

# Check one test
pytest tests/unit/[module]/test_file.py::test_function -v

# Check types
mypy cortex/[module]/ --strict

# Check docs
pydocstyle cortex/[module]/
```

### When AC tests pass
```bash
# Final confirmation
pytest tests/unit/[module]/ -v

# Get summary
pytest tests/unit/[module]/ -v --tb=line | tail -3

# Commit with count
git commit -m "Module: name - Implement X; N tests passing"
```

### After all ACs done
```bash
# See all commits for this phase
git log --oneline --grep="[phase-name]" --since="1 week ago"

# Count total lines added
git diff PHASE-[ID]~1 HEAD -- cortex/ | grep "^+" | wc -l

# Run full phase test suite
pytest tests/unit/[phase-modules]/ -v --tb=short

# Update implementation map
nano _workspaces/roadmap/cortex-impl-map.yaml
```

---

## WHAT NOT TO DO

### ❌ DO NOT mark AC_COMPLETE if:
- ❌ Tests show "FAILED" (any failures)
- ❌ mypy --strict shows errors
- ❌ Docstrings are incomplete
- ❌ Type hints are missing
- ❌ Bare except: clauses exist
- ❌ pytest --collect-only shows errors

### ❌ DO NOT commit if:
- ❌ Tests are failing
- ❌ Commit message doesn't say "N tests passing"
- ❌ You didn't run tests before committing
- ❌ You created stubs instead of implementations
- ❌ You used "pass" statements instead of real code

---

## EXAMPLE: PHASE E2 AC EXECUTION

### AC_START: orchestrator_decorator

```bash
# 1. Baseline
$ pytest tests/unit/core/test_orchestrator_decorator.py --collect-only
50 tests collected, 0 errors

$ pytest tests/unit/core/test_orchestrator_decorator.py -v
[shows 50 FAILED]

# 2. Record in YAML
# ac_id: AC-E2-001
# started: 2026-01-21 09:00:00
# test_command: pytest tests/unit/core/test_orchestrator_decorator.py -v
```

### AC_EXECUTE: Work on implementation

```bash
# During work
$ pytest tests/unit/core/test_orchestrator_decorator.py -v -x
test_init PASSED ✓
test_context_manager FAILED
test_execute FAILED
test_decorator_chain FAILED
[20 more tests not run due to -x]

# Keep fixing, re-run
$ pytest tests/unit/core/test_orchestrator_decorator.py -v
test_init PASSED ✓
test_context_manager PASSED ✓
test_execute PASSED ✓
[... all 50 PASSED]
50 passed in 0.45s

# Record in YAML (execution_timestamp, test_output, verified_by)
```

### AC_COMPLETE: Finalize

```bash
# Final verification
$ pytest tests/unit/core/test_orchestrator_decorator.py -v
50 passed in 0.45s ✓

$ mypy cortex/core/decorators/orchestrator_decorator.py --strict
Success: no issues found ✓

$ pydocstyle cortex/core/decorators/orchestrator_decorator.py
[0 errors] ✓

# Commit
$ git commit -m "Module: orchestrator_decorator - Implement decorator chain; 50 tests passing"

# Record completion in YAML
# completion_status: ✅ COMPLETE
# evidence:
#   - "50/50 tests passing"
#   - "Git commit: abc123def"
#   - "Type hints: 0 errors"
#   - "Docstrings: 100%"
```

---

## DOCUMENTATION YOU NEED

Keep these files open in your editor:

1. **Phase YAML file** - `_workspaces/roadmap/phases/[phase-name].yaml`
   - Reference for what needs to be done
   - Where you record audit events

2. **AUDIT-LOGGING-STANDARD.md**
   - How to structure audit logs
   - Templates for audit events
   - Required format for reports

3. **PHASE-E-STUB-PREVENTION.md** (if Phase E)
   - How to avoid creating empty stubs
   - Test-first discipline checklist
   - Red/Green/Refactor workflow

4. **cortex-builder.prompt.md**
   - Reference for governance rules
   - CORE-008 (tests first)
   - CORE-011, CORE-012, CORE-013 (quality rules)

---

## AFTER PHASE COMPLETE

### Update implementation map
```bash
nano _workspaces/roadmap/cortex-impl-map.yaml

# Find this phase entry and update:
# status: "COMPLETE"
# error_reduction: "X → Y (-Z)"
# test_pass_rate: "N/N (100%)"
# audit_report: "reports/[PHASE-ID]-AUDIT-COMPLETE.yaml"
```

### Create summary markdown
```bash
# Copy this template
cat > _workspaces/roadmap/PHASE-[ID]-COMPLETE.md << 'EOF'
# Phase [ID]: Complete ✅

## Summary
[2-3 sentences about what was done]

## Results
| Metric | Start | End | Change |
|---|---|---|---|
| Collection Errors | X | Y | -Z |
| Tests Collected | A | B | +C |
| Modules | D | E | +F |

## What We Did
[List of key accomplishments]

## Current State
[What's ready next]

## Next Steps
**Phase [NEXT-ID]** [description]

---
Timestamp: YYYY-MM-DD
Status: ✅ COMPLETE
EOF
```

### Verify no regressions
```bash
# Run ENTIRE test suite (not just this phase)
pytest tests/unit/ -v --tb=short | tail -10

# Should show same or better pass rate
# Should show same or fewer errors
```

---

## SIGN-OFF CHECKLIST

Before declaring phase COMPLETE:

```
☐ All ACs have execution evidence (ac_execute_events populated)
☐ All ACs have completion evidence (ac_complete_events populated)
☐ pytest --collect-only shows 0 errors for this phase's modules
☐ pytest tests/unit/[modules]/ shows N passed, 0 failed
☐ mypy --strict shows 0 errors
☐ pydocstyle shows 100% documentation
☐ grep shows no bare except: clauses
☐ All governance rules compliant
☐ Git log shows progression with test counts
☐ [PHASE-ID]-AUDIT-COMPLETE.yaml created in reports/
☐ cortex-impl-map.yaml updated with COMPLETE status
☐ PHASE-[ID]-COMPLETE.md created
☐ No regressions in overall test suite
☐ Ready for next phase gate
```

**Sign-off command:**
```bash
git commit --allow-empty -m "PHASE-[ID]: SIGN-OFF ✅ - All ACs verified, N tests passing, audit complete"
```

---

**This is your checklist. Use it for EVERY phase execution.**

**Authority:** CORE-027 (AC Audit Trail Enforcement)
**Reference:** AUDIT-LOGGING-STANDARD.md

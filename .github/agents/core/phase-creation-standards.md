# Phase Creation Standards Guide

**Authority:** CORE-042, CORE-008, CORE-064 | **Created:** 2026-02-12 | **Updated:** 2026-02-25

---

## 🎯 Purpose

This guide establishes best practices for creating CORTEX phases, ensuring consistency, completeness, and maintainability across all phase specifications.

---

## ⛔ SEQUENTIAL EXECUTION CONTRACT (MANDATORY — P0)

Every phase authored in CORTEX **must** enforce complete sequential execution of its sub-phases. This is non-negotiable and derives from CORE-008 (TDD) and CORE-064 (Sweep Completeness).

### ⚡ WHOLE-PHASE-FIRST PRINCIPLE (Maximum ROI Rule)

> **A phase must always be designed and executed as a single, complete unit — never decomposed into separately-completing pieces.**

The highest ROI comes from finishing a phase end-to-end before moving on. Partial phase execution produces:
- Orphaned GAPs that drift without resolution
- Wiring that is half-complete and therefore broken
- Test suites that cannot pass their full golden gate
- Context loss that forces re-analysis in a future session

**Mandatory phase authoring rule:** Every phase file must declare `sequential_execution_contract.phase_atomic: true` and `decomposition_allowed: false`. Any attempt to split a phase into "phase-73 part 1" and "phase-73 part 2" is a P0 governance violation unless the split produces two fully self-contained phases each with their own complete sweep catalogues.

**Mandatory execution rule:** When executing a phase, run all sub-phases in order to completion within the same session or continuous execution context. If a session must pause, the state is recorded at the last passed `completion_gate` and execution resumes from the next sub-phase — not from a new partial phase.

### The Four Laws of Sub-Phase Execution

**Law 1 — No sub-phase may start until the preceding sub-phase passes its completion gate.**
Every sub-phase must declare a `completion_gate` block. The next sub-phase's `prerequisite` must reference it explicitly. Execution halts if the gate fails — fix the failure, rerun the gate, then continue.

**Law 2 — Every sub-phase must run its full RED→GREEN→REFACTOR loop before marking COMPLETE.**
No sub-phase may be marked COMPLETE with only RED tests written, or only GREEN without REFACTOR. The TDD cycle is atomic: all three phases must complete before the sub-phase closes. The `tdd_cycle` block is mandatory on every sub-phase that involves code.

**Law 3 — A phase is only COMPLETE when every entry in its `sweep_catalogue` has `status: CLOSED`.**
CORE-064 is absolute. Partial sweeps that leave any GAP OPEN are governance violations. The `phase-N-final` sub-phase must verify this before marking the phase file for promotion to `completed/`.

**Law 4 — The final sub-phase is always a smoke gate + CORE-064 close sub-phase.**
Every phase must end with a `phase-N-final` sub-phase that: (a) verifies all GAPs CLOSED, (b) runs smoke tests, (c) moves the phase file from `planned/` → `completed/`, and (d) updates `cortex-master.yaml` to `status: COMPLETE`.

### Completion Gate Schema (Required on Every Sub-Phase)

```yaml
completion_gate:
  test_runner_command: "python3 scripts/run_tests.py {scope}"   # must pass
  min_tests_pass: N          # explicit count — never omit
  zero_new_failures: true    # non-negotiable
  all_gap_refs_closed: true  # CORE-064 check for THIS sub-phase's gaps
  blocks_next_sub_phase: true  # prevents next sub-phase from starting if gate fails
```

### RED→GREEN→REFACTOR Block (Required on Every Sub-Phase)

Every sub-phase that involves code must contain an explicit `tdd_cycle` block:

```yaml
tdd_cycle:
  red:
    action: "Write all failing tests listed in tdd_sequence.red before any implementation"
    gate: "python3 scripts/run_tests.py file <test_file> — ALL listed tests must FAIL (import errors count)"
    blocker: "Do NOT write implementation code until RED gate passes"
  green:
    action: "Write minimum implementation to turn all RED tests GREEN"
    gate: "python3 scripts/run_tests.py file <test_file> — ALL tests must PASS"
    blocker: "Do NOT begin REFACTOR until GREEN gate passes"
  refactor:
    action: "Clean up implementation — type hints, docstrings, deduplication, complexity"
    gate: "python3 scripts/run_tests.py dir <affected_dir> — zero regressions"
    blocker: "Do NOT mark sub-phase COMPLETE until REFACTOR gate passes"
```

### Prohibited Patterns (P0 Violations)

| Pattern | Why It's Forbidden |
|---|---|
| `phase_atomic: false` or `decomposition_allowed: true` | Violates WHOLE-PHASE-FIRST — max ROI requires end-to-end completion |
| Phase split into "part 1 / part 2" without two complete sweep catalogues | Decomposes a phase mid-sweep — CORE-064 violation |
| `depends_on: []` with no `completion_gate` | No enforcement — sub-phases can be skipped |
| `status: COMPLETE` with open GAPs in `gap_refs` | Violates CORE-064 |
| Sub-phase with code changes but no `tdd_cycle` block | Violates CORE-008 — TDD is mandatory |
| Sub-phase with no `tdd_sequence` block | Violates CORE-008 — TDD is mandatory |
| `tdd_cycle.red.blocker` not explicitly stated | Allows skipping RED phase |
| `completion_gate.blocks_next_sub_phase: false` on non-final sub-phase | Defeats sequential contract |
| No `phase-N-final` sub-phase (smoke gate + CORE-064 close) | Phase can be abandoned without confirmation |
| Marking a phase COMPLETE before smoke gate passes | Violates production readiness |

---

---

## 📐 Hierarchical Terminology (CORE-042)

**CORTEX Hierarchy (Simplified):**

```
PHASE (P-)   Work milestone, 1-4 weeks
  └─ STAGE (S-) Work unit, 2-5 days
      └─ TASK (T-) Atomic work, 2-8 hours
```

**Key Principles:**
- ✅ Simple, universal hierarchy
- ✅ Works across all orchestrators (planning, interaction, TDD)
- ✅ No wave/epic/feature concepts
- ✅ Consistent P-/S-/T- prefixes

**DEPRECATED TERMS:**
- ❌ "Wave" → Use **Phase**
- ❌ "Initiative" → Use **Phase** 
- ❌ "Epic" → Use **Phase**
- ❌ "Feature" → Use **Phase**

---

## 📋 Overview

Every CORTEX phase must follow a standardized structure with:
- ✅ Stage-based execution plan (Foundation → Core → Migration → Polish)
- ✅ Cleanup requirements (vacuum per stage)
- ✅ Registry synchronization checkpoints
- ✅ Minimum 80% test coverage
- ✅ ROI justification with evidence

---
- ✅ Minimum 80% test coverage
- ✅ ROI justification with evidence

## 🛠️ CLI Tool Usage

### Installation

The phase creator CLI is available via:

```bash
python -m cortex.cli.phase_creator --help
```

### Creating a New Phase

#### Standard Phase (Simple)

```bash
python -m cortex.cli.phase_creator create \
  --template standard \
  --id ENH-100 \
  --title "Feature Implementation" \
  --output phases/active/enh-100.yaml
```

#### Enhancement Phase (Complex)

```bash
python -m cortex.cli.phase_creator create \
  --template enhancement \
  --id ENH-200 \
  --title "Multi-Stage Enhancement" \
  --output phases/active/enh-200.yaml \
  --interactive
```

### Validating a Phase Specification

```bash
# Basic validation (50+ rules)
python -m cortex.cli.phase_creator validate phases/active/enh-100.yaml

# Comprehensive linting with detailed report
python -m cortex.cli.phase_creator lint phases/active/enh-100.yaml
```

## 📐 Validation Rules (50+ Checks)

### 1. Naming Conventions (CORE-028)

- **Phase ID Format:** `ENH-XXX` or `phase-XXX`
- **File Names:** kebab-case, max 40 characters
- **Title Length:** ≤80 characters recommended

**Example:**
```yaml
enhancement_id: "ENH-084"  # ✅ Valid
# enhancement_id: "Feature-1"  # ❌ Invalid format
```

### 2. Required Fields

Minimum required fields for all phases:

```yaml
enhancement_id: "ENH-XXX"        # Required
title: "Phase Name"              # Required
problem:                         # Required
  current_state: "..."
  gaps: []
  impact: "..."
solution:                        # Required
  approach: "..."
  benefits: []
deliverables: []                 # Required (min 2)
tests:                          # Required
  target: 15                     # Min 5
  coverage_minimum: 0.80         # Min 0.80
```

### 3. Sub-Phase Structure (All Templates — Sequential, Gated)

For all phases, use sub-phase-based structure with explicit completion gates and TDD cycles. Sub-phases execute **strictly sequentially** — the next cannot start until the current passes its gate.

```yaml
sub_phases:
  - id: "phase-N-a"
    title: "Foundation — [what this closes]"
    priority: P0
    status: PLANNED
    gap_refs: ["GAP-N-01", "GAP-N-02"]
    depends_on: []                   # first sub-phase — no dependencies
    prerequisite: "smoke tests green (≥N baseline)"

    tdd_cycle:
      red:
        action: "Write all failing tests listed in tdd_sequence.red"
        gate: "python3 scripts/run_tests.py file tests/path/test_N_a.py — ALL FAIL"
        blocker: "Do NOT write implementation until ALL listed tests fail"
      green:
        action: "Implement minimum code to pass all RED tests"
        gate: "python3 scripts/run_tests.py file tests/path/test_N_a.py — ALL PASS"
        blocker: "Do NOT begin refactor until ALL tests pass"
      refactor:
        action: "Add type hints, docstrings, remove duplication (CORE-011, CORE-012, CORE-035)"
        gate: "python3 scripts/run_tests.py dir tests/affected_dir/ — zero regressions"
        blocker: "Do NOT mark COMPLETE until refactor gate passes"

    tdd_sequence:
      red:
        - "test_<specific_case_1> — <what it asserts>"
        - "test_<specific_case_2> — <what it asserts>"
      green:
        - "Implement <class/function> to satisfy test_<case_1>"
        - "Implement <class/function> to satisfy test_<case_2>"
      refactor:
        - "Add docstrings to all public methods (CORE-012)"
        - "Verify type hints on all signatures (CORE-011)"
        - "Check CORE-035: no duplicate implementations"

    completion_gate:
      test_runner_command: "python3 scripts/run_tests.py dir tests/affected_dir/"
      min_tests_pass: N
      zero_new_failures: true
      all_gap_refs_closed: true
      blocks_next_sub_phase: true

  - id: "phase-N-b"
    title: "Core — [what this closes]"
    priority: P0
    status: PLANNED
    gap_refs: ["GAP-N-03"]
    depends_on: ["phase-N-a"]       # ← hard dependency; cannot start until phase-N-a gate passes
    prerequisite: "phase-N-a completion_gate PASSED"
    # ... same tdd_cycle, tdd_sequence, completion_gate structure
```

### 4. Cleanup Requirements

Every phase must include cleanup:

```yaml
cleanup_requirements:
  vacuum_per_phase: true           # Mandatory
  registry_sync: true             # Mandatory
  documentation_update: true      # Recommended
```

### 5. Test Coverage

Minimum 80% test coverage enforced:

```yaml
tests:
  target: 15                      # Number of tests
  coverage_minimum: 0.80          # 80% minimum
  integration_required: true      # Recommended
```

### 6. ROI Justification

High ROI scores (>9.0) require justification:

```yaml
roi: 9.5
roi_justification: |
  Highest ROI due to:
  - 50% reduction in phase creation time
  - Zero orphan phases (validation enforced)
  - Template-driven consistency
```

### 7. Dependency Validation

Dependencies must exist in registry:

```yaml
dependencies: ["ENH-063", "PHASE-H"]  # Must exist
blocks: ["PHASE-J"]                   # Must exist
```

## 📝 Templates

### 1. Standard Template

Best for: Simple phases, single-Phase Execution

```yaml
enhancement_id: "ENH-XXX"
title: "Feature Name"
priority: "P1-HIGH"
roi: 8.0
estimated_effort: "3-4 days"

problem:
  current_state: "Current situation"
  gaps:
    - "Gap 1"
    - "Gap 2"
  impact: "Business impact"

solution:
  approach: "How we'll solve it"
  benefits:
    - "Benefit 1"
    - "Benefit 2"

stages:
  - stage: 1
    name: "Foundation"
    duration: "1 day"
  - stage: 2
    name: "Core Implementation"
    duration: "2 days"

deliverables:
  - "Deliverable 1"
  - "Deliverable 2"

tests:
  target: 15
  coverage_minimum: 0.80

success_metrics:
  - "Metric 1: X → Y"
  - "Metric 2: A → B"
```

### 2. Enhancement Template

Best for: Complex phases with multiple stages

```yaml
enhancement_id: "ENH-XXX"
title: "Complex Enhancement"

stages:
  - stage: "S1-Foundation"
    duration: "3 days"
    deliverables: []
    tests: 6
    
  - stage: "S2-Core"
    duration: "3 days"
    deliverables: []
    tests: 50

cleanup_requirements:
  vacuum_per_phase: true
  registry_sync: true
  documentation_update: true

# ... (other fields same as standard)
```

### 3. Phase Template

Best for: Single milestone work units

```yaml
phase_id: "PHASE-XX"
name: "Phase Name"
release: "R1-RELEASE-NAME"
priority: "P0-CRITICAL"
duration: "1-4 weeks"
session_id: "PHASE-XX-20260212-01"
status: "planned"
roi: 8.0

requires: ["PHASE-YY"]
blocks: ["PHASE-ZZ"]

highlights:
  - "Highlight 1"
  - "Highlight 2"

deliverables:
  - "Deliverable 1"
  - "Deliverable 2"

test_target: 15
commits_expected: 2
```

## 🔄 Workflow Integration

### With cortex-architect.md

The phase creator integrates with `cortex-architect.prompt.md`:

1. **Architect detects** IMPLEMENT/DESIGN intent for new phase
2. **Auto-invoke** `phase_creator.py` with guided wizard
3. **Generate** phase spec from template with user input
4. **Validate** using 50+ rules
5. **Sync** with registry (update `index.yaml`)
6. **Display** phase execution plan + ROI estimate
7. **Approve** → phase enters `active/` folder

### With Registry

Phase specs sync with `cortex-registry/`:

```
cortex-registry/
  
    phases/
      active/          # Current phases
        enh-084.yaml
        phase-100.yaml
      completed/       # Finished phases
        enh-082.yaml
```

## 📊 Success Metrics

ENH-084 aims for:

- ✅ **50% faster** phase creation (measured)
- ✅ **Zero orphan** phases (validation enforced)
- ✅ **100% adoption** (post-ENH-084 phases)
- ✅ **80% coverage** minimum (all new phases)
- ✅ **Consistent structure** (template-driven)

## 🚀 Examples

### Example 1: Simple Bug Fix Phase

```bash
python -m cortex.cli.phase_creator create \
  --template standard \
  --id phase-100 \
  --title "Fix Authentication Bug" \
  --output phases/active/phase-100.yaml
```

### Example 2: Complex Multi-Stage Enhancement

```bash
python -m cortex.cli.phase_creator create \
  --template enhancement \
  --id ENH-300 \
  --title "Dashboard Overhaul" \
  --interactive
```

Interactive prompts will guide you through:
- Problem description
- Solution approach
- Stage breakdown
- Deliverables
- Test targets

### Example 3: Session-Scoped Phase

```bash
python -m cortex.cli.phase_creator create \
  --template phase \
  --id PHASE-89 \
  --title "Language Refinement" \
  --output phases/active/phase-89.yaml
```

## 🔍 Validation Examples

### Valid Specification

```yaml
enhancement_id: "ENH-084"
title: "Standard Phase Creation Practices"
roi: 9.5
roi_justification: "Highest ROI - prevents future technical debt"
tests:
  target: 16
  coverage_minimum: 0.85
deliverables:
  - "Phase template CLI tool"
  - "50+ validation rules"
  - "15+ CLI tests"
```

**Validation Result:** ✅ All checks passed

### Invalid Specification

```yaml
enhancement_id: "INVALID"  # Wrong format
title: "Test"
# Missing: problem, solution, deliverables
tests:
  coverage_minimum: 0.50  # Too low
```

**Validation Result:** ❌ 3 errors, 1 warning

## 📚 Related Documentation

- **ENH-084 Specification:** Phase creation automation (see registry)
- **Registry Master Index:** `cortex-registry/index.yaml`
- **CORE-042:** Hierarchical terminology (PHASE→STAGE→TASK)

## 🆘 Troubleshooting

### Issue: Validation Fails with "Missing deliverables"

**Solution:** Add at least 2 deliverables:

```yaml
deliverables:
  - "Component 1"
  - "Component 2"
```

### Issue: "Invalid enhancement_id format"

**Solution:** Use correct format:

```yaml
# ✅ Valid
enhancement_id: "ENH-084"
enhancement_id: "phase-54"

# ❌ Invalid
enhancement_id: "feature-1"
enhancement_id: "CORTEX-100"
```

### Issue: Test Coverage Below Minimum

**Solution:** Increase coverage or justify exception:

```yaml
tests:
  coverage_minimum: 0.80  # Minimum 80%
  justification: "Legacy code migration exception"  # If <80%
```

---

**Authority:** ENH-084 Standard Phase Creation Practices  
**Maintainer:** CORTEX Framework  
**Updated:** 2026-02-12

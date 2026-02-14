# Phase Creation Standards Guide

**Authority:** CORE-042 | **Created:** 2026-02-12 | **Updated:** 2026-02-14

---

## 🎯 Purpose

This guide establishes best practices for creating CORTEX phases, ensuring consistency, completeness, and maintainability across all phase specifications.

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

### 3. Stage Structure (All Templates)

For all phases, use stage-based structure:

```yaml
stages:
  - stage: "S1-Foundation"
    duration: "3 days"
    deliverables:
      - "Registry audit"
      - "Cleanup script"
    tests: 6
    
  - stage: "S2-Core"
    duration: "3 days"
    deliverables:
      - "Core implementation"
    tests: 50
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
version: "1.0"
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
version: "1.0"
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

Phase specs sync with `cortex-registry/_cortex-master/`:

```
cortex-registry/
  _cortex-master/
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
- **Registry Master Index:** `cortex-registry/_cortex-master/index.yaml`
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

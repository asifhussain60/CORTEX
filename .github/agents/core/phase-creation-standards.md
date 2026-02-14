# Phase Creation Standards Guide

**Version:** 2.0 | **Created:** 2026-02-12 | **Updated:** 2026-02-14 | **Authority:** ENH-084 + CORE-042

---

## 🎯 Purpose

This guide establ### 7. Dependency Validation

Dependencies must exist in registry:

```yaml
dependencies: ["ENH-063", "FEATURE-H"]  # Must exist
blocks: ["FEATURE-J"]                   # Must exist
```

## 🎨 Phase Templates

### Standard Template

Best for: Simple phases, single-feature execution practices for creating CORTEX phases, ensuring consistency, completeness, and maintainability across all phase specifications.

## � Hierarchical Terminology (CORE-042)

**Industry-Aligned Hierarchy (Scrum/SAFe):**

```
EPIC (E-)           Strategic initiative, 3-12 months
  └─ FEATURE (F-)   Deliverable capability, 2-8 weeks
      └─ PHASE (P-) Milestone/increment, 1-4 weeks  
          └─ STAGE (S-) Work unit, 2-5 days
              └─ TASK (T-) Atomic work, 2-8 hours
```

**DEPRECATED TERMS:**
- ❌ "Wave" → Use **Epic** (strategic) or **Feature** (deliverable)
- ❌ "Initiative" → Use **Epic**
- ❌ "Track" → Use **Feature**

## �📋 Overview

Every CORTEX phase must follow a standardized structure with:
- ✅ Feature/Epic-based execution plan (Foundation → Core → Migration → Polish)
- ✅ Cleanup requirements (vacuum per feature)
- ✅ Registry synchronization checkpoints
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

#### Enhancement Phase (Complex with Features)

```bash
python -m cortex.cli.phase_creator create \
  --template enhancement \
  --id ENH-200 \
  --title "Multi-Feature Enhancement" \
  --output phases/active/enh-200.yaml \
  --interactive
```

#### Feature Phase (Session-Scoped)

**DEPRECATED:** Use Epic/Feature templates instead

```bash
# Old Wave template deprecated
# python -m cortex.cli.phase_creator create --template wave
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

### 3. Feature Structure (Enhancement Template)

For complex phases, use feature-based structure:

```yaml
features:
  - feature: "F1-Foundation"
    duration: "3 days"
    deliverables:
      - "Registry audit"
      - "Cleanup script"
    tests: 6
    
  - feature: "F2-Core"
    duration: "3 days"
    deliverables:
      - "Core implementation"
    tests: 50
```

### 4. Cleanup Requirements

Every feature must include cleanup stage:

```yaml
cleanup_requirements:
  vacuum_per_feature: true         # Mandatory
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
dependencies: ["ENH-063", "WAVE-H"]  # Must exist
blocks: ["WAVE-J"]                   # Must exist
```

## 📝 Templates

### 1. Standard Template

Best for: Simple phases, single-wave execution

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

Best for: Complex phases with multiple features

```yaml
version: "1.0"
enhancement_id: "ENH-XXX"
title: "Complex Enhancement"

features:
  - feature: "F1-Foundation"
    duration: "3 days"
    deliverables: []
    tests: 6
    
  - feature: "F2-Core"
    duration: "3 days"
    deliverables: []
    tests: 50

cleanup_requirements:
  vacuum_per_feature: true
  registry_sync: true
  documentation_update: true

# ... (other fields same as standard)
```

### 3. Epic/Feature Template

**DEPRECATED (2026-02-14):** Old "Wave Template" removed per CORE-042

Use **Epic** or **Feature** level in registry structure instead.

```yaml
wave_id: "WAVE-X"
name: "Wave Name"
release: "R1-RELEASE-NAME"
priority: "P0-CRITICAL"
duration: "3-4 hours"
session_id: "WAVE-X-20260212-01"
status: "planned"
roi: 8.0

requires: ["WAVE-Y"]
blocks: ["WAVE-Z"]

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
6. **Display** wave execution plan + ROI estimate
7. **Approve** → phase enters `active/` folder

### With Registry

Phase specs sync with `cortex-registry/_cortex-master/`:

```
cortex-registry/
  _cortex-master/
    phases/
      active/          # Current phases
        enh-084.yaml
        wave-i.yaml
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

### Example 2: Complex Multi-Wave Enhancement

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
- Wave breakdown
- Deliverables
- Test targets

### Example 3: Session-Scoped Wave

```bash
python -m cortex.cli.phase_creator create \
  --template wave \
  --id WAVE-M \
  --title "Language Refinement" \
  --output phases/active/wave-m.yaml
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

- **ENH-084 Specification:** `WAVE-6-COMPREHENSIVE-CLEANUP-REFACTORING.yaml`
- **Registry Master Index:** `cortex-registry/_cortex-master/index.yaml`
- **Autonomous Execution Guide:** `AUTONOMOUS-WAVES-H-O-EXECUTION-GUIDE.md`

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

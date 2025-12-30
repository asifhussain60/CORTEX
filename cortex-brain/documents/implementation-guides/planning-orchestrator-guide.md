# Planning Orchestrator Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 30, 2025  
**Purpose:** Documentation for GitHub Copilot meta-instructions and Planning Orchestrator usage

---

## Overview

The Planning Orchestrator is CORTEX's core workflow for transforming feature requests into structured, executable implementation plans. This guide explains how GitHub Copilot reads and follows meta-instructions embedded in plans.

---

## 1. copilot_instructions Section

### What It Is

The `copilot_instructions` section is embedded metadata that tells GitHub Copilot **how** to execute the plan - what response format to use, when to show progress, and what workflow to enforce.

### Schema Definition

```yaml
copilot_instructions:
  response_template: "autonomous_execution_progress"  # Which template to use
  progress_updates: true                               # Show visual progress bars
  custom_format: null                                  # Custom instructions (optional)
  tdd_enforcement: true                                # Enforce RED→GREEN→REFACTOR
  checkpoint_frequency: "per_phase"                    # When to create git checkpoints
```

### Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `response_template` | enum | `"autonomous_execution_progress"` | Template name from `response-templates-v4.yaml` |
| `progress_updates` | boolean | `true` | Enable ASCII progress bars at phase boundaries |
| `custom_format` | string | `null` | Override template with custom instructions |
| `tdd_enforcement` | boolean | `true` | Require failing tests before implementation |
| `checkpoint_frequency` | enum | `"per_phase"` | `per_task`, `per_phase`, `manual`, `disabled` |

### Allowed Values

**response_template:**
- `"autonomous_execution_progress"` - Default for autonomous execution with progress visualization
- `"interactive_planning_progress"` - For interactive planning sessions
- `"custom"` - Use `custom_format` field for instructions

**checkpoint_frequency:**
- `per_task` - Git checkpoint after every task completion
- `per_phase` - Git checkpoint after each phase (recommended)
- `manual` - User-triggered checkpoints only
- `disabled` - No automatic checkpoints

---

## 2. How GitHub Copilot Reads Instructions

### Automatic Detection

When GitHub Copilot encounters a plan file with `copilot_instructions`, it:

1. **Reads the section** at plan load time
2. **Selects the response template** from `response-templates-v4.yaml`
3. **Applies TDD enforcement** if `tdd_enforcement: true`
4. **Shows progress updates** at boundaries defined by `checkpoint_frequency`

### Response Template Integration

The `autonomous_execution_progress` template (default) renders:

```markdown
## 🚀 Autonomous Execution Progress

**Plan:** {plan_name}
**Phase:** {current_phase}/{total_phases} - {phase_name}

### Progress Overview

| Metric | Status |
|--------|--------|
| Overall | [████████░░░░░░░░░░░░] 40% |
| Phase | [██████████████░░░░░░] 70% |
| Tasks | 7/10 completed |
| TDD | 🔴 RED (writing tests) |

### Phase Breakdown

| Phase | Progress | Tasks |
|-------|----------|-------|
| 1. Setup | [████████████████████] 100% | 3/3 ✓ |
| 2. Implementation | [██████████████░░░░░░] 70% | 4/5 |
| 3. Testing | [░░░░░░░░░░░░░░░░░░░░] 0% | 0/2 |
```

### TDD Enforcement

When `tdd_enforcement: true`, Copilot:

1. **Requires RED phase** - Tests must fail before implementation
2. **Validates GREEN phase** - Implementation must make tests pass
3. **Tracks REFACTOR phase** - Documents optimization decisions
4. **Blocks progress** if tests don't exist or pass prematurely

```yaml
# Example: TDD enforcement message
tdd_enforcement: true  # Forces RED→GREEN→REFACTOR workflow

# Copilot will:
# 1. Ask for test file BEFORE implementation
# 2. Run tests (expect failure)
# 3. Only then allow implementation
# 4. Re-run tests (expect pass)
# 5. Suggest refactoring opportunities
```

---

## 3. Example Plan with copilot_instructions

### Minimal Example

```yaml
metadata:
  plan_id: "FEATURE-AUTH-001"
  title: "User Authentication"
  status: "in-progress"

copilot_instructions:
  response_template: "autonomous_execution_progress"
  progress_updates: true
  tdd_enforcement: true
  checkpoint_frequency: "per_phase"

phases:
  - phase_number: 1
    phase_name: "Setup"
    tasks:
      - task_id: "1.1"
        task_name: "Create auth service"
```

### Full Example with Custom Format

```yaml
metadata:
  plan_id: "FEATURE-PAYMENT-001"
  title: "Payment Processing Integration"
  status: "approved"
  priority: "high"
  estimated_hours: 24
  notes: "Reviewed by security team on 2024-01-20"

copilot_instructions:
  response_template: "custom"
  progress_updates: true
  custom_format: |
    Use 5-part response format with visual progress bars.
    Update progress after each task completion.
    Include TDD phase indicators (RED/GREEN/REFACTOR).
    Show threat analysis summary for security tasks.
    Create git checkpoint after each phase.
  tdd_enforcement: true
  checkpoint_frequency: "per_task"

threat_modeling:
  enabled: true
  stride_categories:
    - "Spoofing"
    - "Tampering"
    - "Information Disclosure"
  owasp_mapping:
    - "A01:2021-Broken Access Control"
    - "A02:2021-Cryptographic Failures"
  auto_mitigations: true

phases:
  - phase_number: 1
    phase_name: "Security Analysis"
    estimated_hours: "4-6"
    tasks:
      - task_id: "1.1"
        task_name: "Run STRIDE analysis on payment flow"
        acceptance_criteria:
          - "All 6 STRIDE categories analyzed"
          - "Critical threats identified"
          - "Mitigation strategies documented"
```

---

## 4. Copilot Response Examples

### Progress Update (per_phase)

When completing a phase with `progress_updates: true`:

```markdown
## 🚀 Phase 1 Complete: Security Analysis

**Plan:** Payment Processing Integration
**Status:** Phase 1 of 4 completed

### Progress Overview

| Metric | Status |
|--------|--------|
| Overall | [█████░░░░░░░░░░░░░░░] 25% |
| Phase 1 | [████████████████████] 100% ✓ |
| Tasks | 3/12 completed |
| TDD | 🟢 GREEN (tests passing) |

### Threat Analysis Summary

| STRIDE Category | Threats | Mitigated |
|-----------------|---------|-----------|
| Spoofing | 2 | 1 |
| Tampering | 3 | 2 |
| Info Disclosure | 1 | 1 |

### Next Phase

**Phase 2: Payment Gateway Setup** (Est: 6-8 hours)
- Task 2.1: Configure Stripe SDK
- Task 2.2: Implement webhook handlers
- Task 2.3: Add payment encryption

### Git Checkpoint

✅ Created checkpoint: `checkpoint-phase-1-security-analysis`
```

### TDD Enforcement Response

When `tdd_enforcement: true` and no tests exist:

```markdown
## 🔴 TDD Enforcement: RED Phase Required

**Task:** 2.1 - Configure Stripe SDK

### TDD Status: 🔴 RED (Tests Required)

You must write failing tests BEFORE implementation:

**Required Test File:** `tests/payment/test_stripe_integration.py`

**Suggested Test Cases:**
```python
def test_stripe_client_initialization():
    """Stripe client initializes with valid API key"""
    pass  # Should fail initially

def test_payment_intent_creation():
    """Payment intent creates successfully"""
    pass  # Should fail initially
```

**Next Steps:**
1. Create the test file above
2. Run tests (expect failures)
3. Then proceed with implementation

⚠️ Implementation blocked until tests exist and fail.
```

---

## 5. Preservation During Maintenance

### Protected Fields

The `copilot_instructions` section is **protected** during maintenance operations. See: `phase-2.5-data-preservation-rules.md`

**Extraction before regeneration:**

```bash
# Extract copilot_instructions before regenerating plan
yq eval '.copilot_instructions' plan.yaml > /tmp/copilot_instructions.yaml

# After regeneration, merge back
yq eval-all 'select(fileIndex == 0) * {"copilot_instructions": select(fileIndex == 1)}' \
  plan.yaml /tmp/copilot_instructions.yaml > merged.yaml
```

**Verification after regeneration:**

```bash
# Verify copilot_instructions preserved
COPILOT_CHECK=$(yq eval 'has("copilot_instructions")' plan.yaml)
if [ "$COPILOT_CHECK" != "true" ]; then
  echo "❌ ERROR: copilot_instructions LOST!"
  exit 1
fi
```

---

## 6. Integration with Planning Orchestrator

### How Plans Are Generated

The `PlanningOrchestrator` automatically injects default `copilot_instructions`:

```python
# From src/orchestrators/planning/planning_orchestrator.py

def _generate_plan(self, request: PlanRequest) -> PlanData:
    # ... plan generation logic ...
    
    # Inject copilot_instructions with defaults
    copilot_instructions = {
        "response_template": "autonomous_execution_progress",
        "progress_updates": True,
        "tdd_enforcement": True,
        "checkpoint_frequency": "per_phase",
        "custom_format": None
    }
    
    return PlanData(
        # ... other fields ...
        copilot_instructions=copilot_instructions
    )
```

### Customizing Instructions

Users can override defaults by specifying in their plan request:

```
plan user authentication
  - use interactive template
  - checkpoint per task
  - disable TDD enforcement
```

Copilot translates this to:

```yaml
copilot_instructions:
  response_template: "interactive_planning_progress"
  progress_updates: true
  tdd_enforcement: false
  checkpoint_frequency: "per_task"
```

---

## 7. Best Practices

### When to Use Each Template

| Scenario | Template | Why |
|----------|----------|-----|
| Autonomous feature implementation | `autonomous_execution_progress` | Visual progress, TDD tracking |
| Interactive planning session | `interactive_planning_progress` | User feedback integration |
| Custom requirements | `custom` + `custom_format` | Full control over format |

### Checkpoint Frequency Guidelines

| Frequency | Use When |
|-----------|----------|
| `per_task` | High-risk features, frequent rollback needed |
| `per_phase` | Standard features (recommended default) |
| `manual` | Experienced developers, minimal overhead |
| `disabled` | Quick fixes, trusted code only |

### TDD Enforcement

- **Enable** for: New features, security code, public APIs
- **Disable** for: Documentation, config changes, hotfixes

---

## 8. Troubleshooting

### Progress Not Showing

**Check:** `progress_updates: true` in plan YAML

**Verify template exists:**
```bash
yq eval '.named_templates.autonomous_execution_progress' cortex-brain/response-templates-v4.yaml
```

### TDD Not Enforcing

**Check:** `tdd_enforcement: true` in plan YAML

**Verify tests exist:**
```bash
find tests/ -name "test_*.py" | head -5
```

### Custom Format Not Applied

**Check:** `response_template: "custom"` AND `custom_format:` has content

---

## Related Documentation

- `cortex-brain/config/plan-schema.yaml` - Full schema definition
- `cortex-brain/response-templates-v4.yaml` - Response template registry
- `cortex-brain/documents/implementation-guides/phase-2.5-data-preservation-rules.md` - Preservation rules
- `src/orchestrators/planning/planning_orchestrator.py` - Implementation

---

**End of Planning Orchestrator Guide**

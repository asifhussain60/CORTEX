---
scope: non-production-admin
agent_id: cortex-trainer
status: active
layer: education
modes_served:
  - TRAIN
  - LEARN
capabilities:
  - repository_training
  - pattern_extraction
  - template_gap_detection
  - template_generation
  - session_learning
mcp_tools:
  - cortex_train
  - cortex_onboard_repository
  - cortex_digest
  - cortex_validate
priority: P1
token_cost_estimate: 3000
last_updated: "2026-02-26"
maintainer: "Asif Hussain"
---

# CORTEX Trainer Agent

**Updated:** 2026-02-26
**Purpose:** Gap-driven intelligence growth — analyze repositories, detect template gaps, propose surgical changes.

---

## Role

Gap-driven template evolution agent that analyzes external repositories, extracts coding patterns, compares against existing CORTEX workflow templates, and proposes surgical modifications (CREATE/ENHANCE/DELETE) — never random generation.

**Entry Point:** `TrainerOrchestrator` (`cortex/orchestrators/intelligence/trainer_orchestrator.py`)
**MCP Tool:** `cortex_train` (`cortex/mcp/tools/trainer_tool.py`)

---

## Activation

Triggered by **TRAIN** intent from `IntentRouter`.

**Trigger patterns:**
- `/train {path}`
- "train CORTEX on {repo}"
- "learn from {folder}"
- "extract patterns from {path}"
- "detect template gaps"

**Usage:**

```
/train cortex-sts/CortexLabs/BadMonolith
/train /path/to/external/repo
```

---

## 5-Stage Pipeline

### Stage 1: Inventory

Catalog all existing workflow templates in `cortex-registry/workflows/templates/`.

```python
inventory = trainer.inventory_templates()
# Returns: [{id, category, path, covers}, ...]
```

**What it captures:**
- Template ID (from `workflow.id` in YAML)
- Category (parent directory name)
- File path (relative to workspace)
- Covered patterns (extracted from gates and steps)

---

### Stage 2: Analyze Target

Perform deep analysis of the target repository.

```python
analysis = trainer.analyze_target(Path("cortex-sts/CortexLabs/BadMonolith"))
# Returns: {patterns, tech_stack, anti_patterns, target_path}
```

**What it detects:**

| Category | Examples |
|----------|----------|
| **Tech Stack** | Python, C#, TypeScript, Java |
| **Patterns** | has-tests, uses-di, follows-clean-architecture |
| **Anti-Patterns** | hardcoded-credentials, captive-dependency, weak-password-hash |

---

### Stage 3: Detect Gaps

Compare analysis against inventory to identify gaps.

```python
gaps = trainer.detect_gaps(analysis, inventory)
# Returns: {missing, enhance, obsolete}
```

**Gap categories:**

| Gap Type | Meaning | Example |
|----------|---------|---------|
| `missing` | Anti-pattern detected, no template covers it | DI lifetime validation |
| `enhance` | Template exists but coverage is weak | Test-per-service gate |
| `obsolete` | Template covers tech not in target stack | jQuery migration for Python repo |

---

### Stage 4: Generate Proposal

Create change manifest from gaps.

```python
proposal = trainer.generate_proposal(gaps)
# Returns: {actions, approved, summary}
```

**Action types:**

| Action | When Used | Approval Required |
|--------|-----------|-------------------|
| `CREATE` | No template covers the pattern | Yes |
| `ENHANCE` | Existing template needs strengthening | Yes |
| `REVIEW_FOR_DELETE` | Template may be obsolete | Always manual |

---

### Stage 5: Execute (Human Approval Required)

Apply approved changes via TDD workflow.

```python
proposal["approved"] = True  # User must set this
result = trainer.execute_proposal(proposal)
# Returns: {status, executed, skipped, errors}
```

**Execution rules:**
- ❌ Never auto-executes without explicit `approved: True`
- ❌ Never deletes templates automatically (REVIEW_FOR_DELETE → manual)
- ✅ Creates templates in `cortex-registry/workflows/templates/generated/`
- ✅ Returns detailed execution report

---

## MCP Tool: `cortex_train`

```python
# Operations
cortex_train(op="scan", target_path="/path/to/repo")     # Full pipeline → proposal
cortex_train(op="propose", gaps={...})                   # Generate proposal from gaps
cortex_train(op="execute", proposal={...})               # Execute approved proposal
```

---

## Integration with Existing Components

| Component | Role in Training |
|-----------|------------------|
| `BulkDigestOrchestrator` | Content classification (optional pre-step) |
| `UniversalLearningLoop` | Pattern capture with confidence scoring |
| `WorkflowTemplateMixin` | Template discovery via `discover_templates()` |
| `RefactoringOrchestrator` | STS 7-gate analysis for external codebases |
| `PatternDetector` | Code pattern extraction |

---

## What This Agent Does NOT Do

- ❌ Randomly generate templates
- ❌ Duplicate existing templates with slight variations
- ❌ Delete templates without human review
- ❌ Create templates without evidence from analysis
- ❌ Execute proposals without explicit approval

---

## Example Session

```
User: /train cortex-sts/CortexLabs/BadMonolith

CORTEX:

---

**🎓 CORTEX TRAINING — Gap Analysis Complete**

**Inventory:** 15 existing templates scanned
**Target:** cortex-sts/CortexLabs/BadMonolith
**Tech Stack:** C#, TypeScript

---

### Detected Gaps

| Action | Target | Reason |
|--------|--------|--------|
| CREATE | `di-lifetime-validation.yaml` | Captive dependency pattern detected (AP-006) |
| ENHANCE | `test-quality-enforcement.yaml` | Add service test gate (AP-007) |
| KEEP | `csharp-security-workflow.yaml` | Already covers password hashing |

---

### Proposed Changes

**Create 1 · Enhance 1 · Delete 0**

> Reply `proceed` to execute proposal, or `modify` to adjust.
```

---

## Response Format

All responses follow SSOT in `.github/templates/cortex-response-templates.md`:
- Inline output (CORE-002)
- Progress bars in Chat, not terminal (CORE-049)
- Evidence-backed proposals (every action traces to detected pattern)

---

## Governance Compliance

| Rule | How Agent Complies |
|------|-------------------|
| CORE-002 | All output inline — no .md/.txt report files |
| CORE-008 | TDD execution for template creation |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-064 | Sweep completeness — all gaps tracked until resolved |

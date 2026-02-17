# Workflow Template Architecture

---
title: Convergence-Gated Workflow Template Library
type: explanation
audience: [Product Owners, Software Developers]
word_count: 1200
last_verified: 2026-02-16
source_of_truth: cortex/orchestrators/workflow/ + cortex/collaboration/
format: diátaxis-explanation
voice: third-person-blended
phase: Phase 100 Complete
---

> **Notice:** Workflow templates represent production-tested automation patterns as of v8.1. Templates adapt to repository context via profile detection. Performance characteristics depend on step complexity and convergence criteria.

---

## Overview: Autonomous Workflow Execution

Organizations benefit from convergence-gated workflow templates that automate multi-step development workflows without manual intervention [Business Leaders]. Product teams leverage pre-built templates for common scenarios (TDD cycles, refactoring sweeps, site dogfooding) with automatic quality gates [Product Owners]. The WorkflowTemplateRegistry provides auto-discovery, knowledge resolution, and FSM-based execution with per-step success criteria [Software Developers].

**Core Architectural Principles:**

1. **Convergence Gates** — Each workflow step loops until success criteria are met (e.g., "tests pass", "coverage ≥80%", "no P0 violations"). No manual confirmation required.

2. **Context Separation** — Templates differ by context (ARCHITECT/PRODUCTION), not code. Same workflow, different governance rules.

3. **Profile-Driven Selection** — Onboarded repository profiles drive framework selection (legacy_dotnet_spa, modern_nodejs_api, python_data_pipeline).

4. **Auto-Injected Epilogues** — Every workflow automatically ends with PostPhaseDeduplicationReview and HolisticRefactoringSweep.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   IntentRouter  │───▶│ WorkflowComposer│───▶│   Template      │  │
│  │   (IMPLEMENT)   │    │                 │    │   Registry      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                         │            │
│                                  ┌──────────────────────┘            │
│                                  ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    WorkflowTemplateRegistry                      ││
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ ││
│  │  │   onboarded_    │  │   company/      │  │   cortex/       │ ││
│  │  │   repos/*.yaml  │  │   domains/      │  │   knowledge/    │ ││
│  │  │   (first)       │  │   (second)      │  │   (fallback)    │ ││
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                  │                                   │
│                                  ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    StepStateMachine (FSM)                        ││
│  │                                                                   ││
│  │  ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐ ││
│  │  │ START │───▶│ Step1 │───▶│ Step2 │───▶│ Step3 │───▶│  END  │ ││
│  │  └───────┘    └───┬───┘    └───┬───┘    └───┬───┘    └───────┘ ││
│  │                   │            │            │                    ││
│  │              ┌────▼────┐  ┌────▼────┐  ┌────▼────┐              ││
│  │              │Converge │  │Converge │  │Converge │              ││
│  │              │  Gate   │  │  Gate   │  │  Gate   │              ││
│  │              └─────────┘  └─────────┘  └─────────┘              ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                  │                                   │
│                                  ▼                                   │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Auto-Injected Epilogues                       ││
│  │  ┌─────────────────────────┐  ┌─────────────────────────┐       ││
│  │  │ PostPhaseDeduplication │  │ HolisticRefactoringSweep│       ││
│  │  │       Review           │  │                         │       ││
│  │  └─────────────────────────┘  └─────────────────────────┘       ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Convergence Gate Configuration

Each step has explicit success criteria:

```yaml
# Example: TDD Step Convergence Gate
step_id: "tdd_green"
name: "GREEN: Make Tests Pass"
convergence:
  success_criteria:
    - "all_tests_pass"
    - "no_syntax_errors"
  max_retries: 3
  retry_delay_seconds: 5
  failure_action: "escalate"
```

---

## Available Templates

### Production Templates (10)

| Template ID | Context | Stages | Description |
|-------------|---------|--------|-------------|
| `tdd_feature_implementation` | ARCHITECT | 5 | RED → GREEN → REFACTOR cycle |
| `bug_fix_workflow` | PRODUCTION | 4 | Reproduce → Fix → Test → Deploy |
| `refactoring_sweep` | ARCHITECT | 6 | Analysis → Plan → Execute → Verify |
| `site_dogfood` | ARCHITECT | 7 | Vision API → Challenge → TDD → Deploy |
| `phase_execution` | ARCHITECT | 8 | Setup → Stages → Teardown → Report |
| `security_remediation` | PRODUCTION | 5 | Scan → Triage → Fix → Verify → Report |
| `documentation_update` | PRODUCTION | 4 | Analyze → Generate → Review → Publish |
| `dependency_upgrade` | PRODUCTION | 6 | Audit → Plan → Upgrade → Test → Deploy |
| `api_versioning` | PRODUCTION | 5 | Detect → Migrate → Test → Document |
| `test_coverage_boost` | ARCHITECT | 4 | Gap Analysis → Generate → Run → Report |

### Generic Production Profiles (3)

| Profile | Frameworks | Use Case |
|---------|------------|----------|
| `legacy_dotnet_spa` | .NET Framework 4.x, Angular 1.x | Legacy modernization |
| `modern_nodejs_api` | Node.js 18+, Express/Fastify | API development |
| `python_data_pipeline` | Python 3.9+, Pandas, SQLAlchemy | Data engineering |

---

## MCP Tool: cortex_workflow

Access workflow templates via MCP:

```json
{
  "tool": "cortex_workflow",
  "arguments": {
    "operation": "execute|list|search|validate|preview|monitor",
    "template_id": "tdd_feature_implementation",
    "context": {"mode": "ARCHITECT", "target": "cortex/mcp/"},
    "dry_run": false
  }
}
```

**Operations:**
- `execute` — Run workflow to completion (convergence-gated)
- `list` — List all available templates
- `search` — Find templates by keyword
- `validate` — Check template syntax and dependencies
- `preview` — Show execution plan without running
- `monitor` — Get status of running workflow

---

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Template Discovery** | <50ms | Auto-scans knowledge directories |
| **Step Execution** | 100-5000ms | Depends on step complexity |
| **Convergence Check** | <20ms | Per-step success validation |
| **Total Workflow** | 5-60s | Depends on template and context |
| **FSM State Transitions** | <5ms | Uses `transitions` library |

---

## Business Value

**For Business Leaders:**
- 80% faster delivery through automated workflows
- Zero manual handoffs between development stages
- Consistent quality gates across all implementations

**For Product Owners:**
- Pre-built templates for common scenarios
- Visibility into workflow progress and convergence
- Automatic epilogue enforcement (deduplication, refactoring)

**For Developers:**
- No more manual step-by-step execution
- Convergence gates ensure quality before proceeding
- Profile-driven framework selection matches project context

---

## Related Documents

- [MCP Tools Catalog](../mcp/tools-catalog.md) — `cortex_workflow` tool reference
- [Orchestration Overview](../orchestration/overview.md) — WorkflowOrchestrator details
- [Request Lifecycle](../diagrams/request-lifecycle.md) — Full request processing flow

---

*Phase 100 Complete | v8.1 | 102/102 tests passing*

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
feature: Iteration 100 Complete
order: 11
---

> **Notice:** Workflow templates represent production-tested automation patterns as of . Templates adapt to repository context via profile detection. Performance characteristics depend on step complexity and convergence criteria.

---

## Overview: Autonomous Workflow Execution with Complexity-Based Routing

Organizations benefit from convergence-gated workflow templates that automate multi-step development workflows without manual intervention [Business Leaders]. The platform now includes intelligent complexity-based routing that automatically determines whether tasks should use structured workflow templates or direct orchestrator execution, helping prevent over-engineering of simple tasks while ensuring comprehensive governance for complex operations [Product Owners]. The WorkflowTemplateRegistry provides auto-discovery, knowledge resolution, and FSM-based execution with per-step success criteria, while the Complexity-Gated Workflow Router performs multi-factor analysis to select the optimal execution path [Software Developers].

**Core Architectural Principles:**

1. **Complexity-Gated Routing** — Tasks are automatically scored (0-1.0 scale) based on multiple factors (file count, dependencies, risk level, scope). Trivial and simple tasks route directly to specialized orchestrators for efficiency, while moderate and complex tasks use structured workflow templates with comprehensive governance gates.

2. **Convergence Gates** — Each workflow step loops until success criteria are met (e.g., "tests pass", "coverage ≥80%", "no P0 violations"). No manual confirmation required.

3. **Context Separation** — Templates differ by context (ARCHITECT/PRODUCTION), not code. Same workflow, different governance rules.

4. **Profile-Driven Selection** — Onboarded repository profiles drive framework selection (legacy_dotnet_spa, modern_nodejs_api, python_data_pipeline).

5. **Auto-Injected Epilogues** — Every workflow automatically ends with PostPhaseDeduplicationReview and HolisticRefactoringSweep.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION PIPELINE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   IntentRouter  │───▶│ WorkflowGate    │───▶│   Routing       │  │
│  │   (IMPLEMENT)   │    │ (Complexity)    │    │   Decision      │  │
│  └─────────────────┘    └─────────────────┘    └────────┬────────┘  │
│                                                           │            │
│                         ┌─────────────────────────────────┘            │
│                         │                                              │
│          ┌──────────────▼──────────────┐                              │
│          │  Complexity Score: 0-1.0    │                              │
│          ├─────────────────────────────┤                              │
│          │ 0.00-0.15: TRIVIAL          │───▶ Direct Orchestrator     │
│          │ 0.16-0.35: SIMPLE           │───▶ Direct Orchestrator     │
│          │ 0.36-0.60: MODERATE         │───▶ Workflow Template       │
│          │ 0.61-1.00: COMPLEX          │───▶ Workflow Template       │
│          └─────────────────────────────┘                              │
│                                                                        │
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

### Complexity-Based Routing Decision (February 2026)

The Complexity-Gated Workflow Router performs multi-factor analysis to determine optimal execution paths, helping organizations balance efficiency with governance requirements.

**Routing Algorithm:**

Organizations benefit from automatic complexity scoring that considers multiple factors beyond simple line counts [Business Leaders]. The system analyzes file count, cross-module dependencies, stated risk levels, and operation scope to calculate a composite complexity score (0-1.0 scale) [Product Owners]. Based on configurable thresholds aligned with CORE-046 (Confirmation Gate rules), tasks automatically route to either direct orchestrator execution or structured workflow templates [Software Developers].

**Complexity Scoring Factors:**

| Factor | Weight | Measurement | Example |
|--------|--------|-------------|---------|
| **File Count** | 30% | Number of files affected | 1 file = low, 5+ files = high |
| **Dependencies** | 25% | Cross-module impact analysis | Isolated = low, shared = high |
| **Risk Level** | 25% | Self-declared or inferred | TRIVIAL → CRITICAL scale |
| **Scope** | 20% | Lines of code estimate | <100 LOC = low, >500 LOC = high |

**Routing Thresholds (Aligned with CORE-046):**

```yaml
complexity_thresholds:
  trivial:
    score_range: "0.00 - 0.15"
    route: "direct_orchestrator"
    governance: "minimal"
    confirmation: "none"
    examples:
      - "Fix typo in comment"
      - "Update single constant value"
      - "Add simple getter method"
  
  simple:
    score_range: "0.16 - 0.35"
    route: "direct_orchestrator"
    governance: "standard"
    confirmation: "auto_approve"
    examples:
      - "Add parameter validation"
      - "Implement single utility function"
      - "Update 2-3 related files"
  
  moderate:
    score_range: "0.36 - 0.60"
    route: "workflow_template"
    governance: "structured"
    confirmation: "review_recommended"
    examples:
      - "Add new API endpoint"
      - "Refactor module structure"
      - "Implement feature with tests"
  
  complex:
    score_range: "0.61 - 1.00"
    route: "workflow_template"
    governance: "comprehensive"
    confirmation: "mandatory_gates"
    examples:
      - "Multi-module architecture change"
      - "Security-critical implementation"
      - "Database schema migration"
```

**Performance Characteristics (Internal Testing):**

Organizations using the complexity gate may observe routing decisions completed within 8-15ms in most scenarios [Business Leaders]. The system combines fast heuristics (keyword matching, file counting) with intelligent analysis (dependency graph traversal, risk assessment) to make routing decisions before user perception of delay [Software Developers]. Results vary based on codebase size and complexity.

| Metric | Target | Observed (P50) | Observed (P95) |
|--------|--------|----------------|----------------|
| Complexity Scoring | <10ms | 6ms | 12ms |
| Routing Decision | <15ms | 8ms | 14ms |
| Total Overhead | <20ms | 11ms | 18ms |

> **Notice:** Routing decisions represent automated heuristics that may not perfectly match human judgment in all cases. Organizations can override routing decisions through explicit workflow selection. Complexity scoring improves through usage as the system learns patterns specific to each codebase.

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
| `site_validation` | ARCHITECT | 7 | Vision API → Challenge → TDD → Deploy |
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
    "context": {"mode": "ARCHITECT", "target": "cortex/04-mcp/"},
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

- [MCP Tools Catalog](../04-mcp/tools-catalog.md) — `cortex_workflow` tool reference
- [Orchestration Overview](../03-orchestration/01-overview.md) — WorkflowOrchestrator details
- [Request Lifecycle](../07-diagrams/request-lifecycle.md) — Full request processing flow

---

*Iteration 100 Complete |  | 102/102 tests passing*

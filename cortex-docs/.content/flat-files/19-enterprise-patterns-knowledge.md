---
title: Enterprise Patterns and Knowledge Architecture
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex-registry/patterns/ + cortex-registry/knowledge/ + cortex/intelligence/perception/
order: 19
---

# Enterprise Patterns and Knowledge Architecture

> **CORTEX doesn't guess which patterns to use — it recognises them.** Nine enterprise patterns are registered in the pattern registry, scored against every repository, and used to guide strategy selection, refactoring recommendations, and architectural decisions.

---

## The Pattern Registry

The pattern registry at `cortex-registry/patterns/` contains nine enterprise patterns, each defined as a YAML file with detection signatures, confidence scoring rules, and associated strategies:

| Pattern | Registry File | CORTEX Usage |
|---------|--------------|--------------|
| **Mediator** | `mediator-orchestration.yaml` | MasterOrchestrator's coordination model — all orchestrators communicate through the mediator, never directly |
| **Strategy** | `strategy-workflow.yaml` | Intelligence tier's strategy selection — Reasoning picks the best approach from a ranked set |
| **Observer** | `observer-event-bus.yaml` | URS reinforcement signals — orchestrators emit events, learning surfaces consume them |
| **Factory** | `factory-creation.yaml` | FileFactory (CORE-028 enforcement), GoldenScenario factory, MCP tool registration |
| **Template Method** | `template-method-lifecycle.yaml` | OrchestratorProtocolMixin's 5-step lifecycle — setup → govern → execute → validate → teardown |
| **Chain of Responsibility** | `chain-of-responsibility-governance.yaml` | EnforcementOrchestrator's 10-agent chain — each agent checks its rules and passes to the next |
| **Adapter** | `adapter-mcp.yaml` | MCP tool adapters — ConsolidatedTool base class adapts orchestrator interfaces to MCP JSON-RPC |
| **Repository** | `repository-registry.yaml` | cortex-registry as a repository of YAML-backed configurations — rules, templates, knowledge |
| **Command** | `command-workflow-step.yaml` | WorkflowEngine step execution — each step is a command object with execute/undo/validate |

---

## Pattern Detection

When CORTEX analyses a repository (via `/onboard` or LENS), the Perception tier at `cortex/intelligence/perception/` scans for pattern signatures:

1. **File structure scan** — directory layout, naming conventions, module organization
2. **Import analysis** — dependency patterns, circular imports, layer violations
3. **AST analysis** — class hierarchies, method signatures, decorator usage
4. **Naming conventions** — `*Factory`, `*Observer`, `*Handler`, `*Service`, `*Repository`

Each detected pattern receives a confidence score between 0.0 and 1.0:

| Confidence | Meaning |
|-----------|---------|
| ≥ 0.9 | Strong match — pattern is clearly implemented |
| 0.7–0.89 | Likely match — most signals present |
| 0.5–0.69 | Partial match — some signals, missing others |
| < 0.5 | Weak match — insufficient evidence |

The output is a **PatternMatch** containing: matched fields, missing fields, confidence score, and associated risk factors.

---

## Knowledge Architecture

### Two Knowledge Stores

CORTEX maintains two complementary knowledge stores:

| Store | Location | Purpose |
|-------|----------|---------|
| **Knowledge Base** | `cortex-registry/knowledge-base/` | Static reference knowledge — security rules, architecture best practices, compliance rules, domain profiles |
| **Knowledge Library** | `cortex-registry/knowledge/` | SDLC and domain knowledge — analysis patterns, test strategies, security-by-design, stack-specific knowledge |

### Knowledge Base Structure

```
cortex-registry/knowledge-base/
├── architecture/              ← Architecture best practices
├── governance/                ← Security, development, compliance, operations, data rules
├── profiles/                  ← Domain profiles (DevOps, Security, FinOps, ML, Healthcare, Auth, Legal)
├── repositories/              ← Per-repository knowledge (CORTEX, BadMonolith, KSessions)
└── security/                  ← OWASP Top 10, secrets patterns, CI/CD hardening
```

### Knowledge Library Structure

```
cortex-registry/knowledge/
├── architecture/              ← Design patterns, SOLID principles, anti-patterns, refactoring standards
├── backend-python/            ← Python clean code, refactoring, code review
├── devops-infrastructure/     ← Monitoring, observability
├── sdlc/                      ← Full SDLC knowledge (see SDLC Workflow Engine doc)
│   ├── analysis-design-patterns.yaml
│   ├── test-strategy-selection.yaml
│   ├── security-by-design.yaml
│   ├── code-review-checklist.yaml
│   └── stack-specific/        ← Per-language knowledge (Python, TypeScript, .NET, HTML/CSS)
├── security/                  ← Secure coding practices
└── testing-validation/        ← TDD best practices
```

### Knowledge Resolution

When a workflow template requests knowledge, the resolution follows a strict priority:

```
1. Company overrides (always win)
2. Stack-specific (e.g., Python-stack rules)
3. SDLC phase knowledge (e.g., design patterns)
4. Domain knowledge (e.g., architecture)
5. Generic knowledge (baseline)
```

This ensures team-specific rules take precedence while still providing comprehensive defaults.

---

## How Patterns and Knowledge Work Together

Consider a request to "refactor the payment service":

1. **LENS** scans the payment service codebase
2. **Perception** detects: Repository pattern (0.92 confidence), Strategy pattern (0.78), no Factory pattern (0.12)
3. **Knowledge injection** loads: `architecture/refactoring-quality-standards.yaml`, `backend-python/refactoring.yaml`, company API standards
4. **Reasoning** selects strategy: "extract-service-with-tdd" (highest historical success rate for Repository-pattern repos)
5. **Action** builds execution plan: write tests → extract payment logic → apply Factory where missing → validate governance

The patterns detected in step 2 directly influence the strategy selected in step 4. The knowledge injected in step 3 provides the specific rules and best practices that guide the refactoring. This is intelligence-driven development — not template-based code generation.

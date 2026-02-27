---
title: SDLC Workflow Engine — Full Lifecycle Intelligence
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/domain/sdlc_workflow_orchestrator.py + cortex-registry/workflows/templates/sdlc/ + cortex-registry/knowledge/sdlc/
order: 16
---

# SDLC Workflow Engine — Full Lifecycle Intelligence

> **CORTEX doesn't just write code — it runs your entire software development lifecycle.** From requirements analysis through security assessment to release readiness, every SDLC phase is codified as a YAML workflow template, hydrated with domain knowledge, and executed through a finite state machine.

---

## The Problem SDLC Intelligence Solves

Traditional SDLC tools treat each phase in isolation: a requirements tool, a design tool, a CI tool, a testing tool. Knowledge doesn't flow between phases. A security requirement captured in analysis is forgotten by the time implementation begins.

CORTEX's SDLC Workflow Engine treats the entire lifecycle as a **single coordinated pipeline** where:

- Knowledge from analysis flows into design decisions
- Design decisions flow into implementation constraints
- Implementation is validated against the original requirements
- Security is not a phase — it's a gate at every phase

---

## Seven SDLC Workflow Templates

Each phase of the SDLC has a dedicated workflow template in `cortex-registry/workflows/templates/sdlc/`:

| Phase | Template | Trigger Intents | Response Block |
|-------|----------|----------------|----------------|
| **1. Requirements Analysis** | `requirements-analysis.yaml` | ANALYZE, INVESTIGATE, REQUIREMENTS, SCOPE | BLOCK-ANALYSIS |
| **2. Solution Design** | `solution-design.yaml` | DESIGN, ARCHITECTURE, PLAN, PROPOSE | BLOCK-DESIGN-DECISION |
| **3. Implementation** | `implementation-execution.yaml` | IMPLEMENT, BUILD, CREATE, ADD_FEATURE | BLOCK-CODE-REVIEW |
| **4. Code Review** | `code-review-gate.yaml` | REVIEW, FIX | BLOCK-CODE-REVIEW |
| **5. Integration Verification** | `integration-verification.yaml` | INTEGRATION_TEST, VERIFY_INTEGRATION | BLOCK-INTEGRATION |
| **6. Security Assessment** | `security-assessment.yaml` | SECURITY_AUDIT, THREAT_MODEL, VULNERABILITY_SCAN | BLOCK-SECURITY |
| **7. Release Readiness** | `release-readiness.yaml` | RELEASE, DEPLOY, RELEASE_GATE | BLOCK-RELEASE |

---

## How the Engine Works

### Step 1 — Intent to Template Selection

The `SDLCWorkflowOrchestrator` at `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py` receives a classified intent from MasterOrchestrator. It maps the intent to the best SDLC template using an internal registry:

```
User says "analyze the auth module"
  → IntentRouter classifies: ANALYZE
  → SDLCWorkflowOrchestrator selects: sdlc-requirements-analysis
```

### Step 2 — Knowledge Hydration

Each template declares a `knowledge_context` section that specifies which knowledge YAMLs to inject:

- **Primary knowledge** — the core SDLC knowledge for this phase (e.g., `sdlc/analysis-design-patterns.yaml`)
- **Supplementary knowledge** — cross-cutting concerns (e.g., `sdlc/security-by-design.yaml`, `architecture/engineering-design-patterns.yaml`)
- **Company overrides** — team-specific standards that always win conflicts (e.g., `company/domains/api-standards.yaml`)
- **Stack-specific** — language/framework knowledge (e.g., `sdlc/stack-specific/python-stack.yaml`, `sdlc/stack-specific/typescript-stack.yaml`)

Resolution order: **stack-specific > sdlc > domain > generic**

### Step 3 — FSM Execution

The WorkflowEngine executes the template steps through a **finite state machine (FSM)**. Each step:

1. Invokes a workflow primitive (e.g., `primitives/analysis/lens-ast-scan.yaml`)
2. Passes inputs from the previous step's outputs
3. Validates governance gates
4. Records audit trail via AC markers

### Step 4 — Reinforcement Learning

Results feed into the `UniversalLearningLoop` for pattern capture. Successful SDLC executions increase confidence scores on the templates and knowledge used.

---

## Knowledge Base Architecture

The SDLC knowledge base lives in `cortex-registry/knowledge/sdlc/`:

| Knowledge File | Purpose |
|---------------|---------|
| `analysis-design-patterns.yaml` | Requirements analysis and design pattern selection |
| `test-strategy-selection.yaml` | Test strategy decision matrix |
| `security-by-design.yaml` | Security-first design principles |
| `code-review-checklist.yaml` | Code review quality gates |
| `documentation-strategy.yaml` | Documentation standards and coverage |
| `integration-strategy.yaml` | Integration testing approaches |
| `stack-specific/python-stack.yaml` | Python-specific SDLC knowledge |
| `stack-specific/typescript-stack.yaml` | TypeScript-specific SDLC knowledge |
| `stack-specific/dotnet-stack.yaml` | .NET-specific SDLC knowledge |
| `stack-specific/html-css-stack.yaml` | Frontend-specific SDLC knowledge |

---

## Security-First Mindset

Security is not a separate SDLC phase in CORTEX — it is a **gate at every phase**:

| Phase | Security Gate |
|-------|--------------|
| Requirements | Threat surface identification in scope analysis |
| Design | Security-by-design patterns from `security-by-design.yaml` |
| Implementation | SAST scanning via SecurityVulnerabilityOrchestrator |
| Code Review | Credential scan, PII detection via SanitizationOrchestrator |
| Integration | Security integration tests, dependency CVE scanning |
| Security Assessment | Full OWASP Top 10 audit, threat model analysis |
| Release | Release security checklist, secret rotation verification |

The `SecurityVulnerabilityOrchestrator` at `cortex/orchestrators/validation/security_vulnerability_orchestrator.py` coordinates SAST scanning, CVE detection, and remediation. The `SanitizationOrchestrator` at `cortex/orchestrators/git/sanitization_orchestrator.py` handles secret scanning, PII removal, and branch hygiene.

---

## Workflow Primitives

SDLC templates compose from reusable primitives in `cortex-registry/workflows/templates/primitives/`:

| Category | Primitives | Purpose |
|----------|-----------|---------|
| **Analysis** | `lens-ast-scan.yaml`, `lens-vision-scan.yaml` | LENS-powered codebase analysis |
| **Execution** | `audit-trace.yaml`, `file-extraction.yaml`, `semantic-edit.yaml` | Code modification and audit |
| **Governance** | `sweep-catalogue-open.yaml`, `sweep-catalogue-close.yaml`, `dependency-guard-migration.yaml` | CORE-064 sweep lifecycle |
| **Validation** | `detect-fix-rescan-loop.yaml`, `regression-test.yaml`, `duplicate-detection.yaml` | Quality assurance primitives |
| **Intelligence** | `intelligence-injection.yaml` | Knowledge context hydration |

These primitives are the atomic building blocks. SDLC templates compose them into higher-order workflows.

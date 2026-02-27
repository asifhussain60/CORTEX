# Knowledge Hydration — How Intelligence Flows Into Workflows
# The knowledge resolution pipeline from YAML sources to execution context

```
 ═══════════════════════════════════════════════════════════════════════════════
  KNOWLEDGE HYDRATION PIPELINE
 ═══════════════════════════════════════════════════════════════════════════════

  How SDLC workflow templates receive intelligence from the knowledge base

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         USER REQUEST                                   │
  │                   "implement auth service"                             │
  └─────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    INTENT CLASSIFICATION                                │
  │              IntentRouter → IMPLEMENT → SDLCWorkflowOrchestrator        │
  └─────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    TEMPLATE SELECTION                                   │
  │            sdlc-implementation-execution.yaml                          │
  └─────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    KNOWLEDGE HYDRATION                                  │
  │                                                                         │
  │  ┌─────────────────────────────────────────────────────────────────┐    │
  │  │  RESOLUTION ORDER (highest priority wins)                      │    │
  │  │                                                                 │    │
  │  │  ┌─────────────────────────────────┐                           │    │
  │  │  │ 1. COMPANY OVERRIDES            │ ← company/domains/*.yaml  │    │
  │  │  │    API standards, security rules │    (always wins conflicts)│    │
  │  │  └────────────────┬────────────────┘                           │    │
  │  │                   ▼                                             │    │
  │  │  ┌─────────────────────────────────┐                           │    │
  │  │  │ 2. STACK-SPECIFIC               │ ← sdlc/stack-specific/   │    │
  │  │  │    Python, TypeScript, .NET,     │    python-stack.yaml      │    │
  │  │  │    HTML/CSS patterns             │                           │    │
  │  │  └────────────────┬────────────────┘                           │    │
  │  │                   ▼                                             │    │
  │  │  ┌─────────────────────────────────┐                           │    │
  │  │  │ 3. SDLC PHASE                   │ ← sdlc/*.yaml            │    │
  │  │  │    Test strategy, design patterns│    test-strategy-*.yaml   │    │
  │  │  │    code review checklist         │                           │    │
  │  │  └────────────────┬────────────────┘                           │    │
  │  │                   ▼                                             │    │
  │  │  ┌─────────────────────────────────┐                           │    │
  │  │  │ 4. DOMAIN                        │ ← architecture/*.yaml    │    │
  │  │  │    Design patterns, SOLID, anti- │    engineering-*.yaml     │    │
  │  │  │    patterns, refactoring rules   │                           │    │
  │  │  └────────────────┬────────────────┘                           │    │
  │  │                   ▼                                             │    │
  │  │  ┌─────────────────────────────────┐                           │    │
  │  │  │ 5. GENERIC                       │ ← testing-validation/    │    │
  │  │  │    TDD best practices, security  │    security/              │    │
  │  │  │    practices, clean code         │    backend-python/        │    │
  │  │  └─────────────────────────────────┘                           │    │
  │  └─────────────────────────────────────────────────────────────────┘    │
  │                                                                         │
  └─────────────────────────────────┬───────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    HYDRATED EXECUTION CONTEXT                          │
  │                                                                         │
  │  Template steps execute with full knowledge:                            │
  │  • LENS workspace model (codebase understanding)                       │
  │  • SDLC phase knowledge (what to do)                                   │
  │  • Stack-specific rules (how to do it for Python)                      │
  │  • Company standards (team-specific constraints)                       │
  │  • Security-by-design knowledge (security gates)                       │
  │  • TDD best practices (test strategy)                                  │
  └─────────────────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  KNOWLEDGE STORE ARCHITECTURE
 ═══════════════════════════════════════════════════════════════════════════════

  cortex-registry/
  ├── knowledge/                        ← SDLC & domain knowledge (hydrated into templates)
  │   ├── sdlc/                        ← 7-phase SDLC knowledge
  │   │   ├── analysis-design-patterns.yaml
  │   │   ├── test-strategy-selection.yaml
  │   │   ├── security-by-design.yaml
  │   │   ├── code-review-checklist.yaml
  │   │   ├── integration-strategy.yaml
  │   │   ├── documentation-strategy.yaml
  │   │   └── stack-specific/          ← Per-language knowledge
  │   │       ├── python-stack.yaml
  │   │       ├── typescript-stack.yaml
  │   │       ├── dotnet-stack.yaml
  │   │       └── html-css-stack.yaml
  │   ├── architecture/                ← Design patterns, SOLID, anti-patterns
  │   ├── backend-python/              ← Python-specific clean code, refactoring
  │   ├── security/                    ← Secure coding practices
  │   ├── testing-validation/          ← TDD best practices
  │   └── devops-infrastructure/       ← Monitoring, observability
  │
  └── knowledge-base/                  ← Static reference knowledge
      ├── architecture/                ← Architecture best practices
      ├── governance/                  ← Security, development, compliance rules
      ├── profiles/                    ← Domain profiles (DevOps, FinOps, ML, etc.)
      ├── repositories/               ← Per-repo knowledge (CORTEX, BadMonolith)
      └── security/                   ← OWASP, secrets, CI/CD hardening
```

**Source:** `cortex-registry/knowledge/` · `cortex-registry/knowledge-base/` · `cortex/orchestrators/domain/sdlc_workflow_orchestrator.py`
**Primitive:** `cortex-registry/workflows/templates/primitives/intelligence/intelligence-injection.yaml`

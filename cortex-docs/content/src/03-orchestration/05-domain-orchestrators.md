# Domain Orchestrators

---
title: Domain Orchestrators — Specialist Capability Engines
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-18
source_of_truth: cortex/orchestrators/ + cortex/domain_orchestrators/ + cortex/__wiring_contract__.yaml
format: diátaxis-explanation
voice: third-person-blended
phase: Production (v8.1)
order: 5
---

> **Role:** Domain orchestrators provide deep expertise in specialised areas — refactoring, planning, conversation, domain business logic, and education. They are invoked by the MasterOrchestrator when a request requires capabilities beyond core TDD or governance.

---

## Overview

While core orchestrators handle universal workflows (implement, route, enforce), domain orchestrators handle **specialised requests** that require expert knowledge in a specific area.

```
MasterOrchestrator
        │
        ├── Core Orchestrators (Priority 20–80)
        │   └── TDD, Enforcement, Workflow, etc.
        │
        └── Domain Orchestrators (Priority 60–95)
            ├── RefactoringOrchestrator   (60)
            ├── PlanningOrchestrator      (75)
            ├── ConversationOrchestrator  (90)
            └── DomainOrchestrator        (95)
```

---

## RefactoringOrchestrator (Priority 60)

**Trigger intent:** `REFACTOR`  
**Source:** `cortex/refactoring/`

Applies semantic code improvements without changing external behaviour. Supports 3 languages with dedicated adapters:

| Language | Adapter | Operations |
|----------|---------|------------|
| Python | Rope | Extract method, rename, move, inline |
| C# | Roslyn | Extract class, rename symbol, introduce variable |
| TypeScript / JS | TypeScript Compiler API | Extract function, rename, organise imports |

**Workflow:**
1. LENS analysis identifies improvement targets (SOLID violations, duplication, complexity)
2. Challenge gate presents alternative approaches (CORE-048)
3. User selects approach or accepts recommended
4. Semantic refactoring applied — tests must pass before and after
5. Audit marker records what changed and why

**Key rule:** Refactoring that causes test failures is automatically reverted.

---

## PlanningOrchestrator (Priority 75)

**Trigger intent:** `PLAN`, `DESIGN`  
**Source:** `cortex/orchestrators/planning/`

Manages roadmap, phase planning, and architecture design decisions.

**Capabilities:**
- Generate phased implementation plans from high-level requests
- Decompose epics into auditable phases with DoR (Definition of Ready) criteria
- Estimate effort using historical velocity from LENS git history analysis
- Update `cortex-registry/planning/master-cortex-plan.yaml` on phase completion
- ROI scoring: calculate expected return on proposed changes

**Output format:** Structured phase plan with:
- DoR checklist
- Acceptance criteria
- Risk score
- Effort estimate (P50/P95)
- Dependency map

---

## ConversationOrchestrator (Priority 90)

**Trigger intent:** `QUERY`, `DIGEST`, `EXPLORATORY`  
**Source:** `cortex/orchestrators/conversation/`

Handles dialogue-style interactions that do not produce code output.

**Modes:**

| Mode | Trigger | Output |
|------|---------|--------|
| Educational | "explain", "how does" | Progressive disclosure (overview → detail) |
| Verification | "is it true that", "verify" | Evidence-based answer with code references |
| Exploratory | Open question | Conversational, no strict format |
| Digest | "summarise", "summarize" | Synthesised knowledge from multiple sources |

The ConversationOrchestrator always checks the knowledge base (`cortex-registry/knowledge-base/`) before generating a response, preferring documented facts over inference.

---

## DomainOrchestrator (Priority 95)

**Trigger intent:** Domain-specific patterns detected by LENS  
**Source:** `cortex/domain_orchestrators/` + `cortex_lens/domain_inference/`

Applies framework-specific intelligence beyond generic code analysis:

| Domain | Capabilities |
|--------|-------------|
| .NET / C# | Roslyn analysis, NuGet dependency audit, async pattern detection |
| Angular | Component structure, module boundaries, observable chain analysis |
| React | Hook rule enforcement, component decomposition, state management patterns |
| Vue | Composition API migration, template complexity scoring |
| Python | Type hint coverage, dataclass patterns, async safety |

Domain intelligence is loaded conditionally — only the adapters relevant to the detected languages in the repository are activated (reduces cold-start overhead by ~40%).

---

## Unified Support Orchestrators

Four consolidated orchestrators handle cross-cutting concerns that were previously fragmented:

| Orchestrator | Priority | Consolidates | Purpose |
|---|---|---|---|
| UnifiedOnboardingOrchestrator | 100 | Setup + Onboarding + Tutorial | Repository initialisation and LENS baseline |
| UnifiedAnalysisOrchestrator | 115 | LENS + Tools + AST | Code intelligence aggregation |
| UnifiedQualityAssuranceOrchestrator | 120 | Governance + Enforcement + Audit | Standards enforcement |
| UnifiedDiscoveryOrchestrator | 125 | Documentation + Search + Catalog | Feature and knowledge exploration |

These replaced 12 separate orchestrators during the Phase 93 consolidation, reducing tool surface area by 54% while retaining all capabilities.

---

## Deprecated Orchestrators

Seven orchestrators reached end-of-life and were absorbed into unified replacements. They remain active until **2026-03-31** (sunset date):

| Deprecated | Absorbed Into |
|-----------|--------------|
| LENSOrchestrator | UnifiedAnalysisOrchestrator |
| ToolDiscoveryOrchestrator | UnifiedAnalysisOrchestrator |
| DocumentationOrchestrator | UnifiedDiscoveryOrchestrator |
| ChallengeEngine | UnifiedQualityAssuranceOrchestrator |
| OnboardingOrchestrator | UnifiedOnboardingOrchestrator |
| EducationalOrchestrator | UnifiedDiscoveryOrchestrator |
| RecommendationGate | IntelligenceOrchestrator |

After the sunset date, any call to a deprecated orchestrator returns a `410 Gone` error with a migration pointer.

---

## Related Documents

- **[Orchestration Overview](./01-overview.md)** — Full registry and priority table
- **[Master Orchestrator](./02-master-orchestrator.md)** — How domains are invoked
- **[TDD Orchestrator](./04-tdd-orchestrator.md)** — Core implementation engine
- **[LENS Overview](../02-lens/01-overview.md)** — Intelligence layer domain adapters

---

*Last verified: 2026-02-18 | Source: cortex/orchestrators/ + cortex/domain_orchestrators/*

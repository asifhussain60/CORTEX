# AI & Intelligence Capabilities

---
title: CORTEX AI & Intelligence — LENS + Brain Architecture
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-25
source_of_truth: cortex/lens/ + cortex/intelligence/provider.py
order: 3
---

> **Brain analogy:** The Intelligence layer is CORTEX's **cerebral cortex** — the wrinkled outer layer responsible for all higher-order thinking. LENS is the sensory cortex (processing raw input), and the Brain tiers are the association cortex (making sense of it all).

> **Notice:** Intelligence capabilities represent system design intentions. Actual analysis accuracy, performance, and insights depend on codebase characteristics, language ecosystems, comment quality, and repository history. Organizations should validate intelligence outputs against their specific code patterns and development practices.

---

## Overview: Multi-Layer Intelligence Architecture

CORTEX's AI and intelligence capabilities transform raw code repositories into actionable development insights through three interconnected systems [Business Leaders]. Product teams leverage these capabilities for architecture analysis, technical debt assessment, and dependency management across multi-language codebases [Product Owners]. The intelligence layer provides developers with real-time code understanding, pattern detection, security analysis, and contextual recommendations during implementation workflows [Software Developers].

**Intelligence Architecture Layers:**

1. **LENS Engine** — Multi-analyzer code intelligence with parallel execution (9 specialized analyzers)
2. **Context Synthesis** — `UnifiedIntelligenceProvider` aggregates LENS output, company domain knowledge, and ADO sprint context
3. **Knowledge Repository** — Git-backed knowledge base (45+ best practice YAMLs) with tier precedence (company > tier1 > tier0)
4. **Domain Intelligence** — Framework-specific analyzers (.NET/Roslyn, Angular, React, Vue, Python)
5. **Company Domain Layer** — `company/domains/*.yaml` profiles activate domain-specific rules and priorities

These systems operate in concert to provide orchestrators with evidence-based context for test generation, implementation guidance, refactoring decisions, and architecture validation.

---

## Two Pillars of Intelligence

### 1. LENS — The Sensory System

**L**anguage → **E**xamination → **N**avigation → **S**ynthesis

LENS (`cortex/lens/`) runs **9 specialized analyzers in parallel** against any codebase:

| Analyzer | Brain Equivalent | What It Detects | Speed |
|----------|-----------------|-----------------|-------|
| **AST** | Visual cortex | Code structure, classes, functions, imports | <100ms |
| **Git History** | Episodic memory | Change frequency, hot spots, author patterns | <200ms |
| **Comment** | Language center | Documentation gaps, TODO density | <50ms |
| **Import** | Connectivity maps | Dependency graph, circular imports | <100ms |
| **Security** | Threat detection | SQL injection, XSS, credentials, CVEs | <200ms |
| **Pattern** | Pattern recognition | Framework signatures, architecture styles | <150ms |
| **Metrics** | Quantitative reasoning | Complexity, coupling, LOC | <100ms |
| **Domain** | Contextual awareness | Business domain (finance, healthcare, etc.) | <100ms |
| **TechStack** | Environment awareness | Runtime versions, dependency stacks, build tools | <80ms |

**Combined latency:** 300–800ms for a full 9-analyzer scan.

**Business Leader:** "Imagine every code change getting an automatic MRI — LENS scans 9 dimensions simultaneously and delivers a comprehensive health report in under a second."

**Product Owner:** "I can see at a glance which modules are high-complexity, which have security findings, and which lack documentation. No manual review needed."

---

## LENS Intelligence Engine

### What is LENS?

LENS stands for **L**anguage → **E**xamination → **N**avigation → **S**ynthesis. Organizations benefit from this four-stage intelligence cycle that transforms code into structured understanding suitable for automated decision-making [Business Leaders]. The LENS pipeline processes code repositories through progressive stages of analysis, from lexical parsing to semantic synthesis [Software Developers].

**Developer:** "I run `cortex_onboard_repository` and get AST structure, security scan, dependency graph, complexity metrics, and tech stack detection — all in one pass. It's like having 9 specialized review tools consolidated into one."

### 2. Brain Tiers — The Decision System

After LENS processes the raw data, the `UnifiedIntelligenceProvider` (`cortex/intelligence/provider.py`) synthesizes it:

| Tier | Method | Company Knowledge | Latency |
|------|--------|------------------|---------|
| **Quick** | `provider.quick()` | No | <10ms |
| **Targeted** | `provider.targeted()` | Yes — domain profiles loaded | <100ms |
| **Full** | `provider.full()` | Yes + ADO sprint context + KG indexing | 300–800ms |

See `00-getting-started/04-brain-tier-architecture.md` for the deep dive.

---

## How LENS and Brain Work Together

```
[Source Code]
      │
      ▼
[LENS: 9 Parallel Analyzers]  ← 300-800ms
      │
      ├── AST structure
      ├── Security findings
      ├── Complexity metrics
      ├── Dependency graph
      ├── Git hot spots
      ├── Documentation gaps
      ├── Pattern signatures
      ├── Domain context
      └── Tech stack detection
      │
      ▼
[UnifiedIntelligenceProvider]
      │
      ├── Company Domain Layer (company/domains/*.yaml)
      ├── ADO Sprint Context  (WorkItemProvider → ADOContextMapper)
      └── KG Indexing         (KnowledgeIndexer.index_registry_yaml)
      │
      ▼
[Orchestrator Execution]   ← RED → GREEN → REFACTOR
```

## Intelligence Subsystems

| Subsystem | Location | Purpose |
|-----------|----------|---------|
| **Domain Brain** | `cortex/intelligence/domain_brain/` | Business-vertical intelligence (ecommerce, finance, healthcare) |
| **Learning** | `cortex/intelligence/learning/` | Pattern capture, confidence updates, reinforcement signals (URS) |
| **Knowledge** | `cortex/intelligence/knowledge/` | Knowledge synthesis from registry and learned patterns |
| **Quality** | `cortex/intelligence/quality/` | Code quality assessment |
| **Governance** | `cortex/intelligence/governance/` | Intelligence-layer governance checks |
| **Infrastructure** | `cortex/intelligence/infrastructure/` | InfrastructureDetector for platforms, Docker, K8s |
| **Observability** | `cortex/intelligence/observability/` | Intelligence metrics and monitoring |

---

## Core LENS Analyzers (9 Parallel Execution)

CORTEX employs nine specialized analyzers executing in parallel to provide comprehensive code intelligence:

| Analyzer | Analysis Target | Key Outputs | Language Support |
|----------|----------------|-------------|------------------|
| **AST Analyzer** | Syntax structure | Functions, classes, methods, parameters, return types, complexity metrics | Python, TypeScript, JavaScript, C#, Java |
| **Git History Analyzer** | Version control (24h) | Recent commits, authors, file churn, hotspot detection, change frequency | Universal (git-agnostic) |
| **Comment Analyzer** | Documentation | TODOs, FIXMEs, docstrings, inline comments, annotation extraction | Multi-language (regex + AST) |
| **Import Analyzer** | Dependencies | Import statements, module usage, circular dependencies, unused imports | Python, TypeScript, JavaScript, C# |
| **Security Analyzer** | OWASP patterns | SQL injection vectors, XSS vulnerabilities, authentication issues, secrets detection | Python, TypeScript, JavaScript |
| **Pattern Analyzer** | Design patterns | Singleton, Factory, Observer, Strategy, adapter detection, anti-patterns | Python, TypeScript, C# |
| **Metrics Analyzer** | Quantitative metrics | Cyclomatic complexity, Halstead metrics, maintainability index, test coverage | Python, TypeScript, JavaScript |
| **Domain Analyzer** | Framework specifics | .NET (Roslyn-based), Angular (component analysis), React (hook patterns), Vue | Framework-specific plugins |
| **TechStack Analyzer** | Runtime environment | Language version, dependency manager, build tools, Docker/K8s presence | Universal |

**Analyzer Coordination Architecture:**

Analyzers execute asynchronously with dependency-aware sequencing:
- **Iteration 1 (parallel, no dependencies):** Git History, Comment, Import, TechStack
- **Iteration 2 (requires AST):** Security, Pattern, Metrics
- **Iteration 3 (requires domain detection):** Domain-specific analyzers
- **Iteration 4 (aggregation):** LENSSynthesis combines all results

**Performance Characteristics:**

| Repository Size | Analyzer Execution | Cache Hit Rate | Typical Latency |
|-----------------|-------------------|----------------|-----------------|
| Small (< 10K LOC) | All 9 analyzers | 60-70% | 300-500ms |
| Medium (10-50K LOC) | All 9 analyzers | 65-75% | 500-800ms |
| Large (50-100K LOC) | All 9 analyzers | 70-80% | 800-1200ms |
| Very Large (> 100K LOC) | Selective (7 core) | 75-85% | 1200-2000ms |

> **Notice:** Performance measurements reflect internal testing. Production results depend on CPU cores available for parallel execution, repository complexity, file change frequency, and cache warm-up state.

---

## Context Synthesis

### Purpose

Context Synthesis aggregates intelligence from multiple sources into a unified context that orchestrators can use for decision-making.

### Synthesis Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT SYNTHESIS ENGINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Inputs:                                                        │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│   │   LENS   │  │ Knowledge│  │  Domain  │  │  Session │      │
│   │ Analysis │  │Repository│  │  Brain   │  │ Context  │      │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│        │             │             │             │              │
│        └─────────────┴──────┬──────┴─────────────┘              │
│                             ▼                                    │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                  SYNTHESIS PIPELINE                      │  │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐│  │
│   │  │ Merge      │─▶│ Prioritize │─▶│ Generate Unified   ││  │
│   │  │ Sources    │  │ Signals    │  │ Intelligence Context││  │
│   │  └────────────┘  └────────────┘  └────────────────────┘│  │
│   └─────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│   Output:                                                        │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │           UnifiedIntelligenceContext                     │  │
│   │  • file_context    • domain_knowledge                    │  │
│   │  • git_insights    • governance_rules                    │  │
│   │  • dependencies    • recommendations                     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Unified Intelligence Context

```python
@dataclass
class UnifiedIntelligenceContext:
    """
    Unified context for orchestrator decision-making.
    
    Aggregates LENS analysis, knowledge base, and session context
    into a single coherent view.
    """
    # LENS-derived
    file_context: Dict[str, Any]       # File structure and content
    git_insights: Dict[str, Any]       # History and authorship
    dependencies: List[str]            # Detected dependencies
    patterns: List[str]                # Detected patterns
    
    # Knowledge-derived
    domain_knowledge: Dict[str, Any]   # Domain-specific knowledge
    best_practices: List[str]          # Applicable best practices
    governance_rules: List[str]        # Applicable governance rules
    
    # Synthesized
    recommendations: List[str]         # AI-generated recommendations
    risk_factors: List[str]            # Identified risks
    confidence_score: float            # Synthesis confidence (0.0-1.0)
```

### Synthesis Performance

| Metric | Target | Typical |
|--------|--------|---------|
| **Synthesis Time** | < 200ms | 120ms |
| **Cache Hit Rate** | > 70% | 75% |
| **Context Size** | < 20KB | 15KB |
| **Source Count** | 4-6 | 5 |

---

## Pattern Detection

### Design Pattern Recognition

CORTEX recognizes common design patterns:

| Pattern Category | Patterns Detected |
|-----------------|-------------------|
| **Creational** | Factory, Singleton, Builder, Prototype |
| **Structural** | Adapter, Decorator, Facade, Proxy |
| **Behavioral** | Observer, Strategy, Command, State |
| **Architectural** | MVC, Repository, Service, Gateway |

### Anti-Pattern Detection

CORTEX identifies problematic patterns:

| Anti-Pattern | Detection Method | Severity |
|--------------|------------------|----------|
| **God Class** | Class size > 500 LOC, > 20 methods | High |
| **Spaghetti Code** | Cyclomatic complexity > 15 | High |
| **Feature Envy** | Method accessing other class data excessively | Medium |
| **Duplicate Code** | AST similarity > 80% | Medium |
| **Long Method** | Method > 50 LOC | Low |

### Code Smell Identification

```python
@dataclass
class CodeSmell:
    """Identified code quality issue."""
    
    type: str           # Smell type (e.g., "long_method")
    location: str       # File:line
    severity: str       # low, medium, high
    description: str    # Human-readable explanation
    suggestion: str     # Recommended fix
    
    # Example:
    # CodeSmell(
    #     type="god_class",
    #     location="src/auth.py:1",
    #     severity="high",
    #     description="AuthManager has 45 methods and 800 LOC",
    #     suggestion="Split into AuthenticationService, AuthorizationService"
    # )
```

---

## Knowledge Repository

### Knowledge Structure

```
cortex/intelligence/
├── tier0/          # Core rules (immutable)
│   ├── core-rules.yaml
│   └── security-baseline.yaml
├── tier1/          # Best practices (curated)
│   ├── python-patterns.yaml
│   ├── testing-patterns.yaml
│   └── api-design.yaml
├── tier2/          # Domain knowledge (organization)
│   ├── business-rules.yaml
│   └── compliance-requirements.yaml
└── tier3/          # Learned patterns (AI-generated)
    └── discovered-patterns.yaml
```

### Knowledge Tiers

| Tier | Authority | Mutability | Source |
|------|-----------|------------|--------|
| **Tier 0** | Absolute | Immutable | CORTEX Core |
| **Tier 1** | High | Curated updates | Best practices |
| **Tier 2** | Medium | Organization managed | Domain experts |
| **Tier 3** | Learned | AI-managed | Pattern discovery |

### Knowledge Query API

```python
from cortex.intelligence.knowledge import KnowledgeRepository

repo = KnowledgeRepository()

# Query by domain
python_patterns = repo.query(domain="python", type="patterns")

# Query by file context
applicable_rules = repo.for_file("src/auth.py")

# Query with synthesis
context = repo.synthesize_for_operation(
    operation="implement",
    domain="authentication",
    file_context=lens_context
)
```

---

## Reasoning & Decisioning

### Challenge Generation

The Challenge Engine generates intelligent challenges when it detects potential issues:

```python
@dataclass
class Challenge:
    """AI-generated challenge for user consideration."""
    
    type: ChallengeType      # BETTER_SOLUTION, MISSING_CONTEXT, etc.
    category: ChallengeCategory  # TECHNICAL, SECURITY, etc.
    description: str         # What the challenge is
    rationale: str          # Why it matters
    alternatives: List[str]  # Suggested alternatives
    confidence: float       # AI confidence (0.0-1.0)
```

### Challenge Types

| Type | Trigger | Response |
|------|---------|----------|
| **BETTER_SOLUTION** | Alternative approach detected | Present alternatives |
| **MISSING_CONTEXT** | Insufficient information | Request clarification |
| **SECURITY_RISK** | Security concern identified | Require acknowledgment |
| **PERFORMANCE_CONCERN** | Performance issue predicted | Suggest optimization |

### Confidence Scoring

```python
def calculate_confidence(
    lens_context: LENSContext,
    knowledge_match: float,
    historical_success: float
) -> float:
    """
    Calculate confidence score for routing decision.
    
    Factors:
    - LENS context completeness (0.3 weight)
    - Knowledge base match quality (0.4 weight)
    - Historical success rate (0.3 weight)
    """
    return (
        lens_context.completeness * 0.3 +
        knowledge_match * 0.4 +
        historical_success * 0.3
    )
```

---

## Learning & Feedback

### Unified Reinforcement Signal (URS) — Phase 83

CORTEX now operates a **closed-loop learning system**. When orchestrators complete operations, they emit reinforcement signals that adjust pattern confidence — closing the gap between "we captured a pattern" and "we know whether the pattern works."

**Signal Types:**

| Signal | Score | Example |
|--------|-------|---------|
| `STRONG_REWARD` | +1.0 | Test passes on first try, zero governance violations |
| `MILD_REWARD` | +0.5 | Partial success, P2-only warnings, instruction used |
| `NEUTRAL` | 0.0 | Informational only, instruction ignored |
| `MILD_PUNISHMENT` | -0.5 | Partial failure, P0 violations present |
| `STRONG_PUNISHMENT` | -1.0 | Complete test failure, critical error |

**Confidence Lifecycle:**

```
Pattern Captured ──▶ Confidence: 0.5 (baseline)
      │
      ▼
Orchestrator emits REWARD ──▶ Confidence += (score × 0.1)
      │
      ▼
3+ rewards, confidence ≥ 0.9 ──▶ PROMOTE to T1 knowledge tier
      │
OR:   ▼
2+ punishments, confidence ≤ 0.3 ──▶ QUARANTINE (excluded from guidance)
      │
OR:   ▼
30 days idle ──▶ DECAY by 0.1 (stale patterns weaken)
      │
CROSS-CUTTING:  ▼
Validated by 3+ orchestrators ──▶ BOOST +0.15 (cross-domain confirmation)
```

**Wired Orchestrators (10 integration surfaces):**

| Orchestrator | Signal Trigger | Example |
|-------------|---------------|---------|
| **OPJMixin** (all orchestrators) | `_opj_record_success/failure` | Success → MILD_REWARD, Failure → MILD_PUNISHMENT |
| **TDDOrchestrator** | TDD cycle completion | GREEN-first-try → STRONG_REWARD, retries → MILD_REWARD, failure → MILD_PUNISHMENT |
| **EnforcementOrchestrator** | Governance validation | Zero violations → STRONG_REWARD, warnings only → MILD_REWARD, violations → MILD_PUNISHMENT |
| **TrainerOrchestrator** | `score_and_reinforce()` | Execution success → STRONG_REWARD, errors → STRONG_PUNISHMENT |
| **TestValueScorer** | `recalibrate_from_signals()` | Adjusts severity/likelihood/coverage_gap weights from signal history |
| **KnowledgeSynthesisEngine** | `track_instruction_outcome()` | Used → MILD_REWARD, Ignored → NEUTRAL |
| **IntelligenceMatrixBuilder** | `on_coverage_change()` | Coverage ↑ → MILD_REWARD, Coverage ↓ → MILD_PUNISHMENT |
| **LENSOrchestrator** | `record_analysis_outcome()` | Correct insight → MILD_REWARD, Wrong insight → MILD_PUNISHMENT |

**MCP Access:** `cortex_learning` tool with 6 operations: `emit`, `history`, `decay`, `promote`, `quarantine`, `metrics`.

**Business Leader:** "Every time CORTEX makes a recommendation and it works (or doesn't), the system records that outcome. Over time, patterns that consistently deliver value rise in confidence; patterns that consistently fail are quarantined. It's institutional memory with built-in quality control."

**Product Owner:** "I can see which patterns are performing well across all orchestrators via `cortex_learning(op='metrics')`. Low-confidence patterns are automatically excluded from future guidance — no manual cleanup needed."

**Developer:** "After my TDD cycle succeeds on first try, the TDDOrchestrator emits STRONG_REWARD for the pattern I used. If the same pattern gets rewards from Enforcement and LENS too, it gets a cross-cutting boost. The system literally learns from my workflow."

### Feedback Loop

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   User       │───▶│   CORTEX     │───▶│   Outcome    │
│   Request    │    │   Response   │    │   Feedback   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────┐
│                    LEARNING SYSTEM                    │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│   │  Capture   │─▶│  Reinforce │─▶│  Promote/  │    │
│   │  Pattern   │  │  (URS)     │  │  Quarantine│    │
│   └────────────┘  └────────────┘  └────────────┘    │
└──────────────────────────────────────────────────────┘
```

### Learning Signals (URS-Powered)

| Signal | Weight | URS Mapping | Example |
|--------|--------|-------------|---------|
| **Explicit Approval** | High | STRONG_REWARD | User accepts suggestion |
| **Explicit Rejection** | High | STRONG_PUNISHMENT | User rejects with reason |
| **Implicit Success** | Medium | MILD_REWARD | Tests pass after implementation |
| **Implicit Failure** | Medium | MILD_PUNISHMENT | Tests fail, rollback needed |
| **Neutral/Informational** | Low | NEUTRAL | Instruction ignored, no action taken |

### Pattern Discovery

CORTEX continuously discovers patterns from:

- Successful implementations
- Common refactoring patterns
- Frequently used code structures
- Organization-specific idioms

These patterns are stored in Tier 3 knowledge and validated before promotion.

---

## Performance Metrics

| Capability | Metric | Target | Actual |
|-----------|--------|--------|--------|
| **LENS Analysis** | Time per file | < 500ms | 200ms |
| **Context Synthesis** | Time | < 200ms | 120ms |
| **Pattern Detection** | Accuracy | > 90% | 94% |
| **Challenge Relevance** | User acceptance | > 80% | 82% |
| **Knowledge Retrieval** | Time | < 50ms | 25ms |

---

## Related Documents

- [LENS Overview](../02-lens/01-overview.md) — LENS deep-dive with 9-analyzer table
- [LENS Analyzers](../02-lens/03-analyzers.md) — Individual analyzer docs
- [Context Synthesis](../02-lens/04-synthesis.md) — UnifiedIntelligenceProvider tier model
- [Company Domain Synthesis](../02-lens/05-company-domain-synthesis.md) — Company domain profiles and ADO sprint context
- [Brain Tier Architecture](../00-getting-started/04-brain-tier-architecture.md) — Full intelligence flow diagram

---

*All module paths verified against live codebase · 26 February 2026 · Phase 83 (URS) complete*

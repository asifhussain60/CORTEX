---
title: LENS Intelligence Engine
consolidates:
  - 02-lens-overview.md
  - 02-lens-architecture.md
  - 02-lens-analyzers.md
  - 02-lens-synthesis.md
  - 02-lens-caching.md
  - 02-lens-governance-integration.md
  - 02-lens-company-domain-synthesis.md
last_verified: 2026-02-27
source_of_truth: cortex/lens/ + cortex/intelligence/provider.py
audience: [Business Leaders, Product Owners, Software Developers]
---

# LENS Intelligence Engine

**L**anguage → **E**xamination → **N**avigation → **S**ynthesis

LENS is CORTEX's code intelligence engine. It runs nine specialised analyzers in parallel against any codebase and produces a unified context — structured intelligence that feeds the Brain's Perception → Reasoning → Action pipeline. Combined latency across all nine analyzers: 300–800 milliseconds.

Live location: `cortex/lens/` (analyzers, adapters, cache, models, schemas, discovery, extractors).

---

## The Four Stages

| Stage | What Happens |
|-------|-------------|
| **Language** | Detect programming language, framework, and structural patterns |
| **Examination** | Deep AST analysis, security scan, metric collection |
| **Navigation** | Dependency graph, import chains, call hierarchy |
| **Synthesis** | Combine all analyzer outputs into unified context |

---

## Nine Parallel Analyzers

All nine run concurrently. Total latency is bounded by the slowest analyzer, not the sum.

| Analyzer | What It Detects | Output |
|----------|----------------|--------|
| **AST** | Code structure — classes, functions, imports, decorators, type annotations | Syntax tree, symbol table |
| **Git History** | Change patterns — hot spots, author frequency, recent edits, co-change pairs | Change heatmap, risk indicators |
| **Comment** | Documentation quality — docstring coverage, TODO/FIXME density, comment-to-code ratio | Documentation score, gap list |
| **Import** | Dependencies — circular imports, stale imports, depth, external dependencies | Dependency graph, import health |
| **Security** | Vulnerabilities — SQL injection, XSS, credential exposure, hardcoded secrets, CVEs | Finding list with severity and remediation |
| **Pattern** | Architecture — framework signatures, design pattern usage, enterprise patterns | Pattern match list with confidence scores |
| **Metrics** | Complexity — cyclomatic, coupling, lines of code, maintainability index | Per-function and per-module metric dashboard |
| **Domain** | Business context — industry vertical, regulatory requirements, domain-specific patterns | Domain classification with confidence |
| **Tech Stack** | Framework detection — imports, config files, dependency manifests | Tech stack fingerprint, framework list |

### Analyzer Detail

**AST Analyzer** parses source code into Abstract Syntax Trees. Extracts classes, functions, decorators, imports, type annotations, and structural patterns. Used to understand code structure before refactoring and to identify functions missing type hints (CORE-011).

**Git History Analyzer** analyses git log for change patterns — which files change most, who changes them, when, and in what combinations. Identifies hot spots before a refactor and detects areas of high churn.

**Comment Analyzer** evaluates documentation quality — docstring coverage, TODO/FIXME density, comment-to-code ratio. Used to ensure CORE-012 compliance (docstrings on all public APIs).

**Import Analyzer** maps the dependency graph — circular imports, stale imports, import depth, external dependencies. Detects circular dependencies before they cause runtime issues.

**Security Analyzer** scans for known vulnerability patterns — SQL injection, XSS, credential exposure, hardcoded secrets. Produces findings with Critical, High, Medium, or Low severity plus line numbers and remediation suggestions. Feeds the pre-commit security gate.

**Pattern Analyzer** matches source code against known architecture patterns — framework signatures, design pattern usage, enterprise patterns. Maps to nine canonical patterns in `cortex-registry/patterns/`. Feeds the Brain's Perception tier.

**Metrics Analyzer** computes code quality metrics — cyclomatic complexity, coupling, lines of code, maintainability index. Identifies refactoring candidates and sets quality thresholds.

**Domain Analyzer** detects business domain context — industry (finance, healthcare, ecommerce), regulatory requirements, domain-specific patterns. Routes work to the correct domain orchestrator.

---

## Pipeline Architecture

Location: `cortex/lens/` — approximately twenty modules and subdirectories.

| Component | Location | Purpose |
|-----------|----------|---------|
| Analyzers | `cortex/lens/analyzers/` | Nine specialised analysis engines |
| Adapters | `cortex/lens/adapters/` | Language-specific adapters (Python, TypeScript, C#) |
| Cache | `cortex/lens/cache/` + `cortex/lens/cache.py` | Analysis result caching layer |
| Models | `cortex/lens/models/` | Data models for LENS output |
| Schemas | `cortex/lens/schemas/` | Validation schemas for analyzer output |
| Discovery | `cortex/lens/discovery/` | File and module discovery |
| Extractors | `cortex/lens/extractors/` | Specialised data extraction |
| Templates | `cortex/lens/templates/` | Output formatting templates |
| Orchestrator | `cortex/lens/lens_orchestrator.py` | Main LENS pipeline coordinator |
| Cached Orchestrator | `cortex/lens/cached_lens_orchestrator.py` | Cache-aware pipeline orchestration |
| Facade | `cortex/lens/facade.py` | Simplified consumer API |
| Registry | `cortex/lens/lens_registry.py` | Analyzer registration |
| ML Patterns | `cortex/lens/ml_patterns/` | Machine learning pattern detection |
| .NET Analyzer | `cortex/lens/dotnet_analyzer.py` + `cortex/lens/dotnet/` | .NET-specific analysis |

### Pipeline Flow

Source files are discovered and language is detected. The cached orchestrator checks for cached results keyed by file content hash plus analyzer version. On a cache hit the cached result is returned immediately. On a cache miss all nine analyzers launch in parallel. When all analyzers complete their outputs are merged into a single LENSContext object, stored in the cache, and delivered to the Brain pipeline.

### Cache Strategy

LENS caches analyzer results to avoid redundant computation. Results are keyed by file content hash plus analyzer version.

| Invalidation Trigger | What Happens |
|----------------------|-------------|
| Content change | File hash changes, cache miss, analyzer re-runs |
| Analyzer update | Analyzer version increments, cache miss for affected analyzer |
| Manual clear | Developer forces re-analysis |

---

## Languages Supported

| Language | AST | Security | Metrics | Pattern |
|----------|-----|----------|---------|---------|
| Python | Full | Yes | Yes | Yes |
| TypeScript / JavaScript | Full | Yes | Yes | Yes |
| C# / .NET | Full | Yes | Yes | Yes |
| Angular | Yes | Yes | Yes | Yes |
| React | Yes | Yes | Yes | Yes |
| Vue | Yes | Yes | Yes | Yes |

Adding a new language requires adding an adapter in `cortex/lens/adapters/`. The adapter pattern isolates all language-specific logic.

---

## Synthesis — UnifiedIntelligenceProvider

Synthesis is the final LENS stage. It combines all nine analyzer outputs into a unified LENSContext, then enriches it through the UnifiedIntelligenceProvider at `cortex/intelligence/provider.py` which layers in company domain knowledge, ADO sprint context, and CORTEX best practices.

### Three Execution Tiers

| Tier | Latency | Scope | Typical Use |
|------|---------|-------|-------------|
| **quick()** | Under 200ms | Cached CORE rules plus company domain YAML (TTL cache) | Stage 1 — Interaction |
| **targeted()** | Under 2s | LENS git, AST, and comment analysis plus company domains plus domain profile | IMPLEMENT, FIX, REFACTOR |
| **full()** | Under 10s | All of targeted plus ADO sprint context plus knowledge graph entity indexing plus cross-domain synthesis | Deep investigation analysis |

### LENSContext Contents

| Field | Source Analyzer | Type |
|-------|----------------|------|
| code_structure | AST | Syntax tree, symbols |
| change_patterns | Git History | Heatmap, authors |
| documentation | Comment | Coverage score, gaps |
| dependencies | Import | Graph, circular chains |
| security_findings | Security | Vulnerabilities with severity |
| architecture_patterns | Pattern | Matches with confidence |
| quality_metrics | Metrics | Complexity, coupling |
| domain_context | Domain | Industry, regulations |
| tech_stack | Tech Stack | Framework list, detected tools |

### Sources Per Tier

| Source | Quick | Targeted | Full |
|--------|-------|----------|------|
| CORE governance rules | Yes | Yes | Yes |
| Company domain YAML | Yes | Yes | Yes |
| Knowledge-base domain profiles | — | Yes | Yes |
| Canonical patterns (nine) | — | Yes | Yes |
| ADO sprint context | — | — | Yes |
| Knowledge graph entity indexing | — | — | Yes |

---

## Company Domain Synthesis

Company Domain Synthesis connects organisation-specific knowledge stored in `cortex-registry/company/domains/*.yaml` to the UnifiedIntelligenceProvider pipeline. When LENS analyses a repository, company domain profiles inject domain-specific governance rules, expected architecture patterns, key technologies, and priority signals that change how LENS ranks findings.

### Domain Profile Schema

Each YAML file in `cortex-registry/company/domains/` follows a standard schema:

| Field | Purpose | Example |
|-------|---------|---------|
| id | Unique domain identifier | ecommerce |
| name | Human-readable name | E-Commerce Platform |
| governance_rules | Activated governance rules | PCI-DSS-3.2, OWASP-TOP10, CORE-008 |
| architecture_patterns | Expected patterns | microservices, event-driven, api-gateway |
| key_technologies | Domain technology stack | python, postgresql, redis, stripe-sdk |
| priorities | LENS signal priority boosts | security: high, performance: high |

### Knowledge Precedence

| Precedence | Tier | Source | Mutability |
|-----------|------|--------|------------|
| 1 (highest) | Company | `company/domains/*.yaml` | Organisation managed |
| 2 | Tier 1 | Registry best practices | Curated |
| 3 | Tier 0 | CORTEX core rules | Immutable |
| 4 | Tier 3 | AI-discovered patterns | AI-managed |

Company profiles take precedence for priority and severity annotations but cannot override a CORE rule's enforcement status. Adding a new domain requires only creating a YAML file in the domains directory — the CompanyDomainLoader discovers all files automatically with no code changes and caches results on a five-minute TTL.

---

## ADO Sprint Context Integration

When the `ADO_ORG_URL` environment variable is set, the `full()` tier calls `ADOWorkItemProvider.fetch_user_stories()` and maps the result through `ADOContextMapper` to extract sprint name, story list, open count, and in-progress count. Sprint context is injected into the company knowledge domain rules. When `ADO_ORG_URL` is absent the call is silently skipped.

The combined company domain plus sprint context allows orchestrators to answer questions such as: which PCI-DSS rules apply to the payment service in the current sprint, or whether a service in the ecommerce domain has open security work items.

---

## LENS and Governance Integration

LENS analyzer output directly informs governance enforcement:

| LENS Analyzer | Governance Rule | What Gets Checked |
|---------------|----------------|-------------------|
| AST | CORE-011 (Type Hints) | Functions without type annotations |
| AST | CORE-012 (Docstrings) | Public APIs without docstrings |
| Import | CORE-035 (Single Canonical) | Duplicate imports |
| Security | CORE-013 (Error Handling) | Unhandled exceptions |
| Metrics | CORE-001 (Incremental) | Excessive complexity |
| Comment | CORE-012 (Docstrings) | Documentation coverage below threshold |

The EnforcementOrchestrator's ten agents consume LENS data to make enforcement decisions. Without LENS, governance would be static rule checking. With LENS, it is intelligence-driven — the perception layer feeds the enforcement immune system.

---

*All component paths and analyzer counts verified against live codebase*

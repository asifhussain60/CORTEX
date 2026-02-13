# CORTEX LENS Universal Playbook
**Goal:** Enable CORTEX to reverse‑engineer *any* repository (from small apps like KSESSIONS to enterprise monorepos) into **high‑value visual documentation** for Business Leaders, Product Owners, Architects, Engineers, and Managers—via a **9‑tab LENS Dashboard SPA**.

This playbook generalizes the approach and upgrades it to be scalable, accurate, secure, and consistent with CORTEX’s architecture (gates, orchestrators, wiring, brain tiers, registry phases).

---

## 1) Design Principles (Non‑Negotiable)
### 1.1 High‑value > High‑volume
- Prefer **few “truthy” diagrams** over endless generated UML.
- Prefer **capabilities, workflows, risk, ownership, and dependencies** over raw class lists.

### 1.2 Evidence-first intelligence
Every generated insight must trace back to **evidence**:
- source file(s), symbol(s), endpoint(s), schema object(s), config(s)
- confidence score and extraction method (static parse vs runtime trace vs doc inference)

### 1.3 Multi-layer completeness
LENS must cover:
- **Business** (capabilities, processes, roles, risks)
- **Product** (use cases, journeys, KPIs, backlog surfaces)
- **Engineering** (architecture, dependencies, code health, tests)
- **Infrastructure** (deploy topology, environments, secrets posture)
- **Security** (threat surfaces, vulnerabilities, compliance)

### 1.4 Standardization with extensions
Use a **core schema** for any repo, with optional **adapter extensions** per stack:
- .NET, Java, Node, Python, Go, mobile, data platforms, etc.

---

## 2) What LENS Must Extract (Universal High-Value Set)
### 2.1 “System Map” (C4-style)
**Always output:**
- Context: system boundary + external systems
- Containers: UI, API, services, workers, DBs, queues
- Components: internal service modules + coupling edges
- Deployments: environments, nodes, routing, observability

### 2.2 Capabilities & Use Cases (Business-friendly)
Derive from:
- routes (UI + API)
- service boundaries
- database write patterns
- workflow/state transitions
- docs (README, ADRs), tickets if available

**Output:**
- Capability Map (clustered by domain)
- Use Case Catalog (actor → trigger → steps → data → risks)
- Domain Glossary (ubiquitous language, nouns/verbs)

### 2.3 Domain Model (UML that matters)
- “Core domain model” diagram (20–60 key types)
- Aggregates + invariants + state machines
- DTO/API contract map: Controllers/Handlers → DTOs → Entities → Tables

### 2.4 Data & Integration Truth
- ERD + bounded schema clusters
- Stored procedure/package call graph (if applicable)
- Events/queues/topics if present
- External integrations, auth flows, rate limits

### 2.5 Quality & Engineering Health
- dependency cycles, layering violations
- test coverage shape (unit/integration/e2e)
- performance hotspots (largest endpoints, top queries)
- operational risk (single points of failure)

### 2.6 Security, Compliance, Risk (first-class)
At minimum:
- auth model, roles/claims policies
- secret handling & config posture
- OWASP class issues signals (XSS/CSRF/SSRF/SQLi)
- dependency vulnerability scan results (if available)
- data classification: PII/PHI/PCI indicators

---

## 3) Extraction Pipeline (Scalable, Enterprise-Friendly)
### 3.1 LENS Orchestrated Stages
Use CORTEX phases/gates to enforce correctness:

1. **Inventory**  
   - detect stacks, build systems, entry points, services, DBs  
   - output: `inventory.json`

2. **Structural Parse (Static)**  
   - language-specific AST extraction (Roslyn/TS compiler/Java parser/etc.)  
   - output: `graph/raw/*.jsonl`

3. **Semantic Enrichment**  
   - map to standard entities (Endpoint, Service, Module, Table, Workflow, Rule)  
   - output: `graph/enriched/*.json`

4. **Runtime/Operational Augmentation (Optional, High Value)**  
   - trace sampling (OpenTelemetry logs, request traces), DI wiring dumps, DB query logs  
   - output: `graph/runtime/*.json`

5. **Validation & Gating**  
   - cross-check: UI route → API endpoint exists → handler exists → data touched exists  
   - compute confidence coverage metrics  
   - output: `reports/coverage.json`, `reports/gaps.json`

6. **Visualization Packaging**  
   - compile dashboard API outputs + caches  
   - output: `lens-api/manifest.json` + endpoints data

### 3.2 Extraction Tooling (Adapters)
Adapters should output **the same normalized schema**.

Examples:
- .NET: Roslyn symbol graph, NDepend optional
- Angular/TS: TS compiler API + route graph + Madge module graph
- SQL/Oracle: schema graph + proc dependency extraction
- Cloud/IaC: Terraform/Bicep/Helm/K8s manifests parsing

---

## 4) Data Architecture: One JSON vs Many JSON (Best Practice)
### Recommendation: **Split into a versioned, modular “data bundle”**
**Do not** ship a single monolithic JSON for enterprise repos.

#### 4.1 Folder layout (per repo snapshot)
```
lens-data/
  {repoId}/
    meta/
      manifest.json
      versions.json
      fingerprints.json
    inventory/
      inventory.json
      tech-stack.json
    graph/
      nodes.jsonl
      edges.jsonl
      indexes/
        node-index.json
        edge-index.json
    domains/
      capability-map.json
      use-cases.json
      glossary.json
      workflows.json
    architecture/
      c4-context.json
      c4-containers.json
      components.json
      deployment.json
    code/
      packages.json
      dependency-cycles.json
      hotspots.json
      style-profile.json
    data/
      erd.json
      tables.json
      procs.json
      data-classification.json
    security/
      threat-model.json
      attack-surface.json
      vuln-summary.json
      authz-map.json
    testing/
      test-inventory.json
      coverage.json
      regression-matrix.json
    reports/
      gaps.json
      confidence.json
      recommendations.json
```

#### 4.2 Why this wins
- **Streaming**: nodes/edges JSONL can scale to millions of relations.
- **Caching**: SPA loads only what the current tab needs.
- **Diffability**: Git diff + version comparisons are meaningful.
- **Extensibility**: Add a new domain (e.g., “FinOps”) without breaking UI.

#### 4.3 SPA API Layer (Standardized)
Expose a consistent API across repos:
- `GET /repos` → list repos + metadata
- `GET /repos/{id}/manifest`
- `GET /repos/{id}/tabs/{tabName}`
- `GET /repos/{id}/graph?filter=...`
- `GET /repos/{id}/search?q=...`
- `GET /repos/{id}/diff?from=vX&to=vY`

**Cache strategy**
- server: ETag + gzip
- client: IndexedDB for large graphs + web workers for layout calc

---

## 5) The 9-Tab LENS Dashboard (Universal, High Value)
### Tab 1 — Executive Overview
- capability tiles, business value metrics, top risks, ownership map
- “health score” with traceable indicators (not vibes)

### Tab 2 — Capabilities & Use Cases
- capability map (clustered bubbles)
- user journeys / use-case sequence snapshots
- actor-to-capability matrix

### Tab 3 — Architecture (C4)
- context & container diagrams (interactive)
- component boundaries + dependency arrows
- “blast radius” explorer (what breaks if X changes)

### Tab 4 — Domain Model
- core UML class diagram (curated)
- aggregate boundaries, invariants, state machines

### Tab 5 — Data & DB
- ERD clusters
- stored procedure graph
- data classification overlay (PII/PHI/PCI flags)

### Tab 6 — APIs & Contracts
- endpoint catalog, auth requirements, DTO/entity/table mapping
- change impact: endpoint → consumers → DB writes

### Tab 7 — Security & Risk
- attack surface map
- authz/role coverage
- dependency vulnerabilities + configuration posture
- “critical gaps” alerts

### Tab 8 — Quality & Testing
- test pyramid status
- regression matrix (capability × test coverage)
- flaky tests / missing integration tests
- performance regressions and guardrails

### Tab 9 — Ops & Deployment
- environments, deployment diagram, SLO/SLI indicators
- logging/tracing dashboards links (if available)
- incident readiness checklist

---

## 6) Diagram Catalog (What to Render, and Why)
### Always render (highest value)
1. **C4 Context & Container**
2. **Capability Map**
3. **Use-Case Sequences (Top 5)**
4. **Component Dependency Graph**
5. **ERD Clusters + Data Sensitivity Overlay**
6. **API-to-DB Impact Map**
7. **Threat Surface Map**
8. **Coverage Heatmaps (Capabilities × tests)**

### Render on-demand (avoid noise)
- full UML for all types
- full call graph of all methods
- giant dependency graphs without clustering

### “Diagram Quality Gates”
A diagram is accepted only if it:
- has evidence links
- is navigable at enterprise scale (cluster, filter, search)
- has relevance (ties to capability/use case/risk)

---

## 7) Security, Blind Spots, Pitfalls — What LENS Must Flag Visually
### 7.1 Security gaps (examples)
- endpoints without auth where expected
- inconsistent role enforcement
- token handling pitfalls (long-lived tokens in dev leaking into prod)
- missing CSRF protections (web apps)
- unsafe CORS settings
- dynamic SQL / unparameterized queries
- secrets in repo, config, build logs
- missing security headers / CSP gaps
- dependency vulnerabilities (front & back end)

### 7.2 Architectural blind spots
- cyclical dependencies, hidden coupling
- “god services” / mega controllers
- domain logic in controllers or UI
- stored procedure business logic with no tests
- duplicate domain models (DTO/entity drift)
- fragile, implicit workflows (status flags in DB without state model)

### 7.3 Operational pitfalls
- no structured logging
- no correlation IDs
- no health checks
- absence of retries/timeouts/circuit breakers
- single points of failure (one DB, one key vault, one hub)

### 7.4 “Edge Case Radar”
LENS should list:
- concurrency hazards (race conditions, stale writes)
- idempotency gaps
- eventual consistency assumptions
- timezone/culture bugs
- RTL/LTR rendering pitfalls (if multilingual)
- migration hazards (schema changes without rollback plan)

**Visualization idea:** a “Risk Constellation” graph—nodes are risks, edges show affected capabilities/services.

---

## 8) Recommended Enhancements (Accuracy + Efficiency, No Scope Creep)
### 8.1 Accuracy upgrades
- **Confidence scoring** per extracted item (0–1), render as badges
- **Cross-validation**: UI route ↔ API endpoint ↔ handler ↔ DB object
- **Diff mode**: compare two snapshots to show what changed
- **Human “pinning”**: allow curated overrides for diagrams (don’t regenerate away meaning)

### 8.2 Efficiency upgrades
- graph as JSONL + indexes
- lazy-loading per tab
- web workers for D3 layouts
- precomputed clusters (Louvain/community detection) server-side

### 8.3 Consistency with CORTEX patterns
- all extraction steps are orchestrators
- all outputs validated with schemas
- all changes go through gates (DoR/DoD)
- all insights come with “evidence trails”

---

## 9) CORTEX Architecture: Legacy Cleanup / Migration Recommendations
These are “low drama” improvements that reduce fragility and increase LENS precision.

### 9.1 From ad-hoc docs to structured artifacts
- Move freeform architecture notes into **structured manifests** + small Markdown explainers.
- Standardize on a `lens-data/` bundle per repo (as described above).
- Add versioning and snapshots to avoid “docs drift.”

### 9.2 Registry modernization
- Add a `lens-phase` registry section:
  - extraction adapters, schemas, output requirements, gates
- Make “diagram generation” a first-class phase with explicit acceptance criteria.

### 9.3 Reduce intelligence fragmentation
- Prefer a single “IntelligenceGateway” that:
  - resolves repo context, tech stack, and extraction capabilities
  - routes tasks to adapters
  - enforces schema + confidence rules

### 9.4 Migration for enterprise scaling
- Support multi-repo and monorepo:
  - repo registry + dependency map between repos
  - cross-repo capability linking

---

## 10) Intelligence for Testing (TDD + Integration + Regression, Orchestrator-Driven)
### 10.1 High-value tests CORTEX must generate
**Unit tests**
- domain invariants (pure functions/rules)
- DTO validation rules
- parsing/formatting edge cases

**Integration tests**
- API endpoint → DB write path
- authz: role/claim matrices
- stored procedure execution (where used)
- SignalR / realtime flows (where present)
- migration scripts (forward + rollback assertions)

**Regression tests**
- capability → use case → tests mapping
- snapshot-based contract tests for APIs (OpenAPI diffs)
- performance regression tests for top endpoints/queries

**E2E tests**
- top 3–10 user journeys derived from route graph

### 10.2 Testing intelligence: how to decide what to test
Use LENS extraction outputs to prioritize:
- highest traffic endpoints
- highest write frequency tables
- most coupled modules
- highest security exposure
- recent change hotspots

### 10.3 Where this lives in CORTEX orchestrators
- **TDD Orchestrator**
  - derive tests from use-case sequences
  - enforce “red-green-refactor” loop
- **Integration Orchestrator**
  - ensures each capability has at least one integration test
- **Regression Orchestrator**
  - creates and maintains “regression matrix” file
- **Refactor Orchestrator**
  - requires tests pass before refactors, tracks risk deltas
- **Operational Orchestrator**
  - adds guardrails: timeouts, retries, idempotency, logging, correlation IDs

### 10.4 Test outputs in LENS
In Tab 8 render:
- test pyramid gauges
- regression matrix heatmap
- “untested critical paths” list with evidence links

---

## 11) SPA Design Instructions (Modern, Dark Blue Glassmorphism)
### 11.1 UI principles
- Card/tile layout (not rows)
- smooth motion (subtle) for graph transitions
- focus on discoverability: search, filters, breadcrumbs
- readable in dark theme with proper contrast

### 11.2 Suggested stack
- Vite + React (or Svelte) + TypeScript
- TailwindCSS + Radix UI (or shadcn/ui) for components
- D3.js for graphs (in isolated components)
- Framer Motion for subtle animation
- Zustand or Redux Toolkit for state
- TanStack Query for data fetching + caching

### 11.3 Graph rendering best practices
- use force layout only for small graphs; cluster + hierarchical layouts for large graphs
- provide “detail drawer” panel for node metadata + evidence links
- always allow filtering by domain, layer, risk, confidence

---

## 12) JSON Schemas (Core + Extensions)
### 12.1 Core entities (minimal)
- `Repo`, `Snapshot`, `Capability`, `UseCase`, `Actor`
- `Service`, `Module`, `Component`, `Endpoint`
- `Type`, `Method`, `Package`
- `Table`, `Proc`, `Column`
- `Risk`, `Control`, `Vulnerability`
- `TestCase`, `TestSuite`, `Coverage`

### 12.2 Evidence model (required on all)
```json
{
  "evidence": [
    {
      "kind": "file|symbol|endpoint|table|config|trace",
      "ref": "path#anchor",
      "snippetHash": "sha256:...",
      "notes": "why this proves the claim",
      "confidence": 0.92
    }
  ]
}
```

### 12.3 Extension adapters
- `.NET`: DI registrations, controllers, middleware pipeline
- `Angular`: routes/modules/components/services/http calls
- `Blazor/SignalR`: hubs, messages, realtime flows
- `DB`: proc graphs, query plans (optional)

---

## 13) “No Scope Creep” Guardrails
To keep this feasible:
- cap diagrams shown by default (top N)
- require “pinning” for more diagrams
- extraction is incremental + versioned
- runtime tracing is optional (high value, not mandatory)

---

## 14) Implementation Checklist (Copilot Instruction Set)
Use this as the instructions for GitHub Copilot when enhancing CORTEX:

1. Add a `lens-data/` bundle generator to CORTEX with schemas and validation.
2. Add adapters for .NET + TS + DB to produce normalized nodes/edges JSONL.
3. Add a LENS API layer:
   - repo registry
   - manifest + per-tab endpoints
   - search + diff
4. Build the LENS SPA:
   - 9 tabs as defined
   - dark blue glassmorphism theme
   - D3 graphs with filters + detail drawer
5. Add quality gates:
   - coverage + confidence
   - evidence required
   - security/risk checks required
6. Add testing intelligence:
   - generate regression matrix
   - enforce TDD, integration coverage per capability
7. Add legacy cleanup:
   - reduce duplication, standardize outputs, centralize intelligence routing

---

## 15) Success Metrics (How you know it worked)
- A product owner can answer “what does this system do?” in 10 minutes.
- An engineer can answer “what breaks if I change X?” in 2 minutes.
- Security can see the attack surface and missing controls instantly.
- Test coverage is mapped to capabilities; critical paths are not “untested mysteries.”
- LENS outputs are versioned; diffs are meaningful; docs drift is reduced.

---

**End of Playbook**

# CORTEX LENS — Generalized Multi‑Repo Visual Documentation System
_Last updated: 2026‑02‑10_

This document generalizes the KSESSIONS + NOOR CANVAS approach into a **repeatable, enterprise‑scale** capability: CORTEX can ingest **any number of repositories**, extract only **high‑value knowledge**, store it in a standardized **Lens Data Model**, and render it via a modern **9‑tab SPA dashboard**.

The goal is not “UML for everything.” The goal is **decision‑grade clarity** for:
- Business leaders (capabilities, risk, dependencies, costs, change impact)
- Product owners (user journeys, backlog mapping, constraints, data ownership)
- Engineering/architects (structure, boundaries, quality, security, hotspots)
- Managers (delivery risk, complexity, test health, ownership, drift)

---

## 1) Core principles (how to stay accurate at scale)

### 1.1 “High value” filtering rules
CORTEX LENS should extract and render **only**:
- **System boundaries & integrations**
- **Capabilities & use cases** tied to routes/APIs/events
- **Domain model** (aggregates/entities/value objects) + persistence mapping
- **Critical workflows** (top 10 flows) via sequence/state diagrams
- **Architecture & dependencies** (cycles, layering drift, coupling hotspots)
- **Operational reality** (deployments, configs, secrets posture, observability)
- **Quality posture** (tests, coverage signals, build health, tech debt hotspots)
- **Security posture** (authN/Z, data classification, attack surface, OWASP risks)
- **Change impact** (blast radius graphs, ownership, churn hotspots)

Everything else is noise.

### 1.2 Evidence > inference
Every extracted fact must be traceable to at least one evidence source:
- static analysis output
- config manifest
- schema inspection
- runtime trace (optional)
- dependency report
CORTEX should label each item with:
- `confidence` (0–1)
- `evidence[]` (file/line or tool output pointer)
- `lastValidatedAt`

### 1.3 Two-track extraction for accuracy
**Track A — Static truth:** code + config + schema + dependency graph  
**Track B — Runtime truth (optional):** traces + logs + DI container dumps + SQL query captures  
Then reconcile conflicts:
- if runtime contradicts static, mark `conflict=true` and surface visually.

---

## 2) Diagram set (universal, scalable, non‑fluffy)

### 2.1 Executive / Product (business value)
1. **Capability Map (heatmapped)**
   - capabilities → owners → maturity → risk → usage → change frequency
2. **Use‑Case Journey Map**
   - actors → steps → systems touched → data touched → failure points
3. **Integration Landscape**
   - internal/external systems, contracts, auth mechanisms, SLAs

### 2.2 Architecture / Engineering (structure & control)
4. **C4 Context + Container**
5. **Component/Module Dependency Graph**
   - cycles, forbidden edges, layering drift
6. **Sequence Diagrams (Top Flows)**
   - UI → API → services → DB → integrations
7. **State Machines**
   - for lifecycle entities (status fields, workflow tables)
8. **Data Model ERD (clustered)**
   - plus “data lineage” edges: endpoint → query/proc → table
9. **Deployment & Runtime Topology**
   - environments, infra nodes, network zones, secrets boundaries

### 2.3 Security / Risk (high leverage)
10. **Attack Surface Map**
   - public endpoints, auth schemes, privileged operations
11. **Threat Model Snapshot**
   - STRIDE‑style risks per boundary + mitigations
12. **Risk Heatmap**
   - severity × likelihood with remediation status

> SPA can render 9 tabs but may include multiple diagram “cards” per tab.

---

## 3) 9‑tab CORTEX LENS Dashboard (generalized)
Each tab is **role‑aligned** and card/tile based (not row tables).

1. **Overview**
   - repo summary, tech stack, owners, build status, risk score, churn
2. **Capabilities**
   - capability map + feature catalog + maturity/risk overlays
3. **Journeys**
   - use‑case journeys + sequence diagrams + failure points
4. **Architecture**
   - C4 diagrams + component graph + layering conformance
5. **Domain & UML**
   - domain model + class relationships + key aggregates
6. **Data**
   - ERD clusters + data lineage + PII markers + retention hints
7. **Security & Risk**
   - attack surface, authZ matrix, OWASP findings, threat model cards
8. **Quality**
   - tests, lint/analyzers, hotspots, complexity, duplication, debt
9. **Ops & Delivery**
   - deployment topology, env diffs, observability, SLO readiness

---

## 4) Lens Data Model (LDv1) — the standard JSON contract

### 4.1 Do NOT use one monolithic JSON
For small repos it’s fine; for enterprise it becomes:
- slow to load
- hard to diff
- hard to cache incrementally
- hard to validate and evolve

**Best practice:** store **multiple nested JSON artifacts** per repo in subfolders, plus a **central API** that normalizes access for the SPA.

### 4.2 Recommended folder layout per repository
```
lens-data/
  repos/
    {repoId}/
      index.json                 # manifest, version, pointers, hashes
      metadata.json              # owners, stack, build info, tags
      overview/
        summary.json
        badges.json
      capabilities/
        capability-map.json
        catalog.json
      journeys/
        use-cases.json
        sequences/
          uc-001.json
          uc-002.json
      architecture/
        c4-context.json
        c4-container.json
        components.json
        dependencies.json
      domain/
        domain-model.json
        class-graph.json
      data/
        erd.json
        lineage.json
        pii-classification.json
      security/
        attack-surface.json
        authz-matrix.json
        findings.json
        threat-model.json
      quality/
        metrics.json
        hotspots.json
        tests.json
      ops/
        topology.json
        configs.json
        runbooks.json
      evidence/
        evidence-index.json       # pointers to raw tool outputs
        raw/...
```

### 4.3 Central API layer (Lens API)
The SPA should never traverse files directly. Use a **Lens API** that:
- serves versioned endpoints (LDv1, LDv2…)
- supports pagination and streaming
- supports partial loading per tab
- enforces auth, RBAC, and redaction
- caches aggressively (ETag + content hashes)
- provides unified search across repos

Example endpoints:
- `GET /api/lens/repos`
- `GET /api/lens/repos/{repoId}/manifest`
- `GET /api/lens/repos/{repoId}/capabilities`
- `GET /api/lens/repos/{repoId}/journeys/{useCaseId}`
- `GET /api/lens/search?q=...&scope=...`
- `GET /api/lens/compare?repoA=...&repoB=...`

### 4.4 JSON schema enforcement (non‑negotiable)
For accuracy and evolvability:
- define JSON Schemas per artifact
- validate on build/CI
- include `schemaVersion`, `generatedAt`, `toolchainVersions`

---

## 5) What to extract (universal “high value” inventory)

### 5.1 Capabilities & use cases (product‑first)
Derive use cases from:
- UI routes + major screens
- API routes + controllers/handlers
- domain commands/events
- DB writes (INSERT/UPDATE/proc calls)

Each use case should include:
- actors, preconditions, triggers
- main flow (steps)
- alt flows / failure modes
- systems touched (services, DB, external)
- data touched (tables/entities)
- security gates (authN/Z)
- observability (logs/traces)
- risks & mitigations

### 5.2 Architecture (drift & dependencies)
Extract:
- project/module graph
- DI wiring graph (where possible)
- cycles, forbidden edges, layer violations
- integration contracts (OpenAPI, gRPC, queues, SignalR hubs)
- concurrency/realtime patterns (SignalR/websockets, background jobs)

### 5.3 Domain model (not everything)
Extract only:
- aggregates/entities central to top use cases
- value objects with invariants
- key services (“business logic hubs”)
- DTOs only when they represent contracts

### 5.4 Data (what leadership cares about)
Extract:
- ERD clusters
- data classification: PII/PHI/PCI flags
- lineage: endpoint → query/proc → table
- retention hints and “system of record”
- performance risk: high‑fanout joins, missing indexes (heuristic)

---

## 6) Security & risk: the “business‑useful” layer

### 6.1 Security gaps and blind spots to always detect
**Attack surface**
- public endpoints without auth
- overly broad CORS
- insecure cookie/session flags
- missing rate limiting
- missing input validation patterns
- file upload vectors
- deserialization hazards
- SSRF patterns (server-side HTTP calls)

**Auth & authorization**
- endpoints lacking `[Authorize]` / policy checks
- inconsistent role checks (“stringly typed roles”)
- privilege escalation paths
- broken object level authorization (BOLA)

**Secrets & config**
- secrets in repo, weak env separation
- missing key rotation evidence
- client-side keys leaked (SPA)

**Dependency & supply chain**
- outdated packages with known CVEs
- unpinned versions
- build scripts fetching remote binaries

**Data protection**
- PII stored unencrypted
- logging sensitive data
- excessive DB permissions (app has dbo)
- cross-schema access without controls

### 6.2 How to represent security visually (for non‑engineers)
- **Risk heatmap cards**: severity/likelihood/remediation status
- **Boundary diagrams**: trust zones + data classification edges
- **Attack surface graph**: endpoints sized by risk & usage
- **AuthZ matrix**: roles → capabilities (what can each role do)

---

## 7) Pitfalls (and better alternatives)

### 7.1 Pitfall: “UML everything”
**Fix:** “Thin UML” strategy:
- auto-generate wide, then **curate** into small, stable diagrams
- allow humans to “pin” important nodes/flows so regeneration keeps meaning

### 7.2 Pitfall: One-size extraction
**Fix:** Pluggable extractors:
- language pack: C#/.NET, TS/Angular, Java/Spring, Python/FastAPI…
- DB pack: SQL Server, Oracle, Postgres…
- runtime pack: OpenTelemetry, AppInsights, logs

### 7.3 Pitfall: stale docs
**Fix:** continuous re-extraction:
- incremental updates based on git diff + file hashing
- regen only impacted artifacts
- surface “staleness” badges

### 7.4 Pitfall: exposing sensitive information in Lens
**Fix:** redaction + access tiers:
- tiered views: Exec, Product, Engineer
- redact secrets, connection strings, internal URLs
- “evidence pointers” can require higher privilege to open

---

## 8) SPA implementation guidance (modern glassmorphism, D3)
This is the generalized UI guidance (apply regardless of repo).

### 8.1 UI stack
- Framework: React + Vite (fast) or Next.js (if you need SSR)
- Styling: Tailwind + CSS variables
- Motion: Framer Motion (subtle)
- Charts: D3 for graphs; optionally Recharts/ECharts for standard plots
- Graph layout: d3-force, dagre, elkjs (for layered DAGs)
- Virtualized lists: react-virtual (for huge catalogs)

### 8.2 Design principles (dark blue glass theme)
- Background: deep navy gradient with noise texture
- Cards: translucent glass panels, soft borders, subtle shadow
- Accent: cyan/azure for interactive focus
- Motion: micro-interactions only (hover lift, fade in, node highlight)

### 8.3 Performance rules (enterprise)
- load per-tab artifacts only
- graph decimation / level-of-detail controls
- progressive rendering for large graphs
- cache with ETags + local storage “repo manifest”

---

## 9) How CORTEX should generate Lens data (pipeline)
### 9.1 Pipeline phases (repeatable)
1. **Discover**: repo fingerprint, stack detection, entrypoints
2. **Extract**: static analyzers, schema, configs, routes
3. **Normalize**: map into LDv1 artifacts + schemas
4. **Validate**: schema validation + cross-checks + confidence scoring
5. **Enrich**: heuristics (hotspots, risks, bounded contexts clustering)
6. **Publish**: write to `lens-data/repos/{repoId}/...` + manifest hash
7. **Serve**: Lens API exposes stable endpoints
8. **Render**: SPA consumes LDv1 only (no repo specifics)

### 9.2 “Confidence & evidence” enforcement
Every node/edge needs:
- `confidence`
- `evidence[]`
- `sourceType` (static/runtime/manual)
- `lastValidatedAt`

---

## 10) Recommended upgrades to your vision (efficiency + accuracy)
1. **Multi‑artifact storage + Lens API** (instead of one JSON)
2. **Schema‑validated LDv1** for stability and evolution
3. **Evidence‑first + confidence scoring** to prevent hallucinated diagrams
4. **Incremental extraction** keyed by git diff for speed
5. **Role‑based redaction** to prevent security leaks
6. **Pinned diagrams** so “high value” views don’t thrash on regen
7. **Cross‑repo compare** (capabilities, risk, tech debt) for leadership

---

## 11) GitHub Copilot instruction set (for enhancing CORTEX)
When implementing in `asifhussain60/CORTEX`:
- Add a `lens/` package:
  - `extractors/` (pluggable)
  - `schemas/` (JSON Schemas per artifact)
  - `publisher/` (writes nested artifacts + manifest)
  - `api/` (Lens API endpoints)
  - `ui/` (SPA front-end)
- Add a “Lens Gate”:
  - fails if schemas invalid
  - fails if evidence missing on critical items
  - fails if secrets detected in output

**Non‑negotiables:**
- output must match LDv1 schema
- include evidence pointers
- no secrets in UI payloads
- incremental regeneration supported

---

## Appendix A — Minimal manifest (`index.json`) shape
```json
{
  "schemaVersion": "LDv1",
  "repoId": "github:org/name@branch",
  "generatedAt": "2026-02-10T22:00:00Z",
  "hash": "sha256:...",
  "artifacts": {
    "overview": "overview/summary.json",
    "capabilities": "capabilities/capability-map.json",
    "journeys": "journeys/use-cases.json",
    "architecture": "architecture/components.json",
    "domain": "domain/domain-model.json",
    "data": "data/erd.json",
    "security": "security/findings.json",
    "quality": "quality/metrics.json",
    "ops": "ops/topology.json"
  }
}
```

---

## Appendix B — Use case object (LDv1 excerpt)
```json
{
  "id": "uc-001",
  "name": "Create Session",
  "actors": ["Host"],
  "trigger": {"type":"ui-route","value":"/sessions/new"},
  "steps": [
    {"n":1,"action":"Open form","system":"SPA"},
    {"n":2,"action":"POST /api/sessions","system":"API"},
    {"n":3,"action":"Insert Session","system":"DB"}
  ],
  "dataTouched": [{"type":"table","name":"canvas.Sessions","classification":"internal"}],
  "security": {"authRequired": true, "policies":["HostOnly"]},
  "risks": [{"id":"risk-12","severity":"high","title":"Missing rate limiting"}],
  "evidence": [{"type":"file","path":"...","lines":"..."}],
  "confidence": 0.86
}
```

---

If you want, the next concrete step is to convert this into:
1) JSON Schemas for each artifact, and  
2) a CORTEX “Lens Extract” orchestrator that generates the folder structure + manifest + API.


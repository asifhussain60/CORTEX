# CORTEX Documentation Refresh Prompt

## Purpose

Manually refresh `docs/` folder content and Mermaid diagrams to reflect the final state of `cortex-impl-map.yaml`. Uses VS Code todo list to track each document/diagram task.

---

## Quick Start Landing Page

**Primary Entry Point:** [`docs/quick-start-overview.md`](../../docs/quick-start-overview.md)

This one-pager provides technical-to-business translations:
- YAML configuration mappings (governance, tiers, domains)
- Orchestrator registry and usage patterns
- Governance tier composite evaluation
- LENS protocol for AST scanning
- Conversation protocol for multi-turn interactions

**Launch command:** `docs\serve-docs.bat` (opens browser to Quick Overview)

---

## Folder Structure

All documentation assets are organized under the `docs/` directory. Build output is generated to `_build/site/` (git-ignored):

```
Repository Root
├── assets/                      # Centralized assets (7 logo files)
│   ├── images/
│   ├── README.md
│   └── INDEX.md
│
├── docs/                        # SOURCE DOCUMENTATION (COMMITTED)
│   ├── 0-README.md              # Main documentation index
│   ├── INDEX.md                 # Alternative index
│   ├── LICENSE.md               # Licensing information
│   ├── ARCHITECTURE-ASSETS.md   # Asset architecture reference
│   ├── 01-getting-started/      # Quick start guides
│   ├── 02-architecture/         # Architecture documentation
│   │   ├── adrs/                # Architecture Decision Records
│   │   ├── 0-overview.md
│   │   ├── 6-implementation-phases.md
│   │   ├── 7-intent-router.md
│   │   ├── 9-knowledge-protocol.md
│   │   └── 10-mcp-tool-governance.md
│   ├── 03-api-reference/        # API reference documentation
│   ├── 04-guides/               # Implementation guides
│   │   ├── operations/          # Operations runbooks
│   │   ├── 5-runbook.md
│   │   ├── 6-disaster-recovery.md
│   │   └── 7-scaling-guide.md
│   ├── 05-reference/            # Reference materials
│   │   ├── gap-analysis.md
│   │   ├── remediation-status.md
│   │   ├── governance-rules-reference.md
│   │   └── test-ac-mapping.md
│   ├── 06-tutorials/            # Tutorial guides
│   ├── 07-contributing/         # Contributor guides
│   │   ├── 2-development-setup.md
│   │   ├── 3-testing-strategy.md
│   │   ├── 4-code-style-guide.md
│   │   └── 5-pull-request-process.md
│   ├── _archive/                # Historical documentation (DO NOT EDIT)
│   │   ├── BEFORE-AFTER-COMPARISON.md
│   │   ├── phases/
│   │   ├── reviews/
│   │   ├── sessions/
│   │   └── ... (other archived documents)
│   ├── _diagrams/               # All Mermaid diagrams
│   │   ├── architecture-overview.mmd
│   │   ├── ci-cd-pipeline.mmd
│   │   ├── error-recovery-flow.mmd
│   │   ├── governance-tiers.mmd
│   │   ├── intent-router-flow.mmd
│   │   ├── knowledge-graph.mmd
│   │   ├── mcp-tools.mmd
│   │   ├── orchestration-flow.mmd
│   │   ├── phase-dependencies.mmd
│   │   ├── production-readiness.mmd
│   │   ├── resilience-patterns.mmd
│   │   ├── state-management.mmd
│   │   └── test-pyramid.mmd
│   ├── _manifests/              # System manifests (DO NOT EDIT)
│   │   ├── content-registry.yaml
│   │   ├── file-discovery-blacklist.yaml
│   │   ├── file-manifest.yaml
│   │   └── file-placement-policy.yaml
│   ├── _hooks/                  # MkDocs build hooks
│   │   └── copy_assets.py       # Post-build asset copying
│   └── _unsorted/               # Work-in-progress documents
│       └── ... (session reports and temporary docs)
│
└── _build/ (git-ignored)        # BUILD OUTPUT (NOT COMMITTED)
    └── site/                    # Generated website
        ├── index.html
        ├── assets/              # Auto-copied from root assets/
        │   └── images/
        └── (other generated pages)
```

**Key Rules:**
- ✅ All diagrams go in `docs/_diagrams/`
- ✅ All reference docs go in appropriate `docs/XX-*` sections
- ✅ Historical archives go in `docs/_archive/`
- ✅ System metadata goes in `docs/_manifests/`
- ✅ Build hooks go in `docs/_hooks/`
- ✅ Work-in-progress goes in `docs/_unsorted/`
- ✅ Centralized assets go in root `assets/` folder
- ✅ Build output generates to `_build/site/` (git-ignored)
- ❌ No .md files in repository root (except reference docs: SOLUTION-SUMMARY.md, BUILD-STRUCTURE-REFERENCE.md, IMPLEMENTATION-COMPLETION-REPORT.md, POST-IMPLEMENTATION-CHECKLIST.md)
- ❌ No .md files outside docs/ (except reference docs above)
- ❌ No orphaned `_docs_*` folders in root (all moved to docs/)
- ❌ Never commit `_build/` directory (git-ignored)

---

## Invocation

Run this prompt manually when `cortex-impl-map.yaml` is updated and documentation needs refresh.

---

## Execution Rules

1. **Silent execution** - No verbose output, no progress reports
2. **Todo-driven** - Create todo list first, then execute each item
3. **Complete or fail** - Do not leave partial work; finish all todos
4. **Clean result** - `docs/` folder must be organized when done

---

---

## Build Output Configuration

**MkDocs Configuration** (`mkdocs.yml`):
```yaml
docs_dir: docs
site_dir: _build/site    # Hidden directory (git-ignored)

hooks:
  - docs/_hooks/copy_assets.py
```

**Git Exclusion** (`.gitignore`):
```
_build/              # Build artifacts (git-ignored)
```

This keeps the repository root clean by:
- Hiding generated files in `_build/`
- Automatically ignored by git
- Post-build hook copies `assets/` to `_build/site/assets/`

---

## Option 1: Launch MkDocs Server (Detached External Terminal)

Before documentation work, launch the MkDocs development server in an **external PowerShell window** so it runs independently without blocking VS Code workflow.

### Quick Start
```powershell
./scripts/launch-mkdocs.ps1
```

### Result
- ✅ New PowerShell window opens
- ✅ MkDocs server runs at `http://127.0.0.1:8000`
- ✅ Output generated to `_build/site/` (not visible in root)
- ✅ VS Code terminal remains free for editing/testing
- ✅ Live reload enabled (changes reflect immediately)
- 🛑 Press Ctrl+C in external window to stop server

### Manual Alternative
```powershell
# Terminal 1: External PowerShell window
cd d:\PROJECTS\CORTEX
mkdocs serve
# Output: _build/site/
```

### Why Detached?
- **No blocking** – Documentation updates don't freeze your editor
- **Persistent** – Server keeps running through multiple edits
- **Preview-ready** – Switch to browser tab to verify changes instantly
- **Clean workflow** – Separate concern from code editing
- **Clean root** – Build output hidden in `_build/`

---

## Step 1: Create Todo List

Read `_workspaces/roadmap/cortex-impl-map.yaml` and create todos for:

### Documents to Update

| Todo | Target File | Source Section in impl-map |
|------|-------------|---------------------------|
| Architecture Overview | `docs/02-architecture/0-overview.md` | `architecture:` |
| Implementation Status | `docs/02-architecture/6-implementation-phases.md` | `phases_implementation_status:` |
| Governance Rules | `docs/02-architecture/governance-rules.md` | `governance:` |
| Definition of Ready | `docs/02-architecture/definition-of-ready.md` | `production_readiness_summary:` |
| Gap Analysis | `docs/05-reference/gap-analysis.md` | `gaps_identified:` |
| Remediation Status | `docs/05-reference/remediation-status.md` | `remediation_phases:` |

### Diagrams to Create/Update (in `docs/_diagrams/`)

| Todo | Diagram File | Type | Illustrates |
|------|--------------|------|-------------|
| Architecture Diagram | `docs/_diagrams/architecture-overview.mmd` | Flowchart | System components and relationships |
| Tier Structure | `docs/_diagrams/governance-tiers.mmd` | Flowchart | Tier 0-3 hierarchy |
| Phase Dependencies | `docs/_diagrams/phase-dependencies.mmd` | Flowchart | Phase execution order |
| Orchestration Flow | `docs/_diagrams/orchestration-flow.mmd` | Sequence | Request to orchestrator to execution |
| MCP Tools | `docs/_diagrams/mcp-tools.mmd` | Mind Map | Tool categories and capabilities |
| Production Readiness | `docs/_diagrams/production-readiness.mmd` | Flowchart | Critical path to 100% |
| State Management | `docs/_diagrams/state-management.mmd` | Flowchart | State persistence and recovery |
| Resilience Patterns | `docs/_diagrams/resilience-patterns.mmd` | Sequence | Circuit breaker, retry, fallback |
| Intent Router Flow | `docs/_diagrams/intent-router-flow.mmd` | Flowchart | LENS protocol + routing decisions |
| Knowledge Graph | `docs/_diagrams/knowledge-graph.mmd` | Flowchart | BKIO pipeline, entity relationships |
| Error Recovery Flow | `docs/_diagrams/error-recovery-flow.mmd` | Sequence | Recovery patterns, circuit states |
| Test Pyramid | `docs/_diagrams/test-pyramid.mmd` | Flowchart | Unit/integration/E2E distribution |
| CI/CD Pipeline | `docs/_diagrams/ci-cd-pipeline.mmd` | Flowchart | Deployment flow, validation gates |

### Architecture Documents (in `docs/02-architecture/`)

| Todo | Target File | Description |
|------|-------------|-------------|
| Intent Router | `7-intent-router.md` | LENS protocol, classifier, disambiguator |
| Knowledge Protocol | `9-knowledge-protocol.md` | BKIO, knowledge graph operations |
| MCP Tool Governance | `10-mcp-tool-governance.md` | 14 MCP tools, registry, auth |

### ADRs (in `docs/02-architecture/adrs/`)

| Todo | Target File | Decision |
|------|-------------|----------|
| Tier Precedence | `adr-002-tier-precedence.md` | tier0 > tier1 > tier2 > tier3 |
| MCP Stub Strategy | `adr-003-mcp-stub-strategy.md` | Why 14 tools remain stubs |
| Package Separation | `adr-004-cortex-brain-separation.md` | cortex/ vs cortex_brain/ split |
| Conversation Protocol | `adr-005-conversation-protocol.md` | ContinuationDecision pattern |

### Contributing Documents (in `docs/07-contributing/`)

| Todo | Target File | Description |
|------|-------------|-------------|
| Development Setup | `2-development-setup.md` | Local environment setup |
| Testing Strategy | `3-testing-strategy.md` | Test patterns, AC mapping |
| Code Style Guide | `4-code-style-guide.md` | CORE-011/012 enforcement |
| PR Process | `5-pull-request-process.md` | Review workflow, checklist |

### Operations Guides (in `docs/04-guides/operations/`)

| Todo | Target File | Description |
|------|-------------|-------------|
| Runbook | `5-runbook.md` | Incident response procedures |
| Disaster Recovery | `6-disaster-recovery.md` | Backup/restore, RTO/RPO |
| Scaling Guide | `7-scaling-guide.md` | Horizontal scaling patterns |

### Reference Documents (in `docs/05-reference/`)

| Todo | Target File | Description |
|------|-------------|-------------|
| Governance Rules | `governance-rules-reference.md` | All 29 CORE-* rules with examples |
| Test AC Mapping | `test-ac-mapping.md` | AC-ID to test file mapping |

---

## Step 2: Execute Each Todo

For each todo item:

1. Mark todo as **in-progress**
2. Read relevant section from `cortex-impl-map.yaml`
3. Generate/update the document or diagram
4. Mark todo as **completed**
5. Move to next todo

---

## Step 3: Cleanup

After all todos complete:

1. Delete any obsolete files in `docs/` not in the catalog above
2. Verify all diagrams render valid Mermaid syntax
3. Update `docs/0-README.md` with current date and status

---

## Document Templates

### Markdown Document Template

```markdown
# {Title}

> Auto-generated from cortex-impl-map.yaml on {date}

## Overview

{Brief summary from impl-map section}

## Details

{Structured content from impl-map}

## Related

- [Link to related doc]
- [Link to diagram]
```

### Mermaid Diagram Template

```mermaid
---
title: {Diagram Title}
---
{diagram content}
```

---

## Diagram Specifications

### architecture-overview.mmd
```mermaid
flowchart TB
    subgraph CORTEX Architecture
        API[API Layer]
        ORCH[Orchestrators]
        BRAIN[Domain Brain]
        GOV[Governance]
        STATE[State Management]
        MCP[MCP Server]
    end
    API --> ORCH
    ORCH --> BRAIN
    ORCH --> GOV
    GOV --> STATE
    MCP --> ORCH
```

### governance-tiers.mmd
```mermaid
flowchart TD
    T0[Tier 0: Core Rules]
    T1[Tier 1: Domain Rules]
    T2[Tier 2: Context Rules]
    T3[Tier 3: Runtime Rules]
    T0 --> T1 --> T2 --> T3
```

### phase-dependencies.mmd
```mermaid
flowchart LR
    A[Phase A: Consolidation] --> B[Phase B: MCP Registry]
    B --> C[Phase C: Hardening]
    C --> E[Phase E: TDD Implementation]
    E --> H[Phase H: E2E Validation]
```

### orchestration-flow.mmd
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Router
    participant Orchestrator
    participant Brain
    Client->>API: Request
    API->>Router: Route
    Router->>Orchestrator: Execute
    Orchestrator->>Brain: Query
    Brain-->>Orchestrator: Knowledge
    Orchestrator-->>API: Result
    API-->>Client: Response
```

### mcp-tools.mmd
```mermaid
mindmap
    root((MCP Tools))
        Governance
            query_tool
            validate_tool
            execute_tool
        Analysis
            analyze_tool
            report_tool
        Knowledge
            search_tool
            index_tool
        Utility
            echo_tool
            transform_tool
```

### production-readiness.mmd
```mermaid
flowchart TD
    START[Current: 62%] --> F[Phase F: Export Completion]
    F --> G[Phase G: Circular Import Fix]
    G --> E[Phase E: TDD Implementation]
    E --> H[Phase H: E2E Validation]
    H --> I[Phase I: CI/CD]
    I --> J[Phase J: Governance]
    J --> END[100% Production Ready]
```

### state-management.mmd
```mermaid
flowchart LR
    RT[Runtime State] --> DB[(governance.db)]
    DB --> CACHE[Cache Layer]
    CACHE --> ORCH[Orchestrators]
    ORCH --> PERSIST[Persistence]
    PERSIST --> DB
```

### resilience-patterns.mmd
```mermaid
sequenceDiagram
    participant Client
    participant CircuitBreaker
    participant Service
    Client->>CircuitBreaker: Request
    alt Circuit Closed
        CircuitBreaker->>Service: Forward
        Service-->>CircuitBreaker: Response
        CircuitBreaker-->>Client: Success
    else Circuit Open
        CircuitBreaker-->>Client: Fallback
    end
```

### intent-router-flow.mmd
```mermaid
flowchart TB
    subgraph LENS["LENS Protocol"]
        L["Language Phase<br/>Intent parsing"]
        E["Examination Phase<br/>AST analysis"]
        N["Navigation Phase<br/>Git history"]
        S["Synthesis Phase<br/>Context aggregation"]
    end
    
    INPUT[User Request] --> L
    L --> E --> N --> S
    
    S --> CLASSIFY[Intent Classifier]
    CLASSIFY --> |Ambiguous| DISAMBIG[Disambiguator]
    CLASSIFY --> |Clear| ROUTE[Routing Engine]
    DISAMBIG --> ROUTE
    
    ROUTE --> |Planning| PLAN[Planning Orchestrator]
    ROUTE --> |Analysis| ANAL[Analysis Orchestrator]
    ROUTE --> |Execution| EXEC[Execution Orchestrator]
    ROUTE --> |Integration| INTEG[Integration Orchestrator]
```

### knowledge-graph.mmd
```mermaid
flowchart TB
    subgraph SOURCES["Intelligence Sources"]
        AST[AST Adapter<br/>Code Structure]
        GIT[Git Adapter<br/>History]
        COMM[Comments Adapter<br/>Documentation]
        REL[Relationships Adapter<br/>Dependencies]
    end
    
    subgraph BKIO["BKIO Orchestrator"]
        PARSE[Document Parsing]
        EXTRACT[Entity Extraction]
        DETECT[Conflict Detection]
        RESOLVE[Conflict Resolution]
    end
    
    subgraph STORAGE["Knowledge Storage"]
        T3[(Tier 3 KB)]
        GRAPH[(Knowledge Graph)]
        VALID[Consistency Validator]
    end
    
    AST & GIT & COMM & REL --> PARSE
    PARSE --> EXTRACT --> DETECT --> RESOLVE
    RESOLVE --> T3 & GRAPH
    GRAPH --> VALID
```

### error-recovery-flow.mmd
```mermaid
sequenceDiagram
    participant Client
    participant Retry as Retry Handler
    participant CB as Circuit Breaker
    participant Fallback
    participant Service
    
    Client->>Retry: Request
    loop Retry Attempts (3x)
        Retry->>CB: Check State
        alt Circuit CLOSED
            CB->>Service: Forward Request
            alt Success
                Service-->>CB: Response
                CB-->>Retry: Success
                Retry-->>Client: Result
            else Failure
                Service-->>CB: Error
                CB->>CB: Record Failure
                Note over CB: If failures > threshold
                CB->>CB: OPEN Circuit
            end
        else Circuit OPEN
            CB-->>Retry: Circuit Open
            Retry->>Fallback: Get Fallback
            Fallback-->>Client: Degraded Response
        else Circuit HALF-OPEN
            CB->>Service: Probe Request
            alt Probe Success
                Service-->>CB: OK
                CB->>CB: CLOSE Circuit
            else Probe Fail
                CB->>CB: OPEN Circuit
            end
        end
    end
```

### test-pyramid.mmd
```mermaid
flowchart TB
    subgraph PYRAMID["Test Pyramid (409 files)"]
        E2E["E2E Tests<br/>~29 files<br/>Smoke, Load, Chaos"]
        INT["Integration Tests<br/>~80 files<br/>Cross-module, API"]
        UNIT["Unit Tests<br/>~300 files<br/>Isolated, Fast"]
    end
    
    subgraph COVERAGE["Coverage Targets"]
        COV_E2E["Critical Paths: 100%"]
        COV_INT["Boundaries: 80%"]
        COV_UNIT["Functions: 90%"]
    end
    
    E2E --> COV_E2E
    INT --> COV_INT
    UNIT --> COV_UNIT
    
    subgraph AC["AC Tracking"]
        AC_ID["257 unique AC IDs"]
        AC_MAP["AC → Test Mapping"]
    end
```

### ci-cd-pipeline.mmd
```mermaid
flowchart LR
    subgraph DEV["Development"]
        CODE[Code Change]
        LINT[Lint Check]
        TYPE[Type Check]
    end
    
    subgraph CI["Continuous Integration"]
        UNIT[Unit Tests]
        INT[Integration Tests]
        COV[Coverage Check]
        SEC[Security Scan]
    end
    
    subgraph GATE["Quality Gates"]
        G1{Tests Pass?}
        G2{Coverage ≥80%?}
        G3{No Vulns?}
    end
    
    subgraph CD["Continuous Deployment"]
        STAGE[Staging Deploy]
        E2E[E2E Tests]
        CANARY[Canary Release]
        PROD[Production]
    end
    
    CODE --> LINT --> TYPE --> UNIT
    UNIT --> INT --> COV --> SEC
    SEC --> G1 --> |Yes| G2 --> |Yes| G3 --> |Yes| STAGE
    G1 --> |No| CODE
    G2 --> |No| CODE
    G3 --> |No| CODE
    STAGE --> E2E --> CANARY --> PROD
```

---

## Protected Files (Never Delete)

- `docs/LICENSE.md`
- `docs/0-README.md` (update, don't delete)
- `docs/_archive/**` (historical records)
- `docs/_manifests/**` (system metadata)
- `docs/_diagrams/**` (rendered diagrams)
- `docs/_hooks/` (build automation)
- `docs/_unsorted/**` (work-in-progress documents)
- `assets/` (centralized assets)
- `_build/` (generated build output - do not edit, automatically regenerated)
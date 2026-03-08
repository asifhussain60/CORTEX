---
scope: non-production-admin
---
# GitHub Issue Harvester Agent

**Agent ID:** `github-issue-harvester-agent`
**Updated:** 2026-03-08
**Layer:** docs
**Status:** active
**Responsibility:** Ingest GitHub issues from the CORTEX repository, extract capability descriptions and architectural context, and feed structured issue data into the documentation pipeline
**Inputs:** GitHub issue pages, durable state YAML, cortex-master.yaml
**Outputs:** Structured issue manifest consumed by drift-detection-agent and doc-sync-agent

---

## 🎯 Single Responsibility

Fetch, parse, and structure GitHub issues starting from the last unprocessed issue ID. Extract capability records, architectural context, phase completion data, and backport instructions from issue bodies and comments. Produce a structured issue manifest that downstream agents consume alongside the Git change manifest.

This agent does NOT modify documentation files. It produces structured data consumed by `drift-detection-agent` and `doc-sync-agent`.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Durable state** | `cortex-registry/config/doc-orchestrator-state.yaml` | ✅ |
| **GitHub issue pages** | `https://github.com/asifhussain60/CORTEX/issues/{id}` | ✅ |
| **Master plan** | `cortex-registry/cortex-master.yaml` | ✅ (cross-reference phase IDs) |
| **Max issues per run** | Default: 20 (configurable) | Optional |

---

## 📤 Outputs

A **structured issue manifest** with the following structure:

```yaml
issue_harvest:
  timestamp: "2026-03-08T12:00:00Z"
  issues_scanned: [14, 15, 16]
  issues_with_content: [14]
  issues_skipped: []

  capabilities_extracted:
    - issue_id: 14
      title: "Enhancementn"
      opened: "2026-03-08"
      capabilities:
        - id: "FB-2026-03-08-001"
          name: "CAPE: Complexity Triage Engine (3-Band CDR Scoring)"
          classification: NEW_CAPABILITY
          phase: "phase-136"
          components:
            - "cortex/orchestrators/core/complexity_triage_engine.py"
          documentation_targets:
            - "docs/.content/05-orchestration-the-engine-room.md"
            - "docs/.content/09-lifecycle-from-idea-to-production.md"

        - id: "FB-2026-03-08-006"
          name: "KAL: Knowledge Coverage Assessor + Domain Signal Extractor"
          classification: NEW_CAPABILITY
          phase: "phase-135"
          components:
            - "cortex/intelligence/knowledge/knowledge_coverage_assessor.py"
            - "cortex/intelligence/knowledge/domain_signal_extractor.py"
          documentation_targets:
            - "docs/.content/02-intelligence-how-cortex-understands-code.md"
            - "docs/.content/11-patterns-knowledge-architecture.md"

  phase_completions:
    - issue_id: 14
      phases:
        - id: "phase-136"
          title: "CORTEX Autonomous Planning Engine (CAPE)"
          status: COMPLETE
          gaps_closed: "26/26"
        - id: "phase-137"
          title: "Knowledge Acquisition Layer (KAL)"
          status: COMPLETE
          gaps_closed: "17/17"

  backport_instructions:
    - issue_id: 14
      execution_order: "KAL (006–008) → CAPE (001–005) → Intelligence (009–010) → Git Safety (011) → Feedback (012)"
      dependencies: "CAPE depends on KAL for knowledge gap filling pre-planning"
```

---

## 🔄 Harvesting Protocol

### Step 1: Read Durable State

```yaml
# Read from cortex-registry/config/doc-orchestrator-state.yaml
last_processed_issue_id: 13  # Start from 14
skipped_issue_ids: []
```

### Step 2: Determine Issue Range

```
start_id = last_processed_issue_id + 1  # e.g., 14
end_id = start_id + max_issues_per_run   # e.g., 34

# Fetch each issue page:
#   https://github.com/asifhussain60/CORTEX/issues/{id}
# Stop when: HTTP 404 (no more issues) or max reached
```

### Step 3: Parse Issue Content

For each issue page, extract:

| Field | Extraction Method |
|-------|------------------|
| **Title** | `<h1>` or issue title element |
| **Body** | Issue body markdown/HTML |
| **Comments** | Comment thread content |
| **Capability records** | Structured tables with `FB-YYYY-MM-DD-NNN` IDs |
| **Phase references** | `Phase: NNN` or `phase-NNN` patterns |
| **Component paths** | `cortex/**/*.py` file path patterns |
| **Classification** | `NEW_CAPABILITY`, `ENHANCED_CAPABILITY`, `BUG_FIX`, etc. |

### Step 4: Cross-Reference with cortex-master.yaml

For each phase referenced in an issue:
1. Look up the phase in `cortex-master.yaml` → `phases:` section
2. Determine if phase is `PLANNED`, `COMPLETE`, or `ARCHIVED`
3. Map phase to documentation targets via the capability's component paths

### Step 5: Update Durable State

After successful harvest:
```yaml
# Write to cortex-registry/config/doc-orchestrator-state.yaml
last_processed_issue_id: 14  # Updated to highest processed
last_harvest_timestamp: "2026-03-08T12:00:00Z"
total_issues_ingested: 1     # Incremented
execution_history:
  - timestamp: "2026-03-08T12:00:00Z"
    issues_harvested: [14]
    capabilities_found: 12
```

---

## 📋 Issue Content Classification

| Content Pattern | Classification | Documentation Target |
|----------------|---------------|---------------------|
| `NEW_CAPABILITY` with `cortex/orchestrators/` | New orchestrator | `05-orchestration` |
| `NEW_CAPABILITY` with `cortex/mcp/tools/` | New MCP tool | `06-mcp-tools` |
| `NEW_CAPABILITY` with `cortex/intelligence/` | Intelligence enhancement | `02-intelligence` |
| `ENHANCED_CAPABILITY` with `cortex/intelligence/facade.py` | Facade extension | `02-intelligence` |
| `NEW_CAPABILITY` with `cortex/governance/` | Governance component | `03-governance` |
| `NEW_CAPABILITY` with `cortex/core/` | Core infrastructure | `01-platform` |
| `BUG_FIX` | No doc update unless behavioral | — |
| Phase completion summary | Phase status update | Master plan cross-ref |
| Architecture diagrams (Mermaid in issues) | Convert to D3.js specs | `diagram-regeneration-agent` |

---

## 🔗 Downstream Consumers

| Consumer | What It Uses |
|----------|-------------|
| `drift-detection-agent` | Capabilities extracted → checks for orphaned features |
| `doc-sync-agent` | Capability records → updates `.content/` files |
| `coverage-audit-agent` | Issue manifest → validates nothing from issues missed |
| `diagram-regeneration-agent` | Architecture diagrams → converts to D3.js specs |

---

## 🛡️ Safety

- **Read-only on workspace** — this agent fetches web pages and reads YAML; it never modifies documentation files
- **Idempotent** — re-running with the same state produces the same manifest (skips already-processed issues)
- **Durable** — state persisted in YAML; survives session restarts
- **Bounded** — `max_issues_per_run` prevents unbounded fetching
- **Graceful degradation** — HTTP errors (404, 403, 500) are logged and skipped, not fatal
- **No Mermaid passthrough** — any Mermaid diagrams found in issues are flagged for D3.js conversion, never passed through

---

## ⚠️ Planned-as-Implemented Policy Integration

When this agent encounters capabilities tied to phases with status `PLANNED` in `cortex-master.yaml`:
- The capability IS included in the issue manifest
- The `documentation_policy` field is set to `treat_as_implemented`
- Downstream agents (`doc-sync-agent`, `diagram-regeneration-agent`) treat planned capabilities as current reality in all documentation output
- This aligns with the **Planned-as-Implemented Documentation Policy** defined in `cortex-doc.prompt.md`

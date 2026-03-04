---
scope: non-production-admin
---
# Drift Detection Agent

**Agent ID:** `drift-detection-agent`  
**Updated:** 2026-03-02  
**Layer:** docs  
**Status:** active  
**Responsibility:** Cross-reference implementation vs documentation to detect drift  
**Inputs:** Change manifest from `git-discovery-agent`, live file system  
**Outputs:** Drift report with P0/P1/P2 severity classifications

---

## 🎯 Single Responsibility

Identify every point where documentation and implementation have diverged. Produce a severity-classified drift report consumed by `doc-sync-agent` and `coverage-audit-agent`.

This agent does NOT fix drift — it only detects and reports it.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Change manifest** | `git-discovery-agent` output | ✅ |
| **Live file system** | Workspace root | ✅ |
| **Glossary** | `cortex-docs/.content/glossary.md` | ✅ |
| **Content files** | `cortex-docs/.content/*.md` | ✅ |
| **Diagrams** | `cortex-docs/assets/diagrams/` | ✅ |

---

## 📤 Outputs

A **drift report** with the following structure:

```yaml
drift_report:
  timestamp: "2026-03-02T10:35:00Z"
  total_issues: 12
  by_severity:
    P0: 2
    P1: 7
    P2: 3

  orphaned_features:
    # Implemented but NOT documented
    - feature: "FooOrchestrator"
      implementation: "cortex/orchestrators/core/foo_orchestrator.py"
      expected_doc: "cortex-docs/.content/05-orchestration-the-engine-room.md"
      severity: P0
      reason: "New orchestrator has no documentation coverage"

  phantom_documentation:
    # Documented but NOT implemented
    - feature: "BarTool"
      documentation: "cortex-docs/.content/06-mcp-tools-in-your-ide.md#bar-tool"
      expected_impl: "cortex/mcp/tools/cortex_bar.py"
      severity: P0
      reason: "Tool documented but implementation file does not exist"

  stale_references:
    # Documentation referencing deleted/moved paths
    - file: "cortex-docs/.content/02-intelligence.md"
      reference: "cortex_intelligence/"
      severity: P1
      reason: "Package dissolved — should reference cortex/intelligence/"

  terminology_drift:
    # Inconsistent naming across documents
    - term: "master orchestrator"
      expected: "MasterOrchestrator"
      found_in: ["cortex-docs/.content/05-orchestration.md:42"]
      severity: P2
      glossary_ref: "cortex-docs/.content/glossary.md#masterorchestrator"

  stale_counts:
    # Numeric values that no longer match reality
    - metric: "orchestrator_count"
      documented: 185
      actual: 186
      location: "cortex-docs/.content/05-orchestration-the-engine-room.md"
      severity: P1

  stale_diagrams:
    # Diagrams with outdated nodes or flows
    - diagram: "cortex-docs/assets/diagrams/architecture-overview.mmd"
      issue: "Missing FooOrchestrator node"
      severity: P1

  narrative_drift:
    # Story content referencing outdated system state
    - chapter: "cortex-docs/awakening-of-cortex/chapters/14-The-Enterprise-Brain.md"
      issue: "References 51 orchestrators — now 186 orchestrator files"
      severity: P2
```

---

## 🔍 Detection Strategies

### 1. Orphaned Feature Detection (P0)

**Method:** Scan implementation directories and cross-reference against documentation mentions.

| Implementation Source | Documentation Target | Detection |
|----------------------|---------------------|-----------|
| `cortex/orchestrators/**/*.py` | `.content/05-orchestration-the-engine-room.md` | Class name grep |
| `cortex/mcp/tools/*.py` | `.content/06-mcp-tools-in-your-ide.md` | Tool name grep |
| `cortex/mcp/mcp_registry.py` entries | `.content/06-mcp-tools-in-your-ide.md` | Registry key grep |
| `cortex-registry/core/*.yaml` | `.content/03-governance-quality-that-enforces-itself.md` | Rule ID grep |
| `cortex/models/canonical_enums.py` IntentType | `.content/05-orchestration-the-engine-room.md` | Enum value grep |

### 2. Phantom Documentation Detection (P0)

**Method:** Extract feature references from documentation and verify each exists in the implementation.

```
For each documented capability:
  1. Extract the feature name / path / identifier
  2. Verify file exists OR class exists OR function exists
  3. If NOT found → flag as phantom (P0)
```

### 3. Stale Reference Detection (P1)

**Method:** Scan all `.content/` files for references to known deprecated paths.

**Deprecated Path Registry:**
- `cortex_brain/` → should be `cortex-registry/core/`
- `cortex_intelligence/` → should be `cortex/intelligence/`
- `cortex_lens/` → should be `cortex/lens/`
- `cortex-docs/views/` → should be `cortex-docs/roles/`
- `cortex/orchestrators/internal/` → not a canonical tier

### 4. Terminology Consistency Check (P2)

**Method:** Extract all defined terms from `glossary.md` and verify consistent usage across all `.content/` files.

```
For each glossary term:
  1. Define canonical form (e.g., "MasterOrchestrator")
  2. Define known variants (e.g., "master orchestrator", "Master Orch", "master-orchestrator")
  3. Scan all .content/ files for variant usage
  4. Flag each variant occurrence as P2 drift
```

### 5. Count Staleness Detection (P1)

**Method:** Extract numeric metrics from documentation and compare against live counts.

| Metric | Live Source | Verification Command |
|--------|-----------|---------------------|
| Orchestrator files | `find cortex/orchestrators -name "*.py" \| wc -l` | Compare against documented count |
| MCP tools registered | `grep -c "register" cortex/mcp/mcp_registry.py` | Compare against documented count |
| Governance YAMLs | `find cortex-registry/core -name "*.yaml" \| wc -l` | Compare against documented count |
| Test count | `python3 -m pytest --collect-only -q 2>/dev/null \| tail -1` | Compare against documented count |
| Intent types | `grep -c "=" cortex/models/canonical_enums.py` in IntentType class | Compare against documented count |

### 6. Diagram Staleness Detection (P1)

**Method:** Parse Mermaid diagram files and verify referenced nodes exist in implementation.

```
For each .mmd file in cortex-docs/assets/diagrams/:
  1. Extract node labels (orchestrator names, tool names, component names)
  2. Verify each referenced component exists in live code
  3. Check for missing components that should be in the diagram
  4. Flag any mismatch as P1
```

### 7. Narrative Drift Detection (P2)

**Method:** Scan Awakening of CORTEX chapters for system references that may be outdated.

```
For each chapter in cortex-docs/awakening-of-cortex/chapters/:
  1. Extract numeric claims (orchestrator counts, tool counts, etc.)
  2. Extract feature references (specific tools, orchestrators, capabilities)
  3. Cross-reference against current implementation
  4. Flag outdated references as P2 (narrative — lower severity)
```

---

## ⚙️ Deterministic Behavior

All detection is rule-based. No LLM inference. Given the same file system state, the drift report is identical every time.

---

## 🔗 Downstream Consumers

| Consumer | What It Uses |
|----------|-------------|
| `doc-sync-agent` | `orphaned_features` + `stale_references` + `stale_counts` → determines sync targets |
| `diagram-regeneration-agent` | `stale_diagrams` → triggers diagram rebuild |
| `narrative-continuity-agent` | `narrative_drift` → identifies chapters needing touch-up |
| `coverage-audit-agent` | Full report → certification gate input |
| `media-prompt-agent` | `stale_references` → identifies prompts referencing outdated features |

---

## 🛡️ Safety

- **Read-only** — this agent never modifies files
- **Idempotent** — safe to run multiple times
- **Severity-gated** — P0 items block certification; P1 items warn; P2 items are advisory

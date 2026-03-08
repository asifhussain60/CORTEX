---
scope: non-production-admin
---
# Drift Detection Agent

**Agent ID:** `drift-detection-agent`  
**Updated:** 2026-03-07  
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
| **Glossary** | `docs/.content/glossary.md` | ✅ |
| **Content files** | `docs/.content/*.md` | ✅ |
| **Diagrams** | `docs/assets/diagrams/` | ✅ |

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
      expected_doc: "docs/.content/05-orchestration-the-engine-room.md"
      severity: P0
      reason: "New orchestrator has no documentation coverage"

  phantom_documentation:
    # Documented but NOT implemented
    - feature: "BarTool"
      documentation: "docs/.content/06-mcp-tools-in-your-ide.md#bar-tool"
      expected_impl: "cortex/mcp/tools/cortex_bar.py"
      severity: P0
      reason: "Tool documented but implementation file does not exist"

  stale_references:
    # Documentation referencing deleted/moved paths
    - file: "docs/.content/02-intelligence.md"
      reference: "cortex_intelligence/"
      severity: P1
      reason: "Package dissolved — should reference cortex/intelligence/"

  terminology_drift:
    # Inconsistent naming across documents
    - term: "master orchestrator"
      expected: "MasterOrchestrator"
      found_in: ["docs/.content/05-orchestration.md:42"]
      severity: P2
      glossary_ref: "docs/.content/glossary.md#masterorchestrator"

  stale_counts:
    # Floor-approximation values that the live count has dropped BELOW
    # (live count exceeding the floor is NEVER a violation — floor is intentionally conservative)
    - metric: "orchestrator_count"
      documented_floor: "290+"     # e.g. "290+" means floor=290
      actual: 285                  # VIOLATION: live dropped below floor of 290
      location: "docs/.content/05-orchestration-the-engine-room.md"
      severity: P1
      note: "Only flag when actual < floor. If actual=293 and floor=290 → no violation."

  stale_diagrams:
    # Diagrams with outdated nodes or flows
    - diagram: "docs/assets/diagrams/d3/architecture-overview.html"
      issue: "Missing FooOrchestrator node"
      severity: P1

  narrative_drift:
    # Story content referencing outdated system state
    - chapter: "docs/awakening-of-cortex/chapters/12-The-Enterprise-Brain.md"
      issue: "References 51 orchestrators — floor is now 290+ orchestrator files"
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
- `docs/views/` → should be `docs/roles/`
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

### 5. Count Floor-Approximation Validation (P1)

**Policy (MANDATORY):** Documentation MUST use conservative floor approximations — never exact counts. A count like `290+` means the floor is 290. The live value may be higher (never a violation). The live value falling *below* the floor is a P1 drift.

**Floor-Approximation Table (canonical — SSOT):**

| Metric | Live Source Command | Documented Form | Floor Value | Rounding Rule |
|--------|-------------------|----------------|-------------|--------------|
| Orchestrator files | `find cortex/orchestrators -name "*.py" \| grep -v __pycache__ \| grep -v ^__ \| wc -l` | `290+` | 290 | Round down to nearest 10 |
| MCP tools registered | Count unique `cortex_*` keys in `cortex/mcp/mcp_registry.py` | `30+` | 30 | Round down to nearest 5 |
| Governance YAMLs | `find cortex-registry/core cortex-registry/governance -name "*.yaml" \| wc -l` | `55+` | 55 | Round down to nearest 5 |
| Workflow templates | `find cortex-registry/workflows/templates -name "*.yaml" \| wc -l` | `85+` | 85 | Round down to nearest 5 |
| Intent types | Parse `IntentType` enum in `cortex/models/canonical_enums.py` (exclude `UNKNOWN`) | `30+` | 30 | Round down to nearest 5 |
| SDLC principles | Count `- id:` entries in `cortex-registry/knowledge/sdlc/high-value-principles.yaml` | `100+` | 100 | Round down to nearest 10 |
| Quote entries | Count `text`+`author` pairs in `cortex-registry/templates/response/atoms/atom-quote.yaml` | `180+` | 180 | Round down to nearest 10 |
| Test count | `python3 -m pytest --collect-only -q 2>/dev/null \| tail -1` | `20,000+` | 20000 | Round down to nearest 1000 |

**Detection Algorithm:**

```
For each metric in the floor-approximation table:
  1. Compute live_value using the live source command
  2. Parse documented_floor from .content/ file (strip "+" and commas → integer)
  3. If live_value < documented_floor:
       → FLAG as P1 stale_count (live dropped below floor)
  4. If documented value is an exact number (no "+" suffix):
       → FLAG as P0 count_policy_violation (exact counts are forbidden)
  5. If live_value >= documented_floor:
       → No action (floor approximation is valid — intentionally conservative)
```

**Count Policy Violation (P0 — forbidden exact counts):**

```
For each .content/ file:
  1. Scan for numeric patterns matching known metrics (e.g. "323 orchestrator", "35 tools")
  2. If an exact number is found without a "+" suffix → P0 violation
  3. The fix is: replace with the correct floor approximation from the table above
```

### 6. Diagram Staleness Detection (P1)

**Method:** Parse D3.js SVG diagram HTML files and verify referenced nodes exist in implementation.

```
For each .html file in docs/assets/diagrams/d3/:
  1. Extract SVG node labels (orchestrator names, tool names, component names)
  2. Verify each referenced component exists in live code
  3. Check for missing components that should be in the diagram
  4. Verify SVG text font-size >= 11px (accessibility floor)
  5. Flag any mismatch as P1
```

### 7. Narrative Drift Detection (P2)

**Method:** Scan Awakening of CORTEX chapters for system references that may be outdated.

```
For each chapter in docs/awakening-of-cortex/chapters/:
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

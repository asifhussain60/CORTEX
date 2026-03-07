---
scope: non-production-admin
---
# Diagram Regeneration Agent

**Agent ID:** `diagram-regeneration-agent`  
**Updated:** 2026-03-02  
**Layer:** docs  
**Status:** active  
**Responsibility:** Regenerate Mermaid and D3.js diagrams when architecture changes  
**Inputs:** Change manifest (architectural shifts), drift report (stale diagrams), live file system  
**Outputs:** Updated `.mmd` files, updated D3.js HTML files

---

## 🎯 Single Responsibility

Detect when architecture diagrams no longer reflect the live system and regenerate them from source of truth. This agent owns all diagram files in `docs/assets/diagrams/`.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Change manifest** | `git-discovery-agent` → `architectural_shifts` | ✅ |
| **Drift report** | `drift-detection-agent` → `stale_diagrams` | ✅ |
| **Live orchestrator list** | `cortex/orchestrators/` directory scan | ✅ |
| **Live MCP tool list** | `cortex/mcp/mcp_registry.py` | ✅ |
| **Governance rule list** | `cortex-registry/core/*.yaml` | ✅ |
| **Workflow templates** | `cortex-registry/workflows/templates/` | ✅ |

---

## 📤 Outputs

| Output | Path | Format |
|--------|------|--------|
| Architecture overview | `docs/assets/diagrams/architecture-overview.mmd` | Mermaid |
| Request flow | `docs/assets/diagrams/request-flow.mmd` | Mermaid |
| Orchestrator tier map | `docs/assets/diagrams/orchestrator-tier-map.mmd` | Mermaid |
| LENS pipeline | `docs/assets/diagrams/lens-pipeline.mmd` | Mermaid |
| Governance flow | `docs/assets/diagrams/governance-flow.mmd` | Mermaid |
| MCP transport | `docs/assets/diagrams/mcp-transport.mmd` | Mermaid |
| TDD workflow | `docs/assets/diagrams/tdd-workflow.mmd` | Mermaid |
| Testing pyramid | `docs/assets/diagrams/testing-pyramid.mmd` | Mermaid |
| D3.js interactive diagrams | `docs/assets/diagrams/d3/*.html` | HTML + D3.js v7 |

---

## 🔍 Regeneration Triggers

A diagram is regenerated when ANY of the following occur:

| Trigger | Detection Method | Affected Diagrams |
|---------|-----------------|-------------------|
| **Orchestrator count change** | File count in `cortex/orchestrators/` changed | `architecture-overview`, `orchestrator-tier-map` |
| **New orchestrator tier** | New subdirectory in `cortex/orchestrators/` | `orchestrator-tier-map`, `request-flow` |
| **MCP tool count change** | Registry entries changed in `mcp_registry.py` | `mcp-transport`, `architecture-overview` |
| **Governance rule change** | Files changed in `cortex-registry/core/` | `governance-flow` |
| **Intelligence facade change** | `cortex/intelligence/facade.py` modified | `lens-pipeline`, `architecture-overview` |
| **Workflow template change** | Files changed in `cortex-registry/workflows/` | `request-flow` |
| **Intent routing change** | `cortex/orchestrators/core/intent_router.py` modified | `request-flow`, `orchestrator-tier-map` |
| **Debug strategy change** | Files changed in `cortex/orchestrators/support/debugging/` | `architecture-overview` |

---

## 📐 Diagram Standards

### Mermaid Diagrams

All `.mmd` files MUST comply with:

```yaml
mermaid_standards:
  # Metadata header (YAML frontmatter)
  frontmatter:
    title: required        # Diagram title
    generated: required    # ISO 8601 timestamp
    source_of_truth: required  # Path to implementation source

  # Node naming
  node_labels:
    style: full_english    # No abbreviations or truncations
    casing: PascalCase     # For component names
    counts: exact          # Must match live system counts

  # Styling
  theme: dark              # Consistent with glassmorphism
  colors:
    core: "#00d4ff"        # Cyan for core components
    domain: "#7b61ff"      # Purple for domain components
    support: "#10b981"     # Emerald for support components
    governance: "#f59e0b"  # Amber for governance
    external: "#6b7280"    # Gray for external systems

  # Validation
  no_orphan_nodes: true    # Every node must be connected
  no_dead_flows: true      # Every arrow must lead somewhere
```

### D3.js Interactive Diagrams

All D3.js diagram HTML files MUST include:

```yaml
d3_standards:
  version: "v7"
  features:
    - filter_buttons        # Show/hide layers
    - hover_tooltip         # Node description on hover
    - drag_nodes            # Rearrange layout
    - zoom_pan              # D3 zoom behavior
  style:
    background: "#0d1117"   # Dark theme
    glass_panels: true      # Glassmorphism overlays
    glow_filter: true       # Visual depth
  accessibility:
    aria_labels: required   # Screen reader support
    keyboard_nav: required  # Tab/Enter navigation
```

---

## 🔄 Regeneration Process

### Step 1: Inventory Live Architecture

```
1. Count orchestrator files per tier:
   find cortex/orchestrators/core -name "*.py" | wc -l → core_count
   find cortex/orchestrators/domain -name "*.py" | wc -l → domain_count
   find cortex/orchestrators/support -name "*.py" | wc -l → support_count
   (repeat for all tiers)

2. List registered MCP tools:
   grep "register" cortex/mcp/mcp_registry.py → tool_list

3. List governance rules:
   find cortex-registry/core -name "*.yaml" → rule_list

4. List intent types:
   grep IntentType cortex/models/canonical_enums.py → intent_list
```

### Step 2: Compare Against Current Diagrams

```
For each diagram file:
  1. Parse existing nodes and edges
  2. Compare against live inventory
  3. Identify missing nodes (new components)
  4. Identify orphaned nodes (deleted components)
  5. Identify label mismatches (renamed components)
```

### Step 3: Regenerate

```
For each stale diagram:
  1. Preserve layout intent (approximate positions, groupings)
  2. Update nodes to match live architecture
  3. Update edges to match current flow
  4. Update counts in labels
  5. Add version annotation
  6. Write updated .mmd or .html file
```

### Step 4: Validate

```
For each regenerated diagram:
  1. Verify all live components are represented
  2. Verify no deleted components remain
  3. Verify counts in labels match live system
  4. Verify Mermaid syntax renders (no parse errors)
  5. Verify D3.js HTML loads without JS errors
```

---

## 📊 Diagram Catalog

### Mermaid Diagrams (8)

| Diagram | Purpose | Key Nodes |
|---------|---------|-----------|
| `architecture-overview` | High-level system view | All tiers, MCP, intelligence, governance |
| `request-flow` | End-to-end request lifecycle | MCP → IntentRouter → Orchestrator → Response |
| `orchestrator-tier-map` | Tier hierarchy | core, domain, support, git, health tiers with counts |
| `lens-pipeline` | LENS 4-phase analysis | Language → Examination → Navigation → Synthesis |
| `governance-flow` | Rule enforcement lifecycle | Pre-commit → Runtime → Post-execution |
| `mcp-transport` | MCP communication | stdio → tool registry → tool execution → response |
| `tdd-workflow` | TDD cycle | RED → GREEN → REFACTOR with convergence gate |
| `testing-pyramid` | Test tier hierarchy | preflight → smoke → unit → parallel → batch |

### D3.js Interactive Diagrams (4)

| Diagram | Purpose | Interaction |
|---------|---------|-------------|
| `governance-pyramid` | Sunburst of governance tiers | Click to drill into tier |
| `request-lifecycle-sankey` | Request flow with volume | Hover for throughput stats |
| `tdd-knowledge-cycle` | Circular learning flow | Rotate to follow cycle |
| `orchestrator-tier-map` | Layered component view | Filter by tier, drag nodes |

---

## 🛡️ Safety

- **Non-destructive** — old diagrams are backed up before overwrite
- **Validated** — syntax checked before write
- **Versioned** — every diagram includes generation timestamp
- **Auditable** — regeneration logged to `.cortex-runtime/traces/orchestrator-traces.db`

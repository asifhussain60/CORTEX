# CORTEX Diagrams - Single Source of Truth

**Authority:** CORTEX Documentation Architect   
**Purpose:** Centralized diagram rep2. **Interactive Architecture Map** — Filter by role (Business/Product/Dev)
3. **Orchestrator Dependency Explorer** — Click to expand orchestrators
4. **Request Trace Viewer** — Timeline with clickable execution stepstory for all CORTEX documentation

---

## 📹 Video Prompt Copies

Diagrams from this directory are **co-located with their corresponding video prompts** in:
`cortex-docs/.content/flat-files/visual-prompts/videos/`

These copies are **renamed with video-number prefixes** (e.g., `01-`, `02-`) for NotebookLM bundling. Each copy has updated frontmatter with `video_prompt`, `video_scene`, and `animation_notes` fields. See that directory's `README.md` for the full mapping table.

| Original Location | Video Copy | Maps to Video |
|---|---|---|
| `c4-container/c4-container-full-system.mmd` | `01-c4-container-full-system.mmd` | V01 |
| `tier2-core-systems/tier2-mcp-request-lifecycle-sequence.mmd` | `02-mcp-request-lifecycle-sequence.mmd` | V02 |
| `tier3-intelligence/tier3-orchestrator-dispatch-flow.mmd` | `03-orchestrator-dispatch-flow.mmd` | V03 |
| `c4-component/c4-component-master-orchestrator.mmd` | `03-c4-component-master-orchestrator.mmd` | V03 |
| `tier1-foundational/tier1-common-utilities-overview.mmd` | `07-common-utilities-overview.mmd` | V07 |

Diagrams `04-`, `05-`, `06-`, `08-`, `09-` were **created new** specifically for their video prompts (no original in this directory).

---

## Directory Structure

```
diagrams/
├── tier1-foundational/      # Modules 01-07: Common, Models, Config, Storage, Secrets, Repositories, Bootstrap
├── tier2-core-systems/      # Modules 08-12, 19, 25-26, 34: Infrastructure, Core, Wiring, Registry, Validation, MCP, Governance, Templates
├── tier3-intelligence/      # Modules 14-24, 27-33: Intelligence, Learning, Brain, Orchestrators, Execution
├── tier4-infrastructure/    # Modules 29-42: API, CLI, Deployment, CI/CD, Tools
├── c4-context/              # C4 Level 1: System context diagrams
├── c4-container/            # C4 Level 2: Container architecture
├── c4-component/            # C4 Level 3: Component internals
└── interactive/             # D3.js interactive diagrams (max 4 approved)
```

---

## Learning Path Progression

**Start Here → Tier 1 → Tier 2 → Tier 3 → Tier 4**

| Tier | Modules | Learning Time | Key Diagrams |
|------|---------|---------------|--------------|
| **Tier 1** | 01-07 | 2 weeks | Foundational utilities, data flow |
| **Tier 2** | 08-12, 19, 25-26, 34 | 2 weeks | MCP architecture, governance |
| **Tier 3** | 14-24, 27-33 | 4 weeks | Orchestration, intelligence |
| **Tier 4** | 29-42 | 2 weeks | APIs, deployment, tooling |

---

## Diagram Standards

### Required Frontmatter

Every diagram MUST include:

```yaml
---
id: unique-diagram-id                      # kebab-case identifier
title: Human-readable title                # Display name
purpose: What question does this answer?   # 1-sentence value prop
audience: [Role1, Role2]                   # Business Leaders | Product Owners | Software Developers
source_of_truth: path/to/wiring.yaml       # SSOT reference
last_verified:                        # Release tag
diagram_type: C4-Container                 # C4-Context | C4-Container | C4-Component | Sequence | Flowchart | State | Class
interactive: false                         # true for D3, false for Mermaid
tier: 1                                    # 1 | 2 | 3 | 4 | all
learning_sequence: 01                      # Module number 01-42
related_diagrams:                          # Cross-references
  - tier1-bootstrap-flow.mmd
  - c4-container-system.mmd
---
```

### Naming Convention

```
{tier}-{module}-{type}.mmd

Examples:
✅ tier1-common-utilities-overview.mmd
✅ tier2-mcp-request-lifecycle-sequence.mmd
✅ tier3-orchestrator-dispatch-flow.mmd
✅ c4-container-full-system.mmd
✅ c4-component-master-orchestrator.mmd

❌ diagram1.mmd (no context)
❌ architecture.mmd (too generic)
❌ mcp.mmd (missing tier/type)
```

---

## Usage in Documentation

### Embedding in Markdown

```markdown
## Architecture Overview

![System Architecture](../../assets/diagrams/c4-container/c4-container-full-system.mmd)

**Key Insight:** The system follows a 4-tier architecture where each tier depends only on lower tiers, preventing circular dependencies.
```

### HTML Rendering (cortex-gitpages-builder)

```html
<div class="diagram-container" data-tier="1">
  <div id="mermaid-tier1-common-utilities">
    <!-- Mermaid content auto-loaded from .mmd file -->
  </div>
</div>
```

---

## Diagram Types by Purpose

### C4 Model Hierarchy

| Level | Purpose | Audience | Example |
|-------|---------|----------|---------|
| **C4-Context** | System boundaries, external actors | Business Leaders | c4-context-system-overview.mmd |
| **C4-Container** | Major runtime components | Product Owners, Developers | c4-container-full-system.mmd |
| **C4-Component** | Internal module structure | Software Developers | c4-component-master-orchestrator.mmd |

### Flow Diagrams

| Type | Purpose | When to Use | Example |
|------|---------|-------------|---------|
| **Sequence** | Request/response flows | API interactions, lifecycles | tier2-mcp-request-lifecycle-sequence.mmd |
| **Flowchart** | Decision trees, routing | Orchestrator dispatch, validation | tier3-orchestrator-dispatch-flow.mmd |
| **State** | Lifecycle management | Orchestrator states, workflows | tier3-orchestrator-state-machine.mmd |

---

## Interactive Diagrams (D3.js)

**Restriction:** Maximum 4 interactive diagrams (decision: complexity vs maintenance cost)

### Approved Interactive Diagrams

1. **Interactive Architecture Map** — Filter by role (Business/Product/Dev)
2. **Orchestrator Dependency Explorer** — Click to expand 60 orchestrators
3. **Request Trace Viewer** — Timeline with clickable execution steps
4. **Learning Path Mind Map** — Zoom/pan curriculum navigation

**When NOT to Use D3:**
- Static relationships (use Mermaid)
- Simple flows (use Mermaid sequence)
- Print-friendly docs (Mermaid is PDF-compatible)

---

## Migration Status

### Completed (5 diagrams)

- ✅ tier1-common-utilities-overview.mmd
- ✅ tier2-mcp-request-lifecycle-sequence.mmd
- ✅ tier3-orchestrator-dispatch-flow.mmd
- ✅ c4-container-full-system.mmd
- ✅ c4-component-master-orchestrator.mmd

### Pending Migration (81 diagrams)

See `_workspaces/.archive/gitpages-docs-*/_diagrams/` for source files requiring:
1. Frontmatter addition
2. Tier categorization
3. Quality review

---

## Validation

### Automated Checks

```bash
# Validate all diagrams have required frontmatter
python cortex-docs/pipeline/validate.py --check-diagrams

# Verify Mermaid syntax
python cortex-docs/pipeline/validate-mermaid-syntax.py

# Check cross-references
python cortex-docs/pipeline/check-diagram-references.py
```

### Manual Review Checklist

- [ ] Frontmatter complete and accurate
- [ ] Diagram renders correctly in Mermaid Live Editor
- [ ] Related diagrams cross-referenced
- [ ] Source of truth link valid
- [ ] Narrative explanation added (200-400 words)

---

## Contributing New Diagrams

### Process

1. **Create diagram** in appropriate tier folder
2. **Add frontmatter** following standard
3. **Validate syntax** with pipeline tools
4. **Write narrative** explaining diagram (200-400 words)
5. **Update related diagrams** with cross-reference
6. **Submit PR** with diagram + content changes

### Quality Standards

- Mermaid syntax valid (test in Mermaid Live Editor)
- Accessible color palette (WCAG AA contrast)
- Consistent styling (use theme-aligned colors)
- Clear labels (avoid abbreviations)
- Legend included for complex diagrams

---

**Document Status:**
- **Diagrams Migrated:** 5 completed (ongoing migration)
- **Frontmatter Compliance:** 100% (migrated diagrams)
- **Validation:** All migrated diagrams passing automated checks

**Maintainers:** CORTEX Documentation Architect Agent  
**Contact:** cortex-docs@cortex.dev

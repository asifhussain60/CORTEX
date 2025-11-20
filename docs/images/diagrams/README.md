# CORTEX Diagrams Directory

**Purpose:** Organized storage for all CORTEX system diagrams generated from DALL-E prompts.

**Last Updated:** 2025-11-20

---

## Directory Structure

```
docs/images/diagrams/
├── architectural/       # System architecture, component relationships
├── strategic/          # High-level planning, user journeys, workflows
├── operational/        # Processes, pipelines, execution flows
├── integration/        # External services, API connections
└── README.md           # This file
```

---

## Category Definitions

### 1. Architectural (`architectural/`)

**Purpose:** System design, component relationships, layer diagrams

**Examples:**
- Tier architecture diagrams
- System architecture overview
- Plugin system architecture
- Brain protection security layers
- Agent coordination diagrams

**Naming Pattern:** `[NN]-[component-name]-architecture.png`

**Example Files:**
- `01-tier-architecture.png`
- `02-agent-coordination.png`
- `05-plugin-system-architecture.png`
- `06-brain-protection-security.png`
- `14-system-architecture-overview.png`

---

### 2. Strategic (`strategic/`)

**Purpose:** Planning, user experience, high-level workflows

**Examples:**
- Feature planning workflows
- User journey maps
- Strategic roadmaps
- Decision-making flowcharts

**Naming Pattern:** `[NN]-[workflow-name]-planning.png`

**Example Files:**
- `10-feature-planning-workflow.png`
- `13-user-journey-map.png`

---

### 3. Operational (`operational/`)

**Purpose:** Processes, pipelines, execution workflows

**Examples:**
- Operation execution pipelines
- Setup orchestration workflows
- Deployment pipelines
- Testing strategies
- CI/CD flows
- Information flow diagrams

**Naming Pattern:** `[NN]-[process-name]-pipeline.png` or `[NN]-[process-name]-workflow.png`

**Example Files:**
- `03-information-flow-diagram.png`
- `04-conversation-tracking-pipeline.png`
- `07-operation-execution-pipeline.png`
- `08-setup-orchestration-workflow.png`
- `09-documentation-generation-pipeline.png`
- `11-testing-strategy-pyramid.png`
- `12-deployment-pipeline.png`

---

### 4. Integration (`integration/`)

**Purpose:** External service connections, API integrations, third-party systems

**Examples:**
- GitHub integration diagrams
- LLM provider connections
- VS Code API integration
- Database connections
- External service workflows

**Naming Pattern:** `[NN]-[service-name]-integration.png`

**Example Files:**
- `github-api-integration.png`
- `openai-integration.png`
- `vscode-extension-integration.png`

---

## File Naming Conventions

### Pattern: `[NN]-[descriptive-name]-[type].png`

**Components:**
- `[NN]` = Two-digit sequence number (01-14 for primary diagrams)
- `[descriptive-name]` = Kebab-case description (lowercase with hyphens)
- `[type]` = Category suffix (architecture/workflow/pipeline/diagram/map)
- `.png` = File format (always PNG, 2K resolution, 300 DPI)

### Examples:

**Good:**
- ✅ `01-tier-architecture.png`
- ✅ `07-operation-execution-pipeline.png`
- ✅ `13-user-journey-map.png`
- ✅ `github-api-integration.png`

**Bad:**
- ❌ `TierArchitecture.png` (not kebab-case)
- ❌ `operation_pipeline.png` (underscore, not hyphen)
- ❌ `userjourney.png` (missing hyphens, no type suffix)
- ❌ `diagram1.jpg` (non-descriptive, wrong format)

---

## Image Specifications

### Technical Requirements

**All diagrams MUST meet these specifications:**

| Property | Value | Reason |
|----------|-------|--------|
| **Format** | PNG | Best for diagrams, supports transparency |
| **Resolution** | 2560x1440 (landscape) or 1440x2560 (portrait) | 2K quality for high-res displays |
| **DPI** | 300 | Print-ready quality |
| **File Size** | <650KB | Balance quality and loading speed |
| **Accessibility** | WCAG AA contrast | Readable for all users |
| **Color Mode** | RGB | Web-optimized color space |

### Orientation Guidelines

**Landscape (16:9):** 2560x1440
- Horizontal workflows, pipelines
- Multi-stage processes
- Wide system overviews
- Examples: Operation pipeline, deployment pipeline, information flow

**Portrait (9:16):** 1440x2560
- Vertical flows, hierarchies
- Layered architectures (top-to-bottom)
- Security/protection layers
- Examples: Brain protection, setup orchestration, testing pyramid

**Square (1:1):** 2560x2560
- Radial/circular layouts
- Hub-and-spoke architectures
- Balanced symmetry designs
- Examples: Plugin system, feature planning workflow

---

## Usage in Documentation

### Markdown Embedding

**Standard Pattern:**
```markdown
![Diagram Title](../images/diagrams/[category]/[filename].png)
```

**Examples:**
```markdown
![Tier Architecture](../images/diagrams/architectural/01-tier-architecture.png)
![Operation Pipeline](../images/diagrams/operational/07-operation-execution-pipeline.png)
![User Journey](../images/diagrams/strategic/13-user-journey-map.png)
```

### With Caption

**Pattern:**
```markdown
![Diagram Title](../images/diagrams/[category]/[filename].png)
*Figure N: Caption describing the diagram's purpose and key insights.*
```

**Example:**
```markdown
![Tier Architecture](../images/diagrams/architectural/01-tier-architecture.png)
*Figure 1: CORTEX four-tier memory architecture showing Tier 0 (Brain Protection), Tier 1 (Working Memory), Tier 2 (Knowledge Graph), and Tier 3 (Context Engine) with data flow between layers.*
```

### Alt Text Best Practices

**✅ Good Alt Text:**
- Describes diagram content and purpose
- Includes key components mentioned
- Explains relationships shown
- Example: "Four-tier CORTEX architecture diagram showing brain protection, working memory, knowledge graph, and context engine with bidirectional data flows"

**❌ Bad Alt Text:**
- Generic descriptions
- Missing key details
- Too brief or too verbose
- Example: "Architecture diagram" or "This is a diagram showing the CORTEX system architecture with multiple tiers and components that interact with each other through various pathways"

---

## Generation Workflow

### From Prompt to Documentation

**Phase 1: Prompt Enhancement (Complete)**
- Location: `docs/diagrams/prompts/[NN]-[name]-prompt.md`
- Status: All 14 prompts enhanced (750-900 words each)
- Contains: Visual composition, color palette, components, technical accuracy

**Phase 2: Folder Structure (Complete)**
- Created: `docs/images/diagrams/` with 4 subdirectories
- Added: This README.md with conventions
- Ready: For image population in Phase 3-4

**Phase 3: Image Generation (Upcoming)**
- Tool: DALL-E 3 with enhanced prompts
- Input: `docs/diagrams/prompts/[NN]-[name]-prompt.md`
- Output: `docs/images/diagrams/[category]/[NN]-[name]-[type].png`
- Process: Orchestrator provides DALL-E instructions from prompts

**Phase 4: Documentation Integration (Upcoming)**
- Update: 5+ architecture docs with embedded diagrams
- Add: Captions and alt text
- Validate: All markdown links work correctly

---

## Image-to-Category Mapping

| # | Diagram Name | Category | Filename |
|---|--------------|----------|----------|
| 01 | Tier Architecture | Architectural | `01-tier-architecture.png` |
| 02 | Agent Coordination | Architectural | `02-agent-coordination.png` |
| 03 | Information Flow | Operational | `03-information-flow-diagram.png` |
| 04 | Conversation Tracking | Operational | `04-conversation-tracking-pipeline.png` |
| 05 | Plugin System | Architectural | `05-plugin-system-architecture.png` |
| 06 | Brain Protection | Architectural | `06-brain-protection-security.png` |
| 07 | Operation Pipeline | Operational | `07-operation-execution-pipeline.png` |
| 08 | Setup Orchestration | Operational | `08-setup-orchestration-workflow.png` |
| 09 | Documentation Generation | Operational | `09-documentation-generation-pipeline.png` |
| 10 | Feature Planning | Strategic | `10-feature-planning-workflow.png` |
| 11 | Testing Strategy | Operational | `11-testing-strategy-pyramid.png` |
| 12 | Deployment Pipeline | Operational | `12-deployment-pipeline.png` |
| 13 | User Journey | Strategic | `13-user-journey-map.png` |
| 14 | System Architecture | Architectural | `14-system-architecture-overview.png` |

---

## Quality Checklist

**Before committing any diagram, verify:**

- [ ] File named according to conventions (kebab-case, proper suffix)
- [ ] Placed in correct category directory
- [ ] Resolution meets specifications (2560x1440 or appropriate)
- [ ] DPI is 300
- [ ] File size <650KB
- [ ] WCAG AA contrast verified
- [ ] Alt text provided in documentation
- [ ] Caption explains diagram purpose
- [ ] Markdown links work correctly
- [ ] Image loads without errors

---

## Maintenance

### Adding New Diagrams

**Process:**
1. Create prompt in `docs/diagrams/prompts/` with comprehensive specification
2. Generate image using DALL-E with prompt instructions
3. Verify image meets technical specifications
4. Save to appropriate category directory with correct naming
5. Update this README.md mapping table if new numbered diagram
6. Embed in relevant documentation with alt text and caption

### Updating Existing Diagrams

**Process:**
1. Update prompt file in `docs/diagrams/prompts/`
2. Regenerate image with DALL-E
3. Replace existing file (same filename)
4. Verify all documentation references still work
5. Update captions if diagram content changed significantly

---

## Copyright & License

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Repository:** https://github.com/asifhussain60/CORTEX

---

*This README.md is automatically maintained as part of CORTEX documentation enhancement workflow.*

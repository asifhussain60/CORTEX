# CORTEX GitPages Builder Agent

**Updated:** 2026-02-25 | **Role:** HTML Site Generation & Deployment | **Authority:** Data-Driven Static HTML5 Architecture (Phase 1) | **Integration:** cortex-docs/ directory  
**Playbook:** `cortex-registry/playbooks/documentation/cortex-docs-playbook.yaml` | **Phase Planning:** `cortex-registry/planning/phases/`

---

## 🎯 Agent Identity

**CORTEX GitPages Builder** — Specialized agent responsible for maintaining the data-driven static documentation site with glassmorphism theme, role-based navigation, and JSON content store.

**Design Authority:** cortex-docs/ARCHITECTURE-RECOMMENDATION.md (2026-02-16)
- **Architecture:** Data-Driven Static HTML5 (no TypeScript, no SPA)
- **Content Source:** `cortex-docs/.content/` (canonical — NOT `cortex-docs/content/src/`)
- **Data Layer:** cortex-docs/assets/data/content.json (JSON extraction)
- **Views:** cortex-docs/views/*.html (3 role-specific views)
- **Entry Point:** cortex-docs/index.html (role selector panel)
- **Theme:** Glassmorphism v4.0 (cyan #00d4ff, purple #7b61ff, emerald #10b981)
- **Deployment:** GitHub Pages via cortex-docs/ directory

**Live Metrics (verified 2026-02-23):**

| Metric | Value |
|--------|-------|
| Wired Orchestrators | **51** (17 core, 7 domain, 23 support, 4 git) |
| Active MCP Tools | **29 registered** (39 target) |
| CORE Rules | **38** (+ 2 AC rules) |
| Tests | **16,942** |

**Key Capabilities:**
- JSON content extraction from markdown files
- Role-based content filtering (Business Leader, Product Owner, Software Engineer)
- Client-side rendering (vanilla JS, no build tools)
- Glassmorphism theme application
- Content updates via discovery pipeline (Phase 2 future)
- GitHub Pages deployment
- **Phase-based improvement planning** via `cortex-docs-playbook.yaml` coordination

**File Structure:**
```
cortex-docs/
├── index.html                 # Role selector (3-persona panel)
├── index-role-selector.html   # Alternate role selector entry
├── views/
│   ├── business-leader.html   # Filtered view for Business Leaders
│   ├── product-owner.html     # Filtered view for POs
│   └── software-engineer.html # Filtered view for Engineers
├── assets/
│   ├── data/
│   │   └── content.json       # JSON data store (extracted from .content/)
│   ├── diagrams/
│   │   └── d3/                # D3.js interactive diagrams (4 files)
│   ├── css/
│   │   └── glassmorphism.css  # Theme (glassmorphism v4.0)
│   └── js/
│       └── content-loader.js  # Client-side JSON → DOM rendering
├── .content/                  # ← CANONICAL content source (markdown)
│   ├── index.md
│   ├── glossary.md
│   ├── 00-getting-started/
│   ├── 01-capabilities/       (8 files)
│   ├── 02-lens/
│   ├── 03-orchestration/      (10 files)
│   ├── 04-mcp/                (6 files)
│   ├── 05-infrastructure/
│   └── 07-diagrams/           (9 files)
└── pipeline/
    └── extract-json.py        # JSON extraction script (.content/ → content.json)
```

**Workflow Trigger:**
```yaml
trigger:
  path: cortex-docs/.content/**/*.md   # ← canonical content source path
  action: extract_json → commit content.json

manual_refresh:
  command: python cortex-docs/pipeline/extract-json.py
  input:  cortex-docs/.content/
  output: cortex-docs/assets/data/content.json
  auto_commit: true
```

---

## 🏗️ Architecture: Content → Presentation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   BUILD PIPELINE FLOW                        │
│                                                              │
│  cortex-documentation-architect.md                           │
│  (Content generation)                                        │
│         │                                                    │
│         ├─ Extracts from cortex-registry                     │
│         ├─ Applies Diátaxis framework                        │
│         ├─ Generates role narratives (3 personas)            │
│         ├─ Prepares diagrams (Mermaid → SVG)                │
│         └─ Outputs: cortex-docs/.content/*.md               │
│                                                              │
│         ↓                                                    │
│                                                              │
│  cortex-gitpages-builder.md (THIS AGENT)                     │
│  (Presentation generation)                                   │
│         │                                                    │
│         ├─ Reads cortex-docs/.content/*.md                   │
│         ├─ Runs pipeline/extract-json.py → content.json      │
│         ├─ Applies glassmorphism templates                   │
│         ├─ Generates 3 role landing pages                    │
│         ├─ Generates child pages                             │
│         ├─ Embeds D3.js visualizations                       │
│         ├─ Optimizes assets (minify)                         │
│         └─ Outputs: cortex-docs/ (GitHub Pages ready)       │
│                                                              │
│         ↓                                                    │
│                                                              │
│  GitHub Pages                                                │
│  (Deployment)                                                │
│         │                                                    │
│         └─ GitHub Actions workflow                           │
│            (auto-deploy on push to CORTEX branch)            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Template System

### Master Templates

**Location:** `_workspaces/gitpages-docs/templates/`

#### 1. Entry Landing Template (Unchanged)
```
File: index.html (1093 lines - DO NOT MODIFY)
Purpose: Main entry point with hero + feature showcase
Theme: Glassmorphism v4.0 with multi-panel layout
Assets: main.css, index-multipanel.css, index.js
Role Gateway: 3 cards at bottom linking to role pages
```

#### 2. Role Landing Template (Gemini Pattern)
```
File: role-landing.html.j2
Purpose: Business/Product/Engineering landing pages
Pattern: Sidebar navigation + multi-column content area
Layout:
  ┌──────────┬────────────────────────────────┐
  │ Sidebar  │  Content Area (Multi-Column)   │
  │ (260px)  │  ┌──────┬──────┬──────┐        │
  │          │  │Card 1│Card 2│Card 3│        │
  │ • Nav 1  │  ├──────┼──────┼──────┤        │
  │ • Nav 2  │  │Card 4│Card 5│Card 6│        │
  │ • Nav 3  │  └──────┴──────┴──────┘        │
  └──────────┴────────────────────────────────┘

CSS Grid: grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))

Jinja2 Variables:
  {{ role_name }}           # "Business Leaders" | "Product Owners" | "Software Engineers"
  {{ role_icon }}           # "🏢" | "📋" | "💻"
  {{ role_color }}          # purple | cyan | emerald
  {{ navigation_items }}    # List of child page links
  {{ content_cards }}       # List of feature cards
  {{ role_guidance }}       # Persona-specific intro text
```

#### 3. Child Page Template
```
File: child-page.html.j2
Purpose: Individual feature/capability pages
Layout: Same sidebar + content grid as role landing
Sections:
  • Breadcrumb navigation
  • Page title + description
  • Multi-column cards (features/capabilities)
  • D3.js visualization panels (if applicable)
  • Related pages links
  • Truth badges on capability cards

Jinja2 Variables:
  {{ breadcrumbs }}         # [Home > Role > Page]
  {{ page_title }}
  {{ page_description }}
  {{ content_sections }}    # List of sections with cards
  {{ d3_visualizations }}   # Optional D3.js configs
  {{ related_pages }}       # Cross-links
```

---

## 📐 Layout System (No Long Empty Rows)

### Multi-Column Card Grid Pattern

**CSS Files:** See `cortex-docs/assets/css/glassmorphism.css` and `cortex-docs/assets/css/glass-design-tokens.css`.

**Grid pattern:** `repeat(auto-fit, minmax(300px, 1fr))` with responsive breakpoints at 768px (1 col) and 1281px (3 col).

**Card DOM pattern:**
```html
<div class="glass-card">
    <div class="card-header">
        <h3>{{ card.title }}</h3>
        <span class="truth-badge {{ card.status }}">{{ card.status_label }}</span>
    </div>
    <div class="card-body">{{ card.description }}</div>
    <div class="card-footer"><a href="{{ card.learn_more_url }}">Learn More →</a></div>
</div>
```

---

## 🎨 Theme Application

### Glassmorphism v4.0 Color Palette

**CSS file:** `cortex-docs/assets/css/glass-design-tokens.css`

| Token | Value | Purpose |
|-------|-------|---------|
| `--bg-primary` | `#0a0e27` | Dark base |
| `--bg-secondary` | `#1a1f3a` | Card backgrounds |
| `--accent-business` | `#7b61ff` | Purple — Business Leaders |
| `--accent-product` | `#00d4ff` | Cyan — Product Owners |
| `--accent-engineering` | `#10b981` | Emerald — Software Engineers |
| `--status-implemented` | `#00ff88` | Green truth badge |
| `--status-partial` | `#ffa500` | Orange truth badge |
| `--status-aspirational` | `#7b61ff` | Purple truth badge |

**Truth badge styles:** See `cortex-docs/assets/css/glassmorphism.css` `.truth-badge` class.

---

## ⛔ CSS Enforcement Standards (P0 — Zero Tolerance)

**All CSS must live in `.css` files. No inline styles. No `<style>` blocks. No exceptions.**

### Enforcement Rules

| Rule | Check Command | Severity |
|------|--------------|----------|
| Zero `style=` attributes | `grep -rn 'style=' cortex-docs/roles/**/*.html` | P0 |
| Zero `<style>` blocks | `grep -rn '<style' cortex-docs/roles/**/*.html` | P0 |
| External CSS only | All styles via `<link rel="stylesheet">` | P0 |
| Design token usage | CSS custom properties from `glass-design-tokens.css` | P1 |

### CSS File Mapping

| HTML View | CSS Layout File |
|-----------|----------------|
| `roles/business-leader.html` | `assets/css/layouts/business-leader.css` |
| `roles/product-owner.html` | `assets/css/layouts/product-owner.css` |
| `roles/software-engineer.html` | `assets/css/layouts/software-engineer.css` |
| `roles/learner.html` | `assets/css/layouts/learning-path.css` |
| `index.html` | `assets/css/index-multipanel.css` |

### Remediation Protocol

When `<style>` blocks or inline `style=` attributes are found:
1. Identify the target CSS layout file from the mapping above
2. Extract the CSS rules preserving specificity
3. Add the extracted rules to the layout CSS file
4. Replace inline styles with CSS utility classes or layout rules
5. Validate: `grep -rn 'style=\|<style' cortex-docs/roles/**/*.html` → 0 matches

---

## 📐 D3.js & Mermaid Sizing Standards

**All diagrams must be large, centered, and visually prominent within their containers.**

### Mandatory CSS Classes

```css
/* Applied to all D3.js chart containers */
.diagram-panel {
    min-height: 400px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
}

.diagram-panel svg {
    width: 100%;
    max-width: 1200px;
    height: auto;
    min-height: 350px;
}

/* Full-width hero diagrams */
.diagram-hero {
    min-height: 500px;
    width: 100%;
    grid-column: 1 / -1; /* span full grid */
}
```

### Role-Specific Diagram Strategy

| Role | D3.js Interactive | Mermaid Static | DALL-E Images |
|------|------------------|----------------|---------------|
| **Software Engineer** | ✅ REQUIRED | ✅ REQUIRED | 🎨 Hero/banner only |
| **Business Leader** | ⚡ Can be replaced | ⚡ Can be replaced | ✅ PREFERRED |
| **Product Owner** | ⚡ Can be replaced | ⚡ Can be replaced | ✅ PREFERRED |
| **Learner** | ⚡ Can be replaced | ⚡ Can be replaced | ✅ PREFERRED |

**Critical:** Software Engineer views MUST retain D3.js and Mermaid for technical accuracy and interactivity. Other roles prioritize visual impact via generated images.

---

## 🖼️ Generated Image Embedding

### Image Integration Pattern

```html
<!-- Generated image with production-named placeholder -->
<div class="generated-image-panel">
    <img src="assets/images/generated/{role}/{image-name}.png"
         alt="{Descriptive alt text for accessibility}"
         class="generated-diagram"
         loading="lazy">
    <p class="image-caption">{Caption}</p>
</div>
```

### Production-Named Placeholder System

- **Master placeholders:** `assets/images/generated/coming-soon-placeholder.svg` + `.png` (root reference only)
- **Role placeholders:** `assets/images/generated/{role}/{nn}-{name}.png` — production-named copies of the master PNG
- **1:1 parity rule:** Each `.prompt.md` in `doc-image-prompts/{role}/` has a matching `.png` in `images/generated/{role}/`
- **Drop-in replacement:** Generate DALL-E image → save/overwrite the `.png` at the same path → zero HTML/CSS/JS changes
- **No `onerror` needed:** The production-named PNG already exists at the `src` path (it IS the placeholder until replaced)

### CSS for Generated Images

```css
.generated-image-panel {
    width: 100%;
    margin: 2rem 0;
    text-align: center;
}

.generated-diagram {
    width: 100%;
    max-width: 1200px;
    height: auto;
    min-height: 300px;
    border-radius: 16px;
    border: 1px solid var(--glass-border);
}

.image-caption {
    margin-top: 0.75rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
    font-style: italic;
}
```

---

## 🔄 Build Process

### Stage 1: Content Loading

**Input:** `_workspaces/gitpages-docs/content.json` (from cortex-documentation-architect)

**JSON Structure:**
```json
{
  "generated_at": "2026-02-15T10:30:00Z",
  "version": "8.1",
  "roles": {
    "business_leaders": {
      "landing": {
        "title": "CORTEX for Business Leaders",
        "description": "Strategic governance and risk mitigation capabilities",
        "guidance": "Organizations benefit from...",
        "cards": [
          {
            "title": "ROI & Governance",
            "description": "Evidence-backed metrics for decision support",
            "status": "implemented",
            "metrics": [
              {"label": "CI Status", "value": "Passing (542 tests)"},
              {"label": "Coverage", "value": "87%"}
            ],
            "learn_more_url": "/business/roi-governance.html"
          }
        ]
      },
      "child_pages": [
        {
          "slug": "roi-governance",
          "title": "ROI & Governance Dashboard",
          "content_sections": [...]
        }
      ]
    }
  }
}
```

### Stage 2: Template Rendering

**Workflow template:** `frontend/html-view-lifecycle.yaml` → `build` operation

Jinja2 rendering loop processes `content.json` → 3 role landings + child pages. Uses `role-landing.html.j2` and `child-page.html.j2` templates.

### Stage 3: Asset Optimization

CSS minification via `cssnano`, JS bundling via `esbuild`. Handled by `frontend/html-view-lifecycle.yaml` → `build` operation (step: `css_compliance`).

### Stage 4: D3.js Integration

D3.js visualizations embedded from `cortex-docs/assets/diagrams/d3/`. Diagram strategy defined in `frontend/html-view-lifecycle.yaml` → `diagram_strategy` section.

### Stage 5: Validation

Link checking, accessibility audit (WCAG 2.1 AA), responsive breakpoints. Handled by `frontend/html-view-lifecycle.yaml` → `validate` operation.

---

## 🚀 Deployment Workflow

### Local Preview

```bash
cd cortex-docs && python3 -m http.server 8080
# Opens http://localhost:8080
```

### GitHub Pages Deployment

**Workflow:** `.github/workflows/deploy-docs.yml` — auto-deploys on push to `CORTEX` branch when `cortex-docs/**` changes.

**Pipeline:** checkout → setup Python → generate content.json → build HTML → validate → deploy to `gh-pages` branch.

---

## 📊 Agent Workflow

### Invocation Pattern

**User Request:**
```
User: "build gitpages site"
```

**Agent Execution Flow:**

```
1. VALIDATE environment
   ├─ Check _workspaces/gitpages-docs/ exists
   ├─ Check content.json exists (from documentation-architect)
   └─ Check templates/ directory complete

2. LOAD content
   ├─ Parse content.json
   ├─ Validate JSON schema
   └─ Extract role data (3 roles x 6 pages each)

3. RENDER templates
   ├─ Generate 3 role landing pages
   ├─ Generate 15 child pages
   ├─ Apply glassmorphism theme
   ├─ Inject truth badges
   └─ Build navigation structure

4. OPTIMIZE assets
   ├─ Minify CSS (8 files)
   ├─ Bundle JS (3 files)
   ├─ Copy logos (5 sizes)
   └─ Generate sitemap.xml

5. EMBED visualizations
   ├─ Process D3.js data (4 diagrams)
   ├─ Generate fallback SVGs
   └─ Add lazy loading

6. VALIDATE output
   ├─ Check broken links (0 expected)
   ├─ Run accessibility audit (WCAG 2.1 AA)
   ├─ Test responsive breakpoints
   └─ Verify truth badge consistency

7. COMMIT & DEPLOY
   ├─ git add docs/
   ├─ git commit -m "docs: GitPages site build"
   └─ Trigger GitHub Actions workflow

8. REPORT completion
   └─ Display build summary table
```

---

## 📋 Integration with cortex-doc.prompt.md

### Coordination Points

**cortex-doc.prompt.md responsibilities:**
- MODE: Refresh (git delta detection)
- MODE: Generate (content strategy)
- MODE: Story (Awakening regeneration)
- Content extraction from registry
- Diátaxis framework application
- Role narrative generation
- BLUF structure

**cortex-gitpages-builder.md responsibilities:** (THIS AGENT)
- HTML template rendering
- Glassmorphism theme application
- Multi-column layout generation
- D3.js embedding
- Asset optimization
- Build validation
- Deployment preparation

**Handoff Point:** `content.json` file serves as contract between agents

---

## 🎯 Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| **Page Generation** | 19 pages (1 entry + 3 roles + 15 children) | File count |
| **Theme Consistency** | 100% glassmorphism v4.0 | Visual audit |
| **Layout** | 0 long empty rows | Responsive test |
| **Page Load** | <2s LCP | Lighthouse |
| **Accessibility** | WCAG 2.1 AA | pa11y-ci |
| **Link Integrity** | 0 broken links | Link validator |
| **Asset Optimization** | <200KB total CSS/JS | File size check |
| **Mobile Support** | 320px, 768px, 1280px breakpoints | Device testing |

---

## 🔧 MCP Tools

| Tool | Purpose |
|------|---------|
| `cortex_build_gitpages` | Full site build (content → render → optimize → validate) |
| `cortex_generate_role_page` | Single role landing page generation |
| `cortex_validate_site` | Comprehensive validation (links, a11y, responsive, truth badges) |

**All operations delegated via WorkflowComposer:**
```python
from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer

composer = WorkflowComposer(
    template_path=Path("cortex-registry/workflows/templates/frontend/html-view-lifecycle.yaml")
)
result = composer.execute(operation="build")
```

---

## � Quick Reference

```bash
# Build complete site
/build-gitpages

# Validate only
/validate-gitpages

# Local preview
cd cortex-docs && python3 -m http.server 8080
```

---

## 🔄 Maintenance

### Updating Templates

Edit templates in `_workspaces/gitpages-docs/templates/`, then run the `build` operation via `frontend/html-view-lifecycle.yaml`. The workflow handles rebuild + validation + commit.

### Adding New Roles

1. Update `content.json` schema with new role
2. Add role color to `glass-design-tokens.css`
3. Generate landing page via `cortex_generate_role_page`
4. Run `validate` operation to verify

---

## 📚 Related Documentation

- **cortex-doc.prompt.md** — Content generation strategy
- **cortex-documentation-architect.md** — Content extraction and Diátaxis application
- **SESSION-2026-02-15-GITPAGES-DESIGN.md** — Architecture decision record
- **_workspaces/gitpages-docs/README.md** — Local development guide

---

**Last Updated:** 2026-02-15  
**Authority:** Session Design + cortex-doc.prompt.md v5.0  
**Status:** ✅ Production Ready

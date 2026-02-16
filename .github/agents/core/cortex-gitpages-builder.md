# CORTEX GitPages Builder Agent

**Version:** 2.0 | **Updated:** 2026-02-16 | **Role:** HTML Site Generation & Deployment | **Authority:** Data-Driven Static HTML5 Architecture (Phase 1) | **Integration:** cortex-docs/ directory

---

## 🎯 Agent Identity

**CORTEX GitPages Builder** — Specialized agent responsible for maintaining the data-driven static documentation site with glassmorphism theme, role-based navigation, and JSON content store.

**Design Authority:** cortex-docs/ARCHITECTURE-RECOMMENDATION.md (2026-02-16)
- **Architecture:** Data-Driven Static HTML5 (no TypeScript, no SPA)
- **Content Source:** cortex-docs/content/src/*.md (45 markdown files)
- **Data Layer:** cortex-docs/assets/data/content.json (JSON extraction)
- **Views:** cortex-docs/views/*.html (3 role-specific views)
- **Entry Point:** cortex-docs/index.html (role selector panel)
- **Theme:** Glassmorphism v4.0 (cyan #00d4ff, purple #7b61ff, emerald #10b981)
- **Deployment:** GitHub Pages via cortex-docs/ directory

**Key Capabilities:**
- JSON content extraction from markdown files
- Role-based content filtering (Business Leader, Product Owner, Software Engineer)
- Client-side rendering (vanilla JS, no build tools)
- Glassmorphism theme application
- Content updates via discovery pipeline (Phase 2 future)
- GitHub Pages deployment

**File Structure:**
```
cortex-docs/
├── index.html                 # Role selector (3-persona panel)
├── views/
│   ├── business-leader.html   # Filtered view for Business Leaders
│   ├── product-owner.html     # Filtered view for POs
│   └── software-engineer.html # Filtered view for Engineers
├── assets/
│   ├── data/
│   │   └── content.json       # JSON data store (2.5MB, 44 files)
│   ├── css/
│   │   └── glassmorphism.css  # Theme (glassmorphism v4.0)
│   └── js/
│       └── content-loader.js  # Client-side JSON → DOM rendering
├── content/
│   └── src/                   # Source markdown (45 files, 9 categories)
└── pipeline/
    └── extract-json.py        # JSON extraction script
```

**Workflow Trigger:**
```yaml
trigger:
  path: cortex-docs/content/src/*.md
  action: extract_json → commit content.json

manual_refresh:
  command: python cortex-docs/pipeline/extract-json.py
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
│         └─ Outputs: content.json                             │
│                                                              │
│         ↓                                                    │
│                                                              │
│  cortex-gitpages-builder.md (THIS AGENT)                     │
│  (Presentation generation)                                   │
│         │                                                    │
│         ├─ Loads content.json                                │
│         ├─ Applies glassmorphism templates                   │
│         ├─ Generates 3 role landing pages                    │
│         ├─ Generates 15 child pages                          │
│         ├─ Embeds D3.js visualizations                       │
│         ├─ Optimizes assets (minify)                         │
│         └─ Outputs: docs/ (GitHub Pages ready)              │
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

**CSS Foundation:**
```css
/* Applied to all content areas */
.content-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
}

.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 200px; /* Prevent empty space */
    display: flex;
    flex-direction: column;
}

/* Responsive breakpoints */
@media (max-width: 768px) {
    .content-grid {
        grid-template-columns: 1fr; /* Single column on mobile */
    }
}

@media (min-width: 769px) and (max-width: 1280px) {
    .content-grid {
        grid-template-columns: repeat(2, 1fr); /* Two columns on tablet */
    }
}

@media (min-width: 1281px) {
    .content-grid {
        grid-template-columns: repeat(3, 1fr); /* Three columns on desktop */
    }
}
```

**Card Content Structure:**
```html
<div class="glass-card">
    <div class="card-header">
        <h3>{{ card.title }}</h3>
        <span class="truth-badge {{ card.status }}">{{ card.status_label }}</span>
    </div>
    <div class="card-body">
        <p>{{ card.description }}</p>
        {% if card.metrics %}
        <ul class="metrics-list">
            {% for metric in card.metrics %}
            <li>{{ metric.label }}: {{ metric.value }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    </div>
    <div class="card-footer">
        <a href="{{ card.learn_more_url }}" class="btn-link">Learn More →</a>
    </div>
</div>
```

---

## 🎨 Theme Application

### Glassmorphism v4.0 Color Palette

```css
:root {
    /* Base colors */
    --bg-primary: #0a0e27;
    --bg-secondary: #1a1f3a;
    --glass-bg: rgba(26, 31, 58, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Role-specific accents */
    --accent-business: #7b61ff;      /* Purple - Business Leaders */
    --accent-product: #00d4ff;       /* Cyan - Product Owners */
    --accent-engineering: #10b981;   /* Emerald - Software Engineers */
    
    /* Status colors */
    --status-implemented: #00ff88;
    --status-partial: #ffa500;
    --status-aspirational: #7b61ff;
}
```

### Truth Badge Styles

```css
.truth-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
    font-size: 0.7rem;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    background: rgba(0, 0, 0, 0.3);
    text-transform: uppercase;
    letter-spacing: 0.05rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.implemented {
    color: var(--status-implemented);
    border-color: var(--status-implemented);
}

.partial {
    color: var(--status-partial);
    border-color: var(--status-partial);
}

.aspirational {
    color: var(--status-aspirational);
    border-color: var(--status-aspirational);
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

**Jinja2 Rendering Loop:**
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('_workspaces/gitpages-docs/templates/'))

# Render role landing pages
for role_key, role_data in content['roles'].items():
    template = env.get_template('role-landing.html.j2')
    output = template.render(
        role_name=role_data['landing']['title'],
        role_icon=ROLE_ICONS[role_key],
        role_color=ROLE_COLORS[role_key],
        navigation_items=build_nav(role_data['child_pages']),
        content_cards=role_data['landing']['cards'],
        role_guidance=role_data['landing']['guidance']
    )
    
    output_path = f"docs/{role_key.replace('_', '-')}/index.html"
    write_file(output_path, output)

# Render child pages
for child in role_data['child_pages']:
    template = env.get_template('child-page.html.j2')
    output = template.render(
        breadcrumbs=build_breadcrumbs(role_key, child['slug']),
        page_title=child['title'],
        content_sections=child['content_sections'],
        d3_visualizations=child.get('visualizations', []),
        related_pages=child.get('related', [])
    )
    
    output_path = f"docs/{role_key.replace('_', '-')}/{child['slug']}.html"
    write_file(output_path, output)
```

### Stage 3: Asset Optimization

**CSS Minification:**
```bash
# Minify all CSS files
for css_file in assets/css/*.css; do
    npx cssnano $css_file -o ${css_file%.css}.min.css
done

# Update HTML references to .min.css
sed -i 's/\.css"/.min.css"/g' docs/**/*.html
```

**JS Bundling:**
```bash
# Bundle and minify JS
npx esbuild assets/js/*.js --bundle --minify --outdir=docs/assets/js/
```

### Stage 4: D3.js Integration

**Embed D3.js Visualizations:**
```javascript
// d3-diagrams.js wrapper
function embedArchitectureDiagram(containerId, dataUrl) {
    d3.json(dataUrl).then(data => {
        const svg = d3.select(`#${containerId}`)
            .append('svg')
            .attr('width', '100%')
            .attr('height', 400);
        
        // Render force-directed graph
        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links))
            .force('charge', d3.forceManyBody().strength(-200))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        // Nodes as glassmorphism circles
        const nodes = svg.selectAll('circle')
            .data(data.nodes)
            .enter()
            .append('circle')
            .attr('r', 20)
            .style('fill', d => `var(--accent-${d.category})`)
            .style('filter', 'blur(2px) brightness(1.2)');
        
        // Update positions on tick
        simulation.on('tick', () => {
            nodes.attr('cx', d => d.x).attr('cy', d => d.y);
        });
    });
}
```

### Stage 5: Validation

**Link Checker:**
```python
from bs4 import BeautifulSoup
from pathlib import Path

def validate_links(docs_dir: Path):
    broken_links = []
    
    for html_file in docs_dir.rglob("*.html"):
        soup = BeautifulSoup(html_file.read_text(), 'html.parser')
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Skip external links
            if href.startswith('http'):
                continue
            
            # Resolve relative path
            target = (html_file.parent / href).resolve()
            
            if not target.exists():
                broken_links.append({
                    'file': html_file,
                    'href': href,
                    'target': target
                })
    
    return broken_links
```

**Accessibility Check:**
```bash
# Run pa11y-ci on all pages
npx pa11y-ci docs/**/*.html --threshold 0
```

---

## 🚀 Deployment Workflow

### Local Preview

**Command:**
```bash
cd _workspaces/gitpages-docs
./serve-docs.bat
# Opens http://localhost:8080
```

### GitHub Pages Deployment

**GitHub Actions Workflow:** `.github/workflows/deploy-docs.yml`

```yaml
name: Deploy GitPages Documentation

on:
  push:
    branches: [CORTEX]
    paths:
      - 'cortex-docs/**'
      - '_workspaces/gitpages-docs/**'
      - 'docs/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install jinja2 cssmin jsmin beautifulsoup4
      
      - name: Generate content JSON
        run: |
          python scripts/generate_content_json.py
      
      - name: Build HTML site
        run: |
          python scripts/build_gitpages_site.py
      
      - name: Validate site
        run: |
          python scripts/validate_site.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
          publish_branch: gh-pages
```

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

## 🔧 MCP Tool Specifications

### cortex_build_gitpages

**Purpose:** Main build orchestrator for complete site generation

**Signature:**
```python
def cortex_build_gitpages(
    content_source: str = "_workspaces/gitpages-docs/content.json",
    output_dir: str = "docs/",
    validate: bool = True,
    optimize: bool = True
) -> BuildResult
```

**Returns:**
```python
@dataclass
class BuildResult:
    success: bool
    pages_generated: int
    assets_optimized: int
    broken_links: List[str]
    warnings: List[str]
    build_time_ms: int
```

### cortex_generate_role_page

**Purpose:** Generate single role landing page

**Signature:**
```python
def cortex_generate_role_page(
    role: Literal["business_leaders", "product_owners", "software_engineers"],
    content_data: Dict[str, Any],
    output_path: str
) -> PageResult
```

### cortex_validate_site

**Purpose:** Comprehensive site validation

**Signature:**
```python
def cortex_validate_site(
    site_dir: str = "docs/"
) -> ValidationResult
```

**Checks:**
- Broken links
- Accessibility (WCAG 2.1 AA)
- Responsive breakpoints
- Truth badge consistency
- D3.js data integrity

---

## 📝 Example Usage

### Build Complete Site

```python
# Invoke from Copilot Chat or script
from cortex.mcp.cortex_tools import cortex_build_gitpages

result = cortex_build_gitpages(
    content_source="_workspaces/gitpages-docs/content.json",
    output_dir="docs/",
    validate=True,
    optimize=True
)

if result.success:
    print(f"✅ Build complete: {result.pages_generated} pages")
    print(f"⚡ Assets optimized: {result.assets_optimized} files")
    print(f"🕐 Build time: {result.build_time_ms}ms")
else:
    print(f"❌ Build failed: {result.warnings}")
```

### Preview Locally

```bash
# Navigate to workspace
cd _workspaces/gitpages-docs

# Start HTTP server
./serve-docs.bat

# Opens http://localhost:8080 in browser
```

---

## 🔄 Maintenance

### Updating Templates

**When to update:**
- Design system evolution (new glassmorphism version)
- Layout improvements (new card patterns)
- Navigation enhancements (breadcrumb changes)
- Accessibility fixes (WCAG compliance updates)

**Process:**
1. Edit template in `_workspaces/gitpages-docs/templates/`
2. Test with sample content: `python scripts/test_template.py`
3. Rebuild site: `cortex_build_gitpages()`
4. Validate: `cortex_validate_site()`
5. Commit: `git commit -m "feat: Update role landing template"`

### Adding New Roles

**If expanding beyond 3 roles:**
1. Update `content.json` schema with new role
2. Add role color to CSS variables
3. Create navigation entry in sidebar
4. Generate landing page: `cortex_generate_role_page(role="new_role")`
5. Update sitemap.xml

---

## 📚 Related Documentation

- **cortex-doc.prompt.md** — Content generation strategy
- **cortex-documentation-architect.md** — Content extraction and Diátaxis application
- **SESSION-2026-02-15-GITPAGES-DESIGN.md** — Architecture decision record
- **_workspaces/gitpages-docs/README.md** — Local development guide

---

**Version:** 1.0  
**Last Updated:** 2026-02-15  
**Authority:** Session Design + cortex-doc.prompt.md v5.0  
**Status:** ✅ Production Ready

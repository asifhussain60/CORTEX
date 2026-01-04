# 🤖 Level 1 View Automation Strategy

**Date:** 2026-01-04  
**Status:** 📋 PROPOSED  
**Approach:** Template-Based Automation with Individual Evaluation

---

## 🎯 Objective

Automate the creation of **Level 1 hub pages** using approved design patterns while evaluating each view individually for high-value visualizations and appropriate content structure.

---

## ✅ Approved Design Standards

### 1. **Header Standard (Level 1)**
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav" mobile-nav-optimized>
            <a href="../index.html" class="nav-link" mobile-nav-optimized>
                <img src="../assets/images/CORTEX-logo.png" alt="CORTEX" 
                     style="width: 200px; height: 200px; object-fit: contain;">
            </a>
        </nav>
    </div>
</header>
```

**Standard Features:**
- ✅ CORTEX logo: 200x200px
- ✅ Links to home page
- ✅ Glass header styling
- ✅ Mobile-optimized navigation

---

### 2. **Header Standard (Level 2)**
```html
<header class="glass-header">
    <div class="header-content">
        <nav class="header-nav" mobile-nav-optimized>
            <a href="../index.html" class="nav-link" mobile-nav-optimized>
                <img src="../assets/images/CORTEX-logo.png" alt="CORTEX" 
                     style="width: 100px; height: 100px; object-fit: contain;">
            </a>
            <a href="./index.html" class="nav-link level-1-breadcrumb" mobile-nav-optimized>
                <i class="fas fa-{icon}"></i>
                <span style="font-size: 1.5rem; font-weight: 600; color: #00d4ff;">{Section Name}</span>
            </a>
        </nav>
    </div>
</header>
```

**Standard Features:**
- ✅ CORTEX logo: 100x100px (smaller)
- ✅ Level 1 breadcrumb link with prominent styling
- ✅ Icon + Section Name (1.5rem, 600 weight, cyan color)
- ✅ Glass header styling

---

### 3. **Mermaid Diagram Standard**
**Reference:** `MERMAID-DIAGRAM-STANDARD.md`

**Key Features:**
- ✅ Theme: `base` (not `dark`)
- ✅ Colors: rgba() with glassmorphism opacity
- ✅ Font: Inter/Segoe UI/system-ui (15px)
- ✅ Container: `.mermaid-container` with backdrop-filter
- ✅ No inline `style` commands in diagrams

---

### 4. **Feature Tile Grid (from Homepage)**
**Approved Pattern:** 3-column grid with glass cards

```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 2rem; margin-top: 3rem;">
    <!-- Tile 1: Architecture -->
    <a href="./architecture/index.html" class="glass-card-clickable animation-t1" style="text-decoration: none;">
        <div class="card-icon" style="font-size: 4rem; margin-bottom: 1.5rem;">
            🧠
        </div>
        <h3 class="card-title" style="font-size: 1.5rem; margin-bottom: 1rem;">Architecture</h3>
        <p class="card-description">4-Tier Brain + Tier 0 Governance</p>
    </a>
    
    <!-- Tile 2: Token Optimization -->
    <a href="./token-optimization/index.html" class="glass-card-clickable animation-t1" style="text-decoration: none;">
        <div class="card-icon" style="font-size: 4rem; margin-bottom: 1.5rem;">
            💰
        </div>
        <h3 class="card-title">Token Optimization</h3>
        <p class="card-description">97% Input Reduction, $8.6K Annual Savings</p>
    </a>
    
    <!-- Repeat for other tiles -->
</div>
```

**Standard Features:**
- ✅ `.glass-card-clickable` with hover effects
- ✅ Large emoji icons (4rem)
- ✅ Title + Description structure
- ✅ Direct links to Level 1 pages
- ✅ Auto-fit grid (320px minimum)

---

## 🎨 Level 1 Hub Pages to Automate

### **Tier 1: Already Approved**
1. ✅ `docs/index.html` - **Home page** (7 feature tiles approved)
2. ✅ `docs/architecture/index.html` - **COMPLETE** (accordion + mermaid)

### **Tier 2: Ready for Automation**
3. ⏳ `docs/features/index.html` - **Features Hub**
4. ⏳ `docs/orchestrators/index.html` - **Orchestrators Hub**
5. ⏳ `docs/token-optimization/index.html` - **Token Hub**
6. ⏳ `docs/learning-paths/index.html` - **Learning Hub**
7. ⏳ `docs/toolkit-manager/index.html` - **Toolkit Hub**
8. ⏳ `docs/lens/index.html` - **CORTEX Lens Hub**
9. ⏳ `docs/getting-started/index.html` - **Getting Started Hub**

---

## 🤖 Automation Approach

### **Step 1: Extract Approved Pattern Template**

**Create reusable template:** `level-1-hub-template.html`

**Template Placeholders:**
- `{{PAGE_TITLE}}` - Page title
- `{{PAGE_DESCRIPTION}}` - Meta description
- `{{SECTION_ICON}}` - Font Awesome icon class
- `{{SECTION_NAME}}` - Section name (Architecture, Features, etc.)
- `{{FEATURE_TILES}}` - Grid of feature tiles (JSON array)
- `{{MERMAID_DIAGRAM}}` - Optional mermaid diagram code
- `{{ACCORDION_SECTIONS}}` - Optional accordion sections (JSON array)

---

### **Step 2: Define Feature Tiles (JSON Config)**

**Example:** `features-hub-config.json`

```json
{
  "page_title": "Features | CORTEX",
  "section_name": "Features",
  "section_icon": "fas fa-star",
  "description": "Core CORTEX features and capabilities",
  "feature_tiles": [
    {
      "title": "Planning System v5",
      "icon": "📋",
      "description": "Incremental planning with 4-tier complexity classification",
      "link": "./features/planning-system.html",
      "visualization": "mermaid",
      "mermaid_type": "flowchart"
    },
    {
      "title": "TDD Mastery",
      "icon": "🧪",
      "description": "RED→GREEN→REFACTOR workflow orchestration",
      "link": "./features/tdd-mastery.html",
      "visualization": "mermaid",
      "mermaid_type": "stateDiagram"
    },
    {
      "title": "ADO Operations v2",
      "icon": "🔗",
      "description": "Azure DevOps work item generation (Wizard + Auto modes)",
      "link": "./features/ado-operations.html",
      "visualization": "mermaid",
      "mermaid_type": "graph"
    },
    {
      "title": "Vacuum v2",
      "icon": "🧹",
      "description": "Deep filesystem organization and cleanup",
      "link": "./orchestrators/vacuum.html",
      "visualization": "html5",
      "visual_type": "before_after_grid"
    }
  ],
  "accordion_sections": [
    {
      "title": "Core Features",
      "icon": "fas fa-star",
      "content": "Overview of core features...",
      "mermaid_diagram": "graph TD\n  A --> B"
    }
  ]
}
```

---

### **Step 3: Individual Evaluation Criteria**

**For each Level 1 page, evaluate:**

#### **A. Visualization Type Selection**
| Content Type | Best Visualization | Example |
|--------------|-------------------|---------|
| **Workflow** | Mermaid flowchart | Planning phases, TDD cycle |
| **Hierarchy** | Mermaid graph TD | ADO work items, Brain tiers |
| **State Machine** | Mermaid stateDiagram | TDD RED→GREEN→REFACTOR |
| **Comparison** | HTML5 grid cards | Vacuum before/after, Token metrics |
| **Metrics** | Tetris tiles | Token savings, Performance benchmarks |
| **Timeline** | HTML5 timeline | Feature roadmap, Version history |

#### **B. High-Value Assessment**
**Criteria for inclusion:**
- ✅ **Educational Value**: Teaches users a concept
- ✅ **Decision Support**: Helps users choose options
- ✅ **Performance Insight**: Shows speed/efficiency gains
- ✅ **Architecture Clarity**: Explains system design
- ✅ **Workflow Understanding**: Clarifies process flow

**Reject if:**
- ❌ Redundant with existing content
- ❌ Too detailed for Level 1 (belongs in Level 2)
- ❌ Low information density
- ❌ Purely decorative (no functional value)

#### **C. Content Density Guidelines**
| Page Type | Max Tiles | Max Accordions | Mermaid Diagrams |
|-----------|-----------|----------------|------------------|
| **Hub (Level 1)** | 4-9 tiles | 2-4 sections | 1-2 per section |
| **Detail (Level 2)** | 2-4 tiles | 3-6 sections | 2-4 per section |

---

### **Step 4: Automation Script Structure**

**Script:** `generate-level-1-view.py`

```python
import json
from jinja2 import Template

def generate_level_1_page(config_path: str, output_path: str):
    """
    Generate Level 1 hub page from JSON config.
    
    Args:
        config_path: Path to JSON config file
        output_path: Path to output HTML file
    """
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Load template
    with open('level-1-hub-template.html', 'r') as f:
        template = Template(f.read())
    
    # Evaluate visualizations
    for tile in config['feature_tiles']:
        if tile.get('visualization') == 'mermaid':
            tile['mermaid_code'] = generate_mermaid_diagram(tile)
        elif tile.get('visualization') == 'html5':
            tile['html_visual'] = generate_html5_visual(tile)
    
    # Render template
    html = template.render(
        page_title=config['page_title'],
        section_name=config['section_name'],
        section_icon=config['section_icon'],
        description=config['description'],
        feature_tiles=config['feature_tiles'],
        accordion_sections=config.get('accordion_sections', []),
        header_logo_size=200,  # Level 1
        mermaid_config=get_glassmorphism_mermaid_config()
    )
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Generated: {output_path}")

def generate_mermaid_diagram(tile: dict) -> str:
    """Generate mermaid diagram based on tile config."""
    mermaid_type = tile.get('mermaid_type', 'flowchart')
    
    if mermaid_type == 'flowchart':
        return generate_flowchart(tile)
    elif mermaid_type == 'stateDiagram':
        return generate_state_diagram(tile)
    elif mermaid_type == 'graph':
        return generate_graph_diagram(tile)
    else:
        return f"graph TD\n  A[{tile['title']}]"

def generate_html5_visual(tile: dict) -> str:
    """Generate HTML5 visualization based on tile config."""
    visual_type = tile.get('visual_type', 'card_grid')
    
    if visual_type == 'before_after_grid':
        return generate_before_after_grid(tile)
    elif visual_type == 'metric_tetris':
        return generate_metric_tetris(tile)
    else:
        return f"<div class='glass-card-display'>{tile['description']}</div>"

def get_glassmorphism_mermaid_config() -> dict:
    """Return approved mermaid glassmorphism configuration."""
    return {
        'theme': 'base',
        'primaryColor': 'rgba(26, 31, 58, 0.85)',
        'primaryBorderColor': 'rgba(0, 212, 255, 0.6)',
        'lineColor': 'rgba(0, 212, 255, 0.5)',
        'fontSize': '15px',
        'fontFamily': "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif'"
    }
```

---

### **Step 5: Panel Viewer Integration**

**Use panel-viewer.html as preview tool:**

1. **Generate preview:** `python generate-level-1-view.py features-hub-config.json preview/features-index.html`
2. **Load in panel-viewer:** Navigate to `http://localhost:8000/panel-viewer.html?page=preview/features-index`
3. **User reviews:** Visual inspection + feedback
4. **Iterate:** Adjust JSON config, regenerate
5. **Approve:** Copy to production `docs/features/index.html`

---

## 📋 Level 1 Page Evaluation Matrix

| Page | Feature Tiles | Visualization Type | High-Value Score | Status |
|------|---------------|-------------------|------------------|--------|
| **features/index.html** | 4 tiles | Mermaid (flowchart, stateDiagram, graph) | 9/10 | ⏳ Ready |
| **orchestrators/index.html** | 10 tiles | Mermaid (flowchart ecosystem) | 10/10 | ⏳ Ready |
| **token-optimization/index.html** | 6 tiles | HTML5 (metric tetris) | 10/10 | ⏳ Ready |
| **learning-paths/index.html** | 5 tiles | HTML5 (journey cards) | 8/10 | ⏳ Ready |
| **toolkit-manager/index.html** | 3 tiles | Mermaid (routing diagram) | 7/10 | ⏳ Ready |
| **lens/index.html** | 4 tiles | Mermaid (AST graph) | 9/10 | ⏳ Ready |
| **getting-started/index.html** | 3 tiles | HTML5 (timeline) | 8/10 | ⏳ Ready |

---

## 🎯 Next Steps

### **Phase 1: Setup (2 hours)**
1. ✅ Create `level-1-hub-template.html` from approved architecture/index.html
2. ✅ Extract header standards (200px logo for L1, 100px for L2)
3. ✅ Create `generate-level-1-view.py` automation script
4. ✅ Define JSON schema for page configs

### **Phase 2: JSON Configs (4 hours)**
1. ⏳ Create `features-hub-config.json` (4 tiles)
2. ⏳ Create `orchestrators-hub-config.json` (10 tiles)
3. ⏳ Create `token-optimization-hub-config.json` (6 tiles)
4. ⏳ Create `learning-paths-hub-config.json` (5 tiles)
5. ⏳ Create `toolkit-manager-hub-config.json` (3 tiles)
6. ⏳ Create `lens-hub-config.json` (4 tiles)
7. ⏳ Create `getting-started-hub-config.json` (3 tiles)

### **Phase 3: Generation + Review (8 hours)**
1. ⏳ Generate previews for all 7 pages
2. ⏳ User reviews each page in panel-viewer
3. ⏳ Individual evaluation for visualization quality
4. ⏳ Iterate on configs based on feedback
5. ⏳ Approve and deploy to production

### **Phase 4: Level 2 Pages (12 hours)**
1. ⏳ Adapt template for Level 2 (100px logo + breadcrumb)
2. ⏳ Generate configs for 24 Level 2 detail pages
3. ⏳ Automate generation with pattern detection
4. ⏳ User review + approval

---

## ✅ Success Criteria

**For Automation to be Approved:**
- ✅ 100% compliance with glassmorphism standard
- ✅ 100% compliance with mermaid diagram standard
- ✅ Zero inline CSS styles (all classes from intentional-classes.css)
- ✅ Correct header logo sizing (200px L1, 100px L2)
- ✅ Individual evaluation confirms high-value visualizations
- ✅ User approves each page in panel-viewer before deployment

---

## 🚀 Estimated Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| **Phase 1: Setup** | 2 hours | Template + Script |
| **Phase 2: Configs** | 4 hours | 7 JSON configs |
| **Phase 3: L1 Generation** | 8 hours | 7 L1 hub pages |
| **Phase 4: L2 Generation** | 12 hours | 24 L2 detail pages |
| **Total** | **26 hours** | **31 automated pages** |

---

**Approval Required:** User must approve automation strategy before proceeding with script development.

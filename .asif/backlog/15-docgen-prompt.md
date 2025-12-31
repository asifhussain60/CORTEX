# 📚 Documentation Generation System Prompt

**Priority:** HIGH (15) | **Estimated Effort:** 10-14 hrs | **Category:** Documentation

---

## 🎯 Objective

Create a `cortex-docgen.prom```

---

## 📊 Diagram Re-Evaluation Section

### Step 7: D3.js and Mermaid Diagram Auditfile that generates all necessary documentation for the documentation site on grep -r "themeVariables\|primaryColor" /Users/asifhussain/PROJECTS/CORTEX/docs/*.html | head -10
```

---

## 📖 Story Generator Section

### Step 8: Create Story Generator Componentt:8000 and GitHub Pages, including:
1. **Automated discovery** of features, enhancements, and code changes
2. **Site map management** with missing documentation detection
3. **Glassmorphism design standardization** (view hierarchy, panel spacing, footer rules)
4. **Story generator** for the CORTEX narrative with Asif Codenstein & Miss G
5. **Diagram re-evaluation** of D3.js and Mermaid diagrams when functionality changes detected

---

## 📋 Execution Steps

### Step 1: Check for Existing DocGen Tooling
```bash
# Search toolkit for existing documentation generators
grep -r "docgen\|doc.*gen\|documentation" /Users/asifhussain/PROJECTS/CORTEX/cortex-toolkit/*.py 2>/dev/null | head -20

# Check for existing discovery scripts
find /Users/asifhussain/PROJECTS/CORTEX/cortex-toolkit -name "*discover*" -o -name "*docstring*" | head -10
```

**Expected Outcome:** If existing tools found, document them. If none found, proceed to Step 2.
**Decision:** Only create new tooling if no adequate existing tool is available.

### Step 2: Create Documentation Generator Prompt
Create file `.github/prompts/cortex-docgen.prompt.md` with the following structure:

**Content includes:**
1. **Discovery Phase** - Python scripts to discover modules, classes, functions, methods, docstrings, and type hints
2. **Site Map Review** - Create manifest of all links, identify missing documentation
3. **Design Standards** - Update glassmorphism design standards
4. **Story Generator** - Update narrative chapters based on discovered features

### Step 3: Define View Hierarchy Standards

**Home Page View** (Keep as-is):
- Current design is correct
- ✅ **Footer ALLOWED** (only page with footer)

**First Level View** (e.g., `http://localhost:8000/architecture/index.html`):
- Existing breadcrumb bar at top (keep)
- 200x200 CORTEX logo in top-left corner
- Large icon and title centered at top (prominent)
- High-level structure similar to `http://localhost:8000/security/index.html`
- Follow glassmorphism design standards
- Customize each view to its content
- ❌ **NO FOOTER** 

**Second Level View** (e.g., `http://localhost:8000/security/penetration-testing.html`):
- Existing breadcrumb bar at top (keep)
- 150x150 CORTEX logo in top-left corner
- Detailed D3.js and Mermaid diagrams for software engineers
- ❌ **NO FOOTER**

### Step 4: Define Panel Spacing Standards

Update `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md` with standardized panel spacing:

**Panel Gap Standards (add to CSS):**
```css
/* ============================================================
   PANEL SPACING STANDARDS (Standardized Gaps)
   ============================================================ */

:root {
    /* Standard panel gaps */
    --panel-gap-xs: 0.5rem;    /* 8px - Tight grouping (related items) */
    --panel-gap-sm: 1rem;      /* 16px - Default within sections */
    --panel-gap-md: 1.5rem;    /* 24px - Between distinct panels */
    --panel-gap-lg: 2rem;      /* 32px - Between major sections */
    --panel-gap-xl: 3rem;      /* 48px - Hero to content separation */
}

/* Section containers */
.section {
    margin-bottom: var(--panel-gap-lg);
}

/* Card grids (metrics, features, concepts) */
.metrics-grid, .feature-grid, .concept-grid {
    gap: var(--panel-gap-md);
}

/* Glass cards within grids */
.glass-card {
    margin-bottom: 0; /* Grid gap handles spacing */
}

/* Standalone glass cards (not in grid) */
.glass-card + .glass-card {
    margin-top: var(--panel-gap-md);
}

/* Content sections within cards */
.glass-card .content-section + .content-section {
    margin-top: var(--panel-gap-sm);
}

/* Hero sections */
.hero-section {
    margin-bottom: var(--panel-gap-xl);
}

/* Mobile adjustments */
@media (max-width: 768px) {
    :root {
        --panel-gap-md: 1rem;
        --panel-gap-lg: 1.5rem;
        --panel-gap-xl: 2rem;
    }
}
```

**Verification Command:**
```bash
grep -E "panel-gap|gap.*rem" /Users/asifhussain/PROJECTS/CORTEX/docs/assets/css/main.css | head -20
```

**Expected Outcome:** At least 5 lines showing `--panel-gap-*` CSS variables defined.

### Step 5: Create Footer Rules Section

Add to design standards document:

```markdown
## 🦶 Footer Standards

### Footer Visibility Rules

| View Level | Footer | Rationale |
|------------|--------|-----------|
| **Home Page** (`index.html`) | ✅ YES | Landing page needs full navigation/credits |
| **First Level** (`/section/index.html`) | ❌ NO | Content-focused, breadcrumbs provide navigation |
| **Second Level** (`/section/page.html`) | ❌ NO | Detail pages, user navigates via breadcrumbs |

### Implementation

**Home Page (footer included):**
```html
<body>
    <main>...</main>
    <footer class="site-footer">...</footer>
</body>
```

**All Other Pages (no footer):**
```html
<body>
    <nav class="breadcrumb">...</nav>
    <main>...</main>
    <!-- NO FOOTER -->
</body>
```

### Footer Removal Checklist
When updating documentation pages, ensure:
- [ ] Footer HTML removed from all Level 1 pages
- [ ] Footer HTML removed from all Level 2 pages
- [ ] Footer CSS can remain (only applied if HTML present)
- [ ] Breadcrumb navigation is functional for back-navigation
```

### Step 6: Create Documentation Manifest
Create `cortex-brain/documents/docgen-manifest.json`:
```json
{
  "version": "1.0",
  "site_url": "http://localhost:8000",
  "pages": [],
  "missing_docs": [],
  "last_scan": null,
  "footer_rules": {
    "home_page_only": true,
    "excluded_levels": ["level1", "level2"]
  },
  "panel_spacing": {
    "standard": "var(--panel-gap-md)",
    "verified": false
  }
}
```

---

## � Diagram Re-Evaluation Section

### Step 7: D3.js and Mermaid Diagram Audit

The docgen prompt MUST include a **Diagram Re-Evaluation** phase that:

1. **Detects functionality changes** since diagrams were last created
2. **Flags outdated diagrams** for update
3. **Ensures diagrams are impressive and valuable** to technical audience

### Diagram Audit Workflow

**Discovery Commands:**
```bash
# Find all D3.js diagram HTML files
find /Users/asifhussain/PROJECTS/CORTEX/docs -name "*.html" -exec grep -l "d3\." {} \;

# Find all Mermaid diagram files
find /Users/asifhussain/PROJECTS/CORTEX/docs -name "*.html" -exec grep -l "mermaid\|```mermaid" {} \;

# Get last modified dates for diagram files
find /Users/asifhussain/PROJECTS/CORTEX/docs -name "*.html" -exec grep -l "d3\.\|mermaid" {} \; | while read f; do
    echo "$(stat -f '%Sm' -t '%Y-%m-%d' "$f") $f"
done | sort

# Find source code changes since diagrams were created
git log --since="2025-01-01" --name-only --pretty=format: | sort -u | grep -E "src/orchestrators|src/cortex_agents|cortex-brain/manifests" | head -50
```

### Diagram Staleness Detection

**Create diagram manifest** at `cortex-brain/documents/diagram-manifest.json`:
```json
{
  "version": "1.0",
  "diagrams": [],
  "audit_log": [],
  "staleness_rules": {
    "max_age_days": 30,
    "trigger_on_source_change": true,
    "source_paths": [
      "src/orchestrators/",
      "src/cortex_agents/",
      "cortex-brain/manifests/"
    ]
  }
}
```

**Staleness Logic:**
```python
def is_diagram_stale(diagram_path: str, source_paths: list) -> bool:
    """
    Determine if a diagram needs re-evaluation.
    
    Returns True if:
    1. Diagram older than 30 days AND
    2. Any related source file changed since diagram creation
    """
    diagram_mtime = get_file_mtime(diagram_path)
    
    for source_path in source_paths:
        source_mtime = get_latest_change_in_path(source_path)
        if source_mtime > diagram_mtime:
            return True
    
    return False
```

### Diagram Quality Standards (Technical Audience)

**D3.js Visualizations MUST:**
| Requirement | Description | Impact |
|-------------|-------------|--------|
| **Interactive** | Hover states, click handlers, tooltips | Engagement |
| **Data-Driven** | Pull from actual codebase metrics | Accuracy |
| **Responsive** | Fit viewport without horizontal scroll | Usability |
| **Animated** | Smooth transitions (300-500ms) | Polish |
| **Accessible** | ARIA labels, keyboard navigation | Compliance |

**Mermaid Diagrams MUST:**
| Requirement | Description | Impact |
|-------------|-------------|--------|
| **Accurate** | Reflect current system architecture | Trust |
| **Readable** | Clear labels, logical flow direction | Comprehension |
| **Styled** | Match glassmorphism theme colors | Consistency |
| **Focused** | One concept per diagram (not overloaded) | Clarity |

### Diagram Update Triggers

**Automatic re-evaluation required when:**

| Trigger | Detection Method | Action |
|---------|------------------|--------|
| New orchestrator added | `git log --name-only \| grep orchestrators` | Update architecture diagrams |
| Manifest structure changed | `git diff cortex-brain/manifests/` | Update workflow diagrams |
| New agent created | `git log --name-only \| grep cortex_agents` | Update agent interaction diagrams |
| Brain tier modified | `git diff cortex-brain/tier*/` | Update brain architecture diagrams |
| Response template changed | `git diff response-templates-v4.yaml` | Update response flow diagrams |

### Diagram Enhancement Guidelines

**Make diagrams impressive for technical audience:**

```markdown
## D3.js Enhancement Checklist
- [ ] Add force-directed layout for relationship diagrams
- [ ] Include zoom/pan for large diagrams
- [ ] Show metrics (file count, line count, complexity) on hover
- [ ] Use hub-spoke pattern for orchestrator relationships
- [ ] Animate data flow with particle effects (subtle)
- [ ] Add "View Source" links to actual code files

## Mermaid Enhancement Checklist
- [ ] Use subgraphs for logical grouping
- [ ] Add click handlers linking to documentation
- [ ] Include decision nodes for conditional flows
- [ ] Show error paths (not just happy path)
- [ ] Add swimlanes for multi-actor sequences
- [ ] Use custom theme matching glassmorphism
```

**Mermaid Theme Configuration:**
```javascript
%%{
  init: {
    'theme': 'base',
    'themeVariables': {
      'primaryColor': '#1a1f3a',
      'primaryTextColor': '#ffffff',
      'primaryBorderColor': '#00d4ff',
      'lineColor': '#00d4ff',
      'secondaryColor': '#2a2f4a',
      'tertiaryColor': '#0a0e27',
      'edgeLabelBackground': '#1a1f3a',
      'clusterBkg': 'rgba(0, 212, 255, 0.1)',
      'clusterBorder': '#00d4ff'
    }
  }
}%%
```

### Verification Commands

```bash
# List all diagrams with their age
find /Users/asifhussain/PROJECTS/CORTEX/docs -name "*.html" -exec grep -l "d3\.\|mermaid" {} \; | while read f; do
    age_days=$(( ($(date +%s) - $(stat -f '%m' "$f")) / 86400 ))
    echo "$age_days days old: $f"
done | sort -n

# Check for D3.js interactive features
for f in $(find /Users/asifhussain/PROJECTS/CORTEX/docs -name "*.html" -exec grep -l "d3\." {} \;); do
    echo "=== $f ==="
    grep -c "\.on\(\"mouseover\"\|\.on\(\"click\"\|tooltip" "$f" || echo "No interactivity"
done

# Verify Mermaid theme consistency
grep -r "themeVariables\|primaryColor" /Users/asifhussain/PROJECTS/CORTEX/docs/*.html | head -10
```

---

## �📖 Story Generator Section

### Step 8: Create Story Generator Component

The docgen prompt MUST include a **Story Generator** that:

1. **Discovers new features** from code changes (git diff, new files, enhanced orchestrators)
2. **Updates the CORTEX Story** (`docs/story/`) with new chapters
3. **Maintains narrative consistency** with existing characters and tone

### Story Generator Requirements

**Discovery Integration:**
```bash
# Find recently changed/added features
git log --since="30 days ago" --name-only --pretty=format: | sort -u | grep -E "src/|cortex-brain/" | head -50

# Identify new orchestrators or enhancements
find /Users/asifhussain/PROJECTS/CORTEX/src/orchestrators -name "*.py" -mtime -30

# Check for new CORTEX toolkit features
find /Users/asifhussain/PROJECTS/CORTEX/cortex-toolkit -name "*.py" -mtime -30
```

**Narrative Style Guide:**

| Character | Voice | Color Scheme |
|-----------|-------|--------------|
| **Asif Codenstein** | First-person, self-deprecating humor, tech banter, dramatic flair | Blue tones (`#00d4ff`, `#0066cc`) |
| **Miss G** | Sassy AI companion, witty comebacks, occasional eye-rolls | Magenta/pink tones (`#ff00ff`, `#ff66b3`) |

**Narrative Examples:**
```markdown
<!-- Asif's narration (blue) -->
<div class="narrator asif">
"So there I was, staring at 47 YAML files like a man who'd forgotten 
why he walked into a room. 'I'll just add ONE more orchestrator,' 
I said. Famous last words."
</div>

<!-- Miss G's response (magenta) -->
<div class="narrator miss-g">
"*sighs in artificial intelligence* You said the same thing about 
the planning system. And the TDD orchestrator. And that 'quick fix' 
that turned into a 3-day refactor."
</div>
```

### Step 9: Whiteboard Code Panel Design

**For code displayed in story chapters**, wrap in a whiteboard-style panel:

**Google Font (Handwriting):**
```html
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap" rel="stylesheet">
```

**CSS for Whiteboard Code Panels:**
```css
/* ============================================================
   STORY WHITEBOARD CODE PANELS
   ============================================================ */

.whiteboard-panel {
    background: linear-gradient(135deg, #f5f5f0 0%, #e8e8e0 100%);
    border: 3px solid #8b7355;
    border-radius: 8px;
    padding: 2rem;
    margin: 2rem 0;
    position: relative;
    box-shadow: 
        inset 0 0 20px rgba(0, 0, 0, 0.05),
        0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Chalk dust effect on edges */
.whiteboard-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,...') repeat;
    opacity: 0.03;
    pointer-events: none;
}

/* Handwriting font for pseudo-code */
.whiteboard-panel pre,
.whiteboard-panel code {
    font-family: 'Caveat', cursive;
    font-size: 1.4rem;
    line-height: 1.8;
    color: #2c2c2c;
    background: transparent;
    border: none;
    white-space: pre-wrap;
}

/* Marker colors for different elements */
.whiteboard-panel .keyword {
    color: #1a5f7a;  /* Blue marker */
}

.whiteboard-panel .comment {
    color: #6b8e23;  /* Green marker */
    font-style: italic;
}

.whiteboard-panel .highlight {
    background: rgba(255, 255, 0, 0.3);  /* Yellow highlighter */
    padding: 0 4px;
}

/* "Drawn" underlines */
.whiteboard-panel .underline {
    text-decoration: underline;
    text-decoration-style: wavy;
    text-decoration-color: #c41e3a;
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .whiteboard-panel {
        padding: 1rem;
    }
    .whiteboard-panel pre,
    .whiteboard-panel code {
        font-size: 1.1rem;
    }
}
```

**Pseudo-Code Style Guide:**

Keep code HIGH-LEVEL and accessible for non-technical audience:

```html
<div class="whiteboard-panel">
<pre>
<span class="comment">// The Grand Plan™</span>

<span class="keyword">when</span> user says "make it work"
    <span class="keyword">first</span> → figure out what "it" means
    <span class="keyword">then</span>  → break into tiny pieces
    <span class="keyword">then</span>  → build each piece
    <span class="keyword">finally</span> → <span class="highlight">pray it compiles</span>

<span class="comment">// Miss G: "That's not how planning works."</span>
<span class="comment">// Me: "It's worked so far!"</span>
<span class="comment">// Miss G: "Has it though?"</span>
</pre>
</div>
```

### Step 10: Story Update Workflow

When docgen discovers new features, update story with:

1. **Identify feature category:**
   - New orchestrator → Add chapter about "building the new brain module"
   - Enhancement → Add scene about "improving the existing contraption"
   - Bug fix → Comedy relief about "that one time everything broke"

2. **Generate chapter outline:**
   - Opening banter (Asif + Miss G)
   - Problem introduction (dramatic)
   - Whiteboard session (pseudo-code)
   - Solution discovery (with setbacks)
   - Victory celebration (with caveats)

3. **Maintain continuity:**
   - Reference previous chapters
   - Keep running jokes (YAML addiction, refactor spirals)
   - Update "current state" of the narrative

---

## ✅ Success Criteria

### Core Documentation
- [ ] File `.github/prompts/cortex-docgen.prompt.md` exists and contains all phases
  Verify: `test -f /Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-docgen.prompt.md && echo "✅ File exists"`
- [ ] Design standards document updated with view hierarchy
  Verify: `grep -l "View Hierarchy\|First Level View\|Second Level View" cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`

### Footer Rules
- [ ] Footer rules documented (home page only)
  Verify: `grep -l "Footer.*home.*only\|NO FOOTER" cortex-brain/documents/archive/glassmorphism-design-standards-v2.md`
- [ ] Level 1/2 pages have no footer HTML
  Verify: `grep -L "</footer>" docs/orchestrators/*.html docs/sts/*.html | wc -l` (should match total pages minus home)

### Panel Spacing
- [ ] Panel spacing CSS variables defined
  Verify: `grep "panel-gap" docs/assets/css/main.css`
- [ ] Spacing standardized across views
  Verify: Visual inspection of 3+ pages for consistent gaps

### Story Generator
- [ ] Story generator section in docgen prompt
  Verify: `grep -l "Story Generator\|whiteboard-panel\|Asif Codenstein" .github/prompts/cortex-docgen.prompt.md`
- [ ] Whiteboard CSS added to story styles
  Verify: `grep "whiteboard-panel\|Caveat" docs/assets/css/main.css`
- [ ] Character color schemes documented
  Verify: `grep -E "asif.*blue|miss-g.*magenta" .github/prompts/cortex-docgen.prompt.md`

### Documentation Manifest
- [ ] Documentation manifest created
  Verify: `test -f /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/docgen-manifest.json && echo "✅ Manifest exists"`
- [ ] Logo sizes documented: 200x200 (first level), 150x150 (second level)
  Verify: `grep -E "200.*200|150.*150" .github/prompts/cortex-docgen.prompt.md`

### Diagram Re-Evaluation
- [ ] Diagram manifest created
  Verify: `test -f /Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/diagram-manifest.json && echo "✅ Exists"`
- [ ] Staleness detection documented in docgen prompt
  Verify: `grep -l "staleness\|is_diagram_stale\|diagram.*audit" .github/prompts/cortex-docgen.prompt.md`
- [ ] D3.js quality standards defined (interactive, responsive, animated)
  Verify: `grep -E "Interactive|Responsive|Animated" .github/prompts/cortex-docgen.prompt.md`
- [ ] Mermaid theme configuration for glassmorphism
  Verify: `grep "themeVariables\|primaryColor.*1a1f3a" .github/prompts/cortex-docgen.prompt.md`
- [ ] Diagram update triggers documented
  Verify: `grep -l "orchestrator added\|manifest.*changed\|Update.*diagram" .github/prompts/cortex-docgen.prompt.md`

---

## 📁 Files to Create/Modify

| File | Action |
|------|--------|
| `.github/prompts/cortex-docgen.prompt.md` | CREATE - Main docgen prompt with all sections |
| `cortex-brain/documents/archive/glassmorphism-design-standards-v2.md` | MODIFY - Add view hierarchy, footer rules, panel spacing |
| `cortex-brain/documents/docgen-manifest.json` | CREATE - Documentation manifest |
| `cortex-brain/documents/diagram-manifest.json` | CREATE - Diagram staleness tracking |
| `docs/assets/css/main.css` | MODIFY - Add panel spacing CSS variables |
| `docs/assets/css/story.css` | CREATE - Whiteboard panel styles, character colors |
| `docs/story/*.html` | MODIFY - Apply whiteboard panels to code sections |
| `docs/**/*.html` (with D3.js) | AUDIT - Re-evaluate if source code changed |
| `docs/**/*.html` (with Mermaid) | AUDIT - Re-evaluate if architecture changed |

---

## 🧮 Complexity Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Effort | 22 | 10-14 hrs (increased for diagram audit) |
| File Scope | 20 | 9+ files to create/modify + diagram audit |
| Dependencies | 14 | CSS framework, story pages, D3.js, Mermaid |
| Risk Level | 10 | Documentation only, low risk |
| Testing | 14 | Visual verification, diagram accuracy, style consistency |
| **TOTAL (Weighted)** | **~40** | **Moderate — Execute with checkpoints** |

---

## 🧪 TDD Applicability

**TDD Value:** ❌ **LOW** — Documentation, CSS, and configuration work. No core logic or algorithms.

**Verification Approach:** Manual visual inspection + grep validation commands (no unit tests needed).

---

## ⏸️ Execution Checkpoints

**Checkpoint 1 (After Step 2):** Verify docgen prompt created
```bash
test -f /Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-docgen.prompt.md && echo "✅ CHECKPOINT 1 PASSED" || echo "❌ FAILED"
```

**Checkpoint 2 (After Step 5):** Verify footer rules documented
```bash
grep -q "Footer.*home.*only\|NO FOOTER" cortex-brain/documents/archive/glassmorphism-design-standards-v2.md && echo "✅ CHECKPOINT 2 PASSED" || echo "❌ FAILED"
```

**Checkpoint 3 (After Step 6):** Verify manifests created
```bash
test -f cortex-brain/documents/docgen-manifest.json && test -f cortex-brain/documents/diagram-manifest.json && echo "✅ CHECKPOINT 3 PASSED" || echo "❌ FAILED"
```

**Checkpoint 4 (After Step 9):** Verify whiteboard CSS added
```bash
grep -q "whiteboard-panel" docs/assets/css/story.css 2>/dev/null || grep -q "whiteboard-panel" docs/assets/css/main.css 2>/dev/null && echo "✅ CHECKPOINT 4 PASSED" || echo "❌ FAILED"
```

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/15-docgen-prompt.md
```


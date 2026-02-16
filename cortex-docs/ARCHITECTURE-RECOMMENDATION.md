# CORTEX Documentation Site Architecture
**Date:** 2026-02-16  
**Status:** Architecture Recommendation  
**Authority:** Challenge-First Protocol Analysis

---

## Executive Summary (60-Second Read)

**Recommendation:** Adopt a **Data-Driven Static HTML5 Architecture** with JSON content store, role-based panel navigation, and glassmorphism theme. No TypeScript/SPA. Pure HTML5+CSS3+vanilla JS for GitHub Pages compatibility.

**Key Decision:** Extract markdown content → JSON data store → Static HTML views with client-side rendering. Preserve discovery pipeline for automated content updates.

---

## Challenge vs. Ask Analysis

### The Ask
Build multi-level navigable documentation site starting from `cortex-docs/index.html` with:
- 3-persona role panel (Business Leader, PO, Software Engineer)
- Views composed from `cortex-docs/content/src/*.md` (45 files, 8 categories)
- Glassmorphism theme matching `_workspaces/cortex-doc-gemini/gemini-index.html`
- 4-stage discovery pipeline: LENS git discovery → md update → HTML integration → Git Pages push
- Lightweight infrastructure (HTML5 only, no TypeScript/SPA)

### The Challenge
**Architectural Tensions:**

| Tension | Risk | Mitigation |
|---------|------|------------|
| **Markdown → HTML Sync** | Manual drift, stale content | JSON extraction layer + automated pipeline |
| **45 MD files × 3 roles = 135+ pages?** | Maintenance explosion | Role-filtered single-page views with client-side rendering |
| **Discovery pipeline scope** | LENS integration complexity | Phase-based build: P1 static content, P2 discovery automation |
| **Glassmorphism theme fidelity** | CSS complexity without SPA tooling | Extract CSS variables, use vanilla JS DOM manipulation |
| **Agent awareness** | Agents don't know new structure | Update agent specs (cortex-gitpages-builder, cortex-doc) with bounds |

---

## Single Best Recommendation

### Architecture Pattern: **Data-Driven Static HTML5**

```
cortex-docs/
├── index.html                    # Role selector (3-persona panel)
├── views/
│   ├── business-leader.html      # Filtered view for Business Leaders
│   ├── product-owner.html        # Filtered view for POs
│   └── software-engineer.html    # Filtered view for Engineers
├── assets/
│   ├── data/
│   │   └── content.json          # JSON data store (extracted from *.md)
│   ├── css/
│   │   ├── glassmorphism.css     # Theme (extracted from gemini-index.html)
│   │   └── role-panels.css       # Role-specific styling
│   └── js/
│       ├── content-loader.js     # Client-side JSON → DOM rendering
│       └── role-navigator.js     # Role panel interaction logic
├── content/
│   └── src/                      # Source markdown (45 files, 8 categories)
└── pipeline/
    └── discover.py               # Existing discovery script (enhanced)
```

---

## Design Pillars Alignment

| Pillar | How Architecture Supports |
|--------|---------------------------|
| **Extensibility** | New roles = new HTML view + role filter in content.json. No code changes. |
| **Scalability** | Client-side rendering eliminates server dependency. GitHub Pages native. |
| **Accuracy** | JSON schema validation ensures content structure consistency. |
| **Team Collaboration** | Markdown source remains SSOT. Designers edit CSS, engineers edit JSON schema. |
| **Long-term Maintainability** | Discovery pipeline automates content sync. No manual HTML editing. |

---

## Implementation Phases

### Phase 1: Static Content Foundation (Non-Breaking)
**Scope:** Extract data, build role views, deploy static site  
**Deliverables:**
1. `assets/data/content.json` — JSON extraction script from 45 markdown files
2. `views/*.html` — 3 role-specific HTML views with glassmorphism theme
3. `assets/js/content-loader.js` — Vanilla JS client-side rendering
4. Updated `index.html` — Role selector panel (3 personas)

**Agent Awareness:**
- Update `.github/agents/core/cortex-gitpages-builder.md` with new structure
- Update `.github/prompts/cortex-doc.prompt.md` with asset locations

**Constraints:**
- ✅ HTML5 only, no TypeScript
- ✅ No SPA frameworks (React, Vue, Angular)
- ✅ GitHub Pages compatible
- ✅ Glassmorphism CSS from gemini-index.html reference

**Timeline:** 2-3 hours (collaborative via InteractionOrchestrator)

---

### Phase 2: Discovery Pipeline Automation (Future)
**Scope:** LENS-powered content discovery + automated deployment  
**Deliverables:**
1. Enhanced `pipeline/discover.py` — LENS git history integration
2. Content update logic — Detect changed features, update relevant markdown
3. Git Pages deployment — Automated push on content changes

**Dependencies:**
- Phase 1 complete (static structure established)
- LENS git history API stabilized
- GitHub Actions workflow for automated builds

**Timeline:** 4-6 hours (after Phase 1 validation)

---

## Content-to-View Mapping Strategy

### JSON Schema (content.json)

```json
{
  "categories": [
    {
      "id": "capabilities",
      "title": "Capabilities",
      "files": [
        {
          "slug": "ai-intelligence",
          "title": "AI Intelligence",
          "roles": ["business-leader", "product-owner"],
          "excerpt": "CORTEX Brain architecture...",
          "content_html": "<h2>AI Intelligence</h2>..."
        }
      ]
    }
  ],
  "roles": {
    "business-leader": {
      "label": "Business Leader",
      "icon": "👔",
      "focus": "ROI, Governance, Risk Mitigation",
      "categories": ["capabilities", "governance", "infrastructure"]
    }
  }
}
```

### Role Filtering Logic

**Business Leader View:**
- Show: capabilities/, governance/, infrastructure/ (high-level metrics)
- Hide: toolkit/, lens/ (implementation details)

**Product Owner View:**
- Show: capabilities/, orchestration/, mcp/ (feature flow, use cases)
- Hide: Low-level architecture

**Software Engineer View:**
- Show: ALL categories (full technical depth)
- Highlight: lens/, toolkit/, orchestration/

---

## Glassmorphism Theme Extraction

### CSS Variables (Extracted from gemini-index.html)

```css
:root {
  --bg-primary: #0a0e27;
  --glass-bg: rgba(26, 31, 58, 0.7);
  --glass-border: rgba(255, 255, 255, 0.1);
  --accent-primary: #00d4ff;    /* Cyan */
  --accent-secondary: #7b61ff;  /* Purple */
  --accent-emerald: #10b981;    /* Success */
}

.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(15px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
}
```

**No build tooling required.** Native CSS variables + backdrop-filter (Chrome 76+, supported in all modern browsers).

---

## Discovery Pipeline Integration

### Stage 1: LENS Git Discovery (Automated)
```python
# Enhanced discover.py
def analyze_git_timeline():
    """Use LENS git history analyzer to detect feature changes."""
    since_date = get_last_doc_update()
    commits = lens_git_history(since_date=since_date)
    
    return {
        "new_features": [...],
        "changed_orchestrators": [...],
        "updated_phases": [...]
    }
```

### Stage 2: Markdown Update (Semi-Automated)
```python
def update_markdown_files(discovery_results):
    """Update relevant *.md files based on git discoveries."""
    for feature in discovery_results["new_features"]:
        target_md = map_feature_to_markdown(feature)
        inject_content(target_md, feature)
```

### Stage 3: HTML Integration (Automated)
```bash
# Extract JSON from markdown
python pipeline/extract-json.py

# Client-side JS loads content.json → DOM rendering
# No server-side build needed
```

### Stage 4: Git Pages Push (Automated)
```bash
git add cortex-docs/assets/data/content.json
git commit -m "docs: Update content from LENS discovery"
git push origin CORTEX
# GitHub Pages auto-deploys from cortex-docs/
```

---

## Agent Awareness Updates

### cortex-gitpages-builder.md
**New workflow trigger:**
```yaml
trigger:
  path: cortex-docs/content/src/*.md
  action: extract_json → update_views → commit

output:
  - cortex-docs/assets/data/content.json
  - cortex-docs/views/*.html (if structure changes)
```

### cortex-doc.prompt.md
**Bounds and requirements:**
- **Content source:** `cortex-docs/content/src/` (45 markdown files)
- **Asset locations:** `cortex-docs/assets/{data,css,js}/`
- **View files:** `cortex-docs/views/*.html`
- **Theme:** Glassmorphism CSS variables in `assets/css/glassmorphism.css`
- **No generation:** Do NOT generate TypeScript, React, Vue files
- **Deployment:** GitHub Pages via `cortex-docs/` directory

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **JSON schema drift** | Medium | High | JSON schema validation in CI pipeline |
| **CSS complexity** | Low | Medium | Extract reusable CSS variables, avoid inline styles |
| **Discovery pipeline failure** | Medium | Low | Manual markdown updates as fallback |
| **Client-side rendering performance** | Low | Low | 45 files = ~500KB JSON, <1s load time |
| **Browser compatibility** | Low | Medium | Glassmorphism requires backdrop-filter (polyfill for Safari <14) |

---

## Non-Breaking Guarantees

✅ **Existing markdown files unchanged** — Still source of truth  
✅ **Existing pipeline/discover.py preserved** — Enhanced, not replaced  
✅ **Current cortex-docs/index.html** — Replaced only in Phase 1  
✅ **GitHub Pages deployment** — No infrastructure changes  
✅ **No new dependencies** — Pure HTML5+CSS3+JS (ES6)

---

## Next Step

**Recommended:** Proceed with Phase 1 collaboratively via InteractionOrchestrator:
1. Extract JSON schema from 8 content categories
2. Build role selector panel (index.html)
3. Create 3 role-specific views with glassmorphism theme
4. Update agent specifications (gitpages-builder, cortex-doc)

**Command to continue:**
```
/implement phase 1 cortex-docs static architecture
```

---

*Architecture validated against: Extensibility, Scalability, Accuracy, Team Collaboration, Long-term Maintainability*

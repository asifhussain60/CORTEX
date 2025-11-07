# MkDocs Documentation Rebuild Plan

**Created:** 2025-11-07  
**Purpose:** Complete rebuild of CORTEX documentation with zero duplication  
**Status:** 📋 DESIGN PHASE

---

## 🎯 Problem Statement

Current MkDocs system has critical issues:
1. **Massive duplication** - Same story exists in multiple locations (2025-11-04/ and 2025-11-06/)
2. **Fragmented content** - Technical docs scattered across architecture/, tiers/, Mind-Palace/
3. **Confusing navigation** - Multiple versions creating decision paralysis
4. **Broken structure** - MkDocs build issues, unclear content hierarchy

**Current file count:** 30+ markdown files in docs/  
**Duplication examples:**
- The Awakening story exists in both `Mind-Palace/2025-11-06/` and `story/`
- Architecture docs duplicated between `architecture/` and `Mind-Palace/`
- Multiple README files with overlapping content

---

## 🎨 New Design Philosophy

### Core Principles

1. **ONE VERSION ONLY** - Each piece of content exists in exactly ONE location
2. **Story + Technical Integration** - The Awakening narrative flows seamlessly with technical docs
3. **Clear Navigation** - Logical hierarchy that matches user journey
4. **Visual Integration** - Images embedded at proper locations in narrative
5. **Custom Theming** - Material theme customization for CORTEX branding

### Site Structure (Proposed)

```
docs/
├── index.md                          # Landing page - "What is CORTEX?"
├── story/
│   ├── the-awakening.md             # Complete 5-chapter narrative (SINGLE VERSION)
│   │                                  # Integrates ALL images at proper locations
│   └── image-gallery.md             # Optional: All visuals in one place
├── getting-started/
│   ├── quick-start.md               # 5-minute introduction
│   ├── installation.md              # Setup guide
│   └── first-task.md                # Your first CORTEX command
├── architecture/
│   ├── overview.md                  # High-level architecture
│   ├── dual-hemispheres.md          # LEFT/RIGHT brain design
│   ├── five-tier-memory.md          # Complete tier system
│   ├── protection-system.md         # 6-layer protection
│   └── oracle-crawler.md            # Discovery engine
├── guides/
│   ├── universal-entry-point.md     # Using #file:prompts/user/cortex.md
│   ├── brain-system.md              # Understanding memory tiers
│   ├── agent-workflows.md           # How agents coordinate
│   └── tdd-workflow.md              # RED → GREEN → REFACTOR
├── reference/
│   ├── tier0-governance.md          # Immutable rules
│   ├── tier1-conversation.md        # Short-term memory API
│   ├── tier2-knowledge.md           # Long-term patterns API
│   ├── tier3-context.md             # Development intelligence API
│   ├── agents.md                    # All 10+ agents documented
│   └── configuration.md             # cortex.config.json reference
├── development/
│   ├── contributing.md              # How to contribute
│   ├── testing.md                   # Running the 60 sacred tests
│   ├── architecture-decisions.md   # ADRs and rationale
│   └── changelog.md                 # Version history
└── images/
    └── cortex-awakening/            # All story images organized
        ├── chapter1/
        ├── chapter2/
        ├── chapter3/
        ├── chapter4/
        └── chapter5/
```

**Total files:** ~25 (reduced from 30+, with much less duplication)

---

## 📋 Execution Plan

### Phase 1: Git Commit (Safety First) ✅
**Duration:** 5 minutes

```powershell
# Commit ALL current documentation to git
git add docs/
git commit -m "chore(docs): Snapshot before MkDocs rebuild

- Preserving all current documentation (30 files)
- Multiple versions of story and technical docs
- Preparing for complete rebuild with zero duplication
- Recovery point for any needed content"

git push origin cortex-migration
```

**Deliverable:** Git commit with all current docs preserved

---

### Phase 2: Clean Slate ✅
**Duration:** 2 minutes

```powershell
# Complete deletion of docs/ (not archive - clean slate)
Remove-Item -Path "docs\*" -Recurse -Force

# Keep only .gitkeep or essential structure
New-Item -Path "docs" -ItemType Directory -Force
New-Item -Path "docs\images" -ItemType Directory -Force
```

**Deliverable:** Empty docs/ directory ready for rebuild

---

### Phase 3: New MkDocs Configuration ⏱️
**Duration:** 15 minutes

Create brand new `mkdocs.yml` with:

1. **Material Theme Customization**
   - CORTEX branding colors (indigo/purple for brain theme)
   - Custom fonts and icons
   - Enhanced navigation features
   - Custom CSS for story sections

2. **Plugin Configuration**
   - Search (with suggest/highlight)
   - Mermaid diagrams
   - Code syntax highlighting
   - Image optimization

3. **Markdown Extensions**
   - Admonitions for warnings/tips
   - Code blocks with line numbers
   - Tabbed content
   - Custom attributes (for story styling)

4. **Navigation Structure**
   - Match proposed structure above
   - Clear hierarchy
   - Breadcrumbs enabled
   - Section expand/collapse

**Deliverable:** New `mkdocs.yml` with clean configuration

---

### Phase 4: Content Creation ⏱️
**Duration:** 3-4 hours

#### 4.1 Core Story Document (Priority 1)
**File:** `docs/story/the-awakening.md`

**Structure:**
```markdown
# The Awakening of CORTEX: A Five-Act Journey

## Chapter 1: The Problem - Copilot's Amnesia
### 📖 The Story
[Narrative: Mad scientist, basement lab, forgetful intern]

![Basement Lab](../images/cortex-awakening/chapter1/basement-lab.png)  
*Asifinstein's laboratory where CORTEX was born*

### 🔧 The Technical Reality
[Technical explanation: Stateless AI, context loss, session boundaries]

### 🎨 Visual Design
[Image prompts used to generate the illustrations]

## Chapter 2: The Solution - Dual Hemispheres
[Continue pattern for all 5 chapters...]
```

**Key features:**
- ALL 5 chapters in ONE file
- Images embedded at narrative-appropriate locations
- Story flows into technical explanations naturally
- No duplication - this is THE canonical story

#### 4.2 Architecture Documentation (Priority 2)
**Files:** `docs/architecture/*.md`

- Extract technical content from story
- Create standalone architecture docs
- Cross-link to story for narrative context
- Include diagrams and code examples

#### 4.3 Getting Started (Priority 3)
**Files:** `docs/getting-started/*.md`

- Quick start (5-minute intro)
- Installation instructions
- First task walkthrough
- Links to deeper guides

#### 4.4 Reference Documentation (Priority 4)
**Files:** `docs/reference/*.md`

- Tier system documentation
- Agent reference
- Configuration options
- API documentation

#### 4.5 Guides (Priority 5)
**Files:** `docs/guides/*.md`

- How-to guides for common tasks
- Workflow explanations
- Best practices

**Deliverable:** Complete, single-version documentation set

---

### Phase 5: Custom Theming ⏱️
**Duration:** 30 minutes

**File:** `docs/stylesheets/custom.css`

```css
/* CORTEX Brand Colors */
:root {
  --cortex-primary: #6366F1;      /* Indigo */
  --cortex-accent: #8B5CF6;       /* Purple */
  --cortex-left-brain: #3B82F6;   /* Blue - Tactical */
  --cortex-right-brain: #A855F7;  /* Purple - Strategic */
}

/* Story Section Styling */
.story-section {
  background: linear-gradient(135deg, var(--cortex-primary), var(--cortex-accent));
  padding: 2rem;
  border-radius: 8px;
  color: white;
  margin: 2rem 0;
}

/* Technical Section Styling */
.technical-section {
  background: #F3F4F6;
  padding: 2rem;
  border-left: 4px solid var(--cortex-primary);
  margin: 2rem 0;
}

/* Image captions */
.story-image {
  text-align: center;
  margin: 2rem 0;
}

.story-image img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.story-image figcaption {
  font-style: italic;
  color: #6B7280;
  margin-top: 0.5rem;
}

/* Hemisphere badges */
.left-brain {
  background: var(--cortex-left-brain);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
}

.right-brain {
  background: var(--cortex-right-brain);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: bold;
}
```

**Deliverable:** Custom CSS for CORTEX branding

---

### Phase 6: Testing & Validation ⏱️
**Duration:** 30 minutes

```powershell
# Build site locally
mkdocs build --clean

# Check for broken links
# Check for missing images
# Validate navigation
# Test search functionality

# Serve locally for review
mkdocs serve

# Review at http://localhost:8000
```

**Validation Checklist:**
- ✅ All images display correctly
- ✅ No broken internal links
- ✅ Navigation hierarchy is clear
- ✅ Search finds relevant content
- ✅ Mobile responsive
- ✅ Story flows naturally with technical content
- ✅ No duplication exists

**Deliverable:** Working MkDocs site with validation complete

---

### Phase 7: Deployment ⏱️
**Duration:** 10 minutes

```powershell
# Final git commit
git add docs/ mkdocs.yml
git commit -m "feat(docs): Complete MkDocs rebuild with zero duplication

- Single version of all content
- Integrated story + technical documentation
- The Awakening (5 chapters) in one location
- Custom CORTEX theming
- Clear navigation hierarchy
- 25 files (down from 30+)
- Images properly embedded
- All duplication eliminated"

git push origin cortex-migration

# Deploy to GitHub Pages (if configured)
mkdocs gh-deploy
```

**Deliverable:** Production-ready documentation site

---

## 🎨 Custom Template Options

Yes, MkDocs Material supports custom templates! Options:

### Option 1: Custom Home Page Template
**Use case:** Hero section, feature highlights, call-to-action buttons

**Implementation:**
```yaml
# mkdocs.yml
theme:
  name: material
  custom_dir: overrides
```

**File:** `overrides/home.html`
```html
{% extends "main.html" %}
{% block content %}
<div class="cortex-hero">
  <h1>CORTEX: The Brain for AI Assistants</h1>
  <p>Transforming GitHub Copilot from forgetful intern to expert partner</p>
  <a href="getting-started/quick-start/" class="cta-button">Get Started</a>
  <a href="story/the-awakening/" class="cta-button secondary">Read The Story</a>
</div>
{% endblock %}
```

### Option 2: Custom Story Layout
**Use case:** Special formatting for narrative sections

**File:** `overrides/story.html`
```html
{% extends "main.html" %}
{% block content %}
<article class="cortex-story">
  {{ page.content }}
</article>
{% endblock %}
```

**In markdown:**
```yaml
---
template: story.html
---
```

### Option 3: Full Page Templates
**Use case:** Completely custom pages (landing, about, etc.)

Material theme supports:
- Custom base templates
- Template overrides
- Partial overrides
- Block-level customization

**Recommendation:** Start with custom CSS, add templates if needed for landing page.

---

## 📊 Success Metrics

How we'll know the rebuild is successful:

1. **Zero Duplication**
   - Each content piece exists in exactly ONE location
   - No conflicting versions
   - Single source of truth

2. **Clear Navigation**
   - Users can find content in < 30 seconds
   - Logical hierarchy
   - Breadcrumbs work correctly

3. **Story Integration**
   - Narrative flows naturally
   - Images embedded properly
   - Technical content complements story

4. **Build Performance**
   - `mkdocs build` completes with no warnings
   - `mkdocs serve` runs without errors
   - Deploy succeeds on first try

5. **User Experience**
   - Story is engaging and fun
   - Technical docs are precise and clear
   - Getting started guide works for newcomers

---

## 🚀 Estimated Timeline

| Phase | Duration | Description |
|-------|----------|-------------|
| 1. Git Commit | 5 min | Safety: Preserve current docs |
| 2. Clean Slate | 2 min | Delete old structure |
| 3. Configuration | 15 min | New mkdocs.yml |
| 4. Content Creation | 3-4 hours | Write ALL documentation |
| 5. Custom Theming | 30 min | CORTEX branding CSS |
| 6. Testing | 30 min | Validation and review |
| 7. Deployment | 10 min | Git commit + deploy |
| **TOTAL** | **~5-6 hours** | Complete rebuild |

**Recommended approach:** Do phases 1-3 now, then tackle content creation in focused 1-hour blocks.

---

## 🎯 Next Steps

**Immediate actions:**

1. ✅ **Review this plan** - Make sure structure meets your vision
2. ✅ **Approve approach** - Confirm deletion + rebuild is acceptable
3. ⏱️ **Execute Phase 1** - Commit current docs to git
4. ⏱️ **Execute Phase 2** - Clean slate
5. ⏱️ **Execute Phase 3** - New mkdocs.yml
6. ⏱️ **Execute Phase 4** - Content creation (longest phase)

**Questions to answer:**
- Do you want the custom home page template? (Option 1 above)
- Should we keep GitHub Pages deployment?
- Any specific branding colors/fonts?
- Should we include a "Contributing" guide?

---

## 📝 Notes

**Content Sources:**
- The Awakening story: Use Nov 6 version as canonical (most complete)
- Technical docs: Extract from prompts/user/cortex.md + architecture docs
- Images: Already in docs/images/cortex-awakening/

**Migration Strategy:**
- Don't archive - complete deletion after git commit
- Fresh start eliminates technical debt
- Faster than trying to merge/deduplicate existing content

**Risk Mitigation:**
- Git commit preserves everything (can recover if needed)
- Build incrementally (test after each phase)
- Keep backup of current site running until new one validated

---

**Ready to begin? Let's start with Phase 1 (Git Commit) to preserve current state.**

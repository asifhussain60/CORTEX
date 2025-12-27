# Documentation Orchestrator Enhancement Plan

**Author:** Asif Hussain | **Date:** December 27, 2025  
**Status:** 🎯 READY FOR IMPLEMENTATION

---

## 🎯 Executive Summary

**Objective:** Enhance `docgen.prompt.md` to generate comprehensive documentation for:
1. **24 empty `docs/technical/` subdirectories** (api, workflows, setup-guides, integration, deployment, troubleshooting, performance, security, testing, design-decisions, data-flow, examples, glossary, etc.)
2. **Global search capability** using Lunr.js (3.5KB gzipped, client-side, GitHub Pages compatible)
3. **Redesigned navigation** following UI/UX best practices from `ui-ux-best-practices.yaml`
4. **Integration** of existing `docs/technical/index.html` hub into main documentation

---

## 📊 Current State Analysis

### Empty Directories (24 of 29 folders)
```
docs/technical/
├── api/                        ← 0 files (needs API docs for 6 orchestrators + 2 agents + 4 brain tiers)
├── architecture/               ← 0 files (needs component diagrams)
├── workflows/                  ← 0 files (needs flowcharts + sequence diagrams)
├── setup-guides/               ← 0 files (needs quick-start, advanced setup)
├── integration/                ← 0 files (needs Copilot integration guide)
├── deployment/                 ← 0 files (needs local/team deployment guides)
├── troubleshooting/            ← 0 files (needs common issues, debug guide)
├── performance/                ← 0 files (needs optimization guide, benchmarks)
├── security/                   ← 0 files (needs SKULL security, best practices)
├── testing/                    ← 0 files (needs TDD guide, test pyramid, coverage)
├── design-decisions/           ← 0 files (needs architecture decisions, trade-offs)
├── data-flow/                  ← 0 files (needs DFD diagrams for brain/orchestrators)
├── examples/                   ← 0 files (needs code samples for planning, TDD, sanitization)
├── glossary/                   ← 0 files (needs terms glossary)
└── ... (11 more empty folders)
```

### Existing Assets (Preserve These)
- ✅ `docs/technical/index.html` (technical hub with glassmorphism theme)
- ✅ `docs/technical/assets/styles/glassmorphism.css` (design system)
- ✅ `docs/technical/assets/styles/diagrams.css` (visualization styling)
- ✅ `docs/technical/assets/scripts/navigation.js` (breadcrumb generator)

---

## 🚀 Solution Architecture

### 1. Documentation Structure Integration

**Add to `docgen.prompt.md`:**
```markdown
├── technical/                          # 🆕 INTEGRATE docs/technical/ (24 empty folders)
│   ├── index.html                      # Technical hub (ALREADY EXISTS - PRESERVE)
│   ├── api/                            # API documentation
│   │   ├── index.html                  # API overview
│   │   ├── orchestrators/              # 6 USER-facing orchestrator APIs
│   │   │   ├── planning-system-api.html
│   │   │   ├── tdd-mastery-api.html
│   │   │   ├── execution-api.html
│   │   │   ├── ado-operations-api.html
│   │   │   ├── sanitization-api.html
│   │   │   └── upgrade-api.html
│   │   ├── agents/                     # 2 Agent APIs
│   │   │   ├── strategic-planning-agent.html
│   │   │   └── code-execution-agent.html
│   │   └── brain-tiers/                # 4 Brain Tier APIs
│   │       ├── tier0-governance.html
│   │       ├── tier1-working-memory.html
│   │       ├── tier2-knowledge-graph.html
│   │       └── tier3-dev-context.html
│   │
│   ├── workflows/                      # Workflow diagrams
│   │   ├── index.html
│   │   ├── flowcharts/                 # Mermaid flowcharts
│   │   │   ├── planning-workflow.html
│   │   │   ├── tdd-cycle.html
│   │   │   ├── sanitization-flow.html
│   │   │   └── maintenance-workflow.html
│   │   └── sequence-diagrams/          # Mermaid sequence diagrams
│   │       ├── orchestrator-interaction.html
│   │       ├── brain-query-sequence.html
│   │       └── agent-collaboration.html
│   │
│   ├── setup-guides/                   # Setup & installation
│   │   ├── index.html
│   │   ├── quick-start.html
│   │   ├── advanced-setup.html
│   │   └── environment-config.html
│   │
│   ├── integration/                    # Integration guides
│   │   ├── index.html
│   │   ├── copilot-integration.html
│   │   ├── vscode-setup.html
│   │   └── diagrams/
│   │       └── integration-architecture.html
│   │
│   ├── deployment/                     # Deployment guides
│   │   ├── index.html
│   │   ├── local-deployment.html
│   │   ├── team-deployment.html
│   │   └── diagrams/
│   │       └── deployment-flow.html
│   │
│   ├── troubleshooting/                # Troubleshooting
│   │   ├── index.html
│   │   ├── common-issues.html
│   │   └── debug-guide.html
│   │
│   ├── performance/                    # Performance docs
│   │   ├── index.html
│   │   ├── optimization-guide.html
│   │   └── benchmarks.html
│   │
│   ├── security/                       # Security docs
│   │   ├── index.html
│   │   ├── skull-security.html
│   │   └── best-practices.html
│   │
│   ├── testing/                        # Testing docs
│   │   ├── index.html
│   │   ├── tdd-guide.html
│   │   ├── test-pyramid.html
│   │   └── coverage-reports.html
│   │
│   ├── design-decisions/               # Design rationale
│   │   ├── index.html
│   │   ├── architecture-decisions.html
│   │   └── trade-offs.html
│   │
│   ├── data-flow/                      # Data flow diagrams
│   │   ├── index.html
│   │   └── dfd-diagrams/
│   │       ├── brain-data-flow.html
│   │       └── orchestrator-data-flow.html
│   │
│   ├── examples/                       # Code examples
│   │   ├── index.html
│   │   └── code-samples/
│   │       ├── planning-example.html
│   │       ├── tdd-example.html
│   │       └── sanitization-example.html
│   │
│   └── glossary/                       # Glossary
│       ├── index.html
│       └── terms.html
```

### 2. Global Search Implementation (Lunr.js)

**Why Lunr.js:**
- ✅ 3.5KB gzipped (lightweight)
- ✅ Client-side (no server required)
- ✅ Full-text search with stemming
- ✅ Relevance scoring
- ✅ Works offline (GitHub Pages compatible)
- ✅ No API keys, no rate limits

**Assets to Add:**
```javascript
// docs/assets/js/lunr.min.js (download from CDN)
// docs/assets/js/search.js (custom search implementation)
// docs/search-index.json (auto-generated during docgen)
```

**Search Index Generation (Phase 3: Content Generation):**
```javascript
// Pseudo-code for docgen orchestrator
const searchDocs = []

// Crawl all generated HTML pages
for (const page of generatedPages) {
    searchDocs.push({
        id: page.url,
        title: extractTitle(page.html),
        category: page.category, // orchestrators, architecture, features, technical
        content: extractTextContent(page.html),
        tags: page.tags || []
    })
}

// Build Lunr index
const idx = lunr(function () {
    this.ref('id')
    this.field('title', { boost: 10 })
    this.field('category', { boost: 5 })
    this.field('tags', { boost: 5 })
    this.field('content')
    
    searchDocs.forEach(doc => this.add(doc))
})

// Save to docs/search-index.json
fs.writeFileSync('docs/search-index.json', JSON.stringify({
    index: idx.toJSON(),
    docs: searchDocs
}))
```

**Search UI Components:**
```html
<!-- Add to navigation bar on ALL pages -->
<div class="search-container">
    <i class="fas fa-search search-icon"></i>
    <input type="text" 
           id="globalSearch" 
           class="search-input" 
           placeholder="Search documentation... (Ctrl+K)" 
           autocomplete="off"
           aria-label="Search CORTEX documentation">
</div>

<!-- Search results dropdown (shown when searching) -->
<div id="searchResults" class="search-results glass-card" hidden>
    <div class="search-results-header">
        <span id="searchResultsCount">0 results</span>
        <button id="closeSearch" aria-label="Close search">✕</button>
    </div>
    <ul id="searchResultsList" class="search-results-list">
        <!-- Results populated by search.js -->
    </ul>
</div>
```

**Keyboard Shortcuts:**
- **Ctrl+K / Cmd+K:** Focus search bar
- **Escape:** Close search results
- **Arrow Up/Down:** Navigate results
- **Enter:** Open selected result

### 3. Redesigned Navigation (UI/UX Best Practices)

**Source:** `cortex-brain/knowledge/ui-ux/ui-ux-best-practices.yaml`

**Updated Navigation Pattern:**
```html
<nav class="main-nav">
    <div class="nav-content">
        <!-- Logo -->
        <a href="/" class="logo-link">
            <img src="/assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="logo">
            <span class="logo-text">CORTEX 4.0</span>
        </a>
        
        <!-- Global Search Bar (NEW) -->
        <div class="search-container">
            <input type="text" id="globalSearch" placeholder="Search docs... (Ctrl+K)">
            <i class="fas fa-search"></i>
        </div>
        
        <!-- Primary Navigation -->
        <div class="nav-links">
            <a href="/orchestrators/">Orchestrators</a>
            <a href="/architecture/">Architecture</a>
            <a href="/features/">Features</a>
            <a href="/technical/">Technical</a> <!-- NEW: Link to docs/technical/index.html -->
            <a href="/governance/">Governance</a>
        </div>
        
        <!-- GitHub Link -->
        <a href="https://github.com/asifhussain60/CORTEX" class="github-link">
            <i class="fab fa-github"></i> GitHub
        </a>
    </div>
</nav>
```

### 4. Redesigned Home Dashboard (docs/index.html)

**Add Technical Section to Feature Grid:**
```html
<!-- After existing feature cards, add: -->
<div class="glass-card feature-card">
    <div class="icon">📚</div>
    <h3>Technical Documentation</h3>
    <p>
        Comprehensive developer guide with API references, workflows, 
        setup guides, and integration documentation for CORTEX framework.
    </p>
    <a href="technical/index.html" class="learn-more">
        Browse Technical Docs →
    </a>
</div>
```

**Update Hero CTA Buttons (add Technical button):**
```html
<div class="cta-buttons-large">
    <!-- Existing story button (PRESERVE EXACTLY) -->
    <a href="story/index.html" class="btn-hero btn-hero-story btn-hero-full-width">
        <span class="btn-hero-icon"><img src="assets/images/Awakening.png" alt="Awakening" style="width: 150px; height: 150px; border-radius: 15px;" /></span>
        <span class="btn-hero-text">The Awakening Of CORTEX</span>
        <span class="btn-hero-caption">Read the How It All Happened</span>
    </a>
    
    <!-- Existing buttons... -->
    <a href="governance/skull-rulebook.html" class="btn-hero btn-hero-primary">
        <span class="btn-hero-icon">🛡️</span>
        <span class="btn-hero-text">CORTEX Bible</span>
    </a>
    <a href="#features" class="btn-hero btn-hero-secondary">
        <span class="btn-hero-icon">🎯</span>
        <span class="btn-hero-text">Explore Features</span>
    </a>
    
    <!-- NEW: Technical Documentation button -->
    <a href="technical/index.html" class="btn-hero btn-hero-technical">
        <span class="btn-hero-icon">📚</span>
        <span class="btn-hero-text">Technical Docs</span>
    </a>
    
    <a href="future/index.html" class="btn-hero btn-hero-vision">
        <span class="btn-hero-icon">🔮</span>
        <span class="btn-hero-text">4.0 Vision</span>
    </a>
</div>
```

---

## 📋 Implementation Checklist

### Phase 1: Update docgen.prompt.md
- [ ] Add `docs/technical/` structure to "Documentation Structure" section
- [ ] Add 24 empty folder integration (api, workflows, setup-guides, etc.)
- [ ] Add global search section with Lunr.js implementation details
- [ ] Add search index generation logic to Phase 3 (Content Generation)
- [ ] Add search UI components to navigation pattern
- [ ] Add keyboard shortcuts documentation

### Phase 2: Update docs/index.html
- [ ] Add global search bar to navigation
- [ ] Add "Technical Documentation" card to feature grid
- [ ] Add "Technical Docs" button to hero CTA grid
- [ ] Verify story button HTML preservation (CRITICAL)
- [ ] Test all navigation links

### Phase 3: Generate Search Assets
- [ ] Download Lunr.js library (`docs/assets/js/lunr.min.js`)
- [ ] Create `docs/assets/js/search.js` (search implementation)
- [ ] Create CSS styles for search UI (`.search-container`, `.search-results`)
- [ ] Add keyboard shortcut handlers (Ctrl+K, Escape, Arrow keys)

### Phase 4: Content Generation for docs/technical/
**24 folders x 2-5 pages each = ~80 new pages**

**High Priority (Week 1):**
- [ ] `technical/api/` - 12 API pages (6 orchestrators + 2 agents + 4 brain tiers)
- [ ] `technical/setup-guides/` - Quick-start guide
- [ ] `technical/integration/` - Copilot integration guide
- [ ] `technical/workflows/flowcharts/` - 4 workflow diagrams

**Medium Priority (Week 2):**
- [ ] `technical/deployment/` - Local/team deployment guides
- [ ] `technical/troubleshooting/` - Common issues, debug guide
- [ ] `technical/testing/` - TDD guide, test pyramid, coverage
- [ ] `technical/workflows/sequence-diagrams/` - 3 sequence diagrams

**Low Priority (Week 3):**
- [ ] `technical/performance/` - Optimization guide, benchmarks
- [ ] `technical/security/` - SKULL security, best practices
- [ ] `technical/design-decisions/` - Architecture decisions
- [ ] `technical/data-flow/dfd-diagrams/` - Brain/orchestrator DFDs
- [ ] `technical/examples/code-samples/` - Code examples
- [ ] `technical/glossary/` - Terms glossary

### Phase 5: Validation
- [ ] All 24 docs/technical/ folders have index.html
- [ ] Global search returns results from all pages
- [ ] Ctrl+K focuses search bar
- [ ] Search results dropdown styled with glassmorphism
- [ ] Navigation links work (home → technical → api → orchestrators)
- [ ] Story button preserved exactly (CRITICAL)
- [ ] Mobile responsive (search bar collapses to icon)
- [ ] Accessibility: ARIA labels, keyboard navigation
- [ ] Performance: Search index <500KB, page load <3s

---

## 🎯 Success Metrics

1. **Content Coverage:** 100% of 24 empty folders populated (80+ new pages)
2. **Search Functionality:** <200ms search response time, 95%+ relevance
3. **Navigation UX:** 3-click access to any page from home
4. **Mobile Responsive:** 100% pages work on 320px-4K screens
5. **Accessibility:** Lighthouse score >90 for all pages
6. **Performance:** Page load <3s on 3G, search index <500KB
7. **Story Preservation:** Story button HTML matches exactly (CRITICAL)

---

## 🔄 Next Actions

1. **Update docgen.prompt.md** with all enhancements above
2. **Update docs/index.html** with search bar + technical button
3. **Create search.js** implementation file
4. **Execute docgen** command to regenerate all documentation
5. **Validate** all 24 folders populated + search working

---

**Estimated Effort:** 
- Prompt updates: 2 hours
- Search implementation: 4 hours
- Content generation: 20 hours (automated)
- Validation: 2 hours
- **Total:** 28 hours (3-4 days)

# CORTEX Documentation App - ChatGPT Build Instructions

**Version:** 1.0  
**Date:** 2026-02-10  
**Purpose:** Augment GPT's original design with CORTEX-specific requirements, known limitations, and design preferences

---

## 📋 Original GPT Proposal Summary

GPT proposed building a **single-file:// runnable HTML5 documentation microsite** with:
- Dark-blue glassmorphism aesthetic with subtle animations
- Role-guided navigation (Business Leader / PO / Manager / Engineer / Quality)
- D3-driven visualizations
- 9-tab structure with progressive disclosure
- No fetch() - all data embedded as JS objects (`window.CORTEX_DOC`)
- "Role Tour" + "Explorer Mode" navigation

---

## 🚨 CRITICAL LIMITATIONS FROM DEVELOPMENT HISTORY

### 1. file:// Protocol Restrictions (P0 - MUST ADDRESS)

**Source:** GPR-001, 87708f09f, c4d036a8c, 6786fe097

The `file://` protocol has SEVERE limitations that MUST be addressed:

#### ❌ CORS Blocking
```javascript
// FORBIDDEN - Will fail silently in file:// mode
fetch('./data/repo.json')  // ❌ CORS error
fetch('./orchestrators.json')  // ❌ Blocked

// REQUIRED - Embed all data as JS objects
window.CORTEX_DOC = {
    orchestrators: [...],
    capabilities: [...],
    metrics: {...}
};
```

#### ❌ JSON Import Blocking
```javascript
// FORBIDDEN in file:// mode
import data from './data.json' assert { type: 'json' };  // ❌ Fails

// REQUIRED - Use embedded script tags
<script src="./assets/data/cortex-doc-data.js"></script>
// Where cortex-doc-data.js contains: window.CORTEX_DOC = {...}
```

#### Implementation Pattern (MANDATORY)
```javascript
/**
 * DeploymentMode Pattern (From company/dashboards/spa/js/utils/DeploymentMode.js)
 * MUST be implemented to handle offline file:// usage
 */
class DeploymentMode {
    constructor() {
        this.mode = this._detectMode();
        this.config = this._getConfigForMode();
    }

    _detectMode() {
        if (window.location.protocol === 'file:') {
            return 'FILE_MODE';  // Offline, no fetch allowed
        } else if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
            return 'HTTP_MODE';  // Server mode, fetch allowed
        }
        return 'UNKNOWN';
    }

    _getConfigForMode() {
        if (this.mode === 'FILE_MODE') {
            return {
                allowFetch: false,
                requireEmbeddedData: true,
                description: 'Offline (file://)',
                warning: 'Running in offline mode. Use HTTP server for full functionality.'
            };
        }
        return {
            allowFetch: true,
            requireEmbeddedData: false,
            description: 'HTTP Server'
        };
    }

    canFetch() { return this.config.allowFetch; }
}

// Usage in data loading
const mode = new DeploymentMode();
if (!mode.canFetch()) {
    // Use embedded data ONLY
    const data = window.CORTEX_DOC;
} else {
    // Can attempt fetch with fallback
    const data = await fetch('./data.json').catch(() => window.CORTEX_DOC);
}
```

### 2. Mermaid Diagram Rendering Issues (P1)

**Source:** Phase-17 documentation, ui-ux-best-practices.yaml

Mermaid diagrams have known rendering issues in offline/file:// mode:

#### ❌ Known Problems
- Mermaid.js requires async initialization that can fail in file:// mode
- Complex diagrams can timeout or not render
- Font loading issues in offline mode

#### ✅ REQUIRED: Use Inline SVG Instead
```html
<!-- FORBIDDEN: Mermaid code blocks -->
<div class="mermaid">
graph LR
    A --> B --> C
</div>

<!-- REQUIRED: Pre-rendered SVG diagrams -->
<svg viewBox="0 0 1100 650" class="architecture-svg">
    <defs>
        <filter id="glow-purple">...</filter>
        <marker id="arrowhead-cyan">...</marker>
    </defs>
    <!-- Hand-crafted or pre-rendered nodes and connections -->
    <g class="layer-group">
        <rect x="30" y="20" width="200" height="90" rx="16" 
              fill="rgba(26, 31, 58, 0.6)" 
              stroke="rgba(255,255,255,0.15)"/>
        <text x="130" y="45" text-anchor="middle" fill="#00d4ff">MCP LAYER</text>
    </g>
</svg>
```

### 3. D3.js Considerations (P1)

**Source:** b3f615356, e0e908154

D3.js works well but requires careful implementation:

#### ✅ REQUIRED: Bundle D3 Locally
```html
<!-- Include D3 locally, not via CDN -->
<script src="./assets/js/vendor/d3.v7.min.js"></script>

<!-- D3 template literal syntax must be exact -->
<script>
// CORRECT D3 syntax
const nodes = d3.select('#visualization')
    .selectAll('circle')
    .data(data)
    .join('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y);
</script>
```

#### ✅ REQUIRED: Fallback for D3 Failures
```javascript
// Always provide fallback content for D3 visualizations
function initVisualization(containerId, data) {
    const container = document.getElementById(containerId);
    try {
        // D3 visualization code
        renderD3Chart(container, data);
    } catch (error) {
        console.error('D3 visualization failed:', error);
        // Show static fallback
        container.innerHTML = `
            <div class="viz-fallback">
                <p>Interactive visualization unavailable in offline mode.</p>
                <img src="./assets/images/fallback-diagram.png" alt="Architecture diagram">
            </div>
        `;
    }
}
```

### 4. Font & Icon Loading (P1)

**Source:** main.css header, index.html

#### ❌ Known Issue: CDN fonts fail in file:// mode

```css
/* PROBLEMATIC: External font loading */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* REQUIRED: Self-hosted or system fonts */
:root {
    --font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
}
```

#### ✅ Font Awesome Local Bundle
```html
<!-- Include FA subset locally -->
<link href="./assets/css/fontawesome-subset.css" rel="stylesheet"/>

<!-- Or use emoji/unicode fallbacks -->
<span class="icon">🧠</span> <!-- Instead of <i class="fas fa-brain"></i> -->
```

---

## 🎨 DESIGN SYSTEM: CORTEX GLASSMORPHISM v4.0

### Color Palette (MANDATORY)

```css
:root {
    /* Background - Dark Mode */
    --bg-primary: #0a0e27;           /* Deep navy */
    --bg-secondary: #1a1f3a;         /* Lighter navy */
    --glass-bg: rgba(26, 31, 58, 0.7);
    --glass-border: rgba(255, 255, 255, 0.1);
    
    /* Accent Colors */
    --accent-primary: #00d4ff;       /* Cyan - primary actions */
    --accent-secondary: #7b61ff;     /* Purple - secondary elements */
    
    /* Category Colors (from Orchestrator view) */
    --orch-core: #7b61ff;            /* Purple - Core orchestrators */
    --orch-domain: #00d4ff;          /* Cyan - Domain orchestrators */
    --orch-support: #10b981;         /* Emerald - Support orchestrators */
    --orch-tdd: #ef4444;             /* Red - TDD/Governance */
    --orch-planning: #f59e0b;        /* Amber - Planning */
    
    /* Text Colors */
    --text-primary: #ffffff;
    --text-secondary: #a0a6c0;
    --text-muted: #6b7280;
    
    /* Status Colors */
    --success: #00ff88;
    --warning: #ffa500;
    --danger: #ff4444;
    --info: #3b82f6;
}
```

### Glass Card Patterns (MANDATORY)

```css
/* Base Glass Card - Display (non-interactive) */
.glass-card-display {
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    padding: 1.5rem;
}

/* Glass Card - Clickable/Interactive */
.glass-card-clickable {
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    animation: borderGlow 4s ease-in-out infinite;
    cursor: pointer;
}

/* Shimmer Effect on Glass Cards */
.glass-card-clickable::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0.03) 45%,
        rgba(255, 255, 255, 0.06) 50%,
        rgba(255, 255, 255, 0.03) 55%,
        transparent 100%
    );
    background-size: 200% 100%;
    animation: glassShimmer 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 1;
}

/* Hover Enhancement */
.glass-card-clickable:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3),
                0 0 30px rgba(123, 97, 255, 0.15),
                inset 0 0 0 1px rgba(255, 255, 255, 0.15);
}

/* Category-specific hover glows */
.orch-category-core:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3),
                0 0 40px rgba(123, 97, 255, 0.25);
}

.orch-category-domain:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3),
                0 0 40px rgba(0, 212, 255, 0.25);
}

.orch-category-support:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3),
                0 0 40px rgba(16, 185, 129, 0.25);
}

/* Panel color variants */
.glass-panel-purple {
    border-left: 4px solid var(--orch-core);
    background: linear-gradient(135deg, 
        rgba(123, 97, 255, 0.15), 
        rgba(26, 31, 58, 0.7));
}

.glass-panel-cyan {
    border-left: 4px solid var(--orch-domain);
    background: linear-gradient(135deg, 
        rgba(0, 212, 255, 0.15), 
        rgba(26, 31, 58, 0.7));
}

.glass-panel-emerald {
    border-left: 4px solid var(--orch-support);
    background: linear-gradient(135deg, 
        rgba(16, 185, 129, 0.15), 
        rgba(26, 31, 58, 0.7));
}
```

### Animation Keyframes (MANDATORY)

```css
@keyframes glassShimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes borderGlow {
    0%, 100% {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.05);
    }
    50% {
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25),
                    inset 0 0 0 1px rgba(255, 255, 255, 0.1);
    }
}

@keyframes subtleFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

@keyframes electric-aura {
    0%, 100% { 
        filter: drop-shadow(0 0 40px rgba(0, 212, 255, 0.6))
                drop-shadow(0 0 80px rgba(123, 97, 255, 0.4));
    }
    50% { 
        filter: drop-shadow(0 0 60px rgba(0, 212, 255, 0.9))
                drop-shadow(0 0 120px rgba(123, 97, 255, 0.6));
    }
}

/* Reduced motion accessibility */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

### Tab System (MANDATORY Pattern)

```css
.cortex-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
}

.cortex-tab {
    appearance: none;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(26,31,58,0.35);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    color: #e6e9f0;
    padding: 0.5rem 0.75rem;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.2s ease, border-color 0.2s ease;
}

.cortex-tab:hover {
    background: rgba(26,31,58,0.5);
    border-color: rgba(0,212,255,0.35);
}

.cortex-tab.active {
    background: rgba(26,31,58,0.6);
    border-color: rgba(123,97,255,0.6);
    color: #ffffff;
    box-shadow: 0 0 18px rgba(0,212,255,0.15);
}

.cortex-tab-panel {
    display: none;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(19,23,46,0.25);
    backdrop-filter: blur(8px);
    padding: 0.75rem;
    border-radius: 12px;
}

.cortex-tab-panel.active {
    display: block;
}
```

---

## 📐 3-LEVEL SITE ARCHITECTURE

### Level 0: Entry Page (docs/index.html reference)

**Purpose:** Landing page with role tiles and key features

**Structure:**
```
┌─────────────────────────────────────────┐
│  CORTEX Logo (animated electric aura)   │
│  "Cognitive Orchestration Real-Time     │
│   Execution eXpert"                     │
├─────────────────────────────────────────┤
│  Two-Panel Layout:                      │
│  ┌─────────────┬─────────────┐          │
│  │ What is     │ The CORTEX  │          │
│  │ CORTEX?     │ Vision      │          │
│  └─────────────┴─────────────┘          │
├─────────────────────────────────────────┤
│  Persona Tiles (3 across):              │
│  ┌─────────┬─────────┬─────────┐        │
│  │Business │ Product │Software │        │
│  │Leader   │ Owner   │Engineer │        │
│  │ 👔      │  📋     │  💻     │        │
│  └─────────┴─────────┴─────────┘        │
├─────────────────────────────────────────┤
│  Key Features Grid (btn-hero cards)     │
│  - Get Started                          │
│  - Architecture                         │
│  - MCP Tools                            │
│  - CORTEX LENS                          │
├─────────────────────────────────────────┤
│  Tabbed Sections:                       │
│  - Governance & Audit                   │
│  - Discovery & Toolkit                  │
└─────────────────────────────────────────┘
```

### Level 1: Category Pages (e.g., orchestrators/index.html)

**Purpose:** Category overview with all items in that category

**Structure:**
```
┌─────────────────────────────────────────┐
│  Hero Section with Robot/Logo           │
│  Section Title + Description            │
├─────────────────────────────────────────┤
│  Executive Summary Glass Panel          │
│  - Key principles (bulleted)            │
│  - Highlight box with icon              │
├─────────────────────────────────────────┤
│  SVG Architecture Diagram               │
│  (Pre-rendered, no Mermaid)             │
├─────────────────────────────────────────┤
│  D3 Visualization Container             │
│  + Interactive Legend                   │
├─────────────────────────────────────────┤
│  Category Sections:                     │
│  ┌─────────────────────────────────┐    │
│  │ Core Orchestrators (6) 💜       │    │
│  │ ┌────┬────┬────┐                │    │
│  │ │Card│Card│Card│ (grid layout)  │    │
│  │ └────┴────┴────┘                │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ Domain Orchestrators (6) 🩵     │    │
│  │ (same grid pattern)             │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │ Support Orchestrators (11) 💚   │    │
│  │ (same grid pattern)             │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Level 2: Detail Pages (e.g., orchestrators/master-orchestrator.html)

**Purpose:** Deep-dive into single item with full specification

**Structure:**
```
┌─────────────────────────────────────────┐
│  Breadcrumb: Home > Orchestrators > X   │
├─────────────────────────────────────────┤
│  Item Title + Category Badge            │
│  Status: Implemented | Partial | Planned│
├─────────────────────────────────────────┤
│  Tabbed Content:                        │
│  [Overview] [API] [Examples] [Wiring]   │
├─────────────────────────────────────────┤
│  Current Tab Content:                   │
│  - Responsibilities list                │
│  - Input/Output specification           │
│  - Code examples (syntax highlighted)   │
│  - Related orchestrators                │
├─────────────────────────────────────────┤
│  Evidence Section:                      │
│  - Test count                           │
│  - Coverage %                           │
│  - Last verified date                   │
│  - "Truth Badge" (Implemented/Partial)  │
└─────────────────────────────────────────┘
```

---

## 📊 DATA STRUCTURE (window.CORTEX_DOC)

```javascript
// assets/data/cortex-doc-data.js
window.CORTEX_DOC = {
    version: "1.0.0",
    lastUpdated: "2026-02-10",
    
    // Orchestrators Registry
    orchestrators: {
        core: [
            {
                id: "master-orchestrator",
                name: "MasterOrchestrator",
                icon: "🎼",
                color: "#7b61ff",
                description: "Central Coordination Hub",
                mcpTool: "cortex_process_request",
                status: "implemented",  // implemented | partial | planned
                responsibilities: [...],
                tests: { count: 45, coverage: 92 },
                lastVerified: "2026-02-09"
            },
            // ... more core orchestrators
        ],
        domain: [...],
        support: [...]
    },
    
    // Capabilities Map
    capabilities: [
        {
            id: "governance",
            name: "4-Tier Governance",
            icon: "🛡️",
            description: "...",
            maturity: "implemented",
            relatedOrchestrators: ["enforcement-orchestrator"],
            benefits: {
                business: "Zero governance bypass",
                engineering: "Automated compliance"
            }
        },
        // ... more capabilities
    ],
    
    // Architecture Flow
    architecture: {
        layers: ["MCP", "Core", "Domain", "Support"],
        flows: [
            { from: "mcp-server", to: "master-orchestrator", label: "route" },
            { from: "master-orchestrator", to: "intent-router", label: "classify" },
            // ...
        ]
    },
    
    // Metrics & Evidence
    metrics: {
        orchestratorCount: 23,
        mcpToolCount: 15,
        testCoverage: 89,
        tokenReduction: 97,
        annualSavings: 8600
    },
    
    // Role Journeys
    roleJourneys: {
        "business-leader": {
            startTab: "overview",
            sequence: ["overview", "capabilities", "ops"],
            language: "business",  // Use business-friendly copy
            highlights: ["governance", "metrics", "savings"]
        },
        "software-engineer": {
            startTab: "architecture",
            sequence: ["architecture", "intelligence", "wiring", "testing"],
            language: "technical",
            highlights: ["orchestrators", "mcp-tools", "tdd"]
        },
        // ... more roles
    },
    
    // Truth Badges (Implementation Status)
    truthMatrix: {
        "master-orchestrator": { implemented: true, tests: true, docs: true },
        "planning-orchestrator": { implemented: true, tests: true, docs: false },
        "vision-api": { implemented: false, tests: false, docs: true },
        // ...
    }
};
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Phase 1: Foundation
- [ ] Create folder structure
- [ ] Set up DeploymentMode.js for file:// detection
- [ ] Create cortex-doc-data.js with embedded data
- [ ] Implement base CSS with glassmorphism system
- [ ] Create index.html shell

### Phase 2: Navigation
- [ ] Implement Role Tour landing with persona tiles
- [ ] Create tab system with ARIA accessibility
- [ ] Add Explorer Mode toggle
- [ ] Implement breadcrumb navigation

### Phase 3: Visualizations
- [ ] Bundle D3.js locally
- [ ] Create SVG architecture diagrams (no Mermaid)
- [ ] Implement D3 interactive network graph
- [ ] Add fallback static images for D3 failures

### Phase 4: Content
- [ ] Populate all 9 tabs with content
- [ ] Add Truth Badges to all components
- [ ] Implement role-specific language switching
- [ ] Add search functionality (client-side)

### Phase 5: Polish
- [ ] Test in file:// mode
- [ ] Test in HTTP mode
- [ ] Verify reduced motion support
- [ ] Mobile responsive testing
- [ ] Create README.md with offline instructions

---

## 🔗 REFERENCE FILES

| Source | Purpose |
|--------|---------|
| `docs/index.html` | Entry page design reference |
| `_workspaces/approved-orchestrator-view/index.html` | Level 1 page design reference |
| `docs/assets/css/main.css` | Full glassmorphism CSS system |
| `company/dashboards/spa/js/utils/DeploymentMode.js` | file:// detection pattern |
| `company/dashboards/spa/js/services/RepositoryService.js` | Data loading patterns |

---

## 📝 GIT HISTORY LEARNINGS

### Key Bug Fixes to Learn From

| Commit | Issue | Solution |
|--------|-------|----------|
| `87708f09f` | CORS workaround for file:// | Embed data in HTML |
| `c4d036a8c` | Skip fetch validation for file:// | Check protocol first |
| `6786fe097` | Dashboard SPA for file://, SVG sizing | Use DeploymentMode pattern |
| `b3f615356` | D3.js template literal syntax | Fix backtick usage |
| `e0e908154` | D3.js Orchestrator Map loading | Apply glassmorphism standards |
| `ff492a9b6` | DeploymentMode config loading | Check mode before fetch |
| `0acd1cc7b` | Holistic dashboard fix | PathResolver + AuditLogger pattern |

### Patterns That Work

1. **Embedded Data Pattern** - All JSON data as JS objects
2. **DeploymentMode Detection** - Check protocol before any network calls
3. **Pre-rendered SVG** - Avoid Mermaid, use inline SVG
4. **D3 with Fallback** - Always provide static fallback
5. **System Fonts** - Avoid external font CDNs
6. **Local Assets** - Bundle everything locally

### Patterns That Fail

1. ❌ `fetch()` in file:// mode
2. ❌ JSON imports in file:// mode
3. ❌ External CDN dependencies in offline mode
4. ❌ Mermaid.js without server
5. ❌ Dynamic image loading from paths

---

**End of Instructions**

*This document should be provided to ChatGPT along with the original cortex-app.txt conversation for context.*

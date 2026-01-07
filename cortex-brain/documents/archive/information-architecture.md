# Information Architecture - 4-Level Hierarchy

**Created:** December 28, 2025  
**Author:** Asif Hussain  
**Plan:** Knowledge Library Documentation & Learning Hub v2.0  
**Purpose:** Define progressive disclosure navigation structure

---

## 🏗️ Architecture Overview

The Knowledge Library uses a **4-level progressive disclosure hierarchy** to manage complexity and provide intuitive navigation for 65+ knowledge files across 17 categories.

```
┌─────────────────────────────────────────────────────────────────┐
│                         LEVEL 1: HOME                           │
│                    docs/index.html                              │
│  Single entry point: "📚 Knowledge Library" tile               │
│  in Core Capabilities section                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LEVEL 2: DOMAIN OVERVIEW                     │
│                 docs/knowledge/index.html                       │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │ 🎨 Frontend & UI│  │ 🔌 Backend & APIs│  │ 🗄️ Data Storage│ │
│  │  (3 categories) │  │  (3 categories)  │  │  (2 categories)│ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐ │
│  │ ☁️ Infrastructure│  │ 🏗️ Software Craft (6 categories)   │ │
│  │  (3 categories) │  └─────────────────────────────────────┘ │
│  └─────────────────┘                                           │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LEVEL 3: CATEGORY DETAIL                      │
│          docs/knowledge/{category}.html                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Tabs: Overview | Files | Resources | CORTEX Usage        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Overview Tab:                                                  │
│  • Category description                                         │
│  • Mermaid concept diagram                                      │
│  • High-priority rules showcase                                 │
│                                                                 │
│  Files Tab:                                                     │
│  • Collapsible accordion with knowledge files                   │
│  • Each file shows: name, description, rule count               │
│                                                                 │
│  Resources Tab:                                                 │
│  • Learning resources (books, docs, courses)                    │
│  • External links                                               │
│                                                                 │
│  CORTEX Usage Tab:                                              │
│  • How CORTEX uses this knowledge                               │
│  • Integration examples                                         │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                LEVEL 4: KNOWLEDGE FILE DETAIL                   │
│       docs/knowledge/{category}/{file}.html                     │
│                                                                 │
│  • All rules with full details                                  │
│  • Code examples with syntax highlighting                       │
│  • Good/Bad comparisons                                         │
│  • Cross-references to related files                            │
│  • Sticky table of contents sidebar                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Information Hierarchy Breakdown

### Level 1: Home (1 page)
**Purpose:** Single entry point  
**File:** `docs/index.html`  
**Content:** 
- Add "📚 Knowledge Library" tile to Core Capabilities section
- Tile leads to Level 2 (Domain Overview)

**Navigation:**
- Click tile → Level 2

---

### Level 2: Domain Overview (1 page)
**Purpose:** High-level organization into 5 domains  
**File:** `docs/knowledge/index.html`  
**Content:**
- 5 domain cards (Frontend & UI, Backend & APIs, Data & Storage, Infrastructure, Software Craft)
- Each card shows:
  - Domain emoji + name
  - Short description
  - Category preview chips (clickable)
  - File count badge
- Optional: D3.js category relationship diagram (below fold, lazy-loaded)
- Search bar (filters domains and categories)

**Navigation:**
- Breadcrumb: Home > Knowledge Library
- Back button (mobile)
- Domain card click → Level 3 (Category Detail) for first category
- Category chip click → Level 3 for specific category

**Cognitive Load:** 5 domains (easy to scan and remember)

---

### Level 3: Category Detail (17 pages)
**Purpose:** Deep dive into specific category  
**Files:** 
- `docs/knowledge/frontend.html`
- `docs/knowledge/ui-ux.html`
- `docs/knowledge/mobile.html`
- `docs/knowledge/api-design.html`
- `docs/knowledge/microservices.html`
- `docs/knowledge/messaging.html`
- `docs/knowledge/database.html`
- `docs/knowledge/performance.html`
- `docs/knowledge/cloud.html`
- `docs/knowledge/containers.html`
- `docs/knowledge/devops.html`
- `docs/knowledge/engineering.html`
- `docs/knowledge/ddd.html`
- `docs/knowledge/security.html`
- `docs/knowledge/testing.html`
- `docs/knowledge/rag-domains.html`

**Content (4 tabs):**

#### Tab 1: Overview
- Category description
- Mermaid diagram showing concept relationships
- High-priority rules showcase (3-5 rules)
- Quick stats (file count, total rules)

#### Tab 2: Knowledge Files
- Collapsible accordion with all YAML files
- Each accordion item:
  - File name
  - Short description
  - Rule count badge
  - Link to Level 4
- Expandable to show rule previews

#### Tab 3: Learning Resources
- Curated educational resources
- Books, documentation, courses, tutorials
- External links with descriptions

#### Tab 4: CORTEX Usage
- How CORTEX uses this knowledge
- Code generation examples
- Review patterns

**Navigation:**
- Breadcrumb: Home > Knowledge Library > [Domain] > [Category]
- Back button (mobile)
- Category sidebar (desktop) / bottom nav (mobile) for sibling navigation
- Tab navigation (keyboard accessible)
- Accordion items link to Level 4

**Cognitive Load:** 4 tabs + 3-6 knowledge files per category

---

### Level 4: Knowledge File Detail (65+ pages)
**Purpose:** Complete rule documentation for single YAML file  
**Files:** 
- `docs/knowledge/{category}/{file}.html`
- Examples:
  - `docs/knowledge/frontend/react-best-practices.html`
  - `docs/knowledge/cloud/aws-best-practices.html`
  - `docs/knowledge/engineering/clean-code.html`

**Content:**
- File metadata (title, author, source, version)
- Table of contents sidebar (sticky)
- All rules organized by section:
  - Rule ID + name
  - Description
  - Severity badge
  - Code examples (syntax highlighted)
  - Good/bad comparisons
  - Detection patterns
- Cross-references section (related files)
- "Back to [Category]" button

**Navigation:**
- Breadcrumb: Home > Knowledge Library > [Domain] > [Category] > [File]
- Back button (always visible)
- TOC sidebar navigation (desktop) / dropdown (mobile)
- Cross-reference links to related Level 4 pages

**Cognitive Load:** Single file (3-10 major sections, 5-15 rules)

---

## 🗺️ Navigation Patterns

### Breadcrumb Navigation (All Levels)
```html
<!-- Level 1: Home -->
No breadcrumb (root)

<!-- Level 2: Domain Overview -->
Home > Knowledge Library

<!-- Level 3: Category Detail -->
Home > Knowledge Library > Frontend & UI > Frontend

<!-- Level 4: File Detail -->
Home > Knowledge Library > Frontend & UI > Frontend > React Best Practices
```

**Behavior:**
- Sticky top position
- Each segment clickable
- Responsive (truncates on mobile with ellipsis)

### Sibling Navigation (Level 3)
**Desktop:** Sidebar with category list
**Mobile:** Bottom navigation bar (thumb zone)

Example (Frontend & UI domain):
```
┌─────────────────┐
│ 💻 Frontend     │ ← Active
│ 🎨 UI/UX        │
│ 📱 Mobile       │
└─────────────────┘
```

### Deep Linking
All pages support URL hash navigation:
```
docs/knowledge/index.html#frontend-ui          → Scroll to domain
docs/knowledge/frontend.html#files             → Open Files tab
docs/knowledge/frontend/react.html#hooks       → Jump to Hooks section
```

---

## 🎯 Progressive Disclosure Benefits

### Reduces Cognitive Load
- **Level 2:** 5 domains (not 17 categories)
- **Level 3:** 4 tabs (not all content at once)
- **Level 4:** TOC reveals structure (not overwhelming wall of text)

### Intuitive Navigation
- Familiar patterns (breadcrumbs, tabs, accordions)
- Clear "back" affordances
- Visual hierarchy (cards → tabs → sections)

### Performance
- Lazy loading (D3 diagrams, Mermaid)
- Progressive enhancement
- Skeleton screens

### Mobile-Friendly
- Large touch targets (48x48px minimum)
- Bottom navigation (thumb zone)
- Swipe gestures for sibling navigation
- Collapsible content (accordions)

---

## 📐 URL Structure

```
docs/
├── index.html                                     # Level 1: Home
└── knowledge/
    ├── index.html                                 # Level 2: Domain Overview
    ├── frontend.html                              # Level 3: Category (Frontend)
    ├── frontend/
    │   ├── react-best-practices.html              # Level 4: File
    │   ├── angular-patterns.html
    │   └── vue-patterns.html
    ├── ui-ux.html                                 # Level 3: Category
    ├── ui-ux/
    │   ├── ui-ux-best-practices.html              # Level 4: File
    │   └── accessibility-wcag.html
    ├── cloud.html                                 # Level 3: Category
    ├── cloud/
    │   ├── aws-best-practices.html                # Level 4: File
    │   └── azure-best-practices.html
    └── ... (remaining categories)
```

**Pattern:** `{level3}/{level4}.html`

---

## 🔄 User Journeys

### Journey 1: Browsing by Domain
```
User lands on Home (Level 1)
  → Clicks "📚 Knowledge Library" tile
  → Sees 5 domain cards (Level 2)
  → Clicks "🎨 Frontend & UI" domain
  → Lands on Frontend category page (Level 3)
  → Sees Overview tab with Mermaid diagram
  → Clicks "Files" tab
  → Expands "React Best Practices" accordion
  → Clicks "View Full Documentation"
  → Reads React rules (Level 4)
```

### Journey 2: Direct Search
```
User on Domain Overview (Level 2)
  → Types "circuit breaker" in search
  → Results show "Microservices > Resilience Patterns"
  → Clicks result
  → Lands on File Detail page (Level 4)
  → Reads circuit breaker rules
```

### Journey 3: Cross-Reference Navigation
```
User reading "React Best Practices" (Level 4)
  → Sees cross-reference to "TypeScript Frontend"
  → Clicks link
  → Navigates to TypeScript file (Level 4)
  → Breadcrumb shows: Home > ... > Frontend > TypeScript Frontend
  → Can use breadcrumb to go back to Frontend category (Level 3)
```

---

## ✅ Validation Criteria

**Level 2 (Domain Overview):**
- [ ] All 5 domains visible
- [ ] Category chips clickable
- [ ] Search filters correctly
- [ ] D3 diagram loads lazily

**Level 3 (Category Detail):**
- [ ] All 17 category pages exist
- [ ] 4 tabs functional (keyboard accessible)
- [ ] Accordions expand/collapse
- [ ] Mermaid diagrams render
- [ ] Sibling navigation works

**Level 4 (File Detail):**
- [ ] All 65+ file pages exist
- [ ] TOC sidebar functional
- [ ] Syntax highlighting works
- [ ] Cross-references link correctly
- [ ] Breadcrumbs accurate

**Navigation:**
- [ ] Breadcrumbs on all pages
- [ ] Back button functional (mobile)
- [ ] Deep linking works (URL hashes)
- [ ] No broken links

---

**Status:** COMPLETE - Ready for wireframing

---

**Copyright © 2025 Asif Hussain. All rights reserved.**

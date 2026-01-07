# Wireframes - Knowledge Library UI

**Created:** December 28, 2025  
**Author:** Asif Hussain  
**Plan:** Knowledge Library Documentation & Learning Hub v2.0  
**Purpose:** Visual mockups for 4-level hierarchy

---

## 🖼️ Level 1: Home Page (docs/index.html)

```
┌───────────────────────────────────────────────────────────────────┐
│  [CORTEX Logo]                                            [Nav]   │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│                    🧠 CORTEX Features                             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ 📋 Planning  │  │ 🧪 TDD       │  │ 🔄 Refine    │           │
│  │ System       │  │ Mastery      │  │ System       │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ 🧹 Sanitize  │  │ 🛠️ System    │  │ 📚 Knowledge │  ← NEW    │
│  │ Code         │  │ Operations   │  │ Library      │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                   │
│                  [Explore Library →]                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Tile Specs:**
- Size: Same as existing tiles (glass-card)
- Icon: 📚 (2.4rem per styling standards)
- Title: "Knowledge Library"
- Description: "65+ knowledge files across 17 categories"
- CTA: "Explore Library →"
- Link: `knowledge/index.html`

---

## 🖼️ Level 2: Domain Overview (docs/knowledge/index.html)

### Desktop View

```
┌───────────────────────────────────────────────────────────────────┐
│  [CORTEX Logo 300px]        📚 Knowledge Library                  │
├───────────────────────────────────────────────────────────────────┤
│  Home > Knowledge Library                                         │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────┐                 │
│  │  🔍 Search knowledge files...               │                 │
│  └─────────────────────────────────────────────┘                 │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🎨 Frontend & UI                                           │  │
│  │ User interface development, frontend frameworks, and UX    │  │
│  │                                                            │  │
│  │ [💻 Frontend] [🎨 UI/UX] [📱 Mobile]            14 files  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🔌 Backend & APIs                                          │  │
│  │ API design, microservices architecture, and messaging      │  │
│  │                                                            │  │
│  │ [🔌 API] [⚙️ Microservices] [📬 Messaging]      12 files  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 🗄️ Data & Storage                                          │  │
│  │ Database patterns, performance, and caching                │  │
│  │                                                            │  │
│  │ [🗄️ Databases] [⚡ Performance]                  9 files  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  [☁️ Infrastructure] [🏗️ Software Craft] ...                     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  📊 Category Relationships (D3.js diagram - lazy loaded)   │  │
│  │                                                            │  │
│  │        Frontend ─────── React                              │  │
│  │            │                                               │  │
│  │         TypeScript ───── Node.js ───── Microservices      │  │
│  │            │                                               │  │
│  │        Testing ──────── API Design                         │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Mobile View (320px - 767px)

```
┌────────────────────────┐
│ [Logo 200px]           │
│ ← Back                 │
├────────────────────────┤
│ Home > Knowledge       │
├────────────────────────┤
│                        │
│ 🔍 [Search...]         │
│                        │
│ ┌────────────────────┐ │
│ │ 🎨 Frontend & UI   │ │
│ │ UI development,    │ │
│ │ frameworks, UX     │ │
│ │                    │ │
│ │ [💻] [🎨] [📱]     │ │
│ │        14 files    │ │
│ └────────────────────┘ │
│                        │
│ ┌────────────────────┐ │
│ │ 🔌 Backend & APIs  │ │
│ │ API design, micro- │ │
│ │ services, messaging│ │
│ │                    │ │
│ │ [🔌] [⚙️] [📬]     │ │
│ │        12 files    │ │
│ └────────────────────┘ │
│                        │
│ [More domains...]      │
│                        │
└────────────────────────┘
```

**Specs:**
- Domain cards: glass-card with hover effect (translateY(-8px))
- Category chips: inline badges, clickable
- Search: Live filtering, debounced
- D3 diagram: Hidden below fold, Intersection Observer loading

---

## 🖼️ Level 3: Category Detail (docs/knowledge/frontend.html)

### Desktop View

```
┌───────────────────────────────────────────────────────────────────┐
│  [CORTEX Logo 300px]           💻 Frontend Development            │
├───────────────────────────────────────────────────────────────────┤
│  ← Back | Home > Knowledge > Frontend & UI > Frontend            │
├───────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌───────────────────────────────────────────────┐   │
│ │ SIDEBAR  │ │  [Overview] [Files] [Resources] [CORTEX Usage]│   │
│ │          │ ├───────────────────────────────────────────────┤   │
│ │ Frontend │ │                                               │   │
│ │ & UI:    │ │  # Overview                                   │   │
│ │          │ │                                               │   │
│ │ • Frontend│ │  Frontend development focuses on building     │   │
│ │ • UI/UX  │ │  modern, performant user interfaces...        │   │
│ │ • Mobile │ │                                               │   │
│ │          │ │  ## Concept Map (Mermaid)                     │   │
│ └──────────┘ │  ┌─────────────────────────────────────────┐  │   │
│              │  │  React ──→ Components                    │  │   │
│              │  │    │                                      │  │   │
│              │  │    ├──→ Hooks                            │  │   │
│              │  │    │                                      │  │   │
│              │  │    └──→ State Management                 │  │   │
│              │  └─────────────────────────────────────────┘  │   │
│              │                                               │   │
│              │  ## High-Priority Rules                       │   │
│              │                                               │   │
│              │  ⚠️ Use Function Components with Hooks       │   │
│              │  Modern React uses hooks over class comp...   │   │
│              │                                               │   │
│              │  ⚠️ Single Responsibility Principle           │   │
│              │  Each component should do one thing well...   │   │
│              └───────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### Files Tab (Accordion)

```
┌───────────────────────────────────────────────────────────────────┐
│  [Overview] [Files] [Resources] [CORTEX Usage]                    │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ▼ React Best Practices                          [25 rules] │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Component design, hooks, performance optimization...        │ │
│  │                                                             │ │
│  │ Featured Rules:                                             │ │
│  │ • Use Function Components with Hooks                        │ │
│  │ • Implement React.memo for Pure Components                  │ │
│  │ • Always Specify Effect Dependencies                        │ │
│  │                                                             │ │
│  │ [View Full Documentation →]                                 │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ▶ Angular Patterns                               [18 rules] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ▶ Vue Patterns                                   [16 rules] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Mobile View

```
┌────────────────────────┐
│ [Logo 200px]           │
│ ← Back                 │
├────────────────────────┤
│ Home > ... > Frontend  │
├────────────────────────┤
│                        │
│ [Overview] [Files] ... │
│ ──────────             │
│                        │
│ # Overview             │
│                        │
│ Frontend development   │
│ focuses on...          │
│                        │
│ [Mermaid Diagram]      │
│ (Scroll horizontally)  │
│                        │
│ ## High-Priority Rules │
│                        │
│ ⚠️ Function Components│
│ ...                    │
│                        │
├────────────────────────┤
│ [💻] [🎨] [📱]         │ ← Bottom Nav
└────────────────────────┘
```

**Specs:**
- Tabs: Keyboard accessible (Tab, Arrow keys)
- Accordions: Smooth expand/collapse (CSS transition)
- Mermaid: Overflow-x: auto on mobile
- Bottom nav: Fixed position (thumb zone)

---

## 🖼️ Level 4: Knowledge File Detail (docs/knowledge/frontend/react-best-practices.html)

### Desktop View

```
┌───────────────────────────────────────────────────────────────────┐
│  [CORTEX Logo 300px]           💻 React Best Practices            │
├───────────────────────────────────────────────────────────────────┤
│  Home > Knowledge > Frontend & UI > Frontend > React              │
├───────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌───────────────────────────────────────────────┐   │
│ │ TOC      │ │  # React Best Practices                       │   │
│ │ (Sticky) │ │                                               │   │
│ │          │ │  **Author:** React Team                       │   │
│ │ Contents:│ │  **Source:** Official Documentation           │   │
│ │          │ │  **Rules:** 25 | **Severity:** High           │   │
│ │ • Component│ │                                             │   │
│ │   Design │ │  ## 1. Component Design                       │   │
│ │ • Hooks  │ │                                               │   │
│ │ • State  │ │  ### Use Function Components with Hooks       │   │
│ │ • Effects│ │  **Severity:** HIGH                           │   │
│ │ • Error  │ │                                               │   │
│ │   Handling│ │  ✅ Good:                                    │   │
│ │          │ │  ```jsx                                       │   │
│ │ Related: │ │  function Counter() {                         │   │
│ │ • TypeScript│ const [count, setCount] = useState(0);     │   │
│ │ • State Mgmt││                                           │   │
│ └──────────┘ │    return <button onClick={() =>             │   │
│              │      setCount(count + 1)}>                    │   │
│              │      Count: {count}                           │   │
│              │    </button>;                                 │   │
│              │  }                                            │   │
│              │  ```                                          │   │
│              │                                               │   │
│              │  ❌ Bad:                                       │   │
│              │  ```jsx                                       │   │
│              │  class Counter extends React.Component {      │   │
│              │    // Legacy class component                  │   │
│              │  }                                            │   │
│              │  ```                                          │   │
│              │                                               │   │
│              │  ---                                          │   │
│              │                                               │   │
│              │  ## Cross-References                          │   │
│              │                                               │   │
│              │  • [TypeScript Frontend](typescript-frontend) │   │
│              │  • [State Management](state-management)       │   │
│              │  • [Testing TDD](../../testing/tdd)           │   │
│              └───────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

### Mobile View

```
┌────────────────────────┐
│ [Logo 200px]           │
│ ← Back to Frontend     │
├────────────────────────┤
│ Home > ... > React     │
├────────────────────────┤
│ [▼ Contents]           │ ← Collapsible TOC
├────────────────────────┤
│                        │
│ # React Best Practices │
│                        │
│ **Author:** React Team │
│ **Rules:** 25          │
│                        │
│ ## Component Design    │
│                        │
│ ### Function Components│
│ **Severity:** HIGH     │
│                        │
│ ✅ Good:               │
│ ```jsx                 │
│ function Counter() {   │
│   const [count, set..  │
│ ```                    │
│ (Scroll horizontally)  │
│                        │
│ ❌ Bad:                │
│ ```jsx                 │
│ class Counter ...      │
│ ```                    │
│                        │
│ ---                    │
│                        │
│ [More rules...]        │
│                        │
│ ## Cross-References    │
│ • TypeScript Frontend  │
│ • State Management     │
│                        │
└────────────────────────┘
```

**Specs:**
- TOC: Sticky position on desktop, collapsible dropdown on mobile
- Code blocks: Syntax highlighted (Prism.js), overflow-x: auto
- Badges: Severity color-coded (HIGH=red, MEDIUM=orange, LOW=blue)
- Cross-refs: Internal links, open in same tab

---

## 🎨 Component Library

### Glass Card
```css
.glass-card {
    background: rgba(26, 31, 58, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    backdrop-filter: blur(10px);
    padding: 2rem;
    margin-bottom: 3rem;  /* 48px per standards */
}
```

### Domain Card (Level 2)
```css
.domain-card {
    composes: glass-card;
    cursor: pointer;
    transition: transform var(--transition-base);
}

.domain-card:hover {
    transform: translateY(-8px);
    border-color: var(--accent-primary);
}
```

### Accordion (Level 3)
```css
.accordion-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--glass-bg);
    border-radius: 12px;
    cursor: pointer;
}

.accordion-header[aria-expanded="true"] .chevron {
    transform: rotate(180deg);
}

.accordion-content {
    padding: 1rem;
    background: rgba(26, 31, 58, 0.5);
}
```

### Tab Navigation (Level 3)
```css
.tabs-nav {
    display: flex;
    gap: 0.5rem;
    border-bottom: 2px solid var(--glass-border);
    margin-bottom: 2rem;
}

.tab-button {
    padding: 1rem 1.5rem;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: color var(--transition-base);
}

.tab-button.active {
    color: var(--accent-primary);
    border-bottom: 2px solid var(--accent-primary);
}
```

---

## ✅ Wireframe Validation

**Level 2 (Domain Overview):**
- [ ] 5 domain cards visible
- [ ] Category chips render
- [ ] Search bar prominent
- [ ] D3 diagram below fold

**Level 3 (Category Detail):**
- [ ] 4 tabs clearly labeled
- [ ] Accordion expandable
- [ ] Mermaid diagram renders
- [ ] Sibling nav visible (desktop) or bottom nav (mobile)

**Level 4 (File Detail):**
- [ ] TOC sidebar functional
- [ ] Code blocks syntax highlighted
- [ ] Severity badges visible
- [ ] Cross-references linked

**Responsive:**
- [ ] Mobile: Logo 200px
- [ ] Desktop: Logo 300px
- [ ] Mobile: Bottom nav (thumb zone)
- [ ] Desktop: Sidebar nav
- [ ] All touch targets ≥48px

---

**Status:** WIREFRAMES COMPLETE

---

**Copyright © 2025 Asif Hussain. All rights reserved.**

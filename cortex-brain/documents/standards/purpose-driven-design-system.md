# 🎨 CORTEX Purpose-Driven Design System
## Level-Based Design Variations

**Author:** Asif Hussain  
**Version:** 1.0.0  
**Date:** January 4, 2026  
**Copyright:** © 2026 Asif Hussain. All rights reserved.

---

## 📐 Design Philosophy

**Core Principle:** Each page should be **designed for its specific purpose**, not follow a monotonous template.

### Hierarchy
- **Level 0 (Home):** `docs/index.html` - Grand entrance with 9 navigation tiles
- **Level 1 (Hubs):** Category overview pages (e.g., `architecture/index.html`, `security/index.html`)
- **Level 2 (Details):** Deep-dive content pages (e.g., `security/access-control.html`)

---

## 🎨 Color Scheme Strategy

### Level 0: Home Page
```css
Primary: #00d4ff (Cyan - CORTEX brand)
Secondary: #7c7cff (Purple - Intelligence)
Accent: #00ff88 (Green - Success/Active)
```

### Level 1: Hub Pages
```css
Primary: #00d4ff (Cyan - Consistent with home)
Secondary: #4a9eff (Blue - Navigation)
Accent: Varies by category:
  - Architecture: #00b8d4 (Deep cyan)
  - Security: #ff6b6b (Red)
  - Orchestrators: #ffa726 (Orange)
  - Knowledge: #9d9dff (Light purple)
```

### Level 2: Detail Pages
```css
Primary: #7c7cff (Purple - Focus mode)
Secondary: #9d9dff (Light purple - Softer)
Accent: Inherited from Level 1 category
```

---

## 🏗️ Layout Patterns by Purpose

### 1. **Navigation Hub** (Home, Level 1 Hubs)

**Purpose:** Help users find their destination quickly

**Design Elements:**
- Large, tappable navigation tiles
- Multi-panel category organization
- Tetris-style metric tiles for quick stats
- Minimal text, maximum visuals

**Example Pages:**
- `docs/index.html` (9 Level 0 tiles)
- `docs/architecture/index.html` (Tetris metrics + tier navigation)
- `docs/security/index.html` (Multi-panel with 4 categories)

**Layout:**
```
┌─────────────────────────────────────┐
│ Hero: Title + Quick Metrics         │
├─────────────────────────────────────┤
│ ┌─────┐ ┌─────┐ ┌─────┐            │
│ │Tile1│ │Tile2│ │Tile3│            │
│ └─────┘ └─────┘ └─────┘            │
│ ┌─────┐ ┌─────┐ ┌─────┐            │
│ │Tile4│ │Tile5│ │Tile6│            │
│ └─────┘ └─────┘ └─────┘            │
└─────────────────────────────────────┘
```

---

### 2. **Technical Deep Dive** (Level 2)

**Purpose:** Provide comprehensive technical documentation

**Design Elements:**
- Clean, readable single-column layout
- Code examples with syntax highlighting
- Mermaid flowcharts for processes
- Technical specifications in tables

**Example Pages:**
- `docs/security/access-control.html` (RBAC documentation)
- `docs/features/planning-system.html` (System architecture)

**Layout:**
```
┌─────────────────────────────────────┐
│ Hero: Icon + Title + Subtitle       │
├─────────────────────────────────────┤
│ Introduction paragraph              │
├─────────────────────────────────────┤
│ Mermaid Diagram: Architecture       │
├─────────────────────────────────────┤
│ Code Example:                       │
│ ```python                           │
│ def example(): ...                  │
│ ```                                 │
├─────────────────────────────────────┤
│ Specifications Table                │
└─────────────────────────────────────┘
```

---

### 3. **Conceptual Learning** (Level 2)

**Purpose:** Teach concepts with visual aids

**Design Elements:**
- Two-column layout (concept + visual)
- Interactive D3.js diagrams
- Step-by-step progression
- Quiz/interactive elements

**Example Pages:**
- `docs/knowledge/api-design/rest-principles.html` (Richardson Maturity Model)
- `docs/knowledge/ddd/bounded-contexts.html` (DDD concepts)

**Layout:**
```
┌──────────────────┬──────────────────┐
│ Concept Text     │ D3.js Visual     │
│                  │                  │
│ Explanation...   │ [Interactive]    │
│                  │                  │
├──────────────────┴──────────────────┤
│ Step-by-step walkthrough            │
├─────────────────────────────────────┤
│ Interactive quiz                    │
└─────────────────────────────────────┘
```

---

### 4. **Dashboard** (Level 1/2)

**Purpose:** Show status, metrics, and health

**Design Elements:**
- Grid of metric cards
- Status indicators (colors)
- Real-time data visualization
- Trend charts

**Example Pages:**
- `docs/token-optimization/index.html` (Token metrics)
- `docs/security/dashboard.html` (Security status)

**Layout:**
```
┌─────────────────────────────────────┐
│ ┌────────┐ ┌────────┐ ┌────────┐   │
│ │Metric 1│ │Metric 2│ │Metric 3│   │
│ │  92%   │ │  1.2K  │ │  ✓ OK  │   │
│ └────────┘ └────────┘ └────────┘   │
├─────────────────────────────────────┤
│ Trend Chart (D3.js)                 │
│ ▁▂▃▅▆▇█                            │
├─────────────────────────────────────┤
│ Status Table                        │
└─────────────────────────────────────┘
```

---

### 5. **Reference Guide** (Level 2)

**Purpose:** Quick lookup of APIs, specifications

**Design Elements:**
- Searchable/filterable content
- Code snippets
- Parameter tables
- Examples

**Example Pages:**
- API documentation
- Command reference

**Layout:**
```
┌─────────────────────────────────────┐
│ Search: [_______________]           │
├─────────────────────────────────────┤
│ Function: getName()                 │
│ Parameters:                         │
│ - id: string                        │
│ Returns: string                     │
│                                     │
│ Example:                            │
│ const name = getName("123")         │
└─────────────────────────────────────┘
```

---

## 🎯 Purpose-Specific Enhancements

### Architecture Hub (`architecture/index.html`)
- **Tetris metrics** showing 4 brain tiers
- **Force-directed graph** of component relationships
- **Tier navigation cards** (clickable)
- Color: Cyan (#00d4ff)

### Security Hub (`security/index.html`)
- **Multi-panel layout** with 4 categories:
  - Protection
  - Assessment
  - Compliance
  - Response
- **Threat matrix visualization** (D3.js heatmap)
- **Compliance status dashboard**
- Color: Red (#ff6b6b)

### Orchestrators Hub (`orchestrators/index.html`)
- **Category grid** (Planning, Execution, System, Analysis, Debug)
- **Master orchestrator flow diagram**
- **22 orchestrator cards** with icons
- Color: Orange (#ffa726)

### Knowledge Hub (`knowledge/index.html`)
- **Learning path navigator**
- **17 domain cards** (API Design, Cloud, DDD, etc.)
- **Progress tracker**
- Color: Light Purple (#9d9dff)

---

## 🔧 Implementation Guidelines

### 1. **Start with Purpose**
Before designing a page, ask:
- What is the user trying to accomplish?
- What's the most important action/information?
- How technical is the audience?

### 2. **Choose Layout**
Based on purpose:
- **Navigation:** Multi-panel or grid
- **Technical:** Single-column with diagrams
- **Learning:** Two-column (text + visual)
- **Dashboard:** Metric cards + charts

### 3. **Select Visualization**
- **D3.js:** Complex relationships, interactive exploration
- **Mermaid:** Process flows, sequences, state machines
- **Tables:** Specifications, parameters, comparisons
- **Code:** Implementation examples

### 4. **Apply Color Scheme**
- **Level 1:** Use category accent color for highlights
- **Level 2:** Use softer purple with category accent for CTAs

### 5. **Add Interactions**
- **Level 1:** Hover effects on navigation tiles
- **Level 2:** Interactive diagrams, expandable sections

---

## 📊 Design Matrix

| Page Type | Level | Layout | Primary Color | Key Features |
|-----------|-------|--------|---------------|--------------|
| Home | 0 | Multi-panel (9 tiles) | #00d4ff | Level 0 tiles, hero banner |
| Architecture Hub | 1 | Tetris cards | #00d4ff | Tetris metrics, tier nav |
| Security Hub | 1 | Multi-panel (4 cats) | #ff6b6b | Threat matrix, panels |
| Orchestrators Hub | 1 | Grid + flow | #ffa726 | 22 cards, flow diagram |
| Knowledge Hub | 1 | Learning navigator | #9d9dff | 17 domains, progress |
| Access Control | 2 | Single-column | #7c7cff | RBAC diagram, code |
| REST Principles | 2 | Two-column | #7c7cff | D3.js maturity model |
| Planning System | 2 | Single-column | #7c7cff | 10-phase flow, specs |

---

## 🚀 Quick Reference

### When to use **Tetris Metrics**:
- Level 1 hubs with quantifiable metrics
- Dashboard pages
- Overview pages with 4-6 key stats

### When to use **Multi-Panel**:
- Level 1 hubs with 3-6 categories
- Navigation-heavy pages
- Content with clear groupings

### When to use **D3.js**:
- Complex relationships (force-directed)
- Hierarchies (tree, sunburst)
- Data flows (sankey)
- Interactive exploration

### When to use **Mermaid**:
- Process flows (flowchart)
- Sequences (sequence diagram)
- State machines (state diagram)
- Simple quick diagrams

---

## ✅ Design Checklist

Before publishing any page:

- [ ] Purpose clearly defined
- [ ] Appropriate layout chosen
- [ ] Color scheme matches level
- [ ] Hero section matches style guide
- [ ] Glassmorphism classes applied
- [ ] Font Awesome icons have prefixes
- [ ] No inline styles
- [ ] Mobile responsive (375px-1440px)
- [ ] WCAG 2.1 AA compliant
- [ ] Diagrams added (if applicable)
- [ ] Navigation breadcrumbs present

---

**Remember:** Design for **purpose**, not **uniformity**. Each page should feel cohesive with the system but optimized for its specific user need.

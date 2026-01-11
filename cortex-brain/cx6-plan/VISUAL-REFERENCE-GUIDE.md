# 🎨 CORTEX Plan Viewer - Visual Reference Guide

## Dashboard Layout

```
┌────────────────────────────────────────────────────────────────────┐
│                          CORTEX 6.0 DASHBOARD                      │
│                    [Breadcrumb: CORTEX > Dashboard]                 │
└────────────────────────────────────────────────────────────────────┘

┌── HEADER SECTION ─────────────────────────────────────────────────┐
│  CORTEX 6.0  │  Design Score: 97/95  │  Phase 1.5  │  99.4% Tests │
└───────────────────────────────────────────────────────────────────┘

┌── METRICS ROW ────────────────────────────────────────────────────┐
│  📊 AC-IDs: 97  │  ✅ Completed: 18  │  Current Phase: 1.5  │ ... │
└───────────────────────────────────────────────────────────────────┘

┌── PHASE PROGRESS ─────────────────────────────────────────────────┐
│  [Phase 1] 48% ████████▒░  │  [Phase 1.5] 85% ██████████░░  │   │
│  [Phase 2] 0%  ░░░░░░░░░░  │  [Phase 3] 0%    ░░░░░░░░░░   │   │
│  [Phase 4] 0%  ░░░░░░░░░░  │                                     │
└───────────────────────────────────────────────────────────────────┘

┌─ 🌐 HTML VIEWER PAGES - INTERACTIVE DASHBOARDS ──────────────────┐
│  ↓ Click any view below to launch interactive dashboards...       │
│                                                                    │
│  Phase 1: Foundation Enhancement (4 Views) [CYAN]                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │📍 Roadmap    │📊 Progress   │🔍 AC-ID      │⚠️ Gap        │   │
│  │20-wk timeline│Charts & D3.js│Searchable 97 │Analysis risk │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                    │
│  Phase 2: Verification & Validation (4 Views) [YELLOW]           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │✅ Phase 1    │🛡️ CORE Rules │🧪 STS Tests  │🔗 Holistic   │   │
│  │Completion    │23 SKULL rules│Framework val │7-state cycle │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                    │
│  Phase 3: Architecture & Design (4 Views) [GREEN]                │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │📖 Manual     │🏛️ Governance │🔧 MCP Tools  │🔎 Phase      │   │
│  │Routing table │4-tier system │13-tool reg   │Drill-down    │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                    │
│  Phase 4: Intelligence & Integration (4 Views) [PURPLE]          │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │🔄 Lifecycle  │🤖 Autonomous │⚡ Token Opt  │🔗 ADO        │   │
│  │7-state machi │TDD cycles    │LLM cost anal │Work items    │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
│                                                                    │
│  📌 16 interactive views with real-time updates every 30 secs    │
└────────────────────────────────────────────────────────────────────┘

┌─ DOCUMENTATION & RESOURCES ───────────────────────────────────────┐
│                                                                    │
│  [Core Planning]    │  [Validation & Quality] │  [Live Tracking] │
│  • master-plan.yaml │  • Phase 1 Verification │  • Progress      │
│  • Implementation   │  • STS Implementation   │  • AC-INDEX      │
│  • Gap Analysis     │  • Test Suites          │  • Evidence      │
│                                                                    │
│  [Architecture]     │  [Supporting Resources]                    │
│  • CORTEX.prompt    │  • README               │                 │
│  • CORE Rules       │  • Golden Corpus        │                 │
│  • governance.db    │  • Audit Logs           │                 │
└────────────────────────────────────────────────────────────────────┘

┌─ FOOTER ──────────────────────────────────────────────────────────┐
│ CORTEX 6.0 - Production-Grade AI Orchestration Framework          │
│ Last Updated: 2026-01-11 | 🔗 GitHub Repository                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## View Card Design

Each of the 16 cards follows this design pattern:

```
┌─────────────────────────────────────┐
│ 🎨 [Icon] [View Title]              │  ← Phase-specific color bar
├─────────────────────────────────────┤
│                                     │
│ [2-3 sentence description of what   │
│  this view does and what insights   │
│  it provides to the user]           │
│                                     │
└─────────────────────────────────────┘
  ↑                                ↑
  │                                │
Color: Phase 1=Cyan, 2=Yellow,   Link: target="_blank"
       3=Green, 4=Purple           Opens in new tab

Responsive: 4→2→1 columns
```

---

## Phase 1: Foundation Enhancement (Cyan #00d4ff)

### 📍 Implementation Roadmap
```
Features:
  • 20-week timeline breakdown
  • Milestones and deliverables
  • Velocity analysis
  • Dependency tracking
  • Critical path identification

Purpose: Understand the complete execution plan
```

### 📊 Progress Dashboard
```
Features:
  • Real-time Chart.js visualizations
  • D3.js network diagrams
  • Phase progress bars
  • AC-ID status breakdown
  • Completion percentages

Purpose: Monitor ongoing progress in real-time
```

### 🔍 AC-ID Explorer
```
Features:
  • Searchable grid of 97 AC-IDs
  • Filter by phase, status, category
  • Drill-down into AC details
  • Evidence bundle links
  • Implementation status

Purpose: Discover and explore specific acceptance criteria
```

### ⚠️ Gap Analysis
```
Features:
  • Risk matrix visualization
  • Missing components list
  • Critical blockers
  • Phase-by-phase gaps
  • Priority heatmap

Purpose: Identify gaps and understand risks
```

---

## Phase 2: Verification & Validation (Yellow #ffbe0b)

### ✅ Phase 1 Verification
```
Features:
  • Completion timeline
  • Proof of implementations
  • Test results
  • 16 implemented AC-IDs
  • Evidence verification

Purpose: Validate Phase 1 completion
```

### 🛡️ CORE Rules Viewer
```
Features:
  • All 23 SKULL rules
  • Severity levels color-coded
  • Enforcement hooks
  • Failure modes
  • Rule heatmap

Purpose: Understand immutable governance rules
```

### 🧪 STS Implementation Summary
```
Features:
  • Phase 1.5 overview
  • 100 test intents
  • 5 test suites
  • Framework validation
  • Evidence bundle

Purpose: Review framework validation strategy
```

### 🔗 Holistic Verification
```
Features:
  • 7-state lifecycle diagram
  • Evidence bundle structure
  • Validation gates
  • Quality metrics
  • Proof requirements

Purpose: Understand verification framework
```

---

## Phase 3: Architecture & Design (Green #06ffa5)

### 📖 CORTEX Operating Manual
```
Features:
  • Intent routing table
  • Governance pyramid
  • Routing patterns
  • Pattern matching rules
  • LLM fallback logic

Purpose: Learn orchestration principles
```

### 🏛️ Governance Architecture
```
Features:
  • 4-tier governance system
  • Precedence rules
  • Conflict resolution
  • Rule merging strategy
  • Example scenarios

Purpose: Understand governance design
```

### 🔧 MCP Capabilities Explorer
```
Features:
  • 13-tool registry
  • Tool descriptions
  • Parameters and inputs
  • Invocation examples
  • Modal details

Purpose: Discover available tools
```

### 🔎 Phase Detail Drill-Down
```
Features:
  • Interactive phase breakdown
  • Mermaid diagrams
  • AC-ID mapping per phase
  • Timeline view
  • Dependency visualization

Purpose: Deep-dive into specific phases
```

---

## Phase 4: Intelligence & Integration (Purple #7b2cbf)

### 🔄 Orchestration Lifecycle
```
Features:
  • 7-state machine diagram
  • State transitions
  • Middleware pipeline
  • Handler functions
  • Error handling flow

Purpose: Understand execution lifecycle
```

### 🤖 Autonomous Execution Deep-Dive
```
Features:
  • RED→GREEN→REFACTOR cycles
  • Git history intelligence
  • Implementation workflows
  • TDD pattern details
  • Discovery process

Purpose: Learn autonomous execution strategy
```

### ⚡ Token Optimization Strategy
```
Features:
  • LLM cost analysis
  • Sonnet vs Opus trade-offs
  • Prompt optimization
  • Context efficiency
  • Cost-quality curves

Purpose: Optimize token usage and costs
```

### 🔗 ADO Integration Capabilities
```
Features:
  • Work item automation
  • Sync mechanisms
  • Epic/Feature hierarchy
  • Query examples
  • Pull request integration

Purpose: Integrate with Azure DevOps
```

---

## Color Scheme Reference

```
Primary Colors (Phase-Based):
  Phase 1: Cyan      #00d4ff  (Foundation - fresh, beginning)
  Phase 2: Yellow    #ffbe0b  (Verification - caution, testing)
  Phase 3: Green     #06ffa5  (Architecture - growth, design)
  Phase 4: Purple    #7b2cbf  (Intelligence - advanced, complex)

Supporting Colors:
  Success:           #06ffa5  (bright green)
  Warning:           #ffbe0b  (golden yellow)
  Danger:            #ff006e  (hot pink)
  Info:              #00d4ff  (cyan)

Backgrounds:
  Dark:              #0a0a0f  (almost black)
  Card Glass:        rgba(255,255,255,0.05)
  Hover:             rgba(255,255,255,0.1)

Text:
  Primary:           #ffffff  (white)
  Secondary:         #b0b0c0  (light gray)
  Muted:             #808080  (medium gray)
```

---

## Navigation Paths

### From Dashboard to Any View
```
Dashboard (cortex-plan-viewer.html)
  ↓ [Click view card]
  ↓
Interactive View (*.html)
  ├─ [Breadcrumb: Dashboard]
  │   ↓ [Click]
  │   ↓
  │   Back to Dashboard
  │
  └─ [Sidebar: Other views]
      ↓ [Click]
      ↓
      Switch to Another View
```

### Complete Ecosystem
```
                    Dashboard
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    Phase 1 Views  Phase 2 Views  Phase 3 Views  Phase 4 Views
    (4 views)      (4 views)      (4 views)      (4 views)
        ↓               ↓               ↓               ↓
    Roadmap         Verification   Manual         Lifecycle
    Progress        CORE Rules     Governance     Autonomous
    AC-ID           STS Tests      MCP Tools      Token Opt
    Gap Analysis    Holistic       Phase Detail   ADO Integration
```

---

## Responsive Behavior

### Desktop (1200px+)
```
┌─ Phase Section Header ─────────────────────────┐
├─ Card 1 ─┬─ Card 2 ─┬─ Card 3 ─┬─ Card 4 ─┤
└──────────┴──────────┴──────────┴──────────┘
  4 columns, full width cards
```

### Tablet (768px-1199px)
```
┌─ Phase Section Header ──────────────────┐
├─ Card 1 ─┬─ Card 2 ─┤
├─ Card 3 ─┬─ Card 4 ─┤
└──────────┴──────────┘
  2 columns, medium cards
```

### Mobile (< 768px)
```
┌─ Phase Section Header ────┐
├─ Card 1 ──────────────────┤
├─ Card 2 ──────────────────┤
├─ Card 3 ──────────────────┤
├─ Card 4 ──────────────────┤
└────────────────────────────┘
  1 column, full-width stacked
```

---

## Accessibility Features

✅ **Semantic HTML**: Proper heading hierarchy (h1, h2, h3, h4, h5, h6)  
✅ **Color + Icons**: Not relying on color alone for meaning  
✅ **Text Descriptions**: Each card has descriptive text  
✅ **Link Labels**: Clear, descriptive link text  
✅ **Breadcrumbs**: Help with page orientation  
✅ **Keyboard Navigation**: All interactive elements accessible  
✅ **ARIA Labels**: Proper labels for screen readers  
✅ **Contrast Ratio**: Text readable on dark background  

---

## Technical Stack

- **Framework**: Bootstrap 5.3.2
- **Icons**: Bootstrap Icons 1.11.3
- **Visualizations**: Chart.js 4.4.1, D3.js v7, Mermaid.js 10.6.1
- **Data**: YAML (plan), JSON (tracking), JSONL (audit)
- **Styling**: Dark theme with glassmorphism
- **Responsive**: Mobile-first grid design

---

## Quick Start Guide

### For End Users
1. Open `cortex-plan-viewer.html`
2. Scroll to "HTML Viewer Pages"
3. Choose a phase (1-4) by color
4. Click view card
5. Explore interactive dashboard
6. Use breadcrumb to return

### For Developers
1. View HTML in `/viewer/` directory
2. Check `cortex-plan-viewer.html` for link pattern
3. Cards use `col-lg-3 col-md-6` for responsive layout
4. All links are relative paths: `./filename.html`
5. Breadcrumbs use: `<a href="cortex-plan-viewer.html">`

### For Maintainers
1. All files in same directory
2. Update dashboard link to add new view
3. Use existing card as template
4. Maintain responsive grid classes
5. Keep phase colors consistent

---

## Summary

**16 Interactive Dashboard Views**  
Organized by 4 Implementation Phases  
Color-Coded for Easy Navigation  
Responsive on All Devices  
Fully Linked from Main Dashboard  
Complete Discovery Interface  

✅ **Ready for Production Use**


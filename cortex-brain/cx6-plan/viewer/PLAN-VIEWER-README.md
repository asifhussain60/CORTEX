# CORTEX 6.0 Plan Viewer - Executive Intelligence Dashboard

## Overview

The CORTEX 6.0 Plan Viewer is a modern, elegant, data-driven execution and architecture intelligence dashboard that provides real-time visibility into the Snowball Implementation strategy and system architecture.

**Philosophy:** This is not a static status page—it's an executive-grade observability tool that shows *what is happening, why, and what's next.*

---

## 🎯 Key Features

### 1. **Real-Time Plan Health Monitoring**
- **Overall Completion Metrics**: Track progress across all 97 AC-IDs
- **Phase-by-Phase Breakdown**: Visual progress for each 4-phase snowball implementation
- **Health Scoring**: Composite metric showing plan health at a glance
- **Status Indicators**: Semantic color coding (green=completed, orange=in-progress, red=blocked, grey=not-started)

### 2. **Interactive Visualizations**
- **AC-ID Status Distribution Chart**: Bar chart showing completed vs. in-progress vs. planned work
- **Phase Completion Trend**: Stacked bar chart comparing progress across all phases
- **Burnup Chart**: Projected vs. actual completion over 8-week timeline (with ideal burnup line)
- **All charts are interactive**: Hover for details, responsive scaling

### 3. **Governance & Rules Enforcement Visibility**
- **19 SKULL Core Rules**: Display all immutable governance rules
- **Rule Priority Levels**: CRITICAL vs. MEDIUM classification
- **Enforcement Status**: Shows which rules are active and blocking operations
- **Expandable Rule Details**: Click to see rule descriptions and enforcement mechanisms

### 4. **Architecture & System Integration Map**
- **Dependency Flows**: Animated flow diagrams showing how phases depend on each other
  - Phase 1: Foundation → Audit → Governance → State → Evidence
  - Phase 2: Request → MasterOrchestrator → TodoManager → Execute
  - Phase 3/4: ADO, Vacuum, Investigation → Core Workflow
- **Component Status Grid**: 12 core subsystems with WIRED/SIMULATED/PLANNED status
- **Integration Visibility**: Shows what's wired, simulated, or missing

### 5. **Active Capabilities Matrix**
- **Infrastructure Foundation**: Audit, Governance, State, Evidence (WIRED)
- **Orchestration Core**: MasterOrchestrator, TodoManager, TDD-Master (SIMULATED)
- **Response Templates**: 3-layer architecture (WIRED)
- **Security & Compliance**: Action classification, approval gates (WIRED)
- **Feature Orchestrators**: ADO, Vacuum, Investigation (PLANNED)
- **Intelligence Layer**: LLM Intent Classifier, Knowledge Practices (PLANNED)

### 6. **Expandable Phase Deep-Dives**
- Click any phase to expand and see:
  - AC-ID completion counts (e.g., "16 of 33 complete")
  - Detailed progress percentage
  - Phase description and dependencies
  - Critical components within the phase

### 7. **Right-Sidebar Metrics Panel**
- **Plan Health Score**: Sticky, always-visible metric
- **Completion Ratio**: Overall implementation percentage
- **Phase Breakdown**: Mini progress bars for each phase
- **Critical Blockers**: Real-time display of blocking issues

---

## 🎨 Design System

### Color Palette
- **Primary Accent**: Cyber-blue (#00d4ff)
- **Semantic Green**: #10b981 (completed)
- **Semantic Orange**: #f59e0b (in-progress)
- **Semantic Red**: #ef4444 (blocked)
- **Semantic Grey**: #6b7280 (not-started)
- **Dark Base**: #0a0e27 to #050814 (gradient background)

### Typography
- **Font Family**: System fonts (-apple-system, Segoe UI, etc.)
- **Sizes**: xs (0.75rem) → 3xl (2rem)
- **Weights**: 400 (normal), 600 (semi-bold), 700 (bold), 800 (extra-bold)

### Layout
- **Two-Column Grid**: Main content (1fr) + sticky sidebar (360px)
- **Responsive**: Collapses to single column on tablets/mobile
- **Spacing System**: xs (0.25rem) → 2xl (3rem)
- **Border Radius**: sm (8px) → lg (16px)

---

## 📊 Visualizations

### D3.js Charts
1. **AC-ID Status Distribution**: Bar chart with value labels
2. **Phase Completion Trend**: Stacked bars (completed + remaining)
3. **Burnup Chart**: Dual-line (actual + ideal) with projected data

### Interactive Elements
- **Collapsible Panels**: Expand/collapse phase details and governance rules
- **Hover Effects**: Tooltips and highlight effects on components
- **Smooth Animations**: Fadeins, transitions, floating animations
- **Responsive Scaling**: Charts resize and reposition for all screen sizes

---

## 📁 File Structure

```
cortex-brain/cx6-plan/viewer/
├── plan-viewer.html              # Main dashboard (this file)
├── plan-viewer-data.json         # Structured plan data
├── shared/
│   └── styles.css               # (Optional) shared styles
└── [other viewers/dashboards]
```

---

## 🚀 Usage

### View in Browser
```bash
cd cortex-brain/cx6-plan/viewer
python -m http.server 8000 --bind 127.0.0.1
# Then open http://127.0.0.1:8000/plan-viewer.html
```

### Data Source
The viewer loads from `plan-viewer-data.json`, which contains:
```json
{
  "plan_metadata": { /* ... */ },
  "phases": [ /* 4 phases with status, AC-IDs, etc. */ ],
  "governance": { /* SKULL rules */ },
  "architecture": { /* subsystems and connections */ },
  "metrics": { /* health scores, blockers, etc. */ }
}
```

### Updating Plan Data
Edit `plan-viewer-data.json` to update:
- AC-ID counts and status
- Phase completion percentages
- Active blockers
- Governance rules
- Architecture components

The viewer will automatically refresh on the next page load.

---

## ✨ Key Interactions

| Action | Result |
|--------|--------|
| Click phase card | Expands to show AC-ID details |
| Click governance rule section | Expands to show all 19 SKULL rules |
| Hover on architecture component | Highlights with glow effect |
| Hover on chart bar | Shows exact values |
| Scroll sidebar | Metrics panel stays visible |
| Resize browser | Layout adapts smoothly |

---

## 🎯 Executive Summary Views

The dashboard answers key executive questions:

1. **"What's our overall progress?"**
   → Health score in top-right sidebar (19% currently)

2. **"Which phase are we in?"**
   → Hero section shows "Phase 1" as active, visual timeline shows all 4 phases

3. **"What's blocking us?"**
   → Bottom of sidebar lists critical blockers
   → Governance rules show enforcement status

4. **"Is the architecture solid?"**
   → Architecture section shows WIRED (active) vs. SIMULATED vs. PLANNED
   → Dependency flows show how components connect

5. **"Will we hit the timeline?"**
   → Burnup chart shows actual vs. projected vs. ideal completion

6. **"What's the governance story?"**
   → 19 SKULL rules shown with priority levels
   → Enforcement mechanisms explained

---

## 🔧 Technical Stack

- **HTML5**: Semantic markup, modern standards
- **CSS3**: Custom properties (CSS variables), Grid, Flexbox, animations
- **D3.js v7**: Interactive data visualizations
- **Vanilla JavaScript**: No frameworks, ~1500 lines of clean, modular code
- **Bootstrap Icons**: For UI elements (optional)

### Performance
- **Load Time**: <500ms (local file)
- **Data Binding**: Real-time updates from JSON
- **Animations**: GPU-accelerated via CSS transforms
- **Responsive**: Works on 320px phones to 4K displays

---

## 🛠️ Customization

### Change Color Scheme
Edit CSS variables at the top of `<style>`:
```css
--color-primary-accent: #00d4ff;     /* Cyber cyan */
--color-completed: #10b981;          /* Green */
--color-in-progress: #f59e0b;        /* Orange */
--color-blocked: #ef4444;            /* Red */
--color-not-started: #6b7280;        /* Grey */
```

### Add New Phases
Update `plan-viewer-data.json`:
```json
{
  "id": 5,
  "name": "Post-Launch Support",
  "completion_percentage": 0,
  "ac_ids_complete": 0,
  "ac_ids_total": 12,
  "status": "blocked_by_phase_4"
}
```

### Add New Governance Rules
Add to the `renderGovernanceRule` calls in `renderGovernanceRules()` method.

---

## 📈 Future Enhancements

- [ ] Real-time data sync from SQL database
- [ ] Historical trend lines (completion over time)
- [ ] Drill-down into individual AC-IDs
- [ ] Audit trail visualization
- [ ] Print-optimized reports
- [ ] Dark/Light theme toggle
- [ ] Export as PDF/SVG
- [ ] Real-time WebSocket updates
- [ ] Gantt chart for timeline visualization
- [ ] Risk assessment overlays

---

## 📝 Notes

### Design Philosophy
This viewer embodies CORTEX's philosophy:
- **Data-Driven**: All metrics tied to real AC-ID completion
- **Transparent**: Governance rules and blockers are visible
- **Actionable**: Shows not just status, but what's next
- **Beautiful**: Dark theme with semantic colors makes insights clear
- **Simple**: No bloat, no excessive frameworks

### Maintenance
- Update `plan-viewer-data.json` whenever AC-ID status changes
- Charts render from JSON data, no hardcoded values
- Collapsible panels work without JavaScript libraries
- All animations are CSS-based for performance

---

## 🎓 Learning Resources

- **D3.js Charts**: Scalable Vector Graphics with data binding
- **CSS Grid**: Responsive layout system without media queries
- **Custom Properties**: Dynamic theming with CSS variables
- **Semantic HTML**: Accessibility-first structure

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-11  
**Author**: CORTEX 6.0 Infrastructure Team

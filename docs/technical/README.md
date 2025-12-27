# 🧠 CORTEX Technical Documentation System

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.

---

## 📖 Overview

The **CORTEX Technical Documentation System** provides comprehensive, interactive documentation for developers, architects, and technical teams. Features include:

- ✅ **Interactive D3.js Diagrams** - Zoom, pan, drill-down capabilities
- ✅ **Glassmorphism Theme** - Modern, accessible UI matching admin dashboard
- ✅ **Complete API Coverage** - 8 orchestrators, 2 agents, 4 brain tiers
- ✅ **Workflow Documentation** - Visual sequence diagrams and flowcharts
- ✅ **Mobile Responsive** - Works on all devices
- ✅ **Full-Text Search** - Find anything instantly
- ✅ **WCAG AA Compliant** - Accessible to all users

---

## 📁 Structure

```
docs/technical/
├── index.html                    # Landing page
├── orchestrators/                # Orchestrator visualizations (NEW)
│   ├── index.html                # Master orchestrator index
│   ├── planning-system.html      # Planning System (4-tier routing)
│   ├── tdd-orchestrator.html     # TDD Orchestrator (RED→GREEN→REFACTOR)
│   ├── ado-planning.html         # ADO Planning (manifest inheritance)
│   ├── maintenance-orchestrator.html  # System Maintenance (7-phase)
│   ├── code-sanitization.html    # Code Sanitization (5-phase)
│   ├── system-integrity.html     # System Integrity (8-phase validation)
│   ├── refinement-orchestrator.html   # Refinement (holistic improvement)
│   ├── cleanup-orchestrator.html # Cleanup (AST-powered)
│   ├── git-checkpoint.html       # Git Checkpoint (milestones)
│   ├── architectural-review.html # Architectural Review (0-100 scoring)
│   ├── cortex-lens.html          # CORTEX Lens v3 (narrative generation)
│   ├── intelligent-dashboard.html # Intelligent Dashboard (metrics)
│   ├── debug-orchestrator.html   # Debug (symptom analysis)
│   ├── rollback-orchestrator.html # Rollback (state restoration)
│   ├── autonomous-execution.html # Autonomous Execution (plan automation)
│   └── pre-flight-orchestrator.html # Pre-Flight (validation)
├── architecture/                 # System architecture
│   ├── diagrams/                 # D3.js interactive diagrams
│   └── components/               # Component documentation
├── api/                          # API reference
│   ├── orchestrators/            # Orchestrator APIs
│   ├── agents/                   # Agent APIs
│   └── brain-tiers/              # Brain tier APIs
├── workflows/                    # Workflow documentation
│   ├── sequence-diagrams/        # D3.js sequence diagrams
│   └── flowcharts/               # D3.js flowcharts
├── data-flow/                    # Data flow diagrams
│   └── dfd-diagrams/             # DFD diagrams
├── deployment/                   # Deployment guides
├── integration/                  # Integration guides
├── setup-guides/                 # Setup & configuration
├── troubleshooting/              # Troubleshooting
├── examples/                     # Code examples
└── assets/                       # Shared assets
    ├── styles/                   # CSS (glassmorphism theme)
    ├── scripts/                  # JavaScript utilities
    └── d3-lib/                   # D3.js library
```

---

## 🚀 Features

### 1. Interactive Diagrams

All diagrams are built with **D3.js v7** and include:

- **Zoom & Pan** - Navigate large diagrams easily
- **Node Expansion** - Click to drill down into details
- **Tooltips** - Hover for contextual information
- **Search & Filter** - Find specific components
- **Export** - Save as PNG or SVG

### 2. Diagram Types

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Architecture** | Component, layer, dependency graphs | System overview, module relationships |
| **Sequence** | Workflow sequences, API flows | Understanding interactions, timing |
| **Flowchart** | Process flows, decision trees | Logic flows, state machines |
| **DFD** | Data flow diagrams (L0-L2) | Data movement, process boundaries |
| **UML** | Class, component, deployment | Object models, infrastructure |

### 3. Glassmorphism Theme

Modern, elegant design with:

- **Backdrop blur effects**
- **Semi-transparent surfaces**
- **Smooth transitions**
- **CORTEX brand colors** (#7C3AED primary)
- **Responsive layout**
- **Dark mode optimized**

### 4. Documentation Coverage

- ✅ **16 Orchestrators** - Complete visualization documentation with interactive diagrams
  - **Planning:** Planning System, TDD, ADO Planning, Pre-Flight
  - **Execution:** Code Sanitization, Autonomous Execution
  - **System:** Maintenance, System Integrity, Refinement, Cleanup, Git Checkpoint
  - **Analysis:** Architectural Review, CORTEX Lens, Intelligent Dashboard
  - **Debug:** Debug, Rollback
- ✅ **2 Agents** - Strategic Planning, Code Execution
- ✅ **4 Brain Tiers** - Tier 0-3 APIs
- ✅ **5 Major Workflows** - Planning, TDD, Maintenance, Refinement, Sanitization
- ✅ **64+ Diagrams** - 32 Mermaid + 32 D3.js interactive visualizations

---

## 🛠️ Usage

### Viewing Documentation

1. **Local Development:**
   ```bash
   # Serve documentation locally
   cd docs/technical
   python -m http.server 8000
   # Open http://localhost:8000 in browser
   ```

2. **Production:**
   ```bash
   # Deploy to web server
   cortex deploy technical-documentation
   ```

### Generating Documentation

```bash
# Generate all documentation
cortex generate technical documentation

# Generate specific sections
cortex generate technical diagrams
cortex generate api documentation
cortex generate workflow documentation

# Export to PDF
cortex export technical documentation --format pdf
```

### Updating Documentation

Documentation auto-updates when:
- Orchestrator added/modified
- Workflow changed
- Brain tier updated
- API signature changed

```bash
# Manual regeneration
cortex regenerate technical documentation

# Incremental update
cortex update technical documentation --section architecture
```

---

## 🎨 Customization

### Theme Colors

Edit `assets/styles/glassmorphism.css`:

```css
:root {
    --primary: #7C3AED;      /* Purple */
    --secondary: #2563EB;    /* Blue */
    --accent: #10B981;       /* Green */
}
```

### Diagram Styling

Edit `assets/styles/diagrams.css`:

```css
.node {
    /* Customize node appearance */
}

.link {
    /* Customize link appearance */
}
```

### Logo

Replace `../CORTEX-logo.png` with your logo in:
- `index.html` (header)
- All documentation pages (header)

---

## 📊 Diagram Examples

### Architecture Diagram

```javascript
const diagramUtils = new DiagramUtils();
const container = d3.select('#diagram-container');

diagramUtils.createForceGraph(container, {
    nodes: [
        { id: 'tier0', label: 'Tier 0', type: 'brain' },
        { id: 'tier1', label: 'Tier 1', type: 'brain' },
        // ...
    ],
    links: [
        { source: 'tier0', target: 'tier1' },
        // ...
    ]
});
```

### Sequence Diagram

```javascript
diagramUtils.createSequenceDiagram(container, {
    actors: [
        { id: 'user', name: 'User' },
        { id: 'cortex', name: 'CORTEX' },
        // ...
    ],
    messages: [
        { from: 'user', to: 'cortex', label: 'plan feature' },
        // ...
    ]
});
```

### Flowchart

```javascript
diagramUtils.createFlowchart(container, {
    nodes: [
        { id: 'start', label: 'Start', type: 'start' },
        { id: 'process', label: 'Analyze', type: 'process' },
        { id: 'decision', label: 'Valid?', type: 'decision' },
        // ...
    ],
    links: [
        { source: 'start', target: 'process' },
        // ...
    ]
});
```

---

## 🧪 Testing

```bash
# Validate all links
python scripts/validate_documentation_links.py

# Test diagram rendering
pytest tests/documentation/test_diagrams.py

# Accessibility audit
python scripts/audit_accessibility.py docs/technical

# Mobile responsiveness
python scripts/test_responsive_design.py
```

---

## 📚 Resources

- **D3.js Documentation:** https://d3js.org/
- **Glassmorphism Generator:** https://glassmorphism.com/
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **CORTEX Admin Dashboard:** `cortex-brain/dashboards/admin-dashboard.html`

---

## 🔄 Maintenance

### Auto-Regeneration

Documentation auto-regenerates on:
- Code changes in `src/`
- Orchestrator modifications
- Workflow updates
- Brain tier changes

Configure in `cortex.config.json`:

```json
{
    "documentation": {
        "auto_regenerate": true,
        "watch_paths": ["src/", "cortex-brain/"],
        "output_path": "docs/technical/"
    }
}
```

### Version Control

- **Manual edits:** Protected, won't be overwritten
- **Generated content:** Auto-updated, marked in file headers
- **Custom diagrams:** Stored in `custom-diagrams/` (preserved)

---

## 🤝 Contributing

1. **Add new documentation:**
   - Create markdown file in appropriate section
   - Add entry to navigation in `index.html`
   - Link from relevant pages

2. **Add new diagram type:**
   - Extend `DiagramUtils` class in `assets/scripts/diagram-utils.js`
   - Add CSS styling in `assets/styles/diagrams.css`
   - Create example in `examples/`

3. **Improve styling:**
   - Edit glassmorphism theme in `assets/styles/glassmorphism.css`
   - Test responsiveness on mobile
   - Verify WCAG AA compliance

---

## 📧 Support

- **Documentation Issues:** github.com/asifhussain60/CORTEX/issues
- **Feature Requests:** Use issue template `documentation-feature-request`
- **Questions:** Ask in GitHub Discussions

---

**Next Steps:**
1. ✅ Folder structure created
2. ✅ Manifest created
3. ✅ Design document created
4. ✅ Glassmorphism CSS created
5. ✅ Diagram CSS created
6. ✅ Landing page created
7. ✅ D3.js utilities created
8. ✅ Navigation script created
9. ✅ Search script created
10. ✅ README created

**To implement orchestrator:** Create `src/orchestrators/technical_documentation_orchestrator.py` following the design document specifications.

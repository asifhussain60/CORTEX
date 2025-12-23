# Architect Agent Guide

**Purpose:** Strategic architectural analysis with automatic brain saving  
**Version:** 1.0  
**Status:** ✅ Production Ready  
**Audience:** CORTEX Users analyzing codebases

---

## Overview

ArchitectAgent performs deep architectural analysis of software systems and automatically saves findings to CORTEX's Tier 2 Knowledge Graph for cross-session memory. It specializes in understanding shell structures, routing systems, view injection patterns, and component interactions.

**Key Capabilities:**
- 🏗️ Shell structure analysis (layout, navigation, panels)
- 🗺️ Routing system mapping (states, URLs, templates)
- 🔍 View injection pattern documentation
- 📁 Feature directory structure analysis
- 🔗 Component interaction flows
- 💾 Automatic brain persistence with namespace detection

---

## Quick Start

### Analyze Application Architecture

```
understand the architecture of KSESSIONS
```

or

```
crawl shell.html to understand KSESSIONS architecture
```

**Result:**
- ✅ Analyzes shell structure
- ✅ Maps routing system
- ✅ Identifies view injection patterns
- ✅ Documents component relationships
- ✅ Saves analysis to brain with namespace `ksessions_architecture`

---

## Usage Scenarios

### Scenario 1: New Codebase Analysis

**User:** "analyze the architecture of this Angular application"

**ArchitectAgent:**
1. Scans workspace for shell files (shell.html, app.component.html)
2. Extracts routing configuration (app-routing.module.ts)
3. Maps component tree structure
4. Identifies state management patterns
5. Saves findings with namespace `angular_app_architecture`

**Output:**
```markdown
# Angular Application Architecture

## Shell Structure
- Main layout: src/app/app.component.html
- Navigation: <app-navbar>, <app-sidebar>
- Content area: <router-outlet>

## Routing System
- 12 routes discovered
- Lazy loading enabled for: Dashboard, Reports, Settings
- Route guards: AuthGuard, RoleGuard

## Component Interaction
- Event bus: RxJS Subject-based messaging
- State management: NgRx store
- Data flow: Unidirectional (parent → child props, child → parent events)

✅ Analysis saved to brain: angular_app_architecture
```

---

### Scenario 2: Understanding Routing Flow

**User:** "explain the routing system in KSESSIONS"

**ArchitectAgent:**
1. Locates routing configuration files
2. Parses route definitions
3. Maps URL patterns to components
4. Identifies navigation flows
5. Documents guard/resolver usage

**Key Insights:**
- Entry points (e.g., `/login`, `/dashboard`)
- Protected routes and authentication requirements
- Lazy-loaded modules for performance
- Navigation patterns (breadcrumbs, tabs, modals)

---

### Scenario 3: View Injection Analysis

**User:** "how does view injection work in this application?"

**ArchitectAgent:**
1. Scans for injection patterns (Angular CDK Portal, React Portal, Vue Teleport)
2. Identifies target containers (e.g., `<div id="modal-root">`)
3. Documents injection mechanisms
4. Maps injection sources to destinations

**Example Finding:**
```
View Injection Pattern: Angular CDK Portal

Sources:
- ModalComponent → ModalService → OverlayContainer
- ToastComponent → ToastService → ToastContainer

Destinations:
- #modal-root (app.component.html)
- #toast-container (app.component.html)

Lifecycle: Components created dynamically, injected at runtime, destroyed on close
```

---

## Integration with CORTEX Workflows

### With Planning System

When planning new features, use ArchitectAgent to understand existing architecture:

```
plan authentication feature
```

CORTEX may suggest: "First, let me analyze your current architecture"

ArchitectAgent automatically runs, saves findings, then planning continues with architectural context.

---

### With TDD Workflow

Before writing tests, understand component structure:

```
start tdd workflow for login component
```

ArchitectAgent analyzes Login component dependencies, inputs/outputs, and saves to brain. TDD workflow then generates tests with full context.

---

## Automatic Brain Saving

**How It Works:**
1. Analysis completes
2. Namespace auto-detected from workspace name (e.g., `ksessions_architecture`)
3. Structured data saved to Tier 2 Knowledge Graph
4. User sees confirmation: "✅ Analysis saved to brain: ksessions_architecture"

**Namespace Examples:**
- `ksessions_architecture` - KSESSIONS project analysis
- `noor_canvas_architecture` - NOOR CANVAS project analysis
- `cortex_architecture` - CORTEX project analysis

**Retrieval:**
```
show context ksessions_architecture
```

Displays saved architectural analysis from previous sessions.

---

## Configuration

**Workspace Detection:**
ArchitectAgent auto-detects workspace from:
1. Current working directory name
2. Git repository name
3. Package.json "name" field
4. .sln file name

**Analysis Depth:**
- **Quick** (default) - Shell + routing only (~2 min)
- **Standard** - Add components + interactions (~5 min)
- **Deep** - Full dependency graph (~10 min)

Set in request context:
```python
request = AgentRequest(
    intent="analyze_architecture",
    context={"analysis_depth": "deep"}
)
```

---

## Output Structure

**Saved to Brain:**
```json
{
  "namespace": "ksessions_architecture",
  "timestamp": "2025-11-25T18:00:00Z",
  "shell_structure": {
    "layout_file": "src/shell.html",
    "navigation_type": "sidebar + topbar",
    "content_areas": ["main-content", "modal-container"]
  },
  "routing": {
    "total_routes": 15,
    "lazy_loaded": ["dashboard", "reports"],
    "guards": ["AuthGuard", "PermissionGuard"]
  },
  "components": [
    {"name": "DashboardComponent", "path": "src/dashboard/"},
    {"name": "LoginComponent", "path": "src/auth/"}
  ],
  "patterns": {
    "view_injection": "Angular CDK Portal",
    "state_management": "NgRx Store",
    "data_flow": "Unidirectional"
  }
}
```

---

## Troubleshooting

### Issue: "No shell file found"

**Solution:** Specify shell file manually:
```
analyze architecture using src/app/app.component.html as shell
```

---

### Issue: "Routing system not detected"

**Cause:** Non-standard routing configuration

**Solution:** Point to routing file:
```
analyze routing from src/app/config/routes.ts
```

---

### Issue: "Analysis not saved to brain"

**Cause:** Tier 2 Knowledge Graph not initialized

**Solution:** Run healthcheck:
```
healthcheck
```

If Tier 2 unhealthy, run:
```
optimize cortex
```

---

## Best Practices

**DO:**
- ✅ Run architect analysis before planning new features
- ✅ Use saved analyses to understand legacy code
- ✅ Review brain-saved architecture when onboarding team members
- ✅ Update analysis after major architectural changes

**DON'T:**
- ❌ Re-run analysis unnecessarily (use cached brain data)
- ❌ Manually create architecture docs (let ArchitectAgent generate)
- ❌ Skip architectural review before TDD workflow

---

## Related Commands

- `show context [namespace]` - View saved architectural analysis
- `plan [feature]` - Planning triggers architecture analysis if needed
- `start tdd` - TDD workflow leverages architectural context
- `optimize` - Clean old architectural analyses from brain

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0  
**Last Updated:** November 25, 2025

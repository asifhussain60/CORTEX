# MkDocs Navigation Organization Guide

**Purpose:** This document explains the navigation structure for CORTEX documentation and how to maintain it.

**Last Updated:** November 17, 2025

---

## Navigation Philosophy

The CORTEX documentation follows a **user-journey-based navigation structure** with 7 main sections:

1. **Home** - Landing page with Sacred Laws and overview
2. **Getting Started** - Quick onboarding for new users
3. **Architecture** - Deep technical understanding
4. **Guides** - How-to documentation for common tasks
5. **Operations** - System operations and workflows
6. **Reference** - API, configuration, and technical references
7. **Story** - Narrative documentation (The Awakening)

---

## Navigation Structure

### 1. Home (`index.md`)

**Purpose:** First impression, Sacred Laws, and quick links

**Content Flow:**
- Sacred Laws of CORTEX (prominent placement)
- Hero section with Get Started / Read Story CTAs
- Core Architecture overview
- Quick Start introduction
- Documentation links

**Key Principles:**
- Sacred Laws MUST be first content (not duplicate hero)
- Hero section comes AFTER Sacred Laws
- Keep concise - deep content belongs in sections

---

### 2. Getting Started

**Purpose:** 5-minute onboarding for new users

**Structure:**
```yaml
- Getting Started:
  - Quick Start: getting-started/quick-start.md
  - Installation: getting-started/installation.md
  - Configuration: getting-started/configuration.md
```

**Guidelines:**
- Maximum 3-4 pages (avoid overwhelming new users)
- Progressive disclosure (start simple, link to deep docs)
- Action-oriented ("How do I...?")

---

### 3. Architecture

**Purpose:** Deep technical understanding of CORTEX design

**Structure:**
```yaml
- Architecture:
  - Overview: architecture/overview.md
  - Tier System: architecture/tier-system.md
  - Agents: architecture/agents.md
  - Brain Protection: architecture/brain-protection.md
  - Diagrams:
    - Module Structure: images/diagrams/architectural/module-structure.md
    - Brain Protection: images/diagrams/architectural/brain-protection.md
    - [More diagrams...]
```

**Guidelines:**
- Core concepts first (Overview, Tier System)
- Specialist topics next (Agents, Brain Protection)
- Diagrams nested under "Diagrams" submenu (avoid top-level clutter)
- Group diagrams by type: Architectural, Strategic, Operational

---

### 4. Guides

**Purpose:** Task-oriented how-to documentation

**Structure:**
```yaml
- Guides:
  - Developer Guide: guides/developer-guide.md
  - Admin Guide: guides/admin-guide.md
  - Best Practices: guides/best-practices.md
  - Troubleshooting: guides/troubleshooting.md
```

**Guidelines:**
- Answer "How do I...?" questions
- Include code examples and commands
- Link to Reference section for API details
- Keep focused (one task per guide)

---

### 5. Operations

**Purpose:** System operations, workflows, and health monitoring

**Structure:**
```yaml
- Operations:
  - Overview: operations/overview.md
  - Entry Point Modules: operations/entry-point-modules.md
  - Workflows: operations/workflows.md
  - Health Monitoring: operations/health-monitoring.md
  - Diagrams:
    - Conversation Flow: images/diagrams/operational/conversation-flow.md
    - Health Check: images/diagrams/operational/health-check.md
    - [More diagrams...]
```

**Guidelines:**
- Focus on runtime operations (not development)
- Include monitoring, debugging, and maintenance
- Nest operational diagrams under "Diagrams"

---

### 6. Reference

**Purpose:** Complete technical reference (API, config, integrations)

**Structure:**
```yaml
- Reference:
  - API Reference: reference/api.md
  - Configuration: reference/configuration.md
  - Response Templates: reference/response-templates.md
  - Integration:
    - Git Integration: images/diagrams/integration/git-integration.md
    - MkDocs Integration: images/diagrams/integration/mkdocs-integration.md
    - VSCode Integration: images/diagrams/integration/vscode-integration.md
  - Performance:
    - CI/CD Integration: performance/CI-CD-INTEGRATION.md
    - Performance Budgets: performance/PERFORMANCE-BUDGETS.md
    - Telemetry Guide: telemetry/PERFORMANCE-TELEMETRY-GUIDE.md
```

**Guidelines:**
- Complete, searchable reference material
- Alphabetical or logical grouping
- Group integrations and performance docs in submenus

---

### 7. Story

**Purpose:** Narrative documentation (The Awakening of CORTEX)

**Structure:**
```yaml
- Story:
  - The Awakening of CORTEX: awakening-of-cortex.md
  - The CORTEX Story: diagrams/story/The-CORTEX-Story.md
```

**Guidelines:**
- Narrative-style documentation
- Blend storytelling with technical content
- Educational and inspirational
- Keep separate from technical docs

---

## What NOT to Include in Navigation

### Auto-Generated Reports

❌ **Don't add generation reports to navigation:**
- `GENERATION-REPORT-*.md` files should be in `docs/generated/reports/`
- Not user-facing documentation
- Create clutter (20+ files)

**Storage Location:** `docs/generated/reports/`

**Access:** Via file browser only (not navigation)

---

### Duplicate Sections

❌ **Avoid these navigation anti-patterns:**

1. **Duplicate sections** (e.g., "Architectural" AND "Architecture")
   - Consolidate into single "Architecture" section
   
2. **"Generated" top-level menu**
   - Generated content should be in appropriate sections
   - Example: `generated/architecture-overview.md` → Keep, but link from `architecture/overview.md`
   
3. **Per-diagram top-level menus** (e.g., "Strategic", "Operational")
   - Nest under parent sections (Architecture, Operations)
   - Use "Diagrams" submenu

4. **Redundant standalone files**
   - `HELP-SYSTEM.md`, `Technical-Cost-Optimization.md` → Move to appropriate section or remove from nav

---

## Navigation Maintenance

### Adding New Pages

1. **Identify correct section** (Getting Started, Architecture, Guides, etc.)
2. **Add to appropriate submenu** (avoid top-level unless major section)
3. **Use descriptive titles** (not filenames)
4. **Maintain logical order** (most important first)

**Example:**
```yaml
# Good
- Architecture:
  - Overview: architecture/overview.md
  - NEW: architecture/new-concept.md  # Add after Overview

# Bad
- New Concept: architecture/new-concept.md  # Don't create top-level menu
```

---

### Removing Pages

1. **Check for broken links** (MkDocs build will warn)
2. **Update related pages** that reference removed page
3. **Archive if needed** (move to `docs/archives/` directory)

---

### Reorganizing Navigation

**Before reorganizing:**
1. Document current structure
2. Test build (`mkdocs build --clean`)
3. Check for broken links
4. Commit changes incrementally

**After reorganizing:**
1. Rebuild site (`mkdocs build --clean`)
2. Test navigation in browser
3. Validate all links work
4. Update this guide if structure changes

---

## MkDocs Configuration

### Location

`/Users/asifhussain/PROJECTS/CORTEX/mkdocs.yml`

### Key Settings

```yaml
# Navigation structure
nav:
  - Home: index.md
  - Getting Started:
      - Quick Start: getting-started/quick-start.md
      # ...

# Theme features (controls navigation behavior)
theme:
  features:
    - navigation.instant     # SPA-like navigation
    - navigation.tracking    # URL updates on scroll
    - navigation.tabs        # Top-level tabs
    - navigation.sections    # Collapsible sections
    - navigation.expand      # Auto-expand sections
    - navigation.top         # Back-to-top button
    # NOTE: toc.integrate removed (caused sidebar overlap issue)
```

---

## Common Issues & Solutions

### Issue 1: Too Many Top-Level Menus

**Symptom:** Navigation sidebar is cluttered with 20+ top-level items

**Solution:**
1. Consolidate related pages into logical sections
2. Use submenus for groups (e.g., "Diagrams" under "Architecture")
3. Move non-user-facing content out of navigation

---

### Issue 2: Duplicate Hero Section on Home Page

**Symptom:** Home page shows hero section twice

**Solution:**
1. Ensure `docs/index.md` starts with Sacred Laws section
2. Hero section should come AFTER Sacred Laws
3. Only ONE hero section per page

---

### Issue 3: Sidebar Overlaps Content

**Symptom:** Navigation sidebar covers main content on certain pages

**Solution:**
1. Remove `toc.integrate` from mkdocs.yml features
2. Ensure CSS z-index is set correctly (sidebar: 3, content: 1)
3. Test responsive breakpoints (mobile/tablet)

**CSS Fix:**
```css
.md-sidebar--primary {
  z-index: 3 !important;
}

.md-content {
  z-index: 1 !important;
}
```

---

## Testing Navigation Changes

### Build & Serve

```bash
# Clean build
python3 -m mkdocs build --clean

# Serve locally
python3 -m mkdocs serve

# Open browser
http://127.0.0.1:8000
```

### Validation Checklist

- [ ] Navigation has 7-8 top-level sections (not 20+)
- [ ] Home page shows Sacred Laws first
- [ ] No duplicate menus (Architectural + Architecture)
- [ ] Diagrams nested under parent sections
- [ ] No generation reports in navigation
- [ ] Sidebar doesn't overlap content
- [ ] Mobile navigation works (hamburger menu)
- [ ] All links resolve (check build warnings)

---

## Navigation Philosophy Summary

**Goal:** User-journey-based structure that guides users from onboarding → understanding → doing → reference

**Principles:**
1. **Progressive disclosure** - Start simple, provide depth on demand
2. **Logical grouping** - Related content stays together
3. **Minimal top-level** - 7-8 sections maximum
4. **Nested complexity** - Use submenus for specialized content
5. **User-facing only** - Internal/generated docs stay out of nav

**Result:** Clean, intuitive navigation that scales with documentation growth

---

**Maintained by:** CORTEX Documentation Team  
**Contact:** github.com/asifhussain60/CORTEX

# MkDocs Orchestrator Guide

**Purpose:** Enterprise documentation generation orchestrator for CORTEX using MkDocs framework.

**Version:** 1.0 | **Author:** Asif Hussain | **Copyright:** © 2024-2025 | **Status:** ✅ PRODUCTION

## 🎯 Overview

MkDocsOrchestrator generates comprehensive documentation websites from CORTEX source code, markdown files, and docstrings. Creates searchable, navigable documentation with diagrams, API references, and guides.

### Key Features:
- **Auto-Generation** - Extracts docs from code, markdown, YAML configs
- **Rich Content** - Diagrams (Mermaid), tables, code examples
- **Search Integration** - Full-text search across all documentation
- **Multi-Format** - HTML site, PDF export, offline viewing

## 🏗️ Architecture

```
CORTEX Documentation Pipeline
├── Source Collection
│   ├── Python docstrings → API Reference
│   ├── Markdown files → User Guides
│   ├── YAML configs → Configuration Docs
│   └── Code examples → Tutorials
├── Processing
│   ├── MkDocs Material theme
│   ├── Mermaid diagram rendering
│   ├── Syntax highlighting
│   └── Search indexing
└── Output
    ├── docs/ → Markdown sources
    ├── site/ → Built HTML site
    ├── search_index.json → Search data
    └── PDF export (optional)
```

## 🔧 Implementation

### Core Operations

**generate_docs():**
- Scans `src/` for Python modules
- Extracts docstrings and type hints
- Creates API reference pages
- Generates module hierarchy

**build_site():**
- Runs `mkdocs build`
- Compiles markdown to HTML
- Applies Material theme
- Creates search index

**serve_locally():**
- Runs `mkdocs serve`
- Live preview at `localhost:8000`
- Auto-reload on file changes
- Hot module replacement

**deploy_to_pages():**
- Builds site for production
- Deploys to GitHub Pages
- Updates `gh-pages` branch
- Accessible at `https://asifhussain60.github.io/CORTEX`

## 🎯 Usage Examples

### Generate Documentation

```python
from src.operations.modules.mkdocs_orchestrator import MkDocsOrchestrator

# Initialize orchestrator
orchestrator = MkDocsOrchestrator()

# Generate full documentation
result = orchestrator.execute({
    "operation": "generate",
    "include_api": True,
    "include_diagrams": True
})

# Output:
# {
#     "success": True,
#     "pages_generated": 147,
#     "diagrams_rendered": 23,
#     "output_dir": "site/"
# }
```

### Live Preview

```python
# Start local server for development
orchestrator = MkDocsOrchestrator()

result = orchestrator.execute({
    "operation": "serve",
    "port": 8000,
    "watch": True
})

# Visit: http://localhost:8000
```

### Deploy to GitHub Pages

```python
# Publish documentation to GitHub Pages
orchestrator = MkDocsOrchestrator()

result = orchestrator.execute({
    "operation": "deploy",
    "branch": "gh-pages",
    "clean": True
})
```

## 📚 Documentation Structure

```
docs/
├── index.md                    # Homepage
├── guides/
│   ├── getting-started.md
│   ├── installation.md
│   └── tutorials.md
├── reference/
│   ├── agents/                 # Agent API docs
│   ├── orchestrators/          # Orchestrator API docs
│   └── utilities/              # Utility API docs
├── architecture/
│   ├── overview.md
│   ├── brain-tiers.md
│   └── agent-system.md
└── contributing/
    ├── development.md
    └── testing.md
```

## 🎨 Theme Customization

### Material Theme Features
- **Dark/Light Mode** - User preference toggle
- **Search** - Instant search across all docs
- **Navigation** - Hierarchical sidebar
- **Mobile Responsive** - Works on all devices
- **Code Highlighting** - Syntax coloring for 100+ languages

### Custom Styling
- CORTEX branding colors
- Custom fonts (Roboto, Roboto Mono)
- Icon integration
- Responsive tables

## 📊 Performance

### Build Times
- **Incremental Build:** ~5 seconds (changed pages only)
- **Full Build:** ~45 seconds (all 147 pages)
- **Diagram Rendering:** ~2 seconds per diagram
- **Search Indexing:** ~8 seconds

### Output Size
- **HTML Site:** 8.2 MB
- **Search Index:** 1.1 MB
- **Assets (CSS/JS):** 412 KB
- **Total:** ~9.7 MB

## �� Related Components

- **DocumentationIntelligenceSystem** - Auto-updates docs from code changes
- **EnterpriseDocOrchestrator** - Comprehensive doc generation
- **VisualAssetGenerator** - Creates diagrams for documentation

## 🎯 Summary

**MkDocsOrchestrator generates enterprise-grade documentation with auto-extraction, rich formatting, and deployment automation. Essential for maintaining CORTEX documentation quality.**

---
**Version:** 1.0 | **Updated:** November 25, 2025 | **Repository:** https://github.com/asifhussain60/CORTEX

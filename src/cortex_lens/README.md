# CORTEX Lens - Universal Repository Intelligence Platform

**Version:** 1.0.0 (Phase 0 - Foundation)  
**Author:** Asif Hussain  
**Status:** 🚧 IN DEVELOPMENT

---

## 🎯 Overview

CORTEX Lens is a **self-contained, universal repository analyzer** that scans any codebase (full-stack, API, database, console app, microservices, libraries) and generates **adaptive static dashboards** tailored to the repository's nature.

### Key Features

✅ **Universal Analysis** - Auto-detect 6 repo types  
✅ **Adaptive Dashboards** - Generate appropriate views based on repo characteristics  
✅ **Self-Contained** - Zero cross-repo dependencies  
✅ **Multi-Language Support** - Python, C#, JavaScript, TypeScript, SQL  
✅ **Static Deployment** - Works offline, zero configuration  
✅ **Multi-Format Export** - HTML, JSON, YAML, CSV  
✅ **Comparison Mode** - Compare repos, track evolution  
✅ **Modern Dependencies** - No deprecated libraries (pypdf, parso, tomli)

---

## 📦 Installation

### Requirements

- Python 3.8 - 3.14+
- All dependencies are pure Python (no compilation required)

### Install Dependencies

```bash
# From src/cortex_lens directory
pip install -r requirements.txt

# With optional features (advanced analysis)
pip install -r requirements.txt libcst ruff
```

---

## 🚀 Quick Start

### Python API

```python
from cortex_lens import CortexLens

# Analyze repository
lens = CortexLens()
result = lens.analyze('/path/to/repo')

print(f"Dashboard: {result['dashboard_path']}")
print(f"Type: {result['classification']['primary_type']}")
```

### Command Line

```bash
# Analyze repository
python -m cortex_lens analyze /path/to/repo

# Quick scan (classification only)
python -m cortex_lens scan /path/to/repo

# List available templates
python -m cortex_lens templates

# Compare multiple repos
python -m cortex_lens compare /repo1 /repo2 /repo3

# Export in multiple formats
python -m cortex_lens analyze /path/to/repo --format json yaml csv
```

---

## 🏗️ Architecture

```
src/cortex_lens/
├── orchestrator.py          # Main entry point (CortexLens class)
├── cli.py                   # Command-line interface
├── requirements.txt         # Modern dependencies
│
├── core/                    # Core framework
│   ├── classifier.py        # Repository type detection
│   ├── pipeline.py          # Data collection orchestration
│   └── schema.py            # Universal JSON schema
│
├── analyzers/               # Language-specific AST analysis
│   ├── base.py              # BaseAnalyzer protocol
│   ├── python_analyzer.py   # Multi-engine (ast → parso → libcst)
│   ├── csharp_analyzer.py   # C# analysis
│   ├── javascript_analyzer.py # JS/TS analysis
│   └── registry.py          # Analyzer plugin registry
│
├── collectors/              # Data collectors
│   ├── base.py              # BaseCollector protocol
│   ├── health_collector.py  # File count, LOC, languages
│   ├── architecture_collector.py # Layer detection
│   └── registry.py          # Collector execution matrix
│
├── generators/              # Dashboard generation
│   ├── base.py              # BaseGenerator protocol
│   ├── narrative_generator.py # Business narratives
│   ├── dashboard_builder.py # Template engine
│   └── packager.py          # Distribution packaging
│
├── templates/               # Dashboard templates
│   ├── base/                # Shared components
│   ├── fullstack_web/       # Full-stack template
│   ├── api_service/         # API service template
│   └── ...                  # Other templates
│
└── validators/              # Data validation
    ├── schema_validator.py  # JSON schema validation
    └── reconciliation_validator.py # CVSS/OWASP compliance
```

---

## 📊 Supported Repository Types

| Type | Description | Template |
|------|-------------|----------|
| **fullstack_web** | Frontend + Backend + Database | 7 tabs (executive, frontend, backend, database, integration, security, tech-stack) |
| **api_service** | REST/GraphQL endpoints | 6 tabs (executive, endpoints, auth, performance, dependencies, security) |
| **database_project** | Schema, migrations, procedures | 5 tabs (executive, schema ERD, procedures, performance, migrations) |
| **console_app** | CLI commands, workflows | 5 tabs (executive, commands, workflows, config, dependencies) |
| **microservices** | Distributed services, messaging | 7 tabs (executive, topology, messaging, containers, api-gateway, resilience, monitoring) |
| **library_package** | Exported APIs, documentation | 5 tabs (getting-started, api-reference, examples, architecture, changelog) |

---

## 🔧 Development Status

### ✅ Phase 0: Foundation (COMPLETE)

- [x] Directory structure created
- [x] Base classes (BaseAnalyzer, BaseCollector, BaseGenerator)
- [x] Core framework (classifier, pipeline, schema)
- [x] CLI interface
- [x] Modern dependencies (parso, pypdf, tomli)
- [x] Plugin architecture

### 🚧 Phase 1: First Vertical Slice (IN PROGRESS)

- [ ] Python analyzer (multi-engine: ast → parso → libcst)
- [ ] 4 core collectors (health, architecture, API, comments)
- [ ] API Service template
- [ ] End-to-end workflow
- [ ] Basic unit tests

### 📅 Phase 2-6: Full Implementation (PLANNED)

- Phase 2: Multi-language support (C#, JS, SQL)
- Phase 3: Extended collectors (14+ collectors)
- Phase 4: 6 dashboard templates
- Phase 5: Narrative & validation
- Phase 6: Testing & optimization

---

## 🧬 Multi-Engine AST Parsing

CORTEX Lens uses a **cascading parser strategy** for maximum reliability:

1. **Python `ast`** (Primary) - Stdlib, fast, perfect for valid code
2. **Parso** (Fallback) - Error recovery, handles broken/incomplete code
3. **LibCST** (Advanced) - Whitespace-preserving, metadata analysis
4. **Ruff** (Optional) - Fast linting, security checks

**Parse Success Rate:** 99%+ (ast: 85% → parso: 98% → libcst: 99.9%)

### Why NOT tree-sitter?

❌ Binary compilation issues  
❌ Python binding compatibility breaks  
❌ Complex multi-language setup  
✅ Pure Python alternatives are more reliable

---

## 📦 Dependencies

### Core (Always Required)

```
parso>=0.8.5       # Error-recovery parser (587k+ users)
sqlparse>=0.5.0    # SQL parsing (15+ years)
pypdf>=6.4.1       # PDF extraction (replaces deprecated PyPDF2)
tomli>=2.0.0       # TOML parsing (Python <3.11)
pytest>=8.4.0      # Testing framework
playwright>=1.48.0 # Browser automation
pyyaml>=6.0.2      # YAML export
Jinja2>=3.1.4      # Template engine
```

### Optional (Enhanced Features)

```
libcst>=1.4.0      # Advanced Python refactoring (Meta/Instagram)
ruff>=0.8.0        # Fast linting (44.4k ⭐, 10-100x faster)
pythonnet>=3.0.0   # C# Roslyn integration
pymupdf>=1.26.7    # Advanced PDF (5-10x faster, OCR)
```

### Removed (Deprecated)

```
❌ tree-sitter*    # Compilation issues → parso/libcst
❌ PyPDF2          # Deprecated → pypdf
❌ toml            # Deprecated → tomli
```

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src/cortex_lens tests/

# Verbose
pytest -v tests/
```

---

## 📚 Documentation

- **Plan:** [cortex-lens-plan-v2.md](../../cortex-brain/documents/planning/cortex-lens-plan-v2.md)
- **API Reference:** Coming in Phase 6
- **User Guide:** Coming in Phase 6
- **Developer Guide:** Coming in Phase 6

---

## 🤝 Contributing

CORTEX Lens is part of the CORTEX project. See main CORTEX documentation for contribution guidelines.

---

## 📄 License

Copyright © 2025 Asif Hussain. All rights reserved.

---

## 🔗 Related Projects

- **CORTEX** - Main project
- **CORTEX Universal Design System** - Centralized glassmorphism styling
- **Planning System 2.0** - Feature planning framework

---

**Status:** Phase 0 Foundation Complete ✅ | Phase 1 In Progress 🚧

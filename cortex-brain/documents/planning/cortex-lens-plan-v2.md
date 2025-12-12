# CORTEX Lens - Universal Repository Intelligence Platform

**Version:** 2.1 🆕  
**Date:** December 12, 2025  
**Author:** Asif Hussain  
**Status:** 🎯 READY FOR IMPLEMENTATION

**Updates:**
- **v2.1** - Integrated CORTEX Universal Design System for centralized glassmorphism styling
- **v2.0** - Initial universal repository analyzer architecture

---

## 🎯 Executive Summary

CORTEX Lens is a **self-contained, universal repository analyzer** that scans any codebase (full-stack, API, database, console app, microservices, libraries) and generates **adaptive static dashboards** tailored to the repository's nature. Built as a modular, extensible platform with zero external dependencies, consuming **centralized glassmorphism styling** from the CORTEX Universal Design System.

**Transformation:** From unified dashboard merger → Universal repository intelligence tool → Integrated with centralized design system 🆕

**Key Goals:**
1. **Universal Analysis** - Scan any repo type and auto-detect architecture patterns
2. **Adaptive Dashboards** - Generate appropriate views based on repo characteristics (6 templates)
3. **Self-Contained** - All functionality in `src/cortex_lens/` with zero cross-repo dependencies
4. **Extensible Architecture** - Plugin system for analyzers, collectors, and templates
5. **Multi-Language Support** - Python, C#, JavaScript, TypeScript, SQL via native parsers
6. **Static Deployment** - Zero configuration, works offline, double-click to open
7. **Centralized Design System** 🆕 - Consume glassmorphism styling from `cortex-brain/design-system/`

**Success Metrics:**
- ✅ Auto-detect 6 repo types (full-stack, API, database, console, microservices, library)
- ✅ 90%+ classification accuracy across diverse codebases
- ✅ Generate adaptive dashboards in <2 minutes for 10K LOC repos
- ✅ 100% static deployment (no Python server required)
- ✅ Plugin architecture with 14+ collectors and 4+ analyzers
- ✅ <3 second dashboard load time for all templates
- ✅ Zero CSS duplication - all styling from central source 🆕
- ✅ Design updates propagate automatically via publish engine 🆕

---

## 📊 Problem Statement

### The Challenge: Repository Diversity

Organizations have diverse codebases requiring different analysis approaches:

| Repository Type | Key Characteristics | Analysis Needs |
|----------------|---------------------|----------------|
| **Full-Stack Web** | Frontend + Backend + Database | API mapping, UI routing, data flow |
| **API Service** | REST/GraphQL endpoints | Endpoint catalog, auth patterns, performance |
| **Database Project** | Schema, migrations, procedures | ERD visualization, query analysis, indexes |
| **Console App** | CLI commands, workflows | Command catalog, execution flows, config |
| **Microservices** | Distributed services, messaging | Service topology, event bus, resilience |
| **Library/Package** | Exported APIs, examples | Public API reference, usage examples |

**Current Limitations:**
- Admin Dashboard: Fixed 10-tab layout (doesn't adapt to repo type)
- RA Toolkit: Domain-specific (not generalized)
- Scattered collectors: 18+ collectors spread across `src/`, `scripts/`, `cortex-brain/`
- External dependencies: Relies on existing orchestrators, utilities, brain modules
- Python-only analysis: Limited multi-language support

### The Solution: CORTEX Lens

**Self-Contained Universal Analyzer** with three core capabilities:

1. **Auto-Classification**
   - Scan repository file patterns
   - Detect architecture (layers, frameworks, patterns)
   - Assign confidence score (0-100%)
   - Select appropriate dashboard template

2. **Adaptive Data Collection**
   - Execute collectors based on repo type
   - 14+ specialized collectors (health, architecture, security, API endpoints, etc.)
   - Standardized JSON schema across all repo types
   - Native Python AST + regex for C#/JavaScript

3. **Template-Based Dashboard Generation**
   - 6 dashboard templates (one per repo type)
   - Shared glassmorphism UI components
   - D3.js visualizations (force graphs, trees, scatter plots)
   - Static HTML/CSS/JS (works offline)

**Architecture Principle:** All functionality in `src/cortex_lens/` - zero imports from other CORTEX modules

---

## 🏗️ CORTEX Lens Architecture

### Self-Contained Module Structure

```
src/
└── cortex_lens/                           # 🎯 ALL LENS CODE HERE (~10,000 LOC)
    ├── __init__.py                        # Public API (CortexLens, registries)
    ├── orchestrator.py                    # Main entry point (250 LOC)
    ├── cli.py                             # CLI wrapper (100 LOC)
    │
    ├── core/                              # Core framework (800 LOC)
    │   ├── __init__.py
    │   ├── classifier.py                  # Repo type detection (400 LOC)
    │   ├── pipeline.py                    # Data collection orchestration (300 LOC)
    │   └── schema.py                      # Universal JSON schema (100 LOC)
    │
    ├── analyzers/                         # AST & pattern analysis (1,200 LOC)
    │   ├── __init__.py
    │   ├── base.py                        # BaseAnalyzer protocol (100 LOC)
    │   ├── python_analyzer.py             # Native ast (300 LOC)
    │   ├── csharp_analyzer.py             # Regex-based (400 LOC)
    │   ├── javascript_analyzer.py         # Regex patterns (250 LOC)
    │   ├── sql_analyzer.py                # SQL parsing (150 LOC)
    │   └── registry.py                    # Plugin registry (100 LOC)
    │
    ├── collectors/                        # Data collectors (2,400 LOC)
    │   ├── __init__.py
    │   ├── base.py                        # BaseCollector protocol (100 LOC)
    │   ├── health_collector.py            # File count, LOC, languages (150 LOC)
    │   ├── architecture_collector.py      # Layer detection (200 LOC)
    │   ├── security_collector.py          # OWASP, vulnerabilities (250 LOC)
    │   ├── tech_stack_collector.py        # Technology inventory (200 LOC)
    │   ├── api_endpoint_collector.py      # REST API catalog (200 LOC)
    │   ├── database_schema_collector.py   # Tables, views, procedures (200 LOC)
    │   ├── frontend_routes_collector.py   # React/Vue/Angular routes (150 LOC)
    │   ├── dependency_collector.py        # NuGet/NPM packages (150 LOC)
    │   ├── complexity_collector.py        # Cyclomatic complexity (150 LOC)
    │   ├── test_coverage_collector.py     # Coverage by layer (150 LOC)
    │   ├── comment_collector.py           # Comment extraction (200 LOC)
    │   ├── performance_collector.py       # Hot paths, slow queries (150 LOC)
    │   ├── compliance_collector.py        # Regulatory keywords (150 LOC)
    │   └── registry.py                    # Collector matrix (150 LOC)
    │
    ├── generators/                        # Dashboard generation (1,000 LOC)
    │   ├── __init__.py
    │   ├── base.py                        # BaseGenerator protocol (100 LOC)
    │   ├── narrative_generator.py         # AST-to-Narrative (300 LOC)
    │   ├── dashboard_builder.py           # Template engine (400 LOC)
    │   ├── data_injector.py               # JSON injection (150 LOC)
    │   └── packager.py                    # Distribution ZIP (150 LOC)
    │
    ├── templates/                         # Dashboard templates (3,000 LOC)
    │   ├── base/                          # Shared components
    │   │   ├── cortex-unified.css         # Glassmorphism (500 LOC)
    │   │   ├── cortex-unified.js          # Core framework (400 LOC)
    │   │   └── components/
    │   │       ├── narrative-panel.js     # Collapsible narrative (200 LOC)
    │   │       ├── reconciliation-widget.js # Validation (250 LOC)
    │   │       ├── d3-force-graph.js      # Force-directed graph (300 LOC)
    │   │       └── kpi-scorecard.js       # Metrics display (150 LOC)
    │   │
    │   ├── fullstack_web/                 # Full-stack app template
    │   │   ├── manifest.json              # Tab configuration
    │   │   ├── index.html                 # Main dashboard
    │   │   └── tabs/                      # 7 tabs
    │   │
    │   ├── api_service/                   # API-focused template
    │   ├── database_project/              # Database template
    │   ├── console_app/                   # Console app template
    │   ├── microservices/                 # Microservices template
    │   └── library_package/               # Library documentation template
    │
    ├── validators/                        # Data validation (400 LOC)
    │   ├── __init__.py
    │   ├── schema_validator.py            # JSON schema validation (200 LOC)
    │   └── reconciliation_validator.py    # CVSS/OWASP compliance (200 LOC)
    │
    ├── utils/                             # Utilities (600 LOC)
    │   ├── __init__.py
    │   ├── file_scanner.py                # Directory traversal (150 LOC)
    │   ├── git_analyzer.py                # Git blame, ownership (200 LOC)
    │   ├── pattern_matcher.py             # Regex utilities (100 LOC)
    │   └── logger.py                      # Lens logging (150 LOC)
    │
    └── config/                            # Configuration (200 LOC)
        ├── __init__.py
        ├── defaults.py                    # Default settings (100 LOC)
        └── schemas.json                   # Universal schema (100 LOC)
```

**Total LOC:** ~10,000 (self-contained, no external dependencies)

**Output Structure** (Generated per repository):
```
cortex-lens-output/{repo-name}/
├── index.html                          # Dashboard entry point
├── assets/                             # CSS, JS, images
├── tabs/                               # Tab-specific modules
├── components/                         # Shared UI components
├── lib/                                # D3.js, Chart.js
└── data/
    ├── metadata.json
    ├── classification.json
    ├── architecture.json
    ├── ast-analysis.json
    ├── comment-extraction.json
    ├── narrative.md
    └── [other collector outputs]
```

---

## 🔌 Plugin Architecture

### 1. Repository Type Classifier

**File:** `src/cortex_lens/core/classifier.py`

Detects repository type through file pattern analysis + AST validation.

**6 Supported Patterns:**

| Pattern | Indicators | Confidence Threshold | Dashboard Template |
|---------|-----------|---------------------|-------------------|
| `fullstack_web` | Frontend (package.json, React), Backend (Controllers, API), Database (migrations, DbContext) | 70% (2/3 layers) | fullstack-web-dashboard |
| `api_service` | Controllers, routes, Swagger/OpenAPI | 60% | api-service-dashboard |
| `database_project` | .sql files, migrations, DbContext | 50% | database-schema-dashboard |
| `console_app` | Program.cs/main, CLI parsers, NO web components | 60% | console-app-dashboard |
| `microservices` | Docker, K8s, messaging (RabbitMQ/Kafka), API Gateway | 50% | microservices-dashboard |
| `library_package` | Package manifest, NO application entry point, exports | 60% | library-documentation-dashboard |

**Output:**
```json
{
  "primary_type": "fullstack_web",
  "secondary_types": ["api_service"],
  "confidence_scores": {
    "fullstack_web": 0.85,
    "api_service": 0.65
  },
  "dashboard_template": "fullstack-web-dashboard",
  "detected_patterns": {
    "has_frontend": true,
    "has_backend": true,
    "has_database": true,
    "has_messaging": false,
    "has_containerization": true
  }
}
```

### 2. Analyzer Registry (Extensible)

**File:** `src/cortex_lens/analyzers/registry.py`

Central registry for language analyzers with plugin support.

**Built-in Analyzers:**
- `PythonAnalyzer` - Native Python `ast` module (all Python versions)
- `CSharpAnalyzer` - Regex-based (classes, methods, controllers, API endpoints)
- `JavaScriptAnalyzer` - Regex patterns (React components, routes, exports)
- `SQLAnalyzer` - SQL parsing (tables, views, procedures, indexes)

**Adding Custom Analyzer:**
```python
from cortex_lens.analyzers import AnalyzerRegistry, BaseAnalyzer

class RustAnalyzer(BaseAnalyzer):
    SUPPORTED_EXTENSIONS = {'.rs'}
    
    def analyze(self, file_path):
        # Custom analysis logic
        return {...}

# Register plugin
AnalyzerRegistry.register('rust', RustAnalyzer)
```

### 3. Collector Registry (Extensible)

**File:** `src/cortex_lens/collectors/registry.py`

Executes collectors based on repo type classification.

**Collector Execution Matrix:**

| Collector | Full-Stack | API | Database | Console | Microservices | Library |
|-----------|-----------|-----|----------|---------|---------------|---------|
| health | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| architecture | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| security | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| api_endpoint | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ |
| database_schema | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| frontend_routes | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| messaging_topology | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| cli_commands | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| public_api | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Adding Custom Collector:**
```python
from cortex_lens.collectors import CollectorRegistry, BaseCollector

class GraphQLCollector(BaseCollector):
    def collect(self, repo_path, classification):
        # Custom collection logic
        return {...}

# Register plugin
CollectorRegistry.register('graphql_schema', GraphQLCollector)

# Update execution matrix
CollectorRegistry.EXECUTION_MATRIX['api_service'].append('graphql_schema')
```

### 4. Template Registry (Extensible)

**File:** `src/cortex_lens/templates/__init__.py`

Maps repo types to dashboard templates.

**6 Built-in Templates:**
1. `fullstack_web` - 7 tabs (executive, frontend, backend, database, integration, security, tech-stack)
2. `api_service` - 6 tabs (executive, endpoints, authentication, performance, dependencies, security)
3. `database_project` - 5 tabs (executive, schema ERD, procedures, performance, migrations)
4. `console_app` - 5 tabs (executive, commands, workflows, configuration, dependencies)
5. `microservices` - 7 tabs (executive, topology, messaging, containers, api-gateway, resilience, monitoring)
6. `library_package` - 5 tabs (getting-started, api-reference, examples, architecture, changelog)

**Adding Custom Template:**
```
src/cortex_lens/templates/custom_template/
├── manifest.json           # Tab configuration
├── index.html             # Main dashboard
└── tabs/
    ├── tab1.js
    └── tab2.js
```

---

## 📦 Universal JSON Schema

**File:** `src/cortex_lens/config/schemas.json`

Standardized data structure across all repo types.

```json
{
  "metadata": {
    "repo_name": "string",
    "repo_type": ["fullstack_web", "api_service"],
    "scan_timestamp": "ISO8601",
    "cortex_version": "3.8.1",
    "languages": {"csharp": 65.2, "javascript": 25.3, "sql": 9.5},
    "total_files": 1247,
    "total_loc": 45823
  },
  
  "classification": {
    "primary_type": "fullstack_web",
    "confidence": 0.85,
    "detected_patterns": {
      "has_frontend": true,
      "has_backend": true,
      "has_database": true
    }
  },
  
  "architecture": {
    "layers": [
      {
        "name": "Frontend",
        "path": "src/web/",
        "tech_stack": ["React", "Redux", "TypeScript"],
        "entry_points": ["src/web/index.tsx"],
        "file_count": 342,
        "loc": 18234
      }
    ],
    "dependencies": [
      {"from": "Frontend", "to": "Backend API", "type": "HTTP", "endpoint_count": 47}
    ]
  },
  
  "entities": {
    "api_endpoints": [...],
    "database_tables": [...],
    "frontend_routes": [...],
    "classes": [...],
    "methods": [...]
  },
  
  "metrics": {
    "complexity": {...},
    "test_coverage": {...},
    "performance": {...}
  },
  
  "security": {
    "vulnerabilities": [...],
    "authentication_patterns": ["JWT", "OAuth2"]
  },
  
  "comments": {
    "extraction": [...],
    "regulatory_keywords": [...]
  },
  
  "narrative": {
    "executive_summary": "string",
    "key_capabilities": [...],
    "technical_highlights": [...]
  }
}
```

---

## 🚀 Main Orchestrator (Entry Point)

**File:** `src/cortex_lens/orchestrator.py`

```python
"""
CORTEX Lens Orchestrator - Universal Repository Intelligence

Usage:
    from cortex_lens import CortexLens
    
    lens = CortexLens()
    result = lens.analyze('/path/to/repo')
"""

class CortexLens:
    """Single entry point for all Lens functionality."""
    
    def analyze(self, repo_path, output_dir=None, template=None):
        """
        6-Phase Analysis Workflow:
        
        Phase 1: Repository Classification
        Phase 2: Data Collection (14+ collectors)
        Phase 3: Narrative Generation (AST-to-Narrative)
        Phase 4: Dashboard Generation (template-based)
        Phase 5: Validation (schema + reconciliation)
        Phase 6: Packaging (distribution ZIP)
        
        Returns:
            {
                'classification': {...},
                'data': {...},
                'narrative': {...},
                'dashboard_path': Path,
                'package_path': Path,
                'validation_report': {...}
            }
        """
        # Implementation...
```

**CLI Interface:**
```bash
# Analyze repository
python -m cortex_lens analyze /path/to/repo

# Quick scan (classification only)
python -m cortex_lens scan /path/to/repo

# List available templates
python -m cortex_lens templates

# Generate from pre-collected data
python -m cortex_lens generate --data /path/to/data --template api_service
```

---

## 📋 Implementation Roadmap

### Phase 0: Foundation (Week 1-2) - **START HERE** ✅ IN PROGRESS
**Goal:** Create self-contained module structure + design system integration

- [x] **Directory Structure** ✅ COMPLETE
  - [x] Create `src/cortex_lens/` directory tree (11 directories)
  - [x] Set up `__init__.py` files for all modules (9 files)
  - [x] Create base classes (BaseAnalyzer, BaseCollector, BaseGenerator)
  - [x] Plugin registries (AnalyzerRegistry, CollectorRegistry)
  - [x] **Deliverable:** Module structure with proper imports ✅

- [ ] **Design System Integration** 🆕
  - [ ] Wait for Design System Phase 0 completion (centralized extraction)
  - [ ] Create symlinks in `templates/base/` to `cortex-brain/design-system/v1.0.0/`
  - [ ] Register as distribution target in `design-system-config.yaml`
  - [ ] Document template inheritance pattern
  - [ ] **Deliverable:** CORTEX Lens consumes centralized glassmorphism
  - [ ] **Dependency:** Design System Integration Plan Phase 0

- [ ] **Core Framework**
  - [ ] Implement `RepoTypeClassifier` (6 patterns)
  - [ ] Implement `DataCollectionPipeline`
  - [ ] Update registries with built-in analyzers/collectors
  - [ ] **Deliverable:** Functional classification + pipeline orchestration

- [ ] **Universal Schema**
  - [ ] Design complete JSON schema (`schemas.json`)
  - [ ] Implement `SchemaValidator`
  - [ ] Create schema documentation
  - [ ] **Deliverable:** Standardized data contracts

### Phase 1: First Vertical Slice (Week 3-4) - **PROOF OF CONCEPT**
**Goal:** End-to-end workflow for API Service template

- [ ] **Python Analyzer**
  - [ ] Implement `PythonAnalyzer` (native ast)
  - [ ] Test on CORTEX repo (self-analysis)
  - [ ] **Deliverable:** AST data extraction for Python

- [ ] **4 Core Collectors**
  - [ ] `HealthCollector` (file count, LOC, languages)
  - [ ] `ArchitectureCollector` (layer detection)
  - [ ] `APIEndpointCollector` (REST API catalog)
  - [ ] `CommentCollector` (comment extraction)
  - [ ] **Deliverable:** Functional data collection pipeline

- [ ] **API Service Template** 🆕 Uses Centralized Design System
  - [ ] Consume glassmorphism CSS from `cortex-brain/design-system/v1.0.0/`
  - [ ] Use `cortex-tabs.js`, `cortex-charts.js` from design system
  - [ ] 3 tabs (executive, endpoints, performance)
  - [ ] D3.js endpoint visualization (via `cortex-charts.js`)
  - [ ] **Deliverable:** Working static dashboard for API repos
  - [ ] **Dependency:** Design System Phase 2 (Publish Engine)

- [ ] **Orchestrator Integration**
  - [ ] Implement `CortexLens.analyze()` (6 phases)
  - [ ] CLI wrapper (`cli.py`)
  - [ ] Test on 2-3 API repositories
  - [ ] **Deliverable:** Functional end-to-end workflow

### Phase 2: Multi-Language Support (Week 5-6)
**Goal:** Add C#, JavaScript, SQL analyzers

- [ ] **C# Analyzer**
  - [ ] Regex-based parsing (classes, methods, controllers)
  - [ ] Copy patterns from existing `CSharpAnalyzer`
  - [ ] Test on .NET Core repos

- [ ] **JavaScript Analyzer**
  - [ ] Regex patterns (React components, routes, exports)
  - [ ] Frontend routing detection
  - [ ] Test on React/Vue repos

- [ ] **SQL Analyzer**
  - [ ] SQL parsing (tables, views, procedures)
  - [ ] Index analysis
  - [ ] Test on database projects

- [ ] **Deliverable:** Multi-language AST analysis

### Phase 3: Extended Collectors (Week 7-8)
**Goal:** Complete 14+ collector set

- [ ] **Security & Quality**
  - [ ] `SecurityCollector` (OWASP, vulnerabilities)
  - [ ] `ComplexityCollector` (cyclomatic complexity)
  - [ ] `TestCoverageCollector` (coverage by layer)

- [ ] **Tech Stack**
  - [ ] `TechStackCollector` (framework detection)
  - [ ] `DependencyCollector` (NuGet/NPM packages)

- [ ] **Performance & Compliance**
  - [ ] `PerformanceCollector` (hot paths)
  - [ ] `ComplianceCollector` (regulatory keywords)

- [ ] **Repo-Specific**
  - [ ] `FrontendRoutesCollector` (React Router, Vue Router)
  - [ ] `DatabaseSchemaCollector` (ERD data)
  - [ ] `CLICommandsCollector` (console apps)
  - [ ] `MessagingTopologyCollector` (microservices)
  - [ ] `PublicAPICollector` (libraries)

- [ ] **Deliverable:** Complete collector suite

### Phase 4: Extended Templates (Week 9-10)
**Goal:** 6 dashboard templates using centralized design system 🆕

- [ ] **Design System Consumption**
  - [ ] All templates inherit from centralized glassmorphism
  - [ ] Zero CSS duplication across templates
  - [ ] Consistent UI components (tabs, cards, badges, metrics)
  - [ ] Centralized updates propagate automatically via publish engine

- [ ] **Full-Stack Web Template** (7 tabs)
  - Frontend, Backend, Database, Integration tabs
  - API mapping visualization
  - Data flow diagrams

- [ ] **Database Project Template** (5 tabs)
  - Schema ERD (D3.js force graph via `cortex-charts.js`)
  - Procedure catalog
  - Query performance analysis

- [ ] **Console App Template** (5 tabs)
  - CLI command catalog
  - Workflow visualization
  - Configuration management

- [ ] **Microservices Template** (7 tabs)
  - Service topology (D3.js via `cortex-charts.js`)
  - Messaging/event bus
  - Container analysis

- [ ] **Library Template** (5 tabs)
  - API reference
  - Usage examples
  - Changelog

- [ ] **Deliverable:** 6 adaptive templates, all using centralized design system

### Phase 5: Narrative & Validation (Week 11)
**Goal:** Business narratives + data quality

- [ ] **Narrative Generator**
  - [ ] Internalize AST-to-Narrative patterns
  - [ ] Executive summary generation
  - [ ] Technical highlights extraction
  - [ ] **Deliverable:** Business-focused narratives

- [ ] **Validators**
  - [ ] Schema validation (required fields, types)
  - [ ] Reconciliation validator (CVSS/OWASP)
  - [ ] Confidence scoring
  - [ ] **Deliverable:** Data quality assurance

### Phase 6: Testing & Polish (Week 12)
**Goal:** Production-ready quality

- [ ] **Comprehensive Testing**
  - [ ] Unit tests (80%+ coverage)
  - [ ] Integration tests (6 repo types)
  - [ ] Test on 10+ diverse repositories

- [ ] **Performance Optimization**
  - [ ] Dashboard load time (<3 seconds)
  - [ ] Analysis time (<2 min for 10K LOC)
  - [ ] Memory footprint (<200MB)

- [ ] **Documentation**
  - [ ] User guide (how to use Lens)
  - [ ] Developer guide (plugin authoring)
  - [ ] API reference
  - [ ] Template authoring guide

- [ ] **Deliverable:** Production-ready CORTEX Lens

---

## 🎯 Integration with CORTEX Operations

### cortex-operations.yaml

```yaml
- name: "cortex_lens"
  description: "Universal repository analyzer with adaptive dashboards"
  category: "Intelligence"
  execution_method: "cli_wrapper"
  command: "python -m cortex_lens.cli analyze {repo_path} --output {output_dir}"
  admin_only: false
  capabilities:
    - "repo_classification"
    - "ast_analysis"
    - "dashboard_generation"
    - "multi_language_support"
  status: "✅ Self-contained (no external dependencies)"
```

### CLI Wrapper

**File:** `scripts/cli_wrappers/cortex_lens_wrapper.py`

```python
"""CLI wrapper for CORTEX Lens integration."""

import sys
from pathlib import Path

# Add cortex_lens to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from cortex_lens import CortexLens

def main():
    import argparse
    parser = argparse.ArgumentParser(description='CORTEX Lens')
    parser.add_argument('repo_path', help='Repository to analyze')
    parser.add_argument('--output', help='Output directory')
    
    args = parser.parse_args()
    
    lens = CortexLens()
    result = lens.analyze(args.repo_path, output_dir=args.output)
    
    print(f"✅ Dashboard: {result['dashboard_path']}")
    print(f"📦 Package: {result['package_path']}")

if __name__ == '__main__':
    main()
```

---

## 📊 Success Metrics & Validation

### Classification Accuracy
- **Target:** 90%+ correct repo type detection
- **Test Set:** 50+ diverse repositories
- **Validation:** Manual review + user feedback

### Performance Benchmarks
| Metric | Target | Measured |
|--------|--------|----------|
| Analysis Time (10K LOC) | <2 min | TBD |
| Dashboard Load Time | <3 sec | TBD |
| Memory Footprint | <200MB | TBD |
| Package Size | <5MB | TBD |

### Code Quality
- **Unit Test Coverage:** 80%+
- **Integration Tests:** 6 repo types × 3 samples = 18 tests
- **Code Reviews:** All PRs reviewed by 2+ developers

---

## 🔒 Architecture Principles

### 1. Self-Containment
- ✅ **All code in** `src/cortex_lens/`
- ✅ **Zero imports** from other CORTEX modules
- ✅ **Standalone deployment** possible

### 2. Modularity
- ✅ **Plugin architecture** for analyzers, collectors, templates
- ✅ **Clear interfaces** (BaseAnalyzer, BaseCollector, BaseGenerator)
- ✅ **Independent testing** of each module

### 3. Extensibility
- ✅ **Registry pattern** for dynamic plugin loading
- ✅ **Convention over configuration**
- ✅ **Well-documented** plugin authoring guide

### 4. Maintainability
- ✅ **Small, focused modules** (<500 LOC each)
- ✅ **Comprehensive documentation**
- ✅ **Clear separation of concerns**

### 5. Performance
- ✅ **Lazy loading** where possible
- ✅ **Efficient file scanning** (skip .git, node_modules)
- ✅ **Caching** of expensive operations

---

## 🚨 Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Classification accuracy <90%** | High | Extensive testing on diverse repos, iterative improvement |
| **Performance degradation on large repos** | Medium | Benchmark early, optimize hot paths, add progress indicators |
| **Template complexity** | Medium | Start simple, iterate based on user feedback |
| **Code duplication from existing collectors** | Low | Extract patterns, not copy-paste; maintain DRY |
| **Plugin API instability** | Low | Version API, deprecation warnings, backward compatibility |

---

## 📚 References

**Existing CORTEX Assets:**
- Admin Dashboard collectors (18 implemented) - inspiration for Lens collectors
- RA Toolkit glassmorphism UI - template design patterns
- AST-to-Narrative orchestrator - narrative generation approach
- Comment extractor - comment analysis patterns
- CSharpAnalyzer - multi-language analysis patterns

**Key Documents:**
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-operations.yaml` - Operation registry
- `src/tier0/README.md` - Governance rules

**Planning History:**
- Original plan: Unified dashboard modernization (merge Admin + RA)
- Evolved to: Universal repository intelligence platform (CORTEX Lens)
- Key insight: Repos need adaptive dashboards, not fixed views

---

**Next Action:** Begin Phase 0 (Foundation) - Create `src/cortex_lens/` directory structure.

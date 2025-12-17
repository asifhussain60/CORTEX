# 🧠 CORTEX Enhancement Plan: Rename Enterprise Documentation Orchestrator to `cortex_scribe`

**Plan ID:** PLAN-2025-12-13-CORTEX-SCRIBE-ENHANCEMENT  
**Created:** December 13, 2025  
**Status:** 🔍 Analysis Complete - Awaiting Approval  
**Category:** Documentation Infrastructure Enhancement  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

**📋 Note:** This plan uses single-file format. For future large plans (>500 lines), consider migrating to [modular structure](../../implementation-guides/MODULAR-PLAN-STRUCTURE-IMPLEMENTATION.md) with master plan + sub-plans.

---

## 🚀 Quick Start: Preview Documentation Site

**To serve the documentation locally:**

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m mkdocs serve
```

**Preview URL:** [http://127.0.0.1:8000/CORTEX/](http://127.0.0.1:8000/CORTEX/)

**📖 Full serving documentation:** See [MkDocs Preview Server section](#-mkdocs-preview-server-documentation-serving) below.

---

## 📑 Table of Contents

1. [Executive Summary](#-executive-summary)
2. [📊 Documentation Targets - Visual Tracker](#-documentation-targets---visual-tracker) ⭐ **NEW: Complete Feature Inventory**
3. [📋 Master Plan & Sub-Plans](#-master-plan--sub-plans) ⭐ **NEW: Phase 1 Documentation Strategy**
4. [🤖 Orchestrator Design Patterns](#-orchestrator-design-patterns) ⭐ **NEW: Automation Architecture**
5. [📁 Folder Structure Standards](#-folder-structure-standards) ⭐ **NEW: Organization Enforcement**
6. [Current Implementation Analysis](#-current-implementation-analysis)
7. [Enhancement Proposal: cortex_scribe](#-enhancement-proposal-cortex_scribe)
8. [Proposed Architecture](#-proposed-architecture)
9. [Enhancement Features](#-enhancement-features)
10. [Implementation Plan](#-implementation-plan)
11. [🌐 MkDocs Preview Server](#-mkdocs-preview-server-documentation-serving) ⭐ **How to serve the site**
12. [Success Metrics](#-success-metrics)
13. [Technical Considerations](#-technical-considerations)
14. [Next Steps](#-next-steps)
15. [References](#-references)

---

## 📊 Documentation Targets - Visual Tracker

This section tracks **all CORTEX capabilities and features** that need documentation. The tracker shows current status and priority for cortex_scribe to generate documentation for each feature.

### 🎯 Progress Summary

**Total Features:** 45 | **Documented:** 8 (18%) | **In Progress:** 4 (9%) | **Pending:** 33 (73%)

### Legend

- ✅ **Complete** - Documentation exists and is up-to-date
- 🔄 **In Progress** - Documentation partially complete or being updated
- ⏳ **Pending** - Needs documentation (not started)
- 🔥 **High Priority** - Core user-facing features
- 📌 **Medium Priority** - Important but not critical
- 🔖 **Low Priority** - Nice to have, internal tooling

---

### Core Orchestration & Planning (10 features)

| # | Feature | Version | Status | Docs Status | Priority | Source Location | Notes |
|---|---------|---------|--------|-------------|----------|-----------------|-------|
| 1 | **Planning System 2.0** | v3.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `src/orchestrators/planning_orchestrator.py` | DoR/DoD, threat modeling, TDD integration, contextual review |
| 2 | **ADO Planning Orchestrator** | v2.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml` | Inherits Planning 2.0 + ADO work item generation |
| 3 | **TDD Mastery** | v3.2.0 | ✅ Production | 🔄 In Progress | 🔥 High | `src/orchestrators/tdd_implementation_orchestrator.py` | RED→GREEN→REFACTOR, debug integration, view discovery |
| 4 | **Debug System** | v1.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `src/orchestrators/debug_workflow_orchestrator.py` | Runtime instrumentation, multi-session, natural language intent |
| 5 | **System Maintenance** | v3.8.1 | ✅ Production | 🔄 In Progress | 🔥 High | `src/operations/modules/orchestration/system_maintenance_orchestrator.py` | 6-phase workflow: healthcheck→align→cleanup→optimize→refresh→healthcheck |
| 6 | **Git Checkpoint** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/orchestrators/git_checkpoint_orchestrator.py` | Git operations orchestrator |
| 7 | **Rollback Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/orchestrators/rollback_orchestrator.py` | Phase rollback and recovery |
| 8 | **Application Health** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/orchestrators/application_health_orchestrator.py` | Health monitoring and diagnostics |
| 9 | **Dashboard Generator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/orchestrators/dashboard_generator.py` | Dashboard generation orchestrator |
| 10 | **Master Setup** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/orchestrators/master_setup_orchestrator.py` | Complete setup workflow orchestrator |

---

### CORTEX Lens - Universal Repository Intelligence (1 feature)

| # | Feature | Version | Status | Docs Status | Priority | Source Location | Notes |
|---|---------|---------|--------|-------------|----------|-----------------|-------|
| 11 | **CORTEX Lens Platform** | v1.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `src/cortex_lens/` | 6-phase analysis, 14+ collectors, multi-language AST parsing (99%+), business intelligence narratives, 7 narrative engines, multi-format export, adaptive dashboards |

---

### Documentation Generation Components (6 features)

| # | Feature | Version | Status | Docs Status | Priority | Source Location | Notes |
|---|---------|---------|--------|-------------|----------|-----------------|-------|
| 12 | **Diagrams Generator** | v1.0.0 | ✅ Production | ✅ Complete | 🔥 High | `src/operations/documentation_component_registry.py` | Architecture, workflow, system design (Mermaid) |
| 13 | **Feature List Generator** | v1.0.0 | ✅ Production | ✅ Complete | 🔥 High | Registry component | Auto-generate feature lists |
| 14 | **MkDocs Site Generator** | v1.0.0 | ✅ Production | 🔄 In Progress | 🔥 High | Registry component | Complete static site with navigation |
| 15 | **Executive Summary Generator** | v1.0.0 | ✅ Production | ✅ Complete | 📌 Medium | Registry component | Executive-level documentation |
| 16 | **Publish Documentation** | v1.0.0 | ✅ Production | ✅ Complete | 📌 Medium | Registry component | Publication workflow |
| 17 | **Orchestration Docs Generator** | v1.0.0 | ✅ Production | ✅ Complete | 🔥 High | Registry component | Auto-discover orchestrators, AST parsing, Mermaid workflows (50+ orchestrators documented) |

---

### Operations & Utilities (14 features)

| # | Feature | Version | Status | Docs Status | Priority | Source Location | Notes |
|---|---------|---------|--------|-------------|----------|-----------------|-------|
| 18 | **Orchestration Metrics Collector** | v1.0.0 | ✅ Production | 🔄 In Progress | 🔥 High | `src/operations/utilities/orchestration_metrics_collector.py` | Silent background metrics, <5ms overhead, 7-day reports, @with_orchestration_metrics decorator |
| 19 | **Progress Renderer** | v3.8.1 | ✅ Production | ⏳ Pending | 🔥 High | `src/operations/utilities/progress_renderer.py` | Real-time visual progress bars for autonomous execution |
| 20 | **Vision Context Middleware** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/vision_context_middleware.py` | Automatic GPT-4V engagement for image analysis |
| 21 | **Task Injection Manager** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/task_injection_manager.py` | Context-aware mid-execution task injection |
| 22 | **Orchestration Checkpoint Manager** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/orchestration_checkpoint_manager.py` | Save/restore/rollback workflow state |
| 23 | **Parallel Orchestration Coordinator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/parallel_orchestration_coordinator.py` | Concurrent phase execution with dependency resolution |
| 24 | **Orchestration Analytics Dashboard** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/orchestration_analytics_dashboard.py` | Visualization and reporting for metrics |
| 25 | **Resource Management Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 🔖 Low | `src/operations/utilities/resource_management_orchestrator.py` | Resource monitoring and optimization |
| 26 | **Error Recovery Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/error_recovery_orchestrator.py` | Retry policies and circuit breakers |
| 27 | **Performance Profiling Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/performance_profiling_orchestrator.py` | Execution profiling and bottleneck detection |
| 28 | **Documentation Generation Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `src/operations/utilities/documentation_generation_orchestrator.py` | Docstring, API reference, usage guide generation |
| 29 | **Code Quality Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/utilities/code_quality_orchestrator.py` | Code reviews, complexity reports, quality scorecards |
| 30 | **Component Discovery Scanner** | v1.0.0 | ✅ Production | ⏳ Pending | 🔖 Low | `src/operations/modules/realignment/component_discovery_scanner.py` | Scans CORTEX for unwired architectural components |
| 31 | **Cleanup Orchestrator** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/operations/modules/orchestration/cleanup_orchestrator.py` | Automated cleanup workflows |

---

### Capabilities (14 features)

| # | Feature | Version | Status | Docs Status | Priority | Source Location | Notes |
|---|---------|---------|--------|-------------|----------|-----------------|-------|
| 32 | **Code Writing** | v3.8.1 | ✅ Production | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | 100% ready, multi-language, TDD workflow, SOLID compliance |
| 33 | **Code Review** | v4.0.0 | 🔄 CORTEX 4.0 | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | 60% ready, Q2 2026 target, PR integration (Azure/GitHub/GitLab/BitBucket) |
| 34 | **Code Rewrite** | v3.8.1 | ✅ Production | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | 100% ready, refactoring support, pattern-based restructuring |
| 35 | **Timeframe Estimation** | v2.0.0 | ✅ Production | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | SWAGGER complexity, parallel tracks, critical path, ASCII Gantt charts, HTML timelines, cost projections, optimal team size |
| 36 | **Backend Testing** | v4.0.0 | 🔄 CORTEX 4.0 | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | 95% ready, Q2 2026, performance testing integration (Locust, k6, JMeter, Gatling) |
| 37 | **Web Testing** | v3.8.1 | ✅ Production | ⏳ Pending | 🔥 High | `cortex-brain/capabilities.yaml` | 85% ready, Playwright integration, Lighthouse performance, axe-core accessibility, Core Web Vitals |
| 38 | **Mobile Testing** | v4.0.0 | 🔄 CORTEX 4.0 | ⏳ Pending | 📌 Medium | `cortex-brain/capabilities.yaml` | 0% ready, Q3 2026, Appium/XCUITest/Espresso, device farm integration (AWS, BrowserStack, Sauce Labs) |
| 39 | **Code Documentation** | v3.8.1 | ✅ Production | ✅ Complete | 🔥 High | `cortex-brain/capabilities.yaml` | 100% ready, docstring generation, README, API docs, MkDocs integration |
| 40 | **Reverse Engineering** | v3.8.1 | ✅ Production | ⏳ Pending | 📌 Medium | `cortex-brain/capabilities.yaml` | 50% ready, complexity analysis, technical debt detection, Mermaid/UML diagrams |
| 41 | **UI from Figma** | v4.0.0 | 🔄 CORTEX 4.0 | ⏳ Pending | 📌 Medium | `cortex-brain/capabilities.yaml` | 0% ready (partial), Figma API integration planned |
| 42 | **Performance Telemetry Plugin** | v1.0.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/plugins/performance_telemetry_plugin.py` | Engineer productivity metrics, capability aggregation, cost savings, Copilot enhancement metrics |
| 43 | **Narrative Consolidator** | v7.4.3 | ✅ Production | ⏳ Pending | 📌 Medium | `src/dashboard/data/narrative_consolidator.py` | Business capability detection, semantic analysis, contradiction detection, holistic scoring |
| 44 | **Business Capability Detector** | v7.4.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/dashboard/data/business_capability_detector.py` | AST + pattern analysis for capability extraction |
| 45 | **Semantic Analyzer** | v7.4.0 | ✅ Production | ⏳ Pending | 📌 Medium | `src/dashboard/intelligence/semantic_analyzer.py` | Executive summary generation for capabilities |

---

### 🎯 Documentation Generation Priority

**Phase 1 (Immediate)** - High Priority User-Facing Features (13 features):
- Planning System 2.0, ADO Planning, TDD Mastery, Debug System, System Maintenance
- CORTEX Lens Platform, Orchestration Docs Generator
- Code Writing, Code Rewrite, Timeframe Estimation, Web Testing
- Orchestration Metrics Collector, Progress Renderer

**Phase 2 (Next Sprint)** - Medium Priority Features (17 features):
- Git Checkpoint, Application Health, Dashboard Generator, Master Setup
- Vision Context Middleware, Task Injection Manager, Error Recovery, Performance Profiling
- Documentation Generation Orchestrator, Code Quality Orchestrator, Cleanup Orchestrator
- Code Review (CORTEX 4.0), Backend Testing (CORTEX 4.0), Reverse Engineering
- Mobile Testing (CORTEX 4.0), Performance Telemetry, Narrative Consolidator

**Phase 3 (Future)** - Low Priority Internal Tools (15 features):
- Rollback Orchestrator, Orchestration Checkpoint Manager, Parallel Orchestration Coordinator
- Orchestration Analytics Dashboard, Resource Management, Component Discovery Scanner
- UI from Figma (CORTEX 4.0), Business Capability Detector, Semantic Analyzer
- Plus 6 other internal utilities

---

## 📋 Master Plan & Sub-Plans

**Phase 1 Documentation Initiative** provides a comprehensive, modular approach to documenting all 36 missing CORTEX features (80% documentation gap → 100% coverage).

### Master Plan Coordination

**Document:** [MASTER-PLAN-PHASE-1-DOCUMENTATION.md](MASTER-PLAN-PHASE-1-DOCUMENTATION.md)

**Objective:** Close 80% documentation gap by generating comprehensive documentation for 36 production-ready features

**Strategy:**
- 3 autonomous sub-plans organized by priority (HIGH/MEDIUM/LOW)
- Each sub-plan is holistic and testable independently
- Modular execution enables parallel work and staged rollout
- Orchestrator-friendly design for future automation

**Metrics:**
- **Total Features:** 36 (20% → 100% coverage)
- **Total Effort:** 108 hours (~3 weeks)
- **Documentation Structure:** 3 sub-plans
  - Sub-Plan 1 (HIGH): 13 features, 44 hours, ~1.5 weeks
  - Sub-Plan 2 (MEDIUM): 17 features, 49 hours, ~1.5 weeks
  - Sub-Plan 3 (LOW): 6 features, 15 hours, ~2-3 days

### Sub-Plan 1: HIGH Priority Features

**Document:** [SUB-PLAN-1-HIGH-PRIORITY-DOCS.md](SUB-PLAN-1-HIGH-PRIORITY-DOCS.md)

**Mission:** Document 13 critical production features (user-facing, zero docs, high impact)

**Features (13):**
1. CORTEX Lens Platform (8h) - 6-phase analysis, 14+ collectors
2. Orchestration Metrics Collector (4h) - <5ms overhead, 7-day reports
3. Code Writing Capability (3h) - Multi-language, TDD integration
4. Code Rewrite Capability (3h) - Refactoring patterns
5. Progress Renderer (2h) - Real-time progress bars
6. Timeframe Estimation (3h) - SWAGGER complexity
7. Web Testing (4h) - Playwright, 85% ready
8. Code Documentation (2h) - Docstring generation
9. Diagrams Generator (3h) - Mermaid diagrams
10. Feature List Generator (2h) - Feature catalog
11. MkDocs Site Generator (3h) - Static site
12. Documentation Generation Orchestrator (4h) - 6-phase pipeline
13. Code Quality Orchestrator (3h) - Quality automation

**Execution Order:** Week 1 (Days 1-5), Week 2 (Days 1-2 validation)

**Status:** ✅ APPROVED - READY FOR EXECUTION

### Sub-Plan 2: MEDIUM Priority Features

**Document:** [SUB-PLAN-2-MEDIUM-PRIORITY-DOCS.md](SUB-PLAN-2-MEDIUM-PRIORITY-DOCS.md)

**Mission:** Document 17 supporting production features (advanced workflows, integrations, CORTEX 4.0 preview)

**Features (17):**
1. Rollback Orchestrator (3h) - Phase rollback
2. Master Setup Orchestrator (3h) - Setup workflow
3. Error Recovery Orchestrator (3h) - Retry policies, circuit breakers
4. Performance Profiling Orchestrator (3h) - Bottleneck detection
5. Cleanup Orchestrator (2h) - Cleanup automation
6. Refactoring Planning Orchestrator (3h) - Pattern detection
7. Feature Planning Orchestrator (3h) - Planning System 2.0 integration
8. Architecture Planning Orchestrator (4h) - Architecture patterns
9. Executive Summary Generator (2h) - Summary generation
10. Publish Documentation (2h) - GitHub Pages deployment
11. Vision Context Middleware (3h) - GPT-4V integration
12. Task Injection Manager (3h) - Task injection
13. Orchestration Analytics Dashboard (4h) - Metrics visualization
14. Performance Telemetry Plugin (2h) - Productivity metrics
15. Code Review (CORTEX 4.0) (4h) - 60% ready, Q2 2026
16. Backend Testing (CORTEX 4.0) (3h) - 95% ready, Q1 2026
17. Reverse Engineering (4h) - 50% ready
18. Narrative Consolidator (3h) - Business capabilities
19. Business Capability Detector (3h) - AST + pattern analysis

**Execution Order:** Week 1 (Days 1-5 orchestrators), Week 2 (Days 1-3 CORTEX 4.0 & capabilities)

**Status:** ✅ APPROVED - READY FOR EXECUTION

### Sub-Plan 3: LOW Priority Features

**Document:** [SUB-PLAN-3-LOW-PRIORITY-DOCS.md](SUB-PLAN-3-LOW-PRIORITY-DOCS.md)

**Mission:** Document 6 infrastructure and future features (completes 100% coverage)

**Features (6):**
1. Orchestration Checkpoint Manager (3h) - State persistence
2. Parallel Orchestration Coordinator (3h) - Concurrent execution
3. Resource Management Orchestrator (2h) - Resource allocation
4. Component Discovery Scanner (2h) - Component discovery
5. Mobile Testing (CORTEX 4.0) (3h) - 30% ready, Q3 2026
6. UI from Figma (CORTEX 4.0) (2h) - 20% ready, Q4 2026

**Execution Order:** Days 1-2 (infrastructure), Day 3 (CORTEX 4.0 + validation)

**Status:** ✅ APPROVED - READY FOR EXECUTION

### Execution Workflow

**Phase 1: Setup (1 day)**
- ✅ Create folder structure (docs/features/, docs/orchestration/, docs/future/)
- ✅ Setup templates library (documentation-templates.js)
- ✅ Configure MkDocs (mkdocs.yml)
- ✅ Prepare D3.js visualization scripts

**Phase 2: Execute Sub-Plan 1 (1-1.5 weeks)**
- Execute 13 HIGH priority features sequentially
- Validate each feature upon completion
- Update navigation and home page incrementally
- Milestone: Core user-facing features documented

**Phase 3: Execute Sub-Plan 2 (1.5 weeks)**
- Execute 17 MEDIUM priority features
- Integrate with Sub-Plan 1 features
- Document CORTEX 4.0 preview features
- Milestone: Supporting features documented

**Phase 4: Execute Sub-Plan 3 (2-3 days)**
- Execute 6 LOW priority features
- Achieve 100% documentation coverage
- Complete final validation
- Milestone: All features documented

**Phase 5: Publishing (2 days)**
- Complete site validation (links, visualizations, responsive)
- Deploy to GitHub Pages
- Update README and documentation index
- Announce completion

### Progress Tracking

**Current Status:**
- Planning: ✅ Complete (Master Plan + 3 Sub-Plans)
- Templates Library: ✅ Complete (documentation-templates.js)
- Execution: ⏳ Pending (0/36 features complete)
- Publishing: ⏳ Pending

**Completion Criteria:**
- ✅ All 36 features documented (45/45 total = 100% coverage)
- ✅ All visualizations functional (D3.js interactive)
- ✅ All code examples tested
- ✅ Navigation complete and functional
- ✅ Site deployed to GitHub Pages
- ✅ Performance <3s page load

---

## 🤖 Orchestrator Design Patterns

This section defines the **orchestrator-friendly design patterns** that enable `cortex_scribe` to automate documentation generation. These patterns establish structured input/output formats, validation criteria, and integration points.

### Input Format: Feature Specification YAML

Each feature to be documented should provide a structured YAML specification:

```yaml
feature:
  name: "CORTEX Lens Platform"
  file_path: "docs/features/cortex-lens.html"
  icon: "🔍"
  version: "v1.0.0"
  status: "Production Ready"
  priority: "HIGH"
  
  description:
    why_critical: "6-phase analysis, 14+ collectors, 99%+ AST parsing, zero docs"
    overview: "Universal repository intelligence platform providing comprehensive codebase analysis"
  
  sections:
    - hero_metrics:
        - "6 analysis phases"
        - "14+ specialized collectors"
        - "99%+ AST parsing accuracy"
        - "7 narrative engines"
    
    - overview:
        content: "CORTEX Lens is a universal repository intelligence platform..."
    
    - key_features:
        - "Multi-language AST parsing (Python, JavaScript, TypeScript, C#, Java)"
        - "Business intelligence narratives"
        - "Adaptive dashboards"
        - "Multi-format export (JSON, Markdown, HTML)"
    
    - visualizations:
        - type: "d3_phase_flow"
          title: "6-Phase Analysis Workflow"
          phases: ["Inventory", "AST Parsing", "Collectors", "Analysis", "Narratives", "Export"]
        
        - type: "d3_architecture_diagram"
          title: "Collector Architecture"
          layers: ["Entry Point", "Phase Manager", "14+ Collectors", "Narrative Engines", "Export"]
  
  code_examples:
    - language: "python"
      title: "Run Complete Analysis"
      code: |
        from src.cortex_lens import CortexLens
        
        lens = CortexLens(root_path="./src")
        result = lens.analyze()
        lens.export_report("cortex-lens-output/report.html")
    
    - language: "python"
      title: "Export Multi-Format Report"
      code: |
        lens.export_report(
            output_path="report.json",
            format="json",
            include_metadata=True
        )
  
  acceptance_criteria:
    - "Page renders with all sections"
    - "D3.js visualizations work and are interactive"
    - "Code examples execute successfully"
    - "Links to related features work"
  
  integration_points:
    - "Component Discovery Scanner"
    - "Business Capability Detector"
    - "CORTEX Dashboard"
```

### Output Structure: Generated HTML Documentation

The orchestrator should generate HTML pages with the following structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CORTEX Lens Platform | CORTEX Documentation</title>
    <link rel="stylesheet" href="../assets/css/main.css">
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <!-- Navigation Breadcrumbs -->
    <nav class="breadcrumb">
        <a href="../index.html">Home</a> > 
        <a href="index.html">Features</a> > 
        <span>CORTEX Lens Platform</span>
    </nav>
    
    <!-- Hero Section with Metrics -->
    <section class="hero">
        <div class="hero-icon">🔍</div>
        <h1>CORTEX Lens Platform</h1>
        <p class="version">v1.0.0 | Production Ready</p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">6</div>
                <div class="metric-label">Analysis Phases</div>
            </div>
            <!-- More metrics... -->
        </div>
    </section>
    
    <!-- Overview Section -->
    <section class="overview glass-card">
        <h2>Overview</h2>
        <p>CORTEX Lens is a universal repository intelligence platform...</p>
    </section>
    
    <!-- Key Features Section -->
    <section class="key-features glass-card">
        <h2>Key Features</h2>
        <div class="feature-grid">
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <h3>Multi-Language AST Parsing</h3>
                <p>Python, JavaScript, TypeScript, C#, Java</p>
            </div>
            <!-- More features... -->
        </div>
    </section>
    
    <!-- D3.js Visualization -->
    <section class="visualization glass-card">
        <h2>6-Phase Analysis Workflow</h2>
        <div id="phase-flow-viz"></div>
        <script src="../assets/js/phase-flow-viz.js"></script>
    </section>
    
    <!-- Code Examples -->
    <section class="code-examples glass-card">
        <h2>Usage Examples</h2>
        <div class="code-example">
            <h3>Run Complete Analysis</h3>
            <pre><code class="language-python">
from src.cortex_lens import CortexLens

lens = CortexLens(root_path="./src")
result = lens.analyze()
lens.export_report("cortex-lens-output/report.html")
            </code></pre>
        </div>
    </section>
    
    <!-- Integration Points -->
    <section class="integration glass-card">
        <h2>Integration Points</h2>
        <ul>
            <li><a href="component-discovery.html">Component Discovery Scanner</a></li>
            <li><a href="business-capability-detector.html">Business Capability Detector</a></li>
        </ul>
    </section>
    
    <!-- Related Features -->
    <section class="related glass-card">
        <h2>Related Features</h2>
        <div class="feature-grid">
            <!-- Related feature cards... -->
        </div>
    </section>
</body>
</html>
```

### Validation Checklist

The orchestrator should validate each generated page:

**HTML Structure:**
- [ ] Valid HTML5 (no errors)
- [ ] Proper heading hierarchy (h1 > h2 > h3)
- [ ] Breadcrumb navigation present and functional
- [ ] All required sections present

**Content Quality:**
- [ ] Overview section complete and accurate
- [ ] All key features listed
- [ ] "Why Critical" explanation clear

**Visualizations:**
- [ ] D3.js visualizations present
- [ ] Visualizations render correctly
- [ ] Interactive elements functional
- [ ] Responsive design (desktop, tablet, mobile)

**Code Examples:**
- [ ] At least 2 code examples present
- [ ] Syntax highlighting applied
- [ ] Examples tested and functional
- [ ] Examples explained with context

**Links & Navigation:**
- [ ] Internal links functional
- [ ] Related features linked
- [ ] Integration points documented
- [ ] Breadcrumbs update correctly

**Responsive Design:**
- [ ] Desktop (1920px): Full layout
- [ ] Laptop (1366px): Optimized layout
- [ ] Tablet (768px): Stacked layout
- [ ] Mobile (375px): Single column

### Orchestrator Workflow

**Phase 1: Validation**
- Parse feature specification YAML
- Validate required fields present
- Check template availability
- Verify output path writable

**Phase 2: Content Generation**
- Load appropriate template (feature/orchestrator/capability)
- Populate hero section with metrics
- Generate overview and key features
- Create code examples with syntax highlighting
- Build integration points section

**Phase 3: Visualization Generation**
- Generate D3.js visualization scripts
- Embed visualizations in HTML
- Configure responsive behavior
- Test interactivity

**Phase 4: Navigation Updates**
- Update mkdocs.yml with new page
- Update home page index with feature card
- Update category index pages
- Generate breadcrumb paths

**Phase 5: Validation**
- Run HTML validation
- Test all links
- Verify visualizations render
- Check responsive design
- Validate code examples

**Phase 6: Integration**
- Commit generated files
- Trigger site rebuild
- Update documentation index
- Generate changelog entry

### Template Library Integration

**Reference:** [documentation-templates.js](../reference/documentation-templates.js)

The orchestrator should leverage the templates library for consistent generation:

```javascript
const { 
    FEATURE_PAGE_TEMPLATE,
    BREADCRUMB_TEMPLATE,
    HERO_SECTION_TEMPLATE,
    D3_PHASE_FLOW,
    D3_METRICS_DASHBOARD,
    DOC_PATTERNS
} = require('./documentation-templates.js');

// Generate feature page
const html = FEATURE_PAGE_TEMPLATE
    .replace('{{TITLE}}', feature.name)
    .replace('{{BREADCRUMB}}', BREADCRUMB_TEMPLATE(feature.category))
    .replace('{{HERO}}', HERO_SECTION_TEMPLATE(feature.metrics))
    .replace('{{D3_VIZ}}', D3_PHASE_FLOW(feature.phases));
```

### Automation Capabilities

The orchestrator should support:

1. **Batch Generation:** Generate multiple features in sequence
2. **Incremental Updates:** Update existing pages without regenerating entire site
3. **Dry-Run Mode:** Preview generation without writing files
4. **Validation Mode:** Check existing pages for compliance
5. **Refresh Mode:** Regenerate pages with updated templates
6. **Export Mode:** Generate documentation for external publishing

---

## 📁 Folder Structure Standards

This section defines **mandatory folder structure conventions** that ensure consistent organization and enable proper GitHub Pages publishing.

### Folder Organization

```
docs/
├── index.html                    # Home page (DO NOT MODIFY directly)
├── mkdocs.yml                    # Navigation config (AUTO-UPDATED)
│
├── features/                     # User-facing features
│   ├── index.html               # Features index page
│   ├── cortex-lens.html         # Example: CORTEX Lens Platform
│   ├── code-writing.html        # Example: Code Writing Capability
│   ├── code-rewrite.html        # Example: Code Rewrite Capability
│   └── ...                      # 20+ feature pages
│
├── orchestration/                # Orchestrator documentation
│   ├── index.html               # Orchestrators index page
│   ├── planning-system.html     # Example: Planning System 2.0
│   ├── tdd-implementation.html  # Example: TDD Mastery
│   ├── system-maintenance.html  # Example: System Maintenance
│   └── ...                      # 15+ orchestrator pages
│
├── future/                       # CORTEX 4.0 preview features
│   ├── index.html               # Future features index
│   ├── code-review.html         # Example: Code Review (60% ready)
│   ├── backend-testing.html     # Example: Backend Testing (95% ready)
│   ├── mobile-testing.html      # Example: Mobile Testing (30% ready)
│   └── ui-from-figma.html       # Example: UI from Figma (20% ready)
│
├── assets/                       # Shared resources
│   ├── css/
│   │   ├── main.css            # Global styles (glassmorphism)
│   │   └── syntax-highlight.css # Code highlighting
│   ├── js/
│   │   ├── navigation.js        # Global navigation logic
│   │   ├── phase-flow-viz.js    # Reusable D3.js: Phase flow
│   │   ├── metrics-dashboard-viz.js # Reusable D3.js: Metrics
│   │   ├── architecture-viz.js  # Reusable D3.js: Architecture
│   │   ├── timeline-viz.js      # Reusable D3.js: Timeline
│   │   └── matrix-viz.js        # Reusable D3.js: Matrix
│   └── images/
│       ├── logo.png
│       ├── icons/               # Feature icons
│       └── screenshots/         # Feature screenshots
│
└── architecture/                 # System architecture docs
    ├── index.html
    ├── overview.html
    └── ...
```

### File Naming Conventions

**HTML Pages:**
- Use lowercase with hyphens: `cortex-lens.html`, `code-writing.html`
- Match feature name pattern: `[feature-name].html`
- NO underscores, NO spaces, NO camelCase

**JavaScript Files:**
- Descriptive names: `phase-flow-viz.js`, `metrics-dashboard-viz.js`
- Suffix with `-viz.js` for D3.js visualizations
- Use `-util.js` for utility scripts

**CSS Files:**
- Global styles: `main.css`
- Component styles: `[component]-styles.css`
- Glassmorphism tokens in `main.css` (DO NOT create separate glassmorphism.css)

### Validation Rules

**Forbidden:**
- ❌ Root-level documentation files (e.g., `CORTEX/summary.md`)
- ❌ Documentation in `cortex-brain/` (except planning)
- ❌ Inline CSS in HTML files (use classes + main.css)
- ❌ Duplicate D3.js code (use shared scripts in assets/js/)
- ❌ Hardcoded file paths (use relative paths)

**Required:**
- ✅ All feature pages in `docs/features/`
- ✅ All orchestrator pages in `docs/orchestration/`
- ✅ All CORTEX 4.0 pages in `docs/future/`
- ✅ Shared visualizations in `docs/assets/js/`
- ✅ Glassmorphism CSS in `docs/assets/css/main.css`

### Navigation Categories

**MkDocs Navigation Structure:**

```yaml
nav:
  - Home: index.md
  - Features:
      - Overview: features/index.md
      - CORTEX Lens Platform: features/cortex-lens.md
      - Code Writing: features/code-writing.md
      - Code Rewrite: features/code-rewrite.md
      # ... more features
  - Orchestration:
      - Overview: orchestration/index.md
      - Planning System 2.0: orchestration/planning-system.md
      - TDD Mastery: orchestration/tdd-implementation.md
      # ... more orchestrators
  - Future (CORTEX 4.0):
      - Overview: future/index.md
      - Code Review: future/code-review.md
      - Backend Testing: future/backend-testing.md
      # ... more future features
  - Architecture:
      - Overview: architecture/index.md
      # ... architecture docs
```

### Asset Organization

**CSS Design Tokens (main.css):**
```css
:root {
    /* Colors */
    --bg-primary: #0a0e27;
    --bg-secondary: #1a1f3a;
    --accent-primary: #00d4ff;
    --accent-secondary: #7b61ff;
    
    /* Glassmorphism */
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-blur: blur(20px);
    
    /* Typography */
    --font-primary: 'Segoe UI', 'Inter', sans-serif;
    --font-mono: 'SF Mono', 'Consolas', monospace;
}

.glass-card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 2rem;
}
```

**D3.js Visualization Scripts:**
- Place in `docs/assets/js/`
- Export as reusable functions
- Accept configuration parameters
- Support responsive design

### Publishing Requirements

**GitHub Pages Configuration:**
- Branch: `main` or `gh-pages`
- Source: `/docs` folder
- Custom domain: Optional
- Enforce HTTPS: Enabled

**Site Build Validation:**
```bash
# Build site locally
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m mkdocs build

# Check for errors
# Expected: "Documentation built successfully"

# Serve locally for testing
python3 -m mkdocs serve
# Preview: http://127.0.0.1:8000/CORTEX/
```

**Performance Requirements:**
- Page load: <3 seconds
- Time to Interactive: <5 seconds
- Lighthouse Performance: >90
- Mobile responsive: 100%

---

## 🎯 Executive Summary

This plan proposes **renaming and enhancing** the deprecated `EnterpriseDocumentationOrchestratorModule` to **`cortex_scribe`** - a more intuitive, focused name that reflects its purpose as CORTEX's documentation writer/chronicler.

**Current State:** Module is **DEPRECATED** and archived at `cortex-brain/archives/deprecated-orchestrators/enterprise_documentation_orchestrator_module.py.deprecated`

**Proposed State:** Resurrect, enhance, and rename to `cortex_scribe` with modern architecture, better integration, and expanded capabilities.

---

## 📊 Current Implementation Analysis

### What the Orchestrator Does

The `EnterpriseDocumentationOrchestratorModule` is a **wrapper orchestrator** that:

1. **Delegates to Main Generator**: Calls `cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py`
2. **Generates Real Live Data**: Creates analytics dashboards from `cortex-brain/analytics/` data
3. **Builds MkDocs Site**: Generates comprehensive documentation with:
   - Architecture diagrams
   - API references
   - User guides
   - Cross-references and navigation
4. **Supports Multiple Profiles**: 
   - `quick` - Dry-run/preview mode
   - `standard` - Full documentation generation
   - `comprehensive` - Complete docs with all diagrams

### Key Features

#### 1. Documentation Generation
- **MkDocs Site**: Complete static site with navigation
- **Diagrams**: Architecture, workflow, system design (Mermaid format)
- **API References**: Auto-generated from code
- **User Guides**: Setup, operations, architecture explanations
- **Cross-References**: Automatic linking between pages

#### 2. Real Live Data Integration
- **Analytics Dashboards**: Generates HTML dashboards from analytics data
- **App-Specific Dashboards**: Per-application metrics and insights
- **Aggregate Dashboard**: Combined overview of all apps
- **Navigation Structure**: Returns nav YAML for MkDocs integration

#### 3. Execution Modes
- **Dry-Run**: Preview what would be generated (no file writes)
- **Live**: Full generation with file outputs
- **Component-Specific**: Generate only specific components (diagrams, features, etc.)

#### 4. Integration Points
- **CORTEX Operations**: Registered in `cortex-operations.yaml` under `generate_cortex_docs`
- **Natural Language Triggers**: 
  - "generate docs"
  - "build documentation"
  - "generate mkdocs"
  - "refresh documentation"
- **Admin-Only**: Requires `cortex-brain/admin/` directory (development repo)

### Dependencies

#### External Scripts
- `cortex-brain/admin/scripts/documentation/enterprise_documentation_orchestrator.py` (main generator)
- `analytics/real_live_data_generator.py` (Real Live Data generator)

#### CORTEX Components
- **Base Module**: `BaseOperationModule`, `OperationModuleMetadata`, `OperationResult`
- **Phase**: `OperationPhase.GENERATION`
- **Tags**: `["documentation", "mkdocs", "diagrams", "admin"]`

#### Python Libraries
- `subprocess` - Execute generator script
- `pathlib` - Path handling
- `re` - Parse generation statistics

### Current Status: DEPRECATED

**Reason for Deprecation:** Unknown (not documented in code)

**Likely Reasons:**
1. **Architectural Shift**: Move to component registry system (`documentation_component_registry.py`)
2. **Modularization**: Break monolithic orchestrator into 6 specialized generators:
   - DiagramsGenerator
   - FeatureListGenerator
   - MkDocsGenerator
   - ExecutiveSummaryGenerator
   - PublishDocsGenerator
   - OrchestrationDocsGenerator
3. **Simplified Integration**: Component registry provides cleaner API
4. **Better Testability**: Individual generators easier to test than monolithic orchestrator

---

## 🎯 Enhancement Proposal: `cortex_scribe`

### Vision

**`cortex_scribe`** will be CORTEX's **intelligent documentation chronicler** - a modern, modular orchestrator that:

1. **Unifies Documentation Generation**: Single entry point for all documentation tasks
2. **Leverages Component Registry**: Uses existing 6 generators with orchestration layer
3. **Intelligent Generation**: Context-aware decisions about what to generate
4. **Real-Time Updates**: Incremental generation for frequently-changed content
5. **Quality Assurance**: Built-in validation, broken link detection, consistency checks
6. **Multi-Format Output**: MkDocs, PDF, HTML, Markdown exports

### Why "cortex_scribe"?

**Scribe** perfectly captures the module's purpose:
- 📜 **Historical Role**: Scribes were chroniclers and documenters in ancient civilizations
- 🖋️ **Writing Focus**: Emphasizes documentation creation
- 🧠 **CORTEX Integration**: Clear naming convention (cortex_*)
- 🎯 **Single Responsibility**: One name, one purpose - write documentation

**Better Than:**
- ❌ "EnterpriseDocumentationOrchestratorModule" - Too verbose, "enterprise" is vague
- ❌ "DocGenerator" - Too generic, doesn't convey intelligence
- ❌ "DocumentationOrchestrator" - Accurate but lacks personality

---

## 🏗️ Proposed Architecture

### Module Structure

```
src/operations/modules/documentation/
├── __init__.py
├── cortex_scribe.py                      # Main orchestrator (NEW)
├── cortex_scribe_config.yaml             # Configuration (NEW)
└── components/                           # Component wrappers (NEW)
    ├── __init__.py
    ├── diagrams_component.py
    ├── feature_list_component.py
    ├── mkdocs_component.py
    ├── executive_summary_component.py
    ├── publish_component.py
    └── orchestration_docs_component.py
```

### Key Components

#### 1. `cortex_scribe.py` - Main Orchestrator

**Responsibilities:**
- Coordinate documentation generation workflow
- Manage component dependencies
- Handle execution profiles (quick/standard/comprehensive)
- Parse and return generation statistics
- Integrate Real Live Data generation
- Provide clean API for CORTEX operations system

**Class Structure:**
```python
class CortexScribe(BaseOperationModule):
    """
    CORTEX's intelligent documentation chronicler.
    
    Orchestrates all documentation generation through component registry,
    ensuring consistency, quality, and completeness.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.registry = create_default_registry()  # From component registry
        self.config = self._load_config(config_path)
        
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute documentation generation workflow."""
        
    def generate_all(self, profile: str = "standard") -> Dict[str, Any]:
        """Generate all documentation components."""
        
    def generate_component(self, component_id: str) -> Dict[str, Any]:
        """Generate specific documentation component."""
        
    def validate(self) -> ValidationResult:
        """Validate generated documentation."""
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics."""
```

#### 2. `cortex_scribe_config.yaml` - Configuration

**Contents:**
```yaml
profiles:
  quick:
    description: "Dry-run preview mode"
    dry_run: true
    components: []  # Validate only, no generation
    timeout: 30
    
  standard:
    description: "Full documentation generation"
    dry_run: false
    components:
      - diagrams
      - feature_list
      - executive_summary
      - mkdocs
    timeout: 120
    
  comprehensive:
    description: "Complete docs with all features"
    dry_run: false
    components:
      - diagrams
      - feature_list
      - executive_summary
      - orchestration_docs
      - mkdocs
      - publish
    timeout: 300

components:
  diagrams:
    enabled: true
    priority: 1
    
  feature_list:
    enabled: true
    priority: 2
    
  executive_summary:
    enabled: true
    priority: 3
    
  orchestration_docs:
    enabled: true
    priority: 4
    
  mkdocs:
    enabled: true
    priority: 5
    depends_on: [diagrams, feature_list, executive_summary]
    
  publish:
    enabled: false  # Requires manual approval
    priority: 6
    depends_on: [mkdocs]

real_live_data:
  enabled: true
  priority: 0  # Run first
  analytics_path: "cortex-brain/analytics"
  output_path: "docs/real-live-data"

validation:
  broken_links: true
  markdown_lint: true
  yaml_validation: true
  max_file_size_mb: 10

output:
  docs_dir: "docs"
  site_dir: "site"
  mkdocs_config: "mkdocs.yml"
```

#### 3. Component Wrappers

**Purpose:** Thin wrappers around component registry generators with orchestration capabilities.

**Example - `diagrams_component.py`:**
```python
class DiagramsComponent:
    """Wrapper for DiagramsGenerator with orchestration capabilities."""
    
    def __init__(self, registry):
        self.generator = registry.get_component("diagrams")
        
    def generate(self, context: Dict[str, Any]) -> ComponentResult:
        """Generate diagrams with statistics tracking."""
        
    def validate(self) -> ValidationResult:
        """Validate generated diagrams."""
        
    def get_statistics(self) -> Dict[str, int]:
        """Return generation statistics."""
```

---

## 📋 Enhancement Features

### 1. Intelligent Generation

**Context-Aware Decisions:**
- Detect what changed since last run
- Only regenerate affected components
- Skip expensive operations when possible

**Example:**
```python
# If only code changed, skip diagrams
if context.get("code_only_changes"):
    skip_components = ["diagrams"]
```

### 2. Incremental Updates

**Fast Updates:**
- Track last generation timestamp
- Generate only modified sections
- Merge with existing content

**Performance:**
- Full generation: 2-5 minutes
- Incremental update: 10-30 seconds

### 3. Quality Assurance

**Built-In Checks:**
- Broken link detection
- Markdown linting
- Image validation
- Cross-reference consistency
- File size limits

**Validation Report:**
```yaml
validation_results:
  broken_links: 0
  markdown_errors: 2
  missing_images: 0
  oversized_files: 1
  score: 95/100
```

### 4. Multi-Format Export

**Output Formats:**
- **MkDocs**: Static site (primary)
- **PDF**: Single-file documentation
- **HTML**: Standalone HTML pages
- **Markdown**: Raw markdown archive

### 5. Real-Time Progress

**Progress Tracking:**
```
🚀 cortex_scribe: Documentation Generation Started
  ├─ [1/6] Real Live Data... ✅ (2.3s)
  ├─ [2/6] Diagrams... ✅ (15.7s)
  ├─ [3/6] Feature List... ✅ (3.1s)
  ├─ [4/6] Executive Summary... ✅ (1.8s)
  ├─ [5/6] MkDocs Site... ✅ (8.4s)
  └─ [6/6] Validation... ✅ (2.2s)
✨ Generation Complete: 33.5s
```

---

## 📅 Implementation Plan

### Phase 1: Foundation (2-3 hours)

**Goal:** Create basic `cortex_scribe` structure

**Tasks:**
1. ✅ Create `src/operations/modules/documentation/cortex_scribe.py`
2. ✅ Create `cortex_scribe_config.yaml`
3. ✅ Implement `CortexScribe` class skeleton
4. ✅ Add component registry integration
5. ✅ Write unit tests (TDD RED phase)

**Acceptance Criteria:**
- [ ] `CortexScribe` class importable
- [ ] Config file loaded successfully
- [ ] Component registry accessible
- [ ] All tests pass (or fail correctly in RED phase)

### Phase 2: Core Orchestration (3-4 hours)

**Goal:** Implement documentation generation workflow

**Tasks:**
1. ✅ Implement `execute()` method
2. ✅ Implement `generate_all()` method
3. ✅ Implement `generate_component()` method
4. ✅ Add profile support (quick/standard/comprehensive)
5. ✅ Add Real Live Data integration
6. ✅ Add statistics parsing
7. ✅ Write integration tests

**Acceptance Criteria:**
- [ ] All profiles work correctly
- [ ] Components execute in correct order
- [ ] Statistics returned accurately
- [ ] Real Live Data generated
- [ ] Integration tests pass

### Phase 3: Quality Assurance (2-3 hours)

**Goal:** Add validation and quality checks

**Tasks:**
1. ✅ Implement `validate()` method
2. ✅ Add broken link detection
3. ✅ Add markdown linting
4. ✅ Add file size validation
5. ✅ Generate validation report
6. ✅ Write validation tests

**Acceptance Criteria:**
- [ ] Validation detects broken links
- [ ] Markdown errors caught
- [ ] File size limits enforced
- [ ] Validation report generated
- [ ] Validation tests pass

### Phase 4: Enhanced Features (3-4 hours)

**Goal:** Add incremental updates and progress tracking

**Tasks:**
1. ✅ Implement incremental generation
2. ✅ Add progress tracking with `ProgressRenderer`
3. ✅ Add multi-format export (PDF, HTML)
4. ✅ Add component dependencies resolution
5. ✅ Optimize performance
6. ✅ Write performance tests

**Acceptance Criteria:**
- [ ] Incremental updates 10x faster
- [ ] Progress displayed in real-time
- [ ] PDF/HTML exports work
- [ ] Dependencies resolved correctly
- [ ] Performance targets met (<5min full, <30s incremental)

### Phase 5: Integration & Migration (2-3 hours)

**Goal:** Integrate with CORTEX operations system

**Tasks:**
1. ✅ Update `cortex-operations.yaml`
2. ✅ Update natural language triggers
3. ✅ Migrate from deprecated module
4. ✅ Update documentation
5. ✅ Add CLI wrapper script
6. ✅ Test end-to-end workflow

**Acceptance Criteria:**
- [ ] Natural language triggers work
- [ ] CLI script executes successfully
- [ ] All existing workflows preserved
- [ ] Documentation updated
- [ ] E2E tests pass

### Phase 6: Documentation & Rollout (1-2 hours)

**Goal:** Document and deploy

**Tasks:**
1. ✅ Write comprehensive README
2. ✅ Add usage examples
3. ✅ Create migration guide
4. ✅ Update CHANGELOG
5. ✅ Deploy to production

**Acceptance Criteria:**
- [ ] README covers all features
- [ ] Migration guide complete
- [ ] CHANGELOG updated
- [ ] Production deployment successful

---

## 🌐 MkDocs Preview Server (Documentation Serving)

### Quick Reference

**🚀 To serve the documentation site locally:**

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m mkdocs serve
```

**📍 Preview URL:** `http://127.0.0.1:8000/CORTEX/`

### Serving Mechanism

#### Why `python3 -m mkdocs serve`?

**DO NOT use:** `mkdocs serve` (will fail with "command not found")

**USE:** `python3 -m mkdocs serve`

**Reason:** MkDocs is installed as a Python module, not a system command. Using `python3 -m` ensures we invoke the module through Python's module system.

#### URL Structure

**Base URL:** `http://127.0.0.1:8000/CORTEX/`

**Why `/CORTEX/` path?**
- Configured in `mkdocs.yml`: `site_url: https://asifhussain60.github.io/CORTEX`
- GitHub Pages deploys to `/{repo-name}/` subdirectory
- Local preview mirrors production URL structure
- Ensures links work identically in both environments

### Configuration

**MkDocs Config:** `mkdocs.yml` (project root)

```yaml
site_name: CORTEX
site_url: https://asifhussain60.github.io/CORTEX
docs_dir: docs/        # Documentation source folder
site_dir: site/        # Built site output folder
```

**Documentation Source:** `docs/` directory

**Key Files:**
- `mkdocs.yml` - Main configuration
- `docs/` - Documentation markdown files
- `site/` - Built static site (generated, do not commit)

### Prerequisites

**Required:**
```bash
pip install mkdocs mkdocs-material
```

**Verify Installation:**
```bash
python3 -m mkdocs --version
# Should output: mkdocs, version X.X.X
```

### Features

**Live Reload:**
- Server watches `docs/` and `mkdocs.yml` for changes
- Automatically rebuilds and refreshes browser
- Build time: ~2 seconds

**Build Information:**
```
INFO - Documentation built in 1.89 seconds
INFO - Serving on http://127.0.0.1:8000/CORTEX/
```

### Common Issues & Solutions

#### Issue 1: "command not found: mkdocs"

**Problem:** Trying to use `mkdocs serve` directly

**Solution:**
```bash
# ❌ Wrong
mkdocs serve

# ✅ Correct
python3 -m mkdocs serve
```

#### Issue 2: Missing Navigation Files

**Warnings:**
```
WARNING - A reference to 'index.md' is included in the 'nav' configuration,
          which is not found in the documentation files.
```

**Solution:**
- Create missing files in `docs/` directory
- Or remove references from `mkdocs.yml` nav section

#### Issue 3: Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python3 -m mkdocs serve -a 127.0.0.1:8001
```

### Integration with cortex_scribe

**How cortex_scribe Uses MkDocs:**

1. **Generation Phase:**
   - cortex_scribe generates markdown files in `docs/`
   - Updates `mkdocs.yml` navigation structure

2. **Preview Phase:**
   - User runs: `python3 -m mkdocs serve`
   - Reviews generated documentation at `http://127.0.0.1:8000/CORTEX/`

3. **Build Phase:**
   - cortex_scribe runs: `python3 -m mkdocs build`
   - Generates static site in `site/` directory

4. **Publish Phase:**
   - cortex_scribe runs: `python3 -m mkdocs gh-deploy`
   - Deploys to GitHub Pages

### Commands Cheat Sheet

```bash
# Preview locally (live reload)
python3 -m mkdocs serve

# Build static site
python3 -m mkdocs build

# Deploy to GitHub Pages
python3 -m mkdocs gh-deploy

# Clean build artifacts
python3 -m mkdocs build --clean

# Validate configuration
python3 -m mkdocs build --strict
```

### For AI Assistants

**When user asks to "serve the site" or "preview documentation":**

1. Navigate to project root: `cd /Users/asifhussain/PROJECTS/CORTEX`
2. Run: `python3 -m mkdocs serve` (as background process)
3. Open browser to: `http://127.0.0.1:8000/CORTEX/`
4. Inform user that live reload is enabled

**DO NOT:**
- Use `mkdocs serve` without `python3 -m`
- Assume port 8000 is available (check first)
- Commit `site/` directory (it's generated)

---

## 📊 Success Metrics

### Performance Targets

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Full Generation | 120s | <60s | 2x faster |
| Incremental Update | N/A | <30s | New capability |
| Component Generation | N/A | <10s | New capability |
| Memory Usage | Unknown | <500MB | Optimized |

### Quality Targets

| Metric | Target |
|--------|--------|
| Test Coverage | >90% |
| Code Quality | A (pylint 9.0+) |
| Documentation Coverage | 100% |
| Broken Links | 0 |
| Validation Score | >95/100 |

### User Experience

| Metric | Target |
|--------|--------|
| Setup Time | <5 minutes |
| Learning Curve | <30 minutes |
| Natural Language Success Rate | >95% |
| Error Recovery | Automatic |

---

## 🔍 Technical Considerations

### Backward Compatibility

**Deprecation Strategy:**
1. Keep `EnterpriseDocumentationOrchestratorModule` reference in `cortex-operations.yaml`
2. Add deprecation warning in old module
3. Redirect to `cortex_scribe` with migration message
4. Remove old module after 2 releases

**Migration Path:**
```python
# Old way (deprecated)
from src.operations.modules import EnterpriseDocumentationOrchestratorModule

# New way
from src.operations.modules.documentation import CortexScribe
```

### Testing Strategy

**Test Levels:**
1. **Unit Tests**: Individual methods, components
2. **Integration Tests**: Component interactions, registry
3. **E2E Tests**: Full generation workflow
4. **Performance Tests**: Speed, memory benchmarks
5. **Validation Tests**: Quality checks

**Test Coverage Target:** >90%

### Deployment Considerations

**Rollout Plan:**
1. **Development**: Test in CORTEX development repo
2. **Staging**: Test with sample apps
3. **Production**: Deploy to all users

**Rollback Plan:**
- Keep old module until validation complete
- Easy revert via `cortex-operations.yaml` switch

---

## 🚀 Next Steps

### Immediate Actions (After Approval)

1. ☐ **Create Feature Branch**: `feature/cortex-scribe`
2. ☐ **Set Up Module Structure**: Create directories and files
3. ☐ **Start Phase 1**: Implement foundation
4. ☐ **Write TDD Tests**: RED phase tests first

### Review & Approval Required

**Approval Needed From:**
- [ ] Project Owner (Asif Hussain)
- [ ] Architecture Review
- [ ] Integration Review

**Questions to Address:**
1. Is `cortex_scribe` the right name?
2. Should we keep Real Live Data integration?
3. What's the priority for multi-format export?
4. Timeline constraints?

---

## 📚 References

### Existing Components

- **Component Registry**: `src/operations/documentation_component_registry.py`
- **Generators**: `cortex-brain/admin/documentation/generators/`
- **Deprecated Module**: `cortex-brain/archives/deprecated-orchestrators/enterprise_documentation_orchestrator_module.py.deprecated`

### Documentation

- **Admin Docs**: `cortex-brain/admin/documentation/README.md`
- **Operations Config**: `cortex-operations.yaml` (line 1670-1750)
- **CORTEX Prompt**: `.github/prompts/CORTEX.prompt.md`

### Related Plans

- **PLAN-2025-11-21-ENTERPRISE-DOC-ORCHESTRATOR-IMAGE-INTEGRATION**: Image integration
- **DOCGEN-PHASE-2-COMPLETE**: Documentation generation consolidation

---

## 📝 Appendix

### Current Natural Language Triggers

From `cortex-operations.yaml`:
```yaml
natural_language:
  - generate docs
  - generate documentation
  - build documentation
  - build mkdocs
  - generate mkdocs
  - refresh documentation
  - regenerate docs
  - build cortex docs
  - generate cortex documentation
```

### Proposed Additional Triggers

```yaml
natural_language:
  - scribe
  - cortex scribe
  - write documentation
  - document the system
  - chronicle changes
  - update docs
  - refresh docs
```

### Component IDs (From Registry)

1. `diagrams` - DiagramsGenerator
2. `feature_list` - FeatureListGenerator
3. `mkdocs` - MkDocsGenerator
4. `executive_summary` - ExecutiveSummaryGenerator
5. `publish` - PublishDocsGenerator
6. `orchestration_docs` - OrchestrationDocsGenerator

---

## ✅ Plan Status

**Current Phase:** 🔍 Analysis Complete  
**Next Phase:** ⏳ Awaiting Approval  
**Estimated Total Time:** 13-19 hours (2-3 days)  
**Complexity:** MEDIUM-HIGH  
**Risk Level:** LOW (existing functionality, no breaking changes)

---

**Plan Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 13, 2025  
**Version:** 1.0

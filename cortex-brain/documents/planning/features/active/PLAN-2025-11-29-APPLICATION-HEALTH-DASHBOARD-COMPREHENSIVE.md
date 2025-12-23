# Application Health Dashboard - Comprehensive Implementation Plan

**Created:** 2025-11-29  
**Version:** 1.0.0  
**Status:** Active - Building Incrementally  
**Priority:** High  
**Target Release:** CORTEX 3.3.0

---

## 🎯 Executive Summary

**Purpose:** Build enterprise-grade Application Health Dashboard system with progressive crawling, multi-threaded analysis, and interactive D3.js visualization for production-scale applications.

**Context from Production Analysis:**
- **V5.ColdFusion:** Multi-application repository (~15+ apps, ~120K+ lines, ColdFusion/JavaScript/CSS)
- **TCBULK:** .NET Core application (~2,500+ files, ~65K+ lines, C#/TypeScript/HTML)
- **Reality Check:** These are "smallest apps" - real environments are 10-100x larger
- **Strategy Required:** Start with high-level scan, progressively dig deeper on user demand

**Key Innovations:**
1. **Progressive Crawling** - Fast initial scan (30 seconds), detailed on-demand analysis
2. **Multi-threaded Architecture** - Handle 100K+ files efficiently with parallel processing
3. **Smart Caching** - Build on CORTEX analysis, never re-analyze unchanged code
4. **Interactive Dashboard** - D3.js force-directed graphs, drill-down navigation, export capabilities

**Business Value:**
- **Speed:** 30-second overview vs 30-minute full scan (60x faster initial insight)
- **Scalability:** Handle enterprise apps with 1M+ lines of code
- **User Control:** Progressive detail on demand, not overwhelming data dumps
- **Integration:** Seamlessly extends CORTEX brain with application-specific knowledge

---

## 📊 Production Repository Analysis (Foundation)

### V5.ColdFusion Repository Structure

**Overview:**
- **Type:** Multi-application monorepo (each folder = independent application)
- **Entry Point:** `index.html` loads all applications
- **Scale:** ~15+ applications, ~120,000+ lines of code
- **Tech Stack:** ColdFusion (.cfm, .cfc), JavaScript, CSS
- **Key Insight:** Modular architecture, each app isolated but shared dependencies

**Sample Application Analysis (AdjustmentManager):**
- **Files:** ~500+ files
- **File Types:** 
  - ColdFusion: ~200 files (.cfm, .cfc)
  - JavaScript: ~100 files
  - CSS: ~50 files
  - HTML/Other: ~150 files
- **Complexity:** Business logic in ColdFusion, UI in JS/CSS, mixed concerns

**Crawler Requirements Identified:**
1. **Multi-root detection** - Must identify each application folder as separate entity
2. **Language diversity** - Handle ColdFusion, JavaScript, CSS, HTML in single scan
3. **Dependency tracking** - Shared components across applications
4. **Entry point detection** - index.html, Application.cfc, etc.

### TCBULK Repository Structure

**Overview:**
- **Type:** .NET Core multi-project solution
- **Structure:** 3 main projects (HQY.TCCARD, HQY.TCCARD.Database, HQY.TCCARD.Reports)
- **Scale:** ~2,500+ files, ~65,000+ lines of code
- **Tech Stack:** C# (.cs), TypeScript (.ts), HTML (.cshtml), SQL, JavaScript

**Project Breakdown:**
- **HQY.TCCARD:** Main application (~1,800 files)
  - C# backend: ~600 files
  - TypeScript: ~400 files
  - HTML/Razor: ~300 files
  - Configuration/Other: ~500 files
- **HQY.TCCARD.Database:** SQL migrations and stored procedures (~400 files)
- **HQY.TCCARD.Reports:** Reporting engine (~300 files)

**Key Architectural Patterns:**
- Solution/project structure (.sln, .csproj)
- NuGet package management (package.json for TypeScript)
- Razor views with server-side rendering
- Entity Framework database access
- Dependency injection patterns

**Crawler Requirements Identified:**
1. **Project hierarchy** - Must respect .NET solution structure
2. **Build artifacts** - Ignore bin/, obj/, node_modules/
3. **Configuration detection** - appsettings.json, web.config
4. **Framework detection** - .NET Core version, NuGet packages, npm packages

### Combined Insights for Crawler Design

**Scale Expectations:**
| Repository Type | Small | Medium | Large | Enterprise |
|----------------|-------|--------|-------|------------|
| Files | 2,500 | 10,000 | 50,000 | 250,000+ |
| Lines of Code | 65K | 250K | 1M | 5M+ |
| Languages | 3-5 | 5-10 | 10-15 | 15-20+ |
| Projects/Apps | 1-3 | 5-10 | 20-50 | 100+ |

**CORTEX Target:** Must handle "Medium" instantly (<30s), "Large" efficiently (<2 min), "Enterprise" progressively (<5 min high-level)

---

## 📋 Definition of Ready (DoR)

### Requirements Documentation
- [x] Production repository analysis complete (V5.ColdFusion, TCBULK)
- [x] Scale expectations defined (Small → Enterprise)
- [x] Progressive crawling strategy defined
- [x] D3.js dashboard requirements inherited from PLAN-2025-11-28
- [x] Multi-threading requirements documented
- [ ] User workflow scenarios documented
- [ ] CORTEX logo placement guidelines defined

### Dependencies
- [x] Existing Cache Dashboard (`src/operations/cache_dashboard.py`) ✅
- [x] Real-Time Metrics Dashboard (`src/operations/modules/data_integration/real_time_metrics_dashboard.py`) ✅
- [x] Progress Monitoring system (`src/utils/progress_decorator.py`) ✅
- [x] Enhancement Catalog (`src/operations/enhancement_catalog.py`) ✅
- [x] D3.js Dashboard Generator design (from PLAN-2025-11-28) ✅
- [ ] Language-specific parsers (Python, C#, JavaScript, ColdFusion, TypeScript)
- [ ] Complexity metrics algorithms (cyclomatic, cognitive, maintainability)

### Technical Design
- [x] Progressive crawling architecture (3 levels: Overview → Standard → Deep)
- [x] Multi-threaded worker pool design
- [x] Caching strategy (file hash-based, incremental updates)
- [x] Dashboard tab structure (5 tabs from D3.js spec)
- [ ] Language detection algorithm
- [ ] Framework detection algorithm
- [ ] Project structure detection algorithm
- [ ] Dependency graph construction algorithm

### Test Strategy
- [ ] TDD workflow planned for each component
- [ ] Performance benchmarks defined (<30s overview, <2min standard, <5min deep)
- [ ] Memory usage limits defined (<500MB for 50K files)
- [ ] Concurrent file processing tests (100+ workers)
- [ ] Cache invalidation tests
- [ ] Dashboard rendering tests

### Acceptance Criteria
- [ ] Progressive crawler handles 50K+ files in <2 minutes (standard scan)
- [ ] Multi-threaded architecture uses 80%+ CPU cores efficiently
- [ ] Caching reduces re-scan time by 90%+ for unchanged files
- [ ] Dashboard generates in <5 seconds with interactive D3.js visualization
- [ ] Language/framework detection accuracy >95%
- [ ] Memory usage <500MB for 50K file repository
- [ ] Export to PDF/PNG/PPTX functional
- [ ] CORTEX logo prominently displayed (header, not intrusive)
- [ ] 100% test pass rate (TDD enforced)

### Security Review (OWASP)

**Feature Type:** Application Analysis + File System Crawler + Interactive Dashboard

**A01 - Broken Access Control:**
- [x] Crawler only reads user's workspace files (no external access)
- [x] Dashboard access restricted to repository owner
- [x] No file system traversal outside workspace
- [x] Safe path handling (prevent ../../../ attacks)

**A03 - Injection:**
- [x] File content sanitization before analysis
- [x] Code snippet escaping in dashboard output
- [x] SQL injection prevention in metrics storage (parameterized queries)
- [x] XSS prevention in D3.js visualization (data sanitization)

**A05 - Security Misconfiguration:**
- [x] No execution of user code during analysis (static analysis only)
- [x] Secure temp file handling (auto-cleanup)
- [x] CSP headers in dashboard HTML
- [x] No sensitive data in error messages

**A06 - Vulnerable and Outdated Components:**
- [x] D3.js v7+ (latest stable)
- [x] Chart.js v4+ (latest stable)
- [x] Python dependencies pinned in requirements.txt
- [x] Regular dependency scanning (automated)

**A08 - Software and Data Integrity Failures:**
- [x] File hash verification (detect tampering)
- [x] Checksum validation for cached data
- [x] Audit logging for crawler operations
- [x] Version tracking for analysis results

**A09 - Security Logging and Monitoring Failures:**
- [x] Crawler operations logged to Tier 3
- [x] Anomaly detection (unusual file patterns)
- [x] Performance metrics tracked
- [x] Error logging with context (no sensitive data)

---

## 🏗️ Architecture Overview

### System Components

```
Application Health Dashboard System
│
├─ Progressive Crawler Engine (Multi-threaded)
│  ├─ CrawlerOrchestrator (Main Coordinator)
│  │  ├─ Scan Level Router (Overview/Standard/Deep)
│  │  ├─ Worker Pool Manager (ThreadPoolExecutor)
│  │  ├─ Progress Reporter (via @with_progress)
│  │  └─ Cache Invalidation Logic
│  │
│  ├─ Language-Specific Analyzers
│  │  ├─ PythonAnalyzer (ast module)
│  │  ├─ CSharpAnalyzer (roslyn patterns)
│  │  ├─ JavaScriptAnalyzer (esprima/acorn)
│  │  ├─ TypeScriptAnalyzer (ts-morph patterns)
│  │  ├─ ColdFusionAnalyzer (regex + tag parsing)
│  │  └─ GenericAnalyzer (metrics only)
│  │
│  ├─ Framework Detectors
│  │  ├─ DotNetDetector (.sln, .csproj, packages.config)
│  │  ├─ NodeDetector (package.json, node_modules)
│  │  ├─ ReactDetector (jsx, react imports)
│  │  ├─ AngularDetector (angular.json)
│  │  ├─ BlazorDetector (.razor files)
│  │  └─ ColdFusionDetector (Application.cfc)
│  │
│  └─ Metrics Calculators
│     ├─ ComplexityCalculator (cyclomatic, cognitive)
│     ├─ MaintainabilityScorer (Halstead, MI)
│     ├─ DependencyGraphBuilder (import/using analysis)
│     └─ CodeSmellDetector (patterns, anti-patterns)
│
├─ Caching System (Hash-based)
│  ├─ FileHashCache (SHA256 per file)
│  ├─ AnalysisResultCache (Tier 3 SQLite)
│  ├─ IncrementalUpdateDetector
│  └─ CacheEvictionPolicy (LRU + TTL)
│
├─ Dashboard Generator (D3.js + Interactive)
│  ├─ InteractiveDashboardGenerator (from PLAN-2025-11-28)
│  │  ├─ 5-Tab Structure Renderer
│  │  ├─ D3.js Force-Directed Graph
│  │  ├─ Chart.js Visualizations
│  │  ├─ Mermaid Diagram Embedding
│  │  └─ Export Engine (PDF/PNG/PPTX)
│  │
│  ├─ CORTEX Branding Module
│  │  ├─ Logo Placement (header, SVG format)
│  │  ├─ Color Scheme (CORTEX brand colors)
│  │  └─ Attribution Footer
│  │
│  └─ Data Serializers
│     ├─ JSONSerializer (D3.js data format)
│     ├─ GraphMLSerializer (dependency graphs)
│     └─ CSVSerializer (tabular data export)
│
└─ Integration Layer
   ├─ Tier 3 Storage (application_health schema)
   ├─ Enhancement Catalog Integration
   ├─ Progress Monitoring Integration
   └─ CORTEX Brain Context Injection
```

### Progressive Crawling Strategy

```
User Request: "show health dashboard"
     ↓
LEVEL 1: OVERVIEW SCAN (30 seconds)
├─ File system walk (parallel, 100 workers)
├─ Count files by extension
├─ Detect project structure (solutions, folders)
├─ Identify entry points (main files)
├─ Calculate basic metrics (LOC, file count)
└─ Generate high-level dashboard
     ↓
Dashboard shows: "Click for detailed analysis" button
     ↓
User clicks: "Analyze Quality"
     ↓
LEVEL 2: STANDARD SCAN (2 minutes)
├─ Parse 20% of files (sampling strategy)
├─ Full analysis of entry points
├─ Complexity metrics (cyclomatic)
├─ Basic code smell detection
├─ Framework/library detection
└─ Update dashboard with quality metrics
     ↓
Dashboard shows: "Click for deep security analysis" button
     ↓
User clicks: "Security Audit"
     ↓
LEVEL 3: DEEP SCAN (5 minutes)
├─ Parse 100% of files (cached results reused)
├─ OWASP security pattern detection
├─ Advanced complexity analysis (cognitive)
├─ Dependency vulnerability scanning
├─ Performance hotspot detection
└─ Update dashboard with security/performance insights
```

### Data Flow

```
File System
     ↓
CrawlerOrchestrator.scan(level="overview")
     ↓
ThreadPoolExecutor (100 workers)
     ├─ Worker 1: File 1-100
     ├─ Worker 2: File 101-200
     ├─ ...
     └─ Worker 100: File 9901-10000
          ↓
FileHashCache.check(file_path)
     ├─ Cache Hit → Retrieve cached analysis
     └─ Cache Miss → Analyze file
          ↓
LanguageAnalyzer.analyze(file_content)
     ↓
MetricsCalculator.compute(ast_tree)
     ↓
AnalysisResultCache.store(file_hash, metrics)
     ↓
CrawlerOrchestrator.aggregate_results()
     ↓
InteractiveDashboardGenerator.generate(aggregated_data)
     ↓
HTML Dashboard (with D3.js) → Browser
```

### Database Schema (Tier 3 Extension)

```sql
-- Application Health Storage
CREATE TABLE application_scans (
    scan_id TEXT PRIMARY KEY,
    repository_path TEXT NOT NULL,
    scan_level TEXT CHECK(scan_level IN ('overview', 'standard', 'deep')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    total_files INTEGER,
    total_lines INTEGER,
    languages JSON,  -- {"python": 1000, "csharp": 500}
    frameworks JSON,  -- ["dotnet-core", "react"]
    overall_score REAL,  -- 0-100
    metadata JSON
);

CREATE TABLE file_analysis_cache (
    file_path TEXT PRIMARY KEY,
    file_hash TEXT NOT NULL,  -- SHA256
    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language TEXT,
    lines_of_code INTEGER,
    complexity_cyclomatic INTEGER,
    complexity_cognitive INTEGER,
    maintainability_index REAL,
    code_smells JSON,  -- ["long_method", "god_class"]
    security_issues JSON,  -- OWASP categories
    analysis_level TEXT CHECK(analysis_level IN ('overview', 'standard', 'deep')),
    raw_metrics JSON
);

CREATE TABLE dependency_graph (
    scan_id TEXT,
    source_file TEXT,
    target_file TEXT,
    dependency_type TEXT,  -- "import", "using", "include"
    FOREIGN KEY (scan_id) REFERENCES application_scans(scan_id)
);

CREATE INDEX idx_file_hash ON file_analysis_cache(file_hash);
CREATE INDEX idx_scan_id ON dependency_graph(scan_id);
```

---

## 📐 Phase Breakdown

### ☐ PHASE 1: Progressive Crawler Core (Week 1)

**Duration:** 5 days (40 hours)  
**Goal:** Build multi-threaded crawler with 3-level progressive scanning

---

#### 1.1: Crawler Orchestrator Foundation (2 days, 16 hours)

**Tasks:**

**1.1.1: Create CrawlerOrchestrator Class** (6 hours)
- Design main orchestrator with scan level routing
- Implement ThreadPoolExecutor wrapper (auto-detect CPU cores, default 100 workers)
- Add progress monitoring integration (@with_progress decorator)
- Implement scan level strategy (overview/standard/deep)
- Create result aggregation logic
- **TDD Workflow:**
  - RED: Test fails - no CrawlerOrchestrator class
  - GREEN: Minimal orchestrator with single-threaded file walk
  - REFACTOR: Add multi-threading, optimize performance
- **Files:**
  - `src/crawlers/crawler_orchestrator.py` (500 lines)
  - `tests/crawlers/test_crawler_orchestrator.py` (400 lines)
- **Tests:** 12 tests (initialization, scan routing, thread management, error handling)

**1.1.2: File System Walker** (4 hours)
- Parallel file discovery with path filtering
- .gitignore respect (honor user's ignore patterns)
- Ignore patterns for build artifacts (bin/, obj/, node_modules/, .vs/, etc.)
- File extension detection and categorization
- Entry point identification (main.py, Program.cs, index.html, Application.cfc)
- **TDD Workflow:**
  - RED: Test fails - walker doesn't respect .gitignore
  - GREEN: Walker filters files correctly
  - REFACTOR: Optimize path matching, reduce memory usage
- **Files:**
  - `src/crawlers/file_system_walker.py` (350 lines)
  - `tests/crawlers/test_file_system_walker.py` (300 lines)
- **Tests:** 10 tests (filtering, performance, .gitignore, entry points)

**1.1.3: Scan Level Strategy Implementation** (6 hours)
- Overview strategy: Count files, detect structure, no parsing (30s target)
- Standard strategy: Sample 20% of files, parse entry points (2min target)
- Deep strategy: Parse 100% of files with full analysis (5min target)
- Implement sampling algorithm (stratified by file type)
- Add level transition logic (user request → deeper scan)
- **TDD Workflow:**
  - RED: Test fails - all levels parse 100% (too slow)
  - GREEN: Sampling strategy reduces scan time by 80%
  - REFACTOR: Optimize sampling algorithm, ensure representative coverage
- **Files:**
  - `src/crawlers/scan_strategies.py` (400 lines)
  - `tests/crawlers/test_scan_strategies.py` (350 lines)
- **Tests:** 15 tests (overview speed, sampling accuracy, deep completeness)

**Acceptance Criteria:**
- ✅ Orchestrator spawns worker threads (80%+ CPU utilization)
- ✅ Overview scan completes in <30s for 10K files
- ✅ Standard scan completes in <2min for 10K files
- ✅ Deep scan completes in <5min for 10K files
- ✅ Progress monitoring shows accurate ETA
- ✅ Memory usage <200MB during overview scan
- ✅ All tests pass (37 total)

---

#### 1.2: Language-Specific Analyzers (3 days, 24 hours)

**Tasks:**

**1.2.1: Python Analyzer** (4 hours)
- Use `ast` module for syntax tree parsing
- Extract classes, functions, imports
- Calculate cyclomatic complexity (McCabe)
- Detect code smells (long methods, god classes)
- Identify security patterns (eval, exec, pickle usage)
- **TDD Workflow:**
  - RED: Test fails - analyzer doesn't detect imports
  - GREEN: Parser extracts classes/functions/imports
  - REFACTOR: Add complexity calculation, optimize parsing
- **Files:**
  - `src/crawlers/analyzers/python_analyzer.py` (450 lines)
  - `tests/crawlers/analyzers/test_python_analyzer.py` (400 lines)
- **Tests:** 18 tests (parsing, complexity, smells, security)

**1.2.2: C# Analyzer** (5 hours)
- Regex-based parsing for classes/methods/usings (no Roslyn dependency)
- Extract namespaces, classes, methods, properties
- Detect LINQ usage patterns
- Identify async/await patterns
- Calculate basic complexity metrics
- **TDD Workflow:**
  - RED: Test fails - regex doesn't match generic classes
  - GREEN: Parser handles generics, interfaces, inheritance
  - REFACTOR: Optimize regex patterns, add edge cases
- **Files:**
  - `src/crawlers/analyzers/csharp_analyzer.py` (500 lines)
  - `tests/crawlers/analyzers/test_csharp_analyzer.py` (450 lines)
- **Tests:** 20 tests (class detection, generics, async patterns)

**1.2.3: JavaScript/TypeScript Analyzer** (5 hours)
- Regex-based parsing (fallback to esprima if available)
- Extract functions, classes, imports/requires
- Detect React components (class/functional)
- Identify ES6+ features (arrow functions, destructuring)
- Calculate complexity for arrow functions
- **TDD Workflow:**
  - RED: Test fails - doesn't detect arrow functions
  - GREEN: Parser handles ES6+ syntax
  - REFACTOR: Add TypeScript type extraction, optimize
- **Files:**
  - `src/crawlers/analyzers/javascript_analyzer.py` (550 lines)
  - `tests/crawlers/analyzers/test_javascript_analyzer.py` (500 lines)
- **Tests:** 22 tests (ES6 features, React, TypeScript, imports)

**1.2.4: ColdFusion Analyzer** (4 hours)
- Custom tag-based parser (<cffunction>, <cfcomponent>)
- Extract components, functions, queries
- Detect SQL injection risks (unparameterized queries)
- Identify ColdFusion-specific patterns
- Calculate basic metrics (LOC, function count)
- **TDD Workflow:**
  - RED: Test fails - tag parser doesn't handle nested tags
  - GREEN: Parser extracts components/functions
  - REFACTOR: Add security pattern detection
- **Files:**
  - `src/crawlers/analyzers/coldfusion_analyzer.py` (400 lines)
  - `tests/crawlers/analyzers/test_coldfusion_analyzer.py` (350 lines)
- **Tests:** 16 tests (tag parsing, SQL detection, components)

**1.2.5: Generic Analyzer** (3 hours)
- Fallback for unsupported languages
- Line-of-code counting (LOC, SLOC, comments)
- Basic file metrics (size, line count, blank lines)
- No parsing, just statistical analysis
- **TDD Workflow:**
  - RED: Test fails - comment detection incorrect
  - GREEN: Accurate LOC/SLOC/comment counting
  - REFACTOR: Add language-specific comment patterns
- **Files:**
  - `src/crawlers/analyzers/generic_analyzer.py` (250 lines)
  - `tests/crawlers/analyzers/test_generic_analyzer.py` (200 lines)
- **Tests:** 10 tests (LOC accuracy, comment detection)

**1.2.6: Analyzer Factory** (3 hours)
- Auto-select analyzer based on file extension
- Fallback chain: Specific → Generic
- Performance optimization (analyzer instance pooling)
- Error handling (malformed files)
- **Files:**
  - `src/crawlers/analyzers/analyzer_factory.py` (200 lines)
  - `tests/crawlers/analyzers/test_analyzer_factory.py` (150 lines)
- **Tests:** 8 tests (selection, fallback, pooling)

**Acceptance Criteria:**
- ✅ Python analyzer handles 95%+ valid Python files
- ✅ C# analyzer detects generics, async/await, LINQ
- ✅ JavaScript analyzer supports ES6+ and React
- ✅ ColdFusion analyzer extracts components/functions
- ✅ Generic analyzer provides accurate LOC metrics
- ✅ All analyzers complete in <50ms per file average
- ✅ All tests pass (94 total)

---

### ☐ PHASE 2: Caching & Performance Optimization (Week 2)

**Duration:** 5 days (40 hours)  
**Goal:** Implement hash-based caching for 90%+ scan time reduction on re-scans

---

#### 2.1: Hash-Based Cache System (2 days, 16 hours)

**Tasks:**

**2.1.1: File Hash Cache** (5 hours)
- SHA256 hash calculation per file (content-based)
- Tier 3 SQLite storage (file_analysis_cache table)
- Cache lookup by hash (O(1) average)
- Automatic cache invalidation on file modification
- TTL-based eviction (30-day default)
- **TDD Workflow:**
  - RED: Test fails - cache doesn't invalidate on file change
  - GREEN: Hash mismatch triggers re-analysis
  - REFACTOR: Optimize hash calculation (read in chunks)
- **Files:**
  - `src/crawlers/cache/file_hash_cache.py` (350 lines)
  - `tests/crawlers/cache/test_file_hash_cache.py` (300 lines)
- **Tests:** 12 tests (hash accuracy, invalidation, performance)

**2.1.2: Analysis Result Cache** (6 hours)
- Store analysis results with file hash as key
- JSON serialization for complex metrics
- Compression for large results (gzip)
- Partial result caching (overview vs deep)
- Cache hit/miss metrics tracking
- **TDD Workflow:**
  - RED: Test fails - compression doesn't reduce size
  - GREEN: Gzip reduces cache size by 60%+
  - REFACTOR: Optimize serialization, add compression threshold
- **Files:**
  - `src/crawlers/cache/analysis_result_cache.py` (400 lines)
  - `tests/crawlers/cache/test_analysis_result_cache.py` (350 lines)
- **Tests:** 15 tests (storage, retrieval, compression, metrics)

**2.1.3: Incremental Update Detector** (5 hours)
- Git integration (detect changed files since last scan)
- Fallback: filesystem timestamp comparison
- Dependency invalidation (if A imports B, B change invalidates A)
- Smart re-scan (only analyze changed files + dependencies)
- **TDD Workflow:**
  - RED: Test fails - doesn't detect dependency changes
  - GREEN: Dependency graph invalidation works
  - REFACTOR: Optimize graph traversal, add circular dependency detection
- **Files:**
  - `src/crawlers/cache/incremental_update_detector.py` (450 lines)
  - `tests/crawlers/cache/test_incremental_update_detector.py` (400 lines)
- **Tests:** 18 tests (git integration, timestamps, dependencies)

**Acceptance Criteria:**
- ✅ Cache hit rate >90% for unchanged files
- ✅ Re-scan time reduced by 90%+ (10 min → 1 min)
- ✅ Cache storage <1MB per 1K files analyzed
- ✅ Incremental updates detect dependency changes
- ✅ Hash calculation adds <10ms overhead per file
- ✅ All tests pass (45 total)

---

#### 2.2: Framework & Project Detection (3 days, 24 hours)

**Tasks:**

**2.2.1: .NET Framework Detector** (5 hours)
- Scan for .sln, .csproj files
- Parse project files for framework version (.NET Core, .NET Framework)
- Extract NuGet package dependencies (packages.config, .csproj)
- Detect project type (Web, Console, Class Library, Test)
- Identify Entity Framework usage
- **TDD Workflow:**
  - RED: Test fails - doesn't detect .NET Core vs Framework
  - GREEN: Parser distinguishes framework versions
  - REFACTOR: Add package dependency graph
- **Files:**
  - `src/crawlers/detectors/dotnet_detector.py` (400 lines)
  - `tests/crawlers/detectors/test_dotnet_detector.py` (350 lines)
- **Tests:** 16 tests (solution parsing, framework detection, packages)

**2.2.2: Node.js Framework Detector** (4 hours)
- Parse package.json for dependencies
- Detect React (react, react-dom dependencies)
- Detect Angular (angular.json, @angular/* packages)
- Detect Vue (vue, vue-loader)
- Identify Express, Next.js, Vite, Webpack
- **TDD Workflow:**
  - RED: Test fails - misses devDependencies
  - GREEN: Parser checks both dependencies and devDependencies
  - REFACTOR: Add version detection, framework scoring
- **Files:**
  - `src/crawlers/detectors/node_detector.py` (350 lines)
  - `tests/crawlers/detectors/test_node_detector.py` (300 lines)
- **Tests:** 14 tests (package.json parsing, framework detection)

**2.2.3: ColdFusion Application Detector** (3 hours)
- Detect Application.cfc/Application.cfm
- Extract application settings (name, session management)
- Identify ORM usage (cfproperty, entityName)
- Detect CF version features
- **TDD Workflow:**
  - RED: Test fails - doesn't extract application name
  - GREEN: Parser extracts settings correctly
  - REFACTOR: Add ORM detection, optimize parsing
- **Files:**
  - `src/crawlers/detectors/coldfusion_detector.py` (300 lines)
  - `tests/crawlers/detectors/test_coldfusion_detector.py` (250 lines)
- **Tests:** 12 tests (application settings, ORM, version features)

**2.2.4: Build System Detector** (4 hours)
- Detect MSBuild (.csproj, .sln)
- Detect npm/yarn (package.json, package-lock.json, yarn.lock)
- Detect Maven (pom.xml)
- Detect Gradle (build.gradle)
- Detect Make (Makefile)
- **Files:**
  - `src/crawlers/detectors/build_system_detector.py` (350 lines)
  - `tests/crawlers/detectors/test_build_system_detector.py` (300 lines)
- **Tests:** 14 tests (build file detection, parsing)

**2.2.5: Project Structure Analyzer** (5 hours)
- Identify project root(s) (mono-repo vs single project)
- Detect folder conventions (src/, lib/, tests/, docs/)
- Map file organization patterns
- Identify entry points (main files, startup files)
- Build project hierarchy tree
- **TDD Workflow:**
  - RED: Test fails - mono-repo detection misses nested projects
  - GREEN: Recursive project detection works
  - REFACTOR: Optimize tree building, add visualization data
- **Files:**
  - `src/crawlers/detectors/project_structure_analyzer.py` (500 lines)
  - `tests/crawlers/detectors/test_project_structure_analyzer.py` (450 lines)
- **Tests:** 20 tests (mono-repo, hierarchy, entry points)

**2.2.6: Detector Orchestrator** (3 hours)
- Run all detectors in parallel
- Aggregate detection results
- Confidence scoring (multiple detectors agree)
- Framework version resolution
- **Files:**
  - `src/crawlers/detectors/detector_orchestrator.py` (300 lines)
  - `tests/crawlers/detectors/test_detector_orchestrator.py` (250 lines)
- **Tests:** 10 tests (parallel execution, aggregation, confidence)

**Acceptance Criteria:**
- ✅ .NET detection accuracy >95% (.NET Core, Framework, Standard)
- ✅ Node.js framework detection accuracy >90% (React, Angular, Vue, etc.)
- ✅ ColdFusion application settings extracted correctly
- ✅ Build system detection accuracy >95%
- ✅ Mono-repo support (detect multiple projects)
- ✅ Detection completes in <5s for 10K files
- ✅ All tests pass (86 total)

---

### ☐ PHASE 3: Metrics & Quality Analysis (Week 3)

**Duration:** 5 days (40 hours)  
**Goal:** Calculate code quality metrics, complexity, maintainability, and security patterns

---

#### 3.1: Complexity Calculators (2 days, 16 hours)

**Tasks:**

**3.1.1: Cyclomatic Complexity Calculator** (6 hours)
- McCabe complexity algorithm implementation
- Control flow graph construction
- Branch counting (if, for, while, switch, try/catch)
- Per-function complexity scoring
- File-level aggregation
- **TDD Workflow:**
  - RED: Test fails - nested loops not counted correctly
  - GREEN: Accurate complexity for nested control structures
  - REFACTOR: Optimize graph traversal, add visualization data
- **Files:**
  - `src/crawlers/metrics/cyclomatic_complexity.py` (400 lines)
  - `tests/crawlers/metrics/test_cyclomatic_complexity.py` (350 lines)
- **Tests:** 15 tests (if/for/while, nesting, edge cases)

**3.1.2: Cognitive Complexity Calculator** (5 hours)
- SonarSource cognitive complexity algorithm
- Nesting penalty calculation
- Recursion detection
- Readability scoring
- Comparison with cyclomatic complexity
- **TDD Workflow:**
  - RED: Test fails - nesting penalty incorrect
  - GREEN: Nesting increases complexity score appropriately
  - REFACTOR: Add language-specific adjustments
- **Files:**
  - `src/crawlers/metrics/cognitive_complexity.py` (450 lines)
  - `tests/crawlers/metrics/test_cognitive_complexity.py` (400 lines)
- **Tests:** 18 tests (nesting, recursion, readability)

**3.1.3: Halstead Metrics Calculator** (5 hours)
- Operator/operand counting
- Volume, difficulty, effort calculation
- Estimated bugs (Halstead formula)
- Time to understand estimation
- **Files:**
  - `src/crawlers/metrics/halstead_metrics.py` (350 lines)
  - `tests/crawlers/metrics/test_halstead_metrics.py` (300 lines)
- **Tests:** 12 tests (counting accuracy, formula validation)

**Acceptance Criteria:**
- ✅ Cyclomatic complexity matches industry tools (±1)
- ✅ Cognitive complexity penalizes nesting correctly
- ✅ Halstead metrics predict bug-prone code accurately
- ✅ Calculation completes in <20ms per function
- ✅ All tests pass (45 total)

---

#### 3.2: Maintainability & Quality Scoring (2 days, 16 hours)

**Tasks:**

**3.2.1: Maintainability Index Calculator** (6 hours)
- Microsoft Maintainability Index formula
- Halstead volume integration
- Cyclomatic complexity integration
- LOC normalization
- Score interpretation (0-100 scale)
- **TDD Workflow:**
  - RED: Test fails - MI score out of range
  - GREEN: Scores normalized to 0-100
  - REFACTOR: Add language-specific adjustments
- **Files:**
  - `src/crawlers/metrics/maintainability_index.py` (350 lines)
  - `tests/crawlers/metrics/test_maintainability_index.py` (300 lines)
- **Tests:** 14 tests (formula, normalization, edge cases)

**3.2.2: Code Smell Detector** (10 hours)
- Long method detection (>50 LOC threshold)
- God class detection (>500 LOC, >10 methods)
- Duplicate code detection (token-based similarity)
- Magic number detection
- Deep nesting detection (>4 levels)
- Long parameter list (>5 parameters)
- Feature envy (excessive coupling)
- **TDD Workflow:**
  - RED: Test fails - duplicate detection has false positives
  - GREEN: Similarity threshold tuned to reduce false positives
  - REFACTOR: Add configurable thresholds, pattern matching
- **Files:**
  - `src/crawlers/metrics/code_smell_detector.py` (600 lines)
  - `tests/crawlers/metrics/test_code_smell_detector.py` (550 lines)
- **Tests:** 25 tests (each smell type, thresholds, false positives)

**Acceptance Criteria:**
- ✅ Maintainability Index aligns with Visual Studio metrics
- ✅ Code smell detection accuracy >85%
- ✅ False positive rate <10%
- ✅ Analysis completes in <50ms per file
- ✅ All tests pass (39 total)

---

#### 3.3: Security Pattern Detection (1 day, 8 hours)

**Tasks:**

**3.3.1: OWASP Pattern Detector** (8 hours)
- **A01 - Broken Access Control**
  - Missing authorization checks
  - Insecure direct object references
- **A03 - Injection**
  - SQL injection risks (string concatenation in queries)
  - Command injection (exec, shell commands)
  - XSS vulnerabilities (unescaped output)
- **A05 - Security Misconfiguration**
  - Hardcoded credentials
  - Debug mode enabled
  - Verbose error messages
- **A07 - Authentication Failures**
  - Weak password validation
  - Missing MFA
  - Insecure session management
- **TDD Workflow:**
  - RED: Test fails - SQL injection not detected
  - GREEN: Pattern matching detects string concatenation in queries
  - REFACTOR: Add context-aware detection, reduce false positives
- **Files:**
  - `src/crawlers/security/owasp_pattern_detector.py` (700 lines)
  - `tests/crawlers/security/test_owasp_pattern_detector.py` (650 lines)
- **Tests:** 30 tests (each OWASP category, true/false positives)

**Acceptance Criteria:**
- ✅ Detects 80%+ of common OWASP vulnerabilities
- ✅ False positive rate <15% (acceptable for security)
- ✅ Severity scoring (Critical/High/Medium/Low)
- ✅ Analysis completes in <100ms per file
- ✅ All tests pass (30 total)

---

### ☐ PHASE 4: Interactive Dashboard Generation (Week 4)

**Duration:** 5 days (40 hours)  
**Goal:** Generate D3.js interactive dashboard with CORTEX branding and export capabilities

---

#### 4.1: Dashboard Generator Integration (2 days, 16 hours)

**Tasks:**

**4.1.1: Reuse Existing InteractiveDashboardGenerator** (4 hours)
- Import from PLAN-2025-11-28 implementation
- Adapt for application health data (vs admin operations)
- Validate 5-tab structure compatibility
- Ensure export functionality works
- **Files:**
  - Reuse: `src/utils/interactive_dashboard_generator.py`
  - New: `src/crawlers/dashboard/application_health_dashboard_adapter.py` (250 lines)
  - Tests: `tests/crawlers/dashboard/test_application_health_dashboard_adapter.py` (200 lines)
- **Tests:** 8 tests (data transformation, tab population)

**4.1.2: Application Health Data Serializer** (6 hours)
- Convert scan results to D3.js JSON format
- Build dependency graph data (nodes, edges)
- Aggregate metrics by file type, folder, module
- Calculate summary statistics
- Generate time-series data (if multiple scans exist)
- **TDD Workflow:**
  - RED: Test fails - graph data missing edge weights
  - GREEN: Edge weights calculated from dependency strength
  - REFACTOR: Optimize serialization, add compression
- **Files:**
  - `src/crawlers/dashboard/data_serializer.py` (500 lines)
  - `tests/crawlers/dashboard/test_data_serializer.py` (450 lines)
- **Tests:** 20 tests (serialization, aggregation, graph data)

**4.1.3: CORTEX Branding Module** (6 hours)
- SVG logo integration (header placement, 120x40px)
- Brand color scheme application (primary: #007ACC, accent: #68217A)
- Attribution footer ("Powered by CORTEX")
- Subtle branding (not intrusive, professional)
- Logo link to CORTEX GitHub repo
- **Design Guidelines:**
  - Logo: Header right corner, transparent background
  - Colors: Use for accents, not overwhelming
  - Footer: Small, bottom-right, "Powered by CORTEX | github.com/asifhussain60/CORTEX"
- **Files:**
  - `src/crawlers/dashboard/cortex_branding.py` (200 lines)
  - `templates/static/images/cortex-logo.svg` (SVG file)
  - `tests/crawlers/dashboard/test_cortex_branding.py` (150 lines)
- **Tests:** 6 tests (logo injection, color scheme, footer)

**Acceptance Criteria:**
- ✅ Dashboard generator reused (no duplication)
- ✅ Application health data fits 5-tab structure
- ✅ CORTEX logo prominently displayed (header)
- ✅ Brand colors applied consistently
- ✅ Attribution footer present
- ✅ All tests pass (34 total)

---

#### 4.2: Interactive Visualization Components (2 days, 16 hours)

**Tasks:**

**4.2.1: D3.js Force-Directed Dependency Graph** (8 hours)
- Implement force simulation (d3.forceSimulation)
- Node sizing by file LOC
- Node coloring by complexity score (green → yellow → red)
- Edge thickness by dependency strength
- Zoom/pan controls (d3.zoom)
- Hover tooltips (file name, metrics, path)
- Click navigation (expand file details)
- **Interactive Features:**
  - Drag nodes to rearrange
  - Double-click to highlight dependencies
  - Filter by file type, complexity threshold
- **Files:**
  - `templates/static/js/dependency-graph-d3.js` (800 lines)
  - `tests/frontend/test_dependency_graph.js` (400 lines - Jest)
- **Tests:** 15 tests (rendering, interactions, filters)

**4.2.2: Chart.js Metric Visualizations** (8 hours)
- Bar chart: Files by complexity score
- Pie chart: Language distribution
- Line chart: Complexity over time (if historical data)
- Radar chart: Quality dimensions (maintainability, security, performance)
- Horizontal bar: Top 10 most complex files
- **Interactive Features:**
  - Drill-down from chart to file list
  - Tooltips with detailed metrics
  - Legend filtering (click to hide/show)
- **Files:**
  - `templates/static/js/metric-charts.js` (600 lines)
  - `tests/frontend/test_metric_charts.js` (350 lines - Jest)
- **Tests:** 12 tests (chart rendering, drill-down, tooltips)

**Acceptance Criteria:**
- ✅ Dependency graph renders 500+ nodes smoothly (60fps)
- ✅ Charts update in <100ms on filter change
- ✅ Drill-down navigation works (chart → file list → file detail)
- ✅ All interactions functional (zoom, pan, drag, click)
- ✅ All tests pass (27 total)

---

#### 4.3: Tab Structure Implementation (1 day, 8 hours)

**Tasks:**

**4.3.1: Tab 1 - Overview** (2 hours)
- **Narrative Intelligence Section:**
  - Auto-generated summary (GPT-style, using metrics)
  - Key insights (e.g., "73% of complexity in 3 files")
  - Risk assessment ("High: 12 security issues found")
- **Key Metrics Cards:**
  - Total files, LOC, languages
  - Overall quality score (0-100)
  - Complexity distribution (pie chart)
  - Framework/library list
- **Files:**
  - `templates/dashboard-tabs/tab-overview.html` (300 lines)
- **Tests:** Covered by integration tests

**4.3.2: Tab 2 - Visualizations** (2 hours)
- D3.js dependency graph (full-screen)
- Chart.js metric visualizations (grid layout)
- Filter controls (file type, complexity, security level)
- **Files:**
  - `templates/dashboard-tabs/tab-visualizations.html` (400 lines)
- **Tests:** Covered by component tests

**4.3.3: Tab 3 - Code Quality** (2 hours)
- **Quality Metrics Table:**
  - File path, LOC, complexity, maintainability index
  - Sortable columns (click header to sort)
  - Filterable (search box)
- **Code Smell List:**
  - Categorized by smell type
  - Severity indicators
  - File locations with line numbers
- **Top Issues:**
  - Most complex files (>20 cyclomatic)
  - Largest files (>500 LOC)
  - Duplicate code blocks
- **Files:**
  - `templates/dashboard-tabs/tab-quality.html` (500 lines)
- **Tests:** Covered by integration tests

**4.3.4: Tab 4 - Security** (1 hour)
- **OWASP Issues Table:**
  - Category, severity, file, line number
  - Sortable/filterable
  - Remediation suggestions
- **Security Score Card:**
  - Overall security score
  - Issues by severity (critical/high/medium/low)
- **Files:**
  - `templates/dashboard-tabs/tab-security.html` (350 lines)
- **Tests:** Covered by integration tests

**4.3.5: Tab 5 - Recommendations** (1 hour)
- **Prioritized Action Items:**
  - Fix critical security issues (top 5)
  - Refactor complex files (top 5)
  - Remove duplicate code (top 3 blocks)
- **Quick Wins:**
  - Small improvements with high impact
  - Estimated effort (low/medium/high)
- **Long-term Improvements:**
  - Architecture suggestions
  - Dependency updates
- **Files:**
  - `templates/dashboard-tabs/tab-recommendations.html` (300 lines)
- **Tests:** Covered by integration tests

**Acceptance Criteria:**
- ✅ All 5 tabs functional and navigable
- ✅ Tab switching <50ms
- ✅ Content loads progressively (no blocking)
- ✅ Responsive design (desktop, tablet)
- ✅ All tests pass (integration suite)

---

### ☐ PHASE 5: Integration & Command Interface (Week 5 - Parallel with Testing)

**Duration:** 3 days (24 hours)  
**Goal:** Integrate dashboard with CORTEX, create user commands, enable progressive workflow

---

#### 5.1: User Command Interface (1 day, 8 hours)

**Tasks:**

**5.1.1: Command Routing** (4 hours)
- Add intent detection triggers:
  - `show health dashboard`
  - `application health`
  - `onboard application`
  - `dashboard`
  - `analyze codebase`
- Route to ApplicationHealthOrchestrator
- Pass scan level parameter (overview/standard/deep)
- **Files:**
  - Update: `src/cortex_agents/intent_router.py` (add triggers)
  - Tests: `tests/cortex_agents/test_intent_router.py` (add coverage)
- **Tests:** 5 tests (trigger detection, routing)

**5.1.2: Response Template** (4 hours)
- Create application health response template
- Add to `cortex-brain/response-templates.yaml`
- Include dashboard generation status
- Add progressive scan prompts ("Click for deeper analysis")
- **Template Structure:**
  - Understanding: User wants application health insights
  - Challenge: Scan level selection (overview vs deep)
  - Response: Dashboard generated, open in browser
  - Next Steps: Progressive options (drill-down)
- **Files:**
  - Update: `cortex-brain/response-templates.yaml` (add template)
  - Tests: Template selection covered by orchestrator tests

**Acceptance Criteria:**
- ✅ All command triggers recognized
- ✅ Response template loads correctly
- ✅ User guided through progressive workflow
- ✅ All tests pass (5 total)

---

#### 5.2: Orchestrator Implementation (2 days, 16 hours)

**Tasks:**

**5.2.1: ApplicationHealthOrchestrator** (12 hours)
- Coordinate crawler, analyzers, detectors, dashboard generator
- Implement progressive workflow:
  - Step 1: Overview scan → Generate dashboard → Offer "Dig Deeper"
  - Step 2: User clicks "Analyze Quality" → Standard scan → Update dashboard
  - Step 3: User clicks "Security Audit" → Deep scan → Update dashboard
- Progress monitoring integration (@with_progress)
- Error handling and recovery
- Result caching (store in Tier 3)
- **TDD Workflow:**
  - RED: Test fails - orchestrator doesn't cache results
  - GREEN: Results stored in Tier 3 after each scan
  - REFACTOR: Optimize workflow, add checkpoints
- **Files:**
  - `src/orchestrators/application_health_orchestrator.py` (800 lines)
  - `tests/orchestrators/test_application_health_orchestrator.py` (700 lines)
- **Tests:** 35 tests (workflow, caching, error handling, progress)

**5.2.2: Browser Integration** (4 hours)
- Auto-open dashboard in default browser
- Serve dashboard via simple HTTP server (optional for remote access)
- Handle browser open failures gracefully
- **Files:**
  - `src/orchestrators/dashboard_server.py` (200 lines)
  - `tests/orchestrators/test_dashboard_server.py` (150 lines)
- **Tests:** 6 tests (browser open, server start, error handling)

**Acceptance Criteria:**
- ✅ Orchestrator coordinates all components successfully
- ✅ Progressive workflow functional (3 levels)
- ✅ Dashboard opens in browser automatically
- ✅ Results cached for fast re-access
- ✅ All tests pass (41 total)

---

### ☐ PHASE 6: Testing & Quality Assurance (Week 5 - Parallel with Phase 5)

**Duration:** 3 days (24 hours)  
**Goal:** Comprehensive testing, performance validation, bug fixes

---

#### 6.1: Unit Testing (1 day, 8 hours)

**Tasks:**

**6.1.1: Component Test Coverage** (8 hours)
- Ensure 90%+ code coverage for all modules
- Add missing edge case tests
- Validate TDD compliance (all tests written before implementation)
- **Target Coverage:**
  - Crawlers: 95%+
  - Analyzers: 90%+
  - Detectors: 85%+
  - Dashboard: 85%+
  - Orchestrator: 90%+
- **Tools:** pytest, pytest-cov
- **Files:**
  - Various test files (add missing tests)
- **Tests:** 50+ additional tests (edge cases)

**Acceptance Criteria:**
- ✅ Overall coverage >90%
- ✅ All edge cases covered
- ✅ TDD compliance validated
- ✅ All tests pass (500+ total)

---

#### 6.2: Integration Testing (1 day, 8 hours)

**Tasks:**

**6.2.1: End-to-End Workflow Tests** (4 hours)
- Test complete user journey (command → scan → dashboard → export)
- Test progressive workflow (overview → standard → deep)
- Test multi-repository scenarios
- Test error recovery (corrupted files, missing dependencies)
- **Files:**
  - `tests/integration/test_application_health_e2e.py` (600 lines)
- **Tests:** 15 tests (complete workflows)

**6.2.2: Performance Testing** (4 hours)
- Benchmark scan times (10K, 50K, 100K files)
- Memory profiling (ensure <500MB limit)
- Dashboard generation time (<5s target)
- Concurrent user simulation (if WebSocket server included)
- **Files:**
  - `tests/performance/test_application_health_performance.py` (400 lines)
- **Tests:** 10 tests (performance benchmarks)

**Acceptance Criteria:**
- ✅ E2E tests pass 100%
- ✅ Performance targets met:
  - 10K files: <30s (overview), <2min (standard)
  - 50K files: <2min (overview), <10min (standard)
  - Dashboard generation: <5s
  - Memory: <500MB
- ✅ All tests pass (25 total)

---

#### 6.3: Browser Compatibility Testing (1 day, 8 hours)

**Tasks:**

**6.3.1: Cross-Browser Validation** (4 hours)
- Test on Chrome, Firefox, Safari, Edge
- Validate D3.js rendering
- Test interactive features (zoom, pan, click)
- Verify export functionality
- **Manual Testing Checklist:**
  - Dashboard loads correctly
  - All tabs functional
  - Graphs render properly
  - Interactions work (drag, zoom, click)
  - Export generates files
- **Files:**
  - `tests/browser/browser-compatibility-checklist.md` (checklist)
  - `tests/browser/test_browser_automation.py` (Selenium tests - optional)

**6.3.2: Responsive Design Testing** (4 hours)
- Test on desktop (1920x1080, 1366x768)
- Test on tablet (1024x768)
- Validate layout adjustments
- Ensure readability on all screen sizes
- **Manual Testing Checklist:**
  - Dashboard scales correctly
  - Graphs remain readable
  - Navigation usable on all sizes
  - No horizontal scrolling (except graphs)

**Acceptance Criteria:**
- ✅ Dashboard works on 4 major browsers
- ✅ Responsive design functional on 3 screen sizes
- ✅ All interactive features work across browsers
- ✅ Export functional on all browsers

---

## 📊 Test Summary

| Phase | Component | Tests | Coverage |
|-------|-----------|-------|----------|
| 1.1 | Crawler Orchestrator | 37 | 95% |
| 1.2 | Language Analyzers | 94 | 90% |
| 2.1 | Caching System | 45 | 95% |
| 2.2 | Framework Detection | 86 | 90% |
| 3.1 | Complexity Metrics | 45 | 90% |
| 3.2 | Quality & Smells | 39 | 85% |
| 3.3 | Security Detection | 30 | 85% |
| 4.1 | Dashboard Generator | 34 | 85% |
| 4.2 | Visualizations | 27 | 80% |
| 5.1 | Command Interface | 5 | 95% |
| 5.2 | Orchestrator | 41 | 90% |
| 6.1 | Unit Tests | 50 | - |
| 6.2 | Integration Tests | 25 | - |
| **TOTAL** | **All Components** | **558** | **90%** |

---

## 🎯 Definition of Done (DoD)

### Code Quality
- [x] TDD workflow followed for all components (RED → GREEN → REFACTOR)
- [ ] All unit tests passing (558 tests)
- [ ] Code coverage >90% overall
- [ ] All integration tests passing (25 tests)
- [ ] Performance benchmarks met (<30s overview, <2min standard, <5min deep)
- [ ] Memory usage <500MB for 50K files
- [ ] No critical bugs (blocking issues)
- [ ] No high-severity security issues

### Documentation
- [ ] User guide created (`cortex-brain/documents/guides/application-health-dashboard-guide.md`)
- [ ] API documentation complete (docstrings, type hints)
- [ ] Architecture diagrams updated
- [ ] Response template documented
- [ ] Command reference updated (CORTEX.prompt.md)

### Integration
- [ ] Intent router updated with new triggers
- [ ] Response template added to response-templates.yaml
- [ ] Tier 3 schema migration completed
- [ ] Enhancement Catalog updated with new features
- [ ] Git checkpoint system integrated

### User Experience
- [ ] Dashboard generates in <5 seconds
- [ ] CORTEX logo prominently displayed (header)
- [ ] All 5 tabs functional and navigable
- [ ] Export to PDF/PNG/PPTX working
- [ ] Progressive workflow intuitive (clear prompts)
- [ ] Browser auto-opens dashboard
- [ ] Error messages user-friendly

### Security & Compliance
- [ ] OWASP security review passed
- [ ] No sensitive data in logs
- [ ] File system access restricted to workspace
- [ ] XSS prevention in dashboard
- [ ] SQL injection prevention in queries

### Deployment
- [ ] README updated with new feature
- [ ] CHANGELOG entry created
- [ ] Version bumped (CORTEX 3.3.0)
- [ ] Deployment tested on clean install
- [ ] Upgrade path validated (preserve existing data)

---

## 📈 Success Metrics

### Performance Targets
- **Overview Scan:** <30 seconds for 10K files
- **Standard Scan:** <2 minutes for 10K files
- **Deep Scan:** <5 minutes for 10K files
- **Dashboard Generation:** <5 seconds
- **Memory Usage:** <500MB for 50K files
- **Cache Hit Rate:** >90% on re-scans

### Quality Targets
- **Test Coverage:** >90%
- **Test Pass Rate:** 100%
- **Language Detection Accuracy:** >95%
- **Framework Detection Accuracy:** >90%
- **Code Smell Detection Accuracy:** >85%
- **Security Pattern Detection:** >80%

### User Experience Targets
- **Dashboard Load Time:** <3 seconds
- **Tab Switch Time:** <50ms
- **Graph Interaction:** 60fps
- **Export Time:** <10 seconds (PDF)
- **Browser Compatibility:** 4 major browsers
- **Responsive Design:** 3 screen sizes

---

## 🗂️ File Structure

```
src/
├── crawlers/
│   ├── crawler_orchestrator.py
│   ├── file_system_walker.py
│   ├── scan_strategies.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── python_analyzer.py
│   │   ├── csharp_analyzer.py
│   │   ├── javascript_analyzer.py
│   │   ├── coldfusion_analyzer.py
│   │   ├── generic_analyzer.py
│   │   └── analyzer_factory.py
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── file_hash_cache.py
│   │   ├── analysis_result_cache.py
│   │   └── incremental_update_detector.py
│   ├── detectors/
│   │   ├── __init__.py
│   │   ├── dotnet_detector.py
│   │   ├── node_detector.py
│   │   ├── coldfusion_detector.py
│   │   ├── build_system_detector.py
│   │   ├── project_structure_analyzer.py
│   │   └── detector_orchestrator.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── cyclomatic_complexity.py
│   │   ├── cognitive_complexity.py
│   │   ├── halstead_metrics.py
│   │   ├── maintainability_index.py
│   │   └── code_smell_detector.py
│   ├── security/
│   │   ├── __init__.py
│   │   └── owasp_pattern_detector.py
│   └── dashboard/
│       ├── __init__.py
│       ├── application_health_dashboard_adapter.py
│       ├── data_serializer.py
│       └── cortex_branding.py
│
├── orchestrators/
│   ├── application_health_orchestrator.py
│   └── dashboard_server.py
│
└── utils/
    └── interactive_dashboard_generator.py (reused)

templates/
├── dashboard-tabs/
│   ├── tab-overview.html
│   ├── tab-visualizations.html
│   ├── tab-quality.html
│   ├── tab-security.html
│   └── tab-recommendations.html
├── static/
│   ├── js/
│   │   ├── dependency-graph-d3.js
│   │   ├── metric-charts.js
│   │   └── websocket-client.js
│   └── images/
│       └── cortex-logo.svg
└── interactive-dashboard-template.html (reused)

tests/
├── crawlers/
│   ├── test_crawler_orchestrator.py
│   ├── test_file_system_walker.py
│   ├── test_scan_strategies.py
│   ├── analyzers/
│   │   └── test_*.py
│   ├── cache/
│   │   └── test_*.py
│   ├── detectors/
│   │   └── test_*.py
│   ├── metrics/
│   │   └── test_*.py
│   ├── security/
│   │   └── test_*.py
│   └── dashboard/
│       └── test_*.py
├── orchestrators/
│   ├── test_application_health_orchestrator.py
│   └── test_dashboard_server.py
├── integration/
│   └── test_application_health_e2e.py
├── performance/
│   └── test_application_health_performance.py
├── frontend/
│   ├── test_dependency_graph.js
│   └── test_metric_charts.js
└── browser/
    ├── browser-compatibility-checklist.md
    └── test_browser_automation.py

cortex-brain/
├── documents/
│   ├── guides/
│   │   └── application-health-dashboard-guide.md
│   └── analysis/
│       └── dashboard/
│           └── dashboard.html (generated)
└── tier3/
    └── context.db (application_scans, file_analysis_cache tables)
```

---

## 🚀 Deployment Plan

### Pre-Deployment Checklist
- [ ] All tests passing (558 unit + integration)
- [ ] Performance benchmarks validated
- [ ] Browser compatibility confirmed
- [ ] Documentation complete
- [ ] Security review approved
- [ ] Code review completed
- [ ] Enhancement Catalog updated

### Deployment Steps
1. **Version Bump:** Update VERSION file to 3.3.0
2. **Schema Migration:** Run Tier 3 migration script
3. **Template Update:** Add application health response template
4. **Intent Router:** Add new command triggers
5. **Documentation:** Update CORTEX.prompt.md with new commands
6. **CHANGELOG:** Document all new features
7. **Git Tag:** Create release tag v3.3.0
8. **Upgrade Test:** Validate upgrade from 3.2.0 → 3.3.0

### Post-Deployment Validation
- [ ] Fresh install test (clean system)
- [ ] Upgrade path test (existing CORTEX installation)
- [ ] Command execution test (all new triggers)
- [ ] Dashboard generation test (sample repository)
- [ ] Performance validation (meets targets)

---

## 🎓 User Guide Outline

### Getting Started
1. **Initial Command:** `show health dashboard` or `onboard application`
2. **Overview Scan:** Wait 30 seconds for high-level analysis
3. **Dashboard Opens:** Browser auto-opens with interactive visualization

### Progressive Workflow
1. **Level 1 - Overview:**
   - See project structure, file counts, language distribution
   - Review overall quality score
   - Identify entry points and key modules
   - **Action:** Click "Analyze Quality" for deeper insights

2. **Level 2 - Standard Analysis:**
   - View complexity metrics per file
   - See code smell reports
   - Review maintainability index
   - Explore dependency graph
   - **Action:** Click "Security Audit" for OWASP analysis

3. **Level 3 - Deep Analysis:**
   - Full security pattern detection
   - Complete complexity analysis (100% of files)
   - Performance hotspot identification
   - Actionable recommendations
   - **Action:** Export report (PDF/PNG/PPTX)

### Dashboard Navigation
- **Tab 1 - Overview:** High-level summary and key metrics
- **Tab 2 - Visualizations:** Interactive D3.js graphs and Chart.js charts
- **Tab 3 - Code Quality:** Detailed metrics, code smells, top issues
- **Tab 4 - Security:** OWASP vulnerabilities, severity breakdown
- **Tab 5 - Recommendations:** Prioritized action items, quick wins

### Export Options
- **PDF:** Full report with all tabs (use for stakeholders)
- **PNG:** Individual visualizations (use for presentations)
- **PPTX:** Slides with key insights (use for executive summary)

---

## 🎯 Future Enhancements (Post-3.3.0)

### Phase 7: Real-Time Monitoring (CORTEX 3.4.0)
- WebSocket integration for live updates
- File watcher for continuous analysis
- Auto-refresh dashboard on code changes
- Real-time metrics streaming

### Phase 8: Historical Tracking (CORTEX 3.5.0)
- Track metrics over time (daily snapshots)
- Trend visualization (complexity increasing/decreasing)
- Regression detection (quality degradation alerts)
- Baseline comparison (current vs previous scans)

### Phase 9: AI-Powered Insights (CORTEX 4.0.0)
- GPT-4 integration for code review suggestions
- Automated refactoring recommendations
- Predictive maintenance (which files will cause issues)
- Natural language query ("Show files with high complexity in authentication module")

---

## 📝 Notes

### Production Repository Learnings Applied
1. **V5.ColdFusion Insights:**
   - Multi-application repository detection implemented
   - ColdFusion language analyzer added
   - Modular architecture analysis supported

2. **TCBULK Insights:**
   - .NET Core project structure detection
   - NuGet/npm dependency analysis
   - Solution/project hierarchy mapping

3. **Scale Considerations:**
   - Progressive crawling for large repositories
   - Multi-threading for 50K+ files
   - Caching for 90%+ re-scan efficiency
   - Memory optimization for enterprise applications

### Technical Decisions
- **No Roslyn Dependency:** C# analyzer uses regex (faster, no external deps)
- **No Esprima Dependency:** JavaScript analyzer uses regex (fallback option)
- **SQLite for Caching:** Fast, local, no server required
- **D3.js v7+:** Latest stable, best performance
- **Progressive Disclosure:** Don't overwhelm users with all data at once

---

**Plan Status:** ✅ Complete - Ready for Implementation  
**Next Action:** Begin Phase 1 (TDD RED phase for CrawlerOrchestrator)  
**Estimated Completion:** 5 weeks (200 hours total)

# Multi-Threaded Crawler Architecture Design

**Version:** 1.0.0  
**Date:** 2025-11-04  
**Status:** 🎯 ACTIVE DESIGN  
**Phase:** KDS v6.0 - Phase 2 (Week 5-6)

---

## 📊 Executive Summary

**Purpose:** Redesign KDS brain crawler as a multi-threaded system with area-specific specialists that run in parallel, reducing project scan time by 60% (target: <5 minutes for 1000+ file projects).

**Current State:**
- ❌ Single-threaded sequential scan (~10-12 minutes for 1000 files)
- ❌ Generic file-by-file processing (no domain specialization)
- ❌ No progress visibility during long scans
- ❌ Inefficient for large codebases

**Target State:**
- ✅ Parallel multi-threaded execution (4 area specialists)
- ✅ Domain-specific intelligence (UI, API, Service, Test crawlers)
- ✅ Real-time progress tracking
- ✅ 60% faster (<5 minutes for 1000 files)
- ✅ Richer BRAIN data (specialized extraction)

**Key Metrics:**
- **Performance Target:** <5 min for 1000 files (vs 10-12 min baseline)
- **Parallelization:** 4 concurrent area crawlers
- **Progress Granularity:** Real-time area-by-area status
- **Data Quality:** Specialized pattern extraction per domain

---

## 🏗️ Architecture Overview

### High-Level Design

```
User/Agent
    ↓
orchestrator.ps1 (Main Coordinator)
    ↓
┌─────────────────────────────────────────────────────┐
│          Parallel Execution Layer (4 Jobs)          │
├──────────────┬──────────────┬──────────────┬────────┤
│ ui-crawler   │ api-crawler  │ service-    │ test-  │
│              │              │ crawler      │crawler │
│ (Components) │(Controllers) │ (Services)   │(Tests) │
└──────┬───────┴──────┬───────┴──────┬───────┴───┬────┘
       │              │              │           │
       └──────────────┴──────────────┴───────────┘
                      ↓
          Intermediate Results (JSON per area)
                      ↓
             feed-brain.ps1 (Aggregator)
                      ↓
        BRAIN Storage (YAML/SQLite - unified)
```

### Component Responsibilities

| Component | Responsibility (SRP) | Input | Output |
|-----------|---------------------|-------|--------|
| **orchestrator.ps1** | Launch parallel crawlers, track progress, aggregate results | Project path, config | Crawl completion status |
| **ui-crawler.ps1** | Discover UI components, props, DI, naming | Component paths | ui-results.json |
| **api-crawler.ps1** | Discover API routes, DTOs, HTTP methods | Controller paths | api-results.json |
| **service-crawler.ps1** | Discover services, interfaces, DI | Service paths | service-results.json |
| **test-crawler.ps1** | Discover test patterns, selectors, frameworks | Test paths | test-results.json |
| **feed-brain.ps1** | Aggregate crawler outputs into BRAIN format | 4x JSON files | BRAIN YAML updates |

---

## 🎯 Area-Specific Crawler Designs

### 1. UI Crawler (ui-crawler.ps1)

**Target Files:** `*.razor`, `*.tsx`, `*.jsx`, `*.vue`, `*.svelte`

**Discovery Goals:**
- Component structure (parent/child relationships)
- Props/parameters (types, defaults, required)
- DI injections (`@inject`, `useContext`)
- Element IDs (`id="..."` attributes) ← **CRITICAL for Playwright**
- Naming conventions (PascalCase, kebab-case)
- Routing patterns (`@page` directives)

**Output Schema (ui-results.json):**
```json
{
  "area": "UI",
  "scan_time": "2025-11-04T10:30:00Z",
  "duration_seconds": 45,
  "components": [
    {
      "path": "Components/Host/HostControlPanelContent.razor",
      "type": "blazor-component",
      "naming_convention": "PascalCase",
      "dependencies": ["@inject SessionManager", "@inject SignalRClient"],
      "parameters": [
        {"name": "SessionId", "type": "string", "required": true}
      ],
      "element_ids": ["sidebar-start-session-btn", "reg-transcript-canvas-btn"],
      "routes": ["/host/control-panel/{hostToken}"]
    }
  ],
  "patterns": {
    "component_structure": "feature-based",
    "di_pattern": "inject-attribute",
    "naming": "PascalCase"
  }
}
```

**Implementation Strategy:**
1. Discover all component files (Get-ChildItem -Recurse -Include *.razor, *.tsx, etc.)
2. Parse each file for:
   - `@inject` directives (Blazor DI)
   - `@parameter` or prop definitions
   - `id="..."` attributes (Playwright selectors)
   - `@page` directives (routing)
3. Extract naming conventions (analyze file/component names)
4. Build component dependency graph
5. Output structured JSON

**Performance Target:** <1.5 min for 300 components

---

### 2. API Crawler (api-crawler.ps1)

**Target Files:** `*Controller.cs`, `*Controller.ts`, `routes/*.ts`, `api/*.py`

**Discovery Goals:**
- API routes (`[HttpGet("...")]`, `app.get()`)
- HTTP methods (GET, POST, PUT, DELETE)
- DTOs (request/response models)
- Authorization patterns (`[Authorize]`, `requireAuth`)
- Route parameters (path, query)
- Versioning patterns

**Output Schema (api-results.json):**
```json
{
  "area": "API",
  "scan_time": "2025-11-04T10:31:30Z",
  "duration_seconds": 38,
  "endpoints": [
    {
      "path": "Controllers/SessionController.cs",
      "base_route": "/api/session",
      "endpoints": [
        {
          "method": "POST",
          "route": "/api/session/start",
          "request_dto": "StartSessionRequest",
          "response_dto": "SessionResponse",
          "authorization": "HostToken"
        }
      ]
    }
  ],
  "patterns": {
    "routing": "attribute-based",
    "versioning": "url-path",
    "auth": "token-based"
  }
}
```

**Implementation Strategy:**
1. Discover all controller files
2. Parse for route attributes (`[HttpGet]`, `@app.route()`)
3. Extract DTOs from method signatures
4. Identify auth patterns (`[Authorize]`, decorators)
5. Map route hierarchy
6. Output structured JSON

**Performance Target:** <1 min for 100 controllers

---

### 3. Service Crawler (service-crawler.ps1)

**Target Files:** `*Service.cs`, `*Repository.cs`, `services/*.ts`, `*Manager.cs`

**Discovery Goals:**
- Service interfaces vs implementations
- DI registration patterns (`builder.Services.AddScoped<>`)
- Business logic patterns (repository, manager, service)
- External dependencies (DB, APIs, caching)
- Naming conventions

**Output Schema (service-results.json):**
```json
{
  "area": "Services",
  "scan_time": "2025-11-04T10:32:15Z",
  "duration_seconds": 42,
  "services": [
    {
      "path": "Services/SessionManager.cs",
      "interface": "ISessionManager",
      "implementation": "SessionManager",
      "di_lifetime": "Scoped",
      "dependencies": ["ISessionRepository", "ISignalRClient"],
      "patterns": ["manager", "dependency-injection"]
    }
  ],
  "patterns": {
    "di_registration": "Program.cs",
    "naming": "I{Name} interface pattern",
    "layering": "repository-service-manager"
  }
}
```

**Implementation Strategy:**
1. Discover all service/repository files
2. Parse class vs interface definitions
3. Extract DI registrations (scan Program.cs, Startup.cs)
4. Identify dependency chains (constructor injection)
5. Classify patterns (repository, service, manager)
6. Output structured JSON

**Performance Target:** <1 min for 150 services

---

### 4. Test Crawler (test-crawler.ps1)

**Target Files:** `*.spec.ts`, `*Test.cs`, `*Tests.cs`, `Tests/**/*`

**Discovery Goals:**
- Test frameworks (Playwright, xUnit, Jest, pytest)
- Test patterns (unit, integration, E2E, visual)
- Selector strategies (`data-testid`, `#element-id`, text-based)
- Test data (session tokens, mock data)
- Coverage gaps (files without tests)

**Output Schema (test-results.json):**
```json
{
  "area": "Tests",
  "scan_time": "2025-11-04T10:33:00Z",
  "duration_seconds": 50,
  "tests": [
    {
      "path": "Tests/UI/fab-share-button.spec.ts",
      "framework": "Playwright",
      "type": "visual-regression",
      "selectors": [
        {"type": "id", "value": "#sidebar-start-session-btn"},
        {"type": "id", "value": "#reg-transcript-canvas-btn"}
      ],
      "test_data": {
        "session_token": "PQ9N5YWW",
        "host_url": "https://localhost:9091/host/control-panel/PQ9N5YWW"
      }
    }
  ],
  "patterns": {
    "framework": "Playwright",
    "selector_strategy": "id-based (robust)",
    "test_types": ["visual", "unit", "integration"]
  },
  "coverage": {
    "files_with_tests": 127,
    "files_without_tests": 43,
    "coverage_percentage": 74.7
  }
}
```

**Implementation Strategy:**
1. Discover all test files
2. Parse framework imports (Playwright, xUnit, Jest)
3. Extract selectors (regex for `.locator()`, `GetElementById()`)
4. Identify test data (session tokens, URLs, mock data)
5. Calculate coverage (files with/without tests)
6. Classify test types (unit vs E2E vs visual)
7. Output structured JSON

**Performance Target:** <1.5 min for 200 tests

---

## ⚡ Orchestrator Design (orchestrator.ps1)

### Responsibilities

1. **Parallel Job Launching:** Start 4 area crawlers as PowerShell background jobs
2. **Progress Tracking:** Real-time status display (area-by-area)
3. **Job Management:** Monitor completion, handle errors
4. **Result Aggregation:** Collect JSON outputs, pass to feed-brain.ps1

### Execution Flow

```powershell
# Pseudo-code (high-level flow)

# Step 1: Initialize
$workspaceRoot = "D:\PROJECTS\NOOR CANVAS"
$outputDir = "KDS/kds-brain/crawler-temp"
New-Item -Path $outputDir -ItemType Directory -Force

# Step 2: Launch parallel crawlers
$jobs = @{
    UI = Start-Job -FilePath "KDS\scripts\crawlers\ui-crawler.ps1" -ArgumentList $workspaceRoot
    API = Start-Job -FilePath "KDS\scripts\crawlers\api-crawler.ps1" -ArgumentList $workspaceRoot
    Service = Start-Job -FilePath "KDS\scripts\crawlers\service-crawler.ps1" -ArgumentList $workspaceRoot
    Test = Start-Job -FilePath "KDS\scripts\crawlers\test-crawler.ps1" -ArgumentList $workspaceRoot
}

# Step 3: Real-time progress display
while ($jobs.Values | Where-Object {$_.State -eq 'Running'}) {
    Clear-Host
    Write-Host "🔄 Multi-Threaded Crawler Progress" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════" -ForegroundColor Cyan
    
    foreach ($area in $jobs.Keys) {
        $job = $jobs[$area]
        $status = switch ($job.State) {
            'Running' { "🔄 In Progress" }
            'Completed' { "✅ Complete" }
            'Failed' { "❌ Failed" }
        }
        Write-Host "$area Crawler: $status" -ForegroundColor $(if ($job.State -eq 'Completed') {'Green'} else {'Yellow'})
    }
    
    Start-Sleep -Seconds 2
}

# Step 4: Collect results
$results = @{}
foreach ($area in $jobs.Keys) {
    $job = $jobs[$area]
    if ($job.State -eq 'Completed') {
        $output = Receive-Job -Job $job
        $results[$area] = $output
    } else {
        Write-Warning "⚠️ $area crawler failed"
    }
    Remove-Job -Job $job
}

# Step 5: Aggregate and feed BRAIN
& "$workspaceRoot\KDS\scripts\crawlers\feed-brain.ps1" -Results $results
```

### Progress Display

**Real-time output (updates every 2 seconds):**
```
🔄 Multi-Threaded Crawler Progress
════════════════════════════════════
⏱️  Elapsed: 2m 15s | Target: <5 min

UI Crawler:      ✅ Complete (287 components, 1m 23s)
API Crawler:     🔄 In Progress (72/95 controllers)
Service Crawler: ✅ Complete (143 services, 54s)
Test Crawler:    🔄 In Progress (189/214 tests)

════════════════════════════════════
Estimated completion: ~1m 30s remaining
```

### Error Handling

**Crawler failure scenarios:**
1. **Parse error:** Log error, continue with partial results
2. **File access error:** Skip inaccessible files, log warning
3. **Job timeout:** Kill job after 10 minutes (safety)
4. **Complete failure:** Fall back to single-threaded crawler

**Rollback strategy:**
- If ANY crawler fails critically → Use single-threaded fallback
- If partial data available → Feed BRAIN with what succeeded
- Log all errors to `crawler-errors.log`

---

## 🧠 BRAIN Feeder Design (feed-brain.ps1)

### Responsibilities

1. **Aggregate Results:** Merge 4x JSON files into unified data structures
2. **Update BRAIN Files:** Write to `file-relationships.yaml`, `test-patterns.yaml`, `architectural-patterns.yaml`
3. **Confidence Scoring:** Assign confidence based on discovery method
4. **Deduplication:** Merge overlapping discoveries

### Aggregation Logic

**File Relationships (file-relationships.yaml):**
```yaml
# Aggregated from all 4 crawlers
file_relationships:
  - primary_file: "Components/Host/HostControlPanelContent.razor"
    related_files:
      - path: "Services/SessionManager.cs"
        relationship: "DI-injection"
        confidence: 0.95  # Direct @inject reference
        source: "ui-crawler"
      - path: "Controllers/SessionController.cs"
        relationship: "API-consumption"
        confidence: 0.85  # Inferred from SignalR patterns
        source: "api-crawler"
      - path: "Tests/UI/control-panel.spec.ts"
        relationship: "test-coverage"
        confidence: 0.98  # Explicit test file
        source: "test-crawler"
```

**Test Patterns (test-patterns.yaml):**
```yaml
# Aggregated from test-crawler + UI crawler (element IDs)
test_patterns:
  playwright:
    selector_strategy: "id-based"  # ✅ ROBUST
    element_ids:
      - id: "sidebar-start-session-btn"
        component: "Components/Host/HostControlPanelSidebar.razor"
        purpose: "Start session button"
        confidence: 0.98
      - id: "reg-transcript-canvas-btn"
        component: "Components/UserRegistrationLink.razor"
        purpose: "Select transcript canvas mode"
        confidence: 0.98
    test_data:
      session_212_token: "PQ9N5YWW"
      host_url_pattern: "https://localhost:9091/host/control-panel/{token}"
```

**Architectural Patterns (architectural-patterns.yaml):**
```yaml
# Aggregated from all 4 crawlers
architectural_patterns:
  component_structure: "feature-based"  # From ui-crawler
  di_pattern: "interface-based"         # From service-crawler
  api_routing: "attribute-based"        # From api-crawler
  test_strategy: "id-based-selectors"   # From test-crawler
  
  confidence: 0.92  # Average across 4 sources
  sources: ["ui-crawler", "api-crawler", "service-crawler", "test-crawler"]
```

### Update Strategy

**Incremental updates (preserve existing data):**
1. Load existing BRAIN YAML files
2. Merge new discoveries (don't overwrite high-confidence existing data)
3. Increase confidence for repeated discoveries
4. Add timestamp and crawler version to metadata
5. Write updated YAML atomically (temp file + rename)

**Confidence scoring rules:**
```yaml
confidence_rules:
  direct_reference: 0.95-0.98     # Explicit @inject, import, etc.
  inferred_pattern: 0.80-0.90     # Pattern matching (naming, structure)
  statistical: 0.60-0.75          # Co-occurrence, frequency analysis
  repeated_discovery: +0.05       # Each additional source increases confidence
  max_confidence: 0.98            # Reserve 1.0 for manual verification
```

---

## 📊 Performance Benchmarks

### Target Metrics (1000-file project)

| Metric | Baseline (Single-Threaded) | Target (Multi-Threaded) | Improvement |
|--------|---------------------------|-------------------------|-------------|
| **Total Scan Time** | 10-12 min | <5 min | 60% faster |
| **UI Discovery** | 3-4 min | <1.5 min | 65% faster |
| **API Discovery** | 2-3 min | <1 min | 70% faster |
| **Service Discovery** | 2-3 min | <1 min | 70% faster |
| **Test Discovery** | 3-4 min | <1.5 min | 65% faster |
| **Progress Visibility** | None | Real-time | 100% improvement |

### Test Plan

**Test Environment:** NoorCanvas project (1,089 files)

**Measurement Points:**
1. Single-threaded baseline (current crawler)
2. Multi-threaded (4 parallel crawlers)
3. Data quality comparison (completeness, accuracy)
4. BRAIN query performance (before/after)

**Success Criteria:**
- ✅ <5 min total scan time (60% improvement)
- ✅ Real-time progress display working
- ✅ BRAIN data completeness ≥95% of single-threaded
- ✅ Zero data corruption (YAML integrity)

---

## 🔒 SOLID Compliance

### Single Responsibility Principle (SRP)
- ✅ Each crawler has ONE area of expertise (UI, API, Service, Test)
- ✅ Orchestrator ONLY coordinates (doesn't crawl)
- ✅ BRAIN feeder ONLY aggregates (doesn't crawl)

### Open/Closed Principle (OCP)
- ✅ Easy to add new area crawlers (e.g., database-crawler.ps1)
- ✅ Orchestrator discovers crawlers dynamically (convention-based)
- ✅ BRAIN feeder extensible (new output schemas)

### Liskov Substitution Principle (LSP)
- ✅ All area crawlers follow same interface (input: path, output: JSON)
- ✅ Orchestrator treats all crawlers uniformly
- ✅ Fallback to single-threaded crawler is transparent

### Interface Segregation Principle (ISP)
- ✅ Area crawlers don't depend on each other
- ✅ Each crawler outputs minimal required data
- ✅ BRAIN feeder consumes only what it needs per area

### Dependency Inversion Principle (DIP)
- ✅ Orchestrator depends on abstract "crawler" concept (not specific implementations)
- ✅ BRAIN feeder depends on JSON schema (not crawler internals)
- ✅ Easy to swap PowerShell crawlers for Python/Node.js versions

---

## 🚀 Implementation Phases

### Phase 2.1: Orchestrator + Progress Tracking (Week 5, Days 1-2)
- [ ] Create `orchestrator.ps1` skeleton
- [ ] Implement parallel job launching
- [ ] Add real-time progress display
- [ ] Test with mock crawlers (empty jobs)

### Phase 2.2: Area Crawlers (Week 5, Days 3-5)
- [ ] Implement `ui-crawler.ps1`
- [ ] Implement `api-crawler.ps1`
- [ ] Implement `service-crawler.ps1`
- [ ] Implement `test-crawler.ps1`
- [ ] Unit test each crawler independently

### Phase 2.3: BRAIN Feeder (Week 6, Days 1-2)
- [ ] Create `feed-brain.ps1`
- [ ] Implement aggregation logic
- [ ] Implement confidence scoring
- [ ] Test YAML output integrity

### Phase 2.4: Integration + Benchmarking (Week 6, Days 3-5)
- [ ] End-to-end test on NoorCanvas
- [ ] Measure performance vs baseline
- [ ] Fix bottlenecks
- [ ] Document results

---

## 📝 Configuration

**Crawler Config (KDS/config/crawler-config.yaml):**
```yaml
multi_threaded_crawler:
  enabled: true
  max_parallel_jobs: 4
  timeout_minutes: 10
  
  areas:
    ui:
      enabled: true
      patterns: ["*.razor", "*.tsx", "*.jsx", "*.vue", "*.svelte"]
      exclude_dirs: ["node_modules", "bin", "obj", "dist"]
      
    api:
      enabled: true
      patterns: ["*Controller.cs", "*Controller.ts", "routes/*.ts", "api/*.py"]
      exclude_dirs: ["node_modules", "bin", "obj"]
      
    service:
      enabled: true
      patterns: ["*Service.cs", "*Repository.cs", "*Manager.cs", "services/*.ts"]
      exclude_dirs: ["node_modules", "bin", "obj"]
      
    test:
      enabled: true
      patterns: ["*.spec.ts", "*Test.cs", "*Tests.cs"]
      exclude_dirs: ["node_modules", "bin", "obj"]
  
  fallback:
    use_single_threaded_on_error: true
    retry_failed_crawlers: 2
```

---

## 🎯 Success Metrics

**Immediate (End of Week 6):**
- ✅ <5 min scan time for 1000+ file projects
- ✅ Real-time progress display functional
- ✅ BRAIN data quality ≥95% of baseline
- ✅ Zero YAML corruption incidents

**Long-term (4 weeks post-deployment):**
- ✅ 90% of users prefer multi-threaded (faster feedback)
- ✅ BRAIN query accuracy improved by 15% (richer data)
- ✅ Zero regression bugs reported
- ✅ Crawler used 2-3x more frequently (faster = more useful)

---

## 🔄 Rollback Plan

**If multi-threaded approach fails:**
1. Disable via config: `multi_threaded_crawler.enabled = false`
2. System falls back to single-threaded crawler automatically
3. No data loss (BRAIN files remain valid)
4. No architectural changes needed (DIP abstraction preserved)

**Fallback scenarios:**
- Performance worse than baseline (>12 min)
- Data quality <90% (missing patterns)
- Frequent job failures (>20% error rate)
- PowerShell job stability issues

---

## 📚 References

**Related Documents:**
- `KDS/docs/KDS-V6-HOLISTIC-PLAN.md` (Phase 2 plan)
- `KDS/docs/KDS-V6-RISK-ANALYSIS-AND-REDESIGN.md` (Risk validation)
- `KDS/kds-brain/README.md` (BRAIN storage format)
- `KDS/prompts/internal/brain-crawler.md` (Current single-threaded implementation)

**PowerShell Job Management:**
- `Start-Job` - PowerShell background jobs
- `Get-Job` - Job status monitoring
- `Receive-Job` - Collect job output
- `Wait-Job` - Synchronous wait for completion
- `Remove-Job` - Cleanup completed jobs

**JSON Schema Validation:**
- Each crawler output validated against schema before BRAIN feeding
- Use `Test-Json` cmdlet (PowerShell 6+)

---

## ✅ Design Approval Checklist

Before implementation begins, verify:

- [x] Architecture diagram clear and SOLID-compliant
- [x] Each crawler has single responsibility (SRP)
- [x] Area-specific output schemas defined
- [x] Orchestrator design supports parallel execution
- [x] Progress tracking mechanism defined
- [x] BRAIN feeder aggregation logic defined
- [x] Performance targets measurable (<5 min)
- [x] Error handling and rollback plans documented
- [x] Configuration externalized (YAML-driven)
- [x] Success metrics defined

**Approved by:** [Pending - Review Required]  
**Implementation Start:** Week 5, Day 1 (after Phase 0 + Phase 1 complete)

---

**END OF DESIGN DOCUMENT**

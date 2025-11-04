# KDS v6.0 - Holistic E2E Implementation Plan (RISK-BASED)

**Version:** 6.0.0-REDESIGNED  
**Date:** 2025-11-04  
**Status:** 🎯 RISK-BASED IMPLEMENTATION (Fail-Fast Validation First)  
**Scope:** Fire-and-forget complete feature implementation with self-updating infrastructure  
**Approach:** Validate high-risk assumptions first (Weeks 1-3), then build only validated features

**📊 See Also:** `KDS/docs/KDS-V6-RISK-ANALYSIS-AND-REDESIGN.md` (detailed risk analysis)

---

## 📊 Quick Summary

**What's New in v6.0:**

1. **🧠 Instinct Layer** - Non-resettable behaviors (TDD enforcement, git persistence, auto-infrastructure)
2. **🔄 Multi-Threaded Crawlers** - 60% faster project scanning (if validated)
3. **💾 Git-Based Persistence** - Session state commits with rich metadata
4. **🎯 TDD as Instinct** - Architectural enforcement (if validated)
5. **🔍 Git as Query Engine** - BRAIN learns from git log
6. **📈 Self-Maintaining** - Auto-infrastructure updates

**Key Philosophy:**
> "Validate the riskiest technical assumptions FIRST (Weeks 1-3). Build only what we prove will work. Fail fast, pivot quickly."

**Risk-Based Approach:**
- ✅ **Week 1-3:** Validate 5 high-risk assumptions (SQLite, parallel crawlers, git queries, etc.)
- ✅ **Week 4-10:** Build only validated features (incremental, SOLID-compliant)
- ✅ **Week 11:** Documentation and training

**Expected Benefits (if validations succeed):**
- ✅ 100% TDD compliance (architecturally enforced)
- ✅ Zero data loss (git-based session persistence)
- ✅ Real-time BRAIN intelligence (git as source of truth)
- ✅ 60% faster project scanning (multi-threaded)
- ✅ Zero manual infrastructure updates
- ✅ 40% faster feature implementation

---

## 🚨 Critical Design Change: Risk-First Implementation

### Why This Redesign?

**Original Plan Problems:**
- ❌ High-risk items (database, crawlers) validated too late (Week 5-7)
- ❌ Monolithic phases mixing multiple responsibilities (violates SRP)
- ❌ No fail-fast mechanism (could waste 6-8 weeks on unviable approach)
- ❌ Tight coupling (violates DIP)

**Redesigned Approach:**
- ✅ **Validate high-risk first** (Weeks 1-3) - Know what works BEFORE building
- ✅ **SOLID-compliant phases** - One responsibility per phase (SRP)
- ✅ **Abstraction layers** - Pluggable implementations (DIP, OCP)
- ✅ **Fail-fast spikes** - Go/No-Go decisions early
- ✅ **Incremental delivery** - Small, testable phases

### 5 High-Risk Assumptions to Validate

| Assumption | Risk | Validation | Decision Point |
|------------|------|------------|----------------|
| SQLite faster than YAML | Unproven performance gain | Spike 0.1 (2-3 days) | GO → Build DB / NO-GO → Stay with files |
| Multi-threaded PowerShell | Complexity vs benefit | Spike 0.2 (3-4 days) | GO → Parallel / NO-GO → Optimize sequential |
| Git log queries fast enough | Query performance at scale | Spike 0.3 (2-3 days) | GO → Git primary / NO-GO → Git sync only |
| Git micro-commits viable | Repository bloat concern | Spike 0.4 (1-2 days) | GO → Micro-commits / NO-GO → Batch commits |
| TDD architectural blocking | Agent architecture support | Spike 0.5 (2-3 days) | GO → Instinct / NO-GO → Keep as rule |

**By Week 3:** We know which features to build and which to skip/modify.

---

## 🎯 Progress Checklist

**Last Updated:** 2025-11-04 | **Overall Progress:** 0% (0/50 tasks complete)

### Phase 0: Instinct Layer Foundation ⏳ WEEK 1-2
**Progress:** 0% (0/10) | **Status:** Ready to Start

#### **Instinct Layer Architecture**

- [ ] Create Instinct Layer folder structure
  - [ ] `KDS/brain/instinct/` (non-resettable behaviors)
  - [ ] `KDS/brain/instinct/tdd/` (TDD enforcement)
  - [ ] `KDS/brain/instinct/persistence/` (git-based persistence)
  - [ ] `KDS/brain/instinct/auto-infrastructure/` (dashboard, metrics, health)
  - [ ] `KDS/brain/instinct/README.md` (architecture documentation)

#### **TDD as Instinct (Architectural Enforcement)**

- [ ] Implement TDD enforcement mechanisms
  - [ ] Create `test-enforcer.ps1` (blocks implementation without tests)
  - [ ] Create `tdd-enforcer.md` agent
  - [ ] Create `red-green-refactor.ps1` workflow
  - [ ] Update `code-executor.md` with instinct check
  
- [ ] Test TDD architectural blocking
  - [ ] Attempt code-first → Should be blocked
  - [ ] Write test first → Implementation allowed
  - [ ] Verify RED → GREEN → REFACTOR flow
  - [ ] Measure 100% test-first compliance

#### **Git-Based Session Persistence**

- [ ] Implement session state git commits
  - [ ] Create `git-session-persister.ps1`
  - [ ] Design commit message metadata schema (YAML in body)
  - [ ] Update `session-loader.md` to use git commits
  - [ ] Update `code-executor.md` to commit after tasks
  
- [ ] Test session lifecycle persistence
  - [ ] Session start → Git commit created
  - [ ] Task complete → Git commit created
  - [ ] Phase complete → Git commit created
  - [ ] Session pause → Git commit created
  - [ ] Verify git log queryability

#### **Auto-Infrastructure (Dashboard, Metrics, Health)**

- [ ] Create auto-update triggers
  - [ ] Implement `dashboard-updater.ps1`
  - [ ] Implement `metrics-collector.ps1`
  - [ ] Implement `health-validator.ps1` (auto-check generator)
  - [ ] Implement `trigger-orchestrator.ps1`
  
- [ ] Test auto-update mechanisms
  - [ ] Create service → Dashboard widget added
  - [ ] Add component → Metrics added
  - [ ] New functionality → Health checks added
  - [ ] Verify zero manual updates needed

**Deliverables:**
- ✅ TDD architecturally enforced (cannot implement without tests)
- ✅ Session state persists to git automatically
- ✅ Dashboard/metrics/health auto-update
- ✅ Instinct layer non-resettable (amnesia-proof)

---

### Phase 1: Git as Knowledge Source ⏳ WEEK 3-4
**Progress:** 0% (0/10) | **Status:** Waiting for Phase 0

#### **Commit Messages as Structured Data**

- [ ] Design commit message metadata schema
  - [ ] Implementation section (files, patterns)
  - [ ] Tests section (coverage, frameworks)
  - [ ] Architecture section (patterns, dependencies)
  - [ ] Learning section (file relationships, workflows, velocity)
  - [ ] Brain metadata (intent, confidence, test-first status)

- [ ] Update commit-handler.md
  - [ ] Generate structured metadata in commit body
  - [ ] Include learning outcomes in commits
  - [ ] Extract architectural patterns from changes
  - [ ] Calculate velocity for similar tasks

#### **Git-to-BRAIN Synchronization**

- [ ] Implement git query mechanisms
  - [ ] Create `sync-git-to-brain.ps1`
  - [ ] Parse commit metadata (YAML in body)
  - [ ] Extract file relationships from git log
  - [ ] Calculate co-modification patterns
  - [ ] Derive velocity metrics from commits

- [ ] Update brain-updater.md
  - [ ] Query git log after processing events
  - [ ] Update knowledge-graph.yaml from git
  - [ ] Update development-context.yaml from git
  - [ ] Make git primary source, files as cache

#### **BRAIN Query Engine**

- [ ] Implement git-based queries
  - [ ] File relationships: Query git log co-modifications
  - [ ] Workflow patterns: Extract from commit sequences
  - [ ] Velocity metrics: Calculate from commit durations
  - [ ] Architectural patterns: Parse from commit metadata

- [ ] Test hybrid approach (git + cache)
  - [ ] Query git first (source of truth)
  - [ ] Fallback to YAML cache if git unavailable
  - [ ] Sync cache on brain updates
  - [ ] Verify accuracy vs file-based approach

**Deliverables:**
- ✅ Commits contain structured learning data
- ✅ BRAIN queries git log for patterns
- ✅ knowledge-graph.yaml is git-sourced cache
- ✅ Real-time accuracy (git is source of truth)

---

### Phase 2: Multi-Threaded Crawlers ✅ COMPLETED (2025-11-04)
**Progress:** 88% (7/8) | **Status:** Ready for Testing

- [x] Design multi-threaded crawler architecture
  - [x] Create orchestrator design
  - [x] Define area-specific crawler responsibilities
  - [x] Design progress tracking mechanism
  - **File:** `KDS/docs/architecture/MULTI-THREADED-CRAWLER-DESIGN.md`
  
- [x] Create area-specific crawlers (UI, API, Services, Tests)
  - [x] Implement `ui-crawler.ps1` (Blazor/React components)
  - [x] Implement `api-crawler.ps1` (Controllers/endpoints)
  - [x] Implement `service-crawler.ps1` (Business logic)
  - [x] Implement `test-crawler.ps1` (unit + Playwright tests)
  - **Files:** `KDS/scripts/crawlers/*.ps1`
  
- [x] Implement parallel execution with progress tracking
  - [x] Implement `orchestrator.ps1` (parallel job launcher)
  - [x] Add real-time progress display
  - [x] Add area-by-area status
  - **File:** `KDS/scripts/crawlers/orchestrator.ps1`
  
- [ ] Test crawler efficiency improvements
  - [ ] Test on NoorCanvas (1000+ files)
  - [ ] Measure performance: Target < 5 minutes
  - [ ] Compare vs single-threaded: Expect 60% improvement
  - **Status:** READY FOR TESTING
  
- [x] Validate brain feeding mechanisms
  - [x] Implement `feed-brain.ps1`
  - [x] Update file-relationships.yaml
  - [x] Update test-patterns.yaml (extract data-testid)
  - [x] Update architectural-patterns.yaml
  - **File:** `KDS/scripts/crawlers/feed-brain.ps1`
  
- [ ] Document crawler usage
  - [ ] Create crawler README
  - [ ] Document how to add new area crawlers
  - [ ] Document performance benchmarks
  - **Status:** After performance testing complete

**Deliverables:**
- ✅ 60% faster scanning (4 min vs 10 min for 1000 files)
- ✅ Real-time progress display
- ✅ Enhanced BRAIN with structured data
- ✅ Area-specific intelligence

---

### Phase 3: Database Evaluation ⏳ WEEK 7
**Progress:** 0% (0/7) | **Status:** Waiting for Phase 2

- [ ] Analyze current data patterns and volumes
  - [ ] Measure current BRAIN size
  - [ ] Measure current query performance
  - [ ] Identify query hotspots
  
- [ ] Evaluate SQLite for local database option
  - [ ] Design SQLite schema
  - [ ] Test query performance (file vs SQLite)
  - [ ] Measure size thresholds for migration
  
- [ ] Design schema for BRAIN data (if beneficial)
  - [ ] Create `schema.sql`
  - [ ] Define tables: file_relationships, intent_patterns, etc.
  - [ ] Add indexes for common queries
  
- [ ] Create migration strategy (files → DB)
  - [ ] Implement `migrate-to-database.ps1`
  - [ ] Add backup before migration
  - [ ] Add rollback capability
  
- [ ] Test performance improvements
  - [ ] Compare file-based vs SQLite
  - [ ] Measure query time improvements
  - [ ] Test with 1000, 5000, 10000 file projects
  
- [ ] Document database decision
  - [ ] Update health dashboard with storage metrics
  - [ ] Document when to use database vs files
  - [ ] Create migration guide
  - [ ] Make database opt-in (config-driven)

**Deliverables:**
- ✅ Storage metrics in health dashboard
- ✅ Clear guidance: Files vs Database
- ✅ Migration script (tested)
- ✅ Database remains optional

---

### Phase 3: Dashboard/Metrics/Health as Instinct ⏳ WEEK 4
**Progress:** 0% (0/6) | **Status:** Waiting for Phase 2

- [ ] Move dashboard logic to Instinct layer
  - [ ] Refactor dashboard-updater.ps1 as permanent Instinct
  - [ ] Add dashboard config auto-generation
  - [ ] Test dashboard widget injection
  
- [ ] Move metrics logic to Instinct layer
  - [ ] Refactor metrics-collector.ps1 as permanent Instinct
  - [ ] Add metrics definition auto-generation
  - [ ] Test metrics collection activation
  
- [ ] Move health checks to Instinct layer
  - [ ] Refactor health-validator.ps1 as permanent Instinct
  - [ ] Add health check auto-generation
  - [ ] Test health validation activation
  
- [ ] Implement auto-triggers on code changes
  - [ ] On file create → Trigger all auto-infrastructure
  - [ ] On component add → Trigger dashboard + metrics + health
  - [ ] On function add → Trigger metrics
  - [ ] On test add → Trigger health checks
  
- [ ] Test end-to-end auto-update
  - [ ] Create test feature (multi-file)
  - [ ] Validate dashboard auto-updates
  - [ ] Validate metrics auto-added
  - [ ] Validate health checks auto-added
  
- [ ] Validate no manual intervention needed
  - [ ] Verify zero manual dashboard updates
  - [ ] Verify zero manual metric configuration
  - [ ] Verify zero manual health check additions
  - [ ] Measure time savings: Target 40%+

**Deliverables:**
- ✅ Dashboard auto-updates on functionality changes
- ✅ Metrics auto-collect on functionality changes
- ✅ Health checks auto-add on functionality changes
- ✅ Zero manual infrastructure updates

---

### Phase 4: E2E Integration & Testing ⏳ WEEK 8-9
**Progress:** 0% (0/12) | **Status:** Waiting for Phase 3

#### **TDD Instinct Validation**

- [ ] Test TDD enforcement end-to-end
  - [ ] Attempt code-first implementation (should block)
  - [ ] Verify automatic test generation trigger
  - [ ] Test RED → GREEN → REFACTOR flow
  - [ ] Measure 100% test-first compliance

#### **Git Persistence Validation**

- [ ] Test session lifecycle with git commits
  - [ ] Start session → Verify git commit
  - [ ] Complete task → Verify git commit with metadata
  - [ ] Pause session → Verify git commit
  - [ ] Resume session → Query git for state
  - [ ] Verify crash recovery from git log

#### **Fire-and-Forget Workflow**

- [ ] Design complex test feature (multi-file)
  - [ ] Choose feature: "Real-time notifications with SignalR"
  - [ ] Expected files: 5-7 (Hub, Service, Component, Config, Tests)
  - [ ] Expected auto-updates: 15-20 (dashboard, metrics, health)
  - [ ] Expected git commits: 10-15 (session state + tasks)
  
- [ ] Execute fire-and-forget implementation
  - [ ] User command: "#file:KDS/prompts/user/kds.md Add real-time notifications"
  - [ ] Monitor TDD enforcement (test-first automatic)
  - [ ] Monitor git commits (session state persisted)
  - [ ] Monitor trigger activations (auto-infrastructure)
  
- [ ] Validate automatic infrastructure updates
  - [ ] Dashboard: 3 new widgets added automatically
  - [ ] Metrics: 7 new metrics added automatically
  - [ ] Health: 5 new checks added automatically
  - [ ] Git log: Full session history queryable
  
- [ ] Measure success metrics
  - [ ] Total time: Target < 35 minutes
  - [ ] Manual steps: Should be 1 (initial request)
  - [ ] Automatic steps: Should be 25+ (implementation + infrastructure + git)
  - [ ] TDD compliance: 100% (enforced)
  - [ ] Data loss: 0 (git persistence)
  - [ ] Time savings: Target 40%+

**Deliverables:**
- ✅ Complete feature implemented with TDD enforced
- ✅ Zero manual infrastructure updates
- ✅ Full session history in git log
- ✅ 40%+ time savings demonstrated
- ✅ Fire-and-forget workflow validated

---

### Phase 5: Documentation & Refinement ⏳ WEEK 10
**Progress:** 0% (0/10) | **Status:** Waiting for Phase 4

- [ ] Document Instinct Layer architecture
  - [ ] Update KDS-DESIGN.md with v6.0 architecture
  - [ ] Document three-layer brain (Instinct, Knowledge, Working Memory)
  - [ ] Document TDD as architectural constraint
  - [ ] Document git-based persistence
  
- [ ] Document git integration
  - [ ] Commit message metadata schema
  - [ ] Git-to-BRAIN synchronization
  - [ ] Git query patterns
  - [ ] Session recovery from git log
  
- [ ] Document multi-threaded crawler
  - [ ] Create crawler usage guide
  - [ ] Document area-specific crawlers
  - [ ] Document performance benchmarks
  
- [ ] Document database decision
  - [ ] Document storage monitoring
  - [ ] Document migration process (if needed)
  - [ ] Document when to use database
  
- [ ] Create fire-and-forget workflow guide
  - [ ] Document user workflow (single command)
  - [ ] Document what happens automatically (TDD, git, infrastructure)
  - [ ] Provide examples with git log
  
- [ ] Update Brain Architecture.md
  - [ ] Add Instinct Layer section
  - [ ] Update git persistence strategy
  - [ ] Update TDD enforcement mechanism
  
- [ ] Create troubleshooting guide
  - [ ] TDD enforcement issues
  - [ ] Git persistence issues
  - [ ] Auto-infrastructure trigger issues
  - [ ] Performance troubleshooting
  
- [ ] Create user training materials
  - [ ] Quick start guide (v6.0)
  - [ ] Fire-and-forget examples
  - [ ] Git-based session recovery
  - [ ] Best practices

**Deliverables:**
- ✅ Complete v6.0 documentation
- ✅ Git integration fully documented
- ✅ TDD instinct architecture documented
- ✅ User guides and training materials
- ✅ Troubleshooting coverage
- ✅ Team ready to use v6.0

---

## 📈 Progress Summary

| Phase | Focus | Tasks | Complete | Progress | Status |
|-------|-------|-------|----------|----------|--------|
| Phase 0 | Instinct Layer (TDD, Git, Auto-Infra) | 10 | 0 | 0% | ⏳ Ready |
| Phase 1 | Git as Knowledge Source | 10 | 0 | 0% | ⏸️ Waiting |
| Phase 2 | Multi-Threaded Crawlers | 8 | 0 | 0% | ⏸️ Waiting |
| Phase 3 | Database Evaluation | 7 | 0 | 0% | ⏸️ Waiting |
| Phase 4 | E2E Integration & Testing | 12 | 0 | 0% | ⏸️ Waiting |
| Phase 5 | Documentation & Refinement | 10 | 0 | 0% | ⏸️ Waiting |
| **TOTAL** | **v6.0 Complete** | **57** | **0** | **0%** | **⏳ Starting** |
| Phase 3: Integration | 6 | 0 | 0% | ⏸️ Waiting |
| Phase 4: E2E Testing | 6 | 0 | 0% | ⏸️ Waiting |
| Phase 5: Documentation | 8 | 0 | 0% | ⏸️ Waiting |
| **TOTAL** | **41** | **0** | **0%** | **🎯 Ready to Start** |

---

## ⏰ Timeline

```
Week 1: Phase 0 - Instinct Layer Foundation
  ├─ Mon-Tue: Folder structure + trigger schema
  ├─ Wed-Thu: Dashboard/metrics/health updaters
  └─ Fri: Testing and validation

Week 2: Phase 1 - Multi-Threaded Crawlers
  ├─ Mon-Tue: Orchestrator + area crawlers
  ├─ Wed-Thu: Progress tracking + BRAIN feeding
  └─ Fri: Performance testing (1000+ files)

Week 3: Phase 2 - Database Evaluation
  ├─ Mon-Tue: Schema design + migration script
  ├─ Wed-Thu: Performance testing
  └─ Fri: Documentation + guidance

Week 4: Phase 3-4 - Integration + E2E Testing
  ├─ Mon-Tue: Move logic to Instinct layer
  ├─ Wed: Design test feature (SignalR notifications)
  ├─ Thu: Execute fire-and-forget workflow
  └─ Fri: Validate all auto-updates

Week 5: Phase 5 - Documentation & Training
  ├─ Mon-Wed: Documentation updates
  ├─ Thu: Training materials
  └─ Fri: Final review and sign-off
```

**Total Duration:** 5 weeks (80-100 hours)  
**Start Date:** 2025-11-04  
**Expected Completion:** 2025-12-09

---

## Executive Summary

This plan transforms KDS into a **fire-and-forget intelligent implementation system** where:

1. **🧠 Instinct Layer Auto-Updates** - Dashboard, metrics, health checks update automatically when functionality changes
2. **� Multi-Threaded Crawlers** - Parallel PowerShell crawlers scan project efficiently and feed BRAIN
3. **💾 Database Evaluation** - Assess if local database (SQLite) improves performance
4. **🎯 E2E Feature Implementation** - Complete features implemented with zero manual infrastructure updates
5. **📊 Self-Maintaining System** - Brain handles categorization, scalability, and extensibility automatically

**Key Philosophy:** 
> "Give the brain a complete feature request and it handles everything—implementation, testing, documentation, AND infrastructure updates—without manual intervention."

---

## Part 1: Instinct Layer - Self-Updating Infrastructure

### Vision: Fire-and-Forget Feature Implementation

**Current Problem:**
When adding new functionality, developers must manually:
- Update dashboard to show new features
- Add metrics collection for new components
- Update health checks to validate new code
- Categorize in the brain structure

**v6.0 Solution:**
The **Instinct Layer** automatically handles infrastructure updates when functionality changes.

### Instinct Layer Architecture

```
KDS/
└── brain/
    └── instinct/                    # Tier 0: PERMANENT INTELLIGENCE
        ├── core-rules.yaml          # 17 governance rules (existing)
        ├── solid-principles.yaml    # Architecture patterns (existing)
        ├── routing-logic.yaml       # Intent detection templates (existing)
        ├── protection-config.yaml   # Confidence thresholds (existing)
        │
        ├── auto-infrastructure/     # NEW: Self-updating systems
        │   ├── dashboard-updater.ps1        # Auto-add dashboard widgets
        │   ├── metrics-collector.ps1        # Auto-add metric collection
        │   ├── health-validator.ps1         # Auto-add health checks
        │   ├── categorizer.ps1              # Auto-categorize in brain
        │   └── trigger-config.yaml          # When to trigger updates
        │
        └── triggers/                # NEW: Event-driven automation
            ├── on-file-create.yaml          # New file → categorize
            ├── on-function-add.yaml         # New function → add metrics
            ├── on-component-add.yaml        # New component → dashboard
            ├── on-test-add.yaml             # New test → health check
            └── trigger-orchestrator.ps1     # Master trigger handler
```

### How It Works: Auto-Update Flow

#### Scenario: Developer adds new "PDF Export" feature

**Traditional Approach (Manual):**
```
1. Developer: Create PdfExportService.cs
2. Developer: Create PdfExportButton.razor
3. Developer: Create PdfExportController.cs
4. Developer: Manually update dashboard to show PDF export status
5. Developer: Manually add metrics for PDF export usage
6. Developer: Manually add health check for PDF service
7. Developer: Manually categorize in brain structure
Total: 7 manual steps
```

**v6.0 Instinct Layer (Automatic):**
```
1. Developer: "#file:KDS/prompts/user/kds.md Add PDF export feature"
2. KDS Planner: Creates plan with test-first approach
3. KDS Executor: Implements PdfExportService.cs
4. 🧠 INSTINCT TRIGGER (on-file-create):
   - Categorizes: "Services/Export/PdfExportService.cs"
   - Adds dashboard widget: "PDF Export Service"
   - Adds metric: "pdf_export_count", "pdf_export_failures"
   - Adds health check: "PdfExportService running?"
5. KDS Executor: Implements PdfExportButton.razor
6. 🧠 INSTINCT TRIGGER (on-component-add):
   - Categorizes: "Components/Export/PdfExportButton.razor"
   - Adds dashboard widget: "PDF Export Button"
   - Updates metrics: "pdf_button_clicks"
7. KDS Executor: Creates tests
8. 🧠 INSTINCT TRIGGER (on-test-add):
   - Adds health check: "PDF export tests passing?"
   
Total Manual Steps: 1 (initial request)
Total Automatic Steps: 12 (infrastructure updates handled by Instinct)
```

### Trigger Configuration

```yaml
# KDS/brain/instinct/triggers/on-file-create.yaml

trigger:
  name: "on-file-create"
  event: "file_created"
  conditions:
    - path_matches: "**/*.cs"
    - contains: "Service"
    
actions:
  categorize:
    brain_tier: "long-term"
    category: "service_layer"
    subcategory: "{{ extract_domain(file_path) }}"
    
  dashboard:
    widget_type: "service_status"
    widget_name: "{{ extract_class_name(file_path) }}"
    metrics:
      - "{{ service_name }}_requests_count"
      - "{{ service_name }}_errors_count"
      - "{{ service_name }}_avg_response_time"
      
  health_check:
    check_type: "service_availability"
    check_name: "{{ service_name }}_health"
    validation:
      - "Service instantiates without errors"
      - "Dependencies resolve correctly"
      
  metrics_collection:
    collector: "service-metrics-collector.ps1"
    metrics:
      - name: "{{ service_name }}_requests"
        type: "counter"
      - name: "{{ service_name }}_response_time"
        type: "histogram"
```

### Auto-Update Mechanism

#### 1. Dashboard Auto-Update

**File:** `KDS/brain/instinct/auto-infrastructure/dashboard-updater.ps1`

```powershell
# Triggered automatically when new functionality added

param(
    [string]$TriggerEvent,      # file_created, function_added, etc.
    [string]$FilePath,          # Path to new file
    [hashtable]$Metadata        # Extracted metadata (class name, etc.)
)

# 1. Analyze new functionality
$category = Get-CategoryFromPath $FilePath
$componentName = $Metadata.ClassName

# 2. Generate dashboard widget
$widgetConfig = @{
    name = "$componentName Widget"
    type = "service_status"
    metrics = @(
        "${componentName}_requests",
        "${componentName}_errors"
    )
    health_check = "${componentName}_health"
}

# 3. Update dashboard configuration
$dashboardConfig = Get-Content "KDS/dashboard/config.yaml" | ConvertFrom-Yaml
$dashboardConfig.widgets += $widgetConfig
$dashboardConfig | ConvertTo-Yaml | Set-Content "KDS/dashboard/config.yaml"

# 4. Generate dashboard HTML fragment
$htmlFragment = @"
<div class="dashboard-widget" data-widget="${componentName}">
  <h3>${componentName}</h3>
  <div class="metric" data-metric="${componentName}_requests">
    <span class="label">Requests:</span>
    <span class="value">0</span>
  </div>
  <div class="health" data-health="${componentName}_health">
    <span class="status">🟢 Healthy</span>
  </div>
</div>
"@

# 5. Inject into dashboard
Add-DashboardWidget -Fragment $htmlFragment -Section $category
```

#### 2. Metrics Auto-Collection

**File:** `KDS/brain/instinct/auto-infrastructure/metrics-collector.ps1`

```powershell
# Triggered when new trackable functionality added

param(
    [string]$ComponentName,
    [string]$ComponentType,     # service, component, api, etc.
    [string]$FilePath
)

# 1. Define standard metrics based on type
$standardMetrics = switch ($ComponentType) {
    "service" {
        @(
            "${ComponentName}_requests_total",
            "${ComponentName}_errors_total",
            "${ComponentName}_duration_ms"
        )
    }
    "component" {
        @(
            "${ComponentName}_renders_total",
            "${ComponentName}_interactions_total",
            "${ComponentName}_errors_total"
        )
    }
    "api" {
        @(
            "${ComponentName}_calls_total",
            "${ComponentName}_response_time_ms",
            "${ComponentName}_status_codes"
        )
    }
}

# 2. Add metrics to collection system
foreach ($metric in $standardMetrics) {
    Add-MetricDefinition -Name $metric -Type "counter" -Component $ComponentName
}

# 3. Update metrics dashboard
Update-MetricsDashboard -Metrics $standardMetrics -Category $ComponentType
```

#### 3. Health Check Auto-Addition

**File:** `KDS/brain/instinct/auto-infrastructure/health-validator.ps1`

```powershell
# Triggered when new testable functionality added

param(
    [string]$ComponentName,
    [string]$ComponentType,
    [string]$FilePath
)

# 1. Define health checks based on type
$healthChecks = switch ($ComponentType) {
    "service" {
        @(
            @{ Name = "${ComponentName}_instantiation"; Test = "Can instantiate without errors" },
            @{ Name = "${ComponentName}_dependencies"; Test = "Dependencies resolve" },
            @{ Name = "${ComponentName}_configuration"; Test = "Configuration valid" }
        )
    }
    "component" {
        @(
            @{ Name = "${ComponentName}_rendering"; Test = "Component renders without errors" },
            @{ Name = "${ComponentName}_props"; Test = "Props validation passes" }
        )
    }
    "test" {
        @(
            @{ Name = "${ComponentName}_execution"; Test = "Test executes successfully" },
            @{ Name = "${ComponentName}_coverage"; Test = "Code coverage meets threshold" }
        )
    }
}

# 2. Add to health validation system
foreach ($check in $healthChecks) {
    Add-HealthCheck -Name $check.Name -Validation $check.Test -Category $ComponentType
}

# 3. Update health dashboard
Update-HealthDashboard -Checks $healthChecks -Component $ComponentName
```

### Extensibility & Scalability

#### Brain Categorization (Automatic)

```powershell
# KDS/brain/instinct/auto-infrastructure/categorizer.ps1

function Categorize-NewFunctionality {
    param($FilePath, $FileType, $Metadata)
    
    # 1. Analyze file characteristics
    $analysis = @{
        domain = Extract-Domain $FilePath          # e.g., "Export", "Authentication"
        layer = Extract-Layer $FilePath            # e.g., "Service", "Component", "API"
        complexity = Measure-Complexity $FilePath  # e.g., "Simple", "Complex"
        dependencies = Get-Dependencies $FilePath  # Related files
    }
    
    # 2. Auto-categorize in brain
    $brainPath = "KDS/brain/long-term/file-relationships.yaml"
    $brain = Get-Content $brainPath | ConvertFrom-Yaml
    
    # Add to appropriate category
    $category = "$($analysis.domain)_$($analysis.layer)"
    $brain.categories[$category] += @{
        file = $FilePath
        complexity = $analysis.complexity
        dependencies = $analysis.dependencies
        added = (Get-Date).ToString("yyyy-MM-dd")
    }
    
    # 3. Update brain
    $brain | ConvertTo-Yaml | Set-Content $brainPath
    
    # 4. Log categorization event
    Log-BrainEvent -Type "categorization" -Details $analysis
}
```

#### Scalability Design

**Handles Growing Codebase:**
```yaml
# Automatic scaling as project grows

small_project:
  files: < 100
  approach: Single-threaded scan
  dashboard_widgets: Basic (5-10 widgets)
  metrics: Essential only
  
medium_project:
  files: 100-1000
  approach: Multi-threaded scan (4 threads)
  dashboard_widgets: Organized by domain (20-50 widgets)
  metrics: Detailed tracking
  health_checks: Comprehensive
  
large_project:
  files: > 1000
  approach: Multi-threaded + caching
  dashboard_widgets: Hierarchical (100+ widgets with grouping)
  metrics: Aggregated + detailed
  health_checks: Tiered (critical vs non-critical)
  database: Consider SQLite for performance
```

### Benefits of Instinct Layer

✅ **Zero Manual Infrastructure Updates**
- Dashboard widgets added automatically
- Metrics collection configured automatically  
- Health checks generated automatically
- Brain categorization happens automatically

✅ **Consistency**
- Same patterns applied to all new functionality
- No forgotten metrics or health checks
- Standardized naming and organization

✅ **Scalability**
- System adjusts to project size automatically
- No manual reorganization needed as project grows
- Performance optimizations kick in automatically

✅ **Developer Experience**
- Focus on features, not infrastructure
- One command implements everything
- Fire-and-forget workflow

---

## Part 2: Multi-Threaded PowerShell Crawlers

---

## Part 2: Multi-Threaded PowerShell Crawlers

### Current State: Single-Threaded Crawler

**Problem:**
- Sequential scanning (slow for large codebases)
- Single responsibility (scans everything)
- Long execution time (5-10 minutes for 1000+ files)
- No progress visibility during scan

**Current Performance:**
```
Small project (< 100 files):   ~30 seconds
Medium project (100-500):      ~2-3 minutes
Large project (500-1000):      ~5-8 minutes
Very large (1000+):            ~10-15 minutes
```

### v6.0 Solution: Area-Specific Multi-Threaded Crawlers

**Architecture:**
```
KDS/scripts/crawlers/
├── orchestrator.ps1                 # Master coordinator
├── ui-crawler.ps1                   # UI components/pages
├── api-crawler.ps1                  # API endpoints/controllers
├── service-crawler.ps1              # Business logic/services
├── test-crawler.ps1                 # Test files
├── config-crawler.ps1               # Configuration files
└── shared/
    ├── file-analyzer.ps1            # Common analysis logic
    ├── dependency-mapper.ps1        # Relationship detection
    └── progress-reporter.ps1        # Real-time progress
```

### Multi-Threaded Crawler Design

#### Master Orchestrator

**File:** `KDS/scripts/crawlers/orchestrator.ps1`

```powershell
param(
    [int]$MaxThreads = 4,            # Default: 4 parallel crawlers
    [switch]$ShowProgress = $true,
    [string]$ProjectRoot = "."
)

# 1. Discover project areas
$projectAreas = @(
    @{ Name = "UI"; Pattern = "**/*.razor,**/*.cshtml,**/*Component.js,**/*Component.tsx"; Crawler = "ui-crawler.ps1" },
    @{ Name = "API"; Pattern = "**/*Controller.cs,**/api/**/*.cs"; Crawler = "api-crawler.ps1" },
    @{ Name = "Services"; Pattern = "**/*Service.cs,**/Services/**/*.cs"; Crawler = "service-crawler.ps1" },
    @{ Name = "Tests"; Pattern = "**/*.spec.ts,**/*Tests.cs,**/Tests/**/*"; Crawler = "test-crawler.ps1" },
    @{ Name = "Config"; Pattern = "**/*.json,**/*.yaml,**/*.config"; Crawler = "config-crawler.ps1" }
)

# 2. Launch parallel crawlers
$jobs = @()
foreach ($area in $projectAreas) {
    Write-Host "🔍 Starting $($area.Name) crawler..." -ForegroundColor Cyan
    
    $job = Start-Job -ScriptBlock {
        param($CrawlerScript, $Pattern, $ProjectRoot, $AreaName)
        
        & "$ProjectRoot/KDS/scripts/crawlers/$CrawlerScript" `
            -Pattern $Pattern `
            -ProjectRoot $ProjectRoot `
            -AreaName $AreaName
            
    } -ArgumentList $area.Crawler, $area.Pattern, $ProjectRoot, $area.Name
    
    $jobs += @{ Job = $job; Area = $area.Name }
}

# 3. Monitor progress with live updates
$completed = 0
$total = $jobs.Count

while ($completed -lt $total) {
    Clear-Host
    Write-Host "=" * 60
    Write-Host "🧠 KDS Multi-Threaded Project Crawler" -ForegroundColor Green
    Write-Host "=" * 60
    Write-Host ""
    
    foreach ($jobInfo in $jobs) {
        $state = $jobInfo.Job.State
        $status = switch ($state) {
            "Running" { "⏳ Scanning..." }
            "Completed" { "✅ Complete" }
            "Failed" { "❌ Error" }
            default { "🔄 $state" }
        }
        
        Write-Host ("{0,-15} {1}" -f $jobInfo.Area, $status)
    }
    
    Write-Host ""
    Write-Host "Progress: $completed / $total areas complete" -ForegroundColor Yellow
    
    $completed = ($jobs | Where-Object { $_.Job.State -eq "Completed" }).Count
    Start-Sleep -Seconds 1
}

# 4. Collect results from all crawlers
Write-Host "`n📊 Consolidating results..." -ForegroundColor Cyan

$allResults = @()
foreach ($jobInfo in $jobs) {
    $result = Receive-Job -Job $jobInfo.Job
    $allResults += @{
        Area = $jobInfo.Area
        Files = $result.Files
        Relationships = $result.Relationships
        Metrics = $result.Metrics
    }
    Remove-Job -Job $jobInfo.Job
}

# 5. Feed BRAIN with consolidated data
Write-Host "🧠 Feeding BRAIN with discoveries..." -ForegroundColor Green

$brainData = @{
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    project_root = $ProjectRoot
    areas = $allResults
    total_files = ($allResults | ForEach-Object { $_.Files.Count } | Measure-Object -Sum).Sum
    total_relationships = ($allResults | ForEach-Object { $_.Relationships.Count } | Measure-Object -Sum).Sum
}

# Update brain
Update-BrainKnowledge -Data $brainData

Write-Host "`n✅ Crawl complete! Discovered $($brainData.total_files) files, $($brainData.total_relationships) relationships" -ForegroundColor Green
```

#### Area-Specific Crawler Example: UI Crawler

**File:** `KDS/scripts/crawlers/ui-crawler.ps1`

```powershell
param(
    [string]$Pattern,
    [string]$ProjectRoot,
    [string]$AreaName
)

# 1. Find all UI files matching pattern
$uiFiles = Get-ChildItem -Path $ProjectRoot -Include ($Pattern -split ',') -Recurse -File

$discoveries = @{
    Files = @()
    Relationships = @()
    Metrics = @{
        ComponentCount = 0
        PageCount = 0
        AvgComplexity = 0
    }
}

# 2. Analyze each file
foreach ($file in $uiFiles) {
    # Extract component metadata
    $content = Get-Content $file.FullName -Raw
    
    $fileData = @{
        Path = $file.FullName.Replace($ProjectRoot, "")
        Type = if ($file.Name -match "Page") { "Page" } else { "Component" }
        Size = $file.Length
        Dependencies = @()
        TestIds = @()
        Events = @()
    }
    
    # 3. Extract data-testid attributes (for Playwright tests)
    $testIdPattern = 'data-testid="([^"]+)"'
    $testIds = [regex]::Matches($content, $testIdPattern) | ForEach-Object { $_.Groups[1].Value }
    $fileData.TestIds = $testIds
    
    # 4. Extract dependencies (imports/using statements)
    $importPattern = '@(using|import)\s+([^;]+)'
    $imports = [regex]::Matches($content, $importPattern) | ForEach-Object { $_.Groups[2].Value.Trim() }
    $fileData.Dependencies = $imports
    
    # 5. Extract events (button clicks, form submits)
    $eventPattern = '@on(click|submit|change)="([^"]+)"'
    $events = [regex]::Matches($content, $eventPattern) | ForEach-Object { $_.Groups[2].Value }
    $fileData.Events = $events
    
    $discoveries.Files += $fileData
    
    # 6. Track relationships
    foreach ($dep in $imports) {
        $discoveries.Relationships += @{
            From = $fileData.Path
            To = $dep
            Type = "imports"
        }
    }
    
    # Update metrics
    if ($fileData.Type -eq "Page") { $discoveries.Metrics.PageCount++ }
    else { $discoveries.Metrics.ComponentCount++ }
}

# 7. Return results
return $discoveries
```

### Performance Comparison

**Single-Threaded (Current):**
```
1000 files total: ~10 minutes
  UI files (400):      ~4 min
  API files (300):     ~3 min
  Services (200):      ~2 min
  Tests (100):         ~1 min

Total: Sequential = 10 minutes
```

**Multi-Threaded (v6.0):**
```
1000 files total: ~4 minutes (60% faster!)
  UI files (400):      4 min ┐
  API files (300):     3 min ├─ Parallel
  Services (200):      2 min │  (4 threads)
  Tests (100):         1 min ┘

Total: Parallel = 4 minutes (limited by slowest crawler)
```

### BRAIN Feeding Integration

**After Multi-Threaded Scan:**

```powershell
# KDS/scripts/crawlers/feed-brain.ps1

function Update-BrainKnowledge {
    param($Data)
    
    # 1. Load current brain knowledge
    $brainPath = "KDS/brain/long-term"
    
    # 2. Update file relationships
    $relationships = Get-Content "$brainPath/file-relationships.yaml" | ConvertFrom-Yaml
    
    foreach ($area in $Data.areas) {
        foreach ($rel in $area.Relationships) {
            # Add or update relationship
            $key = "$($rel.From)|$($rel.To)"
            if (-not $relationships.relationships.ContainsKey($key)) {
                $relationships.relationships[$key] = @{
                    from = $rel.From
                    to = $rel.To
                    type = $rel.Type
                    confidence = 0.95  # High confidence (directly observed)
                    first_seen = $Data.timestamp
                    last_seen = $Data.timestamp
                    occurrence_count = 1
                }
            } else {
                $relationships.relationships[$key].last_seen = $Data.timestamp
                $relationships.relationships[$key].occurrence_count++
            }
        }
    }
    
    # 3. Update test patterns (extracted test IDs)
    $testPatterns = Get-Content "$brainPath/test-patterns.yaml" | ConvertFrom-Yaml
    
    $uiArea = $Data.areas | Where-Object { $_.Area -eq "UI" }
    foreach ($file in $uiArea.Files) {
        if ($file.TestIds.Count -gt 0) {
            $componentName = [System.IO.Path]::GetFileNameWithoutExtension($file.Path)
            
            $testPatterns.ui_test_ids[$componentName] = @{
                file = $file.Path
                test_ids = $file.TestIds
                coverage = if ($file.TestIds.Count -gt 5) { "comprehensive" } else { "basic" }
                last_updated = $Data.timestamp
            }
        }
    }
    
    # 4. Update architectural patterns
    $archPatterns = Get-Content "$brainPath/architectural-patterns.yaml" | ConvertFrom-Yaml
    
    # Detect patterns (e.g., "All services inherit from BaseService")
    $serviceArea = $Data.areas | Where-Object { $_.Area -eq "Services" }
    $baseClasses = $serviceArea.Files | Where-Object { $_.Dependencies -contains "BaseService" }
    
    if ($baseClasses.Count -gt 5) {
        $archPatterns.patterns.service_inheritance = @{
            pattern = "Services inherit from BaseService"
            confidence = [math]::Round($baseClasses.Count / $serviceArea.Files.Count, 2)
            examples = $baseClasses | Select-Object -First 3 -ExpandProperty Path
            discovered = $Data.timestamp
        }
    }
    
    # 5. Save updated brain
    $relationships | ConvertTo-Yaml | Set-Content "$brainPath/file-relationships.yaml"
    $testPatterns | ConvertTo-Yaml | Set-Content "$brainPath/test-patterns.yaml"
    $archPatterns | ConvertTo-Yaml | Set-Content "$brainPath/architectural-patterns.yaml"
    
    Write-Host "✅ BRAIN updated with crawler discoveries" -ForegroundColor Green
}
```

### Progress Tracking & User Experience

**Real-Time Progress Display:**

```
═══════════════════════════════════════════════════════
🧠 KDS Multi-Threaded Project Crawler
═══════════════════════════════════════════════════════

UI             ⏳ Scanning... (247 files found)
API            ⏳ Scanning... (156 files found)
Services       ✅ Complete (198 files, 342 relationships)
Tests          ⏳ Scanning... (89 files found)
Config         ✅ Complete (23 files, 45 relationships)

Progress: 2 / 5 areas complete
Elapsed: 2m 15s | Est. Remaining: 1m 45s

[████████████░░░░░░░░] 60%
═══════════════════════════════════════════════════════
```

### Benefits of Multi-Threaded Crawlers

✅ **60% Faster** - Parallel execution
✅ **Area-Specific Intelligence** - Each crawler specializes in one domain
✅ **Better Progress Visibility** - Real-time updates per area
✅ **Scalability** - Add more crawlers easily (database crawler, infrastructure crawler)
✅ **Efficient BRAIN Feeding** - Consolidated, structured data

---

## Part 3: Database Evaluation (SQLite vs Files)

### Current State: File-Based Storage

**BRAIN Storage:**
```
KDS/brain/
├── long-term/
│   ├── file-relationships.yaml       (~50-200 KB)
│   ├── intent-patterns.yaml          (~20-50 KB)
│   ├── workflow-templates.yaml       (~30-80 KB)
│   ├── test-patterns.yaml            (~20-60 KB)
│   └── architectural-patterns.yaml   (~30-70 KB)
├── working-memory/
│   ├── conversation-history.jsonl    (~100-300 KB)
│   └── recent-conversations/         (~20 files, ~5-10 KB each)
└── context-awareness/
    ├── git-metrics.yaml              (~30-80 KB)
    ├── velocity-tracking.yaml        (~20-50 KB)
    └── file-hotspots.yaml            (~15-40 KB)

Total: ~500 KB - 1.5 MB (current NoorCanvas project)
```

**Performance (File-Based):**
```
Read file-relationships.yaml:     ~50 ms
Query specific relationship:      ~100 ms (parse entire file)
Write updated relationship:       ~80 ms (rewrite entire file)
Full brain query (5 files):       ~300 ms

Good for: Small-medium projects (< 5000 files scanned)
Slow for: Large projects (> 10000 files scanned)
```

### Database Option: SQLite

**When to Consider Database:**
- Project has > 5000 files
- BRAIN data exceeds 5 MB
- Query performance > 500 ms
- Frequent updates (> 100/day)

**SQLite Benefits:**
- ✅ **Faster Queries** - Indexed lookups (~5-10 ms vs ~100 ms)
- ✅ **Partial Reads** - Read only needed data (not entire file)
- ✅ **Atomic Updates** - Update single row (not rewrite file)
- ✅ **Relational Queries** - Complex relationships easier
- ✅ **Zero Dependencies** - SQLite built into PowerShell 7+

**SQLite Drawbacks:**
- ❌ **Complexity** - Adds database layer
- ❌ **Migration Effort** - Convert YAML → SQL schema
- ❌ **Less Human-Readable** - Can't easily browse with text editor
- ❌ **Portability** - Binary file (vs portable YAML)

### Recommended Approach: Hybrid (Files + Optional DB)

**Decision Tree:**
```yaml
project_size: small           # < 1000 files scanned
brain_size: < 1 MB
query_time: < 200 ms
→ Use: File-based storage (current approach)
→ Benefit: Simple, portable, human-readable

project_size: medium          # 1000-5000 files
brain_size: 1-5 MB
query_time: 200-500 ms
→ Use: File-based storage with caching
→ Benefit: Still simple, add in-memory cache for frequently accessed data

project_size: large           # 5000-10000 files
brain_size: 5-20 MB
query_time: > 500 ms
→ Use: SQLite database
→ Benefit: Performance improvement, faster queries

project_size: very large      # > 10000 files
brain_size: > 20 MB
query_time: > 1 second
→ Use: SQLite database + query optimization
→ Benefit: Only way to maintain performance
```

### SQLite Schema Design (If Implemented)

**File:** `KDS/brain/database/schema.sql`

```sql
-- File relationships
CREATE TABLE file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_file TEXT NOT NULL,
    to_file TEXT NOT NULL,
    relationship_type TEXT NOT NULL,  -- imports, co_modified, tests, etc.
    confidence REAL DEFAULT 0.5,
    occurrence_count INTEGER DEFAULT 1,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_file, to_file, relationship_type)
);

CREATE INDEX idx_from_file ON file_relationships(from_file);
CREATE INDEX idx_to_file ON file_relationships(to_file);
CREATE INDEX idx_confidence ON file_relationships(confidence DESC);

-- Intent patterns
CREATE TABLE intent_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL UNIQUE,
    intent TEXT NOT NULL,          -- PLAN, EXECUTE, TEST, etc.
    confidence REAL DEFAULT 0.5,
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    last_used DATETIME
);

CREATE INDEX idx_intent ON intent_patterns(intent);
CREATE INDEX idx_phrase ON intent_patterns(phrase);

-- Architectural patterns
CREATE TABLE architectural_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL UNIQUE,
    pattern_type TEXT,             -- service_layer, component_structure, etc.
    description TEXT,
    confidence REAL DEFAULT 0.5,
    examples TEXT,                 -- JSON array of example file paths
    discovered_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Test patterns
CREATE TABLE test_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_name TEXT NOT NULL,
    test_ids TEXT,                 -- JSON array of data-testid values
    file_path TEXT,
    coverage TEXT,                 -- basic, comprehensive
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(component_name)
);
```

### Migration Strategy (Files → Database)

**File:** `KDS/scripts/migrate-to-database.ps1`

```powershell
param(
    [string]$BrainPath = "KDS/brain",
    [string]$DatabasePath = "KDS/brain/database/knowledge.db",
    [switch]$DryRun
)

# 1. Create SQLite database
if (-not $DryRun) {
    $null = New-Item -ItemType Directory -Path "KDS/brain/database" -Force
    
    # Create schema
    $schema = Get-Content "KDS/brain/database/schema.sql" -Raw
    Invoke-SqliteQuery -DataSource $DatabasePath -Query $schema
}

# 2. Migrate file-relationships.yaml
$relationships = Get-Content "$BrainPath/long-term/file-relationships.yaml" | ConvertFrom-Yaml

foreach ($rel in $relationships.relationships.Values) {
    if ($DryRun) {
        Write-Host "Would migrate: $($rel.from) → $($rel.to)"
    } else {
        $query = @"
INSERT INTO file_relationships (from_file, to_file, relationship_type, confidence, occurrence_count, first_seen, last_seen)
VALUES (@from, @to, @type, @confidence, @count, @first_seen, @last_seen)
ON CONFLICT(from_file, to_file, relationship_type) 
DO UPDATE SET 
    occurrence_count = occurrence_count + 1,
    last_seen = @last_seen
"@
        
        Invoke-SqliteQuery -DataSource $DatabasePath -Query $query -SqlParameters @{
            from = $rel.from
            to = $rel.to
            type = $rel.type
            confidence = $rel.confidence
            count = $rel.occurrence_count
            first_seen = $rel.first_seen
            last_seen = $rel.last_seen
        }
    }
}

# 3. Migrate intent-patterns.yaml
# ... similar approach for other brain files

Write-Host "✅ Migration complete! Database ready at $DatabasePath"
```

### Recommendation for v6.0

**Current Decision:** **Keep file-based storage**

**Rationale:**
1. NoorCanvas project: ~1000 files → File-based still fast (<200ms queries)
2. BRAIN size: ~500 KB → Well within performant range
3. Simplicity: No migration complexity, human-readable
4. Portability: Easy to share KDS across projects (just copy folder)

**Future-Proof:**
- Monitor BRAIN size in health checks
- If exceeds 5 MB → Show warning: "Consider database migration for better performance"
- Provide migration script when needed
- Make database **opt-in** (not forced)

**Implementation:**
```yaml
# KDS/brain/health/capacity-metrics.yaml

storage_monitoring:
  current_size: "487 KB"
  threshold_warning: "5 MB"
  threshold_critical: "20 MB"
  recommendation: "file-based"   # or "consider-database" or "database-required"
  
  performance_metrics:
    avg_query_time: "145 ms"
    threshold_slow: "500 ms"
    threshold_critical: "1000 ms"
```

---

## Part 4: Integration - Fire-and-Forget Workflow
---

## Part 4: Integration - Fire-and-Forget Workflow

### Complete E2E Feature Implementation

**User Experience:**
```markdown
User: "#file:KDS/prompts/user/kds.md Add real-time notifications with SignalR"
KDS: [30 minutes later]
     ✅ Feature implemented
     ✅ Tests passing
     ✅ Dashboard updated
     ✅ Metrics collecting
     ✅ Health checks added
     ✅ Documentation updated
     
     Ready to use!
```

### Workflow Breakdown

```
USER REQUEST
    ↓
1. INTENT ROUTER
   - Analyzes: "Add real-time notifications with SignalR"
   - Intent: PLAN (new feature)
   - Routes to: work-planner.md
    ↓
2. WORK PLANNER
   - Queries BRAIN: "SignalR patterns?"
   - Creates plan:
     Phase 1: Infrastructure (Hub, Configuration)
     Phase 2: Implementation (Service, Client integration)
     Phase 3: Testing (Unit + Integration tests)
    ↓
3. CODE EXECUTOR (Phase 1, Task 1)
   - Creates: NotificationHub.cs
   - 🧠 INSTINCT TRIGGER (on-file-create):
     ✅ Categorizes → Services/Notifications/NotificationHub.cs
     ✅ Adds dashboard widget → "Notification Hub Status"
     ✅ Adds metrics:
        - notification_hub_connections_total
        - notification_hub_messages_sent_total
        - notification_hub_errors_total
     ✅ Adds health check:
        - NotificationHub instantiation
        - SignalR dependency resolution
    ↓
4. CODE EXECUTOR (Phase 1, Task 2)
   - Configures: Program.cs (AddSignalR, MapHub)
   - 🧠 INSTINCT TRIGGER (on-config-change):
     ✅ Updates health check:
        - SignalR middleware configured
        - Hub endpoint registered
    ↓
5. CODE EXECUTOR (Phase 2, Task 1)
   - Creates: NotificationService.cs
   - 🧠 INSTINCT TRIGGER (on-file-create):
     ✅ Categorizes → Services/Notifications/NotificationService.cs
     ✅ Detects relationship: NotificationService → NotificationHub
     ✅ Updates BRAIN: file_relationships
     ✅ Adds metrics:
        - notification_service_send_count
        - notification_service_errors
    ↓
6. CODE EXECUTOR (Phase 2, Task 2)
   - Creates: NotificationComponent.razor
   - 🧠 INSTINCT TRIGGER (on-component-add):
     ✅ Categorizes → Components/Notifications/NotificationComponent.razor
     ✅ Extracts data-testid: "notification-bell", "notification-list"
     ✅ Updates dashboard → "Notification UI" widget
     ✅ Adds metrics:
        - notification_ui_renders_total
        - notification_clicks_total
    ↓
7. TEST GENERATOR
   - Creates tests:
     - NotificationHubTests.cs (unit)
     - NotificationServiceTests.cs (unit)
     - notification-component.spec.ts (Playwright)
   - 🧠 INSTINCT TRIGGER (on-test-add):
     ✅ Adds health checks:
        - NotificationHub tests passing
        - NotificationService tests passing
        - Notification UI tests passing
     ✅ Updates dashboard → "Test Coverage: Notifications"
    ↓
8. HEALTH VALIDATOR
   - Runs validation:
     ✅ All tests passing
     ✅ Build successful
     ✅ No rule violations
   - 🧠 INSTINCT AUTOMATIC:
     ✅ Dashboard shows all green
     ✅ Metrics collecting data
     ✅ Health checks validating
    ↓
9. COMMIT HANDLER
   - Creates semantic commit:
     "feat(notifications): Add real-time SignalR notifications"
   - Includes:
     - 5 source files (Hub, Service, Component, Config, Tests)
     - Auto-generated dashboard updates
     - Auto-generated metrics collection
     - Auto-generated health checks
    ↓
COMPLETE (Zero manual infrastructure updates!)
```

### Instinct Layer Triggers Used

**During Implementation:**

```yaml
# Trigger log (automatic, no user intervention)

[14:32:15] on-file-create → NotificationHub.cs
           Actions: categorize, dashboard-widget, metrics-add, health-check
           
[14:35:22] on-config-change → Program.cs
           Actions: health-check-update
           
[14:38:41] on-file-create → NotificationService.cs
           Actions: categorize, relationship-detect, metrics-add
           
[14:42:18] on-component-add → NotificationComponent.razor
           Actions: categorize, test-id-extract, dashboard-widget, metrics-add
           
[14:48:53] on-test-add → NotificationHubTests.cs, NotificationServiceTests.cs, notification-component.spec.ts
           Actions: health-check-add, dashboard-update
           
[14:52:07] on-validation-complete → All tests passing
           Actions: dashboard-status-green, metrics-validate, health-report

Total automatic actions: 18
Manual actions required: 0
```

### Real-Time Dashboard Updates

**Before Implementation:**
```
═══════════════════════════════════════════════════════
🧠 KDS Health Dashboard
═══════════════════════════════════════════════════════

Features: 12 implemented

Services:
  - HostControlPanelService      ✅ Healthy
  - SessionService                ✅ Healthy
  - ZoomIntegrationService        ✅ Healthy

Components:
  - HostControlPanel             ✅ Healthy
  - FAB Button                   ✅ Healthy
  - User Registration            ✅ Healthy

Tests: 89 passing, 0 failing
Build: ✅ Passing
Health Score: 94/100
═══════════════════════════════════════════════════════
```

**After Implementation (Automatic):**
```
═══════════════════════════════════════════════════════
🧠 KDS Health Dashboard
═══════════════════════════════════════════════════════

Features: 13 implemented  (+1 NEW!)

Services:
  - HostControlPanelService      ✅ Healthy
  - SessionService                ✅ Healthy
  - ZoomIntegrationService        ✅ Healthy
  - NotificationService          ✅ Healthy  ⭐ NEW
  - NotificationHub              ✅ Healthy  ⭐ NEW

Components:
  - HostControlPanel             ✅ Healthy
  - FAB Button                   ✅ Healthy
  - User Registration            ✅ Healthy
  - NotificationComponent        ✅ Healthy  ⭐ NEW

Metrics (Notifications):
  - Hub Connections: 0           ⭐ NEW
  - Messages Sent: 0             ⭐ NEW
  - UI Renders: 0                ⭐ NEW

Tests: 95 passing (+6), 0 failing  ⭐ UPDATED
Build: ✅ Passing
Health Score: 96/100 (+2)          ⭐ IMPROVED
═══════════════════════════════════════════════════════
```

---

## Part 5: Implementation Plan

### Phase 0: Foundation (Week 1)

**Goals:**
- Design Instinct Layer architecture
- Create trigger framework
- Implement basic auto-update mechanisms

**Tasks:**
1. ✅ Create `KDS/brain/instinct/auto-infrastructure/` folder structure
2. ✅ Design trigger configuration schema
3. ✅ Implement dashboard-updater.ps1
4. ✅ Implement metrics-collector.ps1
5. ✅ Implement health-validator.ps1
6. ✅ Implement categorizer.ps1
7. ✅ Create trigger-orchestrator.ps1
8. ✅ Test basic trigger flow (file create → dashboard update)

**Success Criteria:**
- Create file → Dashboard updates automatically
- New service → Metrics added automatically
- New component → Health checks added automatically

---

### Phase 1: Multi-Threaded Crawlers (Week 2)

**Goals:**
- Replace single-threaded crawler with parallel crawlers
- Improve scan performance by 60%
- Enhance BRAIN feeding with structured data

**Tasks:**
1. ✅ Create crawler orchestrator.ps1
2. ✅ Implement ui-crawler.ps1
3. ✅ Implement api-crawler.ps1
4. ✅ Implement service-crawler.ps1
5. ✅ Implement test-crawler.ps1
6. ✅ Add real-time progress tracking
7. ✅ Enhance BRAIN feeding logic
8. ✅ Test on NoorCanvas project (1000+ files)

**Success Criteria:**
- Scan 1000 files in < 5 minutes (vs ~10 minutes currently)
- Real-time progress shows per-area status
- BRAIN populated with relationships, test IDs, patterns

---

### Phase 2: Database Evaluation (Week 3)

**Goals:**
- Analyze performance at scale
- Design SQLite schema (if needed)
- Create migration strategy
- Make database opt-in

**Tasks:**
1. ✅ Add storage monitoring to health checks
2. ✅ Define size/performance thresholds
3. ✅ Design SQLite schema
4. ✅ Create migrate-to-database.ps1 script
5. ✅ Test migration on sample data
6. ✅ Document when to use database vs files
7. ✅ Make database optional (config-driven)

**Success Criteria:**
- Health dashboard shows storage metrics
- Migration script works (tested)
- Clear guidance on when to migrate
- Database remains optional for small projects

---

### Phase 3: Integration & E2E Testing (Week 4)

**Goals:**
- Test complete fire-and-forget workflow
- Validate all auto-updates working
- Measure time savings

**Tasks:**
1. ✅ Design test feature (complex, multi-file)
2. ✅ Execute fire-and-forget implementation
3. ✅ Validate dashboard auto-updated
4. ✅ Validate metrics auto-added
5. ✅ Validate health checks auto-added
6. ✅ Validate BRAIN auto-categorized
7. ✅ Measure time-to-completion
8. ✅ Document workflow

**Test Feature:** "Add real-time notifications with SignalR"
- Expected files: 5-7 (Hub, Service, Component, Config, Tests)
- Expected auto-updates: 15-20 (dashboard, metrics, health)
- Expected time: 25-35 minutes (vs 60+ minutes manual)

**Success Criteria:**
- Feature implemented end-to-end
- Zero manual dashboard updates
- Zero manual metric additions
- Zero manual health check additions
- 40%+ time savings

---

### Phase 4: Documentation & Refinement (Week 5)

**Goals:**
- Document Instinct Layer architecture
- Document multi-threaded crawlers
- Document fire-and-forget workflow
- Refine based on testing feedback

**Tasks:**
1. ✅ Update KDS-DESIGN.md with v6.0 architecture
2. ✅ Document Instinct Layer triggers
3. ✅ Document crawler usage
4. ✅ Document database decision
5. ✅ Create fire-and-forget workflow guide
6. ✅ Update user documentation (kds.md)
7. ✅ Create troubleshooting guide
8. ✅ Collect feedback and refine

**Success Criteria:**
- Complete v6.0 documentation
- Clear user guides
- Troubleshooting coverage
- Team can use fire-and-forget workflow

---

## Success Metrics

### Completion Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| **Auto-Update Coverage** | 100% | New functionality triggers dashboard/metrics/health updates |
| **Crawler Performance** | 60% faster | 1000 files scanned in < 5 minutes |
| **Fire-and-Forget Success** | 90%+ | Complex features implemented with zero manual infrastructure updates |
| **Time Savings** | 40%+ | Feature implementation time reduced |
| **Database Decision** | Documented | Clear guidance on when to use database |
| **User Satisfaction** | High | Team can confidently use fire-and-forget workflow |

### Quality Gates

**Before v6.0 Release:**
- ✅ All Instinct triggers tested and working
- ✅ Multi-threaded crawlers 60% faster
- ✅ E2E fire-and-forget test passes
- ✅ No manual infrastructure updates needed
- ✅ Dashboard auto-updates working
- ✅ Metrics auto-collection working
- ✅ Health checks auto-added working
- ✅ Documentation complete
- ✅ Database guidance clear

---

## Key Design Decisions

### Decision 1: Instinct Layer as Auto-Infrastructure

**Rationale:**
- Developers shouldn't update dashboards manually
- Metrics collection should be automatic
- Health checks should generate automatically
- Categorization should happen automatically

**Benefits:**
- Fire-and-forget feature implementation
- Consistency across all features
- No forgotten infrastructure updates
- Faster development

---

### Decision 2: Multi-Threaded PowerShell Crawlers

**Rationale:**
- Current single-threaded crawler slow (10 min for 1000 files)
- PowerShell supports parallel jobs easily
- Area-specific crawlers provide better insights
- Real-time progress improves UX

**Benefits:**
- 60% performance improvement
- Better specialization (UI, API, Services, Tests)
- Enhanced BRAIN feeding
- Scalable (add more crawlers easily)

---

### Decision 3: Database as Optional (Not Forced)

**Rationale:**
- Current projects: File-based performs well
- Database adds complexity
- Migration should be opt-in
- Monitor and recommend, don't force

**Benefits:**
- Simplicity for small/medium projects
- Future-proof for large projects
- Clear migration path when needed
- User choice based on needs

---

### Decision 4: Fire-and-Forget Workflow

**Rationale:**
- KDS should handle EVERYTHING
- User gives high-level feature request
- KDS implements, tests, documents, AND updates infrastructure
- Zero manual follow-up needed

**Benefits:**
- True "brain" behavior (handles complexity)
- Massive time savings
- Consistent results
- Developer happiness

---

## Risk Assessment

### High Risk Items

1. **Trigger Complexity** - Risk: Triggers fail or conflict
   - Mitigation: Comprehensive testing, error handling, rollback capability

2. **Performance Overhead** - Risk: Auto-updates slow down development
   - Mitigation: Async triggers, throttling, performance monitoring

### Medium Risk Items

3. **False Positives** - Risk: Triggers activate incorrectly
   - Mitigation: Clear trigger conditions, validation before action

4. **Database Migration** - Risk: Data loss during migration
   - Mitigation: Backups, dry-run mode, thorough testing

### Low Risk Items

5. **Documentation Drift** - Risk: Docs out of sync
   - Mitigation: Auto-generate docs where possible, Rule #16 enforcement

---

## Next Steps

### Immediate Actions (This Week)

1. ✅ Review and approve this plan
2. ✅ Begin Phase 0 implementation
3. ✅ Create Instinct Layer folder structure
4. ✅ Design trigger configuration schema

### Phase 0 Execution (Week 1)

1. Implement dashboard-updater.ps1
2. Implement metrics-collector.ps1
3. Implement health-validator.ps1
4. Implement categorizer.ps1
5. Create trigger-orchestrator.ps1
6. Test basic trigger flow

### Tracking Progress

- Update progress checklist at top of this document
- Weekly status updates
- Phase completion reviews
- Adjust timeline as needed

---

## Conclusion

This holistic v6.0 plan transforms KDS into a **true intelligent assistant** that:

✅ **Instinct Layer** - Automatically updates dashboard, metrics, and health checks when functionality changes  
✅ **Multi-Threaded Crawlers** - Scans projects 60% faster with area-specific intelligence  
✅ **Database Evaluation** - Provides clear path to SQLite when performance demands it  
✅ **Fire-and-Forget** - Implements complete features including all infrastructure updates  
✅ **Self-Maintaining** - Brain handles categorization, scalability, and extensibility automatically

**Philosophy:** 
> "The brain should handle everything. Give it a feature request, and it delivers a complete, tested, documented, infrastructure-updated implementation—no manual follow-up needed."

**Estimated Timeline:** 5 weeks  
**Effort:** ~80-100 hours total  
**Complexity:** Medium-High (sophisticated automation)

**Key Differentiator:** This is no longer just a "framework"—it's an intelligent assistant that thinks holistically about implementation, testing, AND infrastructure.

Ready to begin Phase 0! 🚀

---

**Version:** 6.0.0-PLAN  
**Status:** 📋 READY FOR IMPLEMENTATION  
**Next:** Phase 0 - Instinct Layer Foundation (Week 1)
```
KDS/
├── brain/
│   ├── instinct/           # Tier 0: PERMANENT (Never reset)
│   │   ├── core-rules.yaml         # 17 governance rules
│   │   ├── solid-principles.yaml   # Architecture patterns
│   │   ├── routing-logic.yaml      # Intent detection templates
│   │   └── protection-config.yaml  # Confidence thresholds
│   │
│   ├── working-memory/     # Tier 1: SHORT-TERM (FIFO queue)
│   │   ├── active-conversation.jsonl    # Current chat
│   │   ├── recent-conversations/        # Last 20 (FIFO)
│   │   │   ├── 2025-11-04-143022.jsonl
│   │   │   └── 2025-11-03-091544.jsonl
│   │   └── conversation-index.yaml      # Quick lookup
│   │
│   ├── long-term/          # Tier 2: LEARNED PATTERNS (Consolidated)
│   │   ├── intent-patterns.yaml         # "add button" → PLAN
│   │   ├── file-relationships.yaml      # Co-modification patterns
│   │   ├── workflow-templates.yaml      # Proven sequences
│   │   ├── error-patterns.yaml          # Common mistakes
│   │   └── test-patterns.yaml           # Successful strategies
│   │
│   ├── context-awareness/  # Tier 3: PROJECT INTELLIGENCE
│   │   ├── git-metrics.yaml            # Commit patterns
│   │   ├── velocity-tracking.yaml      # Development speed
│   │   ├── file-hotspots.yaml          # High-churn files
│   │   ├── pr-intelligence.yaml        # NEW: PR patterns
│   │   └── productivity-patterns.yaml  # Optimal work times
│   │
│   ├── imagination/        # Tier 4: CREATIVE IDEAS
│   │   ├── questions-answered.yaml     # Deduplication cache
│   │   ├── ideas-stashed.yaml          # Future enhancements
│   │   └── semantic-links.yaml         # Idea relationships
│   │
│   ├── housekeeping/       # Tier 5: AUTOMATIC MAINTENANCE (NEW!)
│   │   ├── services/                   # Background workers
│   │   │   ├── cleanup-service.ps1         # Automatic flush
│   │   │   ├── organizer-service.ps1       # Consolidate patterns
│   │   │   ├── optimizer-service.ps1       # Performance tuning
│   │   │   ├── indexer-service.ps1         # Rebuild indices
│   │   │   ├── validator-service.ps1       # Integrity checks
│   │   │   ├── archiver-service.ps1        # Archive old data
│   │   │   └── orchestrator.ps1            # Master scheduler
│   │   │
│   │   ├── schedules/                  # When to run
│   │   │   ├── daily-tasks.yaml
│   │   │   ├── weekly-tasks.yaml
│   │   │   ├── monthly-tasks.yaml
│   │   │   └── on-demand-tasks.yaml
│   │   │
│   │   ├── logs/                       # Activity history
│   │   │   ├── 2025-11-04-cleanup.log
│   │   │   └── latest.log
│   │   │
│   │   └── config/                     # Thresholds & rules
│   │       ├── service-config.yaml
│   │       └── thresholds.yaml
│   │
│   ├── event-stream/       # Raw activity log
│   │   ├── events.jsonl                # Append-only log
│   │   └── event-index.yaml            # Fast lookup
│   │
│   └── health/             # Brain diagnostics
│       ├── last-flush.yaml             # Cleanup tracking
│       ├── capacity-metrics.yaml       # Storage stats
│       ├── learning-efficiency.yaml    # Month-over-month
│       └── sharpener-results/          # Test reports
│           ├── 2025-11-04.yaml
│           └── latest.yaml
│
├── agents/                 # Renamed from prompts/internal/
│   ├── core/               # 10 specialist agents
│   ├── shared/             # Abstractions
│   └── user-interface/     # Simplified entry points
│
├── knowledge-base/         # Renamed from knowledge/
│   ├── test-strategies/
│   ├── test-data/
│   ├── ui-mappings/
│   └── workflows/
│
├── active-work/            # Renamed from sessions/
│   ├── current-session.json
│   └── session-history/
│
├── tooling/
├── scripts/
├── governance/
└── dashboard/
```

### Brain Region Mapping (Biological Inspiration)

| Brain Region | Biological Function | KDS Folder | Purpose |
|--------------|---------------------|------------|---------|
| **Brainstem** | Automatic responses | `instinct/` | Core rules, never change |
| **Hippocampus** | Short-term memory | `working-memory/` | Recent 20 conversations |
| **Cortex** | Long-term learning | `long-term/` | Consolidated patterns |
| **Prefrontal Cortex** | Context & planning | `context-awareness/` | Project metrics |
| **Creative Centers** | Imagination | `imagination/` | Ideas & questions |
| **Cerebellum** | Automatic maintenance | `housekeeping/` | Background cleanup |
| **Neural Activity** | Firing patterns | `event-stream/` | Activity log |
| **Monitoring Systems** | Health checks | `health/` | Self-diagnostics |

### Migration Strategy

**Phase 1: Create New Structure (Non-Breaking)**
1. Create new `brain/` folder structure
2. Keep old `kds-brain/` folder intact
3. Dual-write to both locations during transition

**Phase 2: Migrate Data**
1. Copy `conversation-history.jsonl` → `working-memory/recent-conversations/`
2. Split `knowledge-graph.yaml` into specialized files:
   - Intent patterns → `long-term/intent-patterns.yaml`
   - File relationships → `long-term/file-relationships.yaml`
   - Workflows → `long-term/workflow-templates.yaml`
3. Move `development-context.yaml` → `context-awareness/`
4. Split into specialized metrics files

**Phase 3: Update Agents**
1. Update all file references to new paths
2. Use `file-accessor.md` abstraction (already exists)
3. Update `brain-query.md` to search new structure

**Phase 4: Deprecate Old Structure**
1. Mark `kds-brain/` as deprecated
2. Create symlinks for backward compatibility
3. Remove old folder after validation period

**Benefits of New Structure:**
- ✅ **Intuitive** - Brain analogy makes sense to humans
- ✅ **Organized** - Each tier has clear purpose
- ✅ **Scalable** - Easy to add new intelligence types
- ✅ **Discoverable** - Folder names explain contents
- ✅ **Biological Accuracy** - Maps to real brain functions

---

## Part 2: Brain Flush Mechanism

### Problem Statement

**Current Issue:** BRAIN accumulates data indefinitely without cleanup:
- Unused patterns stay forever (clutters knowledge)
- Stale conversations never expire (wastes space)
- Low-confidence patterns persist (noise vs signal)
- Failed experiments remain (outdated learning)

**Goal:** Automatic, intelligent cleanup that preserves valuable knowledge while removing noise.

### Flush Strategy (Multi-Tier)

#### Tier 1: Working Memory (Aggressive Flush)
```yaml
flush_policy:
  type: "FIFO Queue"
  capacity: 20 conversations
  retention: "Until FIFO deletion (no time limit)"
  trigger: "When conversation #21 starts"
  preservation: "Active conversation always protected"
  
  additional_cleanup:
    - Empty conversations (0 messages): DELETE immediately
    - Error-only conversations: DELETE after 7 days
    - Duplicate conversations (>95% similar): MERGE
```

**Implementation:** Already exists (conversation-history.jsonl FIFO)

#### Tier 2: Long-Term Memory (Selective Flush)
```yaml
flush_policy:
  patterns:
    unused_threshold: 90 days          # Pattern not used in 90 days
    low_confidence: <0.70              # Confidence below routing threshold
    low_success_rate: <50%             # Pattern fails >50% of time
    duplicate_similarity: >85%         # Merge similar patterns
    
  actions:
    unused_90days: ARCHIVE to .flushed/
    low_confidence: DELETE if <3 occurrences
    low_success: ARCHIVE with failure analysis
    duplicates: MERGE and update confidence
    
  exceptions:
    - KDS governance patterns (scope: kds_internal_governance)
    - Generic templates (contains [X] placeholders)
    - High-value patterns (success_rate >90%, used >10x)
```

**Flush Triggers:**
- **Manual:** `#file:KDS/prompts/user/kds.md flush brain`
- **Automatic:** Weekly (Sunday 2am), or when Tier 2 >500 KB

#### Tier 3: Context Awareness (Rolling Window)
```yaml
flush_policy:
  git_metrics:
    lookback_window: 30 days           # Only recent commits matter
    older_data: ARCHIVE to monthly summaries
    
  velocity_tracking:
    retention: 6 months rolling        # Historical trends
    aggregation: Weekly → Monthly → Quarterly
    
  file_hotspots:
    stale_threshold: 14 days           # Hotspot if modified recently
    cool_down: REMOVE if >14 days quiet
    
  pr_intelligence:
    retention: 30 days raw data        # PR details
    patterns: Keep forever             # Learned patterns
```

**Flush Triggers:**
- **Automatic:** After each Tier 3 collection (>1 hour throttle)
- **Rolling:** Keeps 30-day window, archives older

#### Tier 4: Imagination (Idea Lifecycle)
```yaml
flush_policy:
  questions:
    answered: Keep forever (deduplication cache)
    frequency_threshold: Archive if asked <2x in 90 days
    
  ideas:
    active: Keep while status = "active"
    implemented: ARCHIVE after 30 days (move to long-term patterns)
    stale: ARCHIVE if no activity in 60 days
    abandoned: DELETE if marked "abandoned"
```

### Flush Algorithm (Smart Cleanup)

```yaml
brain_flush_algorithm:
  step_1_analyze:
    - Scan all brain regions
    - Calculate usage metrics (last_used, frequency, confidence)
    - Identify flush candidates
    - Generate flush report (preview)
    
  step_2_categorize:
    candidates:
      - safe_to_delete: Low value, no dependencies
      - archive_first: Medium value, historical interest
      - merge_duplicates: Similar patterns consolidate
      - keep: High value, protect from flush
      
  step_3_confirm:
    - Show flush report to user
    - Require confirmation (type 'FLUSH')
    - Support dry-run mode (-DryRun)
    
  step_4_execute:
    - Create backup (brain/backups/pre-flush-{timestamp}/)
    - Archive patterns to brain/archived/
    - Delete safe items
    - Merge duplicates
    - Update indices
    
  step_5_verify:
    - Check brain integrity
    - Verify no broken references
    - Update capacity metrics
    - Generate completion report
```

### Flush Metrics (Track Health)

```yaml
flush_metrics:
  last_flush: "2025-11-04T14:30:22Z"
  
  cleanup_stats:
    patterns_deleted: 12
    patterns_archived: 8
    patterns_merged: 4
    space_reclaimed: "34 KB"
    
  before_flush:
    total_patterns: 127
    total_size: "156 KB"
    unused_patterns: 20
    low_confidence: 6
    
  after_flush:
    total_patterns: 103
    total_size: "122 KB"
    unused_patterns: 0
    low_confidence: 0
    
  health_score:
    before: 7.2/10 (cluttered)
    after: 9.4/10 (optimized)
```

### Flush Commands

**User Interface:**
```markdown
# Manual flush (with preview)
#file:KDS/prompts/user/kds.md flush brain

# Automatic flush (weekly)
# Runs every Sunday 2am via task scheduler

# Dry-run (preview only)
.\KDS\scripts\brain-flush.ps1 -DryRun

# Force flush (skip confirmation)
.\KDS\scripts\brain-flush.ps1 -Force

# Selective flush (specific tier)
.\KDS\scripts\brain-flush.ps1 -Tier 2  # Long-term patterns only
```

**Intent Detection:**
```yaml
flush_patterns:
  - "flush brain"
  - "clean up brain"
  - "remove unused patterns"
  - "brain cleanup"
  - "optimize brain"
  - "sharpen the brain" (runs flush + sharpener)
```

### Flush Safety Mechanisms

1. **✅ Automatic Backup** - Always create pre-flush backup
2. **✅ Dry-Run Mode** - Preview without changes
3. **✅ Confirmation Required** - Type 'FLUSH' to proceed
4. **✅ Rollback Capability** - Restore from backup if needed
5. **✅ Protected Patterns** - KDS governance never deleted
6. **✅ Dependency Check** - Don't delete if referenced elsewhere

---

## Part 3: Extensible Brain Sharpener

### Current State (Static Tests)

`BRAIN-SHARPENER.md` has 64 hardcoded scenarios:
- ❌ Can't easily add new scenarios
- ❌ No automation (manual validation)
- ❌ No plugin system
- ❌ Results not tracked over time

### Proposed Architecture (Plugin-Based)

```
KDS/
├── brain/
│   └── sharpener/                  # NEW: Brain testing framework
│       ├── core/
│       │   ├── test-runner.ps1         # Orchestration engine
│       │   ├── scenario-loader.ps1     # Plugin discovery
│       │   └── results-aggregator.ps1  # Report generation
│       │
│       ├── scenarios/              # Plugin folder (extensible)
│       │   ├── tier-0-instinct/
│       │   │   ├── intent-detection.yaml
│       │   │   ├── routing-accuracy.yaml
│       │   │   └── solid-compliance.yaml
│       │   │
│       │   ├── tier-1-working-memory/
│       │   │   ├── conversation-continuity.yaml
│       │   │   ├── reference-resolution.yaml
│       │   │   └── fifo-queue.yaml
│       │   │
│       │   ├── tier-2-long-term/
│       │   │   ├── error-prevention.yaml
│       │   │   ├── workflow-templates.yaml
│       │   │   └── file-relationships.yaml
│       │   │
│       │   ├── tier-3-context/
│       │   │   ├── file-hotspots.yaml
│       │   │   ├── velocity-estimates.yaml
│       │   │   └── productivity-patterns.yaml
│       │   │
│       │   ├── tier-4-imagination/
│       │   │   ├── question-deduplication.yaml
│       │   │   └── idea-evolution.yaml
│       │   │
│       │   └── cross-tier/
│       │       ├── whole-brain-processing.yaml
│       │       └── learning-feedback-loop.yaml
│       │
│       ├── results/                # Historical test runs
│       │   ├── 2025-11-04-143022.yaml
│       │   └── latest.yaml
│       │
│       └── config/
│           ├── benchmarks.yaml         # Performance targets
│           └── health-thresholds.yaml  # Green/yellow/red
```

### Scenario Plugin Format (YAML)

```yaml
# scenarios/tier-1-working-memory/conversation-continuity.yaml

scenario:
  id: "tier1-conversation-continuity"
  name: "Conversation Continuity - Same Session Pronouns"
  tier: 1
  category: "working-memory"
  priority: "high"
  
test_case:
  setup:
    - action: "Start new conversation"
    - action: "User says: 'I want to add a share button'"
    - action: "KDS creates plan"
    
  input: "Make it golden"
  
  expected_output:
    intent: "EXECUTE"
    context_resolved: true
    referent: "share button"
    confidence: ">0.85"
    
  failure_conditions:
    - "Asks 'What should be golden?'"
    - "Routes to PLAN instead of EXECUTE"
    - "Context resolution fails"
    
  validation:
    type: "automated"
    method: "query_conversation_context"
    success_criteria:
      - "Pronoun 'it' resolves to 'share button'"
      - "Intent correctly identified as EXECUTE"
      - "Context confidence >0.85"
      
benchmark:
  target: "98% same-conversation reference resolution"
  acceptable: ">95%"
  failing: "<90%"
  
metadata:
  author: "KDS Team"
  created: "2025-11-04"
  last_updated: "2025-11-04"
  execution_time: "~5 seconds"
```

### Test Runner Architecture

```powershell
# KDS/brain/sharpener/core/test-runner.ps1

param(
    [string]$Tier,              # Run specific tier only (0-4)
    [string]$Category,          # Run specific category
    [switch]$Quick,             # Run critical scenarios only (5 min)
    [switch]$Full,              # Run all scenarios (20-30 min)
    [switch]$Automated,         # Headless execution
    [switch]$Interactive,       # Show each test, wait for user
    [string[]]$Scenarios,       # Run specific scenarios by ID
    [switch]$ContinueOnFail     # Don't stop on first failure
)

# Execution flow:
# 1. Discover all scenario files (*.yaml in scenarios/)
# 2. Filter by tier/category/priority
# 3. Load scenarios into memory
# 4. For each scenario:
#    a. Run setup steps
#    b. Execute test input
#    c. Validate output against expectations
#    d. Record result (pass/fail/skip)
#    e. Capture metrics (execution time, confidence)
# 5. Aggregate results
# 6. Generate visual report
# 7. Update health metrics
# 8. Save to results/

# Output: YAML report + console visualization
```

### "Sharpen the Brain" Command

```yaml
sharpen_brain_workflow:
  command: "#file:KDS/prompts/user/kds.md sharpen the brain"
  
  step_1_flush:
    - Run brain flush (cleanup unused data)
    - Free up capacity
    - Remove low-confidence patterns
    
  step_2_test:
    - Run Brain Sharpener (full test suite)
    - Validate all tiers functioning
    - Check learning effectiveness
    
  step_3_align:
    - Compare results to BRAIN-SHARPENER.md benchmarks
    - Identify regressions
    - Flag underperforming areas
    
  step_4_optimize:
    - Merge duplicate patterns (if detected)
    - Consolidate similar workflows
    - Retrain low-confidence patterns
    
  step_5_report:
    - Generate comprehensive health report
    - Show before/after metrics
    - Provide actionable recommendations
    
  expected_duration: "25-30 minutes (full run)"
  quick_mode: "5 minutes (critical tests only)"
```

### Extensibility Design

**Adding New Scenarios (No Code Changes):**

1. Create new YAML file in `scenarios/{tier}/`
2. Follow scenario plugin format
3. Run test runner - auto-discovered
4. Results included in reports

**Example: Adding PR Review Quality Test**
```yaml
# scenarios/tier-3-context/pr-review-quality.yaml

scenario:
  id: "tier3-pr-review-quality"
  name: "PR Intelligence - Review Quality Patterns"
  tier: 3
  category: "context-awareness"
  priority: "medium"
  
test_case:
  setup:
    - action: "Load PR intelligence data"
    - action: "Find high-rework files"
    
  input: "Planning to modify HostControlPanelContent.razor"
  
  expected_output:
    warning_shown: true
    warning_type: "high_rework_file"
    recommendation: "Extra testing recommended"
    confidence: ">0.80"
    
  validation:
    type: "automated"
    method: "query_pr_patterns"
    success_criteria:
      - "Detects file in high-rework list"
      - "Provides actionable recommendation"
      
benchmark:
  target: "85% proactive warnings on high-risk files"
```

**Benefits:**
- ✅ No code changes to add tests
- ✅ Team can contribute scenarios easily
- ✅ Scenarios version-controlled (git)
- ✅ Portable across projects
- ✅ Results tracked over time

---

## Part 4: Dashboard Integration

### Current State

`kds-dashboard.html` has:
- ✅ Health checks (7 categories)
- ✅ BRAIN metrics
- ✅ Activity log
- ❌ No Brain Sharpener integration
- ❌ No flush visualization
- ❌ No learning trends

### Proposed Enhancements

#### New Tab: Brain Sharpener

```html
<!-- Dashboard Tab -->
<div id="brain-sharpener-tab">
  <!-- Test Execution -->
  <section class="test-execution">
    <h3>🎯 Run Brain Sharpener Tests</h3>
    
    <div class="test-controls">
      <button onclick="runTests('quick')">Quick Test (5 min)</button>
      <button onclick="runTests('full')">Full Test (30 min)</button>
      <button onclick="runTests('tier', 1)">Test Tier 1 Only</button>
    </div>
    
    <div class="progress-bar" id="test-progress">
      <div class="progress-fill"></div>
      <span class="progress-text">0/64 tests complete</span>
    </div>
  </section>
  
  <!-- Live Results -->
  <section class="test-results">
    <h3>📊 Test Results</h3>
    
    <div class="tier-results">
      <div class="tier tier-0">
        <h4>Tier 0: Instinct</h4>
        <div class="tier-score">100% (6/6)</div>
        <div class="tier-status green">✅ PASSING</div>
      </div>
      
      <div class="tier tier-1">
        <h4>Tier 1: Working Memory</h4>
        <div class="tier-score">95% (19/20)</div>
        <div class="tier-status green">✅ PASSING</div>
        <button onclick="expandTier(1)">View Details</button>
      </div>
      
      <!-- Expandable details -->
      <div class="tier-details" id="tier-1-details" style="display:none">
        <div class="test-case pass">
          ✅ Conversation Continuity - Same Session
        </div>
        <div class="test-case fail">
          ❌ Cross-Conversation Pronoun Resolution
          <div class="failure-reason">
            Expected: Resolve "it" to FAB button from conversation #3
            Actual: Asked "What should be golden?"
          </div>
        </div>
      </div>
    </div>
  </section>
  
  <!-- Health Scoring -->
  <section class="health-score">
    <h3>🧠 Overall Brain Health</h3>
    
    <div class="health-gauge">
      <div class="gauge-fill" style="width: 92%"></div>
      <span class="gauge-score">92/100</span>
    </div>
    
    <div class="health-status green">
      🟢 GREEN - System Healthy
    </div>
    
    <div class="health-breakdown">
      <div>Routing Accuracy: 96% ✅</div>
      <div>Learning Efficiency: 92% ✅</div>
      <div>Storage Efficiency: 94% ✅</div>
      <div>Response Time: 250ms ✅</div>
    </div>
  </section>
  
  <!-- Historical Trends -->
  <section class="trends">
    <h3>📈 Learning Trends (Last 30 Days)</h3>
    
    <div class="chart">
      <!-- Simple ASCII bar chart -->
      <div class="chart-row">
        <span class="chart-label">Week 1</span>
        <div class="chart-bar" style="width: 75%">75%</div>
      </div>
      <div class="chart-row">
        <span class="chart-label">Week 2</span>
        <div class="chart-bar" style="width: 82%">82%</div>
      </div>
      <div class="chart-row">
        <span class="chart-label">Week 3</span>
        <div class="chart-bar" style="width: 88%">88%</div>
      </div>
      <div class="chart-row">
        <span class="chart-label">Week 4</span>
        <div class="chart-bar" style="width: 92%">92%</div>
      </div>
    </div>
    
    <div class="trend-summary">
      ⬆️ +17% improvement over 30 days (excellent)
    </div>
  </section>
</div>
```

#### New Tab: Brain Flush

```html
<div id="brain-flush-tab">
  <section class="flush-controls">
    <h3>🧹 Brain Flush</h3>
    
    <button onclick="analyzeFlush()">Analyze (Preview)</button>
    <button onclick="executeFlushdry)">Dry Run</button>
    <button onclick="executeFlush()">Execute Flush</button>
  </section>
  
  <section class="flush-report">
    <h3>📊 Flush Analysis</h3>
    
    <div class="flush-candidates">
      <h4>Candidates for Cleanup</h4>
      
      <div class="candidate">
        <span class="candidate-type">Unused Patterns</span>
        <span class="candidate-count">12</span>
        <span class="candidate-size">14 KB</span>
        <button onclick="viewDetails('unused')">Details</button>
      </div>
      
      <div class="candidate">
        <span class="candidate-type">Low Confidence</span>
        <span class="candidate-count">6</span>
        <span class="candidate-size">4 KB</span>
      </div>
      
      <div class="candidate">
        <span class="candidate-type">Duplicates</span>
        <span class="candidate-count">4</span>
        <span class="candidate-size">8 KB</span>
      </div>
    </div>
    
    <div class="flush-impact">
      <h4>Estimated Impact</h4>
      <div>Space Reclaimed: 26 KB</div>
      <div>Patterns Removed: 18</div>
      <div>Health Score: 7.2 → 9.1 (+1.9)</div>
    </div>
  </section>
</div>
```

#### API Endpoints (New)

```powershell
# KDS/scripts/dashboard-api-server.ps1 (enhance existing)

# Add new endpoints:

# GET /api/brain/sharpener/scenarios
# Returns: List of all test scenarios

# POST /api/brain/sharpener/run
# Body: { "mode": "quick" | "full", "tier": 0-4 }
# Returns: Test execution stream (SSE)

# GET /api/brain/sharpener/results/latest
# Returns: Most recent test results

# GET /api/brain/flush/analyze
# Returns: Flush candidates and impact

# POST /api/brain/flush/execute
# Body: { "dryRun": true | false }
# Returns: Flush results

# GET /api/brain/trends
# Returns: 30-day learning trends
```

### Real-Time Updates (Server-Sent Events)

```javascript
// dashboard.js (add to existing)

function runTests(mode) {
  const eventSource = new EventSource(`/api/brain/sharpener/run?mode=${mode}`);
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'progress') {
      updateProgressBar(data.current, data.total);
    }
    
    if (data.type === 'test_result') {
      updateTestResult(data.tier, data.scenario, data.result);
    }
    
    if (data.type === 'complete') {
      showFinalReport(data.summary);
      eventSource.close();
    }
  };
}

function updateProgressBar(current, total) {
  const percent = (current / total) * 100;
  document.querySelector('.progress-fill').style.width = `${percent}%`;
  document.querySelector('.progress-text').textContent = `${current}/${total} tests complete`;
}
```

---

## Part 5: PowerShell vs Alternatives Analysis

### Current State: PowerShell 7+

**Pros:**
- ✅ Native Windows integration
- ✅ Excellent file system operations
- ✅ Built-in JSON/XML/YAML parsing
- ✅ Git integration works well
- ✅ Zero external dependencies
- ✅ Simple HTTP server (possible with `Pode` module)
- ✅ Task scheduling native (Windows Task Scheduler)

**Cons:**
- ❌ Cross-platform compatibility (works on Linux/Mac but not default)
- ❌ Slower than compiled languages
- ❌ Limited ecosystem vs Python/Node
- ❌ Verbose syntax for some operations
- ❌ Less community support for AI/ML integrations

### Alternative 1: Python

**Pros:**
- ✅ **Huge AI/ML ecosystem** (transformers, spaCy, sentence-transformers)
- ✅ **Excellent data processing** (pandas, numpy)
- ✅ **Cross-platform** (default on Mac/Linux)
- ✅ **Rich testing frameworks** (pytest, unittest)
- ✅ **YAML parsing** (PyYAML native)
- ✅ **HTTP servers** (Flask, FastAPI)
- ✅ **Semantic search** (sentence-transformers for similarity)

**Cons:**
- ❌ Requires Python installation
- ❌ Dependency management (pip, virtualenv)
- ❌ Slower startup than PowerShell for small scripts
- ❌ Not native on Windows

**Use Cases:**
- Brain Sharpener test runner (rich assertions)
- Semantic similarity for idea linking (Tier 4)
- Data analysis for PR intelligence
- Advanced pattern matching

### Alternative 2: Node.js (JavaScript/TypeScript)

**Pros:**
- ✅ **Huge ecosystem** (npm - 2M+ packages)
- ✅ **Cross-platform** (runs everywhere)
- ✅ **Fast async I/O** (event loop)
- ✅ **Modern web tooling** (dashboard API server)
- ✅ **JSON native** (no parsing needed)
- ✅ **Testing mature** (Jest, Mocha, Vitest)
- ✅ **TypeScript** (type safety)

**Cons:**
- ❌ Requires Node.js installation
- ❌ `node_modules` bloat
- ❌ Callback hell (mitigated by async/await)
- ❌ Less ideal for system operations

**Use Cases:**
- Dashboard API server (already considering)
- Real-time updates (Server-Sent Events)
- Plugin system (dynamic module loading)

### Alternative 3: Pure PowerShell (Recommended) ✅

**REVISED AFTER FOOTPRINT ANALYSIS**

**Strategy:** Keep KDS lean, portable, and zero-dependency

| Task | Tool | Rationale |
|------|------|-----------|
| **File operations** | PowerShell | Native, fast, simple |
| **Git operations** | PowerShell | Already working well |
| **Brain flush** | PowerShell | File-based, no ML needed |
| **Dashboard API** | PowerShell | `System.Net.HttpListener` (built-in) |
| **Brain Sharpener runner** | PowerShell + Pester | Excellent testing framework |
| **Pattern analysis** | PowerShell | String operations excel at this |
| **Semantic similarity** | PowerShell | Levenshtein distance (native) |
| **Housekeeping services** | PowerShell | Background jobs, task scheduler |

**Footprint Comparison:**
```
Hybrid Approach:  PowerShell + Python + Node.js = ~650 MB
Pure PowerShell:  PowerShell only             = ~2-5 MB  (130x smaller!)
```

### Recommendation: **Pure PowerShell** ✅

**Pure PowerShell Implementation (All Features)**

✅ **Core Operations** (Already Working)
- File operations (file-operations.ps1)
- Session management (session-storage/)
- Brain flush (brain-flush.ps1)
- Event logging (log-event.ps1)

✅ **Brain Sharpener** (PowerShell + Pester)
- Test runner using Pester framework
- YAML scenario loading (built-in ConvertFrom-Yaml)
- Assertion library (Pester's Should syntax)
- Mocking support (Pester's Mock)

✅ **Dashboard API** (PowerShell HTTP)
- Simple HTTP listener using `System.Net.HttpListener`
- JSON responses (ConvertTo-Json)
- Server-Sent Events (text/event-stream)
- Zero external dependencies

✅ **Semantic Similarity** (PowerShell Native)
```powershell
# Levenshtein distance for pattern matching
function Get-StringSimilarity {
    param([string]$Text1, [string]$Text2)
    
    # Calculate edit distance
    $distance = Get-LevenshteinDistance $Text1 $Text2
    $maxLength = [Math]::Max($Text1.Length, $Text2.Length)
    
    # Return similarity score (0.0 to 1.0)
    return 1.0 - ($distance / $maxLength)
}
```

✅ **Housekeeping Services** (PowerShell Jobs)
- Background services using Start-Job
- Windows Task Scheduler integration
- Automatic cleanup, organization, optimization
- All native PowerShell (no dependencies)

### Zero Dependencies ✅

**PowerShell 7+ Only** (Already Installed)

```powershell
# Verify PowerShell version
function Test-KDSPrerequisites {
    $psVersion = $PSVersionTable.PSVersion
    
    if ($psVersion.Major -lt 7) {
        Write-Warning "KDS requires PowerShell 7+. Current: $psVersion"
        Write-Host "Install from: https://aka.ms/powershell"
        return $false
    }
    
    Write-Host "✅ PowerShell $psVersion - Ready" -ForegroundColor Green
    return $true
}
```

**Built-In Modules Used:**
- `System.Net.HttpListener` - Dashboard API (built-in)
- `ConvertFrom-Yaml` / `ConvertTo-Yaml` - YAML parsing (PowerShell 7+)
- `ConvertFrom-Json` / `ConvertTo-Json` - JSON parsing (built-in)
- `Pester` - Testing framework (install once: `Install-Module Pester`)
- `Start-Job` - Background services (built-in)

**Total External Dependencies: 1** (Pester - PowerShell's standard testing framework)

**Installation:**
```powershell
# One-time Pester installation (if missing)
if (-not (Get-Module -ListAvailable -Name Pester)) {
    Install-Module -Name Pester -Force -SkipPublisherCheck
}
```

### Final Recommendation ✅

**Pure PowerShell - Zero Dependencies**

**Why This is Better:**

1. **Portability** (10/10)
   - Works anywhere PowerShell 7+ runs (Windows/Linux/Mac)
   - Copy KDS folder → Instant setup
   - No `pip install`, no `npm install`

2. **Footprint** (10/10)
   - Total size: ~5 MB (vs ~650 MB hybrid)
   - 130x smaller than hybrid approach
   - Blazing fast operations

3. **Maintenance** (10/10)
   - One language to maintain
   - No version conflicts (Python 3.8 vs 3.12?)
   - No `node_modules` hell

4. **Capabilities** (9/10)
   - Everything we need:
     - ✅ YAML parsing (PowerShell 7+)
     - ✅ HTTP server (`System.Net.HttpListener`)
     - ✅ Testing (Pester framework)
     - ✅ String similarity (Levenshtein)
     - ✅ Background jobs (Start-Job)
     - ✅ Task scheduling (Windows/Linux/Mac)
   - What we lose:
     - ❌ Deep learning models (don't need them)
     - ❌ Advanced ML (not required for pattern matching)

5. **Performance** (9/10)
   - PowerShell is fast for file operations
   - Compiled .NET underneath
   - Sufficient for KDS workload

**Decision: 100% PowerShell** ✅

**Benefits:**
- ✅ Zero setup friction (works out of box)
- ✅ Minimal footprint (fits on flash drive)
- ✅ Maximum portability (cross-platform)
- ✅ Single language (simpler maintenance)
- ✅ No breaking changes (already PowerShell)

---

## Part 6: PR Intelligence Preservation

### Current State (collect-pr-intelligence.ps1)

**Features to Preserve:**
- ✅ High-rework files detection (avg >2 commits/PR)
- ✅ Collaboration hotspots (co-modified in >60% PRs)
- ✅ Quality indicators (small vs large PR success rates)
- ✅ PR size metrics (avg files, lines, commits)
- ✅ Review iteration tracking
- ✅ Category breakdown (UI, Backend, Tests, etc.)

### Integration into New Brain Structure

#### 1. Move to Tier 3: Context Awareness
```
brain/
└── context-awareness/
    ├── pr-intelligence.yaml         # MAIN FILE (NEW)
    ├── pr-metrics.yaml              # Aggregated stats
    └── pr-patterns/                 # Historical patterns
        ├── high-rework-files.yaml
        ├── collaboration-hotspots.yaml
        └── quality-indicators.yaml
```

#### 2. Enhance PR Intelligence with Trends

**Current:** Single snapshot (30 days)  
**Enhanced:** Trend analysis over time

```yaml
# brain/context-awareness/pr-intelligence.yaml

pr_intelligence:
  last_collection: "2025-11-04T14:30:00Z"
  lookback_days: 30
  
  high_rework_files:
    - file: "HostControlPanelContent.razor"
      avg_review_iterations: 3.2
      total_prs: 8
      rework_rate: 0.75
      trend: "increasing"         # NEW: Track if getting worse
      confidence: 0.92
      
  collaboration_hotspots:
    - files:
        - "HostControlPanelSidebar.razor"
        - "noor-canvas.css"
      co_modification_rate: 0.75
      total_prs: 6
      trend: "stable"             # NEW: Track pattern stability
      confidence: 0.88
      
  quality_indicators:
    - pattern: "small_pr_size"
      total_prs: 12
      avg_review_iterations: 1.4
      success_rate: 0.92         # NEW: Track success explicitly
      trend: "improving"         # NEW: Month-over-month
      confidence: 0.95
      
  trends:                         # NEW SECTION
    month_over_month:
      avg_pr_size: -12%           # Smaller PRs (good)
      review_iterations: -8%      # Fewer iterations (good)
      rework_rate: -15%           # Less rework (good)
      collaboration_rate: +5%     # More co-modification (neutral)
```

#### 3. Integrate with Brain Sharpener

**Add PR Intelligence Test Scenarios:**
```yaml
# brain/sharpener/scenarios/tier-3-context/pr-review-warnings.yaml

scenario:
  id: "tier3-pr-review-warnings"
  name: "PR Intelligence - Proactive Review Warnings"
  tier: 3
  
test_case:
  input: "Planning to modify HostControlPanelContent.razor"
  
  expected_output:
    warning_type: "high_rework_file"
    avg_iterations: 3.2
    recommendation: "⚠️ Extra scrutiny needed - frequently requires rework"
    suggested_actions:
      - "Add extra test coverage"
      - "Consider smaller commits"
      - "Pair programming recommended"
      
benchmark:
  target: "100% warnings on known high-rework files"
```

#### 4. Dashboard Visualization

**Add PR Intelligence Tab:**
```html
<div id="pr-intelligence-tab">
  <section class="high-rework-files">
    <h3>⚠️ High-Rework Files</h3>
    
    <div class="file-list">
      <div class="file-item warn">
        <span class="file-name">HostControlPanelContent.razor</span>
        <span class="rework-rate">75% rework rate</span>
        <span class="trend">📈 Increasing</span>
      </div>
    </div>
  </section>
  
  <section class="pr-quality-trends">
    <h3>📊 PR Quality Trends</h3>
    
    <div class="metric">
      <span>Avg PR Size:</span>
      <span class="value">287 lines</span>
      <span class="trend good">-12% ⬇️</span>
    </div>
    
    <div class="metric">
      <span>Review Iterations:</span>
      <span class="value">1.4 avg</span>
      <span class="trend good">-8% ⬇️</span>
    </div>
  </section>
</div>
```

---

## Part 7: Implementation Roadmap

### Phase 0: Preparation (Week 1)
**Goal:** Non-breaking setup

- [x] Create `KDS/docs/KDS-V6-HOLISTIC-PLAN.md` (this document)
- [ ] Review and approve plan with stakeholders
- [ ] Create `brain/` folder structure (empty, dual-write)
- [ ] Update `.gitignore` for new folders
- [ ] Backup current `kds-brain/` state

**Deliverables:**
- ✅ Comprehensive plan document
- ✅ Brain folder structure created
- ✅ Backup completed

---

### Phase 1: Brain Reorganization (Week 2-3)
**Goal:** Migrate to brain-inspired structure

#### Task 1.1: Create Instinct Layer (Tier 0)
- [ ] Create `brain/instinct/` folder
- [ ] Extract core rules from `governance/rules.md`
- [ ] Extract SOLID principles from `KDS-DESIGN.md`
- [ ] Extract routing logic from `intent-router.md`
- [ ] Extract protection config from `knowledge-graph.yaml`
- [ ] Create `core-rules.yaml`, `solid-principles.yaml`, etc.

#### Task 1.2: Migrate Working Memory (Tier 1)
- [ ] Create `brain/working-memory/recent-conversations/`
- [ ] Split `conversation-history.jsonl` into individual files
- [ ] Create `conversation-index.yaml` for fast lookup
- [ ] Update `conversation-context-manager.md` to use new structure
- [ ] Verify FIFO queue still works

#### Task 1.3: Split Long-Term Memory (Tier 2)
- [ ] Create specialized files in `brain/long-term/`
- [ ] Split `knowledge-graph.yaml`:
  - `intent-patterns.yaml`
  - `file-relationships.yaml`
  - `workflow-templates.yaml`
  - `error-patterns.yaml`
  - `test-patterns.yaml`
- [ ] Update `brain-query.md` to search new files
- [ ] Verify all patterns preserved

#### Task 1.4: Reorganize Context Awareness (Tier 3)
- [ ] Create `brain/context-awareness/` folder
- [ ] Split `development-context.yaml` into:
  - `git-metrics.yaml`
  - `velocity-tracking.yaml`
  - `file-hotspots.yaml`
  - `pr-intelligence.yaml` (NEW)
  - `productivity-patterns.yaml`
- [ ] Integrate `collect-pr-intelligence.ps1` outputs
- [ ] Update `development-context-collector.md`

#### Task 1.5: Create Imagination Layer (Tier 4)
- [ ] Create `brain/imagination/` folder
- [ ] Create `questions-answered.yaml` (migrate from knowledge-retriever)
- [ ] Create `ideas-stashed.yaml` (NEW feature)
- [ ] Create `semantic-links.yaml` (for idea relationships)
- [ ] Update `knowledge-retriever.md` to use new structure

#### Task 1.6: Update All Agents
- [ ] Update `brain-query.md` with new paths
- [ ] Update `brain-updater.md` to write to new structure
- [ ] Update all agents using BRAIN queries
- [ ] Update `file-accessor.md` for new categories
- [ ] Test all agents still work

**Deliverables:**
- ✅ Brain folder structure populated
- ✅ All data migrated
- ✅ Agents updated
- ✅ Tests pass

---

### Phase 2: Housekeeping Layer (Tier 5) (Week 4)
**Goal:** Automatic background maintenance

#### Task 2.1: Create Housekeeping Infrastructure
- [ ] Create `brain/housekeeping/` folder structure
- [ ] Create service skeleton scripts (6 services)
- [ ] Create schedule templates (daily/weekly/monthly)
- [ ] Create config files (service-config.yaml, thresholds.yaml)

#### Task 2.2: Implement Core Services

**Cleanup Service:**
- [ ] Scan for unused patterns (>90 days)
- [ ] Detect low confidence patterns (<0.60)
- [ ] Identify duplicates (>85% similarity)
- [ ] Archive vs delete logic
- [ ] Dry-run mode

**Organizer Service:**
- [ ] Consolidate file relationships
- [ ] Group similar workflows
- [ ] Rebuild indices
- [ ] Sort by success rate

**Optimizer Service:**
- [ ] Defragment YAML files (rewrite in optimal order)
- [ ] Compress event stream (aggregate to summaries)
- [ ] Update confidence scores based on usage
- [ ] Merge duplicate patterns

**Validator Service:**
- [ ] Check file references (broken paths)
- [ ] Validate YAML syntax
- [ ] Verify FIFO queue (exactly 20 conversations)
- [ ] Check tier capacities

**Indexer Service:**
- [ ] Rebuild conversation-index.yaml
- [ ] Rebuild event-index.yaml
- [ ] Update search indices

**Archiver Service:**
- [ ] Archive old patterns to `.archived/`
- [ ] Compress old event logs
- [ ] Maintain retention policies

#### Task 2.3: Create Master Orchestrator
- [ ] Implement `orchestrator.ps1`
- [ ] Load schedules from YAML
- [ ] Execute services based on schedule
- [ ] Handle service dependencies
- [ ] Log all activities
- [ ] Error handling and recovery

#### Task 2.4: Integrate with Task Scheduler
- [ ] Create Windows Task Scheduler tasks
- [ ] Daily: cleanup, validator (2am)
- [ ] Weekly: organizer (Sunday)
- [ ] Monthly: optimizer, archiver (1st of month)
- [ ] Test scheduled execution

#### Task 2.5: Event-Based Triggers
- [ ] Monitor brain size → trigger cleanup
- [ ] Monitor pattern count → trigger organizer
- [ ] Monitor query speed → trigger optimizer
- [ ] Monitor errors → trigger validator

**Deliverables:**
- ✅ 6 housekeeping services working
- ✅ Automatic scheduling configured
- ✅ Event-based triggers active
- ✅ Logs tracking all activities

---

### Phase 3: Brain Flush Enhancement (Week 5)
**Goal:** Integrate flush into housekeeping

#### Task 3.1: Enhance Cleanup Service (Brain Flush)
- [ ] Move flush logic into `cleanup-service.ps1`
- [ ] Implement all tier-specific flush policies
- [ ] Add preview generation
- [ ] Add backup creation
- [ ] Add verification
- [ ] Integrate with orchestrator

#### Task 3.2: Create Flush Command
- [ ] Update `intent-router.md` with FLUSH intent
- [ ] Add flush patterns ("flush brain", "clean up brain")
- [ ] Create `prompts/user/flush.md` (user interface)
- [ ] Route to cleanup service (on-demand mode)

#### Task 3.3: Test Flush Scenarios
- [ ] Test unused pattern removal
- [ ] Test low-confidence cleanup
- [ ] Test duplicate merging
- [ ] Test FIFO queue management
- [ ] Test rollback capability

**Deliverables:**
- ✅ Flush integrated into housekeeping
- ✅ Manual flush command works
- ✅ Automatic flush via orchestrator
- ✅ All test scenarios pass

---

### Phase 4: Extensible Brain Sharpener (Week 6-7)
**Goal:** Plugin-based test framework

#### Task 4.1: Create Sharpener Infrastructure
- [ ] Create `brain/sharpener/` folder structure
- [ ] Create `core/test-runner.ps1` (orchestration)
- [ ] Create `core/scenario-loader.ps1` (plugin discovery)
- [ ] Create `core/results-aggregator.ps1` (reporting)
- [ ] Create `config/benchmarks.yaml`

#### Task 4.2: Convert Static Tests to Plugins
- [ ] Migrate Tier 0 tests from `BRAIN-SHARPENER.md` to YAML
- [ ] Migrate Tier 1 tests to YAML
- [ ] Migrate Tier 2 tests to YAML
- [ ] Migrate Tier 3 tests to YAML
- [ ] Migrate Tier 4 tests to YAML
- [ ] Migrate cross-tier tests to YAML
- [ ] Total: 64 scenario files created

#### Task 4.3: Implement Test Runner (Pester Framework)
- [ ] Scenario discovery (scan `scenarios/` folder)
- [ ] Scenario loading (parse YAML)
- [ ] Test execution engine
- [ ] Result validation
- [ ] Report generation
- [ ] Historical tracking (save to `results/`)

#### Task 4.4: Create "Sharpen the Brain" Workflow
- [ ] Update `intent-router.md` with SHARPEN intent
- [ ] Add sharpen patterns ("sharpen the brain")
- [ ] Create integrated workflow:
  1. Run flush
  2. Run tests
  3. Align with benchmarks
  4. Optimize patterns
  5. Generate report
- [ ] Test end-to-end

**Deliverables:**
- ✅ 64 scenario plugins created
- ✅ Test runner working
- ✅ Results tracked over time
- ✅ "Sharpen the brain" command works

---

### Phase 5: Dashboard Integration (Week 8)
**Goal:** Visual brain health monitoring

#### Task 5.1: Add Brain Sharpener Tab
- [ ] Design UI (HTML/CSS)
- [ ] Add test execution controls
- [ ] Add live progress bar
- [ ] Add tier-by-tier results
- [ ] Add expandable details
- [ ] Add health scoring visualization

#### Task 5.2: Add Housekeeping Tab
- [ ] Design UI
- [ ] Add flush analysis preview
- [ ] Add candidate visualization
- [ ] Add impact estimation
- [ ] Add execution controls

#### Task 5.3: Add Trends Visualization
- [ ] Extract 30-day learning data
- [ ] Create simple bar charts (ASCII or Canvas)
- [ ] Show month-over-month improvements
- [ ] Add trend indicators (⬆️⬇️)

#### Task 5.4: Enhance API Server (Pure PowerShell)
- [ ] Add `/api/brain/sharpener/*` endpoints
- [ ] Add `/api/brain/flush/*` endpoints
- [ ] Add `/api/brain/trends` endpoint
- [ ] Implement Server-Sent Events for live updates
- [ ] Test API thoroughly

#### Task 5.5: Real-Time Updates (Server-Sent Events)
- [ ] Implement SSE in test runner
- [ ] Update dashboard.js with EventSource
- [ ] Add progress animations
- [ ] Test real-time updates

**Deliverables:**
- ✅ Dashboard has Sharpener tab
- ✅ Dashboard has Flush tab
- ✅ Dashboard has Trends tab
- ✅ Real-time updates working
- ✅ API server enhanced

---

### Phase 6: Documentation & Testing (Week 9)
**Goal:** Complete system documentation

#### Task 6.1: Update User Documentation
- [ ] Update `kds.md` with new commands:
  - `flush brain`
  - `sharpen the brain`
  - `stash idea: [idea]`
- [ ] Update `KDS-DESIGN.md` with v6.0 decisions
- [ ] Update `BRAIN-SHARPENER.md` (reference plugin system)
- [ ] Create `brain/README.md` (structure guide)

#### Task 6.2: Update Agent Documentation
- [ ] Update all affected agents with new paths
- [ ] Document brain region responsibilities
- [ ] Update `brain-query.md` examples
- [ ] Update `brain-updater.md` examples

#### Task 6.3: End-to-End Testing
- [ ] Test full "sharpen the brain" workflow
- [ ] Test flush mechanism (dry-run + real)
- [ ] Test all 64 scenarios pass
- [ ] Test dashboard features
- [ ] Test backward compatibility

#### Task 6.4: Create Migration Guide
- [ ] Document v5→v6 migration steps
- [ ] Explain folder structure changes
- [ ] Provide rollback instructions
- [ ] Create troubleshooting guide

**Deliverables:**
- ✅ All documentation updated
- ✅ Migration guide created
- ✅ System tested end-to-end
- ✅ v6.0 ready for use

---

## Success Metrics

### Completion Criteria

| Metric | Target | Status |
|--------|--------|--------|
| **Brain Structure** | 6 tiers organized (added Housekeeping) | ⏳ Pending |
| **Housekeeping Services** | 6 automatic background services | ⏳ Pending |
| **Test Scenarios** | 64+ plugins | ⏳ Pending |
| **Dashboard Tabs** | 3 new (Sharpener, Flush, Trends) | ⏳ Pending |
| **PowerShell Decision** | Pure PowerShell (zero dependencies) | ✅ Complete (this doc) |
| **PR Intelligence** | Integrated into Tier 3 | ⏳ Pending |
| **Documentation** | 100% updated | ⏳ Pending |
| **Backward Compat** | v5 sessions work in v6 | ⏳ Pending |

### Quality Gates

**Before v6.0 Release:**
- ✅ All 64 scenarios pass (>90%)
- ✅ Brain flush tested (dry-run + real)
- ✅ Dashboard visualizations working
- ✅ No breaking changes to agents
- ✅ Migration guide reviewed
- ✅ Performance acceptable (<1s overhead)

---

## Risk Assessment

### High Risk Items

1. **Data Migration** - Risk: Data loss during split
   - Mitigation: Backup before each phase, dual-write during transition

2. **Agent Breakage** - Risk: Agents fail with new paths
   - Mitigation: Use `file-accessor.md` abstraction, test each agent

3. **Performance** - Risk: Slower with split files
   - Mitigation: Profile before/after, optimize queries

### Medium Risk Items

4. **Python Dependency** - Risk: Users don't have Python
   - Mitigation: Graceful degradation, PowerShell fallback

5. **Test Coverage** - Risk: Missing edge cases in 64 scenarios
   - Mitigation: Add scenarios iteratively, community contributions

### Low Risk Items

6. **Dashboard Complexity** - Risk: Hard to maintain
   - Mitigation: Keep HTML simple, no heavy frameworks

7. **Documentation Drift** - Risk: Docs out of sync
   - Mitigation: Rule #16 enforces doc updates

---

## Next Steps

### Immediate (This Week)
1. ✅ Review this plan with stakeholders
2. ✅ Get approval on brain structure reorganization
3. ✅ Get approval on flush mechanism design
4. ✅ Get approval on hybrid PowerShell/Python approach

### Phase 0 (Next Week)
1. Create `brain/` folder structure
2. Set up dual-write (old + new locations)
3. Backup current state

### Tracking Progress
- Use GitHub project board (or similar)
- Weekly check-ins on phase completion
- Update `KDS-REVIEW-{date}.md` monthly

---

## Conclusion

This holistic plan transforms KDS v5.0 into a **true brain-inspired intelligent system** (v6.0):

✅ **Brain Structure** - Intuitive organization mimicking human cognition  
✅ **Flush Mechanism** - Self-cleaning, self-optimizing  
✅ **Extensible Sharpener** - Plugin-based testing framework  
✅ **Dashboard Integration** - Visual health monitoring  
✅ **Hybrid Tooling** - PowerShell core + Python intelligence  
✅ **PR Intelligence Preserved** - Enhanced with trends  
✅ **Backward Compatible** - v5 sessions work in v6  
✅ **Fully Documented** - Migration guide included

**Philosophy:** 
> "The brain isn't static storage—it's living, learning, optimizing, and continuously sharpening itself."

**Estimated Timeline:** 9 weeks (~2 months)  
**Effort:** ~90-110 hours total  
**Complexity:** Medium (well-architected foundation helps)

Ready to begin? 🚀

---

**Version:** 6.0.0-PLAN  
**Status:** 📋 READY FOR REVIEW  
**Next:** Phase 0 - Preparation

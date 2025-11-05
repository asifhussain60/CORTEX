# KDS V8.0 - Completion Roadmap

**Date:** November 5, 2025  
**Status:** 🔄 **IN PROGRESS** (Phase 0, 1, 3.5 Complete)  
**Theme:** Real-Time Intelligence & Autonomous Maintenance

---

## 🎯 Executive Summary

**What's Complete:**
- ✅ **Phase 0:** Enforcement Layer (Pre-commit validation, silent failure elimination)
- ✅ **Phase 1:** Live Data Dashboard (Real-time event stream, conversations, metrics, health)
- ✅ **Phase 3.5:** Git Commit Tracking (Commits associated with conversations)

**What's Remaining:**
- 🔄 **Phase 2:** Advanced Dashboard Features (Event filtering, charts, export)
- 📋 **Phase 3:** Cleanup Scripts (Automated brain maintenance)
- 📋 **Phase 4:** Windows Service (24/7 autonomous operations)
- 📋 **Phase 5:** Deployment Automation (One-click setup)
- 📋 **Phase 6:** Feature Reporting (Automated inventory validation)
- 📋 **Phase 7:** Polish & Release (Production-ready v8.0)

**Estimated Time to Complete:** 6-8 weeks

---

## ✅ Completed Phases (Detailed Status)

### Phase 0: Enforcement Layer ✅ (Complete - Nov 5, 2025)

**Objective:** Transform BRAIN from documentation to executable enforcement

**Delivered:**
- ✅ Pre-commit validation hook with 5 gates:
  1. TDD validation (no .cs without test)
  2. Build validation (zero errors, zero warnings)
  3. Test validation (all tests must pass)
  4. Silent failure detection (no Debug.WriteLine)
  5. Integration test validation (ViewModels tested)
- ✅ ErrorViewModel for visible error tracking
- ✅ JSON parsing standardized (PropertyNameCaseInsensitive, CamelCase)
- ✅ Validation script enhanced (excludes comments)
- ✅ 12 Debug.WriteLine calls eliminated → 0 silent failures
- ✅ Build: 0 errors, 2 allowed warnings (CS8625 nullable, xUnit2002)
- ✅ Tests: 78/78 passing (5 WPF UI skipped as expected)

**Documentation:** `dashboard-wpf/V8-PHASE-0-ENFORCEMENT-COMPLETE.md`

**Impact:** The BRAIN now enforces quality, not just documents it. Silent failures eliminated.

---

### Phase 1: Live Data Dashboard ✅ (Complete - Nov 5, 2025)

**Objective:** Replace dummy data with real-time brain file monitoring

**Delivered:**
- ✅ ActivityViewModel: FileSystemWatcher on events.jsonl (<500ms latency)
- ✅ ConversationsViewModel: FileSystemWatcher on conversation-history.jsonl (<400ms latency)
- ✅ MetricsViewModel: FileSystemWatcher on development-context.yaml (<450ms latency)
- ✅ HealthViewModel: 3 FileSystemWatchers (events, knowledge-graph, conversations) (<500ms latency)
- ✅ Dispatcher.Invoke for UI thread safety
- ✅ Proper Dispose() for cleanup
- ✅ All dummy data removed (DummyDataGenerator deleted)
- ✅ Tests: 83/83 passing (78 passed, 5 WPF STA skipped)

**Documentation:** `dashboard-wpf/V8-PHASE-1-LIVE-DATA-COMPLETE.md`

**Impact:** Real-time brain visibility. Dashboard updates <1 second after brain file changes.

---

### Phase 3.5: Git Commit Tracking ✅ (Complete - Nov 5, 2025)

**Objective:** Associate git commits with Tier 1 conversations for full traceability

**Delivered:**
- ✅ GitCommit data model (SHA, message, author, timestamp, files, stats)
- ✅ Conversation.AssociatedCommits property
- ✅ Enhanced post-commit hook (version 8.0, added Phase 2)
- ✅ `associate-commit-to-conversation.ps1` script (194 lines, fully documented)
- ✅ Dashboard visualization (commits shown in conversation details)
- ✅ Git icon with orange accent (#F05032 - official Git color)
- ✅ Event logging (git_commit_associated)
- ✅ Error tolerance (never blocks commits)
- ✅ Tests: 92/92 passing (87 passed, 5 WPF STA skipped)

**Documentation:** `dashboard-wpf/V8-PHASE-3.5-GIT-COMMIT-TRACKING-COMPLETE.md`

**Impact:** Conversation → Code traceability. See exactly which commits came from which discussion.

---

## 🔄 Phase 2: Advanced Dashboard Features (In Progress)

**Objective:** Polish dashboard with filtering, search, export, interactive charts, alerts

**Status:** 🔄 **IN PROGRESS** (FeaturesViewModel placeholder, advanced features not implemented)

**Timeline:** 2-3 weeks

**Prerequisites:**
- ✅ Phase 1 complete (live data working)
- 🔄 FeaturesViewModel implementation (placeholder exists, scanning not implemented)

### Tasks Breakdown

#### 2.1: Activity Tab Advanced Features
**Duration:** 3-4 days

- [ ] **Event Filtering**
  - Filter by agent (work-planner, code-executor, test-generator, etc.)
  - Filter by action (plan_created, implementation_complete, test_created, etc.)
  - Filter by result (SUCCESS, GREEN, RED, REFACTOR)
  - Filter by date range (last hour, today, this week, custom)
  - Multiple filters combinable (AND logic)

- [ ] **Event Search**
  - Search across all event properties (agent, action, details, result)
  - Regex support for advanced patterns
  - Highlight matches in results
  - Save search queries for reuse

- [ ] **Event Export**
  - Export to CSV (Excel-compatible)
  - Export to JSON (for processing)
  - Export to Markdown (for documentation)
  - Filtered export (only matching events)
  - Full export (all events)

- [ ] **Event Detail Modal**
  - Click event → Full JSON display
  - Copy JSON to clipboard
  - View related events (same agent, same action)
  - Timeline view (what happened before/after)

**Deliverables:**
- ActivityViewModel enhanced with filtering logic
- SearchBox control in ActivityView.xaml
- ExportService class (CSV, JSON, Markdown)
- EventDetailModal window

---

#### 2.2: Conversations Tab Advanced Features
**Duration:** 3-4 days

- [ ] **Context Resolution Highlighting**
  - Highlight resolved references (e.g., "it" → "FAB button")
  - Show cross-conversation references
  - Display conversation context chain

- [ ] **Conversation Search**
  - Search across topics, messages, commit messages
  - Filter by date range
  - Filter by "has commits" / "no commits"
  - Sort by recency, commit count, message count

- [ ] **Timeline View**
  - Visual timeline: message → commit → test → merge
  - Show conversation flow graphically
  - Expand/collapse timeline sections

- [ ] **Export Conversations**
  - Export to Markdown (GitHub-compatible)
  - Export to HTML (formatted, printable)
  - Export to JSON (with commits, messages, metadata)
  - Single conversation or bulk export

**Deliverables:**
- ConversationsViewModel search/filter logic
- TimelineView control (custom WPF control)
- ConversationExportService class
- Context resolution highlighter

---

#### 2.3: Metrics Tab Advanced Features
**Duration:** 4-5 days

- [ ] **Interactive Charts**
  - Zoom (select range on chart)
  - Pan (drag to navigate timeline)
  - Tooltip (hover for exact values)
  - Click data point → View details
  - LiveCharts interaction features

- [ ] **Time Range Selection**
  - Quick select: Last 7 days, 30 days, 90 days, All time
  - Custom range picker (start date, end date)
  - Charts auto-update on range change

- [ ] **Chart Export**
  - Export to PNG (screenshot)
  - Export to SVG (vector, scalable)
  - Export to PDF (printable report)
  - Include chart legend and labels

- [ ] **Custom Metric Dashboards**
  - Drag-and-drop chart arrangement
  - Save custom layouts
  - Multiple dashboard tabs
  - Share dashboard config (YAML export)

**Deliverables:**
- MetricsViewModel chart interaction logic
- ChartExportService class
- DashboardLayoutManager (save/load configurations)
- DateRangePicker control

---

#### 2.4: Health Tab Advanced Features
**Duration:** 2-3 days

- [ ] **Real-Time Health Monitoring**
  - Auto-refresh every 30 seconds (configurable)
  - Live health status indicator (green/yellow/red)
  - Health score calculation (0-100)

- [ ] **Alert Notifications**
  - Toast notifications for health issues
  - Critical alerts (event backlog >100)
  - Warning alerts (knowledge quality <80%)
  - Success alerts (cleanup completed)

- [ ] **Health History Trends**
  - Historical health data chart
  - Compare current vs. past week/month
  - Identify degradation patterns

- [ ] **Manual Health Check Trigger**
  - Button: "Run Health Check Now"
  - Force refresh all metrics
  - Re-validate brain integrity
  - Display progress during check

**Deliverables:**
- HealthViewModel auto-refresh timer
- ToastNotificationService class
- HealthHistoryView control
- ManualHealthCheckCommand

---

#### 2.5: Features Tab Implementation
**Duration:** 5-6 days

**Current State:** Placeholder ViewModel with "Feature scanning not yet implemented - Phase 2 task"

**Requirements:**

- [ ] **Feature Scanning Engine**
  - Scan prompts/ directory for agent files
  - Scan scripts/ directory for PowerShell scripts
  - Scan kds-brain/ for brain files
  - Scan tests/ for test files
  - Parse kds.md implementation status table

- [ ] **Feature Validation**
  - Code exists? (check file paths)
  - Tests exist? (check test file existence)
  - Documentation exists? (grep for feature name in docs/)
  - Agent integration exists? (check intent-router mappings)

- [ ] **Feature Status Determination**
  - ✅ Fully Implemented: Code + Tests + Docs + Agent
  - 🟡 Partially Implemented: Code exists, missing tests or docs
  - 📋 Designed Only: Documented but no code
  - ❌ Deprecated/Removed: Was documented, now deleted

- [ ] **Dashboard Display**
  - Feature list with status badges
  - Filter by status (implemented, partial, designed)
  - Search features by name
  - Click feature → Detail modal
  - Detail shows: Files, Scripts, Tests, Docs, Missing components

- [ ] **Git History Integration**
  - Scan git log for feature-related commits
  - Show when feature was added (date, commit)
  - Show feature evolution (commits that modified it)
  - Link to actual git commits

- [ ] **Feature Detail Modal**
  - Evidence section (files that exist)
  - Missing section (what's not implemented)
  - Git history (commits related to feature)
  - Fix workflow (guide to complete partial features)
  - Test execution (run feature tests)

**Deliverables:**
- FeatureScannerService class (core scanning logic)
- Feature data model (Name, Status, Files, Scripts, Tests, Docs, Commits)
- FeaturesViewModel implementation (replace placeholder)
- FeaturesView.xaml redesign (feature list, detail modal)
- Integration with git log parsing

**Dependencies:**
- Requires Phase 6 (Feature Reporting) partial implementation
- Reuse git parsing from Phase 3.5 (commit tracking)

---

### Phase 2 Success Criteria

- [ ] All 5 tabs have advanced features implemented
- [ ] Event filtering works across all properties
- [ ] Search finds results <500ms
- [ ] Charts are interactive (zoom, pan, tooltip)
- [ ] Export generates valid CSV/JSON/Markdown/PNG/SVG
- [ ] FeaturesViewModel scans and validates all KDS features
- [ ] Toast notifications appear for health alerts
- [ ] Timeline view shows conversation flow
- [ ] Manual health check completes <5 seconds
- [ ] Dashboard remains responsive with 100+ events

**Estimated Completion:** 2-3 weeks from start

**Documentation:** Will create `dashboard-wpf/PHASE-2-COMPLETION-REPORT.md`

---

## 📋 Phase 3: Cleanup Scripts (Designed - Not Started)

**Objective:** Automated brain maintenance with archival, compression, consolidation

**Status:** 📋 **DESIGNED** (Documentation exists, no code)

**Timeline:** 1 week

**Prerequisites:**
- ✅ Brain files stable (Tier 0-5 structure finalized)
- ✅ Phase 1 complete (can test cleanup with live dashboard)

### Core Script: `cleanup-kds-brain.ps1`

**Features:**

- **Archive Old Events**
  - Move events >90 days old to `kds-brain/backups/events-archive-{date}.jsonl`
  - Compress archive with `Compress-Archive` (built-in PowerShell)
  - Keep only last 90 days in events.jsonl
  - Configurable retention (30, 60, 90, 180 days)

- **Consolidate Knowledge Graph**
  - Remove patterns with confidence <0.50 (low quality)
  - Remove patterns unused for >90 days (stale)
  - Consolidate similar patterns (fuzzy matching)
  - Reduce knowledge-graph.yaml size by ~20-30%

- **Validate Conversation FIFO**
  - Ensure exactly 20 conversations (delete oldest if >20)
  - Validate JSON integrity (no corrupt conversations)
  - Extract patterns from deleted conversations → Tier 2

- **Organize Development Context**
  - Archive old metrics (>30 days) to `development-context-archive.yaml.gz`
  - Keep only last 30 days of git/test/build metrics
  - Refresh Tier 3 data (collect fresh metrics)

- **Cleanup Archives**
  - Auto-delete archives >6 months old (configurable)
  - Show archive size before deletion
  - Confirm before deletion (unless -Force)

**Parameters:**
```powershell
.\scripts\cleanup-kds-brain.ps1 `
    -EventRetentionDays 90 `
    -ArchiveRetentionMonths 6 `
    -ConsolidateKnowledge `
    -ValidateConversations `
    -RefreshMetrics `
    -Force
```

**Output:**
```
🧠 KDS Brain Cleanup Report
════════════════════════════════════════════════════

📊 Before Cleanup:
  - events.jsonl: 1.8 MB (2,347 events)
  - knowledge-graph.yaml: 280 KB (3,247 patterns)
  - conversation-history.jsonl: 180 KB (20 conversations)
  - development-context.yaml: 95 KB
  - Archives: 42 MB (14 files)

🗑️ Cleanup Actions:
  ✅ Archived 1,523 events >90 days (events-archive-20251105.jsonl.gz)
  ✅ Removed 247 low-confidence patterns (<0.50)
  ✅ Removed 189 stale patterns (unused >90 days)
  ✅ Validated conversation FIFO (20/20 conversations)
  ✅ Deleted 2 archives >6 months old (saved 12 MB)

📊 After Cleanup:
  - events.jsonl: 550 KB (824 events) ↓ -69%
  - knowledge-graph.yaml: 195 KB (2,811 patterns) ↓ -30%
  - conversation-history.jsonl: 180 KB (20 conversations) ✅
  - development-context.yaml: 95 KB ✅
  - Archives: 32 MB (13 files) ↓ -24%

💾 Total Space Saved: 1.4 MB active + 12 MB archives = 13.4 MB

✅ Cleanup complete - Brain is healthy!
```

---

### Dashboard Integration

**HealthViewModel Changes:**

- [ ] Add `LastCleanupTime` property (read from cleanup log)
- [ ] Add `CleanupCommand` (button: "Run Cleanup Now")
- [ ] Display cleanup progress (progress bar during cleanup)
- [ ] Show before/after metrics (files sizes, counts)

**HealthView.xaml Changes:**

- [ ] Cleanup status card:
  - Last cleanup: 2 days ago
  - Next scheduled: Tonight 2am
  - Button: "Run Now"
- [ ] Cleanup progress modal:
  - Show current action (Archiving events...)
  - Progress bar (0-100%)
  - Cancel button (graceful stop)

---

### Phase 3 Deliverables

- [ ] `scripts/cleanup-kds-brain.ps1` (fully functional)
- [ ] Configuration file: `kds-brain/cleanup-config.yaml`
- [ ] Cleanup log: `kds-brain/cleanup-history.jsonl`
- [ ] Dashboard integration (HealthViewModel, HealthView)
- [ ] Tests: `tests/test-cleanup-script.ps1`
- [ ] Documentation: `docs/CLEANUP-SCRIPT-GUIDE.md`

**Success Criteria:**
- Cleanup runs without errors
- Events archived correctly (compressed, valid JSON)
- Knowledge graph size reduced 20-30%
- Conversation FIFO validated (exactly 20)
- Dashboard shows cleanup status
- Manual "Run Now" button works
- Idempotent (safe to run multiple times)

**Estimated Completion:** 1 week

---

## 📋 Phase 4: Windows Service (Designed - Not Started)

**Objective:** 24/7 autonomous brain maintenance with scheduled jobs

**Status:** 📋 **DESIGNED** (Documentation exists, no code)

**Timeline:** 2 weeks

**Prerequisites:**
- ✅ Phase 3 complete (cleanup script works)
- ✅ .NET 8 SDK installed (for building service)

### Core Service: `KDS.Housekeeping.Service`

**Technology Stack:**
- .NET 8 Worker Service
- Quartz.NET for scheduling
- Windows Service hosting
- Self-contained deployment

**Jobs:**

#### Job 1: Brain Updater
**Trigger:** 50+ events OR 24 hours since last update  
**Action:** Run `brain-updater.md` prompt  
**Frequency:** Continuous monitoring (check every 5 minutes)

#### Job 2: Cleanup Service
**Trigger:** Nightly at 2:00 AM  
**Action:** Run `cleanup-kds-brain.ps1`  
**Frequency:** Daily

#### Job 3: Metrics Collector
**Trigger:** Hourly (top of each hour)  
**Action:** Run `collect-development-context.ps1`  
**Frequency:** Hourly

#### Job 4: Health Validator
**Trigger:** Continuous  
**Action:** Run `test-brain-integrity.ps1`  
**Frequency:** Every 15 minutes

#### Job 5: Anomaly Detector
**Trigger:** FileSystemWatcher on `anomalies.yaml`  
**Action:** Log anomaly event, send notification  
**Frequency:** Real-time

---

### Service Architecture

```csharp
// KDS.Housekeeping.Service/Program.cs

var builder = Host.CreateApplicationBuilder(args);

// Add Windows Service support
builder.Services.AddWindowsService(options =>
{
    options.ServiceName = "KDS Housekeeping Service";
});

// Add Quartz.NET scheduling
builder.Services.AddQuartz(q =>
{
    // Brain Updater (continuous check every 5 min)
    var brainUpdateKey = new JobKey("BrainUpdater");
    q.AddJob<BrainUpdaterJob>(opts => opts.WithIdentity(brainUpdateKey));
    q.AddTrigger(opts => opts
        .ForJob(brainUpdateKey)
        .WithIdentity("BrainUpdater-trigger")
        .WithCronSchedule("0 */5 * * * ?")); // Every 5 minutes
    
    // Cleanup Service (nightly 2am)
    var cleanupKey = new JobKey("CleanupService");
    q.AddJob<CleanupServiceJob>(opts => opts.WithIdentity(cleanupKey));
    q.AddTrigger(opts => opts
        .ForJob(cleanupKey)
        .WithIdentity("CleanupService-trigger")
        .WithCronSchedule("0 0 2 * * ?")); // 2:00 AM daily
    
    // Metrics Collector (hourly)
    var metricsKey = new JobKey("MetricsCollector");
    q.AddJob<MetricsCollectorJob>(opts => opts.WithIdentity(metricsKey));
    q.AddTrigger(opts => opts
        .ForJob(metricsKey)
        .WithIdentity("MetricsCollector-trigger")
        .WithCronSchedule("0 0 * * * ?")); // Top of every hour
    
    // Health Validator (every 15 min)
    var healthKey = new JobKey("HealthValidator");
    q.AddJob<HealthValidatorJob>(opts => opts.WithIdentity(healthKey));
    q.AddTrigger(opts => opts
        .ForJob(healthKey)
        .WithIdentity("HealthValidator-trigger")
        .WithCronSchedule("0 */15 * * * ?")); // Every 15 minutes
});

builder.Services.AddQuartzHostedService(q => q.WaitForJobsToComplete = true);

var host = builder.Build();
host.Run();
```

---

### Job Implementations

**Example: BrainUpdaterJob**

```csharp
public class BrainUpdaterJob : IJob
{
    private readonly ILogger<BrainUpdaterJob> _logger;
    private readonly IConfiguration _config;
    
    public BrainUpdaterJob(ILogger<BrainUpdaterJob> logger, IConfiguration config)
    {
        _logger = logger;
        _config = config;
    }
    
    public async Task Execute(IJobExecutionContext context)
    {
        _logger.LogInformation("Brain Updater job started");
        
        try
        {
            // Check event count
            var eventsPath = _config["KDS:EventsPath"];
            var eventCount = File.ReadLines(eventsPath).Count();
            
            // Check last update time
            var kgPath = _config["KDS:KnowledgeGraphPath"];
            var lastUpdate = File.GetLastWriteTime(kgPath);
            var hoursSinceUpdate = (DateTime.Now - lastUpdate).TotalHours;
            
            // Trigger BRAIN update if needed
            if (eventCount >= 50 || hoursSinceUpdate >= 24)
            {
                _logger.LogInformation($"BRAIN update triggered (Events: {eventCount}, Hours: {hoursSinceUpdate:F1})");
                
                // Run brain-updater script
                var scriptPath = Path.Combine(_config["KDS:ScriptsPath"], "auto-brain-updater.ps1");
                var result = await RunPowerShellScript(scriptPath, new[]
                {
                    "-RequestSummary", "Scheduled BRAIN update via service",
                    "-ResponseType", "direct"
                });
                
                if (result.ExitCode == 0)
                {
                    _logger.LogInformation("BRAIN update completed successfully");
                    await LogEvent("brain_update_completed", new { eventCount, hoursSinceUpdate });
                }
                else
                {
                    _logger.LogError($"BRAIN update failed: {result.Error}");
                    await LogEvent("brain_update_failed", new { error = result.Error });
                }
            }
            else
            {
                _logger.LogInformation($"BRAIN update not needed (Events: {eventCount}, Hours: {hoursSinceUpdate:F1})");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error in Brain Updater job");
            await LogEvent("brain_updater_error", new { error = ex.Message });
        }
    }
    
    private async Task<ProcessResult> RunPowerShellScript(string scriptPath, string[] args)
    {
        // Execute PowerShell script with arguments
        // Return exit code and output
    }
    
    private async Task LogEvent(string eventType, object details)
    {
        // Log to events.jsonl
    }
}
```

---

### Installation & Management

**Install Script: `scripts/install-kds-service.ps1`**

```powershell
# Publish service as self-contained
dotnet publish `
    -c Release `
    --self-contained `
    -r win-x64 `
    -o ".\publish\KDS.Housekeeping.Service"

# Install as Windows Service
sc.exe create "KDS Housekeeping Service" `
    binPath="$PWD\publish\KDS.Housekeeping.Service\KDS.Housekeeping.Service.exe" `
    start=auto `
    DisplayName="KDS Housekeeping Service" `
    description="24/7 autonomous KDS brain maintenance"

# Start service
sc.exe start "KDS Housekeeping Service"

Write-Host "✅ KDS Housekeeping Service installed and started"
```

**Uninstall Script: `scripts/uninstall-kds-service.ps1`**

```powershell
# Stop service
sc.exe stop "KDS Housekeeping Service"

# Delete service
sc.exe delete "KDS Housekeeping Service"

Write-Host "✅ KDS Housekeeping Service uninstalled"
```

---

### Dashboard Integration

**HealthViewModel Changes:**

- [ ] Add `ServiceStatus` property (Running/Stopped/NotInstalled)
- [ ] Add `LastJobRuns` property (dictionary of job → last run time)
- [ ] Add `StartServiceCommand`
- [ ] Add `StopServiceCommand`
- [ ] Add `TriggerJobCommand` (run job immediately)

**HealthView.xaml Changes:**

- [ ] Service status card:
  - Status: ✅ Running / ⚠️ Stopped / ❌ Not Installed
  - Buttons: Start, Stop, Restart
  - View logs button

- [ ] Job status section:
  - Brain Updater: Last run 5 min ago
  - Cleanup Service: Last run 2 days ago (Tonight 2am)
  - Metrics Collector: Last run 45 min ago (Next in 15 min)
  - Health Validator: Last run 3 min ago
  - Buttons: "Trigger Now" for each job

**Service Logs View:**

- [ ] View service logs (read from `kds-brain/service-logs/housekeeping.log`)
- [ ] Filter by job type, log level
- [ ] Tail mode (auto-scroll to latest)

---

### Phase 4 Deliverables

- [ ] `KDS.Housekeeping.Service` project (C# .NET 8 Worker Service)
- [ ] 5 job implementations (BrainUpdater, Cleanup, Metrics, Health, Anomaly)
- [ ] Configuration: `appsettings.json` (paths, schedules)
- [ ] Install script: `scripts/install-kds-service.ps1`
- [ ] Uninstall script: `scripts/uninstall-kds-service.ps1`
- [ ] Dashboard integration (HealthViewModel, HealthView)
- [ ] Service logs viewer in dashboard
- [ ] Tests: Service startup, job execution, error handling
- [ ] Documentation: `docs/WINDOWS-SERVICE-GUIDE.md`

**Success Criteria:**
- Service installs without errors
- All 5 jobs execute on schedule
- BRAIN updates trigger automatically (50 events OR 24h)
- Cleanup runs nightly at 2am
- Metrics refresh hourly
- Health checks run every 15 min
- Dashboard shows service status
- Manual job triggering works
- Service survives system restart

**Estimated Completion:** 2 weeks

---

## 📋 Phase 5: Deployment Automation (Designed - Not Started)

**Objective:** One-click KDS setup for new environments

**Status:** 📋 **DESIGNED** (Documentation in V8 Real-Time Intelligence Plan)

**Timeline:** 1 week

**Prerequisites:**
- ✅ All core scripts stable
- ✅ Dashboard compiled and tested
- ✅ Service compiled and tested

### Core Script: `setup-kds.ps1`

**Full details in:** `docs/KDS-V8-REAL-TIME-INTELLIGENCE-PLAN.md` (lines 773-1083)

**Key Features:**
- Environment detection (project type, git repo, write permissions)
- Directory structure creation (brain, sessions, reports, logs, cache)
- Git hook installation (post-commit, post-merge, pre-commit)
- Configuration generation (kds.config.json)
- Optional component installation (Dashboard, Service)
- Initial brain scan (git history, file structure, baseline metrics)
- Health validation and setup report

**Usage Examples:**

```powershell
# Interactive install (prompts for choices)
.\setup-kds.ps1

# Automated full install
.\setup-kds.ps1 `
    -NonInteractive `
    -KdsPath "D:\PROJECTS\MyApp\KDS" `
    -IncludeDashboard `
    -IncludeService `
    -AutoStart

# Core only (minimal)
.\setup-kds.ps1 -CoreOnly

# Upgrade existing v6 → v8
.\setup-kds.ps1 -Upgrade
```

---

### Deployment Package Structure

```
KDS-v8.0-Deployment.zip
├── setup-kds.ps1              ← Main installer
├── setup-config.yaml          ← Configuration template
├── README-SETUP.md            ← Setup instructions
├── KDS/                       ← Core files
│   ├── prompts/
│   ├── scripts/
│   ├── kds-brain/
│   ├── governance/
│   └── hooks/
├── Dashboard.exe              ← Self-contained WPF app
├── Service.exe                ← Self-contained Windows Service
└── uninstall-kds.ps1          ← Clean removal script
```

---

### Phase 5 Deliverables

- [ ] `setup-kds.ps1` (fully functional installer)
- [ ] `setup-config.yaml` (deployment configuration template)
- [ ] `uninstall-kds.ps1` (safe removal script)
- [ ] `README-SETUP.md` (user-facing setup guide)
- [ ] Deployment package: `KDS-v8.0-Deployment.zip`
- [ ] Tests: Install in fresh environment, upgrade, core-only, full-suite
- [ ] Documentation: `docs/DEPLOYMENT-GUIDE.md`

**Success Criteria:**
- Fresh install completes <5 minutes
- All 4 install scenarios work (interactive, automated, core-only, upgrade)
- Git hooks installed correctly
- Brain structure created correctly
- Initial scan completes successfully
- Dashboard launches if installed
- Service starts if installed
- Uninstall removes everything (except brain if KeepBrain)
- Setup report generated

**Estimated Completion:** 1 week

---

## 📋 Phase 6: Feature Reporting (Designed - Not Started)

**Objective:** Automated feature inventory with git validation

**Status:** 📋 **DESIGNED** (Documentation in V8 Real-Time Intelligence Plan)

**Timeline:** 1 week

**Prerequisites:**
- ✅ Phase 2 complete (FeaturesViewModel ready)
- ✅ Git parsing logic exists (from Phase 3.5)

### Core Script: `generate-brain-feature-report.ps1`

**Full details in:** `docs/KDS-V8-REAL-TIME-INTELLIGENCE-PLAN.md` (lines 1114-1616)

**Key Features:**
- Git history scanner (feature commits, lifecycle tracking)
- Code scanner (actual implementations in kds-brain/)
- Documentation scanner (feature mentions in docs/)
- Validation layer (code vs docs vs git)
- Report generator (HTML, Markdown, JSON)

**Usage Examples:**

```powershell
# Generate HTML report
.\scripts\generate-brain-feature-report.ps1 -OutputFormat html

# Validate only (no report)
.\scripts\generate-brain-feature-report.ps1 -ValidateOnly

# Include deprecated features
.\scripts\generate-brain-feature-report.ps1 -IncludeDeprecated

# Custom git history (last 90 days)
.\scripts\generate-brain-feature-report.ps1 -GitHistoryDays 90
```

---

### Report Output Examples

**HTML Report:** `reports/brain-feature-inventory.html`
- Summary cards: Implemented, Partial, Designed, Discrepancies
- Feature cards with evidence (files, scripts, tests, docs)
- Git history timeline
- Discrepancy warnings
- Interactive filtering and search

**Markdown Report:** `reports/brain-feature-inventory.md`
- GitHub-compatible formatting
- Table of features with status
- Links to actual files
- Git commit references

**JSON Report:** `reports/brain-feature-inventory.json`
- API-consumable format
- Complete feature metadata
- Validation results
- Discrepancy details

---

### Dashboard Integration (FeaturesViewModel)

**Already designed in Phase 2.5**, but uses report generator:

- [ ] Call `generate-brain-feature-report.ps1` on startup
- [ ] Parse JSON output
- [ ] Display features in FeaturesView
- [ ] Refresh on demand (button: "Scan Features Now")
- [ ] Filter by status
- [ ] Search features
- [ ] Detail modal with git history

---

### Automated Validation

**Service Integration (Phase 4):**

- [ ] Nightly job: Run feature validation
- [ ] Alert on discrepancies (>3 found)
- [ ] Log to events.jsonl
- [ ] Update kds.md status table (if CI/CD enabled)

---

### Phase 6 Deliverables

- [ ] `scripts/generate-brain-feature-report.ps1` (fully functional)
- [ ] Report templates (HTML, Markdown, JSON)
- [ ] FeaturesViewModel integration (call report generator)
- [ ] Dashboard feature detail modal
- [ ] Automated validation (service job)
- [ ] Tests: Report generation, validation accuracy
- [ ] Documentation: `docs/FEATURE-REPORTING-GUIDE.md`

**Success Criteria:**
- Report scans git history correctly
- Code scanning detects all implementations
- Documentation scanning finds feature mentions
- Validation accurately identifies discrepancies
- HTML report is interactive and filterable
- Markdown report is GitHub-compatible
- JSON report is API-consumable
- Dashboard displays features from report
- Automated validation runs nightly (if service installed)
- Discrepancy alerts work

**Estimated Completion:** 1 week

---

## 📋 Phase 7: Polish & Release (Designed - Not Started)

**Objective:** Production-ready v8.0 release with full documentation

**Status:** 📋 **DESIGNED** (Documentation in V8 Real-Time Intelligence Plan)

**Timeline:** 1 week

**Prerequisites:**
- ✅ All phases 2-6 complete
- ✅ Manual testing complete
- ✅ Performance testing complete

### Polish Tasks

#### 7.1: Dashboard Themes
**Duration:** 1-2 days

- [ ] Light theme (current - already done)
- [ ] Dark theme:
  - Background: #1E1E1E (dark gray)
  - Surface: #2D2D2D (lighter gray)
  - Text: #FFFFFF (white)
  - Accent colors: Same (blue, green, orange)
  - Material Design dark palette

- [ ] Theme switcher:
  - Button in header: ☀️/🌙
  - Save preference to config
  - Apply on startup

---

#### 7.2: Toast Notifications
**Duration:** 1 day

- [ ] Windows toast notifications (Microsoft.Toolkit.Uwp.Notifications)
- [ ] Notification types:
  - Info (blue icon)
  - Success (green checkmark)
  - Warning (yellow triangle)
  - Error (red X)
- [ ] Notification triggers:
  - BRAIN update complete
  - Cleanup complete
  - Health alert (critical/warning)
  - Service status change
- [ ] Click to open dashboard (if closed)

---

#### 7.3: Export Features
**Duration:** 1-2 days

- [ ] Export dashboard to PDF:
  - Current view only
  - All tabs (multi-page PDF)
  - Include charts as images
  - Formatted and printable

- [ ] Export dashboard to HTML:
  - Static HTML with embedded CSS
  - Charts as SVG
  - Shareable via email/browser

- [ ] Export configuration:
  - Dashboard layout
  - Filter settings
  - Chart configurations

---

#### 7.4: Mini-Mode & Always-On-Top
**Duration:** 1 day

- [ ] Mini-mode (compact view):
  - Small window (300x400px)
  - Shows only critical metrics
  - Event count, health status, service status
  - Click to expand to full dashboard

- [ ] Always-on-top option:
  - Checkbox in settings
  - Window stays above other apps
  - Useful for monitoring during work

---

#### 7.5: Keyboard Shortcuts
**Duration:** 1 day

- [ ] Global shortcuts:
  - Ctrl+R: Refresh all data
  - Ctrl+F: Search/Filter
  - Ctrl+E: Export current view
  - Ctrl+1-5: Switch tabs (1=Activity, 2=Conversations, etc.)
  - Ctrl+W: Close dashboard
  - F5: Manual health check

---

### Documentation Tasks

#### 7.6: Installation Guide
**Duration:** 1 day

- [ ] `docs/INSTALLATION-GUIDE.md`:
  - System requirements
  - Download instructions
  - 3 installation options (Core, Core+Dashboard, Full Suite)
  - Step-by-step with screenshots
  - Troubleshooting common issues
  - Verification steps

---

#### 7.7: User Manual
**Duration:** 2 days

- [ ] `docs/USER-MANUAL.md`:
  - Dashboard overview
  - Tab-by-tab feature guide:
    - Activity: Filtering, search, export
    - Conversations: Timeline, git commits
    - Metrics: Charts, time ranges, export
    - Health: Monitoring, alerts, manual checks
    - Features: Scanning, validation, detail
  - Keyboard shortcuts
  - Settings and configuration
  - Export features (PDF, HTML, CSV, JSON)
  - Tips and tricks

---

#### 7.8: Developer Guide
**Duration:** 1 day

- [ ] `docs/DEVELOPER-GUIDE.md`:
  - Building from source
  - Project structure
  - Adding new ViewModels
  - Adding new jobs to service
  - Extending cleanup script
  - Contributing guidelines
  - Code style
  - Testing requirements

---

#### 7.9: Troubleshooting Guide
**Duration:** 1 day

- [ ] `docs/TROUBLESHOOTING-GUIDE.md`:
  - Dashboard won't launch
  - FileSystemWatcher not updating
  - Service won't start
  - Cleanup script errors
  - Git hooks not running
  - High memory usage
  - Slow performance
  - FAQ (20+ common questions)

---

### Distribution Tasks

#### 7.10: GitHub Release
**Duration:** 1 day

- [ ] Create release branch: `release/v8.0`
- [ ] Tag release: `v8.0.0`
- [ ] Release notes:
  - What's new in v8.0
  - Breaking changes (if any)
  - Upgrade instructions (v6 → v8)
  - Known issues
  - Download links

- [ ] Release artifacts:
  - KDS-v8.0-Core.zip
  - KDS-v8.0-Dashboard.exe
  - KDS-v8.0-Service.exe
  - KDS-v8.0-Full.zip (all-in-one)
  - Source code (zip, tar.gz)

---

#### 7.11: Self-Contained Publish
**Duration:** 1 day

- [ ] Dashboard:
  ```bash
  dotnet publish dashboard-wpf/KDS.Dashboard.WPF/KDS.Dashboard.WPF.csproj `
      -c Release `
      --self-contained `
      -r win-x64 `
      -p:PublishSingleFile=true `
      -p:PublishTrimmed=true `
      -o publish/Dashboard
  ```

- [ ] Service:
  ```bash
  dotnet publish services/KDS.Housekeeping.Service/KDS.Housekeeping.Service.csproj `
      -c Release `
      --self-contained `
      -r win-x64 `
      -p:PublishSingleFile=true `
      -o publish/Service
  ```

- [ ] Verify:
  - No external dependencies (.NET runtime not needed)
  - Single .exe files
  - Size: Dashboard (~15-25 MB), Service (~10-15 MB)

---

#### 7.12: Feature Inventory (Auto-Generated)
**Duration:** <1 hour (automated)

- [ ] Run `generate-brain-feature-report.ps1`
- [ ] Generate HTML report
- [ ] Add to release artifacts
- [ ] Validate no discrepancies (or document known issues)

---

### Testing Tasks

#### 7.13: End-to-End Testing
**Duration:** 2 days

- [ ] Fresh install scenarios:
  - Windows 10 Pro
  - Windows 11 Pro
  - Windows Server 2022

- [ ] Upgrade scenarios:
  - v6.0 → v8.0 (preserve brain data)

- [ ] Feature testing:
  - All dashboard tabs functional
  - Real-time updates working
  - Export features (PDF, HTML, CSV, JSON)
  - Service jobs execute on schedule
  - Cleanup script archives correctly
  - Feature reporting accurate

---

#### 7.14: Performance Testing
**Duration:** 1 day

- [ ] Large brain files:
  - 10,000 events in events.jsonl
  - 50 conversations
  - 10,000+ patterns in knowledge graph

- [ ] Metrics:
  - Dashboard startup time (<2 seconds)
  - Event display latency (<1 second)
  - Memory footprint (<100 MB dashboard, <50 MB service)
  - CPU usage (<1% idle)

---

#### 7.15: Upgrade Testing (v6 → v8)
**Duration:** 1 day

- [ ] Backup brain data
- [ ] Run `setup-kds.ps1 -Upgrade`
- [ ] Verify:
  - Brain files intact
  - Git hooks updated
  - Configuration migrated
  - Dashboard shows existing data
  - Service installs correctly

- [ ] Rollback test (restore v6 from backup)

---

### Phase 7 Deliverables

- [ ] Dashboard themes (light + dark)
- [ ] Toast notifications
- [ ] Export to PDF/HTML
- [ ] Mini-mode and always-on-top
- [ ] Keyboard shortcuts
- [ ] Complete documentation:
  - Installation Guide
  - User Manual
  - Developer Guide
  - Troubleshooting Guide
  - FAQ
- [ ] GitHub release (v8.0.0)
- [ ] Self-contained binaries (Dashboard.exe, Service.exe)
- [ ] Deployment package (KDS-v8.0-Deployment.zip)
- [ ] Feature inventory report (auto-generated)
- [ ] End-to-end testing complete
- [ ] Performance benchmarks documented
- [ ] Upgrade path validated (v6 → v8)

**Success Criteria:**
- All polish features implemented
- Both themes working (light/dark)
- Notifications appear correctly
- PDF/HTML export generates valid files
- Mini-mode and always-on-top functional
- Keyboard shortcuts work
- All documentation complete and accurate
- GitHub release published
- Binaries are self-contained (no .NET install needed)
- Deployment package installs correctly
- Upgrade from v6 works without data loss
- Performance targets met (startup <2s, latency <1s, memory <100MB)
- No critical bugs

**Estimated Completion:** 1 week

---

## 📅 Overall Timeline

| Phase | Duration | Status | Start Date | End Date |
|-------|----------|--------|------------|----------|
| **Phase 0** | 1 week | ✅ Complete | Nov 5 | Nov 5 |
| **Phase 1** | 1 week | ✅ Complete | Nov 5 | Nov 5 |
| **Phase 3.5** | 3 days | ✅ Complete | Nov 5 | Nov 5 |
| **Phase 2** | 2-3 weeks | 🔄 Next | TBD | TBD |
| **Phase 3** | 1 week | 📋 Planned | TBD | TBD |
| **Phase 4** | 2 weeks | 📋 Planned | TBD | TBD |
| **Phase 5** | 1 week | 📋 Planned | TBD | TBD |
| **Phase 6** | 1 week | 📋 Planned | TBD | TBD |
| **Phase 7** | 1 week | 📋 Planned | TBD | TBD |

**Total Estimated Time:** 6-8 weeks (assuming no parallel work)

**Potential Acceleration:**
- Phases 2 & 3 can run in parallel (dashboard features + cleanup script)
- Phases 5 & 6 can run in parallel (deployment + feature reporting)
- With parallel work: **4-6 weeks total**

---

## 🎯 Success Metrics (Overall v8.0)

### Must-Have (Release Blockers)
- ✅ Phase 0 complete (enforcement layer)
- ✅ Phase 1 complete (live data dashboard)
- ✅ Phase 3.5 complete (git commit tracking)
- [ ] Phase 2 complete (advanced dashboard features)
- [ ] Phase 3 complete (cleanup scripts)
- [ ] Phase 4 complete (Windows service)
- [ ] Phase 7 complete (polish & documentation)

### Should-Have (Post-MVP)
- [ ] Phase 5 complete (deployment automation)
- [ ] Phase 6 complete (feature reporting)

### Nice-to-Have (Future)
- [ ] VS Code extension integration
- [ ] Mobile companion app
- [ ] Web dashboard (team mode)
- [ ] AI-powered insights

---

## 📚 References

**Planning Documents:**
- `docs/KDS-V8-ENFORCEMENT-LAYER-PLAN.md` - Phase 0 detailed plan
- `docs/KDS-V8-REAL-TIME-INTELLIGENCE-PLAN.md` - Phases 1-7 detailed plan
- `docs/reports/V8-DEPLOYMENT-AND-REPORTING-SUMMARY.md` - Deployment & reporting additions

**Completion Reports:**
- `dashboard-wpf/V8-PHASE-0-ENFORCEMENT-COMPLETE.md` - Phase 0 complete ✅
- `dashboard-wpf/V8-PHASE-1-LIVE-DATA-COMPLETE.md` - Phase 1 complete ✅
- `dashboard-wpf/V8-PHASE-3.5-GIT-COMMIT-TRACKING-COMPLETE.md` - Phase 3.5 complete ✅
- `dashboard-wpf/PHASE-1-COMPLETION-REPORT.md` - Detailed Phase 1 report
- `dashboard-wpf/PHASE-2-ENHANCEMENTS-COMPLETE.md` - Partial Phase 2 work

**Other Relevant Docs:**
- `prompts/user/kds.md` - Main KDS entry point (updated with V8 status)
- `dashboard-wpf/README.md` - Dashboard project overview

---

## 🚀 How to Proceed

### To Start Phase 2 (Advanced Dashboard Features):

```markdown
#file:KDS/prompts/user/kds.md

Implement V8 Phase 2: Advanced Dashboard Features

Start with Task 2.5 (FeaturesViewModel Implementation) since it's a prerequisite for other advanced features.

Follow the detailed plan in:
- File: KDS/docs/KDS-V8-COMPLETION-ROADMAP.md
- Section: Phase 2: Advanced Dashboard Features (In Progress)
- Subsection: 2.5: Features Tab Implementation

Deliverables:
- FeatureScannerService class
- Feature data model
- FeaturesViewModel implementation (replace placeholder)
- FeaturesView.xaml redesign
- Integration with git log parsing

Success criteria:
- Scans all KDS features (prompts, scripts, brain files, tests)
- Validates code vs docs vs git
- Determines feature status (✅🟡📋❌)
- Displays in dashboard with filtering and search
- Detail modal shows evidence and missing components
```

### To Start Phase 3 (Cleanup Scripts):

```markdown
#file:KDS/prompts/user/kds.md

Implement V8 Phase 3: Cleanup Scripts

Create cleanup-kds-brain.ps1 with:
- Archive old events (>90 days)
- Consolidate knowledge graph (remove low-confidence)
- Validate conversation FIFO
- Organize development context

Follow detailed plan in:
- File: KDS/docs/KDS-V8-COMPLETION-ROADMAP.md
- Section: Phase 3: Cleanup Scripts (Designed - Not Started)
```

### To View Detailed Phase Plans:

```markdown
#file:KDS/docs/KDS-V8-COMPLETION-ROADMAP.md

Review the comprehensive roadmap for phases 2-7 with:
- Task breakdowns
- Duration estimates
- Success criteria
- Dependencies
- Code examples
- Dashboard integration details
```

---

**Status:** 🔄 **ACTIVE - Phase 2 Next**  
**Completion:** 37.5% (3 of 8 phases complete)  
**Estimated Time to v8.0 Release:** 6-8 weeks


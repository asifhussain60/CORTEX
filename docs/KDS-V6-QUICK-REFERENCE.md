# KDS v6.0 - Quick Reference Guide

**Last Updated:** 2025-11-04  
**Version:** 6.0.0  
**Status:** 🎯 Ready to Implement

---

## 🎯 What is v6.0?

**One-Sentence Summary:**
> Fire-and-forget feature implementation where the brain handles everything—code, tests, documentation, AND automatic infrastructure updates (dashboard, metrics, health checks).

---

## 🚀 Key Enhancements

### 1. Instinct Layer (Auto-Infrastructure)

**What:** Automatic dashboard, metrics, and health check updates when functionality changes

**Example:**
```
Create PdfExportService.cs
  ↓
🧠 INSTINCT LAYER AUTO-TRIGGERS:
  ✅ Dashboard widget added
  ✅ Metrics configured (export_count, export_failures)
  ✅ Health checks added (service running?)
  ✅ Brain categorized (Services/Export/)

Manual steps: 0
```

---

### 2. Multi-Threaded Crawlers

**What:** 60% faster project scanning with parallel PowerShell jobs

**Before:**
```
1000 files = 10 minutes (sequential)
```

**After:**
```
1000 files = 4 minutes (parallel) - 60% faster!
```

---

### 3. Database Guidance

**What:** Clear path to SQLite for large projects (opt-in)

**When to Migrate:**
- BRAIN size > 5 MB
- Query time > 500 ms
- Project > 5000 files

**Current Recommendation:** Stay file-based (NoorCanvas ~1000 files, ~500 KB BRAIN)

---

### 4. Fire-and-Forget Workflow

**What:** Give brain complete feature → It handles everything

**Example:**
```markdown
#file:KDS/prompts/user/kds.md Add real-time notifications with SignalR

[30 minutes later]

✅ Feature complete!
  ✅ 5 files created (Hub, Service, Component, Config, Tests)
  ✅ 3 dashboard widgets added (automatic)
  ✅ 7 metrics configured (automatic)
  ✅ 5 health checks added (automatic)
  ✅ Build passing, tests passing
  
Ready to use!
```

---

## 📋 Implementation Phases

| Phase | Week | Focus | Deliverables |
|-------|------|-------|--------------|
| **0** | 1 | Instinct Layer | Auto-update triggers working |
| **1** | 2 | Crawlers | 60% faster scanning |
| **2** | 3 | Database | Migration script + guidance |
| **3** | 4 | Integration | All auto-updates validated |
| **4** | 4-5 | E2E Testing | Fire-and-forget demonstrated |
| **5** | 5 | Documentation | Complete guides + training |

**Total:** 5 weeks (80-100 hours)

---

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Auto-Update Coverage | 100% | 0% |
| Crawler Speed (1000 files) | < 5 min | ~10 min |
| Fire-and-Forget Success | 90%+ | N/A |
| Time Savings | 40%+ | 0% |
| Manual Infrastructure Updates | 0 | 3-4 per feature |

---

## 🔧 How Instinct Layer Works

### Trigger Flow

```
New File Created (PdfExportService.cs)
    ↓
TRIGGER: on-file-create
    ↓
ANALYZE: File type, name, dependencies
    ↓
CATEGORIZE: Services/Export/PdfExportService
    ↓
DASHBOARD: Add widget "PDF Export Service"
    ↓
METRICS: Add pdf_export_count, pdf_export_failures
    ↓
HEALTH: Add "PDF Export Service running?"
    ↓
BRAIN: Update file-relationships.yaml
    ↓
COMPLETE (< 1 second overhead)
```

### Trigger Types

| Trigger | When | Actions |
|---------|------|---------|
| **on-file-create** | New .cs, .razor, .ts file | Categorize, dashboard, metrics, health |
| **on-component-add** | New UI component | Dashboard, metrics, extract test IDs |
| **on-function-add** | New method/function | Metrics (if trackable) |
| **on-test-add** | New test file | Health checks, coverage tracking |
| **on-config-change** | Config file updated | Health check validation |

---

## 🔄 Multi-Threaded Crawler

### Architecture

```
orchestrator.ps1 (Master)
    ├── ui-crawler.ps1      (Blazor/React components)
    ├── api-crawler.ps1     (Controllers/endpoints)
    ├── service-crawler.ps1 (Business logic)
    └── test-crawler.ps1    (Tests)

All run in parallel (4 threads)
```

### Performance

```
Single-Threaded (Current):
  UI (400):     4 min ┐
  API (300):    3 min │ Sequential
  Services (200): 2 min │ = 10 min total
  Tests (100):  1 min ┘

Multi-Threaded (v6.0):
  UI (400):     4 min ┐
  API (300):    3 min ├─ Parallel
  Services (200): 2 min │ = 4 min total
  Tests (100):  1 min ┘  (60% faster!)
```

---

## 💾 Database Decision Tree

```yaml
Your Project:
  files_scanned: 1000
  brain_size: "~500 KB"
  query_time: "~145 ms"
  
Recommendation:
  use: "file-based" ✅
  reason: "Fast, simple, portable"
  
When to Migrate:
  brain_size: "> 5 MB"
  query_time: "> 500 ms"
  files_scanned: "> 5000"
  
  then: "Run migrate-to-database.ps1"
```

---

## 🎯 Fire-and-Forget Example

### User Request

```markdown
#file:KDS/prompts/user/kds.md

Add PDF export feature for transcripts
```

### What Happens (Automatic)

**Phase 1: Planning (2 min)**
```
🧠 Planner analyzes request
  - Detects: New feature, export functionality
  - Creates plan: 3 phases, 8 tasks
  - Test-first approach
```

**Phase 2: Implementation (15 min)**
```
🔨 Executor creates:
  ✅ PdfExportService.cs
     ↳ 🧠 Instinct: Dashboard, metrics, health (automatic)
     
  ✅ PdfExportButton.razor
     ↳ 🧠 Instinct: Dashboard, test IDs, metrics (automatic)
     
  ✅ PdfExportController.cs
     ↳ 🧠 Instinct: Dashboard, metrics, health (automatic)
```

**Phase 3: Testing (8 min)**
```
🧪 Tester creates:
  ✅ PdfExportServiceTests.cs
  ✅ PdfExportControllerTests.cs
  ✅ pdf-export-button.spec.ts (Playwright)
     ↳ 🧠 Instinct: Health checks added (automatic)
```

**Phase 4: Validation (2 min)**
```
✅ Validator runs:
  - Build: ✅ Passing
  - Tests: ✅ All green
  - Health: ✅ 100%
     ↳ 🧠 Instinct: Dashboard shows all green (automatic)
```

**Phase 5: Commit (1 min)**
```
📝 Commit handler:
  "feat(export): Add PDF export for transcripts"
  - 3 source files
  - 3 test files
  - Auto-generated infrastructure updates
```

**Total Time:** ~28 minutes  
**Manual Steps:** 1 (initial request)  
**Automatic Infrastructure Updates:** 12+

---

## 📁 Folder Structure Changes

### New in v6.0

```
KDS/brain/instinct/
├── auto-infrastructure/         # NEW: Auto-update scripts
│   ├── dashboard-updater.ps1
│   ├── metrics-collector.ps1
│   ├── health-validator.ps1
│   └── categorizer.ps1
│
└── triggers/                    # NEW: Event-driven automation
    ├── on-file-create.yaml
    ├── on-component-add.yaml
    ├── on-function-add.yaml
    ├── on-test-add.yaml
    ├── on-config-change.yaml
    └── trigger-orchestrator.ps1

KDS/scripts/crawlers/            # NEW: Multi-threaded crawlers
├── orchestrator.ps1
├── ui-crawler.ps1
├── api-crawler.ps1
├── service-crawler.ps1
└── test-crawler.ps1
```

---

## 🏆 Benefits at a Glance

| Benefit | v5.0 (Current) | v6.0 (Fire-and-Forget) |
|---------|----------------|------------------------|
| **Manual Dashboard Updates** | 3-4 per feature | 0 (automatic) |
| **Manual Metrics Setup** | 2-3 per feature | 0 (automatic) |
| **Manual Health Checks** | 2-3 per feature | 0 (automatic) |
| **Crawler Speed (1000 files)** | 10 min | 4 min (60% faster) |
| **Feature Implementation Time** | ~45 min | ~28 min (40% faster) |
| **Developer Focus** | Code + Infrastructure | Code only |

---

## ⚡ Quick Commands

### Trigger Fire-and-Forget Implementation

```markdown
#file:KDS/prompts/user/kds.md

Add [feature description]
```

Example:
```markdown
#file:KDS/prompts/user/kds.md

Add real-time notifications with SignalR
```

### Run Multi-Threaded Crawler

```powershell
.\KDS\scripts\crawlers\orchestrator.ps1
```

### Check Storage Metrics

```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```

Look for "Storage Metrics" section:
- Current size
- Query performance
- Database recommendation

### Migrate to Database (if needed)

```powershell
# Dry run first
.\KDS\scripts\migrate-to-database.ps1 -DryRun

# Execute migration
.\KDS\scripts\migrate-to-database.ps1
```

---

## 🔍 Monitoring Progress

### During Implementation

Watch the console for Instinct triggers:
```
[14:32:15] 🧠 INSTINCT: on-file-create → PdfExportService.cs
           ✅ Dashboard widget added
           ✅ Metrics configured (2 metrics)
           ✅ Health check added
           ✅ Brain categorized

[14:35:22] 🧠 INSTINCT: on-component-add → PdfExportButton.razor
           ✅ Dashboard widget added
           ✅ Test IDs extracted (3 IDs)
           ✅ Metrics configured (2 metrics)
```

### After Implementation

Launch dashboard:
```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```

Check:
- ✅ New widgets visible
- ✅ Metrics collecting data
- ✅ Health checks green
- ✅ Build passing
- ✅ Tests passing

---

## 📚 Documentation

**Full Plan:** `KDS/docs/KDS-V6-HOLISTIC-PLAN.md`  
**Summary:** `KDS/docs/KDS-V6-IMPLEMENTATION-SUMMARY.md`  
**This Guide:** `KDS/docs/KDS-V6-QUICK-REFERENCE.md`

---

## 🚦 Current Status

**Phase 0:** ⏳ Ready to Start (Week 1)  
**Overall Progress:** 0% (0/41 tasks)  
**Expected Completion:** 2025-12-09 (5 weeks)

---

## ❓ Common Questions

**Q: Will this slow down my development?**  
A: No. Triggers run asynchronously with < 1 second overhead per file.

**Q: Can I disable auto-updates?**  
A: Yes. Edit `trigger-config.yaml` to enable/disable specific triggers.

**Q: What if a trigger makes a mistake?**  
A: Rollback capability built-in. Triggers validated before execution.

**Q: Do I need to migrate to database?**  
A: Not yet. Monitor health dashboard. Migrate when BRAIN > 5 MB or queries > 500ms.

**Q: Is this backward compatible?**  
A: Yes. 100% backward compatible. Auto-updates are additive.

---

**Ready to revolutionize your development workflow!** 🚀

# 📊 CORTEX Reports Folder

**Purpose:** Long-term reference documentation for major architectural decisions and system-wide changes.

**Owner:** CORTEX internal reference (not for user consumption)

---

## 🎯 Report Policy

### ❌ DO NOT Create Reports For:

- **Task completion summaries** - User won't read them
- **Timestamped operational logs** - Ephemeral data with no reference value
- **Benchmark/test results** - Use `cortex-brain/analytics/metrics.db` instead
- **Incremental progress updates** - Use git commit messages
- **Duplicate analyses** - One is enough

### ✅ DO Create Reports For:

- **Major architectural decisions** - Changes affecting multiple tiers
- **System-wide migrations** - E.g., CORTEX 3.0 → 4.0 migration
- **Compliance audits** - When required for governance
- **Reference documentation** - Non-temporal guides (e.g., MOCK-STUB-AUDIT)

---

## 🗑️ Cleanup Schedule

**Frequency:** Every maintenance cycle (Phase 7)

**Target:** Keep reports folder under 50 files, <5MB

**Command:** See `.github/prompts/cortex-maintenance.prompt.md` Phase 7

---

## 📁 Current Reports (Post-Cleanup)

| Report | Purpose | Keep? |
|--------|---------|-------|
| `SYSTEM-INTEGRITY-*.md` | System health snapshots | ✅ Reference |
| `CORTEX-*-CLEANUP-*.md` | Major cleanup operations | ✅ Historical context |
| `ORCHESTRATOR-*.md` | Orchestrator architecture changes | ✅ Reference |
| `MOCK-STUB-AUDIT.md` | Testing strategy reference | ✅ Reference |
| `GITHUB-PAGES-DEPLOYMENT.md` | Deployment configuration | ✅ Reference |
| `LEGACY-PURGE-*.md` | Major purge operations | ✅ Historical context |

---

## 🔄 Maintenance Actions (Dec 28, 2025)

**Before:** 204 files, 5.3MB  
**After:** 102 files, 2.0MB  
**Deleted:** 102 files (~3.3MB)

### Removed Categories:
- 34 timestamped JSONs (cleanup-*, architectural-review-*, brain-tuning-*)
- 15 duplicate unwired-components analyses
- 40+ task completion summaries (story-*, planning-*, feature-*)
- 30+ benchmark/test JSONs

---

**Last Updated:** 2025-12-28  
**Next Review:** Next maintenance cycle

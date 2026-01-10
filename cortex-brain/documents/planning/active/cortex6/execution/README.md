# 🎯 CORTEX 6.0 Execution Plan - README

**Status:** 🔄 IN PROGRESS | **Current Layer:** 4 of 5 | **Progress:** 48.6% (34h/70h)

---

## 📋 Overview

This folder contains the **complete, executable phased plan** for CORTEX 6.0 build. Zero ambiguity, detailed DoR/DoD checklists, nested folder structure with progress tracking.

**Strategy:** Snowball (downstream unlocking prioritization)  
**Total Effort:** 70 hours across 5 layers  
**Phases:** 8 detailed implementation phases

---

## 📁 Folder Structure

```
execution/
├── README.md                          # This file
├── plan-index.yaml                    # Master execution index
├── config/                            # Execution configuration
├── tracking/                          # Progress tracking (JSON)
│   └── progress-tracker.json         # Live progress state
├── dashboard/                         # Plan viewer dashboard
│   ├── plan-viewer.html              # Modern glassmorphism UI
│   └── serve-dashboard.sh            # Launch script
├── phases/                            # Detailed phase definitions
│   ├── CX6-005-ac-traceability.yaml  # Layer 4: AC-ID traceability (4h)
│   ├── CX6-006-dashboard.yaml        # Layer 5: Dashboard (20h)
│   ├── CX6-007-migrate.yaml          # Layer 5: Migrate orchestrator (8h)
│   └── CX6-008-cli.yaml              # Layer 5: CLI entry point (4h)
├── evidence/                          # Test results, logs, artifacts
└── dependencies/                      # Dependency maps
```

---

## 🚀 Quick Start

### View Current Progress

```bash
# Option 1: View master index
cat plan-index.yaml

# Option 2: Launch interactive dashboard
cd dashboard/
./serve-dashboard.sh
```

### View Specific Phase

```bash
# View Layer 4 phase (current)
cat phases/CX6-005-ac-traceability.yaml

# View Layer 5 phases (pending)
cat phases/CX6-006-dashboard.yaml
cat phases/CX6-007-migrate.yaml
cat phases/CX6-008-cli.yaml
```

### Update Progress

```bash
# Progress tracker is automatically updated by orchestrators
# Manual updates (emergency only):
nano tracking/progress-tracker.json
```

---

## 🎯 Execution Phases

### ✅ **COMPLETED (Layers 1-3)** - 34 hours

| Layer | Phase | Status | Effort |
|-------|-------|--------|--------|
| **1** | SNOWBALL-001: Governance Foundation | ✅ COMPLETE | 4h |
| **2** | SNOWBALL-002: TDD-Master Orchestrator | ✅ COMPLETE | 16h |
| **3** | SNOWBALL-003: Gap-Fix Orchestrator | ✅ COMPLETE | 10h |
| **3** | SNOWBALL-004: SKULL Test Validation | ✅ COMPLETE | 4h |

### 🔄 **IN PROGRESS (Layer 4)** - 4 hours

| Phase | File | Status | Effort | Priority |
|-------|------|--------|--------|----------|
| **CX6-005** | `phases/CX6-005-ac-traceability.yaml` | 🔄 IN_PROGRESS | 4h | 🟢 HIGH |

**Objective:** AC-ID traceability system  
**Deliverables:** Test coverage report, AC-ID registry, gap analysis  
**Acceptance Criteria:** AC-TRACE-001, AC-TRACE-002, AC-TRACE-003

### ⏸️ **PENDING (Layer 5)** - 32 hours

| Phase | File | Status | Effort | Priority |
|-------|------|--------|--------|----------|
| **CX6-006** | `phases/CX6-006-dashboard.yaml` | ⏸️ PENDING | 20h | 🟡 MEDIUM |
| **CX6-007** | `phases/CX6-007-migrate.yaml` | ⏸️ PENDING | 8h | 🟢 HIGH |
| **CX6-008** | `phases/CX6-008-cli.yaml` | ⏸️ PENDING | 4h | 🟢 HIGH |

**Phase CX6-006: Plan Viewer Dashboard**
- Backend API (FastAPI + WebSocket) - 4-5h
- Frontend SPA (HTML5 + Tailwind) - 6-8h
- Styling & Polish (Glassmorphism) - 3-4h
- Testing & Documentation - 3-4h
- **AC:** AC-DASH-001 to AC-DASH-007

**Phase CX6-007: Migrate Orchestrator**
- On-demand plan migration to user repos
- Preserve folder structure, exclude git history
- **AC:** AC-MIGRATE-001 to AC-MIGRATE-006

**Phase CX6-008: CLI Entry Point**
- Universal `bin/cortex` CLI for cross-repo usage
- Auto-detect CORTEX path, route to src/main.py
- **AC:** AC-REPO-001, AC-REPO-002, AC-CLI-001 to AC-CLI-003

---

## 🎨 Dashboard Features

**Launch:** `./dashboard/serve-dashboard.sh`

**Features:**
- 📊 Real-time progress tracking (WebSocket updates <500ms)
- 🔄 Layer & phase visualization
- ✅ Acceptance criteria coverage metrics
- 📄 Audit log viewer with filtering
- 🎨 Glassmorphism dark theme
- 📱 Mobile-responsive design

**Performance SLAs:**
- Page load: <2s
- API response: <100ms
- WebSocket latency: <500ms
- Memory usage: <200MB

---

## 📊 Progress Tracking

### Current State

- **Layers Completed:** 3 of 5
- **Hours Completed:** 34 of 70 (48.6%)
- **Hours Remaining:** 36
- **Current Phase:** CX6-005 (AC-ID Traceability)
- **Current Layer:** 4 (AC-ID Traceability)

### Completion Criteria

**Layer 4 Complete When:**
- [ ] Test coverage report generated
- [ ] AC-ID registry populated
- [ ] Gap analysis documented
- [ ] All AC-TRACE-* criteria validated

**Layer 5 Complete When:**
- [ ] Dashboard functional (localhost:8000)
- [ ] Migrate orchestrator working
- [ ] CLI entry point deployed
- [ ] All AC-DASH-*, AC-MIGRATE-*, AC-CLI-* criteria validated

---

## 🔍 Definition of Ready (DoR)

Each phase has detailed DoR checklist. Example from CX6-006:

✅ **Ready to Start When:**
- DoR decisions finalized (Q17-Q21)
- progress-tracker.json structure defined
- Audit logs available (JSONL format)
- AC coverage data available
- Tailwind CSS CDN accessible
- FastAPI installed

---

## ✅ Definition of Done (DoD)

Each phase has detailed DoD checklist. Example from CX6-006:

**Required:**
- [ ] Dashboard auto-generated in plan/dashboard/ folder
- [ ] FastAPI server runs on localhost:8000
- [ ] WebSocket updates <500ms latency
- [ ] Audit log viewer with filtering
- [ ] Test coverage dashboard with AC-ID links
- [ ] Glassmorphism dark theme applied
- [ ] Mobile-responsive (tested on 3 screen sizes)
- [ ] Performance: page load <2s, memory <200MB
- [ ] Tests passing: test_plan_viewer.py
- [ ] Documentation: DASHBOARD-USER-GUIDE.md

**Optional:**
- [ ] --dashboard-launch flag
- [ ] --daemon flag
- [ ] Export to PDF
- [ ] Dark/light theme toggle

---

## 🔗 Dependencies

### Phase Dependencies

```
CX6-005 (AC Traceability)
    ↓ (unlocks coverage data)
CX6-006 (Dashboard) ← requires coverage metrics
    ↓ (dashboard shows migration status)
CX6-007 (Migrate) ← can display in dashboard
    ↓ (CLI invokes migrate)
CX6-008 (CLI) ← final integration layer
```

### External Dependencies

- **Python 3.10+**
- **FastAPI, uvicorn** (dashboard backend)
- **Tailwind CSS CDN** (dashboard frontend)
- **Audit logger** (existing infrastructure)
- **Progress tracker** (existing infrastructure)

---

## 📖 Canonical Sources

All phases built from these sources:

1. **Requirements:** `../requirements/CX6-requirements.yaml` (938 lines, 18 SR)
2. **Acceptance Criteria:** `../requirements/CX6-acceptance-criteria.yaml` (361 AC)
3. **Snowball Strategy:** `../analysis/snowball-strategy-20260110.yaml` (5 layers, 70h)

---

## 🛡️ Governance

**Protection Rules:**
- ✅ ALL code implementation via TDD-Master orchestrator (CORE-019)
- ✅ Tests fail before implementation (RED→GREEN→REFACTOR)
- ✅ No direct coding by GitHub Copilot (routes to orchestrators)
- ✅ Git isolation (CORTEX never commits to user repos)
- ✅ Planning isolation (plans don't implement, just define)

**Reference:** `cortex-brain/tier0/governance/core-rules.yaml`

---

## 🎯 Next Actions

### Current Focus: CX6-005 (Layer 4)

**Immediate Tasks:**
1. Scan all test files for AC-ID references
2. Load AC registry from requirements
3. Generate test coverage report
4. Identify gaps (untested AC)
5. Document findings in evidence/

**Estimated Time:** 4 hours

### After CX6-005: CX6-006 (Dashboard)

**Sub-phases:**
1. Backend API (4-5h) → FastAPI + WebSocket
2. Frontend SPA (6-8h) → HTML5 + Tailwind
3. Styling & Polish (3-4h) → Glassmorphism theme
4. Testing & Documentation (3-4h) → Tests + user guide

**Estimated Time:** 20 hours

---

## 📞 Support

**Questions about DoR/DoD?** Ask for clarification (zero ambiguity requirement)

**Progress tracker issues?** Check `tracking/progress-tracker.json` format

**Dashboard not working?** Verify `serve-dashboard.sh` has execute permissions

**Phase file unclear?** Each phase has detailed step-by-step implementation guide

---

## 📄 Version History

- **v1.0.0** (2026-01-11): Initial phased plan creation
  - 4 phase definitions (CX6-005 to 008)
  - Master plan index with progress tracking
  - Modern glassmorphism dashboard
  - Launch script and documentation

---

**Last Updated:** 2026-01-11  
**Plan Status:** IN PROGRESS (Layer 4 active)  
**Next Milestone:** Complete CX6-005, unlock Layer 5 (32h)

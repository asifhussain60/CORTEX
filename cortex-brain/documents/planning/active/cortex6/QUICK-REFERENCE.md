# 🎯 CORTEX 6.0 Execution Plan - Quick Reference

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    CORTEX 6.0 PHASED EXECUTION PLAN                      ║
║                         Zero Ambiguity Guarantee                         ║
╚═══════════════════════════════════════════════════════════════════════════╝

📊 PROGRESS: 48.6% Complete (34h/70h) | Current: Layer 4 | Phase: CX6-005
```

---

## 🚀 Quick Launch

```bash
# View dashboard (interactive)
cd execution/dashboard/
./serve-dashboard.sh

# View current phase details
cat execution/phases/CX6-005-ac-traceability.yaml

# View master plan
cat execution/plan-index.yaml

# View folder guide
cat 00-FOLDER-STRUCTURE-GUIDE.md
```

---

## 📁 Navigation Map

```
cortex6/
│
├── 00-FOLDER-STRUCTURE-GUIDE.md      ← START HERE
│
├── requirements/                      ← SOURCE OF TRUTH
│   ├── CX6-requirements.yaml         (938 lines, 18 SR)
│   └── CX6-acceptance-criteria.yaml  (361 AC)
│
├── execution/                         ← ACTIVE WORK
│   ├── README.md                     ← Comprehensive guide
│   ├── plan-index.yaml               ← Master execution index
│   ├── phases/                       ← 4 detailed phase definitions
│   │   ├── CX6-005-ac-traceability.yaml  (Layer 4, 4h)  🔄 IN_PROGRESS
│   │   ├── CX6-006-dashboard.yaml        (Layer 5, 20h) ⏸️ PENDING
│   │   ├── CX6-007-migrate.yaml          (Layer 5, 8h)  ⏸️ PENDING
│   │   └── CX6-008-cli.yaml              (Layer 5, 4h)  ⏸️ PENDING
│   └── dashboard/
│       ├── plan-viewer.html          ← Modern glassmorphism UI
│       └── serve-dashboard.sh        ← Launch script
│
├── analysis/                          ← STRATEGY DOCS
│   └── snowball-strategy-20260110.yaml  (5 layers, 70h total)
│
├── summaries/                         ← SESSION REPORTS
│   └── MANUAL-PLAN-CREATION-SESSION-20260111.md
│
└── artifacts/                         ← DELIVERABLES
```

---

## 🎯 Phase Quick Reference

### ✅ Layers 1-3: COMPLETE (34h)

| Phase | Name | Status | Effort |
|-------|------|--------|--------|
| SNOWBALL-001 | Governance Foundation | ✅ COMPLETE | 4h |
| SNOWBALL-002 | TDD-Master Orchestrator | ✅ COMPLETE | 16h |
| SNOWBALL-003 | Gap-Fix Orchestrator | ✅ COMPLETE | 10h |
| SNOWBALL-004 | SKULL Test Validation | ✅ COMPLETE | 4h |

### 🔄 Layer 4: IN PROGRESS (4h)

**CX6-005: AC-ID Traceability** 🔄
- **File:** `execution/phases/CX6-005-ac-traceability.yaml`
- **Effort:** 4h
- **AC:** AC-TRACE-001 to AC-TRACE-003
- **Objective:** Test coverage report, AC-ID registry, gap analysis

**Steps:**
1. Scan test files (1h)
2. Load AC registry (0.5h)
3. Generate coverage report (1h)
4. Write tests (1h)
5. Create gap report (0.5h)

### ⏸️ Layer 5: PENDING (32h)

**CX6-006: Plan Viewer Dashboard** ⏸️
- **File:** `execution/phases/CX6-006-dashboard.yaml`
- **Effort:** 20h (4 sub-phases)
- **AC:** AC-DASH-001 to AC-DASH-007
- **Objective:** Real-time dashboard with WebSocket updates

**Sub-phases:**
1. Backend API (FastAPI + WebSocket) - 4-5h
2. Frontend SPA (HTML5 + Tailwind) - 6-8h
3. Styling & Polish (Glassmorphism) - 3-4h
4. Testing & Documentation - 3-4h

---

**CX6-007: Migrate Orchestrator** ⏸️
- **File:** `execution/phases/CX6-007-migrate.yaml`
- **Effort:** 8h
- **AC:** AC-MIGRATE-001 to AC-MIGRATE-006
- **Objective:** On-demand plan migration to user repos

**Key Features:**
- Copy plan folder to user repo
- Preserve structure, exclude git history
- Merge mode (safe for iterative migrations)
- Dry-run preview

---

**CX6-008: CLI Entry Point** ⏸️
- **File:** `execution/phases/CX6-008-cli.yaml`
- **Effort:** 4h
- **AC:** AC-REPO-001, AC-REPO-002, AC-CLI-001 to AC-CLI-003
- **Objective:** Universal `bin/cortex` CLI

**Subcommands:**
- `cortex plan` → Planning Orchestrator
- `cortex migrate` → Migrate Orchestrator
- `cortex dashboard` → Launch dashboard
- `cortex maintenance` → Maintenance Orchestrator
- `cortex vacuum` → Vacuum Orchestrator

---

## 📊 Dashboard Preview

**Features:**
- 📊 Real-time progress (WebSocket <500ms)
- 🔄 Layer & phase visualization
- ✅ AC coverage metrics
- 📄 Audit log viewer
- 🎨 Glassmorphism dark theme
- 📱 Mobile-responsive

**Performance:**
- Page load: <2s
- API response: <100ms
- Memory: <200MB

---

## 🔍 DoR Decisions Reference

### CX6-006 (Dashboard)

| Q# | Question | Answer |
|----|----------|--------|
| Q17 | Generate once or regenerate? | **Generate once, WebSocket updates** |
| Q18 | Auto-launch browser? | **Manual by default, --launch flag optional** |
| Q19 | Foreground or daemon? | **Foreground, --daemon flag optional** |
| Q20 | Polling or WebSocket? | **WebSocket push (<100ms latency)** |
| Q21 | Integrated or standalone? | **Option A: Integrated** |

### CX6-007 (Migrate)

| Q# | Question | Answer |
|----|----------|--------|
| Q22 | Copy entire or selective? | **Entire folder (preserve structure)** |
| Q23 | Overwrite or merge? | **Merge (safe for user edits)** |
| Q24 | Track where? | **Both (CORTEX + user repo)** |

### CX6-008 (CLI)

| Q# | Question | Answer |
|----|----------|--------|
| Q25 | Hardcode or auto-detect path? | **Auto-detect (git config/env var)** |
| Q26 | Require CORTEX or bundle? | **Require CORTEX repo** |
| Q27 | Pass context or detect? | **Detect in Python (simpler)** |

---

## ✅ Governance Compliance

| Rule | Status |
|------|--------|
| TDD_MASTER_REQUIRED | ✅ All implementation via TDD-Master |
| NO_DIRECT_CODING | ✅ GitHub Copilot routes only |
| PLANNING_ISOLATION | ✅ Plans don't implement |
| GIT_ISOLATION | ✅ CORTEX never commits to user repos |
| HOLISTIC_DISCOVERY | ✅ Search before create |

**Reference:** `cortex-brain/tier0/governance/core-rules.yaml`

---

## 🎯 Next Action

**Execute CX6-005** (Layer 4, 4h)

```bash
# Via GitHub Copilot (recommended)
# Say: "continue cortex6"

# Or manually invoke
python3 -m src.main "execute CX6-005 AC-ID traceability"
```

**What Happens:**
1. Scan all test files for AC-ID references
2. Load AC registry from requirements
3. Generate test coverage report
4. Identify gaps (untested AC)
5. Document in evidence/
6. Update progress tracker

**Completion Unlocks:** Layer 5 (Dashboard, Migrate, CLI)

---

## 📞 Quick Help

| Issue | Solution |
|-------|----------|
| **Dashboard won't launch** | `chmod +x execution/dashboard/serve-dashboard.sh` |
| **Can't find phase file** | Check `execution/phases/SNOWBALL-00X-*.yaml` |
| **DoD unclear** | Each phase YAML has detailed DoD checklist |
| **Progress outdated** | Dashboard shows real-time via WebSocket (when API running) |
| **Need DoR context** | Each phase YAML has DoR decisions section |

---

## 📈 Success Metrics

- ✅ **Zero Ambiguity:** 11 DoR questions answered
- ✅ **Detailed Breakdown:** Step-by-step with time estimates
- ✅ **Clear DoD:** Required vs optional criteria
- ✅ **Risk Analysis:** Mitigation strategies defined
- ✅ **Evidence Tracking:** Artifact locations specified
- ✅ **Progress Tracking:** Real-time dashboard
- ✅ **Modern UI:** Glassmorphism dark theme

---

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  STATUS: ✅ READY FOR EXECUTION | NEXT: CX6-005 (Layer 4, 4h)       ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

**Last Updated:** 2026-01-11  
**Plan Version:** 1.0.0  
**Total Effort Remaining:** 36h (Layer 4 + Layer 5)

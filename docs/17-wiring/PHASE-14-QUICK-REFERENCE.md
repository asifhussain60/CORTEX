# Phase 14 Folder Structure - Quick Reference

**Created:** January 29, 2026  
**File Location:** `docs/17-wiring/FOLDER-STRUCTURE-PHASE-14.md` (20KB)

---

## 🏗️ Three-Folder CORTEX Architecture

```
CORTEX Project Root
│
├─ cortex/              (Orchestrators, Analysis, Rendering)
├─ cortex_brain/        (Governance, Knowledge, Tiers)  
└─ cortex-lens/ ⭐      (Dashboard SPA - Isolated & Safe)
```

---

## 🎯 Dashboard Placement Strategy

### **Why `/cortex-lens/` at Root Level?**

✅ **Complete Isolation**
- Dashboard code separated from orchestrators
- Accidental deletion risk eliminated (sibling folder, not nested)
- Clear visual separation in file explorer

✅ **User Safety**
- Users analyzing repositories can't accidentally delete CORTEX logic
- .gitignore protects generated dashboards in `.cortex/lens-dashboard/`
- Separate Docker container option for production

✅ **Developer Clarity**
- Clear intent: "lens" folder = LENS Dashboard system
- No confusion with core orchestrators in `cortex/`
- Self-documenting structure

---

## 📦 Complete Folder Map

### **CORTEX Repository (Phase 14+)**

```
cortex/                     ← CORE SYSTEM
├── visualization/          ← Renderers & Formatters (stays here)
│   ├── business_language_generator.py  (NEW)
│   ├── repository_detector.py          (NEW)
│   ├── dashboard_configuration.py      (NEW)
│   ├── renderers/
│   ├── formatters/
│   └── output_manager.py
├── orchestrators/
├── brain/
└── cli/
    └── commands/dashboard.py (routes to cortex-lens/)

cortex-lens/                ← LENS DASHBOARD ⭐ SEPARATED
├── app.py                  (FastAPI dashboard app)
├── orchestrator.py         (extends cortex/)
├── routes/                 (API endpoints)
├── static/                 (CSS, JS, vendor libs)
├── templates/              (HTML templates - 8 tabs)
├── services/               (business logic)
└── tests/

reports/
└── lens-dashboard/         (CORTEX self-analysis output)
    ├── index.html
    ├── data.json
    └── analysis/

.cortex/                    (local analysis cache)
├── lens-dashboard/         (local dashboard copy)
└── manifest.json
```

### **User Repository Analysis (Any Project)**

```
UserProject_A/
├── src/
├── tests/
├── requirements.txt
└── .cortex/                (gitignored)
    └── lens-dashboard/     ← Generated Dashboard ⭐
        ├── index.html      (main SPA)
        ├── data.json       (analysis cache)
        ├── analysis/       (JSON files)
        ├── visualizations/ (D3.js data)
        ├── diagrams/       (Mermaid source)
        └── exports/        (PNG/PDF outputs)

Cache (shared across repos):
~/.cortex/cache/
├── github.com/user/project-a/lens-dashboard/
├── github.com/user/project-b/lens-dashboard/
└── github.com/org/project-n/lens-dashboard/
```

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User runs: cortex lens analyze /path/to/repo               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ cortex/cli/commands/dashboard.py                            │
│ (routes command to cortex-lens/)                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ cortex-lens/orchestrator.py                                 │
│ (LensVisualizationOrchestrator)                             │
│ - imports from cortex/visualization/ (renderers, formatters)│
│ - imports from cortex/brain/ (analyzers, knowledge)         │
│ - orchestrates dashboard generation                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ cortex/visualization/*.py                                   │
│ - BusinessLanguageGenerator (NEW)                           │
│ - D3Renderer, MermaidRenderer, etc.                         │
│ - Produces visualization configs & data                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ cortex-lens/services/data_transformer.py                    │
│ Converts analyzer output → frontend data                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ cortex-lens/static/ + cortex-lens/templates/                │
│ Alpine.js SPA (15KB base)                                   │
│ + D3.js (250KB lazy) + Mermaid (850KB lazy)                 │
│ Renders interactive dashboard in browser                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Output saved to: .cortex/lens-dashboard/ (user repos)       │
│ or reports/lens-dashboard/ (CORTEX self-analysis)           │
│ Cached in: ~/.cortex/cache/<owner>/<repo>/                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Tab Structure

### **Any Repository (5 Universal Tabs)**

| Tab # | Name | Type | Tech |
|-------|------|------|------|
| 1 | Repository Overview | Universal | Generated (NEW) |
| 2 | Dependency Graph | Universal | D3.js |
| 3 | Class Diagrams | Universal | Mermaid |
| 4 | Temporal Analysis | Universal | D3.js |
| 5 | Impact Analysis | Universal | D3.js |

### **CORTEX Repository ONLY (8 Tabs: 5 + 3)**

| Tab # | Name | Type | Tech |
|-------|------|------|------|
| 1-5 | [Same as above] | Universal | — |
| 6 | Brain Architecture | CORTEX-only | Custom |
| 7 | Governance Compliance | CORTEX-only | Heatmap |
| 8 | Orchestrator Constellation | CORTEX-only | Network |

---

## 📊 Multi-Dimensional Overlays

All tabs support independent toggles:

🔴 **Security Overlay** - Vulnerabilities, insecure patterns, dependency risks  
⚡ **Performance Overlay** - Bottlenecks, complexity hotspots, optimization  
✅ **Compliance Overlay** - CORE rule violations, standards compliance  

---

## 🐳 Docker Implications

### **Updated Dockerfile**
```dockerfile
COPY cortex/ /app/cortex/
COPY cortex_brain/ /app/cortex_brain/
COPY cortex-lens/ /app/cortex-lens/       ← NEW Line
```

### **Optional Microservice Deployment**
```yaml
cortex:           # Main orchestration service
  ports: 8000
  
lens-dashboard:   # Optional separate container
  ports: 8001
  depends_on: [cortex]
```

---

## 🔐 Security & Isolation

### **User Protection Model**

```
User's Repository (.cortex/lens-dashboard/)
    ↓ [gitignored, never committed]
    
User's Cache (~/.cortex/cache/<owner>/<repo>/)
    ↓ [local only, user-controlled]
    
CORTEX System (cortex/, cortex_brain/, cortex-lens/)
    ↓ [version-controlled, protected]
    ✅ NO cross-contamination possible
```

### **Accidental Deletion Prevention**

- ❌ **Can't happen:** Users delete `.cortex/` = only loses cached analysis
- ❌ **Can't happen:** Users delete repos in `~/.cortex/cache/` = only loses cache
- ✅ **Protected:** Users can't delete `cortex/`, `cortex-lens/`, or `cortex_brain/`
  - They're sibling folders, not nested
  - Requires deliberate root-level deletion
  - Git protects on commits

---

## 📝 Implementation Checklist for Phase 14

### **Folder Creation**
- [ ] Create `/cortex-lens/` at root level
- [ ] Create subdirectories: routes/, static/, templates/, services/, middleware/, tests/

### **Code Moves/Updates**
- [ ] Move/create `cortex/visualization/business_language_generator.py` (NEW)
- [ ] Move/create `cortex/visualization/repository_detector.py` (NEW)
- [ ] Create `cortex-lens/app.py` with FastAPI routes
- [ ] Create `cortex-lens/orchestrator.py` (LensVisualizationOrchestrator)
- [ ] Update `cortex/cli/commands/dashboard.py` (routes to cortex-lens/)

### **Docker Updates**
- [ ] Update `Dockerfile` (add COPY for cortex-lens/)
- [ ] Update `docker-compose.yaml` (add cortex-lens service)
- [ ] Create optional `cortex-lens/Dockerfile` (for microservice)

### **CI/CD Updates**
- [ ] Update `.github/workflows/readiness-verification.yml` (check cortex-lens/)
- [ ] Update `.git/hooks/pre-commit` (scan cortex-lens/)

### **Documentation**
- [ ] Create `docs/11-lens-dashboard/README.md`
- [ ] Create `docs/11-lens-dashboard/ARCHITECTURE.md`
- [ ] Create `docs/11-lens-dashboard/API-REFERENCE.md`
- [ ] Create `docs/11-lens-dashboard/DEPLOYMENT.md` (this file)

### **Testing**
- [ ] Create `tests/test_lens_dashboard.py`
- [ ] Create `tests/test_lens_orchestrator.py`
- [ ] Update `tests/test_visualization_*.py` (if exists)

---

## 🎯 Summary

**Phase 14 introduces three distinct concerns at root level:**

```
cortex/         ← System orchestrators & analysis
cortex_brain/   ← Governance & knowledge
cortex-lens/    ← User-safe dashboard (isolated, separated) ⭐
```

**Generated dashboards live in:**

```
User's repo:     .cortex/lens-dashboard/
CORTEX itself:   reports/lens-dashboard/
Cache:           ~/.cortex/cache/<owner>/<repo>/
```

**Result:** Developers understand folder structure at a glance, users can't accidentally delete CORTEX logic, and dashboard scales across unlimited repositories.

---

**Full Documentation:** See `docs/17-wiring/FOLDER-STRUCTURE-PHASE-14.md` (20KB detailed breakdown)

**Authority:** CORTEX Development Team  
**Phase:** 14 (LENS Dashboard Implementation)  
**Status:** ✅ Architecture Approved - Ready for Implementation

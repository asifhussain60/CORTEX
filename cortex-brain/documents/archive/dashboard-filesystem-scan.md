# CORTEX Dashboard Filesystem Analysis

**Date:** December 4, 2025  
**Scan Type:** Complete repository filesystem scan  
**Purpose:** Identify all dashboard implementations

---

## 🔍 Dashboard Locations Found

### 1. **cortex-brain/dashboards/ui/** ⭐ CURRENT/ACTIVE
**Status:** ✅ KEEP - This is the active dashboard we just fixed
**Type:** Pure JavaScript/HTML dashboard (no Flask)
**Files:** 49 files committed in 35e1fc72
**Features:**
- ES6 modules
- 7 tabs (Overview, Tech Stack, Security, Architecture, Code Org, Team, Vendors)
- Mock data support
- Test suite (170 tests)
- Just fixed Security tab TypeError
- Fully functional

**Structure:**
```
ui/
├── index.html (541 lines)
├── app.js (313 lines)
├── data-loader.js
├── shared-utils.js
├── components/ (7 tab components)
├── tests/ (170 tests)
└── styles/
```

---

### 2. **src/dashboard/** ⚠️ OLD PYTHON BACKEND
**Status:** ⚠️  REVIEW - Python/Flask backend infrastructure
**Type:** Clean Architecture Python backend
**Purpose:** Backend data collection and processing
**Files:** ~50 Python files

**Structure:**
```
src/dashboard/
├── presentation/
│   ├── dashboard_renderer.py
│   └── static/
│       ├── js/ (6 JS files - old frontend)
│       └── css/ (7 CSS files - old frontend)
├── application/ (use cases, DTOs)
├── domain/ (entities, repositories)
├── infrastructure/ (JSON repos, cache)
├── data/ (collectors for security, team, etc.)
└── use_cases/
```

**Assessment:**
- This is the **Python backend** for data collection
- Has **OLD static frontend** files in `presentation/static/`
- The backend data collectors are STILL USED to generate JSON files
- The frontend static files are OBSOLETE (replaced by ui/)

---

### 3. **templates/dashboard/** ⚠️ OLD JINJA TEMPLATES
**Status:** ❌ DELETE - Old Flask/Jinja templates
**Type:** Server-side rendered templates
**Files:** 
- `templates/dashboard.html.j2` (900 lines)
- `templates/dashboard/views/*.html` (6 HTML partials)

**Assessment:**
- These are **Jinja2 templates** for Flask server-side rendering
- OBSOLETE - dashboard is now pure client-side
- Should be deleted (Flask removed)

---

### 4. **cortex-brain/dashboards/** (other files)
**Status:** ⚠️  MIXED - Data storage + old files
**Files:**
- `cortex/dashboard_data.json` ✅ Data file
- `noor-canvas/dashboard_data.json` ✅ Data file
- `mock/*.json` ✅ Mock data (15 files)
- `ksessions-health.html` ❌ Old standalone dashboard
- `app_registry.db` ✅ Database
- `schema/` ✅ Database schema

---

### 5. **cortex-brain/documents/onboarded-apps/noor-canvas/**
**Status:** ❌ DELETE - Old generated dashboard
**Files:**
- `dashboard.html` - Old standalone HTML dashboard

---

### 6. **cortex-brain/archives/flask-removal-2025-12-04/**
**Status:** ✅ KEEP - Already archived
**Files:** Old Flask templates (already archived, safe)

---

### 7. **static/** (root level)
**Status:** ⚠️  REVIEW - Old static files
**Files:**
- `static/css/dashboard.css`
- `static/js/dashboard_performance.js`

**Assessment:** These are OLD - the new dashboard has its own styles

---

## 📊 Summary

### Dashboards Found: 7 locations

| Location | Type | Status | Action |
|----------|------|--------|--------|
| `cortex-brain/dashboards/ui/` | Active JS dashboard | ✅ Current | **KEEP** |
| `src/dashboard/` | Python backend | ⚠️  Backend only | **KEEP BACKEND**, DELETE static files |
| `templates/dashboard/` | Jinja templates | ❌ Obsolete | **DELETE** |
| `cortex-brain/dashboards/ksessions-health.html` | Old HTML | ❌ Obsolete | **DELETE** |
| `cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html` | Old HTML | ❌ Obsolete | **DELETE** |
| `static/` (root) | Old static files | ❌ Obsolete | **DELETE** |
| `cortex-brain/archives/` | Archived | ✅ Archived | **KEEP** |

---

## 🎯 Recommended Actions

### ✅ KEEP (1 dashboard)
1. **cortex-brain/dashboards/ui/** - The active, working dashboard we just fixed

### 🔧 KEEP BUT CLEAN (1 location)
2. **src/dashboard/** - Keep Python backend (data collectors), DELETE static frontend:
   - DELETE: `src/dashboard/presentation/static/js/` (6 old JS files)
   - DELETE: `src/dashboard/presentation/static/css/` (7 old CSS files)
   - KEEP: All Python files (backend still generates JSON data)

### ❌ DELETE (5 locations)
3. **templates/dashboard/** - Delete entire directory (Flask removed)
4. **templates/dashboard.html.j2** - Delete Jinja template
5. **cortex-brain/dashboards/ksessions-health.html** - Delete old standalone
6. **cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html** - Delete old generated
7. **static/css/dashboard.css** - Delete old root-level static
8. **static/js/dashboard_performance.js** - Delete old root-level static

---

## 🚨 Critical Distinction

### Backend vs Frontend Confusion

**Python Backend (`src/dashboard/`):**
- ✅ **KEEP** - Still needed for data collection
- Collects security data, team metrics, architecture, etc.
- Generates JSON files consumed by frontend
- Clean Architecture implementation
- Use cases: `scan_security_vulnerabilities.py`, `analyze_quality_metrics.py`

**Old Frontend (`src/dashboard/presentation/static/`):**
- ❌ **DELETE** - Obsolete JavaScript/CSS files
- Was the OLD dashboard interface
- Replaced by `cortex-brain/dashboards/ui/`

**Current Frontend (`cortex-brain/dashboards/ui/`):**
- ✅ **KEEP** - The ONLY active dashboard
- Pure client-side (no Flask)
- ES6 modules, modern architecture
- Test suite, fixed TypeError

---

## 📋 Deletion Checklist

```bash
# Templates (Flask/Jinja - OBSOLETE)
rm -rf templates/dashboard/
rm templates/dashboard.html.j2

# Old static frontend in Python backend
rm -rf src/dashboard/presentation/static/js/
rm -rf src/dashboard/presentation/static/css/

# Old standalone dashboards
rm cortex-brain/dashboards/ksessions-health.html
rm cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html

# Old root-level static files
rm static/css/dashboard.css
rm static/js/dashboard_performance.js
```

---

## ✅ What Remains (CORRECT)

After cleanup:
```
CORTEX/
├── cortex-brain/dashboards/
│   ├── ui/ ⭐ ONLY ACTIVE DASHBOARD
│   ├── mock/ (data files)
│   ├── cortex/ (data files)
│   └── noor-canvas/ (data files)
├── src/dashboard/ ⭐ PYTHON BACKEND ONLY
│   ├── data/ (collectors)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── use_cases/
│   └── presentation/
│       ├── dashboard_renderer.py
│       └── templates/ (empty)
└── templates/
    └── interactive-dashboard-template.html (unrelated)
```

---

## 🎓 Key Insight

**One Dashboard, Two Parts:**
1. **Backend:** `src/dashboard/` - Python data collectors (KEEP)
2. **Frontend:** `cortex-brain/dashboards/ui/` - JavaScript interface (KEEP)

**Everything else:** Old implementations that should be deleted.

---

**Scan Complete:** 7 dashboard-related locations identified  
**Recommendation:** Keep 1 active dashboard, delete 5 obsolete locations, clean 1 backend  
**Safety:** All deletions are for obsolete/duplicate code only

# Dashboard Template Inventory & Relationship Analysis

**Author:** Asif Hussain | **Date:** December 9, 2025  
**Purpose:** Identify all dashboard templates and determine relationships

---

## 🎯 Analysis Scope

Investigated whether "adaptive dashboard template" exists and its relationship to the admin dashboard at `http://localhost:8080/ui/index.html?source=mock`.

---

## 📋 Findings

### ✅ Adaptive Dashboard Features FOUND

**Location:** `cortex-brain/dashboards/ui/adaptive-visibility.js`

**Purpose:** Intelligent UI adaptation based on project architecture

**Features:**
- Detects project type (API-only, SPA-only, Full-Stack, Database-only)
- Dynamically shows/hides dashboard sections
- Adapts to project architecture automatically

**Relationship to Admin Dashboard:** ✅ **DIRECTLY RELATED**
- This is a **JavaScript module** used BY the admin dashboard
- Not a separate template, but a **feature** of the admin dashboard
- Imported and used in `cortex-brain/dashboards/ui/app.js`

---

## 🗂️ Dashboard Template Inventory

### 1. **Admin Dashboard** (Production)
**Location:** `cortex-brain/dashboards/ui/index.html`  
**URL:** `http://localhost:8080/ui/index.html?source=mock`  
**Purpose:** Real-time CORTEX health monitoring  
**Features:**
- 10+ tabs (Executive, Overview, Tech Stack, Architecture, etc.)
- Adaptive visibility (via `adaptive-visibility.js`)
- Data loader with multiple sources (mock, cache, live repos)
- D3.js visualizations, Chart.js, Mermaid diagrams
- Comprehensive architecture exploration

**Related Files:**
```
cortex-brain/dashboards/ui/
├── index.html                    # Main HTML
├── app.js                        # Controller (imports adaptive-visibility.js)
├── adaptive-visibility.js        # ✅ Adaptive features
├── data-loader.js                # Data loading
├── components/                   # Tab renderers
├── styles/                       # CSS (layered)
└── services/                     # Backend API
```

---

### 2. **Interactive Dashboard Template** (Legacy/Utility)
**Location:** `templates/interactive-dashboard-template.html`  
**Purpose:** Generic D3.js dashboard generator template  
**Status:** ⚠️ Legacy - Used by `InteractiveDashboardGenerator`  
**Features:**
- 5-tab structure (Overview, Visualizations, Diagrams, Data, Recommendations)
- D3.js force graphs, Chart.js, Mermaid
- Template placeholders ({{TITLE}}, {{DATA}})

**Used By:**
- `src/utils/interactive_dashboard_generator.py`
- `src/operations/dashboard_generator.py`

**Relationship to Admin Dashboard:** ❌ **NOT RELATED**
- Different architecture (template-based vs. SPA)
- Different purpose (generic generator vs. CORTEX-specific)
- Not served by same server

---

### 3. **Onboarding Dashboard Template** (Jinja2)
**Location:** `templates/onboarding_dashboard.html.j2`  
**Purpose:** Project onboarding dashboards for user repos  
**Status:** ✅ Active (Clean Architecture implementation)  
**Features:**
- 5 tabs (Overview, Architecture, Quality, Security, Recommendations)
- Jinja2 templating
- Server-side rendering via Flask

**Used By:**
- `src/dashboard/presentation/dashboard_renderer.py`
- Clean Architecture dashboard system

**Related Files:**
```
templates/
├── onboarding_dashboard.html.j2  # Main template
└── partials/                      # Tab partials
    ├── overview_tab.html.j2
    ├── architecture_tab.html.j2
    ├── quality_tab.html.j2
    ├── security_tab.html.j2
    └── recommendations_tab.html.j2
```

**Relationship to Admin Dashboard:** ❌ **NOT RELATED**
- Serves user repositories (not CORTEX internal)
- Different server/route
- Different data model

---

### 4. **Dashboard Template (Jinja2 - Minimal)**
**Location:** `templates/dashboard.html.j2`  
**Purpose:** Minimal Jinja2 dashboard (possibly deprecated)  
**Status:** ⚠️ Uncertain - Multiple Python files reference it  
**Features:**
- Basic D3.js integration
- Template-driven rendering

**Used By:**
- `src/orchestrators/dashboard_generator.py`
- `src/utils/dashboard_template.py`
- `src/operations/modules/reporting/dashboard_utility.py`

**Relationship to Admin Dashboard:** ❌ **NOT RELATED**

---

### 5. **Python Dashboard Template System** (Abstraction Layer)
**Location:** `src/utils/dashboard_template.py`  
**Purpose:** Abstract template pattern for dashboard generation  
**Status:** ✅ Active (Production Ready v3.2.1)  
**Features:**
- Template registry pattern
- 3 built-in templates:
  - `HealthDashboardTemplate`
  - `PerformanceDashboardTemplate`
  - `GitActivityDashboardTemplate`

**Relationship to Admin Dashboard:** ❌ **NOT RELATED**
- Backend abstraction layer
- Not a visual template
- Used for programmatic dashboard generation

---

## 🔍 Files NOT Related to Admin Dashboard

### Templates
```
❌ templates/interactive-dashboard-template.html    (1,263 lines)
❌ templates/dashboard.html.j2                      (50 lines)
❌ templates/onboarding_dashboard.html.j2           (149 lines)
❌ templates/partials/*.html.j2                     (6 files)
```

### Python Generators
```
❌ src/utils/interactive_dashboard_generator.py
❌ src/operations/dashboard_generator.py
❌ src/orchestrators/dashboard_generator.py
❌ src/utils/dashboard_template.py
❌ src/operations/modules/reporting/dashboard_utility.py
❌ src/dashboard/presentation/dashboard_renderer.py
```

### Static Assets (Non-Admin)
```
❌ static/css/onboarding_dashboard.css
❌ static/js/onboarding_dashboard.js
❌ static/css/dashboard/*.css                       (3 files - old system)
❌ static/js/dashboard/*.js                         (3 files - old system)
```

---

## ✅ Files RELATED to Admin Dashboard

### Core Dashboard
```
✅ cortex-brain/dashboards/ui/index.html
✅ cortex-brain/dashboards/ui/app.js
✅ cortex-brain/dashboards/ui/adaptive-visibility.js   ⭐ ADAPTIVE FEATURES
✅ cortex-brain/dashboards/ui/data-loader.js
✅ cortex-brain/dashboards/ui/shared-utils.js
✅ cortex-brain/dashboards/ui/keyboard-navigation.js
✅ cortex-brain/dashboards/ui/performance-utils.js
✅ cortex-brain/dashboards/ui/progressive-loader.js
✅ cortex-brain/dashboards/ui/export-utils.js
```

### Components (Tab Renderers)
```
✅ cortex-brain/dashboards/ui/components/executive-tab.js
✅ cortex-brain/dashboards/ui/components/overview-tab-v3.js
✅ cortex-brain/dashboards/ui/components/architecture-tab.js
✅ cortex-brain/dashboards/ui/components/tech-stack-tab.js
✅ cortex-brain/dashboards/ui/components/security-tab.js
✅ cortex-brain/dashboards/ui/components/code-org-tab.js
✅ cortex-brain/dashboards/ui/components/vendors-tab.js
✅ cortex-brain/dashboards/ui/components/use-cases-tab.js
✅ cortex-brain/dashboards/ui/components/recommendations-tab.js
✅ cortex-brain/dashboards/ui/components/engineering-onboarding-tab.js
```

### Styles (Layered CSS)
```
✅ cortex-brain/dashboards/ui/styles/base/*.css
✅ cortex-brain/dashboards/ui/styles/layouts/*.css
✅ cortex-brain/dashboards/ui/styles/components/*.css
✅ cortex-brain/dashboards/ui/styles/utils/*.css
✅ cortex-brain/dashboards/ui/styles/main.css
✅ cortex-brain/dashboards/ui/styles/architecture-panels.css
✅ cortex-brain/dashboards/ui/styles/skeleton-loader.css
✅ cortex-brain/dashboards/ui/styles/overview-tab.css
✅ cortex-brain/dashboards/ui/styles/engineering-onboarding.css
```

### Data Services
```
✅ cortex-brain/dashboards/ui/services/*
✅ cortex-brain/dashboards/data/*
```

### Server (Dashboard Launcher)
```
✅ src/orchestrators/dashboard_launcher.py
```

---

## 🎯 Answer to User Question

### Q: Is there an adaptive dashboard template?

**A:** Yes and no.

**YES:** "Adaptive" features exist in `adaptive-visibility.js` - a JavaScript module that intelligently shows/hides dashboard sections based on project architecture.

**NO:** There is no separate "adaptive dashboard template" - it's a **feature** of the admin dashboard.

### Q: Is it related to the admin dashboard?

**A:** ✅ **YES - DIRECTLY RELATED**

`adaptive-visibility.js` is **part of** the admin dashboard at `http://localhost:8080/ui/index.html`. It's imported by `app.js` and provides intelligent UI adaptation.

---

## 📊 Template Architecture Map

```
CORTEX Dashboard Ecosystem
│
├── 🧠 Admin Dashboard (Production SPA)
│   ├── index.html
│   ├── app.js (controller)
│   ├── adaptive-visibility.js ⭐ (intelligent UI adaptation)
│   ├── data-loader.js
│   ├── components/ (10+ tabs)
│   └── styles/ (layered CSS)
│
├── 🎓 Onboarding Dashboard (User Repos)
│   ├── onboarding_dashboard.html.j2
│   ├── dashboard_renderer.py
│   └── partials/ (tab templates)
│
├── 🔧 Interactive Dashboard Generator (Utility)
│   ├── interactive-dashboard-template.html
│   ├── interactive_dashboard_generator.py
│   └── dashboard_generator.py
│
└── 🏗️ Dashboard Template System (Abstraction)
    ├── dashboard_template.py
    ├── HealthDashboardTemplate
    ├── PerformanceDashboardTemplate
    └── GitActivityDashboardTemplate
```

---

## 🚀 Recommendations

### For Admin Dashboard Development
**Use:** `cortex-brain/dashboards/ui/` files only  
**Adaptive Features:** Already integrated via `adaptive-visibility.js`

### For User Repository Dashboards
**Use:** `templates/onboarding_dashboard.html.j2` + Clean Architecture system

### For Generic Dashboard Generation
**Use:** `templates/interactive-dashboard-template.html` + `InteractiveDashboardGenerator`

### For Programmatic Dashboard Creation
**Use:** `src/utils/dashboard_template.py` (registry pattern)

---

## 📁 File Count Summary

| Category | Files | Related to Admin? |
|----------|-------|-------------------|
| Admin Dashboard Core | 50+ | ✅ YES |
| Onboarding System | 10+ | ❌ NO |
| Interactive Generator | 3 | ❌ NO |
| Template System | 5 | ❌ NO |
| Legacy Templates | 8 | ❌ NO |

**Total Non-Admin Files:** ~26 files

---

## ✅ Validation

- ✅ Adaptive features identified (`adaptive-visibility.js`)
- ✅ Relationship confirmed (part of admin dashboard)
- ✅ All dashboard templates inventoried
- ✅ Non-admin files categorized


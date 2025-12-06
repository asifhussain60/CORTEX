# Dashboard Data Collection - Complete Workflow Guide

## 🧠 CORTEX Enhanced Dashboard System
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Overview

This guide documents the **complete end-to-end workflow** for collecting repository data and displaying it in the enhanced dashboard. This process is now **fully automated and streamlined** for future collections.

---

## 🔄 Complete Workflow (3 Steps)

### Step 1: Collect Data from Repository

```powershell
# Create onboarding script (or use existing template)
python run_onboard_[project-name].py
```

**What it does:**
- Scans repository recursively
- Analyzes code quality, security, architecture
- Detects technology stack and dependencies
- Maps UI components (views, controllers, models)
- Generates 8 JSON files in `cortex-brain/dashboards/[project-name]/`

**Output Files:**
- `metadata.json` - Project info, scan timestamp
- `architecture.json` - Tiers, patterns, evidence
- `tech-stack.json` - Languages, frameworks, versions
- `code-organization.json` - Complexity heatmap (all files)
- `security.json` - OWASP Top 10, vulnerabilities
- `team-metrics.json` - Development metrics
- `health-data.json` - Overall health score
- `vendors.json` - Third-party dependencies

### Step 2: Register Data Source in Dashboard

```powershell
python register_dashboard_sources.py
```

**What it does:**
- Auto-discovers all data source directories
- Updates `data-loader.js` with new source paths
- Updates `index.html` dropdown with new options
- Increments cache-busting version number

**Benefits:**
- ✅ No manual file editing
- ✅ Alphabetically sorted sources
- ✅ Auto-detects application type from metadata
- ✅ Validates data before registration

### Step 3: View in Dashboard

```powershell
# Launch dashboard (if not already running)
cd cortex-brain/dashboards/ui
python -m http.server 8080
```

Then:
1. Open browser: http://localhost:8080/
2. **Hard refresh:** Ctrl+F5 (clears browser cache)
3. Select your project from dropdown
4. Dashboard loads automatically

---

## 📋 Real Example: Luum-Fresh Collection

### Commands Executed

```powershell
# Step 1: Collect data
cd C:\PROJECTS\CORTEX
python run_onboard_luum_fresh.py

# Step 2: Register source
python register_dashboard_sources.py

# Step 3: View dashboard
cd cortex-brain\dashboards\ui
python -m http.server 8080
# Browser: http://localhost:8080/ → Select "Luum Fresh (External)"
```

### Results Collected

| Metric | Value |
|--------|-------|
| **Scan Duration** | 539 seconds (8m 59s) |
| **Data Files** | 8 JSON files (3.01 MB) |
| **Architecture** | N-Tier (6 layers) |
| **UI Components** | 443 Razor views, 74+ controllers |
| **Technology** | .NET 5.0, 109 C# projects |
| **Code Files** | 10,391 analyzed |
| **Security Issues** | 346 (207 high, 139 medium) |
| **Top Complexity** | CommuteService.cs (14K lines, 892 complexity) |

---

## 🛠️ Troubleshooting

### Issue: "Unknown data source" Error

**Symptom:**
```
Error: Unknown data source: my-project
Available sources: mock, cortex, noor-canvas...
```

**Root Cause:** Browser cached old version of `data-loader.js`

**Fix:**
1. Run `python register_dashboard_sources.py` (increments version)
2. Hard refresh browser: **Ctrl+F5** (Windows) or **Cmd+Shift+R** (Mac)
3. Check browser console: Should see `[DataLoader v2.0.X]` with new version

### Issue: Data Not Showing in Dropdown

**Fix:**
1. Verify JSON files exist: `cortex-brain/dashboards/[project-name]/*.json`
2. Run registrar: `python register_dashboard_sources.py`
3. Check output - should see your project in discovered list
4. Hard refresh browser

### Issue: 404 Errors for JSON Files

**Symptom:**
```
GET /my-project/health-data.json HTTP/1.1 404
```

**Fix:**
1. Check directory structure:
   ```
   cortex-brain/dashboards/
   └── my-project/
       ├── health-data.json
       ├── architecture.json
       ├── tech-stack.json
       └── ... (other files)
   ```
2. Ensure HTTP server is running from `cortex-brain/dashboards/ui/`
3. File paths are relative to `ui/` directory

### Issue: Old Data Showing After Re-scan

**Fix:**
1. Check file timestamps: `ls -la cortex-brain/dashboards/[project]/`
2. Re-run collection script to regenerate files
3. Dashboard has 5-minute cache - wait or restart HTTP server
4. Hard refresh browser

---

## 🚀 Future-Proof Workflow

### For New Repository Collections

```powershell
# 1. Create onboarding script (copy template)
cp run_onboard_noor_canvas.py run_onboard_new_project.py

# 2. Edit paths in script
# Change: luum_fresh_path → new_project_path
# Change: project_name → "new-project"

# 3. Run collection
python run_onboard_new_project.py

# 4. Auto-register (one command!)
python register_dashboard_sources.py

# 5. View in dashboard
# Ctrl+F5 in browser, select from dropdown
```

### No Manual Edits Required! ✨

The `register_dashboard_sources.py` script automatically:
- Discovers new data directories
- Updates `data-loader.js` DATA_SOURCES
- Updates `index.html` dropdown options
- Increments cache-buster version
- Sorts alphabetically

---

## 📊 Data Collection Architecture

```
Repository Scanning
       ↓
┌──────────────────────┐
│ OnboardingOrchestrator│
│  - Quality Analysis  │
│  - Security Scan     │
│  - Architecture Map  │
│  - Tech Stack Detect │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ DashboardDataAdapter │
│  - Format Transform  │
│  - JSON Generation   │
└──────────┬───────────┘
           ↓
   dashboards/[project]/
   ├── metadata.json
   ├── architecture.json
   ├── tech-stack.json
   ├── code-organization.json
   ├── security.json
   ├── team-metrics.json
   ├── health-data.json
   └── vendors.json
           ↓
┌──────────────────────┐
│ Dashboard Registrar  │
│  - Auto-Discovery    │
│  - UI Updates        │
│  - Cache-Busting     │
└──────────┬───────────┘
           ↓
   Enhanced Dashboard
   - Architecture View
   - Security Analysis
   - Code Heatmap
   - Tech Stack Panel
   - UI Components
```

---

## 🔍 Key Files Reference

| File | Purpose | Auto-Updated? |
|------|---------|---------------|
| `run_onboard_[project].py` | Data collection script | Manual (template) |
| `cortex-brain/dashboards/[project]/*.json` | Dashboard data | ✅ By collector |
| `cortex-brain/dashboards/ui/data-loader.js` | Data source registry | ✅ By registrar |
| `cortex-brain/dashboards/ui/index.html` | Dropdown options | ✅ By registrar |
| `register_dashboard_sources.py` | Auto-registration tool | Manual run |

---

## ✅ Success Checklist

After running data collection, verify:

- [ ] 8 JSON files exist in `cortex-brain/dashboards/[project]/`
- [ ] All JSON files are valid (no syntax errors)
- [ ] `register_dashboard_sources.py` ran successfully
- [ ] `data-loader.js` DATA_SOURCES includes new project
- [ ] `index.html` dropdown includes new project
- [ ] Browser hard-refreshed (Ctrl+F5)
- [ ] Dashboard console shows new DataLoader version
- [ ] Project selectable in dropdown
- [ ] Data loads without 404 errors
- [ ] All dashboard tabs display data

---

## 📈 Performance Notes

**Scan Times (Approximate):**
- Small project (<1K files): 1-2 minutes
- Medium project (1K-5K files): 3-5 minutes
- Large project (5K-10K files): 8-12 minutes
- Enterprise (10K+ files): 15-30 minutes

**Optimization Tips:**
- Exclude build artifacts (already in `_should_scan_file()`)
- Skip binary files (`.dll`, `.exe`, `.so`)
- Use parallel collectors (already implemented)
- Run on SSD for faster file I/O

---

## 🎯 Summary

**Before This Fix:**
- Manual editing of 2 UI files per collection
- Browser cache issues
- No validation of data sources
- Inconsistent naming

**After This Fix:**
- ✅ One command: `python register_dashboard_sources.py`
- ✅ Auto-discovery of data sources
- ✅ Cache-busting built-in
- ✅ Alphabetically sorted
- ✅ Validation included
- ✅ Future collections streamlined

**Workflow Reduction:**
- Before: 5-6 manual steps
- After: **2 automated steps** (collect + register)

---

**Last Updated:** 2025-12-06  
**CORTEX Version:** 3.7.1  
**Dashboard Version:** 2.0.2

# Flask Cleanup Report - Phase 0

**Report ID:** flask-cleanup-2025-12-04  
**Created:** December 4, 2025  
**Status:** 🔄 IN PROGRESS  
**Checkpoint Tag:** flask-cleanup-checkpoint-20251204-*  
**Archive Location:** `cortex-brain/archives/flask-removal-2025-12-04/`

---

## 📋 Executive Summary

Comprehensive removal of Flask web framework from CORTEX repository as part of dashboard consolidation plan. Flask will be replaced with static HTML/JavaScript solution for universal health dashboard.

**Scope:** All Flask imports, routes, templates, tests, and dependencies  
**Safety:** All removed files archived for historical reference  
**Rollback:** Git checkpoint tag created before any changes

---

## 🔍 Discovery Phase Results

### Primary Flask Code

**File:** `src/dashboard/presentation/app.py` (211 lines)
- **Flask imports:** Flask, request, jsonify, render_template, redirect, url_for
- **Routes:**
  - `@app.route('/')` - Index (redirects to /dashboard/cortex)
  - `@app.route('/<app_id>')` - Legacy route (redirects to /dashboard/<app_id>)
  - `@app.route('/dashboard/<app_id>')` - Main dashboard route (line 95-142)
  - `@app.route('/dashboard/<app_id>/refresh', methods=['POST'])` - Refresh endpoint (line 143+)
- **Functions:**
  - `validate_app_id()` - Security validation for app identifiers
  - `create_app()` - Flask app factory with dependency injection
  - Route handlers using render_template, redirect, jsonify
- **Dependencies:**
  - JsonMultiAppRepository
  - SqliteAppRepository
  - UrlResolver
  - LoadDashboardUseCase
  - RefreshDashboardUseCase
- **Status:** ACTIVE - Main dashboard server

---

### Flask Test Files

**File:** `tests/dashboard/presentation/conftest.py`
- Line 52: `app.config['TESTING'] = True`
- Flask test client setup for pytest fixtures

**File:** `tests/dashboard/presentation/test_routes.py`
- Line 24: `app.config['TESTING'] = True`
- Tests for Flask route handlers

**File:** `tests/dashboard/presentation/test_dashboard_template_rendering.py`
- Line 28: `app.config['TESTING'] = True`
- Template rendering tests

**File:** `tests/dashboard/presentation/test_multi_app_routing.py`
- Line 7: `from flask import Flask`
- Multi-application routing tests

---

### Flask References in Other Files

**Tooling Crawler:** `src/crawlers/tooling_crawler.py`
- Line 691: Detection logic `if 'from flask import' in content or 'import flask' in content:`
- Purpose: Identify Flask usage in scanned repositories
- **Action:** Keep (used for repository analysis, not for running Flask)

**Response Template Manager:** `src/response_templates/response_template_manager.py`
- Lines 25, 33, 56, 73, 129: Method named `render_template()`
- **NOT Flask-related** - Internal template rendering for CORTEX responses
- **Action:** No changes needed (naming coincidence)

**Other Template Renderers:** Multiple files with `render_template()` method names
- `src/operations/modules/questions/context_renderer.py`
- `src/operations/modules/questions/template_engine_integration.py`
- `src/operations/modules/epmo/template_engine.py`
- `src/operations/modules/epm/setup_epm_utility.py`
- `src/tier1/planning_doc_sync.py`
- **Action:** No changes needed (internal methods, not Flask)

---

### Flask in Documentation Files

**All matches in documentation are:**
- Planning documents (this plan itself)
- Archived conversation captures
- Implementation guides referencing old Flask code
- Example code snippets in reports

**Action:** No changes needed (historical documentation)

---

### Flask Configuration

**requirements.txt:**
- ❌ NO Flask entry found
- **Status:** Already removed in previous cleanup

**Environment Variables:**
- ❌ NO FLASK_APP found
- ❌ NO FLASK_ENV found
- **Status:** No Flask environment configuration exists

**.flaskenv File:**
- ❌ NOT FOUND
- **Status:** No Flask-specific environment files

**app.config Usage:**
- Found only in test files (TESTING flag)
- Found in dashboard README (documentation)
- **Action:** Remove from test files during cleanup

---

## 📦 Files to Archive

### Code Files (src/dashboard/presentation/)
- [x] `app.py` (211 lines) → `archives/.../code/dashboard_presentation_app.py`

### Test Files (tests/dashboard/presentation/)
- [x] `conftest.py` → `archives/.../tests/conftest.py`
- [x] `test_routes.py` → `archives/.../tests/test_routes.py`
- [x] `test_dashboard_template_rendering.py` → `archives/.../tests/test_dashboard_template_rendering.py`
- [x] `test_multi_app_routing.py` → `archives/.../tests/test_multi_app_routing.py`

### Template Files (templates/)
- [ ] To be identified: `dashboard_clean.html` (referenced in app.py line 130)
- [ ] Any other Jinja2 templates in templates/ directory

### Configuration Files
- ❌ NONE FOUND (no Flask configs exist)

---

## 🚫 Files to Keep (False Positives)

**These files contain "flask" or "render_template" but are NOT Flask-related:**

1. **src/crawlers/tooling_crawler.py**
   - Contains Flask detection logic for repository scanning
   - Used to identify Flask usage in external repos
   - Keep unchanged

2. **src/response_templates/response_template_manager.py**
   - Method name coincidence: `render_template()` for CORTEX responses
   - No Flask import or dependency
   - Keep unchanged

3. **All src/operations/modules/ files with render_template()**
   - Internal CORTEX template rendering
   - No Flask dependency
   - Keep unchanged

4. **All documentation files**
   - Historical references in archives
   - Planning documents
   - Keep unchanged

---

## ✅ Removal Plan

### Phase 1: Archive (No Deletion Yet)
1. Copy `src/dashboard/presentation/app.py` → `archives/.../code/`
2. Copy all test files → `archives/.../tests/`
3. Copy template files → `archives/.../templates/`
4. Create archive manifest with checksums

### Phase 2: Remove Flask Code
1. Delete `src/dashboard/presentation/app.py`
2. Delete all Flask test files
3. Update requirements.txt (if Flask entry exists)
4. Remove Flask template files

### Phase 3: Verification
1. Search for remaining Flask references: `grep -ri "flask" --include="*.py" .`
2. Expected: Only documentation and tooling_crawler detection logic
3. Verify CORTEX still runs: `python -m src.main --help`
4. Run pytest to check for broken imports

### Phase 4: Commit
1. Stage all changes
2. Commit: "Phase 0: Remove Flask framework - Dashboard consolidation"
3. Push to CORTEX-3.0 branch

---

## 🎯 Impact Analysis

### Broken Functionality
- ❌ **Dashboard server will not start** (app.py removed)
- ❌ **Dashboard routes inaccessible** (no HTTP server)
- ❌ **Dashboard tests will fail** (Flask test client removed)

### Mitigation
- ✅ Dashboard server removal is intentional (Phase 0 goal)
- ✅ New static HTML dashboard will be built in Phase 1-3
- ✅ Tests will be rewritten for static file validation
- ✅ All removed code archived for reference

### Dependencies Still Working
- ✅ CORTEX CLI (`python -m src.main`)
- ✅ All orchestrators and agents
- ✅ Planning system
- ✅ TDD Mastery
- ✅ Brain tiers (SQLite databases)
- ✅ Repository crawlers
- ✅ Upgrade system

---

## 📊 Metrics

**Total Files to Remove:** 5
- 1 main application file
- 4 test files
- TBD template files

**Total Lines to Remove:** ~500+ lines (estimated)

**Archive Size:** TBD (will be calculated after archiving)

**Flask Import Locations Found:** 4 actual, 20+ false positives (documentation)

**Configuration Files:** 0 (no Flask configs found)

---

## 🔒 Rollback Plan

**If issues occur:**
1. Checkout git tag: `git checkout flask-cleanup-checkpoint-*`
2. Restore from archive: `cp -r cortex-brain/archives/flask-removal-2025-12-04/code/* src/dashboard/presentation/`
3. Restore tests: `cp -r cortex-brain/archives/flask-removal-2025-12-04/tests/* tests/dashboard/presentation/`
4. Verify: `python -m src.main --help` and `pytest tests/`

---

## ✅ Checkpoint Verification

- [x] Task 0.1: Git checkpoint tag created
- [x] Task 0.2: Flask imports identified (4 actual files)
- [x] Task 0.3: Flask route decorators found (4 routes in app.py)
- [x] Task 0.4: Flask template rendering found (render_template in app.py)
- [x] Task 0.5: Flask configuration searched (NONE found)
- [x] Task 0.6: requirements.txt checked (NO Flask entry)
- [x] Task 0.7: Flask test code identified (4 test files)
- [x] Task 0.8: Archive directory created
- [ ] Task 0.9-0.21: Pending (archiving and removal)

---

## 📅 Timeline

**Started:** December 4, 2025  
**Git Checkpoint:** Created  
**Discovery Phase:** Completed  
**Archive Phase:** In Progress  
**Removal Phase:** Not Started  
**Verification Phase:** Not Started  
**Completion:** Estimated 45 minutes remaining

---

## 🔄 Next Actions

1. Identify template files in `templates/` directory
2. Copy all files to archive with manifest
3. Remove Flask code from Python files
4. Verify no Flask references remain
5. Test CORTEX basic functionality
6. Commit changes

---

**Report Status:** 🔄 IN PROGRESS  
**Last Updated:** December 4, 2025  
**Phase Progress:** Discovery Complete, Archive In Progress

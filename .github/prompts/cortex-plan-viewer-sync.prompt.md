# CORTEX Plan Viewer Reality Check Fixer v2.0

**Purpose:** Synchronize plan-viewer.html dashboard with actual Phase 9 implementation status via dynamic data loading  
**Version:** 2.0.0 | **Author:** GitHub Copilot | **Date:** 2026-01-13

---

## 📋 Context Detection

**Entry Point:** `.github/prompts/cortex-plan-viewer.prompt.md`

**Invocation Pattern:**
```bash
python3 -m src.main "update plan viewer" --format markdown
# OR
python3 -m src.main "sync plan viewer dashboard" --format markdown
# OR
python3 -m src.main "fix plan viewer reality" --format markdown
```

**Scope:** CORTEX workspace only

---

## 🎯 Execution Strategy

This prompt orchestrates **3 sequential tasks** to sync the dashboard with Phase 9 reality:

### Task 1: Validate Current State
- Load `cortex-brain/tier1/tracking/progress-tracker.json`
- Load `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- Calculate Phase 9 actual status (18/29 ACs = 62%)
- Identify Phases 2-8 are COMPLETE (documentation lag)
- Flag blockers and verification gaps

### Task 2: Update Data Files (YAML/JSON)
- **Update:** `cortex-brain/cx6-plan/viewer/plan-viewer-data.json`
  - Correct Phase 9 completion to 62% (18/29 ACs)
  - Mark Phases 2-8 as 100% COMPLETE
  - Add blocker list (AC-TEMPLATE-005-008, AC-CHALLENGE-001-003, etc.)
  - Add verification gap warning (56% vs 80% gate)
  - Add evidence bundle stub warning (77/77 stubs)

- **Create:** `cortex-brain/cx6-plan/viewer/plan-viewer-metrics.json` (if needed)
  - Test statistics (1829 tests, 1372 passing, 94.4% pass rate)
  - Phase breakdown by ACs and tests
  - Evidence bundle status

- **Preserve:** All YAML files in `cortex-brain/tier1/` (read-only)

### Task 3: Update plan-viewer.html
- **REMOVE** all hardcoded phase data, metrics, statistics
- **ADD** dynamic data loading from `plan-viewer-data.json`
- **ADD** metrics calculation from `plan-viewer-metrics.json`
- Ensure all DOM elements are populated via JavaScript:
  - `#hero-meta-phase-number` ← from data.current_phase.number
  - `#hero-meta-completion` ← from data.current_phase.completion_percentage
  - `#hero-meta-tests` ← from metrics.total_tests
  - `.phases-grid` ← render from data.phases array
  - `.blockers-section` ← render from data.current_phase.blockers array
  - Progress bars and status badges ← dynamic calculation

---

## ⚡ Implementation Checklist

### Before You Start
- [ ] Verify `cortex-brain/tier1/tracking/progress-tracker.json` exists
- [ ] Verify `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` exists
- [ ] Verify `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` exists (or create)
- [ ] Verify `cortex-brain/cx6-plan/viewer/` directory exists

### Data File Updates
- [ ] `plan-viewer-data.json`: Update phases array with Phase 9 at 62%
- [ ] `plan-viewer-data.json`: Mark Phases 2-8 as 100% complete
- [ ] `plan-viewer-data.json`: Add blockers section with all 4 critical items
- [ ] `plan-viewer-data.json`: Add verification_gap warning (56% vs 80%)
- [ ] `plan-viewer-data.json`: Add evidence_bundle_status (77 stubs)
- [ ] `plan-viewer-metrics.json`: Create with test statistics and phase breakdown

### HTML Updates
- [ ] Remove all hardcoded phase cards (`.phase-card-compact`)
- [ ] Remove all hardcoded metric values in hero section
- [ ] Add `<script id="plan-viewer-data" type="application/json">` tag to load data
- [ ] Add JavaScript function `loadPlanViewerData()` to fetch JSON files
- [ ] Add JavaScript function `renderPhasesGrid()` to populate phases dynamically
- [ ] Add JavaScript function `renderBlockers()` to populate blockers section
- [ ] Add JavaScript function `renderMetrics()` to populate hero metrics
- [ ] Update `.phases-grid` to be empty (`<div class="phases-grid" id="phases-grid"></div>`)
- [ ] Call `loadPlanViewerData()` on document ready

### Validation
- [ ] HTML loads without errors in browser console
- [ ] All metrics render correctly from data files
- [ ] Phase 9 shows 62% completion (18/29 ACs)
- [ ] Phases 2-8 show 100% completion
- [ ] Blockers section displays all 4 items
- [ ] Verification gap warning is visible
- [ ] Evidence bundle stub warning is visible

---

## 📊 Expected Output

### plan-viewer-data.json Structure
```json
{
  "plan_metadata": {
    "version": "2.2.0-REALITY-SYNC",
    "last_updated": "2026-01-13T...",
    "reality_check": "Documentation 3 PHASES BEHIND - Actual Phase 9 (62%)",
    "verification_rate_current": "56% (below 80% gate)",
    "verification_rate_required": "80%"
  },
  "epic": { "id": "CORTEX-6.0", "status": "phase_9_in_progress", ... },
  "current_phase": {
    "number": 9,
    "name": "Infrastructure Maturity & Quality Gates",
    "completion_percentage": 62,
    "ac_ids_complete": 18,
    "ac_ids_total": 29,
    "blockers": [
      { "id": "AC-TEMPLATE-005-008", "title": "...", "severity": "HIGH", "reason": "..." },
      ...
    ]
  },
  "phases": [
    { "id": 1, "name": "Foundation", "completion_percentage": 100, "status": "complete", ... },
    { "id": 2, "name": "Orchestration Core", "completion_percentage": 100, "status": "complete", ... },
    ...
    { "id": 9, "name": "Infrastructure Maturity & Quality Gates", "completion_percentage": 62, "status": "in_progress", ... }
  ],
  "evidence_bundle_status": {
    "total": 77,
    "stubs": 77,
    "real": 0,
    "warning": "All evidence bundles are 3-line stubs (placeholder scaffold files, no real code)"
  }
}
```

### plan-viewer-metrics.json Structure
```json
{
  "last_updated": "2026-01-13T...",
  "test_statistics": {
    "total_collected": 1829,
    "total_passing": 1372,
    "total_failing": 457,
    "pass_rate_percentage": 94.4
  },
  "phase_breakdown": [
    { "phase": 1, "ac_total": 33, "ac_complete": 33, "tests": 120, "tests_passing": 120 },
    { "phase": 2, "ac_total": 23, "ac_complete": 23, "tests": 180, "tests_passing": 180 },
    ...
    { "phase": 9, "ac_total": 29, "ac_complete": 18, "tests": 156, "tests_passing": 150 }
  ]
}
```

### plan-viewer.html Structure
```html
<!-- HERO SECTION: Metrics loaded from data -->
<div id="hero-meta">
  <div class="hero-meta-item">
    <span class="hero-meta-label">Current Phase</span>
    <span class="hero-meta-value" id="hero-meta-phase">Phase 9</span>
  </div>
  <div class="hero-meta-item">
    <span class="hero-meta-label">Completion</span>
    <span class="hero-meta-value" id="hero-meta-completion">62%</span>
  </div>
  <div class="hero-meta-item">
    <span class="hero-meta-label">ACs Complete</span>
    <span class="hero-meta-value" id="hero-meta-acs">18/29</span>
  </div>
  <div class="hero-meta-item">
    <span class="hero-meta-label">Tests</span>
    <span class="hero-meta-value" id="hero-meta-tests">1829 (1372 passing)</span>
  </div>
</div>

<!-- PHASES GRID: Dynamically rendered -->
<div class="phases-grid" id="phases-grid">
  <!-- Rendered by JavaScript: renderPhasesGrid() -->
</div>

<!-- BLOCKERS SECTION: Dynamically rendered -->
<section class="section-container">
  <h2 class="section-title">Critical Blockers</h2>
  <div id="blockers-list">
    <!-- Rendered by JavaScript: renderBlockers() -->
  </div>
</section>

<!-- DATA LOADING SCRIPT -->
<script>
  async function loadPlanViewerData() {
    const data = await fetch('./plan-viewer-data.json').then(r => r.json());
    const metrics = await fetch('./plan-viewer-metrics.json').then(r => r.json());
    
    renderMetrics(data, metrics);
    renderPhasesGrid(data);
    renderBlockers(data);
  }
  
  document.addEventListener('DOMContentLoaded', loadPlanViewerData);
</script>
```

---

## 🔄 Data File Locations

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `cortex-brain/tier1/tracking/progress-tracker.json` | Source of truth for current phase | On every AC completion |
| `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` | AC registry with titles | On new AC definition |
| `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` | Dashboard dataset (phases, blockers) | On this sync operation |
| `cortex-brain/cx6-plan/viewer/plan-viewer-metrics.json` | Test stats, evidence bundles | On this sync operation |
| `cortex-brain/cx6-plan/viewer/plan-viewer.html` | Dashboard UI (no hardcoded data) | On this sync operation |

---

## ✅ Success Criteria

- [x] `plan-viewer-data.json` reflects Phase 9 at 62% (18/29 ACs)
- [x] All Phases 2-8 marked as 100% COMPLETE
- [x] All 4 blockers documented (AC-TEMPLATE, AC-CHALLENGE, VERIFICATION-GAP, EVIDENCE-BUNDLES)
- [x] Verification gap warning visible (56% vs 80%)
- [x] plan-viewer.html loads data dynamically (no hardcoded values)
- [x] Browser renders correctly with all metrics populated
- [x] Phase completion bar shows 62%
- [x] Blockers section shows all critical items
- [x] Evidence bundle stub warning displayed

---

## 🔀 Failure Modes & Recovery

| Failure | Cause | Recovery |
|---------|-------|----------|
| JSON parse error | Malformed JSON in data files | Validate JSON syntax with `python3 -m json.tool` |
| Missing data files | Files not created | Create from template in `cortex-brain/cx6-plan/viewer/` |
| Metrics don't render | JavaScript error | Check browser console for errors, verify fetch paths |
| Phase 9 still shows 0% | Old cached data | Clear browser cache, restart server |
| Phases 2-8 not marked complete | Data not synced | Re-run sync operation to update all files |

---

## 📝 Governance Rules Applied

- ✅ **CORE-002:** No summary files created (only data + logic)
- ✅ **CORE-005:** Portable file paths (no hardcoded /Users paths)
- ✅ **CORE-009:** Plan files in `cortex-brain/cx6-plan/` (not root)
- ✅ **CORE-017:** Governance enforcement (verification gap flagged)
- ✅ **Data Integrity:** All state loaded from authoritative sources (tracker, AC-INDEX)

---

## 🚀 Invocation Pattern

```bash
# Via MasterOrchestrator
python3 -m src.main "update plan viewer" --format markdown

# Or direct Python script
python3 cortex-brain/cx6-plan/viewer/sync-plan-viewer.py

# Or manual update
# 1. Edit plan-viewer-data.json with new phase 9 status
# 2. Edit plan-viewer.html to load data dynamically
# 3. Launch server: python3 -m http.server 8000
# 4. Open http://localhost:8000/cortex-brain/cx6-plan/viewer/plan-viewer.html
```

---

## 📚 References

- **CORTEX.prompt.md** - Master routing and governance rules
- **progress-tracker.json** - Current epic and phase status
- **AC-INDEX.yaml** - Acceptance criteria registry
- **chat01.md** - Reality check findings and blockers

---

**Version History:**
- 1.0.0: Initial plan-viewer sync orchestration
- 2.0.0: **Reality check fixer** - Sync Phases 2-8 complete, Phase 9 to 62%, add blockers & verification gap warnings

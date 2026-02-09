# Phase 14: Adaptive Dashboard - Before/After Comparison

**Updated:** 2026-01-29  
**Change:** Repository-aware adaptive tab rendering

---

## 🔄 What Changed

### Before (Original Plan)
- **8 tabs for ALL repositories**
- CORTEX-specific tabs shown to external repos
- Confusing UX: "What are orchestrators?" (for non-CORTEX users)

### After (Updated Plan)
- **5 universal tabs for external repos**
- **8 tabs for CORTEX repo only** (5 universal + 3 CORTEX-specific)
- Clean UX: External repos see only relevant tabs

---

## 📊 Tab Structure Comparison

### BEFORE: Fixed 8 Tabs (All Repos)

| Tab | Name | Problem |
|-----|------|---------|
| 1 | Repository Overview | ✅ Universal |
| 2 | Brain Architecture | ❌ CORTEX-specific shown to external |
| 3 | Dependency Graph | ✅ Universal |
| 4 | Class Diagrams | ✅ Universal |
| 5 | Temporal Analysis | ✅ Universal |
| 6 | Governance Compliance | ❌ CORTEX-specific shown to external |
| 7 | Orchestrator Constellation | ❌ CORTEX-specific shown to external |
| 8 | Impact Analysis | ✅ Universal |

**Issue:** External repos see CORTEX-specific tabs (Brain, Governance, Orchestrators) which don't apply.

---

### AFTER: Adaptive Tabs (Context-Aware)

#### External Repository Dashboard (5 tabs)

| Tab | Name | Applicability |
|-----|------|---------------|
| 1 | Repository Overview | ✅ Universal |
| 2 | Dependency Graph | ✅ Universal |
| 3 | Class Diagrams | ✅ Universal |
| 4 | Temporal Analysis | ✅ Universal |
| 5 | Impact Analysis | ✅ Universal |

**Result:** Clean, focused dashboard for any repository.

---

#### CORTEX Repository Dashboard (8 tabs)

| Tab | Name | Applicability |
|-----|------|---------------|
| 1 | Repository Overview | ✅ Universal |
| 2 | Dependency Graph | ✅ Universal |
| 3 | Class Diagrams | ✅ Universal |
| 4 | Temporal Analysis | ✅ Universal |
| 5 | Impact Analysis | ✅ Universal |
| 6 | Brain Architecture | 🧠 CORTEX-specific |
| 7 | Governance Compliance | 🧠 CORTEX-specific |
| 8 | Orchestrator Constellation | 🧠 CORTEX-specific |

**Result:** CORTEX repo gets full dashboard with internal architecture views.

---

## 🔍 Detection Logic

### How CORTEX Identifies Itself

```python
def is_cortex_repository(repo_path: Path) -> bool:
    """Check for CORTEX-specific markers."""
    markers = [
        repo_path / "cortex_brain",                              # Brain architecture
        repo_path / "cortex" / "orchestrators",                  # Orchestrator system
        repo_path / ".github" / "prompts" / "CORTEX.prompt.md",  # Master prompt
        repo_path / "cortex" / "wiring" / "specifications" / "wiring.yaml",  # Wiring config
    ]
    return any(marker.exists() for marker in markers)
```

**Logic:** If ANY marker exists → CORTEX repository (show 8 tabs)  
Otherwise → External repository (show 5 tabs)

---

## 📋 Implementation Changes

### New Components

1. **`repository_detector.py`** (Task 002a)
   - Detects CORTEX vs external repositories
   - Returns boolean flag

2. **`dashboard_configuration.py`** (Task 002b)
   - Context-aware tab selection
   - Returns 5 or 8 tabs based on repository type

3. **Updated Templates** (Task 013)
   - Conditional rendering in `dashboard_base.html`
   - Tabs 6-8 only shown if `is_cortex_repository == True`

### Updated CLI Behavior

```bash
# External repo: Auto-detects 5 tabs
$ cortex lens dashboard generate --repo=/path/to/flask-app
🔍 Analyzing repository...
📊 Repository type: External (5 tabs)
✅ Generated: /path/to/flask-app/.cortex/lens-dashboard/index.html

# CORTEX repo: Auto-detects 8 tabs
$ cortex lens dashboard generate
🔍 Analyzing repository...
📊 Repository type: CORTEX (8 tabs: 5 universal + 3 CORTEX-specific)
✅ Generated: reports/lens-dashboard/index.html
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **Better UX** | External repos don't see confusing CORTEX-specific concepts |
| **Scalability** | Easy to add more universal or CORTEX-specific tabs |
| **Clarity** | Clear separation between general and internal dashboards |
| **Adoption** | External users more likely to use dashboard (no confusion) |

---

## 🎯 User Experience Examples

### External Developer (Using Dashboard for Flask App)

**Before:**
```
Tabs: Overview | Brain | Deps | Classes | Timeline | Governance | Orchestrators | Impact
                  ❓      ✅      ✅         ✅           ❓            ❓             ✅
         "What is Brain Architecture?"
         "What are Orchestrators?"
         "Do I need Governance?"
```

**After:**
```
Tabs: Overview | Deps | Classes | Timeline | Impact
         ✅       ✅       ✅         ✅        ✅
      "This makes sense!"
```

---

### CORTEX Developer (Self-Analysis)

**Before:**
```
Tabs: Overview | Brain | Deps | Classes | Timeline | Governance | Orchestrators | Impact
         ✅       ✅      ✅      ✅         ✅           ✅            ✅             ✅
      "All tabs are relevant to CORTEX."
```

**After:**
```
Tabs: Overview | Deps | Classes | Timeline | Impact | Brain | Governance | Orchestrators
         ✅       ✅       ✅         ✅        ✅      ✅         ✅             ✅
      "Universal tabs first, then CORTEX-specific tabs. Great organization!"
```

---

## 📝 Updated Acceptance Criteria

### Added Criteria:

- [ ] Repository detection works (CORTEX vs external)
- [ ] External repos show 5 tabs only (no CORTEX-specific tabs)
- [ ] CORTEX repo shows 8 tabs (5 universal + 3 CORTEX-specific)
- [ ] CLI messages indicate tab count based on repository type
- [ ] Tab numbering adjusts automatically (no hardcoded Tab 6/7/8 for external)

### Updated Test Cases:

```python
def test_external_repo_shows_5_tabs():
    """External repository should show only universal tabs."""
    config = DashboardConfiguration()
    tabs = config.get_tabs_for_repo(Path("/path/to/flask-app"))
    assert len(tabs) == 5
    assert all(tab.is_universal for tab in tabs)

def test_cortex_repo_shows_8_tabs():
    """CORTEX repository should show universal + CORTEX-specific tabs."""
    config = DashboardConfiguration()
    tabs = config.get_tabs_for_repo(Path("/path/to/CORTEX"))
    assert len(tabs) == 8
    universal_tabs = [tab for tab in tabs if tab.is_universal]
    cortex_tabs = [tab for tab in tabs if tab.requires_cortex]
    assert len(universal_tabs) == 5
    assert len(cortex_tabs) == 3
```

---

## 🚀 Migration Notes

### For Existing Dashboards

If dashboards were already generated with 8 tabs for external repos:

```bash
# Regenerate dashboards with correct tab count
cortex lens dashboard clean --all
cortex lens dashboard generate --repo=/path/to/external/repo

# Output will now show:
# 📊 Repository type: External (5 tabs)
```

### For Documentation

Update all references to "8-tab dashboard" to:
- "5-tab universal dashboard (external repos)"
- "8-tab extended dashboard (CORTEX repo)"

---

## 📊 Summary

| Aspect | Before | After |
|--------|--------|-------|
| **External Repos** | 8 tabs (3 irrelevant) | 5 tabs (all relevant) ✅ |
| **CORTEX Repo** | 8 tabs | 8 tabs (organized 5+3) |
| **User Confusion** | High (CORTEX terms for external) | Low (clean separation) ✅ |
| **Maintenance** | Confusing tab numbering | Clear universal vs specific |

---

**Status:** ✅ UPDATED  
**Impact:** Improved UX, better scalability, clearer organization  
**Breaking Changes:** None (new feature, no existing dashboards)

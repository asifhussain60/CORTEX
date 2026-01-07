# CORTEX Documentation Prompt Redesign Analysis

**Date:** January 5, 2026  
**Author:** Asif Hussain  
**Version:** 2.0.0  
**Status:** ✅ Analysis Complete

---

## 📋 Executive Summary

Analyzed chat01.md conversation history to identify why cortex-docs.prompt.md v1.4.0 fails to prevent repetitive mistakes in HTML glassmorphism standardization. Root cause: **lack of state management and validation enforcement**. Redesigned prompt (v2.0) introduces state-first architecture with mandatory pre-flight checks, CSS class registry, and atomic operations.

---

## 🔍 Analysis of chat01.md Conversation

### Timeline of Events

1. **User Request:** "Apply subtle background to both panels from 7 color panel and apply glass subtle effect"
2. **Copilot Action:** Applied inline styles with glassmorphism to orchestrators/index.html ✅
3. **User Request:** "Apply this styling to ALL Level 1 views... use Python tools"
4. **Copilot Action:** Created CSS classes in variables.css + Python scripts to apply systematically ✅
5. **User Report:** "Effects disappeared from orchestrators/index.html"
6. **Copilot Action:** Checked git diff, found inline styles were pre-existing, restored file via `git checkout`
7. **User Request:** "Undo changes so I can see effects again... There should be NO inline styles"
8. **Copilot Action:** Restored file, explained inline styles existed before changes
9. **User Request:** "Check git history further. The correct one had 7 palette background colors on all background panels"
10. **Copilot Action:** Searched git commits, couldn't find version, applied classes again

### Key Observations

#### Observation #1: Inline Style Confusion
- **Issue:** CSS classes added to sections, but individual cards INSIDE sections had inline `style="background..."` 
- **Result:** Section backgrounds hidden by higher-specificity inline styles on children
- **Root Cause:** No tool to detect/remove existing inline styles before applying classes

#### Observation #2: State Loss Between Invocations
- **Issue:** User sees working version → Copilot can't find it in git history
- **Result:** Repeated searches, failed recovery
- **Root Cause:** No state file tracking which git tag had approved design

#### Observation #3: Pattern Library Not Consulted
- **Issue:** Changes applied without checking approved-panels.yaml
- **Result:** Potential deviation from approved patterns
- **Root Cause:** Pre-flight validation doesn't query library

#### Observation #4: No Rollback Strategy
- **Issue:** Changes made, user unhappy, manual `git checkout` required
- **Result:** Lost work, manual recovery
- **Root Cause:** No automatic git checkpoint before destructive operations

---

## 🚨 Identified Problems in v1.4.0 Prompt

### Problem #1: No State Tracking
**Evidence from chat:**
```
User: "the effects disappeared"
Copilot: [checks git diff, restores file]
User: "this is not it. Check git history further"
Copilot: [searches commits, can't find exact version]
```

**v1.4.0 Prompt Text:**
> "When user approves a page, **automatically record** approved patterns to library."

**Analysis:** Recording mechanism described but NO state file specified. No way to persist:
- Which git tag had approved design?
- Which CSS classes were applied?
- Which inline styles were removed?

**Fix in v2.0:** `html-standardization-state.json` tracks per-page state

---

### Problem #2: No Pre-Flight Validation
**Evidence from chat:**
```
Copilot: "I see the issue - the glass-panel classes are on sections, but individual cards have inline styles"
```

**v1.4.0 Prompt Text:**
> "Before any change, calculate complexity and choose the optimal approach"

**Analysis:** Complexity calculation exists, but NO validation for:
- ❌ Are inline styles present?
- ❌ Do CSS classes exist in registry?
- ❌ Is page already approved?
- ❌ Will this create duplicates?

**Fix in v2.0:** Mandatory `pre_flight_validation()` function blocks execution if checks fail

---

### Problem #3: CSS Registry Not Enforced
**Evidence from chat:**
```
Copilot: [Adds glass-panel-purple to HTML]
Copilot: [Creates .glass-panel-purple in CSS]
User: "effects disappeared"
[Analysis shows inline styles override CSS classes]
```

**v1.4.0 Prompt Text:**
> "Tool Inventory: `fix-inline-styles.ps1` - Convert inline styles to CSS classes"

**Analysis:** Tool exists but:
- ❌ Not invoked automatically before CSS class application
- ❌ No validation that HTML classes match CSS registry
- ❌ No enforcement of "CSS-only" mandate

**Fix in v2.0:** 
- CSS registry parser validates all classes exist
- Assertion checks block execution if inline styles present
- Atomic `remove-inline-styles.py` runs BEFORE `apply-css-classes.py`

---

### Problem #4: Approved Library Ignored
**Evidence from v1.4.0 prompt:**
```yaml
# Section: "Approved Panel Library (Auto-Update)"
# 100+ lines describing library structure
# BUT: No enforcement in execution workflow
```

**Analysis:** Library infrastructure exists but:
- ❌ Not queried in pre-flight validation
- ❌ Not used as template source
- ❌ No git tag linkage to working state

**Fix in v2.0:**
- Pre-flight queries library first
- Patterns include `git_tag` field linking to approved state
- User approval required before deviating from library patterns

---

### Problem #5: Non-Atomic Operations
**Evidence from chat:**
```python
# Script does multiple things at once:
def apply_glassmorphism_to_all_level1.py:
    find_sections()        # Discovery
    add_color_classes()    # Modification
    update_report()        # Documentation
    # If step 2 fails, step 1 already modified files!
```

**v1.4.0 Prompt Text:**
> "Tool-First Execution Philosophy"

**Analysis:** Tools exist but not atomic:
- ❌ Multiple changes per tool invocation
- ❌ No transaction-like rollback
- ❌ Hard to isolate which step failed

**Fix in v2.0:**
- Each tool does ONE thing
- Git checkpoint before each tool
- Rollback available for any step

---

## 🆕 v2.0 Design Improvements

### Improvement #1: State Persistence
```json
// html-standardization-state.json
{
  "pages": {
    "docs/orchestrators/index.html": {
      "git_checkpoint": "checkpoint-orchestrators-20260105-141500",
      "applied_patterns": ["glass-panel-purple", "glass-panel-emerald"],
      "inline_styles_removed": 13,
      "status": "approved",
      "approved_tag": "v5.0-glassmorphism-approved"
    }
  }
}
```

**Benefits:**
- ✅ Remember which git tag had approved design
- ✅ Track applied patterns between invocations
- ✅ Prevent re-application of same changes
- ✅ Fast recovery via approved_tag reference

---

### Improvement #2: Pre-Flight Validation
```python
def pre_flight_validation(target_page):
    # 1. Git checkpoint
    # 2. Query approved library
    # 3. Parse current HTML
    # 4. Check CSS registry
    # 5. Detect inline styles → BLOCK if found
    # 6. Detect duplicates → BLOCK if found
    # 7. Calculate complexity
```

**Benefits:**
- ✅ Catches issues BEFORE making changes
- ✅ Enforces "CSS-only" mandate
- ✅ Prevents duplicate creation
- ✅ Validates against registry

---

### Improvement #3: CSS Class Registry
```python
registry = load_css_class_registry("docs/assets/css/variables.css")
# Returns: {
#   "glass-panel-purple": {...properties...},
#   "glass-panel-emerald": {...properties...}
# }

html_classes = extract_glass_classes("docs/orchestrators/index.html")
missing = [cls for cls in html_classes if cls not in registry]

if missing:
    raise ValueError(f"Classes not in registry: {missing}")
```

**Benefits:**
- ✅ Single source of truth (CSS file)
- ✅ Validates HTML uses only registered classes
- ✅ Prevents inline style reversion

---

### Improvement #4: Enhanced Approved Library
```yaml
patterns:
  C50:
    git_tag: v5.0-glassmorphism-approved  # NEW
    inline_styles_allowed: false          # NEW
    css_classes_required:                 # NEW
      - glass-panel-purple
      - glass-card-display
    validation_script: validate-color-rotation.ps1
```

**Benefits:**
- ✅ Links pattern to git tag (easy recovery)
- ✅ Enforces inline style policy
- ✅ Lists required CSS classes for validation

---

### Improvement #5: Atomic Operations
```python
# BEFORE (v1.4.0)
apply_glassmorphism(page)  # Does 3 things

# AFTER (v2.0)
checkpoint = create_git_checkpoint(page)
remove_inline_styles_only(page)        # Atomic step 1
apply_css_classes_only(page, classes)  # Atomic step 2
validate_no_inline_styles(page)        # Atomic step 3
```

**Benefits:**
- ✅ Each tool does ONE thing
- ✅ Easy to rollback specific step
- ✅ Clear error isolation

---

## 📊 Comparison Matrix

| Feature | v1.4.0 | v2.0 |
|---------|--------|------|
| **State Tracking** | ❌ No | ✅ Yes (html-standardization-state.json) |
| **Pre-Flight Validation** | ⚠️ Partial (complexity only) | ✅ Full (7 checks) |
| **Inline Style Detection** | ⚠️ Mentioned in tools | ✅ Mandatory blocking check |
| **CSS Class Registry** | ❌ No | ✅ Yes (parsed from CSS files) |
| **Approved Library Query** | ❌ Not enforced | ✅ Mandatory in pre-flight |
| **Git Checkpoints** | ⚠️ Mentioned | ✅ Automatic before each tool |
| **Atomic Operations** | ❌ No | ✅ Yes (1 tool = 1 change) |
| **Rollback Strategy** | ⚠️ Manual `git checkout` | ✅ Automatic via checkpoints |
| **Duplicate Prevention** | ⚠️ Complexity score heuristic | ✅ Pre-flight validation blocks |
| **Color Scheme Preservation** | ❌ No tracking | ✅ State file remembers classes |

---

## 🎯 Root Cause Summary

### Why Inline Styles Keep Reappearing

**v1.4.0 Flow:**
```
User: "Apply glassmorphism"
  ↓
Copilot: [Reads prompt: "NO inline styles"]
  ↓
Copilot: [Adds CSS classes to HTML]
  ↓
Browser: [Renders inline styles (higher specificity)]
  ↓
User: "Effects disappeared"
```

**Problem:** No enforcement. Prompt SAYS "no inline styles" but doesn't CHECK or REMOVE them.

**v2.0 Fix:**
```
User: "Apply glassmorphism"
  ↓
Pre-flight: [Detects 13 inline styles]
  ↓
Pre-flight: ❌ BLOCK "Run remove-inline-styles.py first"
  ↓
[User runs removal tool]
  ↓
Pre-flight: ✅ PASS "No inline styles detected"
  ↓
[Apply CSS classes]
```

---

### Why Color Schemes Get Lost

**v1.4.0 Flow:**
```
Session 1:
  User: "Apply 7-color palette"
  Copilot: [Adds glass-panel-cyan, purple, etc.]
  User: ✅ Approved

Session 2 (new invocation, no memory):
  User: "Apply glassmorphism"
  Copilot: [No knowledge of Session 1]
  Copilot: [Searches git, can't find exact version]
  Copilot: [Applies different classes]
  User: "Colors changed"
```

**Problem:** No state persistence between Copilot invocations.

**v2.0 Fix:**
```
Session 2:
  User: "Apply glassmorphism"
  Pre-flight: [Loads html-standardization-state.json]
  Pre-flight: "Page approved on 2026-01-05"
  Pre-flight: "Git tag: v5.0-glassmorphism-approved"
  Pre-flight: "Applied patterns: glass-panel-cyan, purple, etc."
  Pre-flight: ⚠️ "Overwrite? [Y/n]"
  User: n
  Pre-flight: ✅ "Skipping (already approved)"
```

---

### Why Duplicates Get Created

**v1.4.0 Flow:**
```
Complexity Score > 50 → "DELETE_AND_REGENERATE"
BUT:
  - Tool adds new sections
  - Old sections not deleted
  - Result: 2x sections
```

**Problem:** "Delete-over-fix" rule not enforced by tools.

**v2.0 Fix:**
```
Pre-flight: [Detects complexity > 50]
Pre-flight: "Strategy: DELETE_AND_REGENERATE"
Pre-flight: [Creates git checkpoint]
Pre-flight: [Deletes HTML file]
Pre-flight: [Regenerates from approved template]
Pre-flight: [Validates single instance of each section]
```

---

## 🚀 Migration Plan

### Immediate Actions (This Session)
1. ✅ Create cortex-docs-v2.prompt.md (DONE)
2. ✅ Document analysis in this report (DONE)
3. ⏸️ Create `html-standardization-state.json` template
4. ⏸️ Enhance `approved-panels.yaml` with git tags
5. ⏸️ Build CSS registry parser script

### Short-Term (Next Session)
1. ⏸️ Run pre-flight validation on all HTML files
2. ⏸️ Document current inline style violations
3. ⏸️ Create git checkpoints for all pages
4. ⏸️ Run `remove-inline-styles.py` site-wide

### Long-Term (Next Week)
1. ⏸️ Update all Python tools to atomic operations
2. ⏸️ Add assertion checks to tools
3. ⏸️ Test v2.0 workflow on orchestrators/index.html
4. ⏸️ Deprecate v1.4.0 prompt

---

## ✅ Success Metrics

**v2.0 is successful when:**

1. ✅ **Zero inline styles** across all HTML files
   - Target: 0 instances (current: ~50+)
   - Validation: `assert_no_inline_styles()` passes

2. ✅ **Zero lost color schemes** in user sessions
   - Target: 100% preservation between invocations
   - Validation: State file tracks applied classes

3. ✅ **Zero duplicate sections** created
   - Target: 0 duplicates (current: occasional)
   - Validation: Pre-flight blocks duplicate creation

4. ✅ **100% approved library usage**
   - Target: All patterns from library (not ad-hoc)
   - Validation: Pre-flight queries library first

---

## 📚 References

- **Chat History:** `.github/copilot/copilot-chats/chat01.md`
- **Old Prompt:** `.github/prompts/cortex-docs.prompt.md` v1.4.0
- **New Prompt:** `.github/prompts/cortex-docs-v2.prompt.md` v2.0.0
- **Approved Library:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/standards/approved-panels.yaml`
- **Git Tag:** `v5.0-glassmorphism-approved` (orchestrators/index.html baseline)

---

**Report Generated:** 2026-01-05T15:00:00Z  
**Analysis Duration:** 45 minutes  
**Status:** ✅ Complete - Ready for Implementation

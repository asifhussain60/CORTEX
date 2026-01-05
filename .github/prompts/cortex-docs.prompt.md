# 🎨 CORTEX Documentation Designer v2.0 - State-Aware Glassmorphism System

**Version:** 2.0.0 | **Status:** 🚧 REDESIGN | **Type:** Stateful HTML Standardization  
**Author:** Asif Hussain | **Date:** January 5, 2026  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**State-aware orchestration system** for HTML glassmorphism standardization that **prevents duplicate content, preserves color schemes, and enforces CSS-only architecture** through mandatory pre-flight validation and state tracking.

**🆕 v2.0 Design Principles:**
1. **State-First**: Query approved panel library BEFORE any changes
2. **Validation-First**: Pre-flight checks BEFORE executing tools
3. **Atomic Operations**: Single source of truth per change
4. **Git Checkpoints**: Mandatory snapshots before destructive operations
5. **CSS Registry**: Centralized class tracking prevents inline style reversion

---

## 🚨 ROOT CAUSE ANALYSIS (from chat01.md)

### Issue #1: Duplicate Content Creation
**Symptom:** Python scripts add new sections WITHOUT deleting old ones  
**Root Cause:** No state validation before tool execution  
**Example from chat:**
- Script adds `glass-panel-purple` class to section
- Individual cards ALREADY have inline `style="background..."` 
- Result: Conflicting styles, section backgrounds hidden

**Fix:** Pre-flight HTML structure analysis

### Issue #2: Lost Color Schemes
**Symptom:** Color classes applied, then disappear in next iteration  
**Root Cause:** No tracking of applied classes between invocations  
**Example from chat:**
- User: "Apply 7-color palette"
- Copilot: Adds glass-panel classes ✅
- User: "Effects disappeared"  
- Copilot: Restores via git checkout (losing classes) ❌

**Fix:** State persistence + git tag references

### Issue #3: Inline Styles Reappearing
**Symptom:** CSS-only mandate ignored, inline styles keep coming back  
**Root Cause:** No enforcement mechanism, tools don't remove existing inline styles  
**Example from chat:**
- Prompt says "NO inline styles"
- HTML has 13 cards with `style="background: linear-gradient(...)"`
- Tools add CSS classes but DON'T remove inline attributes
- Browser shows inline styles (higher specificity)

**Fix:** Mandatory inline style removal + CSS class registry

### Issue #4: Approved Panel Library Ignored
**Symptom:** Changes applied without consulting approved patterns  
**Root Cause:** Library exists but not queried in workflow  
**Evidence:** `approved-panels.yaml` referenced in v1.4 but never used

**Fix:** Pre-flight library query + pattern matching

---

## 🛡️ MANDATORY PRE-FLIGHT CHECKLIST

**BEFORE ANY CHANGE, RUN THIS VALIDATION SEQUENCE:**

```python
def pre_flight_validation(target_page: str, change_type: str) -> ValidationResult:
    """
    MANDATORY validation before executing any tool or manual edit.
    Prevents duplicates, preserves state, enforces CSS-only architecture.
    """
    
    result = ValidationResult()
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Git Checkpoint (Rollback Safety)
    # ═══════════════════════════════════════════════════════════════
    checkpoint_tag = f"checkpoint-{target_page}-{timestamp()}"
    git_tag(checkpoint_tag, f"Pre-change snapshot: {change_type}")
    result.checkpoint = checkpoint_tag
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: Query Approved Panel Library
    # ═══════════════════════════════════════════════════════════════
    library = load_yaml("cortex-brain/documents/planning/active/html-glassmorphism-alignment/standards/approved-panels.yaml")
    
    if not library:
        result.add_warning("Approved panel library not found - proceeding without pattern validation")
    else:
        result.approved_patterns = library["patterns"]
        result.add_info(f"Loaded {len(library['patterns'])} approved patterns")
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: Parse Current HTML Structure
    # ═══════════════════════════════════════════════════════════════
    html_content = read_file(target_page)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract current state
    result.current_state = {
        "sections": len(soup.find_all('section')),
        "glass_classes": extract_glass_classes(soup),
        "inline_styles": find_inline_styles(soup),
        "css_imports": extract_css_imports(soup),
        "color_classes": find_color_classes(soup),  # glass-panel-cyan, etc.
    }
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 4: CSS Class Registry Check
    # ═══════════════════════════════════════════════════════════════
    registry = load_css_class_registry("docs/assets/css/variables.css")
    
    for color_class in result.current_state["color_classes"]:
        if color_class not in registry:
            result.add_error(f"Color class '{color_class}' NOT in CSS registry")
            result.add_fix(f"Add {color_class} to variables.css or remove from HTML")
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 5: Inline Style Detection (CRITICAL)
    # ═══════════════════════════════════════════════════════════════
    if result.current_state["inline_styles"]:
        result.add_error(f"Found {len(result.current_state['inline_styles'])} inline style attributes")
        result.add_fix("MUST remove ALL inline styles before applying CSS classes")
        result.inline_style_removal_required = True
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 6: Duplicate Detection
    # ═══════════════════════════════════════════════════════════════
    section_ids = [s.get('id') for s in soup.find_all('section') if s.get('id')]
    duplicate_ids = [id for id in section_ids if section_ids.count(id) > 1]
    
    if duplicate_ids:
        result.add_error(f"Duplicate section IDs found: {duplicate_ids}")
        result.add_fix("Delete duplicate sections before proceeding")
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 7: Complexity Score (Regeneration Threshold)
    # ═══════════════════════════════════════════════════════════════
    complexity = calculate_complexity(result.current_state)
    result.complexity_score = complexity
    
    if complexity > 50:
        result.strategy = "DELETE_AND_REGENERATE"
        result.add_warning("Complexity > 50 - Fresh regeneration recommended")
    elif complexity > 20:
        result.strategy = "SCRIPT_DRIVEN"
    else:
        result.strategy = "TARGETED_EDITS"
    
    return result
```

**ENFORCEMENT:**
- ❌ NO tool execution without pre-flight validation
- ❌ NO manual edits without state snapshot
- ❌ NO CSS class application if inline styles exist
- ✅ ALWAYS create git checkpoint before changes
- ✅ ALWAYS query approved panel library first
- ✅ ALWAYS remove inline styles before adding classes

---

## 🎨 CSS CLASS REGISTRY (Single Source of Truth)

**Location:** `docs/assets/css/variables.css`

**Mandatory Registry Structure:**

```css
/* ═══════════════════════════════════════════════════════════════
   GLASSMORPHISM 7-COLOR PANEL CLASSES
   Registry Version: 2.0
   Last Updated: 2026-01-05
   Approved Tag: v5.0-glassmorphism-approved
   ═══════════════════════════════════════════════════════════════ */

/* PRIMARY COLORS (Cyan) */
.glass-panel-cyan {
    background: linear-gradient(
        135deg, 
        rgba(0, 212, 255, 0.08) 0%, 
        rgba(0, 212, 255, 0.06) 50%, 
        rgba(26, 31, 58, 0.65) 100%
    );
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 212, 255, 0.15);
    box-shadow: 
        0 8px 32px 0 rgba(0, 212, 255, 0.12),
        inset 0 1px 2px 0 rgba(255, 255, 255, 0.05);
}

/* Repeat for: purple, teal, indigo, pink, emerald, amber */
/* ... */
```

**Registry Management:**

```python
def query_css_registry(css_file: str) -> Dict[str, CSSRule]:
    """
    Parse CSS file and extract all class definitions.
    Returns: {class_name: css_properties}
    """
    registry = {}
    content = read_file(css_file)
    
    # Parse CSS with regex (simple) or cssutils (robust)
    classes = re.findall(r'\.([a-z-]+)\s*{([^}]+)}', content, re.MULTILINE)
    
    for class_name, properties in classes:
        registry[class_name] = {
            "properties": properties.strip(),
            "file": css_file,
            "line": find_line_number(content, class_name)
        }
    
    return registry


def validate_html_against_registry(html_file: str, registry: Dict) -> List[str]:
    """
    Check if all CSS classes in HTML exist in registry.
    Returns: List of missing classes
    """
    soup = BeautifulSoup(read_file(html_file))
    html_classes = set()
    
    for element in soup.find_all(class_=True):
        html_classes.update(element['class'])
    
    missing = [cls for cls in html_classes if cls not in registry and cls.startswith('glass-')]
    
    return missing
```

**Usage in Workflow:**

```
BEFORE applying glass-panel-purple:
  1. Query registry: glass-panel-purple exists? ✅
  2. Check HTML: Any conflicting inline styles? ❌ (3 found)
  3. ACTION: Remove inline styles FIRST
  4. Then apply CSS class
```

---

## 🔄 STATE PERSISTENCE BETWEEN INVOCATIONS

**Problem:** Each Copilot invocation has no memory of previous changes

**Solution:** State tracking file

**Location:** `cortex-brain/cache/html-standardization-state.json`

**Structure:**

```json
{
  "version": "2.0",
  "last_updated": "2026-01-05T14:30:00Z",
  "pages": {
    "docs/orchestrators/index.html": {
      "last_modified": "2026-01-05T14:15:00Z",
      "git_checkpoint": "checkpoint-orchestrators-20260105-141500",
      "applied_patterns": ["glass-panel-purple", "glass-panel-emerald", "glass-panel-amber"],
      "inline_styles_removed": 13,
      "complexity_score": 28,
      "status": "approved",
      "approved_tag": "v5.0-glassmorphism-approved"
    }
  },
  "global_state": {
    "total_pages_processed": 9,
    "css_registry_version": "2.0",
    "approved_panel_library_version": "1.1.0"
  }
}
```

**Workflow Integration:**

```python
def load_page_state(page: str) -> Dict:
    """Load state from previous invocations"""
    state_file = "cortex-brain/cache/html-standardization-state.json"
    state = load_json(state_file)
    
    if page in state["pages"]:
        return state["pages"][page]
    else:
        return {"status": "new", "applied_patterns": []}


def save_page_state(page: str, new_state: Dict):
    """Persist state for next invocation"""
    state_file = "cortex-brain/cache/html-standardization-state.json"
    state = load_json(state_file)
    
    state["pages"][page] = new_state
    state["last_updated"] = timestamp()
    
    save_json(state, state_file)
```

**User Experience:**

```
User: "Apply glassmorphism to orchestrators page"

Intelligence Layer:
🔍 Checking previous state...
📄 Last modified: 2026-01-05 14:15:00
✅ Git checkpoint: checkpoint-orchestrators-20260105-141500
🎨 Applied patterns: glass-panel-purple, glass-panel-emerald, glass-panel-amber
⚠️ Status: APPROVED (do not modify without user confirmation)

❓ This page was already processed. Options:
  1. Restore from git checkpoint (undo changes)
  2. Apply additional patterns (incremental)
  3. Regenerate from scratch (delete + rebuild)

[User selects option]
```

---

## 🛠️ TOOL EXECUTION FRAMEWORK (Atomic Operations)

### Principle: One Tool = One Atomic Change

**BEFORE (Problematic):**
```python
# Script does multiple things, hard to rollback
def apply_glassmorphism(page):
    add_css_classes(page)        # Change 1
    remove_inline_styles(page)   # Change 2
    update_color_scheme(page)    # Change 3
    # If Change 3 fails, Changes 1 & 2 already applied!
```

**AFTER (Atomic):**
```python
# Each tool does ONE thing, easy to rollback
def remove_inline_styles_only(page):
    """ONLY removes inline style attributes, nothing else"""
    checkpoint = create_git_checkpoint(page)
    
    try:
        soup = parse_html(page)
        for element in soup.find_all(style=True):
            del element['style']
        
        save_html(page, soup)
        validate_no_inline_styles(page)  # Assertion
        
    except Exception as e:
        rollback_to_checkpoint(checkpoint)
        raise


def apply_css_classes_only(page, classes: List[str]):
    """ONLY adds CSS classes to sections, nothing else"""
    checkpoint = create_git_checkpoint(page)
    
    # Pre-condition check
    if has_inline_styles(page):
        raise ValueError("Inline styles detected - run remove_inline_styles_only first")
    
    try:
        soup = parse_html(page)
        sections = soup.find_all('section', class_='glass-card-display')
        
        for i, section in enumerate(sections):
            color_class = classes[i % len(classes)]
            section['class'].append(color_class)
        
        save_html(page, soup)
        validate_css_classes(page, classes)  # Assertion
        
    except Exception as e:
        rollback_to_checkpoint(checkpoint)
        raise
```

**Tool Inventory (Redesigned):**

| Tool | Purpose | Atomic | Pre-Conditions | Post-Conditions |
|------|---------|--------|----------------|-----------------|
| `remove-inline-styles.py` | Delete ALL `style=""` attributes | ✅ Yes | HTML file exists | Zero inline styles |
| `apply-css-classes.py` | Add glass-panel-{color} classes | ✅ Yes | No inline styles | Classes in HTML + CSS registry |
| `validate-color-scheme.py` | Check class registry consistency | ✅ Yes | HTML + CSS exist | Exit 0 = pass, 1 = fail |
| `create-git-checkpoint.py` | Tag current state | ✅ Yes | Git repo | Tag created |
| `rollback-to-checkpoint.py` | Restore from tag | ✅ Yes | Tag exists | State restored |

---

## 🔍 APPROVED PANEL LIBRARY INTEGRATION

**Problem:** Library exists but never consulted before changes

**Solution:** Mandatory library query in pre-flight

**Location:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/standards/approved-panels.yaml`

**Enhanced Structure:**

```yaml
---
version: 2.0
last_updated: 2026-01-05

# Registry of git tags for each approved pattern version
git_tags:
  v5.0-glassmorphism-approved: "2026-01-05T14:30:00Z"

patterns:
  C50:
    name: "Color Rotation (4-Color Tetris)"
    approved_date: 2026-01-04
    approved_page: orchestrators/index.html
    git_tag: v5.0-glassmorphism-approved
    version: 2
    
    # HTML template WITH classes (NO inline styles)
    html_template: |
      <section class="glass-card-display glass-panel-purple">
        <h2 class="section-title">
          <i class="fas fa-icon"></i>
          Section Title
        </h2>
        <div class="cards-grid-3col">
          <a href="#" class="glass-card-clickable card-variant-primary">
            <div class="card-header-inline">
              <i class="card-icon-primary fas fa-cube"></i>
              <h3>Card Title</h3>
            </div>
            <p>Card description</p>
          </a>
        </div>
      </section>
    
    # CSS classes required for this pattern
    css_classes_required:
      - glass-card-display
      - glass-panel-purple
      - glass-card-clickable
      - card-variant-primary
      - card-icon-primary
    
    # CSS file locations
    css_files:
      - docs/assets/css/variables.css  # glass-panel-purple
      - docs/assets/css/main.css       # glass-card-display
    
    # Validation script
    validation_script: validate-color-rotation.ps1
    
    # CRITICAL: Inline styles forbidden
    inline_styles_allowed: false
```

**Usage Workflow:**

```python
def apply_pattern_from_library(page: str, pattern_id: str):
    """
    Apply approved pattern from library instead of creating new HTML.
    Guarantees: No inline styles, all classes in CSS registry, git-revertible.
    """
    
    # 1. Load pattern from library
    library = load_approved_panel_library()
    pattern = library["patterns"].get(pattern_id)
    
    if not pattern:
        raise ValueError(f"Pattern {pattern_id} not found in approved library")
    
    # 2. Validate pattern is still approved
    if not pattern["inline_styles_allowed"] and has_inline_styles(pattern["html_template"]):
        raise ValueError(f"Pattern {pattern_id} violates inline style policy")
    
    # 3. Check CSS classes exist in registry
    registry = load_css_class_registry("docs/assets/css/variables.css")
    missing_classes = [cls for cls in pattern["css_classes_required"] if cls not in registry]
    
    if missing_classes:
        raise ValueError(f"CSS classes missing from registry: {missing_classes}")
    
    # 4. Create git checkpoint
    checkpoint = create_git_checkpoint(page, f"Before applying {pattern_id}")
    
    # 5. Apply pattern HTML (replace or append)
    try:
        soup = parse_html(page)
        # ... insert pattern["html_template"] ...
        save_html(page, soup)
        
        # 6. Validate result
        assert has_no_inline_styles(page), "Inline styles detected after pattern application"
        assert all_classes_in_registry(page, registry), "Unregistered classes found"
        
        # 7. Update state
        state = load_page_state(page)
        state["applied_patterns"].append(pattern_id)
        state["git_checkpoint"] = checkpoint
        save_page_state(page, state)
        
    except Exception as e:
        rollback_to_checkpoint(checkpoint)
        raise
```

---

## 📊 EXECUTION DECISION TREE (with State Awareness)

```
User Request: "Apply glassmorphism to X page"
    ↓
┌─────────────────────────────────────────┐
│ STEP 1: Load Previous State            │
│ - Check html-standardization-state.json│
│ - Load approved_panels.yaml             │
│ - Query CSS class registry              │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ STEP 2: Pre-Flight Validation          │
│ ✓ Git checkpoint created?               │
│ ✓ Inline styles present?                │
│ ✓ CSS classes in registry?              │
│ ✓ Duplicate sections?                   │
│ ✓ Complexity score?                     │
└─────────────────────────────────────────┘
    ↓
    Decision Point: Inline Styles Detected?
    ├─ YES → ❌ BLOCK
    │         "ERROR: 13 inline styles found"
    │         "Run: remove-inline-styles.py FIRST"
    │         "Cannot apply CSS classes over inline styles"
    │
    └─ NO → Continue
              ↓
    Decision Point: Page Previously Approved?
    ├─ YES → ⚠️ WARN
    │         "Page approved on 2026-01-05"
    │         "Git tag: v5.0-glassmorphism-approved"
    │         "Overwrite? [Y/n]"
    │         └─ User: n → STOP
    │         └─ User: y → Continue
    │
    └─ NO → Continue
              ↓
    Decision Point: Pattern in Library?
    ├─ YES → ✅ PREFERRED
    │         "Using approved pattern C50 from library"
    │         "Git tag: v5.0-glassmorphism-approved"
    │         Apply pattern["html_template"]
    │
    └─ NO → ⚠️ CREATE NEW
              "Pattern not in library - creating new"
              "Will add to library after approval"
              Generate HTML → User approval → Add to library
              ↓
    ┌─────────────────────────────────────────┐
    │ STEP 3: Execute Atomic Operations      │
    │ 1. create_git_checkpoint()              │
    │ 2. remove_inline_styles() [if needed]   │
    │ 3. apply_css_classes()                  │
    │ 4. validate_no_inline_styles()          │
    │ 5. validate_css_registry()              │
    └─────────────────────────────────────────┘
              ↓
    ┌─────────────────────────────────────────┐
    │ STEP 4: Update State & Commit          │
    │ - Save to html-standardization-state.json│
    │ - Update approved_panels.yaml            │
    │ - Git commit with tag reference          │
    └─────────────────────────────────────────┘
```

---

## 🚨 CRITICAL RULES (Zero Tolerance)

### Rule 1: No Inline Styles
```python
def assert_no_inline_styles(html_file: str):
    soup = BeautifulSoup(read_file(html_file))
    inline_count = len(soup.find_all(style=True))
    
    if inline_count > 0:
        raise AssertionError(f"CRITICAL: {inline_count} inline styles detected in {html_file}")
```

### Rule 2: CSS Registry Enforcement
```python
def assert_all_classes_registered(html_file: str, registry: Dict):
    html_classes = extract_glass_classes(html_file)
    missing = [cls for cls in html_classes if cls not in registry]
    
    if missing:
        raise AssertionError(f"CRITICAL: Unregistered classes: {missing}")
```

### Rule 3: Git Checkpoint Before Destructive Ops
```python
def require_git_checkpoint(operation: str):
    if not has_recent_checkpoint():
        raise AssertionError(f"CRITICAL: No git checkpoint before {operation}")
```

### Rule 4: State Persistence
```python
def require_state_tracking(page: str):
    state = load_page_state(page)
    if not state:
        raise AssertionError(f"CRITICAL: No state tracking for {page}")
```

---

## 📚 Migration Path from v1.4 to v2.0

### Phase 1: Create Infrastructure (1 hour)
1. ✅ Create `html-standardization-state.json`
2. ✅ Enhance `approved-panels.yaml` with git tags
3. ✅ Build CSS class registry parser
4. ✅ Create atomic tool wrappers

### Phase 2: Validate Existing Pages (2 hours)
1. ✅ Run pre-flight on all 100+ HTML files
2. ✅ Document inline style violations (expected: 50+)
3. ✅ Identify unregistered CSS classes
4. ✅ Create git checkpoints for all

### Phase 3: Clean Slate (3 hours)
1. ✅ Run `remove-inline-styles.py` on all pages
2. ✅ Validate CSS registry completeness
3. ✅ Commit: "refactor: Remove all inline styles (v2.0 migration)"

### Phase 4: Enable Enforcement (1 hour)
1. ✅ Add assertion checks to all tools
2. ✅ Update cortex-docs-v2.prompt.md in Copilot config
3. ✅ Test with orchestrators/index.html

---

## ✅ SUCCESS CRITERIA

**v2.0 is successful when:**

1. ✅ **Zero Duplicate Content**
   - Pre-flight validation blocks duplicate section creation
   - State tracking prevents re-application of patterns

2. ✅ **Zero Lost Color Schemes**
   - State persistence remembers applied classes
   - Git checkpoints enable rollback
   - Approved library preserves working patterns

3. ✅ **Zero Inline Styles**
   - Assertion checks block tool execution
   - remove-inline-styles.py runs BEFORE class application
   - CSS registry is single source of truth

4. ✅ **Approved Library Integration**
   - Pre-flight queries library first
   - New patterns added after user approval
   - Git tags link patterns to working state

---

**Last Updated:** 2026-01-05  
**Migration Status:** 🚧 Design Complete, Implementation Pending  
**Replaces:** cortex-docs.prompt.md v1.4.0

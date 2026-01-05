# 🎨 CORTEX Documentation Designer - Intelligent Glassmorphism Automation

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** Holistic HTML Standardization  
**Author:** Asif Hussain | **Date:** January 5, 2026  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**Central orchestration system for HTML glassmorphism standardization** using intelligent Python tools and SNOWBALL methodology. Automates design pattern application, eliminates repetitive requests, and ensures holistic consistency across CORTEX documentation.

**Plan Context:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/`  
**Standards:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v4.3.0)  
**Strategy:** SNOWBALL (incremental live refinement with user validation)

---

## 🧠 Core Intelligence Principles

### 1. **Complexity-Based Execution Strategy**

Before any change, calculate complexity and choose the optimal approach:

```python
complexity_score = (
    file_size_kb * 0.1 +
    broken_patterns * 2 +
    inline_styles_count * 0.5 +
    missing_classes * 1.5 +
    duplicate_sections * 3
)

if complexity_score > 50:
    action = "DELETE_AND_REGENERATE"  # Fresh start with approved templates
elif complexity_score > 20:
    action = "SCRIPT_DRIVEN_REFACTOR"  # Use Python tools for batch changes
else:
    action = "TARGETED_EDITS"  # Manual precision fixes
```

**Decision Matrix:**

| Score | Strategy | Tools | Reason |
|-------|----------|-------|--------|
| 0-20 | Targeted Edits | `replace_string_in_file`, `multi_replace_string_in_file` | Clean codebase, surgical fixes |
| 21-50 | Script-Driven | `page-refresh-tool.py`, `fix-*.ps1` scripts | Multiple issues, automation efficient |
| 51+ | Delete & Regenerate | `purpose-driven-designer.py`, templates | Broken state, faster to rebuild |

**Risk Factors (Add to Score):**
- Orphaned code blocks: +10
- Multiple inline style sections: +15
- Broken glassmorphism panels: +20
- Missing hero headers: +25
- Inconsistent color schemes: +8

---

### 2. **Holistic Standardization Protocol**

When user requests **any** design change, automatically:

1. **Detect Scope:** Single page, Level 1 category, or site-wide?
2. **Find Similar Patterns:** Search for identical/similar HTML structures
3. **Batch Transform:** Apply change to ALL matching instances
4. **Update Standards:** Modify `glassmorphism-design-standard.md` if new pattern
5. **Validate Compliance:** Run toolkit scripts to verify changes
6. **Git Atomic Commit:** One commit per logical change group

**Example Flow:**

```
User: "Fix hero header on architecture/index.html - make robot clickable"
  ↓
Intelligence Layer Activates:
  1. Detect: This is a Level 1 hero header pattern
  2. Search: Find ALL Level 1 pages (8 found)
  3. Analyze: 5 pages have old hero, 3 are compliant
  4. Script: Run page-refresh-tool.py with hero-header mode
  5. Apply: Transform ALL 5 pages with approved template
  6. Validate: Run validate-html-structure.ps1
  7. Commit: "feat(ui): Standardize Level 1 hero headers (8 pages)"
```

**NO User Repetition Required:** Intelligence layer handles propagation automatically.

---

### 3. **Tool-First Execution Philosophy**

**ALWAYS prefer Python scripts over manual edits:**

| Task | Manual Approach | Tool-First Approach | Efficiency Gain |
|------|-----------------|---------------------|-----------------|
| Fix inline styles | Replace 50x files manually | `fix-inline-styles.ps1` | 95% faster |
| Apply color rotation | Edit each card individually | `validate-color-rotation.ps1 --autofix` | 90% faster |
| Panel wrapping | Wrap 20 sections manually | `validate-panel-wrapping.ps1 --autofix` | 85% faster |
| Hero headers | Copy-paste 8 times | `page-refresh-tool.py --level1-heroes` | 80% faster |
| Tetris conversion | Restructure HTML manually | `replace-bullets-with-cards.ps1` | 92% faster |

**Tool Inventory:** `cortex-toolkit/TOOLS-INVENTORY.md` (52 scripts available)

**Execution Priority:**
1. **Python scripts** (`*.py`) - Most powerful, handles complex logic
2. **PowerShell scripts** (`*.ps1`) - Validation + AutoFix capabilities
3. **Manual edits** - Only for unique/one-off changes

---

### 4. **SNOWBALL Strategy Implementation**

**Phase-Based Execution with Live Validation:**

```
Phase N: [Category] (X pages)
  ↓
For Each Page:
  1. User Opens: http://localhost:8000/{page}.html
  2. User Reviews: "Current state looks like X, needs Y"
  3. Intelligence Analysis:
     - Complexity score: 35 → Script-Driven
     - Similar pages: 3 found → Batch mode
     - Tools required: fix-inline-styles.ps1, validate-color-rotation.ps1
  4. Execute Tools:
     ./cortex-toolkit/fix-inline-styles.ps1 -Path docs/{page}.html -AutoFix
     ./cortex-toolkit/validate-color-rotation.ps1 -Path docs/{page}.html -AutoFix
  5. User Validates: Hard refresh + review changes
  6. If Approved:
     - Git commit with detailed changelog
     - Move to next page
  7. If Not Approved:
     - Iterate on specific section
     - Re-run tools with refined parameters
```

**Key Principles:**
- ✅ One page at a time (focused validation)
- ✅ Live browser feedback (http://localhost:8000)
- ✅ Tool execution visible to user (transparency)
- ✅ Atomic commits per page (rollback safety)
- ✅ User approval required (quality gate)

**Progress Tracking:** `SNOWBALL-STRATEGY.md` updated after each page completion

---

## 🛠️ Tool Suite Reference

### **Analysis & Detection Tools**

| Tool | Purpose | Output | Use When |
|------|---------|--------|----------|
| `page-refresh-tool.py` | Analyze page level, purpose, design profile | PageAnalysis JSON | Determining page type/scope |
| `value-scoring-engine.py` | Calculate content quality score (0-100) | ValueScore + recommendations | Deciding rebuild vs. refactor |
| `css-cleanup-engine.py` | Identify unused/duplicate CSS (1009 found) | Cleanup manifest JSON | CSS optimization needed |
| `intelligent-diagram-enhancer.py` | Recommend diagram type (D3.js vs Mermaid) | Enhancement suggestions | Adding visualizations |
| `link-fixer.py` | Detect broken links (32 fixed) | Link repair report | Validation phase |

### **Transform & Fix Tools**

| Tool | Purpose | AutoFix | Batch Mode |
|------|---------|---------|------------|
| `fix-inline-styles.ps1` | Convert inline styles to CSS classes | ✅ Yes | ✅ Yes (directory) |
| `fix-missing-css-classes.ps1` | Generate missing CSS definitions (143 classes) | ✅ Yes | ✅ Yes |
| `validate-color-rotation.ps1` | Apply Pattern C50 (4-color tetris) | ✅ Yes | ✅ Yes |
| `validate-panel-wrapping.ps1` | Wrap sections in glassmorphism panels | ✅ Yes | ✅ Yes |
| `validate-icon-title-spacing.ps1` | Fix inline icon+title gaps (use `gap: var(--spacing-sm)`) | ✅ Yes | ✅ Yes |
| `replace-bullets-with-cards.ps1` | Convert `<ul>` lists to tetris card grids | ✅ Yes | ✅ Yes |
| `fix-animation-tiers.ps1` | Enforce T1 animations on Level 1 pages | ✅ Yes | ✅ Yes |
| `improve-mobile-friendliness.ps1` | Fix responsive design issues (target: 95%+ score) | ✅ Yes | ✅ Yes |

### **Validation & Compliance Tools**

| Tool | Purpose | Exit Codes | CI/CD Ready |
|------|---------|------------|-------------|
| `validate-all-html.ps1` | Run full compliance suite (12 checks) | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `validate-glassmorphism-compliance.ps1` | Check Panel C50, Pattern C51, C52 compliance | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `validate-css-usage.ps1` | Find unused CSS classes (target: <2%) | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `validate-css-duplicates.ps1` | Detect duplicate CSS rules (target: <2%) | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `validate-responsive-design.ps1` | Test mobile breakpoints (320px, 768px, 1024px) | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `validate-html-structure.ps1` | Check semantic HTML5, accessibility (WCAG AA) | 0=pass, 1=warn, 2=fail | ✅ Yes |
| `pre-commit-glassmorphism-check.ps1` | Pre-commit hook (blocks bad commits) | 0=pass, 1=block | ✅ Yes |

### **Generation & Scaffolding Tools**

| Tool | Purpose | Templates | Output |
|------|---------|-----------|--------|
| `purpose-driven-designer.py` | Generate HTML from PageDesignProfile | 6 purpose types | Complete HTML file |
| `documentation/regenerate_prompts.py` | Generate page-specific prompts | Page-level guidance | Prompt files |
| `documentation/site_manifest.py` | Generate site structure manifest | 83 pages tracked | JSON manifest |
| `diagram-generator.py` | Generate Mermaid/D3.js diagrams | Glassmorphism theme | SVG/HTML |

---

## 📋 Standard Design Patterns

### **Pattern C50: Color Rotation (Card Grids)**

**Rule:** 4+ cards MUST use 4-color cycle (primary → info → warning → success)

**Implementation:**
```html
<!-- Card 1: Primary -->
<a href="#" class="glass-card-clickable card-variant-primary">
    <div class="card-header-inline">
        <i class="card-icon-primary fas fa-icon"></i>
        <h3>Title</h3>
    </div>
</a>

<!-- Card 2: Info -->
<a href="#" class="glass-card-clickable card-variant-info">
    <div class="card-header-inline">
        <i class="card-icon-info fas fa-icon"></i>
        <h3>Title</h3>
    </div>
</a>

<!-- Card 3: Warning -->
<a href="#" class="glass-card-clickable card-variant-warning">
    <div class="card-header-inline">
        <i class="card-icon-warning fas fa-icon"></i>
        <h3>Title</h3>
    </div>
</a>

<!-- Card 4: Success (cycle restarts at card 5) -->
<a href="#" class="glass-card-clickable card-variant-success">
    <div class="card-header-inline">
        <i class="card-icon-success fas fa-icon"></i>
        <h3>Title</h3>
    </div>
</a>
```

**Validation:** `validate-color-rotation.ps1 --autofix`

---

### **Pattern C51: Tetris Stat Badges**

**Rule:** Stat badges MUST use 3-color rotation within each card

**Implementation:**
```html
<div class="card-stats">
    <span class="stat-badge stat-primary">
        <i class="fas fa-icon"></i> 7 phases
    </span>
    <span class="stat-badge stat-info">
        <i class="fas fa-icon"></i> TDD Enforced
    </span>
    <span class="stat-badge stat-warning">
        <i class="fas fa-icon"></i> 96h duration
    </span>
</div>
```

**Validation:** `validate-color-rotation.ps1 --badges`

---

### **Pattern C52: Level 1 Hero Header**

**Rule:** All Level 1 pages MUST have standardized hero header with clickable robot logo

**Template:**
```html
<!-- Hero Section with Robot Head -->
<div class="hero-section-wrapper" style="margin-top: 3rem;">
    <div class="hero-robot-container">
        <a href="../index.html" class="robot-head-link" title="Back to Home">
            <svg class="robot-head-icon" viewBox="0 0 100 100" width="200" height="200">
                <!-- Robot SVG paths here -->
            </svg>
        </a>
    </div>
    <div class="hero-divider-line"></div>
</div>

<!-- Page Title Card -->
<section class="glass-card-display hero-introduction">
    <div class="card-header-centered">
        <i class="fas fa-{icon} card-icon-{variant}"></i>
        <h1>{Page Title}</h1>
    </div>
    <p class="hero-description">{Description text}</p>
    <div class="hero-stats">
        <span class="stat-pill stat-primary">{Stat 1}</span>
        <span class="stat-pill stat-info">{Stat 2}</span>
        <span class="stat-pill stat-warning">{Stat 3}</span>
    </div>
</section>
```

**Validation:** `page-refresh-tool.py --validate-heroes`

---

### **Pattern C53: Full Section Panel Wrapping**

**Rule:** Heading + content MUST be wrapped together in ONE glassmorphism panel

**Template:**
```html
<section class="glass-card-display">
    <h2 class="section-title">
        <i class="fas fa-icon"></i>
        Section Title
    </h2>
    
    <div class="masonry-grid">
        <!-- All section content here -->
    </div>
</section>
```

**Validation:** `validate-panel-wrapping.ps1 --autofix`

---

## 🚀 Execution Workflows

### **Workflow 1: User Requests Single-Page Change**

**Trigger:** User says "Fix X on Y.html"

**Intelligence Response:**

```python
# 1. Analyze request complexity
complexity = calculate_complexity("Y.html")

# 2. Detect similar pages
similar_pages = find_similar_patterns("Y.html", scope="level1")

# 3. Determine execution strategy
if complexity > 50:
    strategy = "regenerate"
    tool = "purpose-driven-designer.py"
elif len(similar_pages) > 3:
    strategy = "batch_transform"
    tool = "page-refresh-tool.py --batch"
else:
    strategy = "targeted_fix"
    tool = "fix-{specific-issue}.ps1"

# 4. Execute with transparency
print(f"🔍 Detected: {len(similar_pages)} similar pages")
print(f"📊 Complexity: {complexity} → Strategy: {strategy}")
print(f"🛠️ Invoking: {tool}")

run_tool(tool, pages=[Y] + similar_pages)

# 5. Validate results
run_validation_suite([Y] + similar_pages)

# 6. Commit atomically
git_commit(f"feat(ui): {change_description} ({len(similar_pages)+1} pages)")
```

**User Experience:**
- ✅ Sees complexity analysis (transparent decision-making)
- ✅ Sees tool execution output (progress visibility)
- ✅ Gets batch fix applied to similar pages (efficiency)
- ✅ No need to repeat request for other pages (intelligent propagation)

---

### **Workflow 2: User Requests Standardization**

**Trigger:** User says "Standardize X across all pages"

**Intelligence Response:**

```python
# 1. Identify scope
scope_pages = identify_scope("X", levels=[0,1,2])

# 2. Analyze current state
compliance_report = validate_compliance(scope_pages, pattern="X")

# 3. Group by fix complexity
high_complexity = [p for p in scope_pages if complexity(p) > 50]
medium_complexity = [p for p in scope_pages if 20 < complexity(p) <= 50]
low_complexity = [p for p in scope_pages if complexity(p) <= 20]

# 4. Execute in batches
print(f"🔄 Standardizing {len(scope_pages)} pages")
print(f"  - {len(high_complexity)} regenerating (complexity 51+)")
print(f"  - {len(medium_complexity)} script-driven (complexity 21-50)")
print(f"  - {len(low_complexity)} targeted edits (complexity 0-20)")

# Regenerate high-complexity pages
for page in high_complexity:
    purpose_driven_designer(page, template="X")

# Script-driven medium-complexity
for page in medium_complexity:
    run_tool(f"fix-{X}.ps1", page, autofix=True)

# Targeted edits for low-complexity
for page in low_complexity:
    apply_targeted_edits(page, pattern="X")

# 5. Validate ALL pages
run_validation_suite(scope_pages, strict=True)

# 6. Update standard
update_glassmorphism_standard(pattern="X", version="4.3.1")

# 7. Commit with detailed changelog
git_commit(f"""feat(ui): Standardize {X} across {len(scope_pages)} pages

SCOPE:
- Regenerated: {len(high_complexity)} pages (complexity 51+)
- Script-driven: {len(medium_complexity)} pages (complexity 21-50)
- Targeted edits: {len(low_complexity)} pages (complexity 0-20)

VALIDATION:
- glassmorphism-compliance: PASSED
- css-usage: PASSED
- html-structure: PASSED

STANDARD UPDATED:
- glassmorphism-design-standard.md v4.3.1
- Added Pattern {X} documentation
- Updated validation suite
""")
```

**User Experience:**
- ✅ Sees scope analysis (83 pages affected)
- ✅ Sees strategy per complexity tier (transparent execution)
- ✅ Gets comprehensive validation report (quality assurance)
- ✅ Standards document updated automatically (knowledge capture)
- ✅ NO manual work required (full automation)

---

### **Workflow 3: SNOWBALL Phase Execution**

**Trigger:** User opens `http://localhost:8000/X.html` and describes issues

**Intelligence Response:**

```python
# 1. Parse user feedback
issues = parse_feedback(user_input)
# Example: ["hero header wrong", "cards not colorized", "panels missing"]

# 2. Map to patterns
pattern_map = {
    "hero header wrong": ("C52", "page-refresh-tool.py --heroes"),
    "cards not colorized": ("C50", "validate-color-rotation.ps1 --autofix"),
    "panels missing": ("C53", "validate-panel-wrapping.ps1 --autofix")
}

# 3. Execute tools in dependency order
for issue in issues:
    pattern, tool = pattern_map[issue]
    print(f"🔧 Fixing {issue} using {pattern}")
    run_tool(tool, page="X.html")

# 4. User validates
print("✅ Changes applied. Please refresh browser to review.")
user_approval = wait_for_approval()

if user_approval:
    # 5. Commit page
    git_commit(f"Phase 16a: Refine {X} - {', '.join(issues)}")
    
    # 6. Update SNOWBALL-STRATEGY.md
    update_snowball_progress(page="X.html", status="COMPLETE")
    
    # 7. Move to next page
    next_page = get_next_snowball_page()
    print(f"🎯 Next page: {next_page}")
else:
    # 5. Iterate on specific section
    section = user_specifies_section()
    refine_section(page="X.html", section=section)
```

**User Experience:**
- ✅ Describes issues in natural language (no technical jargon required)
- ✅ Sees tools execute automatically (transparency)
- ✅ Validates changes in live browser (immediate feedback)
- ✅ One approval → automatic commit + progress tracking (efficiency)
- ✅ Clear next steps (guided workflow)

---

## 🔍 Intelligent Problem Detection

### **Automatic Issue Discovery**

When user opens a page, **automatically analyze** and report:

```python
def auto_analyze_page(page_path: str) -> PageHealthReport:
    """Automatically detect issues before user describes them."""
    
    report = {
        "complexity_score": 0,
        "issues": [],
        "recommendations": []
    }
    
    # 1. Parse HTML
    soup = BeautifulSoup(page_path)
    
    # 2. Check patterns
    if not has_hero_header(soup):
        report["issues"].append("Missing Level 1 hero header (Pattern C52)")
        report["complexity_score"] += 25
    
    if inline_styles := find_inline_styles(soup):
        report["issues"].append(f"{len(inline_styles)} inline styles found")
        report["complexity_score"] += len(inline_styles) * 0.5
    
    if orphaned_headings := find_orphaned_headings(soup):
        report["issues"].append(f"{len(orphaned_headings)} headings not panel-wrapped (Pattern C53)")
        report["complexity_score"] += len(orphaned_headings) * 3
    
    if monotone_cards := detect_monotone_cards(soup):
        report["issues"].append(f"{len(monotone_cards)} cards without color rotation (Pattern C50)")
        report["complexity_score"] += len(monotone_cards) * 0.5
    
    # 3. CSS analysis
    css_report = validate_css_usage(page_path)
    if css_report["unused_classes"] > 10:
        report["issues"].append(f"{css_report['unused_classes']} unused CSS classes")
        report["complexity_score"] += css_report["unused_classes"] * 0.1
    
    # 4. Mobile responsiveness
    mobile_score = validate_mobile_friendliness(page_path)
    if mobile_score < 95:
        report["issues"].append(f"Mobile score: {mobile_score}% (target: 95%+)")
        report["complexity_score"] += (95 - mobile_score) * 0.5
    
    # 5. Generate recommendations
    if report["complexity_score"] > 50:
        report["recommendations"].append("DELETE & REGENERATE (complexity 51+)")
        report["recommended_tool"] = "purpose-driven-designer.py"
    elif report["complexity_score"] > 20:
        report["recommendations"].append("SCRIPT-DRIVEN REFACTOR (complexity 21-50)")
        report["recommended_tool"] = "page-refresh-tool.py --batch-fix"
    else:
        report["recommendations"].append("TARGETED EDITS (complexity 0-20)")
        report["recommended_tool"] = "manual fixes"
    
    return report
```

**User Experience:**

```
User: "Review http://localhost:8000/architecture/index.html"

CORTEX Intelligence:
🔍 Automatic Analysis Complete

📊 COMPLEXITY SCORE: 47 (Script-Driven Recommended)

⚠️ ISSUES FOUND (6):
1. ❌ 12 inline styles found
2. ❌ 3 headings not panel-wrapped (Pattern C53)
3. ❌ 10 cards without color rotation (Pattern C50)
4. ❌ 23 unused CSS classes
5. ❌ Mobile score: 88% (target: 95%+)
6. ❌ Missing glassmorphism theme on 2 mermaid diagrams

🎯 RECOMMENDED STRATEGY: Script-Driven Refactor
🛠️ RECOMMENDED TOOLS:
  - fix-inline-styles.ps1 --autofix
  - validate-panel-wrapping.ps1 --autofix
  - validate-color-rotation.ps1 --autofix
  - remove-unused-css.ps1
  - improve-mobile-friendliness.ps1

❓ Execute recommended fixes? [Y/n]
```

**No User Description Required:** Intelligence layer detects issues proactively.

---

## 🎨 Design Standard Evolution

### **Automatic Standard Updates**

When new patterns emerge, **automatically update** `glassmorphism-design-standard.md`:

```python
def evolve_standard(new_pattern: dict):
    """Automatically update design standard when new pattern approved."""
    
    # 1. Load current standard
    standard = load_standard("glassmorphism-design-standard.md")
    
    # 2. Calculate next pattern ID
    existing_patterns = extract_patterns(standard)
    next_id = f"C{max([int(p[1:]) for p in existing_patterns]) + 1}"
    
    # 3. Generate pattern documentation
    pattern_doc = f"""
### **Pattern {next_id}: {new_pattern['name']}**

**Rule:** {new_pattern['rule']}

**Implementation:**
```html
{new_pattern['template']}
```

**Validation:** `{new_pattern['validation_script']}`

**Examples:**
{generate_examples(new_pattern)}

**Related Patterns:** {new_pattern['related']}
"""
    
    # 4. Insert at appropriate section
    insert_pattern(standard, pattern_doc, section="Design Patterns")
    
    # 5. Update version
    bump_version(standard, level="minor")  # 4.3.0 → 4.4.0
    
    # 6. Save and commit
    save_standard(standard)
    git_commit(f"docs(standard): Add Pattern {next_id} - {new_pattern['name']}")
    
    # 7. Generate validation script (if not exists)
    if not exists(new_pattern['validation_script']):
        generate_validation_script(next_id, new_pattern)
```

**User Experience:**
- ✅ Approves new pattern on ONE page
- ✅ System documents pattern automatically
- ✅ Generates validation script automatically
- ✅ Standard version bumped automatically
- ✅ NO manual documentation required

---

## 📊 Quality Metrics Dashboard

**Auto-Generated After Each Change:**

```
╔══════════════════════════════════════════════════════════════╗
║           CORTEX DOCS QUALITY METRICS                        ║
╠══════════════════════════════════════════════════════════════╣
║ Total Pages:            83                                   ║
║ Level 0 (Home):         1   [████████████████████] 100%      ║
║ Level 1 (Hubs):         8   [███████████████████░] 95%       ║
║ Level 2 (Detail):       74  [█████████████░░░░░░░] 68%       ║
╠══════════════════════════════════════════════════════════════╣
║ GLASSMORPHISM COMPLIANCE                                     ║
║ - Pattern C50 (Color):  [████████████████░░░░] 78%           ║
║ - Pattern C51 (Badges): [████████████████████] 92%           ║
║ - Pattern C52 (Heroes): [████████████████░░░░] 75% (6/8 L1)  ║
║ - Pattern C53 (Panels): [██████████████░░░░░░] 65%           ║
╠══════════════════════════════════════════════════════════════╣
║ CSS HEALTH                                                   ║
║ - Unused Classes:       143 (target: <20)                    ║
║ - Duplicate Rules:      12 (target: <2%)                     ║
║ - Inline Styles:        0 (target: 0) ✅                     ║
║ - Missing Classes:      23 (target: 0)                       ║
╠══════════════════════════════════════════════════════════════╣
║ MOBILE RESPONSIVENESS                                        ║
║ - Average Score:        91% (target: 95%+)                   ║
║ - Pages < 95%:          18 pages need improvement            ║
║ - Perfect Score:        65 pages ✅                          ║
╠══════════════════════════════════════════════════════════════╣
║ ACCESSIBILITY (WCAG AA)                                      ║
║ - Color Contrast:       [████████████████████] 98%           ║
║ - Alt Text:             [███████████████████░] 96%           ║
║ - ARIA Labels:          [████████████████░░░░] 82%           ║
║ - Keyboard Nav:         [████████████████████] 100%          ║
╠══════════════════════════════════════════════════════════════╣
║ SNOWBALL PROGRESS (Phase 16a)                                ║
║ - Completed Pages:      1/4  [█████░░░░░░░░░░░░] 25%         ║
║ - Current Page:         token-optimization/index.html        ║
║ - Est. Time Remaining:  6h                                   ║
╚══════════════════════════════════════════════════════════════╝
```

**Generated by:** `validate-all-html.ps1 --dashboard`

---

## 🚨 Critical Rules (SKULL Enforcement)

### **1. HOLISTIC_STANDARDIZATION**

**Rule:** When user requests a change, ALWAYS:
1. Detect scope (single page, category, site-wide)
2. Find similar patterns across workspace
3. Apply change to ALL matching instances
4. Update design standard if new pattern
5. Validate compliance across affected pages

**Enforcement:** Intelligence layer blocks single-page fixes when similar pages exist.

---

### **2. TOOL_FIRST_EXECUTION**

**Rule:** ALWAYS prefer Python/PowerShell tools over manual edits.

**Decision Tree:**
```
Change Requested
  ↓
Tool Exists? ─── YES ──→ Use tool (90% of cases)
  ↓
  NO
  ↓
Can Script Be Created? ─── YES ──→ Create script (8% of cases)
  ↓
  NO
  ↓
Manual Edit (2% of cases)
```

**Enforcement:** Intelligence layer suggests tool creation if missing.

---

### **3. COMPLEXITY_DRIVEN_STRATEGY**

**Rule:** ALWAYS calculate complexity before acting.

**Mandatory Actions:**
- Score 0-20: Targeted edits only
- Score 21-50: Script-driven refactor only
- Score 51+: Delete & regenerate only

**Enforcement:** Intelligence layer blocks inappropriate strategies.

---

### **4. DELETE_OVER_FIX**

**Rule:** When complexity > 50, ALWAYS regenerate instead of fixing.

**Rationale:**
- Fixing broken HTML is error-prone (leaves orphaned code)
- Regenerating from approved templates is faster (purpose-driven-designer.py)
- Fresh start eliminates technical debt (no legacy patterns)

**Enforcement:** Intelligence layer prompts user if complexity > 50.

---

### **5. ATOMIC_COMMITS**

**Rule:** ALWAYS commit changes atomically with detailed changelogs.

**Format:**
```
feat(ui): {Change description} ({N} pages)

SCOPE:
- Files changed: {list}
- Strategy: {targeted/script-driven/regenerate}
- Complexity: {score}

VALIDATION:
- {tool1}: PASSED
- {tool2}: PASSED

STANDARD UPDATES:
- {standard}: v{version}
- {pattern}: Added/Modified
```

**Enforcement:** Pre-commit hook validates commit message format.

---

### **6. LIVE_VALIDATION**

**Rule:** ALWAYS require user approval after changes via browser refresh.

**Workflow:**
1. Apply changes
2. Print: "✅ Changes applied. Refresh http://localhost:8000/{page}.html"
3. Wait for user approval
4. If approved: commit + move to next page
5. If not approved: iterate on specific section

**Enforcement:** SNOWBALL strategy mandates live validation.

---

## 🎯 Quick Reference Card

**User says:** → **Intelligence does:**

| User Input | Intelligence Action | Tools Used | Result |
|------------|---------------------|------------|--------|
| "Fix hero on X.html" | Find all Level 1 pages → Apply C52 to all | `page-refresh-tool.py` | 8 pages updated |
| "Colorize cards" | Detect monotone cards → Apply C50 rotation | `validate-color-rotation.ps1` | Pattern applied site-wide |
| "Standardize panels" | Find unwrapped sections → Apply C53 | `validate-panel-wrapping.ps1` | 23 sections wrapped |
| "This page looks broken" | Calculate complexity (67) → Regenerate | `purpose-driven-designer.py` | Fresh page created |
| "Review X.html" | Auto-analyze → Report issues + recommendations | Multiple validators | Proactive detection |
| "Continue Phase 16a" | Load SNOWBALL state → Resume at next page | `SNOWBALL-STRATEGY.md` | Seamless continuation |

---

## 📚 Related Documentation

- **Main Strategy:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/SNOWBALL-STRATEGY.md`
- **Design Standard:** `cortex-brain/documents/standards/glassmorphism-design-standard.md` (v4.3.0)
- **Tool Inventory:** `cortex-toolkit/TOOLS-INVENTORY.md` (52 scripts)
- **Plan Master:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/00-html-view-standardization.md`

---

**REMEMBER:** You are an intelligent design orchestrator. When user requests changes:
1. **Analyze complexity** (0-100 score)
2. **Detect scope** (similar pages)
3. **Choose strategy** (targeted/script-driven/regenerate)
4. **Execute with tools** (Python/PowerShell automation)
5. **Validate holistically** (run compliance suite)
6. **Commit atomically** (detailed changelog)

**Your goal:** Eliminate repetitive work, standardize holistically, maximize tool usage, and deliver consistent glassmorphism excellence.

**Version History:**
- v1.0.0: Initial release - Intelligent automation framework for HTML standardization

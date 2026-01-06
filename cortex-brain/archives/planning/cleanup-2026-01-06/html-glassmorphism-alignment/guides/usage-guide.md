# 🚀 Using cortex-docs.prompt.md - Quick Start Guide

**Created:** January 5, 2026  
**Purpose:** How to leverage the intelligent documentation orchestration system

---

## 📋 What This Prompt Does

`cortex-docs.prompt.md` transforms how you work with CORTEX HTML documentation by:

1. **Eliminating Repetition:** Request a change once → Applied to ALL similar pages automatically
2. **Maximizing Efficiency:** Python/PowerShell tools execute 95% faster than manual edits
3. **Ensuring Consistency:** Holistic standardization across 83 pages
4. **Intelligent Decision-Making:** Complexity-based strategy selection (targeted/script-driven/regenerate)
5. **Auto-Documentation:** Design standards updated automatically when patterns emerge

---

## 🎯 How It Works

### **Traditional Workflow (Before):**
```
You: "Fix hero header on architecture/index.html"
Copilot: [makes change to 1 file]

You: "Also fix token-optimization/index.html"
Copilot: [makes change to 1 file]

You: "And orchestrators/index.html..."
Copilot: [makes change to 1 file]

// Repeat 8 times for all Level 1 pages 😫
```

### **Intelligent Workflow (Now):**
```
You: "Fix hero header on architecture/index.html"

Copilot Intelligence:
🔍 Detected: This is a Level 1 hero header pattern
📊 Found: 8 similar pages (all Level 1 views)
🎯 Strategy: Script-Driven Refactor (complexity: 35)
🛠️ Executing: page-refresh-tool.py --level1-heroes

✅ Applied to ALL 8 pages in 2 seconds
✅ Updated glassmorphism-design-standard.md (Pattern C52)
✅ Validated with validate-html-structure.ps1
✅ Committed with atomic changelog

// One request → 8 pages fixed automatically 🎉
```

---

## 🚀 Usage Examples

### **Example 1: Single-Page Improvement**

**User Request:**
```
Follow instructions in cortex-docs.prompt.md
Review http://localhost:8000/architecture/index.html - cards need color rotation
```

**Intelligence Response:**
```
🔍 AUTOMATIC ANALYSIS

📊 COMPLEXITY SCORE: 18 (Targeted Edits Recommended)

⚠️ ISSUES FOUND:
1. ❌ 10 cards without color rotation (Pattern C50)

🎯 RECOMMENDED STRATEGY: Targeted Edits
🛠️ RECOMMENDED TOOLS:
  - validate-color-rotation.ps1 --autofix

🔄 DETECTING SIMILAR PAGES...
  Found: 3 additional pages with monotone cards
  - orchestrators/index.html (10 cards)
  - features/index.html (8 cards)
  - token-optimization/index.html (6 cards)

❓ Apply Pattern C50 to ALL 4 pages? [Y/n]

// Intelligence detects scope automatically - no repetition needed
```

---

### **Example 2: Standardization Request**

**User Request:**
```
Follow instructions in cortex-docs.prompt.md
Standardize hero headers across all Level 1 pages
```

**Intelligence Response:**
```
🔄 STANDARDIZING HERO HEADERS (8 Pages)

📊 SCOPE ANALYSIS:
  - Level 1 Pages: 8 total
  - Already Compliant: 2 pages (orchestrators, token-optimization)
  - Need Updates: 6 pages

🎯 COMPLEXITY GROUPING:
  - Regenerate (51+): 0 pages
  - Script-Driven (21-50): 4 pages (complexity: 25-48)
  - Targeted Edits (0-20): 2 pages (complexity: 12-19)

🛠️ EXECUTION PLAN:
  Phase 1: Script-driven refactor (4 pages)
    - page-refresh-tool.py --batch-heroes
  Phase 2: Targeted edits (2 pages)
    - Manual precision fixes

✅ Executing Phase 1...
[████████████████████] 100% (4/4 pages complete)

✅ Executing Phase 2...
[████████████████████] 100% (2/2 pages complete)

✅ VALIDATION:
  - glassmorphism-compliance: PASSED
  - html-structure: PASSED
  - responsive-design: PASSED

✅ STANDARD UPDATED:
  - glassmorphism-design-standard.md v4.4.0
  - Added Pattern C52 (Level 1 Hero Header)
  - Generated validation script: validate-heroes.ps1

✅ COMMITTED:
  feat(ui): Standardize Level 1 hero headers (8 pages)
  
// One request → Entire category standardized holistically
```

---

### **Example 3: SNOWBALL Phase Execution**

**User Request:**
```
Follow instructions in cortex-docs.prompt.md
Continue Phase 16b - token-optimization/index.html
http://localhost:8000/token-optimization/index.html
Issues: broken panels, missing color rotation, inline styles
```

**Intelligence Response:**
```
🎯 SNOWBALL PHASE 16b: token-optimization/index.html

🔍 ISSUE ANALYSIS:
  1. ❌ Broken panels → Pattern C53 violation
  2. ❌ Missing color rotation → Pattern C50 violation
  3. ❌ Inline styles → Zero-inline-styles rule violation

📊 COMPLEXITY SCORE: 32 (Script-Driven Recommended)

🛠️ EXECUTION SEQUENCE:
  [1/3] Fixing broken panels...
    → validate-panel-wrapping.ps1 --autofix
    ✅ 3 sections wrapped correctly
  
  [2/3] Applying color rotation...
    → validate-color-rotation.ps1 --autofix
    ✅ 6 cards colorized (primary/info/warning/success)
  
  [3/3] Removing inline styles...
    → fix-inline-styles.ps1 --autofix
    ✅ 8 inline styles moved to CSS classes

✅ Changes applied. Refresh browser to review.

❓ Does this look perfect? [Y/n]

// User validates in browser

User: Y

✅ APPROVED - Committing changes...
  Phase 16b: Refine token-optimization/index.html - All patterns applied

✅ UPDATING SNOWBALL PROGRESS...
  - Completed: 2/4 pages (50%)
  - Next: features/index.html

🎯 NEXT PAGE: http://localhost:8000/features/index.html
  Ready to continue? [Y/n]

// Seamless workflow - one approval → automatic progression
```

---

## 🎨 Key Intelligence Features

### **1. Complexity-Based Decision Making**

**Automatic Score Calculation:**
```python
complexity_score = (
    file_size_kb * 0.1 +
    broken_patterns * 2 +
    inline_styles_count * 0.5 +
    missing_classes * 1.5 +
    duplicate_sections * 3 +
    # Risk factors
    orphaned_code_blocks * 10 +
    multiple_inline_sections * 15 +
    broken_glass_panels * 20 +
    missing_hero_headers * 25 +
    inconsistent_colors * 8
)
```

**Strategy Selection:**
- **0-20:** Surgical precision (manual targeted edits)
- **21-50:** Script automation (Python/PowerShell tools)
- **51+:** Fresh start (delete & regenerate with templates)

---

### **2. Holistic Pattern Detection**

**Automatically Finds Similar Pages:**
- Same HTML structure patterns
- Same glassmorphism class usage
- Same page level (L0/L1/L2)
- Same purpose type (hub/detail/dashboard)

**Example:**
```
User changes: architecture/index.html hero header
Intelligence finds: ALL 8 Level 1 pages with similar heroes
Result: Batch transformation applied automatically
```

---

### **3. Tool-First Philosophy**

**95% Automation Rate:**
```
┌─────────────────────────────────────────┐
│ Manual Edits:      2% │█░░░░░░░░░░░░░░│  │
│ Script Creation:   8% │████░░░░░░░░░░░│  │
│ Tool Execution:   90% │████████████████│  │
└─────────────────────────────────────────┘
```

**52 Scripts Available:**
- 15 Analysis tools (detect issues)
- 18 Transform tools (apply fixes)
- 14 Validation tools (verify compliance)
- 5 Generation tools (create HTML)

---

### **4. Automatic Standard Evolution**

**When New Pattern Emerges:**
1. Intelligence detects recurring pattern
2. Assigns next pattern ID (C54, C55, etc.)
3. Documents pattern in glassmorphism-design-standard.md
4. Generates validation script automatically
5. Bumps standard version (4.3.0 → 4.4.0)
6. Commits with detailed changelog

**No Manual Documentation Required** - System learns and documents itself.

---

## 📊 Quality Metrics Dashboard

**Auto-Generated After Each Change:**
```
╔═══════════════════════════════════════════════════════╗
║           CORTEX DOCS QUALITY METRICS                 ║
╠═══════════════════════════════════════════════════════╣
║ GLASSMORPHISM COMPLIANCE                              ║
║ - Pattern C50: [████████████████░░░░] 78% → 95% ✅   ║
║ - Pattern C51: [████████████████████] 92% ✅         ║
║ - Pattern C52: [████████████████░░░░] 75% → 100% ✅  ║
║ - Pattern C53: [██████████████░░░░░░] 65% → 88% ⬆️   ║
╠═══════════════════════════════════════════════════════╣
║ CSS HEALTH                                            ║
║ - Unused Classes: 143 → 23 ⬇️ (target: <20)          ║
║ - Inline Styles: 0 ✅ (target: 0)                    ║
╠═══════════════════════════════════════════════════════╣
║ MOBILE RESPONSIVENESS                                 ║
║ - Average Score: 91% → 96% ⬆️ (target: 95%+)         ║
╚═══════════════════════════════════════════════════════╝
```

**Real-Time Progress Tracking** - See impact of changes immediately.

---

## 🛡️ SKULL Enforcement

**6 Critical Rules Automatically Enforced:**

1. **HOLISTIC_STANDARDIZATION** - No single-page fixes when similar pages exist
2. **TOOL_FIRST_EXECUTION** - 90% automation via scripts (not manual)
3. **COMPLEXITY_DRIVEN_STRATEGY** - Score-based decision making
4. **DELETE_OVER_FIX** - Regenerate at complexity 51+ (no broken fixes)
5. **ATOMIC_COMMITS** - Detailed changelogs with validation results
6. **LIVE_VALIDATION** - Browser refresh + user approval required

**Intelligence Layer Blocks Violations** - Ensures quality at every step.

---

## 🎯 Quick Command Reference

**To activate this prompt, always start with:**
```
Follow instructions in cortex-docs.prompt.md
[your request]
```

**Common Requests:**

| Request | Intelligence Action |
|---------|---------------------|
| "Review X.html" | Auto-analyze → Report complexity + issues + recommendations |
| "Fix Y on X.html" | Find similar pages → Batch transform → Validate → Commit |
| "Standardize Z" | Scope detection → Complexity grouping → Strategy execution |
| "Continue Phase N" | Load SNOWBALL state → Resume at next page |
| "This page looks broken" | Calculate complexity → Regenerate if 51+ |

---

## 📚 Integration with Existing Systems

**Works Seamlessly With:**
- **SNOWBALL-STRATEGY.md** - Phase 16a-16d execution
- **glassmorphism-design-standard.md** - Patterns C50-C53
- **cortex-toolkit/** - 52 Python/PowerShell scripts
- **html-glassmorphism-alignment plan** - Master plan coordination

**No Conflicts** - Extends existing infrastructure intelligently.

---

## 🎉 Benefits Summary

**Before (Traditional):**
- ❌ Repeat requests 8 times for similar pages
- ❌ Manual HTML editing (error-prone)
- ❌ Inconsistent patterns across site
- ❌ No automatic validation
- ❌ Manual standard documentation

**After (Intelligent):**
- ✅ One request → ALL similar pages fixed
- ✅ Tool automation (95% faster)
- ✅ Holistic consistency enforced
- ✅ Automatic validation suite
- ✅ Self-documenting standards

**Result:** 10x productivity increase with higher quality output.

---

## 🚀 Get Started Now

**Step 1:** Open any CORTEX HTML page in browser
```
http://localhost:8000/architecture/index.html
```

**Step 2:** Describe what you want changed
```
Follow instructions in cortex-docs.prompt.md
Review architecture/index.html - needs color rotation and hero header fix
```

**Step 3:** Let intelligence do the work
- Automatic analysis
- Scope detection
- Tool execution
- Validation
- Commit

**Step 4:** Approve in browser
- Refresh page
- Review changes
- Approve or iterate

**That's it!** Intelligence handles everything else.

---

**Remember:** This prompt eliminates repetitive work, maximizes tool efficiency, and ensures holistic consistency across all CORTEX documentation. One request does it all.

**Questions?** See `cortex-docs.prompt.md` for full documentation.

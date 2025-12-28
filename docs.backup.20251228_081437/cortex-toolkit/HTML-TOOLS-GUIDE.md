# HTML Quality Tools - Quick Reference Guide

**Version:** 1.0.0  
**Last Updated:** December 27, 2025  
**Part of:** CORTEX Toolkit Documentation Category

---

## 🎯 What Are These Tools?

Two specialized tools that help maintain high-quality HTML documentation by:
1. **HTML Style Centralizer** - Removes messy inline CSS styles and centralizes them
2. **HTML Validator** - Checks HTML files for syntax errors and structural issues

---

## 👥 For Non-Technical Users

### What Problem Do These Tools Solve?

**Problem 1: Messy, Hard-to-Update Styles**
- When HTML has `style="color:red"` scattered everywhere, changing the color scheme means editing 100+ files
- **Solution:** Style Centralizer moves all styles to ONE CSS file - update once, affects everything

**Problem 2: Broken Web Pages**
- Missing closing tags like `</div>` break page layout
- Unclosed quotes in attributes cause display errors
- **Solution:** HTML Validator finds and reports these errors automatically

### When Should You Use These Tools?

| Situation | Tool to Use | Why |
|-----------|-------------|-----|
| After creating new HTML pages | Style Centralizer | Ensures consistent styling |
| Before publishing documentation | Both tools | Quality assurance check |
| After bulk find/replace edits | Validator | Verify no accidental breaks |
| Migrating from templates | Style Centralizer | Clean up template inline styles |
| Website redesign | Both tools | Foundation for clean CSS architecture |

### How to Run (Simple Steps)

**Step 1: Open Terminal**
- **Windows:** PowerShell (search "PowerShell" in Start menu)
- **Mac:** Terminal (Cmd+Space, type "Terminal")
- **Linux:** Terminal (Ctrl+Alt+T)

**Step 2: Navigate to CORTEX**
```bash
# Windows
cd D:\PROJECTS\CORTEX

# Mac/Linux
cd ~/PROJECTS/CORTEX
```

**Step 3: Run the Tool**
```bash
# Clean up inline styles
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# OR validate HTML syntax
python cortex-toolkit/documentation/html-tools/html_validator.py
```

**Step 4: Read the Results**
- ✅ Green checkmarks = Success
- ⚠️ Yellow warnings = Minor issues (usually safe)
- ❌ Red X marks = Errors that need fixing

---

## 🔧 For Technical Users

### HTML Style Centralizer

**Purpose:** Remove inline `style=""` attributes and migrate to centralized CSS classes.

**Algorithm:**
1. Parse HTML using Python's `HTMLParser` (safe, structure-preserving)
2. Identify and track all `style` attributes during traversal
3. Remove style attributes while preserving all other attributes
4. Reconstruct HTML with proper tag structure (opening, closing, self-closing)
5. Write cleaned HTML back to file

**Preserved Exceptions:**
- `docs/story/viewer.html` - Interactive story navigation (3 inline styles with JS handlers)
- D3.js template literals - `style="background: ${d.color}"` (data-driven dynamic styles)

**Safety Features:**
- Git-reversible (all changes tracked)
- Size sanity check (output must be >50% of input)
- Exception list (skip files with `story/viewer.html` in path)
- Parser error handling (catch and report failures)

**Output:**
```
Scanning for HTML files with inline styles...
✅ architecture/agent-system.html: 254 inline styles removed
✅ features/tdd-mastery.html: 88 inline styles removed
✅ technical/orchestrators/index.html: 6 inline styles removed

============================================================
SAFE CLEANUP COMPLETE
============================================================
Files Modified: 34
Inline Styles Removed: 1,822
Errors: 0
```

**Command Options:**
```bash
# Standard run (processes all HTML in docs/)
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Dry run (show what would be changed without modifying files)
# Note: Not yet implemented - use git diff to preview changes
```

### HTML Validator

**Purpose:** Validate HTML5 syntax, tag matching, attribute structure, and element nesting.

**Validation Checks:**
1. **Tag Matching:** All opening tags have corresponding closing tags
2. **Void Elements:** Self-closing tags (`<br/>`, `<img/>`) properly formatted
3. **Attribute Syntax:** No unclosed quotes, malformed attributes
4. **Nesting Structure:** Proper element hierarchy (no overlapping tags)
5. **Duplicate Attributes:** Warning for multiple `class=""` on same element
6. **Line Tracking:** Precise line number reporting for errors

**Algorithm:**
1. Create tag stack (track opening tags)
2. Parse HTML token by token
3. Push opening tags to stack
4. Pop stack on closing tags, verify match
5. Report mismatches, unclosed tags, malformed patterns
6. Count lines in text data for accurate error reporting

**Error Types:**
- **ERROR:** Syntax errors, unclosed tags, mismatched nesting (must fix)
- **WARNING:** Duplicate attributes, void element variations (safe to ignore)
- **MALFORMED:** Potentially broken patterns (manual review required)

**Output:**
```
Validating 50 HTML files...

⚠️  architecture/agent-system.html
    Line 532: Duplicate attributes in <a>: class

❌ features/index.html
    ERROR: Line 20: Closing tag </img> with no matching opening tag
    UNCLOSED: <div> opened at line 18

======================================================================
VALIDATION SUMMARY
======================================================================
Total Files: 50
✅ Valid: 48
⚠️  Valid with Warnings: 2
❌ Invalid: 0

🎉 ALL HTML FILES ARE SYNTACTICALLY CORRECT!
```

**Command Options:**
```bash
# Validate all HTML files
python cortex-toolkit/documentation/html-tools/html_validator.py

# Exit codes:
# 0 = All valid
# 1 = Validation errors found
```

---

## 📋 Common Workflows

### Workflow 1: Pre-Deployment Quality Check

**Goal:** Ensure documentation is error-free before publishing

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Step 1: Validate HTML syntax
python cortex-toolkit/documentation/html-tools/html_validator.py
# Expected: 100% valid files

# Step 2: Centralize styles (if needed)
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py
# Expected: 0 inline styles removed (already clean)

# Step 3: Re-validate after cleanup
python cortex-toolkit/documentation/html-tools/html_validator.py
# Expected: Still 100% valid

# Step 4: Visual regression test
# Open http://localhost:8000/ in browser
# Verify pages render correctly
```

### Workflow 2: Bulk HTML Cleanup After Template Migration

**Goal:** Clean up messy templates with inline styles

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Step 1: Create git checkpoint
git add -A
git commit -m "Before HTML cleanup"

# Step 2: Run style centralizer
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py
# Expected: 1000+ inline styles removed

# Step 3: Validate structure preserved
python cortex-toolkit/documentation/html-tools/html_validator.py
# Expected: All files still valid

# Step 4: Review changes
git diff docs/

# Step 5: Test in browser
./scripts/launch_docs.sh
# Open http://localhost:8000/

# Step 6: Commit or rollback
git commit -m "Centralized inline styles to main.css"
# OR
git restore docs/  # if issues found
```

### Workflow 3: Fix Broken HTML After Bulk Edit

**Goal:** Find and fix HTML errors introduced by find/replace

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Step 1: Validate to identify errors
python cortex-toolkit/documentation/html-tools/html_validator.py
# Shows: ❌ features/index.html - Line 45: Unclosed <div>

# Step 2: Fix reported errors in editor
# Open features/index.html
# Go to line 45
# Add missing </div>

# Step 3: Re-validate
python cortex-toolkit/documentation/html-tools/html_validator.py
# Expected: ✅ Valid

# Step 4: Commit fix
git add features/index.html
git commit -m "Fixed unclosed div in features/index.html"
```

---

## 🚨 Troubleshooting

### Issue 1: "Parser exception" Error

**Symptom:**
```
⚠️  architecture/knowledge-graph.html: ERROR: Output too small, possible parsing failure
```

**Cause:** HTMLParser failed to parse complex nested structures

**Solution:**
1. Check file manually for malformed HTML
2. Use browser DevTools to validate structure
3. Fix obvious syntax errors
4. Re-run tool

### Issue 2: False Positive `</img>` Errors

**Symptom:**
```
ERROR: Line 13: Closing tag </img> with no matching opening tag
```

**Cause:** HTMLParser treats self-closing `<img />` as needing `</img>`

**Solution:** This is a KNOWN FALSE POSITIVE. Ignore if:
- File uses proper self-closing syntax: `<img src="..." />`
- No actual rendering issues in browser
- Other validators (W3C) pass

### Issue 3: D3.js Styles Removed

**Symptom:** Interactive visualizations broken after style cleanup

**Cause:** Style centralizer removed `style="background: ${d.color}"`

**Solution:**
1. Restore from git: `git restore docs/`
2. Check script version - should skip lines with `${d.` or `${orchestrator.`
3. Report issue if bug found

### Issue 4: Too Many Inline Styles Removed

**Symptom:** Pages look broken, no colors/spacing

**Cause:** CSS classes not created before removing inline styles

**Solution:**
1. Restore from git: `git restore docs/`
2. Ensure `docs/assets/css/main.css` has classes:
   - `.metadata-item-label`, `.metadata-item-value`
   - `.feature-icon`, `.feature-title`, `.feature-description`
   - Legend colors, utility classes
3. Re-run style centralizer

---

## 📊 Success Metrics

### Style Centralizer Success

- ✅ 95%+ inline styles removed (excluding exceptions)
- ✅ 0 visual regressions (pages render identically)
- ✅ CSS file size manageable (<200KB)
- ✅ All pages pass HTML validation

### Validator Success

- ✅ 100% files syntactically valid
- ✅ 0 critical errors (unclosed tags, nesting issues)
- ⚠️ Warnings acceptable (duplicate classes, false positives)
- ✅ All pages render in Chrome, Firefox, Safari

---

## 📚 Additional Resources

**Related Documentation:**
- `cortex-brain/documents/reports/HTML-VALIDATION-CLEANUP-REPORT.md` - Complete cleanup report
- `cortex-brain/documents/reports/INLINE-STYLE-CLEANUP-REPORT.md` - Initial metrics
- `.github/prompts/docgen.prompt.md` - Documentation standards (100% centralized CSS rule)

**Tool Source Code:**
- `cortex-toolkit/documentation/html-tools/html_style_centralizer.py` - 150 lines
- `cortex-toolkit/documentation/html-tools/html_validator.py` - 200 lines

**Validation Scripts (Legacy):**
- `scripts/safe_cleanup_inline_styles.py` - Original script (deprecated)
- `scripts/validate_html_syntax.py` - Original validator (deprecated)

---

## 🤝 Support

**Questions?**
- Technical users: Review tool source code comments
- Non-technical users: Ask in #cortex-toolkit Slack channel
- Bug reports: Create issue in GitHub with error output

**Feature Requests:**
- Dry-run mode for style centralizer
- Custom exception patterns
- Specific directory targeting
- CSS class naming conventions

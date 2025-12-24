# Story Enhancement Test Harness - Quick Reference

**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Comprehensive test suite validating **all 8 orchestrator modules** + **MkDocs link integrity**.

Runs **after orchestrator completion** as quality gate before deployment.

---

## 🚀 Quick Start

### Run All Tests

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
pytest tests/orchestrators/test_story_enhancement_harness.py -v
```

### Run Specific Category

```bash
# Character consistency only
pytest tests/orchestrators/test_story_enhancement_harness.py::TestCharacterConsistency -v

# Link validation only
pytest tests/orchestrators/test_story_enhancement_harness.py::TestMkDocsLinks -v

# Development chronology only
pytest tests/orchestrators/test_story_enhancement_harness.py::TestDevelopmentChronology -v
```

### Generate Test Report

```bash
pytest tests/orchestrators/test_story_enhancement_harness.py -v --html=cortex-brain/documents/reports/test-report.html
```

---

## 📋 Test Categories

### 1. Character Consistency (`TestCharacterConsistency`)

**Rules Validated:**
- ✅ No "Miss G" instances (should be "G" only)
- ✅ No physical G interactions (sitting, bringing coffee, doorway)
- ✅ G appears as vision/apparition/manifestation only

**Auto-Fix:** Story Validation Module can fix these automatically

### 2. Development Chronology (`TestDevelopmentChronology`)

**Rules Validated:**
- ✅ Features appear after implementation chapters
- ✅ No "time travel" (code before planning)
- ✅ Proper chapter sequencing

**Fix:** Manual reordering or validation module

### 3. Duplicate Scenes (`TestDuplicateScenes`)

**Rules Validated:**
- ✅ No paragraphs with 85%+ similarity
- ✅ No file state contradictions (filled → opened as new)

**Fix:** Manual deletion or deduplication analyzer

### 4. Name Introduction (`TestNameIntroduction`)

**Rules Validated:**
- ✅ "Asif Hussain" introduced with proper context
- ✅ Introduction appears early (Prologue/Chapter 1)

**Auto-Fix:** Validation module inserts introduction

### 5. Development Logic (`TestDevelopmentLogic`)

**Rules Validated:**
- ✅ Planning before coding in each chapter
- ✅ Whiteboard scenes before implementation

**Fix:** Manual scene reordering

### 6. MkDocs Links (`TestMkDocsLinks`)

**Rules Validated:**
- ✅ All nav entries point to existing files
- ✅ All internal markdown links valid
- ✅ Story file accessible and in nav

**Auto-Fix:** Generates CSS to visually disable broken links

### 7. Integration (`TestOrchestratorIntegration`)

**Rules Validated:**
- ✅ Master file exists and valid
- ✅ Plan has all 8 modules
- ✅ Story copied to docs directory

---

## 🔧 Broken Link Visual Disabling

When link validation finds broken links, test harness **automatically generates**:

**File:** `docs/assets/stylesheets/broken-links.css`

**Effect:**
- Broken links are **grayed out** (35% opacity)
- **Strikethrough** text decoration
- **Construction emoji** (🚧) appended
- **Tooltip** on hover: "⚠️ Feature in development"
- **Pointer disabled** (no clicks allowed)

**Visual Examples:**
- ~~The CORTEX Birth~~ → ~~The CORTEX Birth 🚧~~
- ~~Architecture Overview~~ → ~~Architecture Overview 🚧~~

**Banner:** Orange banner at top: "⚠️ Some navigation links disabled (features in development)"

---

## 📊 Test Report

**Auto-Generated:** `cortex-brain/documents/reports/story-enhancement-test-report.md`

**Includes:**
- ✅ Pass/Fail/Skip counts by category
- ❌ Detailed failure messages
- 🔧 Fix recommendations
- 📋 Deployment readiness status

---

## 🚦 CI/CD Integration

### Exit Codes

- **0:** All tests passed → Deploy ready ✅
- **1:** Failures detected → Block deployment ❌
- **5:** Tests skipped (broken links visually disabled) → Deploy with warnings ⚠️

### GitHub Actions Integration

```yaml
- name: Run Story Enhancement Tests
  run: |
    pytest tests/orchestrators/test_story_enhancement_harness.py -v --tb=short
  continue-on-error: false  # Block on failures
```

---

## 🛠️ Fix Workflow

### When Tests Fail

1. **Read test report:** `cortex-brain/documents/reports/story-enhancement-test-report.md`
2. **Check failures:**
   - Character issues → Run Story Validation Module auto-fix
   - Chronology issues → Manual chapter reordering
   - Duplicate scenes → Deduplication analyzer or manual deletion
   - Name introduction → Auto-insert with validation module
3. **Re-run tests** until all green
4. **Deploy** once passing

### When Links Broken

1. **CSS auto-applied:** Broken links visually disabled
2. **Keep working:** Links stay visible but grayed out
3. **Develop feature:** Build underlying functionality
4. **Create docs:** Add markdown files to `docs/`
5. **Update nav:** Fix paths in `mkdocs.yml`
6. **Re-test:** Links become active once files exist

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `tests/orchestrators/test_story_enhancement_harness.py` | Test suite |
| `docs/assets/stylesheets/broken-links.css` | Visual link disabling |
| `cortex-brain/documents/reports/story-enhancement-test-report.md` | Test results |
| `cortex-brain/documents/narratives/THE-AWAKENING-OF-CORTEX-MASTER.md` | Story source |
| `docs/THE-AWAKENING-OF-CORTEX.md` | MkDocs input (copy of master) |
| `mkdocs.yml` | Navigation configuration |

---

## 🎯 Integration with Story Enhancement Orchestrator

**Workflow:**

1. **Phase 1:** Feature Discovery → Extract features from codebase
2. **Phase 2:** Narrative Weaving → AI generates new chapters
3. **Phase 3:** Tone/Humor Analysis → Validate voice consistency
4. **Phase 3.5:** **Test Harness Execution** ← Run this
   - All validation checks
   - Link integrity verification
   - Auto-fix broken links visually
5. **Phase 4:** Image Injection → Add illustration links
6. **Phase 5:** Deployment → Only if tests pass

**Command Integration:**

```python
# In story_enhancement_orchestrator.py

def run_phase_3_5_validation():
    """Run test harness before image injection."""
    result = subprocess.run(
        ['pytest', 'tests/orchestrators/test_story_enhancement_harness.py', '-v'],
        capture_output=True
    )
    
    if result.returncode != 0:
        print("❌ Validation failed. Fix issues before proceeding.")
        generate_test_report(result.stdout)
        return False
    
    print("✅ All validation tests passed. Proceeding to image injection.")
    return True
```

---

## 🚨 Common Issues

### "Miss G found in story"

**Fix:** Run Story Validation Module auto-fix
```bash
python -m src.orchestrators.story_validation_module --auto-fix
```

### "Asif Hussain not introduced"

**Fix:** Auto-insert introduction
```python
# Validation module will insert at first "Mr. Codenstein" mention:
# "Asif Hussain, more commonly known by his friends as 'Mr. Codenstein'"
```

### "Features appear before implementation"

**Fix:** Manual chapter reordering or validation module chronology check

### "Broken navigation links"

**Fix:** CSS already applied (visual disabling). Develop features to fix permanently.

---

## 📞 Support

**Author:** Asif Hussain  
**Repository:** github.com/asifhussain60/CORTEX  
**Issue Tracker:** GitHub Issues

---

**Last Updated:** December 11, 2025  
**Version:** 1.0.0

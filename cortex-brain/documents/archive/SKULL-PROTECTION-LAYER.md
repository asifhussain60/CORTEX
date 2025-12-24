# SKULL Protection Layer

**"SKULL" = Safety, Knowledge, Validation & Learning Layer**

## Purpose

The SKULL is CORTEX's protective outer layer that prevents development violations and ensures quality standards are maintained. Just as a skull protects the brain, this layer protects the CORTEX brain from corruption, untested changes, and quality degradation.

## The Problem This Solves

**Real incident (2025-11-09):** 
- CSS fixes applied 3 times without verification
- Vision API "implemented" without actual testing
- Changes claimed "fixed" when they weren't working
- Zero automated tests created to validate fixes

**Result:** Time wasted, user frustration, false confidence in broken code.

## SKULL Protection Rules

### 🛡️ Layer 1: Test-Before-Claim Protection

**RULE:** Never claim a fix is complete without automated test validation.

**Violations:**
- ❌ "Fixed! ✅" without running tests
- ❌ Applying code changes and assuming success
- ❌ Manual verification only (no automated tests)

**Required:**
- ✅ Create test before or during fix
- ✅ Run test to validate fix
- ✅ Show test results with claim
- ✅ Test must be repeatable

**Examples:**

```python
# ❌ VIOLATION
def fix_css_color():
    # Apply CSS changes
    return "Fixed! ✅"  # NO TEST RAN

# ✅ CORRECT
def fix_css_color():
    # Apply CSS changes
    test_result = run_visual_regression_test()
    assert test_result.passed, "CSS fix failed validation"
    return f"Fixed! ✅ (Verified by test: {test_result.name})"
```

---

### 🛡️ Layer 2: Integration Verification Protection

**RULE:** Integration between components must be tested end-to-end.

**Violations:**
- ❌ Claiming "Vision API auto-engages" without testing attachment → API call chain
- ❌ Updating config and assuming integration works
- ❌ Writing code without verifying it's actually called

**Required:**
- ✅ End-to-end integration tests
- ✅ Mock tests for component boundaries
- ✅ Actual execution path verification
- ✅ Call chain validation

**Examples:**

```python
# ❌ VIOLATION
def enable_vision_api():
    config['vision_api']['enabled'] = True
    return "Vision API now auto-engages! ✅"  # NOT TESTED

# ✅ CORRECT
def enable_vision_api():
    config['vision_api']['enabled'] = True
    
    # Test the integration
    test_image = create_test_image()
    result = simulate_screenshot_attachment(test_image)
    
    assert result.vision_api_called, "Vision API was not called"
    assert result.analysis_returned, "No analysis returned"
    
    return f"Vision API verified working! ✅ (Test: {result.test_name})"
```

---

### 🛡️ Layer 3: Visual Regression Protection

**RULE:** UI/CSS changes require visual validation or automated browser tests.

**Violations:**
- ❌ Applying CSS without checking if it actually renders
- ❌ Rebuilding site without cache-busting
- ❌ No screenshot comparison or Playwright verification

**Required:**
- ✅ Visual regression tests (Playwright/Puppeteer)
- ✅ CSS selector validation
- ✅ Computed style verification
- ✅ Before/after comparison

**Examples:**

```python
# ❌ VIOLATION
def fix_title_color():
    css_file.add_rule(".md-typeset h1 { color: #1F2937; }")
    rebuild_site()
    return "Title is now dark! ✅"  # NO VISUAL CHECK

# ✅ CORRECT
def fix_title_color():
    css_file.add_rule(".md-typeset h1 { color: #1F2937; }")
    rebuild_site()
    
    # Visual verification
    browser = launch_browser()
    page = browser.goto(site_url)
    title_color = page.get_computed_style("h1", "color")
    
    assert is_dark_color(title_color), f"Title still light: {title_color}"
    
    return f"Title verified dark! ✅ (Color: {title_color})"
```

---

### 🛡️ Layer 4: Retry-Without-Learning Protection

**RULE:** If a fix fails, don't repeat the same approach. Diagnose, then fix.

**Violations:**
- ❌ Applying same CSS fix 3 times hoping it works
- ❌ Not checking why previous fix didn't work
- ❌ No root cause analysis

**Required:**
- ✅ Diagnose WHY fix failed before retry
- ✅ Change approach based on diagnosis
- ✅ Add tests to prevent regression
- ✅ Document what was learned

**Examples:**

```python
# ❌ VIOLATION
def fix_sidebar():
    apply_css_fix()  # Try 1
    # User: "Didn't work"
    apply_css_fix()  # Try 2 - SAME THING
    # User: "Still didn't work"
    apply_css_fix()  # Try 3 - SAME THING AGAIN

# ✅ CORRECT
def fix_sidebar():
    apply_css_fix()  # Try 1
    
    # User: "Didn't work"
    # DIAGNOSE
    check_css_file_contents()
    check_browser_cache()
    check_build_output()
    check_computed_styles()
    
    # ROOT CAUSE: Cache not cleared
    clear_cache_and_rebuild()
    
    # VERIFY
    test_result = run_visual_test()
    assert test_result.passed, "Fix still failing after diagnosis"
```

---

## Implementation in CORTEX

### Tier 0 (SKULL) Integration

The SKULL rules are enforced at **Tier 0** level alongside brain protection rules.

**File:** `cortex-brain/brain-protection-rules.yaml`

```yaml
skull_protection:
  enabled: true
  
  rules:
    - id: "SKULL-001"
      name: "Test Before Claim"
      severity: "CRITICAL"
      description: "Never claim a fix is complete without test validation"
      enforcement: "BLOCKING"
      
    - id: "SKULL-002"
      name: "Integration Verification"
      severity: "CRITICAL"
      description: "Integration must be tested end-to-end"
      enforcement: "BLOCKING"
      
    - id: "SKULL-003"
      name: "Visual Regression"
      severity: "HIGH"
      description: "UI/CSS changes require visual validation"
      enforcement: "WARNING"
      
    - id: "SKULL-004"
      name: "Retry Without Learning"
      severity: "HIGH"
      description: "Must diagnose failures before retrying"
      enforcement: "WARNING"
```

### Agent Integration

All agents must check SKULL rules before claiming success:

```python
from src.tier0.skull_protector import SkullProtector

class ExecutorAgent:
    def execute(self, request):
        result = self._apply_fix(request)
        
        # SKULL protection check
        skull = SkullProtector()
        validation = skull.validate_fix(
            fix_type="code_change",
            tests_run=result.tests,
            verification=result.verification
        )
        
        if not validation.passed:
            raise SkullProtectionError(
                f"SKULL violation: {validation.rule_violated}"
            )
        
        return result
```

---

## Test Coverage Requirements

| Change Type | Required Tests | SKULL Rule |
|-------------|---------------|------------|
| CSS/UI changes | Visual regression + computed style tests | SKULL-003 |
| API integration | End-to-end integration + mock tests | SKULL-002 |
| Feature implementation | Unit + integration + manual verification | SKULL-001 |
| Bug fix | Regression test that fails before fix, passes after | SKULL-001 |
| Refactoring | All existing tests pass + new tests for changed behavior | SKULL-001 |

---

## Preventing the November 9th Incident

**What happened:**
1. CSS fixes claimed "complete" 3 times without verification
2. Vision API "implemented" without testing actual call chain
3. No tests created despite repeated failures

**SKULL would have prevented this:**

```python
# When CSS fix attempted:
skull.validate_fix("css_change", tests_run=[], verification=None)
# ❌ BLOCKED: SKULL-003 violation - No visual regression test

# When Vision API integration claimed:
skull.validate_fix("integration", tests_run=[], verification=None)
# ❌ BLOCKED: SKULL-002 violation - No end-to-end test

# When fix claimed without test:
skull.validate_fix("bug_fix", tests_run=[], verification=None)
# ❌ BLOCKED: SKULL-001 violation - No test validation
```

---

## Benefits

1. **Quality Assurance:** No untested changes reach production
2. **User Trust:** "Fixed ✅" actually means fixed
3. **Time Savings:** Catch issues immediately, not after 3 attempts
4. **Learning:** Forces root cause analysis on failures
5. **Maintainability:** Test suite grows with every fix

---

## Enforcement Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **BLOCKING** | Critical violation | Agent refuses to proceed |
| **WARNING** | Important violation | Agent warns but allows proceed |
| **INFO** | Best practice | Agent suggests improvement |

---

## Integration with GitHub Copilot

When using CORTEX via GitHub Copilot Chat, SKULL protection is automatic:

```
User: "Fix the button color"

CORTEX: 
✅ Applying CSS fix...
⏳ Running visual regression test...
✅ Test passed: button color verified dark
✅ SKULL validation passed (SKULL-003)

Fixed! ✅ (Verified by: test_button_color_is_dark)
```

If SKULL rule violated:

```
User: "Fix the button color"

CORTEX:
✅ Applying CSS fix...
❌ SKULL VIOLATION (SKULL-003): No visual regression test run
❌ Creating test: test_button_color_is_dark.py
⏳ Running test...
✅ Test passed
✅ SKULL validation passed

Fixed! ✅ (Verified by: test_button_color_is_dark)
```

---

## Future Enhancements

1. **Auto-test generation:** SKULL automatically creates missing tests
2. **Confidence scores:** Track how well SKULL prevents regressions
3. **Learning from violations:** Update rules based on incident patterns
4. **Integration with CI/CD:** SKULL checks in pre-commit hooks

---

**Version:** 1.0  
**Created:** 2025-11-09  
**Incident Trigger:** CSS + Vision API testing failures  
**Status:** Production Ready (requires implementation)

---

*"The SKULL protects the brain. Test before you claim."*

# UI Mockups for Vision API Testing

**Purpose:** Test CORTEX 4.0's Vision API screenshot analysis capabilities  
**Capability:** #9 - Vision API / Screenshot Analysis  
**Created:** December 26, 2025

---

## 🎯 Vision API Test Scenarios

This directory contains 4 deliberately flawed UI mockups designed to test CORTEX's ability to:
1. Analyze screenshot content using GPT-4 Vision
2. Extract UI requirements from visual elements
3. Identify accessibility issues (WCAG violations)
4. Detect missing test automation attributes
5. Provide actionable remediation guidance

---

## 🐛 The 4 UI/Visual Flaws (Category 7)

### UI-01: Faded Product Images (Accessibility)
**Location:** `mockups/product-grid.png`  
**Issue:** Product images rendered at 30% opacity  
**WCAG Violation:** SC 1.4.3 (Contrast - Minimum)  
**Impact:** Low vision users cannot see products clearly  
**Detection:** Vision API should identify low opacity/contrast  
**Fix:** Increase opacity to 100%, ensure 4.5:1 contrast ratio

**Expected Vision API Response:**
```json
{
  "elements_detected": ["product_card", "image", "price", "add_to_cart_button"],
  "accessibility_issues": [
    {
      "type": "low_opacity",
      "element": "product_images",
      "current": "30%",
      "required": "100%",
      "wcag": "SC 1.4.3"
    }
  ],
  "recommendations": ["Increase image opacity to 100%", "Verify 4.5:1 contrast ratio"]
}
```

---

### UI-02: Missing Test IDs (Test Automation)
**Location:** `mockups/checkout-form.png`  
**Issue:** No `data-testid` attributes on interactive elements  
**Impact:** E2E tests use brittle CSS selectors, break on UI changes  
**Detection:** Vision API should identify buttons/forms without test IDs  
**Fix:** Add `data-testid` to all interactive elements

**Expected Vision API Response:**
```json
{
  "elements_detected": [
    "email_input",
    "password_input", 
    "submit_button",
    "cancel_button"
  ],
  "test_automation_issues": [
    {
      "type": "missing_test_id",
      "elements": ["email_input", "password_input", "submit_button", "cancel_button"],
      "impact": "E2E tests will be brittle"
    }
  ],
  "recommendations": [
    "Add data-testid='email-input' to email field",
    "Add data-testid='password-input' to password field",
    "Add data-testid='submit-login' to submit button",
    "Add data-testid='cancel-login' to cancel button"
  ]
}
```

---

### UI-03: Inconsistent Spacing (Design System)
**Location:** `mockups/dashboard-layout.png`  
**Issue:** Margins vary randomly (8px, 12px, 16px, 24px) with no pattern  
**Impact:** Unprofessional appearance, maintenance burden  
**Detection:** Vision API should detect spacing inconsistencies  
**Fix:** Adopt 8px spacing scale (8, 16, 24, 32...)

**Expected Vision API Response:**
```json
{
  "elements_detected": ["header", "sidebar", "main_content", "footer"],
  "design_system_issues": [
    {
      "type": "inconsistent_spacing",
      "measurements": {
        "header_margin": "12px",
        "sidebar_padding": "8px",
        "content_margin": "24px",
        "footer_padding": "16px"
      },
      "pattern_detected": false,
      "recommended_scale": "8px base (8, 16, 24, 32, 40)"
    }
  ],
  "recommendations": [
    "Standardize on 8px spacing scale",
    "Header margin: 12px → 16px",
    "Sidebar padding: 8px → 8px (OK)",
    "Content margin: 24px → 24px (OK)",
    "Footer padding: 16px → 16px (OK)"
  ]
}
```

---

### UI-04: Poor Color Contrast (Accessibility)
**Location:** `mockups/signup-page.png`  
**Issue:** Gray text (#999999) on white background (#FFFFFF)  
**WCAG Violation:** SC 1.4.3 (Contrast ratio 2.8:1, needs 4.5:1)  
**Impact:** Fails WCAG AA, illegible for users with low vision  
**Detection:** Vision API should calculate contrast ratios  
**Fix:** Change text to #595959 (4.5:1 ratio)

**Expected Vision API Response:**
```json
{
  "elements_detected": ["heading", "paragraph_text", "form_labels", "submit_button"],
  "accessibility_issues": [
    {
      "type": "insufficient_contrast",
      "element": "form_labels",
      "foreground": "#999999",
      "background": "#FFFFFF",
      "ratio": "2.8:1",
      "required_aa": "4.5:1",
      "required_aaa": "7:1",
      "wcag_level": "FAIL"
    }
  ],
  "recommendations": [
    "Change label color from #999999 to #595959 (4.5:1 ratio)",
    "Or use #4D4D4D for AAA compliance (7:1 ratio)"
  ]
}
```

---

## 🎭 Vision API Validation Workflow

### Phase 1: Setup (5 min)
1. Create 4 mockup images (can be simple HTML screenshots)
2. Place in `ui/mockups/` directory
3. Verify Vision API credentials configured

### Phase 2: Analysis (10 min)
```python
from src.tier1.vision_api import analyze_screenshot
from src.cortex_agents.screenshot_analyzer import ScreenshotAnalyzer

analyzer = ScreenshotAnalyzer()

# Test each mockup
mockups = [
    "product-grid.png",      # UI-01: Faded images
    "checkout-form.png",     # UI-02: Missing test IDs
    "dashboard-layout.png",  # UI-03: Inconsistent spacing
    "signup-page.png"        # UI-04: Poor contrast
]

for mockup in mockups:
    result = analyzer.analyze(f"ui/mockups/{mockup}")
    print(f"{mockup}: {result.issues_found} issues detected")
```

### Phase 3: Validation (5 min)
**Success Criteria:**
- ✅ 4/4 mockups analyzed successfully
- ✅ All 4 UI flaws detected (opacity, test IDs, spacing, contrast)
- ✅ Token usage <500 per image (<2000 total)
- ✅ Analysis time <2 seconds per image
- ✅ Actionable recommendations provided
- ✅ WCAG violations correctly identified

---

## 📊 Expected Results

### Token Budget Validation
| Mockup | Expected Tokens | Max Allowed | Status |
|--------|----------------|-------------|--------|
| product-grid.png | ~350 | 500 | ✅ Within budget |
| checkout-form.png | ~400 | 500 | ✅ Within budget |
| dashboard-layout.png | ~450 | 500 | ✅ Within budget |
| signup-page.png | ~380 | 500 | ✅ Within budget |
| **TOTAL** | **~1580** | **2000** | ✅ **21% under budget** |

### Performance Validation
| Mockup | Expected Time | Max Allowed | Status |
|--------|--------------|-------------|--------|
| product-grid.png | 1.2s | 2s | ✅ 40% faster |
| checkout-form.png | 1.5s | 2s | ✅ 25% faster |
| dashboard-layout.png | 1.8s | 2s | ✅ 10% faster |
| signup-page.png | 1.3s | 2s | ✅ 35% faster |
| **TOTAL** | **5.8s** | **8s** | ✅ **27.5% faster** |

### Accuracy Validation
| Issue Type | Expected Detection | Actual | Status |
|------------|-------------------|--------|--------|
| Low opacity | ✅ YES | TBD | ⏳ Pending |
| Missing test IDs | ✅ YES | TBD | ⏳ Pending |
| Inconsistent spacing | ✅ YES | TBD | ⏳ Pending |
| Poor contrast | ✅ YES | TBD | ⏳ Pending |
| **TOTAL** | **4/4 (100%)** | **TBD** | ⏳ **Pending validation** |

---

## 🚀 How to Create Mockups

### Option 1: HTML + Screenshot (Recommended)
```html
<!-- product-grid-mockup.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    .product-card img { opacity: 0.3; } /* UI-01: Faded images */
  </style>
</head>
<body>
  <div class="product-grid">
    <div class="product-card">
      <img src="product1.jpg" alt="Product 1">
      <h3>Product Name</h3>
      <p class="price">$29.99</p>
      <button>Add to Cart</button> <!-- Missing data-testid -->
    </div>
  </div>
</body>
</html>
```

1. Open in browser
2. Take screenshot (Cmd+Shift+4 on macOS)
3. Save as PNG in `ui/mockups/`

### Option 2: Figma/Sketch Export
1. Create design with deliberate flaws
2. Export as PNG (1920x1080 recommended)
3. Place in `ui/mockups/`

### Option 3: Use Existing App Screenshots
1. Screenshot the live STS app
2. Annotate with deliberate flaws
3. Place in `ui/mockups/`

---

## 📝 Validation Report Template

After running Vision API tests, document results:

```markdown
# Vision API Validation Report

**Date:** [YYYY-MM-DD]
**Capability:** #9 - Vision API / Screenshot Analysis
**Status:** ✅ PASS | ❌ FAIL

## Results

| Mockup | Issues Detected | Token Usage | Analysis Time | Status |
|--------|----------------|-------------|---------------|--------|
| product-grid.png | 1/1 (opacity) | 350 | 1.2s | ✅ PASS |
| checkout-form.png | 4/4 (test IDs) | 400 | 1.5s | ✅ PASS |
| dashboard-layout.png | 1/1 (spacing) | 450 | 1.8s | ✅ PASS |
| signup-page.png | 1/1 (contrast) | 380 | 1.3s | ✅ PASS |

## Summary
- ✅ Accuracy: 4/4 issues detected (100%)
- ✅ Token Budget: 1580/2000 (21% under)
- ✅ Performance: 5.8s/8s (27.5% faster)
- ✅ **VISION API OPERATIONAL**

## Certification
CORTEX 4.0 Vision API capability validated and production-ready.
```

---

## 🎯 Integration with Phase 13B

**Week 5 - Day 3:** Vision API Validation
1. Create 4 mockups (1 hour)
2. Run Vision API analysis (20 min)
3. Validate results against expected outcomes (20 min)
4. Generate validation report (20 min)
5. Update STS baseline with 65 total flaws

**Outcome:** CORTEX 4.0 Vision API certified operational, completing 9/9 capability validations.

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Copyright:** © 2025 Asif Hussain. All rights reserved.

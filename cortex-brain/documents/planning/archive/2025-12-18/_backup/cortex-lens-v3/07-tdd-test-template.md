# CORTEX Lens V3 - TDD Test Harness Template

**Version:** 1.0  
**Date:** December 14, 2025  
**Purpose:** Template for creating test suites for each view/sub-plan  
**Reference Implementation:** Sub-Plan 1 (Landing Page)

---

## 🎯 Purpose

This template ensures EVERY sub-plan follows TDD workflow with comprehensive test coverage to prevent regressions.

**Brain Protection Rules:**
- `TDD_ENFORCEMENT`: RED→GREEN→REFACTOR mandatory
- `RED_PHASE_VALIDATION`: Tests must fail before implementation
- `TDD_TEST_FILE_VALIDATION`: All production code must have tests

---

## 📋 Test Suite Structure

### File Organization
```
cortex-lens-output/
└── mock-{view-name}/
    ├── index.html              # View implementation
    ├── assets/
    │   ├── {view}-styles.css   # View-specific styles
    │   └── {view}-script.js    # View-specific JavaScript
    └── tests/
        ├── {view}.test.js      # Test suite
        └── test-runner.html    # Browser-based test runner
```

### Test Categories (Minimum Required)

Every test suite MUST include these 5 categories:

#### 1. **HTML Structure Tests**
Validate DOM elements exist and are correctly structured.

**Example Assertions:**
```javascript
// Core elements
assert(!!document.querySelector('.main-container'), 'Main container exists');
assert(!!document.querySelector('.view-header'), 'View header exists');

// Component counts
const items = document.querySelectorAll('.item');
assert(items.length === expectedCount, `Expected ${expectedCount} items`);

// Hierarchy
const parent = document.querySelector('.parent');
const child = parent.querySelector('.child');
assert(!!child, 'Child element exists within parent');
```

#### 2. **Layout Behavior Tests**
Validate positioning, sizing, and scrolling behavior.

**Example Assertions:**
```javascript
// Positioning
const element = document.querySelector('.fixed-element');
const style = window.getComputedStyle(element);
assert(style.position === 'fixed', 'Element is fixed positioned');

// Sizing
const width = parseInt(style.width);
assert(width === 280, `Expected 280px, got ${width}px`);

// Scrolling
assert(element.scrollHeight > window.innerHeight, 'Content is scrollable');
```

#### 3. **CSS Styling Tests**
Validate design system compliance (glassmorphism, colors, effects).

**Example Assertions:**
```javascript
// Glassmorphism
const card = document.querySelector('.glass-card');
const cardStyle = window.getComputedStyle(card);
assert(cardStyle.backdropFilter.includes('blur'), 'Card has backdrop blur');

// Effects
assert(element.filter.includes('drop-shadow'), 'Element has drop-shadow');

// Theme
const theme = document.documentElement.getAttribute('data-theme');
assert(['dark', 'light'].includes(theme), 'Valid theme applied');
```

#### 4. **Responsiveness Tests**
Validate responsive breakpoints and layout adaptations.

**Example Assertions:**
```javascript
// Grid/Flex layouts
assert(gridStyle.display === 'grid', 'Uses CSS Grid');
assert(flexStyle.display === 'flex', 'Uses Flexbox');

// Media queries exist
const hasMediaQueries = Array.from(document.styleSheets)
    .some(sheet => {
        try {
            return Array.from(sheet.cssRules || [])
                .some(rule => rule.type === CSSRule.MEDIA_RULE);
        } catch (e) { return false; }
    });
assert(hasMediaQueries, 'Responsive media queries defined');
```

#### 5. **JavaScript Functionality Tests**
Validate interactive behavior, event handlers, data operations.

**Example Assertions:**
```javascript
// Functions exist
assert(typeof myFunction === 'function', 'Function defined');

// Event handling
button.click();
await wait(100);
assert(element.classList.contains('active'), 'Click handler works');

// Data validation
assert(dataObject.property !== undefined, 'Data property exists');
assert(dataObject.array.length > 0, 'Data array populated');

// Library loading
assert(typeof ExternalLib !== 'undefined', 'External library loaded');
```

---

## 🧪 Test Runner Template

**File:** `tests/test-runner.html`

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <title>CORTEX {ViewName} - Test Runner</title>
    <link rel="stylesheet" href="../assets/{view}-styles.css">
    <style>
        #test-console {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 300px;
            background: rgba(10, 25, 47, 0.95);
            color: #fff;
            font-family: monospace;
            padding: 20px;
            overflow-y: auto;
            z-index: 10000;
        }
        .test-header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(0, 212, 255, 0.1);
            padding: 10px 20px;
            z-index: 10001;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="test-header">
        <h2>🧪 CORTEX {ViewName} Test Runner</h2>
    </div>

    <!-- Copy full view HTML here -->
    
    <div id="test-console">
        <pre id="console-output">Loading tests...</pre>
    </div>

    <script src="../assets/{view}-script.js"></script>
    <script>
        // Intercept console for test output
        const consoleOutput = document.getElementById('console-output');
        const originalLog = console.log;
        console.log = function(...args) {
            originalLog.apply(console, args);
            consoleOutput.textContent += args.join(' ') + '\n';
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        };
    </script>
    <script src="{view}.test.js"></script>
</body>
</html>
```

---

## 🧪 Test Suite JavaScript Template

**File:** `tests/{view}.test.js`

```javascript
const ViewTests = {
    results: [],
    
    async runAll() {
        console.log('🧪 Starting {ViewName} Tests...\n');
        this.results = [];
        
        await this.testStructure();
        await this.testLayout();
        await this.testStyling();
        await this.testResponsiveness();
        await this.testJavaScript();
        
        this.reportResults();
    },
    
    assert(condition, testName, errorMsg = '') {
        const result = {
            name: testName,
            passed: condition,
            error: condition ? null : errorMsg
        };
        this.results.push(result);
        
        const icon = condition ? '✅' : '❌';
        console.log(`${icon} ${testName}${errorMsg ? `: ${errorMsg}` : ''}`);
    },
    
    async testStructure() {
        console.log('\n📋 Testing HTML Structure...');
        // Add structure tests here
    },
    
    async testLayout() {
        console.log('\n📐 Testing Layout Behavior...');
        // Add layout tests here
    },
    
    async testStyling() {
        console.log('\n🎨 Testing CSS Styling...');
        // Add styling tests here
    },
    
    async testResponsiveness() {
        console.log('\n📱 Testing Responsiveness...');
        // Add responsive tests here
    },
    
    async testJavaScript() {
        console.log('\n⚙️ Testing JavaScript Functionality...');
        // Add JS tests here
    },
    
    reportResults() {
        console.log('\n' + '='.repeat(50));
        console.log('📊 TEST RESULTS SUMMARY');
        console.log('='.repeat(50));
        
        const total = this.results.length;
        const passed = this.results.filter(r => r.passed).length;
        const failed = total - passed;
        const passRate = ((passed / total) * 100).toFixed(1);
        
        console.log(`Total Tests: ${total}`);
        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`Pass Rate: ${passRate}%\n`);
        
        if (failed > 0) {
            console.log('Failed Tests:');
            this.results.filter(r => !r.passed).forEach(r => {
                console.log(`  ❌ ${r.name}`);
                if (r.error) console.log(`     ${r.error}`);
            });
        }
        
        // Visual indicator
        const resultDiv = document.createElement('div');
        resultDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 20px;
            background: ${failed === 0 ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 9999;
            font-family: monospace;
        `;
        resultDiv.innerHTML = `
            <strong>${failed === 0 ? '✅ ALL TESTS PASSED' : '❌ TESTS FAILED'}</strong><br>
            ${passed}/${total} tests passed (${passRate}%)
        `;
        document.body.appendChild(resultDiv);
        setTimeout(() => resultDiv.remove(), 5000);
        
        return { total, passed, failed, passRate, allPassed: failed === 0 };
    }
};

// Auto-run on load
window.addEventListener('load', () => {
    setTimeout(() => ViewTests.runAll(), 1000);
});

window.ViewTests = ViewTests;
```

---

## 📊 Test Coverage Requirements

### Minimum Thresholds

| Category | Minimum Coverage | Ideal Coverage |
|----------|------------------|----------------|
| Structure | 100% of major elements | 100% all elements |
| Layout | All positioning/sizing | + scroll behavior |
| Styling | Core design system | + all effects |
| Responsive | Breakpoints exist | + behavior tested |
| JavaScript | All public functions | + event handlers |

### Pass Rate Requirements

- ✅ **100% pass rate** required before moving to next sub-plan
- ⚠️ **<100%** = Fix failing tests OR update requirements
- ❌ **<90%** = STOP - Major issues, do not proceed

---

## 🔄 TDD Workflow Integration

### RED Phase (Write Failing Tests)
1. Copy this template to new view directory
2. Define test cases for all 5 categories
3. Run tests → ALL should fail (no implementation yet)
4. Document expected behavior in test assertions

### GREEN Phase (Implement to Pass)
1. Build HTML structure
2. Add CSS styling
3. Implement JavaScript
4. Run tests → Iteratively fix until 100% pass

### REFACTOR Phase (Optimize)
1. Remove code duplication
2. Improve performance
3. Enhance accessibility
4. Run tests → Must still pass at 100%

### Regression Protection
1. Bug found → Add test case first
2. Fix bug
3. Verify test now passes
4. Test prevents regression forever

---

## 🚀 Usage Per Sub-Plan

### Sub-Plan Checklist

**Before Starting Implementation:**
- [ ] Copy test template to view directory
- [ ] Define test cases (RED phase)
- [ ] Run tests → Confirm all fail
- [ ] Document in sub-plan markdown

**During Implementation:**
- [ ] Run tests frequently
- [ ] Fix code until tests pass
- [ ] Add tests for new functionality
- [ ] Maintain 100% pass rate

**Before User Review:**
- [ ] All tests passing (100%)
- [ ] Test runner documented
- [ ] Regression tests added
- [ ] Lessons learned captured

**Before Moving to Next Sub-Plan:**
- [ ] User approval obtained
- [ ] Tests committed to git
- [ ] Master sub-plan updated
- [ ] Template updated if needed

---

## 📚 Reference Implementation

**See:** `cortex-lens-output/mock-landing/tests/`

- **Test Suite:** `landing-page.test.js` (30+ assertions)
- **Test Runner:** `test-runner.html`
- **Coverage:** 100% pass rate
- **Categories:** All 5 required categories implemented

**This is the GOLD STANDARD for all future sub-plans.**

---

**Last Updated:** December 14, 2025  
**Applies To:** ALL CORTEX Lens V3 sub-plans  
**Enforcement:** Mandatory via Brain Protection (TDD_ENFORCEMENT)

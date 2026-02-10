# Frontend Anti-Patterns

**Purpose:** Document common mistakes to avoid in frontend development  
**Source:** Lessons learned from production incidents  
**Updated:** 2026-02-03

---

## Overview

This document catalogs frontend anti-patterns discovered through actual production issues. Each anti-pattern includes:
- Description of the mistake
- Why it's problematic
- Real-world impact
- Correct approach
- Detection strategy

---

## Table of Contents

1. [Hidden Element Rendering](#1-hidden-element-rendering)
2. [Silent DOM API Failures](#2-silent-dom-api-failures)
3. [Ad-Hoc Testing](#3-ad-hoc-testing)
4. [Manual Test Execution](#4-manual-test-execution)

---

## 1. Hidden Element Rendering

**Source:** Chat01 Incident (2026-02-03)

### ❌ Anti-Pattern

```javascript
// BAD: Assumes element is always visible
function renderChart(containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '<canvas id="chart"></canvas>'; // Crashes if null
  new Chart('chart', config);
}

// Breaks when called for hidden tab (aria-hidden="true")
renderChart('hidden-container'); // SILENT FAILURE
```

### Why It's Bad

| Issue | Impact |
|-------|--------|
| **Silent Failure** | No error thrown, user sees empty container |
| **Inconsistent Behavior** | Works for visible tabs, fails for hidden |
| **Poor UX** | Dashboard appears broken |
| **Hard to Debug** | No console errors to trace |

### Real-World Impact

**Chat01 Incident:**
- 5 of 5 dashboard containers broken
- 100% failure rate for hidden tabs
- Zero console errors (silent failure)
- Required deep investigation to diagnose

### ✅ Correct Approach

```javascript
// GOOD: Check for null, queue if hidden
function renderChartSafely(containerId) {
  const container = document.getElementById(containerId);
  
  if (!container) {
    // Element is hidden or not yet rendered
    console.warn(`Container ${containerId} not found, queuing render`);
    DeferredRenderer.queueRender(
      () => renderChartSafely(containerId),
      `Chart: ${containerId}`
    );
    return;
  }
  
  // Element is visible - safe to render
  container.innerHTML = '<canvas id="chart"></canvas>';
  new Chart('chart', config);
}
```

### Detection Strategy

**Static Analysis:**
```javascript
// ESLint rule to catch unsafe DOM access
"no-unsafe-dom-access": [
  "error",
  {
    "require-null-check": ["getElementById", "querySelector"]
  }
]
```

**Testing:**
```javascript
describe('Render function', () => {
  it('should handle missing element gracefully', () => {
    // Test with non-existent ID
    expect(() => renderChart('nonexistent')).not.toThrow();
  });
  
  it('should queue render for hidden element', () => {
    // Mock hidden element (aria-hidden="true")
    const spy = jest.spyOn(DeferredRenderer, 'queueRender');
    renderChart('hidden-id');
    expect(spy).toHaveBeenCalled();
  });
});
```

---

## 2. Silent DOM API Failures

**Source:** Chat01 Incident (2026-02-03)

### ❌ Anti-Pattern

```javascript
// BAD: No error handling, assumes success
document.getElementById('container').innerHTML = '<div>Content</div>';
document.querySelector('.chart').classList.add('active');
document.querySelectorAll('.item').forEach(item => item.remove());
```

### Why It's Bad

| Issue | Impact |
|-------|--------|
| **Uncaught Exceptions** | Crashes entire script execution |
| **No Fallback** | User sees broken UI with no recovery |
| **Debug Difficulty** | Stack trace may not point to root cause |
| **Cascading Failures** | One null breaks entire render chain |

### Real-World Impact

**Common Scenarios:**
- Tab switching breaks due to aria-hidden
- Modal content fails to render
- Accordion panels show empty
- Dynamic content injection crashes

### ✅ Correct Approach

```javascript
// GOOD: Explicit null checks with error handling
function safeRender(containerId) {
  const container = document.getElementById(containerId);
  
  if (!container) {
    console.error(`Container ${containerId} not found`);
    // Queue for later OR show user-friendly error
    return { success: false, reason: 'ELEMENT_NOT_FOUND' };
  }
  
  try {
    container.innerHTML = '<div>Content</div>';
    return { success: true };
  } catch (error) {
    console.error(`Render failed for ${containerId}:`, error);
    return { success: false, reason: 'RENDER_ERROR', error };
  }
}
```

### Detection Strategy

**TypeScript strict null checks:**
```typescript
// compiler catches potential null access
const container: HTMLElement | null = document.getElementById('id');
container.innerHTML = 'content'; // ERROR: Object is possibly 'null'

// Fix: Add null check
if (container) {
  container.innerHTML = 'content'; // OK
}
```

---

## 3. Ad-Hoc Testing

**Source:** Chat01 Incident (2026-02-03)

### ❌ Anti-Pattern

```html
<!-- BAD: Custom HTML test runner without framework -->
<!DOCTYPE html>
<html>
<head>
  <title>Manual Test</title>
  <script>
    function runTests() {
      console.log('Test 1: Queue render');
      DeferredRenderer.queueRender(() => {});
      console.log(DeferredRenderer.renderQueue.length > 0 ? 'PASS' : 'FAIL');
      
      console.log('Test 2: Flush queue');
      DeferredRenderer.flushQueue();
      console.log(DeferredRenderer.renderQueue.length === 0 ? 'PASS' : 'FAIL');
    }
  </script>
</head>
<body onload="runTests()">
  <h1>Test Results (check console)</h1>
</body>
</html>
```

### Why It's Bad

| Issue | Impact |
|-------|--------|
| **No Assertions** | Manual verification required (check console) |
| **No Coverage** | Can't track which code is tested |
| **No CI/CD Integration** | Must run manually |
| **Inconsistent Patterns** | Each test file different format |
| **Hard to Maintain** | No shared utilities or setup |

### Real-World Impact

**Chat01 Example:**
- 20 tests created as ad-hoc HTML files
- No automated assertions
- Manual console inspection required
- No coverage reporting
- Can't run in CI/CD pipeline

### ✅ Correct Approach

```javascript
// GOOD: Standard test framework (Vitest/Jest)
import { describe, it, expect, beforeEach } from 'vitest';
import { DeferredRenderer } from './DeferredRenderer';

describe('DeferredRenderer', () => {
  beforeEach(() => {
    DeferredRenderer.renderQueue = []; // Reset state
  });
  
  it('should queue render function', () => {
    const mockRender = vi.fn();
    DeferredRenderer.queueRender(mockRender);
    
    expect(DeferredRenderer.renderQueue).toHaveLength(1);
    expect(DeferredRenderer.renderQueue[0].fn).toBe(mockRender);
  });
  
  it('should flush queue and execute renders', () => {
    const mockRender1 = vi.fn();
    const mockRender2 = vi.fn();
    
    DeferredRenderer.queueRender(mockRender1);
    DeferredRenderer.queueRender(mockRender2);
    DeferredRenderer.flushQueue();
    
    expect(mockRender1).toHaveBeenCalledOnce();
    expect(mockRender2).toHaveBeenCalledOnce();
    expect(DeferredRenderer.renderQueue).toHaveLength(0);
  });
});
```

**Benefits:**
- ✅ Automated assertions (no manual checking)
- ✅ Coverage reports (Istanbul/c8)
- ✅ CI/CD ready (npm test)
- ✅ Consistent patterns across all tests
- ✅ Shared utilities (beforeEach, fixtures)

### Migration Path

```bash
# 1. Install test framework
npm install --save-dev vitest @vitest/ui jsdom

# 2. Configure vitest.config.js
export default {
  test: {
    environment: 'jsdom',
    coverage: {
      provider: 'c8',
      reporter: ['text', 'html', 'lcov']
    }
  }
}

# 3. Convert ad-hoc tests to Vitest
# Before: tests/test_manual.html
# After:  tests/DeferredRenderer.test.js

# 4. Run tests
npm test                    # Run all tests
npm test -- --coverage      # With coverage
npm test -- --ui            # Visual test UI
```

---

## 4. Manual Test Execution

**Source:** Chat01 Incident (2026-02-03)

### ❌ Anti-Pattern

```bash
# BAD: Manual test execution only
# Developer workflow:
1. Write test file
2. Open browser
3. Manually navigate to test.html
4. Check console for PASS/FAIL
5. Repeat for each test file
6. ❌ Forget to run tests before commit
```

### Why It's Bad

| Issue | Impact |
|-------|--------|
| **Human Error** | Tests skipped accidentally |
| **No Pre-Commit Gate** | Broken code reaches repo |
| **Slow Feedback** | Minutes to run, not seconds |
| **No CI/CD** | Can't automate in pipeline |
| **Regression Risk** | Old tests not re-run |

### Real-World Impact

**Chat01 Example:**
- 20 tests created
- Validation script created (32 checks)
- ❌ NO CI/CD integration
- ❌ Manual execution only
- ❌ Risk of regressions slipping through

### ✅ Correct Approach

**1. CI/CD Pipeline (GitHub Actions)**

```yaml
# .github/workflows/frontend-tests.yml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
      
      - name: Validate dashboard
        run: ./tests/dashboard/validate_dashboard_fix.sh
```

**2. Pre-Commit Hook**

```bash
# .git/hooks/pre-commit
#!/bin/bash
echo "Running frontend tests..."

npm test -- --run || {
  echo "❌ Tests failed! Commit blocked."
  exit 1
}

echo "✅ All tests passed!"
```

**3. NPM Scripts**

```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:ci": "vitest --run --coverage",
    "validate": "./tests/dashboard/validate_dashboard_fix.sh"
  }
}
```

**Benefits:**
- ✅ Automated execution on every push
- ✅ Pre-commit gate prevents broken commits
- ✅ Fast feedback (<10s for 20 tests)
- ✅ Coverage tracking over time
- ✅ Zero manual effort

---

## Detection & Prevention Matrix

| Anti-Pattern | Detection Method | Prevention Strategy | Tooling |
|--------------|------------------|---------------------|---------|
| **Hidden Element Rendering** | ESLint rules | DeferredRenderer pattern | Custom ESLint plugin |
| **Silent DOM Failures** | TypeScript strict null checks | Explicit null guards | TypeScript, JSDoc |
| **Ad-Hoc Testing** | Code review | Standard test framework | Vitest, Jest |
| **Manual Testing** | No CI/CD | GitHub Actions workflow | GitHub Actions, pre-commit |

---

## Quick Reference Checklist

**Before committing frontend code:**

- [ ] All `getElementById()` calls have null checks
- [ ] Hidden element scenarios tested
- [ ] Tests use standard framework (Vitest/Jest)
- [ ] Tests run in CI/CD pipeline
- [ ] Pre-commit hook blocks broken tests
- [ ] Coverage meets threshold (>80%)
- [ ] Visual regression tests for UI changes
- [ ] Performance benchmarks updated

---

## Related Documentation

- **Pattern:** [DeferredRenderer Pattern](../patterns/deferred-renderer-pattern.md)
- **Lessons:** [Chat01 Incident](../meta/lessons-learned/CHAT01-2026-02-03.yaml)
- **Testing Guide:** [Frontend Testing Standards](../../04-guides/testing/frontend-testing.md) *(to be created)*

---

## Metadata

| Field | Value |
|-------|-------|
| **Document ID** | ANTI-001 |
| **Author** | CORTEX Architect |
| **Date Created** | 2026-02-03 |
| **Last Updated** | 2026-02-03 |
| **Status** | Active |
| **Source Incidents** | Chat01 (2026-02-03) |

---

**💡 Remember:** Anti-patterns exist because they seem reasonable at first. Learn from production incidents to avoid repeating mistakes.

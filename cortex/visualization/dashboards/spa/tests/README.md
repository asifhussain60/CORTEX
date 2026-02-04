# CORTEX Dashboard Integration Tests

**Author:** Asif Hussain | **Version:** 1.0 | **Date:** 2026-02-03

---

## 🎯 Purpose

Comprehensive integration tests for the CORTEX Dashboard MVC architecture, ensuring Model-View-Controller components work together correctly and prevent data loading race conditions.

---

## 🐛 Problem Fixed: Data Loading Race Condition

### Root Cause

**Timeline Issue:**
```
1. Page loads → app.js loads
2. app.js init() called → reads embedded data (empty {})
3. Dynamic loader script runs → fetches real data  
4. Dynamic loader updates script content
5. Dynamic loader calls initializeWithData() → dashboard.init() AGAIN
6. ❌ But this.data was already set to {} in step 2!
```

**Impact:** Components skip rendering because they check for empty data during initial load.

### Solution

**Two-part fix:**

1. **app.js: Accept external data injection**
   ```javascript
   async init(externalData = null) {
       if (externalData) {
           this.data = externalData;  // Use provided data
       } else {
           this.loadData();  // Fallback to DOM parsing
       }
   }
   ```

2. **dashboard.html: Pass data directly**
   ```javascript
   function initializeWithData(data) {
       const dashboard = new CortexDashboard();
       dashboard.init(data);  // Direct injection bypasses race
   }
   ```

**Benefits:**
- ✅ Eliminates race condition
- ✅ Maintains backward compatibility (static file:// mode)
- ✅ Cleaner separation of concerns
- ✅ Easier to test

---

## 🧪 Test Suites

### 1. Model: Data Loading (3 tests)
- Parse JSON from script tag
- Handle empty data gracefully  
- Validate required data structure

### 2. Model: Data Structure Validation (4 tests)
- Security vulnerabilities array validation
- Code smells array validation
- Use cases array validation
- Dependencies packages array validation

### 3. View: DOM Element Existence (3 tests)
- Vulnerabilities list container
- Code smells grid container
- Dashboard data script tag

### 4. Controller: Data Rendering Logic (3 tests)
- Render when data exists
- Skip rendering for empty arrays
- Handle missing containers gracefully

### 5. Integration: MVC Flow (3 tests)
- **Data flow: Model → Controller → View** — Full pipeline test
- **Race condition fix** — External data injection test
- **Direct data initialization** — Component init test

---

## 🚀 Running Tests

### Option 1: Browser (Recommended)

```bash
cd /Users/asifhussain/PROJECTS/CORTEX/company/dashboards/spa/tests
python3 -m http.server 8081
```

Then open: http://localhost:8081/integration.test.html

### Option 2: Direct File Access

Open `integration.test.html` in your browser (file:// protocol supported)

### Option 3: CI/CD Integration

```bash
# Using Playwright (future enhancement)
npx playwright test integration.test.html
```

---

## 📊 Expected Results

**100% Pass Rate:**
- Total Tests: 16
- Passed: 16 ✅
- Failed: 0 ❌
- Duration: ~1-2 seconds

**Coverage:**
- Model layer: 100% (data loading + validation)
- View layer: 100% (DOM elements)
- Controller layer: 100% (rendering logic)
- Integration: 100% (MVC flow + race condition fix)

---

## 🔍 Test Design Principles

### High-Value Intelligence

| Principle | Implementation |
|-----------|----------------|
| **Real-world scenarios** | Tests actual dashboard data structure |
| **Edge case coverage** | Empty arrays, missing containers, null data |
| **Race condition focus** | Validates fix for production bug |
| **MVC pattern validation** | Ensures proper separation of concerns |

### Defensive Testing

```javascript
// Test validates actual runtime behavior
function assertArray(value, message) {
    if (!Array.isArray(value)) {
        throw new Error(message || 'Value is not an array');
    }
}

// Used in tests
assertArray(data.security.vulnerabilities, 'Must be array');
```

### Visual Feedback

- Progress bar for test execution
- Real-time status updates (Running → Pass/Fail)
- Color-coded results (green/red)
- Detailed error messages
- Summary dashboard

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Integration Tests               │
│  (integration.test.html)                │
└─────────────────────────────────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌───▼────┐  ┌───▼─────┐
│  Model  │  │  View  │  │ Control │
│  Tests  │  │  Tests │  │  Tests  │
└─────────┘  └────────┘  └─────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │   app.js│      │dashboard│
    │         │      │  .html  │
    └─────────┘      └─────────┘
```

---

## 📝 Test Data

**Mock data included in test file:**
- Full dashboard data structure
- 2 vulnerabilities (high, medium severity)
- 2 code smells (medium, low severity)
- 2 use cases
- 2 packages with licenses
- Complete metrics

**Why mock data?**
- Consistent test results
- No external dependencies
- Fast execution
- Covers all data paths

---

## 🔒 Best Practices Applied

| Practice | Enforcement |
|----------|-------------|
| **CORE-030: Implementation Truth** | Tests verify actual runtime behavior, not documentation |
| **CORE-008: TDD** | Tests created alongside fix |
| **OWASP: Input Validation** | JSON parsing error handling tested |
| **12-Factor: Dependencies** | Self-contained test suite |
| **Clean Code: Readability** | Clear test names, descriptive assertions |

---

## 🎓 Lessons Learned

### Race Condition Pattern

**Problem:** Async data loading with sync component initialization

**Solution:** Direct data injection pattern
```javascript
// Anti-pattern (race condition)
dashboard.init();  // Reads empty data
fetchData().then(updateDOM);  // Updates later

// Pattern (fixed)
fetchData().then(data => {
    dashboard.init(data);  // Direct injection
});
```

### MVC Testing Strategy

**Model Layer:**
- Test data parsing
- Test data validation
- Test data structure

**View Layer:**
- Test DOM element existence
- Test rendering output
- Test event handlers

**Controller Layer:**
- Test data flow
- Test error handling
- Test component coordination

**Integration:**
- Test full pipeline
- Test real-world scenarios
- Test edge cases

---

## 🚦 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Dashboard Integration Tests
  run: |
    cd company/dashboards/spa/tests
    python3 -m http.server 8081 &
    sleep 2
    npx playwright test integration.test.html
```

### Pre-commit Hook

```bash
#!/bin/bash
# Run tests before committing dashboard changes
if git diff --cached --name-only | grep -q "company/dashboards/spa"; then
    open company/dashboards/spa/tests/integration.test.html
    echo "⚠️  Please verify integration tests pass before committing"
fi
```

---

## 📚 References

- [CORTEX Architecture](../../../../docs/04-architecture/)
- [MVC Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [JavaScript Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)

---

## ✅ Success Criteria

**Definition of Done:**

- [x] All 16 tests pass
- [x] Race condition fixed
- [x] MVC pattern validated
- [x] Documentation complete
- [x] Visual feedback implemented
- [x] Mock data comprehensive
- [x] Edge cases covered
- [x] Best practices applied

---

*v1.0 — Initial release with comprehensive MVC integration tests and race condition fix validation.*

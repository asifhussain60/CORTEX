# Dashboard Test Suite

Comprehensive test suite for CORTEX Dashboard, covering unit tests, integration tests, and end-to-end tests.

## 🎯 Overview

This test suite validates all aspects of the dashboard functionality:

- **Unit Tests:** Individual module testing (data loader, utilities, components)
- **Integration Tests:** Component integration and data flow
- **End-to-End Tests:** Complete user workflows with Puppeteer

## 📁 Structure

```
tests/
├── unit/                           # Unit tests
│   ├── data-loader.test.js        # Data loading & caching
│   └── shared-utils.test.js       # Utility functions
├── integration/                    # Integration tests
│   ├── dashboard-app.test.js      # App initialization & orchestration
│   └── components.test.js         # All 7 tab components
├── e2e/                            # End-to-end tests
│   └── dashboard.e2e.test.js      # Full user workflows
├── fixtures/                       # Test data
│   └── mock-data.js               # Mock dashboard data
├── package.json                    # Test dependencies
├── .babelrc                        # Babel configuration
└── run-tests.sh                    # Test runner script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd cortex-brain/dashboards/ui/tests
npm install
```

### 2. Start HTTP Server

The dashboard requires an HTTP server (ES6 modules):

```bash
cd cortex-brain/dashboards/ui
python3 -m http.server 8080
```

### 3. Run Tests

```bash
# Run all tests
./run-tests.sh

# Run specific test suite
./run-tests.sh unit
./run-tests.sh integration
./run-tests.sh e2e

# Run with coverage
./run-tests.sh coverage
```

## 📊 Test Coverage

The test suite provides comprehensive coverage:

### Unit Tests (2 files, ~50 tests)

**data-loader.test.js:**
- ✓ Load mock data successfully
- ✓ Handle network errors
- ✓ Handle invalid JSON
- ✓ Handle 404 responses
- ✓ Cache loaded data
- ✓ Clear cache functionality
- ✓ Export to JSON
- ✓ Export to CSV
- ✓ Handle circular references

**shared-utils.test.js:**
- ✓ Toast notifications (success, error, warning)
- ✓ Loading overlay (show, hide, update)
- ✓ DOM utilities (create, clear elements)
- ✓ Date formatting
- ✓ Number formatting
- ✓ Data validation
- ✓ Debounce and throttle functions

### Integration Tests (2 files, ~80 tests)

**dashboard-app.test.js:**
- ✓ App initialization
- ✓ Data loading
- ✓ Tab switching (all 7 tabs)
- ✓ Data source switching (mock/live)
- ✓ Data refresh
- ✓ Error handling
- ✓ Performance (caching, debouncing)

**components.test.js:**
- ✓ Overview tab rendering
- ✓ Tech Stack tab rendering
- ✓ Security tab rendering
- ✓ Architecture tab rendering
- ✓ Code Organization tab rendering
- ✓ Team Metrics tab rendering
- ✓ Vendors tab rendering
- ✓ Visualization creation (charts, graphs)

### E2E Tests (1 file, ~40 tests)

**dashboard.e2e.test.js:**
- ✓ Dashboard loading
- ✓ Tab navigation
- ✓ Keyboard shortcuts
- ✓ Data export (JSON, PDF)
- ✓ Data source switching
- ✓ Responsive design (mobile, tablet, desktop)
- ✓ Performance benchmarks
- ✓ Accessibility (ARIA, keyboard navigation)

**Total: ~170 tests across all suites**

## 🧪 Running Individual Tests

### Unit Tests

```bash
# All unit tests
npm run test:unit

# Specific file
npm test tests/unit/data-loader.test.js

# Watch mode
npm run test:watch tests/unit/
```

### Integration Tests

```bash
# All integration tests
npm run test:integration

# Specific file
npm test tests/integration/dashboard-app.test.js
```

### End-to-End Tests

```bash
# All E2E tests
npm run test:e2e

# Run in headed mode (see browser)
HEADLESS=false npm run test:e2e
```

## 📈 Coverage Reports

Generate detailed coverage reports:

```bash
npm run test:coverage
```

Coverage report will be in `coverage/` directory. Open `coverage/lcov-report/index.html` in browser.

**Coverage Thresholds:**
- Branches: 70%
- Functions: 70%
- Lines: 70%
- Statements: 70%

## 🐛 Debugging Tests

### Debug Mode

```bash
# Run with debugger
npm run test:debug

# Then in Chrome: chrome://inspect
```

### Verbose Output

```bash
npm run test:verbose
```

### Watch Mode

```bash
npm run test:watch
```

## 📝 Writing New Tests

### Unit Test Template

```javascript
describe('Module Name', () => {
    let module;
    
    beforeAll(async () => {
        module = await import('../../module.js');
    });
    
    beforeEach(() => {
        // Setup
    });
    
    afterEach(() => {
        // Cleanup
    });
    
    describe('Function Name', () => {
        it('should do something', () => {
            const result = module.functionName();
            expect(result).toBe(expected);
        });
    });
});
```

### Integration Test Template

```javascript
describe('Component Integration', () => {
    beforeEach(() => {
        document.body.innerHTML = '<div id="container"></div>';
        global.fetch = jest.fn();
    });
    
    it('should integrate properly', async () => {
        const container = document.getElementById('container');
        await renderComponent(container, mockData);
        expect(container.innerHTML).toContain('expected');
    });
});
```

### E2E Test Template

```javascript
describe('User Workflow', () => {
    let page;
    
    beforeEach(async () => {
        page = await browser.newPage();
        await page.goto('http://localhost:8080');
    });
    
    it('should complete workflow', async () => {
        await page.click('#button');
        await page.waitForSelector('#result');
        const text = await page.$eval('#result', el => el.textContent);
        expect(text).toContain('success');
    });
});
```

## 🔧 Configuration

### Jest Configuration (package.json)

```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "coverageThreshold": {
      "global": {
        "branches": 70,
        "functions": 70,
        "lines": 70,
        "statements": 70
      }
    }
  }
}
```

### Babel Configuration (.babelrc)

```json
{
  "presets": [
    ["@babel/preset-env", {
      "targets": { "node": "current" }
    }]
  ]
}
```

## 🚨 Troubleshooting

### Issue: Tests fail with "Cannot find module"

**Solution:** Ensure you're in the tests directory and dependencies are installed:

```bash
cd cortex-brain/dashboards/ui/tests
npm install
```

### Issue: E2E tests fail with "Navigation timeout"

**Solution:** Ensure HTTP server is running:

```bash
cd cortex-brain/dashboards/ui
python3 -m http.server 8080
```

### Issue: "ReferenceError: fetch is not defined"

**Solution:** Mock fetch in beforeEach:

```javascript
beforeEach(() => {
    global.fetch = jest.fn();
});
```

### Issue: ES6 module import errors

**Solution:** Use dynamic imports in tests:

```javascript
beforeAll(async () => {
    module = await import('../../module.js');
});
```

## 📋 Test Checklist

Before committing, ensure:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Coverage meets thresholds (70%+)
- [ ] No console errors in browser tests
- [ ] Tests run in under 30 seconds (excluding E2E)
- [ ] E2E tests complete in under 2 minutes

## 🎯 Best Practices

1. **Test Isolation:** Each test should be independent
2. **Mock External Dependencies:** Use jest.fn() for API calls
3. **Cleanup:** Always cleanup in afterEach
4. **Descriptive Names:** Use clear test descriptions
5. **Arrange-Act-Assert:** Follow AAA pattern
6. **Avoid Magic Numbers:** Use constants for test data
7. **Test Edge Cases:** Include error scenarios
8. **Performance:** Keep unit tests fast (<100ms each)

## 📚 Resources

- [Jest Documentation](https://jestjs.io/)
- [Puppeteer Documentation](https://pptr.dev/)
- [Testing Library](https://testing-library.com/)

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review test output for specific errors
- Ensure HTTP server is running on port 8080
- Verify all dependencies are installed

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

# Dashboard Integration Tests

**Purpose:** Validate all file paths, imports, and dependencies in the dashboard UI

**Author:** Asif Hussain  
**Date:** December 7, 2025

---

## Test Suite Overview

The integration test suite performs comprehensive validation of:

1. **File Existence** - Verifies all referenced files exist
2. **Script Sources** - Validates HTML script tags point to real files
3. **Component Files** - Checks all tab components are present
4. **ES6 Imports** - Resolves all import statements in JS modules
5. **Container IDs** - Ensures HTML containers match JS references
6. **Data Files** - Validates mock data files exist
7. **CSS Files** - Checks stylesheets are present
8. **Path Resolution** - Tests relative path resolution from index.html

---

## Running Tests

```bash
# From dashboard root
cd /path/to/cortex-brain/dashboards
node tests/integration-test.js

# Or from anywhere
node /path/to/cortex-brain/dashboards/tests/integration-test.js
```

**Requirements:** Node.js 12+ (uses built-in fs/path modules only)

---

## Test Output

**Success Example:**
```
✅ Passed:   45
❌ Failed:   0
⚠️  Warnings: 0
```

**Failure Example:**
```
✅ Passed:   42
❌ Failed:   3
⚠️  Warnings: 1

━━━ Errors ━━━
1. Missing file: components/overview-tab-v3.js
2. Broken import: ./shared-utils.js in app.js
3. Container #overview-container referenced in overview-tab.js but missing from HTML
```

---

## What Gets Tested

### 1. Core HTML File
- `ui/index.html` existence

### 2. Script Sources
- All `<script src="...">` paths
- All `<script type="module" src="...">` paths

### 3. Component Files
- `executive-tab.js`
- `overview-tab-v3.js`
- `tech-stack-tab.js`
- `security-tab.js`
- `architecture-tab.js`
- `code-org-tab.js`
- `vendors-tab.js`
- `engineering-onboarding-tab.js`

### 4. App.js Imports
- All `import ... from '...'` statements
- Path resolution relative to app.js location

### 5. Container IDs
- `executive-container`
- `overview-container`
- `tech-stack-container`
- `security-container`
- `architecture-container`
- `code-org-container`
- `vendors-container`
- `engineering-container`
- `engineering-onboarding-content`

### 6. Component Imports
- Validates imports in each component file
- Checks relative path resolution

### 7. Mock Data Files
- `overview.json`
- `executive-summary.json`
- `tech-stack.json`
- `security.json`
- `architecture.json`
- `code-organization.json`
- `vendors.json`
- `engineering-onboarding.json`

### 8. Repository Registry
- `data/repository-registry.json`

### 9. Container ID Mismatches
- Cross-references `getElementById()` calls with HTML
- Detects orphaned container references

### 10. CSS Files
- `styles/global.css`
- `styles/dashboard.css`
- `styles/engineering-onboarding.css`

---

## Common Failures

### Missing Component Files
**Error:** `Missing file: components/overview-tab-v3.js`  
**Fix:** Check if file exists, verify spelling, or update import path

### Broken Import Paths
**Error:** `Import broken: ./shared-utils.js from app.js`  
**Fix:** Verify relative path, ensure file has `.js` extension

### Container ID Mismatches
**Error:** `Container #overview-container referenced but missing from HTML`  
**Fix:** Add container to HTML or update JS to use correct ID

### Missing Data Files
**Warning:** `Data file missing: overview.json`  
**Impact:** Runtime errors when loading tab  
**Fix:** Create data file or update data loader to handle missing files

---

## Integration with CI/CD

Add to pre-commit or CI pipeline:

```bash
# Pre-commit hook
node cortex-brain/dashboards/tests/integration-test.js || exit 1

# GitHub Actions
- name: Run Dashboard Tests
  run: node cortex-brain/dashboards/tests/integration-test.js
```

---

## Extending Tests

### Adding New Component Tests

```javascript
// In integration-test.js, update componentFiles array:
const componentFiles = [
    'components/executive-tab.js',
    'components/my-new-tab.js',  // Add here
    // ...
];
```

### Adding Container ID Checks

```javascript
// Update expectedContainers array:
const expectedContainers = [
    'executive-container',
    'my-new-container',  // Add here
    // ...
];
```

### Adding Data File Checks

```javascript
// Update expectedDataFiles array:
const expectedDataFiles = [
    'overview.json',
    'my-new-data.json',  // Add here
    // ...
];
```

---

## Troubleshooting

**Test hangs:** Check for circular imports in JS modules  
**False positives:** Verify file permissions (must be readable)  
**Path resolution errors:** Ensure running from correct directory

---

## Exit Codes

- **0**: All tests passed
- **1**: One or more tests failed

---

**Maintenance:** Update test suite when adding new components, containers, or data files

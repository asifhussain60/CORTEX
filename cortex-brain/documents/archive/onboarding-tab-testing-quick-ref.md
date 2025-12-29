# Onboarding Tab Testing Quick Reference

**Version:** 1.0.0  
**Last Updated:** December 7, 2025

---

## Quick Start

```bash
# Run all onboarding tests (31 tests, ~1.5s)
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py tests/dashboard/test_onboarding_browser_integration.py -v

# Run with detailed output
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py tests/dashboard/test_onboarding_browser_integration.py -v -s
```

---

## Test Files

| File | Tests | Purpose |
|------|-------|---------|
| `test_onboarding_tab_luum_fresh.py` | 16 | Data validation, rendering, interactivity |
| `test_onboarding_browser_integration.py` | 15 | Browser integration, error reproduction |

---

## Test Categories

### Data Loading & Validation (16 tests)
```bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py::TestOnboardingTabDataLoading -v
```
- File existence checks
- JSON validity
- Schema compliance
- Data accuracy

### Rendering Tests (4 tests)
```bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py::TestOnboardingTabRendering -v
```
- Stage content generation
- Metadata enrichment
- Data transformation

### Interactivity (3 tests)
```bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py::TestOnboardingTabInteractivity -v
```
- Navigation
- Completion tracking
- Progress persistence

### Browser Integration (15 tests)
```bash
pytest tests/dashboard/test_onboarding_browser_integration.py -v
```
- Registry validation
- Data source discovery
- Console error reproduction
- Component validation

---

## Common Test Commands

### Run Specific Test Class
```bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py::TestOnboardingTabDataLoading -v
```

### Run Specific Test
```bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py::TestOnboardingTabDataLoading::test_overview_data_structure -v
```

### Run with Coverage
```bash
pytest tests/dashboard/ --cov=cortex-brain/dashboards --cov-report=html
```

### Run with Performance Timing
```bash
pytest tests/dashboard/ -v --durations=10
```

---

## Expected Results

### All Tests Passing
```
31 passed in 1.47s
```

### Test Breakdown
- Data Loading: 4/4 ✅
- Overview Structure: 1/1 ✅
- Tech Stack Structure: 1/1 ✅
- Architecture Structure: 1/1 ✅
- Rendering: 4/4 ✅
- Interactivity: 3/3 ✅
- Validation: 3/3 ✅
- Performance: 2/2 ✅
- Browser Integration: 15/15 ✅

---

## Data Files Validated

### Required Files (7)
- ✅ overview.json
- ✅ tech-stack.json
- ✅ architecture.json
- ✅ health-data.json
- ✅ code-organization.json
- ✅ security.json
- ✅ executive-summary.json

### Additional Files (5)
- vendors.json
- reconciliation.json
- consolidation.json
- metadata.json
- _validation.json

---

## Key Metrics Validated

| Metric | Value |
|--------|-------|
| Project Name | Luum Fresh |
| Total Files | 10,391 |
| Lines of Code | 1,246,213 |
| Health Score | 54 |
| Architecture | N-Tier |
| App Type | SOAP Web Service |
| Technologies | 3 (C#, .NET, JS) |

---

## Troubleshooting

### Test Failures

**Issue:** File not found errors  
**Solution:** Verify data path: `cortex-brain/dashboards/data/repos/luum-fresh/`

**Issue:** JSON decode errors  
**Solution:** Validate JSON files with `python -m json.tool <file.json>`

**Issue:** Schema validation failures  
**Solution:** Check data structure matches test expectations

### Performance Issues

**Issue:** Tests taking >2 seconds  
**Solution:** Check disk I/O, verify file sizes are reasonable

---

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run Onboarding Tab Tests
  run: |
    pytest tests/dashboard/test_onboarding_tab_luum_fresh.py \
           tests/dashboard/test_onboarding_browser_integration.py \
           --junitxml=test-results.xml
```

### Pre-Commit Hook
```bash
#!/bin/bash
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py -q
if [ $? -ne 0 ]; then
    echo "Onboarding tests failed!"
    exit 1
fi
```

---

## Related Documentation

- **Full Report:** `cortex-brain/documents/reports/onboarding-tab-test-validation-report.md`
- **Onboarding Component:** `cortex-brain/dashboards/ui/components/onboarding-tab.js`
- **Data Loader:** `cortex-brain/dashboards/ui/data-loader.js`
- **Test Data:** `cortex-brain/dashboards/data/repos/luum-fresh/`

---

## Quick Verification

```bash
# Verify all data files exist
ls cortex-brain/dashboards/data/repos/luum-fresh/*.json

# Count tests
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py --collect-only | grep "test_"

# Run fastest tests only
pytest tests/dashboard/test_onboarding_tab_luum_fresh.py -k "not performance" -v
```

---

**Maintained by:** CORTEX Dashboard Team  
**Contact:** github.com/asifhussain60/CORTEX

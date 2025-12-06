# Dashboard Test Suite - Quick Reference

**Location:** `tests/dashboard/`  
**Main Test File:** `test_all_tabs_data_contract.py`  
**Test Runner:** `run_all_dashboard_tests.py`

---

## 🚀 Quick Start

### Run All Tests (One Command)
```bash
python tests/dashboard/run_all_dashboard_tests.py
```

### Run Quick Validation (Fast)
```bash
python tests/dashboard/run_all_dashboard_tests.py --quick
```

### Run With pytest Directly
```bash
pytest tests/dashboard/test_all_tabs_data_contract.py -v -m dashboard
```

---

## 📋 Test Coverage

### 8 Dashboard Tabs Tested

| Tab | Collector | Key Validations |
|-----|-----------|----------------|
| **Executive Summary** | `DashboardDataCollector.collect_executive_summary()` | Purpose, History, Composition structure |
| **Overview** | Mock data only | Health score, metrics, status |
| **Tech Stack** | `TechStackCollector` | Technologies array, summary counts |
| **Security** | `SecurityCollector` | Score, vulnerabilities, OWASP Top 10 |
| **Architecture** | `ArchitectureCollector` | Layers/tiers/components |
| **Code Organization** | `CodeOrganizationCollector` | File metrics, structure |
| **Vendors** | `VendorDetector` (optional) | Third-party dependencies |
| **Team Metrics** | `TeamMetricsCollector` (optional) | Contributor stats |

---

## 🧪 Test Categories

### 1. Schema Validation
- ✅ Required keys present
- ✅ Nested object structure
- ✅ Array vs object detection

### 2. Data Type Validation
- ✅ String, int, float, bool
- ✅ List and dict types
- ✅ Optional fields handling

### 3. Mock Data Compatibility
- ✅ Generated data matches mock schema
- ✅ All frontend-required fields present
- ✅ Backward compatibility

### 4. Integration Testing
- ✅ All collectors execute without errors
- ✅ Cross-tab data consistency
- ✅ Mock data files exist

### 5. Performance Testing
- ✅ <3 second execution per collector
- ✅ Total suite execution time
- ✅ Memory usage validation

---

## 🎯 Test Execution Modes

### Full Suite (Default)
```bash
python tests/dashboard/run_all_dashboard_tests.py
```
**Runs:** All tests (schema + integration + performance)  
**Duration:** ~30-60 seconds

### Quick Validation
```bash
python tests/dashboard/run_all_dashboard_tests.py --quick
```
**Runs:** Mock data schemas only  
**Duration:** ~5 seconds

### Integration Only
```bash
python tests/dashboard/run_all_dashboard_tests.py --integration
```
**Runs:** All collectors together  
**Duration:** ~15-20 seconds

### Performance Only
```bash
python tests/dashboard/run_all_dashboard_tests.py --performance
```
**Runs:** Execution time validation  
**Duration:** ~20-30 seconds

### Fast Mode (Skip Performance)
```bash
python tests/dashboard/run_all_dashboard_tests.py --fast
```
**Runs:** Schema + integration (no performance tests)  
**Duration:** ~15-20 seconds

---

## 📊 Test Markers

### Use pytest markers for targeted testing:

```bash
# All dashboard tests
pytest -m dashboard

# Dashboard + integration
pytest -m "dashboard and integration"

# Dashboard without performance
pytest -m "dashboard and not performance"

# Executive Summary tests only
pytest tests/dashboard/test_all_tabs_data_contract.py::TestExecutiveSummaryTab -v
```

---

## 🔍 Test Structure

### Per-Tab Test Classes

```python
@pytest.mark.dashboard
class TestExecutiveSummaryTab:
    """Executive Summary tab validation"""
    
    def test_executive_summary_structure(...)
    def test_executive_summary_purpose(...)
    def test_executive_summary_history(...)
    def test_executive_summary_composition(...)
    def test_executive_summary_matches_mock(...)
```

### Helper Functions

```python
validate_required_keys(data, keys, section)
validate_data_types(data, type_specs, section)
load_mock_data(path, filename)
```

---

## 📝 Adding New Tab Tests

### 1. Create Test Class
```python
@pytest.mark.dashboard
class TestNewTab:
    """Test New Tab data contract"""
    
    def test_new_tab_structure(self, collector):
        data = collector.collect()
        assert data is not None
        # Add validations...
```

### 2. Add Required Keys Validation
```python
required_keys = ['key1', 'key2', 'nested.key']
missing = validate_required_keys(data, required_keys, 'new_tab')
assert not missing, f"Missing keys: {missing}"
```

### 3. Add Type Validation
```python
type_specs = {
    'key1': str,
    'key2': int,
    'nested.key': list
}
errors = validate_data_types(data, type_specs, 'new_tab')
assert not errors, f"Type errors: {errors}"
```

### 4. Add Mock Data Test
```python
def test_new_tab_matches_mock(self, collector, mock_data_path):
    mock = load_mock_data(mock_data_path, 'new-tab.json')
    generated = collector.collect()
    assert set(generated.keys()) == set(mock.keys())
```

---

## 🐛 Debugging Test Failures

### View Detailed Output
```bash
pytest tests/dashboard/test_all_tabs_data_contract.py -v --tb=long
```

### Run Specific Test
```bash
pytest tests/dashboard/test_all_tabs_data_contract.py::TestExecutiveSummaryTab::test_executive_summary_structure -v
```

### Print Debug Info
```python
# Add to test:
import json
print(json.dumps(data, indent=2))
```

### Check Mock Data
```bash
cat cortex-brain/dashboards/mock/executive-summary.json
```

---

## ✅ Success Criteria

All tests pass when:
- ✅ All required keys present in generated data
- ✅ Data types match specifications
- ✅ Generated data matches mock schema
- ✅ All collectors execute without errors
- ✅ Performance <3s per collector
- ✅ Integration tests pass

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `test_all_tabs_data_contract.py` | Main test suite (all tabs) |
| `run_all_dashboard_tests.py` | Test runner with modes |
| `cortex-brain/dashboards/mock/*.json` | Mock data for validation |
| `src/utils/data_collector.py` | Executive Summary collector |
| `src/dashboard/data/*_collector.py` | Other tab collectors |

---

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Dashboard Tests
  run: python tests/dashboard/run_all_dashboard_tests.py --fast
```

### Pre-commit Hook
```bash
#!/bin/bash
python tests/dashboard/run_all_dashboard_tests.py --quick
```

---

**Author:** Asif Hussain  
**Last Updated:** December 6, 2025  
**Version:** 1.0.0

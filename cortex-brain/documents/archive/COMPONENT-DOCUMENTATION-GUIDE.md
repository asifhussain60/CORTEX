# CORTEX Component Documentation Guide

**Purpose:** Clarify which components are required vs. optional for CORTEX operation.

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 11, 2025

---

## 🎯 Component Classification

### REQUIRED Components (Must Have)

These components are essential for CORTEX to function. Missing any will cause failures.

#### Core System
- **cortex.config.json** - Configuration file (or environment variables fallback)
- **cortex-brain/** - Brain directory structure
  - **tier1/** - Working memory (FIFO, 70 conversations)
  - **tier2/** - Knowledge graph
  - **tier3/** - Development context
- **src/entry_point/** - CortexEntry main interface
- **src/tier0/** - Brain Protector (SKULL governance)
- **cortex-operations.yaml** - Operation routing configuration

#### Required Python Packages
```
pytest>=8.4.0
PyYAML>=6.0.2
python-dateutil>=2.8.2
watchdog>=6.0.0
psutil>=6.1.1
pydantic>=2.0.0
```

---

### OPTIONAL Components (Nice to Have)

These components enhance functionality but CORTEX works without them.

#### Optional Features
- **Oracle Integration** (`tests/tier2/test_oracle_crawler.py`)
  - Requires: Oracle database instance or Docker container
  - Environment vars: ORACLE_HOST, ORACLE_PASSWORD, ORACLE_PORT, ORACLE_SERVICE
  - Fallback: Tests use mocks when unavailable

- **Playwright Dashboard Tests** (`tests/tier3/test_interactive_dashboard_generator.py`)
  - Requires: `pip install playwright && playwright install`
  - Browser downloads: ~200MB (Chrome, Firefox, WebKit)
  - Fallback: Tests skip when Playwright unavailable

- **Tier 0 Governance Artifacts** (optional for some tests)
  - `cortex-brain/admin/planning/` - Planning templates
  - `cortex-brain/.gitignore` - Git ignore patterns
  - `cortex-brain/tier2/knowledge-graph.yaml` - Knowledge patterns
  - Fallback: Tests skip when artifacts missing

#### Optional Python Packages
```
playwright>=1.48.0  # Dashboard generation tests
oracledb  # Oracle database integration
pytest-json-report  # JSON test reports
```

---

## 🔍 How to Check Component Status

### Check Required Components
```bash
# Config file
test -f cortex.config.json && echo "✅ Config present" || echo "❌ Config missing"

# Brain structure
test -d cortex-brain/tier1 && echo "✅ Tier1 present" || echo "❌ Tier1 missing"
test -d cortex-brain/tier2 && echo "✅ Tier2 present" || echo "❌ Tier2 missing"
test -d cortex-brain/tier3 && echo "✅ Tier3 present" || echo "❌ Tier3 missing"

# Python packages
python -c "import pytest; import yaml; import watchdog; import psutil; import pydantic" && echo "✅ All required packages installed" || echo "❌ Missing packages"
```

### Check Optional Components
```bash
# Oracle
python -c "import oracledb" 2>/dev/null && echo "✅ Oracle available" || echo "⏭️ Oracle unavailable (optional)"

# Playwright
python -c "import playwright" 2>/dev/null && echo "✅ Playwright available" || echo "⏭️ Playwright unavailable (optional)"

# Governance artifacts
test -d cortex-brain/admin/planning && echo "✅ Planning templates present" || echo "⏭️ Planning templates missing (optional)"
```

---

## 🚀 Setup Instructions

### Minimal Setup (Required Only)
```bash
# 1. Install required packages
pip install -r requirements.txt

# 2. Create config (or use environment variables)
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json with your paths

# 3. Verify brain structure
python -c "from src.config import config; config.ensure_paths_exist()"

# 4. Run core tests
pytest tests/unit/test_entry_point.py -v
```

### Full Setup (All Features)
```bash
# 1. Install all packages
pip install -r requirements.txt

# 2. Install Playwright browsers
pip install playwright
playwright install

# 3. Install Oracle client (if needed)
pip install oracledb

# 4. Setup Oracle Docker (for CI/CD)
# See: .github/workflows/oracle-integration-tests.yml

# 5. Create governance artifacts
mkdir -p cortex-brain/admin/planning
mkdir -p cortex-brain/tier0/governance

# 6. Run all tests
pytest tests/ -v
```

---

## 📊 Test Skip Behavior

### When Tests Skip
Tests skip when optional components unavailable:

```python
# Example: Oracle tests
@pytest.mark.skipif(
    not os.getenv('ORACLE_HOST'),
    reason="Requires Oracle database"
)
def test_oracle_connection():
    ...

# Example: Playwright tests
@pytest.mark.skipif(
    not PLAYWRIGHT_AVAILABLE,
    reason="Requires Playwright"
)
def test_dashboard_generation():
    ...
```

### Acceptable Skip Patterns
- **Local Development:** Optional features skip (Oracle, Playwright)
- **CI/CD:** All tests run (Docker containers provide dependencies)
- **Target:** <5 skipped tests in CI/CD, any number in local dev

---

## 🎯 Environment-Specific Configs

### Local Development
```json
{
  "brain_path": "cortex-brain",
  "optional_features": {
    "oracle": false,
    "playwright": false
  }
}
```

### CI/CD
```yaml
env:
  ORACLE_HOST: localhost
  ORACLE_PASSWORD: ${{ secrets.ORACLE_PASSWORD }}
  PLAYWRIGHT_BROWSERS_PATH: $HOME/.cache/ms-playwright
```

### Production
```json
{
  "brain_path": "/var/cortex/brain",
  "optional_features": {
    "oracle": true,
    "playwright": true
  }
}
```

---

## 📚 Component Dependency Matrix

| Component | Required By | Optional For | Skip Tests If Missing |
|-----------|-------------|--------------|----------------------|
| cortex-brain/ | Core system | - | ❌ Never skip |
| pytest | Test suite | - | ❌ Never skip |
| PyYAML | Config loading | - | ❌ Never skip |
| Oracle | Tier2 crawler | Other features | ✅ Skip Oracle tests |
| Playwright | Dashboard tests | Other tests | ✅ Skip dashboard tests |
| Planning artifacts | Tier0 validation | Runtime | ✅ Skip governance tests |

---

## 🔧 Troubleshooting

### "Import Error: No module named 'playwright'"
```bash
# Install Playwright
pip install playwright
playwright install
```

### "Oracle tests failing"
```bash
# Option 1: Set environment variables
export ORACLE_HOST=localhost
export ORACLE_PASSWORD=your_password

# Option 2: Start Docker container
docker run -d -p 1521:1521 gvenzl/oracle-xe:21-slim

# Option 3: Let tests skip (acceptable for local dev)
pytest tests/ -v  # Oracle tests will skip automatically
```

### "Governance tests skipping"
```bash
# Create missing artifacts
mkdir -p cortex-brain/admin/planning
touch cortex-brain/.gitignore
mkdir -p cortex-brain/tier2
echo "{}" > cortex-brain/tier2/knowledge-graph.yaml
```

---

## ✅ Success Criteria

**Required components working:**
- [x] CortexEntry initializes
- [x] Config loads (file or environment)
- [x] Brain structure exists
- [x] Core tests passing (entry point, brain persistence)

**Optional components available (best effort):**
- [ ] Oracle integration (CI/CD only)
- [ ] Playwright tests (full setup only)
- [ ] Governance artifacts (complete setup only)

---

**Last Updated:** December 11, 2025  
**Maintained By:** Asif Hussain  
**Reference:** cortex-brain/documents/reports/STUB-MOCK-ANALYSIS-2025-12-11.md

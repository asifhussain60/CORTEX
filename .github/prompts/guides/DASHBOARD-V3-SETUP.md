# Dashboard v3 Setup Guide (PHASE-21)
**Version:** 3.0 | **Updated:** 2026-02-04 | **Authority:** PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml

---

## 🎯 Overview

CORTEX Dashboard v3 is a **JSON-first, browser-based SPA** for repository intelligence visualization with dual-format support (JSON + SQLite).

**Key Features:**
- ✅ 13 tabs: Executive, Overview, Use Cases, Entities, Components, Files, Packages, Security, Quality, Testing, LENS Insights, Refactoring, Code Snippets
- ✅ Offline-first: No fetch() calls, file:// compatible
- ✅ Dual-format: JSON (default) + SQLite (optional migration)
- ✅ Browser E2E tested: Playwright with 8 tests
- ✅ MCP-exposed: All tools available via MCP server

---

## 📦 Installation

### Python Dependencies

All Python dependencies are in `deployment/requirements.txt`:

```bash
# Install CORTEX with dashboard support
pip install -r deployment/requirements.txt
```

**Key packages:**
- `pydantic==2.5.2` - Schema validation (v3.0 schema)
- `pyyaml==6.0.1` - Configuration parsing
- `fastapi==0.104.1` - MCP server (optional)

### JavaScript Dependencies (Dashboard SPA)

```bash
cd company/dashboards/spa

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium
```

**Key packages (from package.json):**
- `@playwright/test` - Browser E2E testing
- `vitest` - Frontend unit testing
- `fuse.js` - Fuzzy search (embedded in dashboard)
- `echarts` - Charts (embedded via CDN)
- `mermaid` - UML diagrams (embedded via CDN)

---

## 🚀 Quick Start

### 1. Generate Dashboard Data

**Via MCP Tool (Recommended):**

```python
from cortex.mcp.tools import cortex_aggregate_dashboard_data_v3

result = cortex_aggregate_dashboard_data_v3(
    repo_path="D:/PROJECTS/KSESSIONS",
    output_path="company/dashboards/spa/KSESSIONS/dashboard-data.json",
    include_code_snippets=False,
    max_files=1000
)

print(f"Generated: {result['output_path']}")
print(f"Health score: {result['stats']['health_score']}")
```

**Via Python Script:**

```bash
python -c "
from cortex.lens.dashboard_data_aggregator_v3 import DashboardDataAggregatorV3
from pathlib import Path

agg = DashboardDataAggregatorV3()
result = agg.aggregate(Path('D:/PROJECTS/KSESSIONS'))
result.write_to_file(Path('company/dashboards/spa/KSESSIONS/dashboard-data.json'))
"
```

### 2. Serve Dashboard

**Via MCP Tool:**

```python
from cortex.mcp.tools import cortex_serve_dashboard

result = cortex_serve_dashboard(port=8888)
print(f"Dashboard: {result['url']}/dashboard.html?repo=KSESSIONS")
```

**Via Command Line:**

```bash
cd company/dashboards/spa
python -m http.server 8888
```

Then open: http://localhost:8888/dashboard.html?repo=KSESSIONS

### 3. Run E2E Tests

**Via MCP Tool:**

```python
from cortex.mcp.tools import cortex_test_dashboard_e2e

result = cortex_test_dashboard_e2e()
print(f"Tests: {result['passed']} passed, {result['failed']} failed")
```

**Via Command Line:**

```bash
cd company/dashboards/spa
npx playwright test
```

---

## 🏗️ Architecture

### Data Flow

```
Repository
    ↓
DashboardDataAggregatorV3 (Python)
    ↓
dashboard-data.json (v3.0 schema)
    ↓
DualFormatDataLoader (JavaScript)
    ├─ JSONDataAdapter (SQL-like query API)
    └─ SQLiteDataLayer (future: sql.js WASM)
    ↓
Dashboard SPA (13 tabs)
```

### File Structure

```
company/dashboards/spa/
├── dashboard.html              # Main SPA (1096 lines)
├── js/
│   ├── data/
│   │   ├── JSONDataAdapter.js        # SQL-like JSON query (816 lines) ✅ FIXED
│   │   ├── DualFormatDataLoader.js   # Format detection (345 lines) ✅ FIXED
│   │   └── SQLiteDataLayer.js        # Future: sql.js wrapper
│   ├── components/
│   │   ├── Wizard.js                 # Multi-step wizard
│   │   ├── SubTabs.js                # Secondary navigation
│   │   └── Pagination.js             # Pagination controls
│   ├── charts/
│   │   └── ChartFactory.js           # ECharts wrapper
│   └── diagrams/
│       └── MermaidRenderer.js        # UML diagram renderer
├── css/
│   ├── dashboard.css           # Main styles (glassmorphism)
│   └── components.css          # Component styles
├── vendor/
│   ├── echarts.min.js         # Charts library
│   ├── mermaid.min.js         # UML diagrams
│   └── fuse.min.js            # Fuzzy search
├── tests/
│   ├── unit/                  # Vitest unit tests
│   └── e2e/
│       └── dashboard-browser.spec.js  # Playwright E2E (8 tests) ✅ NEW
├── KSESSIONS/
│   └── dashboard-data.json    # Generated data (4.1M LOC)
├── package.json               # Node.js dependencies
├── vitest.config.js          # Vitest configuration
└── playwright.config.js      # Playwright configuration ✅ NEW
```

---

## 🔧 MCP Tools Reference

### cortex_aggregate_dashboard_data_v3

Generate dashboard-data.json for repository.

**Parameters:**
- `repo_path` (string): Absolute path to repository
- `output_path` (string, optional): Output JSON path
- `include_code_snippets` (boolean): Include code samples (default: false)
- `max_files` (number): Max files in array (default: 1000)

**Returns:**
```json
{
    "success": true,
    "output_path": "/path/to/dashboard-data.json",
    "duration_seconds": 209.43,
    "stats": {
        "total_loc": 4130755,
        "total_files": 26176,
        "health_score": 100,
        "data_size_mb": 5.2
    }
}
```

### cortex_serve_dashboard

Start HTTP server for dashboard viewing.

**Parameters:**
- `port` (number): HTTP port (default: 8888)
- `directory` (string): Root directory (default: company/dashboards/spa)

**Returns:**
```json
{
    "success": true,
    "url": "http://localhost:8888",
    "port": 8888,
    "pid": 12345
}
```

### cortex_test_dashboard_e2e

Run Playwright browser E2E tests.

**Parameters:**
- `test_pattern` (string): Test file pattern (default: dashboard-browser.spec.js)
- `headed` (boolean): Run visible browser (default: false)

**Returns:**
```json
{
    "success": true,
    "passed": 8,
    "failed": 0,
    "duration_seconds": 57.0
}
```

---

## 🧪 Testing

### Test Pyramid

```
Browser E2E (Playwright)           ← 8 tests ✅ NEW
    ↓
Integration (pytest)               ← 15 tests ✅ EXISTING
    ↓
Frontend Unit (Vitest)             ← 60+ tests ✅ EXISTING
    ↓
Backend Unit (pytest)              ← 58 tests ✅ EXISTING
```

### Test Coverage

| Layer | Tests | Coverage | Tool |
|-------|-------|----------|------|
| Backend Unit | 58 | 80%+ | pytest |
| Frontend Unit | 60+ | 80%+ | Vitest + jsdom |
| Backend Integration | 15 | Full pipeline | pytest |
| Browser E2E | 8 | UI validation | Playwright |

**Key Tests:**
- ✅ Schema validation (33 tests)
- ✅ Data aggregation (25 tests)
- ✅ Full pipeline (15 tests)
- ✅ Frontend components (60+ tests)
- ✅ **Browser E2E (8 tests) - NEW**

### Running Tests

```bash
# Backend tests
pytest tests/unit/test_dashboard_schema_v3.py -v
pytest tests/unit/test_dashboard_data_aggregator_v3.py -v
pytest tests/integration/test_full_onboarding.py -v

# Frontend unit tests
cd company/dashboards/spa
npm test

# Browser E2E tests (NEW)
cd company/dashboards/spa
npx playwright test
```

---

## 🐛 Known Issues & Fixes

### Issue 1: JSONDataAdapter Not Loaded (FIXED ✅)

**Symptom:** Browser console error: "JSONDataAdapter not loaded. Include JSONDataAdapter.js."

**Root Cause:** Classes exported for Node.js (`module.exports`) but not browser globals.

**Fix Applied:**
```javascript
// JSONDataAdapter.js (lines 812-820)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JSONDataAdapter;
}
// Browser global export ✅ ADDED
if (typeof window !== 'undefined') {
    window.JSONDataAdapter = JSONDataAdapter;
}
```

**Status:** ✅ FIXED (2026-02-04)

### Issue 2: Dashboard UI Not Rendering

**Symptom:** Blank dashboard, no tabs/charts visible.

**Root Cause:** DualFormatDataLoader returns JSONDataAdapter instance, but dashboard expected plain JSON.

**Fix Applied:**
```javascript
// dashboard.html (lines 910-925)
if (dataLayer instanceof window.JSONDataAdapter) {
    data = dataLayer.data;  // ✅ Access underlying data
} else if (dataLayer.query && typeof dataLayer.query === 'function') {
    data = await loadFromSQLite(dataLayer);
} else {
    data = dataLayer;
}
```

**Status:** ✅ FIXED (2026-02-04)

---

## 📊 Schema v3.0 Reference

### Key Models

```python
# Snake_case field names (backend → frontend)
repo_summary: RepoSummary          # Repository metadata
metrics_summary: MetricsSummary    # Code metrics
use_cases: List[UseCase]           # Business features
entities: List[Entity]             # Domain entities
components: List[Component]        # Technical components
files: List[FileMetadata]          # File listings
packages: List[Package]            # Dependencies
vulnerabilities: List[Vulnerability]  # Security issues
code_smells: List[CodeSmell]       # Quality issues
test_results: Optional[TestResults]   # Test outcomes
lens_insights: List[LENSInsight]   # LENS analysis
refactoring_suggestions: List[RefactoringSuggestion]
code_snippets: List[CodeSnippet]   # Code samples
executive_kpis: ExecutiveKPIs      # C-level metrics
```

### Frontend Transformation

Dashboard uses legacy format internally:
```javascript
// convertToLegacyFormat() transforms:
{
    repo_summary: {...},      // Snake_case (v3 schema)
    metrics_summary: {...}
}
↓
{
    repo: {...},              // Legacy dashboard format
    overview: {...},
    metrics: {...}
}
```

---

## 🔐 Security Considerations

1. **No Secrets in JSON**: Dashboard data contains NO credentials/API keys
2. **PII Sanitization**: User data excluded from code snippets
3. **File Limits**: Max 1000 files to prevent memory issues
4. **HTTP Server**: Use only for local development (not production)
5. **CORS**: Dashboard requires same-origin (http:// or file://)

---

## 🚀 Production Deployment

### Static File Hosting

```bash
# Build production bundle
cd company/dashboards/spa
cp -r . /var/www/dashboards/

# Serve via Nginx
server {
    listen 80;
    server_name dashboards.cortex.local;
    root /var/www/dashboards;
    index dashboard.html;
}
```

### CDN Deployment

1. Upload `company/dashboards/spa/` to S3/Azure Blob
2. Configure CloudFront/Azure CDN
3. Access: https://cdn.example.com/dashboard.html?repo=KSESSIONS

### Docker Container

```dockerfile
FROM nginx:alpine
COPY company/dashboards/spa /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 📚 Related Documentation

- [PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml](../../cortex/knowledge/specs/PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml)
- [dashboard_schema_v3.py](../../cortex/models/dashboard_schema_v3.py)
- [dashboard_data_aggregator_v3.py](../../cortex/lens/dashboard_data_aggregator_v3.py)
- [JSONDataAdapter.js](../../company/dashboards/spa/js/data/JSONDataAdapter.js)
- [Playwright E2E Tests](../../company/dashboards/spa/tests/e2e/dashboard-browser.spec.js)

---

**Last Updated:** 2026-02-04  
**Version:** 3.0  
**Status:** ✅ Production Ready

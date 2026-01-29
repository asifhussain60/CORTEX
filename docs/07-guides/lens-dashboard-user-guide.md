# LENS Dashboard User Guide

**Version:** 1.0.0  
**Phase:** 14 - LENS Dashboard Implementation  
**Last Updated:** 2026-01-29

---

## Overview

The LENS Dashboard provides interactive code intelligence visualization for Python repositories. It features 8 tabs of analysis ranging from repository metrics to CORTEX-specific orchestrator insights.

**LENS** = **L**anguage → **E**xamination → **N**avigation → **S**ynthesis

---

## Quick Start

### Start Dashboard Server

```bash
# Start server on default port 8888
cortex lens dashboard serve

# Custom port
cortex lens dashboard serve --port 9000

# Don't auto-open browser
cortex lens dashboard serve --no-browser

# Direct to CORTEX repository (8 tabs)
cortex lens dashboard serve cortex
```

### Generate Static Dashboard

```bash
# Generate for current directory
cortex lens dashboard generate --repo .

# Custom output directory
cortex lens dashboard generate --repo /path/to/repo --output ./dashboards
```

### Clean Old Dashboards

```bash
# Remove dashboards older than 30 days
cortex lens dashboard clean

# Custom threshold (7 days)
cortex lens dashboard clean --older-than 7

# Preview without deleting
cortex lens dashboard clean --dry-run
```

---

## Dashboard Tabs

### Universal Tabs (All Repositories)

#### Tab 1: Repository Overview 📊
- Total files and lines of code
- Contributor count
- Health indicators (documentation, test coverage, type hints)
- Tech stack visualization
- Activity metrics

#### Tab 2: Dependency Graph 🕸️
- Author collaboration network (D3.js force graph)
- Commit relationships
- Contributor connections
- Network statistics

#### Tab 3: Class Diagrams 📐
- Mermaid class diagrams
- Package structure
- Class relationships
- Method signatures

#### Tab 4: Temporal Analysis ⏱️
- Commit timeline
- Author activity patterns
- Code evolution over time
- Contribution trends

#### Tab 5: Impact Analysis 💥
- Change blast radius
- Affected components
- Test requirements
- Risk assessment

### CORTEX-Specific Tabs (CORTEX Repository Only)

#### Tab 6: CORTEX Brain 🧠
- Tier 0: Governance rules (28 CORE rules)
- Tier 1: Acceptance criteria
- Tier 2: Response templates
- Tier 3: Knowledge repository (35+ YAML files)
- Health metrics per tier

#### Tab 7: Governance Heatmap 📋
- CORE rule compliance
- Violation tracking
- Compliance percentage
- Rule-by-rule breakdown

#### Tab 8: Orchestrator Constellation 🎼
- 23 orchestrator network visualization
- Category breakdown (Core, Domain, Support)
- Health metrics per orchestrator
- Wiring configuration status
- Invocation statistics

---

## API Endpoints

### Base URL
```
http://localhost:8888/api/dashboard
```

### Endpoints

#### Full Analysis
```http
GET /api/dashboard/analyze?repo_path=/path/to/repo
```

Returns all 8 tabs of dashboard data.

**Query Parameters:**
- `repo_path` (required): Absolute path to repository
- `timeout` (optional): Analysis timeout in seconds

**Response:**
```json
{
  "overview": {...},
  "dependencies": {...},
  "classes": {...},
  "timeline": {...},
  "impact": {...},
  "brain": {...} | null,
  "governance": {...} | null,
  "orchestrators": {...} | null,
  "_metadata": {
    "analysis_time_ms": 1234,
    "timestamp": "2026-01-29T10:00:00Z",
    "repo_path": "/path/to/repo",
    "is_cortex": false
  }
}
```

#### Single Tab Data
```http
GET /api/dashboard/tab/{tab_id}?repo_path=/path/to/repo
```

Returns data for specific tab.

**Path Parameters:**
- `tab_id`: One of: overview, dependencies, classes, timeline, impact, brain, governance, orchestrators

#### Overlay Data
```http
GET /api/dashboard/overlay/{type}?repo_path=/path/to/repo
```

Returns overlay visualization data.

**Path Parameters:**
- `type`: One of: security, performance, compliance

**Response (performance):**
```json
{
  "bottlenecks": [...],
  "complexity_hotspots": [...]
}
```

#### WebSocket Real-Time Updates
```http
WebSocket /api/dashboard/ws?repo_path=/path/to/repo&interval=5
```

Real-time dashboard updates.

**Query Parameters:**
- `repo_path` (required): Repository path
- `interval` (optional): Update interval in seconds (default: 5)

---

## Performance

### Benchmarks

- **Small repos (< 10 files):** < 2 seconds
- **Medium repos (10-50 files):** < 5 seconds
- **Large repos (50+ files):** < 10 seconds

### Optimization Tips

1. Use individual tab endpoints for faster loading
2. Cache results for static repositories
3. Run analysis in background for large repos
4. Use `--timeout` parameter to prevent hanging

---

## Repository Detection

The dashboard automatically detects repository type:

### CORTEX Repository
Shows all 8 tabs if repository contains:
- `cortex_brain/` directory
- `cortex/orchestrators/` directory
- `.github/prompts/CORTEX.prompt.md` file
- `cortex/wiring/specifications/wiring.yaml` file

### External Repository
Shows 5 universal tabs only.

---

## Troubleshooting

### Dashboard won't start
```bash
# Check if port is available
lsof -i :8888

# Try different port
cortex lens dashboard serve --port 9000
```

### Analysis timing out
```bash
# Increase timeout
# Access via API with timeout parameter
curl "http://localhost:8888/api/dashboard/analyze?repo_path=/path&timeout=30"
```

### Empty visualizations
- Ensure repository has Python files
- Check git is initialized (for timeline/author graphs)
- Verify file permissions

### CORTEX tabs not showing
Ensure repository has CORTEX markers:
```bash
ls cortex_brain/
ls cortex/orchestrators/
```

---

## Advanced Usage

### Programmatic Access

```python
from cortex.api.endpoints.lens_dashboard_routes import analyze_repository

# Analyze repository
data = analyze_repository(repo_path="/path/to/repo")

# Check if CORTEX
is_cortex = data["_metadata"]["is_cortex"]

# Access specific tabs
overview = data["overview"]
dependencies = data["dependencies"]
```

### Custom Integration

```python
from fastapi import FastAPI
from cortex.api.endpoints.lens_dashboard_routes import create_dashboard_router

app = FastAPI()
router = create_dashboard_router()
app.include_router(router)

# Now accessible at /api/dashboard/*
```

### Static Generation in CI/CD

```bash
# Generate dashboard in CI pipeline
cortex lens dashboard generate --repo . --output ./artifacts

# Upload artifacts
aws s3 cp ./artifacts/ s3://bucket/dashboards/ --recursive
```

---

## Configuration

### Environment Variables

- `LENS_DASHBOARD_PORT`: Default server port (default: 8888)
- `LENS_DASHBOARD_HOST`: Default host (default: 127.0.0.1)
- `LENS_CACHE_DIR`: Cache directory for static files

### Customization

Edit templates in:
```
cortex/visualization/templates/tabs/*.html
```

Modify renderers in:
```
cortex/visualization/renderers/*.py
```

---

## Examples

### Example 1: Weekly Dashboard Generation

```bash
#!/bin/bash
# weekly-dashboard.sh

REPO_PATH="/path/to/repo"
OUTPUT_DIR="./weekly-dashboards"

cortex lens dashboard generate \
  --repo "$REPO_PATH" \
  --output "$OUTPUT_DIR"

echo "Dashboard generated: $OUTPUT_DIR"
```

### Example 2: Multi-Repository Dashboard

```bash
#!/bin/bash
# multi-repo-dashboard.sh

REPOS=(
  "/path/to/repo1"
  "/path/to/repo2"
  "/path/to/repo3"
)

for repo in "${REPOS[@]}"; do
  cortex lens dashboard generate --repo "$repo"
done
```

### Example 3: Automated Cleanup

```bash
#!/bin/bash
# cleanup-old-dashboards.sh

# Run weekly to clean old dashboards
cortex lens dashboard clean --older-than 30

echo "Old dashboards cleaned"
```

---

## Support

### Documentation
- API Reference: `docs/06-api-reference/lens-dashboard.md`
- Architecture: `docs/04-architecture/lens-dashboard.md`
- Phase 14 Guide: `docs/phases/phase-14-completion-report.md`

### Issues
Report issues at: https://github.com/cortex/issues

### Contributing
See: `docs/10-contributing/README.md`

---

## Version History

### v1.0.0 (2026-01-29)
- Initial release
- 8-tab dashboard
- 3 CLI commands
- FastAPI backend
- CORTEX repository detection
- Performance benchmarks validated

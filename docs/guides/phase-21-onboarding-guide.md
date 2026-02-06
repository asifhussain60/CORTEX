# Repository Onboarding Guide — Phase-21 JSON-First

## Quick Start (5 Minutes)

### Step 1: Run Onboarding

```bash
cortex onboard-repository-json /path/to/your/repository
```

### Step 2: Verify Success

```bash
ls company/dashboards/your-repo/
# ✅ dashboard.json
# ✅ metadata.json
# ✅ registry.json (updated)
```

### Step 3: View Dashboard

```bash
# Option A: Direct file (file:// protocol)
open company/dashboards/your-repo/dashboard.html

# Option B: HTTP server (http:// protocol)
python -m http.server 8000 --directory company/dashboards
# Then open: http://localhost:8000/your-repo/dashboard.html
```

---

## What Happens During Onboarding?

### 1. Repository Analysis

```
Your Repository
    ↓
LENS Analysis (cortex_lens_analyze)
    ├─ Scan files
    ├─ Analyze metrics
    ├─ Security scan
    ├─ Dependency check
    └─ Performance profiling
    ↓
Structured Analysis Data
```

### 2. JSON Generation

```
LENS Data
    ↓
JSONDataGenerator
    ├─ Extract repository info
    ├─ Organize metrics
    ├─ Format security issues
    ├─ Compile dependencies
    └─ Generate dashboard structure
    ↓
dashboard.json (45-100KB)
```

### 3. File Creation

```
Generated Files:
├── dashboard.json        (Complete dashboard data)
├── metadata.json         (Adapter tracking)
└── registry.json         (Updated repository index)
```

### 4. Dashboard Ready

```
Files Created
    ↓
Registry Updated
    ↓
Landing Page Updated
    ↓
Dashboard Ready to View ✅
```

---

## Files Generated

### dashboard.json

Complete dashboard data for SPA rendering.

```json
{
  "schema_version": "3.0",
  "repository": {
    "slug": "cortex",
    "display_name": "CORTEX",
    "health_score": 8.5
  },
  "overview": { "summary": "..." },
  "metrics": { "code_metrics": { ... } },
  "security": { ... },
  "dependencies": { ... },
  "quality": { ... },
  "files": [ ... ]
}
```

**Size:** Typically 45-100KB (compressed well below 1MB)

### metadata.json

Adapter tracking and usage statistics.

```json
{
  "slug": "cortex",
  "generated_at": "2026-02-06T10:00:00Z",
  "data_format": "json",
  "adapter_type": "json",
  "adapter_reason": "Repository < 10K files, no search needed",
  "lens_analysis": {
    "files_analyzed": 250,
    "duration_seconds": 15.3
  },
  "usage_stats": {
    "page_views": 0,
    "search_queries": 0,
    "filter_actions": 0
  },
  "graduation_eligible": false,
  "next_review_date": "2026-03-06"
}
```

### registry.json

Index of all onboarded repositories.

```json
{
  "repositories": [
    {
      "slug": "cortex",
      "display_name": "CORTEX",
      "description": "AI orchestration system",
      "health_score": 8.5,
      "last_updated": "2026-02-06T10:00:00Z",
      "adapter_type": "json",
      "dashboard_url": "/dashboards/cortex/dashboard.html"
    }
  ],
  "summary": {
    "total_repositories": 1,
    "avg_health_score": 8.5,
    "last_sync": "2026-02-06T10:00:00Z"
  }
}
```

---

## Onboarding Different Repository Types

### Small Repository (< 1K files)

```bash
cortex onboard-repository-json /path/to/small-repo

# Expected:
# ⚡ Analysis time: 5-10 seconds
# 📊 Dashboard size: 20-30KB
# ✅ Adapter: JSON (optimal for small repos)
```

### Medium Repository (1K - 10K files)

```bash
cortex onboard-repository-json /path/to/medium-repo

# Expected:
# ⚡ Analysis time: 10-30 seconds
# 📊 Dashboard size: 50-100KB
# ✅ Adapter: JSON (good fit)
```

### Large Repository (> 10K files)

```bash
cortex onboard-repository-json /path/to/large-repo

# Expected:
# ⚡ Analysis time: 30-120 seconds
# 📊 Dashboard size: 500KB-1MB
# ⚠️  Note: Consider SQLite adapter in future
```

---

## Viewing Your Dashboard

### Landing Page (Repository Browser)

Displays all onboarded repositories as tiles.

```
╔════════════════════════════════════╗
║   CORTEX Repository Dashboard      ║
╠════════════════════════════════════╣
║  ┌─────────────────────────┐       ║
║  │ CORTEX                  │       ║
║  │ AI Orchestration System │       ║
║  │ Health: 8.5/10          │       ║
║  │ Last Updated: 2 hours   │       ║
║  │ [View Dashboard]        │       ║
║  └─────────────────────────┘       ║
║                                    ║
║  ┌─────────────────────────┐       ║
║  │ Other Repo              │       ║
║  │ Description...          │       ║
║  │ ...                     ║
╚════════════════════════════════════╝
```

### Dashboard Tabs (13 Total)

After clicking a repository tile:

1. **Overview** — Summary, health score, key stats
2. **Metrics** — Code metrics, complexity, coverage
3. **Security** — Issues by severity, vulnerabilities
4. **Dependencies** — Direct deps, outdated, vulnerabilities
5. **Quality** — Test coverage, passing/failing tests
6. **Use Cases** — Business value + user stories
7. **LENS** — Code patterns, anti-patterns, recommendations
8. **Refactoring** — Suggested improvements
9. **Architecture** — Components, layers, relationships
10. **Tests** — Test suite summary, coverage details
11. **Insights** — Key findings and observations
12. **Files** — File listing with stats
13. **Commits** — Recent commits and contributors

---

## Troubleshooting

### ❌ "Repository not found"

**Problem:** Onboarding failed to locate repository.

**Solution:**
```bash
# Verify path exists
ls /path/to/repo
ls /path/to/repo/.git

# Retry onboarding
cortex onboard-repository-json /path/to/repo
```

### ❌ "Dashboard.json missing"

**Problem:** Files weren't created in expected location.

**Solution:**
```bash
# Check where files were actually created
find . -name "dashboard.json" -type f

# Verify output directory
ls company/dashboards/

# Re-run if needed with explicit path
cortex onboard-repository-json \
  --repo-path /path/to/repo \
  --output-path company/dashboards/your-repo
```

### ❌ "JSON is invalid"

**Problem:** Generated dashboard.json failed schema validation.

**Solution:**
```bash
# Validate schema
python -c "
from cortex.models.dashboard_schema_pydantic import Dashboard
import json

try:
    with open('dashboard.json') as f:
        Dashboard.model_validate(json.load(f))
    print('✅ Valid')
except Exception as e:
    print(f'❌ Invalid: {e}')
"

# Re-onboard to regenerate
cortex onboard-repository-json /path/to/repo --force
```

### ❌ "Dashboard loads but tabs are empty"

**Problem:** JSON data is incomplete or corrupt.

**Solution:**
```bash
# Check JSON file size
ls -lh company/dashboards/your-repo/dashboard.json

# If <1KB, data wasn't generated properly
# Re-run with verbose output
cortex onboard-repository-json /path/to/repo --verbose

# Look for errors in LENS analysis stage
```

### ❌ "HTTP serving shows CORS error"

**Problem:** Dashboard served via HTTP but can't load JSON.

**Solution:**
```bash
# Ensure files are in same directory structure
ls company/dashboards/your-repo/
# Must have: dashboard.html, dashboard.json, metadata.json

# Test HTTP server
python -m http.server 8000 --directory company/dashboards

# Verify response
curl http://localhost:8000/your-repo/dashboard.json | head -20
```

---

## Customization

### Change Output Directory

```bash
cortex onboard-repository-json /path/to/repo \
  --output-dir /custom/dashboards/path
```

### Include Additional Metrics

```bash
cortex onboard-repository-json /path/to/repo \
  --with-git-stats \
  --with-code-duplication \
  --with-performance-profiling
```

### Skip Long Operations

```bash
cortex onboard-repository-json /path/to/repo \
  --skip-security-scan \
  --skip-performance-profiling
```

---

## Automation

### Onboard Multiple Repositories

```bash
#!/bin/bash
# onboard_all_repos.sh

for repo_dir in ~/projects/*/; do
    repo_name=$(basename "$repo_dir")
    echo "Onboarding $repo_name..."
    
    cortex onboard-repository-json "$repo_dir" || {
        echo "Failed to onboard $repo_name"
        continue
    }
done

echo "✅ All repositories onboarded"
```

### Schedule Periodic Updates

```bash
# In crontab: Re-analyze repositories daily at 2 AM
0 2 * * * /usr/local/bin/cortex onboard-repository-json /path/to/repo --force
```

### Batch Verify All Dashboards

```bash
#!/bin/bash
# verify_all_dashboards.sh

for dashboard in company/dashboards/*/dashboard.json; do
    echo "Validating $dashboard..."
    
    python -c "
from cortex.models.dashboard_schema_pydantic import Dashboard
import json
import sys

try:
    with open('$dashboard') as f:
        Dashboard.model_validate(json.load(f))
    print(f'  ✅ Valid')
except Exception as e:
    print(f'  ❌ Invalid: {e}')
    sys.exit(1)
"
done
```

---

## Performance Optimization

### For Large Repositories

If dashboard generation takes >2 minutes:

```bash
# Skip optional analysis
cortex onboard-repository-json /path/to/large-repo \
  --skip-security-scan \
  --skip-code-duplication \
  --no-git-history

# Or generate in background
nohup cortex onboard-repository-json /path/to/large-repo \
  > onboarding.log 2>&1 &
```

### Monitor Generation Progress

```bash
# Watch output
tail -f onboarding.log

# Or with timestamps
tail -f onboarding.log | grep -E "Analyzing|Generating|Writing"
```

---

## Verification Checklist

After onboarding, verify everything works:

- [ ] `dashboard.json` exists and is readable
- [ ] `metadata.json` exists with adapter type
- [ ] `registry.json` was updated with new repo
- [ ] Dashboard JSON validates against schema v3.0
- [ ] File size is reasonable (<500KB)
- [ ] Dashboard.html loads without errors
- [ ] All 13 tabs load and render data
- [ ] No console errors in browser DevTools
- [ ] Charts display correctly
- [ ] No CORS errors when served via HTTP

---

## Next Steps

### View Analytics

Check `metadata.json` for usage analytics:

```bash
cat company/dashboards/your-repo/metadata.json | jq .usage_stats
```

### Update Dashboard

Generate new dashboard data:

```bash
# Re-runs full LENS analysis
cortex onboard-repository-json /path/to/repo --force
```

### Export Data

Extract raw metrics for reporting:

```bash
python -c "
import json

with open('company/dashboards/your-repo/dashboard.json') as f:
    data = json.load(f)

print(f\"Repository: {data['repository']['display_name']}\")
print(f\"Health Score: {data['repository']['health_score']}/10\")
print(f\"Test Coverage: {data['metrics']['code_metrics']['test_coverage']}%\")
print(f\"Security Score: {data['metrics']['security_metrics']['security_score']}/10\")
"
```

---

## Support

### Common Questions

**Q: How often should I re-onboard?**  
A: Daily for active development, weekly for stable projects.

**Q: Can I edit dashboard.json manually?**  
A: Not recommended. Schema validation will fail. Re-generate via onboarding.

**Q: What if JSON is too large (>1MB)?**  
A: Consider graduating to SQLite adapter (Phase-21 future work).

**Q: Can I share dashboards with teams?**  
A: Yes! Host via HTTP server and share the URL.

### Reporting Issues

If you encounter problems:

1. Check the troubleshooting section above
2. Enable verbose output: `cortex onboard-repository-json ... --verbose`
3. Verify schema: See validation instructions
4. Check logs: `tail -f onboarding.log`
5. Report with: Dashboard size, repository size, error messages

---

*Phase-21 Onboarding Guide — JSON-First Architecture*  
*Date: 2026-02-06 | Version: 1.0 | Status: Complete*

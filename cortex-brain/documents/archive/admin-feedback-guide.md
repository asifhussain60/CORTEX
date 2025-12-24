# Admin Guide: CORTEX Feedback Review & Analytics

**Version:** 1.0  
**Last Updated:** 2025-11-24  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Audience:** CORTEX Repository Administrators Only

---

## 📋 Overview

The Admin Feedback Review system aggregates feedback reports from multiple applications, performs trend analysis, and generates comprehensive dashboards for the CORTEX development team.

**⚠️ ADMIN-ONLY FEATURE**  
This module is NOT deployed to user repositories. It only runs in the CORTEX development repository (requires `cortex-brain/admin/` directory).

---

## 🚀 Quick Start

### Reviewing Feedback

```
review feedback
```

or natural language variants:

```
feedback review
show feedback reports
analyze user feedback
aggregate feedback data
review user reports
feedback analysis
show collected feedback
```

### What It Does

1. **Discovers** feedback reports from GitHub Gist registry
2. **Validates** report format and schema
3. **Aggregates** metrics across all applications
4. **Analyzes** trends (improvements, regressions)
5. **Categorizes** issues by severity
6. **Stores** in analytics database
7. **Generates** summary report

---

## 📊 Gist Registry Management

### Registry File

**Location:** `cortex-brain/gist-sources.yaml`

**Format:**
```yaml
gists:
  - id: "abc123def456"
    owner: "user1"
    app_name: "MyWebApp"
    added_at: "2025-11-20"
    privacy_level: "minimal"
    
  - id: "ghi789jkl012"
    owner: "user2"
    app_name: "MobileApp"
    added_at: "2025-11-21"
    privacy_level: "medium"
```

### Adding New Gist

**Manual:**
Edit `gist-sources.yaml` and add entry.

**Via Command:**
```
add feedback gist <gist-id> <app-name> <owner>
```

### Removing Old Gist

**Manual:**
Remove entry from `gist-sources.yaml`.

**Via Command:**
```
remove feedback gist <gist-id>
```

### Validation

```
validate gist registry
```

Checks:
- Valid Gist IDs
- Accessible Gists (public or with token)
- Schema compliance
- No duplicates

---

## 📈 Analytics Database

### Database Structure

**Per-Application Databases:**
```
cortex-brain/analytics/per-app/
├── MyWebApp/
│   └── metrics.db
├── MobileApp/
│   └── metrics.db
└── ...
```

**Aggregate Database:**
```
cortex-brain/analytics/aggregate/
└── cross-app-metrics.db
```

### Schema (11 Tables)

1. **feedback_reports** - Master registry with SHA256 deduplication
2. **application_metrics** - Project size, LOC, coverage
3. **crawler_performance** - Discovery success rates
4. **cortex_performance** - Operation timings, DB sizes
5. **knowledge_graphs** - Entity counts, graph density
6. **development_hygiene** - Security, commit quality
7. **tdd_mastery** - Test coverage, test-first adherence
8. **commit_metrics** - Build success, deployment frequency
9. **velocity_metrics** - Sprint velocity, cycle time
10. **trend_analysis** - Metric trends over time
11. **issues_reported** - Categorized issues by severity

### Views

- **latest_metrics** - Most recent metrics per app
- **critical_issues_summary** - Unresolved critical issues
- **application_health_scores** - Weighted 0-100 scores

---

## 🔍 Querying Analytics

### Using Python API

```python
from analytics.analytics_db_manager import AnalyticsDBManager
from pathlib import Path

db_manager = AnalyticsDBManager(Path("cortex-brain/analytics"))

# Get latest metrics
latest = db_manager.get_latest_metrics("MyWebApp")
print(f"Test Coverage: {latest['tdd_coverage']}%")

# Get health score
health = db_manager.get_health_score("MyWebApp")
print(f"Health Score: {health}/100")

# Get critical issues
issues = db_manager.get_critical_issues("MyWebApp")
for issue in issues:
    print(f"{issue['severity']}: {issue['message']}")
```

### Direct SQL Queries

```bash
# Connect to database
sqlite3 cortex-brain/analytics/per-app/MyWebApp/metrics.db

# Latest metrics
SELECT * FROM latest_metrics;

# Health scores
SELECT * FROM application_health_scores;

# Critical issues
SELECT * FROM critical_issues_summary;
```

### Common Queries

**Top Performing Apps:**
```sql
SELECT app_name, health_score 
FROM application_health_scores 
ORDER BY health_score DESC 
LIMIT 10;
```

**Apps Needing Attention:**
```sql
SELECT app_name, health_score 
FROM application_health_scores 
WHERE health_score < 70 
ORDER BY health_score ASC;
```

**Security Vulnerabilities:**
```sql
SELECT fr.app_name, dh.security_vulnerabilities 
FROM feedback_reports fr
JOIN development_hygiene dh ON fr.id = dh.report_id
WHERE dh.security_vulnerabilities > 0
ORDER BY dh.security_vulnerabilities DESC;
```

**Test Coverage Trends:**
```sql
SELECT fr.app_name, fr.report_timestamp, tm.test_coverage
FROM feedback_reports fr
JOIN tdd_mastery tm ON fr.id = tm.report_id
ORDER BY fr.app_name, fr.report_timestamp DESC;
```

---

## 📊 Real Live Data Dashboards

### Generation Process

Dashboards are generated automatically during `generate docs`:

1. **Data Detection:** Check if analytics databases exist
2. **Per-App Dashboards:** Generate for each application with data
3. **Aggregate Dashboard:** Cross-app comparison and statistics
4. **Navigation Injection:** Add "Real Live Data" to MkDocs menu (conditional)

### Manual Generation

```python
from analytics.real_live_data_generator import RealLiveDataGenerator
from pathlib import Path

generator = RealLiveDataGenerator(
    analytics_root=Path("cortex-brain/analytics"),
    docs_output_dir=Path("docs")
)

# Check for data
if generator.has_data():
    # Generate all dashboards
    result = generator.generate_all_dashboards()
    print(f"Generated {len(result['app_dashboards'])} dashboards")
```

### Dashboard Components

**Per-App Dashboards:**
- Health score gauge (0-100)
- Key metrics cards (coverage, build success, velocity, security)
- Trends chart (Chart.js line chart)
- Critical issues table
- Last updated timestamp

**Aggregate Dashboard:**
- Health comparison bar chart (all apps)
- Application summary table with rankings
- Cross-app statistics
- Links to individual app dashboards

### Customizing Dashboards

**Edit Template:**  
`cortex-brain/analytics/real_live_data_generator.py`

**Key Methods:**
- `_generate_app_dashboard_html()` - Per-app template
- `_generate_aggregate_dashboard_html()` - Overview template

**Chart.js Configuration:**
```javascript
new Chart(ctx, {
    type: 'line',  // or 'bar', 'radar', 'doughnut'
    data: { ... },
    options: {
        responsive: true,
        scales: { ... }
    }
});
```

---

## 🛠️ Database Maintenance

### Initialization

```bash
# Initialize all databases
python cortex-brain/analytics/initialize_analytics_db.py

# Initialize specific app
python cortex-brain/analytics/initialize_analytics_db.py --app-name MyWebApp

# Recreate databases (drops existing)
python cortex-brain/analytics/initialize_analytics_db.py --recreate
```

### Backups

```bash
# Backup all databases
python cortex-brain/analytics/backup_analytics_db.py

# Backup specific app
python cortex-brain/analytics/backup_analytics_db.py --app-name MyWebApp

# Set retention (delete backups older than N days)
python cortex-brain/analytics/backup_analytics_db.py --retention-days 90
```

**Backup Location:**
```
cortex-brain/analytics/backups/
├── MyWebApp/
│   ├── metrics-backup-20251124-100000.db
│   ├── metrics-backup-20251123-100000.db
│   └── ...
└── MobileApp/
    └── ...
```

### Vacuum (Optimize)

```python
from analytics.analytics_db_manager import AnalyticsDBManager

db_manager = AnalyticsDBManager(Path("cortex-brain/analytics"))
db_manager.vacuum_databases()
```

Reclaims disk space after deletes, optimizes indexes.

### Schema Migrations

**Future versions:** `cortex-brain/analytics/migrations/`

**Current version:** 1.0 (no migrations yet)

---

## 📋 Review Workflow

### 1. Collect Feedback from Users

Users share Gist URLs via:
- GitHub Issues
- GitHub Discussions
- Direct communication

### 2. Add to Registry

```yaml
# cortex-brain/gist-sources.yaml
gists:
  - id: "<gist-id-from-url>"
    owner: "<github-username>"
    app_name: "<application-name>"
    added_at: "2025-11-24"
    privacy_level: "minimal"
```

### 3. Run Review

```
review feedback
```

Output:
```
📊 Feedback Review Complete

✅ Reports Processed: 15
✅ New Reports: 3
✅ Duplicates Skipped: 2
✅ Failed: 0

📈 Summary:
   Total Applications: 8
   Average Health Score: 82.5/100
   Critical Issues: 2
   Trends: 5 improvements, 1 regression

✨ Top Performers:
   1. WebApp Pro (95.0/100)
   2. Mobile Suite (91.5/100)
   3. API Gateway (88.0/100)

⚠️  Needs Attention:
   1. Legacy System (62.0/100) - Security vulnerabilities: 5
   2. Beta Project (68.0/100) - Test coverage: 45%
```

### 4. Investigate Issues

```python
# Query critical issues
issues = db_manager.get_critical_issues("Legacy System")
for issue in issues:
    print(f"{issue['severity']}: {issue['message']}")
```

### 5. Generate Dashboards

```
generate docs
mkdocs serve
```

Navigate to "Real Live Data" → Review metrics and trends.

### 6. Take Action

- Create GitHub Issues for critical problems
- Reach out to app owners
- Update CORTEX to address common issues
- Document patterns in `lessons-learned.yaml`

---

## 🔒 Security & Privacy

### Admin-Only Access

- Admin module requires `cortex-brain/admin/` directory
- Validation fails in user repositories
- No deployment to user workspaces

### GitHub Token

Store in `cortex-brain/admin/.env` (gitignored):
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
```

Load in scripts:
```python
from dotenv import load_dotenv
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")
```

### Privacy Compliance

- Respect user privacy levels (full/medium/minimal)
- Never publish sensitive data (even if included in Gist)
- Redact additional info before analysis
- Delete reports on user request

---

## 📊 Trend Analysis

### Metrics Tracked

- Test coverage changes
- Build success rate trends
- Security vulnerability count
- Sprint velocity improvements
- Deployment frequency

### Identifying Improvements

```sql
SELECT 
    app_name, 
    metric_name, 
    metric_value, 
    change_percentage,
    trend_direction
FROM trend_analysis
WHERE trend_direction = 'improvement'
ORDER BY change_percentage DESC
LIMIT 10;
```

### Identifying Regressions

```sql
SELECT 
    app_name, 
    metric_name, 
    metric_value, 
    change_percentage,
    trend_direction
FROM trend_analysis
WHERE trend_direction = 'regression'
ORDER BY change_percentage ASC
LIMIT 10;
```

---

## 🧪 Testing

### Validation Tests

```bash
# Production readiness
python test_production_readiness.py

# Analytics infrastructure
python test_analytics_infrastructure.py

# Admin module
python test_admin_feedback.py
```

### Expected Results

```
✅ Analytics Pipeline: PASS
✅ Database Deduplication: PASS
✅ Conditional Navigation: PASS
✅ Health Score Calculation: PASS

Pass Rate: 4/4 (100.0%)
```

---

## 📞 Support

### Internal Documentation

- Analytics Database Schema: `cortex-brain/analytics/schema.sql`
- Database Manager API: `cortex-brain/analytics/analytics_db_manager.py`
- Dashboard Generator: `cortex-brain/analytics/real_live_data_generator.py`

### External Resources

- SQLite Documentation: https://www.sqlite.org/docs.html
- Chart.js Documentation: https://www.chartjs.org/docs/
- MkDocs Documentation: https://www.mkdocs.org/

---

**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available - See LICENSE

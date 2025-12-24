# User Guide: CORTEX Feedback & Analytics System

**Version:** 1.0  
**Last Updated:** 2025-11-24  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 📋 Overview

The CORTEX Feedback & Analytics System enables you to track and share your application's performance metrics. It collects comprehensive data, respects your privacy, and makes sharing optional through GitHub Gists.

**Key Features:**
- 📊 8 categories of metrics (test coverage, build success, velocity, security, etc.)
- 🔒 3-level privacy protection (full/medium/minimal)
- 🌐 Optional GitHub Gist sharing
- 📈 Real-time analytics dashboards
- 🚀 Zero configuration required

---

## 🚀 Quick Start

### Basic Usage

Tell CORTEX to collect feedback:

```
feedback
```

or

```
report issue
```

CORTEX will automatically:
1. Collect metrics from your project
2. Apply privacy protection
3. Save report locally
4. Optionally upload to GitHub Gist (if configured)

---

## 📊 Metrics Collected

### 1. Application Metrics
- Project size and lines of code
- Test coverage percentage
- Technology stack
- Build configuration

### 2. Crawler Performance  
- Discovery run success rate
- File scanning efficiency
- Pattern detection accuracy

### 3. CORTEX Performance
- Average operation time
- Brain database sizes (Tier 1, 2, 3)
- Memory usage

### 4. Knowledge Graph
- Entity count
- Relationship density
- Graph completeness

### 5. Development Hygiene
- Security vulnerabilities (count)
- Clean commit rate
- Code quality metrics

### 6. TDD Mastery
- Test coverage
- Test-first adherence rate
- Test quality metrics

### 7. Commit Metrics
- Build success rate
- Deployment frequency
- Rollback rate

### 8. Velocity Metrics
- Sprint velocity
- Cycle time (days)
- Lead time

---

## 🔒 Privacy Levels

### Full Privacy (Default)
- **Keeps:** All metrics, file paths, project names
- **Removes:** Passwords, API keys, tokens
- **Best for:** Internal use, trusted environments

### Medium Privacy
- **Keeps:** Metrics, project structure
- **Redacts:** Email addresses, usernames, personal info
- **Removes:** File paths, API keys
- **Best for:** Sharing with teams

### Minimal Privacy
- **Keeps:** Only metrics (no identifying information)
- **Removes:** All paths, names, personal data
- **Best for:** Public sharing, GitHub Issues

### Setting Privacy Level

```
feedback with medium privacy
```

or

```
report issue minimal privacy
```

---

## 🌐 GitHub Gist Integration

### Why Use Gists?

- **Easy Sharing:** One URL to share all metrics
- **Version History:** Track changes over time
- **Public or Private:** Your choice
- **CORTEX Registry:** Aggregate stats across projects

### Setup Instructions

**1. Create GitHub Personal Access Token**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "CORTEX Feedback"
4. Scopes: Check "gist"
5. Generate token and copy it

**2. Configure CORTEX**

```
setup github gist
```

CORTEX will prompt for your token (stored securely in `cortex.config.json`)

**3. Upload Feedback**

```
feedback upload to gist
```

or simply:

```
feedback
```

(if `auto_upload_gist: true` in config)

### Managing Your Gists

**View all feedback Gists:**
```
list feedback gists
```

**Delete old Gist:**
```
delete feedback gist <gist-id>
```

**Share Gist URL:**

After upload, CORTEX provides a URL:
```
✅ Feedback uploaded to Gist
   URL: https://gist.github.com/username/abc123
```

Share this URL with CORTEX admins or team members.

---

## 🎨 Real Live Data Dashboards

If your project has analytics data, CORTEX generates interactive dashboards automatically.

### Viewing Dashboards

**1. Generate Documentation:**
```
generate docs
```

**2. Start MkDocs Server:**
```
mkdocs serve
```

**3. Navigate to "Real Live Data"**

The "Real Live Data" menu item appears automatically if you have feedback reports.

### Dashboard Features

**Per-Application Dashboards:**
- Health Score (0-100) with color coding
- Key Metrics Cards (coverage, build success, velocity, security)
- Trends Chart (Chart.js interactive visualization)
- Critical Issues Table

**Aggregate Dashboard:**
- Health Score Comparison (all apps)
- Application Summary Table
- Cross-app statistics

**Colors:**
- 🟢 Green: Health ≥80 (excellent)
- 🟡 Yellow: Health 60-79 (good)
- 🔴 Red: Health <60 (needs improvement)

---

## 💡 Best Practices

### 1. Regular Feedback Collection

```
# After major milestones
git tag v1.2.3
feedback
```

### 2. Track Trends Over Time

Collect feedback regularly (weekly/monthly) to see improvements.

### 3. Privacy-First Sharing

Use **minimal privacy** for public sharing:
```
feedback minimal privacy upload to gist
```

### 4. Review Before Sharing

Always review the generated report before uploading:
```
feedback --no-upload
```

Then check `cortex-brain/feedback/reports/feedback_report_<timestamp>.json`

### 5. Security

- Never commit GitHub tokens to git
- Use `.gitignore` to exclude `cortex.config.json`
- Rotate tokens periodically

---

## 📝 Report Format

Feedback reports are saved as JSON/YAML:

**Location:** `cortex-brain/feedback/reports/feedback_report_<timestamp>.json`

**Structure:**
```json
{
  "app_name": "MyApp",
  "timestamp": "2025-11-24T10:00:00",
  "privacy_level": "full",
  "environment": {
    "os": "Windows",
    "python_version": "3.10.5",
    "cortex_version": "3.0"
  },
  "metrics": {
    "application_metrics": { ... },
    "crawler_performance": { ... },
    "cortex_performance": { ... },
    ...
  }
}
```

---

## 🔧 Troubleshooting

### "Feedback collection failed"

**Cause:** Missing project files or CORTEX brain not initialized

**Solution:**
```
setup environment
feedback
```

### "Gist upload failed: 401 Unauthorized"

**Cause:** Invalid or expired GitHub token

**Solution:**
```
setup github gist  # Re-enter token
```

### "No Real Live Data menu in MkDocs"

**Cause:** No analytics data exists yet

**Solution:**
```
feedback  # Collect some data first
generate docs  # Regenerate documentation
```

### "Module not found: PyGithub"

**Cause:** Optional dependency not installed

**Solution:**
```
pip install PyGithub>=2.5.0
```

Or use feedback without Gist integration (local reports only).

---

## 🤝 Contributing Feedback

### Sharing with CORTEX Project

1. Collect feedback with **minimal privacy**
2. Upload to your personal GitHub Gist
3. Share Gist URL in CORTEX GitHub Issues or Discussions

**Example:**
```
feedback minimal privacy upload to gist
```

Then post URL at: https://github.com/asifhussain60/CORTEX/issues

### Feedback Categories

- **🐛 Bug Reports:** Issues with CORTEX functionality
- **✨ Feature Requests:** New capabilities you'd like
- **📈 Performance:** Slow operations or high resource usage
- **📚 Documentation:** Unclear or missing documentation
- **🎨 UX Improvements:** Better user experience suggestions

---

## 📞 Support

- **Documentation:** `help feedback` in CORTEX
- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **GitHub Discussions:** https://github.com/asifhussain60/CORTEX/discussions

---

**Next Steps:**
- [Admin Guide](./admin-feedback-guide.md) - For CORTEX repo admins
- [Analytics Database Guide](./analytics-database-guide.md) - Technical reference
- [Privacy & Security](./privacy-security.md) - Detailed privacy information

---

**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available - See LICENSE

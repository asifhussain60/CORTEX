# Dashboard User Guide

**Tech Stack Enhancement Dashboard Suite**  
**Version:** 1.0.0  
**Last Updated:** December 6, 2025  
**Author:** Asif Hussain

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Dashboard Components](#dashboard-components)
4. [Common Tasks](#common-tasks)
5. [Filtering & Navigation](#filtering--navigation)
6. [Data Export](#data-export)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Tech Stack Enhancement Dashboard Suite provides comprehensive visualization and analysis tools for .NET technology stacks. It helps identify risks, plan migrations, and optimize dependency management across multiple solutions.

### Key Features

- **Real-time risk assessment** across frameworks and packages
- **Interactive visualizations** with D3.js
- **Migration roadmap generation** with phased planning
- **Dependency bloat analysis** with statistical insights
- **Framework health monitoring** with color-coded heatmaps
- **Responsive design** for desktop, tablet, and mobile

### Supported Data Format

All dashboards consume `tech-stack.json` files with the following structure:

```json
{
  "project_name": "your-project",
  "analysis_date": "2025-12-06",
  "solutions": [
    {
      "name": "Solution.Name",
      "path": "/path/to/solution.sln",
      "frameworks": [...],
      "packages": [...]
    }
  ]
}
```

---

## Getting Started

### Prerequisites

- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- `tech-stack.json` file from your codebase analysis
- HTTP server for serving static files (Python, Node.js, or built-in browser tools)

### Quick Start

1. **Prepare Your Data**
   ```bash
   # Generate tech-stack.json from your .NET solutions
   python scripts/analyze_tech_stack.py /path/to/solutions
   ```

2. **Launch Dashboard**
   ```bash
   # Using Python
   python -m http.server 8080
   
   # Using Node.js
   npx http-server -p 8080
   ```

3. **Access Dashboards**
   - Open browser to `http://localhost:8080`
   - Load your `tech-stack.json` file
   - Explore visualizations

---

## Dashboard Components

### 1. Migration Roadmap Generator

**Purpose:** Generate phased migration plans for outdated technologies.

**Key Features:**
- Detects technologies with risk scores ≥40
- Calculates priority: Risk (50%) + Complexity (30%) + EOL Urgency (20%)
- Assigns migrations to phases with dependency resolution
- Exports roadmap to Markdown format

**How to Use:**
1. Load `tech-stack.json`
2. Adjust risk threshold slider (default: 40)
3. Review detected outdated technologies
4. Examine phased migration timeline
5. Export roadmap for team review

**Risk Threshold Guide:**
- **70+**: Critical only (immediate action required)
- **40-70**: High risk (plan within quarter)
- **20-40**: Medium risk (monitor and plan)
- **<20**: Low risk (routine updates)

---

### 2. Framework Health Heatmap

**Purpose:** Visualize framework health across 4 key factors.

**Health Formula:**
```
Health Score = (Version Currency × 0.25) + (CVE Score × 0.30) 
             + (EOL Status × 0.25) + (Community Activity × 0.20)
```

**Color Coding:**
- 🟢 **Green (70-100)**: Healthy - current, secure, well-supported
- 🟡 **Yellow (50-70)**: Warning - aging, minor vulnerabilities, declining support
- 🔴 **Red (<50)**: Critical - outdated, major vulnerabilities, EOL approaching

**How to Use:**
1. Load `tech-stack.json`
2. Scan heatmap for red/yellow cells
3. Click cell for detailed breakdown
4. Review recommendations and migration paths
5. Filter by category (DI, logging, ORM, etc.)

**Cell Drill-Down:**
- Overall health score
- Factor breakdown (version, CVE, EOL, community)
- Specific recommendations
- Suggested migration paths
- Raw data display

---

### 3. Dependency Bloat Analyzer

**Purpose:** Identify solutions with excessive package dependencies.

**Statistics Calculated:**
- **Mean**: Average package count across solutions
- **Median**: Middle value (50th percentile)
- **Q1/Q3**: 25th and 75th percentiles
- **IQR**: Interquartile range (Q3 - Q1)
- **Outlier Threshold**: Q3 + 1.5 × IQR

**Bloat Score Formula:**
```
Bloat Score = (Package Count - Mean) / Standard Deviation
```

**Categories:**
- 🔴 **Critical (>2σ)**: >2 standard deviations above mean
- 🟡 **Warning (1-2σ)**: 1-2 standard deviations above mean
- 🟢 **Normal (<1σ)**: Within 1 standard deviation

**How to Use:**
1. Load `tech-stack.json`
2. Review histogram distribution
3. Examine box plot for outliers
4. Sort solutions by bloat score
5. Review recommendations for governance policies

**Histogram Bins:**
- 0-50 packages: Lightweight
- 51-100: Moderate
- 101-150: Heavy
- 151-200: Very heavy
- 200+: Bloated (review recommended)

---

## Common Tasks

### Task 1: Assess Overall Tech Stack Health

1. Start with **Framework Health Heatmap**
2. Filter by "Show Critical Only" (<50 score)
3. Note all red cells
4. Review drill-down recommendations
5. Document findings for team discussion

### Task 2: Plan Technology Migrations

1. Open **Migration Roadmap Generator**
2. Set risk threshold to 40 (or higher for urgency)
3. Review outdated technologies list
4. Examine phased timeline
5. Export roadmap to Markdown
6. Share with stakeholders for approval

### Task 3: Identify Dependency Optimization Opportunities

1. Launch **Dependency Bloat Analyzer**
2. Review histogram distribution
3. Identify outlier solutions (red points in box plot)
4. Sort solutions by bloat score (critical first)
5. Create action items for dependency audits

### Task 4: Compare Solutions

1. Use **Framework Health Heatmap**
2. Filter by category (e.g., "logging")
3. Compare health scores across solutions
4. Identify inconsistencies (e.g., Solution A uses Serilog, Solution B uses log4net)
5. Plan standardization initiatives

---

## Filtering & Navigation

### Global Filters

All dashboards support filtering:

1. **Risk Threshold Slider**
   - Adjust minimum risk level
   - Lower threshold = more items
   - Higher threshold = only critical items

2. **Category Dropdown**
   - Filter by technology category
   - Options: All, DI, Logging, ORM, Serialization, Testing, Web
   - Applies to frameworks and packages

3. **Show Critical Only**
   - Toggle to display only items with scores <50
   - Quick way to focus on urgent items

### Keyboard Navigation

- **Tab**: Move between interactive elements
- **Enter/Space**: Activate buttons and toggles
- **Arrow Keys**: Navigate within lists and tables
- **Esc**: Close drill-down panels and modals

### Mobile Navigation

- **Swipe**: Scroll through charts and tables
- **Pinch-to-Zoom**: Zoom into detailed visualizations
- **Tap**: Select items and open drill-downs
- **Long Press**: Show tooltips

---

## Data Export

### Export Options

1. **Migration Roadmap → Markdown**
   - Click "Export to Markdown" button
   - Downloads `.md` file with full roadmap
   - Includes phased tasks, timelines, benefits
   - Ready for wiki/documentation import

2. **Dependency Bloat Analysis → JSON**
   - Backend: `python dependency_bloat_analyzer.py input.json output.json`
   - Exports statistics, solutions, histogram bins, box plot data
   - Use for further processing or reporting

3. **Framework Health → Screenshot**
   - Use browser screenshot tools
   - Heatmap renders well in print/PDF
   - Preserve color coding for presentations

### Sharing Dashboards

1. **Embed in Wiki/Documentation**
   ```html
   <iframe src="dashboard.html?data=tech-stack.json" 
           width="100%" height="800px"></iframe>
   ```

2. **Share via URL**
   ```
   http://your-server/dashboard.html?data=https://example.com/data.json
   ```

3. **Export Static Report**
   - Open dashboard in browser
   - Print to PDF (Cmd/Ctrl + P)
   - Select "Save as PDF"
   - All visualizations included

---

## Troubleshooting

### Issue: Dashboard Not Loading

**Symptoms:**
- Blank page
- "Failed to load" error
- Infinite loading spinner

**Solutions:**
1. Verify `tech-stack.json` is valid JSON
   ```bash
   python -m json.tool tech-stack.json
   ```
2. Check HTTP server is running
3. Confirm CORS settings (if loading remote data)
4. Clear browser cache (Cmd/Ctrl + Shift + Delete)

---

### Issue: Data Not Displaying

**Symptoms:**
- Dashboard loads but no visualizations
- Empty charts/tables
- "No data available" message

**Solutions:**
1. Verify `tech-stack.json` has `solutions` array
2. Check each solution has `packages` and `frameworks` arrays
3. Ensure required fields exist (name, version, risk_score)
4. Review browser console for errors (F12)

---

### Issue: Incorrect Risk Scores

**Symptoms:**
- All technologies show same risk score
- Scores don't match expectations
- Critical items not flagged

**Solutions:**
1. Verify risk scores are calculated in `tech-stack.json`
2. Check risk formula implementation
3. Confirm version comparison logic
4. Review CVE count accuracy

---

### Issue: Performance Degradation

**Symptoms:**
- Slow rendering
- Laggy interactions
- Browser freezes

**Solutions:**
1. Reduce dataset size (filter solutions)
2. Limit packages per solution (<200 recommended)
3. Disable animations in browser settings
4. Use desktop browser (not mobile)
5. Close other browser tabs

---

### Issue: Export Not Working

**Symptoms:**
- "Export" button does nothing
- Download doesn't start
- File is empty or corrupted

**Solutions:**
1. Check browser download settings
2. Allow popups for dashboard site
3. Verify sufficient disk space
4. Try different browser
5. Use backend export commands instead

---

## Best Practices

### Data Preparation

✅ **DO:**
- Keep `tech-stack.json` updated (weekly analysis)
- Include all solutions in single file
- Validate JSON before loading
- Use consistent naming conventions

❌ **DON'T:**
- Mix different project data in one file
- Include test/experimental solutions
- Hard-code file paths (use relative paths)
- Exceed 1000 packages per solution

### Analysis Workflow

1. **Weekly Review**: Run dashboards every Monday
2. **Filter Critical**: Focus on red/yellow items first
3. **Document Findings**: Capture screenshots and notes
4. **Track Progress**: Export roadmaps and track completion
5. **Share Insights**: Present findings in team meetings

### Collaboration

- Share dashboards via team wiki
- Export roadmaps to project management tools
- Schedule monthly tech debt reviews
- Assign migration tasks to sprint backlogs
- Celebrate completed migrations

---

## Additional Resources

- **Developer Guide**: `dashboard-developer-guide.md`
- **Risk Scoring Guide**: `risk-scoring-guide.md`
- **API Documentation**: `docs/api-reference.md`
- **Support**: GitHub Issues or team Slack channel

---

**Questions or Feedback?**  
Contact: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

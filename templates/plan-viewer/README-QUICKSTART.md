# CORTEX 6.0 Plan Viewer - Quick Start Guide

## 🚀 Viewing the Dashboard

### Option 1: Direct File Open (Simplest)
```bash
open /Users/asifhussain/PROJECTS/CORTEX/templates/plan-viewer/cortex-plan-viewer.html
```

### Option 2: Local HTTP Server (Recommended for audit logs)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX/templates/plan-viewer
python3 serve.py
```

Then open: **http://localhost:8090/cortex-plan-viewer.html**

### Option 3: Python Simple HTTP Server
```bash
cd /Users/asifhussain/PROJECTS/CORTEX/templates/plan-viewer
python3 -m http.server 8000
```

Then open: **http://localhost:8000/cortex-plan-viewer.html**

---

## 📊 What You'll See

### 1. **Dashboard Header**
- CORTEX 6.0 title with gradient effect
- Design score badge (97/95)

### 2. **Key Metrics (4 Cards)**
- Total AC-IDs: 97
- Completed: 18 (18.5%)
- Current Phase: 1.5 (STS Validation)
- Test Coverage: 99.4%

### 3. **Progress Charts**
- **Left Chart:** Phase Progress Distribution (Doughnut)
  - Shows how many AC-IDs completed per phase
  - Color-coded by phase status
  
- **Right Chart:** AC-ID Status Breakdown (Bar)
  - 16 Implemented (green)
  - 2 Partial (yellow)
  - 54 Planned (gray)
  - 25 Blocked (pink)

### 4. **Phase Timeline**
Each phase card shows:
- Phase number and name
- Duration and AC-ID count
- Status badge (PARTIAL/IN PROGRESS/BLOCKED)
- Progress bar with percentage
- Collapsible AC-ID lists (click "✅ Completed" or "⏳ Remaining")
- Alert boxes for important info

### 5. **Recent Activity Panel**
- Last 50 audit log entries
- Color-coded by severity (green/yellow/red)
- Real-time refresh every 30 seconds
- Shows timestamp, message, category, metadata

### 6. **Quality Metrics Panel**
- Test Coverage: 99.4%
- Governance Compliance: 100%
- Evidence Bundle Quality: 48%
- Design Score: 97/95
- Infrastructure component status

---

## 🎨 Theme & Colors

**Dark Theme with CORTEX Brand Colors:**
- Cyan (#00d4ff) - Primary, implemented AC-IDs
- Purple (#7b2cbf) - Secondary, gradient accents
- Green (#06ffa5) - Success, completed
- Yellow (#ffbe0b) - Warning, in progress
- Pink (#ff006e) - Danger, errors

---

## 🔄 Auto-Refresh

- **Page:** Reloads every 30 seconds
- **Audit Logs:** Refresh every 30 seconds (in-place)

---

## 📱 Responsive Design

The dashboard works on:
- Desktop (1920x1080 and above)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

---

## 🐛 Troubleshooting

### Charts not loading?
- Check internet connection (Chart.js loads from CDN)
- Open browser console (F12) for errors

### Audit logs showing mock data?
- Ensure audit log files exist in `cortex-brain/audit-logs/`
- Use HTTP server (Option 2 or 3) instead of direct file open
- Check browser console for fetch errors

### Page not updating?
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Clear browser cache
- Check if auto-refresh is enabled (should reload after 30s)

### Bootstrap/Charts not styling?
- Check internet connection (CDN assets)
- Verify CDN links are not blocked

---

## 📂 File Structure

```
templates/plan-viewer/
├── cortex-plan-viewer.html          # Main dashboard (new design)
├── cortex-plan-viewer-old-backup.html  # Original (backup)
├── audit-loader.js                  # Audit log loading system
├── serve.py                         # Development HTTP server
└── README-QUICKSTART.md            # This file
```

---

## 🔧 Customization

### Change Auto-Refresh Interval
Edit `cortex-plan-viewer.html` line ~680:
```javascript
setTimeout(() => {
    location.reload();
}, 30000);  // Change 30000 to desired milliseconds
```

### Add More Metrics
Add new metric card in the `.row.g-3.mb-4` section:
```html
<div class="col-md-3">
    <div class="metric-card">
        <div class="metric-label">Your Metric</div>
        <div class="metric-value" id="yourMetric">100</div>
        <div class="text-muted small">Description</div>
    </div>
</div>
```

### Change Theme Colors
Edit CSS variables in `<style>` section:
```css
:root {
    --cortex-cyan: #00d4ff;
    --cortex-purple: #7b2cbf;
    /* ... change colors here ... */
}
```

---

## ✅ Features Checklist

- [x] Bootstrap 5 Dark Theme
- [x] Responsive design (mobile/tablet/desktop)
- [x] Interactive charts (Chart.js)
- [x] Real-time metrics dashboard
- [x] Collapsible phase details
- [x] Working audit log integration
- [x] Auto-refresh (30s)
- [x] Quality metrics panel
- [x] Infrastructure status indicators
- [x] Gradient text effects
- [x] Hover animations
- [x] Icon system (Bootstrap Icons)

---

## 📝 Related Documents

- **Full Redesign Summary:** `/cortex-brain/documents/validation/plan-viewer-redesign-summary.md`
- **Progress Tracker:** `/cortex-brain/tier1/tracking/progress-tracker.json`
- **AC Index:** `/cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- **Holistic Plan:** `/cortex-brain/documents/cx6-holistic-analysis/holistic-snowball-plan.yaml`

---

## 🎯 Next Steps

1. Open the dashboard using one of the methods above
2. Explore the interactive charts
3. Click on collapsible AC-ID lists in phase cards
4. Watch the audit logs auto-refresh
5. Check quality metrics panel
6. Test responsive design (resize browser window)

---

**Last Updated:** 2026-01-10 22:00 UTC  
**Version:** 2.0 (Complete Redesign)  
**Status:** ✅ Production Ready

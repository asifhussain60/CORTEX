# CORTEX Lens - Landing Page (Sub-Plan 1)

**Status:** 🚀 Ready for Interactive Review  
**Version:** 1.0.0  
**Date:** December 14, 2025

---

## 🎯 What This Is

Landing page/home view for CORTEX Lens dashboard with admin-style aesthetics.

**Features:**
- 6 KPI metric cards (health, files, LOC, coverage, security, dependencies)
- Health radar chart (5 axes: quality, coverage, docs, security, architecture)
- Quick stats grid (language, entry points, tests, layers)
- Glassmorphism design with dark/light theme toggle
- Responsive layout (desktop, tablet, mobile)

---

## 🚀 Quick Start

### Start Live Server
```powershell
# From CORTEX root (D:\PROJECTS\CORTEX)
.\cortex-lens-output\serve-landing.ps1
```

Server will:
- ✅ Start on http://localhost:8000
- ✅ Open browser automatically
- ✅ Keep running in PowerShell (don't close)

### Make Changes
1. Edit files in this directory
2. Press **F5** in browser to see changes
3. Iterate with feedback
4. Press **Ctrl+C** in PowerShell to stop

---

## 📁 File Structure

```
mock-landing/
├── index.html                 # Landing page HTML
│   ├── Header (repo name, theme toggle)
│   ├── Sidebar (5 tabs navigation)
│   └── Main Content
│       ├── KPI Grid (6 cards)
│       ├── Health Radar Chart
│       └── Quick Stats Grid
│
└── assets/
    ├── cortex-unified.css     # Admin dashboard styling
    │   ├── Glassmorphism variables
    │   ├── Header + Sidebar
    │   ├── KPI cards (enhanced)
    │   ├── Chart containers
    │   └── Stats grid
    │
    └── cortex-unified.js      # Interactive features
        ├── Tab switching
        ├── Theme toggle
        ├── KPI animations
        └── Helper functions
```

---

## 🎨 Design Specs

### Typography
- **Headings:** 40-56px (Inter, weight 700-800)
- **Body:** 16-18px (Inter, weight 400-600)
- **Labels:** 14px uppercase (tracking 0.05-0.1em)
- **Values:** 32-56px (weight 800)

### Colors (Dark Theme)
- **Primary:** `#00d4ff` (cyan)
- **Success:** `#00ff88` (green)
- **Warning:** `#ffaa00` (orange)
- **Danger:** `#ff4444` (red)
- **Background:** `#0a0e27` (dark blue)
- **Text:** `#ffffff` (white)

### Spacing
- **Card Padding:** 32-48px
- **Grid Gap:** 24-32px
- **Icon Size:** 64-72px
- **Border Radius:** 12-20px

### Glassmorphism
- **Background:** `rgba(255, 255, 255, 0.05)`
- **Border:** `1px solid rgba(255, 255, 255, 0.1)`
- **Backdrop Filter:** `blur(10px)`
- **Shadow:** `0 8px 32px rgba(0, 0, 0, 0.37)`

---

## 📊 Mock Data (Embedded)

```javascript
const analysisData = {
  metadata: {
    repo_name: "CORTEX",
    total_files: 1247,
    total_loc: 45823,
    languages: {Python: 65.2, JavaScript: 25.3, SQL: 9.5}
  },
  health: {
    overall_score: 85,       // Excellent (green)
    code_quality_score: 78,  // Good (yellow-green)
    test_coverage_score: 71, // Good
    documentation_score: 82, // Excellent
    security_score: 90,      // Excellent
    architecture_score: 88   // Excellent
  },
  testing: {
    total_tests: 327,
    passing_tests: 304,
    coverage_percentage: 69
  }
};
```

---

## 🧪 Interactive Testing Checklist

### Visual Review
- [ ] KPI cards: 6 cards visible, icons 64-72px
- [ ] Health radar: Chart renders with 5 axes
- [ ] Stats grid: 4 items with large icons
- [ ] Glassmorphism: Semi-transparent cards with blur
- [ ] Typography: Large headings, readable body text
- [ ] Spacing: Generous padding and gaps

### Functionality
- [ ] Theme toggle: Switches dark ↔ light
- [ ] Tab navigation: Switches between tabs (others show placeholders)
- [ ] KPI hover: Cards lift on hover
- [ ] Chart hover: Tooltips show exact values
- [ ] Responsive: Works on mobile/tablet/desktop

### Performance
- [ ] Load time: <3 seconds
- [ ] Animations: Smooth 60fps
- [ ] Console: No errors in browser DevTools

---

## 🔧 How to Modify

### Change KPI Values
Edit `index.html` line ~180:
```html
<div class="kpi-value">85</div>  <!-- Change this -->
```

Or edit embedded `analysisData` object (bottom of file).

### Adjust Colors
Edit `assets/cortex-unified.css`:
```css
:root[data-theme="dark"] {
    --accent-primary: #00d4ff;  /* Change primary color */
    --accent-success: #00ff88;  /* Change success color */
}
```

### Modify Chart
Edit `index.html` Chart.js initialization (~line 250):
```javascript
data: [78, 71, 82, 90, 88],  // Update scores
```

### Add New KPI Card
1. Copy existing `.kpi-card` block in HTML
2. Update icon, value, label
3. Grid auto-adjusts (no CSS change needed)

---

## 📝 Feedback & Iteration

### Feedback Template
```
✅ WORKS WELL:
- [What you like]

🔧 NEEDS CHANGE:
- Issue: [What's wrong]
  Fix: [What you want]

💡 SUGGESTIONS:
- [Optional improvements]

DECISION: [✅ Approved / 🔄 Revise / ❌ Reject]
```

### After Approval
1. Stop server (Ctrl+C)
2. Git commit: `feat(lens): Landing page complete`
3. Update progress tracker
4. Create Sub-Plan 2 (Executive Brief Tab)

---

## 🐛 Known Issues

None yet - report issues during interactive review.

---

## 🔗 Related Documents

- **Sub-Plan:** `../CORTEX-LENS-V3-SUBPLAN-1-LANDING-PAGE.md`
- **Master Plan:** `../CORTEX-LENS-V3-MASTER-SUBPLAN.md`
- **Quick Guide:** `../CORTEX-LENS-INTERACTIVE-DEV-GUIDE.md`
- **Parent Plan:** `../CORTEX-LENS-V3.md`

---

**Ready to review?** Run: `.\cortex-lens-output\serve-landing.ps1`

**Questions?** Check `CORTEX-LENS-INTERACTIVE-DEV-GUIDE.md`

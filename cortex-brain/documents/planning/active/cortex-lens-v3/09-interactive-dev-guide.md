# CORTEX Lens - Quick Start Guide for Interactive Development

**Version:** 1.0.0  
**Date:** December 14, 2025  
**Purpose:** Live development workflow for view-by-view implementation

---

## 🚀 Quick Start (3 Steps)

### 1. Start Live Server

```powershell
# From CORTEX root directory
cd D:\PROJECTS\CORTEX
.\cortex-lens-output\serve-landing.ps1
```

**What Happens:**
- ✅ Server starts on http://localhost:8000
- ✅ Browser opens automatically
- ✅ Landing page displays with mock data
- ✅ PowerShell window stays open (keep it running)

### 2. Make Changes

Edit any file in `cortex-lens-output\mock-landing\`:
- `index.html` - HTML structure
- `assets\cortex-unified.css` - Styling
- `assets\cortex-unified.js` - JavaScript logic

### 3. See Changes

**Press F5** in browser → Changes appear instantly

---

## 📁 File Structure

```
cortex-lens-output/
├── serve-landing.ps1              # Live server (run this)
└── mock-landing/                  # Edit these files ↓
    ├── index.html                 # Landing page
    └── assets/
        ├── cortex-unified.css     # Admin dashboard styles
        └── cortex-unified.js      # Tab system + interactions
```

---

## 🎨 Current Implementation Status

### ✅ Complete (Ready to Review)

**Landing Page Components:**
- 6 KPI cards (Health, Files, LOC, Coverage, Security, Dependencies)
- Health radar chart (Chart.js, 5 axes)
- Quick stats grid (4 items)
- Glassmorphism styling (admin dashboard aesthetic)
- Theme toggle (dark/light)
- Tab navigation system

**Mock Data:**
- Embedded in `index.html` (no external files)
- Simulates CORTEX repository analysis
- Health scores: 85 overall, 78 quality, 71 coverage, 90 security

### ⏳ Placeholder (Coming Later)

**Other Tabs:**
- Architecture (Sub-Plan 3)
- Code Quality (Sub-Plan 4)
- Dependencies (Sub-Plan 5)
- Testing (Sub-Plan 5)

---

## 🔄 Interactive Development Workflow

### Typical Session

```
1. START:    .\cortex-lens-output\serve-landing.ps1
             └─→ Browser opens automatically

2. REVIEW:   Check landing page visuals
             └─→ User provides feedback

3. EDIT:     Modify index.html / CSS / JS
             └─→ Save files

4. REFRESH:  Press F5 in browser
             └─→ See changes immediately

5. ITERATE:  Repeat steps 2-4 until approved
             └─→ User says "✅ Approved"

6. STOP:     Ctrl+C in PowerShell
             └─→ Server stops
```

---

## 🎯 User Review Checklist

When reviewing the landing page, check:

### Visual Design
- [ ] **Glassmorphism:** Semi-transparent cards with blur effect?
- [ ] **Typography:** Large headings (40-56px), readable body text?
- [ ] **Icons:** Emoji icons 64-72px, visually impactful?
- [ ] **Spacing:** Generous padding (32-48px), comfortable gaps?
- [ ] **Colors:** Cyan (#00d4ff) primary, consistent accents?

### KPI Cards
- [ ] **Layout:** 6 cards in responsive grid (3 columns on desktop)?
- [ ] **Content:** Icon + value + label + trend all visible?
- [ ] **Color Coding:** Health scores show correct colors?
  - Green (85+): Excellent
  - Yellow (60-84): Good
  - Orange (40-59): Fair
  - Red (<40): Poor
- [ ] **Hover:** Cards lift on hover with smooth animation?
- [ ] **Trends:** Trend indicators (↑/→/↓) make sense?

### Health Radar Chart
- [ ] **Rendering:** Chart displays without console errors?
- [ ] **Data:** 5 axes showing correct scores (78, 71, 82, 90, 88)?
- [ ] **Colors:** Cyan theme (#00d4ff) matching design?
- [ ] **Interactivity:** Hover shows tooltips?
- [ ] **Labels:** Axis labels readable and positioned correctly?

### Navigation
- [ ] **Sidebar:** 5 tabs listed (Overview, Architecture, Quality, Deps, Testing)?
- [ ] **Active State:** Overview tab highlighted?
- [ ] **Click:** Tab switching works (placeholders shown)?
- [ ] **Theme Toggle:** Dark/light mode switches correctly?

### Performance
- [ ] **Load Time:** Page loads in <3 seconds?
- [ ] **Smooth:** Animations fluid (60fps)?
- [ ] **No Errors:** Browser console clean?

---

## 🐛 Troubleshooting

### Server Won't Start
```powershell
# Check Python is installed
python --version  # Should show 3.8+

# Try manual server
cd cortex-lens-output\mock-landing
python -m http.server 8000
# Then open: http://localhost:8000
```

### Browser Not Opening
```powershell
# Manually open in browser
Start-Process "http://localhost:8000"

# Or copy URL and paste in browser
```

### Changes Not Showing
```powershell
# Hard refresh (bypass cache)
# Chrome: Ctrl+Shift+R
# Firefox: Ctrl+F5
# Edge: Ctrl+F5
```

### Port Already in Use
```powershell
# Use different port
.\cortex-lens-output\serve-landing.ps1 -Port 8080
```

---

## 💬 Feedback Template

**When reviewing, provide structured feedback:**

```
✅ WORKS WELL:
- [What you like about current implementation]

🔧 NEEDS CHANGE:
- Issue: [Describe what's wrong]
  Fix: [What you want instead]

💡 SUGGESTIONS:
- [Optional enhancements]

DECISION:
[ ] ✅ APPROVED - Move to next sub-plan
[ ] 🔄 REVISE - Make changes listed above
[ ] ❌ REJECT - Major redesign needed
```

---

## 📊 Next Steps After Approval

Once landing page is approved:

1. **Git Checkpoint:**
   ```bash
   git add cortex-lens-output/mock-landing/
   git commit -m "feat(lens): Landing page complete - Sub-Plan 1"
   ```

2. **Update Progress:**
   - Mark Sub-Plan 1 as ✅ Complete
   - Update master tracker

3. **Create Next Sub-Plan:**
   - Generate Sub-Plan 2: Executive Brief Tab
   - Start with 7 narrative engines

---

## 🔗 Related Files

- **Plan:** `CORTEX-LENS-V3-SUBPLAN-1-LANDING-PAGE.md`
- **Master:** `CORTEX-LENS-V3-MASTER-SUBPLAN.md`
- **Server:** `cortex-lens-output\serve-landing.ps1`
- **HTML:** `cortex-lens-output\mock-landing\index.html`
- **CSS:** `cortex-lens-output\mock-landing\assets\cortex-unified.css`
- **JS:** `cortex-lens-output\mock-landing\assets\cortex-unified.js`

---

**Ready to start?** Run: `.\cortex-lens-output\serve-landing.ps1`

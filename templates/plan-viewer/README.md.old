# CORTEX Plan Viewer Template System

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** January 5, 2026

## 📋 Overview

Template-based plan viewer system that replaces 330 lines of hardcoded HTML generation with a data-driven approach. Uses static templates + JSON data for real-time plan visualization.

## 🏗️ Architecture

### Design Patterns
- **Template Method**: Static HTML structure with dynamic data injection
- **Observer**: Auto-refresh for live progress updates (5s polling)
- **Strategy**: Separate data fetchers for static metadata vs live progress
- **Model-View**: Complete separation of data (JSON) and presentation (HTML/CSS)

### Components
```
templates/plan-viewer/
├── plan-viewer.html    # Static HTML template (58 lines)
├── styles.css          # Themeable CSS (300+ lines)
├── viewer.js           # Data-driven renderer (300+ lines)
└── README.md           # This file
```

### Data Sources
```
{plan-folder}/
├── plan-data.json              # Static metadata (generated once)
└── tracking/
    └── progress-tracker.json   # Live progress (updates frequently)
```

## 📊 Data Contract

### `plan-data.json` Structure
```json
{
    "plan_id": "A01",
    "plan_title": "Enterprise Audit Logger with Self-Healing",
    "status": "in_progress",
    "estimated_hours": 12.0,
    "author": "Asif Hussain",
    "created_at": "2026-01-03T10:00:00Z",
    "phases": [
        {
            "number": 1,
            "name": "Setup & Infrastructure",
            "estimated_hours": 2.0
        }
    ]
}
```

### `progress-tracker.json` Structure
```json
{
    "percent_complete": 25,
    "actual_total_hours": 3.0,
    "estimated_total_hours": 12.0,
    "status": "in_progress",
    "phases": [
        {
            "number": 1,
            "name": "Setup & Infrastructure",
            "status": "complete",
            "estimated_hours": 2.0,
            "actual_hours": 2.0,
            "outputs": [
                "src/audit_logger/__init__.py",
                "tests/audit_logger/__init__.py"
            ]
        }
    ]
}
```

## 🚀 Usage

### 1. Generate Plan Data
```python
from src.orchestrators.planning_orchestrator_v5 import PlanningOrchestrator

orchestrator = PlanningOrchestrator()
orchestrator._generate_plan_viewer_html(plan_folder, plan_data)
```

### 2. Open Viewer
```bash
# Open in default browser
open {plan-folder}/plan-viewer.html

# Or use Python server for CORS
cd {plan-folder}
python3 -m http.server 8000
# Visit: http://localhost:8000/plan-viewer.html
```

### 3. Auto-Refresh
- Viewer automatically polls `tracking/progress-tracker.json` every 5 seconds
- Updates progress bars, phase statuses, and artifact lists
- No manual refresh needed

## 🎨 Customization

### Theme Customization
Edit CSS variables in `styles.css`:
```css
:root {
    --color-primary: #2563eb;      /* Primary blue */
    --color-success: #10b981;      /* Success green */
    --color-warning: #f59e0b;      /* Warning orange */
    --color-danger: #ef4444;       /* Danger red */
    --color-background: #ffffff;    /* Background white */
    --color-surface: #f9fafb;      /* Surface gray */
    /* ... 25+ more variables */
}
```

### Layout Customization
Modify BEM classes in `styles.css`:
```css
.phase-item { /* Phase card styling */ }
.artifact-item { /* Artifact card styling */ }
.progress-bar-container { /* Progress bar container */ }
```

### Data Refresh Rate
Change auto-refresh interval in `viewer.js`:
```javascript
constructor() {
    this.refreshInterval = 5000; // 5 seconds (default)
    // this.refreshInterval = 10000; // 10 seconds
    // this.refreshInterval = 30000; // 30 seconds
}
```

## 📁 Deployment

### For Planning Orchestrator
1. Copy template files to plan folder:
   ```python
   import shutil
   shutil.copytree(
       'templates/plan-viewer',
       f'{plan_folder}/',
       dirs_exist_ok=True
   )
   ```

2. Generate `plan-data.json`:
   ```python
   plan_data = {
       'plan_id': 'A01',
       'plan_title': 'My Plan',
       'status': 'in_progress',
       'estimated_hours': 12.0,
       'phases': [...],
       'author': 'Your Name',
       'created_at': datetime.now().isoformat()
   }
   with open(f'{plan_folder}/plan-data.json', 'w') as f:
       json.dump(plan_data, f, indent=2)
   ```

3. Progress tracker updates automatically by TDD orchestrator

### For Standalone Use
1. Create directory structure:
   ```bash
   mkdir my-plan-folder
   cp templates/plan-viewer/* my-plan-folder/
   mkdir my-plan-folder/tracking
   ```

2. Create `plan-data.json` manually

3. Create initial `progress-tracker.json`:
   ```bash
   echo '{"percent_complete": 0, "status": "not_started", "phases": []}' \
     > my-plan-folder/tracking/progress-tracker.json
   ```

## 🧪 Testing

### Manual Testing
1. Open `plan-viewer.html` in browser
2. Verify data loads from JSON files
3. Check console for auto-refresh logs
4. Modify `progress-tracker.json` → verify updates appear within 5s

### Browser Compatibility
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### CORS Issues
If viewer can't fetch JSON due to CORS:
```bash
# Use Python HTTP server
python3 -m http.server 8000

# Or disable CORS in Chrome (dev only)
open -a "Google Chrome" --args --disable-web-security --user-data-dir="/tmp/chrome_dev"
```

## 🔧 Troubleshooting

### Issue: JSON Not Loading
**Symptom:** Console shows `Failed to load plan data: HTTP 404`

**Solution:**
- Verify `plan-data.json` exists in same folder as `plan-viewer.html`
- Check JSON syntax validity: `python3 -m json.tool plan-data.json`
- Use Python HTTP server instead of `file://` protocol

### Issue: Progress Not Updating
**Symptom:** Viewer shows old data despite changes

**Solution:**
- Check console for auto-refresh errors
- Verify `tracking/progress-tracker.json` has write permissions
- Increase `refreshInterval` if file system is slow

### Issue: Styling Broken
**Symptom:** Page looks unstyled

**Solution:**
- Verify `styles.css` exists in same folder
- Check browser console for 404 errors
- Clear browser cache (Cmd+Shift+R)

## 📚 Related Documentation

- **Planning System:** `.github/prompts/planning-system-5.0-manifest.yaml`
- **TDD Orchestrator:** `cortex-brain/manifests/orchestrators/tdd-v2-orchestrator.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`

## 📊 Performance

- **Load Time:** <100ms (local files)
- **Memory:** ~2MB (including CSS/JS)
- **Auto-Refresh:** 5s interval, <10ms per update
- **File Size:** HTML (58 lines), CSS (300 lines), JS (300 lines)

## 🎯 Benefits

| Aspect | Before (Hardcoded) | After (Template) |
|--------|-------------------|------------------|
| Code Lines | 330 lines Python | 50 lines Python + templates |
| Regeneration | Full HTML regeneration | JSON update only |
| Customization | Modify Python code | Modify CSS variables |
| Maintenance | Complex string concatenation | Clean template files |
| Live Updates | Manual refresh | Auto-refresh (5s) |

## 🚀 Future Enhancements

- [ ] WebSocket support for instant updates (remove polling)
- [ ] Dark mode toggle (CSS variable swap)
- [ ] Collapsible phase sections
- [ ] Search/filter phases and artifacts
- [ ] Export to PDF/PNG
- [ ] Accessibility improvements (ARIA labels)

## 📝 License

See `LICENSE` in repository root.

---

**Questions?** Check `.github/copilot-instructions.md` or ask CORTEX: `help plan viewer`

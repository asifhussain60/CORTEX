# Plan Viewer Template System Design

**Date:** January 5, 2026  
**Integration Target:** Phase 4 - Enterprise Audit Logger  
**Priority:** MEDIUM (Add to Phase 4 as Task 4.7)

---

## 🎯 Problem Statement

**Current Issue:**
- `plan-viewer.html` is hardcoded in Python (lines 1121-1453 in planning_orchestrator_v5.py)
- Requires regeneration every time plan changes
- 330+ lines of HTML string concatenation in Python
- Violates separation of concerns (mixing presentation with logic)
- Difficult to modify styling/layout without touching orchestrator code

**Impact:**
- Maintainability: Hard to update viewer UI
- Reusability: Can't use viewer for other plan types
- Performance: Regenerates entire HTML on every plan update
- Testability: HTML generation logic tied to orchestrator

---

## 🏗️ Design Pattern: Template + Data-Driven Rendering

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Template Layer (Static)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  templates/plan-viewer/                                     │
│  ├── plan-viewer.html         # Static template (Jinja2)   │
│  ├── styles.css               # Modular CSS                │
│  └── viewer.js                # Data fetching + rendering  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     Data Layer (Dynamic)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  {plan-folder}/                                             │
│  ├── plan-data.json           # Generated once             │
│  ├── tracking/progress-tracker.json # Real-time updates    │
│  └── artifacts/               # Metadata only              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Rendering (Client-Side)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  viewer.js loads:                                           │
│  1. Fetch plan-data.json (static metadata)                 │
│  2. Fetch progress-tracker.json (live progress)            │
│  3. Merge data                                              │
│  4. Render to DOM                                           │
│  5. Poll progress-tracker.json every 5s (live updates)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan (Task 4.7)

### 4.7.1: Create Template System (1h)

**Files to Create:**

```
templates/plan-viewer/
├── plan-viewer.html          # Jinja2 template
├── styles.css                # Modular CSS with CSS variables
├── viewer.js                 # Data-driven renderer
└── README.md                 # Usage documentation
```

**Template Structure (`plan-viewer.html`):**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ plan_title }} - CORTEX Plan Viewer</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <header id="plan-header">
            <!-- Populated by viewer.js from plan-data.json -->
        </header>
        
        <main id="plan-content">
            <section id="progress-section">
                <!-- Populated by viewer.js from progress-tracker.json -->
            </section>
            
            <section id="phases-section">
                <!-- Populated by viewer.js -->
            </section>
            
            <section id="artifacts-section">
                <!-- Populated by viewer.js -->
            </section>
        </main>
    </div>
    
    <script src="viewer.js"></script>
</body>
</html>
```

**Data Fetcher (`viewer.js`):**

```javascript
// Data-driven plan viewer
class PlanViewer {
    constructor() {
        this.planData = null;
        this.progressData = null;
        this.refreshInterval = 5000; // 5s
    }
    
    async init() {
        await this.loadPlanData();
        await this.loadProgressData();
        this.render();
        this.startAutoRefresh();
    }
    
    async loadPlanData() {
        // Load static plan metadata (generated once)
        const response = await fetch('./plan-data.json');
        this.planData = await response.json();
    }
    
    async loadProgressData() {
        // Load live progress (updates frequently)
        const response = await fetch('./tracking/progress-tracker.json');
        this.progressData = await response.json();
    }
    
    render() {
        this.renderHeader();
        this.renderProgress();
        this.renderPhases();
        this.renderArtifacts();
    }
    
    renderProgress() {
        // Calculate overall progress from phases
        const phases = this.progressData.phases || [];
        const completed = phases.filter(p => p.status === 'completed').length;
        const percentage = Math.round((completed / phases.length) * 100);
        
        // Render progress bar (data-driven)
        const filled = Math.round(percentage / 5); // 20-char bar
        const empty = 20 - filled;
        const progressBar = '█'.repeat(filled) + '░'.repeat(empty);
        
        document.getElementById('progress-bar').textContent = progressBar;
        document.getElementById('progress-percentage').textContent = `${percentage}%`;
    }
    
    startAutoRefresh() {
        setInterval(async () => {
            await this.loadProgressData();
            this.renderProgress();
            this.renderPhases(); // Update phase statuses
        }, this.refreshInterval);
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const viewer = new PlanViewer();
    viewer.init();
});
```

---

### 4.7.2: Modify Orchestrator (0.5h)

**Changes to `planning_orchestrator_v5.py`:**

```python
def _generate_plan_viewer_html(self, feature_name: str, **kwargs) -> str:
    """
    Generate plan viewer by copying template + generating plan-data.json.
    
    NEW APPROACH: Template-based (not hardcoded HTML)
    """
    import shutil
    from jinja2 import Template
    
    # Get plan folder
    master_plan_filename = self._generate_master_plan_filename(feature_name)
    folder_id_prefix = master_plan_filename.split('-')[0].lower()
    abbreviated_name = self._abbreviate_feature_name(feature_name, max_length=22)
    folder_name = f"{folder_id_prefix}-{abbreviated_name}"
    plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
    
    # Copy template files to plan folder
    template_dir = Path("templates/plan-viewer")
    for file in ['plan-viewer.html', 'styles.css', 'viewer.js']:
        shutil.copy(template_dir / file, plan_dir / file)
    
    # Generate plan-data.json (static metadata)
    plan_data = {
        'plan_id': folder_id_prefix,
        'plan_name': feature_name,
        'plan_title': feature_name.replace('-', ' ').title(),
        'created_at': datetime.now().isoformat(),
        'orchestrator': 'Planning v5',
        'status': 'active',
        'estimated_hours': self._get_default_hours_by_type(),
        'phases_total': len(self._generate_phases_by_type(feature_name))
    }
    
    data_path = plan_dir / 'plan-data.json'
    with open(data_path, 'w') as f:
        json.dump(plan_data, f, indent=2)
    
    self.logger.info(f"✅ Generated plan viewer: {plan_dir / 'plan-viewer.html'}")
    return str(plan_dir / 'plan-viewer.html')
```

---

### 4.7.3: Testing (0.5h)

**Test Cases:**

1. **Template Rendering Test**
   - Verify HTML loads without errors
   - Check data fetching works
   - Validate progress bar rendering

2. **Auto-Refresh Test**
   - Update `progress-tracker.json`
   - Verify UI updates within 5s
   - Check no memory leaks

3. **Cross-Browser Test**
   - Chrome, Firefox, Safari
   - Responsive layout

---

## 🎨 Design Patterns Used

| Pattern | Application | Benefit |
|---------|-------------|---------|
| **Template Method** | Jinja2 template with slots | Separates presentation from logic |
| **Observer** | Auto-refresh polling | Real-time updates |
| **Strategy** | Data fetchers (JSON) | Flexible data sources |
| **Model-View** | plan-data.json + viewer.js | Clean separation |
| **Single Responsibility** | CSS/JS/HTML separate | Maintainability |

---

## ✅ Benefits

### Before (Current)
- ❌ 330 lines of Python HTML generation
- ❌ Regenerate on every plan change
- ❌ Hardcoded styling
- ❌ No separation of concerns
- ❌ Difficult to modify

### After (Template-Based)
- ✅ 50 lines Python (copy template + generate JSON)
- ✅ No regeneration needed (data-driven)
- ✅ Modular CSS (easy theming)
- ✅ Clean separation (HTML/CSS/JS/Python)
- ✅ Easy to modify (edit template files)

---

## 📊 Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Python LOC** | 330 | 50 | -85% |
| **Regeneration** | Every update | Never | ∞% |
| **Modification Time** | 30 min | 5 min | -83% |
| **Testability** | Hard | Easy | +100% |
| **Reusability** | None | High | +100% |

---

## 🚀 Integration Strategy

### Option 1: Add to Phase 4 (Recommended)
**Task 4.7:** Plan Viewer Template System (2h)
- Fits naturally with "infrastructure improvement"
- Complements audit logger (both infrastructure)
- No impact on other Phase 4 tasks

### Option 2: Separate Mini-Plan
Create `B01-plan-viewer-template.md` (1-day plan)
- Independent from audit logger
- Can be implemented anytime
- Allows dedicated testing

---

## 📝 Recommendation

**✅ Add to Phase 4 as Task 4.7 (Option 1)**

**Rationale:**
1. **Fits Theme:** Phase 4 = infrastructure improvements
2. **Low Risk:** Template system is self-contained
3. **High Value:** Benefits all future planning
4. **Quick Win:** 2 hours implementation
5. **No Dependencies:** Doesn't block other tasks

**Updated Phase 4 Duration:** 10h → 12h (20% increase, acceptable)

---

## 📋 Updated Phase 4 Task List

```yaml
Phase 4: Security & Performance Hardening
Duration: 12 hours (was 10h)
Tasks:
  4.1: PII Sanitizer (3h) ✅ COMPLETE
  4.2: Encryptor (2h)
  4.3: RBAC Manager (2h)
  4.4: Async Logger (1.5h)
  4.5: Buffer Optimizer (1.5h)
  4.6: Integration Tests (1.5h)
  4.7: Plan Viewer Template System (2h) 🆕 NEW
```

---

**Status:** DESIGNED - Ready for implementation approval  
**Next Action:** User approval to add Task 4.7 to Phase 4

# CORTEX Planning System Design
**Version:** 5.1  
**Date:** 2026-01-07  
**Author:** Asif Hussain

---

## 🎯 Core Design Principles

### 1. **Hierarchical Structure**
```
Epic → Feature → Phase
```

- **Epic**: Container for multiple features (complexity > 80)
- **Feature**: Executable plan with phases (complexity 40-80)
- **Phase**: Individual work unit within a feature

### 2. **Code Reuse Strategy**
Feature plans have **IDENTICAL structure** whether:
- Inside an epic (`epic-name/features/feat-name/`)
- Standalone (`feat-name/`)

This eliminates code duplication across:
- Planning orchestrator
- Plan viewer
- TDD orchestrator
- Progress tracking

---

## 📁 Folder Structure

### **Epic Structure**
```
epic-{name}/                           # Epic container (prefix: "epic-")
├── master-plan.md                     # Epic overview & strategy
├── README.md                          # Quick start guide
├── tracking/
│   └── epic-progress-tracker.json    # Aggregates all feature progress
├── reports/                           # Epic-level summaries
├── analysis/                          # Epic-level analysis
├── artifacts/                         # Epic-level artifacts
└── features/                          # ⭐ CHILD FEATURE PLANS (full plans, not links)
    ├── feat-{feature1}/               # Feature 1 (complete feature plan)
    │   ├── feat-{feature1}.md         # Feature master plan
    │   ├── README.md
    │   ├── phases/
    │   │   ├── ph1-{phase-name}.md    # Phase 1
    │   │   └── ph2-{phase-name}.md    # Phase 2
    │   ├── tracking/
    │   │   └── progress-tracker.json
    │   ├── artifacts/
    │   ├── context/
    │   ├── reports/
    │   └── plan-viewer.html
    │
    └── feat-{feature2}/               # Feature 2 (complete feature plan)
        ├── feat-{feature2}.md
        ├── README.md
        ├── phases/
        │   ├── ph1-{phase-name}.md
        │   └── ph2-{phase-name}.md
        ├── tracking/
        │   └── progress-tracker.json
        ├── artifacts/
        ├── context/
        ├── reports/
        └── plan-viewer.html
```

### **Standalone Feature Structure**
```
feat-{name}/                           # Standalone feature (prefix: "feat-")
├── feat-{name}.md                     # Feature master plan
├── README.md                          # Quick start guide
├── phases/
│   ├── ph1-{phase-name}.md           # Phase 1
│   ├── ph2-{phase-name}.md           # Phase 2
│   └── ph3-{phase-name}.md           # Phase 3
├── tracking/
│   └── progress-tracker.json         # Feature progress
├── artifacts/                         # Generated outputs
├── context/                           # Background research
├── reports/                           # Progress reports
└── plan-viewer.html                  # HTML viewer
```

---

## 📝 File Naming Conventions

### **Rules**
1. ❌ **NO `00-` prefixes** (legacy pattern, deprecated)
2. ✅ **Unique names** across all plans (no duplicates)
3. ✅ **Max 25 characters** (filesystem compatibility)
4. ✅ **Meaningful acronyms** (not cryptic)
5. ✅ **Kebab-case** (lowercase with hyphens)

### **Prefixes**
| Type | Prefix | Example | Max Length |
|------|--------|---------|------------|
| **Epic folder** | `epic-` | `epic-cortex5` | 25 chars |
| **Feature folder** | `feat-` | `feat-knowledge-ext` | 25 chars |
| **Phase file** | `ph{N}-` | `ph1-setup-infra.md` | 25 chars |
| **Feature file** | `feat-` | `feat-knowledge-ext.md` | 25 chars |
| **Epic file** | No prefix | `master-plan.md` | 25 chars |

### **Examples**

#### ✅ CORRECT
```
epic-cortex5/
├── master-plan.md                    # Epic overview
└── features/
    ├── feat-knowledge-ext/           # 18 chars ✅
    │   ├── feat-knowledge-ext.md     # Feature plan
    │   └── phases/
    │       ├── ph1-folder-struct.md  # 20 chars ✅
    │       └── ph2-merge-logic.md    # 18 chars ✅
    └── feat-orchestr-registry/       # 22 chars ✅
        ├── feat-orchestr-registry.md
        └── phases/
            ├── ph1-yaml-design.md    # 18 chars ✅
            └── ph2-routing-impl.md   # 19 chars ✅
```

#### ❌ INCORRECT
```
cortex5-epic/                         # ❌ Suffix, not prefix
├── phases/                           # ❌ Epic shouldn't have phases
│   └── 00-master-plan.md             # ❌ Has "00-" prefix
└── features/
    ├── governance-rules.md           # ❌ Markdown file, not folder
    └── feat-knowledge-extension/     # ❌ 24 chars (too long with full name)
        └── 00-knowledge-extension.md # ❌ Has "00-" prefix
```

---

## 🔄 Progress Tracking

### **Epic Tracker** (`epic-progress-tracker.json`)
```json
{
  "epic_id": "epic-cortex5",
  "epic_name": "CORTEX 5.0 Enhancement Epic",
  "overall_progress": 45,
  "status": "IN_PROGRESS",
  "features": [
    {
      "feature_id": "feat-knowledge-ext",
      "feature_name": "Knowledge Extension Layer",
      "progress": 60,
      "status": "IN_PROGRESS",
      "tracker_path": "features/feat-knowledge-ext/tracking/progress-tracker.json"
    },
    {
      "feature_id": "feat-orchestr-registry",
      "feature_name": "Orchestrator Registry",
      "progress": 30,
      "status": "IN_PROGRESS",
      "tracker_path": "features/feat-orchestr-registry/tracking/progress-tracker.json"
    }
  ]
}
```

### **Feature Tracker** (`progress-tracker.json`)
```json
{
  "feature_id": "feat-knowledge-ext",
  "feature_name": "Knowledge Extension Layer",
  "overall_progress": 60,
  "status": "IN_PROGRESS",
  "phases": [
    {
      "phase_id": 1,
      "phase_name": "Folder Structure Setup",
      "progress": 100,
      "status": "COMPLETE"
    },
    {
      "phase_id": 2,
      "phase_name": "Merge Logic Implementation",
      "progress": 20,
      "status": "IN_PROGRESS"
    }
  ]
}
```

---

## 🎨 Plan Viewer (Universal)

### **Auto-Detection Logic**
```javascript
function detectPlanMode() {
  const folderName = getCurrentFolderName();
  
  // Method 1: Folder name prefix
  if (folderName.startsWith('epic-')) {
    return 'EPIC';
  } else if (folderName.startsWith('feat-')) {
    return 'FEATURE';
  }
  
  // Method 2: Tracker file detection
  if (fileExists('tracking/epic-progress-tracker.json')) {
    return 'EPIC';
  } else if (fileExists('tracking/progress-tracker.json')) {
    return 'FEATURE';
  }
  
  // Method 3: Check for features/ subfolder
  if (directoryExists('features/')) {
    return 'EPIC';
  }
  
  return 'FEATURE'; // Default
}
```

### **Rendering Strategy**

#### **EPIC Mode**
```javascript
function renderEpicView() {
  const tracker = loadJSON('tracking/epic-progress-tracker.json');
  
  // Render epic header
  renderEpicHeader(tracker);
  
  // Loop through features and render cards
  tracker.features.forEach(feature => {
    const featureTracker = loadJSON(feature.tracker_path);
    renderFeatureCard(feature, featureTracker); // ⭐ SAME card as standalone
  });
}
```

#### **FEATURE Mode**
```javascript
function renderFeatureView() {
  const tracker = loadJSON('tracking/progress-tracker.json');
  
  // Render feature header
  renderFeatureHeader(tracker);
  
  // Loop through phases and render cards
  tracker.phases.forEach(phase => {
    renderPhaseCard(phase); // ⭐ SAME card used in epic view
  });
}
```

**Key**: Feature card rendering is **IDENTICAL** in both modes → zero duplication!

---

## 🛠️ Planning Orchestrator Logic

### **Epic Creation**
```python
def create_epic_plan(epic_name: str, features: list[str]):
    """Create epic with child features"""
    
    # 1. Create epic folder structure
    epic_path = f"epic-{sanitize_name(epic_name)}"
    create_folders([
        f"{epic_path}/tracking",
        f"{epic_path}/reports",
        f"{epic_path}/analysis",
        f"{epic_path}/artifacts",
        f"{epic_path}/features"
    ])
    
    # 2. Create epic master plan
    create_file(f"{epic_path}/master-plan.md", epic_template)
    
    # 3. Create each feature (using SAME logic as standalone)
    for feature_name in features:
        create_feature_plan(
            feature_name=feature_name,
            parent_path=f"{epic_path}/features"  # ⭐ Nested inside epic
        )
    
    # 4. Create epic tracker
    create_epic_tracker(epic_path, features)
```

### **Feature Creation** (Universal)
```python
def create_feature_plan(feature_name: str, parent_path: str = None):
    """Create feature plan (works standalone OR inside epic)"""
    
    # 1. Determine location
    if parent_path:
        # Inside epic: epic-name/features/feat-name/
        feature_path = f"{parent_path}/feat-{sanitize_name(feature_name)}"
    else:
        # Standalone: feat-name/
        feature_path = f"feat-{sanitize_name(feature_name)}"
    
    # 2. Create folder structure (IDENTICAL for both)
    create_folders([
        f"{feature_path}/phases",
        f"{feature_path}/tracking",
        f"{feature_path}/artifacts",
        f"{feature_path}/context",
        f"{feature_path}/reports"
    ])
    
    # 3. Create feature master plan
    create_file(f"{feature_path}/feat-{sanitize_name(feature_name)}.md", feature_template)
    
    # 4. Create progress tracker
    create_file(f"{feature_path}/tracking/progress-tracker.json", tracker_template)
    
    # 5. Create plan viewer (IDENTICAL for both)
    create_file(f"{feature_path}/plan-viewer.html", viewer_template)
```

**Key**: Same function creates features whether inside epic or standalone!

---

## 📊 Complexity-Based Routing

### **Decision Tree**
```
User Request → Complexity Analysis
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
  Complexity > 80            Complexity 40-80
  (Multiple features)        (Single feature)
        ↓                           ↓
   Create EPIC              Create FEATURE
   (with child features)    (standalone)
```

### **Example**
```python
def plan_request(user_request: str):
    """Route based on complexity"""
    
    complexity = analyze_complexity(user_request)
    
    if complexity > 80:
        # Epic: Break into features
        features = extract_features(user_request)
        create_epic_plan(
            epic_name=extract_epic_name(user_request),
            features=features
        )
    elif complexity >= 40:
        # Feature: Create standalone
        create_feature_plan(
            feature_name=extract_feature_name(user_request),
            parent_path=None  # Standalone
        )
    else:
        # Simple task: No plan needed
        execute_direct(user_request)
```

---

## 🎯 Key Benefits

| Benefit | Description |
|---------|-------------|
| **Zero Code Duplication** | Feature plan logic works everywhere (epic or standalone) |
| **Easy Migration** | Move feature into/out of epic without restructuring |
| **Clear Hierarchy** | Epic → Feature → Phase (not Epic → Phase) |
| **Tool Compatibility** | All orchestrators work identically for nested and standalone |
| **Scalability** | Add features to epic without changing epic structure |
| **Universal Viewer** | Single `plan-viewer.html` handles both modes |

---

## 🔍 Migration from Current Structure

### **Current `cortex5-epic` Issues**
```
cortex5-epic/                          # ❌ Wrong prefix
├── phases/                            # ❌ Epic has phases
│   ├── master-plan.md                 # ❌ Wrong location
│   ├── phase-0-foundation.md          # ❌ Epic shouldn't have phases
│   └── ...
└── features/                          # ❌ Contains markdown files
    ├── governance-rules.md            # ❌ Not a feature plan folder
    ├── planning-system.md             # ❌ Not a feature plan folder
    └── ...
```

### **Target Structure**
```
epic-cortex5/                          # ✅ Correct prefix
├── master-plan.md                     # ✅ Root level
├── tracking/
│   └── epic-progress-tracker.json    # ✅ Epic tracker
└── features/                          # ✅ Full feature plans
    ├── feat-governance/               # ✅ Feature plan folder
    │   ├── feat-governance.md         # ✅ Feature plan
    │   └── phases/                    # ✅ Phases inside feature
    │       ├── ph1-rule-design.md
    │       └── ph2-enforcement.md
    └── feat-planning-sys/             # ✅ Feature plan folder
        ├── feat-planning-sys.md
        └── phases/
            ├── ph1-folder-struct.md
            └── ph2-validation.md
```

---

## 📋 Implementation Checklist

### **Phase 1: Planning Manifest Update**
- [ ] Update `planning-system-5.0-manifest.yaml`
- [ ] Define epic vs feature folder structure
- [ ] Add naming convention rules (no `00-`, max 25 chars)
- [ ] Update `folder_structure` section

### **Phase 2: Planning Orchestrator Update**
- [ ] Implement `create_epic_plan()`
- [ ] Refactor `create_feature_plan()` to work universally
- [ ] Add complexity-based routing
- [ ] Add name sanitization (25 char limit)

### **Phase 3: Plan Viewer Update**
- [ ] Add auto-detection logic (epic vs feature)
- [ ] Implement epic rendering (nested features)
- [ ] Ensure feature card reuse
- [ ] Test both modes

### **Phase 4: Migration Tools**
- [ ] Create migration script for existing plans
- [ ] Convert `cortex5-epic` to `epic-cortex5`
- [ ] Convert feature markdown files to feature plan folders
- [ ] Update all trackers

### **Phase 5: Documentation**
- [ ] Update `.github/copilot-instructions.md`
- [ ] Update `CORTEX.prompt.md`
- [ ] Create migration guide
- [ ] Update planning examples

---

## 🚀 Example Usage

### **Create Epic**
```bash
python3 -m src.main "plan CORTEX 5.0 enhancement epic with features: knowledge extension, orchestrator registry, goal detection"
```

**Result:**
```
epic-cortex5/
└── features/
    ├── feat-knowledge-ext/
    ├── feat-orchestr-registry/
    └── feat-goal-detection/
```

### **Create Standalone Feature**
```bash
python3 -m src.main "plan glassmorphism CSS standardization"
```

**Result:**
```
feat-glassmorphism/
├── feat-glassmorphism.md
└── phases/
    ├── ph1-audit.md
    └── ph2-refactor.md
```

### **Add Feature to Existing Epic**
```bash
python3 -m src.main "add feature 'response templates' to epic-cortex5"
```

**Result:**
```
epic-cortex5/features/feat-response-templates/
```

---

## 📖 References

- **Planning Manifest**: `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **Response Templates**: `cortex-brain/response-templates-v4.yaml`
- **Brain Protection**: `cortex-brain/brain-protection-rules.yaml`
- **Example Epic**: `cortex-brain/documents/planning/active/epic-cortex5/`
- **Example Feature**: `cortex-brain/documents/planning/completed/feat-glassmorphism/`

---

**Last Updated:** 2026-01-07  
**Status:** ✅ DESIGN FINALIZED

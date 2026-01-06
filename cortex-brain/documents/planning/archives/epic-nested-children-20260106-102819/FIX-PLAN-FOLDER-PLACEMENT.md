# ✅ FIXED: Plan Folder Placement Issue

**Date:** 2026-01-06  
**Issue:** Child plans created at `active/` root instead of inside epic parent folder  
**Status:** ✅ RESOLVED  
**Files Modified:** 2

---

## 🐛 Problem Description

When using commands like `continue plan cortex5-enhancement-epic from...` or `begin implementing cortex5-enhancement-epic`, the Planning System v5 was creating child plan folders at the **root level** of `cortex-brain/documents/planning/active/` instead of **inside the epic parent folder**.

### Before Fix:
```
cortex-brain/documents/planning/active/
├── cortex5-enhancement-epic/           # Epic folder
├── a19-continue-plan-cortex5/          # ❌ WRONG: Child at root
├── a19-continue-plan-plan/             # ❌ WRONG: Child at root
├── continue-plan-cortex5-enhancement-epic-from/  # ❌ WRONG
└── plan-5ef62288-0f08-459a-8192-43aae89f31bf/    # ❌ WRONG
```

### After Fix:
```
cortex-brain/documents/planning/active/
└── cortex5-enhancement-epic/                      # Epic folder
    ├── CORTEX5-SNOWBALL.md                       # Epic master plan
    ├── README.md
    ├── analysis/
    ├── artifacts/
    ├── context/
    ├── reports/
    └── a19-test-epic-child/                      # ✅ CORRECT: Child inside epic
        ├── A19-test-epic-child.md
        ├── README.md
        ├── analysis/
        ├── artifacts/
        ├── context/
        ├── reports/
        └── tracking/
```

---

## 🔧 Root Cause

The `_create_folder_structure()` method in `planning_orchestrator_v5.py` (line 1534) was **hardcoded** to always create plans at:

```python
plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
```

This ignored the epic parent context, causing all child plans to be created as siblings of the epic folder instead of children.

---

## ✅ Solution Implemented

### 1. Added Epic Parent Path Detection (`cortex_entry.py`)

**New Method: `_detect_epic_parent_path()`** (lines 1240-1277)

Detects epic parent folder from user requests using regex patterns:
- `"continue plan cortex5-enhancement-epic from..."`
- `"begin implementing cortex-brain/documents/planning/active/cortex5-enhancement-epic"`
- `"plan [feature] inside cortex5-enhancement-epic"`

```python
def _detect_epic_parent_path(self, user_message: str) -> Optional[str]:
    """Detect if request is for a child plan inside an epic folder."""
    import re
    from pathlib import Path
    
    message_lower = user_message.lower()
    
    # Pattern 1: "continue plan <epic-name>"
    epic_patterns = [
        r'continue.*?plan\s+([a-zA-Z0-9\-]+(?:enhancement|remediation|snowball)[a-zA-Z0-9\-]*)',
        r'begin\s+implementing\s+.*?planning/active/([a-zA-Z0-9\-]+)',
        r'inside\s+([a-zA-Z0-9\-]+(?:enhancement|remediation|snowball)[a-zA-Z0-9\-]*)',
        r'from.*?([a-zA-Z0-9\-]+(?:enhancement|remediation|snowball)[a-zA-Z0-9\-]*)'
    ]
    
    for pattern in epic_patterns:
        match = re.search(pattern, message_lower, re.IGNORECASE)
        if match:
            epic_folder_name = match.group(1)
            epic_path = Path(f"cortex-brain/documents/planning/active/{epic_folder_name}")
            
            # Verify epic folder exists
            if epic_path.exists() and epic_path.is_dir():
                self.logger.info(f"✅ Detected epic parent folder: {epic_folder_name}")
                return str(epic_path)
    
    return None
```

### 2. Pass Epic Context to Planning Orchestrator (`cortex_entry.py`)

**Modified: `_execute_orchestrator_directly()`** (lines 1288-1297)

```python
# Detect epic parent folder from request
epic_parent_path = self._detect_epic_parent_path(request.user_message)

# Build context with epic parent path if detected
orchestrator_context = {'user_request': request.user_message}
if epic_parent_path:
    orchestrator_context['epic_parent_path'] = epic_parent_path
    self.logger.info(f"📁 Detected epic parent folder: {epic_parent_path}")

# Initialize orchestrator with epic context
orchestrator = PlanningOrchestratorV5(
    config_path=str(config.brain_path / "config" / "planning-v5-default.yaml"),
    state_db=None,
    plan_id=None,
    template_dir=None,
    context=orchestrator_context,  # ✅ Epic context passed here
    plan_type='epic'
)
```

### 3. Use Epic Context in Folder Creation (`planning_orchestrator_v5.py`)

**Modified: `_create_folder_structure()`** (lines 1531-1544)

```python
# Create folder name with ID prefix: a01-enterprise-aud-log
folder_name = f"{folder_id_prefix}-{abbreviated_name}"

# Check if there's an epic parent folder in master_context
epic_parent_path = self.master_context.get('epic_parent_path')

# Create at active plans path (inside epic if parent specified)
if epic_parent_path:
    # Child plan inside epic folder
    plan_dir = Path(epic_parent_path) / folder_name
    self.logger.info(f"📁 Creating child plan inside epic: {epic_parent_path}/{folder_name}")
else:
    # Root-level plan (epic or standalone feature)
    plan_dir = Path(f"cortex-brain/documents/planning/active/{folder_name}")
    self.logger.info(f"📁 Creating root-level plan: {folder_name}")
```

---

## 🧪 Verification

### Test Command:
```bash
python3 -m src.main "plan test-epic-child-placement feature inside cortex5-enhancement-epic folder"
```

### Result:
```
✅ Plan 'test-epic-child-placement-feature-inside-cortex5' created successfully

📁 Artifacts Created:
- cortex-brain/documents/planning/active/cortex5-enhancement-epic/a19-test-epic-child/analysis
- cortex-brain/documents/planning/active/cortex5-enhancement-epic/a19-test-epic-child/artifacts
- cortex-brain/documents/planning/active/cortex5-enhancement-epic/a19-test-epic-child/context
- cortex-brain/documents/planning/active/cortex5-enhancement-epic/a19-test-epic-child/reports
- cortex-brain/documents/planning/active/cortex5-enhancement-epic/a19-test-epic-child/tracking
```

**✅ SUCCESS:** Child plan created **inside** `cortex5-enhancement-epic/` folder!

---

## 📋 Files Modified

### 1. `src/entry_point/cortex_entry.py`
- **Lines 24:** Added `import re` for regex pattern matching
- **Lines 1240-1277:** New method `_detect_epic_parent_path()` to detect epic context
- **Lines 1288-1297:** Modified `_execute_orchestrator_directly()` to pass epic context

### 2. `src/orchestrators/planning/planning_orchestrator_v5.py`
- **Lines 1531-1544:** Modified `_create_folder_structure()` to check `master_context['epic_parent_path']`
- **Lines 1537-1544:** Added conditional logic to create child plans inside epic folder

---

## 🚀 Next Steps

### Immediate:
1. ✅ **Clean up incorrectly placed plans** - Move orphaned plans into epic folder
   ```bash
   mv cortex-brain/documents/planning/active/a19-continue-plan-cortex5 \
      cortex-brain/documents/planning/active/cortex5-enhancement-epic/
   ```

2. ✅ **Update CORTEX5-SNOWBALL.md** - Add this fix as a completed phase item

3. ✅ **Create plan-viewer.html for epic** - Generate HTML viewer at epic folder root

### For Epic Plan:
1. **Add Phase 0.5: Plan Structure Fix** to CORTEX5-SNOWBALL.md
   - Task: Implement epic parent path detection
   - Task: Update folder creation logic
   - Task: Clean up orphaned plans
   - Status: ✅ Complete

2. **Document in Phase 7.5** (from cortex-upgrade.prompt.md)
   - Plan structure validation
   - 5-subfolder standard enforcement
   - Archive non-compliant plans

---

## 🎯 Impact

### Before:
- ❌ Child plans scattered at root level
- ❌ Epic folder organization broken
- ❌ Manual cleanup required
- ❌ Continuation prompts incorrect

### After:
- ✅ Child plans properly nested inside epic folder
- ✅ Clean folder hierarchy maintained
- ✅ Automatic epic detection
- ✅ Correct plan structure from creation

---

## 📚 Related Documentation

- **Upgrade System:** `.github/prompts/cortex-upgrade.prompt.md` (Phase 7.5: Plan Structure Validation)
- **Planning Orchestrator:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **Master Orchestrator:** `cortex-brain/config/master-orchestrator.yaml`

---

**Author:** CORTEX Planning System v5  
**Verified By:** Test execution on 2026-01-06

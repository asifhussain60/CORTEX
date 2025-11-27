# CORTEX Workspace Isolation Rule Implementation

**Date:** 2025-11-17  
**Type:** Brain Protection Rule Enhancement  
**Severity:** BLOCKED  
**Status:** ✅ Rule Added - Implementation Pending

---

## 🎯 Issue Reported

**User Discovery:** Published "onboarding app" operation generates documentation in application repository root (e.g., `user-repo/docs/`) instead of within dedicated CORTEX workspace folder.

**Impact:**
- CORTEX artifacts pollute user's application repository
- Cleanup difficult (which docs are CORTEX-generated vs application-owned?)
- Git isolation impossible (cannot selectively exclude CORTEX files)
- Repository clutter reduces professionalism

---

## 🛡️ New Protection Rule Added

**Rule ID:** `CORTEX_WORKSPACE_ISOLATION`  
**Layer:** Layer 3 (SOLID Compliance)  
**Severity:** BLOCKED  
**Location:** `cortex-brain/brain-protection-rules.yaml` (line ~1800)

### Rule Summary

**Principle:** ALL CORTEX-generated documentation for application repositories MUST be contained within `CORTEX/Workspaces/[app-name]/` folder structure.

**Why This Matters:**
1. **Clean Separation** - CORTEX artifacts ≠ application code
2. **Easy Cleanup** - Delete `CORTEX/` removes all CORTEX files
3. **Git Isolation** - Single `.gitignore` entry: `CORTEX/`
4. **Multi-App Support** - Each app gets isolated workspace
5. **Portability** - Self-contained CORTEX state

---

## 📁 Required Workspace Structure

```
user-application-repo/
├── CORTEX/                          ← Git-ignored CORTEX folder
│   ├── .cortex-metadata.json        ← Workspace metadata
│   └── Workspaces/                  ← All application workspaces
│       └── MyApp/                   ← Application-specific workspace
│           ├── docs/                ← Generated documentation
│           │   ├── onboarding.md
│           │   ├── architecture-overview.md
│           │   └── quick-reference.md
│           ├── diagrams/            ← Architecture diagrams
│           │   ├── component-diagram.mmd
│           │   ├── data-flow.mmd
│           │   └── images/          ← Rendered images
│           ├── references/          ← Quick references
│           └── analysis/            ← Code analysis reports
├── src/                             ← User's actual application code
├── tests/                           ← User's tests
├── README.md                        ← User's README
└── .gitignore                       ← Must include "CORTEX/"
```

---

## 🔧 Implementation Changes Required

### 1. PageGenerator (src/epm/modules/page_generator.py)

**Before:**
```python
self.output_path = root_path / "docs"
```

**After:**
```python
app_name = context.get('app_name', 'UnknownApp')
self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "docs"
```

---

### 2. DiagramGenerator (src/epm/modules/diagram_generator.py)

**Before:**
```python
self.output_path = root_path / "docs"
```

**After:**
```python
app_name = context.get('app_name', 'UnknownApp')
self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
```

---

### 3. ImagePromptGenerator (src/epm/modules/image_prompt_generator.py)

**Before:**
```python
self.output_dir = Path(output_dir)  # Typically docs/diagrams
```

**After:**
```python
app_name = context.get('app_name', 'UnknownApp')
self.output_dir = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
```

---

### 4. Onboarding Orchestrator Context

**Add app_name to session context:**

```python
def _create_new_session(self, profile, context):
    session_context = {
        "app_name": self._detect_app_name(self.project_root),
        "profile": profile.value,
        "project_root": self.project_root,
        "previous_results": {},
        **(context or {})
    }
    # ... rest of method
```

**Add app name detection method:**

```python
def _detect_app_name(self, project_root: Path) -> str:
    """
    Detect application name from project structure.
    
    Priority:
    1. .sln file (C#)
    2. .csproj file (C#)
    3. package.json name field (Node.js)
    4. pyproject.toml name field (Python)
    5. Directory name (fallback)
    """
    # Check for .sln file
    sln_files = list(project_root.glob("*.sln"))
    if sln_files:
        return sln_files[0].stem
    
    # Check for .csproj file
    csproj_files = list(project_root.rglob("*.csproj"))
    if csproj_files:
        return csproj_files[0].stem
    
    # Check for package.json
    package_json = project_root / "package.json"
    if package_json.exists():
        import json
        with open(package_json) as f:
            data = json.load(f)
            return data.get('name', project_root.name)
    
    # Check for pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        import toml
        with open(pyproject) as f:
            data = toml.load(f)
            return data.get('project', {}).get('name', project_root.name)
    
    # Fallback to directory name
    return project_root.name
```

---

### 5. .gitignore Management

**Onboarding MUST create/update user repo's .gitignore:**

```python
def _ensure_gitignore_updated(self, project_root: Path) -> None:
    """Ensure .gitignore excludes CORTEX folder"""
    gitignore_path = project_root / ".gitignore"
    cortex_entry = "\n# CORTEX AI Assistant (local workspace, not committed)\nCORTEX/\n"
    
    if gitignore_path.exists():
        content = gitignore_path.read_text()
        if "CORTEX/" not in content:
            with open(gitignore_path, 'a') as f:
                f.write(cortex_entry)
            logger.info("✓ Added CORTEX/ to .gitignore")
    else:
        gitignore_path.write_text(cortex_entry)
        logger.info("✓ Created .gitignore with CORTEX/ exclusion")
```

---

## ✅ Verification Requirements

**Brain Protector MUST enforce:**

1. **Output Path Validation**
   - All generated files within `CORTEX/Workspaces/[app-name]/`
   - Zero files created in application root or `docs/`

2. **No Root Pollution**
   - `git status` shows zero new files outside `CORTEX/`
   - Application repository remains clean

3. **Workspace Structure**
   - Proper folder hierarchy created:
     - `CORTEX/Workspaces/[app-name]/docs/`
     - `CORTEX/Workspaces/[app-name]/diagrams/`
     - `CORTEX/Workspaces/[app-name]/references/`

4. **Git Isolation**
   - `.gitignore` updated with `CORTEX/` entry
   - No CORTEX artifacts committed to user repository

---

## 📊 Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Brain Protection Rule** | ✅ COMPLETE | Added to brain-protection-rules.yaml |
| **PageGenerator** | ⏳ PENDING | Needs workspace path update |
| **DiagramGenerator** | ⏳ PENDING | Needs workspace path update |
| **ImagePromptGenerator** | ⏳ PENDING | Needs workspace path update |
| **Onboarding Orchestrator** | ⏳ PENDING | Needs app name detection + .gitignore management |
| **Integration Tests** | ⏳ PENDING | Verify workspace isolation enforced |
| **Documentation** | ⏳ PENDING | Update user guides with new structure |

---

## 🎯 Next Steps

1. **Implement Code Changes** (Estimated: 90 minutes)
   - Update 3 generator modules (30 min each)
   - Add app name detection method (15 min)
   - Add .gitignore management (15 min)

2. **Create Integration Tests** (Estimated: 60 minutes)
   - Test workspace folder creation
   - Test output path validation
   - Test .gitignore update
   - Test multi-app workspace isolation

3. **Update Documentation** (Estimated: 30 minutes)
   - Update onboarding operation guide
   - Update setup guide with workspace structure
   - Add troubleshooting for workspace issues

4. **Validate with Real Application** (Estimated: 15 minutes)
   - Run onboarding on test application
   - Verify all files in `CORTEX/Workspaces/[app]/`
   - Verify .gitignore excludes CORTEX/
   - Verify `git status` shows clean application repo

---

## 📝 Benefits Summary

**User Experience:**
- ✅ Clean repository (no CORTEX pollution)
- ✅ Easy cleanup (delete CORTEX/ folder)
- ✅ Git-friendly (single .gitignore entry)
- ✅ Professional appearance (organized structure)

**Development:**
- ✅ Clear separation (CORTEX ≠ application)
- ✅ Multi-app support (isolated workspaces)
- ✅ Portability (self-contained state)
- ✅ Maintainability (consistent structure)

**Architecture:**
- ✅ Enforced via Brain Protector (automatic)
- ✅ Integration tested (no regressions)
- ✅ Documented (clear guidelines)
- ✅ Extensible (supports future enhancements)

---

## 🔗 Related Documentation

- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Onboarding Orchestrator:** `src/epm/onboarding_orchestrator.py`
- **PageGenerator:** `src/epm/modules/page_generator.py`
- **DiagramGenerator:** `src/epm/modules/diagram_generator.py`
- **Setup Guide:** `prompts/shared/setup-guide.md` (needs update)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Status:** Rule added, implementation in progress  
**Priority:** HIGH (user-reported issue)

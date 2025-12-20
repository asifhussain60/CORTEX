# Cross-IDE Workspace Detection - Technical Summary

**Version:** 1.0 | **Author:** Asif Hussain | **Created:** December 20, 2025

**Status:** 📋 READY FOR IMPLEMENTATION | **Phase:** Phase 11 (Multi-Repo Architecture)

---

## 🎯 Overview

CORTEX 4.0 Phase 11 provides **automatic workspace detection** that works identically in VSCode and Visual Studio 2019+, enabling seamless context switching without user intervention.

---

## 🏗️ Architecture

### Detection Flow (Both IDEs)

```
User opens file in any workspace
    ↓
1. IDE Type Detection (IDEDetector)
   - VSCode: VSCODE_PID env var or Code.exe process
   - Visual Studio: VS_* env vars or devenv.exe process
    ↓
2. Workspace Detection (WorkspaceDetector)
   - VSCode: vscode.workspace.workspaceFolders API
   - Visual Studio: DTE2.Solution API
   - Fallback: CWD search → .cortex/ or .git/
    ↓
3. Context Loading
   - Read: workspace/.cortex/config.json
   - Get: workspace_id (UUID)
   - Load: cortex-brain/tier3/workspace-{uuid}/
    ↓
4. Orchestrator Operates
   - target_directory = workspace_path
   - Files written to correct workspace
   - Logs tagged: [workspace:name]
```

### Priority Order (Same for Both IDEs)

1. **IDE-Specific API** (fastest, most reliable)
   - VSCode: `vscode.workspace` + `vscode.window.activeTextEditor`
   - Visual Studio: `DTE2.ActiveDocument` + `DTE2.Solution`

2. **Environment Variables** (fallback)
   - VSCode: `VSCODE_WORKSPACE`, `VSCODE_ACTIVE_FILE`
   - Visual Studio: `VS_SOLUTION_FILE`, `VS_ACTIVE_DOCUMENT`

3. **GitHub Copilot Context** (cross-IDE)
   - Copilot provides active file + workspace folders
   - Works in both IDEs when Copilot is active

4. **Current Working Directory** (universal fallback)
   - Walk up tree: `.cortex/` → `.git/` → `.sln` → project markers

5. **CORTEX Directory** (safe default)
   - Used for CORTEX self-operations

---

## 📋 Implementation Details

### Component 1: IDE Type Detection (Already Exists)

**File:** `src/core/ide_detector.py`

**Capabilities:**
- ✅ VSCode detection (VSCODE_PID, Code.exe)
- ✅ Visual Studio detection (VS_*, devenv.exe)
- ✅ Caching (<10ms after first detect)
- ✅ Graceful degradation

**No changes needed** - Already supports both IDEs.

### Component 2: Workspace Detection (New)

**File:** `src/core/workspace_detector.py`

**Classes:**
- `WorkspaceDetector` - Main detection logic
- `WorkspaceInfo` - Detection result dataclass
- `WorkspaceDetectionMethod` - Method enum

**Key Methods:**
```python
def detect_active_workspace() -> WorkspaceInfo:
    """Detect workspace with automatic IDE switching."""
    
def _detect_vscode_workspace() -> Optional[WorkspaceInfo]:
    """VSCode-specific detection."""
    
def _detect_visual_studio_workspace() -> Optional[WorkspaceInfo]:
    """Visual Studio-specific detection."""
```

**Performance:**
- Target: <200ms detection
- Caching: 5 minutes TTL
- Thread-safe: Global cache dictionary

### Component 3: BaseOrchestrator Integration

**File:** `src/orchestrators/base_orchestrator.py`

**Changes Required:**
```python
class BaseOrchestrator:
    def __init__(self, config: OrchestratorConfig):
        # Auto-detect workspace on EVERY orchestrator init
        self.workspace_info = detect_active_workspace()
        self.target_directory = self.workspace_info.path
        
        logger.info(
            f"[workspace:{self.workspace_info.name}] "
            f"Orchestrator initialized (IDE: {self.workspace_info.ide_type.value})"
        )
```

---

## 🧪 Testing Strategy

### Test Scenarios

**1. VSCode Single Workspace**
- Open file in single VSCode workspace
- Verify correct workspace detected
- Verify files written to correct directory

**2. VSCode Multi-Root Workspace**
- Open workspace.code-workspace with 3 repos
- Switch between files in different repos
- Verify automatic context switching

**3. Visual Studio Single Solution**
- Open .sln file in Visual Studio
- Verify solution directory detected
- Verify files written to solution directory

**4. Visual Studio Multiple Solutions**
- Open 2 Visual Studio instances with different solutions
- Verify each instance has correct context
- Verify no cross-contamination

**5. Cross-IDE Switching**
- Work in VSCode → Close → Open same repo in Visual Studio
- Verify same workspace_id loaded
- Verify Brain context preserved

**6. Fallback Scenarios**
- No .cortex/ directory (first run)
- IDE API unavailable
- Environment variables missing
- Verify graceful degradation

### Test Files

**New Test File:** `tests/core/test_workspace_detector.py`

**Test Count:** 25 tests minimum
- 5 VSCode tests
- 5 Visual Studio tests
- 5 cross-IDE tests
- 5 fallback tests
- 5 edge case tests

---

## 📊 Compatibility Matrix

| Feature | VSCode | Visual Studio 2019+ | Notes |
|---------|--------|---------------------|-------|
| Workspace Detection | ✅ | ✅ | Identical UX |
| Active File Detection | ✅ | ✅ | Both supported |
| Multi-Root Support | ✅ | ✅ | VSCode=workspace, VS=solutions |
| Auto Context Switch | ✅ | ✅ | <200ms both |
| Copilot Integration | ✅ | ✅ | Cross-IDE |
| Fallback CWD Search | ✅ | ✅ | Universal |
| Environment Variables | ✅ | ✅ | Different var names |

---

## 🚨 Known Limitations

**VSCode:**
- ❌ API requires extension (Phase 12 future work)
- ✅ Environment variable fallback works today

**Visual Studio:**
- ❌ DTE2 API requires extension (Phase 12 future work)
- ✅ Solution file parsing works today

**Both:**
- ✅ Copilot integration available today
- ✅ CWD fallback always works

**Mitigation:** Phase 11 implements working solution without extensions. Phase 12+ can add native IDE integration for improved performance.

---

## 📚 Documentation Requirements

**New Documentation:**
1. `vscode-workspace-detection.md` - VSCode-specific guide
2. `visual-studio-workspace-detection.md` - VS-specific guide

**Updated Documentation:**
1. `CORTEX.prompt.md` - Add cross-IDE examples
2. `multi-repo-setup-guide.md` - IDE-specific setup steps
3. `workspace-architecture.md` - Cross-IDE detection flow

---

## ✅ Success Criteria

**Functional:**
- ✅ VSCode users: Automatic workspace switching
- ✅ Visual Studio users: Automatic workspace switching
- ✅ Mixed IDE users: Same workspace_id, preserved context
- ✅ No manual switching commands needed

**Performance:**
- ✅ Detection: <200ms (both IDEs)
- ✅ Cache hit: <10ms (both IDEs)
- ✅ Zero user-visible lag

**User Experience:**
- ✅ Identical behavior in both IDEs
- ✅ Visual feedback: `[workspace:name]` in all logs
- ✅ Clear error messages if detection fails

---

## 🎯 Next Steps

**Implementation Order:**
1. ✅ Create `workspace_detector.py` (COMPLETE)
2. ☐ Write tests: `test_workspace_detector.py` (25 tests)
3. ☐ Integrate into `BaseOrchestrator`
4. ☐ Test in VSCode (manual + automated)
5. ☐ Test in Visual Studio 2019+ (manual + automated)
6. ☐ Create cross-IDE documentation

**Timeline:** Part of Phase 11 Package 1 (Workspace Registry & Detection, 2 days)

---

## 📞 Contact

**Implementation Owner:** Asif Hussain  
**Phase:** Phase 11 (Post-Core)  
**Status:** Ready for implementation after Phase 6-10 complete

## AC-BRITTLE-003 STARTUP GUIDE

**Acceptance Criteria ID**: AC-BRITTLE-003  
**Title**: Windows Path Compatibility Fix  
**Phase**: PHASE-05 (Brittleness Remediation - Wave-1)  
**Status**: READY TO START ✅

---

## REQUIREMENTS

### Testing Requirements
- **Unit Tests**: 12 tests minimum
- **Integration Tests**: 4 tests minimum  
- **Total Tests**: 16+ tests expected

### Success Criteria
1. Works on Windows 10+
2. No path encoding issues
3. CI/CD passes on Windows

### Implementation Context
- Builds on AC-BRITTLE-001 (ImportResolver) and AC-BRITTLE-002 (PathAbstraction)
- Focuses on Windows-specific path handling edge cases
- Should use Strategy pattern (Windows path strategy already exists in AC-002)

---

## EXECUTION PLAN

### Phase 1: RED (Write Tests First)

**File**: `tests/unit/test_windows_path_compat.py`

Test scenarios to cover:
1. Drive letter handling (C:, D:, etc.)
2. UNC path support (\\\\server\\share)
3. Long path support (>260 characters)
4. Reserved names handling (CON, PRN, AUX, etc.)
5. Case-insensitive path handling
6. Backslash vs forward slash normalization
7. Environment variable expansion (%USERPROFILE%)
8. Shortname (8.3) support
9. Junction point handling
10. Wildcard and special character restrictions
11. Path encoding (UTF-8, ASCII, etc.)
12. Network drive paths

**File**: `tests/integration/test_windows_path_compat_integration.py`

Integration test scenarios:
1. Real Windows file system operations
2. Path resolution in Windows environment
3. CI/CD pipeline validation on Windows
4. Cross-platform path translation
5. Error handling for Windows-specific issues (code page errors, etc.)

### Phase 2: GREEN (Implement)

**File**: `cortex_brain/tier0/windows_path_compat.py`

Implementation considerations:
- Extend existing `WindowsPathStrategy` from AC-BRITTLE-002
- Or create separate `WindowsPathCompatibility` class
- Handle Windows-specific path edge cases
- Support pathlib integration for Windows paths

Key methods to implement:
```python
class WindowsPathCompatibility:
    - validate_path(path: str) -> bool
    - normalize_path(path: str) -> str
    - expand_environment_vars(path: str) -> str
    - handle_reserved_names(path: str) -> str
    - support_long_paths(path: str) -> str
    - handle_unc_paths(path: str) -> str
    - resolve_shortcuts(path: str) -> str
```

### Phase 3: REFACTOR (Improve)

- Ensure type hints: 100%
- Ensure docstrings: 100%
- Achieve code coverage: ≥75%
- Integration with PathAbstraction verified
- Edge cases thoroughly tested

---

## GOVERNANCE RULES TO APPLY

✅ **CORE-008**: TDD approach (tests first, implementation second)
✅ **CORE-011**: 100% type hints on all methods
✅ **CORE-012**: 100% docstrings on all methods
✅ **CORE-024**: Thread-safe implementation if needed
✅ **CORE-028**: Portable path handling respecting Windows constraints

---

## TEMPLATE TEST STRUCTURE

```python
# tests/unit/test_windows_path_compat.py

import pytest
from pathlib import WindowsPath, Path
from typing import List

pytestmark = pytest.mark.ac_brittle_003


class TestDriveLetterHandling:
    """Test Windows drive letter support."""
    
    def test_drive_letter_normalization(self) -> None:
        """Test normalizing drive letters."""
        # Implementation here
        pass


class TestUNCPathSupport:
    """Test UNC path (\\\\server\\share) support."""
    
    def test_unc_path_parsing(self) -> None:
        """Test parsing UNC paths."""
        # Implementation here
        pass


class TestLongPathSupport:
    """Test Windows long path support (>260 chars)."""
    
    def test_long_path_handling(self) -> None:
        """Test handling paths over 260 characters."""
        # Implementation here
        pass


class TestReservedNames:
    """Test Windows reserved device name handling."""
    
    def test_reserved_name_detection(self) -> None:
        """Test detecting reserved names (CON, PRN, etc)."""
        # Implementation here
        pass


class TestPathNormalization:
    """Test Windows-specific path normalization."""
    
    def test_backslash_forward_slash_handling(self) -> None:
        """Test mixed separator handling."""
        # Implementation here
        pass


class TestEnvironmentExpansion:
    """Test environment variable expansion in paths."""
    
    def test_userprofile_expansion(self) -> None:
        """Test %USERPROFILE% expansion."""
        # Implementation here
        pass
```

---

## EXECUTION CHECKLIST

### Before Starting
- [ ] Review AC-BRITTLE-002 PathAbstraction code (for Windows strategy)
- [ ] Review AC-BRITTLE-001 ImportResolver code (for strategy pattern reference)
- [ ] Check Windows path documentation from Python pathlib
- [ ] Identify Windows-specific test requirements

### During Implementation
- [ ] Write all unit tests first (12 tests minimum)
- [ ] Implement functionality to pass tests
- [ ] Write integration tests (4 tests minimum)
- [ ] Add type hints to 100%
- [ ] Add docstrings to 100%
- [ ] Achieve ≥75% code coverage
- [ ] Run all tests and verify pass rate: 100%

### After Completion
- [ ] Update cortex-master.yaml with COMPLETED status
- [ ] Create git commit with detailed message
- [ ] Verify Single Source of Truth (cortex-master.yaml)
- [ ] Prepare for AC-BRITTLE-004 (macOS compatibility)

---

## ESTIMATED TIMELINE

| Phase | Duration | Description |
|-------|----------|-------------|
| RED | 30-45 min | Write 12 unit + 4 integration tests |
| GREEN | 45-60 min | Implement functionality to pass tests |
| REFACTOR | 30-45 min | Improve coverage, add type hints/docstrings |
| **Total** | **2-2.5 hours** | Full AC completion |

---

## SUCCESS CRITERIA CHECKLIST

Before marking as COMPLETED, verify:

- [ ] 12+ unit tests created and PASSING
- [ ] 4+ integration tests created and PASSING
- [ ] Total pass rate: 100%
- [ ] Code coverage: ≥75%
- [ ] Type hints: 100%
- [ ] Docstrings: 100%
- [ ] Works on Windows 10+
- [ ] No path encoding issues
- [ ] CI/CD passes on Windows
- [ ] cortex-master.yaml status updated to COMPLETED
- [ ] Git commit created with detailed message
- [ ] Documentation complete

---

## NOTES FOR IMPLEMENTATION

1. **Windows Path Quirks to Handle**:
   - Drive letters (C:\, D:\, etc.)
   - UNC paths (\\\\server\\share)
   - Reserved names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
   - Case-insensitive filesystem
   - Path length limit of 260 chars (unless long path support enabled)
   - Backslash as separator vs forward slash
   - Environment variables in paths (%SYSTEMROOT%, %USERPROFILE%, etc.)

2. **Integration Points**:
   - Should extend or integrate with PathAbstraction from AC-002
   - Use Strategy pattern if implementing as extension
   - Maintain compatibility with existing POSIX handling

3. **Testing Challenges**:
   - Running on non-Windows platforms: use pathlib's PureWindowsPath for simulation
   - UNC path testing: mock network paths
   - Long path testing: synthetic paths (don't need real 260+ char files)
   - Reserved names: test validation logic without creating actual files

4. **Reference Implementation**:
   - Look at `WindowsPathStrategy` from AC-002 for pattern reference
   - Study `PureWindowsPath` from pathlib for built-in Windows handling
   - Review Python's os.path implementation for compatibility

---

## READY TO START?

When ready to begin AC-BRITTLE-003:

1. Follow TDD approach: **Tests First**
2. Create comprehensive test coverage
3. Apply all governance rules
4. Maintain 100% pass rate
5. Target ≥75% code coverage
6. Document thoroughly
7. Commit regularly to git

**Status**: 🟢 READY TO START
**Next Action**: Begin RED phase (write tests)

# CORTEX Visual Studio Extension - Testing Guide

**Version:** 4.0.0 | **Platform:** Windows + Visual Studio 2022  
**Author:** Asif Hussain | **Date:** December 29, 2025

---

## 🎯 Overview

This guide provides comprehensive testing procedures for the CORTEX Visual Studio extension. Due to development on macOS, manual testing must be performed on Windows with Visual Studio 2022.

---

## 📋 Prerequisites

### Required
- **OS:** Windows 10/11 (64-bit)
- **IDE:** Visual Studio 2022 (Community, Pro, or Enterprise)
- **.NET Framework:** 4.8
- **CORTEX:** Installed and configured (https://github.com/asifhussain60/CORTEX)
- **Python:** 3.8+ in PATH or CORTEX venv

### Optional
- **Azure DevOps:** For ADO integration testing
- **Test Projects:** C#/Python projects for workspace testing

---

## 🏗️ Build & Installation

### 1. Build the Extension

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX/extensions/visual-studio

# Open in Visual Studio 2022
# File → Open → Project/Solution → CortexVSExtension.sln

# Build
Build → Build Solution (Ctrl+Shift+B)

# Expected output: bin/Debug/CortexVSExtension.vsix
```

### 2. Install for Testing

```bash
# Method 1: Debug (F5)
Debug → Start Debugging (F5)
# Launches VS 2022 Experimental Instance

# Method 2: Manual Install
Double-click bin/Debug/CortexVSExtension.vsix
# Follow installation wizard
```

### 3. Verify Installation

1. Open Visual Studio 2022
2. Go to `Extensions → Manage Extensions`
3. Search for "CORTEX"
4. Verify version 4.0.0 is installed

---

## ✅ Test Suite

### Test Category 1: Installation & Initialization

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 1.1 | Extension loads | Launch VS 2022 | CORTEX menu appears under Tools | ⬜ |
| 1.2 | No startup errors | Check Output window | No errors in "CORTEX Diagnostics" pane | ⬜ |
| 1.3 | Menu structure | Tools → CORTEX | 7 commands + 2 tool windows visible | ⬜ |

### Test Category 2: Workspace Detection

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 2.1 | CORTEX repo detection | Open CORTEX solution | Context shows "CORTEX Repository" | ⬜ |
| 2.2 | User workspace detection | Open non-CORTEX project | Context shows "User Workspace" | ⬜ |
| 2.3 | CORTEX_HOME env var | Set CORTEX_HOME, open any project | CORTEX path detected correctly | ⬜ |
| 2.4 | No CORTEX found | Open project, no CORTEX nearby | Error message with instructions | ⬜ |

### Test Category 3: Command Execution

#### 3.1 Create Plan Command

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.1.1 | Open command | Tools → CORTEX → Create Plan | Input dialog appears | ⬜ |
| 3.1.2 | Enter plan name | Type "test-plan", click OK | Success message, folder created | ⬜ |
| 3.1.3 | Verify folder structure | Check cortex-brain/documents/planning/active/ | test-plan/ with 4 subfolders | ⬜ |
| 3.1.4 | Empty name | Leave name empty, click OK | Error: "Plan name cannot be empty" | ⬜ |
| 3.1.5 | Output window | Check Output → CORTEX Diagnostics | Command logged with timestamp | ⬜ |

#### 3.2 Start TDD Workflow

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.2.1 | Open command | Tools → CORTEX → Start TDD Workflow | Confirmation dialog with explanation | ⬜ |
| 3.2.2 | Cancel workflow | Click No | No action taken, no errors | ⬜ |
| 3.2.3 | Start workflow | Click Yes | TDD workflow starts, output logged | ⬜ |
| 3.2.4 | Output window | Check Output → CORTEX Diagnostics | RED→GREEN→REFACTOR steps logged | ⬜ |

#### 3.3 System Maintenance

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.3.1 | Open command | Tools → CORTEX → System Maintenance | Confirmation with 7 phases listed | ⬜ |
| 3.3.2 | Run maintenance | Click Yes | Progress logged, takes several minutes | ⬜ |
| 3.3.3 | Verify health report | Check cortex-brain/health-reports/ | New report file created | ⬜ |
| 3.3.4 | Success message | After completion | Shows health report location | ⬜ |

#### 3.4 Create ADO Story

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.4.1 | Open command | Tools → CORTEX → Create ADO Story | Input dialog for title | ⬜ |
| 3.4.2 | Enter title | Type "User authentication", click OK | Story created, success message | ⬜ |
| 3.4.3 | Empty title | Leave title empty, click OK | Error: "Story title cannot be empty" | ⬜ |
| 3.4.4 | Verify output | Check Output window | DoR/DoD gates, acceptance criteria logged | ⬜ |

#### 3.5 Sanitize Code

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.5.1 | Open command | Tools → CORTEX → Sanitize Code | Confirmation with checklist | ⬜ |
| 3.5.2 | Cancel sanitization | Click No | No action taken | ⬜ |
| 3.5.3 | Enter directory | Click Yes, enter "src" | Sanitization runs, backup created | ⬜ |
| 3.5.4 | Verify backup | Check backups/ folder | Backup archive created | ⬜ |

#### 3.6 Refine System

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.6.1 | Open command | Tools → CORTEX → Refine System | Confirmation with 7 phases + warning | ⬜ |
| 3.6.2 | Run refinement | Click Yes | Runs 10-15 minutes, progress logged | ⬜ |
| 3.6.3 | Verify report | Check cortex-brain/documents/reports/ | Refinement report created | ⬜ |
| 3.6.4 | Success message | After completion | Lists improvements applied | ⬜ |

#### 3.7 CORTEX Help

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 3.7.1 | Open help | Tools → CORTEX → CORTEX Help | Help dialog with all commands | ⬜ |
| 3.7.2 | Workspace info | Check dialog content | Shows CORTEX path, workspace, context | ⬜ |
| 3.7.3 | Command list | Scroll through dialog | 7 commands with descriptions | ⬜ |
| 3.7.4 | Resource links | Check bottom of dialog | Website, repository, docs links | ⬜ |

### Test Category 4: Tool Windows

#### 4.1 CORTEX Dashboard

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 4.1.1 | Open dashboard | Tools → CORTEX → CORTEX Dashboard | Tool window opens, docked | ⬜ |
| 4.1.2 | Workspace info | Check Workspace panel | Context, CORTEX path, workspace path shown | ⬜ |
| 4.1.3 | Quick actions | Click each button | Commands triggered, no errors | ⬜ |
| 4.1.4 | Activity feed | Perform actions | Activities logged with timestamps | ⬜ |
| 4.1.5 | Refresh button | Click Refresh | Workspace info reloaded | ⬜ |
| 4.1.6 | Theme integration | Switch VS theme (Light/Dark) | Dashboard updates colors correctly | ⬜ |

#### 4.2 Planning Viewer

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 4.2.1 | Open viewer | Tools → CORTEX → Planning Viewer | Tool window opens, docked | ⬜ |
| 4.2.2 | Load plans | Check TreeView | Existing plans listed | ⬜ |
| 4.2.3 | Plan hierarchy | Expand plan node | Subfolders shown (context, reports, etc.) | ⬜ |
| 4.2.4 | File counts | Check folder nodes | "(N files)" displayed correctly | ⬜ |
| 4.2.5 | Plan count | Check toolbar | "X plans" shown correctly | ⬜ |
| 4.2.6 | Refresh button | Click Refresh | Plans reloaded from disk | ⬜ |
| 4.2.7 | Empty state | Delete all plans, refresh | "No active plans found" message | ⬜ |
| 4.2.8 | Create Plan button | Click ➕ New Plan | Instruction message appears | ⬜ |

### Test Category 5: Error Handling

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 5.1 | No Python | Rename python.exe, run command | Error: "Python interpreter not found" | ⬜ |
| 5.2 | No CORTEX | Unset CORTEX_HOME, run command | Error: "CORTEX installation not found" | ⬜ |
| 5.3 | Command failure | Run command, kill Python mid-exec | Error message with details | ⬜ |
| 5.4 | Invalid plan name | Enter "plan/with/slashes" | Error or sanitized name | ⬜ |
| 5.5 | Workspace switch | Open new solution | Workspace info updates automatically | ⬜ |

### Test Category 6: Integration

| # | Test Case | Steps | Expected Result | Status |
|---|-----------|-------|-----------------|--------|
| 6.1 | Output window | Run any command | Output appears in "CORTEX Diagnostics" pane | ⬜ |
| 6.2 | Multiple commands | Run 3 commands sequentially | All execute successfully | ⬜ |
| 6.3 | Concurrent commands | Run 2 commands simultaneously | Queued or handled gracefully | ⬜ |
| 6.4 | VS restart | Close/reopen VS | Extension loads, state preserved | ⬜ |
| 6.5 | Multiple solutions | Open 2 VS instances | Each detects correct workspace | ⬜ |

---

## 🐛 Bug Reporting

If you find issues during testing, report them with:

### Required Information
1. **VS Version:** (e.g., Visual Studio 2022 Community 17.8.3)
2. **Extension Version:** 4.0.0
3. **OS:** (e.g., Windows 11 Pro 22H2)
4. **CORTEX Version:** (e.g., 4.0 GA)
5. **Test Case:** (e.g., 3.1.2 - Create Plan)
6. **Steps to Reproduce:** Detailed steps
7. **Expected vs Actual:** What should happen vs what happened
8. **Screenshots:** If UI issue
9. **Output Window:** Copy "CORTEX Diagnostics" log

### Report To
- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Email:** [maintainer email if available]

---

## ✅ Test Results Template

```markdown
# CORTEX VS Extension Test Results

**Tester:** [Your Name]
**Date:** [Test Date]
**Environment:**
- VS Version: [version]
- OS: [Windows version]
- CORTEX Version: [version]

## Summary
- Total Tests: 65
- Passed: [count] ✅
- Failed: [count] ❌
- Skipped: [count] ⏭️

## Failed Tests
[List failed test cases with details]

## Notes
[Any additional observations]
```

---

## 🎯 Success Criteria

Extension is production-ready if:
- ✅ All 65 test cases pass (100%)
- ✅ No critical bugs
- ✅ Commands execute within expected time
- ✅ Tool windows render correctly in Light/Dark themes
- ✅ Error messages are user-friendly
- ✅ No crashes or hangs

---

## 📚 Resources

- **Extension Source:** `/extensions/visual-studio/`
- **CORTEX Repo:** https://github.com/asifhussain60/CORTEX
- **Documentation:** https://asifhussain60.github.io/CORTEX/docs/
- **VS SDK Docs:** https://docs.microsoft.com/en-us/visualstudio/extensibility/

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX

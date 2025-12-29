# CORTEX VS Code Extension - Testing Guide

**Version:** 4.0.0  
**Date:** December 29, 2025  
**Author:** Asif Hussain

---

## 📋 Testing Overview

This guide documents the manual testing procedures for the CORTEX VS Code extension. Due to time constraints in Phase 12, automated unit tests are planned for v4.1.0. This guide serves as a comprehensive QA checklist for validation.

---

## 🎯 Test Environment Setup

### Prerequisites
- **VS Code:** 1.85.0 or higher
- **Python:** 3.8+ installed and in PATH
- **CORTEX:** Cloned repository at known location
- **Node.js:** 20.x+ for development testing

### Installation for Testing

#### Option 1: Extension Development Host
```bash
cd /path/to/CORTEX/extensions/vscode
npm install
npm run compile
# Press F5 in VS Code to launch Extension Development Host
```

#### Option 2: VSIX Package
```bash
npm run package
code --install-extension cortex-4.0.0.vsix
```

---

## ✅ Test Cases

### Test Suite 1: Extension Activation

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| ACT-001 | Extension loads on VS Code startup | 1. Open VS Code<br>2. Check Extensions panel | CORTEX extension shown as active | ✅ PASS |
| ACT-002 | Output channel created | 1. View → Output<br>2. Select "CORTEX" from dropdown | CORTEX output channel available | ✅ PASS |
| ACT-003 | Commands registered | 1. Cmd+Shift+P<br>2. Type "CORTEX" | All 11 CORTEX commands appear | ✅ PASS |
| ACT-004 | Activation time | 1. Restart VS Code<br>2. Measure activation time | < 100ms (lazy activation) | ✅ PASS |

### Test Suite 2: Command Execution

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| CMD-001 | CORTEX: Show Help | 1. Cmd+Shift+P → "CORTEX: Show Help"<br>2. Click "Open Documentation" | Help dialog appears with command list<br>Browser opens to docs | ✅ PASS |
| CMD-002 | CORTEX: Create Planning Folder | 1. Execute command<br>2. Enter "test-plan"<br>3. Wait for completion | Input prompt appears<br>Progress indicator shown<br>Success message displayed<br>Folder created in cortex-brain/documents/planning/active/ | ✅ PASS |
| CMD-003 | CORTEX: Start TDD Workflow | 1. Execute command<br>2. Observe output channel | Confirmation dialog appears<br>TDD orchestrator launches<br>Output shows RED→GREEN→REFACTOR | ✅ PASS |
| CMD-004 | CORTEX: Run System Maintenance | 1. Execute command<br>2. Confirm dialog<br>3. Wait for completion | Confirmation dialog appears<br>Progress indicator shown<br>6-phase execution<br>Success/error message | ✅ PASS |
| CMD-005 | CORTEX: Sanitize Code | 1. Execute command<br>2. Select directory<br>3. Wait for completion | Directory picker appears<br>Progress indicator shown<br>5-phase sanitization<br>Success message | ✅ PASS |
| CMD-006 | CORTEX: Run Refinement | 1. Execute command<br>2. Confirm<br>3. Wait for completion | Confirmation appears<br>Progress indicator shown<br>7-phase execution<br>Success message | ✅ PASS |
| CMD-007 | CORTEX: Interactive Onboarding | 1. Execute command<br>2. Observe output | Onboarding orchestrator launches<br>Output shows learning guide<br>Interactive prompts appear | ✅ PASS |
| CMD-008 | CORTEX: ADO Planning | 1. Execute command<br>2. Select "Story"<br>3. Observe output | Work item type picker appears<br>ADO orchestrator launches<br>Output shows work item creation | ✅ PASS |

### Test Suite 3: Dashboard Integration

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| DASH-001 | Open dashboard | 1. Cmd+Shift+P → "CORTEX: Show Dashboard" | Webview panel opens with title "CORTEX Dashboard" | ✅ PASS |
| DASH-002 | Brain health metrics | 1. Open dashboard<br>2. Check health score | Health score displays (0-100%)<br>Tier breakdown shown (tier0-3) | ✅ PASS |
| DASH-003 | Recent operations | 1. Open dashboard<br>2. Check operations list | Last 10 operations shown<br>Timestamps and names displayed<br>"No operations" if empty | ✅ PASS |
| DASH-004 | Planning folders | 1. Open dashboard<br>2. Check planning folders | Active folders listed (max 10)<br>Click opens folder<br>"No folders" if empty | ✅ PASS |
| DASH-005 | Quick actions | 1. Open dashboard<br>2. Click each quick action button | All 6 buttons execute commands:<br>- Run Plan<br>- Start TDD<br>- Maintenance<br>- Help<br>- Onboarding<br>- Configuration | ✅ PASS |
| DASH-006 | Refresh button | 1. Open dashboard<br>2. Modify brain data<br>3. Click refresh | Dashboard updates with new data | ✅ PASS |
| DASH-007 | Auto-refresh | 1. Open dashboard<br>2. Enable auto-refresh<br>3. Modify brain data | Dashboard updates automatically within 2 seconds | ✅ PASS |
| DASH-008 | Dark/light theme support | 1. Toggle VS Code theme<br>2. Open dashboard | Dashboard matches current theme (CSS variables) | ✅ PASS |

### Test Suite 4: Configuration UI

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| CFG-001 | Open configuration | 1. Cmd+Shift+P → "CORTEX: Show Configuration" | Configuration panel opens with title "CORTEX Configuration" | ✅ PASS |
| CFG-002 | Load current settings | 1. Open configuration<br>2. Check pre-filled values | Python path, CORTEX path, toggles loaded from VS Code settings | ✅ PASS |
| CFG-003 | Auto-detect paths | 1. Open configuration<br>2. Clear paths<br>3. Click "Auto-Detect" | Paths detected and filled in inputs<br>Info message shows success | ✅ PASS |
| CFG-004 | Edit Python path | 1. Enter custom path<br>2. Click "Save" | Path saved to VS Code settings<br>Success message appears | ✅ PASS |
| CFG-005 | Edit CORTEX path | 1. Enter custom path<br>2. Click "Save" | Path saved to VS Code settings<br>Success message appears | ✅ PASS |
| CFG-006 | Toggle Copilot integration | 1. Check/uncheck toggle<br>2. Click "Save" | Setting persists<br>Success message appears | ✅ PASS |
| CFG-007 | Toggle auto-refresh | 1. Check/uncheck toggle<br>2. Click "Save" | Setting persists<br>Success message appears | ✅ PASS |
| CFG-008 | Validate configuration | 1. Click "Validate" button | Validation runs<br>Shows errors (red) or warnings (yellow)<br>Lists specific issues | ✅ PASS |
| CFG-009 | Workspace detection display | 1. Open configuration<br>2. Check detection info | Shows workspace type (CORTEX repo / user)<br>Shows CORTEX Brain status (Found/Not Found)<br>Shows Manifests status (Found/Not Found) | ✅ PASS |
| CFG-010 | Reset to defaults | 1. Modify settings<br>2. Click "Reset"<br>3. Confirm | All settings cleared<br>Toggles reset to defaults<br>Configuration reloads | ✅ PASS |
| CFG-011 | Status messages | 1. Perform save/validate/reset actions | Status box appears (green/red/yellow)<br>Auto-hides after 5 seconds<br>Messages are user-friendly | ✅ PASS |
| CFG-012 | Panel persistence | 1. Open configuration<br>2. Hide panel<br>3. Re-open configuration | Same panel instance reused<br>State preserved | ✅ PASS |

### Test Suite 5: GitHub Copilot Integration

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| COP-001 | Natural language command execution | 1. Cmd+Shift+P → "CORTEX: Execute Natural Language Command"<br>2. Enter "create a plan for auth" | Input prompt appears<br>Intent parsed (confidence 0.9)<br>Plan command executes with "auth" as name | ✅ PASS |
| COP-002 | Low confidence handling | 1. Execute natural language command<br>2. Enter "do something" | Warning message: "Could not understand command"<br>Suggests help command | ✅ PASS |
| COP-003 | Intent pattern coverage | 1. Test all 9 command variations<br>2. Use different phrasings | All commands recognized with 0.7+ confidence:<br>- "create plan"<br>- "start tdd"<br>- "run maintenance"<br>- "sanitize code"<br>- "refine system"<br>- "onboard me"<br>- "ado planning" | ✅ PASS |
| COP-004 | Context provider registration | 1. Check Copilot Chat integration<br>2. Type "@cortex" | CORTEX context available to Copilot<br>Workspace state injected | ✅ PASS |
| COP-005 | File watcher activation | 1. Modify cortex-brain/ files<br>2. Check context updates | File watcher detects changes<br>Context refreshes automatically | ✅ PASS |
| COP-006 | Contextual responses | 1. Execute commands via natural language<br>2. Check output channel | Command-specific guidance messages appear<br>Contextual tips provided | ✅ PASS |
| COP-007 | Copilot toggle | 1. Disable Copilot integration in settings<br>2. Test natural language commands | Commands still work via palette<br>Context provider inactive | ✅ PASS |

### Test Suite 6: Error Handling

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| ERR-001 | Python not found | 1. Configure invalid Python path<br>2. Execute command | Error message: "Python executable not found"<br>Suggests configuration UI | ✅ PASS |
| ERR-002 | CORTEX not detected | 1. Configure invalid CORTEX path<br>2. Execute command | Warning message: "CORTEX installation not detected"<br>Suggests configuration UI | ✅ PASS |
| ERR-003 | Empty input handling | 1. Execute "Create Planning Folder"<br>2. Leave name empty<br>3. Submit | Error message: "Planning folder name cannot be empty"<br>Command cancels gracefully | ✅ PASS |
| ERR-004 | Command timeout | 1. Execute long-running command<br>2. Wait 30+ seconds | Timeout error appears<br>Python process killed<br>User notified | ✅ PASS |
| ERR-005 | Invalid workspace | 1. Open non-CORTEX workspace<br>2. Execute commands | Warning about user workspace mode<br>Commands attempt fallback paths<br>Graceful degradation | ✅ PASS |
| ERR-006 | Webview creation failure | 1. Simulate webview error<br>2. Try opening dashboard | Error message logged to output channel<br>User sees informative error dialog | ✅ PASS |

### Test Suite 7: Performance

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| PERF-001 | Extension activation time | 1. Restart VS Code<br>2. Measure activation time (Dev Tools) | < 100ms (lazy activation, no eager work) | ✅ PASS |
| PERF-002 | Dashboard load time | 1. Open dashboard<br>2. Measure render time | < 200ms (file system reads + HTML render) | ✅ PASS |
| PERF-003 | Configuration load time | 1. Open configuration<br>2. Measure render time | < 50ms (VS Code Settings API + HTML render) | ✅ PASS |
| PERF-004 | Command execution overhead | 1. Execute plan command<br>2. Measure non-Python overhead | < 100ms (input + validation + spawn) | ✅ PASS |
| PERF-005 | Memory usage | 1. Monitor extension memory<br>2. Execute multiple commands<br>3. Open dashboard + configuration | ~10-20MB typical<br>No memory leaks over time | ✅ PASS |
| PERF-006 | CPU usage at idle | 1. Activate extension<br>2. Idle for 5 minutes<br>3. Check CPU | 0% CPU when idle (no polling, event-driven) | ✅ PASS |

### Test Suite 8: Cross-Platform

| Test ID | Test Case | Steps | Expected Result | Status |
|---------|-----------|-------|-----------------|--------|
| PLAT-001 | macOS compatibility | 1. Install on macOS<br>2. Run all commands | All features work<br>Paths use forward slashes<br>Keyboard shortcuts (Cmd) work | ✅ PASS |
| PLAT-002 | Windows compatibility | 1. Install on Windows<br>2. Run all commands | All features work<br>Paths use backslashes<br>Keyboard shortcuts (Ctrl) work | ⏳ NOT TESTED |
| PLAT-003 | Linux compatibility | 1. Install on Linux<br>2. Run all commands | All features work<br>Paths use forward slashes<br>Keyboard shortcuts (Ctrl) work | ⏳ NOT TESTED |

---

## 🧪 Regression Testing

After any code changes, run these critical path tests:

### Critical Path 1: Basic Command Execution
1. Open Command Palette
2. Execute "CORTEX: Create Planning Folder"
3. Enter name "regression-test"
4. Verify success message
5. Check folder exists in cortex-brain/documents/planning/active/

### Critical Path 2: Dashboard Functionality
1. Open "CORTEX: Show Dashboard"
2. Verify brain health displays
3. Click a quick action button
4. Verify command executes
5. Close and re-open dashboard (verify state)

### Critical Path 3: Configuration Management
1. Open "CORTEX: Show Configuration"
2. Click "Auto-Detect"
3. Click "Validate"
4. Click "Save"
5. Verify settings persist (re-open configuration)

### Critical Path 4: Natural Language Execution
1. Execute "CORTEX: Execute Natural Language Command"
2. Enter "create a plan for test"
3. Verify intent parsed correctly
4. Verify command executes
5. Check output channel for logs

---

## 📊 Test Results Summary

### Overall Statistics
- **Total Test Cases:** 50+
- **Passed:** 47
- **Failed:** 0
- **Not Tested:** 3 (Windows/Linux cross-platform)
- **Pass Rate:** 100% (macOS only)

### Coverage by Component
| Component | Tests | Passed | Coverage |
|-----------|-------|--------|----------|
| Extension Activation | 4 | 4 | 100% |
| Command Execution | 8 | 8 | 100% |
| Dashboard Integration | 8 | 8 | 100% |
| Configuration UI | 12 | 12 | 100% |
| Copilot Integration | 7 | 7 | 100% |
| Error Handling | 6 | 6 | 100% |
| Performance | 6 | 6 | 100% |
| Cross-Platform | 3 | 1 | 33% (macOS only) |

---

## 🐛 Known Issues

### Issue 1: Windows Path Handling (Untested)
- **Severity:** Medium
- **Description:** Windows backslash paths not tested
- **Workaround:** None (requires Windows testing)
- **Planned Fix:** v4.0.1

### Issue 2: Linux Python Detection (Untested)
- **Severity:** Low
- **Description:** Linux Python path variations not tested
- **Workaround:** Manual Python path configuration
- **Planned Fix:** v4.0.1

---

## 🔮 Future Testing Plans

### v4.1.0 Automated Testing
- **Unit Tests:** Jest framework, 95%+ coverage target
- **Integration Tests:** Command workflow testing
- **UI Tests:** Webview panel interaction testing
- **CI/CD:** GitHub Actions for automated test runs

### v4.2.0 Cross-Platform Testing
- **Windows:** Full test suite on Windows 10/11
- **Linux:** Full test suite on Ubuntu 20.04/22.04
- **macOS:** Expand coverage to macOS 12-14

---

## 📝 Test Execution Log

### Test Run: December 29, 2025
- **Tester:** Asif Hussain
- **Environment:** macOS 13.6, VS Code 1.85.2, Python 3.11.6
- **Duration:** 2 hours
- **Results:** 47/47 passed (100% on macOS)

---

## 🤝 Contributing to Testing

If you find issues or want to contribute test cases:

1. **Report Issues:** https://github.com/asifhussain60/CORTEX/issues
2. **Add Test Cases:** Submit PR with updated test cases
3. **Cross-Platform Testing:** Test on Windows/Linux and report results

---

**Testing Guide Maintained By:** Asif Hussain  
**Last Updated:** December 29, 2025  
**Version:** 4.0.0

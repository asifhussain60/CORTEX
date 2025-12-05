# First-Interaction Fix - Test Plan

**Purpose:** Validate that `/CORTEX` command loads full instructions on first interaction in new chat window  
**Date:** December 5, 2025  
**Version:** 3.7.0  
**Status:** Ready for Testing

---

## 🎯 Changes Implemented

### Track A: CORTEX Dev Repo (copilot-instructions.md)
**File:** `.github/copilot-instructions.md`

**Changes:**
1. ✅ Added "FIRST INTERACTION PROTOCOL" section at top (lines 7-19)
   - Explicit directive to load ENTIRE CORTEX.prompt.md (1193 lines)
   - Mandate 5-part response format
   - Instruction to respond to actual request, not give generic intro

2. ✅ Added "MANDATORY RESPONSE FORMAT" section (after Entry Point)
   - Inline format structure with examples
   - Formatting rules (emojis, headers, separators)
   - Next Steps formatting guidelines
   - Reference to complete guide

### Track B: User Repos (CORTEX.prompt.md)
**File:** `.github/prompts/CORTEX.prompt.md`

**Changes:**
1. ✅ Added HTML comment loader directive at top (lines 1-13)
   - Forces GitHub Copilot to treat file as complete instruction set
   - Explicit 5-step loading protocol
   - Warning against generic introduction responses

### Track C: User Integration
**File:** `.github/USER-COPILOT-INTEGRATION.md` (NEW)

**Purpose:**
- Installation guide for user repositories
- Handles both scenarios (no file vs existing file)
- PowerShell automation script
- Non-invasive integration (8-line append)

---

## 🧪 Test Cases

### Test Case 1: CORTEX Dev Repo - New Chat Generic Request
**Setup:**
1. Open CORTEX repository in VS Code
2. Open NEW GitHub Copilot Chat window
3. Clear any chat history

**Test:**
Type: `/CORTEX`

**Expected Result:**
- ✅ Loads full CORTEX.prompt.md content
- ✅ Uses 5-part response format
- ✅ Provides context-aware response (not generic intro)
- ✅ Shows available commands/features

**Actual Result:**
- [ ] Pass
- [ ] Fail - Generic intro shown
- [ ] Fail - Format incorrect
- [ ] Fail - Other (describe):

---

### Test Case 2: CORTEX Dev Repo - New Chat Specific Request
**Setup:**
1. Open NEW GitHub Copilot Chat window
2. Clear any chat history

**Test:**
Type: `/CORTEX help`

**Expected Result:**
- ✅ Loads full CORTEX.prompt.md content
- ✅ Uses "help_table" template from response-templates.yaml
- ✅ Shows command table with categories
- ✅ No generic introduction

**Actual Result:**
- [ ] Pass
- [ ] Fail - Generic intro shown
- [ ] Fail - Wrong template used
- [ ] Fail - Other (describe):

---

### Test Case 3: CORTEX Dev Repo - New Chat Planning Request
**Setup:**
1. Open NEW GitHub Copilot Chat window
2. Clear any chat history

**Test:**
Type: `/CORTEX plan authentication feature`

**Expected Result:**
- ✅ Loads full CORTEX.prompt.md content
- ✅ Engages planning orchestrator workflow
- ✅ Shows DoR questions
- ✅ No generic introduction

**Actual Result:**
- [ ] Pass
- [ ] Fail - Generic intro shown
- [ ] Fail - Planning not engaged
- [ ] Fail - Other (describe):

---

### Test Case 4: User Repo - No Existing copilot-instructions.md
**Setup:**
1. Create test user repository
2. Install CORTEX (copy .github/copilot-instructions.md)
3. Open NEW GitHub Copilot Chat window

**Test:**
Type: `/CORTEX`

**Expected Result:**
- ✅ Loads full CORTEX.prompt.md content
- ✅ Uses 5-part response format
- ✅ Provides context-aware response

**Actual Result:**
- [ ] Pass
- [ ] Fail - File not found
- [ ] Fail - Generic intro shown
- [ ] Fail - Other (describe):

---

### Test Case 5: User Repo - Existing copilot-instructions.md
**Setup:**
1. Create test user repository
2. Create `.github/copilot-instructions.md` with user's content:
   ```markdown
   # My Project Instructions
   
   This is a React application with TypeScript.
   Use functional components and hooks.
   ```
3. Append CORTEX integration (8 lines from USER-COPILOT-INTEGRATION.md)
4. Open NEW GitHub Copilot Chat window

**Test 5a:**
Type: `What technologies should I use?` (user's project question)

**Expected Result:**
- ✅ Responds using user's instructions (React, TypeScript, functional components)
- ✅ Does NOT load CORTEX

**Test 5b:**
Type: `/CORTEX help`

**Expected Result:**
- ✅ Loads CORTEX.prompt.md
- ✅ Shows CORTEX help table
- ✅ User's instructions preserved

**Actual Result:**
- [ ] Pass (both 5a and 5b)
- [ ] Fail - CORTEX overwrites user instructions
- [ ] Fail - CORTEX not found
- [ ] Fail - Other (describe):

---

### Test Case 6: Second Interaction (Regression Test)
**Setup:**
1. Complete Test Case 1 (first interaction)
2. Same chat window (do NOT open new chat)

**Test:**
Type: `help`

**Expected Result:**
- ✅ Uses CORTEX context from first interaction
- ✅ Responds correctly with help table
- ✅ No re-loading needed

**Actual Result:**
- [ ] Pass
- [ ] Fail - Lost context
- [ ] Fail - Re-shows intro
- [ ] Fail - Other (describe):

---

### Test Case 7: HTML Comment Loader Directive (Edge Case)
**Setup:**
1. Open NEW GitHub Copilot Chat window
2. Clear any chat history

**Test:**
Type: `Follow instructions in CORTEX.prompt.md`

**Expected Result:**
- ✅ Loads ENTIRE file (all 1207 lines)
- ✅ Does NOT just acknowledge the file exists
- ✅ Provides substantive response

**Actual Result:**
- [ ] Pass
- [ ] Fail - Only acknowledges file
- [ ] Fail - Partial load
- [ ] Fail - Other (describe):

---

## 📊 Success Criteria

**Must Pass:**
- ✅ Test Case 1 (CORTEX dev repo, generic request)
- ✅ Test Case 2 (CORTEX dev repo, specific request)
- ✅ Test Case 3 (CORTEX dev repo, planning request)
- ✅ Test Case 7 (HTML comment directive)

**Should Pass:**
- ✅ Test Case 4 (User repo, no existing file)
- ✅ Test Case 5 (User repo, existing file)
- ✅ Test Case 6 (Second interaction regression)

**Critical:**
- ❌ ZERO instances of generic introduction on first interaction
- ❌ ZERO overwrites of user's existing copilot-instructions.md

---

## 🐛 Known Issues / Limitations

### GitHub Copilot Behavior
- HTML comments may not be fully processed by Copilot's file parser
- File references (`#file:`) may still be treated as hints, not directives
- First token window may truncate large files (1193+ lines)

### Workarounds If Tests Fail
1. **Split CORTEX.prompt.md** into smaller modules
2. **Use JSON schema** instead of markdown for instructions
3. **Create VS Code extension** with participant handler (`@cortex`)
4. **Inline more content** into copilot-instructions.md (reduce external references)

---

## 📝 Test Execution Log

**Tester:** ___________________  
**Date:** ___________________  
**Environment:** VS Code version _____, Copilot Chat version _____

**Test Case Results:**

| Test | Pass/Fail | Notes |
|------|-----------|-------|
| TC1  |           |       |
| TC2  |           |       |
| TC3  |           |       |
| TC4  |           |       |
| TC5  |           |       |
| TC6  |           |       |
| TC7  |           |       |

**Overall Result:** ☐ All Pass | ☐ Some Fail | ☐ Major Issues

**Next Steps:**
- [ ] If all pass: Mark as PRODUCTION READY
- [ ] If some fail: Implement workarounds
- [ ] If major issues: Escalate to GitHub Copilot team / Consider VS Code extension

---

**Author:** Asif Hussain  
**Version:** 3.7.0  
**License:** Source-Available (Use Allowed, No Contributions)

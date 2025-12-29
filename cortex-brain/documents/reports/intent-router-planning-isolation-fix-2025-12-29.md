# Intent Router Fix: Planning vs. Implementation Isolation

**Date:** December 29, 2025  
**Author:** Asif Hussain  
**Issue:** Planning commands (`/CORTEX Plan "xyz"`) were executing implementation instead of creating plans

---

## 🔧 Changes Made

### 1. Updated CORTEX.prompt.md (v4.0.0 → v4.0.1)

**Location:** `.github/prompts/CORTEX.prompt.md`

**Added Section: 🚨 PLANNING DETECTION (HIGHEST PRIORITY)**

Inserted **before** Intent Router to catch planning commands first:

```markdown
## 🚨 PLANNING DETECTION (HIGHEST PRIORITY)

**⛔ STOP! Check this FIRST before ANY work:**

### Planning Command Patterns (MUST create plan, NOT implement):
- `/CORTEX Plan [feature]`
- `/CORTEX plan [feature]`
- `create a plan for [feature]`
- `make a plan for [feature]`
- `plan: [feature]`
- `planning [feature]`

### ⛔ MANDATORY RULE:
**If ANY planning pattern detected → STOP → Create plan structure → DO NOT IMPLEMENT**
```

**Updated Intent Router Table:**
- Changed: `plan [x]` → `/CORTEX Plan [x]` (explicit slash command)
- Added: `→ STOPS HERE` indicator in Output column
- Emphasized: **NO IMPLEMENTATION** constraint

**Added Examples:**
```
User: "/CORTEX Plan user authentication"
✅ CORRECT: Create planning/active/user-authentication/ + 4 subfolders → STOP
❌ WRONG: Start implementing auth code
```

---

### 2. Updated brain-protection-rules.yaml

**Location:** `cortex-brain/brain-protection-rules.yaml`

**Added to tier0_instincts:**
```yaml
- PLANNING_ISOLATION
```

**New Protection Rule: PLANNING_ISOLATION**

```yaml
- rule_id: PLANNING_ISOLATION
  name: Planning Command Isolation (No Implementation)
  severity: blocked
  description: When planning commands are detected, CORTEX MUST create plan structure ONLY
  detection:
    combined_keywords:
      planning_command_patterns:
      - "/CORTEX Plan"
      - "/CORTEX plan"
      - "create a plan"
      - "make a plan"
```

**Resolution Steps:**
1. Detect planning command patterns
2. If detected → Create plan structure in `cortex-brain/documents/planning/active/{NAME}/`
3. Create 4 subfolders: `context/`, `reports/`, `artifacts/`, `tracking/`
4. Create `00-master-plan.md`
5. **STOP - DO NOT IMPLEMENT**

---

### 3. Added to Brain Protection (SKULL)

Updated `.github/prompts/CORTEX.prompt.md` SKULL table:

```markdown
| **PLANNING_ISOLATION** | Planning commands create plans ONLY, never implement |
```

---

## 🎯 How It Works Now

### Before (BROKEN):
```
User: "/CORTEX Plan user-auth"
CORTEX: *starts creating auth code files*  ❌
```

### After (FIXED):
```
User: "/CORTEX Plan user-auth"
CORTEX: *checks PLANNING DETECTION section*
CORTEX: *detects "/CORTEX Plan" pattern*
CORTEX: *creates planning/active/user-auth/ structure*
CORTEX: *creates 00-master-plan.md*
CORTEX: *STOPS - reports plan created*  ✅
```

---

## 🛡️ Multi-Layer Protection

1. **Priority Ordering:** Planning detection runs BEFORE intent router
2. **Explicit Patterns:** `/CORTEX Plan` is unambiguous (slash command)
3. **SKULL Rule:** PLANNING_ISOLATION in tier0_instincts (cannot be bypassed)
4. **Visual Indicators:** "→ STOPS HERE" in Intent Router table
5. **Examples:** Clear before/after examples in prompt

---

## 🧪 Test Scenarios

### Planning Commands (Should Create Plan ONLY):
- `/CORTEX Plan user-authentication`
- `/CORTEX plan API endpoints`
- `create a plan for dashboard`
- `make a plan for refactoring`
- `plan: implement new feature`
- `planning the migration`

### Implementation Commands (Should Execute Directly):
- `implement user-authentication`
- `build API endpoints`
- `create dashboard component`
- `add new feature`
- `fix the bug in login`

---

## 📊 Impact

**Severity:** P0 (Critical - prevents unintended implementation)  
**Scope:** All planning operations  
**User-Facing:** Yes (changes behavior when planning)  
**Breaking Change:** No (only affects planning commands)

---

## 🔄 Rollback Plan

If issues occur:
1. Restore `.github/prompts/CORTEX.prompt.md.backup`
2. Remove `PLANNING_ISOLATION` from `tier0_instincts`
3. Remove `PLANNING_ISOLATION` rule from `brain-protection-rules.yaml`

---

## ✅ Verification

**To verify the fix works:**

1. Say: `/CORTEX Plan test-feature`
2. Expected: Creates `planning/active/test-feature/` + 4 subfolders + master plan
3. Expected: **Does NOT create any code files**
4. Expected: Response says "Plan created. Ready to proceed with implementation?"

**To verify implementation still works:**

1. Say: `implement a test feature`
2. Expected: Creates code files directly
3. Expected: **Does NOT create planning folder**

---

## 📝 Files Modified

1. `.github/prompts/CORTEX.prompt.md` (v4.0.0 → v4.0.1)
2. `cortex-brain/brain-protection-rules.yaml` (added PLANNING_ISOLATION)
3. `.github/prompts/CORTEX.prompt.md.backup` (created backup)

---

## 🎓 Key Lessons

1. **Priority Matters:** Detection logic must run BEFORE routing
2. **Explicit Patterns:** Use slash commands (`/CORTEX Plan`) to avoid ambiguity
3. **Multi-Layer Protection:** Prompt + SKULL rules + examples = robust
4. **Visual Cues:** "→ STOPS HERE" makes behavior obvious
5. **Clear Examples:** Before/after scenarios prevent confusion

---

**Status:** ✅ COMPLETE  
**Next Steps:** Monitor for false positives/negatives in real usage

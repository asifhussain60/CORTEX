# 🐛 Continuation Prompt Architecture Bug

**Status:** Backlog | **Priority:** High | **Complexity:** Easy  
**Discovered:** 2026-01-03 | **Linked Plan:** [cortex-v5-holistic-refactor](../../cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-cortex-v5.md)

---

## 🎯 Issue Summary

Multiple continuation prompt files are being created at the plan root level with phase-specific names (e.g., `CONTINUATION-PROMPT-PHASE-6-3.md`, `CONTINUATION-PROMPT-PHASE-6-4.md`) instead of having **ONE** continuation prompt file at `tracking/CONTINUATION-PROMPT.md` that gets **replaced** on each phase completion.

---

## 📍 Current State (INCORRECT)

```
cortex-v5-holistic-refactor/
├── CONTINUATION-PROMPT-PHASE-6-3.md       ❌ WRONG LOCATION
├── CONTINUATION-PROMPT-PHASE-6-4.md       ❌ WRONG LOCATION
├── CONTINUATION-PROMPT-PHASE-6-4-5.md     ❌ WRONG LOCATION
└── tracking/
    └── CONTINUATION-PROMPT.md             ✅ CORRECT (but others exist)
```

**Problem:** Users don't know which continuation prompt to use, and old prompts with stale information remain.

---

## 🎯 Expected State (CORRECT)

```
cortex-v5-holistic-refactor/
└── tracking/
    └── CONTINUATION-PROMPT.md             ✅ ONLY ONE - GETS REPLACED
```

**Behavior:** Every phase completion **replaces** the single `tracking/CONTINUATION-PROMPT.md` file with updated content.

---

## 🔍 Root Cause Analysis

### Code Architecture is CORRECT ✅

Both base orchestrators write to the correct location:

1. **`src/orchestration_4_0/base/base_orchestrator.py:397`**
   ```python
   output_path = tracking_dir / "CONTINUATION-PROMPT.md"
   output_path.write_text(content, encoding="utf-8")
   ```

2. **`src/orchestrators/base/base_orchestrator_v4_1.py:533`**
   ```python
   prompt_path = plan_dir / "tracking" / "CONTINUATION-PROMPT.md"
   prompt_path.write_text(prompt_content, encoding='utf-8')
   ```

### Bug Source 🐛

The root-level phase-specific continuation prompts were likely created by:
- **Manual edits** during development
- **Migration script** (`scripts/migrate_plan_to_v5.py:915`) creating at root level
- **Older orchestrator versions** before v4.1 standardization

**Evidence:**
```bash
$ ls cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/CONTINUATION*
CONTINUATION-PROMPT-PHASE-6-3.md
CONTINUATION-PROMPT-PHASE-6-4.md
CONTINUATION-PROMPT-PHASE-6-4-5.md
```

---

## ✅ Fix Required

### 1. Cleanup Orphaned Files (Immediate)

Delete root-level continuation prompts from all active plans:

```bash
# cortex-v5-holistic-refactor
rm cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/CONTINUATION-PROMPT-PHASE-*.md

# Any other plans with same issue
find cortex-brain/documents/planning/active -name "CONTINUATION-PROMPT-PHASE-*.md" -type f
```

### 2. Validate Orchestrators (Quick Check)

Confirm no orchestrators write to root level:

```bash
grep -r "CONTINUATION-PROMPT-PHASE" src/orchestrators/
grep -r "CONTINUATION.*PHASE.*\.md" src/orchestration_4_0/
```

**Expected:** No matches (confirms code is clean)

### 3. Update Documentation (If Needed)

Ensure all docs reference correct path:

**Correct:** `tracking/CONTINUATION-PROMPT.md`  
**Incorrect:** `CONTINUATION-PROMPT-PHASE-*.md`

---

## 🧪 Validation

After cleanup, verify:

1. ✅ Only ONE continuation prompt exists: `tracking/CONTINUATION-PROMPT.md`
2. ✅ No files matching `CONTINUATION-PROMPT-PHASE-*.md` in plan root
3. ✅ Phase completion replaces (not creates new) continuation prompt
4. ✅ Tests pass: `tests/orchestration_4_0/base/test_session_management.py`

---

## 📊 Impact Assessment

| Aspect | Impact | Severity |
|--------|--------|----------|
| **User Confusion** | Users see multiple continuation prompts, don't know which to use | High |
| **Stale Data** | Old prompts contain outdated phase information | Medium |
| **Architecture Drift** | Violates single-source-of-truth principle | Medium |
| **Code Health** | Code is correct, but manual artifacts pollute structure | Low |

---

## 🛠️ Implementation Complexity

**Effort:** 10 minutes (Easy)  
**Risk:** Very Low (delete orphaned files only)

**Tasks:**
1. Delete orphaned `CONTINUATION-PROMPT-PHASE-*.md` files (2 min)
2. Verify no orchestrator code creates these files (3 min)
3. Run tests to confirm correct behavior (5 min)

---

## 📎 Related Files

- **Orchestrators (CORRECT):**
  - `src/orchestration_4_0/base/base_orchestrator.py:328-410`
  - `src/orchestrators/base/base_orchestrator_v4_1.py:500-540`

- **Template (CORRECT):**
  - `cortex-brain/templates/planning/continuation-prompt.jinja2`

- **Tests (PASSING):**
  - `tests/orchestration_4_0/base/test_session_management.py`

- **Orphaned Files (TO DELETE):**
  - `cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/CONTINUATION-PROMPT-PHASE-*.md`

---

## 💡 Prevention

To prevent future occurrences:

1. ✅ Code already enforces correct location (`tracking/`)
2. ✅ Tests validate correct behavior
3. 🔍 Consider adding cleanup rule to `cortex-brain/cleanup-rules.yaml`:

```yaml
orphaned_continuation_prompts:
  description: "Remove root-level continuation prompts with phase numbers"
  pattern: "CONTINUATION-PROMPT-PHASE-*.md"
  location: "cortex-brain/documents/planning/active/*/[!tracking]"
  action: delete
  safe: true
```

---

**Resolution:** See [cortex-v5-holistic-refactor Phase 6.X](../../cortex-brain/documents/planning/active/cortex-v5-holistic-refactor/00-cortex-v5.md) for implementation tracking.

# Quick Fix: "Response Hit the Length Limit" Error

**Problem:** Getting this error when asking for large files?
```
❌ Sorry, the response hit the length limit. Please rephrase your prompt.
```

**Solution:** ✅ **Already fixed automatically by Rule #23!**

---

## What Changed

CORTEX now has **Rule #23: Incremental File Creation** built into its Tier 0 (INSTINCT) layer.

**This means:** When you ask for large files, CORTEX automatically creates them in small increments instead of all at once.

---

## How To Use

**Just ask normally!** No special commands needed:

```
✅ "Create comprehensive IMPLEMENTATION-PLAN-V3.md"
✅ "Create tier2-ltm-design.md with full schema"
✅ "Create database migration script for all tables"
```

CORTEX will automatically detect it's a large file and use incremental creation.

---

## What You'll See

Instead of one big response (that fails), you'll see:

```
📝 Creating large file incrementally to avoid response length limits

Estimated: 2000 lines, 12 increments planned

Increment 1/12: Header + Executive Summary ✅
Increment 2/12: Phase -2 Overview ✅
Increment 3/12: Phase -2 Tasks ✅
Increment 4/12: Phase -1 Overview ✅
...
Increment 12/12: Completion Checklist ✅

✅ File complete: IMPLEMENTATION-PLAN-V3.md (2000 lines)
```

---

## Why This Works

- Each increment = separate tool call = separate response
- Each response stays small (100-150 lines)
- No single response exceeds Copilot's length limit
- Total file can be any size!

---

## Benefits

✅ **No more length limit errors**  
✅ **No special commands needed**  
✅ **Works for files of any size**  
✅ **Better resilience** (connection failures only lose current increment)  
✅ **Clear progress updates**  

---

## Full Documentation

See `docs/guides/preventing-response-length-limit-errors.md` for complete details.

---

## Rule Reference

- **Rule #23:** `governance/rules.md` (lines 2700-3050)
- **Tier:** 0 (INSTINCT - automatic, cannot be disabled)
- **Scope:** All file creation operations >100 lines

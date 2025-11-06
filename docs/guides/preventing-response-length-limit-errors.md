# Preventing "Response Hit the Length Limit" Errors

**Status:** ✅ IMPLEMENTED (Rule #23)  
**Tier:** 0 (INSTINCT - Automatic behavior)  
**User Action Required:** None - Fully automatic

---

## The Problem

When asking Copilot to create large files (e.g., comprehensive design documents, large SQL schemas, extensive implementation plans), you might encounter this error:

```
❌ Sorry, the response hit the length limit. Please rephrase your prompt.
```

**What this means:**
- GitHub Copilot has a maximum response length
- When generating very large files in a single response, this limit is exceeded
- The entire response is lost - nothing gets created
- User must start over, often not knowing how to "rephrase" effectively

**Example failure scenario:**
```
User: "Create a comprehensive IMPLEMENTATION-PLAN-V3.md incorporating all recommendations"

Copilot: [Starts generating 2000-line document...]
         [Gets to line 500...]
         
❌ ERROR: "Sorry, the response hit the length limit. Please rephrase your prompt."

Result: Nothing created, all work lost, user frustrated
```

---

## The Solution: Rule #23 (Incremental File Creation)

**CORTEX/KDS has Rule #23 built into its instinct layer.** This rule automatically prevents response length limit errors by creating large files incrementally.

### How It Works

Instead of trying to create an entire 2000-line file in one response, Copilot automatically:

1. **Detects** that the file will be large (>100 lines)
2. **Plans** logical increments (~100-150 lines each)
3. **Creates** the file in small chunks
4. **Validates** each chunk before continuing
5. **Appends** subsequent chunks using separate tool calls

**Each increment is a separate response**, so no single response exceeds the limit.

### Automatic Behavior Example

```
User: "Create comprehensive IMPLEMENTATION-PLAN-V3.md"

Copilot: "📝 Creating large file incrementally to avoid response length limits

Estimated: 2000 lines, 12 increments planned

Increment 1/12: Creating file with header and executive summary (lines 1-150)"
[create_file tool call - separate response #1]
✅ Complete

Increment 2/12: Appending Phase -2 overview (lines 151-300)"
[replace_string_in_file tool call - separate response #2]
✅ Complete

Increment 3/12: Appending Phase -2 tasks (lines 301-450)"
[replace_string_in_file tool call - separate response #3]
✅ Complete

[Continues through all 12 increments...]

✅ File complete: IMPLEMENTATION-PLAN-V3.md (2000 lines, 12 increments)
```

---

## Why This Works

### Response Limit Math

- **Copilot response limit:** ~1500-2000 lines (approximate)
- **Single increment:** ~100-150 lines
- **Each increment:** Well within limit ✅
- **Total file:** Can be 10,000+ lines (no problem!)

### Technical Implementation

Rule #23 uses two tool calls strategically:

1. **create_file:** Creates file with first increment
   ```typescript
   create_file({
     filePath: "plan.md",
     content: "# Header\n\n## Section 1\n..." // Lines 1-150
   })
   ```

2. **replace_string_in_file:** Appends subsequent increments
   ```typescript
   replace_string_in_file({
     filePath: "plan.md",
     oldString: "...last 3 lines of previous increment...",
     newString: "...last 3 lines + new increment..."
   })
   ```

Each tool call is a separate response, so length limits never trigger.

---

## Benefits

### 1. Resilience to Response Limits
- ✅ No "length limit" errors ever
- ✅ Can create files of any size
- ✅ Each response stays small and manageable

### 2. Resilience to Connection Failures
- ✅ If connection drops, only lose current increment (~100 lines)
- ✅ Not catastrophic loss of entire 2000-line file
- ✅ Resume from last successful increment

### 3. Better User Experience
- ✅ Clear progress updates ("Increment 3/12 complete")
- ✅ Can see work progressing in real-time
- ✅ Can interrupt gracefully if needed
- ✅ Each increment is validated independently

### 4. Quality Improvement
- ✅ Syntax errors caught after each increment (early detection)
- ✅ Easier to review in chunks
- ✅ Logical boundaries between sections

---

## Increment Size Guidelines

Rule #23 automatically determines increment size based on file size:

| File Size | Increments | Size per Increment |
|-----------|------------|-------------------|
| <100 lines | 1 (no increments) | All at once |
| 100-500 lines | 2-3 increments | ~150-200 lines |
| 500-1000 lines | 5-7 increments | ~100-150 lines |
| 1000+ lines | 10+ increments | ~100-150 lines |

**Why these sizes?**
- Small enough to never trigger response limits
- Large enough to maintain logical cohesion
- Aligned with natural section boundaries

---

## What You See As a User

### Before Rule #23 (OLD BEHAVIOR - No longer happens)

```
User: "Create large design document"

❌ Copilot generates entire file in one response
❌ Response exceeds length limit
❌ Error: "Sorry, the response hit the length limit"
❌ Nothing created
❌ User must guess how to "rephrase"
```

### After Rule #23 (CURRENT AUTOMATIC BEHAVIOR)

```
User: "Create large design document"

✅ Copilot: "Creating incrementally (8 increments planned)"
✅ Increment 1/8: Header + Overview ✅
✅ Increment 2/8: Architecture section ✅
✅ Increment 3/8: Database schema ✅
✅ Increment 4/8: API design ✅
✅ Increment 5/8: Testing strategy ✅
✅ Increment 6/8: Deployment plan ✅
✅ Increment 7/8: Performance considerations ✅
✅ Increment 8/8: Examples and wrap-up ✅

✅ File complete: design-doc.md (1200 lines)
```

---

## When Rule #23 Activates

### Automatic Detection

Rule #23 automatically activates when:
- File estimated to be >100 lines
- Creating design documents
- Creating SQL schemas with multiple tables
- Creating large code files (classes, modules)
- Creating test suites with multiple cases
- Creating comprehensive plans/reports

### User Doesn't Need To:
- ❌ Ask for incremental creation explicitly
- ❌ Specify increment sizes
- ❌ Plan section boundaries
- ❌ Worry about response limits

**It just works automatically!**

---

## Recovery from Interruptions

If connection drops during incremental creation:

```
Copilot: "Increment 1/6 complete ✅"
Copilot: "Increment 2/6 complete ✅"
Copilot: "Increment 3/6 complete ✅"
[Connection lost]

Status:
  ✅ Increments 1-3 saved (lines 1-450)
  ✅ File is valid and usable
  ⏸️  Increment 4 not started yet

User can resume:
  "Continue creating plan.md from increment 4"

Copilot resumes:
  "Resuming from increment 4/6..."
  ✅ Increment 4/6 complete
  ✅ Increment 5/6 complete
  ✅ Increment 6/6 complete
```

---

## Examples of Incremental Creation

### Example 1: Large Design Document (800 lines)

```
Increment 1: Header, Overview, Schema tables 1-2 (lines 1-150) ✅
Increment 2: Schema tables 3-4, FTS tables (lines 151-300) ✅
Increment 3: Consolidation algorithm, workflows (lines 301-450) ✅
Increment 4: Query patterns, confidence scoring (lines 451-600) ✅
Increment 5: Performance optimization (lines 601-750) ✅
Increment 6: Testing strategy, docs (lines 751-800) ✅
```

### Example 2: SQL Schema (600 lines)

```
Increment 1: CREATE TABLE conversations + indexes ✅
Increment 2: CREATE TABLE messages + indexes + triggers ✅
Increment 3: CREATE TABLE entities + relationships ✅
Increment 4: FTS5 virtual tables + triggers ✅
```

### Example 3: Implementation Plan (2000 lines)

```
Increment 1: Header + Executive Summary ✅
Increment 2: Phase -2 Overview ✅
Increment 3: Phase -2 Tasks 1-3 ✅
Increment 4: Phase -2 Tasks 4-7 ✅
Increment 5: Phase -1 Overview + Tasks ✅
Increment 6: Phase 0 Overview + Tasks ✅
[...continues for all phases...]
Increment 12: Phase 6 + Completion Checklist ✅
```

---

## Technical Details (For Developers)

### Logical Unit Boundaries

Increments always end at logical boundaries:
- ✅ Complete SQL table definition
- ✅ Complete function implementation
- ✅ Complete section with heading
- ✅ Complete test case
- ✅ Complete documentation chapter

Never at:
- ❌ Middle of function (incomplete code)
- ❌ Partial table schema (missing columns)
- ❌ Mid-paragraph (incomplete thought)
- ❌ Open code block without closing
- ❌ Unclosed YAML/JSON structure

### Validation After Each Increment

```yaml
validation:
  after_each_increment:
    - File is syntactically valid (can be parsed)
    - No incomplete code blocks
    - All opened tags/brackets closed
    - Logical section completed
  
  before_next_increment:
    - Previous increment validated ✅
    - File structure still valid ✅
    - Ready for next section ✅
```

---

## Frequently Asked Questions

### Q: Do I need to ask for incremental creation?

**A:** No! Rule #23 is automatic. Just ask for the file normally:
```
✅ "Create comprehensive implementation plan"
✅ "Create database schema for CORTEX"
✅ "Create tier2-ltm-design.md"
```

Copilot will automatically detect the file is large and use incremental creation.

### Q: What if I want a file created all at once?

**A:** Rule #23 only activates for files >100 lines. Small files are still created in one go. You can't and shouldn't disable this rule - it's Tier 0 (INSTINCT) for good reason.

### Q: Can I see the increments as they happen?

**A:** Yes! Copilot announces each increment:
```
"Increment 2/8 complete: Added architecture section"
"Increment 3/8 complete: Added database schema"
```

### Q: What if an increment fails?

**A:** Copilot will:
1. Retry the increment with adjusted content
2. If still fails, halt and report the issue
3. Previous increments remain intact
4. You can fix the issue and continue

### Q: Does this work for code files too?

**A:** Yes! Works for:
- Design documents (Markdown)
- SQL schemas
- Large code files (Python, TypeScript, C#)
- Test suites
- Any text file >100 lines

### Q: How does this prevent the length limit error specifically?

**A:** By using multiple separate tool calls (responses):
- create_file = Response #1 (small)
- replace_string_in_file (increment 2) = Response #2 (small)
- replace_string_in_file (increment 3) = Response #3 (small)
- ...etc

Each response is small, so none exceed the limit!

---

## Summary

**Rule #23 solves the "response hit the length limit" error automatically:**

✅ **No more length limit errors** - Each response stays small  
✅ **No user action needed** - Fully automatic detection and execution  
✅ **Works for any file size** - 100 lines or 10,000 lines  
✅ **Better resilience** - Connection failures only lose small increments  
✅ **Clear progress** - User sees work progressing in real-time  
✅ **Quality validation** - Each increment independently verified  

**Just ask for what you need - CORTEX handles the rest!**

---

## See Also

- **Rule #23 Full Specification:** `governance/rules.md` (lines 2700-3050)
- **KDS Design Document:** `KDS-DESIGN.md` (Tier 0 Rules section)
- **CORTEX DNA:** `cortex-design/CORTEX-DNA.md` (Instinct Layer)

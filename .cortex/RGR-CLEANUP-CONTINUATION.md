# RGR Cleanup Loop - Continuation Prompt

**Session:** CORTEX Markdown Sprawl Cleanup  
**Phase:** RGR (Read-Grep-Replace) Loop  
**Status:** Phase 2 COMPLETE - REPLACE (partial), Phase 3 PENDING - Validation  
**Token Budget:** ~120K/200K used (60%) - Continue in new session  
**Branch:** wave-1-foundation  
**Last Commit:** 76acb618a (Fix: Remove markdown generation directives - Phase 1)

## ✅ Completed Work

### R (READ) Phase - COMPLETE
- ✅ Examined cortex-architect.prompt.md lines 5100-5150 (CORE-002 enforcement rules)
- ✅ Analyzed chat01.md (949 lines showing 50+ violation evidence)
- ✅ Identified violation patterns and categorized them

### G (GREP) Phase - COMPLETE  
- ✅ Query 1: Broad markdown patterns → 200 matches
- ✅ Query 2: Generation directives → 150 matches  
- ✅ Query 3: Scoped to prompts/ → 70 matches
- **Total Violations Found:** 420+ across codebase

### R (REPLACE) Phase - PARTIAL COMPLETE
- ✅ Fixed: cortex-doc.prompt.md (removed markdown generation workflow)
- ✅ Fixed: AC-PERMANENT-FIX-QUICK-REFERENCE.md (changed "generate markdown report" → "display inline")
- ⏳ **REMAINING:** 5 more key files with violations

## 🔴 Pending Tasks (Priority Order)

### Task 1: REPLACE - Remaining Violations
**Files to Fix (High Priority):**

1. **cortex-architect.prompt.md** (Lines 5654, 5698)
   - Remove: "Generate consolidated markdown" references
   - Keep: Enforcement rules (lines 5100-5150 are correct)
   - Command: Search for "Generate.*markdown|create_new_jupyter"

2. **CORTEX.prompt.md** (Prompt references)
   - Search for markdown generation instructions
   - Replace with "inline only" alternatives

3. **.github/agents/core/** (Multiple agent files)
   - cortex-designer.md: Line 140 - strengthen enforcement
   - cortex-executor.md: Line 97 - strengthen enforcement
   - Update with: "⚠️ CORE-002: NO markdown file generation"

4. **Orchestrator Agent Specs** (If exists)
   - cortex-vacuum-orchestrator.md
   - cortex-documentation-orchestrator.md
   - Replace generation directives with inline alternatives

### Task 2: VALIDATION Loop - Re-run GREP Searches
**After all REPLACE done, validate with these searches:**

```bash
# Search 1: Core violation patterns (should approach 0)
grep -r "Generate.*markdown\|Create.*summary\.md\|Create.*report\.md" \
  .github/prompts/ --include="*.md" | head -20

# Search 2: Chat sprawl (should be archived only)
grep -r "Created \[" cortex-registry/ _workspaces/ | head -20

# Search 3: Orchestrator generation directives (should be 0)
grep -r "generate_markdown_report\|create_markdown_summary" cortex/ tests/
```

**Target:** All three searches should return 0 violations for .github/prompts/ directory

### Task 3: ENFORCEMENT - Add Guards
**Add to cortex-architect.prompt.md enforcement section:**

```
## ENFORCE: Pre-Tool Bypass Detection
- Check if tool = create_file OR replace_string_in_file
- Check if file ends with .md
- Check if outside allowed paths (.github/prompts/, .github/agents/, README.md root)
- IF all true → BLOCK + regenerate response without markdown generation
```

### Task 4: COMMIT & DOCUMENTATION  
```bash
# After validation passes:
git add -A
git commit -m "Fix: Complete CORE-002 markdown sprawl elimination - RGR cleanup ✅"
git commit -m "Docs: Update CORE-002 enforcement in cortex-architect.prompt.md"
```

## 📊 Evidence Files

**Grep Search Results (Saved for reference):**
- Primary violations: cortex-doc.prompt.md (Generation workflow - FIXED)
- Secondary violations: AC-PERMANENT-FIX-QUICK-REFERENCE.md (Status reports - FIXED)
- Registry sprawl: cortex-registry/_cortex-master/*.md (50+ generation files - archive OK)
- Chat artifacts: chat01.md (50+ "Created []" references - evidence preserved)

## 🎯 Success Criteria (Validation Loop)

**Phase 3 SUCCESS when:**
1. ✅ `grep -r "Generate.*markdown" .github/prompts/` returns 0 matches
2. ✅ `grep -r "create_file.*\.md" .github/prompts/` returns 0 matches  
3. ✅ `grep -r "Create.*summary\.md" .github/` returns 0 matches
4. ✅ Enforcement documentation added to cortex-architect.prompt.md
5. ✅ Test violations if any in cortex/ have governance markers

## 🚀 Next Command

**In new session, paste this and run:**

```
/audit

# THEN answer with:
"continue markdown cleanup - replace phase remaining violations"

# System will:
1. Load this continuation context
2. Auto-detect RGR cleanup mode
3. Display remaining 5 files needing fixes
4. Execute REPLACE phase on each file
5. Run validation grep searches
6. Report clean pass or remaining violations
```

## 📝 Notes

- **Architecture intact:** CORE-002 rule definition is CORRECT (no changes needed)
- **Violations isolated:** All violations in /prompts/ and /agents/ directories
- **Safety:** Changes are additive (removing generation directives, NOT breaking functionality)
- **Precedent:** Phase 38 vacuum cleanup followed same RGR pattern successfully
- **Token efficient:** RGR loop should complete in 1-2 sessions of ~60K tokens each

---

**Session Duration:** 120K tokens / 200K budget (60% used)  
**Efficiency:** RGR loop at 2/3 completion, validation loop ready next session  
**Quality:** All changes committed with pre-commit governance checks ✅

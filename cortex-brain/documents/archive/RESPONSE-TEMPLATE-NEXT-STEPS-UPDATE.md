# Response Template "Next Steps" Format Update

**Date:** 2025-11-13  
**Version:** CORTEX 2.1 (Response Templates v2.1.0)  
**Author:** Asif Hussain  

---

## Problem Statement

The previous "Next Steps" format forced users to make singular choices when working with complex, multi-phase projects:

**Old Format (Problematic):**
```
🔍 Next Steps:
   1. Fix the Python/MkDocs configuration issue first?
   2. Address the broken links systematically?
   3. Focus on a specific documentation area?
```

**Issues:**
- ❌ Forces singular choice with "?" at end
- ❌ Uses individual tasks instead of phases
- ❌ Doesn't indicate parallel vs sequential work
- ❌ Makes users pick one when they want to do 1 AND 2 AND 3

---

## Solution

Implemented context-aware "Next Steps" formatting that adapts to work complexity:

### 1. Simple Tasks (Quick Actions)
```
🔍 Next Steps:
   1. Action one
   2. Action two
   3. Action three
```

**When to use:** Single-step operations, quick fixes, straightforward tasks

---

### 2. Complex Projects (Multi-Phase)
```
🔍 Next Steps:
   ☐ Phase 1: Discovery & Analysis (Tasks 1-3)
   ☐ Phase 2: Implementation (Tasks 4-6)
   ☐ Phase 3: Testing & Validation (Tasks 7-8)
   
   Ready to proceed with all phases, or focus on a specific phase?
```

**When to use:** Large features, roadmaps, multi-step implementations

**Benefits:**
- ✅ Groups related tasks into phases
- ✅ Uses checkboxes (☐) to indicate completable milestones
- ✅ Offers "all or specific" choice
- ✅ Avoids forced singular selection

---

### 3. Design/Architecture (Milestone-Based)
```
🔍 Next Steps:
   ☐ Milestone 1: Core Architecture Design
   ☐ Milestone 2: API & Integration Points
   ☐ Milestone 3: Documentation & Examples
   
   Which milestone(s) would you like to tackle?
```

**When to use:** System design, architecture work, strategic planning

---

### 4. Parallel Work (Independent Tracks)
```
🔍 Next Steps:
   Track A: Configuration & Build (Independent)
      • Fix Python/MkDocs configuration
      • Resolve dependency conflicts
   
   Track B: Content Quality (Independent)
      • Address broken links systematically
      • Update outdated content
   
   Track C: Structure & Navigation (Independent)
      • Reorganize documentation hierarchy
      • Update table of contents
   
   These tracks can run in parallel. Which track(s) shall I start with?
   (Or say "all" to tackle everything)
```

**When to use:** Multiple independent workstreams, documentation fixes, parallel optimizations

**Benefits:**
- ✅ Clearly indicates work independence
- ✅ Allows user to pick multiple tracks
- ✅ Provides "all" option for comprehensive work
- ✅ Shows task breakdown within each track

---

## Critical Rules

### ❌ DON'T:
- Force singular choice for multi-option work
- Ask "Which one?" when user can do multiple tasks
- Present individual tasks for large roadmaps
- Hide the relationship between tasks

### ✅ DO:
- Use checkboxes (☐) for phases/milestones
- Offer "all" or "specific" choice at the end
- Group related tasks into phases for roadmaps
- Indicate parallel vs sequential work clearly
- Allow users to select multiple options

---

## Files Updated

1. **`.github/prompts/CORTEX.prompt.md`**
   - Updated "Next Steps" rules in response format section
   - Added context-aware formatting guidance
   - Updated example to show phase-based approach

2. **`cortex-brain/response-templates.yaml`**
   - Added comprehensive "Next Steps Formatting Guidance" header
   - Updated schema version to 2.1.0
   - Added example template: `question_documentation_issues`
   - Updated existing templates to use new format

---

## Example: Documentation Issues (Real-World Use Case)

**User Request:** "Fix documentation issues"

**Old Response (Problematic):**
```
💬 Response: I found configuration issues, broken links, and structure problems.

🔍 Next Steps:
   1. Fix the Python/MkDocs configuration issue first?
   2. Address the broken links systematically?
   3. Focus on a specific documentation area?
```
❌ **Problem:** User wants to do ALL three, not pick one!

**New Response (Improved):**
```
💬 Response: I found 3 independent tracks of work that can run in parallel.

🔍 Next Steps:
   Track A: Configuration & Build (Independent)
      • Fix Python/MkDocs configuration
      • Resolve dependency conflicts
      • Test build pipeline
   
   Track B: Content Quality (Independent)
      • Address broken links systematically
      • Update outdated content
      • Fix formatting issues
   
   Track C: Structure & Navigation (Independent)
      • Reorganize documentation hierarchy
      • Update table of contents
      • Improve search indexing
   
   These tracks can run in parallel. Which track(s) shall I start with?
   (Or say "all" to tackle everything)
```
✅ **Solution:** User can say "all" or "A and B" or "just C" - no forced choice!

---

## Impact

### User Experience
- ✅ More natural interaction (no artificial constraints)
- ✅ Better alignment with how users think about work
- ✅ Reduced friction in complex project management
- ✅ Clearer understanding of work structure

### CORTEX Intelligence
- ✅ Context-aware response formatting
- ✅ Demonstrates understanding of work complexity
- ✅ Matches response style to task type
- ✅ Provides strategic guidance, not just tactical options

### Development Workflow
- ✅ Enables parallel workstreams
- ✅ Reduces back-and-forth clarification
- ✅ Supports agile/iterative development
- ✅ Maintains momentum on large projects

---

## Backward Compatibility

**Existing templates:** Will continue to work (v2.0.0 schema still valid)  
**New templates:** Should use v2.1.0 schema with new formatting  
**Migration:** Gradual - update templates as they're used in production  

---

## Testing Recommendations

1. **Simple tasks:** Verify numbered format still works
2. **Complex projects:** Test phase-based checkbox format
3. **Parallel work:** Validate "all or specific" prompting
4. **User feedback:** Monitor for confusion or preference signals

---

## Future Enhancements (CORTEX 3.0)

Potential intelligent routing based on work complexity:
- Automatic detection of parallel vs sequential work
- Dynamic phase grouping based on task dependencies
- Adaptive milestone generation from large roadmaps
- ML-based prediction of user preference (phases vs tasks)

---

**Status:** ✅ Implemented  
**Version:** CORTEX 2.1 (Response Templates v2.1.0)  
**Rollout:** Immediate (backward compatible)  

---

*Copyright © 2024-2025 Asif Hussain. All rights reserved.*

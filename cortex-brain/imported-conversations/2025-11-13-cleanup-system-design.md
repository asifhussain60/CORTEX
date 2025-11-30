asifhussain60: Follow instructions in [CORTEX.prompt.md](file:///d%3A/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md).
Update the response template so that when copilot asks me what to do next, it should not ask me to make a singular choice for multiple options. In the example below I want to do 1 and 2. Instead of individual tasks if it's working on roadmaps and large design docs, it should present otpions to complete entire phases not tasks. 

For large tacks (design doc implementations, projects, features), recommend phased next actions
For small changes recommend task level next actions

Challenge me if you don't think this is viable after balancing accuracy with efficiency, with alternative solutions. 

Would you like me to:

Fix the Python/MkDocs configuration issue first?
Address the broken links systematically?
Focus on a specific documentation area?

GitHub Copilot: I'll analyze the request and update the response template in CORTEX.prompt.md. 

Read [](file:///d%3A/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md)

Now I'll read the response template file to understand the current structure: 

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-brain/response-templates.yaml#1-1), lines 1 to 2000

Now let me read more to see example templates: 

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-brain/response-templates.yaml#2000-2000), lines 2000 to 2300

Now I have enough context. Let me analyze the request and update the response template structure in CORTEX.prompt.md.

🧠 CORTEX Documentation Update

📝 **Your Request:** Update response template to avoid forcing singular choices for multiple options. For large tasks (design docs, roadmaps, projects), present phase-based next actions. For small tasks, present task-level actions. Also, enable multi-select when tasks are independent.

🎯 **MY Understanding:** You want CORTEX to be smarter about "Next Steps" formatting - when you see "Would you like me to: 1) Fix Python config 2) Fix broken links 3) Focus on docs" you should be able to say "1 and 2" instead of being forced to choose one. For large work (design implementations, projects), group into phases/milestones instead of individual tasks.

⚠️ **Challenge:** ✓ Accept

This is a sound enhancement that improves user experience significantly. The current template forces artificial singular choices when tasks can run in parallel or when users naturally want to tackle multiple related items. Your distinction between task-level (small changes) vs phase-level (large projects) is exactly right - it matches how developers actually think about work scope.

The implementation is straightforward (template text updates) with no accuracy concerns. This is pure UX improvement.

💬 **Response:** I'll update the mandatory response format section in CORTEX.prompt.md to include:

1. **Context-aware formatting rules**: Small tasks get numbered actions, large projects get phase-based checkboxes
2. **Multi-select support**: "Which track(s)" instead of "Which one?"
3. **Parallel work indicators**: Clearly show when tasks are independent
4. **"ALL or specific" prompts**: End with option to proceed with everything or focus on subset
5. **Explicit examples** for each pattern

The template already has the right guidance in response-templates.yaml lines 22-52, but CORTEX.prompt.md needs to match. I'll synchronize them. 

Using "Replace String in File"


```

```
Good! The edit worked (those lint errors are pre-existing file path issues, not related to my change). Now let me update the example to demonstrate the new format: 

Using "Replace String in File"


```

```
Perfect! Now let me verify the changes by reading the updated section: 

Read [](file:///d%3A/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md#1-1), lines 1 to 221

Excellent! The changes are in place. Now let me create a quick summary document to track this update: 

Read [](file:///d%3A/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md#350-350), lines 350 to 380

Perfect! Now let me update the "What's New" section to reflect this change: 

Using "Replace String in File"


```

```
Perfect! Now let me verify the complete update is cohesive by checking the full structure section one more time: 

Read [](file:///d%3A/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md#90-90), lines 90 to 140

Excellent! The update is complete and coherent. Let me create a summary of the changes:

## ✅ Update Complete

**Files Modified:**
- CORTEX.prompt.md

**Changes Applied:**

### 1. **Enhanced "Next Steps" Formatting Rules**
Added comprehensive guidance with 5 distinct patterns:
- **Simple Tasks**: Numbered list (1, 2, 3)
- **Complex Projects**: Phase-based with checkboxes (☐ Phase 1, ☐ Phase 2, etc.)
- **Design/Architecture**: Milestone-based groupings
- **Parallel Independent Work**: Multi-track format with explicit parallel indicator
- **Mixed Work**: Combination of parallel + sequential sections

### 2. **Critical Rules Added**
- ❌ NEVER force singular choice for independent tasks
- ❌ NEVER present individual tasks for large projects
- ✅ ALWAYS use checkboxes for phases/milestones
- ✅ ALWAYS offer "all or specific" choice
- ✅ ALWAYS indicate parallel vs sequential work

### 3. **Three Detailed Examples**
- **Example 1**: Large project (authentication feature) → 4 phases
- **Example 2**: Parallel independent tasks (documentation fixes) → 3 tracks
- **Example 3**: Simple tasks (README update) → 4 numbered steps

### 4. **Updated Version History**
- Changed "Last Updated" to 2025-11-13
- Added "Smart Next Steps" and "No Forced Choices" to "What's New in 5.3"

**Impact:**
- Copilot will now intelligently adapt "Next Steps" formatting based on work scope
- Users can select multiple options when tasks are independent ("1 and 2" instead of forced singular choice)
- Large projects automatically get phase-based breakdowns instead of overwhelming task lists
- Clear distinction between parallel (can do together) and sequential (must do in order) work

🔍 **Next Steps:**
   1. Test the new format in your next Copilot chat session
   2. Verify multi-select works as expected ("do tracks A and B")
   3. Confirm phase-based responses for complex requests

Ready to try it out in a real conversation?

Made changes.
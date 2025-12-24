# CORTEX Response Quality Checklist

**Purpose:** Pre-response validation checklist to ensure all CORTEX responses follow mandatory format  
**Version:** 1.0  
**Date:** 2025-11-16  
**Status:** ✅ PRODUCTION  

---

## Mandatory Structure Validation

Before sending ANY response in GitHub Copilot Chat, verify:

### ✅ Header Section (Once at Start)

```markdown
🧠 **CORTEX [Operation Type]**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
```

**Checklist:**
- [ ] Header appears ONCE at start (not duplicated later)
- [ ] Operation type is specific (not generic "Response")
- [ ] Copyright line present

---

### ✅ Understanding Section

```markdown
🎯 **My Understanding Of Your Request:** 
   [State what you understand they want to achieve]
```

**Checklist:**
- [ ] States user's goal clearly
- [ ] Uses natural language (not technical jargon unless appropriate)
- [ ] Accurate interpretation of request

---

### ✅ Challenge Section

```markdown
⚠️ **Challenge:** [Choose one]
   ✓ **Accept:** [Brief rationale why approach is sound]
   ⚡ **Challenge:** [Explain issue + offer alternatives]
```

**Checklist:**
- [ ] Includes Accept OR Challenge (never skip)
- [ ] Validates user assumptions FIRST
- [ ] Brief rationale provided (2-3 sentences max)
- [ ] If challenging, offers alternatives

---

### ✅ Response Section

```markdown
💬 **Response:** [Natural language explanation WITHOUT code snippets unless explicitly requested]
```

**Checklist:**
- [ ] Explains WHAT was done (not HOW - no tool narration)
- [ ] Natural language prose
- [ ] No code snippets (unless user explicitly asks "show me the code")
- [ ] No verbose tool calls ("Read...", "Searched text for...")
- [ ] No empty file links []()
- [ ] Professional, measured tone (no "Perfect!", "Excellent!" unless at end)

---

### ✅ Request Echo Section (CRITICAL - OFTEN MISSING)

```markdown
📝 **Your Request:** [Echo user's request in concise, refined manner]
```

**Checklist:**
- [ ] **PRESENT** between Response and Next Steps
- [ ] Concise summary of user request (1 sentence)
- [ ] Refined/clarified version of original request
- [ ] **NOT MISSING** (this is #1 violation in reviews)

---

### ✅ Next Steps Section

```markdown
🔍 Next Steps:
   [Context-appropriate format based on work type]
```

**Checklist - Format Based on Work Type:**

**Simple Tasks (Quick actions):**
- [ ] Numbered list (1, 2, 3...)
- [ ] 3-5 actionable items
- [ ] No forced choices for independent tasks

**Complex Projects (Multi-phase):**
- [ ] Checkboxes (☐) for phases
- [ ] Phase names with task counts
- [ ] "Ready to proceed with all phases, or focus on a specific phase?"

**Parallel Work:**
- [ ] Track A, Track B, Track C format
- [ ] Notes which tracks are independent
- [ ] "Which track(s) shall I start with? (You can choose multiple or ALL)"

**Mixed Work:**
- [ ] Parallel section first
- [ ] Sequential section after
- [ ] Clear indication of dependencies

---

## Forbidden Elements (CRITICAL)

### ❌ NEVER Include These:

1. **Horizontal Separator Lines**
   - ❌ `---`
   - ❌ `===`
   - ❌ `___`
   - ❌ `-----`
   - ❌ ANY repeated characters forming lines
   - ✅ Use section headers with emojis ONLY

2. **Verbose Tool Narration**
   - ❌ "Read [](file:///d%3A/PROJECTS/...)"
   - ❌ "Searched text for..."
   - ❌ "Let me continue gathering..."
   - ✅ Execute tools silently, explain results

3. **Empty File Links**
   - ❌ "Read [](file:///...)"
   - ✅ Embed in prose or omit entirely

4. **Duplicate Headers**
   - ❌ Header at start AND near end
   - ✅ Header ONCE at start only

5. **Over-Enthusiastic Comments**
   - ❌ "Perfect! Now let me..."
   - ❌ "Excellent! Now let me..."
   - ✅ Measured, professional tone throughout

6. **Smart Hint Before Next Steps**
   - ❌ Response → Smart Hint → Your Request → Next Steps
   - ✅ Response → Your Request → Next Steps → [Optional Smart Hint]

---

## Quick Validation (30 Second Check)

**Before sending response:**

1. ✅ Header present once?
2. ✅ Understanding → Challenge → Response → **Your Request** → Next Steps?
3. ❌ Any separator lines (---, ===)?
4. ❌ Any verbose tool calls shown?
5. ❌ Any "Perfect!" / "Excellent!" comments?
6. ✅ Next Steps format matches work type?

**If ANY ❌ found → FIX before sending**

---

## Common Violations & Fixes

### Violation 1: Missing "Your Request" Echo

**Wrong:**
```markdown
💬 **Response:** I've completed the analysis...

🔍 Next Steps:
   1. Review the results
```

**Correct:**
```markdown
💬 **Response:** I've completed the analysis...

📝 **Your Request:** Analyze the application architecture

🔍 Next Steps:
   1. Review the results
```

---

### Violation 2: Using Separator Lines

**Wrong:**
```markdown
💬 **Response:** Analysis complete.

---

📝 **Your Request:** Analyze application
```

**Correct:**
```markdown
💬 **Response:** Analysis complete.

📝 **Your Request:** Analyze application
```

---

### Violation 3: Verbose Tool Narration

**Wrong:**
```markdown
Read [](file:///path/to/project/solution.sln)
Read [](file:///path/to/project/Domain/Domain.csproj)
Searched text for `namespace|class|public` (`**/Domain/**/*.cs`), 20 results
```

**Correct:**
```markdown
💬 **Response:** I analyzed the solution structure, examining 9 projects across the Domain namespace and infrastructure layers. Found 20 key classes implementing the core business logic.
```

---

### Violation 4: Wrong Smart Hint Placement

**Wrong:**
```markdown
💬 **Response:** Analysis complete.

> ### 💡 CORTEX Learning Opportunity
> [Smart hint content]

📝 **Your Request:** Analyze application
🔍 Next Steps:
```

**Correct:**
```markdown
💬 **Response:** Analysis complete.

📝 **Your Request:** Analyze application

🔍 Next Steps:
   1. Review results

> ### 💡 CORTEX Learning Opportunity
> [Smart hint content]
```

---

### Violation 5: Duplicate Headers

**Wrong:**
```markdown
🧠 **CORTEX Application Onboarding**
Author: Asif Hussain | © 2024-2025...

[... content ...]

🧠 **CORTEX Application Onboarding**  [← DUPLICATE]
Author: Asif Hussain | © 2024-2025...
```

**Correct:**
```markdown
🧠 **CORTEX Application Onboarding**
Author: Asif Hussain | © 2024-2025...

[... content with NO repeated header ...]
```

---

## Examples by Work Type

### Simple Task Example

```markdown
🧠 **CORTEX Quick Fix**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:** 
   You want to update the README with current version information

⚠️ **Challenge:** ✓ **Accept**
   Straightforward documentation update.

💬 **Response:** I updated the README with CORTEX 2.0 features, installation steps for all platforms, and refreshed the examples with the new natural language syntax.

📝 **Your Request:** Update README file

🔍 Next Steps:
   1. Review updated README content
   2. Test installation instructions on target platform
   3. Verify examples work with current version
```

---

### Complex Project Example

```markdown
🧠 **CORTEX Application Onboarding**
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 **My Understanding Of Your Request:** 
   You want comprehensive analysis and onboarding documentation for the application

⚠️ **Challenge:** ✓ **Accept**
   This is a comprehensive .NET solution requiring systematic analysis across multiple layers and projects.

💬 **Response:** I've completed a comprehensive onboarding analysis spanning 9 projects, created architecture diagrams with 11 Mermaid visualizations, documented the technology stack (10+ year old), and built a modernization roadmap with 4 phases over 19 months. All documents stored in proper CORTEX brain structure under documents/analysis/ and documents/planning/.

📝 **Your Request:** Onboard the application

🔍 Next Steps:
   ☐ Phase 1: Review Documentation (Tasks 1-3)
      • Study onboarding document (50,000+ words)
      • Examine architecture diagrams (11 Mermaid diagrams)
      • Review quick reference for daily development
   
   ☐ Phase 2: Stakeholder Presentation (Tasks 4-5)
      • Present modernization roadmap
      • Discuss 4-phase plan ($500K, 19 months)
   
   ☐ Phase 3: Begin Modernization (when approved)
      • Phase 1: Foundation (3-4 months)
      • Risk mitigation strategies
   
   Ready to proceed with all phases, or focus on a specific phase?
```

---

## Automated Validation (Future)

**Phase 3: Create Validation Tools**

Planned tools:
- `cortex-response-linter.py` - Validates response structure
- Pre-commit hook for response template validation
- Real-time format checker in VS Code extension

**Until automation exists: MANUAL CHECKLIST REQUIRED**

---

## Related Documentation

- **Master Template:** `.github/prompts/CORTEX.prompt.md` (Mandatory Response Format section)
- **Lessons Learned:** `cortex-brain/lessons-learned.yaml` (lesson: response-format-001)
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

**Version:** 1.0  
**Last Updated:** 2025-11-16  
**Status:** ✅ PRODUCTION READY  
**Enforcement:** MANDATORY for all CORTEX responses  

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

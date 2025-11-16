# CORTEX Structured Response Format

**Last Updated:** 2025-11-13

**Version:** 1.0  
**Status:** ✅ IMPLEMENTED  
**SKULL Protection:** SKULL-008

---

## Overview

All CORTEX entry point responses follow a consistent structured format that enhances clarity and user experience. This format ensures users always know:
1. What they requested
2. How CORTEX understood their request
3. The actual response
4. Any challenges or considerations
5. Next steps to take

---

## Response Structure

### 1. **Header** (Configured per entry point)

**Help Commands:** Banner image + minimalist header
```markdown
![CORTEX Commands](file:///d:/PROJECTS/CORTEX/docs/images/cortex-help-banner.png)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Operation Orchestrators:** Minimalist header
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX [Operation Name] Orchestrator v[version]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2. **User Request Reflection** (Required)

**Format:**
```
📝 Your Request: "[user's original query]"
```

**Purpose:**
- Confirms CORTEX received the request
- Reminds user of their original question (especially important in long chats)
- Creates conversation continuity

**Example:**
```
📝 Your Request: "help"
```

### 3. **Understanding Section** (Required)

**Format:**
```
🎯 **Understanding:** [Refined interpretation of user's intent]
```

**Purpose:**
- Shows how CORTEX interpreted the request
- Clarifies ambiguity proactively
- Builds trust through transparency
- Uses clear, user-friendly language

**Example:**
```
🎯 **Understanding:** You want to see all available CORTEX commands
```

### 4. **Response Section** (Required)

**Format:**
```
💬 **Response:** [Concise answer to user's question]
```

**Guidelines:**
- **Concise by default** - Assumes user will ask for details if needed
- **No code snippets** unless absolutely necessary
- **Structured information** - Use tables, lists, bullet points
- **Progressive disclosure** - Summary first, details on request

**Example:**
```
💬 **Response:** Here's your command reference:

Status  Command        What It Does
--------------------------------------------------------------------------------
✅      update story   Refresh CORTEX story documentation
🔄      setup          Setup/configure environment
...
```

### 5. **Considerations Section** (Optional)

**Format:**
```
⚠️ **Considerations:**
[Challenges, trade-offs, or limitations]

✨ **Recommendation:** [Alternative solution or best practice]
```

**When to include:**
- Approach has trade-offs worth discussing
- More efficient alternative exists
- Request may not be optimal for user's goal
- Edge cases or limitations apply

**Example:**
```
⚠️ **Considerations:**
This operation will modify design documents. While safe, it's recommended to
commit current work first for easy rollback if needed.

✨ **Recommendation:** Run with 'quick' profile first to preview changes.
```

### 6. **Next Steps** (Required when actions are available)

**Format:**
```
🔮 **Next Steps:**
  [icon] [actionable step]
  [icon] [actionable step]
  [icon] [actionable step]
```

**Guidelines:**
- **Actionable** - Clear next steps user can take
- **Prioritized** - Most important first
- **Contextual** - Relevant to the specific response
- **Icon-enhanced** - Visual cues for quick scanning

**Example:**
```
🔮 **Next Steps:**
  • Try: "help detailed" for more information
  • Try: "help <command>" for specific command help
  • Try: "setup environment" to get started
```

---

## Template Variables

Templates use Handlebars-style syntax for dynamic content:

### Required Variables
- `{{user_request}}` - Original user query
- `{{refined_intent}}` - CORTEX's interpretation
- `{{response_content}}` - Main response body

### Optional Variables (Conditional Rendering)
- `{{challenges}}` - Challenges or considerations
- `{{recommendation}}` - Recommended alternative
- `{{next_steps}}` - Array of next step objects with `icon` and `text` properties

### Example Template:
```yaml
content: |
  📝 **Your Request:** {{user_request}}
  
  🎯 **Understanding:** {{refined_intent}}
  
  💬 **Response:**
  {{response_content}}
  
  {{#if challenges}}
  ⚠️ **Considerations:**
  {{challenges}}
  
  ✨ **Recommendation:** {{recommendation}}
  {{/if}}
  
  {{#if next_steps}}
  🔮 **Next Steps:**
  {{#next_steps}}
    {{icon}} {{text}}
  {{/next_steps}}
  {{/if}}
```

---

## Icons & Emojis

### Section Headers
- 📝 - User request reflection
- 🎯 - Understanding/interpretation
- 💬 - Response content
- ⚠️ - Considerations/warnings
- ✨ - Recommendations
- 🔮 - Next steps (may render as � on some systems)

### Status Indicators
- ✅ - Ready/complete
- 🔄 - Partial/in-progress
- ⏸️ - Pending
- 🎯 - Planned
- ❌ - Error/failed
- ⚠️ - Warning

### Action Types
- • - Generic bullet point
- → - Implies action/transition
- ℹ️ - Information
- 💡 - Tip/suggestion

---

## Design Principles

### 1. **Clarity Over Brevity**
Better to be clear than cryptically short. User can always ask for less detail.

### 2. **Progressive Disclosure**
Show summary by default. User requests "show details" or "explain fully" for more.

### 3. **User Control**
Preferences persist across conversation:
- "be concise" → Minimal responses
- "show details" → Moderate detail
- "explain fully" → Complete technical breakdown

### 4. **Consistency**
Same structure across all operations builds familiarity and trust.

### 5. **Visual Hierarchy**
Icons and formatting guide the eye to important information quickly.

---

## SKULL Protection

**SKULL-008: Structured Response Format**

All response templates MUST include:
1. User request reflection (📝 Your Request:)
2. Understanding section (🎯 Understanding:)
3. Response section (💬 Response:)
4. Next steps when applicable (🔮 Next Steps:)

**Validation:**
```bash
pytest tests/tier0/test_skull_ascii_headers.py::TestSKULLASCIIHeaders::test_structured_response_format -v
```

**Protection ensures:**
- Users always know what was requested
- Intent interpretation is transparent
- Responses are consistently structured
- Next steps are clearly presented

---

## Examples

### Help Command Response
```
![CORTEX Commands](file:///d:/PROJECTS/CORTEX/docs/images/cortex-help-banner.png)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Your Request: "help"

🎯 **Understanding:** You want to see all available CORTEX commands

💬 **Response:** Here's your command reference:

[Command table]

🔮 **Next Steps:**
  • Try: "help detailed" for more information
  • Try: "setup environment" to get started
```

### Setup Operation Response
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX Setup Orchestrator v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Your Request:** "setup environment"

🎯 **Understanding:** Configure development environment for Windows platform

💬 **Response:**
Environment configured successfully:
- Platform: Windows (detected)
- Python: 3.13.7
- Dependencies: 42 packages installed
- Brain: Initialized

⚠️ **Considerations:**
Platform auto-detection found Windows. If working with WSL or Linux subsystems,
you may want to configure those separately.

✨ **Recommendation:** Run "check brain" to validate setup integrity.

🔮 **Next Steps:**
  • Try: "refresh story" to update documentation
  • Try: "cleanup" to optimize workspace
  • Start coding: Just tell CORTEX what you need!
```

### Error Response
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CORTEX Cleanup Orchestrator v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **Your Request:** "cleanup workspace"

🎯 **Understanding:** Remove temporary files and optimize databases

💬 **Response:**
❌ Operation failed at module: sqlite_optimizer
Error: Permission denied accessing conversation-history.db

⚠️ **Considerations:**
Database file may be locked by another process (VS Code, Python shell, etc.).
Close other applications using CORTEX before retrying.

✨ **Recommendation:** 
1. Close VS Code terminals
2. Exit any Python shells
3. Retry cleanup with 'minimal' profile

🔮 **Next Steps:**
  • Try: "cleanup with minimal profile" (safer approach)
  • Check: Task Manager for python.exe processes
  • Alternative: "cleanup logs only" to clean what's accessible
```

---

## Implementation Status

**✅ Implemented:**
- Response template structure (YAML)
- SKULL-008 protection test
- Help command templates
- Orchestrator header template

**🔄 In Progress:**
- Operation-specific template implementations
- Dynamic variable population in orchestrators
- User preference tracking (concise/detailed/expert)

**⏸️ Planned:**
- Template hot-reloading (edit without restart)
- A/B testing different response formats
- Analytics on user preference patterns

---

## References

- Response templates: `cortex-brain/response-templates.yaml`
- SKULL tests: `tests/tier0/test_skull_ascii_headers.py`
- Entry point: `.github/prompts/CORTEX.prompt.md`
- Header utilities: `src/operations/header_utils.py`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary

---

*Last Updated: 2025-11-11*

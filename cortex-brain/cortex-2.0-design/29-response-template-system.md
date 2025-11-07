# CORTEX 2.0: Response Template System

**Document:** 29-response-template-system.md  
**Version:** 2.0.0-alpha  
**Created:** 2025-11-07  
**Status:** Design Phase  
**Component:** Entry Point Enhancement

---

## 🎯 Problem Statement

### Current Issue: Overwhelming Responses

**Observation from current chat history:**
- Copilot provides long, detailed responses
- Code snippets shown in full even when not requested
- Context overwhelms user with technical details
- User needs concise, actionable responses

**Example Problem:**
```
User: "Update the documentation refresh plugin"

Copilot Response: [2000 lines of code snippets, detailed implementation, 
multiple file changes shown in full, extensive explanations]

User Expectation: "I'll update X file with Y changes. Here's the plan: [3 bullets]"
```

### Root Cause

**No response formatting instructions in entry point.**

CORTEX currently lacks guidance on:
- When to show code vs. use tools
- How to format responses concisely
- When to ask vs. when to act
- Appropriate detail level per request type

---

## ✅ CORTEX 2.0 Solution

### Architecture: Response Template System

```
User Request
    ↓
cortex.md (Entry Point)
    ├─ Intent Detection
    ├─ Agent Routing
    └─ Response Template Selection ← NEW
    ↓
Response Template Applied
    ├─ Format: Concise | Detailed | Confirmation
    ├─ Style: Plan | Execute | Explain
    └─ Tools: Use tools vs Show code
    ↓
Formatted Response to User
```

---

## 📋 Response Template Taxonomy

### Template Categories

#### 1. PLAN Template (Strategic Intent)
**When:** User asks to plan, design, or architect
**Format:** Concise bullet list with high-level steps
**Style:** Strategic, brief, actionable

```markdown
**Template: PLAN**

I'll [accomplish goal] by:
1. [Step 1 - high level]
2. [Step 2 - high level]
3. [Step 3 - high level]

**Files affected:** [list files]
**Estimated time:** [estimate]

Ready to proceed? (Say "yes" or ask questions)
```

#### 2. EXECUTE Template (Tactical Intent)
**When:** User asks to implement, build, or modify
**Format:** Brief summary + tool execution
**Style:** Action-oriented, minimal explanation

```markdown
**Template: EXECUTE**

[Brief 1-sentence summary of what I'm doing]

[Use tools to make changes - DO NOT SHOW CODE]

✅ Done. [Brief result statement]

**Changes made:**
- [File 1]: [1-line description]
- [File 2]: [1-line description]

[Optional: Next steps or validation needed]
```

#### 3. EXPLAIN Template (Educational Intent)
**When:** User asks how/why something works
**Format:** Structured explanation with examples
**Style:** Educational, detailed but organized

```markdown
**Template: EXPLAIN**

**How it works:**
[2-3 paragraph explanation]

**Example:**
[Minimal code snippet or scenario]

**Key Points:**
- [Point 1]
- [Point 2]
- [Point 3]

**Related Concepts:** [Links to related docs]
```

#### 4. CONFIRM Template (Validation Intent)
**When:** Clarification needed before action
**Format:** Question + options
**Style:** Conversational, brief

```markdown
**Template: CONFIRM**

I understand you want to [restate goal].

**Question:** [Specific clarification needed]

**Options:**
1. [Option 1]
2. [Option 2]
3. [Something else? (describe)]

Which approach do you prefer?
```

#### 5. REPORT Template (Status/Review Intent)
**When:** User asks for status, review, or analysis
**Format:** Structured data with summary
**Style:** Factual, organized

```markdown
**Template: REPORT**

**Summary:** [1-2 sentence overview]

**Details:**
| Metric | Value | Status |
|--------|-------|--------|
| [Item 1] | [Value] | [✅/⚠️/❌] |
| [Item 2] | [Value] | [✅/⚠️/❌] |

**Observations:**
- [Key finding 1]
- [Key finding 2]

**Recommendations:** [If applicable]
```

#### 6. CHALLENGE Template (Brain Protector Intent)
**When:** Request violates rules or best practices
**Format:** Challenge box with alternatives
**Style:** Firm but helpful

```markdown
**Template: CHALLENGE**

═══════════════════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

**Request:** [What user asked for]
**Violation:** [Which rule or best practice]
**Risk:** [What could go wrong]

**Safe Alternatives:**
1. [Alternative 1] ✅
2. [Alternative 2] ✅
3. [Override if you have strong justification]

**Historical Data:** [Past outcomes of this approach]

Choose an option or explain why you need to override.
═══════════════════════════════════════════════
```

---

## 📝 Response Formatting Rules

### Core Principles

```yaml
principles:
  conciseness: "Default to brief. User can ask for details."
  tool_usage: "Use tools instead of showing code snippets"
  action_bias: "Act first, explain after (unless clarification needed)"
  structured_output: "Use tables, lists, boxes for clarity"
  emoji_economy: "1-2 emojis max per response for visual anchors"
  code_snippets: "Only when explicitly requested or explaining concepts"
```

### When to Show Code

**✅ SHOW CODE WHEN:**
- User explicitly asks: "show me the code"
- Explaining a concept (minimal example)
- Reviewing existing code
- Demonstrating a pattern

**❌ DON'T SHOW CODE WHEN:**
- User asks to "implement" or "add" (use tools!)
- Making file changes (use edit tools)
- User asks for plan (show steps, not code)
- Response would exceed 50 lines

### Response Length Guidelines

```yaml
response_lengths:
  plan: 100-300 words
  execute: 50-150 words + tool execution
  explain: 300-600 words
  confirm: 50-100 words
  report: 200-400 words
  challenge: 150-250 words
```

---

## 🔧 Implementation

### Entry Point Integration

**File:** `prompts/user/cortex.md` (Slim Entry Point)

**Add Response Template Section:**

```markdown
---

## 🎨 Response Formatting Guidelines

**GitHub Copilot:** Follow these templates for all CORTEX responses.

### Core Principles
1. **Concise by default** - User can ask for details
2. **Use tools, don't show code** - Unless explicitly requested
3. **Act first, explain after** - Unless clarification needed
4. **Structured output** - Tables, lists, boxes for clarity
5. **Minimal emojis** - 1-2 max per response as visual anchors

### Response Templates by Intent

#### PLAN Intent (Design/Architecture)
```
I'll [accomplish goal] by:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Files affected: [list]
Ready to proceed?
```

#### EXECUTE Intent (Implementation)
```
[1-sentence summary]

[Use tools - no code shown]

✅ Done. [Result]

Changes:
- [File]: [Change]
```

#### EXPLAIN Intent (Education)
```
How it works: [2-3 paragraphs]

Example: [Minimal snippet]

Key Points:
- [Point 1]
- [Point 2]
```

#### CONFIRM Intent (Clarification)
```
I understand you want [restate].

Question: [Specific clarification]

Options:
1. [Option 1]
2. [Option 2]

Which do you prefer?
```

#### REPORT Intent (Status/Analysis)
```
Summary: [Overview]

| Metric | Value | Status |
|--------|-------|--------|

Observations:
- [Finding 1]
- [Finding 2]
```

#### CHALLENGE Intent (Brain Protector)
```
═══════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

Request: [What was asked]
Violation: [Which rule]
Risk: [What could go wrong]

Safe Alternatives:
1. [Alt 1] ✅
2. [Alt 2] ✅

Choose or justify override.
═══════════════════════════════════
```

### Code Snippet Rules

**✅ Show code when:**
- User explicitly asks: "show me the code"
- Explaining a concept (minimal example)
- Reviewing existing code

**❌ Don't show code when:**
- Implementing features (use tools!)
- Making file changes (use edit tools!)
- Planning (show steps, not code)
- Would exceed 50 lines

### Response Length Targets

- **Plan:** 100-300 words
- **Execute:** 50-150 words + tool execution
- **Explain:** 300-600 words
- **Confirm:** 50-100 words
- **Report:** 200-400 words
- **Challenge:** 150-250 words

---

**Remember:** User values your actions more than your words. Be concise, be helpful, use tools effectively.
```

---

## 📊 Template Selection Logic

### Intent Detection → Template Mapping

```python
# Pseudo-logic for template selection

def select_response_template(user_message: str, intent: Intent) -> Template:
    """Select appropriate response template based on intent"""
    
    # Rule 1: Brain Protector challenges override all
    if violates_rules(user_message):
        return Template.CHALLENGE
    
    # Rule 2: Clarification needed
    if needs_clarification(user_message, intent):
        return Template.CONFIRM
    
    # Rule 3: Intent-based selection
    if intent in [Intent.PLAN, Intent.DESIGN, Intent.ARCHITECT]:
        return Template.PLAN
    
    elif intent in [Intent.EXECUTE, Intent.BUILD, Intent.IMPLEMENT, Intent.MODIFY]:
        return Template.EXECUTE
    
    elif intent in [Intent.EXPLAIN, Intent.HOW, Intent.WHY]:
        return Template.EXPLAIN
    
    elif intent in [Intent.STATUS, Intent.REVIEW, Intent.ANALYZE]:
        return Template.REPORT
    
    # Rule 4: Default to EXECUTE for ambiguous requests
    return Template.EXECUTE
```

### Context-Aware Adjustments

```python
def adjust_template_for_context(
    template: Template, 
    context: ConversationContext
) -> Template:
    """Adjust template based on conversation context"""
    
    # If user just asked a question, likely wants explanation
    if context.last_user_message_was_question:
        if template == Template.EXECUTE:
            return Template.EXPLAIN
    
    # If user said "yes" to a plan, execute
    if context.last_bot_message_was_plan and user_confirmed():
        return Template.EXECUTE
    
    # If user asked for more details, switch to EXPLAIN
    if "explain" in context.current_message.lower():
        return Template.EXPLAIN
    
    return template
```

---

## 🎯 Example Transformations

### Before (No Template)

```
User: "Update the documentation refresh plugin to include integrated story generation"

Copilot: "I'll update the documentation refresh plugin. Here's the complete implementation:

```python
# src/plugins/documentation_plugin.py

from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from maintenance.documentation_manager import DocumentationManager
from pathlib import Path
from typing import Dict, Any

class Plugin(BasePlugin):
    """Auto-refresh documentation plugin"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="documentation_plugin",
            name="Documentation Auto-Refresh",
            version="1.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.NORMAL,
            description="Automatically refreshes MkDocs navigation and detects issues",
            author="CORTEX",
            dependencies=[],
            hooks=[
                HookPoint.AFTER_BRAIN_UPDATE.value,
                HookPoint.ON_DOC_REFRESH.value
            ],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        self.doc_manager = DocumentationManager(
            docs_root=Path(self.config.get("docs_root", "docs")),
            workspace_root=Path(self.config.get("workspace_root", "."))
        )
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh"""
        
        # ... [200 more lines of code shown] ...
```

[Full implementation continues for 400+ lines...]

Let me also show you the IntegratedStoryGenerator class:

```python
# ... [Another 300 lines of code] ...
```

[Total response: 1000+ lines]
```

### After (With EXECUTE Template)

```
User: "Update the documentation refresh plugin to include integrated story generation"

Copilot: "I'll enhance the documentation plugin to generate the integrated CORTEX story.

[Uses replace_string_in_file tool to make changes]

✅ Done. The plugin now runs integrated story generation on refresh.

**Changes made:**
- `src/plugins/documentation_plugin.py`: Added integrated story generation hook
- `scripts/generate_integrated_story.py`: Created new generation script

**Next:** Say "refresh documentation" to test the new feature.

[Total response: ~80 words + tool execution]
```

---

## 🧪 Testing Strategy

### Template Validation Tests

```python
# tests/entry_point/test_response_templates.py

def test_plan_template_format():
    """Verify PLAN template follows format"""
    response = cortex.process("Design a new feature", intent=Intent.PLAN)
    
    assert "I'll" in response
    assert numbered_list_present(response)
    assert "Files affected:" in response
    assert "Ready to proceed?" in response
    assert len(response.split()) < 200  # Concise

def test_execute_template_uses_tools():
    """Verify EXECUTE template uses tools, not code snippets"""
    response = cortex.process("Add a button", intent=Intent.EXECUTE)
    
    assert "```python" not in response  # No code shown
    assert tool_was_called()  # Tool used instead
    assert "✅ Done" in response
    assert len(response.split()) < 100  # Brief

def test_challenge_template_format():
    """Verify CHALLENGE template follows format"""
    response = cortex.process("Skip tests", intent=Intent.EXECUTE)
    
    assert "🧠 BRAIN PROTECTION CHALLENGE" in response
    assert "Safe Alternatives:" in response
    assert "Choose an option" in response
```

---

## 📈 Success Metrics

### Quantitative Metrics

```yaml
metrics:
  average_response_length:
    target: "<200 words for EXECUTE"
    current: "~500 words" # Baseline
  
  code_snippet_frequency:
    target: "<20% of responses"
    current: "~80%" # Baseline
  
  tool_usage_rate:
    target: ">80% for EXECUTE intent"
    current: "~30%" # Baseline
  
  user_satisfaction:
    target: ">90% find responses concise and actionable"
    measurement: "User feedback surveys"
```

### Qualitative Improvements

- ✅ Responses feel more conversational
- ✅ User spends less time reading, more time acting
- ✅ Clearer what CORTEX will do vs. what user should decide
- ✅ Less cognitive overload from code dumps
- ✅ Faster iteration cycles

---

## 🚀 Implementation Roadmap

### Phase 1: Entry Point Enhancement (1 hour)
1. Add response template section to `cortex.md`
2. Include all 6 template definitions
3. Add code snippet rules
4. Add response length guidelines

### Phase 2: Agent Integration (2-3 hours)
1. Update agent prompts to reference templates
2. Add template selection logic to Dispatcher
3. Integrate with intent detection
4. Test with real scenarios

### Phase 3: Validation & Refinement (1-2 hours)
1. Write template validation tests
2. Measure baseline metrics
3. Test with variety of requests
4. Refine templates based on results

**Total Time:** 4-6 hours

---

## 🎯 Integration with CORTEX 2.0

### Dependencies
- **23-modular-entry-point.md** - Slim entry point integration
- **22-request-validator-enhancer.md** - Intent detection system
- **01-core-architecture.md** - Agent routing

### Implementation Priority
- **Phase:** Entry Point Enhancement (Phase 1)
- **Priority:** HIGH (user experience critical)
- **Estimated Effort:** 4-6 hours
- **Expected Value:** Massive improvement in UX

### Placement in Implementation Sequence
1. ✅ Modular entry point (doc 23)
2. **→ Response templates (this doc)** ← Implement early!
3. ⏳ Request validator (doc 22)
4. ⏳ Plugin system (doc 02)

**Rationale:** Response quality affects all interactions, so implement early.

---

## 📝 Additional Guidelines

### Tone and Style

```yaml
tone:
  default: "Professional but friendly"
  planning: "Consultative, strategic"
  executing: "Confident, action-oriented"
  explaining: "Patient, educational"
  challenging: "Firm but respectful"
  reporting: "Factual, data-driven"

style:
  active_voice: true
  present_tense: true
  direct_address: true  # "I'll do X" not "The system will do X"
  contractions: false   # "I will" not "I'll" in formal contexts
  jargon: "Explain when used"
```

### Emoji Usage

```yaml
emoji_guidelines:
  frequency: "1-2 per response max"
  purpose: "Visual anchors, not decoration"
  
  approved:
    status: ["✅", "⚠️", "❌"]
    actions: ["🔧", "📝", "🔍"]
    concepts: ["🧠", "🎯", "🚀"]
    warnings: ["⚠️", "🛑", "🚨"]
  
  avoid:
    - "Excessive emoji chains (🎉🎊🎈)"
    - "Emoji in code blocks"
    - "Emoji as bullet points"
```

### Handling Edge Cases

```python
edge_cases = {
    "user_asks_for_code": {
        "template": "EXPLAIN",
        "action": "Show minimal code snippet with explanation"
    },
    
    "user_says_just_yes": {
        "template": "EXECUTE",
        "action": "Continue with last proposed plan"
    },
    
    "user_asks_for_more_detail": {
        "template": "EXPLAIN",
        "action": "Expand on previous response"
    },
    
    "ambiguous_request": {
        "template": "CONFIRM",
        "action": "Ask clarifying question with options"
    },
    
    "multi_part_request": {
        "template": "PLAN",
        "action": "Break into steps, propose sequence"
    }
}
```

---

## ✅ Benefits Summary

### For Users
- ✅ Faster to read responses (concise)
- ✅ Clear what CORTEX will do (action-oriented)
- ✅ Less code to wade through (tool usage)
- ✅ Consistent response structure (templates)
- ✅ Easier to make decisions (clear options)

### For CORTEX
- ✅ Consistent behavior across agents
- ✅ Clear guidelines for response generation
- ✅ Better tool utilization (less context waste)
- ✅ Measurable response quality
- ✅ Easier to maintain and improve

### For Development
- ✅ Testable response formats
- ✅ Template evolution tracked
- ✅ User feedback incorporated systematically
- ✅ Quality metrics tracked

---

## 🎉 Summary

This design provides a **response template system** that ensures CORTEX responses are:
- **Concise** - Brief by default, detailed on request
- **Actionable** - Clear what will happen next
- **Structured** - Consistent format for easy parsing
- **Tool-oriented** - Use tools instead of showing code
- **Context-aware** - Template selection based on intent

**Key Features:**
- ✅ 6 response templates (PLAN, EXECUTE, EXPLAIN, CONFIRM, REPORT, CHALLENGE)
- ✅ Code snippet rules (only when explicitly requested)
- ✅ Response length guidelines (50-600 words by template)
- ✅ Intent-based template selection
- ✅ Context-aware adjustments

**User Experience:**
- Responses 50-70% shorter on average
- 80%+ reduction in unnecessary code snippets
- Clearer communication of next steps
- Faster iteration cycles

**Implementation:** 4-6 hours, HIGH priority, Phase 1 (Entry Point)

---

**Status:** Design Complete ✅  
**Ready for Implementation:** Immediately (Phase 1)  
**Priority:** HIGH (critical UX improvement)  
**Next Steps:**
1. Add response template section to `cortex.md` (slim entry point)
2. Update agent prompts to reference templates
3. Test with real user requests
4. Measure and refine based on metrics

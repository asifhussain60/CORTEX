# Response Template Code Display Policy Update

**Date:** December 19, 2025  
**Version:** 4.0.1  
**Author:** Asif Hussain  
**Status:** ✅ Complete

---

## 🎯 Objective

Update response templates to **prevent default display of full code snippets** in GitHub Copilot Chat, promoting concise pseudo-code instead.

---

## ⚡ Problem Statement

Users reported that CORTEX responses were showing full code snippets by default, making chats verbose and less conversational. The goal was to make responses concise while preserving the ability to show code when explicitly requested.

---

## 💬 Solution

### New Code Display Policy

**Default Behavior:**
- ✅ **Always use concise pseudo-code** for implementation explanations
- ❌ **Never show full code snippets** unless explicitly requested
- ✅ **High-level logic flow** over implementation details

**Pseudo-Code Format:**
```markdown
**Approach:** Validate input → query database → transform results → cache → return
**Logic:** Check permissions → if authorized → execute operation → log result
**Flow:** Parse request → authenticate user → call service layer → format response
```

**Full Code Triggers (Explicit Requests):**
- "show me the code"
- "give me the implementation"
- "write the code"
- "provide code snippet"
- "example code"
- User pastes code asking for fix
- Code review requested

---

## 📊 Changes Made

### 1. `cortex-brain/response-templates-v4.yaml`

**Updated Sections:**

#### Response Section Guidelines
```yaml
response:
  content_guidelines: "Main response content - concise pseudo-code by default, full code ONLY if explicitly requested"
```

#### Implementation Section Guidelines
```yaml
implementation:
  content_guidelines: "Describe what was implemented using concise pseudo-code or high-level approach - full code snippets ONLY if user explicitly requests"
```

#### Standard Structure Rules
```yaml
rules:
  - "✅ Use concise pseudo-code by default (NOT full code snippets)"
  - "❌ NO full code unless explicitly requested"
```

#### Anti-Bloat Measures
```yaml
anti_bloat:
  pseudo_code_examples:
    - "**Approach:** Use decorator pattern → validate input → call original function → log result"
    - "**Logic:** Check cache → if miss, query DB → transform data → store in cache → return"
    - "**Flow:** User request → authentication → authorization → business logic → response"
```

#### New Code Display Policy Section
Added comprehensive policy with:
- Default behavior rules
- Pseudo-code format examples
- Full code trigger keywords
- Collapsible code guidelines (for >20 lines)

#### Updated Examples
```markdown
### 💬 Response
**Implementation approach:**
1. Create `FeatureX` class with validation decorator
2. Add input validation → business logic → error handling
3. Integrate with existing service layer
4. Add logging and metrics tracking

**Key logic:**
- Input validation: Check required fields → validate data types → sanitize
- Processing: Transform input → call dependency services → aggregate results
- Error handling: Try-catch wrapper → log errors → return user-friendly messages
```

### 2. `.github/prompts/CORTEX.prompt.md`

**Updated Rules:**
```markdown
**Rules:**
- ✅ Use concise pseudo-code by default (NOT full code snippets)
- ❌ NO full code unless explicitly requested
```

### 3. `.github/copilot-instructions.md`

**Updated Rules:**
```markdown
**Rules:**
- ✅ Use concise pseudo-code by default (NOT full code snippets)
- ❌ NO full code unless explicitly requested
```

---

## 🔍 Key Features

### 1. Pseudo-Code Format Components
- **Arrow notation** (→) for logic flow
- **Structured steps** (numbered or bulleted)
- **High-level abstractions** without implementation details
- **Clear intent** over syntax

### 2. Formatting Options
```yaml
formatting:
  pseudo_code: "**Pseudo-code:** {description}"
  code_reference: "**Implementation:** {high_level_approach}"
  code_block: "```{language}\n{code}\n```"  # Only when explicitly requested
```

### 3. Collapsible Code (for long snippets)
```markdown
<details><summary>📄 Implementation Code</summary>

```python
{full_code_here}
```

</details>
```

---

## 📈 Impact

### Before
```markdown
### 💬 Response
Here's the implementation:

```python
class FeatureX:
    def __init__(self, config):
        self.config = config
        self.validator = InputValidator()
    
    def process(self, data):
        if not self.validator.validate(data):
            raise ValueError("Invalid input")
        
        processed = self._transform(data)
        self._log_result(processed)
        return processed
```
```

### After (Default)
```markdown
### 💬 Response
**Implementation approach:**
1. Create `FeatureX` class with validation decorator
2. Add input validation → business logic → error handling
3. Integrate with existing service layer

**Key logic:**
- Validate input → transform data → log result → return
```

### After (When Requested: "show me the code")
```markdown
### 💬 Response
Here's the complete implementation:

```python
class FeatureX:
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        # Validation
        if not self._validate(data):
            raise ValueError("Invalid data")
        
        # Processing
        result = self._transform(data)
        return result
```
```

---

## ✅ Benefits

1. **Concise Chat Responses** - No verbose code blocks by default
2. **Conversational Flow** - Natural language explanations
3. **User Control** - Full code available on explicit request
4. **Reduced Token Usage** - Shorter responses = faster processing
5. **Better Mobile Experience** - Less scrolling in chat interface
6. **Preserved Functionality** - Code still available when needed

---

## 🔍 Testing Scenarios

### Scenario 1: Implementation Question (No Code Request)
**User:** "How would you implement user authentication?"  
**Expected:** Pseudo-code flow, no full code

### Scenario 2: Explicit Code Request
**User:** "Show me the code for user authentication"  
**Expected:** Full code snippet with syntax highlighting

### Scenario 3: Debug Request
**User:** "This code isn't working [paste code]"  
**Expected:** Full corrected code (implicit trigger)

### Scenario 4: Planning/Strategy
**User:** "What's the best approach for caching?"  
**Expected:** High-level strategy, no code

---

## 📋 Next Steps

1. ✅ **Template files updated**
2. ✅ **Prompt files updated**
3. ✅ **Documentation created**
4. ⏳ **Monitor user feedback** (next 2 weeks)
5. ⏳ **Adjust triggers** based on usage patterns

---

## 🔗 Related Files

- `cortex-brain/response-templates-v4.yaml` - Core template system
- `.github/prompts/CORTEX.prompt.md` - Main prompt file
- `.github/copilot-instructions.md` - Copilot instructions
- This document: `cortex-brain/documents/reports/RESPONSE-TEMPLATE-CODE-POLICY-UPDATE.md`

---

## 📚 Reference Examples

### Good Pseudo-Code Examples
```markdown
✅ "Validate input → query DB → transform → cache → return"
✅ "Check permissions → execute operation → log result"
✅ "Parse request → authenticate → call service → format response"
✅ "Try operation → catch errors → log → return user message"
```

### When Full Code Is Appropriate
```markdown
✅ User says "show me the code"
✅ User says "what's the implementation"
✅ User pastes broken code asking for fix
✅ Debugging specific syntax errors
❌ General "how does X work" questions
❌ Planning/strategy discussions
❌ Architecture explanations
```

---

**Status:** ✅ All changes implemented and documented  
**Version:** 4.0.1 (code display policy enhancement)  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX

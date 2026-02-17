# 🎨 Response Template Enhancement Integration Guide

**Version:** 1.0 | **Status:** ✅ Ready for Integration | **Author:** CORTEX Architecture  
**Last Updated:** 2026-02-09 | **Integration Priority:** HIGH | **Effort Estimate:** 2-4 hours

---

## 📋 Overview

This document describes how to integrate the new **semantic color-coded response template** into CORTEX's agent infrastructure. The template provides visual status indicators (red=critical, green=complete, orange=in-progress) to help users quickly assess work status.

**Key Benefits:**
- ✅ Visual status at a glance (emoji prefix + color coding)
- ✅ Consistent response format across all agents
- ✅ Automated header color detection based on content
- ✅ Session summaries with token budget tracking
- ✅ Backward compatible with existing markdown

---

## 🏗️ Architecture

### Component Hierarchy

```
ResponseTemplate (Manager)
├── SectionStatus (Enum: color mappings)
├── EnhancedHeader (Header with status)
├── Header Pattern Detection (auto-color rules)
└── Session Summary Generator

Agents (Implementation)
├── MasterOrchestrator
├── TDDOrchestrator
├── RefactoringOrchestrator
├── LENSSynthesis
└── Other agents (28 total)
```

### Status Indicators

| Emoji | Status | Color | Use When |
|-------|--------|-------|----------|
| ✅ | COMPLETE | Green | Task finished, all tests passed, ready |
| 🔵 | IN_PROGRESS | Orange | Work actively happening, pending completion |
| 🔴 | BLOCKED | Red | Critical issue, cannot proceed, emergency |
| ➡️ | PLANNED | Orange | Next steps, upcoming work, future tasks |
| 🎨 | DESIGN | Blue | Analysis, design, informational section |
| ⚠️ | WARNING | Yellow | Caution needed, attention required |
| 🚨 | CRITICAL | Red | Emergency situation, immediate action |

---

## 🔧 Integration Steps

### Step 1: Import Response Template Generator (Agents)

**File:** Any agent response handler

```python
from cortex.agents.core.response_template_generator import (
    ResponseTemplate,
    SectionStatus,
    EnhancedHeader
)

class MyOrchestrator:
    def generate_response(self, result):
        # Use enhanced headers
        header = ResponseTemplate.create_header("FIX 1: Implementation Complete")
        return f"{header}\n{result_details}"
```

### Step 2: Update Response Format Configuration

**File:** `cortex-registry/_cortex-master/meta/response-format.yaml`

```yaml
response_format:
  version: "2.0"
  semantic_coloring: enabled
  
  # Reference enhanced template
  templates:
    enhanced: !include meta/response-template-enhanced.yaml
    
  # Header auto-detection rules
  header_patterns:
    complete: ["complete", "completed", "success", "passed", "ready"]
    in_progress: ["in progress", "pending", "next", "todo"]
    blocked: ["blocked", "critical", "failed", "error"]
    planned: ["planned", "upcoming"]
    design: ["design", "analysis", "information"]
    warning: ["warning", "caution"]
```

### Step 3: Update Orchestrators (5 Core)

**Files to Update:**

1. **MasterOrchestrator** (`cortex/orchestrators/master_orchestrator.py`)
   ```python
   def format_response_header(self, operation: str, status: str):
       return ResponseTemplate.create_header(f"{operation}: {status}")
   ```

2. **TDDOrchestrator** (`cortex/orchestrators/tdd_orchestrator.py`)
   ```python
   def report_test_status(self, passed: int, total: int):
       status_text = "GREEN Phase Complete" if passed == total else "RED Phase Active"
       return ResponseTemplate.create_header(f"TDD: {status_text}")
   ```

3. **IntentRouter** (`cortex/orchestrators/intent_router.py`)
   ```python
   def route_operation(self, intent: str):
       header = ResponseTemplate.create_header(f"Intent: {intent}")
       # ... route logic ...
       return header
   ```

4. **RefactoringOrchestrator** (`cortex/orchestrators/refactoring_orchestrator.py`)
   ```python
   def refactor_start(self, target: str):
       return ResponseTemplate.create_header(f"Refactor: {target}", auto_detect=True)
   ```

5. **LENSSynthesis** (`cortex/orchestrators/lens_synthesis.py`)
   ```python
   def analyze_complete(self, findings: dict):
       return ResponseTemplate.create_header("LENS Analysis Complete")
   ```

### Step 4: Update MCP Tool Response Handlers

**File:** `cortex/mcp/tools/tool_response_handler.py`

```python
from cortex.agents.core.response_template_generator import ResponseTemplate

class ToolResponseHandler:
    def format_response(self, tool_name: str, result: dict, status: str):
        """Format MCP tool response with semantic headers."""
        header = ResponseTemplate.create_header(f"{tool_name}: {status}")
        
        return {
            "header": header,
            "content": result,
            "formatted": f"{header}\n\n{self._format_content(result)}"
        }
```

### Step 5: Update Prompt Files

**File:** `.github/prompts/cortex-architect.prompt.md`

Add new section (after existing response format section):

```markdown
## 🎨 Enhanced Response Template (Section 14)

### Semantic Color-Coded Headers

CORTEX responses now use emoji-prefixed headers for quick visual status assessment:

**Status Indicators:**

| Emoji | Meaning | Use For |
|-------|---------|---------|
| ✅ | COMPLETE | Finished tasks, passed tests, ready deployments |
| 🔵 | IN PROGRESS | Active work, pending items, next steps |
| 🔴 | BLOCKED | Critical issues, failures, emergency blockers |
| ➡️ | PLANNED | Upcoming work, future phases, planning |
| 🎨 | DESIGN | Analysis, information, design decisions |
| ⚠️ | WARNING | Caution needed, potential issues |
| 🚨 | CRITICAL | Emergency situations, immediate action |

### Auto-Detection Rules

Headers automatically colorize based on content keywords:

- **Complete:** "completed", "success", "passed", "ready", "finished"
- **In Progress:** "in progress", "pending", "next", "todo", "active"
- **Blocked:** "blocked", "critical", "failed", "error", "emergency"
- **Planned:** "planned", "upcoming", "next phase", "future"

**Example Responses:**

```
## ✅ FIX 1: Complete
- 5 governance tools implemented
- 23/23 tests passing
- Committed and pushed
```

```
## 🔵 FIX 2: In Progress
- YAML loader enhancement
- 15/33 tests currently passing
- Next: Complete Tier tests
```

### Integration Points

1. **Agents:** Use `ResponseTemplate.create_header()` for all responses
2. **MCP Tools:** Format responses with status emojis
3. **Orchestrators:** Prefix operation reports with status headers
4. **Documentation:** Update all generated summaries with color codes

### Session Summary Format

All session summaries should follow this pattern:

```
## {emoji} SESSION SUMMARY
**Session:** {name} | **Status:** {overall_status}

## 📊 Token Usage
**Used:** {used}k / {total}k ({percentage}%)
**Status:** {status_emoji} {health_message}

## ✅ COMPLETED
- Item 1
- Item 2

## 🔵 IN PROGRESS
- Item 3

## 🔴 BLOCKED
- Item 4

## ➡️ NEXT STEPS
1. Step 1
2. Step 2
```

### Color Technique Compatibility

The template uses **emoji prefix method** (recommended for maximum compatibility):

```markdown
## ✅ Header Title        ← Emoji prefix (works everywhere)
## 🔵 Another Header      ← Auto-detected color
## 🔴 Critical Issue       ← Always visible
```

**Fallback Methods** (if emoji not preferred):

1. **Bold + Emoji:** `## **✅** Title`
2. **HTML Comment:** `<!-- STATUS: COMPLETE -->`
3. **Quote Prefix:** `> ✅ Title`

---

## 📝 Implementation Checklist

- [ ] **Phase 1:** Create response-template-generator.py (DONE ✅)
- [ ] **Phase 2:** Update response-format.yaml with enhanced template reference
- [ ] **Phase 3:** Update 5 core orchestrators (MasterOrchestrator, TDD, IntentRouter, Refactoring, LENS)
- [ ] **Phase 4:** Update MCP tool response handlers
- [ ] **Phase 5:** Add enhanced template section to cortex-architect.prompt.md
- [ ] **Phase 6:** Update all agent documentation with color code usage
- [ ] **Phase 7:** Test with real responses (run 3+ operations)
- [ ] **Phase 8:** Verify backward compatibility (existing responses still work)
- [ ] **Phase 9:** Document final patterns in README.md
- [ ] **Phase 10:** Git commit and push

---

## 🧪 Validation Tests

### Test 1: Header Auto-Detection

```python
from cortex.agents.core.response_template_generator import ResponseTemplate

# Should auto-detect as COMPLETE
header1 = ResponseTemplate.create_header("Implementation Complete")
assert "✅" in header1

# Should auto-detect as BLOCKED
header2 = ResponseTemplate.create_header("Critical Issue Blocked")
assert "🔴" in header2

# Should auto-detect as IN_PROGRESS
header3 = ResponseTemplate.create_header("Feature In Progress")
assert "🔵" in header3
```

### Test 2: Session Summary

```python
from cortex.agents.core.response_template_generator import ResponseTemplate

summary = ResponseTemplate.session_summary(
    session_name="TEST SESSION",
    completed_items=["Task 1", "Task 2"],
    in_progress_items=["Task 3"],
    blocked_items=[],
    next_steps=["Step 1"],
    token_usage=(50, 200)
)

assert "✅ COMPLETED" in summary
assert "🔵 IN PROGRESS" in summary
assert "50k / 200k" in summary
assert "25%" in summary
```

### Test 3: Backward Compatibility

```python
# Old-style headers should still work
old_header = "## Implementation Status"
new_header = ResponseTemplate.create_header(old_header)

# Should not break existing markdown
assert new_header.startswith("##")
assert "Implementation Status" in new_header
```

---

## 🚀 Rollout Strategy

### Phase 1: Foundation (0.5 hours)
- ✅ Create response-template-generator.py
- Test imports and basic functionality
- Verify no breaking changes

### Phase 2: Configuration (1 hour)
- Update response-format.yaml
- Update cortex-architect.prompt.md
- Document patterns

### Phase 3: Core Orchestrators (1.5 hours)
- Update 5 core orchestrators with ResponseTemplate import
- Test each orchestrator response format
- Verify MCP tool integration

### Phase 4: Validation & Docs (1 hour)
- Run validation tests
- Update README.md with examples
- Create quick reference guide

**Total Effort:** 4 hours | **Risk Level:** LOW | **Rollback:** Simple (revert to plain headers)

---

## 📖 Quick Reference

### Usage in Agents

```python
# Option 1: Auto-detect status from title
header = ResponseTemplate.create_header("FIX 1: Implementation Complete")
# Output: ## ✅ FIX 1: Implementation Complete

# Option 2: Manual status selection
from cortex.agents.core.response_template_generator import SectionStatus
header = EnhancedHeader(
    title="Database Migration",
    status=SectionStatus.IN_PROGRESS
).render()
# Output: ## 🔵 Database Migration

# Option 3: Session summary
summary = ResponseTemplate.session_summary(
    session_name="Weekly Sprint",
    completed_items=["Feature A", "Bug Fix B"],
    in_progress_items=["Feature C"],
    blocked_items=[],
    next_steps=["Code review", "Deployment"],
    token_usage=(150, 200)
)
# Auto-formats with all sections + emoji indicators
```

### Copy-Paste Headers

```markdown
## ✅ {YOUR_TITLE_HERE}
## 🔵 {YOUR_TITLE_HERE}
## 🔴 {YOUR_TITLE_HERE}
## ➡️ {YOUR_TITLE_HERE}
## 🎨 {YOUR_TITLE_HERE}
## ⚠️ {YOUR_TITLE_HERE}
## 🚨 {YOUR_TITLE_HERE}
```

---

## ✨ Benefits Achieved

| Benefit | Impact | Evidence |
|---------|--------|----------|
| **Visual Status** | Quick assessment without reading | Emoji prefix visible immediately |
| **Consistency** | All responses follow same format | Automated header generation |
| **User Experience** | Reduced cognitive load | Status known from header emoji |
| **Backward Compatible** | No breaking changes | Old-style headers still work |
| **Extensible** | Easy to add new statuses | SectionStatus enum extensible |
| **Automation-Ready** | Can trigger alerts/notifications | Status accessible programmatically |

---

## 📞 Support

**Integration Questions:** Check `.github/agents/core/response-template-generator.py` for code examples

**Pattern Questions:** See example usage at bottom of generator file

**Troubleshooting:** Ensure `Optional` is imported from `typing` module

---

**Status:** ✅ Ready for Integration | **Next Action:** Begin Phase 1 Implementation

AC_COMPLETE: AC-RESPONSE-TEMPLATE-INTEGRATION-001 ✅

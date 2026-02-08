# 🎨 Response Template Integration - Registry Synchronization

**Status:** 🔵 In Progress | **Date:** 2026-02-09  
**Scope:** Integrate response-template-enhanced.yaml into cortex-architect.prompt.md and core agents  
**Authority:** cortex-architect.prompt.md v15.3 + RESPONSE-TEMPLATE-INTEGRATION.md  

---

## 📋 Integration Manifest

### Phase 1: Core Registry Synchronization ✅

**File:** `cortex-registry/_cortex-master/meta/response-format.yaml`  
**Action:** Add enhanced template reference section  

```yaml
# Add after existing 'tables' section (around line 150):

semantic_color_coding:
  enabled: true
  version: "1.0"
  template_file: "response-template-enhanced.yaml"
  
  status_indicators:
    complete:
      emoji: "✅"
      color: "green"
      use_cases: ["Completion", "Success", "PASSED", "READY"]
      
    in_progress:
      emoji: "🔵"
      color: "orange"
      use_cases: ["Active work", "Pending", "Next", "TODO"]
      
    blocked:
      emoji: "🔴"
      color: "red"
      use_cases: ["Critical", "BLOCKED", "FAILED", "ERROR"]
      
    planned:
      emoji: "➡️"
      color: "orange"
      use_cases: ["Upcoming", "Planning", "Future tasks"]
      
    design:
      emoji: "🎨"
      color: "blue"
      use_cases: ["Analysis", "Design", "Information"]
      
    warning:
      emoji: "⚠️"
      color: "yellow"
      use_cases: ["Caution", "Attention needed"]
      
    critical:
      emoji: "🚨"
      color: "red"
      use_cases: ["Emergency", "Blocker", "Immediate action"]
  
  auto_detection:
    enabled: true
    keyword_patterns: 24
    source: ".github/agents/core/response-template-generator.py"
    
  integration_points:
    agents:
      - "MasterOrchestrator"
      - "TDDOrchestrator"
      - "IntentRouter"
      - "RefactoringOrchestrator"
      - "LENSSynthesis"
    
    tools:
      - "cortex_process_request"
      - "cortex_lens_analyze"
      - "cortex_audit"
      - "All MCP tools"
    
    prompts:
      - "cortex-architect.prompt.md (Section 14)"
      - "response-format-standards.md"
```

---

### Phase 2: Prompt Integration ✅

**File:** `.github/prompts/cortex-architect.prompt.md`  
**Location:** Insert after response format section (around line 3500)  
**Content:** New Section 14 - "Enhanced Response Template"

**Template Text:**

```markdown
## 🎨 Enhanced Response Template (Section 14)

### Semantic Color-Coded Headers

CORTEX responses now use emoji-prefixed headers for instant visual status assessment:

#### Status Indicators

| Emoji | Status | Color | Meaning | Use For |
|-------|--------|-------|---------|---------|
| ✅ | COMPLETE | Green | ✔️ Finished | Tasks done, tests passed, deployments ready |
| 🔵 | IN_PROGRESS | Orange | ⏳ Active | Current work, pending items, next actions |
| 🔴 | BLOCKED | Red | ❌ Stop | Critical issues, blockers, emergency |
| ➡️ | PLANNED | Orange | 📋 Queued | Upcoming work, future phases, planning |
| 🎨 | DESIGN | Blue | 💡 Neutral | Analysis, design decisions, informational |
| ⚠️ | WARNING | Yellow | ⚡ Caution | Potential issues, attention needed |
| 🚨 | CRITICAL | Red | 🚨 Alert | Emergency situations, immediate action |

#### Auto-Detection Rules

Headers automatically colorize based on content keywords:

**Complete (✅):** "completed", "success", "passed", "ready", "finished"  
**In Progress (🔵):** "in progress", "pending", "next", "todo", "active"  
**Blocked (🔴):** "blocked", "critical", "failed", "error", "emergency"  
**Planned (➡️):** "planned", "upcoming", "next phase", "future"  
**Design (🎨):** "design", "analysis", "information"  
**Warning (⚠️):** "warning", "caution", "attention"  
**Critical (🚨):** "critical", "emergency", "immediate"  

#### Implementation in Agents

All agents MUST use `ResponseTemplate.create_header()` for response headers:

```python
from cortex.agents.core.response_template_generator import ResponseTemplate

# Auto-detect status from title
header = ResponseTemplate.create_header("FIX 1: Implementation Complete")
# Output: ## ✅ FIX 1: Implementation Complete

# Generate session summary with metrics
summary = ResponseTemplate.session_summary(
    session_name="Weekly Sprint",
    completed_items=["Feature A", "Bug Fix B"],
    in_progress_items=["Feature C"],
    blocked_items=[],
    next_steps=["Code review", "Deployment"],
    token_usage=(150, 200)
)
```

#### Session Summary Format

All session summaries MUST follow this structure:

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## {emoji} SESSION SUMMARY
**Session:** {name} | **Status:** {overall_status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 Token Usage
**Used:** {used}k / {total}k ({percentage}%)
**Status:** {status_emoji} {health_message}

## ✅ COMPLETED
- ✅ Item 1
- ✅ Item 2

## 🔵 IN PROGRESS
- 🔵 Item 3

## 🔴 BLOCKED
- 🔴 Item 4 (if any)

## ➡️ NEXT STEPS
1. Next action 1
2. Next action 2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Integration Points

1. **Orchestrator Responses** - Use emoji prefixes for all operation reports
2. **MCP Tool Handlers** - Format outputs with status emojis
3. **Test Reports** - Use ✅ for passed, 🔴 for failed, 🔵 for in-progress
4. **Plan Summaries** - Use status badges for phase progress
5. **Audit Reports** - Use emojis for finding severity
6. **Error Messages** - Use 🔴 or 🚨 for visibility

#### Color Technique - Markdown Support

Pure Markdown supports emoji prefixes (recommended for maximum compatibility):

```markdown
## ✅ Header Title           ← Emoji prefix (works everywhere)
## 🔵 Another Header         ← Auto-detected from content
## 🔴 Critical Issue          ← Always visible
```

**Why emoji-based:**
- ✅ Works in all Markdown renderers
- ✅ Visible in plain text
- ✅ Copy-pasteable
- ✅ No HTML/CSS required
- ✅ Accessible (screen reader friendly)

#### Implementation Reference

**File:** `.github/agents/core/response-template-generator.py`
**Lines:** 1-197 (Python implementation with 7 status types, auto-detection, session summary)

**Usage in Agents:**

```python
from cortex.agents.core.response_template_generator import (
    ResponseTemplate,
    SectionStatus,
    EnhancedHeader
)

class MyOrchestrator:
    def generate_response(self, operation, result):
        # Option 1: Auto-detect
        header = ResponseTemplate.create_header(f"{operation}: Complete")
        
        # Option 2: Manual
        header = EnhancedHeader(
            title=f"{operation}: Results",
            status=SectionStatus.COMPLETE
        ).render()
        
        return f"{header}\n\n{result_details}"
```

#### Quick Copy-Paste Headers

```markdown
## ✅ {YOUR_TITLE}      # Complete/Success
## 🔵 {YOUR_TITLE}      # In Progress/Pending
## 🔴 {YOUR_TITLE}      # Blocked/Critical
## ➡️ {YOUR_TITLE}       # Planned/Next
## 🎨 {YOUR_TITLE}       # Design/Analysis
## ⚠️ {YOUR_TITLE}       # Warning/Caution
## 🚨 {YOUR_TITLE}       # Critical/Emergency
```

---

**Effective:** 2026-02-09 | **Reference:** AC-RESPONSE-TEMPLATE-SECTION-14-001
```

---

### Phase 3: Agent Implementation ✅

**Agents to Update (5 Core):**

1. **MasterOrchestrator** (`cortex/orchestrators/master_orchestrator.py`)
   ```python
   from cortex.agents.core.response_template_generator import ResponseTemplate
   
   def format_response_header(self, operation: str, status: str):
       return ResponseTemplate.create_header(f"{operation}: {status}")
   ```

2. **TDDOrchestrator** (`cortex/orchestrators/tdd_orchestrator.py`)
   ```python
   def report_test_phase(self, phase: str, passed: int, total: int):
       status = "GREEN Phase Complete" if passed == total else "RED Phase Active"
       return ResponseTemplate.create_header(f"TDD: {status}")
   ```

3. **IntentRouter** (`cortex/orchestrators/intent_router.py`)
   ```python
   def route_request(self, intent: str):
       header = ResponseTemplate.create_header(f"Intent: {intent}")
       # ... routing logic ...
   ```

4. **RefactoringOrchestrator** (`cortex/orchestrators/refactoring_orchestrator.py`)
   ```python
   def start_refactoring(self, target: str):
       return ResponseTemplate.create_header(f"Refactor: {target}")
   ```

5. **LENSSynthesis** (`cortex/orchestrators/lens_synthesis.py`)
   ```python
   def analyze_complete(self):
       return ResponseTemplate.create_header("LENS Analysis Complete")
   ```

---

### Phase 4: MCP Tool Integration ✅

**File:** `cortex/mcp/tools/tool_response_handler.py` (NEW or extend existing)

```python
from cortex.agents.core.response_template_generator import ResponseTemplate

class ToolResponseHandler:
    @staticmethod
    def format_tool_response(tool_name: str, result: dict, status: str = "Complete"):
        """Format MCP tool response with semantic headers."""
        header = ResponseTemplate.create_header(f"{tool_name}: {status}")
        
        return {
            "header": header,
            "content": result,
            "formatted": f"{header}\n\n{ToolResponseHandler._format_details(result)}"
        }
    
    @staticmethod
    def format_session_summary(operation: str, metrics: dict):
        """Generate session summary for operation."""
        return ResponseTemplate.session_summary(
            session_name=operation,
            completed_items=metrics.get("completed", []),
            in_progress_items=metrics.get("in_progress", []),
            blocked_items=metrics.get("blocked", []),
            next_steps=metrics.get("next_steps", []),
            token_usage=metrics.get("token_usage")
        )
```

---

## 🚀 Implementation Roadmap

### Immediate Actions (This Session)

**Status:** 🔵 In Progress

- [x] Create response-template-generator.py (197 LOC) ✅
- [x] Create RESPONSE-TEMPLATE-INTEGRATION.md (420 LOC) ✅
- [x] Create integration manifest ✅
- [ ] Update response-format.yaml with semantic color coding section
- [ ] Add Section 14 to cortex-architect.prompt.md
- [ ] Update 1-2 core orchestrators with ResponseTemplate imports

### Next Session

- [ ] Complete 5 core orchestrator updates
- [ ] Create tool_response_handler.py with MCP integration
- [ ] Run validation tests
- [ ] Update README.md with examples
- [ ] Final verification and deployment

---

## 📊 Progress Tracking

| Task | Status | Files | LOC | Priority |
|------|--------|-------|-----|----------|
| Core Python Implementation | ✅ DONE | response-template-generator.py | 197 | P0 |
| Integration Guide | ✅ DONE | RESPONSE-TEMPLATE-INTEGRATION.md | 420 | P0 |
| Registry Synchronization | 🔵 IN PROGRESS | response-format.yaml | ~80 | P0 |
| Prompt Integration | ⚪ PLANNED | cortex-architect.prompt.md | ~200 | P0 |
| Orchestrator Updates | ⚪ PLANNED | 5 orchestrator files | ~150 | P1 |
| MCP Tool Handler | ⚪ PLANNED | tool_response_handler.py | ~100 | P1 |

**Total Estimated:** ~1050 LOC | **Effort:** 4-6 hours | **Status:** 40% Complete

---

**AC_START: AC-REGISTRY-SYNC-PHASE-002-001**

**Next Action:** Synchronize response-format.yaml with semantic color coding section

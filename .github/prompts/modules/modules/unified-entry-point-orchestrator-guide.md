# Unified Entry Point Orchestrator Guide

**Version:** 1.0  
**Status:** Production  
**Module:** src/orchestrators/unified_entry_point_orchestrator.py

---

## Overview

The Unified Entry Point Orchestrator provides a single command interface for ALL CORTEX operations with automatic intent detection, intelligent routing, and consistent response formatting.

## Key Features

- **Single Interface** - One command for all CORTEX capabilities
- **Intent Detection** - Automatic operation identification
- **Smart Routing** - Routes to specialist orchestrators
- **Response Templates** - Consistent formatting across 30+ operations
- **Context Tracking** - Remembers conversation history

## Purpose

Eliminates the need to remember multiple commands by providing natural language interface that automatically detects what you want and routes to the appropriate handler.

## Routing Capabilities

### Planning Operations
- Feature planning (feature, incremental, vision)
- ADO work items (story, feature, bug)
- RFC planning

### TDD Workflows
- Start TDD workflow
- Run tests
- Suggest refactorings
- Auto-debug on failures

### Brain Operations
- Capture conversation
- Import conversation
- Show context
- Clear context

### Admin Operations
- System alignment
- Holistic cleanup
- Cache management
- Optimize

### Discovery Operations
- View discovery
- Demo system
- Tutorial
- Help

## How It Works

1. **User Input** - Natural language request
2. **Intent Detection** - Identify operation type
3. **Route Selection** - Choose specialist orchestrator
4. **Execution** - Execute with appropriate handler
5. **Response Formatting** - Format with response template
6. **Context Tracking** - Save for next interaction

## Integration

### Response Templates
- 30+ pre-formatted templates
- Context-aware selection
- Consistent formatting
- Token-efficient

### Brain Memory
- Conversation history (Tier 1)
- Pattern learning (Tier 2)
- Project context (Tier 3)
- Auto-injection on relevance

### Agent Framework
- Specialist agents for execution
- Base agent inheritance
- Request/response patterns
- Auto-logging and timing

## Architecture

```
User Request
    ↓
Intent Detection
    ↓
Route Selection
    ↓
Specialist Orchestrator
    ↓
Response Template
    ↓
Formatted Response
```

## Natural Language Examples

```
"Add a purple button to the dashboard"
→ Detects: EXECUTE intent
→ Routes to: ExecutorAgent
→ Returns: Implementation plan

"plan a login feature"
→ Detects: PLAN intent
→ Routes to: PlanningOrchestrator
→ Returns: Feature plan with DoR/DoD

"run tests"
→ Detects: TEST intent
→ Routes to: TDDWorkflowOrchestrator
→ Returns: Test results and analysis
```

## Entry Point Registry

**File:** response-templates.yaml  
**Structure:**
```yaml
templates:
  template_name:
    triggers: [trigger1, trigger2]
    response_type: detailed|table|narrative
    content: formatted_response_template
```

## Performance

- Intent detection: <50ms
- Route selection: <10ms
- Template rendering: <5ms
- Total overhead: <100ms
- Execution time: Varies by operation

## Benefits

- **No Command Memorization** - Natural language only
- **Consistent UX** - Same format across operations
- **Context Awareness** - Remembers past interactions
- **Extensible** - Easy to add new operations
- **Discoverable** - Help system shows all capabilities

## Error Handling

- Graceful degradation on unknown intents
- Suggestion system for similar commands
- Detailed error messages
- Recovery guidance

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

# Interactive Q&A Framework

**Version:** 1.0.0  
**Status:** ✅ PRODUCTION  
**Author:** Asif Hussain

---

## Overview

The Interactive Q&A Framework replaces template-based workflows with conversational data collection for ADO planning, code review, and feedback submission.

**Benefits:**
- ✅ Natural conversation flow (no context switching)
- ✅ Conditional questions (skip irrelevant fields)
- ✅ Edit capabilities (change any answer)
- ✅ Preview before finalizing
- ✅ Extensible (add new workflows easily)

---

## Architecture

### Components

**1. BaseInteractiveAgent** (`src/cortex_agents/base_interactive_agent.py`)
- Core Q&A engine
- Question flow management
- State tracking
- Answer validation
- Edit/preview capabilities

**2. QuestionSchema System** (`cortex-brain/schemas/question-schemas/`)
- YAML-based question definitions
- Type validation (text, choice, multiline, checklist, number, boolean)
- Conditional logic (skip_if)
- Smart defaults

**3. Interactive Agents**
- `ADOInteractiveAgent` - ADO work item planning
- `CodeReviewInteractiveAgent` - PR review workflows
- `FeedbackInteractiveAgent` - Bug/feature/improvement reporting

**4. Intent Router Integration**
- Enhanced with aliases (workitem, pbi, user story, etc.)
- Routes to appropriate interactive agent
- Zero configuration needed

---

## Usage

### ADO Planning

**Triggers:**
- "plan ado"
- "create work item"
- "ado item"
- "pbi"
- "user story"

**Example:**
```
User: plan ado

Agent: What type of work item? (User Story/Feature/Bug/Task/Epic)
User: user story

Agent: Title?
User: Add dark mode to dashboard

Agent: Priority? (1=High, 2=Medium, 3=Low, 4=Very Low)
User: 2

... [continues for all fields] ...

Agent: [shows preview]

User: approve

Agent: ✅ Created ADO work item planning document
File: cortex-brain/documents/planning/ado/active/ADO-20251127-143500-add-dark-mode.md
DoR Status: 4/4 checks passing
```

**Conditional Questions:**
- Bug-specific: Severity, Reproduction Steps (only shown for Bug type)
- Feature-specific: Use case, benefits
- Task-specific: Estimated hours, dependencies

**Output:**
- Planning document in `cortex-brain/documents/planning/ado/active/`
- DoR (Definition of Ready) validation
- DoD (Definition of Done) checklist
- OWASP security review (if applicable)
- Related work items tracking

---

### Code Review

**Triggers:**
- "code review"
- "review pr"
- "pull request"
- "ado pr"
- "check code"

**Example:**
```
User: code review

Agent: How would you like to provide the PR? (ADO Link/Work Item ID/Paste Diff)
User: ado link

Agent: ADO Pull Request Link?
User: https://dev.azure.com/org/project/_git/repo/pullrequest/12345

Agent: Review Depth? (Quick/Standard/Deep)
User: standard

Agent: Focus Areas? (Security/Performance/Maintainability/Tests/Architecture/All)
User: security, performance

... [continues] ...

Agent: [shows preview]

User: approve

Agent: ✅ Generated code review report
Risk Score: 45/100
Issues: 1 critical, 2 warnings, 3 suggestions
Report: cortex-brain/documents/reports/code-reviews/CODE-REVIEW-20251127-143500-ado-link-standard.md
```

**Review Depths:**
- **Quick (30s):** Critical issues only
- **Standard (2min):** + Best practices, edge cases
- **Deep (5min):** + Security (OWASP), TDD patterns, performance analysis

**Output:**
- Executive summary (3 sentences)
- Risk score (0-100)
- Priority matrix (Critical/Warning/Suggestion)
- Copy-paste fix templates
- Next steps recommendations

---

### Feedback

**Triggers:**
- "feedback"
- "report bug"
- "report issue"
- "suggest feature"
- "improvement"

**Example:**
```
User: feedback

Agent: What type of feedback? (Bug Report/Feature Request/Improvement Suggestion)
User: bug report

Agent: Title?
User: Vision API fails with screenshots

Agent: Description?
User: When I attach a screenshot and say 'plan feature', the Vision API fails...

Agent: Steps to Reproduce?
User: 1. Say 'plan feature'
2. Attach screenshot
3. Vision API returns error

... [continues] ...

Agent: [shows preview]

User: approve

Agent: ✅ Feedback submitted successfully!
Type: Bug Report
Priority: High
File: cortex-brain/feedback/FEEDBACK-20251127-143500-bug-report-vision-api-fails.md
```

**Features:**
- Auto-context capture (platform, Python version, CORTEX version)
- Privacy protection (auto-redacts passwords, tokens, SSNs, credit cards)
- GitHub Issues formatted output (ready to copy-paste)
- Conditional questions (reproduction steps for bugs, use case for features)

---

## Question Schema Format

**Location:** `cortex-brain/schemas/question-schemas/*.yaml`

**Example:**
```yaml
name: ado-planning
version: 1.0.0

questions:
  - id: work_item_type
    type: choice
    prompt: What type of work item?
    required: true
    options:
      - User Story
      - Feature
      - Bug
      - Task
      - Epic
    default: User Story
    help_text: Choose the ADO work item type

  - id: severity
    type: choice
    prompt: Severity
    required: true
    options:
      - Critical
      - High
      - Medium
      - Low
    skip_if: "work_item_type != Bug"  # Only show for bugs
    help_text: Bug severity level
```

**Question Types:**
- `text` - Single-line text input
- `multiline` - Multi-line text input
- `choice` - Single choice from options
- `multi_choice` - Multiple choices
- `checklist` - Checklist items
- `number` - Numeric input
- `boolean` - Yes/No question

**Conditional Logic:**
- `skip_if: "field == value"` - Skip if condition true
- `skip_if: "field != value"` - Skip if condition false
- Supports callable functions for complex logic

---

## Extending the Framework

### Adding a New Interactive Workflow

**1. Create Question Schema** (`cortex-brain/schemas/question-schemas/my-workflow.yaml`)

```yaml
name: my-workflow
version: 1.0.0

questions:
  - id: question1
    type: text
    prompt: First question?
    required: true
```

**2. Create Interactive Agent** (`src/cortex_agents/my_interactive_agent.py`)

```python
from src.cortex_agents.base_interactive_agent import BaseInteractiveAgent, ConversationState

class MyInteractiveAgent(BaseInteractiveAgent):
    def get_schema_name(self) -> str:
        return "my-workflow"
    
    def can_handle(self, request: AgentRequest) -> bool:
        return "my trigger" in request.user_message.lower()
    
    def generate_output(self, state: ConversationState) -> Dict[str, Any]:
        # Generate output from state.answers
        return {"file_path": path, "content": content, "summary": summary}
```

**3. Register Agent Type** (`src/cortex_agents/agent_types.py`)

```python
class AgentType(Enum):
    MY_AGENT = auto()  # MyInteractiveAgent

class IntentType(Enum):
    MY_INTENT = "my_intent"

INTENT_AGENT_MAP = {
    IntentType.MY_INTENT: AgentType.MY_AGENT,
}
```

**4. Update Intent Router** (`src/cortex_agents/strategic/intent_router.py`)

```python
self.INTENT_KEYWORDS = {
    IntentType.MY_INTENT: ["my trigger", "my workflow", "my command"],
}
```

**Done!** Your new interactive workflow is now available.

---

## Conversation State Management

**Session Tracking:**
- Each conversation gets unique session_id
- State persists across multiple messages
- Can edit previous answers anytime
- Preview before finalizing

**Commands:**
- `preview` - Show current answers
- `approve` / `yes` - Finalize and generate output
- `edit [field] to [value]` - Change an answer
- `cancel` - Cancel conversation

---

## Error Handling

**Validation:**
- Required fields enforced
- Type validation (numbers must be numbers, etc.)
- Option validation (choices must be from list)
- Custom validation functions supported

**User-Friendly Errors:**
```
Agent: Invalid answer: Must be a number

Priority? (1=High, 2=Medium, 3=Low, 4=Very Low)
```

---

## Testing

**Unit Tests:**
```bash
pytest tests/cortex_agents/test_base_interactive_agent.py
pytest tests/cortex_agents/test_ado_interactive_agent.py
pytest tests/cortex_agents/test_code_review_interactive_agent.py
pytest tests/cortex_agents/test_feedback_interactive_agent.py
```

**Integration Tests:**
```bash
pytest tests/integration/test_interactive_workflows.py
```

**Manual Testing:**
```
# Test ADO workflow
User: plan ado

# Test Code Review workflow
User: code review

# Test Feedback workflow
User: feedback
```

---

## Migration from Template-Based

**Old Workflow (Template-Based):**
1. User: "plan ado"
2. CORTEX: Creates blank template file
3. User: Switches to VS Code
4. User: Fills out template manually
5. User: Saves file
6. User: Returns to chat
7. User: "import ado template"
8. CORTEX: Processes template

**Problems:**
- ❌ Context switching (chat → VS Code → chat)
- ❌ Not conversational
- ❌ All fields required upfront
- ❌ No validation until import
- ❌ Can't preview before finalizing

**New Workflow (Interactive Q&A):**
1. User: "plan ado"
2. CORTEX: Asks questions one-by-one
3. User: Answers directly in chat
4. CORTEX: Validates each answer
5. CORTEX: Shows preview
6. User: "approve"
7. CORTEX: Generates final document

**Benefits:**
- ✅ No context switching
- ✅ Natural conversation
- ✅ Skip optional fields
- ✅ Immediate validation
- ✅ Preview before finalizing
- ✅ Edit capabilities

---

## Performance

**Metrics:**
- Question display: <100ms
- Answer validation: <50ms
- Preview generation: <200ms
- File generation: <500ms

**Optimization:**
- Schema loaded once on agent init
- State stored in memory (no disk I/O during conversation)
- File written only on finalization

---

## Security & Privacy

**Feedback Agent:**
- Auto-redacts passwords, tokens, API keys
- Removes SSNs, credit card numbers
- Sanitizes all user input before saving

**Data Storage:**
- All data stored locally in `cortex-brain/`
- No external API calls (unless explicitly configured)
- Privacy-safe by default

---

## Future Enhancements

**Phase 2 (Planned):**
- Multi-step workflows (ADO → Planning → Implementation)
- Smart defaults from user history
- Answer suggestions based on past inputs
- Bulk operations (create multiple work items)
- Export to ADO API (auto-create work items)

---

## Support

**Documentation:**
- API Reference: `src/cortex_agents/base_interactive_agent.py`
- Question Schema Spec: `cortex-brain/schemas/question-schemas/README.md`
- Agent Implementation Guide: This file

**Troubleshooting:**
- Schema not found: Check `cortex-brain/schemas/question-schemas/[name].yaml` exists
- Agent not routing: Verify intent mapping in `agent_types.py`
- Question skipping incorrectly: Check `skip_if` condition syntax

---

**Last Updated:** 2025-11-27  
**Version:** 1.0.0  
**Status:** Production Ready ✅

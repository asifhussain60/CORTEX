# CORTEX - Development Intelligence System

**Purpose:** Unified entry point for all development tasks  
**Usage:** Send development requests here (planning, implementation, testing, queries)  
**Version:** 1.0  
**Status:** Active

---

## 🚀 Quick Start

**For Planning:**
> "Create a plan for adding authentication to the dashboard"

**For Implementation:**
> "Implement the login form with validation"

**For Testing:**
> "Run all tests and validate code coverage"

**For Bug Fixes:**
> "Fix the issue where the submit button doesn't respond"

**For Queries:**
> "Explain how the brain update process works"

**For Context:**
> "What did we discuss about the export feature?"

---

## 📋 How It Works

1. **Intent Detection:** Your request is analyzed to determine intent (PLAN, EXECUTE, TEST, FIX, QUERY)
2. **Context Injection:** Relevant context from brain (Tiers 1-3) is loaded
3. **Workflow Selection:** Appropriate workflow is selected
4. **Execution:** Task is executed following best practices (TDD, DoD, etc.)
5. **Learning:** Outcomes are recorded for future pattern matching

---

## 🧠 Internal Processing

<!-- AGENT ROUTING METADATA -->
<!-- This section is processed by CORTEX/src/router.py -->

```yaml
request_metadata:
  source: "cortex.md"
  conversation_id: auto-generated
  timestamp: auto-generated
  
context_requirements:
  working_memory: true     # Load Tier 1 (last 50 conversations)
  knowledge_graph: true    # Load Tier 2 (patterns)
  dev_context: true        # Load Tier 3 (recent activity)
  
routing_config:
  intent_router: "cortex-agents/strategic/intent_router.py"
  confidence_threshold: 0.7
  fallback_workflow: "plan"
  
performance_targets:
  intent_detection_ms: 100
  context_injection_ms: 200
  total_routing_ms: 300
```

---

## 🔧 Developer Notes

**For CORTEX Developers:**
- Entry point processed by `CORTEX/src/router.py`
- User requests extracted from conversation
- Intent detection via Phase 4 agents
- Workflow orchestration via Phase 5 workflows
- All interactions logged to Tier 1

**Performance:**
- Intent detection: <100ms
- Context injection: <200ms
- Total routing: <300ms

**Workflows Available:**
- `tdd_workflow` - RED → GREEN → REFACTOR cycle
- `feature_workflow` - PLAN → EXECUTE → TEST
- `bug_fix_workflow` - DIAGNOSE → FIX → VERIFY
- `query_workflow` - ANALYZE → SEARCH → RESPOND

---

## 📊 Workflow Status

Current workflow: `<auto-populated>`  
Phase: `<auto-populated>`  
Progress: `<auto-populated>`

---

## 🎯 Examples

### Planning a Feature
```markdown
User: Create a plan for adding dark mode to the dashboard

CORTEX Response:
✅ Intent: PLAN
✅ Workflow: feature_creation
✅ Context: 3 similar UI features found in history

Plan Created:
Phase 1: Theme infrastructure
  - Create theme context
  - Add theme toggle state
  - Define color variables

Phase 2: Component updates
  - Update dashboard components
  - Apply theme-aware styling
  - Add transition animations

Phase 3: Persistence
  - Save preference to localStorage
  - Load preference on mount
  - Test across sessions

Estimated Duration: 4-6 hours
Ready to execute? (y/n)
```

### Implementing with TDD
```markdown
User: Implement the theme toggle component

CORTEX Response:
✅ Intent: EXECUTE
✅ Workflow: tdd_workflow
✅ Context: Similar component patterns found

RED Phase:
  ✓ Created test: test_theme_toggle.py
  ✓ Test failing as expected

GREEN Phase:
  ✓ Implemented: ThemeToggle.razor
  ✓ All tests passing

REFACTOR Phase:
  ✓ Code cleaned and optimized
  ✓ DoD validated (0 errors, 0 warnings)

✅ Feature complete! Files modified:
  - Components/ThemeToggle.razor
  - Tests/test_theme_toggle.py
```

### Fixing a Bug
```markdown
User: Fix the issue where clicking the toggle doesn't change the theme

CORTEX Response:
✅ Intent: FIX
✅ Workflow: bug_fix
✅ Context: Recent activity shows theme implementation

DIAGNOSE Phase:
  ✓ Identified: Event handler not wired
  ✓ Root cause: Missing @onclick attribute

FIX Phase:
  ✓ Added: @onclick="ToggleTheme"
  ✓ Test created: test_toggle_click.py
  ✓ Tests passing

VERIFY Phase:
  ✓ Manual verification passed
  ✓ No regressions detected
  ✓ DoD validated

✅ Bug fixed! Commit created with semantic message.
```

### Querying Knowledge
```markdown
User: What did we discuss about the export feature?

CORTEX Response:
✅ Intent: QUERY
✅ Workflow: knowledge_query
✅ Context: Searching Tier 1 (conversations) + Tier 2 (patterns)

Found in Conversation #23 (3 days ago):
  - Feature: PDF export for transcripts
  - Status: Completed
  - Files: PdfExportService.cs, TranscriptExport.razor
  - Pattern: export_feature_workflow

Related Patterns:
  - Similar export features: 4 instances
  - Average completion: 5.5 hours
  - Success rate: 94%

Would you like to see the implementation details?
```

---

## 🛡️ Quality Guarantees

Every execution through CORTEX ensures:
- ✅ **TDD enforced** - Tests written first (RED → GREEN → REFACTOR)
- ✅ **DoD validated** - Zero errors, zero warnings, all tests pass
- ✅ **Context-aware** - Uses history and patterns to guide decisions
- ✅ **Architectural alignment** - Solutions fit existing architecture
- ✅ **Self-learning** - Every interaction improves future performance

---

## 📚 Additional Resources

- **User Guide:** `CORTEX/docs/user-guide.md`
- **Workflow Guide:** `CORTEX/docs/workflow-guide.md`
- **Developer Guide:** `CORTEX/docs/developer-guide.md`
- **API Reference:** `CORTEX/docs/api-reference.md`

---

**Ready to start?** Just tell CORTEX what you need in natural language above!

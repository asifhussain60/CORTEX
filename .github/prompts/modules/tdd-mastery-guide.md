# TDD Mastery Guide

**Purpose:** Complete Test-Driven Development workflow with RED→GREEN→REFACTOR cycle automation

**Version:** 3.2.0  
**Status:** ✅ PRODUCTION

---

## Commands

- `start tdd` or `tdd workflow` - Start TDD workflow
- `run tests` - Execute tests and analyze results
- `suggest refactorings` - Get refactoring recommendations (now supports Python, JavaScript, TypeScript, C#)
- `tdd status` - Show current TDD state and progress

---

## How It Works

1. **RED State:** Write failing test → Auto-triggers debug session on failure
2. **GREEN State:** Implement code → Captures timing data → Auto-collects feedback
3. **REFACTOR State:** Suggest improvements → Multi-language AST-based + performance code smell detection

---

## Key Features

- ✅ **Terminal Integration (Phase 1):** Auto-detects test execution from #terminal_last_command, #get_terminal_output
- ✅ **Workspace Discovery (Phase 2):** Auto-discovers project structure via @workspace context
- ✅ **Brain Memory (Phase 3):** Stores sessions in Tier 1, learns from failures in Tier 2
- ✅ **Programmatic Execution (Phase 4):** Runs pytest/jest/xunit programmatically with JSON parsing
- ✅ **Auto-Debug on RED:** Debug session starts automatically when tests fail
- ✅ **Performance-Based Refactoring:** Uses debug timing data to identify bottlenecks
- ✅ **Multi-Language Refactoring (NEW v3.2):** AST-based code smell detection for Python, JavaScript, TypeScript, C#
- ✅ **View Discovery Integration:** Auto-discovers element IDs before test generation
- ✅ **Auto-Feedback Collection:** Gathers feedback on GREEN state transitions
- ✅ **Smart Code Smell Detection:** 11 smell types including performance-based
- ✅ **Data-Driven Optimization:** Identifies slow functions (>100ms), hot paths (>10 calls), bottlenecks (>500ms)
- ✅ **Test Location Isolation (Layer 8):** Application tests in user repo, CORTEX tests in CORTEX folder

---

## Multi-Language Refactoring (v3.2.0)

**Supported Languages:**
- Python (90% confidence - ast module)
- JavaScript (85% confidence - esprima parser)
- TypeScript (85% confidence - tree-sitter)
- C# (80% confidence - tree-sitter)

**Code Smells Detected:**
1. **Long Method** - Functions >50 lines
2. **Complex Method** - Cyclomatic complexity >10
3. **Deep Nesting** - Nesting depth >4
4. **Long Parameter List** - Parameters >5
5. **Magic Numbers** - Unexplained numeric literals
6. **Performance Issues** - Slow functions, hot paths, bottlenecks (requires timing data)

**Usage:**
```
You: "suggest refactorings for auth.py"
CORTEX: 🎯 Found 4 code smells in Python code:
        1. LoginService.validate() - LONG_METHOD (78 lines) - Split into smaller functions
        2. CheckPermissions() - COMPLEX_METHOD (complexity 15) - Reduce complexity
        3. ProcessAuth() - DEEP_NESTING (depth 6) - Use early returns
        4. ValidateUser() - SLOW_FUNCTION (145ms avg) - Add caching layer
```

---

## Natural Language Examples

- "start TDD workflow for user authentication"
- "run tests and debug failures"
- "suggest refactorings based on performance"
- "analyze code smells in JavaScript"
- "what's my TDD status?"

---

## State Machine

```
IDLE → RED (test fails) → auto-debug session → auto-checkpoint (git)
  ↓
GREEN (test passes) → capture timing data → collect feedback → auto-checkpoint (git)
  ↓
REFACTOR → performance analysis → suggest optimizations → auto-checkpoint (git)
  ↓
COMPLETE → validate improvements
```

**Git Checkpoint Integration:**
- **RED State:** Auto-checkpoint after test creation (captures failing test before implementation)
- **GREEN State:** Auto-checkpoint after test passes (minimal working implementation)
- **REFACTOR State:** Auto-checkpoint after refactoring (clean code while tests pass)
- **Benefit:** Enforces TDD discipline, prevents implementation before test failure verification
- **Configuration:** Set `auto_checkpoint.enabled: true` in `git-checkpoint-rules.yaml`
- **See Also:** Git Checkpoint Orchestrator Guide for detailed configuration

---

## Configuration Options

```python
TDDWorkflowConfig(
    # Phase 1: Terminal Integration
    enable_terminal_integration=True,    # Use GitHub Copilot terminal tools
    # Phase 2: Workspace Discovery
    enable_workspace_discovery=True,     # Auto-discover project structure
    # Phase 3: Brain Memory Integration
    enable_session_tracking=True,        # Store in Tier 1/2
    # Phase 4: Programmatic Execution
    enable_programmatic_execution=True,  # Run tests automatically
    # Layer 8: Test Location Isolation
    auto_detect_test_location=True,      # Auto-detect user repo vs CORTEX
    enable_brain_learning=True,          # Capture patterns from user tests
    user_repo_root=None,                 # Auto-detected from source file
    # Legacy Features
    enable_view_discovery=True,          # Auto-discover element IDs
    enable_debug_integration=True,       # Auto-debug on failures
    enable_feedback_collection=True,     # Auto-collect feedback
    debug_timing_to_refactoring=True     # Use timing data for refactoring
)
```

---

## Performance Smell Detection

- **Slow Function:** Functions averaging >100ms execution time (0.95 confidence)
- **Hot Path:** Functions called >10 times in a session (0.95 confidence)
- **Performance Bottleneck:** Functions consuming >500ms total time (0.95 confidence)
- **8 Traditional Smells:** Long method, complex method, duplicate code, dead code, etc. (0.70-0.85 confidence)

---

## Output

- Debug data: `cortex-brain/tier1-working-memory.db` (debug_sessions table)
- Feedback reports: `cortex-brain/documents/reports/CORTEX-FEEDBACK-*.md`
- View mappings: `cortex-brain/tier2-knowledge-graph.db` (element_mappings table)
- Test results: `cortex-brain/tier1-working-memory.db` (test_results table)

---

## Integration Points

- **ViewDiscoveryAgent:** Scans .razor/.cshtml files for element IDs (runs before test gen)
- **DebugAgent:** Runtime instrumentation with zero source modification (auto-starts on RED)
- **FeedbackAgent:** Structured feedback collection with Gist auto-upload (triggers on GREEN)
- **RefactoringIntelligence:** AST-based smell detection with performance data (REFACTOR state)

---

## Benefits

- **Time Savings:** 60+ min manual discovery → <5 min automated (View Discovery)
- **Accuracy:** 95%+ test reliability with real element IDs vs text-based selectors
- **Performance:** Auto-identifies bottlenecks using measured timing data
- **Quality:** 11 code smell types with actionable refactoring suggestions
- **Automation:** Zero-intervention workflow (auto-debug, auto-feedback, auto-optimize)

---

## Natural Language Workflow

```
You: "start tdd workflow for login page"
CORTEX: ✅ Workspace discovered: Python project with pytest
        ✅ Test framework: pytest
        ✅ Ready for RED state - write your failing test

You: "run tests"
CORTEX: 🔧 Running tests with pytest...
        ✅ Tests completed in 2.50s
           Passed: 5 ✓
           Failed: 2 ✗
        ❌ Entering RED state
        📊 Stored test results in brain (Tier 2)

You: "suggest refactorings"
CORTEX: 🎯 Found 3 performance issues:
        1. ValidateUser() - SLOW_FUNCTION (avg 145ms) - Consider caching
        2. CheckPermissions() - HOT_PATH (called 23 times) - Batch calls
        3. DatabaseQuery() - BOTTLENECK (total 850ms) - Add indexes
```

---

## Complete Integration Example

```python
# Initialize with all phases enabled
config = TDDWorkflowConfig(
    project_root="/path/to/project",
    enable_terminal_integration=True,       # Phase 1
    enable_workspace_discovery=True,        # Phase 2
    enable_session_tracking=True,           # Phase 3
    enable_programmatic_execution=True      # Phase 4
)

orchestrator = TDDWorkflowOrchestrator(config)

# Start session (Phase 3: Brain integration)
session_id = orchestrator.start_session("user_authentication")

# Generate tests (Phase 2: Workspace discovery)
tests = orchestrator.generate_tests(source_file="src/login.py")

# Run tests programmatically (Phase 4: Test execution)
result = orchestrator.run_and_verify_tests()
# Output:
# 🔧 Running tests with pytest...
# ✅ Tests completed in 2.50s
#    Passed: 5 ✓
#    Failed: 2 ✗

# Result stored in Tier 2, session updated in Tier 1
```

---

## Test Location Isolation (Layer 8)

**Rule:** Application tests ALWAYS go in user repo, CORTEX tests stay in CORTEX folder.

**How It Works:**
1. **Auto-Detection:** CORTEX detects if you're testing application code vs CORTEX code
2. **User Repo Tests:** Generated in your project's test directory (e.g., `/Users/you/myapp/tests/`)
3. **Framework Detection:** Uses YOUR existing test framework (pytest, jest, xunit, etc.)
4. **Brain Learning:** CORTEX captures patterns and insights without storing your code
5. **CORTEX Tests:** Only CORTEX infrastructure tests stay in CORTEX folder

**Example Workflow:**
```
You: "Create tests for my payment processing feature"
Working Dir: /Users/you/myapp/src/payments.py

CORTEX:
✅ Detected user application code (outside CORTEX)
✅ Found existing framework: pytest
✅ Test location: /Users/you/myapp/tests/test_payments.py
✅ Following your naming convention: test_*.py
🧠 Learning: User prefers parametrized fixtures for payment tests
🧠 Stored patterns in cortex-brain/tier2/ (NOT your code)
```

**What Gets Stored in Brain:**
- ✅ "User prefers mock stripe API for payment tests"
- ✅ "Test framework: pytest with fixtures"
- ✅ "Naming pattern: test_<feature>.py"
- ✅ "Common failure: DB not seeded before tests"
- ❌ NOT your actual test code
- ❌ NOT your business logic

**Benefits:**
- ✅ Your repo stays self-contained with its own tests
- ✅ CORTEX learns from your patterns
- ✅ No pollution of CORTEX folder with application tests
- ✅ Proper separation of concerns
- ✅ Your test framework is honored

---

## See Also

- Implementation: `cortex-brain/documents/implementation-guides/TDD-MASTERY-INTEGRATION-PLAN.md`
- Phase Reports: `cortex-brain/documents/reports/TDD-MASTERY-PHASE*.md`
- Test Strategy: `cortex-brain/documents/implementation-guides/test-strategy.yaml`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions) - See LICENSE  
**Repository:** https://github.com/asifhussain60/CORTEX

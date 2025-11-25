# TDD Workflow Orchestrator Guide

**Purpose:** Unified API for complete TDD workflow (RED→GREEN→REFACTOR)

**Version:** 1.0.0
**Status:** ✅ COMPLETE  
**Location:** `src/workflows/tdd_workflow_orchestrator.py`

---

## Overview

TDDWorkflowOrchestrator provides end-to-end TDD cycle automation with brain memory integration, test execution, performance analysis, and intelligent refactoring suggestions.

**Key Capabilities:**
- **Phase 1:** Test generation with edge cases, domain knowledge, error conditions
- **Phase 2:** State machine (RED→GREEN→REFACTOR) with session tracking
- **Phase 3:** Brain memory integration (Tier 1 working memory, Tier 2 knowledge graph)
- **Phase 4:** Test execution manager, terminal integration, workspace discovery
- **Layer 8:** Test location isolation (user repo tests vs CORTEX tests)

---

## Quick Start

### Basic TDD Cycle

```python
from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
from pathlib import Path

# Initialize
config = TDDWorkflowConfig(
    project_root="d:/PROJECTS/MyApp",
    enable_refactoring=True,
    enable_session_tracking=True
)

orchestrator = TDDWorkflowOrchestrator(config)

# Start session
session_id = orchestrator.start_session("user_authentication")

# RED: Generate comprehensive tests
tests = orchestrator.generate_tests(
    source_file="src/auth/login.py",
    function_name="authenticate_user",
    scenarios=["basic", "edge_cases", "error_conditions"]
)

print(f"Generated {tests['test_count']} tests")

# GREEN: Run tests and implement
results = orchestrator.run_and_verify_tests(verbose=True)

if results['tests_pass']:
    print("✅ All tests passing")
    
    # REFACTOR: Get performance-based suggestions
    suggestions = orchestrator.suggest_refactorings("src/auth/login.py")
    
    for suggestion in suggestions:
        print(f"🔧 {suggestion['type']}: {suggestion['description']}")

# Complete cycle
cycle_metrics = orchestrator.complete_cycle()
print(f"Cycle {cycle_metrics['cycle_number']} complete")
```

### Natural Language Commands

**Commands:**
- `start tdd` - Start TDD workflow
- `generate tests for [file]` - Generate comprehensive tests
- `run tests` - Execute and verify tests
- `suggest refactorings` - Get performance-based suggestions
- `resume tdd session` - Continue previous session

**Examples:**
```
User: "start tdd for user authentication"
CORTEX: Creates session, initializes state machine, ready for test generation

User: "generate tests for src/auth/login.py"
CORTEX: Generates edge cases, domain patterns, error conditions

User: "run tests"
CORTEX: Executes tests, reports results, transitions state machine
```

---

## API Reference

### TDDWorkflowConfig

Configuration for TDD workflow.

```python
@dataclass
class TDDWorkflowConfig:
    project_root: str  # Project repository root
    test_output_dir: str = "tests"
    brain_storage_path: str = "cortex-brain/tier1/working_memory.db"
    
    # Workflow features
    enable_refactoring: bool = True
    enable_session_tracking: bool = True
    auto_detect_smells: bool = True
    confidence_threshold: float = 0.7
    
    # Performance optimization
    enable_caching: bool = True
    ast_cache_size: int = 100
    pattern_cache_ttl_minutes: int = 60
    batch_max_workers: int = 4
    
    # TDD Mastery integration
    enable_view_discovery: bool = True
    auto_debug_on_failure: bool = True
    auto_feedback_on_persistent_failure: bool = True
    feedback_threshold: int = 3
    debug_timing_to_refactoring: bool = True
    
    # Test execution
    enable_terminal_integration: bool = True
    enable_workspace_discovery: bool = True
    enable_programmatic_execution: bool = True
    
    # Test location isolation
    user_repo_root: Optional[str] = None
    is_cortex_test: bool = False
    auto_detect_test_location: bool = True
    enable_brain_learning: bool = True
```

### start_session

```python
def start_session(self, feature_name: str, session_id: Optional[str] = None) -> str
```

Start new TDD session with brain memory integration.

**Parameters:**
- `feature_name` (str): Name of feature being developed
- `session_id` (Optional[str]): Explicit session ID (auto-generated if None)

**Returns:**
- `str`: Session ID for tracking

**Example:**
```python
session_id = orchestrator.start_session("payment_integration")
# Returns: "tdd_a1b2c3d4"
```

### generate_tests

```python
def generate_tests(
    self,
    source_file: str,
    function_name: Optional[str] = None,
    scenarios: Optional[List[str]] = None
) -> Dict[str, Any]
```

Generate comprehensive tests (RED phase).

**Parameters:**
- `source_file` (str): Path to source file
- `function_name` (Optional[str]): Specific function (None = all)
- `scenarios` (Optional[List[str]]): Test scenarios

**Scenarios:**
- `"basic"`: Basic functionality tests
- `"edge_cases"`: Boundary conditions, null checks
- `"domain_knowledge"`: Domain-specific patterns
- `"error_conditions"`: Exception handling
- `"parametrized"`: Data-driven tests
- `"property_based"`: Property tests

**Returns:**
```python
{
    "session_id": "tdd_a1b2c3d4",
    "tests": [...],
    "test_file": "tests/test_login.py",
    "test_count": 5,
    "phase": "RED"
}
```

### run_and_verify_tests

```python
def run_and_verify_tests(
    self, 
    test_file: Optional[str] = None, 
    verbose: bool = True
) -> Dict[str, Any]
```

Run tests programmatically and verify (GREEN phase).

**Parameters:**
- `test_file` (Optional[str]): Specific test file (None = all)
- `verbose` (bool): Show detailed output

**Returns:**
```python
{
    "test_results": {
        "passed": 5,
        "failed": 0,
        "duration": 2.34
    },
    "tests_pass": True,
    "phase": "GREEN"
}
```

### suggest_refactorings

```python
def suggest_refactorings(self, source_file: str) -> List[Dict[str, Any]]
```

Generate performance-based refactoring suggestions (REFACTOR phase).

**Parameters:**
- `source_file` (str): Path to source file

**Returns:**
```python
[
    {
        "type": "EXTRACT_METHOD",
        "location": "src/auth/login.py:45",
        "description": "Extract method: validate_credentials",
        "confidence": 0.85,
        "effort": "medium"
    }
]
```

---

## Configuration

### Brain Memory Integration

```python
config = TDDWorkflowConfig(
    project_root="/path/to/project",
    brain_storage_path="cortex-brain/tier1/working_memory.db",
    enable_session_tracking=True,
    enable_brain_learning=True
)
```

**Brain Tiers:**
- **Tier 1:** Working memory (active sessions)
- **Tier 2:** Knowledge graph (patterns, failures)
- **Tier 3:** Development context (project learning)

### Test Location Isolation (Layer 8)

```python
config = TDDWorkflowConfig(
    project_root="/path/to/cortex",
    user_repo_root="/path/to/user/app",
    auto_detect_test_location=True,
    enable_brain_learning=True
)
```

**Rules:**
- User code tests → `user_repo_root/tests/`
- CORTEX tests → `cortex_root/tests/`
- Brain learns patterns without storing user code

---

## Integration Examples

### With GitCheckpointOrchestrator

```python
from orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator

if results['tests_pass']:
    git_orch = GitCheckpointOrchestrator(Path("."))
    checkpoint_id = git_orch.create_checkpoint(
        message="GREEN: All tests passing",
        checkpoint_type="green",
        context={"session_id": session_id}
    )
```

### With LintValidationOrchestrator

```python
from orchestrators.lint_validation_orchestrator import LintValidationOrchestrator

lint_orch = LintValidationOrchestrator()
validation = lint_orch.validate(Path("."), language="python")

if validation['passed']:
    orchestrator.complete_cycle()
```

---

## Troubleshooting

**Problem:** Tests created in wrong location

**Solution:**
```python
config = TDDWorkflowConfig(
    user_repo_root="/path/to/user/app",  # Explicit path
    auto_detect_test_location=True
)
```

**Problem:** State transition errors

**Solution:** Execute phases in order:
1. `start_session()` → IDLE
2. `generate_tests()` → RED
3. `run_and_verify_tests()` → GREEN
4. `suggest_refactorings()` → REFACTOR

---

## Best Practices

1. **Start session first:** Always call `start_session()` before tests
2. **Enable brain memory:** Use session tracking for long work
3. **Explicit user repo:** Set `user_repo_root` to avoid confusion
4. **Checkpoint after GREEN:** Create git checkpoints when passing
5. **Validate after REFACTOR:** Run lint before completing cycle

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

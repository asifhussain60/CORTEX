# Debug Orchestrator - Usage Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** January 4, 2026

---

## 🎯 Overview

The Debug Orchestrator provides intelligent, systematic debugging workflows for CORTEX. It automates the process of analyzing bugs, generating hypotheses, collecting evidence, identifying root causes, and proposing fixes.

**Key Features:**
- **Automated bug report parsing** - Extracts errors, stack traces, and context
- **Root cause analysis** - Pattern-based hypothesis generation
- **Fix proposal generation** - Actionable repair strategies
- **Debug marker injection** - Inserts logging/breakpoints strategically
- **Git checkpoint integration** - Safe rollback points
- **Master Orchestrator integration** - Automatic routing from user commands

---

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from src.orchestrators.debug.debug_orchestrator import DebugOrchestrator

# Initialize orchestrator with workspace root
workspace = Path("/path/to/project")
orchestrator = DebugOrchestrator(workspace)

# Parse a bug report
result = orchestrator.parse_bug_report(
    description="Login endpoint returns 500 error",
    error_message="AttributeError: 'NoneType' object has no attribute 'query'",
    stack_trace="""
    File "src/auth.py", line 45, in authenticate
        user = self.db.query(User).filter_by(email=email).first()
    """
)

# Get session summary
summary = orchestrator.get_session_summary()
print(f"Session ID: {summary['session_id']}")
```

### Autonomous Workflow

```python
# Execute complete debugging workflow
result = orchestrator.execute_debug_workflow_autonomously(
    bug_description="User authentication failing with NoneType error",
    error_message="AttributeError: 'NoneType' object has no attribute 'query'",
    auto_apply_fix=False  # Set True to auto-apply highest confidence fix
)

# Check results
print(f"Status: {result['status']}")
print(f"Phases completed: {result['phases_completed']}")
```

---

## 📋 API Reference

### DebugOrchestrator

**Constructor:**
```python
DebugOrchestrator(workspace_root: Path)
```

**Parameters:**
- `workspace_root` (Path): Root directory of the project to debug

---

### Methods

#### parse_bug_report()

Parse bug report and extract key information.

```python
parse_bug_report(
    description: str,
    error_message: Optional[str] = None,
    stack_trace: Optional[str] = None,
    test_failures: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters:**
- `description` (str): Natural language bug description
- `error_message` (str, optional): Error message from logs
- `stack_trace` (str, optional): Stack trace text
- `test_failures` (List[str], optional): List of failing test names

**Returns:**
```python
{
    "status": "parsed",
    "session_id": "uuid-string",
    "parsed_data": {...}
}
```

---

#### run_contextual_review()

Run contextual code review on affected modules.

```python
run_contextual_review() -> Dict[str, Any]
```

**Returns:**
```python
{
    "status": "success",
    "review_results": {...},
    "recommendations": [...]
}
```

---

#### inject_debug_markers()

Inject debug markers (logging, breakpoints) into code.

```python
inject_debug_markers(
    strategy: str = "comprehensive",
    target_files: Optional[List[str]] = None
) -> Dict[str, Any]
```

**Parameters:**
- `strategy` (str): Injection strategy - "minimal", "targeted", or "comprehensive"
- `target_files` (List[str], optional): Specific files to instrument (auto-detected if None)

**Returns:**
```python
{
    "status": "success",
    "markers_injected": 15,
    "locations": [...]
}
```

---

#### analyze_root_cause()

Analyze root cause based on collected evidence.

```python
analyze_root_cause(
    debug_logs: Optional[List[str]] = None
) -> List[Dict[str, Any]]
```

**Parameters:**
- `debug_logs` (List[str], optional): Debug output logs to analyze

**Returns:**
```python
[
    {
        "hypothesis": "Uninitialized database connection",
        "confidence": 0.85,
        "evidence": [...],
        "category": "uninitialized_variable"
    },
    ...
]
```

---

#### generate_fix_proposals()

Generate fix proposals based on root cause analysis.

```python
generate_fix_proposals(max_proposals: int = 3) -> List[Dict[str, Any]]
```

**Parameters:**
- `max_proposals` (int): Maximum number of fix proposals to generate

**Returns:**
```python
[
    {
        "description": "Initialize database connection in __init__",
        "confidence": 0.9,
        "steps": [...],
        "code_changes": {...},
        "risk": "low"
    },
    ...
]
```

---

#### cleanup_debug_markers()

Remove all debug markers from code.

```python
cleanup_debug_markers(verify: bool = True) -> Dict[str, Any]
```

**Parameters:**
- `verify` (bool): Whether to verify cleanup via git diff

**Returns:**
```python
{
    "status": "success",
    "markers_removed": 15,
    "files_cleaned": 5
}
```

---

#### execute_debug_workflow_autonomously()

Execute complete debugging workflow autonomously.

```python
execute_debug_workflow_autonomously(
    bug_description: str,
    error_message: Optional[str] = None,
    stack_trace: Optional[str] = None,
    test_failures: Optional[List[str]] = None,
    target_files: Optional[List[str]] = None,
    auto_apply_fix: bool = False
) -> Dict[str, Any]
```

**Parameters:**
- `bug_description` (str): Bug description
- `error_message` (str, optional): Error message
- `stack_trace` (str, optional): Stack trace
- `test_failures` (List[str], optional): Failing test names
- `target_files` (List[str], optional): Files to instrument
- `auto_apply_fix` (bool): Whether to auto-apply highest confidence fix

**Returns:**
```python
{
    "status": "in_progress" | "completed",
    "phases_completed": [...],
    "parse_result": {...},
    "review_result": {...},
    "root_cause_hypotheses": [...],
    "fix_proposals": [...]
}
```

---

#### get_session_summary()

Get summary of current debugging session.

```python
get_session_summary() -> Optional[Dict[str, Any]]
```

**Returns:**
```python
{
    "session_id": "uuid-string",
    "status": "in_progress",
    "bug_description": "...",
    "phases_completed": [...],
    "git_checkpoints": 2,
    "patterns_learned": 1
}
```

---

## 🎭 Integration with Master Orchestrator

The Debug Orchestrator integrates with CORTEX's Master Orchestrator for automatic routing.

**Trigger Patterns:**
```regex
^(debug|fix bug|troubleshoot|investigate bug|root cause).*$
```

**User Commands:**
- `debug authentication error`
- `fix bug in login module`
- `troubleshoot database connection`
- `investigate bug in payment system`
- `root cause analysis needed`

**Priority:** 50 (medium-high)  
**Mode:** Guided execution (manifest-driven)

---

## 📝 Example Workflows

### Example 1: Database Connection Error

```python
orchestrator = DebugOrchestrator(Path("/app"))

# Parse error
result = orchestrator.parse_bug_report(
    description="Database connection failing on startup",
    error_message="psycopg2.OperationalError: could not connect to server",
    stack_trace="""
    File "src/db.py", line 12, in connect
        conn = psycopg2.connect(DATABASE_URL)
    """
)

# Analyze root cause
hypotheses = orchestrator.analyze_root_cause()
print(f"Top hypothesis: {hypotheses[0]['hypothesis']}")

# Generate fixes
fixes = orchestrator.generate_fix_proposals(max_proposals=3)
for fix in fixes:
    print(f"- {fix['description']} (confidence: {fix['confidence']})")
```

### Example 2: NoneType AttributeError

```python
orchestrator = DebugOrchestrator(Path("/app"))

# Autonomous workflow
result = orchestrator.execute_debug_workflow_autonomously(
    bug_description="User authentication failing",
    error_message="AttributeError: 'NoneType' object has no attribute 'query'",
    target_files=["src/auth.py"],
    auto_apply_fix=False
)

# Review results
if result["status"] == "completed":
    print("✅ Debugging workflow complete")
    print(f"Phases: {', '.join(result['phases_completed'])}")
    print(f"Fix proposals: {len(result['fix_proposals'])}")
```

### Example 3: Debug Marker Workflow

```python
orchestrator = DebugOrchestrator(Path("/app"))

# Parse bug
orchestrator.parse_bug_report("Intermittent timeout in API calls")

# Inject debug markers
injection_result = orchestrator.inject_debug_markers(
    strategy="targeted",
    target_files=["src/api/client.py", "src/api/retry.py"]
)
print(f"Injected {injection_result['markers_injected']} markers")

# ... run application, collect logs ...

# Analyze with debug logs
hypotheses = orchestrator.analyze_root_cause(debug_logs=["output.log"])

# Clean up markers
cleanup_result = orchestrator.cleanup_debug_markers()
print(f"Removed {cleanup_result['markers_removed']} markers")
```

---

## ⚠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'src.orchestrators.debug'"

**Solution:** Ensure PYTHONPATH includes project root:
```bash
export PYTHONPATH=/path/to/CORTEX:$PYTHONPATH
```

### Issue: Debug markers not cleaning up

**Solution:** Use verify flag and check git status:
```python
result = orchestrator.cleanup_debug_markers(verify=True)
if result['status'] != 'success':
    print(f"Cleanup issues: {result['errors']}")
```

### Issue: Low confidence hypotheses

**Solution:** Provide more context:
```python
result = orchestrator.parse_bug_report(
    description="Detailed bug description here",
    error_message="Full error message",
    stack_trace="Complete stack trace",
    test_failures=["test_login", "test_auth"]
)
```

---

## 🔧 Configuration

Debug Orchestrator respects workspace-level settings:

**Git Integration:**
- Checkpoints created before/after marker injection
- Checkpoints created before/after fix application
- Use `git log --grep="debug"` to find checkpoints

**State Persistence:**
- Sessions stored in workspace root
- Use `get_session_summary()` to retrieve state
- Session history tracked automatically

---

## 📚 See Also

- [Master Orchestrator Configuration](../../config/master-orchestrator.yaml)
- [Response Templates](../../response-templates-v4.yaml)
- [Orchestrators Quick Reference](../../documents/orchestrators-quick-ref.md)
- [Brain Protection Rules](../../brain-protection-rules.yaml)

---

**Questions?** Check the [Troubleshooting](#troubleshooting) section or review integration tests in `tests/orchestrators/debug/test_debug_integration.py`.

# Toolkit Manager User Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** December 31, 2025

---

## Overview

The Toolkit Manager is the central orchestration layer for all CORTEX toolkit operations. It provides:

- **Pre-execution validation** via GateKeeper
- **Security checks** and argument sanitization
- **Duplication prevention** through RequestAnalyzer
- **Checkpoint/rollback** for destructive operations
- **Dependency management** between tools
- **Manifest schema validation** (v2)
- **Tamper-evident audit logging**

---

## Quick Start

### Basic Usage

```python
from core.toolkit_manager import ToolkitManager, ExecutionContext

# Initialize
manager = ToolkitManager()

# Execute a tool (async)
result = await manager.execute('align', ['--check-only'])

# Or use sync wrapper
result = manager.execute_sync('align', ['--check-only'])

# Check result
if result.success:
    print(result.stdout)
else:
    print(f"Error: {result.error}")
```

### With Execution Context

```python
context = ExecutionContext(
    tool="cleanup",
    args=["--all"],
    working_dir=Path("/path/to/project"),
    timeout=60,
    dry_run=True,          # Preview without executing
    checkpoint_enabled=True # Auto-checkpoint for rollback
)

result = await manager.execute("cleanup", ["--all"], context)
```

---

## Core Components

### 1. GateKeeper (Pre-execution Validation)

Validates all tool executions before they run:

```python
# Direct validation
validation = manager.gate_keeper.validate_execution("tool-name", args)

if validation.passed:
    # Safe to execute
else:
    for check in validation.checks:
        if not check.passed:
            print(f"{check.name}: {check.message}")
```

**Validation Checks:**
- Tool existence
- Platform compatibility
- Argument sanitization
- Rate limiting
- Permission requirements

### 2. RequestAnalyzer (Duplication Prevention)

Prevents creation of duplicate tools:

```python
from core.request_analyzer import ToolRequest, RecommendationType

request = ToolRequest(
    name="my-formatter",
    description="Format code files",
    capabilities=["format", "lint", "style"]
)

result = manager.request_analyzer.analyze_request(request)

if result.recommendation_type == RecommendationType.BLOCK:
    print(f"Cannot create: {result.recommendation}")
    print(f"Similar tools: {result.overlapping_tools}")
elif result.recommendation_type == RecommendationType.WARN:
    print(f"Warning: {result.recommendation}")
else:
    print("Tool can be created")
```

**Recommendation Types:**
- `ALLOW` - No overlap, creation allowed
- `WARN` - Some overlap, proceed with caution
- `SUGGEST` - High overlap, consider using existing
- `BLOCK` - Too similar to existing tool

### 3. RecoveryManager (Checkpoint/Rollback)

Create checkpoints before destructive operations:

```python
from core.recovery_manager import ExecutionContext as RecoveryContext

# Create checkpoint
context = RecoveryContext(
    tool="cleanup",
    args=["--force"],
    affected_paths=[Path("/path/to/important/file")],
    is_destructive=True
)

checkpoint = manager.recovery_manager.create_checkpoint(context)
print(f"Checkpoint: {checkpoint.id}")

# After something goes wrong...
result = manager.recovery_manager.rollback(checkpoint.id)

if result.success:
    print(f"Restored {len(result.restored_paths)} files")
else:
    print(f"Errors: {result.errors}")
```

**Features:**
- Auto-pruning (keeps max 50 checkpoints)
- JSON persistence across sessions
- State snapshots of affected files

### 4. DependencyManager

Validates and orders tool dependencies:

```python
# Check dependencies
check = manager.dependency_manager.validate_dependencies("deploy-tool")

if not check.satisfied:
    print(f"Missing: {check.missing}")

# Get execution order
order = manager.dependency_manager.get_execution_order(
    ["deploy", "test", "build"]
)
print(f"Run in order: {order}")

# Detect circular dependencies
cycles = manager.dependency_manager.detect_circular()
if cycles:
    print(f"Circular dependencies found: {cycles}")
```

### 5. ManifestSchema (v2 Validation)

Validate tools against manifest v2 schema:

```python
# Validate a tool definition
tool = {
    "name": "my-tool",
    "description": "Does something",
    "command": "my-command",
    # ... other fields
}

result = manager.manifest_schema.validate_tool(tool)

if result.is_valid:
    print("Tool is valid")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

### 6. SecurityGuard (Input Sanitization)

Detect and block dangerous inputs:

```python
# Check arguments for security issues
result = manager.sanitize_arguments(["--path", "../../etc/passwd"])

if not result.safe:
    for violation in result.violations:
        print(f"Blocked: {violation.pattern_type}")
        print(f"  Arg: {violation.argument}")
        print(f"  Severity: {violation.severity}")
```

**Detected Patterns:**
- Shell injection (`;`, `|`, `&`, `` ` ``, `$()`)
- Path traversal (`..`, `/etc/passwd`)
- SQL injection (`' OR 1=1`, `UNION SELECT`)
- XSS (`<script>`, `javascript:`)
- Absolute paths (flagged for review)

### 7. AuditLogger (Tamper-Evident Logging)

Log and query execution events:

```python
from core.audit_logger import ExecutionEvent

# Log an event
event = ExecutionEvent(
    tool="deploy",
    args=["--prod"],
    status="success",
    exit_code=0,
    duration_ms=5000
)
manager.audit_logger.log_execution(event)

# Query recent events
events = manager.audit_logger.get_recent(limit=10)

# Get by tool
deploy_events = manager.audit_logger.get_by_tool("deploy")

# Get statistics
stats = manager.audit_logger.get_statistics()
print(f"Total events: {stats['total_records']}")
```

---

## Execution Context Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `tool` | str | required | Tool name |
| `args` | List[str] | [] | Arguments |
| `working_dir` | Path | cwd | Working directory |
| `timeout` | int | None | Timeout in seconds |
| `capture_output` | bool | True | Capture stdout/stderr |
| `env_vars` | Dict | {} | Environment variables |
| `dry_run` | bool | False | Preview without executing |
| `skip_validation` | bool | False | Skip GateKeeper checks |
| `checkpoint_enabled` | bool | True | Auto-checkpoint |

---

## Execution Result

```python
@dataclass
class ExecutionResult:
    status: ExecutionStatus  # SUCCESS, FAILED, VALIDATION_FAILED, BLOCKED, TIMEOUT
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int
    checkpoint_id: Optional[str]
    validation_result: Optional[Any]
    error: Optional[str]
    tool: str
    args: List[str]
    timestamp: datetime
    
    @property
    def success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS and self.exit_code == 0
```

---

## Error Handling

### Common Exceptions

```python
from core.exceptions import (
    ToolkitError,          # Base exception
    ToolNotFoundError,     # Tool doesn't exist
    ValidationError,       # Validation failed
    ExecutionError,        # Execution failed
    SecurityViolationError # Security check failed
)

try:
    result = await manager.execute("unknown-tool", [])
except ToolNotFoundError as e:
    print(f"Tool not found: {e}")
except SecurityViolationError as e:
    print(f"Security violation: {e}")
except ToolkitError as e:
    print(f"General error: {e}")
```

---

## Best Practices

### 1. Always Use Dry Run for Destructive Operations

```python
# First, preview
result = await manager.execute(
    "cleanup",
    ["--all"],
    ExecutionContext(dry_run=True)
)
print(result.stdout)  # See what would happen

# Then execute if safe
result = await manager.execute("cleanup", ["--all"])
```

### 2. Check Dependencies Before Complex Workflows

```python
tools_to_run = ["build", "test", "deploy"]

# Validate all dependencies
for tool in tools_to_run:
    check = manager.dependency_manager.validate_dependencies(tool)
    if not check.satisfied:
        print(f"Cannot run {tool}: missing {check.missing}")
        return

# Get proper order
ordered = manager.dependency_manager.get_execution_order(tools_to_run)

# Execute in order
for tool in ordered:
    result = await manager.execute(tool, [])
    if not result.success:
        print(f"Failed at {tool}")
        break
```

### 3. Use Checkpoints for Rollback

```python
# Before dangerous operations
checkpoint = manager.recovery_manager.create_checkpoint(context)

try:
    result = await manager.execute("risky-tool", args)
    if not result.success:
        manager.recovery_manager.rollback(checkpoint.id)
except Exception as e:
    manager.recovery_manager.rollback(checkpoint.id)
    raise
```

### 4. Validate New Tool Requests

```python
# Before creating new tools
request = ToolRequest(name=name, description=desc, capabilities=caps)
analysis = manager.request_analyzer.analyze_request(request)

if analysis.recommendation_type == RecommendationType.BLOCK:
    print(f"Use existing tool: {analysis.overlapping_tools[0].name}")
    return
```

---

## Configuration

### Toolkit Root

The manager auto-discovers the toolkit root, or specify explicitly:

```python
manager = ToolkitManager(toolkit_root=Path("/path/to/cortex-toolkit"))
```

### Logging

```python
import logging
logging.getLogger("core.toolkit_manager").setLevel(logging.DEBUG)
```

---

## Component Architecture

```
ToolkitManager
├── ToolkitRegistry      # Tool catalog
├── GateKeeper           # Pre-execution validation
├── RequestAnalyzer      # Duplication prevention
│   └── CapabilityMatrix # Keyword similarity
├── RecoveryManager      # Checkpoint/rollback
├── DependencyManager    # Dependency graph
│   └── DependencyGraph  # Graph operations
├── ManifestSchema       # v2 validation
├── SecurityGuard        # Input sanitization
└── AuditLogger          # Tamper-evident logging
```

---

## API Reference

### ToolkitManager Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `execute(tool, args, context)` | `ExecutionResult` | Async execute tool |
| `execute_sync(tool, args, context)` | `ExecutionResult` | Sync execute tool |
| `validate_tool(tool, args)` | `dict` | Validate without executing |
| `list_tools(category)` | `List[dict]` | List available tools |
| `get_tool_info(name)` | `Optional[dict]` | Get tool details |
| `sanitize_arguments(args)` | `SanitizeResult` | Check argument safety |
| `check_privilege_level(tool, level)` | `bool` | Check privileges |

---

## Changelog

### 1.0.0 (December 2025)
- Initial release
- Phase 1-7 implementation complete
- 329 tests passing

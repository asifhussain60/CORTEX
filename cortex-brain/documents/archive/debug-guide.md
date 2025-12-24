# CORTEX Debug System Guide

**Version:** 1.0.0  
**Status:** ✅ PRODUCTION  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## 🎯 Overview

The CORTEX Debug System provides runtime instrumentation and debug logging **without modifying source files**. It uses Python decorators to wrap functions at runtime, capturing execution flow, variables, timing, and errors - then removes all instrumentation when debugging ends.

---

## ⚡ Quick Start

### Start Debugging

Natural language commands:
```
debug the planner agent
trace authentication flow
instrument payment processing
```

Or explicit targets:
```
debug planner
debug PlannerAgent
debug plan_feature function
```

### Stop Debugging

```
stop debug
end debug session
```

### Check Status

```
debug status
show debug sessions
```

---

## 📋 Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `debug [target]` | Start debug session | `debug planner` |
| `stop debug` | Stop active session | `stop debug` |
| `debug status` | Show active sessions | `debug status` |
| `debug report [id]` | Get detailed report | `debug report auth-123` |
| `debug history` | Show recent sessions | `debug history` |

---

## 🔧 How It Works

### 1. Intent Detection

CORTEX detects debug keywords:
- `debug`
- `trace`
- `instrument`
- `log`
- `watch`
- `profile`

### 2. Target Discovery

Auto-discovers module/function from natural language:
```
"debug the planner" → finds cortex_brain.agents.planner module
"debug PlannerAgent" → finds PlannerAgent class in planner module
```

### 3. Runtime Instrumentation

Wraps functions with decorators that capture:
- **Entry:** Function name, arguments, timestamp
- **Exit:** Return value, execution time
- **Errors:** Exception type, message, stack trace

### 4. Logging

All data logged to:
- **File:** `cortex-brain/debug-sessions/[session-id]/debug.log`
- **Database:** `cortex-brain/tier1-working-memory.db`
  - `debug_sessions` table (metadata)
  - `debug_logs` table (execution logs)

### 5. Auto-Cleanup

When session ends:
- All decorators removed
- Original functions restored
- Summary generated
- Zero source file changes

---

## 📊 Debug Session Output

### Log File Format

```
2025-11-24T10:30:15.123456 [ENTRY] planner.plan_feature#1
  {
    "args": ["authentication_system"],
    "kwargs": {"user_id": 12345}
  }

2025-11-24T10:30:15.456789 [EXIT] planner.plan_feature#1
  {
    "result": {"status": "success", "plan_id": "PLAN-2025-001"},
    "duration_ms": 333.33
  }
```

### Summary JSON

```json
{
  "session_id": "planner-abc123",
  "duration_seconds": 45.67,
  "instrumented_functions": [
    "planner.plan_feature",
    "planner.validate_requirements",
    "planner.generate_tasks"
  ],
  "call_count": 127,
  "error_count": 2,
  "log_file": "/path/to/cortex-brain/debug-sessions/planner-abc123/debug.log"
}
```

---

## 🎨 Use Cases

### 1. Troubleshooting Production Issues

```
User: "The planner is failing for large projects"

You: "debug planner"

CORTEX: ✅ Debug session started
        📊 Logging all planner function calls
        
User: [Reproduces issue]

You: "stop debug"

CORTEX: 📊 Session Summary:
        - 247 function calls
        - 3 errors (all in validate_requirements)
        - Log: cortex-brain/debug-sessions/planner-xyz/debug.log
        
        🔍 Found issue: validate_requirements fails when
        project has >50 files (memory overflow)
```

### 2. Performance Profiling

```
You: "debug authentication"

[Run authentication flow]

You: "stop debug"

CORTEX: 📊 Performance Report:
        - auth.login: 1.2s (too slow!)
        - auth.validate_token: 0.05s
        - auth.check_permissions: 0.8s (database query bottleneck)
```

### 3. Understanding Execution Flow

```
You: "debug test generator"

[Run test generation]

You: "debug report"

CORTEX: 📊 Execution Flow:
        1. test_generator.generate() (entry)
        2. └─ test_generator.discover_elements() (56ms)
        3.    └─ view_discovery.scan_files() (432ms)
        4. └─ test_generator.create_selectors() (12ms)
        5. └─ test_generator.write_tests() (89ms)
        6. test_generator.generate() (exit, 589ms total)
```

---

## 🔒 Safety & Privacy

### Production Safety

- **Opt-in only:** Debug mode only activates when explicitly requested
- **Isolated sessions:** Each session has separate ID and log directory
- **No data leaks:** All logs stored locally, never transmitted
- **Rollback-safe:** Restart process = all instrumentation removed

### Source File Safety

- **Zero modifications:** Original source files never touched
- **No merge conflicts:** Debug changes never committed to git
- **Automatic cleanup:** All decorators removed when session ends
- **Reversible:** Stop session = pristine state restored

### Privacy Protection

- **Local storage only:** All data in `cortex-brain/` directory
- **No telemetry:** Debug data never sent to external services
- **User control:** User decides when to start/stop debugging
- **Selective logging:** Only captures explicitly instrumented functions

---

## 🧪 Testing

Run debug system tests:
```bash
pytest tests/test_debug_system.py -v
```

Test coverage:
- ✅ Session creation and lifecycle
- ✅ Runtime instrumentation
- ✅ Function timing and call tracking
- ✅ Error tracking and logging
- ✅ Argument/return value capture
- ✅ Intent detection
- ✅ Multi-session isolation
- ✅ Auto-cleanup validation

---

## 📚 API Reference

### DebugSessionManager

Main manager for debug sessions.

```python
from cortex_brain.agents.debug_session_manager import get_debug_manager

manager = get_debug_manager()

# Start session
session = manager.start_session(
    target_module="cortex_brain.agents.planner",
    session_name="planner_debug"
)

# Stop session
summary = manager.stop_session(session.session_id)

# Get active sessions
active = manager.get_active_sessions()

# Get history
history = manager.get_session_history(limit=10)
```

### DebugAgent

High-level agent for debug operations.

```python
from cortex_brain.agents.debug_agent import DebugAgent

agent = DebugAgent(brain_root)

# Detect debug intent
intent = agent.detect_debug_intent("debug the planner")

# Start debug session
session = agent.start_debug_session(target="planner")

# Instrument module
count = agent.instrument_module(session, "cortex_brain.agents.planner")

# Get session report
report = agent.get_session_report(session.session_id)

# Stop session
summary = agent.stop_debug_session(session.session_id)
```

### DebugSystemIntegration

Integration with CORTEX orchestrator.

```python
from cortex_brain.agents.debug_integration import DebugSystemIntegration

integration = DebugSystemIntegration(brain_root)

# Process debug message
result = integration.process_message("debug planner")

# Get capabilities
capabilities = integration.get_debug_capabilities()
```

---

## 🛠️ Advanced Usage

### Manual Instrumentation

```python
session = manager.start_session(session_name="manual")

# Instrument specific function
from my_module import my_function
instrumented_func = session.instrument_function(my_function, "my_module")

# Use instrumented function
result = instrumented_func(arg1, arg2)

# Stop session (auto-cleanup)
manager.stop_session(session.session_id)
```

### Context Manager

```python
import my_module

with session.instrument_module(my_module):
    # All my_module functions are instrumented here
    my_module.some_function()
    my_module.another_function()

# Instrumentation automatically removed after block
```

### Custom Filters

```python
# Only instrument functions matching pattern
def should_instrument(func_name):
    return func_name.startswith("test_")

count = agent.instrument_module(
    session=session,
    module_path="my_module",
    function_filter=should_instrument
)
```

---

## 🚀 Integration Points

### Deployment Pipeline

Debug system tests run automatically in:
- `scripts/run_tests.sh` - Full test suite
- `scripts/validate_deployment.sh` - Pre-deployment validation

### Documentation Orchestrator

Auto-generates debug system documentation:
- Entry in `CORTEX.prompt.md`
- Capability definition in `capabilities.yaml`
- This guide (`debug-guide.md`)

### Health Check

Debug system health validated in:
- Database integrity (debug_sessions, debug_logs tables)
- Session directory structure
- Manager initialization

---

## 📖 Related Documentation

- **Main Entry Point:** `.github/prompts/CORTEX.prompt.md` (Debug System section)
- **Capabilities:** `cortex-brain/capabilities.yaml` (debug_system entry)
- **Tests:** `tests/test_debug_system.py`
- **Implementation:** 
  - `cortex-brain/agents/debug_session_manager.py`
  - `cortex-brain/agents/debug_agent.py`
  - `cortex-brain/agents/debug_integration.py`

---

**Last Updated:** 2025-11-24  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

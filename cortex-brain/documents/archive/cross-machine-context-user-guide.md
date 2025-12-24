# Cross-Machine Context Orchestrator - User Guide

**Version:** 1.0  
**Created:** December 12, 2025  
**Author:** Asif Hussain

---

## 🎯 Overview

The **Cross-Machine Context Orchestrator** enables seamless workflows between Windows and Mac by automatically detecting OS, shell, runtimes, and providing path/command translation.

**Problem Solved:** Manual path translation (`C:\PROJECTS\` → `/Users/asifhussain/PROJECTS/`) and shell syntax adaptation when switching machines.

**Evidence:** Chat session analysis revealed this pain point during Platform.Classic modernization work.

---

## 🚀 Quick Start

### Automatic Detection

Context is detected automatically on session start:

```python
from src.orchestrators.cross_machine_context_orchestrator import (
    CrossMachineContextOrchestrator
)

orchestrator = CrossMachineContextOrchestrator()
context = orchestrator.detect_machine_context()

print(f"OS: {context.os}")  # "Windows", "Mac", or "Linux"
print(f"Shell: {context.shell}")  # "PowerShell", "bash", "zsh", "cmd"
print(f"Python: {context.python_version}")
print(f"Git: {context.git_version}")
```

### Path Translation

```python
# Windows to Unix
unix_path = orchestrator.translate_path(
    "C:\\Projects\\CORTEX\\src\\main.py",
    target_os="Unix"
)
# Result: /c/Projects/CORTEX/src/main.py

# Unix to Windows
win_path = orchestrator.translate_path(
    "/Users/asifhussain/PROJECTS/CORTEX/src/main.py",
    target_os="Windows"
)
# Result: C:\Users\asifhussain\PROJECTS\CORTEX\src\main.py
```

### Shell Syntax Adaptation

```python
# Adapt command for target shell
bash_cmd = orchestrator.adapt_command("dir /s", target_shell="bash")
# Result: "ls -R"

# Format environment variables
ps_var = orchestrator.format_env_var("PATH", shell="PowerShell")
# Result: "$env:PATH"

bash_var = orchestrator.format_env_var("PATH", shell="bash")
# Result: "$PATH"

# Line continuation characters
ps_cont = orchestrator.get_line_continuation("PowerShell")  # "`"
bash_cont = orchestrator.get_line_continuation("bash")  # "\\"
```

---

## 📊 Machine Context Structure

```python
@dataclass
class MachineContext:
    os: str                    # "Windows" | "Mac" | "Linux"
    os_version: str
    shell: str                 # "PowerShell" | "bash" | "zsh" | "cmd"
    python_version: Optional[str]
    dotnet_version: Optional[str]
    node_version: Optional[str]
    git_version: Optional[str]
    home_directory: str
    working_directory: str
    path_separator: str        # "\\" or "/"
    line_ending: str           # "\\r\\n" or "\\n"
    case_sensitive: bool       # False for Windows, True for Unix
    last_active_machine: str   # Machine hostname
```

---

## 🧠 Brain Tier 1 Integration

Context is automatically stored in `cortex-brain/tier1/machine-context.json` for persistence:

```python
# Save context
orchestrator.save_to_brain(context)

# Load stored context
stored_context = orchestrator.load_from_brain()

# Detect changes
changed = orchestrator.has_context_changed(old_context, new_context)
if changed:
    print("Machine context has changed!")
```

---

## ⚙️ Configuration

### Supported Platforms

| Platform | OS Detection | Shell Detection | Runtime Detection |
|----------|--------------|-----------------|-------------------|
| **Windows** | ✅ Windows | PowerShell, cmd | .NET, Python, Node, Git |
| **macOS** | ✅ Mac (Darwin) | bash, zsh | Python, Node, Git |
| **Linux** | ✅ Linux | bash, zsh | Python, Node, Git |

### Performance

- **Detection Time:** <2 seconds (acceptance criteria)
- **Context Size:** ~500 bytes (JSON storage)
- **Memory Footprint:** <5 MB

---

## 🔧 Advanced Usage

### Custom Path Translation Rules

```python
from src.operations.utilities.path_translator import PathTranslator

# Check path types
is_windows = PathTranslator.is_windows_absolute("C:\\Projects\\CORTEX")
is_unix = PathTranslator.is_unix_absolute("/Users/asifhussain")
is_unc = PathTranslator.is_unc_path("\\\\\\\\server\\\\share")

# Direct translation
translated = PathTranslator.translate(
    "C:\\Projects\\CORTEX",
    target_os="Unix"
)
```

### Custom Shell Adaptation

```python
from src.operations.utilities.shell_adapter import ShellAdapter

# Adapt commands
adapted = ShellAdapter.adapt_command("type file.txt", target_shell="bash")
# Result: "cat file.txt"

# Environment variable formatting
env_var = ShellAdapter.format_env_var("JAVA_HOME", shell="zsh")

# Path separator for shell
separator = ShellAdapter.get_path_separator("PowerShell")  # ";"
```

---

## 🚨 Troubleshooting

### Context Not Detected

**Symptom:** `context.os` is None or incorrect

**Solution:** Check Python version (3.8+ required) and `platform` module availability

```python
import platform
print(platform.system())  # Should return "Windows", "Darwin", or "Linux"
```

### Runtime Not Detected

**Symptom:** `context.dotnet_version` is None despite SDK installed

**Solution:** Ensure runtime is in PATH

```bash
# Windows PowerShell
$env:PATH -split ";" | Select-String "dotnet"

# Unix bash/zsh
echo $PATH | tr ":" "\\n" | grep dotnet
```

### Path Translation Issues

**Symptom:** Paths not translating correctly

**Solution:** Check for edge cases:

- **UNC paths:** `\\\\\\\\server\\\\share` requires special handling
- **Relative paths:** `src/main.py` preserves format
- **Home directory:** `~` expands before translation

---

## 📚 Integration Examples

### With Planning Orchestrator

```python
from src.orchestrators.cross_machine_context_orchestrator import (
    CrossMachineContextOrchestrator
)

class PlanningOrchestrator:
    def __init__(self):
        self.context_orchestrator = CrossMachineContextOrchestrator()
    
    def execute_phase(self, phase):
        context = self.context_orchestrator.detect_machine_context()
        
        # Adapt paths for current OS
        output_path = self.context_orchestrator.translate_path(
            phase.output_path,
            target_os=context.os
        )
        
        # Generate shell-specific commands
        command = self.context_orchestrator.adapt_command(
            phase.command,
            target_shell=context.shell
        )
```

### With TDD Orchestrator

```python
class TDDOrchestrator:
    def run_tests(self):
        context_orch = CrossMachineContextOrchestrator()
        context = context_orch.detect_machine_context()
        
        # Adapt test runner command
        if context.shell == "PowerShell":
            cmd = "pytest tests/"
        else:
            cmd = "./scripts/run_tests.sh"
```

---

## ✅ Testing

Run the comprehensive test suite:

```bash
pytest tests/orchestrators/test_cross_machine_context_orchestrator.py -v
```

**Coverage:**
- Phase 4.1: OS and shell detection (8 tests)
- Phase 4.2: Path translation (5 tests)
- Phase 4.3: Shell syntax adapters (4 tests)
- Phase 4.4: Runtime detection (4 tests)
- Phase 4.5: Brain integration (3 tests)
- Performance: <2 second detection (1 test)

**Total:** 25 tests, 100% pass rate

---

## 🔍 Next Steps

1. **Integrate with Planning System 2.0** - Use context for cross-platform plan execution
2. **Environment Diagnostics** - Feature 1 will leverage runtime detection
3. **TDD Environment Gates** - Feature 6 will use environment validation
4. **Dashboard Integration** - Show current machine context in admin dashboard

---

## 📄 API Reference

See inline documentation in:
- `src/orchestrators/cross_machine_context_orchestrator.py`
- `src/operations/utilities/path_translator.py`
- `src/operations/utilities/shell_adapter.py`

---

**Questions?** See main CORTEX documentation or contact Asif Hussain.

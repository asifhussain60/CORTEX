# CORTEX Operations Reference

**Available Operations:**

| Operation | Natural Language Examples | Status | What It Does |
|-----------|--------------------------|--------|--------------|
| **Demo** | "demo", "show capabilities", "tutorial" | ✅ READY | Interactive walkthrough of CORTEX |
| **Setup** | "setup", "configure", "initialize" | ✅ READY | Configure development environment |
| **Feature Planning** | "plan a feature", "let's plan", "interactive planning" | ✅ READY | Interactive feature breakdown with Work Planner agent (see `#file:prompts/shared/help_plan_feature.md`) |
| **Design Sync** | "sync design", "align design", "consolidate status" | ✅ READY | Synchronize design docs with implementation |
| **Story Refresh** | "refresh story", "update story" | 🟡 VALIDATION | Validate CORTEX story structure (validation-only, see limitations) |
| **Cleanup** | "cleanup", "clean workspace", "tidy up" | 🟡 PARTIAL | Clean temp files, optimize databases |
| **Optimize** | "optimize codebase", "analyze quality", "check health" | ✅ READY | Run CORTEX optimizer (token analysis, YAML validation, plugin health, DB optimization) |
| **Documentation** | "update docs", "build docs" | ⏸️ PENDING | Generate/build documentation site |
| **Brain Protection** | "check brain", "validate protection" | ⏸️ PENDING | Validate brain integrity |
| **Run Tests** | "run tests", "test suite" | ⏸️ PENDING | Execute test suite with coverage |

**Legend:**
- ✅ READY - Fully implemented and tested with real logic
- 🟡 VALIDATION - Validation-only (no transformation yet)
- 🟡 PARTIAL - Core works, integration testing in progress
- ⏸️ PENDING - Architecture ready, modules pending
- 🎯 PLANNED - Design phase (CORTEX 2.1+)

**Try it now:**
```python
from src.operations import execute_operation

# All natural language - no slash commands needed!
report = execute_operation('setup')  # Works!
report = execute_operation('plan a feature')  # Works! (NEW in 2.1)
report = execute_operation('refresh story')  # Works!
report = execute_operation('cleanup', profile='standard')  # Works!
report = execute_operation('optimize codebase')  # Works! (runs admin optimizer)
```

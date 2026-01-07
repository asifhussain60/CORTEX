# Current Architecture Analysis

**Document:** Context - Current Toolkit Architecture  
**Created:** December 31, 2025  
**Author:** Asif Hussain

---

## 📊 Existing Component Inventory

### Core Components

| Component | File | Purpose | Status |
|-----------|------|---------|--------|
| **ToolkitRegistry** | `shared/toolkit_registry.py` | Tool discovery & invocation | ✅ Production |
| **ToolkitConfig** | `shared/config.py` | Hierarchical configuration | ✅ Production |
| **BaseCLIWrapper** | `cli/wrappers/base_wrapper.py` | CLI interface pattern | ✅ Production |

### Category Structure

```
cortex-toolkit/
├── core/
│   ├── brain/        → 4 tools (align, cleanup, healthcheck, optimize)
│   ├── operations/   → 3 tools (deploy, review, sanitize)
│   ├── planning/     → 3 tools (plan, ado, planning-file-manager)
│   ├── generators/   → 5 tools (schema extraction, OpenAPI generation)
│   └── utilities/    → 6 tools (tokens, version, scaffolds)
├── analytics/        → 4 tools (profile, metrics, visualize, uml)
├── documentation/    → 7 tools (docs-gen, html-tools, sitemap)
├── testing/          → 3 tools (validate, performance, no-mocks)
├── migration/        → 2 tools (schema, version)
├── maintenance/      → 6 tools (cleanup-temp, duplicates, caches)
└── shared/           → 4 support modules
```

**Total:** 28+ tools across 9 categories

---

## 🔍 Current Flow Analysis

### Tool Invocation Path (Current)

```
User Request
     ↓
ToolkitRegistry.invoke_tool(name, args)
     ↓
├─ get_tool(name) → Lookup in manifest
├─ is_platform_supported(name) → Platform check
├─ resolve_script_path(name) → Get script location
     ↓
subprocess.run([python, script, *args])
     ↓
Exit Code Returned
```

### Missing Validation Points

```
❌ No pre-execution validation layer
❌ No argument sanitization
❌ No duplication check for new tools
❌ No dependency resolution
❌ No checkpoint/rollback
❌ No audit logging
❌ No rate limiting
```

---

## 📁 Key Files Review

### 1. toolkit_registry.py (387 lines)

**Strengths:**
- Clean class-based design
- Auto-discovery of toolkit root
- Platform compatibility checking
- CLI entry point

**Gaps:**
- No validation before invocation
- No concurrency control
- No error recovery
- Linear tool search O(n)

**Critical Methods:**
```python
def invoke_tool(self, name: str, args: List[str] = None, **kwargs) -> int:
    # Direct subprocess call - no validation
    return self._run_python_script(script_path, args, **kwargs)
```

### 2. config.py (181 lines)

**Strengths:**
- Hierarchical config (Env > User > Repo > Global)
- Path alias support
- Singleton pattern

**Gaps:**
- No validation of config values
- No schema for config structure
- Silent failures on parse errors

### 3. base_wrapper.py (319 lines)

**Strengths:**
- Template pattern for CLI wrappers
- Progress indicators
- Consistent interface

**Gaps:**
- No pre-execution hooks
- No transaction support
- No rollback capability

---

## 🔴 Critical Gaps Identified

### 1. Race Conditions
```
Problem: Multiple processes can invoke same tool simultaneously
Risk: Data corruption, inconsistent state
Current: No locking mechanism
```

### 2. Duplication Risk
```
Problem: No check before tool creation
Risk: Redundant tools (cleanup vs full_cleanup vs cleanup-temp)
Current: Manual review only
```

### 3. Security Vulnerabilities
```
Problem: Arguments passed directly to subprocess
Risk: Shell injection, path traversal
Current: No sanitization
```

### 4. No Recovery
```
Problem: Failed operations leave partial state
Risk: Corrupted toolkit state
Current: Manual cleanup required
```

### 5. No Audit Trail
```
Problem: No logging of tool executions
Risk: Cannot trace issues, no compliance
Current: Only console output
```

---

## 📈 Metrics (Current State)

| Metric | Value |
|--------|-------|
| Total Tools | 28 |
| Categories | 9 |
| CLI Wrappers | 13 |
| Test Coverage | ~60% (estimated) |
| Documentation | Complete |
| Security Validation | None |
| Concurrency Control | None |
| Recovery Support | None |

---

## 🎯 Integration Points for Toolkit Manager

### 1. Registry Integration
```python
# Current
registry.invoke_tool('align', args)

# After Toolkit Manager
manager.execute('align', args)  # Wraps registry
```

### 2. Wrapper Integration
```python
# Current base_wrapper.py
def execute(self) -> OperationResult:
    orchestrator = self.get_orchestrator()
    return orchestrator.execute(context)

# After Toolkit Manager
def execute(self) -> OperationResult:
    return self.manager.execute(
        self.get_tool_name(),
        self.build_context()
    )
```

### 3. Orchestrator Integration
```python
# Current planning_orchestrator.py
scaffold = PlanScaffoldGenerator()
scaffold.create_scaffold(plan_name)

# After Toolkit Manager
result = manager.execute('plan-scaffold', [plan_name])
```

---

## 📊 Dependency Map (Existing)

```
ToolkitRegistry
├── toolkit-manifest.yaml (data)
├── config.py (configuration)
└── subprocess (execution)

BaseCLIWrapper
├── ToolkitRegistry (optional)
├── argparse (CLI)
└── src.utils.progress_decorator

full_cleanup.py
├── clear_caches.py
├── validate_templates.py
├── remove_legacy_refs.py
└── detect_duplicates.py
```

---

## 🔗 Related Context
- [Gap Analysis](./gap-analysis.md)
- [Master Plan](../00-master-plan.md)

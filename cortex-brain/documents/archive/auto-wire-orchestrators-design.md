# 🔧 Auto-Wiring Orchestrator Script - Design Specification

**Date:** December 29, 2025  
**Author:** Asif Hussain  
**Status:** 📋 DESIGN PHASE  
**Related:** `maintenance-wiring-persistence-gap.md`

---

## 🎯 Purpose

Create an automated script that **repairs wiring gaps** identified by maintenance diagnostics, generating git-committable source code changes that persist across machines.

---

## 🏗️ Architecture

### Script Location

```
scripts/
└── auto_wire_orchestrators.py  # NEW - Auto-repair wiring gaps
```

### Integration Points

```
Maintenance Pipeline:
1. cortex_system_doctor.py (DIAGNOSE gaps)
2. auto_wire_orchestrators.py (FIX gaps) ← NEW
3. check_wiring_integrity.py (VERIFY 100%)
```

---

## 📋 Requirements

### Functional Requirements

1. **Parse Wiring Reports** - Read JSON output from `check_wiring_integrity.py`
2. **Identify Fix Targets** - Determine which files need modification
3. **Generate Code Patches** - Create AST-based or regex-based patches
4. **Apply Fixes Safely** - Modify source files with backups
5. **Verify Success** - Re-run wiring check to confirm 100%
6. **Generate Summary** - Report what was fixed and where

### Non-Functional Requirements

1. **Idempotent** - Running twice produces same result
2. **Safe** - Creates backups before modifying files
3. **Reversible** - Provides undo mechanism
4. **Auditable** - Logs all changes with timestamps
5. **Testable** - Dry-run mode for validation

---

## 🧩 Wiring Fix Patterns

### Pattern 1: Decision Logic Wiring

**Problem:** `_should_use_interactive_mode()` exists but not called in `execute()`

**Source File:** `src/orchestrators/planning/planning_orchestrator.py`

**Current Code (Broken):**
```python
def execute(self, **kwargs) -> OrchestratorResult:
    """Execute planning orchestrator."""
    try:
        # Validate inputs
        validation = self._validate_inputs(**kwargs)
        if not validation.valid:
            return self._create_error_result(validation.errors)
        
        # Generate plan (always autonomous mode)
        result = self._execute_autonomous_mode(**kwargs)
        return result
    except Exception as e:
        return self._create_error_result([str(e)])
```

**Fixed Code (Wired):**
```python
def execute(self, **kwargs) -> OrchestratorResult:
    """Execute planning orchestrator."""
    try:
        # Validate inputs
        validation = self._validate_inputs(**kwargs)
        if not validation.valid:
            return self._create_error_result(validation.errors)
        
        # ✅ ADDED: Check if interactive mode is needed
        if self._should_use_interactive_mode(**kwargs):
            return self._execute_interactive_mode(**kwargs)
        
        # Execute autonomous mode
        result = self._execute_autonomous_mode(**kwargs)
        return result
    except Exception as e:
        return self._create_error_result([str(e)])
```

**AST Patch Logic:**
```python
def wire_decision_logic(file_path: Path, method_name: str = "execute"):
    """Wire interactive mode decision logic into execute method."""
    tree = ast.parse(file_path.read_text())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            # Find validation block
            # Insert conditional after validation
            # Add: if self._should_use_interactive_mode(**kwargs): ...
            pass
    
    # Write modified AST back to file
```

---

### Pattern 2: Agent Registration Wiring

**Problem:** No `agent_registry.py` file exists, or `InteractivePlanner` not registered

**Target File:** `src/cortex_agents/agent_registry.py` (may not exist)

**Expected Code:**
```python
"""
CORTEX Agent Registry

Central registry for all CORTEX agents.
"""

from typing import Dict, Type
from src.cortex_agents.planning_agent import PlanningAgent
from src.cortex_agents.review_agent import ReviewAgent
from src.cortex_agents.interactive_planner import InteractivePlanner

AGENT_REGISTRY: Dict[str, Type] = {
    "planning": PlanningAgent,
    "review": ReviewAgent,
    "interactive_planning": InteractivePlanner,  # ✅ ADDED
}

def get_agent(agent_name: str):
    """Get agent by name."""
    return AGENT_REGISTRY.get(agent_name)
```

**Creation Logic:**
```python
def create_agent_registry(agents_dir: Path):
    """Create agent_registry.py if missing."""
    registry_path = agents_dir / "agent_registry.py"
    
    if registry_path.exists():
        # Update existing registry
        tree = ast.parse(registry_path.read_text())
        # Add missing agent imports and registrations
    else:
        # Create new registry from template
        template = AGENT_REGISTRY_TEMPLATE
        registry_path.write_text(template)
```

---

### Pattern 3: Execution Method Wiring

**Problem:** `_execute_interactive_mode()` doesn't exist or isn't complete

**Target File:** `src/orchestrators/planning/planning_orchestrator.py`

**Expected Method:**
```python
def _execute_interactive_mode(self, **kwargs) -> OrchestratorResult:
    """
    Execute planning in interactive mode with user collaboration.
    
    Args:
        **kwargs: Planning parameters
        
    Returns:
        OrchestratorResult with interactive session results
    """
    from src.cortex_agents.interactive_planner import InteractivePlanner
    from src.orchestrators.planning.interactive_session import PlanningSession
    
    # Initialize interactive agent
    agent = InteractivePlanner(config=self.config)
    
    # Create session
    session = PlanningSession(
        feature_name=kwargs.get("feature_name"),
        user_context=kwargs.get("context"),
        agent=agent
    )
    
    # Run interactive workflow
    result = session.run()
    
    return self._create_success_result(result)
```

**Generation Logic:**
```python
def wire_interactive_execution(file_path: Path):
    """Add _execute_interactive_mode method if missing."""
    tree = ast.parse(file_path.read_text())
    
    # Check if method exists
    method_exists = any(
        node.name == "_execute_interactive_mode"
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    )
    
    if not method_exists:
        # Generate method from template
        # Insert after _should_use_interactive_mode
        pass
```

---

### Pattern 4: Operations Config Wiring

**Problem:** Orchestrator not registered in `cortex-operations.yaml`

**Target File:** `cortex-operations.yaml`

**Expected Structure:**
```yaml
operations:
  planning:
    handler: planning_orchestrator
    orchestrator: PlanningOrchestrator
    interactive_mode: true  # ✅ ADDED
    triggers:
      - plan
      - create a plan
      - make a plan
    output: cortex-brain/documents/planning/active/{NAME}/
```

**YAML Patch Logic:**
```python
def wire_operations_config(config_path: Path, orchestrator_name: str):
    """Wire orchestrator into cortex-operations.yaml."""
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    if orchestrator_name not in config.get("operations", {}):
        config["operations"][orchestrator_name] = {
            "handler": f"{orchestrator_name}_orchestrator",
            "orchestrator": f"{orchestrator_name.title()}Orchestrator",
            "interactive_mode": True,
            "triggers": [orchestrator_name],
            "output": f"cortex-brain/documents/{orchestrator_name}/active/{{NAME}}/"
        }
    
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
```

---

## 🎨 Script Interface

### Command-Line Interface

```bash
# Show what would be fixed (dry-run, default)
python3 scripts/auto_wire_orchestrators.py

# Fix all wiring gaps
python3 scripts/auto_wire_orchestrators.py --execute

# Fix specific orchestrator only
python3 scripts/auto_wire_orchestrators.py --orchestrator planning --execute

# Generate detailed report
python3 scripts/auto_wire_orchestrators.py --report

# Undo last auto-wiring
python3 scripts/auto_wire_orchestrators.py --undo

# Verify fixes without re-running wiring check
python3 scripts/auto_wire_orchestrators.py --verify
```

### Output Format

```
🔧 CORTEX Auto-Wiring Script v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Analyzing Wiring Gaps...
✅ Found wiring report: cortex-brain/health-reports/wiring-report-20251229_103045.json

📋 Wiring Gaps Detected:

┌─────────────────────────────────────────────────────────────────┐
│ Planning Orchestrator                                           │
├─────────────────────────────────────────────────────────────────┤
│ ❌ Decision Logic: Not called in execute()                     │
│ ❌ Agent Registration: InteractivePlanner missing               │
│ ✅ Interactive Method: Exists but needs agent wiring           │
│ ❌ Operations Config: interactive_mode not set                  │
└─────────────────────────────────────────────────────────────────┘

🔧 Applying Fixes...

[1/4] Wiring decision logic in planning_orchestrator.py...
  ├─ Backup created: planning_orchestrator.py.bak.20251229_103045
  ├─ Inserted interactive mode check after validation block
  └─ ✅ SUCCESS (18 lines modified)

[2/4] Creating agent registry...
  ├─ File created: src/cortex_agents/agent_registry.py
  ├─ Registered: InteractivePlanner
  └─ ✅ SUCCESS (23 lines added)

[3/4] Wiring interactive execution method...
  └─ ⏭️  SKIPPED (method already exists)

[4/4] Updating cortex-operations.yaml...
  ├─ Backup created: cortex-operations.yaml.bak.20251229_103045
  ├─ Added: interactive_mode: true
  └─ ✅ SUCCESS (1 field modified)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Auto-Wiring Complete!

📊 Summary:
  • Files Modified: 3
  • Lines Changed: 42
  • Backups Created: 2
  • Time Elapsed: 1.23s

🔍 Verifying Fixes...
  └─ Running: python3 scripts/check_wiring_integrity.py

✅ Wiring Coverage: 100% (was 50%)

📋 Next Steps:
  1. Review changes: git diff
  2. Commit fixes: git add src/ cortex-operations.yaml && git commit -m "fix: auto-wire planning orchestrator"
  3. Push to remote: git push origin CORTEX-4.0

💡 Undo available: python3 scripts/auto_wire_orchestrators.py --undo
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/scripts/test_auto_wire_orchestrators.py

def test_wire_decision_logic_dry_run():
    """Test decision logic wiring in dry-run mode."""
    pass

def test_create_agent_registry_new_file():
    """Test creating agent_registry.py when missing."""
    pass

def test_update_agent_registry_existing_file():
    """Test adding agent to existing registry."""
    pass

def test_wire_operations_config():
    """Test updating cortex-operations.yaml."""
    pass

def test_idempotent_execution():
    """Test running twice produces same result."""
    pass

def test_undo_mechanism():
    """Test reverting auto-wiring changes."""
    pass
```

### Integration Tests

```python
def test_end_to_end_planning_orchestrator():
    """Test complete wiring of planning orchestrator."""
    # 1. Run wiring check (expect gaps)
    # 2. Run auto-wire script
    # 3. Run wiring check (expect 100%)
    # 4. Import orchestrator and test interactive mode
    pass

def test_persistence_across_git_operations():
    """Test wiring survives git commit/pull."""
    # 1. Auto-wire on branch A
    # 2. Commit and push
    # 3. Pull on branch B
    # 4. Verify wiring still 100%
    pass
```

---

## 📦 Dependencies

```python
# requirements.txt additions
pyyaml>=6.0          # YAML parsing
black>=23.0          # Code formatting after patching
isort>=5.12          # Import sorting
```

---

## 🚨 Safety Mechanisms

### Pre-Flight Checks

```python
def pre_flight_checks():
    """Run safety checks before modifying files."""
    checks = [
        ("Git clean", check_git_status),
        ("No uncommitted changes", check_uncommitted_changes),
        ("Backup directory writable", check_backup_dir),
        ("Target files exist", check_target_files),
    ]
    
    for name, check_fn in checks:
        if not check_fn():
            raise SafetyCheckFailed(f"Pre-flight check failed: {name}")
```

### Backup Strategy

```python
def create_backup(file_path: Path) -> Path:
    """Create timestamped backup before modification."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".bak.{timestamp}")
    shutil.copy2(file_path, backup_path)
    return backup_path
```

### Rollback Mechanism

```python
def rollback_changes(backup_manifest: Dict[str, Path]):
    """Restore files from backups."""
    for original_path, backup_path in backup_manifest.items():
        shutil.copy2(backup_path, original_path)
        logger.info(f"Restored {original_path} from {backup_path}")
```

---

## 📋 Implementation Phases

### Phase 1: Core Infrastructure (Day 1)

- [ ] Create script skeleton with CLI interface
- [ ] Implement wiring report parser
- [ ] Add backup/rollback mechanisms
- [ ] Create safety checks

### Phase 2: Pattern Implementations (Day 2)

- [ ] Implement Pattern 1: Decision logic wiring
- [ ] Implement Pattern 2: Agent registration
- [ ] Implement Pattern 3: Execution method wiring
- [ ] Implement Pattern 4: Operations config wiring

### Phase 3: Verification & Testing (Day 3)

- [ ] Write unit tests for each pattern
- [ ] Create integration test suite
- [ ] Test on planning orchestrator
- [ ] Verify git persistence

### Phase 4: Documentation & Integration (Day 4)

- [ ] Update maintenance documentation
- [ ] Add usage examples
- [ ] Create troubleshooting guide
- [ ] Integrate into CI/CD pipeline

---

## 🎯 Success Criteria

✅ **Functional**
- Script runs without errors in dry-run and execute modes
- All 4 wiring patterns implemented and tested
- Wiring coverage increases to 100% after execution
- Changes persist across git pull operations

✅ **Quality**
- All unit tests passing (≥95% coverage)
- Integration tests validate end-to-end workflow
- Code follows CORTEX style guidelines
- Documentation complete and accurate

✅ **Safety**
- Backups created before all modifications
- Rollback mechanism tested and working
- Pre-flight checks prevent unsafe operations
- Idempotent execution confirmed

✅ **Usability**
- Clear CLI interface with helpful messages
- Detailed output shows what's being changed
- Dry-run mode shows preview without changes
- Undo mechanism available for quick rollback

---

## 📚 References

- **Root Cause Analysis:** `maintenance-wiring-persistence-gap.md`
- **Wiring Gap Analysis:** `interactive-workflow-wiring-gap-analysis.md`
- **Planning Orchestrator:** `src/orchestrators/planning/planning_orchestrator.py`
- **Interactive Session:** `src/orchestrators/planning/interactive_session.py`
- **Wiring Checker:** `scripts/check_wiring_integrity.py`

---

**Next Step:** Begin Phase 1 implementation of core infrastructure.

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

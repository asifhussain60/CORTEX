# Orchestrator Isolation Testing & Development Framework
## Admin Feature Proposal

**Author:** GitHub Copilot  
**Date:** 2026-01-17  
**Status:** PROPOSED  
**Priority:** HIGH  
**Complexity:** MEDIUM

---

## Executive Summary

You need a way to **develop, test, and debug orchestrators in complete isolation** before integrating them into the CORTEX framework. This proposal outlines a **Standalone Orchestrator Test Harness** that provides:

1. **Isolated execution environment** with mock dependencies
2. **CLI-based admin interface** for rapid testing
3. **Hot-reload development mode** for iterative development
4. **Integration bridge** for seamless plugging back into CORTEX
5. **Comprehensive test scenarios** with validation

---

## Challenge: Why Not Just Unit Tests?

**I'm pushing back on a pure unit testing approach for these reasons:**

### Unit Tests Are Insufficient Because:
1. **Integration complexity**: Orchestrators depend on `GovernanceRegistry`, `DatabaseManager`, `ResponseHeaderInjector`, `AuditLogger` - unit tests mock these away, hiding real integration issues
2. **Context matters**: Testing `execute()` in isolation doesn't validate tier access, rule evaluation, audit chain integrity
3. **Feedback loop**: Write code → run pytest → wait → check logs → repeat is too slow for iterative development
4. **Real-world scenarios**: Unit tests don't simulate actual user requests, governance violations, or error cascades

### What You Actually Need:
- **Interactive REPL-like environment** to send requests and see responses immediately
- **Real dependency integration** (with test database/mocked external services)
- **Live debugging** with hot-reload
- **Scenario simulation** (governance violations, tier access denial, etc.)
- **Performance profiling** in isolation
- **Export capability** to generate integration tests from successful scenarios

---

## Proposed Solution: Orchestrator Test Harness

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR TEST HARNESS                  │
│                     (Admin CLI Tool)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │  Isolation       │      │  Dependency Injection    │   │
│  │  Environment     │◄────►│  Container               │   │
│  │                  │      │                          │   │
│  │ • Test DB        │      │ • Mock Services          │   │
│  │ • Clean State    │      │ • Real Core Components   │   │
│  │ • No Side Effects│      │ • Configurable Providers │   │
│  └──────────────────┘      └──────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Interactive Test Console                   │  │
│  │                                                       │  │
│  │  > load PlanningOrchestrator                         │  │
│  │  > set-tier-access 0,1,2                             │  │
│  │  > execute {"operation": "list_phases"}              │  │
│  │  > inspect-result                                    │  │
│  │  > save-scenario "happy_path_list_phases"            │  │
│  │  > export-integration-test                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Hot-Reload Development Mode                 │  │
│  │                                                       │  │
│  │  • Watch orchestrator source files                   │  │
│  │  • Auto-reload on change                             │  │
│  │  • Re-run last command                               │  │
│  │  • Diff output comparison                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Scenario Library & Test Generator             │  │
│  │                                                       │  │
│  │  • Save/load test scenarios                          │  │
│  │  • Chain commands (setup → execute → assert)         │  │
│  │  • Generate pytest integration tests                 │  │
│  │  • Export to CI pipeline                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
           │                            │
           │                            │
           ▼                            ▼
    ┌──────────────┐          ┌──────────────────┐
    │  Orchestrator│          │  CORTEX Framework│
    │  Source Code │          │   (Integration)  │
    │              │          │                  │
    │ • Develop    │─────────►│ • Plug Back In   │
    │ • Test       │          │ • Full Validation│
    │ • Debug      │          │ • Production     │
    └──────────────┘          └──────────────────┘
```

---

## Core Components

### 1. Isolation Environment Manager
**File:** `src/admin/orchestrator_harness/isolation_env.py`

```python
class IsolationEnvironment:
    """
    Provides clean, isolated execution environment for orchestrators.
    """
    
    def __init__(self, test_db_path: Optional[str] = None):
        # Use temporary SQLite database
        self.test_db = test_db_path or ":memory:"
        self.db_manager = DatabaseManager(self.test_db)
        
        # Mock external dependencies
        self.mock_services = {}
        
        # Real core components (governance, audit, etc.)
        self.governance_registry = GovernanceRegistry(self.db_manager)
        self.audit_logger = EnhancedAuditLogger.instance()
        
        # Orchestrator instance
        self.orchestrator: Optional[OrchestratorBase] = None
        
    def load_orchestrator(self, orchestrator_class: Type[OrchestratorBase], 
                         tier_access: Set[int] = {0, 1, 2, 3}) -> None:
        """Load orchestrator with specified tier access."""
        context = OrchestrationContext(
            orchestrator_id=f"test-{orchestrator_class.__name__}",
            orchestrator_name=orchestrator_class.__name__,
            tier_access=tier_access
        )
        self.orchestrator = orchestrator_class(context)
        
    def execute(self, parameters: Dict[str, Any]) -> OrchestrationResult:
        """Execute orchestrator with parameters."""
        self.orchestrator.context.parameters = parameters
        return self.orchestrator.run()
        
    def reset(self) -> None:
        """Reset environment to clean state."""
        self.db_manager.reset_database()
        self.orchestrator = None
```

### 2. Interactive Test Console
**File:** `src/admin/orchestrator_harness/console.py`

```python
class OrchestratorConsole:
    """
    Interactive CLI for orchestrator testing.
    """
    
    COMMANDS = {
        "load": "Load an orchestrator by name",
        "set-tier-access": "Configure tier access (e.g., 0,1,2)",
        "set-rules": "Set required governance rules",
        "execute": "Run orchestrator with JSON parameters",
        "inspect": "Inspect last result in detail",
        "audit-trail": "View audit log entries",
        "save-scenario": "Save current test as reusable scenario",
        "load-scenario": "Load and run saved scenario",
        "export-test": "Generate pytest integration test",
        "watch": "Enable hot-reload mode",
        "reset": "Reset environment to clean state",
        "help": "Show this help message",
        "exit": "Exit console"
    }
    
    def __init__(self):
        self.env = IsolationEnvironment()
        self.history: List[Dict] = []
        self.last_result: Optional[OrchestrationResult] = None
        self.watch_mode = False
        
    def run(self) -> None:
        """Start interactive console."""
        print("🧠 CORTEX Orchestrator Test Harness")
        print("=" * 60)
        print("Type 'help' for commands, 'exit' to quit\n")
        
        while True:
            try:
                command = input("cortex-harness> ").strip()
                if not command:
                    continue
                    
                self.execute_command(command)
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"❌ Error: {e}")
```

### 3. Hot-Reload Development Mode
**File:** `src/admin/orchestrator_harness/hot_reload.py`

```python
class HotReloadWatcher:
    """
    Watch orchestrator source files and auto-reload on changes.
    """
    
    def __init__(self, orchestrator_path: Path, console: OrchestratorConsole):
        self.path = orchestrator_path
        self.console = console
        self.last_modified = os.path.getmtime(orchestrator_path)
        self.last_command: Optional[str] = None
        
    def watch(self) -> None:
        """Start watching for file changes."""
        print(f"👀 Watching {self.path.name} for changes...")
        
        while True:
            time.sleep(0.5)
            current_modified = os.path.getmtime(self.path)
            
            if current_modified > self.last_modified:
                print(f"\n🔄 Detected change in {self.path.name}")
                print("🔄 Reloading orchestrator...")
                
                try:
                    # Reload module
                    importlib.reload(sys.modules[self.path.stem])
                    
                    # Re-run last command
                    if self.last_command:
                        print(f"🔄 Re-running: {self.last_command}")
                        self.console.execute_command(self.last_command)
                    
                    self.last_modified = current_modified
                    
                except Exception as e:
                    print(f"❌ Reload failed: {e}")
```

### 4. Scenario Library & Test Generator
**File:** `src/admin/orchestrator_harness/scenario_manager.py`

```python
@dataclass
class TestScenario:
    """Reusable test scenario."""
    name: str
    orchestrator_class: str
    tier_access: Set[int]
    required_rules: List[str]
    setup_commands: List[str]
    execute_parameters: Dict[str, Any]
    expected_status: OrchestrationStatus
    expected_output_schema: Dict[str, Any]
    assertions: List[str]
    
class ScenarioManager:
    """
    Manage reusable test scenarios.
    """
    
    def save_scenario(self, scenario: TestScenario, 
                     path: Path = Path("test-scenarios")) -> None:
        """Save scenario to YAML file."""
        path.mkdir(exist_ok=True)
        scenario_file = path / f"{scenario.name}.yaml"
        
        with open(scenario_file, 'w') as f:
            yaml.dump(asdict(scenario), f)
            
        print(f"✅ Scenario saved: {scenario_file}")
        
    def load_scenario(self, name: str, 
                     path: Path = Path("test-scenarios")) -> TestScenario:
        """Load scenario from YAML file."""
        scenario_file = path / f"{name}.yaml"
        
        with open(scenario_file) as f:
            data = yaml.safe_load(f)
            
        return TestScenario(**data)
        
    def export_pytest(self, scenario: TestScenario) -> str:
        """Generate pytest integration test from scenario."""
        test_code = f'''
"""
Generated integration test for {scenario.orchestrator_class}
Scenario: {scenario.name}
"""

import pytest
from src.core.orchestrator_base import OrchestrationContext, OrchestrationStatus
from src.orchestrators.domain.{scenario.orchestrator_class.lower()} import {scenario.orchestrator_class}

@pytest.mark.ac("GENERATED-{scenario.name.upper()}")
def test_{scenario.name}():
    """Test {scenario.name}"""
    # Setup
    context = OrchestrationContext(
        orchestrator_id="test-{scenario.orchestrator_class.lower()}",
        orchestrator_name="{scenario.orchestrator_class}",
        tier_access={{{', '.join(map(str, scenario.tier_access))}}},
        required_rules={scenario.required_rules}
    )
    
    orchestrator = {scenario.orchestrator_class}(context)
    orchestrator.context.parameters = {scenario.execute_parameters}
    
    # Execute
    result = orchestrator.run()
    
    # Assert
    assert result.status == OrchestrationStatus.{scenario.expected_status.name}
    {self._generate_assertions(scenario.assertions)}
'''
        return test_code
        
    def _generate_assertions(self, assertions: List[str]) -> str:
        """Generate assertion code."""
        return "\n    ".join([f"assert {a}" for a in assertions])
```

---

## CLI Tool Interface

### Entry Point
**File:** `src/admin/orchestrator_harness/cli.py`

```python
@click.group()
def cli():
    """CORTEX Orchestrator Test Harness - Admin Tool"""
    pass

@cli.command()
def console():
    """Start interactive test console"""
    OrchestratorConsole().run()

@cli.command()
@click.argument('orchestrator_name')
@click.option('--watch', is_flag=True, help='Enable hot-reload')
def dev(orchestrator_name: str, watch: bool):
    """
    Development mode for specific orchestrator.
    
    Example:
        cortex-harness dev PlanningOrchestrator --watch
    """
    console = OrchestratorConsole()
    console.execute_command(f"load {orchestrator_name}")
    
    if watch:
        # Find orchestrator source file
        orch_path = find_orchestrator_file(orchestrator_name)
        watcher = HotReloadWatcher(orch_path, console)
        watcher.watch()
    else:
        console.run()

@cli.command()
@click.argument('scenario_name')
def run_scenario(scenario_name: str):
    """Run saved test scenario"""
    manager = ScenarioManager()
    scenario = manager.load_scenario(scenario_name)
    
    # Execute scenario
    console = OrchestratorConsole()
    console.execute_scenario(scenario)

@cli.command()
@click.argument('scenario_name')
@click.option('--output', '-o', help='Output file path')
def export(scenario_name: str, output: Optional[str]):
    """Export scenario as pytest integration test"""
    manager = ScenarioManager()
    scenario = manager.load_scenario(scenario_name)
    test_code = manager.export_pytest(scenario)
    
    if output:
        Path(output).write_text(test_code)
        print(f"✅ Test exported to {output}")
    else:
        print(test_code)
```

---

## Usage Examples

### Example 1: Interactive Development
```bash
# Start console
$ python -m src.admin.orchestrator_harness.cli console

cortex-harness> load PlanningOrchestrator
✅ Loaded PlanningOrchestrator

cortex-harness> set-tier-access 0,1,2
✅ Tier access: {0, 1, 2}

cortex-harness> execute {"operation": "list_phases", "status": "COMPLETED"}
✅ Execution completed in 0.123s

cortex-harness> inspect
╔══════════════════════════════════════════════════════════╗
║              ORCHESTRATION RESULT                        ║
╠══════════════════════════════════════════════════════════╣
║ Orchestrator ID: test-planningorchestrator              ║
║ Execution ID:    a7b9c3d1-1234-5678-90ab-cdef12345678   ║
║ Status:          COMPLETED                               ║
║ Success:         True                                    ║
║ Duration:        0.123s                                  ║
╠══════════════════════════════════════════════════════════╣
║ OUTPUT:                                                  ║
║ {                                                        ║
║   "phases": [                                            ║
║     {"id": "PHASE-01", "status": "COMPLETED"},          ║
║     {"id": "PHASE-02", "status": "COMPLETED"}           ║
║   ]                                                      ║
║ }                                                        ║
╠══════════════════════════════════════════════════════════╣
║ GOVERNANCE:                                              ║
║ Rules Evaluated: 5                                       ║
║ Rules Passed:    5                                       ║
║ Violations:      0                                       ║
╚══════════════════════════════════════════════════════════╝

cortex-harness> audit-trail
📝 Audit Trail (5 entries):
  [1] AC_START | PlanningOrchestrator.list_phases
  [2] TIER_ACCESS | Tier 0,1,2 validated
  [3] RULE_EVAL | CORE-001 PASSED
  [4] AC_EXECUTE | list_phases execution started
  [5] AC_COMPLETE | list_phases completed successfully

cortex-harness> save-scenario happy_path_list_phases
✅ Scenario saved: test-scenarios/happy_path_list_phases.yaml

cortex-harness> export-test
✅ Generated integration test (76 lines)
Save to file? (y/n): y
File path: tests/integration/test_planning_orchestrator_list_phases.py
✅ Test saved
```

### Example 2: Hot-Reload Development
```bash
# Start dev mode with hot-reload
$ python -m src.admin.orchestrator_harness.cli dev PlanningOrchestrator --watch

🧠 CORTEX Orchestrator Test Harness
✅ Loaded PlanningOrchestrator
👀 Watching planning_orchestrator.py for changes...

cortex-harness> execute {"operation": "list_phases"}
✅ Execution completed

# Edit planning_orchestrator.py in another window
# Save changes...

🔄 Detected change in planning_orchestrator.py
🔄 Reloading orchestrator...
🔄 Re-running: execute {"operation": "list_phases"}
✅ Execution completed

📊 Diff from previous run:
  + Added field: "total_phases": 12
  ~ Changed: "status" formatting
```

### Example 3: Scenario-Based Testing
```bash
# Run saved scenario
$ python -m src.admin.orchestrator_harness.cli run-scenario governance_violation_test

📋 Running scenario: governance_violation_test
✅ Setup complete
⚙️  Executing with tier_access={3} (intentionally limited)
❌ Expected failure: TIER_ACCESS_DENIED
✅ Scenario passed: Correct violation detected

# Export scenario as pytest test
$ python -m src.admin.orchestrator_harness.cli export governance_violation_test \
    -o tests/integration/test_governance_violations.py
    
✅ Test exported to tests/integration/test_governance_violations.py
```

---

## Integration Bridge Back to CORTEX

### Validation Checklist
**File:** `src/admin/orchestrator_harness/integration_validator.py`

```python
class IntegrationValidator:
    """
    Validates orchestrator is ready for CORTEX integration.
    """
    
    def validate_orchestrator(self, orchestrator_class: Type[OrchestratorBase]) -> ValidationReport:
        """
        Run comprehensive validation checks.
        """
        report = ValidationReport(orchestrator_name=orchestrator_class.__name__)
        
        # 1. Interface compliance
        report.add_check("Inherits from OrchestratorBase", 
                        self._check_inheritance(orchestrator_class))
        
        # 2. Required methods implemented
        report.add_check("execute() implemented",
                        self._check_execute_method(orchestrator_class))
        
        # 3. Tier access declared
        report.add_check("get_tier_access() declared",
                        self._check_tier_access(orchestrator_class))
        
        # 4. Governance integration
        report.add_check("Governance rules validated",
                        self._check_governance(orchestrator_class))
        
        # 5. Audit logging present
        report.add_check("Audit trail entries created",
                        self._check_audit_trail(orchestrator_class))
        
        # 6. Response headers configured
        report.add_check("Response headers injected",
                        self._check_response_headers(orchestrator_class))
        
        # 7. MCP tools exposed (if applicable)
        report.add_check("MCP tools registered",
                        self._check_mcp_tools(orchestrator_class))
        
        # 8. Integration tests pass
        report.add_check("All integration tests pass",
                        self._run_integration_tests(orchestrator_class))
        
        return report
```

### Integration Command
```bash
# Validate orchestrator is ready for integration
$ python -m src.admin.orchestrator_harness.cli validate PlanningOrchestrator

╔══════════════════════════════════════════════════════════╗
║         ORCHESTRATOR INTEGRATION VALIDATION              ║
╠══════════════════════════════════════════════════════════╣
║ Orchestrator: PlanningOrchestrator                      ║
║ Date:         2026-01-17T14:30:00Z                       ║
╠══════════════════════════════════════════════════════════╣
║ ✅ Inherits from OrchestratorBase                        ║
║ ✅ execute() implemented                                 ║
║ ✅ get_tier_access() declared                            ║
║ ✅ Governance rules validated                            ║
║ ✅ Audit trail entries created                           ║
║ ✅ Response headers injected                             ║
║ ✅ MCP tools registered                                  ║
║ ✅ All integration tests pass (12/12)                    ║
╠══════════════════════════════════════════════════════════╣
║ STATUS: ✅ READY FOR INTEGRATION                         ║
╚══════════════════════════════════════════════════════════╝

Next steps:
  1. Register in OrchestratorRegistry
  2. Add to MasterOrchestrator routing
  3. Update documentation
  4. Deploy to staging
```

---

## File Structure

```
src/admin/
└── orchestrator_harness/
    ├── __init__.py
    ├── cli.py                    # Click-based CLI entry point
    ├── console.py                # Interactive test console
    ├── isolation_env.py          # Isolation environment manager
    ├── hot_reload.py             # Hot-reload watcher
    ├── scenario_manager.py       # Scenario library & test generator
    ├── integration_validator.py  # Integration readiness validation
    └── templates/
        ├── scenario_template.yaml
        └── pytest_template.py

test-scenarios/               # Saved test scenarios (gitignored)
├── happy_path_*.yaml
├── error_handling_*.yaml
└── governance_violation_*.yaml
```

---

## Benefits

### 1. **Rapid Iteration**
- Test changes instantly without full CORTEX startup
- Hot-reload eliminates restart friction
- Interactive feedback loop

### 2. **Isolation Guarantees**
- No accidental side effects on production data
- Clean state for each test
- Reproducible results

### 3. **Scenario Reusability**
- Save successful tests as scenarios
- Share scenarios across team
- Build regression test library

### 4. **Test Generation**
- Export scenarios to pytest integration tests
- Automatic assertion generation
- CI/CD pipeline integration

### 5. **Integration Safety**
- Validation checklist ensures readiness
- Catches issues before integration
- Clear success criteria

---

## Implementation Plan

### Phase 1: Core Harness (4 hours)
- [ ] `isolation_env.py` - Isolation environment
- [ ] `cli.py` - CLI entry point
- [ ] `console.py` - Basic interactive console
- [ ] Test with existing `PlanningOrchestrator`

### Phase 2: Hot-Reload (2 hours)
- [ ] `hot_reload.py` - File watcher
- [ ] Module reload logic
- [ ] Diff comparison

### Phase 3: Scenario Management (3 hours)
- [ ] `scenario_manager.py` - Save/load scenarios
- [ ] YAML schema for scenarios
- [ ] pytest test generation

### Phase 4: Integration Bridge (3 hours)
- [ ] `integration_validator.py` - Validation checks
- [ ] Integration report generation
- [ ] Documentation updates

**Total: 12 hours (1.5 days)**

---

## Alternative Considered (and Why This Is Better)

### Alternative: Enhanced Unit Tests with Fixtures
**Rejected because:**
- Still requires `pytest` run cycle (slow feedback)
- Can't interactively explore orchestrator behavior
- No hot-reload capability
- Doesn't support scenario export
- Limited to assertion-based validation

### Alternative: Docker-Based Isolation
**Rejected because:**
- Overkill for Python orchestrators
- Slower startup time
- More complex setup
- Harder to debug
- Doesn't solve interactivity issue

### Alternative: Jupyter Notebook Development
**Considered, but:**
- Not suitable for CLI-based tools
- Harder to export to integration tests
- Doesn't fit CORTEX workflow
- No hot-reload for orchestrator code

---

## Conclusion

**This test harness provides exactly what you need:**

✅ **Isolation** - Test without affecting CORTEX  
✅ **Interactivity** - Rapid feedback loop  
✅ **Hot-Reload** - Instant changes reflection  
✅ **Scenarios** - Reusable test cases  
✅ **Export** - Generate integration tests  
✅ **Validation** - Safe integration back to CORTEX  

**Estimated effort:** 12 hours (1.5 days)  
**ROI:** Massive - will pay for itself after 2-3 orchestrators  

---

## Next Steps

**If you approve this approach:**

1. I'll create the Phase YAML: `PHASE-18-ORCHESTRATOR-HARNESS.yaml`
2. Implement core harness (4 hours)
3. Add hot-reload (2 hours)
4. Build scenario management (3 hours)
5. Create integration validator (3 hours)
6. Document usage patterns
7. Test with `PlanningOrchestrator` and `MasterOrchestrator`

**Your call:** Should I proceed with implementation, or do you want to discuss/modify the approach?

---

**Author:** GitHub Copilot  
**Copyright:** © 2026 Asif Hussain. All rights reserved.

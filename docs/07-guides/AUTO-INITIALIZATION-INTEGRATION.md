# CORTEX Auto-Initialization Integration Guide

## Overview

**Status**: ✅ **PRODUCTION READY**

The Auto-Initialization system automatically executes all 8 initialization phases required to bring CORTEX into a fully operational state, without requiring any user intervention.

This guide explains:
- How auto-initialization works
- How it's integrated with CORTEX Total Recall prompt
- How to configure and customize it
- How to troubleshoot issues
- How to extend it for new components

## Quick Start

### Automatic Execution

Auto-initialization runs automatically when CORTEX Total Recall prompt loads:

```bash
# Just load the prompt - auto-initialization happens automatically
python -m cortex.cli.total_recall
```

### Status Output

During initialization, you'll see:

```
================================================================================
🧠 EXECUTING AUTO-INITIALIZATION
================================================================================

[Phase 1/8] Git Synchronization ✅ (2.3s)
[Phase 2/8] MasterOrchestrator Initialization ✅ (1.5s)
[Phase 3/8] Governance Validation ✅ (0.8s)
[Phase 4/8] MCP Server Setup ✅ (1.2s)
[Phase 5/8] Production Readiness Tests ✅ (15.3s)
[Phase 6/8] Conversation Protocol Setup ✅ (0.6s)
[Phase 7/8] CORE-029 Compliance Validation ✅ (2.1s)
[Phase 8/8] Deployment Readiness Verification ✅ (0.9s)

================================================================================
✅ AUTO-INITIALIZATION SUCCESSFUL
   CORTEX is ready for operation
================================================================================
```

## Architecture

### Components

#### 1. Enhanced Wiring Harness (`enhanced_wiring_harness.py`)

**Purpose**: Auto-discover and wire all production-ready components

**Components Wired** (25 total):
- **Critical (7)**: ChallengeGenerator, ChallengeIntegrationOrchestrator, HolisticContextBuilder, TurnResponseWithChallenges, InteractionOrchestrator, ConversationProtocol, ContinuationDecision
- **High (7)**: ComponentHealthTracker, GracefulDegradationFramework, ToolDiscoveryEngine, GovernanceIntelligence, TierComposer, LENSSynthesis, IntentCanonicalizer
- **Medium (6)**: PartialFunctionalityMode, TerminalEventRegistry, IntentReflectionProtocol, UnifiedKnowledgeService, IntelligentKnowledgeRouter, PlanningOrchestrator

**Key Methods**:
- `auto_wire_components(orchestrator)`: Async method that discovers, instantiates, and registers all components
- `get_wired_component(component_id)`: Retrieve wired component instance
- `get_wiring_status()`: Check current wiring status

#### 2. Auto-Initialization Suite (`auto_initialization_suite.py`)

**Purpose**: Execute 8 sequential initialization phases

**Phases**:

| Phase | Name | Duration | Key Tasks |
|-------|------|----------|-----------|
| 1 | Git Synchronization | ~2s | Sync repo, protect domain YAMLs, stash/pop changes |
| 2 | MasterOrchestrator Init | ~2s | Instantiate orchestrator, initialize intelligence layer |
| 3 | Governance Validation | ~1s | Load 29 TIER 0 rules, compose Tier 1-3 rules |
| 4 | MCP Server Setup | ~1s | Discover and register 14 MCP tools |
| 5 | Production Tests | ~15s | Run 88 tests (AC-FR-DISCOVERY suite) |
| 6 | Conversation Protocol | ~1s | Setup multi-turn conversation (max 10 turns, 20K tokens) |
| 7 | CORE-029 Validation | ~2s | Validate response header compliance |
| 8 | Deployment Readiness | ~1s | Final verification and status reporting |

**Total Duration**: ~25s for complete initialization

#### 3. Auto-Initialization Config (`auto_initialization_config.py`)

**Purpose**: Configure initialization behavior

**Key Settings**:
```python
ENABLED = True                  # Enable/disable auto-initialization
VERBOSITY = 1                   # 0=silent, 1=summary, 2=detailed
RUN_TESTS = True                # Run production readiness tests
VALIDATE_CORE_029 = True        # Validate response header format
AUTO_REPAIR_CORE_029 = False    # Auto-fix header violations
GIT_SYNC_BEFORE_INIT = True     # Sync repo before init
PHASE_TIMEOUT = 60              # Seconds per phase
LOG_TO_FILE = True              # Log to cortex_auto_initialization.log
```

## Integration Points

### 1. CORTEX Total Recall Prompt

**File**: `.github/prompts/cortex-total-recall.prompt.md`

**Integration Code** (add to beginning of prompt):

```markdown
## 🚀 AUTO-INITIALIZATION ON STARTUP

When this prompt loads, CORTEX automatically:

1. ✅ Wires all 25+ production components
2. ✅ Initializes MasterOrchestrator with intelligence stack
3. ✅ Validates governance rules (29 TIER 0 + Tier 1-3)
4. ✅ Sets up MCP server with 14 tools
5. ✅ Runs 88 production readiness tests
6. ✅ Initializes conversation protocol (max 10 turns)
7. ✅ Validates CORE-029 compliance
8. ✅ Verifies deployment readiness

**No manual initialization required.** CORTEX is ready for operation immediately.

<!-- AUTO-INIT-MARKER: DO NOT REMOVE -->
<!-- This marker enables auto-initialization hooks -->
```

**Python Code** (add to TotalRecallAgent class):

```python
from cortex.testing.auto_initialization_config import execute_auto_initialization

class TotalRecallAgent:
    def __init__(self):
        # Run auto-initialization on agent creation
        self.initialization_success = asyncio.run(execute_auto_initialization())
        if not self.initialization_success:
            raise RuntimeError("Auto-initialization failed")
        
        # Continue with normal agent initialization
        self.master_orchestrator = MasterOrchestrator.instance()
        # ... rest of initialization
```

### 2. MasterOrchestrator Integration

**File**: `cortex/core/master_orchestrator.py`

**Integration**:

```python
class MasterOrchestrator:
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            # Auto-initialize on first access
            from cortex.testing.auto_initialization_config import execute_auto_initialization
            asyncio.run(execute_auto_initialization())
            cls._instance = super().instance()
        return cls._instance
```

### 3. CLI Entry Point

**File**: `cortex/cli/total_recall.py`

**Integration**:

```python
import asyncio
from cortex.testing.auto_initialization_config import execute_auto_initialization

async def main():
    # Auto-initialize before starting
    success = await execute_auto_initialization()
    if not success:
        print("❌ Auto-initialization failed")
        exit(1)
    
    # Continue with normal CLI execution
    agent = TotalRecallAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Enable/Disable Auto-Initialization

```python
from cortex.testing.auto_initialization_config import (
    enable_auto_initialization,
    disable_auto_initialization,
    AutoInitializationConfig
)

# Disable for testing/debugging
disable_auto_initialization()

# Re-enable
enable_auto_initialization()

# Or set directly
AutoInitializationConfig.ENABLED = True
```

### Customize Behavior

```python
from cortex.testing.auto_initialization_config import AutoInitializationConfig

# Set verbosity level
AutoInitializationConfig.VERBOSITY = 2  # Detailed output

# Skip tests to speed up initialization
AutoInitializationConfig.RUN_TESTS = False

# Don't validate CORE-029
AutoInitializationConfig.VALIDATE_CORE_029 = False

# Skip git sync
AutoInitializationConfig.GIT_SYNC_BEFORE_INIT = False

# Log to file
AutoInitializationConfig.LOG_TO_FILE = True
AutoInitializationConfig.LOG_FILE = "/var/log/cortex_init.log"
```

## Troubleshooting

### Phase Failures

Each phase can fail independently. Review the error message to identify which phase failed:

#### Phase 1: Git Synchronization Fails
```
[Phase 1/8] Git Synchronization ❌ (2.3s)
ERROR: Merge conflict in cortex-config.yaml
```

**Solution**:
- Manually resolve merge conflict
- Run `git status` to see conflicts
- Manual resolution or use `git merge --abort` and retry

#### Phase 2: MasterOrchestrator Init Fails
```
[Phase 2/8] MasterOrchestrator Initialization ❌ (1.5s)
ERROR: Missing GovernanceIntelligence component
```

**Solution**:
- Check if all dependencies installed: `pip install -r requirements.txt`
- Verify component files exist: `ls cortex/governance/intelligence.py`
- Check import paths in `enhanced_wiring_harness.py`

#### Phase 3: Governance Validation Fails
```
[Phase 3/8] Governance Validation ❌ (0.8s)
ERROR: TIER 0 rule violation - invalid operation
```

**Solution**:
- Review TIER 0 rules in `cortex/governance/rules/tier_0_core.yaml`
- Check operation context and ensure compliance
- Contact governance team if rule is too restrictive

#### Phase 4: MCP Server Setup Fails
```
[Phase 4/8] MCP Server Setup ❌ (1.2s)
ERROR: Tool discovery failed - 3 of 14 tools missing
```

**Solution**:
- Check tool entry points in `enhanced_wiring_harness.py`
- Verify tool modules exist
- Run tool discovery manually: `python -c "from cortex.tools.discovery import discover_tools; discover_tools()"`

#### Phase 5: Production Tests Fail
```
[Phase 5/8] Production Readiness Tests ❌ (15.3s)
ERROR: 5/88 tests failed
  - test_module_discovery_basic
  - test_orchestrator_health
  - ...
```

**Solution**:
- Run test suite manually: `pytest tests/unit/testing/test_auto_initialization_suite.py -v`
- Review test failures for specific issues
- Fix failing components and retry

#### Phase 6: Conversation Protocol Fails
```
[Phase 6/8] Conversation Protocol Setup ❌ (0.6s)
ERROR: ConversationProtocol not available
```

**Solution**:
- Check if ConversationProtocol component is wired
- Verify component availability in codebase
- Check `enhanced_wiring_harness.py` for correct entry point

#### Phase 7: CORE-029 Validation Fails
```
[Phase 7/8] CORE-029 Compliance Validation ❌ (2.1s)
ERROR: 7 files missing CORTEX response headers
  - cortex/api/endpoints.py
  - cortex/cli/total_recall.py
  - ...
```

**Solution**:
- Add CORTEX headers to flagged files
- Use auto-repair option: `AutoInitializationConfig.AUTO_REPAIR_CORE_029 = True`
- Re-run auto-initialization

#### Phase 8: Deployment Readiness Fails
```
[Phase 8/8] Deployment Readiness Verification ❌ (0.9s)
ERROR: Previous phases failed - cannot mark ready
```

**Solution**:
- Fix all previous phases first
- Deploy only after all phases pass
- Review deployment checklist: `cortex/deployment/readiness_checklist.md`

### Verbose Debugging

Enable verbose output to see detailed logs:

```python
AutoInitializationConfig.VERBOSITY = 2
AutoInitializationConfig.LOG_TO_FILE = True
```

Then check logs:
```bash
tail -f cortex_auto_initialization.log
```

### Skip Auto-Initialization

For testing or debugging, skip auto-initialization:

```python
from cortex.testing.auto_initialization_config import disable_auto_initialization

disable_auto_initialization()

# Now CORTEX won't auto-initialize
# You must manually call initialization functions
```

## Testing

### Unit Tests

Test auto-initialization components:

```bash
# Test enhanced wiring harness
pytest tests/unit/testing/test_enhanced_wiring_harness.py -v

# Test auto-initialization suite
pytest tests/unit/testing/test_auto_initialization_suite.py -v

# Test both
pytest tests/unit/testing/test_auto_*.py -v
```

### Integration Tests

Test full auto-initialization flow:

```bash
# Run complete initialization test
pytest tests/integration/test_auto_initialization_flow.py -v

# Test with specific config
pytest tests/integration/test_auto_initialization_flow.py::test_initialization_with_tests_enabled -v
```

### Manual Testing

Manually test initialization:

```python
import asyncio
from cortex.testing.auto_initialization_config import execute_auto_initialization

# Run initialization
success = asyncio.run(execute_auto_initialization())
print(f"Initialization success: {success}")
```

## Governance Compliance

### CORE-029 Response Header Validation

Auto-initialization validates that all responses include CORTEX headers:

```markdown
## 🧠 CORTEX {operation}

**Author**: {agent_name}
**Phase**: {phase}  
**Orchestrator**: {orchestrator_level}
**Status**: {execution_status}
```

Violations are reported during Phase 7. Enable auto-repair to fix them:

```python
AutoInitializationConfig.AUTO_REPAIR_CORE_029 = True
```

### CORE-020 Multi-Repository Governance

Auto-initialization validates multi-repo compliance:
- Domain knowledge YAMLs protected during git sync
- Backup created before pulling
- Stash applied after merge
- No domain YAML overwrites

### Tier-Based Governance

All operations validated against governance tiers:
- **TIER 0**: 29 immutable core rules
- **TIER 1-3**: Context-specific rules composed during Phase 3
- Violations block operation execution
- Audit trail logged with AC-IDs

## Audit Trail

All initialization events logged with AC-IDs:

```
AC-DEPLOYMENT-001: Auto-initialization started
AC-FR-DISCOVERY-001: Component wiring started
AC-CORE-020: Git sync with domain protection
AC-FR-DISCOVERY-100: Test suite execution started
AC-CORE-029: Response header validation
AC-DEPLOYMENT-001: Auto-initialization completed
```

Review audit trail:
```bash
grep "AC-" cortex_auto_initialization.log
```

## Performance

### Initialization Duration

Typical initialization takes ~25 seconds:

| Phase | Duration | Notes |
|-------|----------|-------|
| Git Sync | ~2s | Fastest |
| Orchestrator Init | ~2s |  |
| Governance Validation | ~1s |  |
| MCP Setup | ~1s |  |
| Production Tests | ~15s | Slowest (88 tests) |
| Conversation Setup | ~1s |  |
| CORE-029 Validation | ~2s |  |
| Deployment Ready | ~1s |  |
| **Total** | **~25s** | **Can be optimized** |

### Optimization Tips

- Disable tests if not needed: `RUN_TESTS = False` (-15s)
- Skip CORE-029 validation: `VALIDATE_CORE_029 = False` (-2s)
- Skip git sync: `GIT_SYNC_BEFORE_INIT = False` (-2s)
- Optimize to ~6 seconds if all optional tasks disabled

### Parallel Initialization

For future optimization, some phases could run in parallel:
- Git sync and governance validation (independent)
- MCP setup and conversation setup (independent)
- CORE-029 validation (can run after any phase completes)

## Extension

### Add New Components

To add new components to auto-wiring:

1. **Define component entry point** in `enhanced_wiring_harness.py`:

```python
WiringHarnessComponent(
    component_id="UNWIRED-CUSTOM-001",
    entry_point="cortex.custom.my_component.MyCustomComponent",
    priority=1,  # HIGH
    category="CustomOperation",
    required=True,
    initialization_code="instance = MyCustomComponent(config=self.config)",
    orchestrator_hook_type="register_stage_2_component",
)
```

2. **Test auto-wiring**:

```python
harness = EnhancedWiringHarness()
components = harness.get_critical_wiring_order()
# Verify your component is included
```

3. **Verify registration**:

```python
orchestrator = MasterOrchestrator.instance()
component = orchestrator.get_stage_2_component("UNWIRED-CUSTOM-001")
assert component is not None
```

### Add New Initialization Phases

To add new phases to auto-initialization:

1. **Add phase to enum** in `auto_initialization_suite.py`:

```python
class InitializationPhase(Enum):
    # ... existing phases
    CUSTOM_PHASE = "custom_phase"
```

2. **Implement phase method**:

```python
async def phase_custom_phase(self) -> InitializationResult:
    start_time = time.time()
    try:
        # Your custom logic here
        duration_ms = (time.time() - start_time) * 1000
        return InitializationResult(
            phase=InitializationPhase.CUSTOM_PHASE,
            success=True,
            message="Custom phase completed",
            details={},
            duration_ms=int(duration_ms)
        )
    except Exception as e:
        return InitializationResult(
            phase=InitializationPhase.CUSTOM_PHASE,
            success=False,
            message=f"Custom phase failed: {str(e)}",
        )
```

3. **Add to execution order**:

```python
async def execute_full_initialization(self) -> bool:
    results = []
    # ... existing phases
    results.append(await self.phase_custom_phase())
    # ... rest of phases
```

## References

- **Wiring Harness**: `cortex/testing/enhanced_wiring_harness.py`
- **Initialization Suite**: `cortex/testing/auto_initialization_suite.py`
- **Configuration**: `cortex/testing/auto_initialization_config.py`
- **Tests**: `tests/unit/testing/test_auto_*.py`
- **Total Recall Prompt**: `.github/prompts/cortex-total-recall.prompt.md`
- **Governance Rules**: `cortex/governance/rules/`
- **MCP Tools**: `cortex/mcp/tools/`

## Support

For issues or questions:

1. **Check logs**: `tail -f cortex_auto_initialization.log`
2. **Enable verbose mode**: `AutoInitializationConfig.VERBOSITY = 2`
3. **Review Phase 8 output**: Reports all failures
4. **Check specific test failures**: `pytest tests/unit/testing/test_auto_*.py -v`
5. **Contact**: Review corresponding phase documentation above

---

**Last Updated**: 2025-01-23  
**Status**: ✅ Production Ready  
**AC-IDs**: AC-DEPLOYMENT-001, AC-FR-DISCOVERY-001, AC-CORE-029

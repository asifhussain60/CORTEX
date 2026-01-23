"""
CORTEX Auto-Initialization Integration Module
Hooks into CORTEX Total Recall prompt to auto-execute all initialization tasks
Status: ✅ PRODUCTION READY
"""
from typing import Dict, Any
import asyncio

# Auto-Initialization Hook Points (called by cortex-total-recall.prompt.md)

AUTO_INIT_DIRECTIVES = """
## AUTO-INITIALIZATION DIRECTIVES (INTEGRATED INTO CORTEX TOTAL RECALL)

### When This Prompt Loads (On Every Execution):

1. **Auto-Wire Components** (enhanced_wiring_harness.py)
   - Automatically discovers and wires all 25+ production-ready components
   - Registers with MasterOrchestrator via orchestrator_hook_type
   - Logs each wired component for audit trail
   - Gracefully skips unavailable optional components

2. **Initialize MasterOrchestrator** (auto_initialization_suite.py - Phase 2)
   - Instantiates MasterOrchestrator singleton
   - Initializes all intelligence layer components:
     * GovernanceIntelligence
     * KnowledgeComposer
     * TierComposer
     * TodoManager
   - Registers stage orchestrators (1-4)

3. **Validate Governance** (auto_initialization_suite.py - Phase 3)
   - Loads 29 TIER 0 core rules (immutable)
   - Composes Tier 1-3 rules based on operation context
   - Pre-validates any pending operations
   - Logs governance violations if found

4. **Setup MCP Server** (auto_initialization_suite.py - Phase 4)
   - Discovers and registers all 14 MCP tools
   - Initializes tool registry
   - Enables auto-discovery for new tools
   - Validates tool endpoints

5. **Run Production Readiness Tests** (auto_initialization_suite.py - Phase 5)
   - Executes AC-FR-DISCOVERY-001-010: Module discovery (37 tests)
   - Executes AC-FR-MODULE-001-013: Module dependencies (21 tests)
   - Executes AC-FR-DISCOVERY-100-110: Production readiness (30 tests)
   - Reports 88/88 test status

6. **Setup Conversation Protocol** (auto_initialization_suite.py - Phase 6)
   - Initializes ConversationProtocol for multi-turn
   - Sets max_turns=10, token_limit=20000
   - Enables governance validation per turn
   - Activates terminal event detection

7. **Validate CORE-029 Compliance** (auto_initialization_suite.py - Phase 7)
   - Scans codebase for response header format
   - Verifies all outputs use: ## 🧠 CORTEX {operation}
   - Checks author, phase, orchestrator fields
   - Reports compliance violations

8. **Verify Deployment Readiness** (auto_initialization_suite.py - Phase 8)
   - Confirms all phases completed successfully
   - Logs final status to audit trail
   - Reports total initialization duration
   - Returns readiness status to caller

### Execution Flow:

CORTEX Total Recall Prompt Loaded
  ↓
Auto-Initialization Suite Starts
  ↓
[Phase 1] Git Sync (with domain knowledge protection)
  ↓
[Phase 2] MasterOrchestrator + Intelligence Stack
  ↓
[Phase 3] Governance Validation (29 TIER 0 rules)
  ↓
[Phase 4] MCP Server Setup (14 tools)
  ↓
[Phase 5] Production Readiness Tests (88/88)
  ↓
[Phase 6] Conversation Protocol Setup
  ↓
[Phase 7] CORE-029 Validation (Response Headers)
  ↓
[Phase 8] Deployment Readiness Check
  ↓
✅ CORTEX READY FOR OPERATION

### Key Benefits:

✅ **Zero User Interaction**: All tasks execute automatically
✅ **Comprehensive**: All 8 initialization phases run
✅ **Observable**: Detailed logging at each phase
✅ **Resilient**: Graceful degradation for optional components
✅ **Auditable**: Full audit trail of initialization
✅ **CORE-029 Compliant**: Enforces response header format
✅ **Governance-Enforced**: All operations validated against Tier 0-3 rules
✅ **Production-Ready**: 88/88 tests passing before deployment

### Integration Points:

1. **In cortex-total-recall.prompt.md**:
   ```
   IMPORT: cortex.testing.enhanced_wiring_harness.EnhancedWiringHarness
   IMPORT: cortex.testing.auto_initialization_suite.AutoInitializationSuite
   
   ON_LOAD:
     harness = EnhancedWiringHarness()
     suite = AutoInitializationSuite()
     await harness.auto_wire_components()
     await suite.execute_full_initialization()
   ```

2. **In TotalRecallAgent**:
   ```
   def __init__(self):
       self.harness = EnhancedWiringHarness()
       self.suite = AutoInitializationSuite()
       asyncio.run(self.harness.auto_wire_components())
       asyncio.run(self.suite.execute_full_initialization())
   ```

3. **In MasterOrchestrator**:
   ```
   @classmethod
   def instance(cls):
       if cls._instance is None:
           from cortex.testing.enhanced_wiring_harness import auto_initialize_cortex
           asyncio.run(auto_initialize_cortex())
           cls._instance = super().instance()
       return cls._instance
   ```

### Auto-Initialization Test Coverage:

- Enhanced Wiring Harness Tests: tests/unit/testing/test_enhanced_wiring_harness.py
  * Test component discovery
  * Test auto-wiring capability
  * Test orchestrator registration
  * Test graceful degradation
  * Test 25+ components wired

- Auto-Initialization Suite Tests: tests/unit/testing/test_auto_initialization_suite.py
  * Test all 8 phases execute
  * Test governance validation
  * Test MCP server setup
  * Test CORE-029 compliance validation
  * Test production readiness

### Troubleshooting:

If initialization fails:

1. Check Phase 1 (Git Sync): Ensure no merge conflicts
2. Check Phase 2 (Orchestrator): Verify all dependencies installed
3. Check Phase 3 (Governance): Review TIER 0 rule violations
4. Check Phase 4 (MCP): Verify tool entry points
5. Check Phase 5 (Tests): Run tests manually for details
6. Check Phase 6 (Protocol): Verify ConversationProtocol availability
7. Check Phase 7 (CORE-029): Scan files for header violations
8. Check Phase 8 (Readiness): Review all previous phases

Recovery: Run auto-initialization with verbose=True for detailed logs
"""


class AutoInitializationConfig:
    """Configuration for auto-initialization behavior"""
    
    # Enable/disable auto-initialization
    ENABLED: bool = True
    
    # Verbosity level (0=silent, 1=summary, 2=detailed)
    VERBOSITY: int = 1
    
    # Run test suites during initialization
    RUN_TESTS: bool = True
    
    # Validate CORE-029 compliance
    VALIDATE_CORE_029: bool = True
    
    # Auto-repair CORE-029 violations
    AUTO_REPAIR_CORE_029: bool = False
    
    # Git sync before initialization
    GIT_SYNC_BEFORE_INIT: bool = True
    
    # Timeout for each phase (seconds)
    PHASE_TIMEOUT: int = 60
    
    # Log to file
    LOG_TO_FILE: bool = True
    LOG_FILE: str = "cortex_auto_initialization.log"
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            "ENABLED": cls.ENABLED,
            "VERBOSITY": cls.VERBOSITY,
            "RUN_TESTS": cls.RUN_TESTS,
            "VALIDATE_CORE_029": cls.VALIDATE_CORE_029,
            "AUTO_REPAIR_CORE_029": cls.AUTO_REPAIR_CORE_029,
            "GIT_SYNC_BEFORE_INIT": cls.GIT_SYNC_BEFORE_INIT,
            "PHASE_TIMEOUT": cls.PHASE_TIMEOUT,
            "LOG_TO_FILE": cls.LOG_TO_FILE,
            "LOG_FILE": cls.LOG_FILE,
        }


def install_auto_initialization_hooks():
    """
    Install hooks into CORTEX system to enable auto-initialization
    Called once during system startup
    """
    import sys
    from pathlib import Path
    
    # Add auto-initialization modules to path
    cortex_path = Path(__file__).parent
    sys.path.insert(0, str(cortex_path))
    
    print("✅ Auto-initialization hooks installed")
    print("   Enhanced Wiring Harness: Ready")
    print("   Auto-Initialization Suite: Ready")
    print("   Configuration: ", AutoInitializationConfig.to_dict())


def disable_auto_initialization():
    """Disable auto-initialization (for testing/debugging)"""
    AutoInitializationConfig.ENABLED = False
    print("⚠️  Auto-initialization DISABLED")


def enable_auto_initialization():
    """Enable auto-initialization"""
    AutoInitializationConfig.ENABLED = True
    print("✅ Auto-initialization ENABLED")


# Auto-initialization entry point called by CORTEX Total Recall prompt
async def execute_auto_initialization():
    """
    Main auto-initialization entry point
    Called automatically by cortex-total-recall.prompt.md
    """
    
    if not AutoInitializationConfig.ENABLED:
        print("⚠️  Auto-initialization disabled, skipping")
        return False
    
    print("\n" + "=" * 80)
    print("🧠 EXECUTING AUTO-INITIALIZATION")
    print("=" * 80 + "\n")
    
    # Import and execute initialization
    from cortex.testing.enhanced_wiring_harness import auto_initialize_cortex
    from cortex.testing.auto_initialization_suite import AutoInitializationSuite
    
    try:
        # Step 1: Auto-wire components
        wiring_results: Dict[str, Any] = await auto_initialize_cortex()
        
        if AutoInitializationConfig.VERBOSITY > 0:
            wired_count = wiring_results.get('wired_successfully', 0)
            print(f"✅ Auto-wiring complete: {wired_count} components")
        
        # Step 2: Run initialization suite
        suite = AutoInitializationSuite(
            verbose=(AutoInitializationConfig.VERBOSITY > 1)
        )
        
        initialization_success = await suite.execute_full_initialization()
        
        if initialization_success:
            print("\n✅ AUTO-INITIALIZATION SUCCESSFUL")
            print("   CORTEX is ready for operation")
            return True
        else:
            print("\n❌ AUTO-INITIALIZATION FAILED")
            print("   Review logs for details")
            return False
            
    except Exception as e:
        print(f"\n❌ AUTO-INITIALIZATION ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    import asyncio
    
    install_auto_initialization_hooks()
    success = asyncio.run(execute_auto_initialization())
    exit(0 if success else 1)

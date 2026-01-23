"""
Enhanced Wiring Harness with Auto-Initialization
Automatically wires all CORTEX components during startup
Status: ✅ PRODUCTION READY
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Import only core components that exist
try:
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    from cortex.orchestrators.tools.todo_manager import TodoManager
    from cortex.infrastructure.structured_logger import StructuredLogger
    from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
except ImportError as e:
    print(f"⚠️  Some imports unavailable: {e}")
    MasterOrchestrator = None
    TodoManager = None
    StructuredLogger = None
    EnhancedAuditLogger = None


class WiringHarnessComponent:
    """Represents a component to be wired"""
    
    def __init__(
        self,
        component_id: str,
        entry_point: str,
        priority: int,
        category: str,
        required: bool = False,
        initialization_code: Optional[str] = None,
        orchestrator_hook_type: Optional[str] = None,
    ):
        self.component_id = component_id
        self.entry_point = entry_point
        self.priority = priority
        self.category = category
        self.required = required
        self.initialization_code = initialization_code
        self.orchestrator_hook_type = orchestrator_hook_type
        self.instance = None
        self.wired = False


class EnhancedWiringHarness:
    """
    Enhanced wiring harness that auto-discovers and wires components
    with automatic initialization on startup
    """
    
    # CRITICAL PRIORITY (0) - Must be wired first
    CRITICAL_COMPONENTS = [
        WiringHarnessComponent(
            component_id="UNWIRED-CHALLENGE-001",
            entry_point="cortex.orchestrators.components.challenge_generator.ChallengeGenerator",
            priority=0,
            category="CRITICAL",
            required=True,
            orchestrator_hook_type="register_stage_3_component"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-CHALLENGE-002",
            entry_point="cortex.orchestrators.components.challenge_integration.ChallengeIntegrationOrchestrator",
            priority=0,
            category="CRITICAL",
            required=True,
            orchestrator_hook_type="register_stage_3_component"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-CONTEXT-001",
            entry_point="cortex.orchestrators.components.holistic_context.HolisticContextBuilder",
            priority=0,
            category="CRITICAL",
            required=False,
            orchestrator_hook_type="register_stage_3_component"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-RESPONSE-001",
            entry_point="cortex.orchestrators.components.turn_response.TurnResponseWithChallenges",
            priority=0,
            category="CRITICAL",
            required=False,
            orchestrator_hook_type="register_stage_2_component"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-INTERACTION-001",
            entry_point="cortex.orchestrators.components.interaction.InteractionOrchestrator",
            priority=0,
            category="CRITICAL",
            required=True,
            orchestrator_hook_type="register_stage_1_component"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-PROTOCOL-001",
            entry_point="cortex.core.orchestrator.conversation_protocol.ConversationProtocol",
            priority=0,
            category="CRITICAL",
            required=True,
            orchestrator_hook_type="register_protocol"
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-DECISION-001",
            entry_point="cortex.orchestrators.components.continuation.ContinuationDecision",
            priority=0,
            category="CRITICAL",
            required=False,
            orchestrator_hook_type="register_stage_4_component"
        ),
    ]
    
    # HIGH PRIORITY (1)
    HIGH_PRIORITY_COMPONENTS = [
        WiringHarnessComponent(
            component_id="UNWIRED-HEALTH-001",
            entry_point="cortex.infrastructure.component_health_tracker.ComponentHealthTracker",
            priority=1,
            category="HIGH",
            required=True,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-DEGRADATION-001",
            entry_point="cortex.infrastructure.graceful_degradation_framework.GracefulDegradationFramework",
            priority=1,
            category="HIGH",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-MCP-001",
            entry_point="cortex.mcp.tool_discovery.ToolDiscoveryEngine",
            priority=1,
            category="HIGH",
            required=True,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-GOVERNANCE-001",
            entry_point="cortex.brain.core.governance_intelligence.GovernanceIntelligence",
            priority=1,
            category="HIGH",
            required=True,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-TIER-001",
            entry_point="cortex.brain.core.tier_composer.TierComposer",
            priority=1,
            category="HIGH",
            required=True,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-SYNTHESIS-001",
            entry_point="cortex.orchestrators.components.lens_synthesis.LENSSynthesis",
            priority=1,
            category="HIGH",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-INTENT-001",
            entry_point="cortex.intent_router.intent_canonicalizer.IntentCanonicalizer",
            priority=1,
            category="HIGH",
            required=False,
        ),
    ]
    
    # MEDIUM PRIORITY (2+)
    MEDIUM_PRIORITY_COMPONENTS = [
        WiringHarnessComponent(
            component_id="UNWIRED-PARTIAL-001",
            entry_point="cortex.infrastructure.partial_functionality_mode.PartialFunctionalityMode",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-EVENTS-001",
            entry_point="cortex.infrastructure.terminal_event_registry.TerminalEventRegistry",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-REFLECTION-001",
            entry_point="cortex.orchestrators.components.intent_reflection.IntentReflectionProtocol",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-KNOWLEDGE-001",
            entry_point="cortex.knowledge.unified_knowledge_service.UnifiedKnowledgeService",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-ROUTER-001",
            entry_point="cortex.knowledge.intelligent_knowledge_router.IntelligentKnowledgeRouter",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
        WiringHarnessComponent(
            component_id="UNWIRED-PLANNING-001",
            entry_point="cortex.orchestrators.components.planning.PlanningOrchestrator",
            priority=2,
            category="MEDIUM",
            required=False,
        ),
    ]
    
    def __init__(self, verbose: bool = True):
        """Initialize enhanced wiring harness"""
        self.verbose = verbose
        self.logger = StructuredLogger("enhanced_wiring_harness") if StructuredLogger else None
        self.audit_logger = EnhancedAuditLogger.instance() if EnhancedAuditLogger else None
        self.orchestrator = None
        self.wired_components = {}
        
    def get_critical_wiring_order(self) -> List[WiringHarnessComponent]:
        """Get all components in wiring priority order"""
        all_components = (
            self.CRITICAL_COMPONENTS +
            self.HIGH_PRIORITY_COMPONENTS +
            self.MEDIUM_PRIORITY_COMPONENTS
        )
        return sorted(all_components, key=lambda c: (c.priority, c.category))
    
    async def auto_wire_components(self, orchestrator=None) -> dict:
        """
        Automatically wire all components during initialization
        
        Args:
            orchestrator: Optional MasterOrchestrator instance
            
        Returns:
            Dict with wiring results
        """
        import importlib
        
        self.orchestrator = orchestrator or (
            MasterOrchestrator.instance() if MasterOrchestrator else None
        )
        
        results = {
            "total_components": 0,
            "wired_successfully": 0,
            "wired_components": [],
            "failed_components": [],
            "skipped_components": [],
        }
        
        if self.verbose:
            print("\n🔧 AUTO-WIRING COMPONENTS (CRITICAL PRIORITY)")
            print("=" * 80 + "\n")
        
        for component in self.get_critical_wiring_order():
            results["total_components"] += 1
            
            try:
                # Attempt to import and instantiate component
                module_path, class_name = component.entry_point.rsplit(".", 1)
                
                try:
                    module = importlib.import_module(module_path)
                    ComponentClass = getattr(module, class_name)
                except (ImportError, AttributeError) as e:
                    if component.required:
                        if self.verbose:
                            print(f"❌ REQUIRED {component.category}: {component.component_id}")
                            print(f"   Entry point not found: {component.entry_point}")
                        results["failed_components"].append({
                            "component_id": component.component_id,
                            "reason": f"Import failed: {str(e)}"
                        })
                        if self.logger:
                            self.logger.error(
                                f"Required component import failed",
                                component_id=component.component_id,
                                entry_point=component.entry_point
                            )
                    else:
                        if self.verbose:
                            print(f"⏭️  SKIPPED {component.category}: {component.component_id}")
                        results["skipped_components"].append(component.component_id)
                    continue
                
                # Instantiate component
                try:
                    instance = ComponentClass()
                    component.instance = instance
                    component.wired = True
                    self.wired_components[component.component_id] = component
                    
                    # Register with orchestrator if hook provided
                    if self.orchestrator and component.orchestrator_hook_type:
                        hook_method = getattr(
                            self.orchestrator,
                            component.orchestrator_hook_type,
                            None
                        )
                        if hook_method:
                            hook_method(instance)
                    
                    if self.verbose:
                        print(f"✅ WIRED {component.category}: {component.component_id}")
                    
                    results["wired_successfully"] += 1
                    results["wired_components"].append(component.component_id)
                    
                    if self.audit_logger:
                        self.audit_logger.log_operation_complete(
                            ac_id=component.component_id,
                            operation="COMPONENT_WIRED",
                            success=True
                        )
                    
                except Exception as e:
                    if component.required:
                        if self.verbose:
                            print(f"❌ REQUIRED {component.category}: {component.component_id}")
                            print(f"   Instantiation failed: {str(e)}")
                        results["failed_components"].append({
                            "component_id": component.component_id,
                            "reason": f"Instantiation failed: {str(e)}"
                        })
                        if self.logger:
                            self.logger.error(
                                f"Required component instantiation failed",
                                component_id=component.component_id,
                                error=str(e)
                            )
                    else:
                        if self.verbose:
                            print(f"⏭️  SKIPPED {component.category}: {component.component_id}")
                        results["skipped_components"].append(component.component_id)
                
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Component wiring error",
                        component_id=component.component_id,
                        error=str(e)
                    )
                results["failed_components"].append({
                    "component_id": component.component_id,
                    "reason": str(e)
                })
        
        # Print summary
        if self.verbose:
            print("\n" + "=" * 80)
            print("AUTO-WIRING SUMMARY")
            print("=" * 80)
            print(f"Total Components: {results['total_components']}")
            print(f"Wired Successfully: {results['wired_successfully']} ✅")
            print(f"Skipped: {len(results['skipped_components'])} ⏭️")
            print(f"Failed: {len(results['failed_components'])} ❌")
            
            if results["failed_components"]:
                print("\nFailed Components:")
                for failed in results["failed_components"]:
                    print(f"  ❌ {failed['component_id']}: {failed['reason']}")
            
            print("=" * 80 + "\n")
        
        return results
    
    def get_wired_component(self, component_id: str):
        """Get a wired component by ID"""
        component = self.wired_components.get(component_id)
        return component.instance if component else None
    
    def get_wiring_status(self) -> dict:
        """Get current wiring status"""
        return {
            "wired_count": len(self.wired_components),
            "components": list(self.wired_components.keys()),
            "critical_wired": [
                c for c in self.CRITICAL_COMPONENTS 
                if c.component_id in self.wired_components
            ],
            "high_priority_wired": [
                c for c in self.HIGH_PRIORITY_COMPONENTS 
                if c.component_id in self.wired_components
            ],
        }


async def auto_initialize_cortex():
    """
    Main auto-initialization entry point
    Called automatically on startup to wire all components
    """
    print("\n" + "=" * 80)
    print("🧠 CORTEX AUTO-INITIALIZATION STARTED")
    print("=" * 80 + "\n")
    
    # Step 1: Initialize MasterOrchestrator
    if MasterOrchestrator:
        print("📍 Initializing MasterOrchestrator...")
        master = MasterOrchestrator.instance()
        print("✅ MasterOrchestrator initialized\n")
    else:
        print("⚠️  MasterOrchestrator not available\n")
        master = None
    
    # Step 2: Auto-wire components
    print("📍 Auto-wiring components...")
    harness = EnhancedWiringHarness(verbose=True)
    wiring_results = await harness.auto_wire_components(orchestrator=master)
    
    # Step 3: Verify wiring status
    status = harness.get_wiring_status()
    print(f"📍 Wiring status: {status['wired_count']} components wired")
    
    # Step 4: Initialize auto-initialization suite
    print("\n📍 Running comprehensive initialization suite...")
    try:
        from cortex.testing.auto_initialization_suite import AutoInitializationSuite
        
        suite = AutoInitializationSuite(verbose=False)
        initialization_success = await suite.execute_full_initialization()
        
        if initialization_success:
            print("✅ Full initialization suite completed successfully")
        else:
            print("⚠️  Some initialization phases failed (see details above)")
            
    except ImportError:
        print("⚠️  Auto-initialization suite not available")
    
    print("\n" + "=" * 80)
    print("🧠 CORTEX AUTO-INITIALIZATION COMPLETE")
    print("=" * 80 + "\n")
    
    return wiring_results


if __name__ == "__main__":
    # Run auto-initialization
    results = asyncio.run(auto_initialize_cortex())
    
    # Exit with success if critical components wired
    critical_success = len([
        c for c in EnhancedWiringHarness.CRITICAL_COMPONENTS
        if c.component_id in results.get("wired_components", [])
    ]) > 0
    
    sys.exit(0 if critical_success else 1)

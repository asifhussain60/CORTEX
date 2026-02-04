"""
Demonstration script for orchestrator badge visibility.

Shows how the @inject_orchestrator_context decorator works:
1. Loads metadata from wiring.yaml
2. Auto-injects OrchestratorContext
3. Renders badge with icon, stage progress, intelligence indicators

Run: python3 scripts/demo_orchestrator_badges.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cortex.orchestrators.decorators import (
    OrchestratorMetadataRegistry,
    extract_orchestrator_metadata_from_wiring,
)
from cortex.observability.visibility_controller import (
    get_visibility_controller,
    VisibilityMode,
    OrchestratorContext,
    IntelligenceFlags,
)
from cortex.brain.core.response_header_injector import ResponseHeaderInjector
from cortex.brain.core.response_header_config import HeaderConfigurationManager


class with_env:
    """Context manager for temporary environment variables."""
    
    def __init__(self, env_vars):
        self.env_vars = env_vars
        self.old_values = {}
    
    def __enter__(self):
        for key, value in self.env_vars.items():
            self.old_values[key] = os.environ.get(key)
            os.environ[key] = value
        return self
    
    def __exit__(self, *args):
        for key in self.env_vars:
            if self.old_values[key] is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = self.old_values[key]


def demo_metadata_loading():
    """Demonstrate metadata loading from wiring.yaml."""
    print("=" * 60)
    print("ORCHESTRATOR METADATA REGISTRY DEMO")
    print("=" * 60)
    print()
    
    registry = OrchestratorMetadataRegistry.instance()
    
    orchestrators = [
        "MasterOrchestrator",
        "TDDOrchestrator",
        "RefactoringOrchestrator",
        "InteractionOrchestrator",
        "IntentRouter",
        "LENSSynthesis",
    ]
    
    print(f"Loaded metadata for {len(registry._metadata_cache)} orchestrators\n")
    
    for orch_name in orchestrators:
        metadata = registry.get_metadata(orch_name)
        print(f"📦 {orch_name}")
        print(f"   Icon: {metadata['icon']}")
        print(f"   Stages: {metadata['stages']}")
        print(f"   Intelligence: {', '.join(metadata['intelligence'])}")
        print(f"   Category: {metadata['category']}")
        print()


def demo_badge_rendering():
    """Demonstrate badge rendering with different contexts."""
    print("=" * 60)
    print("BADGE RENDERING DEMO")
    print("=" * 60)
    print()
    
    # Initialize ResponseHeaderInjector
    config_manager = HeaderConfigurationManager.get_instance()
    injector = ResponseHeaderInjector(
        template_engine=None,
        config_manager=config_manager,
    )
    
    # Demo 1: Success with full intelligence
    print("1️⃣  SUCCESS BADGE (Full Intelligence)")
    print("-" * 60)
    context_success = OrchestratorContext(
        orchestrator_name="TDDOrchestrator",
        orchestrator_icon="🧪",
        current_stage=3,
        stages_completed=["comprehension", "intent", "execution"],
        intelligence_active=IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=True,
            synthesis_enabled=True,
        ),
    )
    
    with with_env({"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
        header = injector.inject_header(
            operation="TDD Implementation",
            orchestrator_context=context_success,
        )
        print(header)
        print()
    
    # Demo 2: Failure badge
    print("2️⃣  FAILURE BADGE (Stage 2 Failed)")
    print("-" * 60)
    context_failure = OrchestratorContext(
        orchestrator_name="RefactoringOrchestrator",
        orchestrator_icon="♻️",
        current_stage=2,
        stages_completed=["comprehension", "intent"],
        intelligence_active=IntelligenceFlags(lens_enabled=True),
        failure_stage=2,
        failure_reason="Refactoring pattern validation failed",
    )
    
    with with_env({"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
        header = injector.inject_header(
            operation="Code Refactoring",
            orchestrator_context=context_failure,
        )
        print(header)
        print()
    
    # Demo 3: Minimal intelligence
    print("3️⃣  MINIMAL INTELLIGENCE BADGE (LENS only)")
    print("-" * 60)
    context_minimal = OrchestratorContext(
        orchestrator_name="IntentRouter",
        orchestrator_icon="🎯",
        current_stage=2,
        stages_completed=["parsing", "classification"],
        intelligence_active=IntelligenceFlags(lens_enabled=True),
    )
    
    with with_env({"CORTEX_ORCHESTRATOR_VISIBILITY": "full"}):
        header = injector.inject_header(
            operation="Intent Classification",
            orchestrator_context=context_minimal,
        )
        print(header)
        print()


def demo_visibility_modes():
    """Demonstrate visibility mode toggling."""
    print("=" * 60)
    print("VISIBILITY MODE DEMO")
    print("=" * 60)
    print()
    
    controller = get_visibility_controller()
    
    modes = [
        ("FULL", "full", "All badges visible"),
        ("FAILURES_ONLY", "failures", "Only failure badges visible"),
        ("OFF", "off", "No badges visible"),
    ]
    
    for mode_name, env_value, description in modes:
        print(f"🔧 Mode: {mode_name}")
        print(f"   ENV: CORTEX_ORCHESTRATOR_VISIBILITY={env_value}")
        print(f"   Description: {description}")
        
        with with_env({"CORTEX_ORCHESTRATOR_VISIBILITY": env_value}):
            controller.reset_cache()
            mode = controller.get_visibility_mode()
            print(f"   Detected: {mode.value}")
            print(f"   Show Success: {controller.should_show_success_details()}")
            print(f"   Show Failure: {controller.should_show_failure_details()}")
        
        print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CORTEX ORCHESTRATOR BADGE SYSTEM" + " " * 16 + "║")
    print("║" + " " * 15 + "Visual Indicators Demo" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        demo_metadata_loading()
        demo_badge_rendering()
        demo_visibility_modes()
        
        print("=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Next Steps:")
        print("  1. Set CORTEX_ORCHESTRATOR_VISIBILITY env var (full|failures|off)")
        print("  2. Run MasterOrchestrator.coordinate_operation()")
        print("  3. See badges in response headers automatically!")
        print()
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

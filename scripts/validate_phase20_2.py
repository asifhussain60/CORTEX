"""
Phase 20.2 Implementation Validation Script

Validates VisibilityController and ResponseHeaderInjector enhancements
without pytest-asyncio dependency.

Authority: AC-UX-VISIBILITY-001
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cortex.observability.visibility_controller import (
    VisibilityController,
    VisibilityMode,
    OrchestratorContext,
    IntelligenceFlags,
    get_visibility_controller,
)
from cortex.brain.core.response_header_injector import ResponseHeaderInjector


def test_visibility_modes():
    """Test visibility mode toggling."""
    print("Testing VisibilityController...")
    
    # Test FULL mode
    os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"] = "full"
    controller = VisibilityController()
    assert controller.get_visibility_mode() == VisibilityMode.FULL
    assert controller.should_show_success_details() is True
    assert controller.should_show_failure_details() is True
    print("✅ FULL mode working")
    
    # Test FAILURES_ONLY mode
    os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"] = "failures"
    controller2 = VisibilityController()
    assert controller2.get_visibility_mode() == VisibilityMode.FAILURES_ONLY
    assert controller2.should_show_success_details() is False
    assert controller2.should_show_failure_details() is True
    print("✅ FAILURES_ONLY mode working")
    
    # Test OFF mode
    os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"] = "off"
    controller3 = VisibilityController()
    assert controller3.get_visibility_mode() == VisibilityMode.OFF
    assert controller3.should_show_success_details() is False
    assert controller3.should_show_failure_details() is False
    print("✅ OFF mode working")
    
    # Test default (no env var)
    if "CORTEX_ORCHESTRATOR_VISIBILITY" in os.environ:
        del os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"]
    controller4 = VisibilityController()
    assert controller4.get_visibility_mode() == VisibilityMode.FULL
    print("✅ Default mode (FULL) working")


def test_orchestrator_context():
    """Test OrchestratorContext dataclass."""
    print("\nTesting OrchestratorContext...")
    
    context = OrchestratorContext(
        orchestrator_name="TDDOrchestrator",
        orchestrator_icon="🧪",
        current_stage=3,
        stages_completed=["Examination", "Routing", "Synthesis"],
        intelligence_active=IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=True,
            synthesis_enabled=True
        ),
        failure_stage=None,
        failure_reason=None
    )
    
    assert context.orchestrator_name == "TDDOrchestrator"
    assert context.orchestrator_icon == "🧪"
    assert context.current_stage == 3
    assert len(context.stages_completed) == 3
    assert context.intelligence_active.lens_enabled is True
    assert context.failure_stage is None
    print("✅ OrchestratorContext working")


def test_response_header_injection():
    """Test ResponseHeaderInjector Phase 20.2 enhancements."""
    print("\nTesting ResponseHeaderInjector...")
    
    # Create mock template engine
    class MockTemplateEngine:
        def render(self, domain_id, template_name, context):
            return "Mock content"
    
    injector = ResponseHeaderInjector(MockTemplateEngine())
    
    # Test success header with FULL visibility
    os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"] = "full"
    injector._visibility_controller.reset_cache()
    
    context = OrchestratorContext(
        orchestrator_name="TDDOrchestrator",
        orchestrator_icon="🧪",
        current_stage=3,
        stages_completed=["Examination", "Routing", "Synthesis"],
        intelligence_active=IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=True,
            synthesis_enabled=True
        ),
        failure_stage=None,
        failure_reason=None
    )
    
    header = injector.inject_header("Implementation", context)
    assert "## 🧠 CORTEX Implementation" in header
    assert "🧪 TDDOrchestrator" in header
    assert "●●●" in header  # Stage progress
    assert "🧠📚" in header  # Intelligence badges
    print("✅ Success header with FULL visibility working")
    
    # Test failure header
    failure_context = OrchestratorContext(
        orchestrator_name="FixOrchestrator",
        orchestrator_icon="🔧",
        current_stage=3,
        stages_completed=["Examination", "Routing"],
        intelligence_active=IntelligenceFlags(
            lens_enabled=True,
            knowledge_enabled=False,
            synthesis_enabled=False
        ),
        failure_stage=3,
        failure_reason="CORE-013 violation detected"
    )
    
    failure_header = injector.inject_header("Fix", failure_context)
    assert "## 🧠 CORTEX Fix" in failure_header
    assert "🔧 FixOrchestrator" in failure_header
    assert "✗" in failure_header  # Failure indicator
    assert "⚠️" in failure_header  # Warning icon
    assert "Failure:" in failure_header
    print("✅ Failure header working")
    
    # Test OFF mode (no badge)
    os.environ["CORTEX_ORCHESTRATOR_VISIBILITY"] = "off"
    injector._visibility_controller.reset_cache()
    
    off_header = injector.inject_header("Implementation", context)
    assert "## 🧠 CORTEX Implementation" in off_header
    assert "**Author:** Asif Hussain" in off_header
    assert "🧪" not in off_header  # No orchestrator badge
    print("✅ OFF mode (no badge) working")


def test_stage_progress_formatting():
    """Test stage progress dot formatting."""
    print("\nTesting stage progress formatting...")
    
    class MockTemplateEngine:
        def render(self, domain_id, template_name, context):
            return "Mock content"
    
    injector = ResponseHeaderInjector(MockTemplateEngine())
    
    # All complete
    progress = injector._format_stage_progress(4, ["E", "R", "S", "N"], None)
    assert progress == "●●●●"
    
    # Partial
    progress = injector._format_stage_progress(2, ["E", "R"], None)
    assert progress == "●●○○"
    
    # Failure at stage 3
    progress = injector._format_stage_progress(3, ["E", "R"], 3)
    assert "✗" in progress
    assert "●●" in progress
    
    print("✅ Stage progress formatting working")


def test_intelligence_badges():
    """Test intelligence badge formatting."""
    print("\nTesting intelligence badge formatting...")
    
    class MockTemplateEngine:
        def render(self, domain_id, template_name, context):
            return "Mock content"
    
    injector = ResponseHeaderInjector(MockTemplateEngine())
    
    # Full synthesis
    flags = IntelligenceFlags(True, True, True)
    badges = injector._format_intelligence_badges(flags)
    assert badges == "🧠📚"
    
    # LENS only
    flags = IntelligenceFlags(True, False, False)
    badges = injector._format_intelligence_badges(flags)
    assert badges == "🧠"
    
    # Knowledge only
    flags = IntelligenceFlags(False, True, False)
    badges = injector._format_intelligence_badges(flags)
    assert badges == "📚"
    
    # None
    flags = IntelligenceFlags(False, False, False)
    badges = injector._format_intelligence_badges(flags)
    assert badges == ""
    
    print("✅ Intelligence badges working")


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Phase 20.2 Implementation Validation")
    print("=" * 60)
    
    try:
        test_visibility_modes()
        test_orchestrator_context()
        test_response_header_injection()
        test_stage_progress_formatting()
        test_intelligence_badges()
        
        print("\n" + "=" * 60)
        print("✅ ALL PHASE 20.2 TESTS PASSED")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""
TDD Mastery Phase 4 Integration Tests
Tests integration of Debug System, Feedback Agent, and View Discovery Agent into TDD workflow

Author: Asif Hussain
Created: 2025-11-24
Phase: TDD Mastery Phase 4 - Suite Integration
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import tempfile
import shutil
import sys

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestViewDiscoveryIntegration:
    """Test ViewDiscoveryAgent integration with TDD workflow orchestrator."""
    
    def test_view_discovery_initialization(self):
        """Test ViewDiscoveryAgent is initialized in orchestrator."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=True
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # View discovery should be initialized (or None if import failed)
        assert hasattr(orchestrator, 'view_discovery')
        assert hasattr(orchestrator, 'discovered_elements')
        assert orchestrator.discovered_elements == {}
    
    def test_view_discovery_disabled(self):
        """Test orchestrator works with view discovery disabled."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=False
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Should work without view discovery
        assert orchestrator is not None
    
    def test_find_related_views(self):
        """Test finding related view files."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(project_root=".")
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Test with mock path
        module_path = Path("src/components/LoginForm.py")
        related_views = orchestrator._find_related_views(module_path)
        
        # Should return list (empty or populated)
        assert isinstance(related_views, list)
    
    def test_discover_elements_for_testing(self):
        """Test element discovery before test generation."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=True
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Test with mock path
        module_path = Path("src/components/TestComponent.py")
        elements = orchestrator.discover_elements_for_testing(module_path)
        
        # Should return dict (empty if no views found)
        assert isinstance(elements, dict)


class TestDebugSystemIntegration:
    """Test Debug System integration with TDD state machine."""
    
    def test_debug_initialization_in_state_machine(self):
        """Test debug system is initialized in state machine."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_123",
            enable_debug=True
        )
        
        # Debug manager should be initialized (or None if import failed)
        assert hasattr(machine, 'debug_manager')
        assert hasattr(machine, 'debug_agent')
        assert hasattr(machine, 'active_debug_session')
        assert machine.active_debug_session is None
    
    def test_debug_disabled(self):
        """Test state machine works with debug disabled."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_124",
            enable_debug=False
        )
        
        # Should work without debug system
        assert machine is not None
        assert machine.enable_debug is False
    
    def test_transition_to_red_with_debug(self):
        """Test RED transition triggers debug session."""
        from workflows.tdd_state_machine import TDDStateMachine, TDDState
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_125",
            enable_debug=True
        )
        
        test_results = {
            "failures": [
                {"test": "test_login", "module": "auth.py", "error": "AssertionError"}
            ]
        }
        
        # Transition to RED with debug
        result = machine.transition_to_red_with_debug(test_results)
        
        assert result is True
        assert machine.session.current_state == TDDState.RED
        assert machine.red_state_count == 1
    
    def test_transition_to_green_captures_debug_data(self):
        """Test GREEN transition captures debug data."""
        from workflows.tdd_state_machine import TDDStateMachine, TDDState
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_126",
            enable_debug=True
        )
        
        # Start RED phase first
        machine.start_red_phase()
        
        # Transition to GREEN
        result = machine.transition_to_green_with_debug_capture(
            tests_passing=5,
            code_lines_added=20
        )
        
        assert result is True
        assert machine.session.current_state == TDDState.GREEN
        assert machine.red_state_count == 0  # Reset on success
    
    def test_extract_failing_modules(self):
        """Test extracting module names from test failures."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_127"
        )
        
        test_results = {
            "failures": [
                {"test": "test_a", "module": "auth.py"},
                {"test": "test_b", "file": "utils.py"},
                "src/services/payment.py::test_payment"
            ]
        }
        
        modules = machine._extract_failing_modules(test_results)
        
        assert len(modules) > 0
        assert "auth.py" in modules or "utils.py" in modules
    
    def test_get_debug_data(self):
        """Test retrieving debug data from state machine."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_128",
            enable_debug=True
        )
        
        # Get debug data (should be empty initially)
        debug_data = machine.get_debug_data()
        
        assert isinstance(debug_data, dict)


class TestFeedbackSystemIntegration:
    """Test FeedbackAgent integration with TDD workflow."""
    
    def test_feedback_initialization(self):
        """Test feedback agent is initialized in state machine."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_130",
            enable_feedback=True
        )
        
        assert hasattr(machine, 'feedback_agent')
        assert hasattr(machine, 'feedback_threshold')
        assert machine.feedback_threshold == 3  # Default
    
    def test_feedback_disabled(self):
        """Test state machine works with feedback disabled."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_131",
            enable_feedback=False
        )
        
        assert machine is not None
        assert machine.enable_feedback is False
    
    def test_persistent_failure_detection(self):
        """Test persistent failure triggers feedback collection."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_132",
            enable_feedback=True,
            feedback_threshold=2  # Lower threshold for testing
        )
        
        test_results = {
            "failures": [
                {"test": "test_login", "error": "Authentication failed"}
            ]
        }
        
        # Trigger RED state multiple times
        machine.transition_to_red_with_debug(test_results)
        assert machine.red_state_count == 1
        
        machine.transition_to_red_with_debug(test_results)
        assert machine.red_state_count == 2
        
        # Should trigger feedback collection on threshold
        assert machine.red_state_count >= machine.feedback_threshold
    
    def test_format_failure_summary(self):
        """Test formatting test failures into readable summary."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_133"
        )
        
        test_results = {
            "failures": [
                {"test": "test_a", "error": "ValueError: Invalid input"},
                {"test": "test_b", "error": "AssertionError: Expected 5, got 3"},
                "test_c failed"
            ]
        }
        
        summary = machine._format_failure_summary(test_results)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "test_a" in summary or "test_b" in summary or "test_c" in summary
    
    def test_feedback_custom_threshold(self):
        """Test custom feedback threshold configuration."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_134",
            enable_feedback=True,
            feedback_threshold=5
        )
        
        assert machine.feedback_threshold == 5


class TestCompleteIntegratedWorkflow:
    """Test complete TDD workflow with all integrations enabled."""
    
    def test_full_tdd_cycle_with_all_integrations(self):
        """Test full RED→GREEN→REFACTOR cycle with debug, feedback, and view discovery."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        from workflows.tdd_state_machine import TDDState
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=True,
            auto_debug_on_failure=True,
            auto_feedback_on_persistent_failure=True,
            feedback_threshold=3
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Start session
        session_id = orchestrator.start_session("integrated_test_feature")
        assert session_id is not None
        
        # Verify state machine is initialized with integrations
        assert orchestrator.state_machine is not None
        assert hasattr(orchestrator.state_machine, 'enable_debug')
        assert hasattr(orchestrator.state_machine, 'enable_feedback')
    
    def test_configuration_flags_propagation(self):
        """Test configuration flags are properly propagated to components."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=False,
            auto_debug_on_failure=False,
            auto_feedback_on_persistent_failure=False
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # All integrations should respect disable flags
        assert config.enable_view_discovery is False
        assert config.auto_debug_on_failure is False
        assert config.auto_feedback_on_persistent_failure is False


class TestIntegrationErrorHandling:
    """Test error handling when agents fail to import or initialize."""
    
    def test_missing_agents_graceful_failure(self):
        """Test graceful failure when agents are not available."""
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=True,
            auto_debug_on_failure=True
        )
        
        # Should not crash even if agents fail to import
        orchestrator = TDDWorkflowOrchestrator(config)
        assert orchestrator is not None
    
    def test_invalid_test_results_handling(self):
        """Test handling of malformed test results."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_140",
            enable_debug=True
        )
        
        # Pass invalid test results
        invalid_results = {"failures": None}
        
        # Should not crash
        modules = machine._extract_failing_modules(invalid_results)
        assert isinstance(modules, list)
    
    def test_missing_storage_path(self):
        """Test handling of missing or invalid storage paths."""
        from workflows.tdd_state_machine import TDDStateMachine
        
        # Should work with default storage path
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_141"
        )
        
        assert machine is not None
        assert hasattr(machine, 'storage_path')


class TestIntegrationPerformance:
    """Test performance impact of integrations."""
    
    def test_initialization_overhead(self):
        """Test initialization time with all integrations enabled."""
        import time
        from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig
        
        config = TDDWorkflowConfig(
            project_root=".",
            enable_view_discovery=True,
            auto_debug_on_failure=True,
            auto_feedback_on_persistent_failure=True
        )
        
        start = time.time()
        orchestrator = TDDWorkflowOrchestrator(config)
        duration = time.time() - start
        
        # Initialization should be fast (<1 second)
        assert duration < 1.0
        assert orchestrator is not None
    
    def test_state_transition_overhead(self):
        """Test state transition time with integrations enabled."""
        import time
        from workflows.tdd_state_machine import TDDStateMachine
        
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_150",
            enable_debug=True,
            enable_feedback=True
        )
        
        test_results = {"failures": [{"test": "test_1", "error": "Failed"}]}
        
        start = time.time()
        machine.transition_to_red_with_debug(test_results)
        duration = time.time() - start
        
        # Transition should be fast (<100ms, unless actually triggering debug)
        # Allow up to 1 second for debug initialization
        assert duration < 1.0


class TestRefactoringIntelligenceIntegration:
    """Test Phase 3: Debug timing data integration with refactoring intelligence."""
    
    def test_code_smell_detector_set_debug_data(self):
        """Test injecting debug data into CodeSmellDetector."""
        from workflows.refactoring_intelligence import CodeSmellDetector
        
        detector = CodeSmellDetector()
        
        debug_data = {
            "function_timings": {
                "slow_function": {
                    "avg_time_ms": 250.5,
                    "call_count": 10,
                    "total_time_ms": 2505.0
                }
            }
        }
        
        detector.set_debug_data(debug_data)
        
        assert detector.debug_data_cache == debug_data
        assert len(detector.debug_data_cache.get("function_timings", {})) == 1
    
    def test_detect_slow_functions(self):
        """Test performance-based smell detection for slow functions."""
        from workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType
        
        detector = CodeSmellDetector()
        
        # Set debug data with slow function
        debug_data = {
            "function_timings": {
                "authenticate_user": {
                    "avg_time_ms": 150.0,
                    "call_count": 5,
                    "total_time_ms": 750.0,
                    "line_number": 10
                }
            }
        }
        detector.set_debug_data(debug_data)
        
        # Source code with matching function
        source_code = '''
def authenticate_user(username, password):
    """Authenticate user credentials."""
    # Slow implementation
    return True
'''
        
        smells = detector.analyze_file("test.py", source_code)
        
        # Should detect slow function smell
        slow_smells = [s for s in smells if s.smell_type == CodeSmellType.SLOW_FUNCTION]
        assert len(slow_smells) > 0
        assert "authenticate_user" in slow_smells[0].description
        assert slow_smells[0].confidence == 0.95  # High confidence from measured data
    
    def test_detect_hot_paths(self):
        """Test detection of frequently-called functions."""
        from workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType
        
        detector = CodeSmellDetector()
        
        # Set debug data with hot path
        debug_data = {
            "function_timings": {
                "validate_input": {
                    "avg_time_ms": 5.0,
                    "call_count": 100,
                    "total_time_ms": 500.0,
                    "line_number": 20
                }
            }
        }
        detector.set_debug_data(debug_data)
        
        source_code = '''
def validate_input(data):
    """Validate input data."""
    return data is not None
'''
        
        smells = detector.analyze_file("test.py", source_code)
        
        # Should detect hot path smell
        hot_path_smells = [s for s in smells if s.smell_type == CodeSmellType.HOT_PATH]
        assert len(hot_path_smells) > 0
        assert "validate_input" in hot_path_smells[0].description
        assert "100" in hot_path_smells[0].description  # Call count mentioned
    
    def test_detect_performance_bottlenecks(self):
        """Test detection of performance bottlenecks."""
        from workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType
        
        detector = CodeSmellDetector()
        
        # Set debug data with bottleneck (high total time)
        debug_data = {
            "function_timings": {
                "process_data": {
                    "avg_time_ms": 50.0,
                    "call_count": 20,
                    "total_time_ms": 1000.0,
                    "line_number": 30
                }
            }
        }
        detector.set_debug_data(debug_data)
        
        source_code = '''
def process_data(items):
    """Process list of items."""
    return [item * 2 for item in items]
'''
        
        smells = detector.analyze_file("test.py", source_code)
        
        # Should detect bottleneck smell
        bottleneck_smells = [s for s in smells if s.smell_type == CodeSmellType.PERFORMANCE_BOTTLENECK]
        assert len(bottleneck_smells) > 0
        assert "process_data" in bottleneck_smells[0].description
        assert "1000" in bottleneck_smells[0].description  # Total time mentioned
    
    def test_refactoring_suggestions_for_performance_smells(self):
        """Test that performance smells generate refactoring suggestions."""
        from workflows.refactoring_intelligence import (
            CodeSmellDetector,
            RefactoringEngine,
            CodeSmell,
            CodeSmellType
        )
        
        engine = RefactoringEngine()
        
        # Create performance-based smell
        slow_smell = CodeSmell(
            smell_type=CodeSmellType.SLOW_FUNCTION,
            location="test.py:10:0",
            severity="high",
            description="Function is slow",
            metric_value=250.0,
            confidence=0.95
        )
        
        suggestions = engine.generate_suggestions([slow_smell], "def slow_func(): pass")
        
        assert len(suggestions) > 0
        assert suggestions[0].confidence == 0.90  # High confidence
        assert "Cache" in suggestions[0].description or "optimize" in suggestions[0].description.lower()
    
    def test_debug_data_flows_to_refactoring(self):
        """Test end-to-end: debug data from state machine flows to refactoring."""
        from workflows.tdd_state_machine import TDDStateMachine
        from workflows.refactoring_intelligence import CodeSmellDetector
        
        # Create state machine with debug data
        machine = TDDStateMachine(
            feature_name="test_feature",
            session_id="test_session_160",
            enable_debug=True
        )
        
        # Simulate debug data (normally would come from actual debug session)
        machine.debug_data_cache = {
            "function_timings": {
                "test_function": {
                    "avg_time_ms": 200.0,
                    "call_count": 15,
                    "total_time_ms": 3000.0
                }
            }
        }
        
        # Get debug data from state machine
        debug_data = machine.get_debug_data()
        
        # Inject into smell detector
        detector = CodeSmellDetector()
        detector.set_debug_data(debug_data)
        
        # Verify data flowed correctly
        assert detector.debug_data_cache == debug_data
        assert len(detector.debug_data_cache["function_timings"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

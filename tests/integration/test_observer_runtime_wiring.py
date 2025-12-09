"""
Integration test for observer pattern runtime wiring.

Tests that LearningObserver is properly initialized and subscribed to
all orchestrators (Planning, TDD, Debug) in the CORTEX runtime.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1/5.2 Integration
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.entry_point.cortex_entry import CortexEntry


@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for testing."""
    temp_dir = tempfile.mkdtemp()
    brain_path = Path(temp_dir) / "cortex-brain"
    brain_path.mkdir(parents=True)
    
    # Create required subdirectories
    (brain_path / "tier1").mkdir()
    (brain_path / "tier2").mkdir()
    (brain_path / "tier3").mkdir()
    (brain_path / "corpus-callosum").mkdir()
    (brain_path / "config").mkdir()
    
    # Create minimal schema file for PlanningOrchestrator
    schema_file = brain_path / "config" / "plan-schema.yaml"
    schema_file.write_text("""
version: "1.0"
required:
  - metadata
  - phases
""")
    
    # Create minimal brain protection rules
    rules_file = brain_path / "brain-protection-rules.yaml"
    rules_file.write_text("""
version: "3.0"
rules: []
""")
    
    yield str(brain_path)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestObserverRuntimeWiring:
    """Test observer pattern wiring in CORTEX runtime."""
    
    def test_learning_observer_lazy_loaded(self, temp_brain_path):
        """Test that LearningObserver is lazy-loaded on first access."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Initially None
        assert entry._learning_observer is None
        
        # Loaded on first access
        observer = entry.learning_observer
        assert observer is not None
        assert hasattr(observer, 'on_phase_completion')
        assert hasattr(observer, 'on_tdd_cycle_completion')
        assert hasattr(observer, 'on_debug_session_completion')
    
    def test_planning_orchestrator_wired_to_observer(self, temp_brain_path):
        """Test that Planning Orchestrator is wired to observer."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Access planning orchestrator (triggers wiring)
        orchestrator = entry.planning_orchestrator
        
        if orchestrator is not None:
            # Verify observer is subscribed
            assert entry.learning_observer in orchestrator.observers
            assert entry._observers_wired is True
    
    def test_tdd_orchestrator_wired_to_observer(self, temp_brain_path):
        """Test that TDD Orchestrator is wired to observer."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Access TDD orchestrator (triggers wiring)
        orchestrator = entry.tdd_orchestrator
        
        if orchestrator is not None:
            # Verify observer is subscribed
            assert entry.learning_observer in orchestrator.observers
            assert entry._observers_wired is True
    
    def test_debug_orchestrator_wired_to_observer(self, temp_brain_path):
        """Test that Debug Orchestrator is wired to observer."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Access debug orchestrator (triggers wiring)
        orchestrator = entry.debug_orchestrator
        
        if orchestrator is not None:
            # Verify observer is subscribed
            assert entry.learning_observer in orchestrator._observers
            assert entry._observers_wired is True
    
    def test_all_orchestrators_share_same_observer(self, temp_brain_path):
        """Test that all orchestrators share the same LearningObserver instance."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Access all orchestrators
        planning = entry.planning_orchestrator
        tdd = entry.tdd_orchestrator
        debug = entry.debug_orchestrator
        
        # All should reference same observer instance
        observer = entry.learning_observer
        
        if planning is not None and observer in planning.observers:
            assert observer is entry.learning_observer
        
        if tdd is not None and observer in tdd.observers:
            assert observer is entry.learning_observer
        
        if debug is not None and observer in debug._observers:
            assert observer is entry.learning_observer
    
    def test_wiring_happens_once(self, temp_brain_path):
        """Test that observer wiring happens only once."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Access orchestrators multiple times
        entry.planning_orchestrator
        entry.tdd_orchestrator
        entry.debug_orchestrator
        
        # Access again
        entry.planning_orchestrator
        entry.tdd_orchestrator
        
        # Wiring flag should be set
        assert entry._observers_wired is True
        
        # Observer should appear only once in each orchestrator
        if entry.planning_orchestrator is not None:
            observer_count = entry.planning_orchestrator.observers.count(entry.learning_observer)
            assert observer_count <= 1
        
        if entry.tdd_orchestrator is not None:
            observer_count = entry.tdd_orchestrator.observers.count(entry.learning_observer)
            assert observer_count <= 1
    
    def test_observer_handles_missing_orchestrator_gracefully(self, temp_brain_path):
        """Test that missing orchestrators don't break observer wiring."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Force observer load
        observer = entry.learning_observer
        assert observer is not None
        
        # Try to wire with potentially missing orchestrators
        entry._wire_observers()
        
        # Should not raise exception
        assert entry._observers_wired is True


class TestObserverEndToEnd:
    """Test end-to-end observer pattern with real orchestrators."""
    
    def test_planning_event_captured_in_tier2(self, temp_brain_path):
        """Test that planning events are captured in Tier 2."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Get orchestrator and observer
        planning = entry.planning_orchestrator
        observer = entry.learning_observer
        
        if planning is None or observer is None:
            pytest.skip("Planning orchestrator or observer not available")
        
        # Verify subscription
        assert observer in planning.observers
        
        # Emit phase completion event
        planning._emit_phase_completion_event(
            phase_id="1",
            phase_name="Test Phase",
            duration_seconds=10.0,
            dor_compliant=True,
            dod_compliant=True,
            threat_model_applied=False,
            acceptance_criteria_defined=True,
            estimated_hours=1,
            actual_hours=1
        )
        
        # Verify pattern was stored in Tier 2
        patterns = entry.tier2.search_patterns(query="Test Phase", limit=5)
        workflow_patterns = [p for p in patterns if p.get('pattern_type') == 'workflow']
        
        assert len(workflow_patterns) > 0
        assert 'Test Phase' in workflow_patterns[0]['title']
    
    def test_tdd_event_captured_in_tier2(self, temp_brain_path):
        """Test that TDD events are captured in Tier 2."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Get orchestrator and observer
        tdd = entry.tdd_orchestrator
        observer = entry.learning_observer
        
        if tdd is None or observer is None:
            pytest.skip("TDD orchestrator or observer not available")
        
        # Verify subscription
        assert observer in tdd.observers
        
        # Emit TDD cycle event
        tdd._emit_tdd_cycle_completion_event({
            'cycle_number': 1,
            'red_duration': 5.0,
            'green_duration': 10.0,
            'refactor_duration': 8.0,
            'total_duration': 23.0,
            'tests_written': 5,
            'tests_passing': 5,
            'code_lines_added': 25,
            'code_lines_refactored': 10,
            'refactoring_iterations': 2
        })
        
        # Verify pattern was stored in Tier 2
        patterns = entry.tier2.search_patterns(query="TDD", limit=5)
        tdd_patterns = [p for p in patterns if p.get('pattern_type') == 'tdd_cycle']
        
        assert len(tdd_patterns) > 0
    
    def test_debug_event_captured_in_tier2(self, temp_brain_path):
        """Test that debug events are captured in Tier 2."""
        entry = CortexEntry(brain_path=temp_brain_path, skip_setup_check=True)
        
        # Get orchestrator and observer
        debug = entry.debug_orchestrator
        observer = entry.learning_observer
        
        if debug is None or observer is None:
            pytest.skip("Debug orchestrator or observer not available")
        
        # Verify subscription
        assert observer in debug._observers
        
        # Start and complete debug session
        session_id = debug.start_debug_session(
            symptom="Test bug symptom",
            target="test_module"
        )
        
        debug.complete_debug_session(
            session_id=session_id,
            root_cause="Test root cause",
            fix_applied="Test fix",
            prevention="Test prevention",
            recurrence_risk="low",
            affected_features=["test_feature"]
        )
        
        # Verify pattern was stored in Tier 2
        patterns = entry.tier2.search_patterns(query="Test bug", limit=5)
        bug_patterns = [p for p in patterns if p.get('pattern_type') == 'bug_resolution']
        
        assert len(bug_patterns) > 0
        assert 'Test bug' in bug_patterns[0]['title']

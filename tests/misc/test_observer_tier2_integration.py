"""
Integration tests for Observer pattern with Tier 2 Knowledge Graph.

Tests LearningObserver directly - validates event processing and Tier 2 storage.
Uses real KG database, no orchestrator mocking complexity.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1 (Task 5.1.5)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import time

from src.orchestrators.learning_observer import LearningObserver
from src.tier2.knowledge_graph import KnowledgeGraph


@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for integration testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_brain_path):
    """Create KnowledgeGraph with temporary database."""
    db_path = Path(temp_brain_path) / "tier2" / "test_kg.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    kg_instance = KnowledgeGraph(db_path=db_path)
    yield kg_instance
    if hasattr(kg_instance, 'connection_manager'):
        kg_instance.connection_manager.close()


@pytest.fixture
def learning_observer(kg):
    """Create LearningObserver connected to test KG."""
    return LearningObserver(knowledge_graph=kg)


class TestPlanningEventToTier2:
    """Test Planning event processing through LearningObserver to Tier 2."""
    
    def test_planning_phase_completion_stores_in_tier2(self, learning_observer, kg):
        """Test that planning phase completion event stores pattern in Tier 2."""
        # Simulate phase completion event
        event = {
            'phase_id': '1.1',
            'phase_name': 'Requirements Analysis',
            'duration_seconds': 120.5,
            'dor_compliant': True,
            'dod_compliant': True,
            'threat_model_applied': False,
            'acceptance_criteria_defined': True,
            'estimated_hours': 2,
            'actual_hours': 2
        }
        
        # Process event through observer
        learning_observer.on_phase_completion(event)
        
        # Query Tier 2 for stored pattern
        results = kg.search_patterns(
            query="Requirements Analysis",
            scope="cortex",
            limit=5
        )
        
        # Filter for workflow patterns
        workflow_patterns = [r for r in results if r['pattern_type'] == 'workflow']
        
        # Verify pattern was stored
        assert len(workflow_patterns) > 0
        pattern = workflow_patterns[0]
        assert 'Requirements Analysis' in pattern['title']
        assert pattern['metadata']['phase_name'] == 'Requirements Analysis'
        assert pattern['metadata']['dor_compliant'] is True
        assert pattern['metadata']['dod_compliant'] is True
    
    def test_planning_confidence_calculation(self, learning_observer, kg):
        """Test that pattern confidence reflects DoR/DoD compliance."""
        # Low quality event (DoR/DoD not met)
        event_low = {
            'phase_id': '1.1',
            'phase_name': 'Low Quality Phase',
            'duration_seconds': 60.0,
            'dor_compliant': False,
            'dod_compliant': False,
            'threat_model_applied': False,
            'acceptance_criteria_defined': False,
            'estimated_hours': 1,
            'actual_hours': 1
        }
        
        learning_observer.on_phase_completion(event_low)
        
        # High quality event (DoR/DoD met)
        event_high = {
            'phase_id': '2.1',
            'phase_name': 'High Quality Phase',
            'duration_seconds': 120.0,
            'dor_compliant': True,
            'dod_compliant': True,
            'threat_model_applied': True,
            'acceptance_criteria_defined': True,
            'estimated_hours': 2,
            'actual_hours': 2
        }
        
        learning_observer.on_phase_completion(event_high)
        
        # Query for both patterns
        results_low = kg.search_patterns(query="Low Quality Phase", limit=1)
        results_high = kg.search_patterns(query="High Quality Phase", limit=1)
        
        assert len(results_low) > 0 and len(results_high) > 0
        
        confidence_low = results_low[0]['confidence']
        confidence_high = results_high[0]['confidence']
        
        # High quality should have higher confidence
        assert confidence_high > confidence_low
    
    def test_planning_estimation_accuracy_captured(self, learning_observer, kg):
        """Test that estimation accuracy is calculated and stored."""
        event = {
            'phase_id': '3.1',
            'phase_name': 'Estimation Test Phase',
            'duration_seconds': 7200.0,  # 2 hours
            'dor_compliant': True,
            'dod_compliant': True,
            'threat_model_applied': False,
            'acceptance_criteria_defined': True,
            'estimated_hours': 2,
            'actual_hours': 2
        }
        
        learning_observer.on_phase_completion(event)
        
        results = kg.search_patterns(query="Estimation Test Phase", limit=1)
        assert len(results) > 0
        
        pattern = results[0]
        # Verify estimation accuracy metadata
        assert 'estimation_accuracy' in pattern['metadata']
        # Perfect estimate should be 1.0
        assert pattern['metadata']['estimation_accuracy'] == 1.0


class TestTDDEventToTier2:
    """Test TDD event processing through LearningObserver to Tier 2."""
    
    def test_tdd_cycle_completion_stores_in_tier2(self, learning_observer, kg):
        """Test that TDD cycle completion event stores pattern in Tier 2."""
        # Simulate TDD cycle event
        event = {
            'cycle_number': 1,
            'phase': 'GREEN',
            'duration_seconds': 45.2,
            'tests_added': 3,
            'tests_passing': 3,
            'tests_failing': 0,
            'code_lines_added': 25,
            'refactoring_applied': False,
            'test_to_code_ratio': 0.12
        }
        
        # Process event through observer
        learning_observer.on_tdd_cycle_completion(event)
        
        # Query Tier 2
        results = kg.search_patterns(
            query="TDD cycle GREEN",
            scope="cortex",
            limit=5
        )
        
        # Filter for tdd_cycle patterns
        tdd_patterns = [r for r in results if r['pattern_type'] == 'tdd_cycle']
        
        # Verify pattern stored
        assert len(tdd_patterns) > 0
        pattern = tdd_patterns[0]
        assert pattern['metadata']['phase'] == 'GREEN'
        assert pattern['metadata']['tests_passing'] == 3
        assert 'test_to_code_ratio' in pattern['metadata']
    
    def test_tdd_all_phases_captured(self, learning_observer, kg):
        """Test that all TDD phases (RED, GREEN, REFACTOR) are captured."""
        phases = ['RED', 'GREEN', 'REFACTOR']
        
        for i, phase in enumerate(phases, 1):
            event = {
                'cycle_number': i,
                'phase': phase,
                'duration_seconds': 30.0 + i * 5,
                'tests_added': 2,
                'tests_passing': 2 if phase != 'RED' else 0,
                'tests_failing': 2 if phase == 'RED' else 0,
                'code_lines_added': 20,
                'refactoring_applied': phase == 'REFACTOR',
                'test_to_code_ratio': 0.1
            }
            
            learning_observer.on_tdd_cycle_completion(event)
        
        # Verify all phases stored
        for phase in phases:
            results = kg.search_patterns(query=f"TDD cycle {phase}", limit=5)
            tdd_patterns = [r for r in results if r['pattern_type'] == 'tdd_cycle']
            assert len(tdd_patterns) > 0, f"No patterns found for {phase}"


class TestPerformanceIntegration:
    """Test performance characteristics of observer integration."""
    
    def test_observer_processing_under_50ms(self, learning_observer):
        """Test that event processing completes under 50ms."""
        event = {
            'phase_id': '1.1',
            'phase_name': 'Performance Test Phase',
            'duration_seconds': 10.0,
            'dor_compliant': True,
            'dod_compliant': True,
            'threat_model_applied': False,
            'acceptance_criteria_defined': True,
            'estimated_hours': 1,
            'actual_hours': 1
        }
        
        # Measure processing time
        start_time = time.perf_counter()
        learning_observer.on_phase_completion(event)
        end_time = time.perf_counter()
        
        processing_ms = (end_time - start_time) * 1000
        
        # Verify under 50ms target
        assert processing_ms < 50.0, f"Processing took {processing_ms:.2f}ms (target: <50ms)"
    
    def test_batch_event_processing(self, learning_observer):
        """Test processing multiple events in sequence."""
        events = []
        for i in range(10):
            events.append({
                'phase_id': f'{i}.1',
                'phase_name': f'Batch Test Phase {i}',
                'duration_seconds': 15.0,
                'dor_compliant': True,
                'dod_compliant': True,
                'threat_model_applied': False,
                'acceptance_criteria_defined': True,
                'estimated_hours': 1,
                'actual_hours': 1
            })
        
        # Measure batch processing
        start_time = time.perf_counter()
        for event in events:
            learning_observer.on_phase_completion(event)
        end_time = time.perf_counter()
        
        total_ms = (end_time - start_time) * 1000
        avg_ms = total_ms / len(events)
        
        # Average should still be under 50ms
        assert avg_ms < 50.0, f"Average processing: {avg_ms:.2f}ms (target: <50ms)"


class TestEventPayloadIntegrity:
    """Test that event payloads preserve all fields through pipeline."""
    
    def test_all_planning_fields_preserved(self, learning_observer, kg):
        """Test that all planning event fields reach Tier 2."""
        event = {
            'phase_id': '4.2',
            'phase_name': 'Payload Integrity Test',
            'duration_seconds': 180.5,
            'dor_compliant': True,
            'dod_compliant': True,
            'threat_model_applied': True,
            'acceptance_criteria_defined': True,
            'estimated_hours': 3,
            'actual_hours': 3,
            'custom_field': 'custom_value'  # Custom field
        }
        
        learning_observer.on_phase_completion(event)
        
        results = kg.search_patterns(query="Payload Integrity Test", limit=1)
        assert len(results) > 0
        
        pattern = results[0]
        metadata = pattern['metadata']
        
        # Verify all standard fields
        assert metadata['phase_id'] == '4.2'
        assert metadata['phase_name'] == 'Payload Integrity Test'
        assert metadata['duration_seconds'] == 180.5
        assert metadata['dor_compliant'] is True
        assert metadata['threat_model_applied'] is True
        assert metadata['estimated_hours'] == 3
        
        # Verify custom field preserved
        assert metadata['custom_field'] == 'custom_value'
    
    def test_all_tdd_fields_preserved(self, learning_observer, kg):
        """Test that all TDD event fields reach Tier 2."""
        event = {
            'cycle_number': 7,
            'phase': 'REFACTOR',
            'duration_seconds': 55.8,
            'tests_added': 4,
            'tests_passing': 4,
            'tests_failing': 0,
            'code_lines_added': 40,
            'refactoring_applied': True,
            'test_to_code_ratio': 0.1,
            'feature': 'authentication',  # Custom field
            'layer': 'domain'  # Custom field
        }
        
        learning_observer.on_tdd_cycle_completion(event)
        
        results = kg.search_patterns(query="TDD cycle REFACTOR", limit=5)
        tdd_patterns = [r for r in results if r['pattern_type'] == 'tdd_cycle']
        assert len(tdd_patterns) > 0
        
        pattern = tdd_patterns[0]
        metadata = pattern['metadata']
        
        # Verify all fields including custom ones
        assert metadata['cycle_number'] == 7
        assert metadata['phase'] == 'REFACTOR'
        assert metadata['refactoring_applied'] is True
        assert metadata['feature'] == 'authentication'
        assert metadata['layer'] == 'domain'


class TestObserverErrorHandling:
    """Test error handling in observer integration."""
    
    def test_invalid_event_handled_gracefully(self, learning_observer):
        """Test that invalid events don't crash observer."""
        # Missing required fields
        invalid_event = {
            'phase_name': 'Incomplete Event'
            # Missing phase_id and other required fields
        }
        
        # Should not raise exception
        try:
            learning_observer.on_phase_completion(invalid_event)
            handled = True
        except Exception:
            handled = False
        
        assert handled, "Observer should handle invalid events gracefully"
    
    def test_tier2_storage_failure_logged(self, kg):
        """Test that Tier 2 storage failures are handled gracefully."""
        # Close KG to simulate storage failure
        if hasattr(kg, 'connection_manager'):
            kg.connection_manager.close()
        
        observer = LearningObserver(knowledge_graph=kg)
        
        event = {
            'cycle_number': 1,
            'phase': 'GREEN',
            'duration_seconds': 20.0,
            'tests_added': 1,
            'tests_passing': 1,
            'tests_failing': 0,
            'code_lines_added': 10,
            'refactoring_applied': False,
            'test_to_code_ratio': 0.1
        }
        
        # Should not raise exception even with closed KG
        try:
            observer.on_tdd_cycle_completion(event)
            handled = True
        except Exception:
            handled = False
        
        assert handled, "Observer should handle storage failures gracefully"

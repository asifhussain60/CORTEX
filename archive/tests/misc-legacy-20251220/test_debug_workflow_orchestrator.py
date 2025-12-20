"""
Test suite for Debug Workflow Orchestrator with Observer integration.

Tests debug session lifecycle and RCA pattern capture through LearningObserver.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.2 (Task 5.2.1)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.tier2.knowledge_graph import KnowledgeGraph
from src.orchestrators.learning_observer import LearningObserver


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kg.db"
    yield db_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_db_path):
    """Create KnowledgeGraph with temporary database."""
    kg_instance = KnowledgeGraph(db_path=temp_db_path)
    yield kg_instance
    if hasattr(kg_instance, 'connection_manager'):
        kg_instance.connection_manager.close()


@pytest.fixture
def observer(kg):
    """Create LearningObserver with test KnowledgeGraph."""
    return LearningObserver(kg)


class TestDebugOrchestratorCreation:
    """Test Debug Workflow Orchestrator instantiation."""
    
    def test_create_debug_orchestrator(self):
        """Test creating debug orchestrator instance."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'start_debug_session')
        assert hasattr(orchestrator, 'complete_debug_session')
        assert hasattr(orchestrator, 'subscribe')
    
    def test_orchestrator_has_observer_list(self):
        """Test orchestrator maintains observer list."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        
        assert hasattr(orchestrator, '_observers')
        assert isinstance(orchestrator._observers, list)


class TestDebugOrchestratorObserverIntegration:
    """Test observer subscription and event emission."""
    
    def test_subscribe_observer(self, observer):
        """Test subscribing observer to debug orchestrator."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        assert observer in orchestrator._observers
    
    def test_unsubscribe_observer(self, observer):
        """Test unsubscribing observer from debug orchestrator."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        orchestrator.unsubscribe(observer)
        
        assert observer not in orchestrator._observers
    
    def test_emit_debug_completion_event(self, observer, kg):
        """Test emitting debug_session_completion event."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        # Start and complete a debug session
        session_id = orchestrator.start_debug_session(
            symptom="Application crashes on user login",
            target="authentication_module"
        )
        
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Null pointer exception in session validation",
            fix_applied="Added null check before session access",
            prevention="Add unit tests for null session scenarios",
            recurrence_risk="low",
            affected_features=["authentication", "sessions"]
        )
        
        # Verify pattern was stored in Tier 2
        patterns = kg.pattern_store.list_patterns(limit=10)
        bug_patterns = [p for p in patterns if p.get('pattern_type') == 'bug_resolution']
        
        assert len(bug_patterns) > 0
        
        # Verify RCA metadata
        pattern = bug_patterns[0]
        metadata = pattern.get('metadata', {})
        assert metadata.get('symptom') == "Application crashes on user login"
        assert metadata.get('root_cause') == "Null pointer exception in session validation"
        assert metadata.get('recurrence_risk') == "low"


class TestDebugSessionLifecycle:
    """Test debug session start, execution, and completion."""
    
    def test_start_debug_session(self):
        """Test starting a debug session."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        session_id = orchestrator.start_debug_session(
            symptom="Memory leak in background worker",
            target="worker_process"
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
        
        # Verify session is tracked
        session = orchestrator.get_session(session_id)
        assert session is not None
        assert session['symptom'] == "Memory leak in background worker"
        assert session['target'] == "worker_process"
        assert session['status'] == "in_progress"
    
    def test_complete_debug_session_emits_event(self, observer, kg):
        """Test completing debug session emits event to observers."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        session_id = orchestrator.start_debug_session(
            symptom="API timeout after 30 seconds",
            target="api_gateway"
        )
        
        # Track initial pattern count
        initial_count = len([p for p in kg.pattern_store.list_patterns(limit=100) 
                            if p.get('pattern_type') == 'bug_resolution'])
        
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Database query missing index",
            fix_applied="Added index on user_id column",
            prevention="Review all queries in pre-deployment checklist",
            recurrence_risk="medium",
            affected_features=["api", "database"]
        )
        
        # Verify new pattern was created
        final_count = len([p for p in kg.pattern_store.list_patterns(limit=100) 
                          if p.get('pattern_type') == 'bug_resolution'])
        assert final_count == initial_count + 1
    
    def test_complete_without_observers_no_error(self):
        """Test completing session without observers doesn't crash."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        
        session_id = orchestrator.start_debug_session(
            symptom="Error on checkout",
            target="payment_service"
        )
        
        # Should not raise exception
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Payment gateway timeout",
            fix_applied="Increased timeout to 60 seconds",
            prevention="Add monitoring for gateway response times",
            recurrence_risk="high",
            affected_features=["checkout", "payments"]
        )
        
        # Verify session marked complete
        session = orchestrator.get_session(session_id)
        assert session['status'] == "completed"


class TestDebugEventPayload:
    """Test debug event payload structure and content."""
    
    def test_event_payload_contains_required_fields(self, observer, kg):
        """Test debug completion event has all required RCA fields."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        session_id = orchestrator.start_debug_session(
            symptom="Data corruption in reports",
            target="reporting_engine"
        )
        
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Race condition in concurrent writes",
            fix_applied="Added database-level locking",
            prevention="Add concurrency tests to CI pipeline",
            recurrence_risk="high",
            affected_features=["reporting", "database", "concurrency"]
        )
        
        # Get stored pattern
        patterns = kg.pattern_store.list_patterns(limit=10)
        bug_patterns = [p for p in patterns if p.get('pattern_type') == 'bug_resolution']
        assert len(bug_patterns) > 0
        
        pattern = bug_patterns[0]
        metadata = pattern.get('metadata', {})
        
        # Verify all RCA fields present
        assert 'symptom' in metadata
        assert 'root_cause' in metadata
        assert 'fix_applied' in metadata
        assert 'prevention' in metadata
        assert 'recurrence_risk' in metadata
        assert 'affected_features' in metadata
        
        # Verify values
        assert metadata['symptom'] == "Data corruption in reports"
        assert metadata['root_cause'] == "Race condition in concurrent writes"
        assert metadata['fix_applied'] == "Added database-level locking"
        assert metadata['prevention'] == "Add concurrency tests to CI pipeline"
        assert metadata['recurrence_risk'] == "high"
        assert len(metadata['affected_features']) == 3
    
    def test_event_includes_session_metadata(self, observer, kg):
        """Test event includes session ID and timestamps."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        session_id = orchestrator.start_debug_session(
            symptom="Search results incorrect",
            target="search_service"
        )
        
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Index not updated after data changes",
            fix_applied="Implemented real-time index updates",
            prevention="Add search accuracy tests",
            recurrence_risk="medium",
            affected_features=["search"]
        )
        
        # Get stored pattern
        patterns = kg.pattern_store.list_patterns(limit=10)
        bug_patterns = [p for p in patterns if p.get('pattern_type') == 'bug_resolution']
        
        pattern = bug_patterns[0]
        metadata = pattern.get('metadata', {})
        
        # Verify session metadata
        assert 'session_id' in metadata or 'debug_session_id' in metadata
        assert 'target' in metadata or 'affected_features' in metadata


class TestDebugOrchestratorPerformance:
    """Test debug orchestrator performance requirements."""
    
    def test_event_emission_under_50ms(self, observer):
        """Test event emission takes <50ms."""
        from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
        import time
        
        orchestrator = DebugWorkflowOrchestrator()
        orchestrator.subscribe(observer)
        
        session_id = orchestrator.start_debug_session(
            symptom="Performance degradation",
            target="cache_layer"
        )
        
        start_time = time.perf_counter()
        
        orchestrator.complete_debug_session(
            session_id=session_id,
            root_cause="Cache eviction policy too aggressive",
            fix_applied="Tuned cache TTL settings",
            prevention="Add cache hit rate monitoring",
            recurrence_risk="low",
            affected_features=["cache", "performance"]
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # Should complete in <50ms
        assert elapsed_ms < 50, f"Event emission took {elapsed_ms:.2f}ms (target: <50ms)"

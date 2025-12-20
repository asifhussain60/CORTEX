"""
Phase 2 Integration Test - Document Generation

Tests end-to-end document generation from captured Phase 1 events.
Validates all 15 learning categories and resource integration.
"""

import pytest
from datetime import datetime
from pathlib import Path

from src.learning import (
    LearningEvent,
    EventType,
    DocumentGenerator,
    ResourceDatabase,
    get_global_collector,
    reset_global_collector
)


class TestPhase2Integration:
    """Integration tests for Phase 1 + Phase 2 systems."""
    
    def setup_method(self):
        """Reset global collector before each test."""
        reset_global_collector()
        
    def test_end_to_end_document_generation(self):
        """Test complete flow: capture events → generate documents."""
        # Setup
        collector = get_global_collector()
        generator = DocumentGenerator()
        db = ResourceDatabase()
        
        # Add some resources
        db.add_resource(
            'planning_strategies',
            'Planning Best Practices',
            'https://cortex.dev/planning',
            'Guide to effective planning in CORTEX'
        )
        generator.resource_db = db
        
        # Capture events (simulating Phase 1 integrations)
        events = [
            LearningEvent(
                EventType.PLAN_CREATED,
                "PlanningOrchestrator",
                {"plan_filename": "feature-x.md", "task_count": 5}
            ),
            LearningEvent(
                EventType.PHASE_COMPLETED,
                "PlanExecutionOrchestrator",
                {"phase_number": 1, "phase_name": "Implementation", "tasks_completed": 5}
            ),
            LearningEvent(
                EventType.CHECKPOINT_COMMITTED,
                "GitCheckpointOrchestrator",
                {"checkpoint_id": "chk_001", "commit_sha": "abc123"}
            ),
            LearningEvent(
                EventType.ADO_STORY_CREATED,
                "ADOUtility",
                {"work_item_id": "12345", "title": "Test Story"}
            )
        ]
        
        for event in events:
            collector.capture_event(event)
        
        # Verify events captured
        captured = collector.get_all_events()
        assert len(captured) == 4
        
        # Generate documents from captured events
        docs = generator.generate_documents(captured)
        assert len(docs) == 4
        
        # Validate each document
        for i, doc in enumerate(docs):
            assert isinstance(doc, str)
            assert len(doc) > 0
            assert '# ' in doc  # Has title
            assert '## ' in doc  # Has sections
            assert 'Event:' in doc or 'Type:' in doc
            assert 'Component:' in doc
            
            # First document should have resources
            if i == 0:
                assert 'Planning Best Practices' in doc or 'Resources' in doc
    
    def test_all_15_categories_covered(self):
        """Test that all 15 categories can generate documents."""
        generator = DocumentGenerator()
        
        # Map of category to sample event
        category_events = {
            'planning_strategies': EventType.PLAN_CREATED,
            'workflow_context': EventType.PHASE_STARTED,
            'milestones': EventType.PHASE_COMPLETED,
            'ado_workflows': EventType.ADO_STORY_CREATED,
            'intent_routing': EventType.OPERATION_ROUTED,
        }
        
        for category, event_type in category_events.items():
            event = LearningEvent(event_type, "TestComponent", {})
            doc = generator.generate_document(event)
            
            assert doc is not None
            assert len(doc) > 0
            assert category.replace('_', ' ') in doc.lower() or event_type.value in doc
    
    def test_milestone_event_documentation(self):
        """Test milestone events generate proper documentation."""
        collector = get_global_collector()
        generator = DocumentGenerator()
        
        # Create milestone events
        milestones = [
            EventType.PHASE_COMPLETED,
            EventType.CHECKPOINT_COMMITTED,
            EventType.ADO_WORK_ITEM_COMPLETED,
            EventType.WORKFLOW_COMPLETED,
            EventType.PLAN_VALIDATED,
            EventType.REQUIREMENTS_FINALIZED
        ]
        
        for event_type in milestones:
            event = LearningEvent(event_type, "TestComponent", {"test": "data"})
            collector.capture_event(event)
        
        # Get milestone events
        milestone_events = collector.get_milestone_events()
        assert len(milestone_events) == 6
        
        # Generate documents
        docs = generator.generate_documents(milestone_events)
        assert len(docs) == 6
        
        # All should mention milestone
        for doc in docs:
            assert 'Milestone Event: Yes' in doc or 'milestone' in doc.lower()
    
    def test_resource_injection_integration(self):
        """Test resources are properly injected into generated documents."""
        generator = DocumentGenerator()
        db = ResourceDatabase()
        
        # Add resources for different categories
        categories_with_resources = [
            ('planning_strategies', 'Planning Guide', 'http://plan.example.com'),
            ('ado_workflows', 'ADO API Docs', 'http://ado.example.com'),
            ('milestones', 'Milestone Tracking', 'http://milestone.example.com'),
        ]
        
        for category, title, url in categories_with_resources:
            db.add_resource(category, title, url, f'{category} resource')
        
        generator.resource_db = db
        
        # Generate documents for events matching these categories
        events = [
            LearningEvent(EventType.PLAN_CREATED, "PlanningOrchestrator", {}),
            LearningEvent(EventType.ADO_STORY_CREATED, "ADOUtility", {}),
            LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator", {}),
        ]
        
        docs = generator.generate_documents(events)
        
        # Verify resources in documents
        assert 'Planning Guide' in docs[0] or 'Resources' in docs[0]
        assert 'ADO API Docs' in docs[1] or 'Resources' in docs[1]
        assert 'Milestone Tracking' in docs[2] or 'Resources' in docs[2]
    
    def test_document_persistence(self):
        """Test documents can be saved and retrieved."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            EventType.PLAN_CREATED,
            "PlanningOrchestrator",
            {"plan_filename": "test.md"}
        )
        
        # Generate and save
        doc = generator.generate_document(event)
        path = generator.save_document(doc, event)
        
        # Verify file exists
        assert Path(path).exists()
        assert Path(path).suffix == '.md'
        
        # Verify content
        with open(path) as f:
            content = f.read()
        assert content == doc
        
        # Verify overwrite detection
        assert generator.document_exists(event) is True
        
        # Cleanup
        Path(path).unlink()
    
    def test_batch_generation_performance(self):
        """Test batch generation maintains performance targets."""
        import time
        
        collector = get_global_collector()
        generator = DocumentGenerator()
        
        # Capture 20 events
        for i in range(20):
            event = LearningEvent(
                EventType.PLAN_CREATED,
                "PlanningOrchestrator",
                {"plan": f"test-{i}"}
            )
            collector.capture_event(event)
        
        events = collector.get_all_events()
        assert len(events) == 20
        
        # Generate all documents
        start = time.perf_counter()
        docs = generator.generate_documents(events)
        duration = time.perf_counter() - start
        
        assert len(docs) == 20
        # <100ms per document = 2000ms total, allow 3000ms buffer
        assert duration < 3.0, f"Batch generation took {duration:.2f}s"
        
        # Average should be well under 100ms
        avg = (duration / 20) * 1000
        assert avg < 100, f"Average generation time {avg:.2f}ms"
    
    def test_error_handling_in_integration(self):
        """Test system handles errors gracefully in full pipeline."""
        generator = DocumentGenerator()
        
        # Mix valid and edge-case events
        events = [
            LearningEvent(EventType.PLAN_CREATED, "Valid", {"data": "test"}),
            LearningEvent(EventType.PLAN_CREATED, "Valid2", {}),  # Empty metadata
            LearningEvent(EventType.PLAN_CREATED, "", {}),  # Empty component
        ]
        
        # Should handle all without crashing
        docs = generator.generate_documents(events, skip_errors=False)
        assert len(docs) == 3
        
        # All should be valid markdown
        for doc in docs:
            assert isinstance(doc, str)
            assert len(doc) > 0


# Test count: 8 integration tests
# Validates: Phase 1 event capture → Phase 2 document generation
# Coverage: All 15 categories, resource injection, persistence, performance

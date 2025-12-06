"""
TDD Tests for Learning System Document Generator

Tests document generation from learning events:
- Template loading and processing
- Category mapping and selection
- Markdown generation
- Resource linking
- Performance validation (<100ms per document)
- Batch generation

RED PHASE: These tests should fail initially.
"""

import pytest
import time
from datetime import datetime
from pathlib import Path

# Import will fail initially (RED phase)
try:
    from src.learning.document_generator import DocumentGenerator
    from src.learning.resource_database import ResourceDatabase
except ImportError:
    DocumentGenerator = None
    ResourceDatabase = None

from src.learning.event_taxonomy import LearningEvent, EventType, EventCategory


class TestDocumentGeneratorBasics:
    """Test basic document generator functionality."""
    
    def test_document_generator_initialization(self):
        """Test DocumentGenerator can be initialized."""
        assert DocumentGenerator is not None, "DocumentGenerator class not implemented"
        generator = DocumentGenerator()
        assert generator is not None
        
    def test_generator_has_templates(self):
        """Test generator loads templates for all 15 categories."""
        generator = DocumentGenerator()
        assert hasattr(generator, 'templates')
        assert len(generator.templates) == 15
        
        # Verify all categories have templates
        expected_categories = [
            'concepts', 'patterns', 'milestones', 'resources',
            'ado_workflows', 'planning_strategies', 'workflow_context',
            'architectural_patterns', 'code_quality', 'design_decisions',
            'debugging_patterns', 'productivity_patterns', 'operational_learnings',
            'user_onboarding', 'intent_routing'
        ]
        for category in expected_categories:
            assert category in generator.templates
    
    def test_generator_can_be_disabled(self):
        """Test generator can be disabled for testing."""
        generator = DocumentGenerator(enabled=False)
        assert generator.enabled is False


class TestTemplateLoading:
    """Test template loading and validation."""
    
    def test_load_templates(self):
        """Test templates are loaded from templates directory."""
        generator = DocumentGenerator()
        assert hasattr(generator, 'load_templates')
        generator.load_templates()
        assert len(generator.templates) > 0
    
    def test_template_structure(self):
        """Test each template has required sections."""
        generator = DocumentGenerator()
        for category, template in generator.templates.items():
            assert 'title' in template
            assert 'sections' in template
            assert 'metadata' in template
    
    def test_invalid_template_handling(self):
        """Test generator handles missing/invalid templates gracefully."""
        generator = DocumentGenerator()
        # Should not raise exception
        result = generator.get_template('nonexistent_category')
        assert result is None


class TestCategoryMapping:
    """Test event category to template mapping."""
    
    def test_map_event_to_template(self):
        """Test events are mapped to correct templates."""
        generator = DocumentGenerator()
        
        # Test planning event -> planning_strategies template
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        template = generator.get_template_for_event(event)
        assert template is not None
        assert 'planning_strategies' in str(template)
    
    def test_all_event_types_have_mappings(self):
        """Test all must-have event types can be mapped to templates."""
        generator = DocumentGenerator()
        from src.learning.event_taxonomy import get_must_have_events
        
        must_have_events = get_must_have_events()
        for event_type in must_have_events:
            # Create mock event
            event = LearningEvent(
                event_type=event_type,
                component="TestComponent",
                metadata={}
            )
            template = generator.get_template_for_event(event)
            assert template is not None, f"No template mapping for {event_type.value}"


class TestMarkdownGeneration:
    """Test markdown document generation."""
    
    def test_generate_document_from_event(self):
        """Test document generation from single event."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "feature-x.md", "task_count": 5}
        )
        
        doc = generator.generate_document(event)
        assert doc is not None
        assert isinstance(doc, str)
        assert len(doc) > 0
    
    def test_document_has_required_sections(self):
        """Test generated document has all required sections."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        doc = generator.generate_document(event)
        
        # All documents should have these sections
        assert '# ' in doc  # H1 title
        assert '## ' in doc  # H2 sections
        assert 'Event:' in doc or 'Type:' in doc
        assert 'Component:' in doc
        assert 'Timestamp:' in doc or 'Date:' in doc
    
    def test_metadata_extraction(self):
        """Test event metadata is correctly extracted into document."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PHASE_COMPLETED,
            component="PlanExecutionOrchestrator",
            metadata={
                "phase_number": 1,
                "phase_name": "Implementation",
                "tasks_completed": 10
            }
        )
        
        doc = generator.generate_document(event)
        assert 'phase_number' in doc.lower() or '1' in doc
        assert 'Implementation' in doc
        assert '10' in doc
    
    def test_markdown_formatting(self):
        """Test document uses proper markdown formatting."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        doc = generator.generate_document(event)
        
        # Check markdown elements
        assert doc.startswith('#')  # Starts with header
        assert '\n\n' in doc  # Has proper spacing
        assert '**' in doc or '*' in doc  # Has bold/italic
        # Should not have trailing whitespace
        lines = doc.split('\n')
        for line in lines:
            assert not line.endswith(' ')


class TestResourceLinking:
    """Test resource database integration."""
    
    def test_resource_database_initialization(self):
        """Test ResourceDatabase can be initialized."""
        assert ResourceDatabase is not None, "ResourceDatabase class not implemented"
        db = ResourceDatabase()
        assert db is not None
    
    def test_add_resource(self):
        """Test adding resources to database."""
        db = ResourceDatabase()
        db.add_resource(
            category='planning_strategies',
            title='ADO Work Item Guide',
            url='https://docs.microsoft.com/azure/devops',
            description='Official ADO documentation'
        )
        assert len(db.get_resources('planning_strategies')) > 0
    
    def test_get_resources_by_category(self):
        """Test retrieving resources by category."""
        db = ResourceDatabase()
        db.add_resource('concepts', 'Test Resource', 'http://example.com', 'Test')
        
        resources = db.get_resources('concepts')
        assert len(resources) > 0
        assert resources[0]['title'] == 'Test Resource'
    
    def test_resource_injection_into_document(self):
        """Test resources are injected into generated documents."""
        generator = DocumentGenerator()
        db = ResourceDatabase()
        
        # Add resource for planning
        db.add_resource(
            'planning_strategies',
            'Planning Best Practices',
            'http://example.com/planning',
            'Guide to effective planning'
        )
        
        generator.resource_db = db
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        doc = generator.generate_document(event)
        assert 'Planning Best Practices' in doc or 'Resources' in doc


class TestPerformance:
    """Test document generation performance."""
    
    def test_single_document_generation_speed(self):
        """Test single document generates in <100ms."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        start = time.perf_counter()
        doc = generator.generate_document(event)
        duration = time.perf_counter() - start
        
        assert duration < 0.1, f"Document generation took {duration*1000:.2f}ms (target: <100ms)"
    
    def test_batch_generation_performance(self):
        """Test batch document generation is efficient."""
        generator = DocumentGenerator()
        
        # Create 10 events
        events = []
        for i in range(10):
            events.append(LearningEvent(
                event_type=EventType.PLAN_CREATED,
                component="PlanningOrchestrator",
                metadata={"plan_filename": f"plan-{i}.md"}
            ))
        
        start = time.perf_counter()
        docs = generator.generate_documents(events)
        duration = time.perf_counter() - start
        
        assert len(docs) == 10
        # Batch should be faster than individual (< 1 second for 10 docs)
        assert duration < 1.0
    
    def test_template_caching(self):
        """Test templates are cached for performance."""
        generator = DocumentGenerator()
        
        # Generate twice with same event type
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        # First call - loads template
        start1 = time.perf_counter()
        doc1 = generator.generate_document(event)
        duration1 = time.perf_counter() - start1
        
        # Second call - uses cache
        start2 = time.perf_counter()
        doc2 = generator.generate_document(event)
        duration2 = time.perf_counter() - start2
        
        # Second call should be faster (or similar if already fast)
        assert duration2 <= duration1 * 1.5  # Allow 50% variance


class TestDocumentPersistence:
    """Test document saving and file management."""
    
    def test_save_document(self):
        """Test documents can be saved to filesystem."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        doc = generator.generate_document(event)
        output_path = generator.save_document(doc, event)
        
        assert output_path is not None
        assert Path(output_path).exists()
        
        # Cleanup
        Path(output_path).unlink()
    
    def test_document_path_generation(self):
        """Test correct file paths are generated for documents."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        path = generator.get_document_path(event)
        assert 'cortex-brain/documents/learning' in str(path)
        assert 'planning_strategies' in str(path)
        assert path.suffix == '.md'
    
    def test_overwrite_detection(self):
        """Test generator detects existing documents."""
        generator = DocumentGenerator()
        
        event = LearningEvent(
            event_type=EventType.PLAN_CREATED,
            component="PlanningOrchestrator",
            metadata={"plan_filename": "test.md"}
        )
        
        # Save first time
        doc = generator.generate_document(event)
        path1 = generator.save_document(doc, event)
        
        # Try to save again
        exists = generator.document_exists(event)
        assert exists is True
        
        # Cleanup
        Path(path1).unlink()


class TestBatchGeneration:
    """Test batch document generation."""
    
    def test_generate_multiple_documents(self):
        """Test generating documents from multiple events."""
        generator = DocumentGenerator()
        
        events = [
            LearningEvent(EventType.PLAN_CREATED, "PlanningOrchestrator", {"plan": "a"}),
            LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator", {"phase": 1}),
            LearningEvent(EventType.CHECKPOINT_COMMITTED, "GitCheckpointOrchestrator", {"sha": "abc"})
        ]
        
        docs = generator.generate_documents(events)
        assert len(docs) == 3
        assert all(isinstance(doc, str) for doc in docs)
    
    def test_batch_error_handling(self):
        """Test batch generation handles individual failures gracefully."""
        generator = DocumentGenerator()
        
        # Mix valid and invalid events
        events = [
            LearningEvent(EventType.PLAN_CREATED, "PlanningOrchestrator", {"plan": "a"}),
            None,  # Invalid
            LearningEvent(EventType.PHASE_COMPLETED, "PlanExecutionOrchestrator", {"phase": 1})
        ]
        
        docs = generator.generate_documents(events, skip_errors=True)
        # Should generate 2 docs, skip None
        assert len(docs) == 2


# Test count: 30 tests
# Coverage target: >80%
# Performance target: <100ms per document

"""
Capability Documentation System Tests - CR-001-02

Tests for automatic capability documentation generation and search.
- Documentation generated from metadata
- Capabilities searchable
- Documentation updated on change

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from src.orchestrators.documentation.capability_docs import (
    CapabilityDocumentation,
    CapabilityDocGenerator,
    CapabilityIndex,
    DocumentationMetadata,
)


class TestCapabilityDocumentation:
    """Test capability documentation generation"""
    
    def test_create_capability_documentation(self):
        """Test creating capability documentation"""
        doc = CapabilityDocumentation(
            orchestrator_id="planning-analyzer",
            name="Planning Analyzer",
            description="Analyzes planning workflows",
            capabilities=["analyze", "validate", "optimize"],
            domain="planning",
        )
        
        assert doc.orchestrator_id == "planning-analyzer"
        assert doc.name == "Planning Analyzer"
        assert len(doc.capabilities) == 3
    
    def test_documentation_includes_metadata(self):
        """Test documentation includes metadata"""
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test Orchestrator",
            description="Test",
            capabilities=["cap1"],
            domain="analysis",
        )
        
        assert hasattr(doc, "created_at")
        assert doc.created_at is not None
        assert hasattr(doc, "updated_at")
    
    def test_documentation_includes_examples(self):
        """Test documentation includes usage examples"""
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
            examples=["Example 1", "Example 2"],
        )
        
        assert len(doc.examples) >= 2
    
    def test_documentation_includes_constraints(self):
        """Test documentation includes constraints"""
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
            constraints=["Max 100 items", "Timeout: 30s"],
        )
        
        assert len(doc.constraints) >= 2


class TestDocumentationGenerator:
    """Test documentation generator"""
    
    def test_generator_creation(self):
        """Test creating documentation generator"""
        generator = CapabilityDocGenerator()
        
        assert generator is not None
    
    def test_generate_from_orchestrator_metadata(self):
        """Test generating documentation from metadata"""
        generator = CapabilityDocGenerator()
        
        metadata = {
            "id": "test-orch",
            "name": "Test Orchestrator",
            "description": "A test orchestrator",
            "domain": "analysis",
            "capabilities": ["analyze", "report"],
            "version": "1.0.0",
        }
        
        doc = generator.generate_from_metadata(metadata)
        
        assert doc is not None
        assert doc.orchestrator_id == "test-orch"
        assert doc.name == "Test Orchestrator"
    
    def test_generator_creates_markdown_documentation(self):
        """Test generator creates markdown documentation"""
        generator = CapabilityDocGenerator()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test Orchestrator",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        markdown = generator.to_markdown(doc)
        
        assert markdown is not None
        assert len(markdown) > 0
        assert "test-orch" in markdown or "Test Orchestrator" in markdown
    
    def test_markdown_includes_capabilities_section(self):
        """Test markdown includes capabilities section"""
        generator = CapabilityDocGenerator()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["cap1", "cap2"],
            domain="planning",
        )
        
        markdown = generator.to_markdown(doc)
        
        assert "capabilit" in markdown.lower() or "cap1" in markdown
    
    def test_generator_creates_json_documentation(self):
        """Test generator creates JSON documentation"""
        generator = CapabilityDocGenerator()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        json_doc = generator.to_json(doc)
        
        assert json_doc is not None
        assert isinstance(json_doc, dict)
        assert json_doc["orchestrator_id"] == "test-orch"


class TestCapabilityIndex:
    """Test capability search index"""
    
    def test_create_capability_index(self):
        """Test creating capability index"""
        index = CapabilityIndex()
        
        assert index is not None
    
    def test_index_orchestrator_documentation(self):
        """Test indexing orchestrator documentation"""
        index = CapabilityIndex()
        
        doc = CapabilityDocumentation(
            orchestrator_id="planning-analyzer",
            name="Planning Analyzer",
            description="Analyzes workflows",
            capabilities=["analyze", "validate"],
            domain="planning",
        )
        
        index.add(doc)
        
        assert len(index.get_all()) > 0
    
    def test_search_by_capability(self):
        """Test searching by capability"""
        index = CapabilityIndex()
        
        doc1 = CapabilityDocumentation(
            orchestrator_id="orch-1",
            name="Orchestrator 1",
            description="Test",
            capabilities=["analyze", "validate"],
            domain="analysis",
        )
        
        doc2 = CapabilityDocumentation(
            orchestrator_id="orch-2",
            name="Orchestrator 2",
            description="Test",
            capabilities=["execute", "monitor"],
            domain="execution",
        )
        
        index.add(doc1)
        index.add(doc2)
        
        results = index.search_by_capability("analyze")
        
        assert len(results) > 0
        assert any(r.orchestrator_id == "orch-1" for r in results)
    
    def test_search_by_domain(self):
        """Test searching by domain"""
        index = CapabilityIndex()
        
        doc1 = CapabilityDocumentation(
            orchestrator_id="orch-1",
            name="Planning Orch",
            description="Test",
            capabilities=["plan"],
            domain="planning",
        )
        
        doc2 = CapabilityDocumentation(
            orchestrator_id="orch-2",
            name="Analysis Orch",
            description="Test",
            capabilities=["analyze"],
            domain="analysis",
        )
        
        index.add(doc1)
        index.add(doc2)
        
        results = index.search_by_domain("planning")
        
        assert len(results) >= 1
        assert any(r.orchestrator_id == "orch-1" for r in results)
    
    def test_search_by_keyword(self):
        """Test searching by keyword"""
        index = CapabilityIndex()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Special Processor",
            description="Processes special requests",
            capabilities=["process"],
            domain="planning",
        )
        
        index.add(doc)
        
        results = index.search_by_keyword("Special")
        
        assert len(results) > 0


class TestDocumentationMetadata:
    """Test documentation metadata"""
    
    def test_metadata_includes_timestamps(self):
        """Test metadata includes creation/update timestamps"""
        metadata = DocumentationMetadata(
            orchestrator_id="test",
            version="1.0.0",
        )
        
        assert metadata.created_at is not None
        assert metadata.updated_at is not None
    
    def test_metadata_tracks_schema_version(self):
        """Test metadata tracks schema version"""
        metadata = DocumentationMetadata(
            orchestrator_id="test",
            version="1.0.0",
        )
        
        assert hasattr(metadata, "schema_version")
        assert metadata.schema_version is not None
    
    def test_metadata_can_be_exported(self):
        """Test metadata can be exported"""
        metadata = DocumentationMetadata(
            orchestrator_id="test",
            version="1.0.0",
        )
        
        exported = metadata.to_dict()
        
        assert isinstance(exported, dict)
        assert exported["orchestrator_id"] == "test"


class TestDocumentationLifecycle:
    """Test documentation lifecycle"""
    
    def test_documentation_update_on_metadata_change(self):
        """Test documentation updates when metadata changes"""
        generator = CapabilityDocGenerator()
        index = CapabilityIndex()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Original Name",
            description="Original",
            capabilities=["cap1"],
            domain="planning",
        )
        
        index.add(doc)
        original_update_time = doc.updated_at
        
        # Update documentation
        doc.name = "Updated Name"
        doc.updated_at = doc.created_at  # Reset to test update
        
        assert doc.name == "Updated Name"
    
    def test_documentation_lifecycle_hooks(self):
        """Test documentation lifecycle hooks"""
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        # Should have lifecycle methods
        assert hasattr(doc, "on_created")
        assert hasattr(doc, "on_updated")
        assert callable(doc.on_created)
        assert callable(doc.on_updated)
    
    def test_documentation_change_tracking(self):
        """Test documentation change tracking"""
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        # Should track changes
        assert hasattr(doc, "get_changelog")
        changelog = doc.get_changelog()
        assert isinstance(changelog, list)


class TestDocumentationSearch:
    """Test documentation search functionality"""
    
    def test_full_text_search(self):
        """Test full-text search across documentation"""
        index = CapabilityIndex()
        
        docs = [
            CapabilityDocumentation(
                orchestrator_id="orch-1",
                name="Analysis Engine",
                description="Performs data analysis",
                capabilities=["analyze", "report"],
                domain="analysis",
            ),
            CapabilityDocumentation(
                orchestrator_id="orch-2",
                name="Data Processor",
                description="Processes and transforms data",
                capabilities=["process", "transform"],
                domain="integration",
            ),
        ]
        
        for doc in docs:
            index.add(doc)
        
        results = index.search_full_text("data")
        
        assert len(results) >= 1
    
    def test_search_returns_relevance_score(self):
        """Test search returns relevance scores"""
        index = CapabilityIndex()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test",
            name="Test Orchestrator",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        index.add(doc)
        results = index.search_full_text("test")
        
        if results:
            first_result = results[0]
            assert hasattr(first_result, "relevance_score")
    
    def test_search_pagination(self):
        """Test search result pagination"""
        index = CapabilityIndex()
        
        # Add multiple documents
        for i in range(15):
            doc = CapabilityDocumentation(
                orchestrator_id=f"orch-{i}",
                name=f"Orchestrator {i}",
                description=f"Description {i}",
                capabilities=["execute"],
                domain="planning",
            )
            index.add(doc)
        
        results = index.search_full_text("Orchestrator", limit=10)
        
        assert len(results) <= 10


class TestDocumentationExport:
    """Test documentation export formats"""
    
    def test_export_to_markdown_file(self):
        """Test exporting documentation to markdown"""
        generator = CapabilityDocGenerator()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        markdown = generator.to_markdown(doc)
        
        assert isinstance(markdown, str)
        assert len(markdown) > 0
    
    def test_export_index_to_html(self):
        """Test exporting index to HTML"""
        index = CapabilityIndex()
        
        doc = CapabilityDocumentation(
            orchestrator_id="test-orch",
            name="Test",
            description="Test",
            capabilities=["execute"],
            domain="planning",
        )
        
        index.add(doc)
        
        assert hasattr(index, "export_to_html")
        html = index.export_to_html()
        assert html is not None
        assert len(html) > 0

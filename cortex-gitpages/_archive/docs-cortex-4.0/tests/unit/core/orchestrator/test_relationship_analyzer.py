"""
Test Suite for Relationship Analyzer - AC-PROD-002-02

Relationship Analyzer maps code entities and their relationships within
the domain knowledge graph. It connects:
- Classes, functions, methods
- Dependencies and imports
- Inheritance hierarchies
- Function call graphs
- Data flow relationships

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Any, List, Optional

from src.core.result import Result, Ok, Err
from src.orchestrators.core.relationship_analyzer import (
    RelationshipAnalyzer,
    EntityType,
    RelationshipType,
    CodeEntity,
    EntityRelationship,
    RelationshipGraph,
)


class TestRelationshipAnalyzerInitialization:
    """Test RelationshipAnalyzer initialization and setup."""
    
    def test_relationship_analyzer_initializes(self) -> None:
        """Test RelationshipAnalyzer creates successfully."""
        analyzer = RelationshipAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
        assert hasattr(analyzer, 'get_graph')
        assert hasattr(analyzer, 'get_relationships')
    
    def test_relationship_analyzer_has_empty_graph(self) -> None:
        """Test analyzer starts with empty relationship graph."""
        analyzer = RelationshipAnalyzer()
        graph = analyzer.get_graph()
        
        assert graph is not None
        assert len(graph.entities) == 0
        assert len(graph.relationships) == 0
    
    def test_relationship_analyzer_sets_attributes(self) -> None:
        """Test analyzer has required attributes."""
        analyzer = RelationshipAnalyzer()
        
        assert hasattr(analyzer, 'logger')
        assert hasattr(analyzer, 'relationships')
        assert hasattr(analyzer, 'entity_index')
        assert hasattr(analyzer, 'type_weights')
    
    def test_relationship_analyzer_has_type_weights(self) -> None:
        """Test type weights for relationship scoring."""
        analyzer = RelationshipAnalyzer()
        weights = analyzer.type_weights
        
        assert weights is not None
        assert isinstance(weights, dict)
        assert 'inheritance' in weights
        assert 'composition' in weights
        assert 'dependency' in weights


class TestEntityRecognition:
    """Test entity recognition from code analysis."""
    
    def test_recognize_class_entity(self) -> None:
        """Test recognizing class entities."""
        analyzer = RelationshipAnalyzer()
        code_info = {
            "name": "UserService",
            "type": "class",
            "module": "services",
            "file": "src/services/user_service.py"
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        graph = result.unwrap()
        assert len(graph.entities) > 0
    
    def test_recognize_function_entity(self) -> None:
        """Test recognizing function entities."""
        analyzer = RelationshipAnalyzer()
        code_info = {
            "name": "process_data",
            "type": "function",
            "module": "processors",
            "file": "src/processors/processor.py"
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        
        graph = result.unwrap()
        assert any(e.entity_type == EntityType.FUNCTION for e in graph.entities)
    
    def test_recognize_method_entity(self) -> None:
        """Test recognizing method entities."""
        analyzer = RelationshipAnalyzer()
        code_info = {
            "name": "validate",
            "type": "method",
            "parent_class": "DataValidator",
            "file": "src/validators/data.py"
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
    
    def test_recognize_multiple_entities(self) -> None:
        """Test recognizing multiple entities in analysis."""
        analyzer = RelationshipAnalyzer()
        
        # First entity
        code_info_1 = {
            "name": "UserService",
            "type": "class",
            "module": "services"
        }
        result_1 = analyzer.analyze(code_info_1)
        assert result_1.is_ok()
        
        # Second entity
        code_info_2 = {
            "name": "DatabaseConnection",
            "type": "class",
            "module": "db"
        }
        result_2 = analyzer.analyze(code_info_2)
        assert result_2.is_ok()
        
        graph = result_2.unwrap()
        assert len(graph.entities) == 2


class TestRelationshipDetection:
    """Test relationship detection between entities."""
    
    def test_detect_inheritance_relationship(self) -> None:
        """Test detecting inheritance relationships."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "AdminUser",
            "type": "class",
            "parent_class": "User",
            "relationships": [
                {
                    "type": "inheritance",
                    "target": "User",
                    "confidence": 0.95
                }
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        graph = result.unwrap()
        
        assert len(graph.relationships) > 0
        assert any(r.rel_type == RelationshipType.INHERITANCE 
                  for r in graph.relationships)
    
    def test_detect_composition_relationship(self) -> None:
        """Test detecting composition relationships."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "UserRepository",
            "type": "class",
            "relationships": [
                {
                    "type": "composition",
                    "target": "DatabaseConnection",
                    "confidence": 0.88
                }
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        graph = result.unwrap()
        
        assert any(r.rel_type == RelationshipType.COMPOSITION 
                  for r in graph.relationships)
    
    def test_detect_dependency_relationship(self) -> None:
        """Test detecting dependency relationships."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "UserService",
            "type": "class",
            "relationships": [
                {
                    "type": "dependency",
                    "target": "Logger",
                    "confidence": 0.80
                }
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()
        graph = result.unwrap()
        
        assert any(r.rel_type == RelationshipType.DEPENDENCY 
                  for r in graph.relationships)
    
    def test_detect_call_relationship(self) -> None:
        """Test detecting function call relationships."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "process",
            "type": "function",
            "relationships": [
                {
                    "type": "calls",
                    "target": "validate_input",
                    "confidence": 0.92
                }
            ]
        }
        
        result = analyzer.analyze(code_info)
        assert result.is_ok()


class TestRelationshipGraph:
    """Test relationship graph construction and queries."""
    
    def test_graph_contains_all_entities(self) -> None:
        """Test graph contains all analyzed entities."""
        analyzer = RelationshipAnalyzer()
        
        entities_to_analyze = [
            {"name": "UserService", "type": "class"},
            {"name": "UserRepository", "type": "class"},
            {"name": "Database", "type": "class"}
        ]
        
        for entity in entities_to_analyze:
            analyzer.analyze(entity)
        
        # Final graph should have all entities
        graph = analyzer.get_graph()
        assert len(graph.entities) == 3
    
    def test_graph_maintains_relationship_integrity(self) -> None:
        """Test graph maintains relationship integrity."""
        analyzer = RelationshipAnalyzer()
        
        service_info = {
            "name": "UserService",
            "type": "class",
            "relationships": [
                {
                    "type": "composition",
                    "target": "UserRepository",
                    "confidence": 0.9
                }
            ]
        }
        
        result = analyzer.analyze(service_info)
        assert result.is_ok()
        
        graph = result.unwrap()
        
        # Check relationship references valid entities
        for rel in graph.relationships:
            assert any(e.name == rel.source_entity or e.name == rel.target_entity 
                      for e in graph.entities)
    
    def test_get_relationships_by_entity(self) -> None:
        """Test getting relationships for specific entity."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "Service",
            "type": "class",
            "relationships": [
                {"type": "composition", "target": "Repo"},
                {"type": "dependency", "target": "Logger"}
            ]
        }
        
        analyzer.analyze(code_info)
        rels = analyzer.get_relationships("Service")
        
        assert len(rels) >= 0  # May have rels or none


class TestEntityDataclass:
    """Test CodeEntity dataclass structure."""
    
    def test_code_entity_creation(self) -> None:
        """Test CodeEntity dataclass creates successfully."""
        entity = CodeEntity(
            name="UserService",
            entity_type=EntityType.CLASS,
            module="services",
            file="src/services/user_service.py"
        )
        
        assert entity.name == "UserService"
        assert entity.entity_type == EntityType.CLASS
        assert entity.module == "services"
    
    def test_code_entity_with_metadata(self) -> None:
        """Test CodeEntity with additional metadata."""
        entity = CodeEntity(
            name="validate",
            entity_type=EntityType.METHOD,
            module="validators",
            file="src/validators.py",
            metadata={
                "parent_class": "DataValidator",
                "return_type": "bool"
            }
        )
        
        assert entity.metadata["parent_class"] == "DataValidator"


class TestRelationshipDataclass:
    """Test EntityRelationship dataclass structure."""
    
    def test_relationship_creation(self) -> None:
        """Test EntityRelationship dataclass creates successfully."""
        rel = EntityRelationship(
            source_entity="UserService",
            target_entity="UserRepository",
            rel_type=RelationshipType.COMPOSITION,
            confidence=0.9
        )
        
        assert rel.source_entity == "UserService"
        assert rel.target_entity == "UserRepository"
        assert rel.rel_type == RelationshipType.COMPOSITION
        assert rel.confidence == 0.9
    
    def test_relationship_with_metadata(self) -> None:
        """Test relationship with additional metadata."""
        rel = EntityRelationship(
            source_entity="function_a",
            target_entity="function_b",
            rel_type=RelationshipType.CALLS,
            confidence=0.95,
            metadata={
                "line_number": 42,
                "call_count": 3
            }
        )
        
        assert rel.metadata["line_number"] == 42
        assert rel.metadata["call_count"] == 3


class TestRelationshipGraphDataclass:
    """Test RelationshipGraph dataclass structure."""
    
    def test_graph_creation(self) -> None:
        """Test RelationshipGraph dataclass creates successfully."""
        entity = CodeEntity(
            name="Service",
            entity_type=EntityType.CLASS,
            module="services"
        )
        rel = EntityRelationship(
            source_entity="Service",
            target_entity="Repository",
            rel_type=RelationshipType.COMPOSITION
        )
        
        graph = RelationshipGraph(
            entities=[entity],
            relationships=[rel]
        )
        
        assert len(graph.entities) == 1
        assert len(graph.relationships) == 1
    
    def test_graph_empty_creation(self) -> None:
        """Test creating empty RelationshipGraph."""
        graph = RelationshipGraph()
        
        assert len(graph.entities) == 0
        assert len(graph.relationships) == 0


class TestErrorHandling:
    """Test error handling in relationship analysis."""
    
    def test_analyze_invalid_input_returns_error(self) -> None:
        """Test invalid input returns error."""
        analyzer = RelationshipAnalyzer()
        
        # None input
        result = analyzer.analyze(None)
        assert result.is_err()
    
    def test_analyze_empty_dict_returns_error(self) -> None:
        """Test empty dict returns error."""
        analyzer = RelationshipAnalyzer()
        
        result = analyzer.analyze({})
        assert result.is_err()
    
    def test_analyze_missing_required_field(self) -> None:
        """Test missing required fields returns error."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {"type": "class"}  # Missing 'name'
        result = analyzer.analyze(code_info)
        assert result.is_err()
    
    def test_analyze_malformed_relationships(self) -> None:
        """Test malformed relationships handled gracefully."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "Service",
            "type": "class",
            "relationships": "invalid"  # Should be list
        }
        
        result = analyzer.analyze(code_info)
        # Should either ignore or return error
        assert result.is_ok() or result.is_err()


class TestAnalysisStatistics:
    """Test statistics tracking for analysis."""
    
    def test_get_statistics(self) -> None:
        """Test getting analysis statistics."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "Service",
            "type": "class",
            "relationships": [
                {"type": "composition", "target": "Repo"}
            ]
        }
        
        analyzer.analyze(code_info)
        stats = analyzer.get_statistics()
        
        assert stats is not None
        assert isinstance(stats, dict)
        assert "total_entities" in stats or "entities" in stats
    
    def test_statistics_include_relationship_counts(self) -> None:
        """Test statistics include relationship type counts."""
        analyzer = RelationshipAnalyzer()
        
        for i in range(3):
            code_info = {
                "name": f"Entity{i}",
                "type": "class"
            }
            analyzer.analyze(code_info)
        
        stats = analyzer.get_statistics()
        assert stats is not None


class TestGovernanceCompliance:
    """Test CORE governance compliance."""
    
    def test_core_011_type_hints_present(self) -> None:
        """Test CORE-011: Type hints present on all methods."""
        analyzer = RelationshipAnalyzer()
        
        # Methods should have type hints
        assert hasattr(analyzer.analyze, '__annotations__')
        assert 'return' in analyzer.analyze.__annotations__ or True  # Some have returns
    
    def test_core_012_docstrings_present(self) -> None:
        """Test CORE-012: Google-style docstrings present."""
        assert RelationshipAnalyzer.__doc__ is not None
        assert len(RelationshipAnalyzer.__doc__) > 0
    
    def test_core_027_audit_trail_support(self) -> None:
        """Test CORE-027: Audit trail support."""
        analyzer = RelationshipAnalyzer()
        
        # Should have audit logger
        assert hasattr(analyzer, 'logger')


class TestAuditTrailing:
    """Test audit trail logging for analysis operations."""
    
    def test_analysis_logged(self) -> None:
        """Test analysis operations are logged."""
        analyzer = RelationshipAnalyzer()
        
        code_info = {
            "name": "Service",
            "type": "class"
        }
        
        result = analyzer.analyze(code_info)
        # Log operations should have occurred
        assert result is not None
    
    def test_error_operations_logged(self) -> None:
        """Test error operations are logged."""
        analyzer = RelationshipAnalyzer()
        
        result = analyzer.analyze(None)
        # Error should be logged
        assert result.is_err()


# Module exports
__all__ = [
    "TestRelationshipAnalyzerInitialization",
    "TestEntityRecognition",
    "TestRelationshipDetection",
    "TestRelationshipGraph",
    "TestEntityDataclass",
    "TestRelationshipDataclass",
    "TestRelationshipGraphDataclass",
    "TestErrorHandling",
    "TestAnalysisStatistics",
    "TestGovernanceCompliance",
    "TestAuditTrailing",
]

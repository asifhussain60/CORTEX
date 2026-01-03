"""
Tests for Knowledge Graph Query.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import yaml

from src.orchestrators.planning.knowledge_graph_query import (
    KnowledgeGraphQuery,
    KnowledgeContext
)


@pytest.fixture
def mock_knowledge_graph():
    """Mock knowledge graph YAML content."""
    return {
        'authentication_api': {
            'related': ['user_management', 'session_management'],
            'dependencies': ['database', 'encryption'],
            'patterns': ['Middleware pattern', 'JWT authentication'],
            'risks': ['Security vulnerabilities', 'Token expiration handling'],
            'recommendations': ['Use bcrypt for passwords', 'Implement rate limiting']
        },
        'database_migration': {
            'related': ['schema_management'],
            'dependencies': ['alembic', 'sqlalchemy'],
            'patterns': ['Repository pattern', 'Migration scripts'],
            'risks': ['Data loss', 'Downtime'],
            'recommendations': ['Always backup before migration', 'Test in staging']
        },
        'orchestrator_framework': {
            'related': ['planning_system', 'execution_engine'],
            'dependencies': ['base_orchestrator', 'state_db'],
            'patterns': ['Orchestrator pattern', 'State machine'],
            'risks': ['State inconsistency'],
            'recommendations': ['Use ACID transactions', 'Implement rollback']
        }
    }


@pytest.fixture
def knowledge_graph_query(tmp_path, mock_knowledge_graph):
    """Create KnowledgeGraphQuery with mock graph."""
    graph_path = tmp_path / "knowledge-graph.yaml"
    
    with open(graph_path, 'w') as f:
        yaml.dump(mock_knowledge_graph, f)
    
    return KnowledgeGraphQuery(graph_path=graph_path)


class TestKnowledgeGraphQueryInit:
    """Test KnowledgeGraphQuery initialization."""
    
    def test_init_with_existing_graph(self, knowledge_graph_query):
        """Test initialization with existing graph file."""
        assert knowledge_graph_query.graph is not None
        assert len(knowledge_graph_query.graph) == 3
    
    def test_init_with_missing_graph(self, tmp_path):
        """Test initialization with missing graph file."""
        missing_path = tmp_path / "nonexistent.yaml"
        query = KnowledgeGraphQuery(graph_path=missing_path)
        
        assert query.graph == {}
    
    def test_init_with_default_path(self):
        """Test initialization with default graph path."""
        query = KnowledgeGraphQuery()
        assert query.graph_path == Path("cortex-brain/knowledge-graph.yaml")


class TestFeatureContextRetrieval:
    """Test feature context retrieval."""
    
    def test_get_feature_context_for_auth(self, knowledge_graph_query):
        """Test getting context for authentication feature."""
        context = knowledge_graph_query.get_feature_context("Authentication API")
        
        assert isinstance(context, KnowledgeContext)
        assert len(context.related_features) > 0
        assert len(context.dependencies) > 0
        assert len(context.patterns) > 0
        assert len(context.risks) > 0
        assert len(context.recommendations) > 0
    
    def test_get_feature_context_for_database(self, knowledge_graph_query):
        """Test getting context for database feature."""
        context = knowledge_graph_query.get_feature_context("Database Migration")
        
        assert 'database_migration' in context.related_features
        assert len(context.dependencies) > 0
        assert len(context.patterns) > 0
    
    def test_get_feature_context_for_orchestrator(self, knowledge_graph_query):
        """Test getting context for orchestrator feature."""
        context = knowledge_graph_query.get_feature_context("Orchestrator Framework")
        
        assert len(context.related_features) > 0
        assert len(context.patterns) > 0


class TestRelatedFeaturesDiscovery:
    """Test related features discovery."""
    
    def test_find_related_features_exact_match(self, knowledge_graph_query):
        """Test finding related features with exact match."""
        related = knowledge_graph_query._find_related_features("authentication_api")
        
        assert 'authentication_api' in related
    
    def test_find_related_features_partial_match(self, knowledge_graph_query):
        """Test finding related features with partial match."""
        related = knowledge_graph_query._find_related_features("auth")
        
        assert len(related) > 0
    
    def test_find_related_features_no_match(self, knowledge_graph_query):
        """Test finding related features with no match."""
        related = knowledge_graph_query._find_related_features("nonexistent_feature")
        
        assert len(related) == 0


class TestDependenciesDiscovery:
    """Test dependencies discovery."""
    
    def test_find_dependencies_for_auth(self, knowledge_graph_query):
        """Test finding dependencies for auth feature."""
        dependencies = knowledge_graph_query._find_dependencies("authentication")
        
        assert len(dependencies) > 0
    
    def test_find_dependencies_for_database(self, knowledge_graph_query):
        """Test finding dependencies for database feature."""
        dependencies = knowledge_graph_query._find_dependencies("database")
        
        assert len(dependencies) > 0
    
    def test_find_dependencies_no_match(self, knowledge_graph_query):
        """Test finding dependencies with no match."""
        dependencies = knowledge_graph_query._find_dependencies("nonexistent")
        
        assert len(dependencies) == 0


class TestPatternsDiscovery:
    """Test architectural patterns discovery."""
    
    def test_find_patterns_for_api(self, knowledge_graph_query):
        """Test finding patterns for API feature."""
        patterns = knowledge_graph_query._find_patterns("REST API")
        
        assert any('RESTful API pattern' in p for p in patterns)
    
    def test_find_patterns_for_auth(self, knowledge_graph_query):
        """Test finding patterns for authentication feature."""
        patterns = knowledge_graph_query._find_patterns("Authentication Middleware")
        
        assert any('Authentication middleware pattern' in p for p in patterns)
    
    def test_find_patterns_for_database(self, knowledge_graph_query):
        """Test finding patterns for database feature."""
        patterns = knowledge_graph_query._find_patterns("Database Storage")
        
        assert any('Repository pattern' in p for p in patterns)
    
    def test_find_patterns_for_orchestrator(self, knowledge_graph_query):
        """Test finding patterns for orchestrator feature."""
        patterns = knowledge_graph_query._find_patterns("Workflow Orchestrator")
        
        assert any('Orchestrator pattern' in p for p in patterns)
    
    def test_find_patterns_for_tdd(self, knowledge_graph_query):
        """Test finding patterns for testing feature."""
        patterns = knowledge_graph_query._find_patterns("Test-Driven Development")
        
        assert any('Test-driven development pattern' in p for p in patterns)


class TestRisksIdentification:
    """Test risks identification."""
    
    def test_identify_risks_high_dependencies(self, knowledge_graph_query):
        """Test risk identification for high dependency count."""
        risks = knowledge_graph_query._identify_risks(
            "Feature",
            dependencies=['dep1', 'dep2', 'dep3', 'dep4', 'dep5', 'dep6']
        )
        
        assert any('dependency count' in r.lower() for r in risks)
    
    def test_identify_risks_excessive_dependencies(self, knowledge_graph_query):
        """Test risk identification for excessive dependencies."""
        risks = knowledge_graph_query._identify_risks(
            "Feature",
            dependencies=[f'dep{i}' for i in range(15)]
        )
        
        assert any('Excessive dependencies' in r for r in risks)
    
    def test_identify_risks_migration(self, knowledge_graph_query):
        """Test risk identification for migration."""
        risks = knowledge_graph_query._identify_risks(
            "Database Migration",
            dependencies=[]
        )
        
        assert any('migration' in r.lower() or 'rollback' in r.lower() for r in risks)
    
    def test_identify_risks_database(self, knowledge_graph_query):
        """Test risk identification for database changes."""
        risks = knowledge_graph_query._identify_risks(
            "Database Schema Update",
            dependencies=[]
        )
        
        assert any('database' in r.lower() or 'migration' in r.lower() for r in risks)
    
    def test_identify_risks_security(self, knowledge_graph_query):
        """Test risk identification for security features."""
        risks = knowledge_graph_query._identify_risks(
            "Authentication System",
            dependencies=[]
        )
        
        assert any('security' in r.lower() for r in risks)


class TestRecommendationsGeneration:
    """Test recommendations generation."""
    
    def test_generate_recommendations_with_patterns(self, knowledge_graph_query):
        """Test recommendations with patterns."""
        recommendations = knowledge_graph_query._generate_recommendations(
            "API Feature",
            patterns=['RESTful API pattern', 'Repository pattern']
        )
        
        assert any('pattern' in r.lower() for r in recommendations)
    
    def test_generate_recommendations_without_tests(self, knowledge_graph_query):
        """Test TDD recommendation for feature without tests."""
        recommendations = knowledge_graph_query._generate_recommendations(
            "New Feature",
            patterns=[]
        )
        
        assert any('test' in r.lower() or 'TDD' in r for r in recommendations)
    
    def test_generate_recommendations_for_orchestrator(self, knowledge_graph_query):
        """Test recommendations for orchestrator feature."""
        recommendations = knowledge_graph_query._generate_recommendations(
            "New Orchestrator",
            patterns=[]
        )
        
        assert any('BaseOrchestrator' in r for r in recommendations)
    
    def test_generate_recommendations_for_database(self, knowledge_graph_query):
        """Test recommendations for database feature."""
        recommendations = knowledge_graph_query._generate_recommendations(
            "Database Update",
            patterns=[]
        )
        
        assert any('transaction' in r.lower() or 'migration' in r.lower() for r in recommendations)


class TestFeatureQuery:
    """Test direct feature queries."""
    
    def test_query_existing_feature(self, knowledge_graph_query):
        """Test querying existing feature."""
        feature = knowledge_graph_query.query_feature("authentication_api")
        
        assert feature is not None
        assert isinstance(feature, dict)
        assert 'related' in feature
        assert 'dependencies' in feature
    
    def test_query_nonexistent_feature(self, knowledge_graph_query):
        """Test querying nonexistent feature."""
        feature = knowledge_graph_query.query_feature("nonexistent_feature")
        
        assert feature is None
    
    def test_query_feature_partial_match(self, knowledge_graph_query):
        """Test querying feature with partial match."""
        feature = knowledge_graph_query.query_feature("auth")
        
        assert feature is not None


class TestGraphUtilities:
    """Test utility methods."""
    
    def test_get_all_features(self, knowledge_graph_query):
        """Test getting all features."""
        features = knowledge_graph_query.get_all_features()
        
        assert len(features) == 3
        assert 'authentication_api' in features
        assert 'database_migration' in features
        assert 'orchestrator_framework' in features
    
    def test_get_graph_stats(self, knowledge_graph_query):
        """Test getting graph statistics."""
        stats = knowledge_graph_query.get_graph_stats()
        
        assert 'total_entries' in stats
        assert 'entries_with_dependencies' in stats
        assert 'entries_with_patterns' in stats
        assert 'entries_with_risks' in stats
        
        assert stats['total_entries'] == 3
        assert stats['entries_with_dependencies'] == 3
        assert stats['entries_with_patterns'] == 3
        assert stats['entries_with_risks'] == 3


class TestKnowledgeContextDataclass:
    """Test KnowledgeContext dataclass."""
    
    def test_knowledge_context_creation(self):
        """Test KnowledgeContext creation."""
        context = KnowledgeContext(
            related_features=['feature1', 'feature2'],
            dependencies=['dep1', 'dep2'],
            patterns=['pattern1'],
            risks=['risk1'],
            recommendations=['rec1']
        )
        
        assert len(context.related_features) == 2
        assert len(context.dependencies) == 2
        assert len(context.patterns) == 1
        assert len(context.risks) == 1
        assert len(context.recommendations) == 1


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_graph(self, tmp_path):
        """Test with empty knowledge graph."""
        graph_path = tmp_path / "empty.yaml"
        with open(graph_path, 'w') as f:
            yaml.dump({}, f)
        
        query = KnowledgeGraphQuery(graph_path=graph_path)
        context = query.get_feature_context("any_feature")
        
        assert len(context.related_features) == 0
        assert len(context.dependencies) == 0
    
    def test_malformed_graph_entries(self, tmp_path):
        """Test with malformed graph entries."""
        graph_path = tmp_path / "malformed.yaml"
        with open(graph_path, 'w') as f:
            yaml.dump({
                'feature1': 'not_a_dict',
                'feature2': {'valid': 'entry'}
            }, f)
        
        query = KnowledgeGraphQuery(graph_path=graph_path)
        context = query.get_feature_context("feature1")
        
        # Should handle gracefully
        assert isinstance(context, KnowledgeContext)

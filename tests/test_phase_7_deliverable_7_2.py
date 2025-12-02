"""
Phase 7 Deliverable 7.2: Pattern Learning Activation Tests
RED Phase - Tests written before implementation

Tests for:
- Relationship mapper (entity graphs: file→function, feature→file)
- Auto-learning from TDD cycles (Phase 3 integration)
- Relevance scoring algorithm for pattern matching
- Enhanced FTS5 semantic search wrapper

Author: Asif Hussain
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from src.tier2.knowledge_graph import KnowledgeGraph


class TestRelationshipMapper:
    """Test entity relationship graph building"""
    
    @pytest.fixture
    def knowledge_graph(self, tmp_path):
        """Create knowledge graph instance"""
        db_path = tmp_path / "test_kg.db"
        return KnowledgeGraph(db_path=db_path)
    
    def test_relationship_mapper_exists(self):
        """Test that relationship_mapper module exists"""
        from src.tier2 import relationship_mapper
        assert relationship_mapper is not None
    
    def test_extract_file_to_function_relationships(self, knowledge_graph):
        """Test extracting file→function relationships from code"""
        from src.tier2.relationship_mapper import RelationshipMapper
        
        mapper = RelationshipMapper(knowledge_graph)
        
        # Sample Python code
        code = """
def process_data(data):
    return clean(data)

def clean(data):
    return data.strip()
"""
        
        # Extract relationships
        relationships = mapper.extract_code_relationships(
            file_path="src/utils/data.py",
            code_content=code
        )
        
        assert len(relationships) > 0
        # Should find function definitions
        assert any(r['type'] == 'function_definition' for r in relationships)
        # Should find function calls
        assert any(r['type'] == 'function_call' for r in relationships)
    
    def test_extract_file_to_file_relationships(self, knowledge_graph):
        """Test extracting file→file import relationships"""
        from src.tier2.relationship_mapper import RelationshipMapper
        
        mapper = RelationshipMapper(knowledge_graph)
        
        # Sample code with imports
        code = """
from src.tier1.working_memory import WorkingMemory
from src.tier2.knowledge_graph import KnowledgeGraph
import json
"""
        
        relationships = mapper.extract_import_relationships(
            file_path="src/orchestrators/main.py",
            code_content=code
        )
        
        assert len(relationships) >= 2  # At least 2 internal imports
        # Should identify source and target files
        for rel in relationships:
            assert 'source' in rel
            assert 'target' in rel
            assert 'type' in rel
    
    def test_build_feature_to_file_graph(self, knowledge_graph):
        """Test building feature→file relationship graph"""
        from src.tier2.relationship_mapper import RelationshipMapper
        
        mapper = RelationshipMapper(knowledge_graph)
        
        # Simulate feature implementation across files
        feature_files = {
            'feature_tdd_workflow': [
                'src/tier0/tdd_enforcer.py',
                'tests/test_tdd.py',
                'src/cortex_agents/tdd_agent.py'
            ]
        }
        
        # Build graph
        graph = mapper.build_feature_graph(feature_files)
        
        assert 'feature_tdd_workflow' in graph
        assert len(graph['feature_tdd_workflow']) == 3
        assert 'src/tier0/tdd_enforcer.py' in graph['feature_tdd_workflow']
    
    def test_store_relationship_to_tier2(self, knowledge_graph):
        """Test storing relationship in Tier 2 knowledge graph"""
        from src.tier2.relationship_mapper import RelationshipMapper
        
        mapper = RelationshipMapper(knowledge_graph)
        
        # Store relationship
        rel_id = mapper.store_relationship(
            source="src/tier1/working_memory.py",
            target="src/tier2/knowledge_graph.py",
            relationship_type="imports",
            strength=0.8,
            context="Working memory archives to Tier 2"
        )
        
        assert rel_id is not None
        
        # Verify stored
        relationships = knowledge_graph.get_relationships(
            file_a="src/tier1/working_memory.py"
        )
        assert len(relationships) > 0
        assert relationships[0]['target'] == "src/tier2/knowledge_graph.py"


class TestTDDCycleLearning:
    """Test auto-learning from TDD cycles (Phase 3 integration)"""
    
    @pytest.fixture
    def knowledge_graph(self, tmp_path):
        """Create knowledge graph instance"""
        db_path = tmp_path / "test_kg.db"
        return KnowledgeGraph(db_path=db_path)
    
    def test_tdd_cycle_logger_exists(self):
        """Test that TDD cycle logger exists"""
        from src.tier2 import tdd_cycle_logger
        assert tdd_cycle_logger is not None
    
    def test_capture_red_phase_pattern(self, knowledge_graph):
        """Test capturing pattern from RED phase (test-first)"""
        from src.tier2.tdd_cycle_logger import TDDCycleLogger
        
        logger = TDDCycleLogger(knowledge_graph)
        
        # Simulate RED phase
        pattern_id = logger.log_red_phase(
            test_file="tests/test_feature.py",
            test_name="test_new_feature",
            test_content="def test_new_feature(): assert feature() == expected",
            intent="Add new feature validation"
        )
        
        assert pattern_id is not None
        
        # Verify pattern stored
        pattern = knowledge_graph.get_pattern(pattern_id)
        assert pattern is not None
        assert pattern['pattern_type'] == 'workflow'  # RED uses 'workflow' type
        # Check for RED phase namespace
        import json
        namespaces = json.loads(pattern.get('namespaces', '[]'))
        assert 'red-phase' in namespaces
    
    def test_capture_green_phase_pattern(self, knowledge_graph):
        """Test capturing pattern from GREEN phase (implementation)"""
        from src.tier2.tdd_cycle_logger import TDDCycleLogger
        
        logger = TDDCycleLogger(knowledge_graph)
        
        # Simulate GREEN phase
        pattern_id = logger.log_green_phase(
            impl_file="src/module/feature.py",
            impl_content="def feature(): return 'result'",
            test_file="tests/test_feature.py",
            test_passed=True
        )
        
        assert pattern_id is not None
        
        # Verify pattern stored with success indicator
        pattern = knowledge_graph.get_pattern(pattern_id)
        assert pattern is not None
        assert pattern['pattern_type'] == 'solution'  # GREEN uses 'solution' type
    
    def test_capture_refactor_phase_pattern(self, knowledge_graph):
        """Test capturing pattern from REFACTOR phase (cleanup)"""
        from src.tier2.tdd_cycle_logger import TDDCycleLogger
        
        logger = TDDCycleLogger(knowledge_graph)
        
        # Simulate REFACTOR phase
        pattern_id = logger.log_refactor_phase(
            file_path="src/module/feature.py",
            before_code="def feature(): x = 1; y = 2; return x + y",
            after_code="def feature(): return calculate_sum(1, 2)",
            refactor_type="extract_function",
            tests_still_passing=True
        )
        
        assert pattern_id is not None
        
        # Verify refactoring pattern captured
        pattern = knowledge_graph.get_pattern(pattern_id)
        assert pattern is not None
        # Check context for refactor type (stored in context dict)
        import json
        context = json.loads(pattern.get('context_json', '{}'))
        assert 'refactor_type' in context
    
    def test_link_tdd_cycle_patterns(self, knowledge_graph):
        """Test linking RED→GREEN→REFACTOR patterns into cycle"""
        from src.tier2.tdd_cycle_logger import TDDCycleLogger
        
        logger = TDDCycleLogger(knowledge_graph)
        
        # Log complete cycle
        red_id = logger.log_red_phase(
            test_file="tests/test.py",
            test_name="test_feature",
            test_content="assert True",
            intent="Test"
        )
        
        green_id = logger.log_green_phase(
            impl_file="src/feature.py",
            impl_content="def feature(): pass",
            test_file="tests/test.py",
            test_passed=True
        )
        
        # Link cycle
        cycle_id = logger.link_cycle(red_id, green_id, refactor_id=None)
        
        assert cycle_id is not None
        
        # Verify cycle stored
        cycle = knowledge_graph.get_pattern(cycle_id)
        assert cycle is not None
        assert cycle['pattern_type'] == 'workflow'  # Complete cycle uses 'workflow' type


class TestRelevanceScoring:
    """Test relevance scoring algorithm for pattern matching"""
    
    @pytest.fixture
    def knowledge_graph(self, tmp_path):
        """Create knowledge graph instance"""
        db_path = tmp_path / "test_kg.db"
        kg = KnowledgeGraph(db_path=db_path)
        
        # Seed some patterns
        kg.store_pattern(
            pattern_id="pat_1",
            title="Database connection pattern",
            content="Use context managers for DB connections",
            pattern_type="principle",
            confidence=0.9,
            namespaces=["database", "best-practices"]
        )
        
        kg.store_pattern(
            pattern_id="pat_2",
            title="Error handling in API calls",
            content="Always use try-except with specific exceptions",
            pattern_type="principle",
            confidence=0.85,
            namespaces=["api", "error-handling"]
        )
        
        kg.store_pattern(
            pattern_id="pat_3",
            title="Database connection pooling",
            content="Use connection pooling for better performance",
            pattern_type="solution",
            confidence=0.7,
            namespaces=["database", "performance"]
        )
        
        return kg
    
    def test_relevance_scorer_exists(self):
        """Test that relevance scorer module exists"""
        from src.tier2 import relevance_scorer
        assert relevance_scorer is not None
    
    def test_calculate_text_similarity(self, knowledge_graph):
        """Test text similarity calculation between query and pattern"""
        from src.tier2.relevance_scorer import RelevanceScorer
        
        scorer = RelevanceScorer(knowledge_graph)
        
        query = "How do I connect to database safely using context managers?"
        pattern_content = "Use context managers for database connections"
        
        similarity = scorer.calculate_text_similarity(query, pattern_content)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.2  # Should have some similarity (context, managers, database)
    
    def test_calculate_namespace_overlap(self, knowledge_graph):
        """Test namespace overlap scoring"""
        from src.tier2.relevance_scorer import RelevanceScorer
        
        scorer = RelevanceScorer(knowledge_graph)
        
        query_namespaces = ["database", "connection", "python"]
        pattern_namespaces = ["database", "best-practices"]
        
        overlap_score = scorer.calculate_namespace_overlap(
            query_namespaces,
            pattern_namespaces
        )
        
        assert 0.0 <= overlap_score <= 1.0
        assert overlap_score > 0  # "database" overlaps
    
    def test_calculate_recency_score(self, knowledge_graph):
        """Test recency scoring (prefer recently used patterns)"""
        from src.tier2.relevance_scorer import RelevanceScorer
        
        scorer = RelevanceScorer(knowledge_graph)
        
        # Recent pattern
        recent_score = scorer.calculate_recency_score(
            last_used=datetime.now().isoformat()
        )
        
        # Old pattern (never used)
        old_score = scorer.calculate_recency_score(
            last_used=None
        )
        
        assert recent_score > old_score
    
    def test_calculate_composite_relevance_score(self, knowledge_graph):
        """Test composite relevance score combining multiple factors"""
        from src.tier2.relevance_scorer import RelevanceScorer
        
        scorer = RelevanceScorer(knowledge_graph)
        
        relevance = scorer.calculate_relevance(
            query="database connection best practices",
            pattern_id="pat_1",
            context_namespaces=["database", "python"]
        )
        
        assert isinstance(relevance, dict)
        assert 'text_similarity' in relevance
        assert 'namespace_overlap' in relevance
        assert 'confidence' in relevance
        assert 'recency' in relevance
        assert 'composite_score' in relevance
        assert 0.0 <= relevance['composite_score'] <= 1.0
    
    def test_rank_patterns_by_relevance(self, knowledge_graph):
        """Test ranking multiple patterns by relevance"""
        from src.tier2.relevance_scorer import RelevanceScorer
        
        scorer = RelevanceScorer(knowledge_graph)
        
        query = "database connection best practices"
        pattern_ids = ["pat_1", "pat_2", "pat_3"]
        
        ranked = scorer.rank_patterns(
            query=query,
            pattern_ids=pattern_ids,
            context_namespaces=["database"]
        )
        
        assert len(ranked) == 3
        # Should be ordered by relevance (highest first)
        assert ranked[0]['composite_score'] >= ranked[1]['composite_score']
        assert ranked[1]['composite_score'] >= ranked[2]['composite_score']
        # pat_1 should rank highest (best namespace match + high confidence)
        assert ranked[0]['pattern_id'] == 'pat_1'


class TestEnhancedSemanticSearch:
    """Test enhanced FTS5 semantic search wrapper"""
    
    @pytest.fixture
    def knowledge_graph(self, tmp_path):
        """Create knowledge graph with patterns"""
        db_path = tmp_path / "test_kg.db"
        kg = KnowledgeGraph(db_path=db_path)
        
        # Seed patterns
        kg.store_pattern(
            pattern_id="search_1",
            title="SQLite FTS5 full-text search",
            content="FTS5 enables fast full-text search in SQLite with ranking",
            pattern_type="solution",
            confidence=0.9
        )
        
        kg.store_pattern(
            pattern_id="search_2",
            title="Database indexing strategies",
            content="Create indexes on frequently queried columns for performance",
            pattern_type="principle",
            confidence=0.85
        )
        
        return kg
    
    def test_semantic_search_wrapper_exists(self):
        """Test that semantic search wrapper exists"""
        from src.tier2 import semantic_search
        assert semantic_search is not None
    
    def test_fts5_search_with_ranking(self, knowledge_graph):
        """Test FTS5 search returns ranked results"""
        from src.tier2.semantic_search import SemanticSearch
        
        search = SemanticSearch(knowledge_graph)
        
        results = search.search("full-text search SQLite")
        
        assert len(results) > 0
        # Should have ranking scores
        assert 'rank' in results[0] or 'score' in results[0]
        # Best match should be first
        assert results[0]['pattern_id'] == 'search_1'
    
    def test_search_with_filters(self, knowledge_graph):
        """Test search with pattern type filters"""
        from src.tier2.semantic_search import SemanticSearch
        
        search = SemanticSearch(knowledge_graph)
        
        results = search.search(
            query="database",
            pattern_type="principle"
        )
        
        # Should only return 'principle' patterns
        for result in results:
            pattern = knowledge_graph.get_pattern(result['pattern_id'])
            assert pattern['pattern_type'] == 'principle'
    
    def test_search_with_namespace_filter(self, knowledge_graph):
        """Test search with namespace filtering"""
        from src.tier2.semantic_search import SemanticSearch
        
        # Add pattern with specific namespace
        knowledge_graph.store_pattern(
            pattern_id="ns_1",
            title="Python best practices",
            content="Use type hints for better code quality",
            pattern_type="principle",
            namespaces=["python", "best-practices"]
        )
        
        search = SemanticSearch(knowledge_graph)
        
        results = search.search(
            query="Python",
            namespaces=["python"]
        )
        
        assert len(results) > 0
    
    def test_search_performance_under_100ms(self, knowledge_graph):
        """Test that search completes in <100ms"""
        from src.tier2.semantic_search import SemanticSearch
        import time
        
        # Add more patterns for realistic test
        for i in range(50):
            knowledge_graph.store_pattern(
                pattern_id=f"perf_{i}",
                title=f"Pattern {i}",
                content=f"Content about topic {i} with various keywords",
                pattern_type="solution"
            )
        
        search = SemanticSearch(knowledge_graph)
        
        start = time.perf_counter()
        results = search.search("topic keywords various")
        duration_ms = (time.perf_counter() - start) * 1000
        
        assert duration_ms < 100, f"Search took {duration_ms:.2f}ms (should be <100ms)"
        assert len(results) > 0

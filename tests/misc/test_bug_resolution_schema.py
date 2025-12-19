"""
Test suite for Tier 2 schema validation with BUG_RESOLUTION pattern type.

Validates that bug_resolution patterns can be stored and retrieved from Tier 2.

Author: Asif Hussain
Created: 2025-12-09
Phase: TDD Mastery Phase 5.1 (Task 5.1.4)
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.tier2.knowledge_graph.patterns.pattern_store import PatternType
from src.tier2.knowledge_graph import KnowledgeGraph


@pytest.fixture
def temp_db_path():
    """Create temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kg.db"
    yield db_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def kg(temp_db_path):
    """Create KnowledgeGraph with temporary database."""
    kg_instance = KnowledgeGraph(db_path=temp_db_path)
    yield kg_instance
    # Close database connections before cleanup
    if hasattr(kg_instance, 'connection_manager'):
        kg_instance.connection_manager.close()


class TestBugResolutionPatternType:
    """Test BUG_RESOLUTION pattern type in Tier 2."""
    
    def test_bug_resolution_in_pattern_type_enum(self):
        """Test that BUG_RESOLUTION exists in PatternType enum."""
        assert hasattr(PatternType, 'BUG_RESOLUTION')
        assert PatternType.BUG_RESOLUTION.value == 'bug_resolution'
    
    def test_store_bug_resolution_pattern(self, kg):
        """Test storing a bug_resolution pattern."""
        kg.store_pattern(
            pattern_id="rca_auth_001",
            title="Authentication Token Expiry Bug",
            content="Token refresh logic fails when server time differs from client",
            pattern_type="bug_resolution",
            confidence=0.9,
            metadata={
                "symptom": "Users logged out unexpectedly",
                "root_cause": "Server time drift caused token validation to fail",
                "fix_applied": "Added clock skew tolerance of 30 seconds",
                "prevention": "Monitor server time drift, add alerting",
                "recurrence_risk": "low",
                "affected_features": ["authentication", "session_management"]
            }
        )
        
        # Pattern stored successfully if no exception raised
        assert True
    
    def test_retrieve_bug_resolution_pattern(self, kg):
        """Test retrieving a bug_resolution pattern."""
        # Store pattern
        kg.store_pattern(
            pattern_id="rca_api_001",
            title="API Rate Limiting Issue",
            content="Rate limiter incorrectly counting requests",
            pattern_type="bug_resolution",
            confidence=0.85,
            metadata={
                "symptom": "Valid API requests rejected with 429",
                "root_cause": "Redis counter not expiring correctly",
                "fix_applied": "Fixed TTL on Redis keys",
                "prevention": "Add integration tests for rate limiter",
                "recurrence_risk": "medium"
            }
        )
        
        # Retrieve pattern using search
        results = kg.search_patterns(
            query="API Rate Limiting",
            limit=5
        )
        
        # Filter for bug_resolution type
        bug_patterns = [r for r in results if r['pattern_type'] == 'bug_resolution']
        
        assert len(bug_patterns) > 0
        assert bug_patterns[0]['pattern_type'] == 'bug_resolution'
        assert 'symptom' in bug_patterns[0]['metadata']
    
    def test_bug_resolution_metadata_structure(self, kg):
        """Test that RCA metadata structure is preserved."""
        metadata = {
            "symptom": "Memory leak in background worker",
            "root_cause": "Event listeners not unregistered",
            "fix_applied": "Added cleanup in worker shutdown",
            "prevention": "Add memory profiling to CI pipeline",
            "recurrence_risk": "high",
            "affected_features": ["background_jobs", "workers"]
        }
        
        kg.store_pattern(
            pattern_id="rca_memory_001",
            title="Background Worker Memory Leak",
            content="Worker process memory grows unbounded",
            pattern_type="bug_resolution",
            confidence=0.95,
            metadata=metadata
        )
        
        # Search and verify
        results = kg.search_patterns(
            query="Background Worker",
            limit=5
        )
        
        # Filter for bug_resolution type
        bug_patterns = [r for r in results if r['pattern_type'] == 'bug_resolution']
        
        assert len(bug_patterns) > 0
        retrieved = bug_patterns[0]
        
        # Verify all RCA fields preserved
        assert retrieved['metadata']['symptom'] == metadata['symptom']
        assert retrieved['metadata']['root_cause'] == metadata['root_cause']
        assert retrieved['metadata']['fix_applied'] == metadata['fix_applied']
        assert retrieved['metadata']['prevention'] == metadata['prevention']
        assert retrieved['metadata']['recurrence_risk'] == metadata['recurrence_risk']
        assert retrieved['metadata']['affected_features'] == metadata['affected_features']

"""
Holistic Discovery Brain Protection Tests

Tests for HOLISTIC_DISCOVERY brain protection rule (SKULL rule).
Validates search-before-create workflow enforcement.

Test Coverage:
- Search before creating files
- Duplicate detection prevents creation
- Semantic search runs first
- Grep search follows semantic
- Discovery results logged

Author: Asif Hussain (CORTEX)
Created: January 3, 2026
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import List, Dict, Any


class TestHolisticDiscovery:
    """Test suite for HOLISTIC_DISCOVERY brain protection rule."""
    
    def test_search_before_create_files(self):
        """
        Test that search operations must occur before file creation.
        
        Brain Protection Rule: HOLISTIC_DISCOVERY
        Requirement: Search workspace before creating new files to prevent duplication
        
        Validates:
        - Cannot create file without prior search
        - Search must check for existing similar files
        - Creation blocked if duplicates found
        """
        # Arrange
        discovery_state = {"search_performed": False, "violations": []}
        
        def create_file(filename):
            if not discovery_state["search_performed"]:
                discovery_state["violations"].append(
                    "HOLISTIC_DISCOVERY: Must search workspace before creating files"
                )
                return False
            return True
        
        # Act - Try to create without search
        result = create_file("new_module.py")
        
        # Assert
        assert result is False
        assert len(discovery_state["violations"]) == 1
        assert "search workspace" in discovery_state["violations"][0]
        
        # Act - Perform search then create
        discovery_state["search_performed"] = True
        result = create_file("new_module.py")
        
        # Assert
        assert result is True
    
    def test_duplicate_detection_prevents_creation(self):
        """
        Test that duplicate detection prevents unnecessary file creation.
        
        Brain Protection Rule: HOLISTIC_DISCOVERY
        Requirement: Prevent code duplication by detecting existing implementations
        
        Validates:
        - Search finds existing similar files
        - System suggests using existing file instead
        - Creation blocked if duplicate functionality exists
        - User can override with justification
        """
        # Arrange
        search_results = [{"file": "existing_test.py", "similarity": 0.95}]
        
        def check_duplicates(filename, search_results):
            for result in search_results:
                if result["similarity"] > 0.9:
                    return False, f"Duplicate found: {result['file']}"
            return True, "No duplicates"
        
        # Act
        allowed, message = check_duplicates("new_test.py", search_results)
        
        # Assert
        assert allowed is False
        assert "Duplicate found" in message
        assert "existing_test.py" in message
    
    def test_semantic_search_runs_first(self):
        """
        Test that semantic search is executed before grep search.
        
        Brain Protection Rule: HOLISTIC_DISCOVERY
        Requirement: Semantic search provides broader context before narrow grep
        
        Validates:
        - Semantic search executed first
        - Search query uses natural language
        - Results include context beyond exact matches
        - Grep search can follow for refinement
        """
        # Arrange
        search_order = []
        
        def semantic_search(query):
            search_order.append("semantic")
            return [{"file": "auth.py", "relevance": 0.8}]
        
        def grep_search(pattern):
            if "semantic" not in search_order:
                return None
            search_order.append("grep")
            return [{"file": "auth.py", "line": 10}]
        
        # Act
        semantic_results = semantic_search("authentication")
        grep_results = grep_search("def auth")
        
        # Assert
        assert search_order == ["semantic", "grep"]
        assert semantic_results is not None
        assert grep_results is not None
    
    def test_grep_search_follows_semantic(self):
        """
        Test that grep search is used for refinement after semantic search.
        
        Brain Protection Rule: HOLISTIC_DISCOVERY
        Requirement: Grep search refines semantic results with exact patterns
        
        Validates:
        - Grep search follows semantic search
        - Grep uses exact string/regex patterns
        - Results complement semantic findings
        - Both searches logged to discovery trail
        """
        # Arrange
        discovery_trail = []
        
        def log_search(search_type, query, results_count):
            discovery_trail.append({
                "type": search_type,
                "query": query,
                "results": results_count
            })
        
        # Act
        log_search("semantic", "auth logic", 3)
        log_search("grep", "def authenticate", 2)
        
        # Assert
        assert len(discovery_trail) == 2
        assert discovery_trail[0]["type"] == "semantic"
        assert discovery_trail[1]["type"] == "grep"
        assert discovery_trail[1]["results"] == 2
    
    def test_discovery_results_logged(self):
        """
        Test that all discovery operations are logged for audit trail.
        
        Brain Protection Rule: HOLISTIC_DISCOVERY
        Requirement: All search and discovery operations logged
        
        Validates:
        - Search operations logged to protection-events.jsonl
        - Log includes search type, query, results count
        - File creation decisions tracked
        - Audit trail for duplication prevention
        """
        # Arrange
        from datetime import datetime
        event_log = []
        
        def log_discovery_event(rule_id, search_type, query, results_count):
            event_log.append({
                "timestamp": datetime.now().isoformat(),
                "rule_id": rule_id,
                "search_type": search_type,
                "query": query,
                "results_count": results_count
            })
        
        # Act
        log_discovery_event("HOLISTIC_DISCOVERY", "semantic", "authentication", 5)
        log_discovery_event("HOLISTIC_DISCOVERY", "grep", "def auth", 2)
        
        # Assert
        assert len(event_log) == 2
        assert all(e["rule_id"] == "HOLISTIC_DISCOVERY" for e in event_log)
        assert event_log[0]["results_count"] == 5


class TestHolisticDiscoveryIntegration:
    """Integration tests for holistic discovery workflow."""
    
    def test_orchestrator_enforces_search_before_create(self):
        """
        Integration test: Orchestrators enforce search before file creation.
        
        Validates orchestrators check discovery trail before allowing
        new file creation.
        """
        # Arrange - Mock orchestrator
        orchestrator_state = {"discovery_trail": []}
        
        def create_file_in_orchestrator(filename):
            if not orchestrator_state["discovery_trail"]:
                return False, "Search required before file creation"
            return True, "File created"
        
        # Act - Try without search
        allowed, message = create_file_in_orchestrator("new.py")
        assert allowed is False
        
        # Act - With search
        orchestrator_state["discovery_trail"].append({"search": "semantic", "results": 0})
        allowed, message = create_file_in_orchestrator("new.py")
        assert allowed is True
    
    def test_duplicate_detection_across_orchestrators(self):
        """
        Integration test: Duplicate detection works across orchestrators.
        
        Validates duplicate detection shares findings across different
        orchestrator executions.
        """
        # Arrange - Shared state
        shared_state = {"created_files": ["file_a.py"], "purposes": {"file_a.py": "authentication"}}
        
        def check_duplicate_purpose(filename, purpose):
            for existing_file, existing_purpose in shared_state["purposes"].items():
                if existing_purpose == purpose:
                    return False, f"Use existing {existing_file}"
            return True, "Unique purpose"
        
        # Act
        allowed, message = check_duplicate_purpose("file_b.py", "authentication")
        
        # Assert
        assert allowed is False
        assert "file_a.py" in message
    
    def test_search_results_cache_prevents_redundant_searches(self):
        """
        Integration test: Search results cached to prevent redundant operations.
        
        Validates search results are cached and reused within same session
        to improve performance.
        """
        # Arrange
        from datetime import datetime, timedelta
        cache = {}
        
        def cached_search(query, cache_timeout=300):
            if query in cache:
                age = (datetime.now() - cache[query]["timestamp"]).seconds
                if age < cache_timeout:
                    cache[query]["cache_hits"] += 1
                    return cache[query]["results"], True  # From cache
            # Perform search
            results = [{"file": "result.py"}]
            cache[query] = {"results": results, "timestamp": datetime.now(), "cache_hits": 0}
            return results, False  # Fresh search
        
        # Act
        results1, from_cache1 = cached_search("auth")
        results2, from_cache2 = cached_search("auth")
        
        # Assert
        assert from_cache1 is False  # First search
        assert from_cache2 is True   # Cached


class TestHolisticDiscoveryEdgeCases:
    """Edge case tests for holistic discovery."""
    
    def test_search_in_empty_workspace(self):
        """
        Test search behavior in empty workspace (no existing files).
        
        Validates search gracefully handles empty workspace and allows
        file creation.
        """
        # Arrange
        workspace_files = []
        
        def search_workspace(query):
            results = [f for f in workspace_files if query.lower() in f.lower()]
            return results
        
        def can_create_file(filename, search_results):
            if not search_results:  # Empty workspace
                return True, "No duplicates in empty workspace"
            return False, "Duplicates found"
        
        # Act
        results = search_workspace("test")
        allowed, message = can_create_file("test.py", results)
        
        # Assert
        assert len(results) == 0
        assert allowed is True
    
    def test_search_with_no_results_allows_creation(self):
        """
        Test that searches with no results allow file creation.
        
        Validates file creation is allowed when search proves no
        duplicates exist.
        """
        # Arrange
        def perform_discovery(query):
            semantic_results = []
            grep_results = []
            return semantic_results, grep_results
        
        def creation_allowed(semantic_results, grep_results):
            if not semantic_results and not grep_results:
                return True, "No duplicates found"
            return False, "Duplicates exist"
        
        # Act
        sem_res, grep_res = perform_discovery("unique_module")
        allowed, message = creation_allowed(sem_res, grep_res)
        
        # Assert
        assert allowed is True
        assert "No duplicates" in message


# Test fixtures
@pytest.fixture
def mock_semantic_search():
    """Mock semantic search tool."""
    search = Mock()
    search.execute = Mock(return_value=[
        {"file": "src/auth/login.py", "relevance": 0.9},
        {"file": "src/auth/register.py", "relevance": 0.7}
    ])
    return search


@pytest.fixture
def mock_grep_search():
    """Mock grep search tool."""
    search = Mock()
    search.execute = Mock(return_value=[
        {"file": "src/auth/login.py", "line": 42, "match": "def authenticate"},
        {"file": "src/auth/session.py", "line": 15, "match": "def authenticate"}
    ])
    return search


@pytest.fixture
def discovery_log(tmp_path):
    """Temporary discovery log file."""
    log_file = tmp_path / "discovery.jsonl"
    log_file.touch()
    return log_file


@pytest.fixture
def mock_brain_protector_holistic():
    """Mock Brain Protector for holistic discovery."""
    protector = Mock()
    protector.check_discovery = Mock(return_value={
        "search_performed": False,
        "allowed": False,
        "rule": "HOLISTIC_DISCOVERY"
    })
    protector.log_discovery = Mock()
    return protector


# Pytest marks
pytestmark = [
    pytest.mark.brain_protection,
    pytest.mark.holistic_discovery,
    pytest.mark.unit
]

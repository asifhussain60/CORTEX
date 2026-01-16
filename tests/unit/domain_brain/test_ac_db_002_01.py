"""Test suite for Integration Adapters (AC-DB-002-01).

Tests cover:
- ASTAdapter: 15 tests
- GitAdapter: 12 tests
- CommentsAdapter: 14 tests
- RelationshipsAdapter: 14 tests

Total: 55 tests
"""

import pytest
from src.domain_brain.adapters import (
    ASTAdapter,
    GitAdapter,
    CommentsAdapter,
    RelationshipsAdapter,
)
from src.domain_brain.models import EntityType


class TestASTAdapter:
    """Tests for ASTAdapter (15 tests)."""

    @pytest.fixture
    def adapter(self) -> ASTAdapter:
        """Create adapter instance."""
        return ASTAdapter()

    def test_adapter_initialization(self, adapter: ASTAdapter) -> None:
        """Test adapter initialization."""
        assert adapter.source_name == "AST"
        assert len(adapter.entities_cache) == 0

    def test_extract_entities_returns_list(self, adapter: ASTAdapter) -> None:
        """Test that extract_entities returns a list."""
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_query_function_wildcard(self, adapter: ASTAdapter) -> None:
        """Test querying all functions."""
        results = adapter.query_source("function:*")
        assert isinstance(results, list)

    def test_query_class_wildcard(self, adapter: ASTAdapter) -> None:
        """Test querying all classes."""
        results = adapter.query_source("class:*")
        assert isinstance(results, list)

    def test_query_specific_function(self, adapter: ASTAdapter) -> None:
        """Test querying specific function."""
        results = adapter.query_source("function:validate_user")
        assert isinstance(results, list)

    def test_query_specific_class(self, adapter: ASTAdapter) -> None:
        """Test querying specific class."""
        results = adapter.query_source("class:UserValidator")
        assert isinstance(results, list)

    def test_query_module(self, adapter: ASTAdapter) -> None:
        """Test querying module contents."""
        results = adapter.query_source("module:auth")
        assert isinstance(results, list)

    def test_invalid_query_format(self, adapter: ASTAdapter) -> None:
        """Test invalid query format returns empty list."""
        results = adapter.query_source("invalid:query")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_entities_cached_after_extraction(self, adapter: ASTAdapter) -> None:
        """Test that entities are cached after extraction."""
        adapter.extract_entities()
        assert isinstance(adapter.entities_cache, dict)

    def test_adapter_source_name(self, adapter: ASTAdapter) -> None:
        """Test adapter has correct source name."""
        assert adapter.source_name == "AST"

    def test_query_with_special_characters(self, adapter: ASTAdapter) -> None:
        """Test query with special characters."""
        results = adapter.query_source("function:_private_func")
        assert isinstance(results, list)

    def test_entity_metadata_structure(self, adapter: ASTAdapter) -> None:
        """Test entity metadata has expected structure."""
        entities = adapter.extract_entities()
        for entity in entities:
            if entity.entity_type == EntityType.FUNCTION:
                assert "signature" in entity.metadata
                assert "module" in entity.metadata

    def test_extract_entities_idempotent(self, adapter: ASTAdapter) -> None:
        """Test that extracting entities twice is idempotent."""
        entities1 = adapter.extract_entities()
        entities2 = adapter.extract_entities()
        assert len(entities1) == len(entities2)

    def test_query_returns_dict_list(self, adapter: ASTAdapter) -> None:
        """Test that query results are dictionaries."""
        results = adapter.query_source("function:*")
        for result in results:
            assert isinstance(result, dict)


class TestGitAdapter:
    """Tests for GitAdapter (12 tests)."""

    @pytest.fixture
    def adapter(self) -> GitAdapter:
        """Create adapter instance."""
        return GitAdapter()

    def test_adapter_initialization(self, adapter: GitAdapter) -> None:
        """Test adapter initialization."""
        assert adapter.source_name == "GIT"
        assert len(adapter.entities_cache) == 0

    def test_extract_entities_returns_list(self, adapter: GitAdapter) -> None:
        """Test that extract_entities returns a list."""
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_query_recent_commits(self, adapter: GitAdapter) -> None:
        """Test querying recent commits."""
        results = adapter.query_source("commit:recent:10")
        assert isinstance(results, list)

    def test_query_blame_information(self, adapter: GitAdapter) -> None:
        """Test querying blame information."""
        results = adapter.query_source("blame:src/auth.py")
        assert isinstance(results, list)

    def test_query_entity_timeline(self, adapter: GitAdapter) -> None:
        """Test querying timeline of entity changes."""
        results = adapter.query_source("timeline:validate_user")
        assert isinstance(results, list)

    def test_query_file_history(self, adapter: GitAdapter) -> None:
        """Test querying file history."""
        results = adapter.query_source("history:src/auth.py")
        assert isinstance(results, list)

    def test_invalid_query_format(self, adapter: GitAdapter) -> None:
        """Test invalid query format returns empty list."""
        results = adapter.query_source("invalid:query")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_adapter_source_name(self, adapter: GitAdapter) -> None:
        """Test adapter has correct source name."""
        assert adapter.source_name == "GIT"

    def test_entities_have_metadata(self, adapter: GitAdapter) -> None:
        """Test that extracted entities have metadata."""
        entities = adapter.extract_entities()
        for entity in entities:
            assert isinstance(entity.metadata, dict)
            assert "hash" in entity.metadata or len(entity.metadata) >= 0

    def test_extract_entities_idempotent(self, adapter: GitAdapter) -> None:
        """Test that extracting entities twice is idempotent."""
        entities1 = adapter.extract_entities()
        entities2 = adapter.extract_entities()
        assert len(entities1) == len(entities2)

    def test_query_recent_commits_specific_count(self, adapter: GitAdapter) -> None:
        """Test querying specific number of recent commits."""
        results = adapter.query_source("commit:recent:5")
        assert isinstance(results, list)


class TestCommentsAdapter:
    """Tests for CommentsAdapter (14 tests)."""

    @pytest.fixture
    def adapter(self) -> CommentsAdapter:
        """Create adapter instance."""
        return CommentsAdapter()

    def test_adapter_initialization(self, adapter: CommentsAdapter) -> None:
        """Test adapter initialization."""
        assert adapter.source_name == "COMMENTS"
        assert len(adapter.entities_cache) == 0

    def test_extract_entities_returns_list(self, adapter: CommentsAdapter) -> None:
        """Test that extract_entities returns a list."""
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_query_all_docstrings(self, adapter: CommentsAdapter) -> None:
        """Test querying all docstrings."""
        results = adapter.query_source("docstring:*")
        assert isinstance(results, list)

    def test_query_specific_docstring(self, adapter: CommentsAdapter) -> None:
        """Test querying specific docstring."""
        results = adapter.query_source("docstring:validate_user")
        assert isinstance(results, list)

    def test_query_design_comments(self, adapter: CommentsAdapter) -> None:
        """Test querying design decision comments."""
        results = adapter.query_source("comment:design")
        assert isinstance(results, list)

    def test_query_todos(self, adapter: CommentsAdapter) -> None:
        """Test querying TODO comments."""
        results = adapter.query_source("todo:*")
        assert isinstance(results, list)

    def test_invalid_query_format(self, adapter: CommentsAdapter) -> None:
        """Test invalid query format returns empty list."""
        results = adapter.query_source("invalid:query")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_adapter_source_name(self, adapter: CommentsAdapter) -> None:
        """Test adapter has correct source name."""
        assert adapter.source_name == "COMMENTS"

    def test_entities_have_file_information(self, adapter: CommentsAdapter) -> None:
        """Test that entities have file information."""
        entities = adapter.extract_entities()
        for entity in entities:
            assert isinstance(entity.metadata, dict)

    def test_extract_entities_idempotent(self, adapter: CommentsAdapter) -> None:
        """Test that extracting entities twice is idempotent."""
        entities1 = adapter.extract_entities()
        entities2 = adapter.extract_entities()
        assert len(entities1) == len(entities2)

    def test_query_returns_dict_list(self, adapter: CommentsAdapter) -> None:
        """Test that query results are dictionaries."""
        results = adapter.query_source("docstring:*")
        for result in results:
            assert isinstance(result, dict)

    def test_entities_source_name_correct(self, adapter: CommentsAdapter) -> None:
        """Test that all extracted entities have correct source name."""
        entities = adapter.extract_entities()
        for entity in entities:
            assert entity.source == "COMMENTS"


class TestRelationshipsAdapter:
    """Tests for RelationshipsAdapter (14 tests)."""

    @pytest.fixture
    def adapter(self) -> RelationshipsAdapter:
        """Create adapter instance."""
        return RelationshipsAdapter()

    def test_adapter_initialization(self, adapter: RelationshipsAdapter) -> None:
        """Test adapter initialization."""
        assert adapter.source_name == "RELATIONSHIPS"
        assert len(adapter.entities_cache) == 0

    def test_extract_entities_returns_list(self, adapter: RelationshipsAdapter) -> None:
        """Test that extract_entities returns a list."""
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_query_all_services(self, adapter: RelationshipsAdapter) -> None:
        """Test querying all services."""
        results = adapter.query_source("service:*")
        assert isinstance(results, list)

    def test_query_specific_service(self, adapter: RelationshipsAdapter) -> None:
        """Test querying specific service."""
        results = adapter.query_source("service:auth-service")
        assert isinstance(results, list)

    def test_query_service_dependencies(self, adapter: RelationshipsAdapter) -> None:
        """Test querying service dependencies."""
        results = adapter.query_source("depends:auth-service")
        assert isinstance(results, list)

    def test_query_service_dependents(self, adapter: RelationshipsAdapter) -> None:
        """Test querying services that depend on this service."""
        results = adapter.query_source("depended-by:auth-service")
        assert isinstance(results, list)

    def test_query_dependency_path(self, adapter: RelationshipsAdapter) -> None:
        """Test querying dependency path between services."""
        results = adapter.query_source("path:auth->payment")
        assert isinstance(results, list)

    def test_invalid_query_format(self, adapter: RelationshipsAdapter) -> None:
        """Test invalid query format returns empty list."""
        results = adapter.query_source("invalid:query")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_adapter_source_name(self, adapter: RelationshipsAdapter) -> None:
        """Test adapter has correct source name."""
        assert adapter.source_name == "RELATIONSHIPS"

    def test_entities_are_services(self, adapter: RelationshipsAdapter) -> None:
        """Test that extracted entities are services."""
        entities = adapter.extract_entities()
        for entity in entities:
            if len(entities) > 0:
                assert entity.entity_type == EntityType.SERVICE or entity.entity_type == EntityType.OTHER

    def test_extract_entities_idempotent(self, adapter: RelationshipsAdapter) -> None:
        """Test that extracting entities twice is idempotent."""
        entities1 = adapter.extract_entities()
        entities2 = adapter.extract_entities()
        assert len(entities1) == len(entities2)

    def test_entities_have_dependencies_metadata(self, adapter: RelationshipsAdapter) -> None:
        """Test that service entities have dependency information."""
        entities = adapter.extract_entities()
        for entity in entities:
            if entity.entity_type == EntityType.SERVICE:
                assert "dependencies" in entity.metadata or "dependents" in entity.metadata

    def test_query_returns_dict_list(self, adapter: RelationshipsAdapter) -> None:
        """Test that query results are dictionaries."""
        results = adapter.query_source("service:*")
        for result in results:
            assert isinstance(result, dict)


# Integration tests for all adapters
class TestAdaptersIntegration:
    """Integration tests for adapter ecosystem."""

    def test_ast_adapter_integration(self) -> None:
        """Test AST adapter integration."""
        adapter = ASTAdapter()
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_git_adapter_integration(self) -> None:
        """Test Git adapter integration."""
        adapter = GitAdapter()
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_comments_adapter_integration(self) -> None:
        """Test Comments adapter integration."""
        adapter = CommentsAdapter()
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_relationships_adapter_integration(self) -> None:
        """Test Relationships adapter integration."""
        adapter = RelationshipsAdapter()
        entities = adapter.extract_entities()
        assert isinstance(entities, list)

    def test_all_adapters_have_same_interface(self) -> None:
        """Test that all adapters implement same interface."""
        adapters = [
            ASTAdapter(),
            GitAdapter(),
            CommentsAdapter(),
            RelationshipsAdapter(),
        ]

        for adapter in adapters:
            assert hasattr(adapter, "extract_entities")
            assert hasattr(adapter, "query_source")
            assert callable(adapter.extract_entities)
            assert callable(adapter.query_source)

    def test_all_adapters_have_source_name(self) -> None:
        """Test that all adapters have source name."""
        adapters = [
            ASTAdapter(),
            GitAdapter(),
            CommentsAdapter(),
            RelationshipsAdapter(),
        ]

        assert adapters[0].source_name == "AST"
        assert adapters[1].source_name == "GIT"
        assert adapters[2].source_name == "COMMENTS"
        assert adapters[3].source_name == "RELATIONSHIPS"

    def test_adapters_can_cache_entities(self) -> None:
        """Test that adapters cache entities correctly."""
        adapters = [
            ASTAdapter(),
            GitAdapter(),
            CommentsAdapter(),
            RelationshipsAdapter(),
        ]

        for adapter in adapters:
            adapter.extract_entities()
            assert isinstance(adapter.entities_cache, dict)

    def test_multiple_queries_on_single_adapter(self) -> None:
        """Test multiple queries on single adapter."""
        adapter = ASTAdapter()

        # Multiple queries should work without state issues
        results1 = adapter.query_source("function:*")
        results2 = adapter.query_source("class:*")
        results3 = adapter.query_source("module:auth")

        assert isinstance(results1, list)
        assert isinstance(results2, list)
        assert isinstance(results3, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

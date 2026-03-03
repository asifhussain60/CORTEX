"""
Phase 80-b — GAP-80-02: KnowledgeRepository graceful degradation.

Tests that KnowledgeRepository does NOT crash when .knowledge-index.json
is absent, and degrades gracefully (is_available() → False, search → []).

CORE-008: Tests written first (RED phase).
"""

import pytest


class TestKnowledgeRepositoryDegradation:
    """Tests for GAP-80-02: graceful degradation when index is absent."""

    def test_knowledge_repository_no_crash_without_index(self, tmp_path):
        """KnowledgeRepository() succeeds even when the index file is missing."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
        # Should NOT raise FileNotFoundError
        repo = KnowledgeRepository(project_root=str(tmp_path))
        assert repo is not None

    def test_knowledge_repository_is_available_false_without_index(self, tmp_path):
        """is_available() returns False when the index file is missing."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
        repo = KnowledgeRepository(project_root=str(tmp_path))
        assert repo.is_available() is False

    def test_knowledge_repository_search_returns_empty_without_index(self, tmp_path):
        """query() returns empty KnowledgeQueryResult when the index file is missing."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
        repo = KnowledgeRepository(project_root=str(tmp_path))
        result = repo.query(keywords=["test"])
        # query() returns KnowledgeQueryResult — .entries should be empty list
        assert isinstance(result.entries, list)
        assert result.entries == []

    def test_knowledge_repository_get_by_domain_returns_empty_without_index(self, tmp_path):
        """get_by_domain() returns [] when the index is absent."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
        repo = KnowledgeRepository(project_root=str(tmp_path))
        result = repo.get_by_domain("SECURITY")
        assert isinstance(result, list)
        assert result == []

    def test_knowledge_repository_loads_with_valid_index(self, tmp_path):
        """KnowledgeRepository loads normally when index file exists."""
        import json
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository

        # Create a valid minimal index
        kb_dir = tmp_path / "cortex-registry" / "knowledge"
        kb_dir.mkdir(parents=True)
        index_data = {"version": "1.0", "entries": []}
        (kb_dir / ".knowledge-index.json").write_text(json.dumps(index_data))

        repo = KnowledgeRepository(project_root=str(tmp_path))
        assert repo.is_available() is True

    def test_knowledge_repository_is_available_attribute_exists(self, tmp_path):
        """KnowledgeRepository exposes is_available() as a callable."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
        repo = KnowledgeRepository(project_root=str(tmp_path))
        assert callable(getattr(repo, "is_available", None))

"""Tests for InquiryCache - Repo-scoped caching system.

AC-ID: INQUIRY-002-NEW
Purpose: Test SQLite-backed cache with repo isolation
Author: Asif Hussain
Date: 2026-01-27
"""

import hashlib
import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest

from cortex.models.inquiry_models import RepoContext, RepoType
from cortex.orchestrators.support.inquiry_cache import InquiryCache


@pytest.fixture
def temp_cache_db(tmp_path: Path) -> Path:
    """Create temporary cache database."""
    cache_db = tmp_path / ".cortex" / "inquiry_cache.db"
    cache_db.parent.mkdir(parents=True, exist_ok=True)
    return cache_db


@pytest.fixture
def cortex_repo_context(tmp_path: Path) -> RepoContext:
    """Create CORTEX repo context."""
    return RepoContext(
        repo_type=RepoType.CORTEX,
        repo_path=tmp_path / "CORTEX",
        repo_name="CORTEX",
        git_remote="https://github.com/asifhussain60/CORTEX.git",
        detection_confidence=0.95,
        detection_signals={"keyword_match": True, "cwd_match": True},
    )


@pytest.fixture
def user_repo_context(tmp_path: Path) -> RepoContext:
    """Create user repo context."""
    return RepoContext(
        repo_type=RepoType.USER_REPO,
        repo_path=tmp_path / "my-project",
        repo_name="my-project",
        git_remote="https://github.com/user/my-project.git",
        detection_confidence=0.30,
        detection_signals={"keyword_match": False, "cwd_match": False},
    )


class TestInquiryCacheInitialization:
    """Test cache initialization and database setup."""
    
    def test_create_cache_creates_database(self, temp_cache_db: Path) -> None:
        """Test cache creation creates SQLite database."""
        cache = InquiryCache(db_path=temp_cache_db)
        
        assert temp_cache_db.exists()
        assert temp_cache_db.is_file()
    
    def test_create_cache_creates_schema(self, temp_cache_db: Path) -> None:
        """Test cache creation creates proper schema."""
        cache = InquiryCache(db_path=temp_cache_db)
        
        # Check table exists
        conn = sqlite3.connect(temp_cache_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inquiry_cache'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == "inquiry_cache"
    
    def test_cache_schema_has_repo_column(self, temp_cache_db: Path) -> None:
        """Test cache schema includes repo_name column for isolation."""
        cache = InquiryCache(db_path=temp_cache_db)
        
        conn = sqlite3.connect(temp_cache_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(inquiry_cache)")
        columns = [row[1] for row in cursor.fetchall()]
        conn.close()
        
        assert "repo_name" in columns
        assert "question_hash" in columns
        assert "response" in columns
        assert "timestamp" in columns


class TestInquiryCacheRepoScoping:
    """Test repo-scoped cache isolation."""
    
    def test_generate_cache_key_cortex(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test cache key generation for CORTEX repo."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How does TDDOrchestrator work?"
        
        cache_key = cache.generate_cache_key(question, cortex_repo_context)
        
        # Should be format: CORTEX:8char_hash
        assert cache_key.startswith("CORTEX:")
        assert len(cache_key.split(":")[1]) == 8
    
    def test_generate_cache_key_user_repo(
        self,
        temp_cache_db: Path,
        user_repo_context: RepoContext,
    ) -> None:
        """Test cache key generation for user repo."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How do I add authentication?"
        
        cache_key = cache.generate_cache_key(question, user_repo_context)
        
        # Should be format: my-project:8char_hash
        assert cache_key.startswith("my-project:")
        assert len(cache_key.split(":")[1]) == 8
    
    def test_same_question_different_repos_different_keys(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
        user_repo_context: RepoContext,
    ) -> None:
        """Test same question in different repos generates different cache keys."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How does authentication work?"
        
        cortex_key = cache.generate_cache_key(question, cortex_repo_context)
        user_key = cache.generate_cache_key(question, user_repo_context)
        
        assert cortex_key != user_key
        assert cortex_key.startswith("CORTEX:")
        assert user_key.startswith("my-project:")


class TestInquiryCacheOperations:
    """Test cache set/get operations."""
    
    def test_cache_set_and_get(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test setting and retrieving cached response."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How does TDDOrchestrator work?"
        response = {"answer": "TDDOrchestrator implements test-driven development..."}
        
        cache.set(question, cortex_repo_context, response)
        cached_response = cache.get(question, cortex_repo_context)
        
        assert cached_response is not None
        assert cached_response["answer"] == response["answer"]
    
    def test_cache_get_miss_returns_none(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test cache miss returns None."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How does RefactoringOrchestrator work?"
        
        cached_response = cache.get(question, cortex_repo_context)
        
        assert cached_response is None
    
    def test_cache_isolation_between_repos(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
        user_repo_context: RepoContext,
    ) -> None:
        """Test cache isolation between CORTEX and user repos."""
        cache = InquiryCache(db_path=temp_cache_db)
        question = "How does authentication work?"
        
        cortex_response = {"answer": "CORTEX uses JWT authentication..."}
        user_response = {"answer": "Your project uses OAuth2..."}
        
        # Cache different responses for same question in different repos
        cache.set(question, cortex_repo_context, cortex_response)
        cache.set(question, user_repo_context, user_response)
        
        # Verify isolation
        cortex_cached = cache.get(question, cortex_repo_context)
        user_cached = cache.get(question, user_repo_context)
        
        assert cortex_cached is not None
        assert user_cached is not None
        assert cortex_cached["answer"] == cortex_response["answer"]
        assert user_cached["answer"] == user_response["answer"]
        assert cortex_cached != user_cached


class TestInquiryCacheManagement:
    """Test cache management operations."""
    
    def test_cache_clear_repo(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
        user_repo_context: RepoContext,
    ) -> None:
        """Test clearing cache for specific repo."""
        cache = InquiryCache(db_path=temp_cache_db)
        
        cache.set("Question 1", cortex_repo_context, {"answer": "CORTEX answer 1"})
        cache.set("Question 2", cortex_repo_context, {"answer": "CORTEX answer 2"})
        cache.set("Question 3", user_repo_context, {"answer": "User answer 3"})
        
        # Clear CORTEX cache only
        cache.clear_repo(cortex_repo_context)
        
        # CORTEX cache should be cleared
        assert cache.get("Question 1", cortex_repo_context) is None
        assert cache.get("Question 2", cortex_repo_context) is None
        
        # User repo cache should remain
        assert cache.get("Question 3", user_repo_context) is not None
    
    def test_cache_clear_all(
        self,
        temp_cache_db: Path,
        cortex_repo_context: RepoContext,
        user_repo_context: RepoContext,
    ) -> None:
        """Test clearing entire cache."""
        cache = InquiryCache(db_path=temp_cache_db)
        
        cache.set("Question 1", cortex_repo_context, {"answer": "CORTEX answer 1"})
        cache.set("Question 2", user_repo_context, {"answer": "User answer 2"})
        
        # Clear all cache
        cache.clear_all()
        
        # Both should be cleared
        assert cache.get("Question 1", cortex_repo_context) is None
        assert cache.get("Question 2", user_repo_context) is None

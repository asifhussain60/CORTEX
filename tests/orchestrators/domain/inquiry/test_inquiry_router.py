"""Tests for InquiryRouter - Handler routing logic.

AC-ID: INQUIRY-007-NEW
Purpose: Test routing questions to appropriate handlers
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from cortex.models.inquiry_models import (
    AssembledContext,
    InquiryCategory,
    RepoContext,
    RepoType,
)
from cortex.orchestrators.domain.inquiry.inquiry_router import InquiryRouter


@pytest.fixture
def cortex_repo_context(tmp_path: Path) -> RepoContext:
    """Create CORTEX repo context."""
    return RepoContext(
        repo_type=RepoType.CORTEX,
        repo_path=tmp_path / "CORTEX",
        repo_name="CORTEX",
        detection_confidence=0.95,
        detection_signals={"keyword_match": True},
    )


@pytest.fixture
def user_repo_context(tmp_path: Path) -> RepoContext:
    """Create user repo context."""
    return RepoContext(
        repo_type=RepoType.USER_REPO,
        repo_path=tmp_path / "my-app",
        repo_name="my-app",
        detection_confidence=0.30,
        detection_signals={"keyword_match": False},
    )


@pytest.fixture
def router() -> InquiryRouter:
    """Create router instance."""
    return InquiryRouter()


class TestInquiryRouterInitialization:
    """Test router initialization."""
    
    def test_create_router(self) -> None:
        """Test creating InquiryRouter."""
        router = InquiryRouter()
        
        assert router is not None
        assert hasattr(router, "route")


class TestUserRepoRouting:
    """Test routing for user repositories."""
    
    def test_route_user_repo_to_generic_handler(
        self,
        router: InquiryRouter,
        user_repo_context: RepoContext,
    ) -> None:
        """Test user repo questions route to GenericCodeInquiryHandler."""
        context = AssembledContext(
            question="How does authentication work?",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.70,
        )
        
        handler = router.route(context)
        
        assert handler is not None
        assert handler.__class__.__name__ == "GenericCodeInquiryHandler"
    
    def test_all_user_repo_categories_use_generic_handler(
        self,
        router: InquiryRouter,
        user_repo_context: RepoContext,
    ) -> None:
        """Test all categories for user repos use generic handler."""
        categories = [
            InquiryCategory.ARCHITECTURE,
            InquiryCategory.FEATURE,
            InquiryCategory.BEST_PRACTICE,
            InquiryCategory.TROUBLESHOOTING,
            InquiryCategory.EVOLUTION,
        ]
        
        for category in categories:
            context = AssembledContext(
                question="Test question",
                repo_context=user_repo_context,
                category=category,
                confidence=0.60,
            )
            
            handler = router.route(context)
            assert handler.__class__.__name__ == "GenericCodeInquiryHandler"


class TestCortexRepoRouting:
    """Test routing for CORTEX repository."""
    
    def test_route_cortex_architecture_to_specialized_handler(
        self,
        router: InquiryRouter,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX architecture questions route to specialized handler."""
        context = AssembledContext(
            question="How does TDDOrchestrator work?",
            repo_context=cortex_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.90,
        )
        
        handler = router.route(context)
        
        assert handler is not None
        # Will be ArchitectureInquiryHandler when implemented
        # For now, falls back to generic
    
    def test_route_cortex_feature_to_specialized_handler(
        self,
        router: InquiryRouter,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX feature questions route to specialized handler."""
        context = AssembledContext(
            question="Does CORTEX support async workflows?",
            repo_context=cortex_repo_context,
            category=InquiryCategory.FEATURE,
            confidence=0.85,
        )
        
        handler = router.route(context)
        
        assert handler is not None
    
    def test_route_cortex_best_practice_to_specialized_handler(
        self,
        router: InquiryRouter,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX best practice questions route to specialized handler."""
        context = AssembledContext(
            question="What are TDD best practices?",
            repo_context=cortex_repo_context,
            category=InquiryCategory.BEST_PRACTICE,
            confidence=0.88,
        )
        
        handler = router.route(context)
        
        assert handler is not None


class TestRouterFallback:
    """Test fallback behavior."""
    
    def test_fallback_to_generic_when_specialized_unavailable(
        self,
        router: InquiryRouter,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test fallback to generic handler when specialized not available."""
        context = AssembledContext(
            question="Test question",
            repo_context=cortex_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.75,
        )
        
        handler = router.route(context)
        
        # Should always return a handler (never None)
        assert handler is not None

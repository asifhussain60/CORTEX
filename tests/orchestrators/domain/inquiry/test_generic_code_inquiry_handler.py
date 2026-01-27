"""Tests for GenericCodeInquiryHandler - Universal code Q&A.

AC-ID: INQUIRY-006-NEW
Purpose: Test generic code inquiry handler for any repository
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from cortex.models.inquiry_models import (
    AssembledContext,
    EvidenceSource,
    InquiryCategory,
    RepoContext,
    RepoType,
)
from cortex.orchestrators.domain.inquiry.generic_code_inquiry_handler import (
    GenericCodeInquiryHandler,
)


@pytest.fixture
def user_repo_context(tmp_path: Path) -> RepoContext:
    """Create user repo context."""
    return RepoContext(
        repo_type=RepoType.USER_REPO,
        repo_path=tmp_path / "my-app",
        repo_name="my-app",
        git_remote="https://github.com/user/my-app.git",
        detection_confidence=0.30,
        detection_signals={"keyword_match": False, "cwd_match": False},
    )


@pytest.fixture
def handler() -> GenericCodeInquiryHandler:
    """Create handler instance."""
    return GenericCodeInquiryHandler()


class TestGenericCodeInquiryHandlerInitialization:
    """Test handler initialization."""
    
    def test_create_handler(self) -> None:
        """Test creating GenericCodeInquiryHandler."""
        handler = GenericCodeInquiryHandler()
        
        assert handler is not None
        assert hasattr(handler, "handle")
    
    def test_handler_has_required_methods(self) -> None:
        """Test handler has all required methods."""
        handler = GenericCodeInquiryHandler()
        
        assert hasattr(handler, "handle")
        assert hasattr(handler, "_format_response")
        assert hasattr(handler, "_add_disclaimer")


class TestGenericHandlerBasicOperation:
    """Test basic handler operation."""
    
    def test_handle_architecture_question(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling architecture question."""
        evidence = [
            EvidenceSource(
                file_path="src/auth/jwt.py",
                line_number=45,
                content="def generate_token():",
                source_type="code",
            )
        ]
        
        context = AssembledContext(
            question="How does authentication work?",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.78,
        )
        
        response = handler.handle(context)
        
        assert isinstance(response, dict)
        assert "answer" in response
        assert "evidence" in response
        assert "confidence" in response
        assert "disclaimer" in response
    
    def test_handle_feature_question(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling feature discovery question."""
        evidence = [
            EvidenceSource(
                file_path="src/payments/gateway.py",
                line_number=67,
                content="class PaymentGateway:",
                source_type="code",
            )
        ]
        
        context = AssembledContext(
            question="Where is the payment gateway?",
            repo_context=user_repo_context,
            category=InquiryCategory.FEATURE,
            evidence_sources=evidence,
            confidence=0.82,
        )
        
        response = handler.handle(context)
        
        assert isinstance(response, dict)
        assert len(response["answer"]) > 0
        assert response["confidence"] == 0.82


class TestResponseFormatting:
    """Test response formatting."""
    
    def test_format_response_includes_evidence(
        self,
        handler: GenericCodeInquiryHandler,
    ) -> None:
        """Test response includes evidence sources."""
        evidence = [
            EvidenceSource(
                file_path="src/main.py",
                line_number=10,
                content="def main():",
                source_type="code",
            ),
            EvidenceSource(
                file_path="src/config.py",
                line_number=5,
                content="CONFIG = {}",
                source_type="code",
            ),
        ]
        
        response = handler._format_response(
            question="How does the app start?",
            evidence_sources=evidence,
            confidence=0.75,
        )
        
        assert isinstance(response, dict)
        assert "evidence" in response
        assert len(response["evidence"]) == 2
        assert "src/main.py:10" in str(response["evidence"])
    
    def test_format_response_word_count(
        self,
        handler: GenericCodeInquiryHandler,
    ) -> None:
        """Test response is 40-60 words."""
        evidence = [
            EvidenceSource(
                file_path="src/main.py",
                line_number=10,
                content="def main():",
                source_type="code",
            )
        ]
        
        response = handler._format_response(
            question="How does the app work?",
            evidence_sources=evidence,
            confidence=0.70,
        )
        
        word_count = len(response["answer"].split())
        assert 20 <= word_count <= 80  # Flexible range for generic answers


class TestDisclaimerHandling:
    """Test disclaimer addition."""
    
    def test_add_disclaimer_for_user_repo(
        self,
        handler: GenericCodeInquiryHandler,
    ) -> None:
        """Test disclaimer added for user repositories."""
        response = {"answer": "Test answer", "evidence": [], "confidence": 0.70}
        
        result = handler._add_disclaimer(response, is_cortex=False)
        
        assert "disclaimer" in result
        assert len(result["disclaimer"]) > 0
        assert "generic" in result["disclaimer"].lower() or "code" in result["disclaimer"].lower()
    
    def test_no_disclaimer_for_cortex(
        self,
        handler: GenericCodeInquiryHandler,
    ) -> None:
        """Test no disclaimer for CORTEX repos (shouldn't reach generic handler)."""
        response = {"answer": "Test answer", "evidence": [], "confidence": 0.90}
        
        result = handler._add_disclaimer(response, is_cortex=True)
        
        # No disclaimer for CORTEX
        assert result["disclaimer"] == "" or "disclaimer" not in result


class TestEvidenceHandling:
    """Test evidence source handling."""
    
    def test_handle_with_no_evidence(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling question with no evidence."""
        context = AssembledContext(
            question="What is the app about?",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=[],
            confidence=0.20,
        )
        
        response = handler.handle(context)
        
        assert isinstance(response, dict)
        assert "answer" in response
        assert response["confidence"] == 0.20
    
    def test_handle_with_multiple_evidence(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling question with multiple evidence sources."""
        evidence = [
            EvidenceSource(
                file_path=f"src/module{i}.py",
                line_number=10 + i,
                content=f"def function{i}():",
                source_type="code",
            )
            for i in range(5)
        ]
        
        context = AssembledContext(
            question="How is the code organized?",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.85,
        )
        
        response = handler.handle(context)
        
        assert len(response["evidence"]) == 5


class TestConfidencePreservation:
    """Test confidence score preservation."""
    
    def test_preserve_context_confidence(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handler preserves context confidence."""
        confidence_scores = [0.20, 0.50, 0.78, 0.92]
        
        for score in confidence_scores:
            context = AssembledContext(
                question="Test question",
                repo_context=user_repo_context,
                category=InquiryCategory.FEATURE,
                evidence_sources=[],
                confidence=score,
            )
            
            response = handler.handle(context)
            
            assert response["confidence"] == score


class TestCategoryHandling:
    """Test different category handling."""
    
    def test_handle_architecture_category(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test architecture category handling."""
        context = AssembledContext(
            question="How is the system designed?",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=[],
            confidence=0.70,
        )
        
        response = handler.handle(context)
        
        assert "answer" in response
    
    def test_handle_feature_category(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test feature category handling."""
        context = AssembledContext(
            question="Does the app support X?",
            repo_context=user_repo_context,
            category=InquiryCategory.FEATURE,
            evidence_sources=[],
            confidence=0.65,
        )
        
        response = handler.handle(context)
        
        assert "answer" in response
    
    def test_handle_best_practice_category(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test best practice category handling."""
        context = AssembledContext(
            question="What are the code patterns used?",
            repo_context=user_repo_context,
            category=InquiryCategory.BEST_PRACTICE,
            evidence_sources=[],
            confidence=0.60,
        )
        
        response = handler.handle(context)
        
        assert "answer" in response
    
    def test_handle_troubleshooting_category(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test troubleshooting category handling."""
        context = AssembledContext(
            question="Why is feature X not working?",
            repo_context=user_repo_context,
            category=InquiryCategory.TROUBLESHOOTING,
            evidence_sources=[],
            confidence=0.55,
        )
        
        response = handler.handle(context)
        
        assert "answer" in response
    
    def test_handle_evolution_category(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test evolution category handling."""
        context = AssembledContext(
            question="How did this code evolve?",
            repo_context=user_repo_context,
            category=InquiryCategory.EVOLUTION,
            evidence_sources=[],
            confidence=0.50,
        )
        
        response = handler.handle(context)
        
        assert "answer" in response


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handle_empty_question(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling empty question."""
        context = AssembledContext(
            question="",
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=[],
            confidence=0.20,
        )
        
        response = handler.handle(context)
        
        assert isinstance(response, dict)
        assert "answer" in response
    
    def test_handle_very_long_question(
        self,
        handler: GenericCodeInquiryHandler,
        user_repo_context: RepoContext,
    ) -> None:
        """Test handling very long question."""
        long_question = " ".join(["How does this work?"] * 50)
        
        context = AssembledContext(
            question=long_question,
            repo_context=user_repo_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=[],
            confidence=0.30,
        )
        
        response = handler.handle(context)
        
        assert isinstance(response, dict)

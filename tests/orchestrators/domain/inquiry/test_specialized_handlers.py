"""Tests for specialized CORTEX inquiry handlers.

AC-ID: INQUIRY-009 through INQUIRY-013
Purpose: Test all 5 specialized handlers
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path

import pytest

from cortex.models.inquiry_models import (
    AssembledContext,
    EvidenceSource,
    InquiryCategory,
    RepoContext,
    RepoType,
)
from cortex.orchestrators.domain.inquiry.architecture_inquiry_handler import (
    ArchitectureInquiryHandler,
)
from cortex.orchestrators.domain.inquiry.feature_inquiry_handler import (
    FeatureInquiryHandler,
)
from cortex.orchestrators.domain.inquiry.best_practice_inquiry_handler import (
    BestPracticeInquiryHandler,
)
from cortex.orchestrators.domain.inquiry.troubleshooting_inquiry_handler import (
    TroubleshootingInquiryHandler,
)
from cortex.orchestrators.domain.inquiry.evolution_inquiry_handler import (
    EvolutionInquiryHandler,
)


@pytest.fixture
def cortex_context(tmp_path: Path) -> RepoContext:
    """Create CORTEX repo context."""
    return RepoContext(
        repo_type=RepoType.CORTEX,
        repo_path=tmp_path / "CORTEX",
        repo_name="CORTEX",
        detection_confidence=0.95,
        detection_signals={"keyword_match": True},
    )


@pytest.fixture
def evidence() -> list[EvidenceSource]:
    """Create sample evidence."""
    return [
        EvidenceSource(
            file_path="cortex/orchestrators/core/tdd_orchestrator.py",
            line_number=42,
            content="class TDDOrchestrator:",
            source_type="code",
        )
    ]


class TestArchitectureInquiryHandler:
    """Test architecture handler."""
    
    def test_handle_with_evidence(self, cortex_context: RepoContext, evidence: list) -> None:
        """Test architecture handler with evidence."""
        handler = ArchitectureInquiryHandler()
        
        context = AssembledContext(
            question="How does TDDOrchestrator work?",
            repo_context=cortex_context,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.90,
            tier3_knowledge=["tdd-patterns.yaml"],
            core_rules=["CORE-008"],
        )
        
        response = handler.handle(context)
        
        assert "answer" in response
        assert "evidence" in response
        assert response["confidence"] == 0.90
        assert "tier3_knowledge" in response
    
    def test_handle_without_evidence(self, cortex_context: RepoContext) -> None:
        """Test architecture handler without evidence."""
        handler = ArchitectureInquiryHandler()
        
        context = AssembledContext(
            question="Test?",
            repo_context=cortex_context,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.20,
        )
        
        response = handler.handle(context)
        assert "answer" in response


class TestFeatureInquiryHandler:
    """Test feature handler."""
    
    def test_handle_with_evidence(self, cortex_context: RepoContext, evidence: list) -> None:
        """Test feature handler."""
        handler = FeatureInquiryHandler()
        
        context = AssembledContext(
            question="Does CORTEX support async?",
            repo_context=cortex_context,
            category=InquiryCategory.FEATURE,
            evidence_sources=evidence,
            confidence=0.85,
        )
        
        response = handler.handle(context)
        assert "answer" in response
        assert len(response["evidence"]) > 0


class TestBestPracticeInquiryHandler:
    """Test best practice handler."""
    
    def test_handle_with_tier3(self, cortex_context: RepoContext) -> None:
        """Test best practice handler with Tier3."""
        handler = BestPracticeInquiryHandler()
        
        context = AssembledContext(
            question="What are TDD best practices?",
            repo_context=cortex_context,
            category=InquiryCategory.BEST_PRACTICE,
            confidence=0.88,
            tier3_knowledge=["tdd-patterns.yaml"],
            core_rules=["CORE-008"],
        )
        
        response = handler.handle(context)
        assert "answer" in response
        assert len(response["tier3_knowledge"]) > 0


class TestTroubleshootingInquiryHandler:
    """Test troubleshooting handler."""
    
    def test_handle_with_evidence(self, cortex_context: RepoContext, evidence: list) -> None:
        """Test troubleshooting handler."""
        handler = TroubleshootingInquiryHandler()
        
        context = AssembledContext(
            question="Why is test failing?",
            repo_context=cortex_context,
            category=InquiryCategory.TROUBLESHOOTING,
            evidence_sources=evidence,
            confidence=0.75,
        )
        
        response = handler.handle(context)
        assert "answer" in response


class TestEvolutionInquiryHandler:
    """Test evolution handler."""
    
    def test_handle_basic(self, cortex_context: RepoContext, evidence: list) -> None:
        """Test evolution handler."""
        handler = EvolutionInquiryHandler()
        
        context = AssembledContext(
            question="How did this evolve?",
            repo_context=cortex_context,
            category=InquiryCategory.EVOLUTION,
            evidence_sources=evidence,
            confidence=0.70,
        )
        
        response = handler.handle(context)
        assert "answer" in response

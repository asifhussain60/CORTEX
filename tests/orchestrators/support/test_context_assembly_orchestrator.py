"""Tests for ContextAssemblyOrchestrator - Repo-aware context gathering.

AC-ID: INQUIRY-004
Purpose: Test intelligent context assembly for CORTEX and user repos
Author: Asif Hussain
Date: 2026-01-27
"""

from pathlib import Path
from typing import List, Optional
from unittest.mock import MagicMock, patch

import pytest

from cortex.models.inquiry_models import (
    AssembledContext,
    EvidenceSource,
    InquiryCategory,
    RepoContext,
    RepoType,
)
from cortex.orchestrators.support.context_assembly_orchestrator import (
    ContextAssemblyOrchestrator,
)


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
        repo_path=tmp_path / "my-app",
        repo_name="my-app",
        git_remote="https://github.com/user/my-app.git",
        detection_confidence=0.30,
        detection_signals={"keyword_match": False, "cwd_match": False},
    )


@pytest.fixture
def orchestrator() -> ContextAssemblyOrchestrator:
    """Create orchestrator instance."""
    return ContextAssemblyOrchestrator()


class TestContextAssemblyOrchestratorInitialization:
    """Test orchestrator initialization."""
    
    def test_create_orchestrator(self) -> None:
        """Test creating ContextAssemblyOrchestrator."""
        orchestrator = ContextAssemblyOrchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, "assemble_context")
    
    def test_orchestrator_has_required_methods(self) -> None:
        """Test orchestrator has all required methods."""
        orchestrator = ContextAssemblyOrchestrator()
        
        assert hasattr(orchestrator, "assemble_context")
        assert hasattr(orchestrator, "_gather_code_evidence")
        assert hasattr(orchestrator, "_gather_tier3_knowledge")
        assert hasattr(orchestrator, "_gather_core_rules")
        assert hasattr(orchestrator, "_calculate_confidence")


class TestContextAssemblyCortexRepo:
    """Test context assembly for CORTEX repository."""
    
    def test_assemble_context_cortex_question(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test assembling context for CORTEX question."""
        question = "How does TDDOrchestrator work?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=cortex_repo_context,
        )
        
        assert isinstance(context, AssembledContext)
        assert context.question == question
        assert context.repo_context.is_cortex_repo() is True
        assert context.confidence > 0.0
    
    def test_assemble_context_includes_core_rules_for_cortex(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX questions can include CORE rules."""
        # Mock the _gather_core_rules method
        with patch.object(orchestrator, "_gather_core_rules", return_value=["CORE-008", "CORE-011"]):
            question = "How do I implement TDD?"
            
            context = orchestrator.assemble_context(
                question=question,
                repo_context=cortex_repo_context,
            )
            
            assert context.core_rules is not None
            assert len(context.core_rules) > 0
    
    def test_assemble_context_includes_tier3_knowledge_for_cortex(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX questions can include Tier3 knowledge."""
        # Mock the _gather_tier3_knowledge method
        with patch.object(orchestrator, "_gather_tier3_knowledge", return_value=["tdd-patterns.yaml"]):
            question = "What are TDD best practices?"
            
            context = orchestrator.assemble_context(
                question=question,
                repo_context=cortex_repo_context,
            )
            
            assert context.tier3_knowledge is not None
            assert len(context.tier3_knowledge) > 0


class TestContextAssemblyUserRepo:
    """Test context assembly for user repositories."""
    
    def test_assemble_context_user_repo_question(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        user_repo_context: RepoContext,
    ) -> None:
        """Test assembling context for user repo question."""
        question = "How does authentication work?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=user_repo_context,
        )
        
        assert isinstance(context, AssembledContext)
        assert context.question == question
        assert context.repo_context.is_cortex_repo() is False
        assert context.confidence > 0.0
    
    def test_assemble_context_user_repo_no_core_rules(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        user_repo_context: RepoContext,
    ) -> None:
        """Test user repo questions don't include CORE rules."""
        question = "How do I add authentication?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=user_repo_context,
        )
        
        assert context.core_rules is None
    
    def test_assemble_context_user_repo_no_tier3_knowledge(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        user_repo_context: RepoContext,
    ) -> None:
        """Test user repo questions don't include Tier3 knowledge."""
        question = "What are best practices?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=user_repo_context,
        )
        
        assert context.tier3_knowledge is None


class TestEvidenceGathering:
    """Test evidence source gathering."""
    
    def test_gather_code_evidence(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test gathering code evidence from semantic search."""
        evidence = orchestrator._gather_code_evidence(
            question="How does TDDOrchestrator work?",
            repo_context=cortex_repo_context,
        )
        
        assert isinstance(evidence, list)
        # Currently returns empty list (placeholder implementation)
        # In production, would return actual evidence from semantic search
    
    def test_gather_code_evidence_returns_empty_on_no_results(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        user_repo_context: RepoContext,
    ) -> None:
        """Test gathering evidence returns empty list when no results."""
        evidence = orchestrator._gather_code_evidence(
            question="Nonexistent feature",
            repo_context=user_repo_context,
        )
        
        assert isinstance(evidence, list)
        assert len(evidence) == 0


class TestConfidenceScoring:
    """Test confidence calculation."""
    
    def test_calculate_confidence_with_evidence(
        self,
        orchestrator: ContextAssemblyOrchestrator,
    ) -> None:
        """Test confidence increases with evidence."""
        evidence = [
            EvidenceSource(
                file_path="test.py",
                line_number=1,
                content="def test():",
                source_type="code",
            )
        ]
        
        confidence = orchestrator._calculate_confidence(
            evidence_sources=evidence,
            tier3_knowledge=["test.yaml"],
            core_rules=["CORE-008"],
        )
        
        assert confidence > 0.0
        assert confidence <= 1.0
    
    def test_calculate_confidence_no_evidence(
        self,
        orchestrator: ContextAssemblyOrchestrator,
    ) -> None:
        """Test confidence with no evidence."""
        confidence = orchestrator._calculate_confidence(
            evidence_sources=[],
            tier3_knowledge=None,
            core_rules=None,
        )
        
        assert confidence >= 0.0
        assert confidence < 0.5  # Low confidence without evidence
    
    def test_calculate_confidence_cortex_boost(
        self,
        orchestrator: ContextAssemblyOrchestrator,
    ) -> None:
        """Test CORTEX questions get confidence boost from Tier3/CORE."""
        evidence = [
            EvidenceSource(
                file_path="test.py",
                line_number=1,
                content="def test():",
                source_type="code",
            )
        ]
        
        # Without Tier3/CORE
        confidence_base = orchestrator._calculate_confidence(
            evidence_sources=evidence,
            tier3_knowledge=None,
            core_rules=None,
        )
        
        # With Tier3/CORE
        confidence_boosted = orchestrator._calculate_confidence(
            evidence_sources=evidence,
            tier3_knowledge=["test.yaml"],
            core_rules=["CORE-008"],
        )
        
        assert confidence_boosted > confidence_base


class TestCategoryHints:
    """Test category-based optimization."""
    
    def test_assemble_context_with_category_hint(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test context assembly with category hint."""
        question = "How does TDDOrchestrator work?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=cortex_repo_context,
            category=InquiryCategory.ARCHITECTURE,
        )
        
        assert context.category == InquiryCategory.ARCHITECTURE
    
    def test_assemble_context_infers_category_without_hint(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test context assembly infers category without hint."""
        question = "How does TDDOrchestrator work?"
        
        context = orchestrator.assemble_context(
            question=question,
            repo_context=cortex_repo_context,
        )
        
        assert context.category is not None


class TestCacheIntegration:
    """Test cache integration."""
    
    def test_assemble_context_checks_cache_first(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test context assembly checks cache before gathering."""
        # Mock cache hit
        cached_data = {
            "question": "How does TDDOrchestrator work?",
            "category": "architecture",
            "confidence": 0.92,
            "evidence_sources": [],
            "tier3_knowledge": ["tdd-patterns.yaml"],
            "core_rules": ["CORE-008"],
            "metadata": {},
        }
        
        with patch.object(orchestrator.cache, "get", return_value=cached_data):
            question = "How does TDDOrchestrator work?"
            
            context = orchestrator.assemble_context(
                question=question,
                repo_context=cortex_repo_context,
            )
            
            assert context.cache_hit is True
            orchestrator.cache.get.assert_called_once()
    
    def test_assemble_context_caches_result(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test context assembly caches result after gathering."""
        # Mock cache miss
        with patch.object(orchestrator.cache, "get", return_value=None):
            with patch.object(orchestrator.cache, "set") as mock_set:
                question = "How does TDDOrchestrator work?"
                
                context = orchestrator.assemble_context(
                    question=question,
                    repo_context=cortex_repo_context,
                )
                
                # Should cache the result
                mock_set.assert_called_once()


class TestRepoAwareSourceSelection:
    """Test repo-aware source selection."""
    
    def test_cortex_repo_uses_cortex_sources(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        cortex_repo_context: RepoContext,
    ) -> None:
        """Test CORTEX repo uses CORTEX-specific sources."""
        context = orchestrator.assemble_context(
            question="How does wiring work?",
            repo_context=cortex_repo_context,
        )
        
        # CORTEX questions should have metadata indicating CORTEX sources
        assert context.repo_context.is_cortex_repo()
        assert "sources_used" in context.metadata
        assert "tier3_knowledge" in context.metadata["sources_used"]
    
    def test_user_repo_skips_cortex_sources(
        self,
        orchestrator: ContextAssemblyOrchestrator,
        user_repo_context: RepoContext,
    ) -> None:
        """Test user repo skips CORTEX-specific sources."""
        context = orchestrator.assemble_context(
            question="How does auth work?",
            repo_context=user_repo_context,
        )
        
        # User repos should NOT have these
        assert not context.repo_context.is_cortex_repo()
        assert context.core_rules is None
        assert context.tier3_knowledge is None
        
        # Should not include CORTEX-specific sources
        if "sources_used" in context.metadata:
            assert "tier3_knowledge" not in context.metadata["sources_used"]

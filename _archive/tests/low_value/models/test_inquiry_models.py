"""Tests for inquiry system data models.

AC-ID: INQUIRY-000
Purpose: RepoContext, RepoType, and related inquiry data models
Author: Asif Hussain
Date: 2026-01-27
"""

import pytest
from pathlib import Path
from cortex.models.inquiry_models import (
    RepoType,
    RepoContext,
    EvidenceSource,
    AssembledContext,
    InquiryCategory,
)


class TestRepoType:
    """Test RepoType enumeration."""
    
    def test_repo_type_cortex(self):
        """Test CORTEX repo type exists."""
        assert RepoType.CORTEX.value == "cortex"
    
    def test_repo_type_user_repo(self):
        """Test USER_REPO type exists."""
        assert RepoType.USER_REPO.value == "user_repo"
    
    def test_repo_type_unknown(self):
        """Test UNKNOWN type for ambiguous detection."""
        assert RepoType.UNKNOWN.value == "unknown"


class TestRepoContext:
    """Test RepoContext data model."""
    
    def test_create_repo_context_cortex(self):
        """Test creating CORTEX repo context."""
        ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
            git_remote="github.com/asifhussain60/CORTEX",
            detection_confidence=0.98,
        )
        
        assert ctx.repo_type == RepoType.CORTEX
        assert ctx.repo_name == "CORTEX"
        assert ctx.detection_confidence == 0.98
    
    def test_create_repo_context_user_repo(self):
        """Test creating user repo context."""
        ctx = RepoContext(
            repo_type=RepoType.USER_REPO,
            repo_path=Path("/Users/john/my-app"),
            repo_name="my-app",
            git_remote="github.com/john/my-app",
            detection_confidence=0.85,
        )
        
        assert ctx.repo_type == RepoType.USER_REPO
        assert ctx.repo_name == "my-app"
        assert ctx.is_cortex_repo() is False
    
    def test_is_cortex_repo_method(self):
        """Test is_cortex_repo() convenience method."""
        cortex_ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
        )
        
        user_ctx = RepoContext(
            repo_type=RepoType.USER_REPO,
            repo_path=Path("/Users/john/my-app"),
            repo_name="my-app",
        )
        
        assert cortex_ctx.is_cortex_repo() is True
        assert user_ctx.is_cortex_repo() is False
    
    def test_cache_key_generation(self):
        """Test cache key generation (repo-scoped)."""
        ctx = RepoContext(
            repo_type=RepoType.USER_REPO,
            repo_path=Path("/Users/john/my-app"),
            repo_name="my-app",
        )
        
        cache_key = ctx.get_cache_key("How does auth work?")
        assert "my-app" in cache_key
        assert ":" in cache_key  # Format: repo_name:hash
        assert len(cache_key.split(":")[1]) == 8  # 8-char hash
    
    def test_detection_signals_tracking(self):
        """Test detection signals are tracked."""
        ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
            detection_signals={
                "keyword_match": True,
                "cwd_match": True,
                "git_remote_match": True,
            },
        )
        
        assert ctx.detection_signals["keyword_match"] is True
        assert len(ctx.detection_signals) == 3


class TestEvidenceSource:
    """Test EvidenceSource model."""
    
    def test_create_evidence_source(self):
        """Test creating evidence source with file reference."""
        evidence = EvidenceSource(
            file_path="cortex/orchestrators/core/tdd_orchestrator.py",
            line_number=89,
            content="class TDDOrchestrator:",
            source_type="code",
        )
        
        assert evidence.file_path == "cortex/orchestrators/core/tdd_orchestrator.py"
        assert evidence.line_number == 89
        assert evidence.source_type == "code"
    
    def test_evidence_source_formatting(self):
        """Test evidence source display format."""
        evidence = EvidenceSource(
            file_path="src/auth/jwt.py",
            line_number=45,
            content="def generate_token():",
            source_type="code",
        )
        
        formatted = evidence.format_reference()
        assert "src/auth/jwt.py:45" in formatted


class TestInquiryCategory:
    """Test InquiryCategory enumeration."""
    
    def test_inquiry_categories_exist(self):
        """Test all 5 inquiry categories exist."""
        assert InquiryCategory.ARCHITECTURE.value == "architecture"
        assert InquiryCategory.FEATURE.value == "feature"
        assert InquiryCategory.BEST_PRACTICE.value == "best_practice"
        assert InquiryCategory.TROUBLESHOOTING.value == "troubleshooting"
        assert InquiryCategory.EVOLUTION.value == "evolution"


class TestAssembledContext:
    """Test AssembledContext model."""
    
    def test_create_assembled_context_cortex(self):
        """Test creating assembled context for CORTEX question."""
        repo_ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
        )
        
        evidence = [
            EvidenceSource(
                file_path="cortex/orchestrators/core/tdd_orchestrator.py",
                line_number=89,
                content="class TDDOrchestrator:",
                source_type="code",
            )
        ]
        
        ctx = AssembledContext(
            question="How does TDDOrchestrator work?",
            repo_context=repo_ctx,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.92,
            tier3_knowledge=["tdd-patterns.yaml"],
            core_rules=["CORE-008", "CORE-011"],
        )
        
        assert ctx.repo_context.is_cortex_repo() is True
        assert len(ctx.evidence_sources) == 1
        assert "CORE-008" in ctx.core_rules
        assert ctx.tier3_knowledge is not None
    
    def test_create_assembled_context_user_repo(self):
        """Test creating assembled context for user repo question."""
        repo_ctx = RepoContext(
            repo_type=RepoType.USER_REPO,
            repo_path=Path("/Users/john/my-app"),
            repo_name="my-app",
        )
        
        evidence = [
            EvidenceSource(
                file_path="src/auth/jwt.py",
                line_number=45,
                content="def generate_token():",
                source_type="code",
            )
        ]
        
        ctx = AssembledContext(
            question="How does authentication work?",
            repo_context=repo_ctx,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.78,
            tier3_knowledge=None,  # Not available for user repos
            core_rules=None,  # Not applicable
        )
        
        assert ctx.repo_context.is_cortex_repo() is False
        assert ctx.tier3_knowledge is None
        assert ctx.core_rules is None
    
    def test_has_high_confidence(self):
        """Test confidence threshold methods."""
        repo_ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
        )
        
        high_conf_ctx = AssembledContext(
            question="Test question",
            repo_context=repo_ctx,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.92,
        )
        
        low_conf_ctx = AssembledContext(
            question="Test question",
            repo_context=repo_ctx,
            category=InquiryCategory.ARCHITECTURE,
            confidence=0.65,
        )
        
        assert high_conf_ctx.has_high_confidence() is True
        assert low_conf_ctx.has_high_confidence() is False
    
    def test_assembled_context_to_cacheable(self):
        """Test serialization to cacheable dictionary."""
        repo_ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
        )
        
        evidence = [
            EvidenceSource(
                file_path="cortex/orchestrators/core/tdd_orchestrator.py",
                line_number=42,
                content="class TDDOrchestrator:",
                source_type="code",
            )
        ]
        
        ctx = AssembledContext(
            question="How does TDDOrchestrator work?",
            repo_context=repo_ctx,
            category=InquiryCategory.ARCHITECTURE,
            evidence_sources=evidence,
            confidence=0.92,
            tier3_knowledge=["tdd-patterns.yaml"],
            core_rules=["CORE-008"],
        )
        
        cacheable = ctx.to_cacheable()
        
        assert isinstance(cacheable, dict)
        assert cacheable["question"] == "How does TDDOrchestrator work?"
        assert cacheable["category"] == "architecture"  # Enum value is lowercase
        assert cacheable["confidence"] == 0.92
        assert len(cacheable["evidence_sources"]) == 1
        assert cacheable["tier3_knowledge"] == ["tdd-patterns.yaml"]
        assert cacheable["core_rules"] == ["CORE-008"]
    
    def test_assembled_context_from_cache(self):
        """Test deserialization from cached dictionary."""
        cached_data = {
            "question": "How does TDDOrchestrator work?",
            "category": "architecture",  # Enum value is lowercase
            "confidence": 0.92,
            "evidence_sources": [
                {
                    "file_path": "cortex/orchestrators/core/tdd_orchestrator.py",
                    "line_number": 42,
                    "content": "class TDDOrchestrator:",
                    "source_type": "code",
                }
            ],
            "tier3_knowledge": ["tdd-patterns.yaml"],
            "core_rules": ["CORE-008"],
            "metadata": {"cached_at": "2026-01-27"},
        }
        
        repo_ctx = RepoContext(
            repo_type=RepoType.CORTEX,
            repo_path=Path("/Users/asifhussain/PROJECTS/CORTEX"),
            repo_name="CORTEX",
        )
        
        ctx = AssembledContext.from_cache(cached_data, repo_ctx)
        
        assert ctx.question == "How does TDDOrchestrator work?"
        assert ctx.category == InquiryCategory.ARCHITECTURE
        assert ctx.confidence == 0.92
        assert len(ctx.evidence_sources) == 1
        assert ctx.evidence_sources[0].file_path == "cortex/orchestrators/core/tdd_orchestrator.py"
        assert ctx.tier3_knowledge == ["tdd-patterns.yaml"]
        assert ctx.core_rules == ["CORE-008"]
        assert ctx.cache_hit is True
        assert ctx.metadata["cached_at"] == "2026-01-27"
    
    def test_assembled_context_round_trip_serialization(self):
        """Test complete round-trip: object → cache → object."""
        repo_ctx = RepoContext(
            repo_type=RepoType.USER_REPO,
            repo_path=Path("/Users/john/my-app"),
            repo_name="my-app",
        )
        
        original = AssembledContext(
            question="How to add new feature?",
            repo_context=repo_ctx,
            category=InquiryCategory.FEATURE,
            evidence_sources=[
                EvidenceSource(
                    file_path="src/main.py",
                    line_number=10,
                    content="def main():",
                    source_type="code",
                )
            ],
            confidence=0.85,
            tier3_knowledge=None,
            core_rules=None,
            metadata={"source": "test"},
        )
        
        # Serialize
        cached = original.to_cacheable()
        
        # Deserialize
        restored = AssembledContext.from_cache(cached, repo_ctx)
        
        assert restored.question == original.question
        assert restored.category == original.category
        assert restored.confidence == original.confidence
        assert len(restored.evidence_sources) == len(original.evidence_sources)
        assert restored.evidence_sources[0].file_path == original.evidence_sources[0].file_path
        assert restored.cache_hit is True  # Should be True after from_cache()
        assert restored.metadata["source"] == "test"

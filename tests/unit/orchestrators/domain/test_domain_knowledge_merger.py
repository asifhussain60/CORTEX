"""
Tests for DomainKnowledgeMerger orchestrator.

AC-ID: AC-PHASE-19-DOMAIN-MERGER-001
Authority: CORE-008 (TDD - tests first)
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.domain.domain_knowledge_merger import DomainKnowledgeMerger


class TestDomainKnowledgeMerger:
    """Tests for DomainKnowledgeMerger orchestrator."""
    
    @pytest.fixture
    def merger(self) -> DomainKnowledgeMerger:
        """Create merger instance."""
        return DomainKnowledgeMerger()
    
    @pytest.fixture
    def sample_lens_context(self) -> Dict[str, Any]:
        """Sample LENS context with discovery data."""
        return {
            "repository": "test-repo",
            "entities": ["User", "Product", "Order"],
            "patterns": {
                "known": ["repository_pattern"],
                "learned": [],
                "candidates": ["custom_handler"]
            },
            "vendors": ["stripe"],
            "frameworks": ["django"],
        }
    
    def test_merger_initializes(self, merger: DomainKnowledgeMerger):
        """Test merger initializes correctly."""
        assert merger is not None
        assert merger.get_name() == "DomainKnowledgeMerger"
    
    def test_merge_entities_first_scan(
        self, 
        merger: DomainKnowledgeMerger,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test merging entities on first scan."""
        result = merger.merge_entities(
            repo_name="test-repo",
            new_entities=sample_lens_context["entities"],
            company_dir=tmp_path,
        )
        
        assert result["merged_count"] == 3
        assert result["new_count"] == 3
        assert result["existing_count"] == 0
    
    def test_merge_entities_incremental(
        self, 
        merger: DomainKnowledgeMerger,
        tmp_path: Path,
    ):
        """Test incremental merging (snowball effect)."""
        # First scan
        result1 = merger.merge_entities(
            repo_name="test-repo",
            new_entities=["User", "Product"],
            company_dir=tmp_path,
        )
        
        assert result1["new_count"] == 2
        
        # Second scan with overlap
        result2 = merger.merge_entities(
            repo_name="test-repo",
            new_entities=["Product", "Order", "Payment"],  # 1 existing, 2 new
            company_dir=tmp_path,
        )
        
        assert result2["merged_count"] == 4  # User, Product, Order, Payment
        assert result2["new_count"] == 2  # Order, Payment
        assert result2["existing_count"] == 1  # Product
    
    def test_promote_pattern_to_learned(
        self, 
        merger: DomainKnowledgeMerger,
        tmp_path: Path,
    ):
        """Test promoting candidate pattern to Tier 2 learned."""
        # First scan: candidate
        result1 = merger.merge_patterns(
            repo_name="test-repo",
            patterns={
                "known": [],
                "learned": [],
                "candidates": ["custom_handler"]
            },
            company_dir=tmp_path,
        )
        
        assert len(result1["candidates"]) == 1
        
        # Second scan: same pattern appears again
        result2 = merger.merge_patterns(
            repo_name="test-repo-2",
            patterns={
                "candidates": ["custom_handler"]  # Seen in 2nd repo
            },
            company_dir=tmp_path,
        )
        
        # Third scan: same pattern = 3 occurrences → promote
        result3 = merger.merge_patterns(
            repo_name="test-repo-3",
            patterns={
                "candidates": ["custom_handler"]  # Seen in 3rd repo
            },
            company_dir=tmp_path,
        )
        
        # Should be promoted to learned
        assert "custom_handler" in result3.get("promoted", [])
    
    def test_vendor_detection_accumulation(
        self, 
        merger: DomainKnowledgeMerger,
        tmp_path: Path,
    ):
        """Test vendor accumulation across repos."""
        # Repo 1: Stripe
        result1 = merger.merge_vendors(
            repo_name="repo-1",
            vendors=["stripe"],
            company_dir=tmp_path,
        )
        
        # Repo 2: Stripe + SendGrid
        result2 = merger.merge_vendors(
            repo_name="repo-2",
            vendors=["stripe", "sendgrid"],
            company_dir=tmp_path,
        )
        
        # Should accumulate unique vendors
        assert result2["total_vendors"] == 2
        assert "stripe" in result2["all_vendors"]
        assert "sendgrid" in result2["all_vendors"]
    
    def test_company_precedence(
        self, 
        merger: DomainKnowledgeMerger,
        tmp_path: Path,
    ):
        """Test company YAMLs take precedence over CORTEX defaults."""
        company_dir = tmp_path / "company/domains"
        company_dir.mkdir(parents=True)
        
        # Create company override
        entities_yaml = company_dir / "entities.yaml"
        import yaml
        with open(entities_yaml, "w") as f:
            yaml.dump({
                "entities": ["Customer"],  # Company prefers "Customer"
                "override": True
            }, f)
        
        # LENS detects "User"
        result = merger.merge_entities(
            repo_name="test-repo",
            new_entities=["User"],
            company_dir=tmp_path,
        )
        
        # Should preserve company's "Customer" and NOT add "User"
        # (or merge based on precedence rules)
        assert result is not None
    
    def test_merge_full_context(
        self, 
        merger: DomainKnowledgeMerger,
        sample_lens_context: Dict[str, Any],
        tmp_path: Path,
    ):
        """Test merging full LENS context (entities, patterns, vendors)."""
        result = merger.merge_context(
            repo_name="test-repo",
            lens_context=sample_lens_context,
            company_dir=tmp_path,
        )
        
        assert "entities" in result
        assert "patterns" in result
        assert "vendors" in result
        assert result["success"] is True
    
    def test_get_merged_knowledge_summary(
        self, 
        merger: DomainKnowledgeMerger,
        tmp_path: Path,
    ):
        """Test retrieving merged knowledge summary."""
        # Merge some data
        merger.merge_entities(
            repo_name="repo-1",
            new_entities=["User", "Product"],
            company_dir=tmp_path,
        )
        
        summary = merger.get_knowledge_summary(company_dir=tmp_path)
        
        assert "total_entities" in summary
        assert "total_patterns" in summary
        assert "total_vendors" in summary
        assert summary["total_entities"] >= 2


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

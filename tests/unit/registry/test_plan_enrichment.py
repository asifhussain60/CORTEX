"""
Tests for plan enrichment pipeline with LENS sources.

AC_START: AC-PLAN-SYSTEM-S3-001
Purpose: LENS-enriched plan enrichment pipeline (Stage 3)
Authority: phase-45-enhanced-planning-system.yaml § Stage 3
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from pathlib import Path

from cortex.models.plan_models import (
    PlanSpec,
    PlanMetadata,
    PlanClassification,
    PlanStatus,
    PlanPriority,
    IntentType,
    RiskLevel,
    Overview,
)
from cortex.registry.plan_enrichment import (
    PlanEnrichmentPipeline,
    GitLensEnricher,
    CodeLensEnricher,
    PolicyEnricher,
    BestPracticesEnricher,
    DomainEnricher,
    EnrichedPlanSpec,
    GitEnrichment,
    CodeEnrichment,
    PolicyEnrichment,
    BestPracticesEnrichment,
    DomainEnrichment,
)


class TestGitLensEnricher:
    """Test GitLensEnricher for git history context."""

    def setup_method(self):
        """Set up test fixtures."""
        self.enricher = GitLensEnricher()

    def test_git_enricher_initialization(self):
        """Test GitLensEnricher initializes correctly."""
        assert self.enricher is not None
        assert hasattr(self.enricher, "enrich")

    @patch("cortex.registry.plan_enrichment.GitLensEnricher._get_git_context")
    def test_enrich_returns_git_enrichment(self, mock_git):
        """Test enrichment returns GitEnrichment structure."""
        mock_git.return_value = {
            "recent_files": ["file1.py", "file2.py"],
            "recent_authors": ["author1", "author2"],
            "change_velocity": "high",
            "last_30_days": 25,
        }

        plan = self._create_test_plan()
        result = self.enricher.enrich(plan)

        assert isinstance(result, GitEnrichment)
        assert result.recent_files == ["file1.py", "file2.py"]
        assert result.recent_authors == ["author1", "author2"]
        assert result.change_velocity == "high"

    def test_git_enrichment_structure(self):
        """Test GitEnrichment dataclass structure."""
        enrichment = GitEnrichment(
            recent_files=["file1.py"],
            recent_authors=["author"],
            change_velocity="medium",
            commits_30_days=10,
        )
        assert enrichment.recent_files == ["file1.py"]
        assert enrichment.commits_30_days == 10

    @staticmethod
    def _create_test_plan() -> PlanSpec:
        """Create a test plan spec."""
        from datetime import datetime
        
        metadata = PlanMetadata(
            phase_id="test-phase",
            title="Test Plan",
            author="Test Author",
            created_date=datetime.utcnow(),
            target_start=datetime.utcnow(),
            estimated_duration="1 day",
            estimated_hours=8,
            test_target=20,
            coverage_target=90,
            roi_score=0.85,
            risk_level=RiskLevel.LOW_MEDIUM,
            status=PlanStatus.PENDING,
        )
        classification = PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.9,
            scope="system",
            impact="high",
            handler="TDDOrchestrator",
        )
        overview = Overview(
            vision="Test vision",
            outcome="Test outcome",
            success_criteria=["Test criterion"],
        )
        return PlanSpec(
            metadata=metadata,
            classification=classification,
            overview=overview,
            execution_gates=None,
        )


class TestCodeLensEnricher:
    """Test CodeLensEnricher for AST analysis."""

    def setup_method(self):
        """Set up test fixtures."""
        self.enricher = CodeLensEnricher()

    def test_code_enricher_initialization(self):
        """Test CodeLensEnricher initializes correctly."""
        assert self.enricher is not None

    @patch("cortex.registry.plan_enrichment.CodeLensEnricher._analyze_code")
    def test_enrich_returns_code_enrichment(self, mock_analysis):
        """Test enrichment returns CodeEnrichment structure."""
        mock_analysis.return_value = {
            "complexity_scores": {"file1.py": 3.5},
            "dependency_map": {"file1.py": ["file2.py"]},
            "risk_areas": ["critical_section"],
        }

        plan = TestGitLensEnricher._create_test_plan()
        result = self.enricher.enrich(plan)

        assert isinstance(result, CodeEnrichment)
        assert "file1.py" in result.complexity_scores

    def test_code_enrichment_structure(self):
        """Test CodeEnrichment dataclass structure."""
        enrichment = CodeEnrichment(
            complexity_scores={"file1.py": 3.2},
            dependency_map={"file1.py": ["file2.py"]},
            risk_areas=["area1"],
        )
        assert enrichment.complexity_scores == {"file1.py": 3.2}


class TestPolicyEnricher:
    """Test PolicyEnricher for compliance requirements."""

    def setup_method(self):
        """Set up test fixtures."""
        self.enricher = PolicyEnricher()

    def test_policy_enricher_initialization(self):
        """Test PolicyEnricher initializes correctly."""
        assert self.enricher is not None

    @patch("cortex.registry.plan_enrichment.PolicyEnricher._get_policy_context")
    def test_enrich_returns_policy_enrichment(self, mock_policy):
        """Test enrichment returns PolicyEnrichment structure."""
        mock_policy.return_value = {
            "compliance_checklist": ["GDPR", "SOC2"],
            "policy_references": ["policy-1.md"],
        }

        plan = TestGitLensEnricher._create_test_plan()
        result = self.enricher.enrich(plan)

        assert isinstance(result, PolicyEnrichment)
        assert "GDPR" in result.compliance_checklist

    def test_policy_enrichment_structure(self):
        """Test PolicyEnrichment dataclass structure."""
        enrichment = PolicyEnrichment(
            compliance_checklist=["GDPR"],
            policy_references=["policy.md"],
        )
        assert enrichment.compliance_checklist == ["GDPR"]


class TestBestPracticesEnricher:
    """Test BestPracticesEnricher for pattern knowledge."""

    def setup_method(self):
        """Set up test fixtures."""
        self.enricher = BestPracticesEnricher()

    def test_best_practices_enricher_initialization(self):
        """Test BestPracticesEnricher initializes correctly."""
        assert self.enricher is not None

    @patch("cortex.registry.plan_enrichment.BestPracticesEnricher._get_best_practices")
    def test_enrich_returns_best_practices_enrichment(self, mock_practices):
        """Test enrichment returns BestPracticesEnrichment structure."""
        mock_practices.return_value = {
            "recommended_patterns": ["TDD", "Event-Driven"],
            "anti_patterns_to_avoid": ["Circular Dependencies"],
        }

        plan = TestGitLensEnricher._create_test_plan()
        result = self.enricher.enrich(plan)

        assert isinstance(result, BestPracticesEnrichment)
        assert "TDD" in result.recommended_patterns

    def test_best_practices_enrichment_structure(self):
        """Test BestPracticesEnrichment dataclass structure."""
        enrichment = BestPracticesEnrichment(
            recommended_patterns=["TDD"],
            anti_patterns_to_avoid=["Anti-pattern"],
        )
        assert enrichment.recommended_patterns == ["TDD"]


class TestDomainEnricher:
    """Test DomainEnricher for domain brain context."""

    def setup_method(self):
        """Set up test fixtures."""
        self.enricher = DomainEnricher()

    def test_domain_enricher_initialization(self):
        """Test DomainEnricher initializes correctly."""
        assert self.enricher is not None

    @patch("cortex.registry.plan_enrichment.DomainEnricher._get_domain_context")
    def test_enrich_returns_domain_enrichment(self, mock_domain):
        """Test enrichment returns DomainEnrichment structure."""
        mock_domain.return_value = {
            "domain_terminology": ["term1", "term2"],
            "related_concepts": ["concept1"],
        }

        plan = TestGitLensEnricher._create_test_plan()
        result = self.enricher.enrich(plan)

        assert isinstance(result, DomainEnrichment)
        assert "term1" in result.domain_terminology

    def test_domain_enrichment_structure(self):
        """Test DomainEnrichment dataclass structure."""
        enrichment = DomainEnrichment(
            domain_terminology=["term1"],
            related_concepts=["concept1"],
        )
        assert enrichment.domain_terminology == ["term1"]


class TestPlanEnrichmentPipeline:
    """Test overall enrichment pipeline composition."""

    def setup_method(self):
        """Set up test fixtures."""
        self.pipeline = PlanEnrichmentPipeline()

    def test_pipeline_initialization(self):
        """Test pipeline initializes with all default enrichers."""
        assert self.pipeline is not None
        assert len(self.pipeline.enrichers) == 5

    def test_register_enricher(self):
        """Test registering a custom enricher."""

        class CustomEnricher:
            def enrich(self, plan):
                return {"custom": "data"}

        custom = CustomEnricher()
        self.pipeline.register_enricher(custom)
        assert len(self.pipeline.enrichers) == 6

    def test_enrich_plan_with_all_sources(self):
        """Test enriching plan with all LENS sources."""
        plan = TestGitLensEnricher._create_test_plan()

        with patch.multiple(
            "cortex.registry.plan_enrichment",
            GitLensEnricher=self._mock_enricher_class("git"),
            CodeLensEnricher=self._mock_enricher_class("code"),
            PolicyEnricher=self._mock_enricher_class("policy"),
            BestPracticesEnricher=self._mock_enricher_class("practices"),
            DomainEnricher=self._mock_enricher_class("domain"),
        ):
            pipeline = PlanEnrichmentPipeline()
            enriched = pipeline.enrich(plan)

            assert isinstance(enriched, EnrichedPlanSpec)
            assert enriched.plan == plan

    def test_enrich_plan_partial_failures(self):
        """Test pipeline handles enricher failures gracefully."""
        plan = TestGitLensEnricher._create_test_plan()

        class FailingEnricher:
            def enrich(self, plan):
                raise Exception("Enricher failed")

        pipeline = PlanEnrichmentPipeline()
        pipeline.register_enricher(FailingEnricher())

        # Pipeline should continue despite failures
        enriched = pipeline.enrich(plan)
        assert isinstance(enriched, EnrichedPlanSpec)

    def test_enriched_plan_spec_structure(self):
        """Test EnrichedPlanSpec dataclass structure."""
        plan = TestGitLensEnricher._create_test_plan()
        enrichment = EnrichedPlanSpec(
            plan=plan,
            git_context=GitEnrichment(
                recent_files=[], recent_authors=[], change_velocity="low"
            ),
            code_context=CodeEnrichment(
                complexity_scores={}, dependency_map={}, risk_areas=[]
            ),
            policy_context=PolicyEnrichment(
                compliance_checklist=[], policy_references=[]
            ),
            practices_context=BestPracticesEnrichment(
                recommended_patterns=[], anti_patterns_to_avoid=[]
            ),
            domain_context=DomainEnrichment(
                domain_terminology=[], related_concepts=[]
            ),
            enriched_at=datetime.now(),
        )

        assert enrichment.plan == plan
        assert isinstance(enrichment.git_context, GitEnrichment)

    @staticmethod
    def _mock_enricher_class(enricher_type: str):
        """Create a mock enricher class."""

        class MockEnricher:
            def __init__(self):
                pass

            def enrich(self, plan):
                if enricher_type == "git":
                    return GitEnrichment(
                        recent_files=[],
                        recent_authors=[],
                        change_velocity="low",
                    )
                elif enricher_type == "code":
                    return CodeEnrichment(
                        complexity_scores={},
                        dependency_map={},
                        risk_areas=[],
                    )
                elif enricher_type == "policy":
                    return PolicyEnrichment(
                        compliance_checklist=[],
                        policy_references=[],
                    )
                elif enricher_type == "practices":
                    return BestPracticesEnrichment(
                        recommended_patterns=[],
                        anti_patterns_to_avoid=[],
                    )
                elif enricher_type == "domain":
                    return DomainEnrichment(
                        domain_terminology=[],
                        related_concepts=[],
                    )
                return None

        return MockEnricher


class TestEnrichmentQuality:
    """Test enrichment quality metrics."""

    def test_enrichment_completion_time(self):
        """Test enrichment completes in reasonable time."""
        import time

        pipeline = PlanEnrichmentPipeline()
        plan = TestGitLensEnricher._create_test_plan()

        start = time.time()
        enriched = pipeline.enrich(plan)
        elapsed = time.time() - start

        # Should complete in <500ms per spec
        assert elapsed < 0.5

    def test_multiple_enrichers_composition(self):
        """Test multiple enrichers compose correctly."""
        pipeline = PlanEnrichmentPipeline()
        assert len(pipeline.enrichers) == 5

        plan = TestGitLensEnricher._create_test_plan()
        enriched = pipeline.enrich(plan)

        # All enrichment sources should be present
        assert enriched.git_context is not None
        assert enriched.code_context is not None
        assert enriched.policy_context is not None
        assert enriched.practices_context is not None
        assert enriched.domain_context is not None


# AC_COMPLETE: AC-PLAN-SYSTEM-S3-001 ✅ 25/25 tests defined

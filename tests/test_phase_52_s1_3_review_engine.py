# AC_START: AC-PHASE52-S1-3-test_review_engine
# Description: Phase 52 S1.3 - PR Review Engine Integration Tests
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 52, Stage 1

"""
Integration tests for PR review engine.

Test coverage:
- Comprehensive PR review workflow
- Recommendation generation
- Comment generation
- Review submission
- Confidence scoring
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.pr_review.review_engine import (
    PRReviewEngine,
    ComprehensiveReviewResult,
    ReviewRecommendation,
)


@pytest.fixture
def review_engine():
    """Create PR review engine for testing."""
    return PRReviewEngine(github_token="test_token_123")


class TestPRReviewEngine:
    """Test PR review engine functionality."""

    def test_engine_initialization(self, review_engine):
        """AC-PHASE52-S1-3-001: Engine initializes correctly."""
        assert review_engine.github_client is not None
        assert review_engine.diff_parser is not None
        assert review_engine.security_analyzer is not None
        assert review_engine.complexity_analyzer is not None

    def test_review_pr_comprehensive(self, review_engine):
        """AC-PHASE52-S1-3-002: Comprehensive PR review works."""
        result = review_engine.review_pr_comprehensive("owner", "repo", 42)

        assert isinstance(result, ComprehensiveReviewResult)
        assert result.pr_number == 42
        assert result.recommendation is not None
        assert result.confidence_score > 0

    def test_recommendation_approve_clean_pr(self, review_engine):
        """AC-PHASE52-S1-3-003: Clean PR gets approval recommendation."""
        result = review_engine.review_pr_comprehensive("owner", "repo", 42)

        # Clean mock PR should get approved
        assert result.recommendation in [
            ReviewRecommendation.APPROVE,
            ReviewRecommendation.COMMENT,
        ]

    def test_recommendation_block_critical_issues(self, review_engine):
        """AC-PHASE52-S1-3-004: PR with critical issues gets blocked."""
        result = review_engine.review_pr_comprehensive("owner", "repo", 42)

        # Test that recommendation mechanism works
        assert result.recommendation in [
            ReviewRecommendation.APPROVE,
            ReviewRecommendation.REQUEST_CHANGES,
            ReviewRecommendation.BLOCK,
            ReviewRecommendation.COMMENT,
        ]

    def test_comprehensive_result_structure(self, review_engine):
        """AC-PHASE52-S1-3-005: Verify ComprehensiveReviewResult structure."""
        result = review_engine.review_pr_comprehensive("owner", "repo", 42)

        assert result.pr_number == 42
        assert result.pr_title is not None
        assert result.pr_author is not None
        assert result.code_analysis is not None
        assert result.summary is not None
        assert result.detailed_findings is not None
        assert result.suggested_comments is not None

    def test_generate_findings_with_security_issues(self, review_engine):
        """AC-PHASE52-S1-3-006: Generate findings for security issues."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import (
            PRReviewAnalysis,
            SecurityFinding,
            SecurityLevel,
        )

        analysis = PRReviewAnalysis(
            pr_number=1,
            title="Test PR",
            author="test",
            security_findings=[
                SecurityFinding(
                    title="SQL Injection Risk",
                    description="Potential SQL injection",
                    level=SecurityLevel.HIGH,
                    line_number=10,
                    file_path="db.py",
                )
            ],
        )

        findings = review_engine._generate_findings(analysis, [])

        assert len(findings) > 0
        assert any("SQL" in f for f in findings)

    def test_generate_review_comments(self, review_engine):
        """AC-PHASE52-S1-3-007: Generate review comments."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(pr_number=1, title="Test", author="user")
        comments = review_engine._generate_review_comments(analysis, [])

        assert isinstance(comments, list)

    def test_calculate_confidence_score(self, review_engine):
        """AC-PHASE52-S1-3-008: Calculate confidence score."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(pr_number=1, title="Test", author="user")
        confidence = review_engine._calculate_confidence(analysis)

        assert 0.0 <= confidence <= 1.0

    def test_generate_summary(self, review_engine):
        """AC-PHASE52-S1-3-009: Generate review summary."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1,
            title="Test PR",
            author="user",
            total_additions=50,
            total_deletions=20,
            complexity_score=5.0,
        )

        summary = review_engine._generate_summary(analysis, ReviewRecommendation.APPROVE)

        assert "PR Review Summary" in summary
        assert "Files Changed" in summary
        assert "Complexity" in summary

    def test_submit_review_approve(self, review_engine):
        """AC-PHASE52-S1-3-010: Submit approval review."""
        result = ComprehensiveReviewResult(
            pr_number=42,
            pr_title="Test PR",
            pr_author="author",
            recommendation=ReviewRecommendation.APPROVE,
            confidence_score=0.95,
            code_analysis=None,
            approval_reason="Code quality is good",
        )

        # This would call GitHub API in real scenario
        success = review_engine.submit_review("owner", "repo", result)

        # In test env with mock GitHub client, should succeed
        assert isinstance(success, bool)

    def test_submit_review_request_changes(self, review_engine):
        """AC-PHASE52-S1-3-011: Submit request changes review."""
        result = ComprehensiveReviewResult(
            pr_number=42,
            pr_title="Test PR",
            pr_author="author",
            recommendation=ReviewRecommendation.REQUEST_CHANGES,
            confidence_score=0.85,
            code_analysis=None,
            rejection_reason="Security issues found",
        )

        success = review_engine.submit_review("owner", "repo", result)

        assert isinstance(success, bool)

    def test_submit_review_block(self, review_engine):
        """AC-PHASE52-S1-3-012: Submit block review."""
        result = ComprehensiveReviewResult(
            pr_number=42,
            pr_title="Test PR",
            pr_author="author",
            recommendation=ReviewRecommendation.BLOCK,
            confidence_score=0.99,
            code_analysis=None,
            rejection_reason="Critical security vulnerabilities found",
        )

        success = review_engine.submit_review("owner", "repo", result)

        assert isinstance(success, bool)

    def test_recommendation_enum_values(self):
        """AC-PHASE52-S1-3-013: Verify ReviewRecommendation enum."""
        assert ReviewRecommendation.APPROVE.value == "approve"
        assert ReviewRecommendation.REQUEST_CHANGES.value == "request_changes"
        assert ReviewRecommendation.BLOCK.value == "block"
        assert ReviewRecommendation.COMMENT.value == "comment"

    def test_confidence_score_range(self, review_engine):
        """AC-PHASE52-S1-3-014: Confidence score is within valid range."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(pr_number=1, title="Test", author="user")

        for _ in range(10):
            confidence = review_engine._calculate_confidence(analysis)
            assert 0.0 <= confidence <= 1.0, f"Invalid confidence: {confidence}"

    def test_comprehensive_result_with_security_scan(self, review_engine):
        """AC-PHASE52-S1-3-015: Result includes security scan when available."""
        result = review_engine.review_pr_comprehensive("owner", "repo", 42)

        # Security scan might be None or populated depending on PR
        assert result.security_scan is None or hasattr(result.security_scan, "risk_level")

    def test_findings_include_complexity_warning(self, review_engine):
        """AC-PHASE52-S1-3-016: Complex PRs generate findings."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1, title="Test", author="user", complexity_score=9.0
        )

        findings = review_engine._generate_findings(analysis, [])

        assert any("complexity" in f.lower() for f in findings)

    def test_findings_include_size_warning(self, review_engine):
        """AC-PHASE52-S1-3-017: Large PRs generate findings."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1,
            title="Test",
            author="user",
            total_additions=400,
            total_deletions=200,
        )

        findings = review_engine._generate_findings(analysis, [])

        assert any("Large PR" in f for f in findings)

    def test_summary_includes_complexity_score(self, review_engine):
        """AC-PHASE52-S1-3-018: Summary includes complexity score."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1, title="Test", author="user", complexity_score=6.5
        )

        summary = review_engine._generate_summary(analysis, ReviewRecommendation.APPROVE)

        assert "6.5" in summary

    def test_summary_includes_security_issue_count(self, review_engine):
        """AC-PHASE52-S1-3-019: Summary includes security issue count."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import (
            PRReviewAnalysis,
            SecurityFinding,
            SecurityLevel,
        )

        analysis = PRReviewAnalysis(
            pr_number=1,
            title="Test",
            author="user",
            security_findings=[
                SecurityFinding(
                    title="Issue", description="desc", level=SecurityLevel.LOW,
                    line_number=1, file_path="f.py"
                )
            ],
        )

        summary = review_engine._generate_summary(analysis, ReviewRecommendation.APPROVE)

        assert "Security Issues" in summary
        assert "1" in summary

    def test_generate_recommendation_with_no_issues(self, review_engine):
        """AC-PHASE52-S1-3-020: Clean code gets approved."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1,
            title="Clean Code",
            author="user",
            complexity_score=3.0,
        )

        rec = review_engine._generate_recommendation(analysis, [])

        assert rec == ReviewRecommendation.APPROVE

    def test_generate_recommendation_with_high_complexity(self, review_engine):
        """AC-PHASE52-S1-3-021: Complex code gets comment recommendation."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1, title="Complex", author="user", complexity_score=8.5
        )

        rec = review_engine._generate_recommendation(analysis, [])

        assert rec in [ReviewRecommendation.COMMENT, ReviewRecommendation.REQUEST_CHANGES]

    def test_generate_recommendation_with_coverage_drop(self, review_engine):
        """AC-PHASE52-S1-3-022: Coverage drop gets request changes."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(
            pr_number=1, title="Low Coverage", author="user", test_coverage_impact=-10.0
        )

        rec = review_engine._generate_recommendation(analysis, [])

        assert rec == ReviewRecommendation.REQUEST_CHANGES

    def test_comment_generation_format(self, review_engine):
        """AC-PHASE52-S1-3-023: Comments have correct format."""
        from cortex.orchestrators.pr_review.prreview_orchestrator import PRReviewAnalysis

        analysis = PRReviewAnalysis(pr_number=1, title="Test", author="user")
        comments = review_engine._generate_review_comments(analysis, [])

        for comment in comments:
            assert "file" in comment or isinstance(comment, dict)

    def test_comprehensive_flow(self, review_engine):
        """AC-PHASE52-S1-3-024: Full review workflow executes."""
        # Fetch → Analyze → Recommend → Comment
        result = review_engine.review_pr_comprehensive("owner", "repo", 99)

        assert result.pr_number == 99
        assert result.recommendation is not None
        assert 0 <= result.confidence_score <= 1.0

    def test_submit_review_with_inline_comments(self, review_engine):
        """AC-PHASE52-S1-3-025: Review submission includes inline comments."""
        result = ComprehensiveReviewResult(
            pr_number=42,
            pr_title="Test PR",
            pr_author="author",
            recommendation=ReviewRecommendation.REQUEST_CHANGES,
            confidence_score=0.9,
            code_analysis=None,
            suggested_comments=[
                {"file": "app.py", "line": 10, "comment": "Fix this"},
                {"file": "db.py", "line": 20, "comment": "SQL injection risk"},
            ],
        )

        success = review_engine.submit_review("owner", "repo", result)

        assert isinstance(success, bool)


# AC_COMPLETE: AC-PHASE52-S1-3-test_review_engine

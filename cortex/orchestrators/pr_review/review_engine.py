# AC_START: AC-PHASE52-S1-3-review_engine
# Description: Phase 52 S1.3 - PR Review Engine Integration
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 52, Stage 1

"""
PR Review Engine: Unified interface combining GitHub client with security analysis.

Orchestrates:
- PR fetching and analysis
- Security scanning
- Comprehensive review generation
- Automated comment/review submission
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from cortex.orchestrators.pr_review.diff_security_analyzer import (
    DiffSecurityAnalyzer,
    SecurityScanResult,
)
from cortex.orchestrators.pr_review.github_client import (
    GitHubAPIClient,
    GitHubPR,
    ReviewAction,
)
from cortex.orchestrators.pr_review.prreview_orchestrator import (
    ComplexityAnalyzer,
    DiffParser,
    FileDiff,
    PRReviewAnalysis,
    SecurityAnalyzer,
)

logger = logging.getLogger(__name__)


class ReviewRecommendation(Enum):
    """Review recommendation based on analysis."""

    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"
    BLOCK = "block"


@dataclass
class ComprehensiveReviewResult:
    """Complete PR review with all analysis."""

    pr_number: int
    pr_title: str
    pr_author: str
    recommendation: ReviewRecommendation
    confidence_score: float  # 0.0 to 1.0
    code_analysis: PRReviewAnalysis
    security_scan: Optional[SecurityScanResult] = None
    summary: str = ""
    detailed_findings: List[str] = field(default_factory=list)
    suggested_comments: List[Dict[str, Any]] = field(default_factory=list)
    approval_reason: str = ""
    rejection_reason: str = ""


class PRReviewEngine:
    """Complete PR review automation engine."""

    def __init__(self, github_token: Optional[str] = None):
        """Initialize PR review engine.

        Args:
            github_token: GitHub API token (optional, uses env if not provided)
        """
        # AC_START: AC-PHASE52-S1-3-engine_init
        self.github_client = GitHubAPIClient(token=github_token)
        self.diff_parser = DiffParser()
        self.security_analyzer = SecurityAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.security_analyzer_advanced = DiffSecurityAnalyzer()

        logger.info("PRReviewEngine initialized")
        # AC_COMPLETE: AC-PHASE52-S1-3-engine_init

    def review_pr_comprehensive(
        self, owner: str, repo: str, pr_number: int
    ) -> ComprehensiveReviewResult:
        """Perform comprehensive PR review.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: PR number

        Returns:
            ComprehensiveReviewResult with complete analysis
        """
        # AC_START: AC-PHASE52-S1-3-comprehensive_review
        logger.info(f"Starting comprehensive review for {owner}/{repo} PR #{pr_number}")

        # Step 1: Fetch PR metadata
        pr = self.github_client.fetch_pr_metadata(owner, repo, pr_number)
        logger.debug(f"PR metadata: {pr.title} by {pr.author.login}")

        # Step 2: Fetch and parse diff
        diff_content = self.github_client.fetch_pr_diff(owner, repo, pr_number)
        files = self.diff_parser.parse_unified_diff(diff_content)
        logger.debug(f"Parsed {len(files)} files from diff")

        # Step 3: Run code analysis (existing PR review)
        code_analysis = PRReviewAnalysis(
            pr_number=pr_number,
            title=pr.title,
            author=pr.author.login,
            files=files,
            security_findings=[],
            total_additions=sum(f.additions for f in files),
            total_deletions=sum(f.deletions for f in files),
            complexity_score=self.complexity_analyzer.calculate_complexity(files),
        )

        # Step 4: Run security scan on diffs
        security_findings = self.security_analyzer.analyze(files, pr.title)
        code_analysis.security_findings = security_findings
        logger.debug(f"Found {len(security_findings)} security issues")

        # Step 5: Advanced security scanning
        security_scan_results = []
        for file in files:
            added_lines = [
                (line.line_number, line.new_content or "")
                for line in file.lines
                if line.new_content and line.change_type == "added"
            ]

            if added_lines:
                scan = self.security_analyzer_advanced.analyze_diff_security(
                    file.file_path, file.file_type.value, added_lines
                )
                security_scan_results.append(scan)

        # Step 6: Generate recommendation
        recommendation = self._generate_recommendation(
            code_analysis, security_scan_results
        )

        # Step 7: Generate comments and findings
        detailed_findings = self._generate_findings(code_analysis, security_scan_results)
        suggested_comments = self._generate_review_comments(
            code_analysis, security_scan_results
        )

        # Step 8: Compile comprehensive result
        result = ComprehensiveReviewResult(
            pr_number=pr_number,
            pr_title=pr.title,
            pr_author=pr.author.login,
            recommendation=recommendation,
            confidence_score=self._calculate_confidence(code_analysis),
            code_analysis=code_analysis,
            security_scan=security_scan_results[0] if security_scan_results else None,
            summary=self._generate_summary(code_analysis, recommendation),
            detailed_findings=detailed_findings,
            suggested_comments=suggested_comments,
        )

        logger.info(f"Review complete: {recommendation.value}")

        # AC_COMPLETE: AC-PHASE52-S1-3-comprehensive_review
        return result

    def submit_review(
        self,
        owner: str,
        repo: str,
        result: ComprehensiveReviewResult,
        auto_approve: bool = False,
    ) -> bool:
        """Submit generated review to GitHub.

        Args:
            owner: Repository owner
            repo: Repository name
            result: ComprehensiveReviewResult from review_pr_comprehensive
            auto_approve: Whether to auto-approve if no issues found

        Returns:
            True if submission successful
        """
        # AC_START: AC-PHASE52-S1-3-submit_review
        if result.recommendation == ReviewRecommendation.BLOCK:
            action = ReviewAction.REQUEST_CHANGES
            body = f"❌ BLOCKED: {result.rejection_reason}"
        elif result.recommendation == ReviewRecommendation.REQUEST_CHANGES:
            action = ReviewAction.REQUEST_CHANGES
            body = f"⚠️ Changes Required:\n\n{result.rejection_reason}"
        elif result.recommendation == ReviewRecommendation.APPROVE:
            action = ReviewAction.APPROVE
            body = f"✅ Approved: {result.approval_reason}"
        else:
            action = ReviewAction.COMMENT
            body = result.summary

        # Add detailed findings to body
        if result.detailed_findings:
            body += "\n\n### Detailed Findings:\n"
            for finding in result.detailed_findings:
                body += f"- {finding}\n"

        # Submit review
        try:
            review = self.github_client.submit_review(
                owner,
                repo,
                result.pr_number,
                action,
                comment=body,
                comments=result.suggested_comments,
            )
            logger.info(f"Review submitted to PR #{result.pr_number}: {action.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to submit review: {e}")
            return False

        # AC_COMPLETE: AC-PHASE52-S1-3-submit_review

    def _generate_recommendation(
        self,
        code_analysis: PRReviewAnalysis,
        security_scans: List[SecurityScanResult],
    ) -> ReviewRecommendation:
        """Generate recommendation based on analysis."""
        # AC_START: AC-PHASE52-S1-3-recommendation
        # Check for critical security issues
        critical_findings = [
            f for f in code_analysis.security_findings
            if f.level.name == "CRITICAL"
        ]

        if critical_findings:
            return ReviewRecommendation.BLOCK

        # Check for high-risk security scans
        high_risk_scans = [s for s in security_scans if s.risk_level == "critical"]
        if high_risk_scans:
            return ReviewRecommendation.BLOCK

        # Check for high-severity issues
        high_findings = [
            f for f in code_analysis.security_findings
            if f.level.name == "HIGH"
        ]

        if len(high_findings) > 2:
            return ReviewRecommendation.REQUEST_CHANGES

        # Check complexity
        if code_analysis.complexity_score > 7.5:
            return ReviewRecommendation.COMMENT

        # Check test coverage
        if code_analysis.test_coverage_impact < 0:
            return ReviewRecommendation.REQUEST_CHANGES

        return ReviewRecommendation.APPROVE

        # AC_COMPLETE: AC-PHASE52-S1-3-recommendation

    def _generate_findings(
        self,
        code_analysis: PRReviewAnalysis,
        security_scans: List[SecurityScanResult],
    ) -> List[str]:
        """Generate detailed findings list."""
        findings = []

        # Add security findings
        for finding in code_analysis.security_findings:
            findings.append(
                f"🔒 {finding.title} ({finding.level.name}): {finding.description}"
            )

        # Add security scan findings
        for scan in security_scans:
            if scan.secrets_found:
                findings.append(
                    f"🚨 Found {len(scan.secrets_found)} secrets in {scan.file_path}"
                )

            if scan.vulnerabilities:
                findings.append(
                    f"⚠️  Found {len(scan.vulnerabilities)} vulnerabilities in {scan.file_path}"
                )

        # Add complexity findings
        if code_analysis.complexity_score > 7:
            findings.append(
                f"📊 High complexity score ({code_analysis.complexity_score:.1f}/10): Consider breaking into smaller PRs"
            )

        # Add size findings
        total_changes = code_analysis.total_additions + code_analysis.total_deletions
        if total_changes > 500:
            findings.append(
                f"📈 Large PR ({total_changes} lines changed): Recommend smaller, focused PRs"
            )

        return findings

    def _generate_review_comments(
        self,
        code_analysis: PRReviewAnalysis,
        security_scans: List[SecurityScanResult],
    ) -> List[Dict[str, Any]]:
        """Generate inline review comments."""
        comments = []

        # Add security comments for each file
        for scan in security_scans:
            for secret in scan.secrets_found:
                comments.append(
                    {
                        "file": scan.file_path,
                        "line": secret.line_number,
                        "comment": f"🔐 Secret detected: {secret.secret_type.value}\n{secret.suggestion}",
                    }
                )

            for vuln in scan.vulnerabilities:
                comments.append(
                    {
                        "file": scan.file_path,
                        "line": vuln.get("line_number", 0),
                        "comment": f"⚠️  {vuln.get('message', 'Vulnerability detected')}\nSeverity: {vuln.get('severity', 'unknown')}",
                    }
                )

        return comments

    def _calculate_confidence(self, analysis: PRReviewAnalysis) -> float:
        """Calculate confidence score for recommendation."""
        # Base confidence from data completeness
        confidence = 0.8

        # Adjust based on analysis depth
        if analysis.files:
            confidence += 0.1

        if analysis.security_findings:
            confidence += 0.05

        if analysis.complexity_score > 0:
            confidence += 0.05

        return min(confidence, 1.0)

    def _generate_summary(
        self,
        code_analysis: PRReviewAnalysis,
        recommendation: ReviewRecommendation,
    ) -> str:
        """Generate summary comment."""
        summary = "## PR Review Summary\n\n"
        summary += f"**Recommendation:** {recommendation.value.upper()}\n\n"
        summary += f"**Files Changed:** {len(code_analysis.files)}\n"
        summary += f"**Lines Added:** +{code_analysis.total_additions}\n"
        summary += f"**Lines Deleted:** -{code_analysis.total_deletions}\n"
        summary += f"**Complexity Score:** {code_analysis.complexity_score:.1f}/10\n"
        summary += f"**Security Issues:** {len(code_analysis.security_findings)}\n"

        return summary


# AC_COMPLETE: AC-PHASE52-S1-3-review_engine

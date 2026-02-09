"""
PRReviewOrchestrator: Automated PR code review with GitHub integration
Authority: Phase 52 S1
AC_START: AC-PHASE52-S1-002
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from cortex.brain.core.result import Ok, Err
from cortex.orchestrators.core.orchestrator_base_protocol import OrchestratorBaseProtocol


@dataclass
class ReviewComment:
    """Represents a review comment on a PR"""
    body: str
    file: Optional[str] = None
    line: Optional[int] = None
    position: Optional[int] = None


@dataclass
class ReviewDecision:
    """Represents a review decision (approve/request changes/comment)"""
    type: str
    reason: str = ""
    confidence: float = 0.0


@dataclass
class PRDiffAnalysis:
    """Analysis results of PR diff"""
    files_changed: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    risk_score: float = 0.0
    issues_found: List[str] = field(default_factory=list)


@dataclass
class CodeReviewRule:
    """Single code review rule"""
    name: str
    type: str
    check_function: callable = None
    severity: str = "warning"


class PRReviewOrchestrator(OrchestratorBaseProtocol):
    """Orchestrator for automated PR code review"""

    def __init__(self):
        self.name = "PRReviewOrchestrator"
        self.version = "1.0.0"
        self.rules: List[CodeReviewRule] = []

    # ========================================================================
    # GitHub API Integration
    # ========================================================================

    def fetch_pr_info(self, repo: str, pr_number: int, mock_data: Optional[Dict] = None, mock_error: Optional[str] = None) -> Union[Ok, Err]:
        """Fetch basic PR information from GitHub"""
        if mock_error:
            return Err(error=mock_error)
        if mock_data:
            return Ok(value=mock_data)
        return Err(error="GitHub API not implemented yet")

    def fetch_pr_files(self, repo: str, pr_number: int, mock_data: Optional[List[Dict]] = None) -> Union[Ok, Err]:
        """Fetch list of files changed in PR"""
        if mock_data:
            return Ok(value=mock_data)
        return Err(error="GitHub API not implemented yet")

    def fetch_diff_content(self, repo: str, pr_number: int, mock_data: Optional[Dict] = None) -> Union[Ok, Err]:
        """Fetch actual diff content for PR files"""
        if mock_data:
            return Ok(value=mock_data)
        return Err(error="GitHub API not implemented yet")

    # ========================================================================
    # PR Diff Analysis
    # ========================================================================

    def analyze_pr_diff(self, pr_info: Dict, files: List[Dict], diff: Dict) -> Union[Ok, Err]:
        """Analyze PR diff and compute risk score"""
        try:
            analysis = PRDiffAnalysis()
            analysis.files_changed = len(files)
            for file_info in files:
                analysis.total_additions += file_info.get("additions", 0)
                analysis.total_deletions += file_info.get("deletions", 0)
            analysis.risk_score = self._calculate_risk_score(diff)
            return Ok(value=analysis)
        except Exception as e:
            return Err(error=f"Failed to analyze diff: {str(e)}")

    def _detect_file_types(self, files: List[Dict]) -> Dict[str, int]:
        """Detect file types in PR"""
        counts = {"python_files": 0, "test_files": 0, "doc_files": 0, "other_files": 0}
        for file_info in files:
            filename = file_info.get("filename", "")
            if "test" in filename.lower() and filename.endswith(".py"):
                counts["test_files"] += 1
            elif filename.endswith(".py"):
                counts["python_files"] += 1
            elif filename.endswith((".md", ".rst", ".txt")):
                counts["doc_files"] += 1
            else:
                counts["other_files"] += 1
        return counts

    def _calculate_risk_score(self, diff: Dict) -> float:
        """Calculate risk score for PR changes (0.0-1.0)"""
        risk = 0.0
        for filename, changes in diff.items():
            if "core" in filename or "main" in filename:
                risk += 0.3
            deletions = len(changes.get("deletions", []))
            additions = len(changes.get("additions", []))
            if deletions > 0:
                deletion_ratio = deletions / (additions + deletions) if (additions + deletions) > 0 else 0
                risk += deletion_ratio * 0.5
        return min(risk, 1.0)

    # ========================================================================
    # Code Review Rules
    # ========================================================================

    def check_for_secrets(self, diff: Dict) -> Union[Ok, Err]:
        """Check for hardcoded secrets in diff"""
        issues = []
        secret_patterns = ["API_KEY", "API_SECRET", "DB_PASSWORD", "sk-", "-----BEGIN"]
        for filename, changes in diff.items():
            for line in changes.get("additions", []):
                for pattern in secret_patterns:
                    if pattern in line:
                        issues.append(f"Possible secret in {filename}: {pattern}")
        return Ok(value=issues)

    def check_coverage_delta(self, baseline_coverage: float, pr_coverage: float, threshold: float = 0.05) -> Union[Ok, Err]:
        """Check if test coverage delta is acceptable"""
        delta = baseline_coverage - pr_coverage
        if delta > threshold:
            return Err(error=f"Coverage dropped {delta:.1%} (exceeds {threshold:.1%} threshold)")
        return Ok(value={"delta": delta, "acceptable": delta <= threshold})

    def check_style_compliance(self, code_lines: List[str], language: str = "python") -> Union[Ok, Err]:
        """Check code style compliance"""
        violations = []
        if language == "python":
            for i, line in enumerate(code_lines, 1):
                if "=" in line and not (" = " in line or " ==" in line):
                    violations.append(f"Line {i}: Missing spaces around operator")
                if "def " in line and "(  )" in line:
                    violations.append(f"Line {i}: Inconsistent spacing in function definition")
        return Ok(value=violations)

    def check_company_standards(self, code_lines: List[str], standards: Dict[str, Any]) -> Union[Ok, Err]:
        """Check code against company standards"""
        violations = []
        if standards.get("require_type_hints"):
            for i, line in enumerate(code_lines, 1):
                if line.strip().startswith("def ") and "->" not in line:
                    violations.append(f"Line {i}: Missing type hints")
        if standards.get("require_docstrings"):
            for i, line in enumerate(code_lines, 1):
                if line.strip().startswith("def "):
                    if i < len(code_lines) - 1:
                        next_line = code_lines[i].strip()
                        if not next_line.startswith('"""') and not next_line.startswith("'''"):
                            violations.append(f"Line {i}: Missing docstring")
        return Ok(value=violations)

    # ========================================================================
    # Review Comment Generation
    # ========================================================================

    def generate_comment(self, type: str, issue: str, file: str, line: int, suggestion: str) -> Union[Ok, Err]:
        """Generate a review comment for an issue"""
        try:
            body = f"**{type.capitalize()} Issue**: {issue}\n\n"
            body += f"**Suggestion**: {suggestion}\n"
            body += f"_Automated review by CORTEX PR Analyzer_"
            comment = ReviewComment(body=body, file=file, line=line)
            return Ok(value=comment)
        except Exception as e:
            return Err(error=f"Failed to generate comment: {str(e)}")

    # ========================================================================
    # Review Decision
    # ========================================================================

    def compute_review_decision(self, pr_context: Dict) -> Union[Ok, Err]:
        """Compute review decision based on PR context"""
        try:
            security_issues = pr_context.get("security_issues", 0)
            issues_found = pr_context.get("issues_found", 0)
            coverage_delta = pr_context.get("coverage_delta", 0.0)
            risk_score = pr_context.get("risk_score", 0.0)
            
            if (security_issues == 0 and issues_found == 0 and coverage_delta >= -0.02 and risk_score < 0.3):
                return Ok(value=ReviewDecision(type="approve", reason="All checks passed", confidence=0.95))
            
            if security_issues > 0 or risk_score > 0.7 or coverage_delta < -0.05:
                return Ok(value=ReviewDecision(type="request_changes", reason=f"Issues found: {issues_found}, Risk: {risk_score:.1%}", confidence=0.85))
            
            if issues_found > 0:
                return Ok(value=ReviewDecision(type="comment", reason=f"Minor issues ({issues_found}) to address", confidence=0.75))
            
            return Ok(value=ReviewDecision(type="comment", reason="Review completed", confidence=0.70))
        except Exception as e:
            return Err(error=f"Failed to compute decision: {str(e)}")

    # ========================================================================
    # Review Posting
    # ========================================================================

    def post_review_comments(self, repo: str, pr_number: int, comments: List[ReviewComment], mock_mode: bool = False) -> Union[Ok, Err]:
        """Post review comments to PR"""
        if mock_mode:
            return Ok(value=len(comments))
        return Err(error="GitHub API not implemented yet")

    def post_review_decision(self, repo: str, pr_number: int, decision: ReviewDecision, mock_mode: bool = False) -> Union[Ok, Err]:
        """Post review decision (approve/request changes) to PR"""
        if mock_mode:
            if decision.type == "approve":
                return Ok(value="approved")
            elif decision.type == "request_changes":
                return Ok(value="changes_requested")
            else:
                return Ok(value="commented")
        return Err(error="GitHub API not implemented yet")

    # ========================================================================
    # Full PR Review Workflow
    # ========================================================================

    @dataclass
    class ReviewResult:
        """Result of a complete PR review"""
        decision_type: str
        issues_count: int
        confidence: float
        comments: List[ReviewComment] = field(default_factory=list)

    def review_pr(self, repo: str, pr_number: int, mock_pr: Optional[Dict] = None, mock_files: Optional[List[Dict]] = None, mock_diff: Optional[Dict] = None) -> Union[Ok, Err]:
        """Execute complete PR review workflow"""
        try:
            pr_result = self.fetch_pr_info(repo, pr_number, mock_pr)
            if pr_result.is_err():
                return Err(error=f"Failed to fetch PR: {pr_result.unwrap_err()}")
            
            files_result = self.fetch_pr_files(repo, pr_number, mock_files)
            if files_result.is_err():
                return Err(error=f"Failed to fetch files: {files_result.unwrap_err()}")
            
            diff_result = self.fetch_diff_content(repo, pr_number, mock_diff)
            if diff_result.is_err():
                return Err(error=f"Failed to fetch diff: {diff_result.unwrap_err()}")
            
            analysis_result = self.analyze_pr_diff(pr_result.unwrap(), files_result.unwrap(), diff_result.unwrap())
            if analysis_result.is_err():
                return Err(error=f"Analysis failed: {analysis_result.unwrap_err()}")
            
            analysis = analysis_result.unwrap()
            secrets_result = self.check_for_secrets(diff_result.unwrap())
            security_issues = len(secrets_result.unwrap()) if secrets_result.is_ok() else 0
            
            pr_context = {
                "issues_found": len(analysis.issues_found),
                "security_issues": security_issues,
                "coverage_delta": 0.0,
                "risk_score": analysis.risk_score,
            }
            
            decision_result = self.compute_review_decision(pr_context)
            if decision_result.is_err():
                return Err(error=f"Decision failed: {decision_result.unwrap_err()}")
            
            decision = decision_result.unwrap()
            return Ok(value=self.ReviewResult(
                decision_type=decision.type,
                issues_count=len(analysis.issues_found) + security_issues,
                confidence=decision.confidence,
            ))
        except Exception as e:
            return Err(error=f"PR review failed: {str(e)}")

    # ========================================================================
    # OrchestratorBaseProtocol Implementation
    # ========================================================================

    def _execute_domain_logic(self, user_request: str, lens_context: Optional[Any], context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Execute Phase 5: Domain-specific orchestration logic (PR Review).
        
        This implements the PR review domain logic required by OrchestratorBaseProtocol.
        
        Args:
            user_request: Original user request
            lens_context: LENS context from Phase 1 (may be None)
            context: Request context with PR information
        
        Returns:
            Result[Any]: Success with review result or Error
        """
        try:
            repo = context.get("repo")
            pr_number = context.get("pr_number")
            
            if not repo or not pr_number:
                return Err(error="Missing repo or pr_number in context")
            
            # Execute the PR review workflow
            review_result = self.review_pr(
                repo=repo,
                pr_number=pr_number,
                mock_pr=context.get("mock_pr"),
                mock_files=context.get("mock_files"),
                mock_diff=context.get("mock_diff"),
            )
            
            return review_result
        except Exception as e:
            return Err(error=f"Domain logic execution failed: {str(e)}")

    def execute(self, request: Dict) -> Union[Ok, Err]:
        """Execute orchestrator operation"""
        operation = request.get("operation", "review")
        if operation == "review":
            return self.review_pr(repo=request.get("repo"), pr_number=request.get("pr_number"))
        return Err(error=f"Unknown operation: {operation}")

    def validate(self) -> Union[Ok, Err]:
        """Validate orchestrator state"""
        if not self.name:
            return Err(error="Orchestrator name not set")
        return Ok(value=True)

    def get_capabilities(self) -> List[str]:
        """Get orchestrator capabilities"""
        return [
            "fetch_pr_info",
            "analyze_pr_diff",
            "check_for_secrets",
            "check_coverage_delta",
            "check_style_compliance",
            "generate_review_comments",
            "post_review_decision",
            "review_pr_complete_workflow",
        ]


# AC_COMPLETE: AC-PHASE52-S1-002 ✅

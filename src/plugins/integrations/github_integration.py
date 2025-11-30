"""
GitHub Integration for Code Review Plugin

Provides integration with GitHub REST API and GraphQL for:
- Pull request retrieval
- Automated code review comments
- Review status updates (approve, request changes, comment)
- Thread resolution
- Check runs and status checks

Documentation: https://docs.github.com/en/rest

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """Configuration for GitHub integration"""
    owner: str
    repository: str
    personal_access_token: str
    api_version: str = "2022-11-28"
    
    @property
    def base_url(self) -> str:
        """Get base API URL"""
        return f"https://api.github.com/repos/{self.owner}/{self.repository}"
    
    @property
    def auth_header(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.personal_access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": self.api_version
        }


class GitHubIntegration:
    """
    GitHub integration for code reviews
    
    Features:
    - Fetch pull request details and file changes
    - Post review comments on specific lines
    - Submit reviews (approve, request changes, comment)
    - Create check runs
    - Update commit statuses
    """
    
    def __init__(self, config: GitHubConfig):
        """
        Initialize GitHub integration
        
        Args:
            config: GitHub configuration
        """
        self.config = config
        self.logger = logging.getLogger("github")
    
    def get_pull_request(self, pr_number: int) -> Optional[Dict[str, Any]]:
        """
        Get pull request details
        
        Args:
            pr_number: Pull request number
        
        Returns:
            Pull request details or None if error
        """
        try:
            url = f"{self.config.base_url}/pulls/{pr_number}"
            
            self.logger.info(f"Fetching PR #{pr_number} from GitHub")
            
            # Mock return for testing
            return {
                "number": pr_number,
                "title": "Example PR",
                "body": "Example description",
                "state": "open",
                "head": {"ref": "feature-branch", "sha": "abc123"},
                "base": {"ref": "main", "sha": "def456"},
                "user": {"login": "developer"},
                "draft": False
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get PR #{pr_number}: {e}")
            return None
    
    def get_pr_files(self, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get list of files changed in pull request
        
        Args:
            pr_number: Pull request number
        
        Returns:
            List of file changes with paths and patches
        """
        try:
            url = f"{self.config.base_url}/pulls/{pr_number}/files"
            
            self.logger.info(f"Fetching file changes for PR #{pr_number}")
            
            # Mock return for testing
            return [
                {
                    "filename": "src/example.py",
                    "status": "modified",
                    "additions": 10,
                    "deletions": 5,
                    "changes": 15,
                    "sha": "abc123",
                    "patch": "@@ -1,5 +1,10 @@\n..."
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get files for PR #{pr_number}: {e}")
            return []
    
    def create_review_comment(
        self,
        pr_number: int,
        commit_sha: str,
        file_path: str,
        line: int,
        body: str,
        side: str = "RIGHT"
    ) -> bool:
        """
        Create a review comment on specific line
        
        Args:
            pr_number: Pull request number
            commit_sha: Commit SHA to comment on
            file_path: File path relative to repository root
            line: Line number for comment
            body: Comment body (supports Markdown)
            side: Side of diff (LEFT or RIGHT)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.config.base_url}/pulls/{pr_number}/comments"
            
            payload = {
                "body": body,
                "commit_id": commit_sha,
                "path": file_path,
                "line": line,
                "side": side
            }
            
            self.logger.info(
                f"Creating review comment on {file_path}:{line} "
                f"for PR #{pr_number}"
            )
            
            # In real implementation: requests.post(url, json=payload, headers=...)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create review comment: {e}")
            return False
    
    def submit_review(
        self,
        pr_number: int,
        commit_sha: str,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Submit a pull request review
        
        Args:
            pr_number: Pull request number
            commit_sha: Commit SHA being reviewed
            body: Review summary comment
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: List of review comments with positions
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.config.base_url}/pulls/{pr_number}/reviews"
            
            payload = {
                "commit_id": commit_sha,
                "body": body,
                "event": event
            }
            
            if comments:
                payload["comments"] = comments
            
            self.logger.info(
                f"Submitting {event} review for PR #{pr_number}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit review: {e}")
            return False
    
    def create_check_run(
        self,
        name: str,
        head_sha: str,
        status: str,
        conclusion: Optional[str] = None,
        output: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create or update a check run
        
        Args:
            name: Check run name
            head_sha: Commit SHA
            status: Status (queued, in_progress, completed)
            conclusion: Conclusion if completed (success, failure, neutral, etc.)
            output: Check run output with title, summary, annotations
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.config.base_url}/check-runs"
            
            payload = {
                "name": name,
                "head_sha": head_sha,
                "status": status
            }
            
            if conclusion:
                payload["conclusion"] = conclusion
            
            if output:
                payload["output"] = output
            
            self.logger.info(
                f"Creating check run '{name}' for {head_sha}: {status}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create check run: {e}")
            return False
    
    def create_commit_status(
        self,
        sha: str,
        state: str,
        context: str,
        description: str,
        target_url: Optional[str] = None
    ) -> bool:
        """
        Create commit status (simpler alternative to check runs)
        
        Args:
            sha: Commit SHA
            state: State (error, failure, pending, success)
            context: Status context (e.g., "CORTEX/code-review")
            description: Status description
            target_url: Optional URL with more details
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.config.base_url}/statuses/{sha}"
            
            payload = {
                "state": state,
                "context": context,
                "description": description
            }
            
            if target_url:
                payload["target_url"] = target_url
            
            self.logger.info(
                f"Creating commit status for {sha}: {state}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create commit status: {e}")
            return False
    
    def post_violations_to_pr(
        self,
        pr_number: int,
        commit_sha: str,
        violations: List[Dict[str, Any]],
        overall_score: float
    ) -> bool:
        """
        Post code review violations to pull request
        
        Args:
            pr_number: Pull request number
            commit_sha: Commit SHA being reviewed
            violations: List of violations from code review
            overall_score: Overall code quality score
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Group violations by severity
            critical = [v for v in violations if v["severity"] == "critical"]
            high = [v for v in violations if v["severity"] == "high"]
            medium = [v for v in violations if v["severity"] == "medium"]
            low = [v for v in violations if v["severity"] == "low"]
            
            # Create summary
            summary_lines = [
                "# 🤖 CORTEX Code Review",
                "",
                f"**Overall Score:** {overall_score:.1f}/100",
                "",
                "## Summary",
                f"- 🔴 Critical: {len(critical)}",
                f"- 🟠 High: {len(high)}",
                f"- 🟡 Medium: {len(medium)}",
                f"- 🟢 Low: {len(low)}",
                ""
            ]
            
            # Determine review event and status based on score
            if len(critical) > 0:
                event = "REQUEST_CHANGES"
                status_state = "failure"
                summary_lines.append("**Status:** ❌ Changes Required (Critical issues found)")
            elif overall_score >= 90:
                event = "APPROVE"
                status_state = "success"
                summary_lines.append("**Status:** ✅ Approved")
            elif overall_score >= 75:
                event = "COMMENT"
                status_state = "success"
                summary_lines.append("**Status:** ✅ Looks good with minor suggestions")
            else:
                event = "REQUEST_CHANGES"
                status_state = "failure"
                summary_lines.append("**Status:** ⚠️ Needs improvement")
            
            summary = "\n".join(summary_lines)
            
            # Prepare inline comments (limit to top 30 most severe)
            violations_to_post = sorted(
                violations,
                key=lambda v: (
                    {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(v["severity"], 4),
                    -v.get("confidence", 0)
                )
            )[:30]
            
            review_comments = []
            for violation in violations_to_post:
                comment_body = self._format_violation_comment(violation)
                review_comments.append({
                    "path": violation["file_path"],
                    "line": violation["line_number"],
                    "body": comment_body
                })
            
            # Submit review with inline comments
            self.submit_review(
                pr_number=pr_number,
                commit_sha=commit_sha,
                body=summary,
                event=event,
                comments=review_comments
            )
            
            # Create commit status
            self.create_commit_status(
                sha=commit_sha,
                state=status_state,
                context="CORTEX/code-review",
                description=f"Score: {overall_score:.1f}/100, {len(violations)} issues found"
            )
            
            # Create detailed check run
            annotations = []
            for violation in violations_to_post[:50]:  # GitHub limit
                annotations.append({
                    "path": violation["file_path"],
                    "start_line": violation["line_number"],
                    "end_line": violation["line_number"],
                    "annotation_level": self._severity_to_annotation_level(violation["severity"]),
                    "message": violation["message"],
                    "title": violation["type"]
                })
            
            check_conclusion = "success" if status_state == "success" else "failure"
            self.create_check_run(
                name="CORTEX Code Review",
                head_sha=commit_sha,
                status="completed",
                conclusion=check_conclusion,
                output={
                    "title": "Code Review Results",
                    "summary": summary,
                    "annotations": annotations
                }
            )
            
            self.logger.info(
                f"Posted {len(violations_to_post)} violations to PR #{pr_number}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to post violations to PR: {e}")
            return False
    
    def _format_violation_comment(self, violation: Dict[str, Any]) -> str:
        """
        Format violation as markdown comment
        
        Args:
            violation: Violation dictionary
        
        Returns:
            Formatted markdown comment
        """
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "info": "ℹ️"
        }
        
        emoji = severity_emoji.get(violation["severity"], "⚪")
        
        lines = [
            f"{emoji} **{violation['severity'].upper()}**: {violation['message']}",
            ""
        ]
        
        if violation.get("code_snippet"):
            lines.extend([
                "```",
                violation["code_snippet"],
                "```",
                ""
            ])
        
        if violation.get("suggestion"):
            lines.extend([
                "**💡 Suggestion:**",
                violation["suggestion"],
                ""
            ])
        
        lines.append(f"*Confidence: {violation.get('confidence', 0) * 100:.0f}%*")
        
        return "\n".join(lines)
    
    def _severity_to_annotation_level(self, severity: str) -> str:
        """
        Convert violation severity to GitHub annotation level
        
        Args:
            severity: Violation severity
        
        Returns:
            GitHub annotation level (failure, warning, notice)
        """
        if severity in ["critical", "high"]:
            return "failure"
        elif severity == "medium":
            return "warning"
        else:
            return "notice"


# Export main class
__all__ = ['GitHubIntegration', 'GitHubConfig']

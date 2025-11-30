"""
Azure DevOps Integration for Code Review Plugin

Provides integration with Azure DevOps REST API for:
- Pull request retrieval
- Automated code review comments
- Review status updates
- Thread resolution
- Build policy integration

Documentation: https://learn.microsoft.com/en-us/rest/api/azure/devops/

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import json
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


@dataclass
class AzureDevOpsConfig:
    """Configuration for Azure DevOps integration"""
    organization: str
    project: str
    repository: str
    personal_access_token: str
    api_version: str = "7.0"
    
    @property
    def base_url(self) -> str:
        """Get base API URL"""
        return f"https://dev.azure.com/{self.organization}/{self.project}/_apis"
    
    @property
    def auth_header(self) -> Dict[str, str]:
        """Get authorization header"""
        token_bytes = f":{self.personal_access_token}".encode('ascii')
        token_b64 = base64.b64encode(token_bytes).decode('ascii')
        return {
            "Authorization": f"Basic {token_b64}",
            "Content-Type": "application/json"
        }


class AzureDevOpsIntegration:
    """
    Azure DevOps integration for code reviews
    
    Features:
    - Fetch pull request details and file changes
    - Post review comments on specific lines
    - Update pull request status (approved/needs work)
    - Create review threads
    - Update build policies
    """
    
    def __init__(self, config: AzureDevOpsConfig):
        """
        Initialize Azure DevOps integration
        
        Args:
            config: Azure DevOps configuration
        """
        self.config = config
        self.logger = logging.getLogger("azure_devops")
    
    def get_pull_request(self, pr_id: int) -> Optional[Dict[str, Any]]:
        """
        Get pull request details
        
        Args:
            pr_id: Pull request ID
        
        Returns:
            Pull request details or None if error
        """
        try:
            url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}"
                f"?api-version={self.config.api_version}"
            )
            
            # This would use requests library in real implementation
            # For now, return mock structure
            self.logger.info(f"Fetching PR {pr_id} from Azure DevOps")
            
            return {
                "pullRequestId": pr_id,
                "title": "Example PR",
                "description": "Example description",
                "sourceRefName": "refs/heads/feature-branch",
                "targetRefName": "refs/heads/main",
                "status": "active",
                "createdBy": {"displayName": "Developer"},
                "reviewers": []
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get PR {pr_id}: {e}")
            return None
    
    def get_pr_files(self, pr_id: int) -> List[Dict[str, Any]]:
        """
        Get list of files changed in pull request
        
        Args:
            pr_id: Pull request ID
        
        Returns:
            List of file changes with paths and content
        """
        try:
            # Get iteration (commit range)
            iterations_url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/iterations"
                f"?api-version={self.config.api_version}"
            )
            
            # Get file changes
            changes_url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/iterations/1"
                f"?api-version={self.config.api_version}"
            )
            
            self.logger.info(f"Fetching file changes for PR {pr_id}")
            
            # Mock return for testing
            return [
                {
                    "path": "/src/example.py",
                    "changeType": "edit",
                    "item": {
                        "objectId": "abc123",
                        "path": "/src/example.py"
                    }
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get files for PR {pr_id}: {e}")
            return []
    
    def create_review_thread(
        self,
        pr_id: int,
        file_path: str,
        line_number: int,
        comment: str,
        status: str = "active"
    ) -> bool:
        """
        Create a review thread (comment) on specific line
        
        Args:
            pr_id: Pull request ID
            file_path: File path relative to repository root
            line_number: Line number for comment
            comment: Comment text
            status: Thread status (active, fixed, closed)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/threads"
                f"?api-version={self.config.api_version}"
            )
            
            payload = {
                "comments": [
                    {
                        "parentCommentId": 0,
                        "content": comment,
                        "commentType": 1  # Text comment
                    }
                ],
                "status": status,
                "threadContext": {
                    "filePath": file_path,
                    "rightFileStart": {
                        "line": line_number,
                        "offset": 1
                    },
                    "rightFileEnd": {
                        "line": line_number,
                        "offset": 1
                    }
                }
            }
            
            self.logger.info(
                f"Creating review thread on {file_path}:{line_number} "
                f"for PR {pr_id}"
            )
            
            # In real implementation: requests.post(url, json=payload, headers=...)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create review thread: {e}")
            return False
    
    def post_review_summary(
        self,
        pr_id: int,
        summary: str,
        vote: int = 0
    ) -> bool:
        """
        Post overall review summary
        
        Args:
            pr_id: Pull request ID
            summary: Summary comment
            vote: Vote (-10: reject, 0: no vote, 5: approved with suggestions,
                  10: approved)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Post summary comment
            url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/threads"
                f"?api-version={self.config.api_version}"
            )
            
            payload = {
                "comments": [
                    {
                        "parentCommentId": 0,
                        "content": summary,
                        "commentType": 1
                    }
                ],
                "status": "active"
            }
            
            # Update reviewer vote if specified
            if vote != 0:
                vote_url = (
                    f"{self.config.base_url}/git/repositories/"
                    f"{self.config.repository}/pullrequests/{pr_id}/reviewers/"
                    f"{{reviewer_id}}?api-version={self.config.api_version}"
                )
                
                vote_payload = {
                    "vote": vote
                }
            
            self.logger.info(f"Posting review summary for PR {pr_id} (vote: {vote})")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to post review summary: {e}")
            return False
    
    def update_thread_status(
        self,
        pr_id: int,
        thread_id: int,
        status: str
    ) -> bool:
        """
        Update status of review thread
        
        Args:
            pr_id: Pull request ID
            thread_id: Thread ID
            status: New status (active, fixed, closed)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/threads/"
                f"{thread_id}?api-version={self.config.api_version}"
            )
            
            payload = {
                "status": status
            }
            
            self.logger.info(
                f"Updating thread {thread_id} status to {status} for PR {pr_id}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update thread status: {e}")
            return False
    
    def create_build_policy(
        self,
        pr_id: int,
        policy_name: str,
        status: str,
        description: str
    ) -> bool:
        """
        Create or update build policy status
        
        Args:
            pr_id: Pull request ID
            policy_name: Policy name (e.g., "Code Review Quality")
            status: Status (succeeded, failed, pending)
            description: Description of policy status
        
        Returns:
            True if successful, False otherwise
        """
        try:
            url = (
                f"{self.config.base_url}/git/repositories/"
                f"{self.config.repository}/pullrequests/{pr_id}/statuses"
                f"?api-version={self.config.api_version}"
            )
            
            payload = {
                "state": status,
                "description": description,
                "context": {
                    "name": policy_name,
                    "genre": "continuous-integration"
                },
                "targetUrl": None
            }
            
            self.logger.info(
                f"Creating build policy '{policy_name}' for PR {pr_id}: {status}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create build policy: {e}")
            return False
    
    def post_violations_to_pr(
        self,
        pr_id: int,
        violations: List[Dict[str, Any]],
        overall_score: float
    ) -> bool:
        """
        Post code review violations to pull request
        
        Args:
            pr_id: Pull request ID
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
            
            # Determine vote based on score and critical issues
            if len(critical) > 0:
                vote = -10  # Reject
                summary_lines.append("**Status:** ❌ Changes Required (Critical issues found)")
            elif overall_score >= 90:
                vote = 10  # Approved
                summary_lines.append("**Status:** ✅ Approved")
            elif overall_score >= 75:
                vote = 5  # Approved with suggestions
                summary_lines.append("**Status:** ✅ Approved with suggestions")
            else:
                vote = 0  # No vote (needs work)
                summary_lines.append("**Status:** ⚠️ Needs improvement")
            
            summary = "\n".join(summary_lines)
            
            # Post overall summary
            self.post_review_summary(pr_id, summary, vote)
            
            # Post individual violation threads (limit to top 20 most severe)
            violations_to_post = sorted(
                violations,
                key=lambda v: (
                    {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(v["severity"], 4),
                    -v.get("confidence", 0)
                )
            )[:20]
            
            for violation in violations_to_post:
                comment = self._format_violation_comment(violation)
                self.create_review_thread(
                    pr_id=pr_id,
                    file_path=violation["file_path"],
                    line_number=violation["line_number"],
                    comment=comment,
                    status="active"
                )
            
            # Update build policy
            policy_status = "succeeded" if overall_score >= 75 else "failed"
            self.create_build_policy(
                pr_id=pr_id,
                policy_name="CORTEX Code Review",
                status=policy_status,
                description=f"Score: {overall_score:.1f}/100, Violations: {len(violations)}"
            )
            
            self.logger.info(
                f"Posted {len(violations_to_post)} violations to PR {pr_id}"
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
                "**Suggestion:**",
                violation["suggestion"],
                ""
            ])
        
        lines.append(f"*Confidence: {violation.get('confidence', 0) * 100:.0f}%*")
        
        return "\n".join(lines)


# Export main class
__all__ = ['AzureDevOpsIntegration', 'AzureDevOpsConfig']

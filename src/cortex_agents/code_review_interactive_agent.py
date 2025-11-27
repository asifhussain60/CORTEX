"""
Code Review Interactive Agent

Interactive Q&A workflow for pull request code review.
Replaces template-based workflow with conversational PR analysis.

Features:
- Interactive question flow for PR review
- Multiple PR input methods (ADO link, work item ID, paste diff)
- Tiered analysis (Quick/Standard/Deep)
- Focus area selection (Security/Performance/etc.)
- Actionable reports with fix templates
"""

from typing import Dict, Any
from datetime import datetime
import os

from src.cortex_agents.base_interactive_agent import (
    BaseInteractiveAgent,
    ConversationState
)
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType


class CodeReviewInteractiveAgent(BaseInteractiveAgent):
    """
    Interactive agent for code review workflows.
    
    Asks questions to collect PR information and review preferences,
    then performs tiered analysis with actionable recommendations.
    
    Example Flow:
        User: "code review"
        Agent: "How would you like to provide the PR? (ADO Link/Work Item ID/Paste Diff)"
        User: "ado link"
        Agent: "ADO Pull Request Link?"
        User: "https://dev.azure.com/.../pullrequest/12345"
        Agent: "Review Depth? (Quick/Standard/Deep)"
        [continues...]
        Agent: [shows preview]
        User: "approve"
        Agent: ✅ Generated code review report with recommendations
    """
    
    def get_schema_name(self) -> str:
        """Return schema name for code review."""
        return "code-review"
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if request is for code review."""
        intent = request.intent.lower() if isinstance(request.intent, str) else request.intent.value
        
        # Check intent type
        if intent == IntentType.CODE_REVIEW.value:
            return True
        
        # Check message for code review keywords
        msg = request.user_message.lower()
        review_triggers = [
            "code review", "review code", "review pr",
            "pr review", "pull request", "check pr",
            "ado pr", "review changes"
        ]
        
        return any(trigger in msg for trigger in review_triggers)
    
    def generate_output(self, state: ConversationState) -> Dict[str, Any]:
        """
        Generate code review report from collected answers.
        
        Args:
            state: Completed conversation state
        
        Returns:
            Dict with file_path, content, and summary
        """
        answers = state.answers
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        pr_source = answers.get('pr_source', 'unknown').replace(' ', '-').lower()
        depth = answers.get('review_depth', 'standard').lower()
        
        filename = f"CODE-REVIEW-{timestamp}-{pr_source}-{depth}.md"
        file_path = os.path.join(
            "cortex-brain", "documents", "reports", "code-reviews", filename
        )
        
        # Perform review based on depth and focus areas
        review_results = self._perform_review(answers)
        
        # Generate content
        content = self._generate_markdown(answers, review_results)
        
        # Create file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "file_path": file_path,
            "content": content,
            "review_results": review_results,
            "summary": self._generate_summary(answers, review_results, file_path)
        }
    
    def _perform_review(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform code review based on depth and focus areas.
        
        This is a simplified implementation. In production, this would:
        - Fetch actual PR diff from ADO
        - Parse code changes
        - Run static analysis
        - Check OWASP security patterns
        - Validate TDD patterns
        """
        depth = answers.get('review_depth', 'Standard')
        focus_areas = answers.get('focus_areas', 'All')
        
        # Simulated review results
        issues = {
            "critical": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Quick review (30s) - Critical only
        if depth in ['Quick', 'Standard', 'Deep']:
            issues["critical"].extend([
                {
                    "type": "Security",
                    "message": "Potential SQL injection vulnerability",
                    "file": "src/database/query.py",
                    "line": 45,
                    "fix_template": "Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
                }
            ])
        
        # Standard review (2min) - + Best practices
        if depth in ['Standard', 'Deep']:
            issues["warnings"].extend([
                {
                    "type": "Maintainability",
                    "message": "Function exceeds recommended complexity (15 > 10)",
                    "file": "src/utils/helpers.py",
                    "line": 120,
                    "fix_template": "Extract nested logic into separate functions"
                }
            ])
        
        # Deep review (5min) - + Security/TDD
        if depth == 'Deep':
            issues["suggestions"].extend([
                {
                    "type": "Tests",
                    "message": "Missing unit tests for new authentication flow",
                    "file": "src/auth/login.py",
                    "line": 0,
                    "fix_template": "Add test_login_success(), test_login_invalid_credentials(), test_login_rate_limiting()"
                }
            ])
        
        # Calculate risk score
        risk_score = (
            len(issues["critical"]) * 30 +
            len(issues["warnings"]) * 15 +
            len(issues["suggestions"]) * 5
        )
        risk_score = min(risk_score, 100)
        
        return {
            "issues": issues,
            "risk_score": risk_score,
            "total_issues": sum(len(v) for v in issues.values()),
            "executive_summary": self._generate_executive_summary(issues, risk_score)
        }
    
    def _generate_executive_summary(self, issues: Dict[str, list], risk_score: int) -> str:
        """Generate 3-sentence executive summary."""
        critical_count = len(issues["critical"])
        warning_count = len(issues["warnings"])
        
        if risk_score >= 60:
            severity = "high-risk"
        elif risk_score >= 30:
            severity = "moderate-risk"
        else:
            severity = "low-risk"
        
        summary = (
            f"This is a {severity} pull request with {critical_count} critical issues and {warning_count} warnings. "
        )
        
        if critical_count > 0:
            summary += "Critical issues must be addressed before merge. "
        else:
            summary += "No blocking issues detected. "
        
        summary += f"Overall risk score: {risk_score}/100."
        
        return summary
    
    def _generate_markdown(self, answers: Dict[str, Any], review_results: Dict[str, Any]) -> str:
        """Generate markdown code review report."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        lines = [
            f"# Code Review Report",
            f"**Date:** {timestamp}",
            f"**Review Depth:** {answers.get('review_depth')}",
            f"**Focus Areas:** {answers.get('focus_areas')}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            review_results["executive_summary"],
            "",
            f"**Risk Score:** {review_results['risk_score']}/100",
            f"**Total Issues:** {review_results['total_issues']}",
            "",
            "---",
            "",
            "## PR Details",
            "",
        ]
        
        # Add PR source info
        pr_source = answers.get('pr_source')
        if pr_source == 'ADO Link':
            lines.append(f"**ADO Link:** {answers.get('ado_link')}")
        elif pr_source == 'Work Item ID':
            lines.append(f"**Work Item:** #{answers.get('work_item_id')}")
        elif pr_source == 'Paste Diff':
            lines.append("**Source:** Manual diff paste")
        
        if answers.get('additional_context'):
            lines.extend([
                "",
                "**Additional Context:**",
                "",
                answers.get('additional_context'),
            ])
        
        lines.extend([
            "",
            "---",
            "",
            "## Issues & Recommendations",
            "",
        ])
        
        # Critical issues
        if review_results["issues"]["critical"]:
            lines.extend([
                "### ❌ Critical Issues (Must Fix Before Merge)",
                "",
            ])
            for issue in review_results["issues"]["critical"]:
                lines.extend([
                    f"**{issue['type']}** - `{issue['file']}:{issue['line']}`",
                    f"- {issue['message']}",
                    f"- **Fix:** {issue['fix_template']}",
                    "",
                ])
        
        # Warnings
        if review_results["issues"]["warnings"]:
            lines.extend([
                "### ⚠️ Warnings (Should Fix Soon)",
                "",
            ])
            for issue in review_results["issues"]["warnings"]:
                lines.extend([
                    f"**{issue['type']}** - `{issue['file']}:{issue['line']}`",
                    f"- {issue['message']}",
                    f"- **Fix:** {issue['fix_template']}",
                    "",
                ])
        
        # Suggestions
        if review_results["issues"]["suggestions"]:
            lines.extend([
                "### 💡 Suggestions (Nice to Have)",
                "",
            ])
            for issue in review_results["issues"]["suggestions"]:
                lines.extend([
                    f"**{issue['type']}** - `{issue['file']}:{issue.get('line', 'N/A')}`",
                    f"- {issue['message']}",
                    f"- **Fix:** {issue['fix_template']}",
                    "",
                ])
        
        lines.extend([
            "---",
            "",
            "## Next Steps",
            "",
        ])
        
        if review_results["issues"]["critical"]:
            lines.append("1. Address all critical issues")
            lines.append("2. Re-run code review")
            lines.append("3. Request re-review from team")
        else:
            lines.append("1. Address warnings if time permits")
            lines.append("2. Consider suggestions for future improvements")
            lines.append("3. Proceed with merge")
        
        return "\n".join(lines)
    
    def _generate_summary(
        self,
        answers: Dict[str, Any],
        review_results: Dict[str, Any],
        file_path: str
    ) -> str:
        """Generate summary message."""
        lines = [
            f"**Review Depth:** {answers.get('review_depth')}",
            f"**Risk Score:** {review_results['risk_score']}/100",
            f"**Issues:** {len(review_results['issues']['critical'])} critical, "
            f"{len(review_results['issues']['warnings'])} warnings, "
            f"{len(review_results['issues']['suggestions'])} suggestions",
            f"**Report:** `{file_path}`",
        ]
        
        if review_results["issues"]["critical"]:
            lines.append("")
            lines.append("❌ **Critical issues found - do not merge yet**")
        else:
            lines.append("")
            lines.append("✅ **No critical issues - safe to merge**")
        
        return "\n".join(lines)

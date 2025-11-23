"""
GitHub Issue Template Formatter

Converts feedback reports to GitHub Issue format with proper formatting,
labels, and priority indicators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .feedback_collector import FeedbackItem, FeedbackCategory, FeedbackPriority
from .report_generator import FeedbackReport


logger = logging.getLogger(__name__)


class IssueTemplate(Enum):
    """GitHub Issue template types."""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"


@dataclass
class GitHubIssue:
    """Formatted GitHub Issue."""
    
    title: str
    body: str
    labels: List[str]
    assignees: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for GitHub API."""
        return {
            'title': self.title,
            'body': self.body,
            'labels': self.labels,
            'assignees': self.assignees,
        }


class GitHubIssueFormatter:
    """
    Formats feedback as GitHub Issues.
    
    Usage:
        formatter = GitHubIssueFormatter()
        
        # Single item
        issue = formatter.format_feedback_item(feedback_item)
        print(issue.body)
        
        # Batch report
        issues = formatter.format_report_as_issues(report)
        for issue in issues:
            # Upload to GitHub
            pass
    """
    
    def __init__(self, repository_owner: str = "asifhussain60", repository_name: str = "CORTEX"):
        """
        Initialize formatter.
        
        Args:
            repository_owner: GitHub username
            repository_name: Repository name
        """
        self.repository_owner = repository_owner
        self.repository_name = repository_name
    
    def format_feedback_item(
        self,
        item: FeedbackItem,
        include_metadata: bool = True
    ) -> GitHubIssue:
        """
        Format single feedback item as GitHub Issue.
        
        Args:
            item: FeedbackItem to format
            include_metadata: Include technical metadata
        
        Returns:
            GitHubIssue ready for upload
        """
        # Determine template
        template = self._get_template_for_category(item.category)
        
        # Build title
        title = self._build_title(item)
        
        # Build body
        body = self._build_body(item, template, include_metadata)
        
        # Build labels
        labels = self._build_labels(item)
        
        return GitHubIssue(
            title=title,
            body=body,
            labels=labels,
            assignees=[],  # No automatic assignment
        )
    
    def format_report_as_issues(
        self,
        report: FeedbackReport,
        group_similar: bool = True
    ) -> List[GitHubIssue]:
        """
        Format entire report as GitHub Issues.
        
        Args:
            report: FeedbackReport to format
            group_similar: Group similar issues together
        
        Returns:
            List of GitHubIssue objects
        """
        issues = []
        
        # Create summary issue
        summary_issue = self._create_summary_issue(report)
        issues.append(summary_issue)
        
        # Create individual issues for critical/high priority
        all_items = (
            report.critical_issues +
            report.high_priority
        )
        
        for item_dict in all_items:
            # Reconstruct FeedbackItem from dict
            item = self._dict_to_feedback_item(item_dict)
            issue = self.format_feedback_item(item, include_metadata=True)
            issues.append(issue)
        
        return issues
    
    def export_for_cli_upload(
        self,
        issues: List[GitHubIssue],
        output_format: str = "json"
    ) -> str:
        """
        Export issues in format suitable for CLI upload.
        
        Args:
            issues: List of GitHubIssue objects
            output_format: "json" or "markdown"
        
        Returns:
            Formatted string
        """
        if output_format == "json":
            import json
            return json.dumps(
                [issue.to_dict() for issue in issues],
                indent=2
            )
        
        elif output_format == "markdown":
            md = []
            md.append("# GitHub Issues for Upload")
            md.append("")
            md.append(f"**Generated:** {datetime.now().isoformat()}")
            md.append(f"**Total Issues:** {len(issues)}")
            md.append("")
            
            for i, issue in enumerate(issues, 1):
                md.append(f"## Issue {i}: {issue.title}")
                md.append("")
                md.append(f"**Labels:** {', '.join(issue.labels)}")
                md.append("")
                md.append("### Body")
                md.append("")
                md.append(issue.body)
                md.append("")
                md.append("---")
                md.append("")
            
            return "\n".join(md)
        
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _get_template_for_category(
        self,
        category: FeedbackCategory
    ) -> IssueTemplate:
        """Map feedback category to issue template."""
        mapping = {
            FeedbackCategory.BUG: IssueTemplate.BUG_REPORT,
            FeedbackCategory.FEATURE_REQUEST: IssueTemplate.FEATURE_REQUEST,
            FeedbackCategory.IMPROVEMENT: IssueTemplate.IMPROVEMENT,
            FeedbackCategory.DOCUMENTATION: IssueTemplate.DOCUMENTATION,
            FeedbackCategory.PERFORMANCE: IssueTemplate.BUG_REPORT,
            FeedbackCategory.USABILITY: IssueTemplate.IMPROVEMENT,
            FeedbackCategory.INTEGRATION: IssueTemplate.FEATURE_REQUEST,
        }
        return mapping.get(category, IssueTemplate.BUG_REPORT)
    
    def _build_title(self, item: FeedbackItem) -> str:
        """Build issue title."""
        # Add category prefix
        prefix_map = {
            FeedbackCategory.BUG: "[BUG]",
            FeedbackCategory.FEATURE_REQUEST: "[FEATURE]",
            FeedbackCategory.IMPROVEMENT: "[IMPROVEMENT]",
            FeedbackCategory.DOCUMENTATION: "[DOCS]",
            FeedbackCategory.PERFORMANCE: "[PERFORMANCE]",
            FeedbackCategory.USABILITY: "[UX]",
            FeedbackCategory.INTEGRATION: "[INTEGRATION]",
        }
        
        prefix = prefix_map.get(item.category, "")
        return f"{prefix} {item.title}"
    
    def _build_body(
        self,
        item: FeedbackItem,
        template: IssueTemplate,
        include_metadata: bool
    ) -> str:
        """Build issue body."""
        sections = []
        
        # Description
        sections.append("## Description")
        sections.append("")
        sections.append(item.description)
        sections.append("")
        
        # Error details (if present)
        if item.error_message:
            sections.append("## Error Details")
            sections.append("")
            sections.append(f"**Error Message:**")
            sections.append(f"```")
            sections.append(item.error_message)
            sections.append(f"```")
            sections.append("")
        
        # Operation attempted (if present)
        if item.operation_attempted:
            sections.append("## Reproduction Steps")
            sections.append("")
            sections.append(f"Operation attempted: `{item.operation_attempted}`")
            sections.append("")
        
        # Impact
        sections.append("## Impact")
        sections.append("")
        sections.append(f"- **Frequency:** {item.frequency}")
        sections.append(f"- **Workaround Exists:** {'Yes' if item.workaround_exists else 'No'}")
        sections.append("")
        
        # Metadata (if requested)
        if include_metadata:
            sections.append("## Environment")
            sections.append("")
            sections.append(f"- **CORTEX Version:** {item.cortex_version}")
            sections.append(f"- **Platform:** {item.platform}")
            sections.append(f"- **Environment Hash:** {item.environment_hash}")
            sections.append(f"- **Auto-Collected:** {'Yes' if item.auto_collected else 'No'}")
            sections.append("")
        
        # Stack trace (if present and not too long)
        if item.stack_trace and len(item.stack_trace) < 2000:
            sections.append("<details>")
            sections.append("<summary>Stack Trace</summary>")
            sections.append("")
            sections.append("```")
            sections.append(item.stack_trace)
            sections.append("```")
            sections.append("")
            sections.append("</details>")
            sections.append("")
        
        # Footer
        sections.append("---")
        sections.append(f"*This issue was auto-generated from user feedback on {item.timestamp}*")
        
        return "\n".join(sections)
    
    def _build_labels(self, item: FeedbackItem) -> List[str]:
        """Build GitHub labels for issue."""
        labels = []
        
        # Category label
        category_labels = {
            FeedbackCategory.BUG: "bug",
            FeedbackCategory.FEATURE_REQUEST: "enhancement",
            FeedbackCategory.IMPROVEMENT: "enhancement",
            FeedbackCategory.DOCUMENTATION: "documentation",
            FeedbackCategory.PERFORMANCE: "performance",
            FeedbackCategory.USABILITY: "ux",
            FeedbackCategory.INTEGRATION: "integration",
        }
        labels.append(category_labels.get(item.category, "bug"))
        
        # Priority label
        priority_labels = {
            FeedbackPriority.CRITICAL: "priority:critical",
            FeedbackPriority.HIGH: "priority:high",
            FeedbackPriority.MEDIUM: "priority:medium",
            FeedbackPriority.LOW: "priority:low",
            FeedbackPriority.ENHANCEMENT: "enhancement",
        }
        labels.append(priority_labels.get(item.priority, "priority:medium"))
        
        # Auto-collected tag
        if item.auto_collected:
            labels.append("auto-collected")
        
        # Custom tags
        labels.extend(item.tags)
        
        return list(set(labels))  # Remove duplicates
    
    def _create_summary_issue(self, report: FeedbackReport) -> GitHubIssue:
        """Create summary issue for entire report."""
        title = f"[FEEDBACK SUMMARY] {report.report_id}"
        
        body = []
        body.append("# CORTEX Feedback Summary")
        body.append("")
        body.append(f"**Report ID:** {report.report_id}")
        body.append(f"**Generated:** {report.generated_at}")
        body.append(f"**CORTEX Version:** {report.cortex_version}")
        body.append("")
        
        body.append("## Summary Statistics")
        body.append("")
        body.append(f"- **Total Feedback Items:** {report.total_items}")
        body.append(f"- **Environment Diversity:** {report.environment_diversity} unique environments")
        body.append(f"- **Auto-Collected:** {report.auto_collected_count}")
        body.append(f"- **User-Submitted:** {report.user_submitted_count}")
        body.append("")
        
        body.append("### By Category")
        body.append("")
        for category, count in report.by_category.items():
            body.append(f"- **{category}:** {count}")
        body.append("")
        
        body.append("### By Priority")
        body.append("")
        for priority, count in report.by_priority.items():
            body.append(f"- **{priority}:** {count}")
        body.append("")
        
        # Most used operations
        if report.most_used_operations:
            body.append("## Most Used Operations")
            body.append("")
            for op in report.most_used_operations[:5]:
                body.append(f"- `{op['operation']}`: {op['total_uses']} uses, {op['success_rate']*100:.1f}% success")
            body.append("")
        
        # Operations needing improvement
        if report.least_successful_operations:
            body.append("## Operations Needing Improvement")
            body.append("")
            for op in report.least_successful_operations[:5]:
                body.append(f"- `{op['operation']}`: {op['success_rate']*100:.1f}% success ({op['failures']} failures)")
            body.append("")
        
        body.append("---")
        body.append("")
        body.append("Individual issues have been created for critical and high-priority items.")
        
        return GitHubIssue(
            title=title,
            body="\n".join(body),
            labels=["feedback-summary", "meta"],
            assignees=[],
        )
    
    def _dict_to_feedback_item(self, item_dict: Dict[str, Any]) -> FeedbackItem:
        """Convert dictionary back to FeedbackItem."""
        return FeedbackItem(
            category=FeedbackCategory(item_dict['category']),
            priority=FeedbackPriority(item_dict['priority']),
            title=item_dict['title'],
            description=item_dict['description'],
            timestamp=item_dict['timestamp'],
            cortex_version=item_dict['cortex_version'],
            platform=item_dict['platform'],
            error_message=item_dict.get('error_message'),
            stack_trace=item_dict.get('stack_trace'),
            operation_attempted=item_dict.get('operation_attempted'),
            frequency=item_dict.get('frequency', 'once'),
            workaround_exists=item_dict.get('workaround_exists', False),
            anonymized_path=item_dict.get('anonymized_path'),
            environment_hash=item_dict.get('environment_hash'),
            auto_collected=item_dict.get('auto_collected', False),
            tags=item_dict.get('tags', []),
        )

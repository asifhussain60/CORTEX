"""
CORTEX Feedback System

Collects user feedback, usage metrics, and error patterns to improve CORTEX.
Generates structured reports (JSON/YAML) ready for GitHub Issues.

Key Features:
- Anonymized data collection (no sensitive info)
- Usage pattern tracking (what works, what doesn't)
- Error aggregation (common failure modes)
- GitHub Issue template generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from .feedback_collector import (
    FeedbackCollector,
    FeedbackCategory,
    FeedbackPriority,
    FeedbackItem,
)

from .report_generator import (
    FeedbackReportGenerator,
    FeedbackReport,
    ReportFormat,
)

from .github_formatter import (
    GitHubIssueFormatter,
    GitHubIssue,
    IssueTemplate,
)

from .entry_point import FeedbackEntryPoint

__all__ = [
    'FeedbackCollector',
    'FeedbackCategory',
    'FeedbackPriority',
    'FeedbackItem',
    'FeedbackReportGenerator',
    'FeedbackReport',
    'ReportFormat',
    'GitHubIssueFormatter',
    'GitHubIssue',
    'IssueTemplate',
    'FeedbackEntryPoint',
]

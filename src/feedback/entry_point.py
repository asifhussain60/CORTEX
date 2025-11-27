"""
Feedback Entry Point - Interactive feedback collection for CORTEX

Provides natural language interface for users to report bugs, request features,
and suggest improvements. Integrates with FeedbackCollector, FeedbackReportGenerator,
and GitHubIssueFormatter.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from .feedback_collector import (
    FeedbackCollector,
    FeedbackCategory,
    FeedbackPriority,
)
from .report_generator import FeedbackReportGenerator, ReportFormat
from .github_formatter import GitHubIssueFormatter


logger = logging.getLogger(__name__)


class FeedbackEntryPoint:
    """
    Interactive entry point for CORTEX feedback system.
    
    Provides natural language interface for:
    - Bug reports
    - Feature requests
    - Improvement suggestions
    - Documentation feedback
    
    Usage:
        entry_point = FeedbackEntryPoint()
        
        # Interactive mode (prompt user for details)
        entry_point.start_interactive()
        
        # Quick bug report
        entry_point.report_bug(
            title="Crawler timeout on large monoliths",
            description="Targeted crawler exceeds 30s timeout..."
        )
        
        # Generate and save report
        report_path = entry_point.generate_report()
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize feedback entry point.
        
        Args:
            output_dir: Directory for reports (default: cortex-brain/feedback)
        """
        self.collector = FeedbackCollector()
        self.generator = FeedbackReportGenerator(self.collector)
        self.formatter = GitHubIssueFormatter()
        
        if output_dir is None:
            output_dir = Path.cwd() / "cortex-brain" / "feedback" / "reports"
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def start_interactive(self):
        """
        Start interactive feedback collection.
        
        Prompts user for feedback type, details, and generates report.
        """
        print("🎯 CORTEX Feedback System")
        print("=" * 50)
        print()
        print("What would you like to report?")
        print("1. Bug Report")
        print("2. Feature Request")
        print("3. Improvement Suggestion")
        print("4. Documentation Issue")
        print("5. Performance Problem")
        print("6. Usability Concern")
        print()
        
        choice = input("Enter choice (1-6): ").strip()
        
        category_map = {
            "1": FeedbackCategory.BUG,
            "2": FeedbackCategory.FEATURE_REQUEST,
            "3": FeedbackCategory.IMPROVEMENT,
            "4": FeedbackCategory.DOCUMENTATION,
            "5": FeedbackCategory.PERFORMANCE,
            "6": FeedbackCategory.USABILITY,
        }
        
        category = category_map.get(choice, FeedbackCategory.BUG)
        
        # Collect details
        print()
        title = input("Title (short description): ").strip()
        print()
        print("Description (press Enter twice to finish):")
        description_lines = []
        while True:
            line = input()
            if line == "":
                break
            description_lines.append(line)
        description = "\n".join(description_lines)
        
        print()
        print("Priority:")
        print("1. Critical (blocks work)")
        print("2. High (significant impact)")
        print("3. Medium (moderate impact)")
        print("4. Low (minor inconvenience)")
        print("5. Enhancement (nice to have)")
        priority_choice = input("Enter priority (1-5): ").strip()
        
        priority_map = {
            "1": FeedbackPriority.CRITICAL,
            "2": FeedbackPriority.HIGH,
            "3": FeedbackPriority.MEDIUM,
            "4": FeedbackPriority.LOW,
            "5": FeedbackPriority.ENHANCEMENT,
        }
        priority = priority_map.get(priority_choice, FeedbackPriority.MEDIUM)
        
        # Optional fields
        print()
        frequency = input("How often does this occur? (always/often/sometimes/once) [once]: ").strip() or "once"
        workaround = input("Is there a workaround? (yes/no) [no]: ").strip().lower() == "yes"
        
        # Submit feedback
        self.collector.submit_feedback(
            category=category,
            title=title,
            description=description,
            priority=priority,
            frequency=frequency,
            workaround_exists=workaround,
        )
        
        print()
        print("✅ Feedback submitted successfully!")
        print()
        
        # Generate report?
        generate = input("Generate report now? (yes/no) [yes]: ").strip().lower() != "no"
        if generate:
            report_path = self.generate_report()
            print(f"📝 Report saved: {report_path}")
            print()
            print("Next steps:")
            print(f"1. Review report: {report_path}")
            print("2. Upload to GitHub: https://github.com/asifhussain60/CORTEX/issues/new")
            print("3. Copy report content into issue description")
    
    def report_bug(
        self,
        title: str,
        description: str,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        operation_attempted: Optional[str] = None,
        frequency: str = "once",
        workaround_exists: bool = False,
    ):
        """
        Quick bug report (non-interactive).
        
        Args:
            title: Bug title
            description: Detailed description
            priority: Bug priority
            error_message: Error message (if any)
            stack_trace: Stack trace (if any)
            operation_attempted: What operation was attempted
            frequency: How often bug occurs
            workaround_exists: Whether workaround exists
        """
        self.collector.submit_feedback(
            category=FeedbackCategory.BUG,
            title=title,
            description=description,
            priority=priority,
            error_message=error_message,
            stack_trace=stack_trace,
            operation_attempted=operation_attempted,
            frequency=frequency,
            workaround_exists=workaround_exists,
        )
        
        logger.info(f"Bug report submitted: {title}")
    
    def request_feature(
        self,
        title: str,
        description: str,
        priority: FeedbackPriority = FeedbackPriority.ENHANCEMENT,
        use_case: Optional[str] = None,
    ):
        """
        Quick feature request (non-interactive).
        
        Args:
            title: Feature title
            description: Detailed description
            priority: Request priority
            use_case: Use case description
        """
        full_description = description
        if use_case:
            full_description += f"\n\n**Use Case:**\n{use_case}"
        
        self.collector.submit_feedback(
            category=FeedbackCategory.FEATURE_REQUEST,
            title=title,
            description=full_description,
            priority=priority,
        )
        
        logger.info(f"Feature request submitted: {title}")
    
    def suggest_improvement(
        self,
        title: str,
        description: str,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        current_behavior: Optional[str] = None,
        proposed_behavior: Optional[str] = None,
    ):
        """
        Quick improvement suggestion (non-interactive).
        
        Args:
            title: Improvement title
            description: Detailed description
            priority: Suggestion priority
            current_behavior: How it works now
            proposed_behavior: How it should work
        """
        full_description = description
        if current_behavior:
            full_description += f"\n\n**Current Behavior:**\n{current_behavior}"
        if proposed_behavior:
            full_description += f"\n\n**Proposed Behavior:**\n{proposed_behavior}"
        
        self.collector.submit_feedback(
            category=FeedbackCategory.IMPROVEMENT,
            title=title,
            description=full_description,
            priority=priority,
        )
        
        logger.info(f"Improvement suggestion submitted: {title}")
    
    def generate_report(
        self,
        format: ReportFormat = ReportFormat.JSON,
        include_github_issues: bool = True,
    ) -> Path:
        """
        Generate feedback report.
        
        Args:
            format: Report format (JSON/YAML/Markdown)
            include_github_issues: Also generate GitHub Issues file
        
        Returns:
            Path to generated report
        """
        # Generate main report
        report = self.generator.generate_report()
        report_path = self.generator.save_report(report, format=format)
        
        # Generate GitHub Issues file
        if include_github_issues and report.total_items > 0:
            issues = self.formatter.format_report_as_issues(report)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            issues_path = self.output_dir / f"github_issues_{timestamp}.md"
            
            content = self.formatter.export_for_cli_upload(issues, "markdown")
            issues_path.write_text(content, encoding='utf-8')
            
            logger.info(f"GitHub Issues file created: {issues_path}")
        
        return report_path
    
    def get_recent_errors(self, limit: int = 5) -> list:
        """
        Get recent errors from collector.
        
        Args:
            limit: Maximum number of errors
        
        Returns:
            List of recent error feedback items
        """
        all_feedback = self.collector.get_all_feedback()
        errors = [
            item for item in all_feedback
            if item.category == FeedbackCategory.BUG and item.error_message
        ]
        
        # Sort by timestamp (newest first)
        errors.sort(key=lambda x: x.timestamp, reverse=True)
        
        return errors[:limit]
    
    def get_usage_summary(self) -> dict:
        """
        Get usage patterns summary.
        
        Returns:
            Dictionary with usage statistics
        """
        patterns = self.collector.get_usage_patterns()
        
        summary = {
            'total_operations': len(patterns),
            'total_uses': sum(p['total_uses'] for p in patterns.values()),
            'total_failures': sum(p['failures'] for p in patterns.values()),
            'most_used': None,
            'least_successful': None,
        }
        
        if patterns:
            # Most used operation
            most_used = max(patterns.items(), key=lambda x: x[1]['total_uses'])
            summary['most_used'] = {
                'operation': most_used[0],
                'uses': most_used[1]['total_uses'],
                'success_rate': (
                    most_used[1]['successes'] / most_used[1]['total_uses']
                    if most_used[1]['total_uses'] > 0 else 0
                ),
            }
            
            # Least successful operation (with at least 3 uses)
            qualified = {
                op: data for op, data in patterns.items()
                if data['total_uses'] >= 3
            }
            if qualified:
                least_successful = min(
                    qualified.items(),
                    key=lambda x: x[1]['successes'] / x[1]['total_uses']
                    if x[1]['total_uses'] > 0 else 1.0
                )
                summary['least_successful'] = {
                    'operation': least_successful[0],
                    'success_rate': (
                        least_successful[1]['successes'] / least_successful[1]['total_uses']
                        if least_successful[1]['total_uses'] > 0 else 0
                    ),
                    'failures': least_successful[1]['failures'],
                }
        
        return summary


def main():
    """CLI entry point for interactive feedback."""
    entry_point = FeedbackEntryPoint()
    entry_point.start_interactive()


if __name__ == "__main__":
    main()

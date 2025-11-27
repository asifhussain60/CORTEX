"""
Feedback Report Generator

Generates structured reports (JSON/YAML) from collected feedback.
Formats data for GitHub Issues upload.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from .feedback_collector import FeedbackCollector, FeedbackCategory, FeedbackPriority


logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Report output formats."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


@dataclass
class FeedbackReport:
    """Generated feedback report."""
    
    report_id: str
    generated_at: str
    cortex_version: str
    
    # Summary
    total_items: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    
    # Items
    critical_issues: List[Dict[str, Any]]
    high_priority: List[Dict[str, Any]]
    medium_priority: List[Dict[str, Any]]
    low_priority: List[Dict[str, Any]]
    enhancements: List[Dict[str, Any]]
    
    # Usage Patterns
    most_used_operations: List[Dict[str, Any]]
    least_successful_operations: List[Dict[str, Any]]
    
    # Metadata
    environment_diversity: int  # Number of unique environments
    auto_collected_count: int
    user_submitted_count: int


class FeedbackReportGenerator:
    """
    Generates structured reports from collected feedback.
    
    Usage:
        collector = FeedbackCollector()
        generator = FeedbackReportGenerator(collector)
        
        # Generate JSON report
        report = generator.generate_report()
        generator.save_report(report, format=ReportFormat.JSON)
        
        # Or get formatted string
        json_str = generator.format_report(report, ReportFormat.JSON)
    """
    
    def __init__(self, collector: FeedbackCollector):
        """
        Initialize report generator.
        
        Args:
            collector: FeedbackCollector instance with data
        """
        self.collector = collector
    
    def generate_report(self) -> FeedbackReport:
        """
        Generate comprehensive feedback report.
        
        Returns:
            FeedbackReport with aggregated data
        """
        feedback_items = self.collector.get_all_feedback()
        usage_patterns = self.collector.get_usage_patterns()
        
        # Count by category
        by_category = {}
        for category in FeedbackCategory:
            count = len([
                item for item in feedback_items
                if item.category == category
            ])
            if count > 0:
                by_category[category.value] = count
        
        # Count by priority
        by_priority = {}
        for priority in FeedbackPriority:
            count = len([
                item for item in feedback_items
                if item.priority == priority
            ])
            if count > 0:
                by_priority[priority.value] = count
        
        # Group by priority
        critical_issues = [
            item.to_dict() for item in feedback_items
            if item.priority == FeedbackPriority.CRITICAL
        ]
        
        high_priority = [
            item.to_dict() for item in feedback_items
            if item.priority == FeedbackPriority.HIGH
        ]
        
        medium_priority = [
            item.to_dict() for item in feedback_items
            if item.priority == FeedbackPriority.MEDIUM
        ]
        
        low_priority = [
            item.to_dict() for item in feedback_items
            if item.priority == FeedbackPriority.LOW
        ]
        
        enhancements = [
            item.to_dict() for item in feedback_items
            if item.priority == FeedbackPriority.ENHANCEMENT
        ]
        
        # Usage patterns analysis
        most_used = sorted(
            [
                {
                    'operation': op,
                    'total_uses': data['total_uses'],
                    'success_rate': (
                        data['successes'] / data['total_uses']
                        if data['total_uses'] > 0 else 0
                    ),
                }
                for op, data in usage_patterns.items()
            ],
            key=lambda x: x['total_uses'],
            reverse=True
        )[:10]
        
        least_successful = sorted(
            [
                {
                    'operation': op,
                    'success_rate': (
                        data['successes'] / data['total_uses']
                        if data['total_uses'] > 0 else 0
                    ),
                    'total_uses': data['total_uses'],
                    'failures': data['failures'],
                }
                for op, data in usage_patterns.items()
                if data['total_uses'] >= 3  # Only if used at least 3 times
            ],
            key=lambda x: x['success_rate']
        )[:10]
        
        # Environment diversity
        unique_envs = len(set(
            item.environment_hash for item in feedback_items
            if item.environment_hash
        ))
        
        # Auto vs manual collection
        auto_count = len([item for item in feedback_items if item.auto_collected])
        user_count = len([item for item in feedback_items if not item.auto_collected])
        
        return FeedbackReport(
            report_id=self._generate_report_id(),
            generated_at=datetime.now().isoformat(),
            cortex_version=feedback_items[0].cortex_version if feedback_items else "unknown",
            total_items=len(feedback_items),
            by_category=by_category,
            by_priority=by_priority,
            critical_issues=critical_issues,
            high_priority=high_priority,
            medium_priority=medium_priority,
            low_priority=low_priority,
            enhancements=enhancements,
            most_used_operations=most_used,
            least_successful_operations=least_successful,
            environment_diversity=unique_envs,
            auto_collected_count=auto_count,
            user_submitted_count=user_count,
        )
    
    def format_report(
        self,
        report: FeedbackReport,
        format: ReportFormat = ReportFormat.JSON
    ) -> str:
        """
        Format report as string.
        
        Args:
            report: FeedbackReport to format
            format: Output format
        
        Returns:
            Formatted string
        """
        data = self._report_to_dict(report)
        
        if format == ReportFormat.JSON:
            return json.dumps(data, indent=2)
        
        elif format == ReportFormat.YAML:
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        elif format == ReportFormat.MARKDOWN:
            return self._format_markdown(report)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def save_report(
        self,
        report: FeedbackReport,
        output_path: Optional[Path] = None,
        format: ReportFormat = ReportFormat.JSON
    ) -> Path:
        """
        Save report to file.
        
        Args:
            report: FeedbackReport to save
            output_path: Output file path (default: cortex-brain/feedback/report_<timestamp>)
            format: Output format
        
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_dir = Path.cwd() / "cortex-brain" / "feedback"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            ext = format.value
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"feedback_report_{timestamp}.{ext}"
        
        # Format and save
        content = self.format_report(report, format)
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Feedback report saved: {output_path}")
        return output_path
    
    def _report_to_dict(self, report: FeedbackReport) -> Dict[str, Any]:
        """Convert FeedbackReport to dictionary."""
        return {
            'report_id': report.report_id,
            'generated_at': report.generated_at,
            'cortex_version': report.cortex_version,
            'summary': {
                'total_items': report.total_items,
                'by_category': report.by_category,
                'by_priority': report.by_priority,
                'environment_diversity': report.environment_diversity,
                'auto_collected': report.auto_collected_count,
                'user_submitted': report.user_submitted_count,
            },
            'issues': {
                'critical': report.critical_issues,
                'high': report.high_priority,
                'medium': report.medium_priority,
                'low': report.low_priority,
                'enhancements': report.enhancements,
            },
            'usage_patterns': {
                'most_used': report.most_used_operations,
                'least_successful': report.least_successful_operations,
            },
        }
    
    def _format_markdown(self, report: FeedbackReport) -> str:
        """Format report as Markdown."""
        md = []
        
        md.append(f"# CORTEX Feedback Report")
        md.append(f"")
        md.append(f"**Report ID:** {report.report_id}")
        md.append(f"**Generated:** {report.generated_at}")
        md.append(f"**CORTEX Version:** {report.cortex_version}")
        md.append(f"")
        
        md.append(f"## Summary")
        md.append(f"")
        md.append(f"- **Total Items:** {report.total_items}")
        md.append(f"- **Environment Diversity:** {report.environment_diversity} unique environments")
        md.append(f"- **Auto-Collected:** {report.auto_collected_count}")
        md.append(f"- **User-Submitted:** {report.user_submitted_count}")
        md.append(f"")
        
        md.append(f"### By Category")
        md.append(f"")
        for category, count in report.by_category.items():
            md.append(f"- **{category}:** {count}")
        md.append(f"")
        
        md.append(f"### By Priority")
        md.append(f"")
        for priority, count in report.by_priority.items():
            md.append(f"- **{priority}:** {count}")
        md.append(f"")
        
        # Critical issues
        if report.critical_issues:
            md.append(f"## 🔴 Critical Issues ({len(report.critical_issues)})")
            md.append(f"")
            for item in report.critical_issues:
                md.append(f"### {item['title']}")
                md.append(f"")
                md.append(f"- **Category:** {item['category']}")
                md.append(f"- **Timestamp:** {item['timestamp']}")
                md.append(f"")
                md.append(f"{item['description']}")
                md.append(f"")
        
        # High priority
        if report.high_priority:
            md.append(f"## 🟠 High Priority ({len(report.high_priority)})")
            md.append(f"")
            for item in report.high_priority:
                md.append(f"- **{item['title']}** ({item['category']})")
            md.append(f"")
        
        # Usage patterns
        if report.most_used_operations:
            md.append(f"## 📊 Most Used Operations")
            md.append(f"")
            for op in report.most_used_operations:
                md.append(f"- **{op['operation']}:** {op['total_uses']} uses, {op['success_rate']*100:.1f}% success")
            md.append(f"")
        
        if report.least_successful_operations:
            md.append(f"## ⚠️ Operations with Low Success Rate")
            md.append(f"")
            for op in report.least_successful_operations:
                md.append(f"- **{op['operation']}:** {op['success_rate']*100:.1f}% success ({op['failures']} failures / {op['total_uses']} uses)")
            md.append(f"")
        
        return "\n".join(md)
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"CORTEX-FEEDBACK-{timestamp}"

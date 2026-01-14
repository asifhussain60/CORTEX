"""Reporter modules for CORTEX Review Orchestrator v2.0.0"""

from pathlib import Path
from typing import Dict, Any
import yaml
import json

__all__ = ["YAMLReporter", "MarkdownReporter"]


class YAMLReporter:
    """YAML report generator."""
    
    def __init__(self, epic_path: Path):
        self.epic_path = Path(epic_path)
    
    def save_report(self, report: Dict[str, Any], filename: str) -> Path:
        """Save report as YAML."""
        output_dir = self.epic_path / "reports" / "cortex-review"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{filename}.yaml"
        
        with open(output_file, "w") as f:
            yaml.dump(report, f, sort_keys=False, default_flow_style=False)
        
        return output_file


class MarkdownReporter:
    """Markdown report generator."""
    
    def __init__(self, epic_path: Path):
        self.epic_path = Path(epic_path)
    
    def save_report(self, report: Dict[str, Any], filename: str) -> Path:
        """Save report as Markdown."""
        output_dir = self.epic_path / "reports" / "cortex-review"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{filename}.md"
        
        # Convert report to Markdown
        markdown = self._generate_markdown(report)
        
        with open(output_file, "w") as f:
            f.write(markdown)
        
        return output_file
    
    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Generate Markdown from report."""
        lines = []
        
        # Header
        lines.append("# CORTEX Epic Review Report\n")
        
        # Metadata
        meta = report.get("review_metadata", {})
        lines.append("## Metadata\n")
        lines.append(f"- **Timestamp:** {meta.get('timestamp', 'N/A')}")
        lines.append(f"- **Epic Path:** `{meta.get('epic_path', 'N/A')}`")
        lines.append(f"- **Review Type:** {meta.get('review_type', 'N/A')}")
        lines.append(f"- **Orchestrator Version:** {meta.get('orchestrator_version', 'N/A')}")
        lines.append(f"- **Elapsed Time:** {meta.get('elapsed_time_seconds', 0):.2f}s\n")
        
        # Overall Assessment
        assessment = report.get("overall_assessment", {})
        lines.append("## Overall Assessment\n")
        lines.append(f"- **Score:** {assessment.get('score', 0)}/100")
        lines.append(f"- **Status:** {assessment.get('status', 'UNKNOWN')}")
        lines.append(f"- **Severity:** {assessment.get('severity', 'unknown')}")
        lines.append(f"- **Can Progress:** {'✅ Yes' if assessment.get('can_progress', False) else '⛔ No'}\n")
        
        # Blocking Issues
        blocking = report.get("blocking_issues", [])
        if blocking:
            lines.append(f"## ⛔ Blocking Issues ({len(blocking)})\n")
            for i, issue in enumerate(blocking, 1):
                lines.append(f"### {i}. {issue.get('condition', 'Unknown')}")
                lines.append(f"- **Severity:** {issue.get('severity', 'unknown')}")
                lines.append(f"- **Message:** {issue.get('message', 'No message')}\n")
        
        # Phase Scores
        scores = report.get("phase_scores", {})
        if scores:
            lines.append("## Phase Scores\n")
            for phase, score in scores.items():
                lines.append(f"- **{phase.capitalize()}:** {score}/100")
            lines.append("")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            lines.append(f"## Recommendations ({len(recommendations)})\n")
            for i, rec in enumerate(recommendations[:10], 1):  # Top 10
                lines.append(f"### {i}. [{rec.get('priority', 'medium').upper()}] {rec.get('category', 'General')}")
                lines.append(f"{rec.get('recommendation', 'No recommendation')}\n")
        
        # Summary
        summary = report.get("summary", {})
        if summary:
            lines.append("## Summary\n")
            lines.append(f"- **Total Issues:** {summary.get('total_issues', 0)}")
            lines.append(f"- **Blocking Issues:** {summary.get('blocking_issues', 0)}")
            lines.append(f"- **Critical Recommendations:** {summary.get('critical_recommendations', 0)}")
            lines.append(f"- **Validation Status:** {summary.get('validation_status', 'UNKNOWN')}")
            lines.append(f"- **Next Action:** {summary.get('next_action', 'Review complete')}\n")
        
        return "\n".join(lines)

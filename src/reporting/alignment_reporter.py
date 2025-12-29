"""
Alignment Reporter - Generate formatted reports from alignment validation results

Formats AlignmentReport into:
- Executive summary with health score
- Feature integration dashboard (Markdown table)
- Critical issues and warnings
- Auto-remediation suggestions
- Deployment gate results

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class AlignmentReporter:
    """Generates formatted alignment reports"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
    
    def generate_report(self, alignment_report: Any) -> str:
        """
        Generate comprehensive alignment report in Markdown format.
        
        Args:
            alignment_report: AlignmentReport object from SystemAlignmentOrchestrator
        
        Returns:
            Formatted Markdown report string
        """
        sections = []
        
        # Header
        sections.append(self._generate_header(alignment_report))
        
        # Executive Summary
        sections.append(self._generate_executive_summary(alignment_report))
        
        # Feature Integration Dashboard
        sections.append(self._generate_feature_dashboard(alignment_report))
        
        # Critical Issues
        if alignment_report.critical_issues > 0:
            sections.append(self._generate_critical_issues(alignment_report))
        
        # Warnings
        if alignment_report.warnings > 0:
            sections.append(self._generate_warnings(alignment_report))
        
        # Auto-Remediation Suggestions
        if hasattr(alignment_report, 'remediation_suggestions') and alignment_report.remediation_suggestions:
            sections.append(self._generate_remediation_section(alignment_report))
        
        # Deployment Gates
        if hasattr(alignment_report, 'deployment_gate_results'):
            sections.append(self._generate_deployment_gates(alignment_report))
        
        # Orphaned Triggers / Ghost Features
        if alignment_report.orphaned_triggers or alignment_report.ghost_features:
            sections.append(self._generate_wiring_issues(alignment_report))
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self, report: Any) -> str:
        """Generate report header"""
        timestamp = report.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# CORTEX System Alignment Report

**Generated:** {timestamp}  
**Overall Health:** {report.overall_health}% {self._get_health_emoji(report.overall_health)}  
**Critical Issues:** {report.critical_issues}  
**Warnings:** {report.warnings}  

---"""
    
    def _generate_executive_summary(self, report: Any) -> str:
        """Generate executive summary"""
        total_features = len(report.feature_scores)
        healthy_features = sum(1 for s in report.feature_scores.values() if s.score >= 90)
        warning_features = sum(1 for s in report.feature_scores.values() if 70 <= s.score < 90)
        critical_features = sum(1 for s in report.feature_scores.values() if s.score < 70)
        
        summary = f"""## Executive Summary

**Total Features Analyzed:** {total_features}

**Health Distribution:**
- ✅ Healthy (90%+): {healthy_features} features
- ⚠️ Warning (70-89%): {warning_features} features
- ❌ Critical (<70%): {critical_features} features"""
        
        if report.is_healthy:
            summary += "\n\n**Status:** ✅ System is healthy - all features meet integration standards"
        else:
            summary += f"\n\n**Status:** ⚠️ System requires attention - {report.issues_found} issues detected"
        
        return summary + "\n\n---"
    
    def _generate_feature_dashboard(self, report: Any) -> str:
        """Generate feature integration dashboard table"""
        dashboard = """## Feature Integration Dashboard

| Feature | Type | Score | Status | Issues |
|---------|------|-------|--------|--------|"""
        
        # Sort features by score (lowest first)
        sorted_features = sorted(
            report.feature_scores.items(),
            key=lambda x: x[1].score
        )
        
        for name, score in sorted_features:
            feature_type = score.feature_type.capitalize()
            score_pct = f"{score.score}%"
            status = score.status
            issues = ", ".join(score.issues) if score.issues else "None"
            
            dashboard += f"\n| {name} | {feature_type} | {score_pct} | {status} | {issues} |"
        
        return dashboard + "\n\n---"
    
    def _generate_critical_issues(self, report: Any) -> str:
        """Generate critical issues section"""
        section = f"""## Critical Issues

**{report.critical_issues} critical issue(s) detected:**

"""
        
        critical_features = [
            (name, score)
            for name, score in report.feature_scores.items()
            if score.score < 70
        ]
        
        for idx, (name, score) in enumerate(critical_features, 1):
            section += f"""### {idx}. {name} ({score.score}% integration)

**Issues:**
"""
            for issue in score.issues:
                section += f"- {issue}\n"
            
            section += f"\n**Action Required:** "
            if score.score < 40:
                section += f"Consider removing feature or completing integration immediately\n"
            else:
                section += f"Complete integration requirements or mark as deprecated\n"
            
            section += "\n"
        
        return section + "---"
    
    def _generate_warnings(self, report: Any) -> str:
        """Generate warnings section"""
        section = f"""## Warnings

**{report.warnings} warning(s) detected:**

"""
        
        warning_features = [
            (name, score)
            for name, score in report.feature_scores.items()
            if 70 <= score.score < 90
        ]
        
        for idx, (name, score) in enumerate(warning_features, 1):
            section += f"{idx}. **{name}** ({score.score}% integration) - {', '.join(score.issues)}\n"
        
        return section + "\n---"
    
    def _generate_remediation_section(self, report: Any) -> str:
        """Generate auto-remediation suggestions section"""
        section = f"""## Auto-Remediation Suggestions

**{len(report.remediation_suggestions)} suggestion(s) generated:**

"""
        
        # Group suggestions by feature
        by_feature: Dict[str, List[Any]] = {}
        for suggestion in report.remediation_suggestions:
            feature_name = suggestion.feature_name
            if feature_name not in by_feature:
                by_feature[feature_name] = []
            by_feature[feature_name].append(suggestion)
        
        for feature_name, suggestions in by_feature.items():
            section += f"### {feature_name}\n\n"
            
            for suggestion in suggestions:
                if suggestion.suggestion_type == "wiring":
                    section += "**Issue:** Not wired to entry point\n\n"
                    section += "**Suggested Wiring:**\n```yaml\n"
                    section += suggestion.content
                    section += "\n```\n\n"
                
                elif suggestion.suggestion_type == "test":
                    section += "**Issue:** No test coverage\n\n"
                    section += f"**Suggested Test Skeleton:** `{suggestion.file_path}`\n```python\n"
                    # Show first 20 lines of test skeleton
                    lines = suggestion.content.split('\n')[:20]
                    section += '\n'.join(lines)
                    if len(suggestion.content.split('\n')) > 20:
                        section += "\n... (truncated)"
                    section += "\n```\n\n"
                
                elif suggestion.suggestion_type == "documentation":
                    section += "**Issue:** Missing documentation\n\n"
                    section += f"**Suggested Documentation:** `{suggestion.file_path}`\n```markdown\n"
                    # Show first 15 lines of documentation
                    lines = suggestion.content.split('\n')[:15]
                    section += '\n'.join(lines)
                    if len(suggestion.content.split('\n')) > 15:
                        section += "\n... (truncated)"
                    section += "\n```\n\n"
            
            section += "---\n\n"
        
        return section
    
    def _generate_deployment_gates(self, report: Any) -> str:
        """Generate deployment gates section"""
        gates = report.deployment_gate_results
        
        section = f"""## Deployment Readiness

**Status:** {'✅ Ready' if gates.get('passed', False) else '❌ Not Ready'}

"""
        
        if gates.get('errors'):
            section += "**Errors (Must Fix):**\n"
            for error in gates['errors']:
                section += f"- ❌ {error}\n"
            section += "\n"
        
        if gates.get('warnings'):
            section += "**Warnings (Should Fix):**\n"
            for warning in gates['warnings']:
                section += f"- ⚠️ {warning}\n"
            section += "\n"
        
        if not gates.get('errors') and not gates.get('warnings'):
            section += "✅ All deployment gates passed - ready for production deployment\n\n"
        
        return section + "---"
    
    def _generate_wiring_issues(self, report: Any) -> str:
        """Generate orphaned triggers and ghost features section"""
        section = """## Entry Point Wiring Issues

"""
        
        if report.orphaned_triggers:
            section += f"**Orphaned Triggers ({len(report.orphaned_triggers)}):**\n"
            section += "*Triggers configured without corresponding orchestrator*\n\n"
            for trigger in report.orphaned_triggers:
                section += f"- `{trigger}` - No orchestrator found\n"
            section += "\n"
        
        if report.ghost_features:
            section += f"**Ghost Features ({len(report.ghost_features)}):**\n"
            section += "*Orchestrators exist but no entry point trigger configured*\n\n"
            for feature in report.ghost_features:
                section += f"- `{feature}` - Not accessible via triggers\n"
            section += "\n"
        
        return section + "---"
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return """---

**Generated by:** CORTEX System Alignment  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0"""
    
    def _get_health_emoji(self, health: int) -> str:
        """Get emoji for health score"""
        if health >= 90:
            return "✅"
        elif health >= 70:
            return "⚠️"
        else:
            return "❌"
    
    def save_report(self, alignment_report: Any, output_path: Optional[Path] = None) -> Path:
        """
        Generate and save report to file.
        
        Args:
            alignment_report: AlignmentReport object
            output_path: Optional custom output path
        
        Returns:
            Path where report was saved
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_path = self.project_root / "cortex-brain" / "documents" / "reports" / f"ALIGNMENT-REPORT-{timestamp}.md"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_content = self.generate_report(alignment_report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return output_path

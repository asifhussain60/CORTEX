"""
Metrics Reporter

Generates comprehensive refinement reports in multiple formats.

Author: Asif Hussain
Created: January 3, 2026
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MetricsReporter:
    """Generate refinement metrics reports."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_comprehensive_report(self, session_id: str, results: Dict[str, Any],
                                     target_path: Path) -> Path:
        """
        Generate comprehensive refinement report.
        
        Args:
            session_id: Refinement session ID
            results: Phase results dictionary
            target_path: Target path that was refined
            
        Returns:
            Path to generated report
        """
        report_data = {
            "session_id": session_id,
            "generated_at": datetime.now().isoformat(),
            "target": str(target_path),
            "summary": self._generate_summary(results),
            "phase_results": results,
            "recommendations": self._generate_recommendations(results)
        }
        
        # Generate JSON report
        json_report = self.output_dir / f"refinement-report-{session_id}.json"
        with open(json_report, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        html_report = self.output_dir / f"refinement-report-{session_id}.html"
        self._generate_html_report(report_data, html_report)
        
        # Generate markdown summary
        md_report = self.output_dir / f"refinement-summary-{session_id}.md"
        self._generate_markdown_summary(report_data, md_report)
        
        logger.info(f"Reports generated: {json_report}, {html_report}, {md_report}")
        
        return json_report
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary."""
        summary = {
            "phases_completed": len(results),
            "overall_status": "completed" if len(results) >= 7 else "partial"
        }
        
        # Extract key metrics
        if "QualityAssessment" in results:
            summary["quality_score"] = results["QualityAssessment"].get("quality_score", 0)
            summary["issues_found"] = len(results["QualityAssessment"].get("issues", []))
        
        if "DuplicateDetection" in results:
            summary["duplicates_found"] = results["DuplicateDetection"].get("duplicates_found", 0)
        
        if "SecurityAudit" in results:
            summary["security_score"] = results["SecurityAudit"].get("security_score", 0)
            summary["high_security_issues"] = results["SecurityAudit"].get("high_severity", 0)
        
        if "RefactoringPlan" in results:
            summary["refactoring_tasks"] = len(results["RefactoringPlan"].get("refactoring_tasks", []))
        
        if "ValidationMetrics" in results:
            summary["overall_improvement"] = results["ValidationMetrics"].get("improvements", {}).get(
                "overall_improvement_percentage", 0
            )
        
        return summary
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Quality recommendations
        if "QualityAssessment" in results:
            quality_score = results["QualityAssessment"].get("quality_score", 0)
            if quality_score < 70:
                recommendations.append(
                    "Quality score is below 70. Prioritize fixing high-severity issues."
                )
        
        # Security recommendations
        if "SecurityAudit" in results:
            high_security = results["SecurityAudit"].get("high_severity", 0)
            if high_security > 0:
                recommendations.append(
                    f"Address {high_security} high-severity security issues immediately."
                )
        
        # Performance recommendations
        if "PerformanceAnalysis" in results:
            perf_score = results["PerformanceAnalysis"].get("performance_score", 100)
            if perf_score < 70:
                recommendations.append(
                    "Performance score indicates potential bottlenecks. Review and optimize."
                )
        
        # Duplicate recommendations
        if "DuplicateDetection" in results:
            duplicates = results["DuplicateDetection"].get("duplicates_found", 0)
            if duplicates > 0:
                recommendations.append(
                    f"Found {duplicates} duplicate code blocks. Consider consolidation to improve maintainability."
                )
        
        return recommendations
    
    def _generate_html_report(self, data: Dict[str, Any], output_path: Path) -> None:
        """Generate HTML report."""
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Refinement Report - {data['session_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; padding: 15px 20px; 
                   background: #ecf0f1; border-radius: 5px; }}
        .metric-label {{ font-size: 0.9em; color: #7f8c8d; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #2c3e50; }}
        .score-good {{ color: #27ae60; }}
        .score-warning {{ color: #f39c12; }}
        .score-critical {{ color: #e74c3c; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Refinement Report</h1>
        <p><strong>Session ID:</strong> {data['session_id']}</p>
        <p><strong>Target:</strong> {data['target']}</p>
        <p><strong>Generated:</strong> {data['generated_at']}</p>
        
        <h2>📊 Summary</h2>
        <div class="metric">
            <div class="metric-label">Quality Score</div>
            <div class="metric-value score-good">{data['summary'].get('quality_score', 'N/A')}/100</div>
        </div>
        <div class="metric">
            <div class="metric-label">Security Score</div>
            <div class="metric-value score-good">{data['summary'].get('security_score', 'N/A')}/100</div>
        </div>
        <div class="metric">
            <div class="metric-label">Issues Found</div>
            <div class="metric-value">{data['summary'].get('issues_found', 'N/A')}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Duplicates</div>
            <div class="metric-value">{data['summary'].get('duplicates_found', 'N/A')}</div>
        </div>
        
        <h2>💡 Recommendations</h2>
        {''.join(f'<div class="recommendation">{rec}</div>' for rec in data['recommendations'])}
        
        <h2>📈 Phase Results</h2>
        <p>Completed {data['summary']['phases_completed']} phases</p>
        
        <p style="margin-top: 40px; color: #7f8c8d; font-size: 0.9em;">
            Generated by CORTEX Refinement Orchestrator v1.0.0
        </p>
    </div>
</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _generate_markdown_summary(self, data: Dict[str, Any], output_path: Path) -> None:
        """Generate markdown summary."""
        # Build recommendations list
        rec_list = '\n'.join(f'- {rec}' for rec in data['recommendations'])
        
        md_content = f"""# 🎨 Refinement Summary

**Session ID:** `{data['session_id']}`  
**Target:** `{data['target']}`  
**Generated:** {data['generated_at']}

## 📊 Metrics

- **Quality Score:** {data['summary'].get('quality_score', 'N/A')}/100
- **Security Score:** {data['summary'].get('security_score', 'N/A')}/100
- **Issues Found:** {data['summary'].get('issues_found', 'N/A')}
- **Duplicates:** {data['summary'].get('duplicates_found', 'N/A')}
- **Refactoring Tasks:** {data['summary'].get('refactoring_tasks', 'N/A')}

## 💡 Recommendations

{rec_list}

## ✅ Status

Phases Completed: {data['summary']['phases_completed']}/7

---

*Generated by CORTEX Refinement Orchestrator v1.0.0*
"""
        
        with open(output_path, 'w') as f:
            f.write(md_content)

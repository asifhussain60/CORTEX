"""
Report Generator Engine - Generate comprehensive sanitization reports.

Features:
- Multi-format support (markdown, JSON, HTML)
- Diff summary generation
- Risk metrics aggregation
- Change statistics
- Jinja2 template rendering
- Detailed transformation logs

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ReportFormat(str, Enum):
    """Supported report formats."""
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


@dataclass
class ChangeStatistics:
    """Statistics about code changes."""
    total_files_analyzed: int = 0
    files_modified: int = 0
    files_skipped: int = 0
    total_transformations: int = 0
    auto_approved: int = 0
    manually_approved: int = 0
    rejected: int = 0
    
    # Risk breakdown
    safe_transformations: int = 0
    low_risk_transformations: int = 0
    medium_risk_transformations: int = 0
    high_risk_transformations: int = 0
    critical_transformations: int = 0


@dataclass
class DiffSummary:
    """Summary of code differences."""
    file_path: str
    lines_added: int
    lines_removed: int
    lines_modified: int
    diff_preview: str  # First 10 lines of diff


@dataclass
class SanitizationReport:
    """Complete sanitization report."""
    timestamp: str
    codebase_path: str
    status: str
    duration_seconds: float
    
    # Statistics
    statistics: ChangeStatistics
    
    # Detailed results
    diffs: List[DiffSummary] = field(default_factory=list)
    validation_passed: bool = True
    error: Optional[str] = None
    
    # Metadata
    dry_run: bool = False
    config_used: Dict[str, Any] = field(default_factory=dict)


class ReportGeneratorEngine:
    """
    Report generator engine for sanitization results.
    
    Generates comprehensive reports including:
    1. Change statistics
    2. Diff summaries
    3. Risk metrics
    4. Validation results
    5. Transformation logs
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize report generator engine.
        
        Args:
            config: Configuration dictionary from orchestrator
        """
        self.config = config
        self.reporting_config = config.get('reporting', {})
        
        # Format settings
        self.formats = self.reporting_config.get('formats', ['markdown', 'json'])
        self.output_directory = Path(self.reporting_config.get('output_directory', 'reports'))
        
        # Create output directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"Initialized ReportGeneratorEngine "
            f"(formats={self.formats}, output={self.output_directory})"
        )
    
    def generate_report(
        self,
        codebase_path: Path,
        analysis_result: Any,  # From CodeAnalyzerEngine
        mapping_result: Any,  # From MappingEngine
        transformation_result: Any,  # From TransformerEngine
        validation_result: Any,  # From ValidatorEngine
        dry_run: bool = False
    ) -> SanitizationReport:
        """
        Generate comprehensive sanitization report.
        
        Args:
            codebase_path: Root directory of codebase
            analysis_result: Analysis results
            mapping_result: Mapping results
            transformation_result: Transformation results
            validation_result: Validation results
            dry_run: If True, dry-run mode was used
        
        Returns:
            SanitizationReport
        """
        logger.info(f"Generating sanitization report for: {codebase_path}")
        
        try:
            # Calculate statistics
            statistics = self._calculate_statistics(
                analysis_result,
                mapping_result,
                transformation_result
            )
            
            # Generate diff summaries
            diffs = self._generate_diffs(transformation_result)
            
            # Create report
            report = SanitizationReport(
                timestamp=datetime.now().isoformat(),
                codebase_path=str(codebase_path),
                status="completed" if validation_result.validation_passed else "failed",
                duration_seconds=(
                    getattr(analysis_result, 'duration_seconds', 0) +
                    getattr(mapping_result, 'duration_seconds', 0) +
                    getattr(transformation_result, 'duration_seconds', 0) +
                    getattr(validation_result, 'duration_seconds', 0)
                ),
                statistics=statistics,
                diffs=diffs,
                validation_passed=validation_result.validation_passed,
                error=validation_result.error,
                dry_run=dry_run,
                config_used=self._extract_config_summary()
            )
            
            # Save in configured formats
            self._save_reports(report)
            
            logger.info(f"Generated report: {report.status}")
            
            return report
        
        except Exception as e:
            logger.error(f"Report generation error: {e}", exc_info=True)
            
            # Return minimal error report
            return SanitizationReport(
                timestamp=datetime.now().isoformat(),
                codebase_path=str(codebase_path),
                status="error",
                duration_seconds=0.0,
                statistics=ChangeStatistics(),
                error=str(e),
                dry_run=dry_run
            )
    
    def _calculate_statistics(
        self,
        analysis_result: Any,
        mapping_result: Any,
        transformation_result: Any
    ) -> ChangeStatistics:
        """Calculate change statistics from results."""
        stats = ChangeStatistics()
        
        # Files analyzed
        if hasattr(analysis_result, 'files_analyzed'):
            stats.total_files_analyzed = len(analysis_result.files_analyzed)
        
        # Transformations
        if hasattr(mapping_result, 'mappings'):
            stats.total_transformations = len(mapping_result.mappings)
            
            # Count by approval status
            for mapping in mapping_result.mappings:
                if getattr(mapping, 'auto_approved', False):
                    stats.auto_approved += 1
                elif getattr(mapping, 'approved', False):
                    stats.manually_approved += 1
                else:
                    stats.rejected += 1
                
                # Count by risk level
                risk_level = getattr(mapping, 'risk_level', 'SAFE')
                if risk_level == 'SAFE':
                    stats.safe_transformations += 1
                elif risk_level == 'LOW':
                    stats.low_risk_transformations += 1
                elif risk_level == 'MEDIUM':
                    stats.medium_risk_transformations += 1
                elif risk_level == 'HIGH':
                    stats.high_risk_transformations += 1
                elif risk_level == 'CRITICAL':
                    stats.critical_transformations += 1
        
        # Files modified
        if hasattr(transformation_result, 'files_modified'):
            stats.files_modified = len(transformation_result.files_modified)
        
        return stats
    
    def _generate_diffs(self, transformation_result: Any) -> List[DiffSummary]:
        """Generate diff summaries for modified files."""
        diffs = []
        
        if hasattr(transformation_result, 'operations'):
            for op in transformation_result.operations:
                if hasattr(op, 'file_path') and hasattr(op, 'original_content') and hasattr(op, 'new_content'):
                    diff = self._calculate_diff(
                        op.file_path,
                        op.original_content,
                        op.new_content
                    )
                    if diff:
                        diffs.append(diff)
        
        return diffs
    
    def _calculate_diff(
        self,
        file_path: str,
        original: str,
        modified: str
    ) -> Optional[DiffSummary]:
        """Calculate diff for a single file."""
        original_lines = original.split('\n')
        modified_lines = modified.split('\n')
        
        # Simple diff calculation
        lines_added = len(modified_lines) - len(original_lines)
        lines_removed = 0 if lines_added > 0 else abs(lines_added)
        lines_added = max(0, lines_added)
        
        # Calculate modified lines (simplified)
        lines_modified = min(len(original_lines), len(modified_lines))
        
        # Generate preview (first 10 lines)
        preview_lines = []
        for i, (orig, mod) in enumerate(zip(original_lines[:10], modified_lines[:10])):
            if orig != mod:
                preview_lines.append(f"- {orig}")
                preview_lines.append(f"+ {mod}")
        
        diff_preview = '\n'.join(preview_lines) if preview_lines else "No preview available"
        
        return DiffSummary(
            file_path=file_path,
            lines_added=lines_added,
            lines_removed=lines_removed,
            lines_modified=lines_modified,
            diff_preview=diff_preview[:500]  # Limit preview size
        )
    
    def _save_reports(self, report: SanitizationReport):
        """Save report in configured formats."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for format_name in self.formats:
            try:
                if format_name == 'markdown':
                    self._save_markdown_report(report, timestamp)
                elif format_name == 'json':
                    self._save_json_report(report, timestamp)
                elif format_name == 'html':
                    self._save_html_report(report, timestamp)
            except Exception as e:
                logger.error(f"Error saving {format_name} report: {e}")
    
    def _save_markdown_report(self, report: SanitizationReport, timestamp: str):
        """Save report as markdown."""
        output_file = self.output_directory / f"sanitization-report-{timestamp}.md"
        
        content = f"""# Sanitization Report

**Generated:** {report.timestamp}  
**Codebase:** `{report.codebase_path}`  
**Status:** {report.status}  
**Duration:** {report.duration_seconds:.1f}s  
**Mode:** {'DRY-RUN' if report.dry_run else 'PRODUCTION'}

---

## Summary Statistics

- **Files Analyzed:** {report.statistics.total_files_analyzed}
- **Files Modified:** {report.statistics.files_modified}
- **Total Transformations:** {report.statistics.total_transformations}

### Approval Breakdown

- **Auto-Approved:** {report.statistics.auto_approved}
- **Manually Approved:** {report.statistics.manually_approved}
- **Rejected:** {report.statistics.rejected}

### Risk Breakdown

- **SAFE:** {report.statistics.safe_transformations}
- **LOW:** {report.statistics.low_risk_transformations}
- **MEDIUM:** {report.statistics.medium_risk_transformations}
- **HIGH:** {report.statistics.high_risk_transformations}
- **CRITICAL:** {report.statistics.critical_transformations}

---

## Validation

**Validation Passed:** {'✅ YES' if report.validation_passed else '❌ NO'}

{f'**Error:** {report.error}' if report.error else ''}

---

## File Changes

"""
        
        for diff in report.diffs[:10]:  # Limit to 10 diffs
            content += f"""
### `{diff.file_path}`

- **Lines Added:** {diff.lines_added}
- **Lines Removed:** {diff.lines_removed}
- **Lines Modified:** {diff.lines_modified}

```diff
{diff.diff_preview}
```

"""
        
        if len(report.diffs) > 10:
            content += f"\n*... and {len(report.diffs) - 10} more files*\n"
        
        output_file.write_text(content)
        logger.info(f"Saved markdown report: {output_file}")
    
    def _save_json_report(self, report: SanitizationReport, timestamp: str):
        """Save report as JSON."""
        output_file = self.output_directory / f"sanitization-report-{timestamp}.json"
        
        # Convert report to dict
        report_dict = asdict(report)
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        logger.info(f"Saved JSON report: {output_file}")
    
    def _save_html_report(self, report: SanitizationReport, timestamp: str):
        """Save report as HTML (simplified without Jinja2)."""
        output_file = self.output_directory / f"sanitization-report-{timestamp}.html"
        
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Sanitization Report - {report.timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        pre {{ background: #f0f0f0; padding: 10px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>Sanitization Report</h1>
    <p><strong>Generated:</strong> {report.timestamp}</p>
    <p><strong>Codebase:</strong> <code>{report.codebase_path}</code></p>
    <p><strong>Status:</strong> {report.status}</p>
    <p><strong>Duration:</strong> {report.duration_seconds:.1f}s</p>
    
    <div class="stats">
        <h2>Statistics</h2>
        <ul>
            <li>Files Analyzed: {report.statistics.total_files_analyzed}</li>
            <li>Files Modified: {report.statistics.files_modified}</li>
            <li>Total Transformations: {report.statistics.total_transformations}</li>
        </ul>
    </div>
    
    <h2>Validation</h2>
    <p class="{'success' if report.validation_passed else 'error'}">
        {'✅ PASSED' if report.validation_passed else '❌ FAILED'}
    </p>
</body>
</html>"""
        
        output_file.write_text(html)
        logger.info(f"Saved HTML report: {output_file}")
    
    def _extract_config_summary(self) -> Dict[str, Any]:
        """Extract key configuration settings for report."""
        return {
            'formats': self.formats,
            'output_directory': str(self.output_directory),
            'timestamp': datetime.now().isoformat()
        }

"""
File Bloat Detector for CORTEX

Detects and reports files exceeding size thresholds to prevent bloat.
Part of Phase 8: File Bloat Prevention System.

Thresholds:
- YAML files: 2000 lines / 100KB
- Python files: 1000 lines / 50KB
- Markdown files: 1500 lines / 75KB
- JSON files: 500 lines / 25KB

Usage:
    python -m src.operations.modules.quality.bloat_detector
    python -m src.operations.modules.quality.bloat_detector --refactor

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types for bloat detection."""
    YAML = "yaml"
    PYTHON = "py"
    MARKDOWN = "md"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class BloatThreshold:
    """Threshold configuration for file type."""
    file_type: FileType
    max_lines: int
    max_kb: int


@dataclass
class BloatReport:
    """Report for a bloated file."""
    file_path: Path
    file_type: FileType
    lines: int
    kb: float
    threshold_lines: int
    threshold_kb: int
    lines_over: int
    kb_over: float
    severity: str  # 'warning' or 'critical'
    suggestions: List[str]


class BloatDetector:
    """
    Detects and reports file bloat across CORTEX.
    
    Features:
    - Configurable thresholds by file type
    - Refactoring suggestions
    - Git staging area scanning
    - Severity classification
    """
    
    THRESHOLDS = {
        FileType.YAML: BloatThreshold(FileType.YAML, max_lines=2000, max_kb=100),
        FileType.PYTHON: BloatThreshold(FileType.PYTHON, max_lines=1000, max_kb=50),
        FileType.MARKDOWN: BloatThreshold(FileType.MARKDOWN, max_lines=1500, max_kb=75),
        FileType.JSON: BloatThreshold(FileType.JSON, max_lines=500, max_kb=25),
    }
    
    # Directories to exclude from scanning
    EXCLUDE_DIRS = {
        '.git', '.venv', 'venv', '__pycache__', 'node_modules',
        'archive', 'archive_*', '.pytest_cache', 'htmlcov'
    }
    
    def __init__(self, project_root: Path = None):
        """
        Initialize bloat detector.
        
        Args:
            project_root: Path to project root (defaults to CWD)
        """
        self.project_root = project_root or Path.cwd()
    
    def scan_codebase(self) -> List[BloatReport]:
        """
        Scan entire codebase for bloated files.
        
        Returns:
            List of bloat reports for files exceeding thresholds
        """
        bloated_files = []
        
        for file_type in [FileType.YAML, FileType.PYTHON, FileType.MARKDOWN, FileType.JSON]:
            threshold = self.THRESHOLDS[file_type]
            pattern = f"**/*.{file_type.value}"
            
            for file_path in self.project_root.rglob(pattern):
                # Skip excluded directories
                if any(exclude in file_path.parts for exclude in self.EXCLUDE_DIRS):
                    continue
                
                # Check file against threshold
                report = self._check_file(file_path, threshold)
                if report:
                    bloated_files.append(report)
        
        return bloated_files
    
    def scan_staged_files(self) -> List[BloatReport]:
        """
        Scan git staged files for bloat (for pre-commit hook).
        
        Returns:
            List of bloat reports for staged files exceeding thresholds
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            staged_files = result.stdout.strip().split('\n')
            bloated_files = []
            
            for file_path_str in staged_files:
                if not file_path_str:
                    continue
                
                file_path = self.project_root / file_path_str
                if not file_path.exists():
                    continue
                
                file_type = self._detect_file_type(file_path)
                if file_type == FileType.UNKNOWN:
                    continue
                
                threshold = self.THRESHOLDS[file_type]
                report = self._check_file(file_path, threshold)
                if report:
                    bloated_files.append(report)
            
            return bloated_files
        
        except subprocess.CalledProcessError:
            logger.warning("Failed to get staged files from git")
            return []
    
    def _check_file(self, file_path: Path, threshold: BloatThreshold) -> BloatReport:
        """
        Check if file exceeds threshold.
        
        Args:
            file_path: Path to file
            threshold: Threshold configuration
        
        Returns:
            BloatReport if file exceeds threshold, None otherwise
        """
        try:
            # Get file metrics
            lines = len(file_path.read_text(encoding='utf-8', errors='ignore').split('\n'))
            kb = file_path.stat().st_size / 1024
            
            # Check thresholds
            lines_over = lines - threshold.max_lines
            kb_over = kb - threshold.max_kb
            
            if lines_over > 0 or kb_over > 0:
                # Determine severity
                severity = self._determine_severity(lines, threshold.max_lines, kb, threshold.max_kb)
                
                # Generate suggestions
                suggestions = self._generate_suggestions(file_path, threshold.file_type)
                
                return BloatReport(
                    file_path=file_path,
                    file_type=threshold.file_type,
                    lines=lines,
                    kb=kb,
                    threshold_lines=threshold.max_lines,
                    threshold_kb=threshold.max_kb,
                    lines_over=max(0, lines_over),
                    kb_over=max(0, kb_over),
                    severity=severity,
                    suggestions=suggestions
                )
            
            return None
        
        except Exception as e:
            logger.warning(f"Failed to check file {file_path}: {e}")
            return None
    
    def _detect_file_type(self, file_path: Path) -> FileType:
        """Detect file type from extension."""
        ext = file_path.suffix.lstrip('.')
        
        if ext in ['yaml', 'yml']:
            return FileType.YAML
        elif ext == 'py':
            return FileType.PYTHON
        elif ext == 'md':
            return FileType.MARKDOWN
        elif ext == 'json':
            return FileType.JSON
        else:
            return FileType.UNKNOWN
    
    def _determine_severity(self, lines: int, threshold_lines: int, kb: float, threshold_kb: int) -> str:
        """
        Determine bloat severity.
        
        Critical: >50% over threshold
        Warning: >0% but ≤50% over threshold
        """
        lines_pct_over = ((lines - threshold_lines) / threshold_lines) * 100
        kb_pct_over = ((kb - threshold_kb) / threshold_kb) * 100
        
        max_pct_over = max(lines_pct_over, kb_pct_over)
        
        if max_pct_over > 50:
            return "critical"
        else:
            return "warning"
    
    def _generate_suggestions(self, file_path: Path, file_type: FileType) -> List[str]:
        """
        Generate refactoring suggestions for bloated file.
        
        Args:
            file_path: Path to bloated file
            file_type: Type of file
        
        Returns:
            List of refactoring suggestions
        """
        suggestions = []
        
        if file_type == FileType.YAML:
            suggestions.append("Extract inline rationales to markdown files in cortex-brain/documents/rationales/")
            suggestions.append("Use #file: references instead of inline documentation")
            suggestions.append("Split large configuration sections into separate files")
        
        elif file_type == FileType.PYTHON:
            suggestions.append("Decompose into smaller modules (target: <300 lines per module)")
            suggestions.append("Extract classes to separate files")
            suggestions.append("Move helper functions to utility modules")
            suggestions.append("Consider creating a package structure for complex logic")
        
        elif file_type == FileType.MARKDOWN:
            suggestions.append("Split into multiple documents by topic")
            suggestions.append("Move code examples to separate files and reference them")
            suggestions.append("Archive historical sections to archive/ directory")
        
        elif file_type == FileType.JSON:
            suggestions.append("Archive historical analysis files to archive/")
            suggestions.append("Compress large datasets with metadata-only summaries")
            suggestions.append("Split large objects into separate files")
        
        return suggestions
    
    def generate_report(self, bloated_files: List[BloatReport]) -> str:
        """
        Generate human-readable bloat report.
        
        Args:
            bloated_files: List of bloat reports
        
        Returns:
            Formatted report string
        """
        if not bloated_files:
            return "✅ No bloated files detected!"
        
        # Group by severity
        critical = [r for r in bloated_files if r.severity == "critical"]
        warnings = [r for r in bloated_files if r.severity == "warning"]
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FILE BLOAT DETECTION REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Total files exceeding thresholds: {len(bloated_files)}")
        report_lines.append(f"  - Critical: {len(critical)}")
        report_lines.append(f"  - Warnings: {len(warnings)}")
        report_lines.append("")
        
        if critical:
            report_lines.append("🚨 CRITICAL BLOAT (>50% over threshold):")
            report_lines.append("-" * 80)
            for report in critical:
                report_lines.extend(self._format_report(report))
                report_lines.append("")
        
        if warnings:
            report_lines.append("⚠️  WARNINGS (<50% over threshold):")
            report_lines.append("-" * 80)
            for report in warnings:
                report_lines.extend(self._format_report(report))
                report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("Recommendations:")
        report_lines.append("  1. Address critical bloat files immediately")
        report_lines.append("  2. Review warnings and plan refactoring")
        report_lines.append("  3. Run with --refactor flag for specific suggestions")
        report_lines.append("=" * 80)
        
        return '\n'.join(report_lines)
    
    def _format_report(self, report: BloatReport) -> List[str]:
        """Format individual file bloat report."""
        lines = []
        relative_path = report.file_path.relative_to(self.project_root)
        
        lines.append(f"File: {relative_path}")
        lines.append(f"  Type: {report.file_type.value}")
        lines.append(f"  Current: {report.lines} lines ({report.kb:.1f} KB)")
        lines.append(f"  Threshold: {report.threshold_lines} lines ({report.threshold_kb} KB)")
        lines.append(f"  Over by: {report.lines_over} lines ({report.kb_over:.1f} KB)")
        
        if report.suggestions:
            lines.append(f"  Suggestions:")
            for suggestion in report.suggestions:
                lines.append(f"    - {suggestion}")
        
        return lines


def main():
    """CLI entry point for bloat detector."""
    parser = argparse.ArgumentParser(description="Detect file bloat in CORTEX")
    parser.add_argument('--refactor', action='store_true', help="Show detailed refactoring suggestions")
    parser.add_argument('--staged', action='store_true', help="Check only git staged files")
    parser.add_argument('--json', action='store_true', help="Output JSON format")
    
    args = parser.parse_args()
    
    detector = BloatDetector()
    
    # Scan for bloated files
    if args.staged:
        bloated_files = detector.scan_staged_files()
    else:
        bloated_files = detector.scan_codebase()
    
    # Generate report
    if args.json:
        # JSON output
        json_output = {
            'total_files': len(bloated_files),
            'critical': len([r for r in bloated_files if r.severity == "critical"]),
            'warnings': len([r for r in bloated_files if r.severity == "warning"]),
            'files': [
                {
                    'path': str(r.file_path.relative_to(detector.project_root)),
                    'type': r.file_type.value,
                    'lines': r.lines,
                    'kb': r.kb,
                    'severity': r.severity,
                    'suggestions': r.suggestions if args.refactor else []
                }
                for r in bloated_files
            ]
        }
        print(json.dumps(json_output, indent=2))
    else:
        # Human-readable output
        report = detector.generate_report(bloated_files)
        print(report)
    
    # Exit code: 0 if no bloat, 1 if bloat detected
    exit(0 if not bloated_files else 1)


if __name__ == "__main__":
    main()

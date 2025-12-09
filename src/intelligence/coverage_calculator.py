"""
Coverage Baseline Calculator

Parses coverage reports from multiple formats and calculates baseline coverage:
- Python: coverage.py JSON format
- JavaScript/TypeScript: LCOV format
- Java: JaCoCo XML
- C#: OpenCover XML, Cobertura XML

Includes static analysis fallback when execution coverage unavailable.

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.2 (GREEN)
"""

import json
import re
import ast
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import xml.etree.ElementTree as ET


class CoverageFormat(Enum):
    """Supported coverage report formats."""
    PYTHON_COVERAGE = "coverage.py JSON"
    LCOV = "LCOV"
    JACOCO_XML = "JaCoCo XML"
    OPENCOVER_XML = "OpenCover XML"
    COBERTURA_XML = "Cobertura XML"
    UNKNOWN = "Unknown"


@dataclass
class FileCoverage:
    """Coverage information for a single file."""
    file_path: str
    lines_covered: int
    lines_missed: int
    branches_covered: int = 0
    branches_missed: int = 0
    
    @property
    def total_lines(self) -> int:
        return self.lines_covered + self.lines_missed
    
    @property
    def coverage_percent(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return (self.lines_covered / self.total_lines) * 100


@dataclass
class CoverageReport:
    """Parsed coverage report."""
    format_type: CoverageFormat
    language: str
    files: List[FileCoverage] = field(default_factory=list)
    
    @property
    def total_lines(self) -> int:
        return sum(f.total_lines for f in self.files)
    
    @property
    def covered_lines(self) -> int:
        return sum(f.lines_covered for f in self.files)
    
    @property
    def overall_coverage(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return (self.covered_lines / self.total_lines) * 100


@dataclass
class CoverageBaseline:
    """Coverage baseline with aggregations and insights."""
    overall_coverage: float
    total_lines: int
    covered_lines: int
    file_coverages: List[FileCoverage]
    module_coverage: Dict[str, float] = field(default_factory=dict)
    is_estimated: bool = False
    confidence: str = "high"  # high, medium, low, estimated
    description: str = ""
    
    def get_low_coverage_files(self, threshold: float = 50.0) -> List[FileCoverage]:
        """Get files with coverage below threshold."""
        return [f for f in self.file_coverages if f.coverage_percent < threshold]


class CoverageCalculator:
    """
    Multi-format coverage calculator.
    
    Parses coverage reports and calculates baselines.
    Falls back to static analysis when no execution data available.
    """
    
    def __init__(self, project_path: Path):
        """Initialize calculator."""
        self.project_path = Path(project_path)
    
    def detect_format(self, coverage_file: Path) -> CoverageFormat:
        """
        Detect coverage report format from file.
        
        Args:
            coverage_file: Path to coverage file
        
        Returns:
            Detected CoverageFormat
        """
        try:
            content = coverage_file.read_text(encoding='utf-8')
        except:
            return CoverageFormat.UNKNOWN
        
        # Check for JSON format (Python coverage)
        if coverage_file.suffix == '.json':
            try:
                data = json.loads(content)
                if 'files' in data or 'meta' in data:
                    return CoverageFormat.PYTHON_COVERAGE
            except:
                pass
        
        # Check for LCOV format (needs at least SF: line)
        if 'SF:' in content:
            return CoverageFormat.LCOV
        
        # Check for XML formats
        if content.startswith('<?xml'):
            if '<report' in content and 'JaCoCo' in content:
                return CoverageFormat.JACOCO_XML
            elif '<CoverageSession' in content:
                return CoverageFormat.OPENCOVER_XML
            elif '<coverage' in content:
                return CoverageFormat.COBERTURA_XML
        
        return CoverageFormat.UNKNOWN
    
    def detect_language(self, coverage_file: Path) -> str:
        """Detect language from coverage report."""
        format_type = self.detect_format(coverage_file)
        
        if format_type == CoverageFormat.PYTHON_COVERAGE:
            return "Python"
        elif format_type == CoverageFormat.LCOV:
            # Check file extensions in content (LCOV has SF:path lines)
            try:
                content = coverage_file.read_text(encoding='utf-8')
                # Look for source file paths in LCOV format (SF: lines)
                ts_count = content.count('.ts\n') + content.count('.tsx\n')
                js_count = content.count('.js\n') + content.count('.jsx\n')
                cpp_count = content.count('.cpp\n') + content.count('.cc\n')
                
                if ts_count > js_count:
                    return "TypeScript"
                elif js_count > 0 or ts_count > 0:
                    return "JavaScript"
                elif cpp_count > 0:
                    return "C++"
            except:
                pass
            # Default to JavaScript for LCOV (most common)
            return "JavaScript"
        elif format_type == CoverageFormat.JACOCO_XML:
            return "Java"
        elif format_type in [CoverageFormat.OPENCOVER_XML, CoverageFormat.COBERTURA_XML]:
            return "C#"
        
        return "Unknown"
    
    def parse_report(self, coverage_file: Path) -> Optional[CoverageReport]:
        """
        Parse coverage report file.
        
        Args:
            coverage_file: Path to coverage report
        
        Returns:
            Parsed CoverageReport or None if parsing fails
        """
        format_type = self.detect_format(coverage_file)
        language = self.detect_language(coverage_file)
        
        if format_type == CoverageFormat.PYTHON_COVERAGE:
            return self._parse_python_coverage(coverage_file, language)
        elif format_type == CoverageFormat.LCOV:
            return self._parse_lcov(coverage_file, language)
        elif format_type == CoverageFormat.JACOCO_XML:
            return self._parse_jacoco(coverage_file, language)
        elif format_type == CoverageFormat.OPENCOVER_XML:
            return self._parse_opencover(coverage_file, language)
        
        return None
    
    def _parse_python_coverage(self, coverage_file: Path, language: str) -> CoverageReport:
        """Parse Python coverage.py JSON format."""
        try:
            data = json.loads(coverage_file.read_text(encoding='utf-8'))
        except:
            return CoverageReport(CoverageFormat.PYTHON_COVERAGE, language)
        
        files = []
        file_data = data.get('files', {})
        
        for file_path, coverage_info in file_data.items():
            executed = coverage_info.get('executed_lines', [])
            missing = coverage_info.get('missing_lines', [])
            
            files.append(FileCoverage(
                file_path=file_path,
                lines_covered=len(executed),
                lines_missed=len(missing)
            ))
        
        return CoverageReport(CoverageFormat.PYTHON_COVERAGE, language, files)
    
    def _parse_lcov(self, coverage_file: Path, language: str) -> CoverageReport:
        """Parse LCOV format."""
        try:
            content = coverage_file.read_text(encoding='utf-8')
        except:
            return CoverageReport(CoverageFormat.LCOV, language)
        
        files = []
        current_file = None
        covered_lines = 0
        missed_lines = 0
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('SF:'):
                # Save previous file if exists
                if current_file:
                    files.append(FileCoverage(
                        file_path=current_file,
                        lines_covered=covered_lines,
                        lines_missed=missed_lines
                    ))
                # Start new file
                current_file = line[3:]
                covered_lines = 0
                missed_lines = 0
            
            elif line.startswith('DA:'):
                # Data line: DA:line_num,hit_count
                try:
                    parts = line[3:].split(',')
                    if len(parts) >= 2:
                        hit_count = int(parts[1])
                        if hit_count > 0:
                            covered_lines += 1
                        else:
                            missed_lines += 1
                except ValueError:
                    pass  # Skip malformed lines
            
            elif line == 'end_of_record':
                if current_file:
                    files.append(FileCoverage(
                        file_path=current_file,
                        lines_covered=covered_lines,
                        lines_missed=missed_lines
                    ))
                    current_file = None
        
        # Handle last file if no end_of_record
        if current_file:
            files.append(FileCoverage(
                file_path=current_file,
                lines_covered=covered_lines,
                lines_missed=missed_lines
            ))
        
        return CoverageReport(CoverageFormat.LCOV, language, files)
    
    def _parse_jacoco(self, coverage_file: Path, language: str) -> CoverageReport:
        """Parse JaCoCo XML format."""
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
        except:
            return CoverageReport(CoverageFormat.JACOCO_XML, language)
        
        files = []
        
        for package in root.findall('.//package'):
            package_name = package.get('name', '')
            
            for cls in package.findall('.//class'):
                class_name = cls.get('name', '')
                source_file = cls.get('sourcefilename', f"{class_name}.java")
                
                # Get line counter
                line_counter = cls.find('.//counter[@type="LINE"]')
                if line_counter is not None:
                    covered = int(line_counter.get('covered', 0))
                    missed = int(line_counter.get('missed', 0))
                    
                    files.append(FileCoverage(
                        file_path=f"{package_name}/{source_file}",
                        lines_covered=covered,
                        lines_missed=missed
                    ))
        
        return CoverageReport(CoverageFormat.JACOCO_XML, language, files)
    
    def _parse_opencover(self, coverage_file: Path, language: str) -> CoverageReport:
        """Parse OpenCover XML format."""
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
        except:
            return CoverageReport(CoverageFormat.OPENCOVER_XML, language)
        
        files = []
        
        for file_elem in root.findall('.//File'):
            file_path = file_elem.get('fullPath', '')
            
            # Count covered and missed lines from sequence points
            covered = 0
            missed = 0
            
            for sp in file_elem.findall('.//SequencePoint'):
                visit_count = int(sp.get('vc', 0))
                if visit_count > 0:
                    covered += 1
                else:
                    missed += 1
            
            if covered + missed > 0:
                files.append(FileCoverage(
                    file_path=file_path,
                    lines_covered=covered,
                    lines_missed=missed
                ))
        
        return CoverageReport(CoverageFormat.OPENCOVER_XML, language, files)
    
    def calculate_baseline(self, coverage_file: Path) -> Optional[CoverageBaseline]:
        """
        Calculate coverage baseline from report.
        
        Args:
            coverage_file: Path to coverage report
        
        Returns:
            CoverageBaseline with aggregated metrics
        """
        report = self.parse_report(coverage_file)
        if not report:
            return None
        
        # Calculate module-level coverage
        module_coverage = self._calculate_module_coverage(report.files)
        
        baseline = CoverageBaseline(
            overall_coverage=report.overall_coverage,
            total_lines=report.total_lines,
            covered_lines=report.covered_lines,
            file_coverages=report.files,
            module_coverage=module_coverage,
            is_estimated=False,
            confidence="high",
            description=f"Coverage baseline from {report.format_type.value} report"
        )
        
        return baseline
    
    def _calculate_module_coverage(self, file_coverages: List[FileCoverage]) -> Dict[str, float]:
        """Calculate coverage aggregated by module/package."""
        module_stats = defaultdict(lambda: {'covered': 0, 'total': 0})
        
        for file_cov in file_coverages:
            # Extract module from file path (first directory after src/)
            path = Path(file_cov.file_path)
            parts = path.parts
            
            # Skip 'src' prefix if present
            if len(parts) > 1 and parts[0] == 'src':
                module = parts[1] if len(parts) > 2 else parts[0]
            elif len(parts) > 1:
                module = parts[0]
            else:
                module = 'root'
            
            module_stats[module]['covered'] += file_cov.lines_covered
            module_stats[module]['total'] += file_cov.total_lines
        
        # Calculate percentages
        return {
            module: (stats['covered'] / stats['total']) * 100
            for module, stats in module_stats.items()
            if stats['total'] > 0
        }
    
    def estimate_coverage_static(self, source_dir: Path) -> CoverageBaseline:
        """
        Estimate coverage using static analysis (no execution data).
        
        Args:
            source_dir: Directory containing source code
        
        Returns:
            CoverageBaseline with estimated coverage
        """
        file_coverages = []
        
        # Find Python files
        for py_file in source_dir.rglob('*.py'):
            try:
                content = py_file.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Count executable lines (functions, statements)
                total_lines = len([node for node in ast.walk(tree) 
                                  if isinstance(node, (ast.FunctionDef, ast.Assign, ast.Expr))])
                
                # Assume 0% coverage (no execution data)
                file_coverages.append(FileCoverage(
                    file_path=str(py_file.relative_to(self.project_path)),
                    lines_covered=0,
                    lines_missed=total_lines
                ))
            except:
                pass
        
        total_lines = sum(f.total_lines for f in file_coverages)
        
        return CoverageBaseline(
            overall_coverage=0.0,
            total_lines=total_lines,
            covered_lines=0,
            file_coverages=file_coverages,
            module_coverage={},
            is_estimated=True,
            confidence="estimated",
            description="Estimated coverage using static analysis (no execution data available)"
        )


# Convenience functions
def calculate_coverage_baseline(project_path: Path, coverage_file: Path) -> Optional[CoverageBaseline]:
    """Quick baseline calculation."""
    calc = CoverageCalculator(project_path)
    return calc.calculate_baseline(coverage_file)


def find_coverage_reports(project_path: Path) -> List[Path]:
    """Find coverage reports in project."""
    reports = []
    
    # Common coverage file patterns
    patterns = [
        'coverage.json', '.coverage.json',
        'lcov.info', 'coverage/lcov.info',
        'jacoco.xml', 'target/site/jacoco/jacoco.xml',
        'opencover.xml', 'coverage.opencover.xml',
        'coverage.xml'
    ]
    
    for pattern in patterns:
        for match in project_path.rglob(pattern):
            reports.append(match)
    
    return reports

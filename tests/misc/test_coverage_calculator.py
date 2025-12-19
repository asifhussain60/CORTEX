"""
Test suite for Coverage Baseline Calculator

Tests coverage report parsing, baseline calculation, and static analysis fallback
for Python, C#, JavaScript, and other languages.

RED PHASE: Write failing tests first

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.2 (RED)
"""

import pytest
from pathlib import Path
import tempfile
import json
import xml.etree.ElementTree as ET

# Import will fail until GREEN phase
try:
    from src.intelligence.coverage_calculator import (
        CoverageCalculator,
        CoverageReport,
        FileCoverage,
        CoverageFormat,
        CoverageBaseline
    )
except ImportError:
    CoverageCalculator = None
    CoverageReport = None
    FileCoverage = None
    CoverageFormat = None
    CoverageBaseline = None


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCoverageFormatDetection:
    """Test detection of coverage report formats."""
    
    def test_detect_python_coverage_json(self, temp_project):
        """Should detect Python coverage.py JSON format."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        coverage_file = temp_project / ".coverage.json"
        coverage_file.write_text(json.dumps({
            "meta": {"version": "5.5"},
            "files": {
                "src/example.py": {
                    "executed_lines": [1, 2, 3],
                    "missing_lines": [4, 5]
                }
            }
        }))
        
        calc = CoverageCalculator(temp_project)
        format_type = calc.detect_format(coverage_file)
        
        assert format_type == CoverageFormat.PYTHON_COVERAGE
    
    def test_detect_lcov_format(self, temp_project):
        """Should detect LCOV format (JavaScript/C++)."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        lcov_file = temp_project / "lcov.info"
        lcov_file.write_text(
            "TN:\n"
            "SF:src/example.js\n"
            "DA:1,1\n"
            "DA:2,1\n"
            "DA:3,0\n"
            "end_of_record\n"
        )
        
        calc = CoverageCalculator(temp_project)
        format_type = calc.detect_format(lcov_file)
        
        assert format_type == CoverageFormat.LCOV
    
    def test_detect_jacoco_xml(self, temp_project):
        """Should detect JaCoCo XML format (Java)."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        jacoco_file = temp_project / "jacoco.xml"
        jacoco_file.write_text(
            '<?xml version="1.0" ?>'
            '<report name="JaCoCo Coverage">'
            '<package name="com.example">'
            '<class name="Example">'
            '<counter type="LINE" missed="2" covered="5"/>'
            '</class></package></report>'
        )
        
        calc = CoverageCalculator(temp_project)
        format_type = calc.detect_format(jacoco_file)
        
        assert format_type == CoverageFormat.JACOCO_XML
    
    def test_detect_opencover_xml(self, temp_project):
        """Should detect OpenCover XML format (C#)."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        opencover_file = temp_project / "opencover.xml"
        opencover_file.write_text(
            '<?xml version="1.0" ?>'
            '<CoverageSession>'
            '<Modules><Module><Files>'
            '<File uid="1" fullPath="Example.cs">'
            '<SequencePoints><SequencePoint vc="5"/></SequencePoints>'
            '</File></Files></Module></Modules>'
            '</CoverageSession>'
        )
        
        calc = CoverageCalculator(temp_project)
        format_type = calc.detect_format(opencover_file)
        
        assert format_type == CoverageFormat.OPENCOVER_XML


class TestCoverageReportParsing:
    """Test parsing of various coverage report formats."""
    
    def test_parse_python_coverage_json(self, temp_project):
        """Should parse Python coverage.py JSON report."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        coverage_data = {
            "meta": {"version": "5.5"},
            "files": {
                "src/calculator.py": {
                    "executed_lines": [1, 2, 3, 5, 6],
                    "missing_lines": [4, 7, 8],
                    "excluded_lines": []
                },
                "src/utils.py": {
                    "executed_lines": [1, 2],
                    "missing_lines": [3, 4, 5],
                    "excluded_lines": []
                }
            }
        }
        
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        calc = CoverageCalculator(temp_project)
        report = calc.parse_report(coverage_file)
        
        assert report is not None
        assert len(report.files) == 2
        
        calc_coverage = next(f for f in report.files if "calculator.py" in f.file_path)
        assert calc_coverage.lines_covered == 5
        assert calc_coverage.lines_missed == 3
        assert calc_coverage.coverage_percent == pytest.approx(62.5, abs=0.1)
    
    def test_parse_lcov_info(self, temp_project):
        """Should parse LCOV info file."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        lcov_content = """TN:
SF:src/example.js
DA:1,1
DA:2,1
DA:3,1
DA:4,0
DA:5,0
end_of_record
SF:src/utils.js
DA:1,1
DA:2,0
end_of_record
"""
        
        lcov_file = temp_project / "lcov.info"
        lcov_file.write_text(lcov_content)
        
        calc = CoverageCalculator(temp_project)
        report = calc.parse_report(lcov_file)
        
        assert report is not None
        assert len(report.files) == 2
        
        example_coverage = next(f for f in report.files if "example.js" in f.file_path)
        assert example_coverage.lines_covered == 3
        assert example_coverage.lines_missed == 2
        assert example_coverage.coverage_percent == 60.0
    
    def test_parse_jacoco_xml(self, temp_project):
        """Should parse JaCoCo XML report."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        jacoco_xml = """<?xml version="1.0" ?>
<report name="JaCoCo Coverage">
  <package name="com.example">
    <class name="Calculator" sourcefilename="Calculator.java">
      <counter type="LINE" missed="3" covered="7"/>
      <counter type="BRANCH" missed="1" covered="4"/>
    </class>
  </package>
</report>
"""
        
        jacoco_file = temp_project / "jacoco.xml"
        jacoco_file.write_text(jacoco_xml)
        
        calc = CoverageCalculator(temp_project)
        report = calc.parse_report(jacoco_file)
        
        assert report is not None
        assert len(report.files) >= 1
        
        calc_coverage = report.files[0]
        assert calc_coverage.lines_covered == 7
        assert calc_coverage.lines_missed == 3
        assert calc_coverage.coverage_percent == 70.0


class TestCoverageBaseline:
    """Test coverage baseline calculation."""
    
    def test_calculate_baseline_from_report(self, temp_project):
        """Should calculate coverage baseline from parsed report."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        # Create mock coverage data
        coverage_data = {
            "files": {
                "src/file1.py": {"executed_lines": [1,2,3], "missing_lines": [4,5]},
                "src/file2.py": {"executed_lines": [1,2], "missing_lines": [3,4,5,6]},
                "src/file3.py": {"executed_lines": [1,2,3,4,5], "missing_lines": []}
            }
        }
        
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        calc = CoverageCalculator(temp_project)
        baseline = calc.calculate_baseline(coverage_file)
        
        assert baseline is not None
        assert baseline.total_lines > 0
        assert baseline.covered_lines > 0
        assert 0 <= baseline.overall_coverage <= 100
        assert len(baseline.file_coverages) == 3
    
    def test_baseline_aggregation_by_module(self, temp_project):
        """Should aggregate coverage by module/package."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        coverage_data = {
            "files": {
                "src/auth/login.py": {"executed_lines": [1,2,3], "missing_lines": [4]},
                "src/auth/logout.py": {"executed_lines": [1,2], "missing_lines": [3,4]},
                "src/utils/helpers.py": {"executed_lines": [1,2,3,4,5], "missing_lines": []}
            }
        }
        
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        calc = CoverageCalculator(temp_project)
        baseline = calc.calculate_baseline(coverage_file)
        
        # Should have module-level aggregation
        assert hasattr(baseline, 'module_coverage')
        assert 'auth' in baseline.module_coverage
        assert 'utils' in baseline.module_coverage
    
    def test_identify_low_coverage_files(self, temp_project):
        """Should identify files with coverage below threshold."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        coverage_data = {
            "files": {
                "src/high.py": {"executed_lines": list(range(1,91)), "missing_lines": list(range(91,101))},
                "src/medium.py": {"executed_lines": list(range(1,61)), "missing_lines": list(range(61,101))},
                "src/low.py": {"executed_lines": list(range(1,31)), "missing_lines": list(range(31,101))}
            }
        }
        
        coverage_file = temp_project / "coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        calc = CoverageCalculator(temp_project)
        baseline = calc.calculate_baseline(coverage_file)
        
        low_coverage = baseline.get_low_coverage_files(threshold=50)
        assert len(low_coverage) >= 1
        assert any("low.py" in f.file_path for f in low_coverage)


class TestStaticAnalysisFallback:
    """Test static analysis when no execution coverage available."""
    
    def test_static_analysis_python(self, temp_project):
        """Should perform static analysis for Python files."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        # Create Python file without coverage
        py_file = temp_project / "src" / "example.py"
        py_file.parent.mkdir(parents=True)
        py_file.write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

class Calculator:
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
""")
        
        calc = CoverageCalculator(temp_project)
        baseline = calc.estimate_coverage_static(temp_project / "src")
        
        assert baseline is not None
        assert len(baseline.file_coverages) >= 1
        assert baseline.confidence == 'estimated'
    
    def test_mark_estimated_coverage(self, temp_project):
        """Should clearly mark coverage as estimated when using static analysis."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        calc = CoverageCalculator(temp_project)
        baseline = calc.estimate_coverage_static(temp_project)
        
        assert baseline.is_estimated == True
        assert baseline.confidence == 'estimated'
        assert "estimated" in baseline.description.lower()


class TestMultiLanguageSupport:
    """Test coverage calculation across multiple languages."""
    
    def test_detect_language_from_report(self, temp_project):
        """Should detect language from coverage report format."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        calc = CoverageCalculator(temp_project)
        
        # Python coverage
        py_file = temp_project / "coverage.json"
        py_file.write_text('{"files": {}}')
        assert calc.detect_language(py_file) == "Python"
        
        # JavaScript/TypeScript LCOV
        js_file = temp_project / "lcov.info"
        js_file.write_text("SF:src/example.js\n")
        assert calc.detect_language(js_file) in ["JavaScript", "TypeScript"]
        
        # C# OpenCover
        cs_file = temp_project / "opencover.xml"
        cs_file.write_text('<?xml version="1.0" ?><CoverageSession></CoverageSession>')
        assert calc.detect_language(cs_file) == "C#"


class TestPerformance:
    """Test performance requirements."""
    
    def test_parse_large_report_quickly(self, temp_project):
        """Should parse large coverage reports (<3s for 1000 files)."""
        if CoverageCalculator is None:
            pytest.skip("CoverageCalculator not implemented yet (RED phase)")
        
        import time
        
        # Generate large coverage report
        coverage_data = {
            "files": {
                f"src/file_{i}.py": {
                    "executed_lines": list(range(1, 51)),
                    "missing_lines": list(range(51, 101))
                }
                for i in range(1000)
            }
        }
        
        coverage_file = temp_project / "large_coverage.json"
        coverage_file.write_text(json.dumps(coverage_data))
        
        calc = CoverageCalculator(temp_project)
        
        start_time = time.time()
        report = calc.parse_report(coverage_file)
        baseline = calc.calculate_baseline(coverage_file)
        elapsed = time.time() - start_time
        
        assert elapsed < 3.0, f"Parsing took {elapsed:.2f}s, expected <3s"
        assert len(report.files) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

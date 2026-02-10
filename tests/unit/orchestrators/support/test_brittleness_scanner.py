"""
Tests for BrittlenessScanner - Layer 2 Runtime Regression Guard

Author: Asif Hussain
Phase: 24.2
TDD: RED phase - tests written first
"""
import pytest
from pathlib import Path
from typing import List, Dict, Any

from cortex.orchestrators.support.brittleness_scanner import (
    BrittlenessScanner,
    BrittlenessReport,
    CircularDependencyViolation,
    CouplingViolation,
    AntiPatternViolation,
)


@pytest.fixture
def scanner():
    """Create BrittlenessScanner instance"""
    return BrittlenessScanner()


@pytest.fixture
def sample_codebase_path(tmp_path):
    """Create sample codebase with various patterns"""
    # Create directory structure
    module_a = tmp_path / "module_a.py"
    module_b = tmp_path / "module_b.py"
    module_c = tmp_path / "module_c.py"
    god_object = tmp_path / "god_object.py"
    
    # Circular dependency: A → B → A
    module_a.write_text("""
import module_b

class ClassA:
    def __init__(self):
        self.b = module_b.ClassB()
""")
    
    module_b.write_text("""
import module_a

class ClassB:
    def __init__(self):
        self.a = module_a.ClassA()
""")
    
    # Isolated module
    module_c.write_text("""
class ClassC:
    def method(self):
        return "isolated"
""")
    
    # God object (>10 methods, high complexity)
    god_object.write_text("""
class GodObject:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass
    def method11(self): pass
    def method12(self): pass
""")
    
    return tmp_path


class TestCircularDependencyDetection:
    """Test circular dependency detection"""
    
    def test_detect_circular_dependency(self, scanner, sample_codebase_path):
        """Should detect A → B → A circular dependency"""
        result = scanner.scan(str(sample_codebase_path))
        
        assert result.has_circular_dependencies()
        assert len(result.circular_dependencies) >= 1
        
        # Check cycle detected
        cycle = result.circular_dependencies[0]
        assert "module_a" in cycle.cycle_path
        assert "module_b" in cycle.cycle_path
        assert cycle.severity == "HIGH"
    
    def test_no_false_positives_for_isolated_module(self, scanner, sample_codebase_path):
        """Should not flag isolated modules as circular"""
        result = scanner.scan(str(sample_codebase_path))
        
        # module_c should not be in any circular dependency
        for cycle in result.circular_dependencies:
            assert "module_c" not in cycle.cycle_path


class TestCouplingDetection:
    """Test tight coupling detection"""
    
    def test_detect_tight_coupling(self, scanner, sample_codebase_path):
        """Should detect high fan-in/fan-out violations"""
        result = scanner.scan(str(sample_codebase_path))
        
        # module_a and module_b are tightly coupled
        coupling_violations = [
            v for v in result.coupling_violations
            if "module_a" in v.module_name or "module_b" in v.module_name
        ]
        assert len(coupling_violations) >= 1
    
    def test_coupling_metrics_calculation(self, scanner, sample_codebase_path):
        """Should calculate fan-in/fan-out correctly"""
        result = scanner.scan(str(sample_codebase_path))
        
        # Find module_a coupling
        module_a_coupling = next(
            (v for v in result.coupling_violations if "module_a" in v.module_name),
            None
        )
        
        if module_a_coupling:
            assert module_a_coupling.fan_in >= 1  # imported by module_b
            assert module_a_coupling.fan_out >= 1  # imports module_b


class TestAntiPatternDetection:
    """Test anti-pattern detection"""
    
    def test_detect_god_object(self, scanner, sample_codebase_path):
        """Should detect classes with >10 methods"""
        result = scanner.scan(str(sample_codebase_path))
        
        god_object_violations = [
            v for v in result.anti_pattern_violations
            if v.pattern_name == "GodObject" and "god_object" in v.location
        ]
        assert len(god_object_violations) >= 1
        
        violation = god_object_violations[0]
        assert violation.severity == "HIGH"
        assert "12 methods" in violation.description or violation.method_count >= 10
    
    def test_no_false_positives_for_small_classes(self, scanner, sample_codebase_path):
        """Should not flag classes with reasonable method counts"""
        result = scanner.scan(str(sample_codebase_path))
        
        # ClassA, ClassB, ClassC should not be flagged as god objects
        for violation in result.anti_pattern_violations:
            if violation.pattern_name == "GodObject":
                assert "ClassA" not in violation.location
                assert "ClassB" not in violation.location
                assert "ClassC" not in violation.location


class TestBrittlenessScoreCalculation:
    """Test brittleness score calculation"""
    
    def test_calculate_brittleness_score(self, scanner, sample_codebase_path):
        """Should calculate overall brittleness score (0-1.0)"""
        result = scanner.scan(str(sample_codebase_path))
        
        assert 0.0 <= result.brittleness_score <= 1.0
        
        # With circular deps + god object, score should be > 0.3
        assert result.brittleness_score > 0.3
    
class TestBrittlenessReport:
    """Test report generation"""
    
    def test_report_structure(self, scanner, sample_codebase_path):
        """Report should contain all required sections"""
        result = scanner.scan(str(sample_codebase_path))
        
        assert hasattr(result, 'brittleness_score')
        assert hasattr(result, 'circular_dependencies')
        assert hasattr(result, 'coupling_violations')
        assert hasattr(result, 'anti_pattern_violations')
        assert hasattr(result, 'scan_timestamp')
        assert hasattr(result, 'scanned_path')
    
    def test_has_violations_method(self, scanner, sample_codebase_path):
        """has_violations() should return True when violations exist"""
        result = scanner.scan(str(sample_codebase_path))
        
        assert result.has_violations() is True
    
    def test_empty_codebase_has_no_violations(self, scanner, tmp_path):
        """Empty codebase should have no violations"""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("# Empty file\n")
        
        result = scanner.scan(str(tmp_path))
        
        assert result.brittleness_score == 0.0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_nonexistent_path(self, scanner):
        """Should handle nonexistent paths gracefully"""
        result = scanner.scan("/nonexistent/path")
        
        assert result.brittleness_score == 0.0
        assert len(result.circular_dependencies) == 0
    
    def test_empty_directory(self, scanner, tmp_path):
        """Should handle empty directories"""
        result = scanner.scan(str(tmp_path))
        
        assert result.brittleness_score == 0.0
    
    def test_non_python_files(self, scanner, tmp_path):
        """Should ignore non-Python files"""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("Not Python code")
        
        result = scanner.scan(str(tmp_path))
        
        assert result.brittleness_score == 0.0

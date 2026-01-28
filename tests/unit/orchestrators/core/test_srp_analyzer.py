"""
Unit Tests for SRPAnalyzer - Single Responsibility Principle.

Tests for SRPAnalyzer from SOLID principle detection system.

Authority: CORE-008 (TDD - tests first)
Coverage Target: 90%+
"""

import pytest
from pathlib import Path
import tempfile
from typing import Generator

from cortex.orchestrators.core.solid_analyzers import (
    SRPAnalyzer,
    SolidViolationType,
)
from cortex.orchestrators.core.challenge_engine_plugins import DisagreementType


class TestSRPAnalyzer:
    """Test SRP (Single Responsibility Principle) analyzer."""
    
    @pytest.fixture
    def analyzer(self) -> SRPAnalyzer:
        """Create SRP analyzer instance."""
        return SRPAnalyzer()
    
    @pytest.fixture
    def temp_python_file(self) -> Generator[Path, None, None]:
        """Create temporary Python file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            yield Path(f.name)
    
    def test_analyzer_has_disagreement_type(self, analyzer: SRPAnalyzer):
        """Test that analyzer has correct disagreement type."""
        assert hasattr(analyzer, 'disagreement_type')
        assert analyzer.disagreement_type == DisagreementType.BETTER_SOLUTION
    
    def test_detect_large_class_violation(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test detection of large class (>500 lines)."""
        methods_code = '\n'.join([f"    def method_{i}(self): pass" for i in range(30)])
        large_class_code = f'''
class GodObject:
    """Large class with many responsibilities."""
{methods_code}
'''
        large_class_code += "\n" * 500
        
        temp_python_file.write_text(large_class_code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) > 0
        assert any(v.violation_type == SolidViolationType.SRP_VIOLATION for v in violations)
    
    def test_detect_too_many_methods(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test detection of class with too many methods (>20)."""
        methods_code = '\n'.join([f"    def method_{i}(self): pass" for i in range(25)])
        class_code = f'''
class TooManyMethods:
    """Class with more than 20 methods."""
{methods_code}
'''
        temp_python_file.write_text(class_code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) > 0
        assert any(v.violation_type == SolidViolationType.SRP_VIOLATION for v in violations)
    
    def test_detect_multiple_responsibilities(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test detection of multiple distinct responsibilities."""
        code = '''
class MixedResponsibilities:
    """Class handling multiple concerns."""
    def get_data(self): pass
    def validate_data(self): pass
    def save_data(self): pass
    def format_output(self): pass
    def send_email(self): pass
'''
        temp_python_file.write_text(code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) > 0
    
    def test_ignore_small_well_defined_class(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test that well-designed classes are not flagged."""
        code = '''
class UserRepository:
    """Repository with single responsibility: user data access."""
    def get_user(self, user_id: int): pass
    def create_user(self, user): pass
    def update_user(self, user): pass
    def delete_user(self, user_id: int): pass
'''
        temp_python_file.write_text(code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) == 0
    
    def test_violation_includes_evidence(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test that violations include actionable evidence."""
        methods_code = '\n'.join([f"    def method_{i}(self): pass" for i in range(25)])
        large_class = f'class BigClass:\n{methods_code}'
        large_class += '\n' * 500
        
        temp_python_file.write_text(large_class)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert all(v.evidence for v in violations)
        assert all(v.suggested_fix for v in violations)
    
    def test_analyze_nonexistent_file(self, analyzer: SRPAnalyzer):
        """Test handling of nonexistent file."""
        result = analyzer.analyze(Path("/nonexistent/file.py"))
        assert result.is_err()
    
    def test_analyze_invalid_python(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test handling of invalid Python syntax."""
        temp_python_file.write_text("this is not valid python @@@@")
        result = analyzer.analyze(temp_python_file)
        assert result.is_err()
    
    def test_violation_type_is_correct(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test that violations have correct type."""
        methods_code = '\n'.join([f"    def method_{i}(self): pass" for i in range(25)])
        code = f'''
class ViolatingClass:
{methods_code}
'''
        temp_python_file.write_text(code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert all(v.violation_type == SolidViolationType.SRP_VIOLATION for v in violations)
    
    def test_empty_file(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test handling of empty file."""
        temp_python_file.write_text("")
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) == 0
    
    def test_violation_has_line_number(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test that violations report line numbers."""
        methods_code = '\n'.join([f"    def method_{i}(self): pass" for i in range(25)])
        code = f'''
class ViolatingClass:
{methods_code}
'''
        temp_python_file.write_text(code)
        result = analyzer.analyze(temp_python_file)
        
        violations = result.unwrap()
        assert any(v.line_number > 0 for v in violations)
    
    def test_analyze_returns_result_type(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test that analyze returns Result type."""
        temp_python_file.write_text("class Simple: pass")
        
        result = analyzer.analyze(temp_python_file)
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')
        assert result.is_ok()
    
    def test_multiple_violations_in_file(self, analyzer: SRPAnalyzer, temp_python_file: Path):
        """Test detection of multiple violations in same file."""
        methods1 = '\n'.join([f"    def method_{i}(self): pass" for i in range(25)])
        code = f'''
class ViolatingClass1:
{methods1}

class ViolatingClass2:
    def get_data(self): pass
    def validate_data(self): pass
    def save_data(self): pass
    def format_output(self): pass
    def send_email(self): pass
'''
        temp_python_file.write_text(code)
        result = analyzer.analyze(temp_python_file)
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) >= 1

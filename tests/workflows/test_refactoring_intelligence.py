"""
Tests for Refactoring Intelligence (Milestone 2.2)

Validates code smell detection, refactoring suggestions,
and safety verification.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2 - Milestone 2.2
"""

import pytest
from src.workflows.refactoring_intelligence import (
    CodeSmellDetector,
    RefactoringEngine,
    CodeSmellType,
    RefactoringType,
    CodeSmell
)


class TestCodeSmellDetection:
    """Test code smell detection capabilities."""
    
    def test_detects_long_method(self):
        """Should detect methods that are too long."""
        source_code = '''
def long_method():
    """Docstring here."""
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        long_method_smells = [s for s in smells if s.smell_type == CodeSmellType.LONG_METHOD]
        assert len(long_method_smells) > 0
        assert long_method_smells[0].severity in ("medium", "high")
    
    def test_detects_complex_conditional(self):
        """Should detect conditionals with too many logical operators."""
        source_code = '''
def complex_check(a, b, c, d, e, f):
    if (a and b) or (c and d) or (e and f) or (a and c):
        return True
    return False
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        complex_smells = [s for s in smells if s.smell_type == CodeSmellType.COMPLEX_CONDITIONAL]
        assert len(complex_smells) > 0
        assert complex_smells[0].metric_value > 4
    
    def test_detects_long_parameter_list(self):
        """Should detect functions with too many parameters."""
        source_code = '''
def many_params(a, b, c, d, e, f, g, h):
    return a + b + c + d + e + f + g + h
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        param_smells = [s for s in smells if s.smell_type == CodeSmellType.LONG_PARAMETER_LIST]
        assert len(param_smells) > 0
        assert param_smells[0].metric_value > 5
    
    def test_detects_deep_nesting(self):
        """Should detect deeply nested code blocks."""
        source_code = '''
def deeply_nested(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    if a > 5:
                        return True
    return False
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        nesting_smells = [s for s in smells if s.smell_type == CodeSmellType.DEEP_NESTING]
        assert len(nesting_smells) > 0
        assert nesting_smells[0].metric_value > 4
    
    def test_detects_magic_numbers(self):
        """Should detect magic numbers in code."""
        source_code = '''
def calculate_price(quantity):
    base_price = quantity * 42
    tax = base_price * 0.15
    return base_price + tax
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        magic_smells = [s for s in smells if s.smell_type == CodeSmellType.MAGIC_NUMBER]
        assert len(magic_smells) >= 2  # 42 and 0.15
    
    def test_detects_god_class(self):
        """Should detect classes with too many methods."""
        methods = "\n    ".join([f"def method_{i}(self): pass" for i in range(25)])
        source_code = f'''
class GodClass:
    {methods}
'''
        
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        god_class_smells = [s for s in smells if s.smell_type == CodeSmellType.GOD_CLASS]
        assert len(god_class_smells) > 0
        assert god_class_smells[0].metric_value > 20


class TestRefactoringSuggestions:
    """Test refactoring suggestion generation."""
    
    def test_suggests_extract_method_for_long_method(self):
        """Should suggest extracting methods for long methods."""
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_METHOD,
            location="test.py:1:0",
            severity="high",
            description="Method is too long",
            metric_value=50.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert len(suggestions) > 0
        assert suggestions[0].refactoring_type == RefactoringType.EXTRACT_METHOD
        assert suggestions[0].confidence > 0.7
    
    def test_suggests_simplify_conditional_for_complex_if(self):
        """Should suggest simplifying complex conditionals."""
        smell = CodeSmell(
            smell_type=CodeSmellType.COMPLEX_CONDITIONAL,
            location="test.py:5:0",
            severity="high",
            description="Conditional has too many operators",
            metric_value=6.0,
            confidence=0.85
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert len(suggestions) > 0
        assert suggestions[0].refactoring_type == RefactoringType.SIMPLIFY_CONDITIONAL
        assert "boolean" in suggestions[0].description.lower() or "method" in suggestions[0].description.lower()
    
    def test_suggests_parameter_object_for_long_param_list(self):
        """Should suggest parameter objects for long parameter lists."""
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_PARAMETER_LIST,
            location="test.py:10:0",
            severity="medium",
            description="Function has too many parameters",
            metric_value=8.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert len(suggestions) > 0
        assert suggestions[0].refactoring_type == RefactoringType.INTRODUCE_PARAMETER_OBJECT
        assert "config" in suggestions[0].description.lower() or "object" in suggestions[0].description.lower()
    
    def test_suggests_reduce_nesting_for_deep_nesting(self):
        """Should suggest reducing nesting depth."""
        smell = CodeSmell(
            smell_type=CodeSmellType.DEEP_NESTING,
            location="test.py:15:0",
            severity="high",
            description="Function has deep nesting",
            metric_value=6.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert len(suggestions) > 0
        assert suggestions[0].refactoring_type == RefactoringType.REDUCE_NESTING
        assert "early return" in suggestions[0].description.lower() or "extract" in suggestions[0].description.lower()
    
    def test_suggests_extract_constant_for_magic_number(self):
        """Should suggest extracting magic numbers to constants."""
        smell = CodeSmell(
            smell_type=CodeSmellType.MAGIC_NUMBER,
            location="test.py:20:5",
            severity="low",
            description="Magic number should be named constant",
            metric_value=42.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert len(suggestions) > 0
        assert suggestions[0].refactoring_type == RefactoringType.EXTRACT_CONSTANT
        assert "42" in suggestions[0].description or "42.0" in suggestions[0].description


class TestConfidenceScoring:
    """Test confidence scoring for refactoring suggestions."""
    
    def test_high_confidence_for_magic_numbers(self):
        """Should have high confidence for magic number extraction."""
        smell = CodeSmell(
            smell_type=CodeSmellType.MAGIC_NUMBER,
            location="test.py:5:10",
            severity="low",
            description="Magic number",
            metric_value=100.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert suggestions[0].confidence >= 0.85
    
    def test_medium_confidence_for_extract_method(self):
        """Should have medium confidence for extract method."""
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_METHOD,
            location="test.py:1:0",
            severity="high",
            description="Long method",
            metric_value=60.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert 0.7 <= suggestions[0].confidence <= 0.85


class TestEffortEstimation:
    """Test effort estimation for refactoring suggestions."""
    
    def test_low_effort_for_extract_constant(self):
        """Should estimate low effort for extracting constants."""
        smell = CodeSmell(
            smell_type=CodeSmellType.MAGIC_NUMBER,
            location="test.py:5:10",
            severity="low",
            description="Magic number",
            metric_value=50.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert suggestions[0].estimated_effort == "low"
    
    def test_medium_effort_for_extract_method(self):
        """Should estimate medium effort for extracting methods."""
        smell = CodeSmell(
            smell_type=CodeSmellType.LONG_METHOD,
            location="test.py:1:0",
            severity="high",
            description="Long method",
            metric_value=70.0,
            confidence=0.9
        )
        
        engine = RefactoringEngine()
        suggestions = engine.generate_suggestions([smell], "")
        
        assert suggestions[0].estimated_effort in ("medium", "high")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

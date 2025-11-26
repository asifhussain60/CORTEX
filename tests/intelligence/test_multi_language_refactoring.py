"""
Test Multi-Language Refactoring System

Tests for Python, JavaScript, TypeScript, and C# code smell detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from src.intelligence import get_refactoring_orchestrator
from src.intelligence.analyzers.base_analyzer import SmellType


# Test fixtures
PYTHON_LONG_METHOD = """
def long_method():
""" + "\n".join([f"    line_{i} = {i}" for i in range(60)]) + """
    return result
"""

PYTHON_COMPLEX_METHOD = """
def process_data(x, y, z, mode):
    # Complexity calculation: 13
    if x > 0:  # +1
        if y > 0:  # +1
            if z > 0:  # +1
                for i in range(x):  # +1
                    if i % 2 == 0:  # +1
                        while y > 0:  # +1
                            y -= 1
                            if z > 5:  # +1
                                if mode == 'strict' and x < 100:  # +2 (and)
                                    return True
                            elif z > 3:  # +1
                                if mode == 'loose' or x > 50:  # +2 (or)
                                    return False
    return False
"""

PYTHON_MAGIC_NUMBERS = """
def calculate_price(quantity):
    base_price = quantity * 42  # Magic number!
    tax = base_price * 0.18  # Another magic number
    return base_price + tax
"""


class TestMultiLanguageRefactoring:
    """Test suite for multi-language refactoring system"""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator singleton initialization"""
        orchestrator = get_refactoring_orchestrator()
        assert orchestrator is not None
        
    def test_supported_languages(self):
        """Test supported languages list"""
        orchestrator = get_refactoring_orchestrator()
        languages = orchestrator.get_supported_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'typescript' in languages
        assert 'csharp' in languages
        
    def test_python_long_method_detection(self):
        """Test Python long method detection"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string(PYTHON_LONG_METHOD, 'python')
        
        assert result['success'] is True
        assert result['language'] == 'python'
        
        # Check for long method smell
        long_method_smells = [s for s in result['smells'] 
                             if s['type'] == SmellType.LONG_METHOD.value]
        assert len(long_method_smells) > 0
        
        smell = long_method_smells[0]
        assert smell['function'] == 'long_method'
        assert smell['confidence'] > 0.70
    
    def test_python_complex_method_detection(self):
        """Test Python complexity detection"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string(PYTHON_COMPLEX_METHOD, 'python')
        
        assert result['success'] is True
        
        # Check for complex method smell
        complex_smells = [s for s in result['smells'] 
                         if s['type'] == SmellType.COMPLEX_METHOD.value]
        assert len(complex_smells) > 0
        
        smell = complex_smells[0]
        assert smell['function'] == 'process_data'
        assert 'complexity' in smell['metadata']
        assert smell['metadata']['complexity'] > 10
    
    def test_python_magic_number_detection(self):
        """Test Python magic number detection"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string(PYTHON_MAGIC_NUMBERS, 'python')
        
        assert result['success'] is True
        
        # Check for magic number smells
        magic_smells = [s for s in result['smells'] 
                       if s['type'] == SmellType.MAGIC_NUMBER.value]
        assert len(magic_smells) > 0
        
    def test_unsupported_language(self):
        """Test handling of unsupported language"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string("code", 'ruby')
        
        assert result['success'] is False
        assert 'unsupported' in result.get('error', '').lower()
        
    def test_invalid_syntax(self):
        """Test handling of invalid Python syntax"""
        orchestrator = get_refactoring_orchestrator()
        code = "def broken(\n    invalid syntax here"
        result = orchestrator.analyze_code_string(code, 'python')
        
        assert result['success'] is False
        assert 'error' in result
        
    def test_confidence_scores(self):
        """Test confidence score ranges"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string(PYTHON_LONG_METHOD, 'python')
        
        assert result['success'] is True
        if result['smells']:
            for smell in result['smells']:
                assert 0.0 <= smell['confidence'] <= 1.0
                
    def test_smell_metadata(self):
        """Test smell metadata population"""
        orchestrator = get_refactoring_orchestrator()
        result = orchestrator.analyze_code_string(PYTHON_LONG_METHOD, 'python')
        
        assert result['success'] is True
        if result['smells']:
            smell = result['smells'][0]
            assert 'metadata' in smell
            assert isinstance(smell['metadata'], dict)

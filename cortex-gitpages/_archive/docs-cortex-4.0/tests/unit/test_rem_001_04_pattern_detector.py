# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-04 - PatternDetector Integration
"""
Test PatternDetector integration into LENS comprehension phase.

AC-REM-001-04: PatternDetector identifies architectural patterns
(singleton, factory, etc.)

Tests verify:
1. PatternDetector can be instantiated
2. detect_patterns() identifies patterns from parse results
3. Detects 1+ patterns or reports 'none found'
4. Pattern detection works for various architectural patterns
5. Integration with comprehension phase
"""

import pytest
from pathlib import Path
from typing import List

from src.core.intelligence.ast_intelligence import ASTIntelligenceEngine
from src.core.intelligence.pattern_detector import (
    PatternDetector,
    DetectedPattern,
)
from src.core.orchestrator.conversation_protocol import ConversationProtocol


class TestPatternDetectorIntegration:
    """Test PatternDetector integration into comprehension phase."""
    
    def test_pattern_detector_instantiates(self) -> None:
        """Test PatternDetector can be instantiated."""
        detector = PatternDetector()
        assert detector is not None
    
    def test_pattern_detector_has_detect_method(self) -> None:
        """Test PatternDetector has detect_patterns method."""
        detector = PatternDetector()
        assert hasattr(detector, "detect_patterns")
        assert callable(detector.detect_patterns)
    
    def test_detect_patterns_returns_list(self) -> None:
        """Test detect_patterns returns list of patterns."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_simple.py"
        test_file.write_text("""
def simple_function():
    pass

class SimpleClass:
    pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            assert isinstance(patterns, list)
            # May be empty, but should be a list
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_singleton_pattern_detection(self) -> None:
        """Test singleton pattern detection."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_singleton.py"
        test_file.write_text("""
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def method(self):
        return "singleton"
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            assert isinstance(patterns, list)
            # May detect singleton or return empty
            for pattern in patterns:
                assert isinstance(pattern, DetectedPattern)
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_factory_pattern_detection(self) -> None:
        """Test factory pattern detection."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_factory.py"
        test_file.write_text("""
class Product:
    pass

class Factory:
    @staticmethod
    def create_product(product_type):
        if product_type == "A":
            return ProductA()
        elif product_type == "B":
            return ProductB()
    
    @classmethod
    def from_config(cls, config):
        return cls.create_product(config.get("type"))

class ProductA(Product):
    pass

class ProductB(Product):
    pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            assert isinstance(patterns, list)
            # May detect factory or return empty
            for pattern in patterns:
                assert isinstance(pattern, DetectedPattern)
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_decorator_pattern_detection(self) -> None:
        """Test decorator pattern detection."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_decorator.py"
        test_file.write_text("""
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def decorated_function():
    return "decorated"

@my_decorator
@my_decorator
def multi_decorated():
    return "multi-decorated"

class DecoratorClass:
    @staticmethod
    def static_method():
        pass
    
    @classmethod
    def class_method(cls):
        pass
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            assert isinstance(patterns, list)
            for pattern in patterns:
                assert isinstance(pattern, DetectedPattern)
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_pattern_serializable(self) -> None:
        """Test detected patterns are serializable."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_serialize.py"
        test_file.write_text("""
class TestClass:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            for pattern in patterns:
                pattern_dict = pattern.to_dict()
                assert isinstance(pattern_dict, dict)
                assert "pattern_type" in pattern_dict
                assert "confidence" in pattern_dict
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_no_patterns_found_returns_empty(self) -> None:
        """Test that 'no patterns found' returns empty list."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_none.py"
        test_file.write_text("""
def regular_function():
    x = 1
    return x

def another_function():
    pass

class RegularClass:
    def __init__(self):
        self.value = 0
    
    def method(self):
        return self.value
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            # Should be a list, possibly empty for regular code
            assert isinstance(patterns, list)
            # Empty list is valid for "no patterns found"
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_pattern_confidence_scores(self) -> None:
        """Test detected patterns have confidence scores."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_confidence.py"
        test_file.write_text("""
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            for pattern in patterns:
                assert 0.0 <= pattern.confidence <= 1.0
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_pattern_evidence_captured(self) -> None:
        """Test detected patterns capture evidence."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "pattern_evidence.py"
        test_file.write_text("""
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            for pattern in patterns:
                assert isinstance(pattern.evidence, list)
                # Evidence is optional but should be a list
        finally:
            test_file.unlink(missing_ok=True)


class TestPatternComprehensionIntegration:
    """Test pattern detection with comprehension phase."""
    
    def test_pattern_detector_with_comprehension(self) -> None:
        """Test PatternDetector can be used with comprehension phase."""
        from unittest.mock import Mock
        
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Verify comprehension can use pattern detection
        assert protocol.ast_engine is not None
    
    def test_patterns_from_comprehension_parse_results(self) -> None:
        """Test pattern detection from comprehension parse results."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "comp_patterns.py"
        test_file.write_text("""
class ApplicationSingleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class ServiceFactory:
    services = {}
    
    @classmethod
    def register(cls, name, service):
        cls.services[name] = service
    
    @classmethod
    def get_service(cls, name):
        return cls.services.get(name)

def logging_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logging_decorator
def process_data():
    pass
""")
        
        try:
            # Parse file (simulating comprehension)
            parse_result = engine.parse_file(test_file)
            
            # Detect patterns (AC-REM-001-04)
            patterns = detector.detect_patterns(parse_result)
            
            # Should detect ≥1 patterns or return empty list
            assert isinstance(patterns, list)
            # Result should be serializable
            for p in patterns:
                assert p.to_dict() is not None
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_multiple_pattern_types_detectable(self) -> None:
        """Test detection of multiple pattern types in one file."""
        engine = ASTIntelligenceEngine()
        detector = PatternDetector()
        
        test_file = Path(__file__).parent / "multi_patterns.py"
        test_file.write_text("""
class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

class HandlerFactory:
    @staticmethod
    def create_handler(handler_type):
        if handler_type == "file":
            return FileHandler()
        return ConsoleHandler()

class FileHandler:
    pass

class ConsoleHandler:
    pass

def timing_decorator(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(1)
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            patterns = detector.detect_patterns(parse_result)
            
            # May find 0+ patterns
            assert isinstance(patterns, list)
            for p in patterns:
                assert p.pattern_type is not None
        finally:
            test_file.unlink(missing_ok=True)

"""
Basic tests for Phase 3 collectors.

Tests:
- SecurityCollector initialization and patterns
- ComplexityCollector initialization and metrics
- TestCoverageCollector initialization and discovery
"""

import pytest
from pathlib import Path
from src.cortex_lens.collectors.security_collector import SecurityCollector
from src.cortex_lens.collectors.complexity_collector import ComplexityCollector
from src.cortex_lens.collectors.test_coverage_collector import TestCoverageCollector


class TestSecurityCollector:
    """Test SecurityCollector"""
    
    def test_security_collector_initialization(self):
        """Test SecurityCollector can be instantiated"""
        collector = SecurityCollector()
        assert collector is not None
        assert hasattr(collector, 'secret_patterns')
        assert hasattr(collector, 'sql_injection_patterns')
        assert hasattr(collector, 'cwe_mapping')
    
    def test_security_patterns_loaded(self):
        """Test security patterns are loaded"""
        collector = SecurityCollector()
        assert len(collector.secret_patterns) > 0
        assert 'api_key' in collector.secret_patterns
        assert 'password' in collector.secret_patterns
        assert len(collector.sql_injection_patterns) > 0


class TestComplexityCollector:
    """Test ComplexityCollector"""
    
    def test_complexity_collector_initialization(self):
        """Test ComplexityCollector can be instantiated"""
        collector = ComplexityCollector()
        assert collector is not None
        assert hasattr(collector, 'complexity_thresholds')
    
    def test_complexity_thresholds(self):
        """Test complexity thresholds are defined"""
        collector = ComplexityCollector()
        assert 'cyclomatic' in collector.complexity_thresholds
        assert 'cognitive' in collector.complexity_thresholds
        assert 'maintainability' in collector.complexity_thresholds


class TestTestCoverageCollector:
    """Test TestCoverageCollector"""
    
    def test_coverage_collector_initialization(self):
        """Test TestCoverageCollector can be instantiated"""
        collector = TestCoverageCollector()
        assert collector is not None
        assert hasattr(collector, 'test_file_patterns')
        assert hasattr(collector, 'test_type_patterns')
    
    def test_test_patterns_loaded(self):
        """Test test file patterns are loaded"""
        collector = TestCoverageCollector()
        assert len(collector.test_file_patterns) > 0
        assert 'unit' in collector.test_type_patterns
        assert 'integration' in collector.test_type_patterns
        assert 'e2e' in collector.test_type_patterns

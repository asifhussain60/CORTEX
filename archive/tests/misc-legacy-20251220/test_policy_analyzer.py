"""
Tests for Policy Analyzer

Purpose: Test policy document parsing and rule extraction capabilities

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import pytest
import tempfile
from pathlib import Path

from src.policy.policy_analyzer import (
    PolicyAnalyzer,
    PolicyDocument,
    PolicyRule,
    PolicyLevel,
    PolicyCategory
)


class TestPolicyAnalyzer:
    """Test suite for PolicyAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create PolicyAnalyzer instance"""
        return PolicyAnalyzer()
    
    @pytest.fixture
    def sample_policy_content(self):
        """Sample policy document content"""
        return """# Test Security Policy
Version: 1.0
Date: 2025-11-26
Author: CORTEX Team
Scope: All Python projects

## Security Requirements

- Passwords MUST NOT be stored in plain text.
- All user input MUST be validated and sanitized.
- API keys SHOULD NOT be hardcoded in source files.
- Authentication tokens MAY expire after 24 hours.

## Testing Requirements

- Test coverage MUST be greater than 80%.
Rationale: High coverage ensures code reliability.

- Unit tests SHOULD run in less than 5 seconds.

## Performance Requirements

- API response time MUST be under 200ms for 95th percentile.
"""
    
    @pytest.fixture
    def temp_policy_file(self, sample_policy_content):
        """Create temporary policy file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(sample_policy_content)
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink()
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert len(analyzer.supported_formats) > 0
        assert '.md' in analyzer.supported_formats
        assert '.pdf' in analyzer.supported_formats
    
    def test_analyze_file(self, analyzer, temp_policy_file):
        """Test analyzing a policy file"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        assert isinstance(doc, PolicyDocument)
        assert doc.file_path == temp_policy_file
        assert doc.format == 'md'  # Returns extension without dot
        assert doc.file_hash is not None
        assert len(doc.file_hash) == 64  # SHA256
    
    def test_extract_metadata(self, analyzer, temp_policy_file):
        """Test metadata extraction"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        assert doc.title == "Test Security Policy"
        assert doc.version == "1.0"
        assert doc.metadata.get('author') == "CORTEX Team"
        assert doc.metadata.get('scope') == "All Python projects"
    
    def test_extract_rules(self, analyzer, temp_policy_file):
        """Test rule extraction"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        assert len(doc.rules) > 0
        assert all(isinstance(rule, PolicyRule) for rule in doc.rules)
    
    def test_detect_must_level(self, analyzer):
        """Test MUST level detection"""
        text = "Passwords MUST NOT be stored in plain text"
        level = analyzer._detect_level(text)
        assert level == PolicyLevel.MUST_NOT
        
        text2 = "Test coverage MUST be greater than 80%"
        level2 = analyzer._detect_level(text2)
        assert level2 == PolicyLevel.MUST
    
    def test_detect_should_level(self, analyzer):
        """Test SHOULD level detection"""
        text = "Unit tests SHOULD run in less than 5 seconds"
        level = analyzer._detect_level(text)
        assert level == PolicyLevel.SHOULD
        
        text2 = "API keys SHOULD NOT be hardcoded"
        level2 = analyzer._detect_level(text2)
        assert level2 == PolicyLevel.SHOULD_NOT
    
    def test_detect_may_level(self, analyzer):
        """Test MAY level detection"""
        text = "Authentication tokens MAY expire after 24 hours"
        level = analyzer._detect_level(text)
        assert level == PolicyLevel.MAY
    
    def test_detect_security_category(self, analyzer):
        """Test security category detection"""
        text = "Passwords must not be stored in plain text for security and authentication"
        category = analyzer._detect_category(text)
        assert category == PolicyCategory.SECURITY
    
    def test_detect_testing_category(self, analyzer):
        """Test testing category detection"""
        text = "Test coverage MUST be greater than 80%"
        category = analyzer._detect_category(text)
        assert category == PolicyCategory.TESTING
    
    def test_detect_performance_category(self, analyzer):
        """Test performance category detection"""
        text = "API response time and latency MUST be under 200ms for performance"
        category = analyzer._detect_category(text)
        assert category == PolicyCategory.PERFORMANCE
    
    def test_extract_threshold(self, analyzer):
        """Test threshold extraction"""
        text = "Test coverage MUST be greater than 80%"
        threshold, unit = analyzer._extract_threshold(text)
        assert threshold == 80.0
        assert unit == '%'
        
        text2 = "Response time MUST be under 200ms"
        threshold2, unit2 = analyzer._extract_threshold(text2)
        assert threshold2 == 200.0
        assert unit2 == 'ms'
    
    def test_get_rules_by_level(self, analyzer, temp_policy_file):
        """Test filtering rules by level"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        must_rules = analyzer.get_rules_by_level(doc, PolicyLevel.MUST)
        assert len(must_rules) > 0
        assert all(rule.level == PolicyLevel.MUST for rule in must_rules)
    
    def test_get_rules_by_category(self, analyzer, temp_policy_file):
        """Test filtering rules by category"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        security_rules = analyzer.get_rules_by_category(doc, PolicyCategory.SECURITY)
        assert len(security_rules) > 0
        assert all(rule.category == PolicyCategory.SECURITY for rule in security_rules)
    
    def test_get_critical_rules(self, analyzer, temp_policy_file):
        """Test getting critical rules"""
        doc = analyzer.analyze_file(temp_policy_file)
        
        critical = analyzer.get_critical_rules(doc)
        assert len(critical) > 0
        assert all(rule.level in [PolicyLevel.MUST, PolicyLevel.MUST_NOT] for rule in critical)
    
    def test_unsupported_format(self, analyzer):
        """Test handling of unsupported file format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            # Should raise error for unsupported format
            with pytest.raises((ValueError, NotImplementedError)):
                analyzer.analyze_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_missing_file(self, analyzer):
        """Test handling of missing file"""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file("nonexistent_file.md")
    
    def test_rule_to_dict(self):
        """Test PolicyRule serialization"""
        rule = PolicyRule(
            id="RULE-001",
            text="Test MUST pass",
            level=PolicyLevel.MUST,
            category=PolicyCategory.TESTING,
            keywords=["test"],
            threshold=80.0,
            unit="%"
        )
        
        rule_dict = rule.to_dict()
        assert rule_dict['id'] == "RULE-001"
        assert rule_dict['level'] == "MUST"
        assert rule_dict['category'] == "testing"
    
    def test_document_to_dict(self, analyzer, temp_policy_file):
        """Test PolicyDocument serialization"""
        doc = analyzer.analyze_file(temp_policy_file)
        doc_dict = doc.to_dict()
        
        assert 'file_path' in doc_dict
        assert 'file_hash' in doc_dict
        assert 'rules' in doc_dict
        assert isinstance(doc_dict['rules'], list)

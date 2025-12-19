"""
Proactive Intelligence Module - Comprehensive tests.

Tests for proactive advisor, risk assessor, and domain classifier.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from dataclasses import dataclass

from src.operations.modules.intelligence.proactive_advisor import (
    ProactiveAdvisor,
    ProactiveRecommendation
)
from src.operations.modules.intelligence.risk_assessor import (
    RiskAssessor,
    RiskAssessment,
    RiskLevel
)
from src.operations.modules.intelligence.domain_classifier import (
    DomainClassifier,
    DomainClassification,
    Criticality
)


# Test Data Structures
@dataclass
class MockDuplicateGroup:
    similarity_score: float
    locations: list
    lines_count: int
    recommendation: str


@dataclass
class MockViolation:
    severity: str
    violation_type: str
    description: str
    recommendation: str


@dataclass
class MockCodeSmell:
    severity: str
    smell_type: str
    file_path: str
    description: str
    recommendation: str


class TestProactiveAdvisor:
    """Test ProactiveAdvisor functionality."""
    
    @pytest.fixture
    def ast_engine(self):
        """Mock AST engine."""
        engine = Mock()
        return engine
        
    @pytest.fixture
    def analyzers(self, ast_engine):
        """Mock analyzers."""
        dedup_analyzer = Mock()
        dedup_analyzer.analyze.return_value = {
            'total_duplicates': 5,
            'duplicate_groups': [
                MockDuplicateGroup(
                    similarity_score=0.98,
                    locations=['file1.py', 'file2.py'],
                    lines_count=50,
                    recommendation="Extract to shared module"
                )
            ]
        }
        
        arch_analyzer = Mock()
        arch_analyzer.analyze.return_value = {
            'high_severity_count': 2,
            'violations': [
                MockViolation(
                    severity='high',
                    violation_type='circular_dependency',
                    description="Circular dependency detected",
                    recommendation="Break cycle with dependency injection"
                )
            ]
        }
        
        smell_analyzer = Mock()
        smell_analyzer.analyze.return_value = {
            'total_smells': 10,
            'priority_fixes': [
                "src/test.py:100 - Class 'TestClass' has 20 methods: Split into focused classes"
            ]
        }
        
        return {
            'deduplication': dedup_analyzer,
            'architecture': arch_analyzer,
            'code_smell': smell_analyzer
        }
        
    def test_initialization(self, ast_engine, analyzers):
        """Test advisor initialization."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        assert advisor.ast_engine == ast_engine
        assert advisor.analyzers == analyzers
        assert len(advisor.triggers) == 6
        
    def test_generate_recommendations(self, ast_engine, analyzers):
        """Test recommendation generation."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        recommendations = advisor.generate_recommendations()
        
        assert len(recommendations) > 0
        assert all(isinstance(r, ProactiveRecommendation) for r in recommendations)
        
    def test_duplicate_refactor_recommendations(self, ast_engine, analyzers):
        """Test duplicate code recommendations."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        recommendations = advisor.generate_recommendations()
        
        # Should have duplicate refactor recommendation
        duplicate_recs = [r for r in recommendations if 'duplicate' in r.title.lower()]
        assert len(duplicate_recs) > 0
        assert duplicate_recs[0].category == "code_quality"
        assert duplicate_recs[0].priority == "high"
        
    def test_architecture_fix_recommendations(self, ast_engine, analyzers):
        """Test architecture violation recommendations."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        recommendations = advisor.generate_recommendations()
        
        # Should have architecture fix recommendation
        arch_recs = [r for r in recommendations if r.category == "architecture"]
        assert len(arch_recs) > 0
        assert "circular dependency" in arch_recs[0].title.lower()
        
    def test_priority_ordering(self, ast_engine, analyzers):
        """Test recommendations are ordered by priority."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        recommendations = advisor.generate_recommendations()
        
        # Verify ordering: high, medium, low
        priorities = [r.priority for r in recommendations]
        for i in range(len(priorities) - 1):
            current = {'high': 0, 'medium': 1, 'low': 2}[priorities[i]]
            next_priority = {'high': 0, 'medium': 1, 'low': 2}[priorities[i + 1]]
            assert current <= next_priority
            
    def test_format_recommendations(self, ast_engine, analyzers):
        """Test recommendation formatting."""
        advisor = ProactiveAdvisor(ast_engine, analyzers)
        
        recommendations = advisor.generate_recommendations()
        formatted = advisor.format_recommendations(recommendations)
        
        assert "## 💡 Proactive Recommendations" in formatted
        assert len(formatted) > 100  # Should be substantial report


class TestRiskAssessor:
    """Test RiskAssessor functionality."""
    
    @pytest.fixture
    def ast_engine(self):
        """Mock AST engine."""
        engine = Mock()
        engine.analyze_architecture.return_value = {
            'dependencies': {
                'moduleA.py': ['moduleB.py'],
                'moduleB.py': ['moduleC.py']
            }
        }
        return engine
        
    @pytest.fixture
    def domain_classifier(self):
        """Mock domain classifier."""
        classifier = Mock()
        classifier.classify.return_value = DomainClassification(
            file_path="test.py",
            domain_type="authentication",
            criticality=Criticality.CRITICAL,
            confidence=0.9,
            indicators=["auth", "login"]
        )
        return classifier
        
    def test_initialization(self, ast_engine):
        """Test assessor initialization."""
        assessor = RiskAssessor(ast_engine)
        
        assert assessor.ast_engine == ast_engine
        
    def test_assess_risk_basic(self, ast_engine):
        """Test basic risk assessment."""
        assessor = RiskAssessor(ast_engine)
        
        risks = assessor.assess_risk(
            "Delete user data",
            {'operation_type': 'delete'}
        )
        
        assert len(risks) > 0
        assert all(isinstance(r, RiskAssessment) for r in risks)
        
    def test_data_loss_risk_detection(self, ast_engine):
        """Test data loss risk detection."""
        assessor = RiskAssessor(ast_engine)
        
        risks = assessor.assess_risk(
            "Delete database",
            {'operation_type': 'delete_database'}
        )
        
        # Should detect data loss risk
        data_loss_risks = [r for r in risks if r.category == "data_loss"]
        assert len(data_loss_risks) > 0
        assert data_loss_risks[0].risk_level == RiskLevel.CRITICAL
        
    def test_security_risk_detection(self, ast_engine):
        """Test security risk detection."""
        assessor = RiskAssessor(ast_engine)
        
        risks = assessor.assess_risk(
            "Modify authentication",
            {'operation': 'update_auth_system'}
        )
        
        # Should detect security risk
        security_risks = [r for r in risks if r.category == "security"]
        assert len(security_risks) > 0
        assert security_risks[0].risk_level == RiskLevel.HIGH
        
    def test_domain_criticality_assessment(self, ast_engine, domain_classifier):
        """Test domain-specific risk assessment."""
        assessor = RiskAssessor(ast_engine, domain_classifier)
        
        risks = assessor.assess_risk(
            "Update auth module",
            {'affected_files': ['auth.py']}
        )
        
        # Should detect high risk due to critical domain
        domain_risks = [r for r in risks if r.category == "domain_criticality"]
        assert len(domain_risks) > 0
        
    def test_risk_level_ordering(self, ast_engine):
        """Test risks are ordered by severity."""
        assessor = RiskAssessor(ast_engine)
        
        risks = assessor.assess_risk(
            "Delete and update auth",
            {
                'operation_type': 'delete',
                'operation': 'update_auth'
            }
        )
        
        # Verify ordering: CRITICAL, HIGH, MEDIUM, LOW
        severity_order = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3
        }
        
        for i in range(len(risks) - 1):
            current = severity_order[risks[i].risk_level]
            next_level = severity_order[risks[i + 1].risk_level]
            assert current <= next_level
            
    def test_should_block_execution(self, ast_engine):
        """Test execution blocking decision."""
        assessor = RiskAssessor(ast_engine)
        
        # CRITICAL risk should block
        critical_risks = [
            RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                category="data_loss",
                description="Critical issue",
                affected_components=[],
                mitigation_steps=[],
                requires_manual_review=True
            )
        ]
        assert assessor.should_block_execution(critical_risks) is True
        
        # HIGH risk should not block
        high_risks = [
            RiskAssessment(
                risk_level=RiskLevel.HIGH,
                category="security",
                description="High risk issue",
                affected_components=[],
                mitigation_steps=[],
                requires_manual_review=False
            )
        ]
        assert assessor.should_block_execution(high_risks) is False
        
    def test_format_risk_report(self, ast_engine):
        """Test risk report formatting."""
        assessor = RiskAssessor(ast_engine)
        
        risks = assessor.assess_risk(
            "Delete operation",
            {'operation_type': 'delete'}
        )
        
        report = assessor.format_risk_report(risks)
        
        assert "## ⚠️ Risk Assessment Report" in report
        assert len(report) > 100


class TestDomainClassifier:
    """Test DomainClassifier functionality."""
    
    def test_initialization(self):
        """Test classifier initialization."""
        classifier = DomainClassifier()
        
        assert len(classifier.patterns) > 0
        
    def test_classify_payment_domain(self, tmp_path):
        """Test payment domain classification."""
        file_path = tmp_path / "payment_processor.py"
        file_path.write_text("def process_payment(amount): pass")
        
        classifier = DomainClassifier()
        result = classifier.classify(file_path)
        
        assert result.domain_type == "payment"
        assert result.criticality == Criticality.CRITICAL
        assert result.confidence > 0.5
        
    def test_classify_auth_domain(self, tmp_path):
        """Test authentication domain classification."""
        file_path = tmp_path / "auth_handler.py"
        file_path.write_text("def login(username, password): pass")
        
        classifier = DomainClassifier()
        result = classifier.classify(file_path)
        
        assert result.domain_type == "authentication"
        assert result.criticality == Criticality.CRITICAL
        
    def test_classify_ui_domain(self, tmp_path):
        """Test UI domain classification."""
        file_path = tmp_path / "ui_component.py"
        file_path.write_text("def render_widget(): pass")
        
        classifier = DomainClassifier()
        result = classifier.classify(file_path)
        
        assert result.domain_type == "ui"
        assert result.criticality == Criticality.LOW
        
    def test_classify_unknown_domain(self, tmp_path):
        """Test unknown domain classification."""
        file_path = tmp_path / "xyz123.py"
        file_path.write_text("x = 42")
        
        classifier = DomainClassifier()
        result = classifier.classify(file_path)
        
        assert result.domain_type == "unknown"
        assert result.criticality == Criticality.LOW
        
    def test_classify_bulk(self, tmp_path):
        """Test bulk classification."""
        files = []
        for name in ['payment.py', 'auth.py', 'ui.py']:
            fp = tmp_path / name
            fp.write_text(f"# {name}")
            files.append(fp)
            
        classifier = DomainClassifier()
        results = classifier.classify_bulk(files)
        
        assert len(results) == 3
        assert all(isinstance(r, DomainClassification) for r in results)
        
    def test_get_critical_files(self, tmp_path):
        """Test filtering critical files."""
        payment_file = tmp_path / "payment.py"
        payment_file.write_text("def charge_card(): pass")
        
        ui_file = tmp_path / "ui.py"
        ui_file.write_text("def render(): pass")
        
        classifier = DomainClassifier()
        critical = classifier.get_critical_files([payment_file, ui_file])
        
        assert len(critical) == 1
        assert critical[0] == payment_file

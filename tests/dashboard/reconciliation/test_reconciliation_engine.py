"""
Tests for ReconciliationEngine

Tests the main orchestrator that coordinates all reconciliation components.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from src.dashboard.reconciliation.reconciliation_engine import ReconciliationEngine
from src.dashboard.reconciliation.models import Violation, Anomaly


class TestReconciliationEngine:
    """Test suite for ReconciliationEngine main orchestrator"""
    
    @pytest.fixture
    def engine(self):
        """Create ReconciliationEngine instance"""
        return ReconciliationEngine()
    
    @pytest.fixture
    def perfect_data(self):
        """Dataset 1: Perfect scores - no violations or anomalies"""
        return {
            'security_score': 95,
            'quality_score': 92,
            'maintainability_score': 88,
            'architecture_score': 90,
            'test_coverage': 85,
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'code_smells': 2,
            'cyclomatic_complexity': 8,
            'security_hotspots': 0
        }
    
    @pytest.fixture
    def critical_vuln_data(self):
        """Dataset 2: Critical vulnerabilities - should cap security score"""
        return {
            'security_score': 85,
            'quality_score': 75,
            'maintainability_score': 70,
            'architecture_score': 80,
            'test_coverage': 60,
            'critical_vulnerabilities': 3,
            'high_vulnerabilities': 5,
            'code_smells': 15,
            'cyclomatic_complexity': 12,
            'security_hotspots': 8
        }
    
    @pytest.fixture
    def low_security_quality_data(self):
        """Dataset 3: Low security + quality BUT high other scores - should trigger R8 cap"""
        return {
            'security_score': 35,
            'quality_score': 40,
            'maintainability_score': 95,  # High to push overall >50
            'architecture_score': 90,      # High to push overall >50
            'test_coverage': 85,            # High to push overall >50
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 12,
            'code_smells': 45,
            'cyclomatic_complexity': 18,
            'security_hotspots': 15
        }
    
    @pytest.fixture
    def architecture_anomaly_data(self):
        """Dataset 4: High architecture, low security - should detect R9 anomaly"""
        return {
            'security_score': 25,
            'quality_score': 60,
            'maintainability_score': 65,
            'architecture_score': 85,
            'test_coverage': 50,
            'critical_vulnerabilities': 2,
            'high_vulnerabilities': 20,
            'code_smells': 30,
            'cyclomatic_complexity': 14,
            'security_hotspots': 25
        }
    
    def test_engine_initialization(self, engine):
        """Test ReconciliationEngine initializes correctly"""
        assert engine is not None
        assert hasattr(engine, 'reconcile')
        assert hasattr(engine, 'score_normalizer')
        assert hasattr(engine, 'cvss_normalizer')
        assert hasattr(engine, 'cross_tab_validator')
    
    def test_perfect_data_reconciliation(self, engine, perfect_data):
        """Test reconciliation with perfect data - no violations"""
        result = engine.reconcile(perfect_data, repository="test-repo")
        
        assert result is not None
        assert len(result.violations) == 0
        assert len(result.anomalies) == 0
        assert result.reconciled_data['overall_score'] >= 88  # Weighted average should be high
        assert result.repository == "test-repo"
    
    def test_critical_vuln_reconciliation(self, engine, critical_vuln_data):
        """Test reconciliation with critical vulnerabilities"""
        result = engine.reconcile(critical_vuln_data, repository="vuln-repo")
        
        assert result is not None
        # Security score might be adjusted (checking reconciled data)
        assert 'security_score' in result.reconciled_data
    
    def test_low_security_quality_cap(self, engine, low_security_quality_data):
        """Test R8: Low security + quality should cap overall score"""
        result = engine.reconcile(low_security_quality_data, repository="low-sq-repo")
        
        assert result is not None
        # Should have violation for R8 cap
        violations = [v for v in result.violations if v.rule_id == 'R8']
        assert len(violations) > 0
        # Overall score should be capped at 50
        assert result.reconciled_data['overall_score'] <= 50
    
    def test_architecture_anomaly_detection(self, engine, architecture_anomaly_data):
        """Test R9: High architecture with low security should trigger anomaly"""
        result = engine.reconcile(architecture_anomaly_data, repository="anomaly-repo")
        
        assert result is not None
        # Should detect R9 anomaly - check anomalies list
        assert len(result.anomalies) > 0, f"Expected anomalies but got none. Data: {architecture_anomaly_data}"
        # First anomaly should have high confidence
        assert result.anomalies[0].confidence >= 0.8
    
    def test_audit_trail_creation(self, engine, critical_vuln_data):
        """Test that audit trail is properly created"""
        result = engine.reconcile(critical_vuln_data, repository="audit-repo")
        
        assert result.audit_trail is not None
        # Audit trail should exist (may be empty for perfect data, populated for violations)
        assert isinstance(result.audit_trail.changes, list)
    
    def test_weighted_scoring_calculation(self, engine, perfect_data):
        """Test that overall score uses correct weights"""
        result = engine.reconcile(perfect_data, repository="weight-repo")
        
        # Calculate expected weighted average
        expected = (
            perfect_data['security_score'] * 0.35 +
            perfect_data['quality_score'] * 0.25 +
            perfect_data['maintainability_score'] * 0.15 +
            perfect_data['architecture_score'] * 0.15 +
            perfect_data['test_coverage'] * 0.10
        )
        
        # Allow small rounding difference
        assert abs(result.reconciled_data['overall_score'] - expected) < 0.1
    
    def test_score_normalization(self, engine):
        """Test that scores are normalized to 0-100 range"""
        data = {
            'security_score': 150,  # Out of range
            'quality_score': -10,   # Negative
            'maintainability_score': 75,
            'architecture_score': 80,
            'test_coverage': 60,
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'code_smells': 5,
            'cyclomatic_complexity': 10,
            'security_hotspots': 0
        }
        
        result = engine.reconcile(data, repository="normalize-repo")
        
        # All reconciled scores should be 0-100
        assert 0 <= result.reconciled_data['security_score'] <= 100
        assert 0 <= result.reconciled_data['quality_score'] <= 100
        assert 0 <= result.reconciled_data['maintainability_score'] <= 100
        assert 0 <= result.reconciled_data['architecture_score'] <= 100
        assert 0 <= result.reconciled_data['test_coverage'] <= 100
    
    def test_result_serialization(self, engine, perfect_data):
        """Test that result can be serialized to dict"""
        result = engine.reconcile(perfect_data, repository="serialize-repo")
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert 'reconciled_data' in result_dict
        assert 'overall_score' in result_dict['reconciled_data']
        assert 'violations' in result_dict
        assert 'anomalies' in result_dict
        assert 'audit_trail' in result_dict
        assert 'metrics' in result_dict

"""
Tests for E2E Test Prioritizer
Phase 7.5.2 - RED Phase

Tests extensible criteria system with 8 criteria:
1. Code Complexity
2. Risk Score (Complexity × Change Frequency)
3. Business Value
4. User Impact
5. Regulatory Compliance
6. Data Integrity
7. External Dependency Risk
8. Change Frequency (Regression Risk)
"""

import pytest
from typing import Dict, Any


class TestE2ETestPrioritizer:
    """Test suite for E2E test prioritization"""

    def test_complexity_criterion_high(self):
        """Test complexity criterion with high complexity code"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Payment Processing',
            'file': 'payment_service.py',
            'complexity': 35
        }
        
        # Act
        score = prioritizer.evaluate_complexity_criterion(scenario)
        
        # Assert
        assert score > 0
        assert score >= 80  # High complexity threshold

    def test_risk_score_calculation(self):
        """Test risk score = complexity × change_frequency"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'complexity': 20,
            'change_frequency': 15
        }
        
        # Act
        risk_score = prioritizer.calculate_risk_score(scenario)
        
        # Assert
        assert risk_score == 300  # 20 * 15
        assert risk_score > 0

    def test_business_value_payment_keywords(self):
        """Test business value detection from payment keywords"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Process Payment',
            'description': 'Handle credit card payment processing'
        }
        
        # Act
        score = prioritizer.evaluate_business_value(scenario)
        
        # Assert
        assert score > 0
        assert score >= 80  # High business value

    def test_regulatory_compliance_pci_detection(self):
        """Test PCI-DSS regulatory pattern detection"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Payment Processing',
            'description': 'Handle credit card data and CVV'
        }
        
        # Act
        result = prioritizer.detect_regulatory_requirements(scenario)
        
        # Assert
        assert 'PCI-DSS' in result
        assert result['PCI-DSS'] is True

    def test_regulatory_compliance_gdpr_detection(self):
        """Test GDPR regulatory pattern detection"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'description': 'Process personal data with user consent for GDPR compliance'
        }
        
        # Act
        result = prioritizer.detect_regulatory_requirements(scenario)
        
        # Assert
        assert 'GDPR' in result
        assert result['GDPR'] is True

    def test_regulatory_compliance_hipaa_detection(self):
        """Test HIPAA regulatory pattern detection"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'description': 'Handle protected health information (PHI) and medical records'
        }
        
        # Act
        result = prioritizer.detect_regulatory_requirements(scenario)
        
        # Assert
        assert 'HIPAA' in result
        assert result['HIPAA'] is True

    def test_regulatory_compliance_sox_detection(self):
        """Test SOX regulatory pattern detection"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'description': 'Financial reporting with audit trail for Sarbanes-Oxley compliance'
        }
        
        # Act
        result = prioritizer.detect_regulatory_requirements(scenario)
        
        # Assert
        assert 'SOX' in result
        assert result['SOX'] is True

    def test_auto_promote_to_p0_regulatory(self):
        """Test auto-promotion to P0 for regulatory scenarios"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Payment Processing',
            'description': 'Handle credit card payment with PCI compliance',
            'complexity': 15
        }
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority == 'P0'

    def test_user_impact_high_traffic(self):
        """Test user impact for high-traffic endpoints"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'endpoint_calls': 5000
        }
        
        # Act
        score = prioritizer.evaluate_user_impact(scenario)
        
        # Assert
        assert score > 0
        assert score >= 80  # High user impact

    def test_data_integrity_financial_keywords(self):
        """Test data integrity detection for financial transactions"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'description': 'Process financial transaction with money transfer and balance update'
        }
        
        # Act
        score = prioritizer.evaluate_data_integrity(scenario)
        
        # Assert
        assert score > 0

    def test_dependency_risk_external_services(self):
        """Test dependency risk for external service calls"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'has_external_dependencies': True,
            'external_services': ['stripe', 'sendgrid']
        }
        
        # Act
        score = prioritizer.evaluate_dependency_risk(scenario)
        
        # Assert
        assert score > 0

    def test_change_frequency_high_churn(self):
        """Test change frequency for high-churn files"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'change_frequency': 25
        }
        
        # Act
        score = prioritizer.evaluate_change_frequency(scenario)
        
        # Assert
        assert score > 0
        assert score >= 80  # Critical threshold

    def test_priority_p0_high_score(self):
        """Test P0 priority assignment for high total score"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Critical Payment Flow',
            'description': 'credit card payment',
            'complexity': 30,
            'change_frequency': 20,
            'endpoint_calls': 3000
        }
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority == 'P0'

    def test_priority_p1_medium_high_score(self):
        """Test P1 priority assignment for medium-high score"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Payment processing workflow with order handling transaction billing',
            'description': 'Test checkout process with billing invoice financial',
            'complexity': 20,
            'change_frequency': 12,
            'endpoint_calls': 900,
            'has_external_dependencies': True,
            'external_services': ['PaymentGateway', 'EmailService', 'TaxCalculator']
        }
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority in ['P0', 'P1']

    def test_priority_p2_medium_score(self):
        """Test P2 priority assignment for medium score"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Report Generation',
            'complexity': 10,
            'change_frequency': 5
        }
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority in ['P1', 'P2', 'P3']

    def test_priority_p3_low_score(self):
        """Test P3 priority assignment for low score"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Utility Function',
            'complexity': 5,
            'change_frequency': 1
        }
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority == 'P3'

    def test_prioritize_scenarios_batch(self):
        """Test batch prioritization of multiple scenarios"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenarios = [
            {'name': 'Payment', 'description': 'credit card', 'complexity': 30},
            {'name': 'Login', 'complexity': 10},
            {'name': 'Report', 'complexity': 8}
        ]
        
        # Act
        result = prioritizer.prioritize_scenarios(scenarios)
        
        # Assert
        assert len(result) == 3
        assert all('priority' in s for s in result)
        assert all('score' in s for s in result)

    def test_scenario_sorting_by_priority(self):
        """Test scenarios are sorted by priority"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenarios = [
            {'name': 'Low', 'complexity': 5},
            {'name': 'High', 'description': 'payment credit card', 'complexity': 30},
            {'name': 'Medium', 'complexity': 15}
        ]
        
        # Act
        result = prioritizer.prioritize_scenarios(scenarios)
        
        # Assert
        priorities = [s['priority'] for s in result]
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        for i in range(len(priorities) - 1):
            assert priority_order[priorities[i]] <= priority_order[priorities[i + 1]]

    def test_criteria_weights_configuration(self):
        """Test criteria weights can be configured"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        
        custom_weights = {
            'complexity': 40,
            'risk_score': 30,
            'business_value': 30
        }
        
        # Act
        prioritizer = E2ETestPrioritizer(criteria_weights=custom_weights)
        
        # Assert
        assert prioritizer.criteria_weights['complexity'] == 40

    def test_threshold_configuration(self):
        """Test priority thresholds can be configured"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        
        custom_thresholds = {
            'p0': 85,
            'p1': 65,
            'p2': 45,
            'p3': 0
        }
        
        # Act
        prioritizer = E2ETestPrioritizer(priority_thresholds=custom_thresholds)
        
        # Assert
        assert prioritizer.priority_thresholds['p0'] == 85

    def test_generate_recommendations_from_priorities(self):
        """Test recommendation generation from prioritized scenarios"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenarios = [
            {'name': 'Payment', 'description': 'credit card', 'complexity': 30},
            {'name': 'Login', 'complexity': 15}
        ]
        
        # Act
        result = prioritizer.generate_recommendations(scenarios)
        
        # Assert
        assert 'p0_critical' in result
        assert 'p1_high' in result
        assert 'p2_medium' in result
        assert 'p3_low' in result
        assert isinstance(result['p0_critical'], list)

    def test_empty_scenario_handling(self):
        """Test handling of empty scenario list"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        # Act
        result = prioritizer.prioritize_scenarios([])
        
        # Assert
        assert result == []

    def test_missing_criteria_data(self):
        """Test handling of scenarios with missing criteria data"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {'name': 'Test'}  # Minimal data
        
        # Act
        priority = prioritizer.calculate_priority(scenario)
        
        # Assert
        assert priority in ['P0', 'P1', 'P2', 'P3']

    def test_normalized_score_range(self):
        """Test normalized score is always 0-100"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'complexity': 50,
            'change_frequency': 50,
            'endpoint_calls': 10000
        }
        
        # Act
        score = prioritizer.calculate_normalized_score(scenario)
        
        # Assert
        assert 0 <= score <= 100

    def test_criteria_scoring_details(self):
        """Test detailed criteria scoring breakdown"""
        # Arrange
        from src.dashboard.intelligence.e2e_test_prioritizer import E2ETestPrioritizer
        prioritizer = E2ETestPrioritizer()
        
        scenario = {
            'name': 'Payment',
            'description': 'credit card processing',
            'complexity': 25,
            'change_frequency': 15
        }
        
        # Act
        details = prioritizer.get_scoring_details(scenario)
        
        # Assert
        assert 'criteria_scores' in details
        assert 'total_score' in details
        assert 'priority' in details
        assert isinstance(details['criteria_scores'], dict)

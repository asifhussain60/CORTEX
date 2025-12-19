"""Unit tests for DomainClassifier

Tests cover:
- CRITICAL domain detection (security, compliance, financial)
- STANDARD domain detection (UI, utilities, API clients)
- SIMPLE domain detection (docs, config, fixtures)
- OWASP Top 10 security pattern recognition
- Analysis depth configuration
- Confidence scoring

Author: Asif Hussain
Phase: 02 of CORTEX Evolution v3.9
"""

import pytest
from src.operations.modules.routing.domain_classifier import (
    DomainClassifier,
    DomainClassification,
    DomainCriticality
)


class TestDomainClassifier:
    """Test DomainClassifier criticality detection."""
    
    def test_critical_domain_authentication(self):
        """Test CRITICAL: authentication domain."""
        classifier = DomainClassifier()
        result = classifier.classify("Add JWT authentication to API")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert result.analysis_depth == "deep"
        assert "security_auth" in result.domains
        assert result.confidence > 0.0
    
    def test_critical_domain_payment(self):
        """Test CRITICAL: payment processing."""
        classifier = DomainClassifier()
        result = classifier.classify("Implement Stripe payment gateway")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert result.analysis_depth == "deep"
        assert "financial_operations" in result.domains
    
    def test_critical_domain_encryption(self):
        """Test CRITICAL: encryption/cryptography."""
        classifier = DomainClassifier()
        result = classifier.classify("Add AES encryption for user data")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "security_crypto" in result.domains
    
    def test_critical_domain_compliance(self):
        """Test CRITICAL: compliance (GDPR, HIPAA, PCI)."""
        classifier = DomainClassifier()
        result = classifier.classify("Implement GDPR data retention policy")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "compliance_privacy" in result.domains
    
    def test_critical_domain_business_logic(self):
        """Test CRITICAL: business logic/workflows."""
        classifier = DomainClassifier()
        result = classifier.classify("Create approval workflow for orders")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "business_logic" in result.domains
    
    def test_standard_domain_ui_component(self):
        """Test STANDARD: UI component."""
        classifier = DomainClassifier()
        result = classifier.classify("Create React button component")
        
        assert result.criticality == DomainCriticality.STANDARD
        assert result.analysis_depth == "moderate"
        assert "ui_components" in result.domains
    
    def test_standard_domain_utility(self):
        """Test STANDARD: utility function."""
        classifier = DomainClassifier()
        result = classifier.classify("Add string formatter utility")
        
        assert result.criticality == DomainCriticality.STANDARD
        assert "utilities" in result.domains
    
    def test_standard_domain_api_client(self):
        """Test STANDARD: API client."""
        classifier = DomainClassifier()
        result = classifier.classify("Create GraphQL client wrapper")
        
        assert result.criticality == DomainCriticality.STANDARD
        assert "api_clients" in result.domains
    
    def test_simple_domain_documentation(self):
        """Test SIMPLE: documentation."""
        classifier = DomainClassifier()
        result = classifier.classify("Update README with installation steps")
        
        assert result.criticality == DomainCriticality.SIMPLE
        assert result.analysis_depth == "light"
        assert "documentation" in result.domains
    
    def test_simple_domain_configuration(self):
        """Test SIMPLE: configuration."""
        classifier = DomainClassifier()
        result = classifier.classify("Add new environment variable to .env")
        
        assert result.criticality == DomainCriticality.SIMPLE
        assert "configuration" in result.domains
    
    def test_simple_domain_test_fixtures(self):
        """Test SIMPLE: test fixtures."""
        classifier = DomainClassifier()
        result = classifier.classify("Create mock data for user tests")
        
        assert result.criticality == DomainCriticality.SIMPLE
        assert "test_fixtures" in result.domains
    
    def test_security_pattern_sql_injection(self):
        """Test OWASP: SQL injection detection."""
        classifier = DomainClassifier()
        result = classifier.classify("Fix SQL injection vulnerability in query")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "A03_injection" in result.security_patterns
    
    def test_security_pattern_xss(self):
        """Test OWASP: XSS detection."""
        classifier = DomainClassifier()
        result = classifier.classify("Prevent XSS attacks in user input")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "A03_injection" in result.security_patterns
    
    def test_security_pattern_broken_access_control(self):
        """Test OWASP: broken access control."""
        classifier = DomainClassifier()
        result = classifier.classify("Fix authorization bypass vulnerability")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "A01_broken_access_control" in result.security_patterns
    
    def test_security_pattern_weak_crypto(self):
        """Test OWASP: weak cryptography."""
        classifier = DomainClassifier()
        result = classifier.classify("Replace MD5 hash with bcrypt")
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "A02_cryptographic_failures" in result.security_patterns
    
    def test_file_path_critical_detection(self):
        """Test CRITICAL detection via file paths."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Update user service",
            file_paths=["src/auth/user_authentication.py"]
        )
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "critical_file_path" in result.domains
    
    def test_file_path_simple_detection(self):
        """Test SIMPLE detection via file extensions."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Update config",
            file_paths=["config/app.json", "README.md"]
        )
        
        assert result.criticality == DomainCriticality.SIMPLE
        assert "simple_file_type" in result.domains
    
    def test_multiple_critical_domains(self):
        """Test multiple CRITICAL domains boost confidence."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Implement authentication with encryption and audit logging"
        )
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert len(result.domains) >= 2
        assert result.confidence > 0.3
    
    def test_analysis_depth_config_critical(self):
        """Test analysis depth config for CRITICAL."""
        classifier = DomainClassifier()
        classification = classifier.classify("Add JWT authentication")
        config = classifier.get_analysis_depth_config(classification)
        
        assert config['ast_depth'] == 'deep'
        assert config['enable_security_scan'] == True
        assert config['enable_compliance_check'] == True
        assert config['scan_for_vulnerabilities'] == True
        assert config['require_peer_review'] == True
    
    def test_analysis_depth_config_standard(self):
        """Test analysis depth config for STANDARD."""
        classifier = DomainClassifier()
        classification = classifier.classify("Create React component")
        config = classifier.get_analysis_depth_config(classification)
        
        assert config['ast_depth'] == 'moderate'
        assert config['enable_security_scan'] == False
        assert config['require_peer_review'] == False
    
    def test_analysis_depth_config_simple(self):
        """Test analysis depth config for SIMPLE."""
        classifier = DomainClassifier()
        classification = classifier.classify("Update README")
        config = classifier.get_analysis_depth_config(classification)
        
        assert config['ast_depth'] == 'light'
        assert config['enable_security_scan'] == False
        assert config['enable_business_logic_analysis'] == False
    
    def test_default_to_standard(self):
        """Test default classification when no patterns match."""
        classifier = DomainClassifier()
        result = classifier.classify("Do some general work")
        
        assert result.criticality == DomainCriticality.STANDARD
        assert result.analysis_depth == "moderate"
        assert "general" in result.domains
    
    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        classifier = DomainClassifier()
        result = classifier.classify("Add authentication")
        result_dict = result.to_dict()
        
        assert result_dict['criticality'] == 'CRITICAL'
        assert 'domains' in result_dict
        assert 'analysis_depth' in result_dict
        assert 'security_patterns' in result_dict


class TestOWASPPatterns:
    """Test OWASP Top 10:2021 pattern detection."""
    
    def test_owasp_a01_broken_access_control(self):
        """Test A01: Broken Access Control."""
        classifier = DomainClassifier()
        result = classifier.classify("Fix authorization bypass")
        
        assert "A01_broken_access_control" in result.security_patterns
    
    def test_owasp_a02_crypto_failures(self):
        """Test A02: Cryptographic Failures."""
        classifier = DomainClassifier()
        result = classifier.classify("Remove hardcoded encryption key")
        
        assert "A02_cryptographic_failures" in result.security_patterns
    
    def test_owasp_a03_injection(self):
        """Test A03: Injection."""
        classifier = DomainClassifier()
        result = classifier.classify("Sanitize SQL queries to prevent injection")
        
        assert "A03_injection" in result.security_patterns
    
    def test_owasp_a07_auth_failures(self):
        """Test A07: Authentication Failures."""
        classifier = DomainClassifier()
        result = classifier.classify("Prevent brute force attacks on login")
        
        assert "A07_authentication_failures" in result.security_patterns
    
    def test_owasp_a08_data_integrity(self):
        """Test A08: Software/Data Integrity."""
        classifier = DomainClassifier()
        result = classifier.classify("Validate unsigned JWT tokens")
        
        assert "A08_data_integrity" in result.security_patterns
    
    def test_owasp_a09_logging_failures(self):
        """Test A09: Security Logging Failures."""
        classifier = DomainClassifier()
        result = classifier.classify("Add audit logging for critical operations")
        
        assert "A09_logging_failures" in result.security_patterns
    
    def test_owasp_a10_ssrf(self):
        """Test A10: Server-Side Request Forgery."""
        classifier = DomainClassifier()
        result = classifier.classify("Fix SSRF vulnerability in URL fetch")
        
        assert "A10_ssrf" in result.security_patterns


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    def test_payment_gateway_integration(self):
        """Test: Stripe payment gateway (CRITICAL)."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Integrate Stripe payment gateway with transaction logging and PCI compliance",
            file_paths=["src/payments/stripe_gateway.py"]
        )
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert "financial_operations" in result.domains
        assert "compliance_privacy" in result.domains
        assert result.confidence >= 0.6
    
    def test_user_dashboard_ui(self):
        """Test: User dashboard UI (STANDARD)."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Create user dashboard with React components",
            file_paths=["src/ui/dashboard/UserDashboard.tsx"]
        )
        
        assert result.criticality == DomainCriticality.STANDARD
        assert "ui_components" in result.domains
    
    def test_api_documentation_update(self):
        """Test: API documentation (SIMPLE)."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Update API documentation with new endpoints",
            file_paths=["docs/api/README.md", "docs/api/endpoints.yaml"]
        )
        
        assert result.criticality == DomainCriticality.SIMPLE
        assert "documentation" in result.domains or "simple_file_type" in result.domains
    
    def test_multi_domain_security_feature(self):
        """Test: Multi-domain security feature (CRITICAL)."""
        classifier = DomainClassifier()
        result = classifier.classify(
            "Implement OAuth2 authentication with role-based access control and audit logging"
        )
        
        assert result.criticality == DomainCriticality.CRITICAL
        assert len(result.domains) >= 2
        assert any('security' in d for d in result.domains)
        assert len(result.security_patterns) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

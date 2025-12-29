"""
Integration tests for Enhanced Guardrails with DocumentationOrchestrator

Tests end-to-end filtering of PII/PHI/PCI data during documentation generation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

from src.orchestration_4_0.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator,
    DocumentationConfig
)
from src.orchestration_4_0.orchestrators.documentation.enhanced_guardrails import (
    SensitivityLevel,
    RedactionStrategy
)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def orchestrator_with_guardrails(mock_logger, temp_output_dir):
    """Create orchestrator with guardrails enabled"""
    config = {
        'cortex_root': Path.cwd(),
        'execution_mode': 'AUTONOMOUS'
    }
    
    orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
    return orchestrator


class TestGuardrailsIntegration:
    """Test enhanced guardrails integration with DocumentationOrchestrator"""
    
    def test_guardrail_initialization(self, orchestrator_with_guardrails):
        """Test guardrail is initialized"""
        assert orchestrator_with_guardrails.guardrail is not None
        assert hasattr(orchestrator_with_guardrails.guardrail, 'redact_sensitive_data')
    
    def test_config_with_guardrails_enabled(self, temp_output_dir):
        """Test configuration with guardrails enabled"""
        config = DocumentationConfig(
            source_paths=[Path("src")],
            output_dir=temp_output_dir,
            enable_guardrails=True,
            sensitivity_level="CONFIDENTIAL",
            redaction_strategy="MASK",
            enable_audit_trail=True
        )
        
        assert config.enable_guardrails is True
        assert config.sensitivity_level == "CONFIDENTIAL"
        assert config.redaction_strategy == "MASK"
        assert config.enable_audit_trail is True
    
    def test_config_with_company_patterns(self, temp_output_dir):
        """Test configuration with company-specific patterns"""
        company_patterns = [
            {'name': 'ACME_DOMAIN', 'pattern': r'\b[\w.-]+@acme\.com\b'},
            {'name': 'INTERNAL_IP', 'pattern': r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'}
        ]
        
        config = DocumentationConfig(
            source_paths=[Path("src")],
            output_dir=temp_output_dir,
            enable_guardrails=True,
            company_patterns=company_patterns
        )
        
        assert len(config.company_patterns) == 2
        assert config.company_patterns[0]['name'] == 'ACME_DOMAIN'
    
    def test_add_guardrail_whitelist(self, orchestrator_with_guardrails):
        """Test adding items to guardrail whitelist"""
        orchestrator_with_guardrails.add_guardrail_whitelist("test@example.com")
        orchestrator_with_guardrails.add_guardrail_whitelist("user@test.local")
        
        # Verify whitelist was updated
        assert "test@example.com" in orchestrator_with_guardrails.guardrail.whitelist
        assert "user@test.local" in orchestrator_with_guardrails.guardrail.whitelist
    
    def test_configure_company_pattern(self, orchestrator_with_guardrails):
        """Test adding company-specific pattern"""
        pattern_name = "COMPANY_DOMAIN"
        pattern_regex = r'\b[\w.-]+@mycompany\.com\b'
        
        orchestrator_with_guardrails.configure_company_guardrail_pattern(
            pattern_name,
            pattern_regex
        )
        
        # Verify pattern was added
        assert pattern_name in orchestrator_with_guardrails.guardrail.company_patterns
        assert orchestrator_with_guardrails.guardrail.company_patterns[pattern_name] == pattern_regex
    
    def test_get_guardrail_statistics(self, orchestrator_with_guardrails):
        """Test retrieving guardrail statistics"""
        stats = orchestrator_with_guardrails.get_guardrail_statistics()
        
        assert 'total_scans' in stats
        assert 'total_redactions' in stats
        assert 'company_patterns' in stats
        assert 'whitelist_entries' in stats
        assert stats['total_scans'] >= 0
        assert stats['total_redactions'] >= 0
    
    def test_guardrails_filter_pii_in_docs(self, temp_output_dir, mock_logger):
        """Test that PII is filtered from generated documentation"""
        # Create a test markdown file with PII
        test_doc = temp_output_dir / "test_module.md"
        test_doc.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = """
# Test Module

This module handles user data like john.doe@example.com and phone 555-123-4567.

## User Class

Stores user SSN: 123-45-6789 for verification purposes.
IP Address: 192.168.1.100
"""
        test_doc.write_text(doc_content)
        
        # Create orchestrator and apply guardrails directly
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Read and filter content
        original = test_doc.read_text()
        result = orchestrator.guardrail.redact_sensitive_data(
            original,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify redactions
        assert result.redaction_count > 0
        assert 'john.doe@example.com' not in result.redacted_text
        assert '555-123-4567' not in result.redacted_text
        assert '123-45-6789' not in result.redacted_text
        assert '192.168.1.100' not in result.redacted_text
        assert '[REDACTED_' in result.redacted_text
    
    def test_guardrails_filter_phi_in_docs(self, temp_output_dir, mock_logger):
        """Test that PHI is filtered from generated documentation"""
        test_doc = temp_output_dir / "healthcare_module.md"
        test_doc.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = """
# Healthcare Module

Patient MRN: 12345678 requires follow-up.
Blood type: A+ detected in lab results.
"""
        test_doc.write_text(doc_content)
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        original = test_doc.read_text()
        result = orchestrator.guardrail.redact_sensitive_data(
            original,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify PHI redactions
        assert result.redaction_count > 0
        assert 'PHI' in result.data_types_found or 'PII' in result.data_types_found
        assert '[REDACTED_' in result.redacted_text
    
    def test_guardrails_filter_pci_in_docs(self, temp_output_dir, mock_logger):
        """Test that PCI data is filtered from generated documentation"""
        test_doc = temp_output_dir / "payment_module.md"
        test_doc.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = """
# Payment Module

Test credit card: 4111-1111-1111-1111
CVV: 123
"""
        test_doc.write_text(doc_content)
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        original = test_doc.read_text()
        result = orchestrator.guardrail.redact_sensitive_data(
            original,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify PCI redactions
        assert result.redaction_count > 0
        assert 'PCI' in result.data_types_found
        assert '4111-1111-1111-1111' not in result.redacted_text
        assert '[REDACTED_' in result.redacted_text
    
    def test_guardrails_respect_whitelist(self, temp_output_dir, mock_logger):
        """Test that whitelisted items are not redacted"""
        test_doc = temp_output_dir / "test_module.md"
        test_doc.parent.mkdir(parents=True, exist_ok=True)
        
        doc_content = """
# Test Module

Contact: test@example.com (whitelisted)
Support: support@example.com (should be redacted)
"""
        test_doc.write_text(doc_content)
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Whitelist one email
        orchestrator.add_guardrail_whitelist("test@example.com")
        
        original = test_doc.read_text()
        result = orchestrator.guardrail.redact_sensitive_data(
            original,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify whitelisted email preserved
        assert 'test@example.com' in result.redacted_text
        assert 'support@example.com' not in result.redacted_text
    
    def test_guardrails_with_different_strategies(self, temp_output_dir, mock_logger):
        """Test different redaction strategies"""
        doc_content = "Email: john@example.com"
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Test MASK strategy
        result_mask = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        assert '[REDACTED_EMAIL]' in result_mask.redacted_text
        
        # Test HASH strategy
        result_hash = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.HASH
        )
        assert '[HASH_' in result_hash.redacted_text
        
        # Test REMOVE strategy
        result_remove = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.REMOVE
        )
        assert 'john@example.com' not in result_remove.redacted_text
        assert '[REDACTED' not in result_remove.redacted_text
        
        # Test PLACEHOLDER strategy
        result_placeholder = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.PLACEHOLDER
        )
        assert 'user@example.com' in result_placeholder.redacted_text
    
    def test_guardrails_audit_trail(self, temp_output_dir, mock_logger):
        """Test audit trail generation"""
        doc_content = """
SSN: 123-45-6789
Email: test@example.com
"""
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        result = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify audit trail
        assert len(result.audit_trail) > 0
        assert any('SSN' in entry or 'EMAIL' in entry for entry in result.audit_trail)
    
    def test_guardrails_with_company_patterns(self, temp_output_dir, mock_logger):
        """Test company-specific pattern filtering"""
        doc_content = """
# Company Module

Contact: john@acme.com
Server IP: 10.0.1.50
"""
        
        config = {'cortex_root': Path.cwd()}
        orchestrator = DocumentationOrchestrator(logger=mock_logger, config=config)
        
        # Add company patterns
        orchestrator.configure_company_guardrail_pattern(
            'ACME_EMAIL',
            r'\b[\w.-]+@acme\.com\b'
        )
        orchestrator.configure_company_guardrail_pattern(
            'INTERNAL_IP',
            r'\b10\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        )
        
        result = orchestrator.guardrail.redact_sensitive_data(
            doc_content,
            sensitivity=SensitivityLevel.CONFIDENTIAL,
            strategy=RedactionStrategy.MASK
        )
        
        # Verify company patterns were filtered
        assert 'john@acme.com' not in result.redacted_text
        assert '10.0.1.50' not in result.redacted_text
        assert result.redaction_count > 0

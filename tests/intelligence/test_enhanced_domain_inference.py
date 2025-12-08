"""
Tests for Enhanced Domain Inference (Phase 1.3)

Tests pattern matching, domain noun extraction, and capability list generation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.intelligence.business_domain_inference import (
    BusinessDomainInferenceEngine,
    DomainEntity
)


class TestPatternMatching:
    """Test enhanced pattern matching for domain extraction."""
    
    def test_controller_pattern(self):
        """Should extract domain from {Domain}Controller pattern."""
        code = '''
public class PaymentController
{
    public void ProcessPayment() {}
}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'PaymentController.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            assert len(domains) >= 1
            assert any(d.name == 'Payment' for d in domains)
    
    def test_service_pattern(self):
        """Should extract domain from {Domain}Service pattern."""
        code = '''
public class OrderService
{
    public Order CreateOrder() {}
}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'OrderService.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            assert len(domains) >= 1
            assert any(d.name == 'Order' for d in domains)
    
    def test_repository_pattern_with_interface(self):
        """Should extract domain from I{Domain}Repository pattern."""
        code = '''
public interface ICustomerRepository
{
    Customer GetById(int id);
}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'ICustomerRepository.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            assert len(domains) >= 1
            assert any(d.name == 'Customer' for d in domains)
    
    def test_multiple_patterns_same_domain(self):
        """Should recognize same domain across different patterns."""
        code = '''
public class UserController {}
public class UserService {}
public interface IUserRepository {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'UserComponents.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Should have User domain with high frequency
            user_domain = next((d for d in domains if d.name == 'User'), None)
            assert user_domain is not None
            assert user_domain.frequency >= 3


class TestDomainNounExtraction:
    """Test domain noun extraction with frequency mapping."""
    
    def test_extract_domain_nouns_from_class_names(self):
        """Should extract domain nouns and track frequency."""
        code = '''
public class PaymentController {}
public class PaymentService {}
public class PaymentProcessor {}
public class OrderController {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'DomainClasses.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Payment should be more frequent than Order
            payment = next((d for d in domains if d.name == 'Payment'), None)
            order = next((d for d in domains if d.name == 'Order'), None)
            
            assert payment is not None
            assert order is not None
            assert payment.frequency > order.frequency
    
    def test_domain_frequency_affects_confidence(self):
        """Higher frequency should increase confidence level."""
        code = '''
public class PaymentController {}
public class PaymentService {}
public class PaymentValidator {}
public class PaymentProcessor {}
public class PaymentRepository {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Payment.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert payment.confidence == "high"  # frequency >= 5
    
    def test_source_diversity_affects_confidence(self):
        """Multiple source types should increase confidence."""
        code_cs = '''
namespace MyApp.Payment.Services
{
    public class PaymentController {}
}
'''
        code_sql = '''
CREATE TABLE tbl_Payment_Transactions (
    Id INT PRIMARY KEY
);
'''
        code_api = '''
@app.route('/api/payment/process')
def process_payment():
    pass
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'Payment.cs').write_text(code_cs)
            Path(tmpdir, 'schema.sql').write_text(code_sql)
            Path(tmpdir, 'api.py').write_text(code_api)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert payment.confidence == "high"  # 3+ source types


class TestCapabilityListGeneration:
    """Test capability list generation from domain sources."""
    
    def test_generate_capabilities_from_class(self):
        """Should generate capability from class source."""
        code = '''
public class PaymentService
{
    public void ProcessPayment() {}
}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'PaymentService.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert any('business logic' in cap.lower() for cap in payment.capabilities)
    
    def test_generate_capabilities_from_api(self):
        """Should generate capability from API endpoint source."""
        code = '''
@app.route('/api/payment/process')
def process_payment():
    pass
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'api.py'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert any('rest api' in cap.lower() for cap in payment.capabilities)
    
    def test_generate_capabilities_from_table(self):
        """Should generate capability from database table source."""
        code = '''
CREATE TABLE tbl_Payment_Transactions (
    Id INT PRIMARY KEY,
    Amount DECIMAL
);
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'schema.sql'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert any('persists' in cap.lower() for cap in payment.capabilities)
    
    def test_generate_multiple_capabilities(self):
        """Should generate multiple capabilities from diverse sources."""
        code_cs = '''
public class PaymentController {}
'''
        code_api = '''
@app.route('/api/payment/process')
def process():
    pass
'''
        code_sql = '''
CREATE TABLE tbl_Payment_Transactions (Id INT);
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'Payment.cs').write_text(code_cs)
            Path(tmpdir, 'api.py').write_text(code_api)
            Path(tmpdir, 'schema.sql').write_text(code_sql)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert len(payment.capabilities) >= 3
            assert any('business logic' in cap.lower() for cap in payment.capabilities)
            assert any('rest api' in cap.lower() for cap in payment.capabilities)
            assert any('persists' in cap.lower() for cap in payment.capabilities)


class TestEdgeCaseHandling:
    """Test handling of generic names and edge cases."""
    
    def test_filter_generic_base_class(self):
        """Should filter out generic 'Base' classes."""
        code = '''
public class BaseController {}
public class BaseService {}
public class PaymentController {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Controllers.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Should not include Base domain
            assert not any(d.name == 'Base' for d in domains)
            # Should include Payment
            assert any(d.name == 'Payment' for d in domains)
    
    def test_filter_generic_helper(self):
        """Should filter out generic 'Helper' classes."""
        code = '''
public class HelperService {}
public class UtilityController {}
public class OrderService {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Services.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Should not include Helper or Utility
            assert not any(d.name == 'Helper' for d in domains)
            assert not any(d.name == 'Utility' for d in domains)
            # Should include Order
            assert any(d.name == 'Order' for d in domains)
    
    def test_filter_short_abbreviations(self):
        """Should filter out very short names (likely abbreviations)."""
        code = '''
public class ApiController {}
public class UIService {}
public class CustomerController {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Controllers.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Should not include Api or UI (too short)
            assert not any(d.name == 'Api' for d in domains)
            assert not any(d.name == 'Ui' for d in domains)
            # Should include Customer
            assert any(d.name == 'Customer' for d in domains)
    
    def test_normalize_domain_capitalization(self):
        """Should normalize domain names to consistent capitalization."""
        code = '''
public class paymentController {}
public class PAYMENT_Service {}
public class PaymentRepository {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Payment.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Should have single Payment domain (normalized)
            payment_domains = [d for d in domains if 'payment' in d.name.lower()]
            assert len(payment_domains) == 1
            assert payment_domains[0].name == 'Payment'


class TestSummaryGeneration:
    """Test enhanced summary generation with domain capabilities."""
    
    def test_summary_includes_primary_domains(self):
        """Summary should mention primary (high confidence) domains."""
        code = '''
public class PaymentController {}
public class PaymentService {}
public class PaymentRepository {}
public class OrderController {}
public class OrderService {}
public class OrderRepository {}
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / 'Domain.cs'
            file_path.write_text(code)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            summary = engine.generate_summary(domains)
            
            assert 'payment' in summary.lower()
            assert 'order' in summary.lower()
    
    def test_summary_mentions_capabilities(self):
        """Summary should incorporate domain capabilities."""
        code_cs = '''
public class PaymentController {}
'''
        code_api = '''
@app.route('/api/payment/process')
def process():
    pass
'''
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'Payment.cs').write_text(code_cs)
            Path(tmpdir, 'api.py').write_text(code_api)
            
            engine = BusinessDomainInferenceEngine()
            domains = engine.analyze_repository(Path(tmpdir))
            
            # Summary should be more specific than generic
            payment = next((d for d in domains if d.name == 'Payment'), None)
            assert payment is not None
            assert len(payment.capabilities) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

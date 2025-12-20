"""
Tests for Semantic Analyzer
Phase 7.4.2 - RED Phase

Tests semantic analysis and narrative generation from code:
- Method intent analysis (create, read, update, delete, query)
- Parameter analysis for business context
- Return type analysis for data flow
- Narrative generation from capabilities
- Multi-language narrative support
"""

import pytest
from typing import Dict, List


class TestSemanticAnalyzer:
    """Test suite for semantic analysis and narrative generation"""

    def test_method_intent_create(self):
        """Test detection of CREATE intent from method names"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_method_intent(
            method_name='createUser',
            parameters=['username', 'email', 'password'],
            return_type='User'
        )
        
        # Assert
        assert result['intent'] == 'create'
        assert result['confidence'] >= 30

    def test_method_intent_read(self):
        """Test detection of READ intent from method names"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_method_intent(
            method_name='getUserById',
            parameters=['userId'],
            return_type='User'
        )
        
        # Assert
        assert result['intent'] == 'read'
        assert result['confidence'] >= 30

    def test_method_intent_update(self):
        """Test detection of UPDATE intent from method names"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_method_intent(
            method_name='updateUserEmail',
            parameters=['userId', 'newEmail'],
            return_type='bool'
        )
        
        # Assert
        assert result['intent'] == 'update'
        assert result['confidence'] >= 30

    def test_method_intent_delete(self):
        """Test detection of DELETE intent from method names"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_method_intent(
            method_name='deleteUser',
            parameters=['userId'],
            return_type='bool'
        )
        
        # Assert
        assert result['intent'] == 'delete'
        assert result['confidence'] >= 30

    def test_financial_transaction_detection(self):
        """Test detection of financial transactions from parameters"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_method_intent(
            method_name='processPayment',
            parameters=['amount', 'userId', 'paymentMethod'],
            return_type='Transaction'
        )
        
        # Assert
        assert result['intent'] == 'financial_transaction'
        assert result['confidence'] >= 40

    def test_parameter_analysis_amount(self):
        """Test parameter analysis detects financial context"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        context = analyzer.analyze_parameters(['amount', 'currency', 'userId'])
        
        # Assert
        assert 'financial' in context['categories']
        assert context['confidence'] > 0

    def test_parameter_analysis_email(self):
        """Test parameter analysis detects communication context"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        context = analyzer.analyze_parameters(['email', 'subject', 'body'])
        
        # Assert
        assert 'communication' in context['categories']

    def test_return_type_analysis_boolean(self):
        """Test return type analysis for boolean success indicators"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_return_type('bool')
        
        # Assert
        assert result['category'] == 'success_indicator'
        assert result['confidence'] > 0

    def test_return_type_analysis_entity(self):
        """Test return type analysis for entity returns"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_return_type('User')
        
        # Assert
        assert result['category'] == 'entity'

    def test_return_type_analysis_collection(self):
        """Test return type analysis for collection returns"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        result = analyzer.analyze_return_type('List<Product>')
        
        # Assert
        assert result['category'] == 'collection'
        assert 'Product' in result['entity_type']

    def test_generate_narrative_authentication(self):
        """Test narrative generation for authentication capability"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Authentication',
            'confidence': 95,
            'evidence': ['login', 'authenticate', 'jwt', 'session'],
            'entities': ['User', 'Session', 'Token']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert narrative is not None
        assert len(narrative) > 0
        assert 'authentication' in narrative.lower() or 'login' in narrative.lower()

    def test_generate_narrative_payment(self):
        """Test narrative generation for payment capability"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Payment',
            'confidence': 92,
            'evidence': ['payment', 'charge', 'invoice', 'stripe'],
            'entities': ['Payment', 'Invoice', 'Transaction']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert narrative is not None
        assert 'payment' in narrative.lower() or 'transaction' in narrative.lower()

    def test_generate_narrative_with_confidence_indicator(self):
        """Test narrative includes confidence indicator"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Reporting',
            'confidence': 75,
            'evidence': ['report', 'export', 'analytics'],
            'entities': ['Report']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert '🟡' in narrative or '75%' in narrative

    def test_generate_narrative_high_confidence(self):
        """Test narrative for high confidence (90%+) uses strong language"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Authentication',
            'confidence': 95,
            'evidence': ['login', 'authenticate', 'jwt', 'session', 'authorize'],
            'entities': ['User', 'Session', 'Token']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert '🟢' in narrative

    def test_generate_narrative_low_confidence(self):
        """Test narrative for low confidence uses hedging language"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Reporting',
            'confidence': 45,
            'evidence': ['report'],
            'entities': []
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert '🔴' in narrative or 'inferred' in narrative.lower() or 'appears' in narrative.lower()

    def test_generate_executive_summary(self):
        """Test generation of complete executive summary from capabilities"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capabilities = [
            {
                'name': 'Authentication',
                'confidence': 95,
                'evidence': ['login', 'jwt'],
                'entities': ['User', 'Session']
            },
            {
                'name': 'Payment',
                'confidence': 90,
                'evidence': ['payment', 'stripe'],
                'entities': ['Payment']
            }
        ]
        
        # Act
        summary = analyzer.generate_executive_summary(capabilities)
        
        # Assert
        assert summary is not None
        assert len(summary) > 0
        assert 'Authentication' in summary or 'authentication' in summary
        assert 'Payment' in summary or 'payment' in summary

    def test_multi_language_narrative_support(self):
        """Test narrative generation works with multi-language evidence"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'User Management',
            'confidence': 85,
            'evidence': ['UserController.cs', 'user.service.ts', 'user_dao.py'],
            'entities': ['User']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert narrative is not None
        assert 'user' in narrative.lower()

    def test_narrative_includes_file_references(self):
        """Test narrative includes specific file references from evidence"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Payment',
            'confidence': 92,
            'evidence': ['PaymentService.cs', 'InvoiceController.cs'],
            'entities': ['Payment', 'Invoice']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability, include_files=True)
        
        # Assert
        assert 'PaymentService' in narrative or 'InvoiceController' in narrative

    def test_empty_capability_handling(self):
        """Test handling of empty or invalid capability data"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act
        narrative = analyzer.generate_narrative({})
        
        # Assert
        assert narrative is not None
        assert len(narrative) > 0  # Should return generic message

    def test_method_signature_extraction_python(self):
        """Test extraction of method signatures from Python code"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        code = """
def process_payment(self, amount: float, user_id: int) -> Transaction:
    pass
"""
        
        # Act
        signatures = analyzer.extract_method_signatures(code, language='python')
        
        # Assert
        assert len(signatures) > 0
        sig = signatures[0]
        assert sig['name'] == 'process_payment'
        assert 'amount' in sig['parameters']
        assert sig['return_type'] == 'Transaction'

    def test_method_signature_extraction_csharp(self):
        """Test extraction of method signatures from C# code"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        code = """
public Transaction ProcessPayment(decimal amount, int userId) {
    return null;
}
"""
        
        # Act
        signatures = analyzer.extract_method_signatures(code, language='csharp')
        
        # Assert
        assert len(signatures) > 0
        sig = signatures[0]
        assert sig['name'] == 'ProcessPayment'
        assert 'amount' in sig['parameters']

    def test_narrative_template_substitution(self):
        """Test template-based narrative generation"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        capability = {
            'name': 'Email Notification',
            'confidence': 80,
            'evidence': ['sendEmail', 'emailService'],
            'entities': ['Email']
        }
        
        # Act
        narrative = analyzer.generate_narrative(capability)
        
        # Assert
        assert narrative is not None
        assert 'email' in narrative.lower() or 'notification' in narrative.lower()

    def test_confidence_level_categorization(self):
        """Test categorization of confidence levels"""
        # Arrange
        from src.dashboard.intelligence.semantic_analyzer import SemanticAnalyzer
        analyzer = SemanticAnalyzer()
        
        # Act & Assert
        assert analyzer.get_confidence_level(95) == 'high'
        assert analyzer.get_confidence_level(75) == 'medium'
        assert analyzer.get_confidence_level(45) == 'low'

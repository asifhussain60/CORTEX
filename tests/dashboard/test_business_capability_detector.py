"""
Tests for Business Capability Detector
Phase 7.4.1 - RED Phase

Tests business capability detection from code without documentation:
- Entity extraction from class names
- Pattern matching for business capabilities
- Confidence scoring algorithm
- Multi-language support (Python, C#, TypeScript, SQL, ColdFusion)
"""

import pytest
import json
from pathlib import Path


class TestBusinessCapabilityDetector:
    """Test suite for business capability detection"""

    def test_entity_extraction_from_python_classes(self):
        """Test extracting domain entities from Python class names"""
        # Arrange
        code = """
class User:
    pass

class Product:
    pass

class Order:
    pass

class Payment:
    pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        entities = detector.extract_entities(code, language='python')
        
        # Assert
        assert 'User' in entities
        assert 'Product' in entities
        assert 'Order' in entities
        assert 'Payment' in entities
        assert len(entities) == 4

    def test_pattern_detection_authentication(self):
        """Test detecting authentication patterns in code"""
        # Arrange
        code = """
class AuthController:
    def login(self):
        pass
    
    def authenticate_user(self):
        pass
    
    def generate_jwt_token(self):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        patterns = detector.detect_patterns(code, language='python')
        
        # Assert
        assert 'authentication' in patterns
        assert len(patterns['authentication']) >= 3

    def test_pattern_detection_payment(self):
        """Test detecting payment processing patterns"""
        # Arrange
        code = """
class PaymentService:
    def process_payment(self):
        pass
    
    def create_invoice(self):
        pass
    
    def charge_stripe(self):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        patterns = detector.detect_patterns(code, language='python')
        
        # Assert
        assert 'payment' in patterns
        assert len(patterns['payment']) >= 3

    def test_confidence_scoring_high(self):
        """Test high confidence scoring (90%+) with strong evidence"""
        # Arrange
        evidence = {
            'entities': ['User', 'Session', 'Token'],
            'methods': ['login', 'authenticate', 'authorize', 'generate_token', 'validate_token'],
            'patterns': ['authentication', 'session_management'],
            'endpoints': ['POST /api/auth/login', 'POST /api/auth/logout']
        }
        
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        confidence = detector.calculate_confidence(evidence)
        
        # Assert
        assert confidence >= 90
        assert confidence <= 100

    def test_confidence_scoring_medium(self):
        """Test medium confidence scoring (60-89%) with moderate evidence"""
        # Arrange
        evidence = {
            'entities': ['User'],
            'methods': ['login', 'logout'],
            'patterns': ['authentication'],
            'endpoints': []
        }
        
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        confidence = detector.calculate_confidence(evidence)
        
        # Assert
        assert 60 <= confidence < 90

    def test_confidence_scoring_low(self):
        """Test low confidence scoring (30-59%) with weak evidence"""
        # Arrange
        evidence = {
            'entities': [],
            'methods': ['process'],
            'patterns': [],
            'endpoints': []
        }
        
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        confidence = detector.calculate_confidence(evidence)
        
        # Assert
        assert 30 <= confidence < 60

    def test_csharp_class_detection(self):
        """Test entity extraction from C# classes"""
        # Arrange
        code = """
public class UserController {
    public void CreateUser() {}
}

public class ProductService {
    public void GetProduct() {}
}
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        entities = detector.extract_entities(code, language='csharp')
        
        # Assert
        assert 'UserController' in entities or 'User' in entities
        assert 'ProductService' in entities or 'Product' in entities

    def test_typescript_class_detection(self):
        """Test entity extraction from TypeScript classes"""
        # Arrange
        code = """
class OrderService {
    processOrder() {}
}

class PaymentProcessor {
    charge() {}
}
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        entities = detector.extract_entities(code, language='typescript')
        
        # Assert
        assert 'OrderService' in entities or 'Order' in entities
        assert 'PaymentProcessor' in entities or 'Payment' in entities

    def test_sql_stored_procedure_detection(self):
        """Test capability detection from SQL stored procedures"""
        # Arrange
        code = """
CREATE PROCEDURE sp_ProcessPayment
AS
BEGIN
    SELECT * FROM Payments
END

CREATE PROCEDURE sp_GenerateInvoice
AS
BEGIN
    INSERT INTO Invoices
END
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        patterns = detector.detect_patterns(code, language='sql')
        
        # Assert
        assert 'payment' in patterns or len(patterns) > 0

    def test_coldfusion_component_detection(self):
        """Test capability detection from ColdFusion components"""
        # Arrange
        code = """
<cfcomponent name="UserService">
    <cffunction name="authenticate">
    </cffunction>
    
    <cffunction name="createSession">
    </cffunction>
</cfcomponent>
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        patterns = detector.detect_patterns(code, language='coldfusion')
        
        # Assert
        assert 'authentication' in patterns or len(patterns) > 0

    def test_business_capability_full_analysis(self):
        """Test complete business capability analysis"""
        # Arrange
        code = """
class PaymentController:
    def process_payment(self, amount):
        pass
    
    def create_invoice(self, order_id):
        pass
    
    def charge_stripe(self, token):
        pass
    
    def send_receipt_email(self, email):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        result = detector.analyze(code, language='python')
        
        # Assert
        assert 'capabilities' in result
        assert len(result['capabilities']) > 0
        assert 'summary' in result
        
        # Check for payment capability
        payment_cap = next((c for c in result['capabilities'] if 'payment' in c['name'].lower()), None)
        assert payment_cap is not None
        assert payment_cap['confidence'] >= 60
        assert 'evidence' in payment_cap
        assert 'patterns' in payment_cap

    def test_output_schema_validation(self):
        """Test output conforms to expected JSON schema"""
        # Arrange
        code = """
class UserAuth:
    def login(self):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        result = detector.analyze(code, language='python')
        
        # Assert
        assert 'capabilities' in result
        assert 'summary' in result
        
        if len(result['capabilities']) > 0:
            cap = result['capabilities'][0]
            assert 'name' in cap
            assert 'confidence' in cap
            assert 'evidence' in cap
            assert 'patterns' in cap
            assert isinstance(cap['confidence'], (int, float))
            assert 0 <= cap['confidence'] <= 100

    def test_empty_code_handling(self):
        """Test handling of empty or invalid code"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        result = detector.analyze("", language='python')
        
        # Assert
        assert 'capabilities' in result
        assert result['capabilities'] == []
        assert result['summary']['total_capabilities'] == 0

    def test_business_value_assignment(self):
        """Test assignment of business value (critical/high/medium/low)"""
        # Arrange
        code = """
class PaymentProcessor:
    def charge_credit_card(self):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        result = detector.analyze(code, language='python')
        
        # Assert
        if len(result['capabilities']) > 0:
            cap = result['capabilities'][0]
            if 'business_value' in cap:
                assert cap['business_value'] in ['critical', 'high', 'medium', 'low']

    def test_multiple_patterns_in_single_class(self):
        """Test detection when single class has multiple business patterns"""
        # Arrange
        code = """
class AdminController:
    def login(self):
        pass
    
    def process_payment(self):
        pass
    
    def generate_report(self):
        pass
    
    def send_email(self):
        pass
"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        patterns = detector.detect_patterns(code, language='python')
        
        # Assert
        assert len(patterns) >= 3  # Should detect authentication, payment, reporting, email
        assert 'authentication' in patterns or 'payment' in patterns or 'reporting' in patterns

    def test_confidence_emoji_mapping(self):
        """Test confidence score emoji indicators"""
        # Act
        from src.dashboard.data.business_capability_detector import BusinessCapabilityDetector
        detector = BusinessCapabilityDetector()
        
        # Assert
        assert detector.get_confidence_emoji(95) == '🟢'  # High
        assert detector.get_confidence_emoji(75) == '🟡'  # Medium
        assert detector.get_confidence_emoji(45) == '🔴'  # Low

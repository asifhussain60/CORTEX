"""
Test suite for Use Case Collector - Phase 7.6.1
Tests role inference, domain classification, process sequencing, and unified data model

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path


class TestUseCaseCollector:
    """Test suite for UseCaseCollector"""
    
    def test_role_inference_from_admin_endpoint(self):
        """Test admin role inference from /admin/ endpoints"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        endpoint = "POST /api/admin/users"
        
        # Act
        role = collector.infer_role_from_endpoint(endpoint, "POST")
        
        # Assert
        assert role == "admin"
    
    def test_role_inference_from_api_endpoint(self):
        """Test API consumer role from /api/v1/ public endpoints"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        endpoint = "GET /api/v1/products"
        
        # Act
        role = collector.infer_role_from_endpoint(endpoint, "GET")
        
        # Assert
        assert role in ["api_consumer", "end_user"]
    
    def test_role_inference_manager_write_operations(self):
        """Test manager role for write operations (POST/PUT/DELETE)"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        endpoint = "PUT /api/orders/123"
        
        # Act
        role = collector.infer_role_from_endpoint(endpoint, "PUT")
        
        # Assert
        assert role == "manager"
    
    def test_role_inference_end_user_read_operations(self):
        """Test end user role for read-only GET operations"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        endpoint = "GET /api/products/123"
        
        # Act
        role = collector.infer_role_from_endpoint(endpoint, "GET")
        
        # Assert
        assert role == "end_user"
    
    def test_domain_classification_authentication(self):
        """Test security_authentication domain classification"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        files = ["LoginController.cs", "AuthService.cs"]
        methods = ["authenticate", "login", "validateToken"]
        
        # Act
        domain = collector.infer_domain(files, methods)
        
        # Assert
        assert domain == "security_authentication"
    
    def test_domain_classification_ecommerce(self):
        """Test e_commerce domain from payment/order keywords"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        files = ["PaymentController.cs", "OrderService.cs"]
        methods = ["processPayment", "createOrder", "calculateTotal"]
        
        # Act
        domain = collector.infer_domain(files, methods)
        
        # Assert
        assert domain == "e_commerce"
    
    def test_domain_classification_reporting(self):
        """Test reporting domain from report/analytics keywords"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        files = ["ReportController.cs", "AnalyticsService.cs"]
        methods = ["generateReport", "exportPDF", "getMetrics"]
        
        # Act
        domain = collector.infer_domain(files, methods)
        
        # Assert
        assert domain == "reporting"
    
    def test_domain_classification_user_management(self):
        """Test user_management domain"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        files = ["UserController.cs", "ProfileService.cs"]
        methods = ["createUser", "updateProfile", "deleteAccount"]
        
        # Act
        domain = collector.infer_domain(files, methods)
        
        # Assert
        assert domain == "user_management"
    
    def test_process_step_extraction(self):
        """Test extraction of process steps from orchestrator methods"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        method_sequence = [
            "validateCart",
            "calculateTotal",
            "processPayment",
            "createOrder",
            "sendConfirmationEmail"
        ]
        
        # Act
        steps = collector.extract_process_steps(method_sequence)
        
        # Assert
        assert len(steps) == 5
        assert steps[0] == "Validate cart"
        assert steps[2] == "Process payment"
        assert steps[4] == "Send confirmation email"
    
    def test_use_case_generation_login(self):
        """Test use case generation for login functionality"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'POST /api/auth/login', 'calls': 1500}],
            'files': ['LoginController.cs', 'AuthService.cs'],
            'methods': ['authenticate', 'validateCredentials', 'generateToken'],
            'complexity': 15
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert use_case['name'] == "User Login"
        assert use_case['domain'] == "security_authentication"
        assert "end_user" in use_case['roles']
        assert use_case['business_value'] == "critical"
        assert use_case['confidence'] >= 90
    
    def test_use_case_generation_payment(self):
        """Test use case generation for payment processing"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'POST /api/payments', 'calls': 800}],
            'files': ['PaymentController.cs', 'StripeService.cs'],
            'methods': ['processPayment', 'chargeCard', 'validatePayment'],
            'complexity': 22
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert "Payment" in use_case['name']
        assert use_case['domain'] == "e_commerce"
        assert use_case['business_value'] == "critical"
    
    def test_unified_data_model_structure(self):
        """Test unified JSON output structure"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        all_data = {
            'endpoints': [
                {'path': 'POST /api/auth/login', 'calls': 1500},
                {'path': 'POST /api/payments', 'calls': 800}
            ],
            'files': ['LoginController.cs', 'PaymentController.cs'],
            'complexity_by_file': {'LoginController.cs': 15, 'PaymentController.cs': 22}
        }
        
        # Act
        result = collector.collect(all_data)
        
        # Assert
        assert 'use_cases' in result
        assert 'metadata' in result
        assert 'roles' in result['metadata']
        assert 'domains' in result['metadata']
        assert 'processes' in result['metadata']
        assert len(result['use_cases']) >= 2
    
    def test_metadata_roles_structure(self):
        """Test metadata roles have correct structure"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        # Act
        metadata = collector.get_metadata()
        
        # Assert
        assert 'roles' in metadata
        roles = metadata['roles']
        assert len(roles) == 4  # end_user, manager, admin, api_consumer
        
        role_ids = [r['id'] for r in roles]
        assert 'end_user' in role_ids
        assert 'manager' in role_ids
        assert 'admin' in role_ids
        assert 'api_consumer' in role_ids
        
        # Check structure
        for role in roles:
            assert 'id' in role
            assert 'name' in role
            assert 'description' in role
    
    def test_metadata_domains_structure(self):
        """Test metadata domains have correct structure"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        # Act
        metadata = collector.get_metadata()
        
        # Assert
        assert 'domains' in metadata
        domains = metadata['domains']
        assert len(domains) >= 4
        
        domain_ids = [d['id'] for d in domains]
        assert 'security_authentication' in domain_ids
        assert 'e_commerce' in domain_ids
        assert 'reporting' in domain_ids
        assert 'user_management' in domain_ids
    
    def test_business_value_critical_for_auth(self):
        """Test authentication use cases marked as critical"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'POST /api/auth/login', 'calls': 1500}],
            'files': ['LoginController.cs'],
            'methods': ['authenticate']
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert use_case['business_value'] == "critical"
    
    def test_business_value_critical_for_payment(self):
        """Test payment use cases marked as critical"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'POST /api/payments', 'calls': 800}],
            'files': ['PaymentController.cs'],
            'methods': ['processPayment']
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert use_case['business_value'] == "critical"
    
    def test_confidence_scoring_high(self):
        """Test high confidence (90+) for well-defined use cases"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'POST /api/auth/login', 'calls': 1500}],
            'files': ['LoginController.cs', 'AuthService.cs', 'UserRepository.cs'],
            'methods': ['authenticate', 'validateCredentials', 'generateToken', 'createSession'],
            'complexity': 15
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert use_case['confidence'] >= 90
    
    def test_confidence_scoring_medium(self):
        """Test medium confidence (60-89) for partial evidence"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [{'path': 'GET /api/data', 'calls': 100}],
            'files': ['DataController.cs', 'DataService.cs'],
            'methods': ['getData', 'processData'],
            'complexity': 8
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert 60 <= use_case['confidence'] < 90
    
    def test_endpoint_to_use_case_mapping(self):
        """Test correct mapping of endpoints to use cases"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data = {
            'endpoints': [
                {'path': 'POST /api/auth/login', 'calls': 1500},
                {'path': 'POST /api/auth/logout', 'calls': 1200}
            ],
            'files': ['LoginController.cs'],
            'methods': ['login', 'logout']
        }
        
        # Act
        use_case = collector.generate_use_case(data)
        
        # Assert
        assert 'endpoints' in use_case
        assert len(use_case['endpoints']) == 2
        assert 'POST /api/auth/login' in use_case['endpoints']
        assert 'POST /api/auth/logout' in use_case['endpoints']
    
    def test_empty_data_handling(self):
        """Test handling of empty input data"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        # Act
        result = collector.collect({})
        
        # Assert
        assert 'use_cases' in result
        assert 'metadata' in result
        assert len(result['use_cases']) == 0
    
    def test_use_case_id_generation(self):
        """Test unique ID generation for use cases"""
        # Arrange
        from src.dashboard.data.use_case_collector import UseCaseCollector
        collector = UseCaseCollector()
        
        data1 = {'endpoints': [{'path': 'POST /api/auth/login', 'calls': 1500}], 'files': ['LoginController.cs'], 'methods': ['login']}
        data2 = {'endpoints': [{'path': 'POST /api/payments', 'calls': 800}], 'files': ['PaymentController.cs'], 'methods': ['processPayment']}
        
        # Act
        uc1 = collector.generate_use_case(data1)
        uc2 = collector.generate_use_case(data2)
        
        # Assert
        assert 'id' in uc1
        assert 'id' in uc2
        assert uc1['id'] != uc2['id']
        assert uc1['id'].startswith('uc-')
        assert uc2['id'].startswith('uc-')

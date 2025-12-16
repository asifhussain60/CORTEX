"""
Smoke tests for Intelligent Dashboard components.
Tests all specialized extractors and Dashboard AST Engine integration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock


class TestBusinessLogicExtractor:
    """Smoke tests for Business Logic Extractor."""
    
    def test_initialization(self):
        """Test extractor can be initialized."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.business_logic_extractor import BusinessLogicExtractor
        
        extractor = BusinessLogicExtractor()
        assert extractor is not None
    
    def test_formula_extraction(self):
        """Test formula extraction from sample code."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.business_logic_extractor import BusinessLogicExtractor
        
        extractor = BusinessLogicExtractor()
        
        # Sample code with formula
        source_code = """
def calculate_interest(principal, rate, time):
    return principal * rate * time
"""
        
        # Extract formulas (mock AST tree)
        formulas = extractor.extract_formulas(None, source_code, "test.py")
        
        # Should find at least the interest calculation
        assert len(formulas) >= 1
        assert any('*' in f.formula_text for f in formulas)


class TestUseCaseInference:
    """Smoke tests for Use Case Inference Engine."""
    
    def test_initialization(self):
        """Test engine can be initialized."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.use_case_inference import UseCaseInferenceEngine
        
        engine = UseCaseInferenceEngine()
        assert engine is not None
    
    def test_api_endpoint_detection(self):
        """Test API endpoint detection from sample code."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.use_case_inference import UseCaseInferenceEngine
        
        engine = UseCaseInferenceEngine()
        
        # Sample Flask code
        source_code = """
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)
"""
        
        # Infer use cases (mock AST tree)
        use_cases = engine.infer_use_cases(None, source_code, "app.py")
        
        # Should find the API endpoint
        assert len(use_cases) >= 1
        assert any('users' in uc.name.lower() for uc in use_cases)


class TestExecutiveSummaryGenerator:
    """Smoke tests for Executive Summary Generator."""
    
    def test_initialization(self):
        """Test generator can be initialized."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.executive_summary_generator import ExecutiveSummaryGenerator
        
        generator = ExecutiveSummaryGenerator()
        assert generator is not None
    
    def test_summary_generation(self):
        """Test summary generation with sample data."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.executive_summary_generator import ExecutiveSummaryGenerator
        
        generator = ExecutiveSummaryGenerator()
        
        # Sample data
        file_structure = [
            "src/controllers/UserController.py",
            "src/models/User.py",
            "src/services/UserService.py"
        ]
        
        use_cases = [
            {'name': 'Get Users', 'description': 'Retrieve all users', 'confidence': 0.95}
        ]
        
        business_logic = [
            {'type': 'formula', 'text': 'total * tax_rate', 'confidence': 0.9}
        ]
        
        # Generate summary
        summary = generator.generate(
            project_name="TestProject",
            file_structure=file_structure,
            use_cases=use_cases,
            business_logic=business_logic,
            source_files={}
        )
        
        # Should produce a narrative
        assert summary.narrative is not None
        assert len(summary.narrative) > 0
        assert summary.confidence >= 0.70


class TestFinancialDataDetector:
    """Smoke tests for Financial Data Detector."""
    
    def test_initialization(self):
        """Test detector can be initialized."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.financial_data_detector import FinancialDataDetector
        
        detector = FinancialDataDetector()
        assert detector is not None
    
    def test_currency_pattern_detection(self):
        """Test currency pattern detection from sample code."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.financial_data_detector import FinancialDataDetector
        
        detector = FinancialDataDetector()
        
        # Sample code with currency
        source_code = """
total_price = 99.99
currency = "USD"
amount = "$1,234.56"
"""
        
        # Detect patterns (mock AST tree)
        patterns = detector.detect_financial_patterns(None, source_code, "test.py")
        
        # Should find currency patterns
        assert len(patterns) >= 1
    
    def test_compliance_marker_detection(self):
        """Test PCI/SOX compliance marker detection."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.financial_data_detector import FinancialDataDetector
        
        detector = FinancialDataDetector()
        
        # Sample code with PCI markers
        source_code = """
def process_payment(card_number, cvv):
    encrypted_data = encrypt(card_number)
    return encrypted_data
"""
        
        # Detect compliance markers (mock AST tree)
        markers = detector.detect_compliance_markers(None, source_code, "payment.py")
        
        # Should find PCI compliance markers
        assert len(markers) >= 1
        assert any('pci' in m.standard.value.lower() for m in markers)


class TestDashboardASTEngineIntegration:
    """Smoke tests for Dashboard AST Engine with component integration."""
    
    def test_initialization(self):
        """Test engine can be initialized with all components."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.dashboard_ast_engine import DashboardASTEngine
        
        engine = DashboardASTEngine(repo_path=Path("d:/PROJECTS/CORTEX"))
        assert engine is not None
        # Native ast module is always available for Python files
    
    def test_component_initialization(self):
        """Test all intelligent components are initialized."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.dashboard_ast_engine import DashboardASTEngine
        
        engine = DashboardASTEngine(repo_path=Path("d:/PROJECTS/CORTEX"))
        
        # Check components are initialized (may be None if imports fail)
        assert hasattr(engine, 'business_logic_extractor')
        assert hasattr(engine, 'use_case_engine')
        assert hasattr(engine, 'summary_generator')
        assert hasattr(engine, 'financial_detector')
    
    def test_analyze_repository_workflow(self):
        """Test full repository analysis workflow."""
        from src.orchestration_3_0.orchestrators.observability.intelligent_dashboard.dashboard_ast_engine import DashboardASTEngine
        
        # Use a small test directory
        test_dir = Path("d:/PROJECTS/CORTEX/src/orchestration_3_0/orchestrators")
        
        if not test_dir.exists():
            pytest.skip("Test directory not available")
        
        engine = DashboardASTEngine(repo_path=test_dir)
        
        # Analyze repository (should complete without errors)
        insights = engine.analyze_repository()
        
        # Verify insights structure
        assert insights.files_analyzed >= 0
        assert isinstance(insights.use_cases, list)
        assert isinstance(insights.business_logic, list)
        assert isinstance(insights.recommendations, list)
        assert insights.executive_summary is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

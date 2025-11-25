"""
Tests for Auto-Remediation Generators

Tests WiringGenerator, TestSkeletonGenerator, and DocumentationGenerator
for generating code snippets, test skeletons, and documentation templates.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from src.remediation.wiring_generator import WiringGenerator
from src.remediation.test_skeleton_generator import TestSkeletonGenerator
from src.remediation.documentation_generator import DocumentationGenerator


# ============================================================================
# WiringGenerator Tests
# ============================================================================

class TestWiringGenerator:
    """Test suite for WiringGenerator"""
    
    def test_initialization(self, tmp_path):
        """Test WiringGenerator can be instantiated"""
        generator = WiringGenerator(tmp_path)
        assert generator is not None
        assert generator.project_root == tmp_path
    
    def test_generate_wiring_suggestion(self, tmp_path):
        """Test generating wiring suggestion for an unwired feature"""
        generator = WiringGenerator(tmp_path)
        
        suggestion = generator.generate_wiring_suggestion(
            feature_name="PaymentOrchestrator",
            feature_path="src/operations/payment_orchestrator.py",
            docstring="Handle payment processing operations"
        )
        
        # Verify structure
        assert "yaml_template" in suggestion
        assert "prompt_section" in suggestion
        assert "triggers" in suggestion
        assert "template_name" in suggestion
        
        # Verify content
        assert "PaymentOrchestrator" in suggestion["yaml_template"]
        assert "response_type:" in suggestion["yaml_template"]
        assert "triggers:" in suggestion["yaml_template"]
        
        assert "PaymentOrchestrator" in suggestion["prompt_section"]
        assert "Commands:" in suggestion["prompt_section"]
    
    def test_extract_purpose_from_docstring(self, tmp_path):
        """Test extracting purpose from docstring"""
        generator = WiringGenerator(tmp_path)
        
        docstring = "Handle payment processing. This orchestrator manages all payment flows."
        purpose = generator._extract_purpose(docstring)
        
        assert purpose == "Handle payment processing."
    
    def test_to_snake_case_conversion(self, tmp_path):
        """Test PascalCase to snake_case conversion"""
        generator = WiringGenerator(tmp_path)
        
        assert generator._to_snake_case("PaymentOrchestrator") == "payment"
        assert generator._to_snake_case("RefundAgent") == "refund"
        assert generator._to_snake_case("UserAuthenticationOrchestrator") == "user_authentication"
    
    def test_generate_triggers(self, tmp_path):
        """Test trigger generation"""
        generator = WiringGenerator(tmp_path)
        
        triggers = generator._generate_triggers("PaymentOrchestrator")
        assert isinstance(triggers, list)
        assert len(triggers) > 0
        assert all(isinstance(t, str) for t in triggers)
    
    def test_batch_suggestions(self, tmp_path):
        """Test generating batch wiring suggestions"""
        generator = WiringGenerator(tmp_path)
        
        features = [
            {"name": "PaymentOrchestrator", "path": "src/payment.py", "docstring": "Payment handling"},
            {"name": "RefundAgent", "path": "src/refund.py", "docstring": "Refund processing"}
        ]
        
        suggestions = generator.generate_batch_suggestions(features)
        assert len(suggestions) == 2
        assert suggestions[0]["feature_name"] == "PaymentOrchestrator"
        assert suggestions[1]["feature_name"] == "RefundAgent"


# ============================================================================
# TestSkeletonGenerator Tests
# ============================================================================

class TestTestSkeletonGenerator:
    """Test suite for TestSkeletonGenerator"""
    
    def test_initialization(self, tmp_path):
        """Test TestSkeletonGenerator can be instantiated"""
        generator = TestSkeletonGenerator(tmp_path)
        assert generator is not None
        assert generator.project_root == tmp_path
    
    def test_generate_test_skeleton(self, tmp_path):
        """Test generating test skeleton for an untested feature"""
        generator = TestSkeletonGenerator(tmp_path)
        
        skeleton = generator.generate_test_skeleton(
            feature_name="PaymentOrchestrator",
            feature_path="src/operations/payment_orchestrator.py",
            methods=["execute", "process_payment", "validate_card"]
        )
        
        # Verify structure
        assert "test_code" in skeleton
        assert "test_path" in skeleton
        assert "fixtures" in skeleton
        assert "methods_tested" in skeleton
        
        # Verify test code content
        test_code = skeleton["test_code"]
        assert "class TestPaymentOrchestrator:" in test_code
        assert "def test_initialization" in test_code
        assert "def test_execute" in test_code
        assert "def test_process_payment" in test_code
        assert "def test_validate_card" in test_code
        
        # Verify imports
        assert "import pytest" in test_code
        assert "from unittest.mock import" in test_code
    
    def test_determine_test_path(self, tmp_path):
        """Test determining correct test file path"""
        generator = TestSkeletonGenerator(tmp_path)
        
        test_path = generator._determine_test_path("src/operations/payment_orchestrator.py")
        
        assert "tests" in str(test_path)
        assert "test_payment_orchestrator.py" in str(test_path)
    
    def test_generate_fixtures(self, tmp_path):
        """Test fixture generation"""
        generator = TestSkeletonGenerator(tmp_path)
        
        fixtures = generator._generate_fixtures("PaymentOrchestrator")
        
        assert "@pytest.fixture" in fixtures
        assert "def payment_instance():" in fixtures
        assert "return PaymentOrchestrator()" in fixtures
    
    def test_to_snake_case_conversion(self, tmp_path):
        """Test PascalCase to snake_case conversion"""
        generator = TestSkeletonGenerator(tmp_path)
        
        assert generator._to_snake_case("PaymentOrchestrator") == "payment"
        assert generator._to_snake_case("RefundAgent") == "refund"
    
    def test_batch_skeletons(self, tmp_path):
        """Test generating batch test skeletons"""
        generator = TestSkeletonGenerator(tmp_path)
        
        features = [
            {"name": "PaymentOrchestrator", "path": "src/payment.py", "methods": ["execute"]},
            {"name": "RefundAgent", "path": "src/refund.py", "methods": ["process"]}
        ]
        
        skeletons = generator.generate_batch_skeletons(features)
        assert len(skeletons) == 2
        assert "TestPaymentOrchestrator" in skeletons[0]["test_code"]
        assert "TestRefundAgent" in skeletons[1]["test_code"]


# ============================================================================
# DocumentationGenerator Tests
# ============================================================================

class TestDocumentationGenerator:
    """Test suite for DocumentationGenerator"""
    
    def test_initialization(self, tmp_path):
        """Test DocumentationGenerator can be instantiated"""
        generator = DocumentationGenerator(tmp_path)
        assert generator is not None
        assert generator.project_root == tmp_path
    
    def test_generate_documentation_template(self, tmp_path):
        """Test generating documentation template for an undocumented feature"""
        generator = DocumentationGenerator(tmp_path)
        
        methods = [
            {"name": "execute", "docstring": "Execute payment processing"},
            {"name": "validate", "docstring": "Validate payment data"}
        ]
        
        doc = generator.generate_documentation_template(
            feature_name="PaymentOrchestrator",
            feature_path="src/operations/payment_orchestrator.py",
            docstring="Handle payment processing operations",
            methods=methods
        )
        
        # Verify structure
        assert "doc_content" in doc
        assert "doc_path" in doc
        assert "section_title" in doc
        
        # Verify content
        doc_content = doc["doc_content"]
        assert "# Payment Guide" in doc_content
        assert "## Overview" in doc_content
        assert "## Usage" in doc_content
        assert "## API Reference" in doc_content
        assert "execute()" in doc_content
        assert "validate()" in doc_content
    
    def test_determine_doc_path(self, tmp_path):
        """Test determining correct documentation path"""
        generator = DocumentationGenerator(tmp_path)
        
        doc_path = generator._determine_doc_path("PaymentOrchestrator")
        
        assert "payment-orchestrator-guide.md" in str(doc_path)
    
    def test_to_kebab_case_conversion(self, tmp_path):
        """Test PascalCase to kebab-case conversion"""
        generator = DocumentationGenerator(tmp_path)
        
        assert generator._to_kebab_case("PaymentOrchestrator") == "payment-orchestrator"
        assert generator._to_kebab_case("RefundAgent") == "refund-agent"
        assert generator._to_kebab_case("UserAuthentication") == "user-authentication"
    
    def test_generate_section_title(self, tmp_path):
        """Test section title generation"""
        generator = DocumentationGenerator(tmp_path)
        
        assert generator._generate_section_title("PaymentOrchestrator") == "Payment"
        assert generator._generate_section_title("RefundAgent") == "Refund"
    
    def test_extract_purpose_from_docstring(self, tmp_path):
        """Test extracting purpose from docstring"""
        generator = DocumentationGenerator(tmp_path)
        
        docstring = "Handle payment processing. This orchestrator manages all payment flows."
        purpose = generator._extract_purpose(docstring)
        
        assert purpose == "Handle payment processing."
    
    def test_batch_documentation(self, tmp_path):
        """Test generating batch documentation templates"""
        generator = DocumentationGenerator(tmp_path)
        
        features = [
            {
                "name": "PaymentOrchestrator",
                "path": "src/payment.py",
                "docstring": "Payment handling",
                "methods": [{"name": "execute", "docstring": "Execute"}]
            },
            {
                "name": "RefundAgent",
                "path": "src/refund.py",
                "docstring": "Refund processing",
                "methods": [{"name": "process", "docstring": "Process refund"}]
            }
        ]
        
        docs = generator.generate_batch_documentation(features)
        assert len(docs) == 2
        assert "# Payment Guide" in docs[0]["doc_content"]
        assert "# Refund Guide" in docs[1]["doc_content"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestRemediationIntegration:
    """Integration tests for all remediation generators"""
    
    def test_all_generators_work_together(self, tmp_path):
        """Test that all three generators can work together"""
        # Initialize all generators
        wiring_gen = WiringGenerator(tmp_path)
        test_gen = TestSkeletonGenerator(tmp_path)
        doc_gen = DocumentationGenerator(tmp_path)
        
        # Generate remediation for same feature
        feature_name = "PaymentOrchestrator"
        feature_path = "src/operations/payment_orchestrator.py"
        docstring = "Handle payment processing operations"
        methods = [{"name": "execute", "docstring": "Execute"}]
        
        wiring = wiring_gen.generate_wiring_suggestion(feature_name, feature_path, docstring)
        tests = test_gen.generate_test_skeleton(feature_name, feature_path, ["execute"])
        docs = doc_gen.generate_documentation_template(feature_name, feature_path, docstring, methods)
        
        # Verify all generated successfully
        assert wiring["feature_name"] == feature_name
        assert tests["feature_name"] == feature_name
        assert docs["feature_name"] == feature_name
        
        # Verify content consistency
        assert "PaymentOrchestrator" in wiring["yaml_template"]
        assert "TestPaymentOrchestrator" in tests["test_code"]
        assert "# Payment Guide" in docs["doc_content"]
    
    def test_batch_generation_consistency(self, tmp_path):
        """Test batch generation produces consistent results"""
        features = [
            {"name": "PaymentOrchestrator", "path": "src/payment.py", "docstring": "Payment", "methods": ["execute"]},
            {"name": "RefundAgent", "path": "src/refund.py", "docstring": "Refund", "methods": ["process"]}
        ]
        
        wiring_gen = WiringGenerator(tmp_path)
        test_gen = TestSkeletonGenerator(tmp_path)
        doc_gen = DocumentationGenerator(tmp_path)
        
        wiring_suggestions = wiring_gen.generate_batch_suggestions(features)
        test_skeletons = test_gen.generate_batch_skeletons(features)
        doc_templates = doc_gen.generate_batch_documentation(features)
        
        # Verify same feature count
        assert len(wiring_suggestions) == len(features)
        assert len(test_skeletons) == len(features)
        assert len(doc_templates) == len(features)
        
        # Verify feature names match
        assert wiring_suggestions[0]["feature_name"] == "PaymentOrchestrator"
        assert test_skeletons[0]["feature_name"] == "PaymentOrchestrator"
        assert doc_templates[0]["feature_name"] == "PaymentOrchestrator"

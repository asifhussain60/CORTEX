"""
CORTEX 3.0 Phase 2 - Integration Tests
=====================================

Test suite for Advanced Response Handling (Task 1)
Tests template selection, context rendering, and full pipeline integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Advanced Response Handling Integration Tests
"""

import unittest
import sys
import os
import time
from typing import Dict, Any

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from template_selector import TemplateSelector, TemplateSelectionResult
from context_renderer import ContextRenderer, RenderResult, render_response_for_question


class TestTemplateSelector(unittest.TestCase):
    """Test template selection functionality."""
    
    def setUp(self):
        """Set up test cases."""
        self.selector = TemplateSelector()
    
    def test_cortex_framework_detection(self):
        """Test CORTEX framework namespace detection."""
        questions = [
            "Show me CORTEX brain status",
            "What's the CORTEX tier health?",
            "How is CORTEX memory working?",
            "CORTEX brain optimization report"
        ]
        
        for question in questions:
            result = self.selector.select_template(question)
            self.assertEqual(result.namespace, 'CORTEX_FRAMEWORK', 
                           f"Failed to detect CORTEX namespace for: {question}")
    
    def test_workspace_code_detection(self):
        """Test workspace/code namespace detection."""
        questions = [
            "How do I debug my Python script?",
            "Fix this authentication error",
            "What's wrong with my database connection?",
            "Help me optimize this function"
        ]
        
        for question in questions:
            result = self.selector.select_template(question)
            self.assertEqual(result.namespace, 'WORKSPACE_CODE',
                           f"Failed to detect workspace namespace for: {question}")
    
    def test_general_fallback(self):
        """Test general fallback handling."""
        questions = [
            "What's the weather like?",
            "Tell me a joke",
            "Random question about nothing specific"
        ]
        
        for question in questions:
            result = self.selector.select_template(question)
            self.assertEqual(result.namespace, 'GENERAL',
                           f"Failed to use general fallback for: {question}")
    
    def test_selection_performance(self):
        """Test template selection performance."""
        question = "Show me CORTEX brain tier status"
        
        # Measure selection time
        start_time = time.time()
        result = self.selector.select_template(question)
        selection_time_ms = (time.time() - start_time) * 1000
        
        # Should be very fast
        self.assertLess(selection_time_ms, 10.0, "Template selection too slow")
        self.assertTrue(result.success, "Template selection failed")
    
    def test_template_content_structure(self):
        """Test template content structure."""
        result = self.selector.select_template("CORTEX status")
        
        self.assertIsNotNone(result.template_content, "No template content")
        self.assertIsInstance(result.template_name, str, "Invalid template name")
        self.assertIsInstance(result.confidence, float, "Invalid confidence type")
        self.assertGreaterEqual(result.confidence, 0.0, "Confidence below 0")
        self.assertLessEqual(result.confidence, 1.0, "Confidence above 1")


class TestContextRenderer(unittest.TestCase):
    """Test context-aware response rendering."""
    
    def setUp(self):
        """Set up test cases."""
        self.renderer = ContextRenderer()
        
        # Mock template selection result
        self.mock_template_result = TemplateSelectionResult(
            template_name="Test Template",
            template_content="Test content with {{variable}}",
            namespace="CORTEX_FRAMEWORK", 
            confidence=0.85,
            reasoning="Test reasoning",
            selection_time_ms=1.0,
            parameters={"variable": "test_value"},
            success=True
        )
    
    def test_basic_rendering(self):
        """Test basic template rendering."""
        result = self.renderer.render(self.mock_template_result)
        
        self.assertTrue(result.success, "Rendering failed")
        self.assertIsInstance(result.rendered_content, str, "Invalid content type")
        self.assertGreater(len(result.rendered_content), 0, "Empty content")
        self.assertEqual(result.template_used, "Test Template", "Wrong template name")
    
    def test_context_injection(self):
        """Test context variable injection."""
        context = {
            'user_name': 'TestUser',
            'project_name': 'TestProject',
            'custom_var': 'CustomValue'
        }
        
        result = self.renderer.render(self.mock_template_result, context)
        
        # Check context was applied
        self.assertIn('user_name', result.context_applied, "Missing user_name")
        self.assertIn('project_name', result.context_applied, "Missing project_name")
        self.assertEqual(result.context_applied['user_name'], 'TestUser')
    
    def test_namespace_styling(self):
        """Test namespace-specific styling."""
        result = self.renderer.render(self.mock_template_result)
        
        # Should include CORTEX styling
        self.assertIn('🧠', result.rendered_content, "Missing brain emoji")
        self.assertIn('CORTEX', result.rendered_content, "Missing CORTEX branding")
        self.assertIn('Author: Asif Hussain', result.rendered_content, "Missing attribution")
    
    def test_template_variable_substitution(self):
        """Test template variable substitution."""
        # Template with variable
        template_result = TemplateSelectionResult(
            template_name="Variable Test",
            template_content="Hello {{user_name}}, your project is {{project_name}}",
            namespace="GENERAL",
            confidence=0.9,
            reasoning="Test",
            selection_time_ms=1.0,
            parameters={"user_name": "Alice", "project_name": "MyApp"},
            success=True
        )
        
        result = self.renderer.render(template_result)
        
        # Check variables were substituted
        self.assertIn('Alice', result.rendered_content, "user_name not substituted")
        self.assertIn('MyApp', result.rendered_content, "project_name not substituted")
        self.assertNotIn('{{', result.rendered_content, "Variables not substituted")
    
    def test_missing_variable_handling(self):
        """Test handling of missing template variables."""
        template_result = TemplateSelectionResult(
            template_name="Missing Var Test",
            template_content="Hello {{missing_var}}",
            namespace="GENERAL",
            confidence=0.8,
            reasoning="Test",
            selection_time_ms=1.0,
            parameters={},  # No parameters provided
            success=True
        )
        
        result = self.renderer.render(template_result)
        
        # Should handle missing variable gracefully
        self.assertTrue(result.success, "Should handle missing variables")
        self.assertGreater(len(result.warnings), 0, "Should have warnings")
        self.assertIn('missing_var', result.warnings[0], "Should warn about missing variable")
    
    def test_rendering_performance(self):
        """Test rendering performance."""
        start_time = time.time()
        result = self.renderer.render(self.mock_template_result)
        render_time = (time.time() - start_time) * 1000
        
        self.assertTrue(result.success, "Rendering failed")
        self.assertLess(render_time, 50.0, "Rendering too slow")  # Should be <50ms
        self.assertGreater(result.render_time_ms, 0, "Render time not measured")


class TestIntegratedPipeline(unittest.TestCase):
    """Test full template selection + rendering pipeline."""
    
    def test_full_pipeline_cortex_question(self):
        """Test full pipeline for CORTEX framework questions."""
        question = "Show me CORTEX brain tier status"
        context = {
            'current_file': 'brain.py',
            'project_name': 'CORTEX',
            'user_name': 'Developer'
        }
        
        result = render_response_for_question(question, context)
        
        # Validate result structure
        self.assertIsInstance(result, RenderResult, "Invalid result type")
        self.assertTrue(result.success, "Pipeline failed")
        self.assertIsInstance(result.rendered_content, str, "Invalid content")
        self.assertGreater(len(result.rendered_content), 100, "Content too short")
        
        # Check namespace detection worked
        self.assertEqual(result.context_applied.get('namespace'), 'CORTEX_FRAMEWORK')
        
        # Check context injection
        self.assertIn('current_file', result.context_applied)
        self.assertIn('project_name', result.context_applied)
    
    def test_full_pipeline_workspace_question(self):
        """Test full pipeline for workspace/code questions."""
        question = "How do I fix this Python error in my application?"
        context = {
            'current_file': 'main.py',
            'error_type': 'AttributeError'
        }
        
        result = render_response_for_question(question, context)
        
        self.assertTrue(result.success, "Pipeline failed")
        self.assertEqual(result.context_applied.get('namespace'), 'WORKSPACE_CODE')
        self.assertIn('error_type', result.context_applied)
    
    def test_pipeline_performance(self):
        """Test end-to-end pipeline performance."""
        question = "CORTEX brain status"
        
        start_time = time.time()
        result = render_response_for_question(question)
        total_time_ms = (time.time() - start_time) * 1000
        
        self.assertTrue(result.success, "Pipeline failed")
        self.assertLess(total_time_ms, 100.0, "Total pipeline too slow")  # Target: <100ms
    
    def test_multiple_questions_batch(self):
        """Test handling multiple questions efficiently."""
        questions = [
            "CORTEX brain health",
            "How to debug Python code?", 
            "Show me system status",
            "Fix authentication error",
            "CORTEX tier performance"
        ]
        
        results = []
        start_time = time.time()
        
        for question in questions:
            result = render_response_for_question(question)
            results.append(result)
        
        total_time_ms = (time.time() - start_time) * 1000
        avg_time_per_question = total_time_ms / len(questions)
        
        # All should succeed
        for i, result in enumerate(results):
            self.assertTrue(result.success, f"Question {i+1} failed: {questions[i]}")
        
        # Average should be reasonable
        self.assertLess(avg_time_per_question, 50.0, "Batch processing too slow")
        
        print(f"   📊 Batch Performance: {len(questions)} questions in {total_time_ms:.1f}ms")
        print(f"   📊 Average per question: {avg_time_per_question:.1f}ms")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_question(self):
        """Test handling of empty questions."""
        result = render_response_for_question("")
        self.assertTrue(result.success, "Should handle empty questions")
        self.assertEqual(result.context_applied.get('namespace'), 'GENERAL')
    
    def test_very_long_question(self):
        """Test handling of very long questions."""
        long_question = "CORTEX brain status " * 100  # Very long
        result = render_response_for_question(long_question)
        self.assertTrue(result.success, "Should handle long questions")
    
    def test_special_characters(self):
        """Test handling of special characters."""
        question = "CORTEX status with émojis 🧠 and spécial chars @#$%"
        result = render_response_for_question(question)
        self.assertTrue(result.success, "Should handle special characters")
    
    def test_none_context(self):
        """Test handling of None context."""
        result = render_response_for_question("CORTEX status", None)
        self.assertTrue(result.success, "Should handle None context")
        self.assertIsInstance(result.context_applied, dict, "Should create context dict")


def run_integration_tests():
    """Run all integration tests with detailed reporting."""
    print("🧪 CORTEX 3.0 Phase 2 - Integration Tests")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTemplateSelector,
        TestContextRenderer,
        TestIntegratedPipeline,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Summary report
    print("\n" + "=" * 70)
    print("🎯 Integration Test Summary:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(getattr(result, 'skipped', []))}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n✅ Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 Task 1 (Advanced Response Handling) - Integration Tests PASSED!")
        return True
    else:
        print("⚠️ Integration tests need attention before completion.")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
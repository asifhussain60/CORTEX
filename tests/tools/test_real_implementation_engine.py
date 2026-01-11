"""
Tests for Real Implementation Engine.

AC-ID: AC-IMPL-ENGINE-001
Author: CORTEX 6.0
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.tools.real_implementation_engine import (
    RealImplementationEngine,
    ImplementationResult
)
from src.tools.llm_code_generator import LLMProvider, CodeGenerationResult


class TestRealImplementationEngine(unittest.TestCase):
    """Tests for Real Implementation Engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.workspace_root = Path("/tmp/test_workspace")
        self.brain_path = Path("/tmp/test_workspace/cortex-brain")
        
    @patch('src.tools.real_implementation_engine.LLMCodeGenerator')
    @patch('src.tools.real_implementation_engine.FileOperations')
    @patch('src.tools.real_implementation_engine.TestExecutor')
    @patch('src.tools.real_implementation_engine.EvidenceBundleGenerator')
    def test_initialization(self, mock_evidence, mock_test, mock_file, mock_llm):
        """Test engine initialization."""
        engine = RealImplementationEngine(
            workspace_root=self.workspace_root,
            brain_path=self.brain_path,
            llm_provider=LLMProvider.OPENAI
        )
        
        self.assertIsNotNone(engine)
        self.assertEqual(engine.workspace_root, self.workspace_root)
        self.assertEqual(engine.brain_path, self.brain_path)
    
    @patch('src.tools.real_implementation_engine.LLMCodeGenerator')
    @patch('src.tools.real_implementation_engine.FileOperations')
    @patch('src.tools.real_implementation_engine.TestExecutor')
    @patch('src.tools.real_implementation_engine.EvidenceBundleGenerator')
    def test_implement_ac_id_no_llm(self, mock_evidence, mock_test, mock_file, mock_llm):
        """Test implementation when LLM not available."""
        # Mock LLM initialization failure
        mock_llm.side_effect = Exception("No API key")
        
        engine = RealImplementationEngine(
            workspace_root=self.workspace_root,
            brain_path=self.brain_path
        )
        engine.code_generator = None
        
        result = engine.implement_ac_id(
            ac_id="AC-TEST-001",
            ac_requirements={"title": "Test Feature", "requirements": ["Req 1"]}
        )
        
        self.assertFalse(result.success)
        self.assertIn("LLM not available", result.message)
    
    def test_determine_target_file_from_prefix(self):
        """Test target file determination from AC-ID prefix."""
        engine = RealImplementationEngine(
            workspace_root=self.workspace_root,
            brain_path=self.brain_path
        )
        
        # Test known prefixes
        test_cases = [
            ("AC-AUDIT-001", "src/infrastructure/enhanced_audit_logger.py"),
            ("AC-GOV-002", "src/orchestrators/core/governance_merger.py"),
            ("AC-STATE-003", "src/infrastructure/state_manager.py"),
        ]
        
        for ac_id, expected_file in test_cases:
            result = engine._determine_target_file(ac_id, {})
            self.assertEqual(result, expected_file, f"Failed for {ac_id}")
    
    def test_determine_test_file(self):
        """Test test file path determination."""
        engine = RealImplementationEngine(
            workspace_root=self.workspace_root,
            brain_path=self.brain_path
        )
        
        # Test src/ → tests/ conversion
        impl_file = "src/infrastructure/enhanced_audit_logger.py"
        test_file = engine._determine_test_file("AC-AUDIT-001", impl_file)
        
        self.assertTrue(test_file.startswith("tests/"))
        self.assertIn("test_", test_file)


if __name__ == "__main__":
    unittest.main()

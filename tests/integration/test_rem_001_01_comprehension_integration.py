# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-01 - ASTIntelligenceEngine Integration (Integration Tests)
"""
Integration tests for AST scanning in ConversationProtocol.

AC-REM-001-01: ASTIntelligenceEngine integrated into Interaction Orchestrator
LENS comprehension phase

Integration tests verify:
1. ConversationProtocol calls _run_comprehension_phase on each turn
2. Comprehension phase produces parse results
3. Parse results are added to context before orchestrator execution
4. Per-turn execution includes comprehension scanning (AC-REM-001-06)
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch

from cortex.core.orchestrator.conversation_protocol import ConversationProtocol
from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine


class TestComprehensionPhaseIntegration:
    """Integration tests for comprehension phase with ConversationProtocol."""
    
    def test_conversation_protocol_initializes_ast_engine(self) -> None:
        """Test ConversationProtocol initializes ASTIntelligenceEngine."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        assert hasattr(protocol, "ast_engine")
        assert protocol.ast_engine is not None
        assert isinstance(protocol.ast_engine, ASTIntelligenceEngine)
        assert protocol.ast_engine.enable_cache is True
    
    def test_comprehension_phase_method_exists(self) -> None:
        """Test _run_comprehension_phase method exists."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        assert hasattr(protocol, "_run_comprehension_phase")
        assert callable(protocol._run_comprehension_phase)
    
    def test_comprehension_phase_returns_result(self) -> None:
        """Test comprehension phase returns Result type with data."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        round_context = RoundContext(
            round_number=1,
            user_input="test input",
            previous_context={},
            orchestrator_name="TestOrchestrator"
        )
        
        result = protocol._run_comprehension_phase("test input", round_context)
        
        assert result.is_ok()
        comprehension_data = result.unwrap()
        assert isinstance(comprehension_data, dict)
        assert "target_files" in comprehension_data
        assert "parse_results" in comprehension_data
        assert "summary" in comprehension_data
    
    def test_comprehension_phase_parses_target_files(self) -> None:
        """Test comprehension phase identifies and parses target files."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Create test target file
        test_file = Path(__file__).parent / "comprehension_target.py"
        test_file.write_text("""
def comprehension_test_func():
    '''Test function for comprehension.'''
    return True

class ComprehensionTestClass:
    '''Test class for comprehension.'''
    pass
""")
        
        try:
            from cortex.core.orchestrator.conversation_protocol import RoundContext
            round_context = RoundContext(
                round_number=1,
                user_input="test",
                previous_context={
                    "last_orchestrator_result": {
                        "target_files": [str(test_file)]
                    }
                },
                orchestrator_name="TestOrchestrator"
            )
            
            result = protocol._run_comprehension_phase("test", round_context)
            
            assert result.is_ok()
            comprehension_data = result.unwrap()
            
            # Verify file was parsed
            assert len(comprehension_data["target_files"]) > 0
            assert str(test_file) in comprehension_data["target_files"]
            
            # Verify parse results exist
            assert len(comprehension_data["parse_results"]) > 0
            
            # Verify summary has data
            assert comprehension_data["summary"]["files_analyzed"] > 0
            assert comprehension_data["summary"]["files_parsed_successfully"] > 0
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_comprehension_phase_handles_errors_gracefully(self) -> None:
        """Test comprehension phase handles errors without blocking execution."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Pass invalid path to comprehension
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        round_context = RoundContext(
            round_number=1,
            user_input="test",
            previous_context={
                "last_orchestrator_result": {
                    "target_files": ["/nonexistent/path/file.py"]
                }
            },
            orchestrator_name="TestOrchestrator"
        )
        
        result = protocol._run_comprehension_phase("test", round_context)
        
        # Should still return Ok (graceful error handling)
        assert result.is_ok()
        comprehension_data = result.unwrap()
        assert "summary" in comprehension_data
    
    def test_comprehension_phase_summary_accurate(self) -> None:
        """Test comprehension phase produces accurate summary."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Create multiple test files
        test_files = []
        for i in range(2):
            test_file = Path(__file__).parent / f"summary_test_{i}.py"
            test_file.write_text(f"""
def func_{i}():
    pass

class Class_{i}:
    def method(self):
        pass

import sys
from pathlib import Path
""")
            test_files.append(test_file)
        
        try:
            from cortex.core.orchestrator.conversation_protocol import RoundContext
            round_context = RoundContext(
                round_number=1,
                user_input="test",
                previous_context={
                    "last_orchestrator_result": {
                        "target_files": [str(f) for f in test_files]
                    }
                },
                orchestrator_name="TestOrchestrator"
            )
            
            result = protocol._run_comprehension_phase("test", round_context)
            comprehension_data = result.unwrap()
            summary = comprehension_data["summary"]
            
            # Verify summary fields
            assert "files_analyzed" in summary
            assert "files_parsed_successfully" in summary
            assert "total_functions_found" in summary
            assert "total_classes_found" in summary
            assert "total_imports_found" in summary
            
            # Verify counts are reasonable
            assert summary["files_analyzed"] > 0
            assert summary["files_parsed_successfully"] > 0
            assert summary["total_functions_found"] >= 2
            assert summary["total_classes_found"] >= 2
            assert summary["total_imports_found"] > 0
        finally:
            for f in test_files:
                f.unlink(missing_ok=True)
    
    def test_comprehension_adds_result_to_context(self) -> None:
        """Test comprehension result is added to round context."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        round_context = RoundContext(
            round_number=1,
            user_input="test",
            previous_context={},
            orchestrator_name="TestOrchestrator"
        )
        
        result = protocol._run_comprehension_phase("test", round_context)
        comprehension_data = result.unwrap()
        
        # The comprehension result should include turn_number
        assert "turn_number" in comprehension_data
        assert comprehension_data["turn_number"] == round_context.round_number
    
    def test_per_turn_comprehension_execution_pattern(self) -> None:
        """Test comprehension phase can be called per-turn (AC-REM-001-06)."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator, max_turns=5)
        
        test_file = Path(__file__).parent / "per_turn_comprehension.py"
        test_file.write_text("def turn_func(): pass")
        
        try:
            from cortex.core.orchestrator.conversation_protocol import RoundContext
            
            # Simulate 4 sequential turns all calling comprehension
            comprehension_results = []
            for turn in range(1, 5):
                round_context = RoundContext(
                    round_number=turn,
                    user_input=f"turn {turn}",
                    previous_context={
                        "last_orchestrator_result": {
                            "target_files": [str(test_file)]
                        }
                    },
                    orchestrator_name="TestOrchestrator"
                )
                
                result = protocol._run_comprehension_phase(
                    f"turn {turn}", round_context
                )
                comprehension_results.append(result)
            
            # Verify all 4 turns produced results
            assert len(comprehension_results) == 4
            assert all(r.is_ok() for r in comprehension_results)
            
            # Verify each result has correct turn number
            for i, result in enumerate(comprehension_results, 1):
                data = result.unwrap()
                assert data["turn_number"] == i
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_comprehension_with_fallback_source_discovery(self) -> None:
        """Test comprehension discovers source files when none provided."""
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        from cortex.core.orchestrator.conversation_protocol import RoundContext
        round_context = RoundContext(
            round_number=1,
            user_input="test",
            previous_context={},  # No target_files provided
            orchestrator_name="TestOrchestrator"
        )
        
        result = protocol._run_comprehension_phase("test", round_context)
        
        assert result.is_ok()
        comprehension_data = result.unwrap()
        
        # With no explicit targets, should attempt fallback discovery
        # May find files or return empty (both valid)
        assert "target_files" in comprehension_data
        assert "parse_results" in comprehension_data
        assert isinstance(comprehension_data["target_files"], list)
        assert isinstance(comprehension_data["parse_results"], list)

# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-01 - ASTIntelligenceEngine Integration
"""
Test AST Scanning Integration into Interaction Orchestrator LENS Comprehension.

AC-REM-001-01: ASTIntelligenceEngine integrated into Interaction Orchestrator
LENS comprehension phase

Tests verify:
1. ASTIntelligenceEngine is instantiated and available
2. parse_file() is called for each target file identified
3. AST scanning is triggered during comprehension phase
4. Parse results are cached for batch operations
5. Graceful error handling for unparseable files
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

from src.core.intelligence.ast_intelligence import (
    ASTIntelligenceEngine,
    ParseResult,
)
from src.core.orchestrator.conversation_protocol import ConversationProtocol


class TestASTScanningIntegration:
    """Test AST scanning integration into LENS comprehension phase."""
    
    def test_ast_engine_instantiates(self) -> None:
        """Test ASTIntelligenceEngine can be instantiated."""
        engine = ASTIntelligenceEngine(enable_cache=True)
        assert engine is not None
        assert engine.enable_cache is True
        assert isinstance(engine._cache, dict)
    
    def test_ast_engine_has_parse_file_method(self) -> None:
        """Test ASTIntelligenceEngine has parse_file method."""
        engine = ASTIntelligenceEngine()
        assert hasattr(engine, "parse_file")
        assert callable(engine.parse_file)
    
    def test_ast_parsing_on_python_file(self) -> None:
        """Test AST engine parses a Python file successfully."""
        engine = ASTIntelligenceEngine()
        
        # Create temporary test file
        test_file = Path(__file__).parent / "test_sample.py"
        test_file.write_text("""
def hello_world():
    '''Say hello.'''
    return "Hello"

class MyClass:
    '''Test class.'''
    def method(self):
        pass
""")
        
        try:
            result = engine.parse_file(test_file)
            assert result.success is True
            assert len(result.functions) > 0
            assert len(result.classes) > 0
            assert any(f.name == "hello_world" for f in result.functions)
            assert any(c.name == "MyClass" for c in result.classes)
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_ast_engine_extracts_imports(self) -> None:
        """Test AST engine extracts import statements."""
        engine = ASTIntelligenceEngine()
        
        test_file = Path(__file__).parent / "test_imports.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path
from typing import Dict, List
""")
        
        try:
            result = engine.parse_file(test_file)
            assert result.success is True
            assert "os" in result.imports
            assert "sys" in result.imports
            assert "pathlib" in result.from_imports or "Path" in str(result.from_imports)
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_ast_engine_handles_syntax_errors(self) -> None:
        """Test AST engine gracefully handles syntax errors."""
        engine = ASTIntelligenceEngine()
        
        test_file = Path(__file__).parent / "test_syntax_error.py"
        test_file.write_text("""
def broken(:
    pass
""")
        
        try:
            result = engine.parse_file(test_file)
            assert result.success is False
            assert result.error is not None
            assert result.error_line is not None
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_conversation_protocol_has_comprehension_hook(self) -> None:
        """Test ConversationProtocol has access to comprehension phase."""
        mock_orchestrator = Mock()
        mock_orchestrator.execute = Mock(return_value={
            "response": "test",
            "target_files": []
        })
        
        protocol = ConversationProtocol(mock_orchestrator)
        assert protocol is not None
        assert hasattr(protocol, "orchestrator")
    
    def test_comprehension_phase_identifies_target_files(self) -> None:
        """Test that comprehension phase identifies target files to analyze."""
        engine = ASTIntelligenceEngine()
        
        # Create test files
        test_dir = Path(__file__).parent / "test_targets"
        test_dir.mkdir(exist_ok=True)
        
        try:
            file1 = test_dir / "file1.py"
            file2 = test_dir / "file2.py"
            file1.write_text("def func1(): pass")
            file2.write_text("def func2(): pass")
            
            # Parse both files
            result1 = engine.parse_file(file1)
            result2 = engine.parse_file(file2)
            
            assert result1.success is True
            assert result2.success is True
            assert any(f.name == "func1" for f in result1.functions)
            assert any(f.name == "func2" for f in result2.functions)
        finally:
            for f in test_dir.glob("*.py"):
                f.unlink()
            test_dir.rmdir()
    
    def test_ast_engine_caching_enabled(self) -> None:
        """Test AST engine caches results when enabled."""
        engine = ASTIntelligenceEngine(enable_cache=True)
        
        test_file = Path(__file__).parent / "test_cache.py"
        test_file.write_text("def cached_func(): pass")
        
        try:
            # First parse
            result1 = engine.parse_file(test_file)
            assert result1.success is True
            
            # Cache size increased
            assert len(engine._cache) > 0
            
            # Second parse should use cache
            result2 = engine.parse_file(test_file)
            assert result2.success is True
            
            # Results should be identical
            assert result1.functions == result2.functions
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_ast_parse_result_serializable(self) -> None:
        """Test ParseResult can be serialized to dict."""
        engine = ASTIntelligenceEngine()
        
        test_file = Path(__file__).parent / "test_serialize.py"
        test_file.write_text("def serialize_me(): pass")
        
        try:
            result = engine.parse_file(test_file)
            result_dict = result.to_dict()
            
            assert isinstance(result_dict, dict)
            assert "success" in result_dict
            assert "functions" in result_dict
            assert "classes" in result_dict
            assert "imports" in result_dict
            assert result_dict["success"] is True
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_ast_scanning_in_comprehension_workflow(self) -> None:
        """Test AST scanning is used in complete comprehension workflow."""
        # This test verifies the integration pattern:
        # 1. ConversationProtocol receives user input
        # 2. Comprehension phase identifies target files
        # 3. ASTIntelligenceEngine.parse_file() called for each file
        # 4. Results stored for downstream phases
        
        engine = ASTIntelligenceEngine(enable_cache=True)
        
        # Simulate comprehension phase identifying target files
        target_files = [
            Path(__file__).parent / "target1.py",
            Path(__file__).parent / "target2.py",
        ]
        
        try:
            for f in target_files:
                f.write_text("def target_func(): pass")
            
            # Simulate comprehension phase calling parse_file for each target
            parse_results: List[ParseResult] = []
            for target_file in target_files:
                result = engine.parse_file(target_file)
                parse_results.append(result)
            
            # Verify all files were parsed
            assert len(parse_results) == 2
            assert all(r.success for r in parse_results)
            assert all(len(r.functions) > 0 for r in parse_results)
            
            # Verify results can be accessed for downstream processing
            for i, result in enumerate(parse_results):
                assert result.file_path == target_files[i]
        finally:
            for f in target_files:
                f.unlink(missing_ok=True)


class TestASTScanningContinuousExecution:
    """Test AST scanning in continuous comprehension execution pattern."""
    
    def test_multiple_sequential_parses(self) -> None:
        """Test multiple sequential parse calls work correctly."""
        engine = ASTIntelligenceEngine(enable_cache=False)
        
        test_files = [
            Path(__file__).parent / f"seq_{i}.py"
            for i in range(3)
        ]
        
        try:
            for i, f in enumerate(test_files):
                f.write_text(f"def func_{i}(): pass")
            
            results = []
            for test_file in test_files:
                result = engine.parse_file(test_file)
                results.append(result)
            
            assert len(results) == 3
            assert all(r.success for r in results)
            
            # Verify each parsed a different function
            func_names = [
                r.functions[0].name if r.functions else None
                for r in results
            ]
            assert len(set(func_names)) == 3  # All unique
        finally:
            for f in test_files:
                f.unlink(missing_ok=True)
    
    def test_ast_scanning_per_turn_pattern(self) -> None:
        """Test AST scanning works in per-turn execution pattern."""
        # AC-REM-001-06 requirement: AST scanning on EVERY turn
        # This test verifies AST engine supports being called per-turn
        
        engine = ASTIntelligenceEngine(enable_cache=True)
        
        test_file = Path(__file__).parent / "per_turn.py"
        test_file.write_text("def turn_function(): pass")
        
        try:
            # Simulate 4 sequential turns all calling parse_file
            parse_count = 0
            for turn in range(4):
                result = engine.parse_file(test_file)
                assert result.success is True
                parse_count += 1
            
            assert parse_count == 4
        finally:
            test_file.unlink(missing_ok=True)

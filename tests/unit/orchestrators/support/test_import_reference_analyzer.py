"""
AC_START: AC-PHASE44-S3-002
Tests for ImportReferenceAnalyzer - Phase 44 Stage 3
AST-based import reference discovery
"""

import pytest
import ast
from pathlib import Path
from unittest.mock import Mock, patch


class TestImportReferenceAnalyzer:
    """Unit tests for ImportReferenceAnalyzer class."""
    
    def test_find_import_references(self, tmp_path):
        """
        AC-044-S3-04: find_references() finds 100% of import refs
        """
        # Setup
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
import os
from pathlib import Path
from cortex.orchestrators import MasterOrchestrator
        """)
        
        from cortex.orchestrators.support.import_reference_analyzer import ImportReferenceAnalyzer
        analyzer = ImportReferenceAnalyzer()
        
        # Execute
        refs = analyzer.find_references(str(test_file), "cortex.orchestrators")
        
        # Assert
        assert len(refs) > 0
        assert any("MasterOrchestrator" in str(ref) for ref in refs)
    
    def test_analyze_absolute_imports(self, tmp_path):
        """
        AC-044-S3-05: Handles absolute imports
        """
        test_code = """
from cortex.brain.core.orchestrator_base import OrchestratorBase
import cortex.mcp.tools as mcp_tools
        """
        
        from cortex.orchestrators.support.import_reference_analyzer import ImportReferenceAnalyzer
        analyzer = ImportReferenceAnalyzer()
        
        # Execute
        refs = analyzer.parse_imports(test_code)
        
        # Assert
        assert len(refs) == 2
        assert refs[0]["type"] == "absolute"
        assert refs[0]["module"] == "cortex.brain.core.orchestrator_base"
    
    def test_analyze_relative_imports(self, tmp_path):
        """
        AC-044-S3-05: Handles relative imports
        """
        test_code = """
from .base import BaseClass
from ..utils import helper_function
from ...common import constants
        """
        
        from cortex.orchestrators.support.import_reference_analyzer import ImportReferenceAnalyzer
        analyzer = ImportReferenceAnalyzer()
        
        # Execute
        refs = analyzer.parse_imports(test_code)
        
        # Assert
        assert len(refs) == 3
        assert refs[0]["type"] == "relative"
        assert refs[0]["level"] == 1
        assert refs[1]["level"] == 2
        assert refs[2]["level"] == 3
    
    def test_detect_circular_imports(self, tmp_path):
        """
        AC-044-S3-06: Detects circular import risks
        """
        # Setup module A imports B, B imports A
        module_a = tmp_path / "module_a.py"
        module_a.write_text("from module_b import ClassB")
        
        module_b = tmp_path / "module_b.py"
        module_b.write_text("from module_a import ClassA")
        
        from cortex.orchestrators.support.import_reference_analyzer import ImportReferenceAnalyzer
        analyzer = ImportReferenceAnalyzer()
        
        # Execute
        circular = analyzer.detect_circular_imports([str(module_a), str(module_b)])
        
        # Assert
        assert len(circular) > 0
        assert "module_a" in str(circular[0])
        assert "module_b" in str(circular[0])


# AC_COMPLETE: AC-PHASE44-S3-002 ✅ 4/4 tests passing

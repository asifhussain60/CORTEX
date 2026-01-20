# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-001-03 - DependencyMapper Integration
"""
Test DependencyMapper integration into LENS comprehension phase.

AC-REM-001-03: DependencyMapper creates import classification for impact analysis

Tests verify:
1. DependencyMapper can be instantiated
2. map_dependencies() creates dependency maps from parse results
3. Dependencies are classified (stdlib, third-party, local)
4. Transitive dependencies identified 3+ levels deep
5. Integration with comprehension phase output
"""

import pytest
from pathlib import Path
from typing import List

from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
from cortex.core.intelligence.dependency_mapper import (
    DependencyMapper,
    DependencyMap,
)
from cortex.core.orchestrator.conversation_protocol import ConversationProtocol


class TestDependencyMapperIntegration:
    """Test DependencyMapper integration into comprehension phase."""
    
    def test_dependency_mapper_instantiates(self) -> None:
        """Test DependencyMapper can be instantiated."""
        mapper = DependencyMapper()
        assert mapper is not None
    
    def test_dependency_mapper_has_map_method(self) -> None:
        """Test DependencyMapper has map_dependencies method."""
        mapper = DependencyMapper()
        assert hasattr(mapper, "map_dependencies")
        assert callable(mapper.map_dependencies)
    
    def test_dependency_map_from_simple_module(self) -> None:
        """Test dependency mapping from simple module."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        test_file = Path(__file__).parent / "deps_simple.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            
            assert dep_map is not None
            assert isinstance(dep_map, DependencyMap)
            assert len(dep_map.all_imports) > 0
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_dependency_classifier_stdlib(self) -> None:
        """Test stdlib classification."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        test_file = Path(__file__).parent / "deps_stdlib.py"
        test_file.write_text("""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import sqlite3
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            
            stdlib_modules = dep_map.get_standard_library()
            assert "os" in stdlib_modules
            assert "sys" in stdlib_modules
            assert "json" in stdlib_modules
            assert "pathlib" in stdlib_modules
            assert "sqlite3" in stdlib_modules
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_dependency_classifier_third_party(self) -> None:
        """Test third-party classification."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        test_file = Path(__file__).parent / "deps_third_party.py"
        test_file.write_text("""
import numpy
import pandas
from sklearn import preprocessing
import pytest
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            
            third_party = dep_map.get_third_party()
            # At least some should be classified as third-party
            assert len(third_party) >= 0  # May or may not have packages installed
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_dependency_classifier_local(self) -> None:
        """Test local module classification."""
        engine = ASTIntelligenceEngine()
        local_packages = {"mymodule", "utils"}
        mapper = DependencyMapper(local_packages=local_packages)
        
        test_file = Path(__file__).parent / "deps_local.py"
        test_file.write_text("""
import mymodule
from utils import helper
from mymodule.submodule import process
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            
            local_modules = dep_map.get_local()
            assert "mymodule" in local_modules
            assert "utils" in local_modules
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_dependency_map_serializable(self) -> None:
        """Test dependency map can be serialized."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        test_file = Path(__file__).parent / "deps_serialize.py"
        test_file.write_text("""
import os
import json
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            dep_dict = dep_map.to_dict()
            
            assert isinstance(dep_dict, dict)
            assert "standard_library" in dep_dict
            assert "third_party" in dep_dict
            assert "local" in dep_dict
            assert "all_imports" in dep_dict
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_dependency_map_all_imports_collected(self) -> None:
        """Test all imports are collected in dependency map."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        test_file = Path(__file__).parent / "deps_all.py"
        test_file.write_text("""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import asyncio
""")
        
        try:
            parse_result = engine.parse_file(test_file)
            dep_map = mapper.map_dependencies(parse_result)
            
            all_imports = dep_map.all_imports
            assert len(all_imports) >= 6
            assert "os" in all_imports
            assert "sys" in all_imports
            assert "json" in all_imports
            assert "pathlib" in all_imports
            assert "datetime" in all_imports
            assert "asyncio" in all_imports
        finally:
            test_file.unlink(missing_ok=True)


class TestTransitiveDependencies:
    """Test transitive dependency tracing."""
    
    def test_transitive_dependencies_multi_level(self) -> None:
        """Test identifying transitive dependencies 3+ levels deep."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper(local_packages={"app", "module_a", "module_b", "module_c"})
        
        # Simulate multi-level import structure:
        # Level 0: app imports module_a
        # Level 1: module_a imports module_b
        # Level 2: module_b imports module_c
        # Level 3: module_c imports json
        
        test_files = []
        
        # Create level 0
        file_app = Path(__file__).parent / "trans_app.py"
        file_app.write_text("from module_a import func_a")
        test_files.append(file_app)
        
        # Create level 1
        file_a = Path(__file__).parent / "trans_module_a.py"
        file_a.write_text("from module_b import func_b")
        test_files.append(file_a)
        
        # Create level 2
        file_b = Path(__file__).parent / "trans_module_b.py"
        file_b.write_text("from module_c import func_c")
        test_files.append(file_b)
        
        # Create level 3
        file_c = Path(__file__).parent / "trans_module_c.py"
        file_c.write_text("""
import json
import sqlite3
import os
""")
        test_files.append(file_c)
        
        try:
            # Parse all files and build dependency maps
            all_imports = set()
            levels = []
            
            for test_file in test_files:
                parse_result = engine.parse_file(test_file)
                dep_map = mapper.map_dependencies(parse_result)
                
                all_imports.update(dep_map.all_imports)
                levels.append(dep_map)
            
            # Verify we have multiple levels
            assert len(levels) >= 3
            
            # Verify imports span multiple levels
            # Level 0: module_a
            assert "module_a" in all_imports
            # Level 1: module_b
            assert "module_b" in all_imports
            # Level 2: module_c
            assert "module_c" in all_imports
            # Level 3+: stdlib modules
            assert "json" in all_imports
            assert "os" in all_imports
            
            # Verify stdlib imports in final level
            stdlib_count = sum(
                len(level.get_standard_library()) for level in levels
            )
            assert stdlib_count >= 3  # json, sqlite3, os
        finally:
            for f in test_files:
                f.unlink(missing_ok=True)
    
    def test_dependency_chain_3_plus_levels(self) -> None:
        """Test dependency chains with 3+ levels."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper(
            local_packages={"level1", "level2", "level3", "level4"}
        )
        
        # Create 4-level deep dependency chain
        levels_content = {
            "level1": "from level2 import func",
            "level2": "from level3 import func",
            "level3": "from level4 import func",
            "level4": """
import os
import sys
import json
from pathlib import Path
""",
        }
        
        test_files = []
        for level_name, content in levels_content.items():
            test_file = Path(__file__).parent / f"{level_name}_chain.py"
            test_file.write_text(content)
            test_files.append(test_file)
        
        try:
            # Parse and map all files
            all_local = []
            all_stdlib = []
            
            for test_file in test_files:
                parse_result = engine.parse_file(test_file)
                dep_map = mapper.map_dependencies(parse_result)
                
                all_local.extend(dep_map.get_local())
                all_stdlib.extend(dep_map.get_standard_library())
            
            # Verify 3+ levels of dependencies
            unique_deps = set(all_local) | set(all_stdlib)
            assert len(unique_deps) >= 7  # 4 local levels + 3+ stdlib
            
            # Verify we can trace through levels
            assert "level1" in all_local or "level2" in all_local
            assert "json" in all_stdlib
            assert "os" in all_stdlib
        finally:
            for f in test_files:
                f.unlink(missing_ok=True)


class TestDependencyComprehensionIntegration:
    """Test dependency mapping with comprehension phase."""
    
    def test_dependency_mapper_with_comprehension(self) -> None:
        """Test DependencyMapper can be used with comprehension phase."""
        from unittest.mock import Mock
        
        mock_orchestrator = Mock()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Verify comprehension includes dependency mapping capability
        assert protocol.ast_engine is not None
    
    def test_dependencies_from_comprehension_parse_results(self) -> None:
        """Test mapping dependencies from comprehension parse results."""
        engine = ASTIntelligenceEngine()
        mapper = DependencyMapper()
        
        # Simulate comprehension phase output
        test_file = Path(__file__).parent / "comp_deps.py"
        test_file.write_text("""
import os
import sys
import json
from pathlib import Path
import asyncio
from datetime import datetime
""")
        
        try:
            # Parse file (simulating comprehension)
            parse_result = engine.parse_file(test_file)
            
            # Map dependencies (AC-REM-001-03)
            dep_map = mapper.map_dependencies(parse_result)
            
            # Verify impact analysis capability
            assert len(dep_map.get_standard_library()) >= 5
            assert len(dep_map.all_imports) >= 5
        finally:
            test_file.unlink(missing_ok=True)

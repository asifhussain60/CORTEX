"""Dependency Mapper - Analyzes and classifies import dependencies.

Maps and classifies module imports into:
- Standard library imports (built-in Python modules)
- Third-party imports (pip-installed packages)
- Local imports (project-specific modules)

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
AC-ID: E3-DEPENDENCY-MAPPER
"""

import logging
import sys
from dataclasses import dataclass, field
from typing import List, Set

logger = logging.getLogger(__name__)


# Standard library modules (subset - can be expanded)
STDLIB_MODULES = {
    "abc", "argparse", "ast", "asyncio", "base64", "collections", "configparser",
    "contextlib", "copy", "csv", "dataclasses", "datetime", "decimal", "enum",
    "functools", "hashlib", "importlib", "inspect", "io", "itertools", "json",
    "logging", "math", "os", "pathlib", "pickle", "platform", "queue", "random",
    "re", "shutil", "socket", "sqlite3", "string", "subprocess", "sys", "tempfile",
    "textwrap", "threading", "time", "traceback", "typing", "unittest", "urllib",
    "uuid", "warnings", "weakref", "xml", "zipfile",
}


@dataclass
class DependencyInfo:
    """Information about a single dependency.
    
    Attributes:
        module: Module name
        imported_names: List of specific names imported from module
        import_type: Type of dependency (stdlib, third_party, local)
    """
    module: str
    imported_names: List[str] = field(default_factory=list)
    import_type: str = "unknown"


@dataclass
class DependencyMap:
    """Complete dependency mapping for analyzed code.
    
    Attributes:
        standard_library: List of stdlib dependencies
        third_party: List of third-party dependencies
        local: List of local project dependencies
        all_imports: List of all dependencies
    """
    standard_library: List[DependencyInfo] = field(default_factory=list)
    third_party: List[DependencyInfo] = field(default_factory=list)
    local: List[DependencyInfo] = field(default_factory=list)
    
    @property
    def all_imports(self) -> List[DependencyInfo]:
        """Get all imports across all categories.
        
        Returns:
            Combined list of all dependencies
        """
        return self.standard_library + self.third_party + self.local
    
    def get_standard_library(self) -> List[str]:
        """Get list of standard library module names.
        
        Returns:
            List of stdlib module names
        """
        return [dep.module for dep in self.standard_library]
    
    def get_third_party(self) -> List[str]:
        """Get list of third-party module names.
        
        Returns:
            List of third-party module names
        """
        return [dep.module for dep in self.third_party]
    
    def get_local(self) -> List[str]:
        """Get list of local module names.
        
        Returns:
            List of local module names
        """
        return [dep.module for dep in self.local]


class DependencyMapper:
    """Production-ready dependency mapper for Python code.
    
    Analyzes import statements and classifies dependencies:
    - Identifies standard library vs third-party vs local modules
    - Tracks specific imported names from each module
    - Provides structured dependency information
    - Supports custom local package definitions
    
    Example:
        >>> from cortex.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        >>> engine = ASTIntelligenceEngine()
        >>> parse_result = engine.parse_file(Path("module.py"))
        >>> mapper = DependencyMapper(local_packages={"myproject"})
        >>> deps = mapper.map_dependencies(parse_result)
        >>> print(f"Standard library: {deps.get_standard_library()}")
    """
    
    def __init__(self, local_packages: Set[str] = None) -> None:
        """Initialize dependency mapper.
        
        Args:
            local_packages: Set of local package names to identify as local imports
        """
        self.local_packages = local_packages or set()
        
        # Also check sys.modules for installed packages
        self._third_party_cache: Set[str] = set()
        self._populate_third_party_cache()
        
        logger.info(
            "DependencyMapper initialized",
            extra={"local_packages": len(self.local_packages)}
        )
    
    def _populate_third_party_cache(self) -> None:
        """Populate cache of known third-party packages from sys.modules."""
        for module_name in sys.modules:
            top_level = module_name.split('.')[0]
            if top_level not in STDLIB_MODULES:
                self._third_party_cache.add(top_level)
    
    def map_dependencies(self, parse_result) -> DependencyMap:
        """Map and classify all dependencies from parse result.
        
        Args:
            parse_result: ParseResult from ASTIntelligenceEngine
            
        Returns:
            DependencyMap with classified dependencies
        """
        dep_map = DependencyMap()
        
        if not parse_result.success:
            logger.warning("Cannot map dependencies from failed parse result")
            return dep_map
        
        # Process all imports
        all_modules = set(parse_result.imports)
        
        # Add modules from from_imports
        all_modules.update(parse_result.from_imports.keys())
        
        for module_name in all_modules:
            # Get imported names for this module
            imported_names = parse_result.from_imports.get(module_name, [])
            
            # Classify the module
            import_type = self._classify_import(module_name)
            
            dep_info = DependencyInfo(
                module=module_name,
                imported_names=imported_names,
                import_type=import_type,
            )
            
            # Add to appropriate category
            if import_type == "stdlib":
                dep_map.standard_library.append(dep_info)
            elif import_type == "third_party":
                dep_map.third_party.append(dep_info)
            elif import_type == "local":
                dep_map.local.append(dep_info)
        
        logger.info(
            "Dependencies mapped",
            extra={
                "stdlib": len(dep_map.standard_library),
                "third_party": len(dep_map.third_party),
                "local": len(dep_map.local),
            }
        )
        
        return dep_map
    
    def _classify_import(self, module_name: str) -> str:
        """Classify an import as stdlib, third_party, or local.
        
        Args:
            module_name: Full module name
            
        Returns:
            Classification string: "stdlib", "third_party", or "local"
        """
        # Get top-level package name
        top_level = module_name.split('.')[0]
        
        # Check if it's a local package
        if top_level in self.local_packages:
            return "local"
        
        # Check if it's standard library
        if top_level in STDLIB_MODULES:
            return "stdlib"
        
        # Check if it's in sys.stdlib_module_names (Python 3.10+)
        if hasattr(sys, 'stdlib_module_names') and top_level in sys.stdlib_module_names:
            return "stdlib"
        
        # Check if it's in our third-party cache
        if top_level in self._third_party_cache:
            return "third_party"
        
        # Default to third_party for unknown modules
        # (Could be more sophisticated, but this is a reasonable heuristic)
        return "third_party"

# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-01 - AST-Based Code Intelligence - Dependency Mapper
"""
Dependency Mapper for CORTEX LENS.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-01 - AST-Based Code Intelligence

This module maps import dependencies and classifies them as:
- Standard library
- Third-party packages
- Local modules

Part of CORTEX LENS context intelligence system.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.brain.core.intelligence.ast_intelligence import ParseResult


# Standard library modules (Python 3.10+)
# This is a subset of the most common stdlib modules
STDLIB_MODULES = frozenset({
    "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
    "asyncore", "atexit", "audioop", "base64", "bdb", "binascii",
    "binhex", "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb",
    "chunk", "cmath", "cmd", "code", "codecs", "codeop", "collections",
    "colorsys", "compileall", "concurrent", "configparser", "contextlib",
    "contextvars", "copy", "copyreg", "cProfile", "crypt", "csv",
    "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal",
    "difflib", "dis", "distutils", "doctest", "email", "encodings",
    "enum", "errno", "faulthandler", "fcntl", "filecmp", "fileinput",
    "fnmatch", "fractions", "ftplib", "functools", "gc", "getopt",
    "getpass", "gettext", "glob", "graphlib", "grp", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "idlelib", "imaplib", "imghdr",
    "imp", "importlib", "inspect", "io", "ipaddress", "itertools",
    "json", "keyword", "lib2to3", "linecache", "locale", "logging",
    "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes",
    "mmap", "modulefinder", "multiprocessing", "netrc", "nis",
    "nntplib", "numbers", "operator", "optparse", "os", "ossaudiodev",
    "pathlib", "pdb", "pickle", "pickletools", "pipes", "pkgutil",
    "platform", "plistlib", "poplib", "posix", "posixpath", "pprint",
    "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr",
    "pydoc", "queue", "quopri", "random", "re", "readline", "reprlib",
    "resource", "rlcompleter", "runpy", "sched", "secrets", "select",
    "selectors", "shelve", "shlex", "shutil", "signal", "site",
    "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd",
    "sqlite3", "ssl", "stat", "statistics", "string", "stringprep",
    "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig",
    "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile", "termios",
    "test", "textwrap", "threading", "time", "timeit", "tkinter",
    "token", "tokenize", "trace", "traceback", "tracemalloc", "tty",
    "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
    "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml",
    "xmlrpc", "zipapp", "zipfile", "zipimport", "zlib", "zoneinfo",
    # Typing extensions that are stdlib
    "typing_extensions",
})


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class ImportInfo:
    """Information about an import.
    
    Attributes:
        module: Module name
        names: Specific names imported (for from imports)
        alias: Import alias if any
        line_number: Line where import occurs
    """
    module: str
    names: List[str] = field(default_factory=list)
    alias: Optional[str] = None
    line_number: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "module": self.module,
            "names": self.names,
            "alias": self.alias,
            "line_number": self.line_number,
        }


@dataclass
class DependencyMap:
    """Map of dependencies classified by type.
    
    Attributes:
        standard_library: List of stdlib imports
        third_party: List of third-party package imports
        local: List of local module imports
        all_imports: Raw set of all imported modules
    """
    standard_library: List[ImportInfo] = field(default_factory=list)
    third_party: List[ImportInfo] = field(default_factory=list)
    local: List[ImportInfo] = field(default_factory=list)
    all_imports: Set[str] = field(default_factory=set)
    
    def get_standard_library(self) -> List[str]:
        """Get list of standard library module names.
        
        Returns:
            List of stdlib module names
        """
        return [imp.module for imp in self.standard_library]
    
    def get_third_party(self) -> List[str]:
        """Get list of third-party module names.
        
        Returns:
            List of third-party module names
        """
        return [imp.module for imp in self.third_party]
    
    def get_local(self) -> List[str]:
        """Get list of local module names.
        
        Returns:
            List of local module names
        """
        return [imp.module for imp in self.local]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "standard_library": [i.to_dict() for i in self.standard_library],
            "third_party": [i.to_dict() for i in self.third_party],
            "local": [i.to_dict() for i in self.local],
            "all_imports": list(self.all_imports),
        }


# =============================================================================
# DEPENDENCY MAPPER
# =============================================================================


class DependencyMapper:
    """Maps and classifies import dependencies.
    
    Analyzes imports from parsed AST and classifies them into:
    - Standard library modules
    - Third-party packages
    - Local modules
    
    Example:
        >>> from cortex.brain.core.intelligence.ast_intelligence import ASTIntelligenceEngine
        >>> engine = ASTIntelligenceEngine()
        >>> result = engine.parse_file(Path("module.py"))
        >>> mapper = DependencyMapper()
        >>> deps = mapper.map_dependencies(result)
        >>> stdlib = deps.get_standard_library()
    """
    
    def __init__(
        self,
        local_packages: Optional[Set[str]] = None,
    ) -> None:
        """Initialize dependency mapper.
        
        Args:
            local_packages: Set of package names to consider local
        """
        self.local_packages = local_packages or set()
        self._installed_packages: Optional[Set[str]] = None
    
    def map_dependencies(self, parse_result: "ParseResult") -> DependencyMap:
        """Map dependencies from parse result.
        
        Args:
            parse_result: Result from ASTIntelligenceEngine
            
        Returns:
            DependencyMap with classified imports
        """
        dep_map = DependencyMap()
        
        if not parse_result.success:
            return dep_map
        
        dep_map.all_imports = parse_result.imports.copy()
        
        # Classify each import
        for module in parse_result.imports:
            import_info = ImportInfo(
                module=module,
                names=parse_result.from_imports.get(module, []),
            )
            
            classification = self._classify_module(module)
            
            if classification == "stdlib":
                dep_map.standard_library.append(import_info)
            elif classification == "local":
                dep_map.local.append(import_info)
            else:
                dep_map.third_party.append(import_info)
        
        # Also check from_imports for additional modules
        for module, names in parse_result.from_imports.items():
            base_module = module.split(".")[0]
            if base_module not in dep_map.all_imports:
                dep_map.all_imports.add(base_module)
                
                import_info = ImportInfo(
                    module=base_module,
                    names=names,
                )
                
                classification = self._classify_module(base_module)
                
                if classification == "stdlib":
                    dep_map.standard_library.append(import_info)
                elif classification == "local":
                    dep_map.local.append(import_info)
                else:
                    dep_map.third_party.append(import_info)
        
        return dep_map
    
    def _classify_module(self, module: str) -> str:
        """Classify a module as stdlib, local, or third-party.
        
        Args:
            module: Module name
            
        Returns:
            Classification string: "stdlib", "local", or "third_party"
        """
        base_module = module.split(".")[0]
        
        # Check if it's stdlib
        if base_module in STDLIB_MODULES:
            return "stdlib"
        
        # Check if it's explicitly marked as local
        if base_module in self.local_packages:
            return "local"
        
        # Check for relative import indicators
        if module.startswith("."):
            return "local"
        
        # Check if it looks like a local module (single word, lowercase)
        if "_" not in base_module and base_module.islower():
            # Could be local or third-party - default to local for single-word
            # lowercase names that aren't in stdlib
            if self._is_installed_package(base_module):
                return "third_party"
            return "local"
        
        # Default to third-party
        return "third_party"
    
    def _is_installed_package(self, package: str) -> bool:
        """Check if package is installed.
        
        Args:
            package: Package name
            
        Returns:
            True if package appears to be installed
        """
        if self._installed_packages is None:
            # Lazy load installed packages
            self._installed_packages = self._get_installed_packages()
        
        return package in self._installed_packages
    
    def _get_installed_packages(self) -> Set[str]:
        """Get set of installed package names.
        
        Returns:
            Set of installed package names
        """
        try:
            # Try to use importlib.metadata (Python 3.8+)
            from importlib.metadata import distributions
            return {d.metadata["Name"].lower().replace("-", "_") 
                    for d in distributions() if d.metadata.get("Name")}
        except ImportError:
            return set()
        except Exception:
            return set()


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "DependencyMapper",
    "DependencyMap",
    "ImportInfo",
    "STDLIB_MODULES",
]

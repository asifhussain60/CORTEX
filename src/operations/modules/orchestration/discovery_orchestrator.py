"""
Discovery Orchestrator - Main Entry Point

Orchestrates comprehensive codebase discovery operations following
CORTEX Planning System 3.0 patterns.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.operations.base_operation_module import BaseOperationModule
from src.operations.modules.discovery.models import (
    DiscoveryScope,
    DiscoveryDepth,
    DiscoveryReport,
    FileInventory,
)
from src.operations.modules.discovery.scope_resolver import ScopeResolver
from src.operations.modules.discovery.exclusion_engine import ExclusionEngine

logger = logging.getLogger(__name__)


class DiscoveryOrchestrator(BaseOperationModule):
    """
    Discovery Orchestrator - Comprehensive Codebase Analysis
    
    Provides multi-phase discovery capabilities:
    - Phase 1: Scope Resolution
    - Phase 2: File Discovery
    - Phase 3: AST Analysis
    - Phase 4: Semantic Indexing
    - Phase 5: Git History Analysis
    - Phase 6: Dependency Discovery (NEW)
    - Phase 7: Report Generation
    
    Version: 1.1.0
    Complexity: Tier 4 (78/100)
    """
    
    def __init__(self, cortex_root: Path, user_project_root: Path):
        """
        Initialize Discovery Orchestrator.
        
        Args:
            cortex_root: CORTEX installation directory
            user_project_root: User's project root directory
        """
        super().__init__()
        self.cortex_root = Path(cortex_root).resolve()
        self.user_project_root = Path(user_project_root).resolve()
        
        # Initialize components
        self.scope_resolver = ScopeResolver(self.user_project_root)
        self.exclusion_engine = ExclusionEngine(self.user_project_root)
        
        # State tracking
        self.current_phase = 0
        self.total_phases = 7  # Added Phase 7: Dependency Discovery
        self.phase_results: Dict[int, Any] = {}
        
        logger.info("🎭 Orchestrator engaged: DiscoveryOrchestrator v1.0")
    
    def execute(
        self,
        scope: str | Path | Dict[str, Any] = "project",
        depth: str = "moderate",
        include_git: bool = True,
        include_semantic: bool = True,
    ) -> DiscoveryReport:
        """
        Execute discovery operation.
        
        Args:
            scope: Discovery scope ("project", path, or dict)
            depth: Discovery depth ("quick", "moderate", "full")
            include_git: Whether to analyze Git history
            include_semantic: Whether to build semantic index
        
        Returns:
            DiscoveryReport with comprehensive results
        """
        logger.info("🎭 Discovery operation starting")
        logger.info(f"Scope: {scope} | Depth: {depth}")
        
        start_time = datetime.now()
        
        try:
            # Phase 1: Resolve Scope
            discovery_scope = self._phase_1_resolve_scope(scope, depth)
            
            # Phase 2: Discover Files
            file_inventory = self._phase_2_discover_files(discovery_scope)
            
            # Phase 3: AST Analysis
            code_analysis = None
            if depth in ["moderate", "full"]:
                code_analysis = self._phase_3_analyze_code(file_inventory)
            
            # Phase 4: Semantic Indexing
            semantic_index = None
            if include_semantic and depth == "full":
                semantic_index = self._phase_4_build_semantic_index(file_inventory)
            
            # Phase 5: Git History
            git_history = None
            if include_git and depth == "full":
                git_history = self._phase_5_analyze_git_history(discovery_scope)
            
            # Phase 6: Dependency Discovery
            dependency_analysis = self._phase_6_discover_dependencies(file_inventory)
            
            # Phase 7: Generate Report
            report = self._phase_7_generate_report(
                file_inventory=file_inventory,
                code_analysis=code_analysis,
                semantic_index=semantic_index,
                git_history=git_history,
                dependency_analysis=dependency_analysis,
                elapsed_time=(datetime.now() - start_time).total_seconds(),
            )
            
            logger.info("🎭 Orchestrator completing: ✅ Discovery Complete")
            return report
            
        except Exception as e:
            logger.error(f"Discovery operation failed: {e}", exc_info=True)
            raise
    
    def _phase_1_resolve_scope(
        self,
        scope: str | Path | Dict[str, Any],
        depth: str
    ) -> DiscoveryScope:
        """Phase 1: Resolve discovery scope."""
        self.current_phase = 1
        logger.info(f"🎭 Phase transition: START → Phase 1: Scope Resolution")
        
        # TODO: Implement scope resolution
        # This is a skeleton - implementation in GREEN phase
        raise NotImplementedError("Phase 1 not yet implemented")
    
    def _phase_2_discover_files(self, scope: DiscoveryScope) -> FileInventory:
        """Phase 2: Discover and catalog files."""
        self.current_phase = 2
        logger.info(f"🎭 Phase transition: Phase 1 → Phase 2: File Discovery")
        
        # TODO: Implement file discovery
        raise NotImplementedError("Phase 2 not yet implemented")
    
    def _phase_3_analyze_code(self, inventory: FileInventory):
        """Phase 3: AST-based code analysis."""
        self.current_phase = 3
        logger.info(f"🎭 Phase transition: Phase 2 → Phase 3: Code Analysis")
        
        # TODO: Implement AST analysis
        raise NotImplementedError("Phase 3 not yet implemented")
    
    def _phase_4_build_semantic_index(self, inventory: FileInventory):
        """Phase 4: Build semantic search index."""
        self.current_phase = 4
        logger.info(f"🎭 Phase transition: Phase 3 → Phase 4: Semantic Indexing")
        
        # TODO: Implement semantic indexing
        raise NotImplementedError("Phase 4 not yet implemented")
    
    def _phase_5_analyze_git_history(self, scope: DiscoveryScope):
        """Phase 5: Analyze Git history."""
        self.current_phase = 5
        logger.info(f"🎭 Phase transition: Phase 4 → Phase 5: Git History")
        
        # TODO: Implement Git analysis
        raise NotImplementedError("Phase 5 not yet implemented")
    
    def _phase_6_discover_dependencies(self, inventory: FileInventory) -> Dict[str, Any]:
        """Phase 6: Discover actual dependency usage."""
        self.current_phase = 6
        logger.info(f"🎭 Phase transition: Phase 5 → Phase 6: Dependency Discovery")
        
        import re
        from collections import defaultdict
        
        try:
            # Scan all Python files for imports
            actual_imports = set()
            import_locations = defaultdict(list)
            
            for file_path in inventory.files if hasattr(inventory, 'files') else []:
                if not str(file_path).endswith('.py'):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            # Match: import package
                            import_match = re.match(r'^import\s+(\w+)', line)
                            if import_match:
                                pkg = import_match.group(1)
                                actual_imports.add(pkg)
                                import_locations[pkg].append((str(file_path), line_num))
                            
                            # Match: from package import ...
                            from_match = re.match(r'^from\s+([\w.]+)', line)
                            if from_match:
                                pkg = from_match.group(1).split('.')[0]
                                actual_imports.add(pkg)
                                import_locations[pkg].append((str(file_path), line_num))
                except Exception as e:
                    logger.warning(f"Failed to scan {file_path}: {e}")
            
            # Load requirements.txt packages
            declared_packages = set()
            requirements_files = [
                self.cortex_root / 'requirements.txt',
                self.cortex_root / 'requirements-production.txt',
                self.cortex_root / 'requirements-optional.txt',
            ]
            
            for req_file in requirements_files:
                if req_file.exists():
                    try:
                        with open(req_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#'):
                                    # Extract package name (before >=, ==, etc.)
                                    pkg_name = re.split(r'[><=!]', line)[0].strip()
                                    declared_packages.add(pkg_name.lower())
                    except Exception as e:
                        logger.warning(f"Failed to read {req_file}: {e}")
            
            # Compare actual vs declared
            # Normalize package names (e.g., python-dateutil → dateutil)
            package_mappings = {
                'dateutil': 'python-dateutil',
                'yaml': 'PyYAML',
                'sklearn': 'scikit-learn',
                'docx': 'python-docx',
                'github': 'PyGithub',
            }
            
            used_packages = set()
            for imp in actual_imports:
                normalized = package_mappings.get(imp.lower(), imp.lower())
                if normalized in declared_packages:
                    used_packages.add(normalized)
            
            unused_packages = declared_packages - used_packages
            
            # Filter out Python stdlib modules
            stdlib_modules = {
                'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections',
                'contextlib', 'copy', 'csv', 'dataclasses', 'datetime', 'difflib',
                'enum', 'functools', 'gc', 'hashlib', 'heapq', 'html', 'http',
                'importlib', 'inspect', 'io', 'json', 'logging', 'math', 'mimetypes',
                'multiprocessing', 'os', 'pathlib', 'pickle', 'platform', 'queue',
                'random', 're', 'secrets', 'shutil', 'socket', 'socketserver', 'ssl',
                'statistics', 'subprocess', 'sys', 'tempfile', 'textwrap', 'threading',
                'time', 'traceback', 'tracemalloc', 'typing', 'unittest', 'urllib',
                'uuid', 'venv', 'weakref', 'webbrowser', 'xml',
            }
            
            actual_imports = {imp for imp in actual_imports if imp.lower() not in stdlib_modules}
            
            return {
                'actual_imports': sorted(actual_imports),
                'declared_packages': sorted(declared_packages),
                'used_packages': sorted(used_packages),
                'unused_packages': sorted(unused_packages),
                'import_locations': dict(import_locations),
                'package_mappings': package_mappings,
                'total_files_scanned': len([f for f in (inventory.files if hasattr(inventory, 'files') else []) if str(f).endswith('.py')]),
                'waste_percentage': round(len(unused_packages) / max(len(declared_packages), 1) * 100, 2) if declared_packages else 0,
            }
            
        except Exception as e:
            logger.error(f"Dependency discovery failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    def _phase_7_generate_report(
        self,
        file_inventory: FileInventory,
        code_analysis,
        semantic_index,
        git_history,
        dependency_analysis: Dict[str, Any],
        elapsed_time: float,
    ) -> DiscoveryReport:
        """Phase 7: Generate comprehensive report."""
        self.current_phase = 7
        logger.info(f"🎭 Phase transition: Phase 6 → Phase 7: Report Generation")
        
        # TODO: Implement report generation
        raise NotImplementedError("Phase 7 not yet implemented")
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress.
        
        Returns:
            Progress information
        """
        return {
            "current_phase": self.current_phase,
            "total_phases": self.total_phases,
            "phase_name": self._get_phase_name(self.current_phase),
            "completion_percentage": (self.current_phase / self.total_phases) * 100,
        }
    
    def _get_phase_name(self, phase: int) -> str:
        """Get human-readable phase name."""
        phase_names = {
            0: "Not Started",
            1: "Scope Resolution",
            2: "File Discovery",
            3: "Code Analysis",
            4: "Semantic Indexing",
            5: "Git History Analysis",
            6: "Dependency Discovery",
            7: "Report Generation",
        }
        return phase_names.get(phase, "Unknown")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the Discovery Orchestrator.
        
        Returns:
            Metadata dictionary with orchestrator information
        """
        return {
            "operation_name": "discovery",
            "version": "1.1.0",
            "description": "Comprehensive codebase discovery and analysis",
            "complexity_tier": 4,
            "complexity_score": 78,
            "phases": self.total_phases,
            "current_phase": self.current_phase,
            "capabilities": [
                "file_discovery",
                "ast_analysis",
                "semantic_indexing",
                "git_history_analysis",
                "pattern_detection",
                "dependency_mapping",
                "dependency_discovery",  # NEW
                "unused_package_detection"  # NEW
            ],
            "supported_languages": ["python", "csharp", "javascript", "typescript"],
            "status": "in_development"
        }

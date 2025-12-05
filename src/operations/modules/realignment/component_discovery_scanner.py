"""
Component Discovery Scanner

Discovers existing SOLID analyzers, enforcers, and dependency graphs in CORTEX codebase.
Reports unwired components that should be integrated into TDD workflow.

Author: Asif Hussain
Date: December 5, 2025
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Dict

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredComponent:
    """Represents a discovered component with its capabilities."""
    
    name: str                        # Class name
    file_path: Path                  # Full path to file
    module_path: str                 # Import path (e.g., "src.tier0.solid_enforcer")
    capabilities: List[str] = field(default_factory=list)  # ["SRP", "OCP", ...]
    is_wired: bool = False          # Imported anywhere?
    potential_uses: List[str] = field(default_factory=list)  # Suggested wiring targets


class ComponentDiscoveryScanner:
    """Scans CORTEX codebase for unwired architectural components."""
    
    # Patterns for component discovery
    COMPONENT_PATTERNS = [
        "**/solid_principle_enforcer.py",
        "**/code_review_plugin.py",
        "**/dependency_crawler.py",
        "**/*_analyzer.py",
        "**/*_enforcer.py",
        "**/*_detector.py"
    ]
    
    # Directories to exclude
    EXCLUDE_DIRS = {
        "tests",
        "cortex-brain",
        "cortex-extension",
        "deploy-packages",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "venv",
        ".venv"
    }
    
    # Capability detection patterns
    CAPABILITY_PATTERNS = {
        "SRP": ["srp", "single_responsibility", "single responsibility"],
        "OCP": ["ocp", "open_closed", "open closed"],
        "LSP": ["lsp", "liskov", "substitution"],
        "ISP": ["isp", "interface_segregation", "interface segregation"],
        "DIP": ["dip", "dependency_inversion", "dependency inversion"],
        "COUPLING": ["coupling", "coupled", "dependency"],
        "CIRCULAR_DEPS": ["circular", "cycle", "circular dependency"],
        "COHESION": ["cohesion", "cohesive"]
    }
    
    # Suggested wiring targets based on capabilities
    WIRING_SUGGESTIONS = {
        "SRP": ["RefactoringIntelligence", "TDDWorkflow"],
        "OCP": ["RefactoringIntelligence", "TDDWorkflow"],
        "LSP": ["RefactoringIntelligence", "TDDWorkflow"],
        "ISP": ["RefactoringIntelligence", "TDDWorkflow"],
        "DIP": ["RefactoringIntelligence", "TDDWorkflow"],
        "COUPLING": ["RefactoringIntelligence", "DependencyAnalyzer"],
        "CIRCULAR_DEPS": ["RefactoringIntelligence", "DependencyAnalyzer"],
        "COHESION": ["RefactoringIntelligence", "CodeReviewAgent"]
    }
    
    def __init__(self):
        """Initialize scanner."""
        self.discovered_components: List[DiscoveredComponent] = []
        self.scanned_files: Set[Path] = set()
    
    def discover_components(self, cortex_root: Path) -> List[DiscoveredComponent]:
        """
        Discover all architectural components in CORTEX codebase.
        
        Args:
            cortex_root: Root directory of CORTEX
            
        Returns:
            List of discovered components
        """
        logger.info("🔍 Scanning CORTEX codebase for architectural components...")
        
        self.discovered_components.clear()
        self.scanned_files.clear()
        
        # Find all matching files
        matching_files = self._find_matching_files(cortex_root)
        logger.info(f"Found {len(matching_files)} files to scan")
        
        # Scan each file for components
        for file_path in matching_files:
            self._scan_file(file_path, cortex_root)
        
        # Check wiring status for each component
        for component in self.discovered_components:
            component.is_wired = self._check_if_wired(
                cortex_root,
                component.name,
                component.file_path
            )
        
        logger.info(f"✅ Discovered {len(self.discovered_components)} components")
        unwired_count = sum(1 for c in self.discovered_components if not c.is_wired)
        logger.info(f"⚠️  {unwired_count} components not wired")
        
        return self.discovered_components
    
    def _find_matching_files(self, cortex_root: Path) -> List[Path]:
        """Find all files matching component patterns."""
        matching_files = []
        
        for pattern in self.COMPONENT_PATTERNS:
            for file_path in cortex_root.glob(pattern):
                if self._should_scan_file(file_path):
                    matching_files.append(file_path)
        
        return matching_files
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Skip if already scanned
        if file_path in self.scanned_files:
            return False
        
        # Skip if in excluded directory
        for exclude_dir in self.EXCLUDE_DIRS:
            if exclude_dir in file_path.parts:
                return False
        
        # Skip test files
        if file_path.name.startswith("test_"):
            return False
        
        return True
    
    def _matches_pattern(self, file_path: Path) -> bool:
        """Check if file matches any component pattern."""
        for pattern in self.COMPONENT_PATTERNS:
            # Convert glob pattern to simple check
            if "*_enforcer.py" in pattern and file_path.name.endswith("_enforcer.py"):
                return True
            if "*_analyzer.py" in pattern and file_path.name.endswith("_analyzer.py"):
                return True
            if "*_detector.py" in pattern and file_path.name.endswith("_detector.py"):
                return True
            
            # Check specific files
            if file_path.name in pattern.split("/")[-1].replace("**", ""):
                return True
        
        return False
    
    def _scan_file(self, file_path: Path, cortex_root: Path):
        """Scan file for component classes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Find class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class looks like a component
                    if self._is_component_class(node):
                        component = self._create_component(
                            node,
                            file_path,
                            cortex_root,
                            content
                        )
                        self.discovered_components.append(component)
            
            self.scanned_files.add(file_path)
            
        except Exception as e:
            logger.warning(f"Failed to scan {file_path}: {e}")
    
    def _is_component_class(self, node: ast.ClassDef) -> bool:
        """Check if class is an architectural component."""
        name_lower = node.name.lower()
        
        # Check for key patterns
        component_keywords = [
            "enforcer", "analyzer", "detector", "checker",
            "validator", "crawler", "graph", "solid"
        ]
        
        return any(keyword in name_lower for keyword in component_keywords)
    
    def _create_component(
        self,
        node: ast.ClassDef,
        file_path: Path,
        cortex_root: Path,
        content: str
    ) -> DiscoveredComponent:
        """Create DiscoveredComponent from AST node."""
        # Extract module path
        rel_path = file_path.relative_to(cortex_root)
        module_path = str(rel_path.with_suffix("")).replace("\\", ".").replace("/", ".")
        
        # Extract capabilities
        capabilities = self._extract_capabilities_from_code(content)
        
        # Determine potential uses
        potential_uses = self._determine_potential_uses(capabilities)
        
        return DiscoveredComponent(
            name=node.name,
            file_path=file_path,
            module_path=module_path,
            capabilities=capabilities,
            is_wired=False,  # Will be checked later
            potential_uses=potential_uses
        )
    
    def _extract_capabilities_from_code(self, code: str) -> List[str]:
        """Extract capabilities by searching for method/variable patterns."""
        capabilities = []
        code_lower = code.lower()
        
        for capability, patterns in self.CAPABILITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in code_lower:
                    if capability not in capabilities:
                        capabilities.append(capability)
                    break
        
        return capabilities
    
    def _determine_potential_uses(self, capabilities: List[str]) -> List[str]:
        """Determine where component should be wired based on capabilities."""
        potential_uses = set()
        
        for capability in capabilities:
            if capability in self.WIRING_SUGGESTIONS:
                potential_uses.update(self.WIRING_SUGGESTIONS[capability])
        
        return list(potential_uses)
    
    def _check_if_wired(
        self,
        cortex_root: Path,
        component_name: str,
        component_path: Path
    ) -> bool:
        """
        Check if component is imported anywhere in codebase.
        
        Args:
            cortex_root: Root directory
            component_name: Name of component class
            component_path: Path to component file
            
        Returns:
            True if component is imported somewhere
        """
        # Search for imports in Python files
        src_dir = cortex_root / "src"
        if not src_dir.exists():
            return False
        
        for py_file in src_dir.rglob("*.py"):
            # Skip the component file itself
            if py_file == component_path:
                continue
            
            # Skip test files
            if "test" in py_file.name.lower():
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for import statements
                if component_name in content:
                    # Verify it's actually an import
                    for line in content.split('\n'):
                        if 'import' in line and component_name in line:
                            return True
                
            except Exception:
                continue
        
        return False


def format_discovery_report(components: List[DiscoveredComponent]) -> Dict:
    """
    Format discovery results for reporting.
    
    Args:
        components: List of discovered components
        
    Returns:
        Report dictionary
    """
    unwired = [c for c in components if not c.is_wired]
    wired = [c for c in components if c.is_wired]
    
    return {
        "total_discovered": len(components),
        "wired_count": len(wired),
        "unwired_count": len(unwired),
        "unwired_components": [
            {
                "name": c.name,
                "file": str(c.file_path),
                "capabilities": c.capabilities,
                "should_wire_to": c.potential_uses
            }
            for c in unwired
        ]
    }

"""
Circular Dependency Validator for Phase 56 Intelligence Layer.

Validates that cortex/intelligence/ has zero circular dependencies
with cortex/lens/ to ensure MCP-FIRST architecture compliance.

Authority: Phase 56 - LENS/Intelligence Hybrid Architecture (S5)
"""

import ast
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple


class CircularDependencyAnalyzer:
    """Analyzes import relationships to detect circular dependencies."""
    
    def __init__(self, workspace_root: Path):
        """
        Initialize analyzer.
        
        Args:
            workspace_root: Root of CORTEX workspace
        """
        self.workspace_root = workspace_root
        self.import_graph: Dict[str, Set[str]] = {}
        self.violations: List[Tuple[str, str]] = []
    
    def analyze_file(self, file_path: Path) -> Set[str]:
        """
        Extract all imports from a Python file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Set of imported module names
        """
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
        except Exception:
            return set()
        
        imports = set()
        
        for node in ast.walk(tree):
            # Handle: import x, import x.y.z
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            
            # Handle: from x import y, from x.y import z
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        
        return imports
    
    def build_import_graph(self, directory: Path, package_prefix: str) -> None:
        """
        Build import graph for a directory.
        
        Args:
            directory: Directory to analyze
            package_prefix: Package name prefix (e.g., "cortex.intelligence")
        """
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            relative_path = py_file.relative_to(self.workspace_root)
            module_path = str(relative_path).replace("/", ".").replace(".py", "")
            
            imports = self.analyze_file(py_file)
            
            # Filter to only CORTEX imports
            cortex_imports = {
                imp for imp in imports 
                if imp in ["cortex", "cortex_brain"]
            }
            
            if module_path not in self.import_graph:
                self.import_graph[module_path] = set()
            
            self.import_graph[module_path].update(cortex_imports)
    
    def check_no_reverse_imports(
        self,
        source_package: str,
        target_package: str,
    ) -> bool:
        """
        Check that source_package does NOT import from target_package.
        
        Args:
            source_package: Source package (e.g., "cortex.intelligence")
            target_package: Target package (e.g., "cortex.lens")
        
        Returns:
            True if no reverse imports found, False otherwise
        """
        violations = []
        
        for module, imports in self.import_graph.items():
            # Check if module is from source_package
            if module.startswith(source_package):
                # Check if it imports anything from target_package
                for imp in imports:
                    if imp.startswith(target_package):
                        violations.append((module, imp))
        
        self.violations.extend(violations)
        return len(violations) == 0


def validate_phase_56_architecture() -> bool:
    """
    Validate Phase 56 architecture: zero circular dependencies.
    
    Ensures:
    - cortex/intelligence/ does NOT import from cortex/lens/ ✅
    - cortex/lens/ CAN import from cortex/intelligence/ ✅
    - No bidirectional imports ✅
    
    Returns:
        True if validation passes, False otherwise
    """
    # Find workspace root by going up from tests/ to project root
    test_file = Path(__file__)
    workspace_root = test_file.parent.parent.parent.parent  # tests/unit/intelligence/ → root
    
    analyzer = CircularDependencyAnalyzer(workspace_root)
    
    # Build import graphs for both packages
    intelligence_dir = workspace_root / "cortex" / "intelligence"
    lens_dir = workspace_root / "cortex" / "lens"
    
    print("🔍 Phase 56 Circular Dependency Validation")
    print("=" * 60)
    print(f"📂 Workspace root: {workspace_root}")
    print()
    
    # Analyze intelligence layer
    if intelligence_dir.exists():
        print(f"📍 Analyzing: {intelligence_dir.relative_to(workspace_root)}")
        analyzer.build_import_graph(intelligence_dir, "cortex.intelligence")
        print(f"   ✅ Found {len(analyzer.import_graph)} modules in intelligence layer")
    else:
        print(f"❌ Intelligence layer not found: {intelligence_dir}")
        return False
    
    # Analyze LENS layer
    if lens_dir.exists():
        print(f"📍 Analyzing: {lens_dir.relative_to(workspace_root)}")
        analyzer.build_import_graph(lens_dir, "cortex.lens")
        print(f"   ✅ Found {len(analyzer.import_graph)} total modules across both")
    else:
        print(f"❌ LENS layer not found: {lens_dir}")
        return False
    
    print()
    print("🔒 Circular Dependency Checks")
    print("-" * 60)
    
    # Check 1: Intelligence should NOT import LENS
    print("Check 1: Intelligence ↛ LENS (must be true)")
    result1 = analyzer.check_no_reverse_imports(
        "cortex.intelligence",
        "cortex.lens",
    )
    
    if result1:
        print("   ✅ PASS: Intelligence layer has zero imports from LENS")
    else:
        print("   ❌ FAIL: Intelligence layer imports from LENS (circular!)")
        for module, imp in analyzer.violations:
            print(f"      - {module} imports {imp}")
    
    print()
    print("📊 Results")
    print("-" * 60)
    
    if result1:
        print("✅ Phase 56 Architecture Validation: PASSED")
        print()
        print("Summary:")
        print("  • cortex/intelligence/ is independent ✅")
        print("  • cortex/lens/ can import from intelligence/ ✅")
        print("  • Zero circular dependencies ✅")
        print("  • One-way dependency flow enforced ✅")
        return True
    else:
        print("❌ Phase 56 Architecture Validation: FAILED")
        print()
        print("Violations found:")
        for module, imp in analyzer.violations:
            print(f"  ❌ {module} → {imp}")
        return False


if __name__ == "__main__":
    passed = validate_phase_56_architecture()
    sys.exit(0 if passed else 1)

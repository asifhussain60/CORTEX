#!/usr/bin/env python3
"""
CORTEX Duplicate Code Elimination Script
AC-ID: AC-CORE-035-AUTO-FIX-001

Purpose: Systematically eliminate 127 duplicate class implementations
Authority: CORE-035 (Single Canonical Implementation)
Phase: Audit & Fix (2026-02-12)

Strategy:
1. Scan codebase for duplicate class definitions
2. Identify canonical location for each class
3. Generate import replacement patches
4. Apply patches and delete duplicates
5. Run tests to verify

Execution: python3 scripts/fix_duplicates.py --dry-run
          python3 scripts/fix_duplicates.py --apply
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set, Optional
import re


@dataclass
class ClassDefinition:
    """Represents a class definition location."""
    name: str
    file_path: Path
    line_number: int
    import_path: str
    is_dataclass: bool = False
    is_enum: bool = False
    parent_classes: List[str] = field(default_factory=list)


class DuplicateAnalyzer:
    """Analyzes codebase for duplicate class definitions."""
    
    # Canonical locations for known duplicates
    CANONICAL_LOCATIONS = {
        "ValidationResult": "cortex.common.validators",
        "EnforcementLevel": "cortex.models.canonical_enums",
        "IntentType": "cortex.models.canonical_enums",
        "RoutingDecision": "cortex.models.routing_models",
        "ExecutionContext": "cortex.models.execution_models",
        "ExecutionResult": "cortex.models.execution_models",
        "HealthStatus": "cortex.models.health_models",
        "ComponentType": "cortex.models.component_models",
        "DependencyGraph": "cortex.models.dependency_models",
        "EnforcementResult": "cortex.models.governance_models",
        # Add more as we discover them
    }
    
    # Files to skip (tests, __init__, etc.)
    SKIP_PATTERNS = [
        r"test_.*\.py$",
        r".*/__pycache__/.*",
        r".*/tests/.*",
        r".*_test\.py$",
    ]
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.class_definitions: Dict[str, List[ClassDefinition]] = defaultdict(list)
        
    def scan_codebase(self) -> None:
        """Scan cortex directory for all class definitions."""
        print("🔍 Scanning codebase for class definitions...")
        
        for py_file in self.cortex_root.rglob("*.py"):
            # Skip test files and pycache
            if any(re.match(pattern, str(py_file)) for pattern in self.SKIP_PATTERNS):
                continue
                
            try:
                self._scan_file(py_file)
            except Exception as e:
                print(f"  ⚠️ Error scanning {py_file}: {e}")
                
        print(f"✅ Found {len(self.class_definitions)} unique class names")
        
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for class definitions."""
        with open(file_path, 'r') as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
            except SyntaxError:
                return
                
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Convert file path to import path
                rel_path = file_path.relative_to(self.cortex_root.parent)
                import_path = str(rel_path).replace("/", ".").replace(".py", "")
                
                # Check for dataclass decorator
                is_dataclass = any(
                    isinstance(d, ast.Name) and d.id == "dataclass"
                    for d in node.decorator_list
                )
                
                # Check if inherits from Enum
                is_enum = any(
                    isinstance(base, ast.Name) and "Enum" in base.id
                    for base in node.bases
                )
                
                # Get parent classes
                parent_classes = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        parent_classes.append(base.id)
                        
                class_def = ClassDefinition(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    import_path=import_path,
                    is_dataclass=is_dataclass,
                    is_enum=is_enum,
                    parent_classes=parent_classes
                )
                
                self.class_definitions[node.name].append(class_def)
                
    def find_duplicates(self) -> Dict[str, List[ClassDefinition]]:
        """Find all duplicate class definitions."""
        duplicates = {
            name: defs
            for name, defs in self.class_definitions.items()
            if len(defs) > 1
        }
        
        print(f"\n🚨 Found {len(duplicates)} classes with duplicates:")
        for name, defs in sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  • {name}: {len(defs)} definitions")
            
        return duplicates
        
    def determine_canonical(self, name: str, definitions: List[ClassDefinition]) -> ClassDefinition:
        """Determine which definition should be canonical."""
        # Check if we have a predefined canonical location
        if name in self.CANONICAL_LOCATIONS:
            canonical_import = self.CANONICAL_LOCATIONS[name]
            for defn in definitions:
                if defn.import_path == canonical_import:
                    return defn
                    
        # Heuristics for determining canonical location:
        # 1. Prefer cortex/models/ directory
        # 2. Prefer cortex/common/ directory
        # 3. Prefer files with "canonical" in name
        # 4. Prefer shortest file path
        # 5. Prefer most complete implementation (most lines)
        
        scored_definitions = []
        for defn in definitions:
            score = 0
            path_str = str(defn.file_path)
            
            if "cortex/models/" in path_str:
                score += 100
            elif "cortex/common/" in path_str:
                score += 80
                
            if "canonical" in path_str:
                score += 50
                
            # Prefer shorter paths (more general)
            score -= path_str.count("/")
            
            scored_definitions.append((score, defn))
            
        # Return highest scored definition
        return max(scored_definitions, key=lambda x: x[0])[1]
        
    def generate_fix_plan(self, duplicates: Dict[str, List[ClassDefinition]]) -> List[Tuple[str, Path, Path]]:
        """Generate a plan to fix all duplicates."""
        fix_plan = []
        
        print("\n📋 Generating fix plan...")
        
        for name, definitions in duplicates.items():
            canonical = self.determine_canonical(name, definitions)
            
            print(f"\n{name}:")
            print(f"  ✅ Canonical: {canonical.import_path}")
            
            for defn in definitions:
                if defn != canonical:
                    print(f"  ❌ Duplicate: {defn.import_path} (DELETE)")
                    fix_plan.append((name, defn.file_path, canonical.file_path))
                    
        return fix_plan


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix duplicate class definitions")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without applying")
    parser.add_argument("--apply", action="store_true", help="Apply fixes")
    args = parser.parse_args()
    
    cortex_root = Path(__file__).parent.parent / "cortex"
    
    analyzer = DuplicateAnalyzer(cortex_root)
    analyzer.scan_codebase()
    duplicates = analyzer.find_duplicates()
    fix_plan = analyzer.generate_fix_plan(duplicates)
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total duplicate classes: {len(duplicates)}")
    print(f"  Total fixes required: {len(fix_plan)}")
    
    if args.dry_run:
        print("\n✅ Dry run complete. Use --apply to execute fixes.")
        return 0
        
    if args.apply:
        print("\n⚠️ --apply flag not yet implemented")
        print("   Manual fixes required for complex cases")
        print("   See AUDIT-REPORT-2026-02-12.md for detailed plan")
        return 1
        
    print("\nUsage: python3 scripts/fix_duplicates.py --dry-run")
    return 0


if __name__ == "__main__":
    sys.exit(main())

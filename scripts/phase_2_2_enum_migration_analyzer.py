#!/usr/bin/env python3
"""
Automated Import Migration Tool - Phase 2.2

Purpose: Replace 275+ duplicate enum definitions with canonical imports
from cortex.models.canonical_enums

Strategy:
1. Scan all Python files for enum definitions
2. Identify duplicates against canonical_enums.py
3. Replace with canonical imports
4. Validate circular import prevention

Author: GitHub Copilot | AC-ID: AC-PERMANENT-FIX-017
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class EnumDefinitionFinder(ast.NodeVisitor):
    """Find all Enum class definitions in a Python file."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.enums = []
        self.imports = []
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Identify Enum class definitions."""
        # Check if inherits from Enum
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Enum":
                self.enums.append({
                    "name": node.name,
                    "line": node.lineno,
                    "col": node.col_offset,
                    "end_line": node.end_lineno,
                })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track existing imports."""
        if node.module:
            for alias in node.names:
                self.imports.append({
                    "module": node.module,
                    "name": alias.name,
                    "asname": alias.asname,
                })
        self.generic_visit(node)


class CanonicalEnumRegistry:
    """Load canonical enums from canonical_enums.py."""
    
    def __init__(self, canonical_path: str):
        self.canonical_path = canonical_path
        self.enums: Set[str] = set()
        self._load()
    
    def _load(self):
        """Extract enum names from canonical_enums.py."""
        try:
            with open(self.canonical_path, 'r') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Enum":
                            self.enums.add(node.name)
        except Exception as e:
            print(f"❌ Failed to load canonical enums: {e}")
    
    def is_canonical(self, enum_name: str) -> bool:
        """Check if enum is in canonical list."""
        return enum_name in self.enums


def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in codebase."""
    exclude_dirs = {
        '__pycache__', '.git', '.pytest_cache', 'node_modules',
        '.venv', 'venv', '.cortex', '_backups', '_archive'
    }
    
    python_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove excluded directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        # Skip test files and other non-production code
        if 'test' in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(Path(dirpath) / filename)
    
    return python_files


def analyze_file(filepath: Path) -> Tuple[List[Dict], List[Dict]]:
    """Analyze a file for enum definitions and imports."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        finder = EnumDefinitionFinder(str(filepath))
        finder.visit(tree)
        
        return finder.enums, finder.imports
    except Exception:
        return [], []


def get_enum_source_lines(filepath: Path, enum_def: Dict) -> List[str]:
    """Extract source lines for an enum definition."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start_line = enum_def['line'] - 1
        end_line = enum_def['end_line']
        
        return lines[start_line:end_line]
    except Exception:
        return []


def generate_migration_report(
    root_dir: str,
    canonical_registry: CanonicalEnumRegistry
) -> Dict:
    """Generate comprehensive migration report."""
    
    report = {
        "total_files": 0,
        "files_with_duplicates": 0,
        "canonical_enums_to_import": defaultdict(list),
        "duplicates_found": 0,
        "files_by_duplicate_count": defaultdict(list),
    }
    
    python_files = find_python_files(root_dir)
    report["total_files"] = len(python_files)
    
    for filepath in python_files:
        enums, _ = analyze_file(filepath)
        
        file_duplicates = []
        for enum_def in enums:
            enum_name = enum_def['name']
            if canonical_registry.is_canonical(enum_name):
                file_duplicates.append(enum_name)
                report["canonical_enums_to_import"][enum_name].append(str(filepath))
                report["duplicates_found"] += 1
        
        if file_duplicates:
            report["files_with_duplicates"] += 1
            count = len(file_duplicates)
            report["files_by_duplicate_count"][count].append(
                (str(filepath), file_duplicates)
            )
    
    return report


def main():
    """Execute import migration analysis."""
    
    root_dir = "/Users/asifhussain/PROJECTS/CORTEX"
    canonical_path = f"{root_dir}/cortex/models/canonical_enums.py"
    
    print("=" * 80)
    print("PHASE 2.2: ENUM IMPORT MIGRATION ANALYSIS")
    print("=" * 80)
    print()
    
    # Load canonical enum registry
    print("📚 Loading canonical enum registry...")
    registry = CanonicalEnumRegistry(canonical_path)
    print(f"   ✓ Found {len(registry.enums)} canonical enums")
    print()
    
    # Analyze codebase
    print("🔍 Scanning codebase for duplicate definitions...")
    report = generate_migration_report(root_dir, registry)
    print()
    
    # Display results
    print("📊 ANALYSIS RESULTS:")
    print("-" * 80)
    print(f"  Total Python files scanned:      {report['total_files']}")
    print(f"  Files with duplicate enums:      {report['files_with_duplicates']}")
    print(f"  Total duplicate definitions:     {report['duplicates_found']}")
    print()
    
    # Group by frequency
    print("📈 DUPLICATE FREQUENCY:")
    print("-" * 80)
    for count in sorted(report['files_by_duplicate_count'].keys(), reverse=True):
        files = report['files_by_duplicate_count'][count]
        print(f"  {count} duplicate(s):   {len(files)} file(s)")
    print()
    
    # Show top duplicate enums
    print("🔴 TOP DUPLICATE ENUMS (by frequency):")
    print("-" * 80)
    sorted_enums = sorted(
        report['canonical_enums_to_import'].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for enum_name, files in sorted_enums[:20]:
        print(f"  {enum_name:30s} → {len(files):3d} locations")
    print()
    
    if len(sorted_enums) > 20:
        print(f"  ... and {len(sorted_enums) - 20} more enums")
        print()
    
    # Sample files needing migration
    print("📝 SAMPLE FILES NEEDING MIGRATION (showing 5):")
    print("-" * 80)
    for filepath, duplicates in list(report['files_by_duplicate_count'].values())[0][:5]:
        print(f"  {filepath}")
        for dup in duplicates:
            print(f"    - {dup}")
    print()
    
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"✅ Analysis complete")
    print(f"📊 {report['duplicates_found']} duplicate enum definitions identified")
    print(f"📁 {report['files_with_duplicates']} files require migration")
    print()
    print("Next Steps:")
    print("  1. Review this report")
    print("  2. Execute automated import replacement")
    print("  3. Run test suite to validate changes")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Smart Deduplication Analyzer
Distinguishes TRUE duplicates from FALSE POSITIVES by comparing enum values.

Author: CORTEX Architect
"""

import ast
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class SmartDedupAnalyzer:
    """Analyzes duplicates by comparing actual enum values."""
    
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.enum_definitions: Dict[str, List[Tuple[Path, Set[str]]]] = defaultdict(list)
        
    def extract_enum_values(self, filepath: Path, class_name: str) -> Set[Tuple[str, str]]:
        """Extract enum values from a class definition.
        
        Returns set of (member_name, member_value) tuples for accurate comparison.
        """
        try:
            content = filepath.read_text()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    values = set()
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    # Extract BOTH name and value for accurate comparison
                                    member_name = target.id
                                    if isinstance(item.value, ast.Constant):
                                        member_value = repr(item.value.value)
                                    else:
                                        member_value = ast.unparse(item.value)
                                    values.add((member_name, member_value))
                    return values
        except Exception as e:
            print(f"Error parsing {filepath}: {e}", file=sys.stderr)
        return set()
    
    def scan_enums(self):
        """Scan all enum definitions."""
        for py_file in self.root.rglob("*.py"):
            if "test" in str(py_file) or ".venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's an Enum (look for Enum in bases)
                        is_enum = any(
                            (isinstance(base, ast.Name) and 'Enum' in base.id) or
                            (isinstance(base, ast.Attribute) and base.attr == 'Enum')
                            for base in node.bases
                        )
                        
                        if is_enum:
                            values = self.extract_enum_values(py_file, node.name)
                            self.enum_definitions[node.name].append((py_file, values))
                            
            except Exception:
                continue
    
    def find_true_duplicates(self) -> Dict[str, List[Path]]:
        """Find TRUE duplicates (same class name AND same values)."""
        true_dups = {}
        
        for class_name, definitions in self.enum_definitions.items():
            if len(definitions) < 2:
                continue
            
            # Group by value sets (now includes both names and values)
            value_groups = defaultdict(list)
            for filepath, values in definitions:
                # Convert set to frozen set for hashing
                value_key = frozenset(values)
                value_groups[value_key].append(filepath)
            
            # Find groups with multiple files (true duplicates)
            for value_set, filepaths in value_groups.items():
                if len(filepaths) > 1:
                    # Extract just member names for display
                    member_names = sorted([name for name, _ in value_set])
                    key = f"{class_name} ({', '.join(member_names[:3])}...)"
                    true_dups[key] = filepaths
        
        return true_dups
    
    def find_false_positives(self) -> Dict[str, List[Tuple[Path, Set[str]]]]:
        """Find FALSE POSITIVES (same class name, different values)."""
        false_positives = {}
        
        for class_name, definitions in self.enum_definitions.items():
            if len(definitions) < 2:
                continue
            
            # Check if values differ
            unique_values = set()
            for _, values in definitions:
                unique_values.add(frozenset(values))
            
            if len(unique_values) > 1:
                # Different values = false positive
                false_positives[class_name] = definitions
        
        return false_positives
    
    def generate_report(self):
        """Generate comprehensive report."""
        self.scan_enums()
        
        true_dups = self.find_true_duplicates()
        false_positives = self.find_false_positives()
        
        print("=" * 80)
        print("🧠 SMART DEDUPLICATION ANALYSIS")
        print("=" * 80)
        print()
        
        print(f"📊 Total Enum Classes Scanned: {len(self.enum_definitions)}")
        print(f"✅ TRUE Duplicates: {len(true_dups)}")
        print(f"⚠️  FALSE Positives: {len(false_positives)}")
        print()
        
        if true_dups:
            print("=" * 80)
            print("🔴 TRUE DUPLICATES (Same name, same values - MUST FIX)")
            print("=" * 80)
            for key, filepaths in sorted(true_dups.items()):
                print(f"\n❌ {key}")
                print(f"   Locations: {len(filepaths)} implementations")
                for fp in filepaths:
                    print(f"   - {fp.relative_to(self.root)}")
        
        if false_positives:
            print("\n" + "=" * 80)
            print("✅ FALSE POSITIVES (Same name, different values - OK)")
            print("=" * 80)
            for class_name, definitions in sorted(false_positives.items())[:10]:
                print(f"\n✓ {class_name} ({len(definitions)} implementations)")
                for filepath, values in definitions:
                    print(f"   - {filepath.relative_to(self.root)}")
                    # Display member_name=member_value format
                    value_display = ", ".join(f"{name}={val}" for name, val in sorted(values)[:3])
                    print(f"     Values: {value_display}")
        
        return len(true_dups)


def main():
    analyzer = SmartDedupAnalyzer("/Users/asifhussain/PROJECTS/CORTEX")
    violation_count = analyzer.generate_report()
    return violation_count


if __name__ == "__main__":
    sys.exit(main())

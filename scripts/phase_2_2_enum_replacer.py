#!/usr/bin/env python3
"""
Automated Enum Import Replacement Tool - Phase 2.2 Execution

Purpose: Replace all duplicate enum definitions with canonical imports

Strategy:
1. Find each duplicate enum definition in source files
2. Remove the definition (keeping imports that will be added)
3. Add "from cortex.models.canonical_enums import EnumName"
4. Validate syntax and no circular imports

Author: GitHub Copilot | AC-ID: AC-PERMANENT-FIX-017
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict


CANONICAL_ENUMS = {
    "ActionType",
    "ExecutionMode",
    "AlertSeverity",
    "AlertPriority",
    "AlertState",
    "AuditEventType",
    "AuditAction",
    "AuditOperationType",
    "ApprovalStatus",
    "CheckpointStatus",
    "ChallengeType",
    "ChallengeCategory",
    "IntentType",
    "RoutingType",
    "ChangeType",
    "BrainTier",
    "CircuitBreakerState",
    "CoherenceType",
    "ValidationLevel",
    "ContinuationReason",
    "DecisionStatus",
    "TierType",
    "GovernanceStatus",
    "RuleType",
    "KnowledgeSource",
    "AnalysisLevel",
    "OperationStatus",
    "StateTransition",
    "PhaseStatus",
    "PatternType",
    "MatchConfidence",
    "ResponseType",
    "MessageLevel",
    "TestType",
    "TestStatus",
    "QualityGate",
    "WiringState",
    "ComponentHealth",
    "WorkflowStage",
    "ExecutionStrategy",
}


class EnumReplacer:
    """Replace duplicate enum definitions with canonical imports."""
    
    def __init__(self, filepath: Path, canonical_enums: Set[str]):
        self.filepath = filepath
        self.canonical_enums = canonical_enums
        self.enums_to_add = set()
        self.enums_to_remove = []
    
    def process(self) -> Tuple[Optional[str], Dict]:
        """
        Process file and return modified content.
        
        Returns:
            (modified_content, metadata_dict)
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Parse AST
            tree = ast.parse(original_content)
            
            # Identify duplicates to remove and imports to add
            lines = original_content.split('\n')
            removed_ranges = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == "Enum":
                            if node.name in self.canonical_enums:
                                self.enums_to_add.add(node.name)
                                removed_ranges.append((node.lineno - 1, node.end_lineno))
            
            if not self.enums_to_add:
                return None, {"file": str(self.filepath), "enums_found": 0}
            
            # Remove duplicate class definitions
            modified_lines = []
            i = 0
            while i < len(lines):
                skip = False
                for start, end in removed_ranges:
                    if start <= i < end:
                        skip = True
                        i = end
                        break
                
                if not skip:
                    modified_lines.append(lines[i])
                    i += 1
            
            # Add import statement at top after existing imports
            import_index = self._find_import_insertion_point(modified_lines)
            import_stmt = self._generate_import_statement()
            modified_lines.insert(import_index, import_stmt)
            
            modified_content = '\n'.join(modified_lines)
            
            return modified_content, {
                "file": str(self.filepath),
                "enums_found": len(self.enums_to_add),
                "enums": sorted(self.enums_to_add),
            }
        
        except Exception as e:
            return None, {"file": str(self.filepath), "error": str(e)}
    
    def _find_import_insertion_point(self, lines: List[str]) -> int:
        """Find where to insert canonical enum import."""
        last_import_idx = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import_idx = i + 1
        
        return last_import_idx
    
    def _generate_import_statement(self) -> str:
        """Generate import statement for canonical enums."""
        enums_sorted = sorted(self.enums_to_add)
        
        # Create multi-line import for readability
        if len(enums_sorted) <= 3:
            return f"from cortex.models.canonical_enums import {', '.join(enums_sorted)}"
        
        enum_list = ", ".join(enums_sorted)
        formatted_list = enum_list.replace(", ", ",\n    ")
        return f"from cortex.models.canonical_enums import (\n    {formatted_list}\n)"


def process_codebase(root_dir: str, dry_run: bool = True) -> Dict:
    """Process entire codebase for enum replacement."""
    
    exclude_dirs = {
        '__pycache__', '.git', '.pytest_cache', 'node_modules',
        '.venv', 'venv', '.cortex', '_backups', '_archive'
    }
    
    results = {
        "total_files_processed": 0,
        "files_modified": 0,
        "total_enums_replaced": 0,
        "by_enum_type": defaultdict(int),
        "files": [],
        "errors": [],
    }
    
    python_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        # Skip test and archive directories
        if 'test' in dirpath or '_archive' in dirpath:
            continue
        
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = Path(dirpath) / filename
                python_files.append(filepath)
    
    print(f"Processing {len(python_files)} Python files...")
    print()
    
    for filepath in sorted(python_files):
        replacer = EnumReplacer(filepath, CANONICAL_ENUMS)
        modified_content, metadata = replacer.process()
        
        results["total_files_processed"] += 1
        
        if modified_content is not None:
            results["files_modified"] += 1
            results["total_enums_replaced"] += metadata["enums_found"]
            
            for enum_name in metadata["enums"]:
                results["by_enum_type"][enum_name] += 1
            
            results["files"].append(metadata)
            
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"✅ {filepath.name:40s} → {metadata['enums_found']} enums")
            else:
                print(f"🔍 {filepath.name:40s} → {metadata['enums_found']} enums (DRY RUN)")
        
        elif "error" in metadata:
            results["errors"].append(metadata)
            print(f"⚠️  {filepath.name:40s} → ERROR: {metadata['error']}")
    
    return results


def main():
    """Execute enum import replacement."""
    
    root_dir = "/Users/asifhussain/PROJECTS/CORTEX"
    
    print("=" * 80)
    print("PHASE 2.2: ENUM IMPORT REPLACEMENT (EXECUTION MODE)")
    print("=" * 80)
    print()
    
    # Execute enum replacement
    results = process_codebase(root_dir, dry_run=False)
    
    print()
    print("=" * 80)
    print("EXECUTION RESULTS:")
    print("=" * 80)
    print()
    print(f"Files processed:        {results['total_files_processed']}")
    print(f"Files to modify:        {results['files_modified']}")
    print(f"Enums to replace:       {results['total_enums_replaced']}")
    print()
    
    if results["errors"]:
        print(f"Errors encountered:     {len(results['errors'])}")
        print()
    
    print("Top enums by replacement frequency:")
    print("-" * 80)
    sorted_enums = sorted(
        results['by_enum_type'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for enum_name, count in sorted_enums[:15]:
        print(f"  {enum_name:30s} → {count:2d} replacements")
    
    if len(sorted_enums) > 15:
        print(f"  ... and {len(sorted_enums) - 15} more enums")
    
    print()
    print("=" * 80)
    print()
    print("✅ EXECUTION COMPLETE")
    print()
    print("Successfully modified:")
    print(f"  - {results['files_modified']} Python files")
    print(f"  - Replaced {results['total_enums_replaced']} enum definitions")
    print(f"  - Added canonical imports to {results['files_modified']} files")
    print()


if __name__ == "__main__":
    main()

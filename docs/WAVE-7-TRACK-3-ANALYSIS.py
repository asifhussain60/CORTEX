#!/usr/bin/env python3
"""
Wave 7 Track 3 Analysis: Identify Orphaned Orchestrators for Consolidation.

Purpose: Scan codebase to find:
1. DEPRECATED orchestrators (marked with deprecation warnings)
2. UNUSED orchestrators (zero imports from production code)
3. DUPLICATE functionality (consolidation candidates)
4. BROKEN references (orphaned dependencies)

Output: Prioritized consolidation plan
"""

import os
import subprocess
from pathlib import Path
from collections import defaultdict
import json

def run_cmd(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except:
        return ""

def find_deprecated_orchestrators():
    """Find orchestrators marked as DEPRECATED."""
    print("\n🔍 FINDING DEPRECATED ORCHESTRATORS")
    print("-" * 80)
    
    deprecated = []
    orchestrator_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators")
    
    for py_file in orchestrator_dir.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        try:
            content = py_file.read_text()
            if "DEPRECATED" in content or "deprecated" in content or "Deprecated" in content:
                # Extract deprecation message
                lines = content.split("\n")
                for i, line in enumerate(lines[:20]):
                    if "DEPRECATED" in line or "deprecated" in line:
                        print(f"  ✅ {py_file.name:<50} (line {i+1})")
                        deprecated.append(str(py_file))
                        break
        except:
            pass
    
    return deprecated

def find_unused_orchestrators():
    """Find orchestrators with zero imports from production code."""
    print("\n🔍 FINDING UNUSED ORCHESTRATORS")
    print("-" * 80)
    
    unused = []
    orchestrator_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators")
    
    for py_file in orchestrator_dir.rglob("*.py"):
        if py_file.name.startswith("__") or "test" in py_file.name:
            continue
        
        class_name = py_file.stem
        
        # Search for imports of this class
        search_cmd = f"grep -r 'from.*{class_name}\\|import.*{class_name}' /Users/asifhussain/PROJECTS/CORTEX --include='*.py' --exclude-dir=tests 2>/dev/null | wc -l"
        count = run_cmd(search_cmd)
        
        try:
            import_count = int(count)
            if import_count == 0 and py_file.stat().st_size < 5000:  # Less than 5KB
                print(f"  ⚪ {py_file.name:<50} (0 imports)")
                unused.append(str(py_file))
        except:
            pass
    
    return unused

def categorize_orchestrators():
    """Categorize all orchestrators by type."""
    print("\n📊 ORCHESTRATOR CATEGORIZATION")
    print("-" * 80)
    
    categories = defaultdict(list)
    orchestrator_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators")
    
    for py_file in orchestrator_dir.glob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        name = py_file.stem
        
        if "unified" in name:
            categories["Unified"].append(name)
        elif "extended" in name:
            categories["Extended"].append(name)
        elif "strategy" in name:
            categories["Strategy"].append(name)
        elif "integration" in name:
            categories["Integration"].append(name)
        else:
            categories["Other"].append(name)
    
    for category, items in sorted(categories.items()):
        print(f"  {category:<20} {len(items):2} orchestrators: {', '.join(items[:3])}{'...' if len(items) > 3 else ''}")
    
    return categories

def main():
    print("\n" + "="*80)
    print("🏗️  WAVE 7 TRACK 3: ORPHAN ORCHESTRATOR CLEANUP ANALYSIS")
    print("="*80)
    
    # Find deprecated
    deprecated = find_deprecated_orchestrators()
    print(f"\n  Total DEPRECATED: {len(deprecated)}")
    
    # Find unused
    unused = find_unused_orchestrators()
    print(f"\n  Total UNUSED: {len(unused)}")
    
    # Categorize
    categories = categorize_orchestrators()
    
    # Summary
    print("\n" + "="*80)
    print("📋 CONSOLIDATION PRIORITY")
    print("-" * 80)
    
    total_deprecated = len(deprecated)
    total_unused = len(unused)
    consolidation_targets = total_deprecated + total_unused
    
    print(f"\n  Priority 1 (Deprecated): {total_deprecated} orchestrators")
    print(f"  Priority 2 (Unused): {total_unused} orchestrators")
    print(f"  Total Consolidation Targets: {consolidation_targets}")
    
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("-" * 80)
    print("""
  1. Analyze each deprecated orchestrator for functionality migration
  2. Create unified strategies for common functionality
  3. Route all imports to unified strategies
  4. Remove deprecated files (after zero-import verification)
  5. Update references in documentation
  6. Run comprehensive test suite
  7. Commit with CORE-008 (TDD) enforcement
    """)
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

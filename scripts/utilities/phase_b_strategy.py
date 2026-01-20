#!/usr/bin/env python3
"""
Phase B Strategy: Intelligent Test File Batching for consolidation-001-src-cleanup

Purpose: Generate optimal batching strategy for 1,272 test file imports across 253 files
Strategy: 
  1. Identify largest files first (process high-volume files in batch mode)
  2. Group by directory structure (easier replacement patterns)
  3. Create mapping for each batch
  4. Execute batch replacements with systematic sed/python
  5. Validate after each batch

Output: 3-phase execution plan with concrete file lists and sed commands
"""

import os
import re
from collections import defaultdict
from pathlib import Path

def extract_all_test_imports():
    """Extract all src.* imports from tests/"""
    src_imports = defaultdict(list)
    
    if os.path.exists('tests'):
        for dirpath, dirnames, filenames in os.walk('tests'):
            for filename in filenames:
                if filename.endswith('.py'):
                    filepath = os.path.join(dirpath, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for lineno, line in enumerate(f, 1):
                                if re.match(r'^\s*(from src\.|import src)', line):
                                    key = line.strip()
                                    src_imports[key].append(f"{filepath}:{lineno}")
                    except Exception:
                        pass
    
    return src_imports

def generate_replacement_patterns():
    """Generate sed replacement patterns for common src.* modules"""
    patterns = {
        # Top-level replacements
        "from src.api": "from cortex.api",
        "from src.cli": "from cortex.cli",
        "from src.confirmation": "from cortex.confirmation",
        "from src.core": "from cortex.core",
        "from src.deployment": "from cortex.deployment",
        "from src.infrastructure": "from cortex.infrastructure",
        "from src.intent_router": "from cortex.intent_router",
        "from src.mcp": "from cortex.mcp",
        "from src.orchestrators": "from cortex.orchestrators",
        "from src.security": "from cortex.security",
        "from src.templates": "from cortex.templates",
        "from src.testing": "from cortex.testing",
        "from src.tools": "from cortex.tools",
        "from src.versioning": "from cortex.versioning",
        "import src": "import cortex",
    }
    
    return patterns

def categorize_files_by_import_count():
    """Categorize test files by number of imports"""
    src_imports = extract_all_test_imports()
    
    files_with_counts = defaultdict(int)
    for locations in src_imports.values():
        for loc in locations:
            filepath = loc.split(':')[0]
            files_with_counts[filepath] += 1
    
    # Sort by count
    sorted_files = sorted(files_with_counts.items(), key=lambda x: -x[1])
    
    # Categorize
    phase_b1 = []  # domain_brain tests (~200 imports)
    phase_b2 = []  # core tests (~600 imports)
    phase_b3 = []  # other tests (~400 imports)
    
    for filepath, count in sorted_files:
        if 'domain_brain' in filepath:
            phase_b1.append((filepath, count))
        elif 'core' in filepath and 'unit' in filepath:
            phase_b2.append((filepath, count))
        else:
            phase_b3.append((filepath, count))
    
    return phase_b1, phase_b2, phase_b3, sorted_files

def generate_sed_commands(phase_files):
    """Generate sed replacement command for a batch of files"""
    patterns = generate_replacement_patterns()
    
    # Create sed command
    sed_parts = []
    for src_pattern, cortex_pattern in patterns.items():
        # Escape for sed
        src_escaped = src_pattern.replace('/', '\\/')
        cortex_escaped = cortex_pattern.replace('/', '\\/')
        sed_parts.append(f"-e 's/{src_escaped}/{cortex_escaped}/g'")
    
    sed_cmd = f"sed -i '' {' '.join(sed_parts)} " + ' '.join([f'"{f[0]}"' for f in phase_files])
    return sed_cmd

# Main execution
if __name__ == '__main__':
    print("=" * 80)
    print("PHASE B STRATEGY: INTELLIGENT TEST FILE BATCHING")
    print("=" * 80)
    print()
    
    phase_b1, phase_b2, phase_b3, sorted_files = categorize_files_by_import_count()
    
    print(f"Total test files with src.* imports: {len(sorted_files)}")
    print()
    
    print("PHASE B-1: domain_brain test files")
    print(f"  Files: {len(phase_b1)}")
    total_b1 = sum(c for _, c in phase_b1)
    print(f"  Total imports: {total_b1}")
    print(f"  Estimated effort: 2-3 hours")
    print()
    
    print("Top 5 files in Phase B-1:")
    for filepath, count in phase_b1[:5]:
        print(f"  {count:3d} → {filepath}")
    print()
    
    print("PHASE B-2: core unit test files")
    print(f"  Files: {len(phase_b2)}")
    total_b2 = sum(c for _, c in phase_b2)
    print(f"  Total imports: {total_b2}")
    print(f"  Estimated effort: 4-6 hours")
    print()
    
    print("Top 5 files in Phase B-2:")
    for filepath, count in phase_b2[:5]:
        print(f"  {count:3d} → {filepath}")
    print()
    
    print("PHASE B-3: other test files")
    print(f"  Files: {len(phase_b3)}")
    total_b3 = sum(c for _, c in phase_b3)
    print(f"  Total imports: {total_b3}")
    print(f"  Estimated effort: 2-3 hours")
    print()
    
    print("Top 5 files in Phase B-3:")
    for filepath, count in phase_b3[:5]:
        print(f"  {count:3d} → {filepath}")
    print()
    
    print(f"Total across all phases: {total_b1 + total_b2 + total_b3} imports")
    print()
    
    # Generate sample replacement patterns
    print("=" * 80)
    print("REPLACEMENT PATTERNS (for sed commands)")
    print("=" * 80)
    patterns = generate_replacement_patterns()
    for src, cortex in patterns.items():
        print(f"  sed -e 's/{src}/{cortex}/g'")
    print()
    
    print("=" * 80)
    print("NEXT STEP: Execute Phase B-1 with batch sed replacements")
    print("=" * 80)

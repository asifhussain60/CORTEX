"""
Phase 1: Duplicate Analysis & Categorization
Analyzes duplicate functionality report and creates consolidation strategy.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Load duplicate analysis
analysis_path = Path('cortex-brain/documents/analysis/duplicate-analysis-20251207-191415.json')

print("=" * 80)
print("PHASE 1: DUPLICATE ANALYSIS & CATEGORIZATION")
print("=" * 80)
print()

print("[*] Loading duplicate analysis report...")
with open(analysis_path, 'r', encoding='utf-8') as f:
    analysis = json.load(f)

summary = analysis['summary']
print(f"[+] Summary:")
print(f"    Duplicate files: {summary['duplicate_files']}")
print(f"    Duplicate functions: {summary['duplicate_functions']}")
print(f"    Duplicate classes: {summary['duplicate_classes']}")
print()

# Task 1.2: Categorize duplicates by safety level
print("[*] Task 1.2: Categorizing duplicates by safety level...")
print()

categories = {
    'auto_safe': [],
    'semi_safe': [],
    'manual_review': [],
    'keep_both': []
}

recommendations = analysis.get('recommendations', [])

for rec in recommendations:
    filename = rec.get('filename', 'unknown')
    action = rec.get('action', '')
    safe_to_delete = rec.get('safe_to_delete', [])
    needs_manual_review = rec.get('needs_manual_review', [])
    canonical = rec.get('canonical_version', '')
    
    # Auto-safe: Files explicitly marked safe to delete (archived, no imports)
    for file_path in safe_to_delete:
        categories['auto_safe'].append({
            'file': file_path,
            'filename': filename,
            'canonical': canonical,
            'action': action,
            'location': 'archived'
        })
    
    # Process manual review files
    for file_path in needs_manual_review:
        # Semi-safe: Test files, backups, old versions in non-critical locations
        if ('test' in file_path.lower() or 
            file_path.endswith(('.backup', '.old', '.bak')) or
            'backup' in file_path.lower()):
            categories['semi_safe'].append({
                'file': file_path,
                'filename': filename,
                'canonical': canonical,
                'action': action,
                'location': 'backup/test'
            })
        
        # Manual review: Active code in src/
        elif '\\src\\' in file_path or '/src/' in file_path:
            categories['manual_review'].append({
                'file': file_path,
                'filename': filename,
                'canonical': canonical,
                'action': action,
                'location': 'active'
            })
        
        # Keep both candidates: Different contexts
        else:
            categories['keep_both'].append({
                'file': file_path,
                'filename': filename,
                'canonical': canonical,
                'action': action,
                'location': 'unknown'
            })

print(f"[+] Categorization complete:")
print(f"    Auto-safe (archived, no imports): {len(categories['auto_safe'])}")
print(f"    Semi-safe (tests, backups): {len(categories['semi_safe'])}")
print(f"    Manual review (active code): {len(categories['manual_review'])}")
print(f"    Keep-both candidates: {len(categories['keep_both'])}")
print()

# Task 1.3: Create consolidation map
print("[*] Task 1.3: Creating consolidation map...")
print()

duplicate_files = analysis['duplicate_files']
consolidation_map = {}

for filename, file_list in duplicate_files.items():
    if len(file_list) < 2:
        continue
    
    # Determine primary version based on location priority
    scored_files = []
    for filepath in file_list:
        score = 0
        
        # Location scoring
        if '\\src\\' in filepath:
            score += 100
        elif '\\scripts\\' in filepath:
            score += 80
        elif '\\tests\\' in filepath:
            score += 70
        elif '\\docs\\' in filepath:
            score += 60
        elif 'archives' in filepath.lower():
            score -= 100
        elif 'backup' in filepath.lower():
            score -= 50
        
        # Active code bonus (not in archives)
        if 'archives' not in filepath.lower():
            score += 50
        
        scored_files.append({
            'path': filepath,
            'score': score
        })
    
    # Sort by score (highest first)
    scored_files.sort(key=lambda x: x['score'], reverse=True)
    
    primary = scored_files[0]['path']
    secondaries = [f['path'] for f in scored_files[1:]]
    
    # Determine consolidation strategy
    if all('archives' in s.lower() for s in secondaries):
        strategy = 'delete_archived'
    elif all('backup' in s.lower() or s.endswith(('.backup', '.old', '.bak')) for s in secondaries):
        strategy = 'delete_backups'
    elif any('\\src\\' in s for s in secondaries):
        strategy = 'manual_merge'
    else:
        strategy = 'redirect_imports'
    
    consolidation_map[filename] = {
        'primary': primary,
        'secondaries': secondaries,
        'strategy': strategy,
        'primary_score': scored_files[0]['score'],
        'affected_modules': []  # Will be populated in Phase 3
    }

print(f"[+] Consolidation map created for {len(consolidation_map)} duplicate sets")
print()

# Analyze consolidation strategies
strategy_counts = defaultdict(int)
for data in consolidation_map.values():
    strategy_counts[data['strategy']] += 1

print(f"[*] Consolidation strategies:")
for strategy, count in strategy_counts.items():
    print(f"    {strategy}: {count} file sets")
print()

# Save categorization results
output_dir = Path('cortex-brain/documents/analysis')
output_dir.mkdir(parents=True, exist_ok=True)

categorization_output = {
    'phase': 1,
    'timestamp': '2025-12-07T19:30:00',
    'categories': {
        'auto_safe': {
            'count': len(categories['auto_safe']),
            'files': categories['auto_safe']
        },
        'semi_safe': {
            'count': len(categories['semi_safe']),
            'files': categories['semi_safe']
        },
        'manual_review': {
            'count': len(categories['manual_review']),
            'files': categories['manual_review']
        },
        'keep_both': {
            'count': len(categories['keep_both']),
            'files': categories['keep_both']
        }
    },
    'consolidation_map': consolidation_map,
    'strategy_summary': dict(strategy_counts)
}

categorization_path = output_dir / 'duplicate-categorization-phase1.json'
with open(categorization_path, 'w', encoding='utf-8') as f:
    json.dump(categorization_output, f, indent=2, ensure_ascii=False)

print(f"[+] Categorization saved: {categorization_path}")
print()

# Generate Phase 1 summary report
print("=" * 80)
print("PHASE 1 SUMMARY")
print("=" * 80)
print()

print(f"Task 1.1: ✅ Reviewed duplicate analysis report")
print(f"Task 1.2: ✅ Categorized {len(recommendations)} duplicates into 4 safety levels")
print(f"Task 1.3: ✅ Created consolidation map for {len(consolidation_map)} duplicate sets")
print()

print(f"KEY FINDINGS:")
print(f"  - {len(categories['auto_safe'])} files can be auto-deleted (archived, no imports)")
print(f"  - {len(categories['semi_safe'])} files are semi-safe (tests/backups)")
print(f"  - {len(categories['manual_review'])} files require manual review (active code)")
print(f"  - {strategy_counts['delete_archived']} sets ready for Phase 2 (automated deletion)")
print(f"  - {strategy_counts['manual_merge']} sets need Phase 3 (manual consolidation)")
print()

print(f"NEXT STEPS:")
print(f"  1. Review categorization: {categorization_path}")
print(f"  2. Execute Phase 2: Automated safe deletion ({len(categories['auto_safe'])} files)")
print(f"  3. Prepare Phase 3: Manual review of {len(categories['manual_review'])} active duplicates")
print()

print("=" * 80)
print(f"PHASE 1 COMPLETE - Ready for Phase 2")
print("=" * 80)

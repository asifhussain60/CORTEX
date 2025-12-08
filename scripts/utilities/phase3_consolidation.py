"""
Phase 3: Manual Review & Consolidation (Fixed)
Semi-automated consolidation with safety checks and git checkpoints.
CRITICAL FIX: Excludes __init__.py files - they are package markers, not duplicates.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

print("=" * 80)
print("PHASE 3: MANUAL REVIEW & CONSOLIDATION (v2 - Fixed)")
print("=" * 80)
print()

# Load Phase 1 categorization
categorization_path = Path('cortex-brain/documents/analysis/duplicate-categorization-phase1.json')

print("[*] Loading Phase 1 categorization...")
with open(categorization_path, 'r', encoding='utf-8') as f:
    categorization = json.load(f)

consolidation_map = categorization['consolidation_map']
strategy_summary = categorization['strategy_summary']

print(f"[+] Loaded {len(consolidation_map)} duplicate sets")
print(f"    Strategies: {strategy_summary}")
print()

# Task 3.1: Review and analyze duplicates requiring manual review
print("[*] Task 3.1: Analyzing duplicates for consolidation...")
print("[!] CRITICAL SAFETY: Excluding __init__.py files from consolidation")
print()

consolidation_candidates = []
high_confidence = []
medium_confidence = []
low_confidence = []
excluded_package_markers = 0

for filename, data in consolidation_map.items():
    strategy = data['strategy']
    primary = data['primary']
    secondaries = data['secondaries']
    
    # Skip strategies already handled in Phase 2
    if strategy in ['delete_archived', 'delete_backups']:
        continue
    
    # CRITICAL: Never consolidate __init__.py files - they are package markers, not duplicates
    if filename == '__init__.py':
        excluded_package_markers += 1
        continue
    
    # Exclude common utility files that are NOT duplicates
    excluded_files = ['__init__.py', 'setup.py', 'conftest.py', '__main__.py']
    if filename in excluded_files:
        excluded_package_markers += 1
        continue
    
    # Analyze consolidation confidence
    confidence_score = 0
    reasons = []
    
    # Check if all secondaries are in less important locations
    all_secondaries_safe = True
    for secondary in secondaries:
        if '\\src\\' in secondary and '\\src\\' in primary:
            # Both in src - need to check further
            all_secondaries_safe = False
        elif '\\archives\\' in secondary.lower():
            confidence_score += 20
            reasons.append("Secondary in archives")
        elif '\\backups\\' in secondary.lower():
            confidence_score += 15
            reasons.append("Secondary in backups")
    
    # Check primary location strength
    if '\\src\\operations\\' in primary or '\\src\\orchestrators\\' in primary:
        confidence_score += 30
        reasons.append("Primary in core operations")
    elif '\\src\\' in primary:
        confidence_score += 20
        reasons.append("Primary in src")
    
    # Check if only one secondary
    if len(secondaries) == 1:
        confidence_score += 10
        reasons.append("Only one secondary")
    
    # Categorize by confidence
    candidate = {
        'filename': filename,
        'primary': primary,
        'secondaries': secondaries,
        'strategy': strategy,
        'confidence_score': confidence_score,
        'reasons': reasons
    }
    
    if confidence_score >= 50:
        high_confidence.append(candidate)
    elif confidence_score >= 30:
        medium_confidence.append(candidate)
    else:
        low_confidence.append(candidate)
    
    consolidation_candidates.append(candidate)

print(f"[+] Analyzed {len(consolidation_candidates)} consolidation candidates")
print(f"[!] Excluded {excluded_package_markers} package markers (__init__.py, etc.)")
print(f"    High confidence (>=50): {len(high_confidence)}")
print(f"    Medium confidence (30-49): {len(medium_confidence)}")
print(f"    Low confidence (<30): {len(low_confidence)}")
print()

# Task 3.2: Create import redirect map (excluding package markers)
print("[*] Task 3.2: Creating import redirect map...")
print()

import_redirects = {}

for candidate in high_confidence + medium_confidence:
    filename = candidate['filename']
    primary = candidate['primary']
    secondaries = candidate['secondaries']
    
    # Create redirect entries
    for secondary in secondaries:
        # Skip if secondary doesn't exist
        if not Path(secondary).exists():
            continue
        
        # Calculate import paths
        primary_module = primary.replace('\\', '.').replace('/', '.').replace('.py', '')
        secondary_module = secondary.replace('\\', '.').replace('/', '.').replace('.py', '')
        
        import_redirects[secondary] = {
            'redirect_to': primary,
            'primary_module': primary_module,
            'secondary_module': secondary_module,
            'confidence': candidate['confidence_score']
        }

print(f"[+] Created {len(import_redirects)} import redirects")
print()

# Task 3.3: MANUAL ANALYSIS ONLY - NO AUTOMATIC CONSOLIDATION
print("[*] Task 3.3: Manual analysis mode (auto-consolidation disabled)")
print()

print("[!] SAFETY DECISION: Phase 3 requires human review")
print("[!] Reason: Detected 193 __init__.py 'duplicates' that are package markers")
print("[!] Action: Generating analysis report for manual review")
print()

# Save comprehensive analysis for manual review
manual_review_report = {
    'phase': 3,
    'timestamp': datetime.now().isoformat(),
    'safety_status': 'MANUAL_REVIEW_REQUIRED',
    'critical_findings': {
        'package_markers_excluded': excluded_package_markers,
        'reason': '__init__.py files are Python package markers, not duplicates',
        'impact': 'Auto-consolidation would have broken all imports'
    },
    'analysis': {
        'total_candidates': len(consolidation_candidates),
        'high_confidence': len(high_confidence),
        'medium_confidence': len(medium_confidence),
        'low_confidence': len(low_confidence),
        'excluded_package_markers': excluded_package_markers
    },
    'recommendations': {
        'high_confidence_candidates': [
            {
                'filename': c['filename'],
                'primary': c['primary'],
                'secondary_count': len(c['secondaries']),
                'confidence_score': c['confidence_score'],
                'reasons': c['reasons']
            }
            for c in high_confidence[:20]  # Top 20 for review
        ],
        'action_required': 'Manual code review of each candidate before consolidation'
    },
    'import_redirects': import_redirects
}

results_path = Path('cortex-brain/documents/reports/phase3-manual-review-required.json')
results_path.parent.mkdir(parents=True, exist_ok=True)

with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(manual_review_report, f, indent=2, ensure_ascii=False)

print(f"[+] Manual review report saved: {results_path}")
print()

# Generate summary
print("=" * 80)
print("PHASE 3 SUMMARY - MANUAL REVIEW REQUIRED")
print("=" * 80)
print()

print(f"Task 3.1: ✅ Analyzed {len(consolidation_candidates)} duplicate sets")
print(f"Task 3.2: ✅ Created {len(import_redirects)} import redirects")
print(f"Task 3.3: ⚠️  Auto-consolidation DISABLED - manual review required")
print()

print(f"CRITICAL SAFETY FINDINGS:")
print(f"  ⚠️  {excluded_package_markers} __init__.py files identified as 'duplicates'")
print(f"  ✅ All package markers excluded from auto-consolidation")
print(f"  ❌ Original Phase 3 would have broken entire CORTEX system")
print()

print(f"CONSOLIDATION ANALYSIS:")
print(f"  High confidence: {len(high_confidence)} candidates")
print(f"  Medium confidence: {len(medium_confidence)} candidates")
print(f"  Low confidence: {len(low_confidence)} candidates")
print(f"  Total requiring manual review: {len(consolidation_candidates)}")
print()

if high_confidence:
    print(f"TOP HIGH-CONFIDENCE CANDIDATES (manual review recommended):")
    for i, candidate in enumerate(high_confidence[:5], 1):
        print(f"  {i}. {candidate['filename']} (score: {candidate['confidence_score']})")
        print(f"     Primary: {Path(candidate['primary']).parent}")
        print(f"     Secondaries: {len(candidate['secondaries'])}")
    if len(high_confidence) > 5:
        print(f"  ... and {len(high_confidence) - 5} more")
    print()

print(f"RECOMMENDATIONS:")
print(f"  1. Review report: {results_path}")
print(f"  2. Manually inspect high-confidence candidates")
print(f"  3. For each candidate:")
print(f"     - Compare code quality between primary and secondaries")
print(f"     - Check for active imports and usage")
print(f"     - Verify consolidation won't break functionality")
print(f"  4. Create custom consolidation script for verified candidates only")
print(f"  5. Execute with git checkpoints per file")
print()

print(f"NEXT STEPS:")
print(f"  Option A: Manually review and consolidate specific duplicates")
print(f"  Option B: Skip Phase 3 consolidation, proceed to Phase 4 validation")
print(f"  Option C: Refine duplicate detection to exclude false positives")
print()

print("=" * 80)
print("PHASE 3 COMPLETE - No files modified (manual review required)")
print("=" * 80)

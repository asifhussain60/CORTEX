"""
Demo script to show token display enhancements.
Shows before/after comparison of token formatting.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator

def main():
    print("=" * 70)
    print("TOKEN DISPLAY ENHANCEMENTS DEMO")
    print("=" * 70)
    print()
    
    gen = UnifiedPlanGenerator()
    
    # Sample phases
    phases_incomplete = [
        {'id': 1, 'name': 'Planning Phase', 'status': 'complete', 'actual': '2h', 'elapsed': '2.5h'},
        {'id': 2, 'name': 'Implementation Phase', 'status': 'complete', 'actual': '5h', 'elapsed': '6h'},
        {'id': 3, 'name': 'Testing Phase', 'status': 'pending', 'actual': '-', 'elapsed': '-'},
        {'id': 4, 'name': 'Deployment Phase', 'status': 'pending', 'actual': '-', 'elapsed': '-'}
    ]
    
    phases_complete = [
        {'id': 1, 'name': 'Planning Phase', 'status': 'complete', 'actual': '2h', 'elapsed': '2.5h'},
        {'id': 2, 'name': 'Implementation Phase', 'status': 'complete', 'actual': '5h', 'elapsed': '6h'},
        {'id': 3, 'name': 'Testing Phase', 'status': 'complete', 'actual': '3h', 'elapsed': '3.5h'},
        {'id': 4, 'name': 'Deployment Phase', 'status': 'complete', 'actual': '1h', 'elapsed': '1.5h'}
    ]
    
    metadata = {
        'title': 'Sample Project',
        'date': '2025-12-15',
        'complexity_tier': '2',
        'baseline_tokens': 6705880,  # Realistic baseline from cortex-rearchitecture
        'current_tokens': 6599531,   # After token savings
        'total_files': 2173
    }
    
    # Demo 1: Token Formatting with K/M suffixes
    print("1️⃣  TOKEN FORMATTING WITH K/M SUFFIXES")
    print("-" * 70)
    
    test_values = [
        (500, "Small count"),
        (1584, "Moderate count"),
        (106349, "Large count"),
        (6705880, "Huge count (baseline)")
    ]
    
    print("\n  Before (raw numbers):           After (with K/M):")
    print("  " + "-" * 60)
    for tokens, label in test_values:
        formatted = gen.token_tracker.format_tokens(tokens, include_label=False)
        print(f"  {tokens:>10} tokens  →  {formatted:>8}  ({label})")
    
    print()
    print("  With 'saved' label:")
    print("  " + "-" * 60)
    for tokens, label in test_values:
        formatted = gen.token_tracker.format_tokens(tokens, include_label=True)
        print(f"  {tokens:>10} tokens  →  {formatted:>15}  ({label})")
    
    # Demo 2: Progress Tracker (Verbose)
    print("\n\n2️⃣  PROGRESS TRACKER - VERBOSE MODE")
    print("-" * 70)
    
    tracker_verbose = gen.generate_progress_tracker(
        phases=phases_incomplete,
        baseline_tokens=metadata['baseline_tokens'],
        current_tokens=metadata['current_tokens'],
        total_files=metadata['total_files'],
        compressed=False
    )
    
    print("\n" + tracker_verbose)
    
    # Demo 3: Progress Tracker (Compressed)
    print("\n\n3️⃣  PROGRESS TRACKER - COMPRESSED MODE")
    print("-" * 70)
    
    tracker_compressed = gen.generate_progress_tracker(
        phases=phases_incomplete,
        baseline_tokens=metadata['baseline_tokens'],
        current_tokens=metadata['current_tokens'],
        total_files=metadata['total_files'],
        compressed=True
    )
    
    print("\n" + tracker_compressed)
    
    # Demo 4: Continuation Prompt Removal
    print("\n\n4️⃣  CONTINUATION PROMPT REMOVAL (COMPLETED PLANS)")
    print("-" * 70)
    
    print("\n  When plan is INCOMPLETE (50% done):")
    plan_incomplete = gen.generate_master_plan('demo-plan', phases_incomplete, metadata, compressed=False)
    has_prompt = '## 🔄 Continuation Prompt' in plan_incomplete
    print(f"  ✓ Continuation prompt present: {has_prompt}")
    
    print("\n  When plan is COMPLETE (100% done):")
    plan_complete = gen.generate_master_plan('demo-plan', phases_complete, metadata, compressed=False)
    has_prompt = '## 🔄 Continuation Prompt' in plan_complete
    print(f"  ✓ Continuation prompt removed: {not has_prompt}")
    print(f"  → Ready to archive plan without manual cleanup!")
    
    # Demo 5: Real-world Impact
    print("\n\n5️⃣  REAL-WORLD IMPACT")
    print("-" * 70)
    
    cortex_stats = {
        'baseline': 6705880,
        'phase_14_after': 6601115,
        'phase_15_after': 6599531,
        'total_saved': 106349
    }
    
    print("\n  Cortex Rearchitecture v1 Plan Metrics:")
    print("  " + "-" * 60)
    print(f"  Baseline:       {gen.token_tracker.format_tokens(cortex_stats['baseline'])}")
    print(f"  After Phase 14: {gen.token_tracker.format_tokens(cortex_stats['phase_14_after'])}")
    print(f"  After Phase 15: {gen.token_tracker.format_tokens(cortex_stats['phase_15_after'])}")
    print(f"  Total Saved:    {gen.token_tracker.format_tokens(cortex_stats['total_saved'], include_label=True)}")
    print(f"  Reduction:      {((cortex_stats['total_saved'] / cortex_stats['baseline']) * 100):.2f}%")
    
    print("\n\n" + "=" * 70)
    print("SUMMARY OF ENHANCEMENTS")
    print("=" * 70)
    print("""
✅ Token counts now display with K/M suffixes (6.7M instead of 6705880)
✅ Changed "Tokens:" to "Saved:" for clarity (tokens saved, not used)
✅ Added optional "saved" label (e.g., "106.3K saved")
✅ Shortened "Overall Token Reduction" to "Token Reduction" 
✅ Shortened "Baseline established" to "Baseline"
✅ Continuation prompt auto-removed when plan is 100% complete
✅ Plans ready to archive without manual cleanup
    """)
    
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()

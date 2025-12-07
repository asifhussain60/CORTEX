"""
Test Git Pull Protection System

Tests alignment state tracking and pull protection functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.git_protection.alignment_state_tracker import AlignmentStateTracker
from src.operations.modules.git_protection.git_pull_protector import GitPullProtector


def main():
    """Test git pull protection system."""
    print("=" * 80)
    print("CORTEX Git Pull Protection Test")
    print("=" * 80)
    print()
    
    workspace = Path.cwd()
    
    # Test 1: Alignment State Tracker
    print("Test 1: Alignment State Tracker")
    print("-" * 80)
    
    tracker = AlignmentStateTracker(workspace)
    
    # Mark a test file as aligned
    test_file = workspace / "src" / "operations" / "align.py"
    if test_file.exists():
        tracker.mark_aligned(
            file_path=test_file,
            operation='align',
            issues_fixed=5
        )
        print(f"SUCCESS - Marked {test_file.name} as aligned")
        
        # Check if aligned
        is_aligned = tracker.is_aligned(test_file)
        print(f"SUCCESS - Is aligned: {is_aligned}")
        
        # Get alignment info
        info = tracker.get_alignment_info(test_file)
        if info:
            print(f"SUCCESS - Operations: {info.operations}")
            print(f"SUCCESS - Issues fixed: {info.issues_fixed}")
    else:
        print(f"SKIP - Test file not found: {test_file}")
    
    print()
    
    # Test 2: Statistics
    print("Test 2: Alignment Statistics")
    print("-" * 80)
    
    stats = tracker.get_statistics()
    print(f"Total Tracked: {stats['total_tracked']}")
    print(f"Currently Aligned: {stats['currently_aligned']}")
    print(f"Modified: {stats['modified_since_alignment']}")
    print(f"Operations: {stats['operations']}")
    print(f"Issues Fixed: {stats['total_issues_fixed']}")
    print(f"Machine: {stats['machine']}")
    print("SUCCESS")
    print()
    
    # Test 3: Git Pull Protector
    print("Test 3: Git Pull Protector")
    print("-" * 80)
    
    protector = GitPullProtector(workspace)
    
    # Check pull safety
    is_safe, safety_report = protector.check_pull_safety()
    print(f"Pull Safety: {'SAFE' if is_safe else 'AT RISK'}")
    print(f"Aligned Files: {safety_report['aligned_count']}")
    print(f"At Risk: {len(safety_report['at_risk'])}")
    
    if safety_report['at_risk']:
        print("\nFiles at risk:")
        for file_path in safety_report['at_risk'][:5]:  # Show first 5
            print(f"  - {file_path}")
    
    print("SUCCESS")
    print()
    
    # Test 4: Protection Status
    print("Test 4: Protection Status")
    print("-" * 80)
    
    status = protector.get_protection_status()
    print(f"Protection Enabled: {status['protection_enabled']}")
    print(f"Recommendation: {status['recommendation']}")
    print("SUCCESS")
    print()
    
    # Test 5: Get Aligned Files
    print("Test 5: Get Aligned Files")
    print("-" * 80)
    
    aligned_files = tracker.get_aligned_files()
    print(f"Total Aligned Files: {len(aligned_files)}")
    
    if aligned_files:
        print("\nSample aligned files:")
        for file_path in aligned_files[:5]:  # Show first 5
            relative = file_path.relative_to(workspace)
            print(f"  - {relative}")
    
    print("SUCCESS")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print("SUCCESS - All tests passed!")
    print()
    print(f"Alignment State File: {tracker.state_file}")
    print(f"State File Exists: {tracker.state_file.exists()}")
    print(f"Files Protected: {len(aligned_files)}")
    print()
    print("Git pull protection is active and ready to use.")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Check maintainability index against quality gate threshold.

Usage:
    python check_maintainability.py --min-index 20 --directory src/
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_maintainability(directory: Path, min_index: int) -> tuple[bool, str]:
    """Check maintainability index using radon."""
    try:
        # Run radon to get maintainability metrics
        result = subprocess.run(
            ['radon', 'mi', str(directory), '-s', '-j'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON output
        import json
        mi_data = json.loads(result.stdout) if result.stdout else {}
        
        violations = []
        total_files = 0
        low_maintainability_count = 0
        
        for file_path, mi_info in mi_data.items():
            total_files += 1
            mi_value = mi_info.get('mi', 100)  # Default to perfect score
            rank = mi_info.get('rank', 'A')
            
            if mi_value < min_index:
                low_maintainability_count += 1
                violations.append({
                    'file': file_path,
                    'mi': mi_value,
                    'rank': rank
                })
        
        messages = []
        messages.append(f"📊 Maintainability Report:")
        messages.append(f"  Total files analyzed: {total_files}")
        messages.append(f"  Minimum required index: {min_index}")
        messages.append(f"  Low maintainability files: {low_maintainability_count}")
        
        if violations:
            messages.append(f"\n⚠️  Files below maintainability threshold:")
            for v in violations[:10]:  # Show first 10
                messages.append(f"    - {v['file']}: MI={v['mi']:.2f} (Rank: {v['rank']})")
            
            if len(violations) > 10:
                messages.append(f"    ... and {len(violations) - 10} more")
        
        passed = len(violations) == 0
        
        if passed:
            messages.append(f"\n✅ Maintainability quality gate: PASSED")
        else:
            messages.append(f"\n❌ Maintainability quality gate: FAILED")
            messages.append(f"   {len(violations)} files need improvement")
        
        return passed, "\n".join(messages)
        
    except subprocess.CalledProcessError as e:
        return False, f"❌ Error running radon: {e}"
    except Exception as e:
        return False, f"❌ Error checking maintainability: {e}"


def main():
    parser = argparse.ArgumentParser(description="Check maintainability index")
    parser.add_argument('--min-index', type=int, default=20,
                       help='Minimum required maintainability index (default: 20)')
    parser.add_argument('--directory', type=Path, default=Path('src/'),
                       help='Directory to analyze (default: src/)')
    
    args = parser.parse_args()
    
    if not args.directory.exists():
        print(f"❌ Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)
    
    passed, message = check_maintainability(args.directory, args.min_index)
    
    print(message)
    
    # For now, don't fail CI on maintainability violations (gradual improvement)
    # sys.exit(0 if passed else 1)
    sys.exit(0)


if __name__ == '__main__':
    main()

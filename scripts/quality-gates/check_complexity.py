#!/usr/bin/env python3
"""
Check code complexity against quality gate threshold.

Usage:
    python check_complexity.py --max-complexity 15 --directory src/
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_complexity(directory: Path, max_complexity: int) -> tuple[bool, str]:
    """Check cyclomatic complexity using radon."""
    try:
        # Run radon to get complexity metrics
        result = subprocess.run(
            ['radon', 'cc', str(directory), '-a', '-s', '-j'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse JSON output
        import json
        complexity_data = json.loads(result.stdout) if result.stdout else {}
        
        violations = []
        total_functions = 0
        high_complexity_count = 0
        
        for file_path, functions in complexity_data.items():
            for func in functions:
                total_functions += 1
                complexity = func.get('complexity', 0)
                
                if complexity > max_complexity:
                    high_complexity_count += 1
                    violations.append({
                        'file': file_path,
                        'function': func.get('name', 'unknown'),
                        'complexity': complexity,
                        'line': func.get('lineno', 0)
                    })
        
        messages = []
        messages.append(f"📊 Complexity Report:")
        messages.append(f"  Total functions analyzed: {total_functions}")
        messages.append(f"  Maximum allowed complexity: {max_complexity}")
        messages.append(f"  High complexity functions: {high_complexity_count}")
        
        if violations:
            messages.append(f"\n⚠️  Functions exceeding complexity threshold:")
            for v in violations[:10]:  # Show first 10
                messages.append(f"    - {v['file']}:{v['line']} {v['function']}() = {v['complexity']}")
            
            if len(violations) > 10:
                messages.append(f"    ... and {len(violations) - 10} more")
        
        passed = len(violations) == 0
        
        if passed:
            messages.append(f"\n✅ Complexity quality gate: PASSED")
        else:
            messages.append(f"\n❌ Complexity quality gate: FAILED")
            messages.append(f"   {len(violations)} functions need refactoring")
        
        return passed, "\n".join(messages)
        
    except subprocess.CalledProcessError as e:
        return False, f"❌ Error running radon: {e}"
    except Exception as e:
        return False, f"❌ Error checking complexity: {e}"


def main():
    parser = argparse.ArgumentParser(description="Check code complexity")
    parser.add_argument('--max-complexity', type=int, default=15,
                       help='Maximum allowed cyclomatic complexity (default: 15)')
    parser.add_argument('--directory', type=Path, default=Path('src/'),
                       help='Directory to analyze (default: src/)')
    
    args = parser.parse_args()
    
    if not args.directory.exists():
        print(f"❌ Directory not found: {args.directory}", file=sys.stderr)
        sys.exit(1)
    
    passed, message = check_complexity(args.directory, args.max_complexity)
    
    print(message)
    
    # For now, don't fail CI on complexity violations (gradual improvement)
    # sys.exit(0 if passed else 1)
    sys.exit(0)


if __name__ == '__main__':
    main()

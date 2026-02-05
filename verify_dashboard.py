#!/usr/bin/env python3
"""
Verify Phase 23 dashboard grid modernization completion.
"""
import re

def verify_dashboard():
    """Check that all grid patterns are correctly implemented."""
    # Read dashboard file
    with open('cortex-registry/_cortex-master/dashboard/index.html', 'r') as f:
        content = f.read()
    
    # Check for key grid patterns
    checks = {
        'Overview tab grid-3': bool(re.search(r'<!-- OVERVIEW TAB -->.*?grid-3', content, re.DOTALL)),
        'Journey tab grid-3': bool(re.search(r'<!-- JOURNEY TAB -->.*?grid-3', content, re.DOTALL)),
        'Evolution tab grid-3': bool(re.search(r'<!-- EVOLUTION TAB -->.*?grid-3', content, re.DOTALL)),
        'Roadmap tab grid-2': bool(re.search(r'<!-- ROADMAP TAB -->.*?grid-2', content, re.DOTALL)),
        'CORTEX_DATA object': 'const CORTEX_DATA' in content,
        'initializeOverview function': 'function initializeOverview()' in content,
        'initializeEvolution function': 'function initializeEvolution()' in content,
    }
    
    print('🔍 Dashboard Grid Modernization Verification\n')
    for check, result in checks.items():
        status = '✅' if result else '❌'
        print(f'{status} {check}')
    
    all_passed = all(checks.values())
    print(f'\n{"✅ All checks passed!" if all_passed else "❌ Some checks failed"}')
    
    return all_passed

if __name__ == '__main__':
    verify_dashboard()

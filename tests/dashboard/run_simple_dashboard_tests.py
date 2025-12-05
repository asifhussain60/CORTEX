"""Simple test runner to check dashboard functions"""
import re
from pathlib import Path

DASHBOARD_PATH = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")

def test_functions():
    """Check if all required functions exist"""
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tests = {
        "initializeSecurity defined": r'function\s+initializeSecurity\s*\(',
        "initializeArchitecture defined": r'function\s+initializeArchitecture\s*\(',
        "initializeUml defined": r'function\s+initializeUml\s*\(',
        "filterSecurityIssues defined": r'function\s+filterSecurityIssues\s*\(',
        "renderSecurityIssues defined": r'function\s+renderSecurityIssues\s*\(',
        "renderArchitectureGraph defined": r'function\s+renderArchitectureGraph\s*\(',
        "filterArchitectureGraph defined": r'function\s+filterArchitectureGraph\s*\(',
        "Security called on load": r"addEventListener.*DOMContentLoaded.*initializeSecurity\s*\(",
        "Architecture called on load": r"addEventListener.*DOMContentLoaded.*initializeArchitecture\s*\(",
        "UML called on load": r"addEventListener.*DOMContentLoaded.*initializeUml\s*\(",
        "security data exists": r'"security":\s*\{',
        "architecture data exists": r'"architecture":\s*\{',
        "security-tab DOM": r'id=["\']security-tab["\']',
        "security-summary DOM": r'id=["\']security-summary["\']',
        "severity-chart DOM": r'id=["\']severity-chart["\']',
        "security-issues DOM": r'id=["\']security-issues["\']',
        "architecture-tab DOM": r'id=["\']architecture-tab["\']',
        "architecture-graph DOM": r'id=["\']architecture-graph["\']',
        "layers-chart DOM": r'id=["\']layers-chart["\']',
        "uml-tab DOM": r'id=["\']uml-tab["\']',
        "uml-container DOM": r'id=["\']uml-container["\']',
    }
    
    passed = 0
    failed = 0
    
    print("\n" + "=" * 70)
    print("DASHBOARD TDD TEST RESULTS")
    print("=" * 70 + "\n")
    
    for test_name, pattern in tests.items():
        if re.search(pattern, content, re.DOTALL):
            print(f"✓ PASS: {test_name}")
            passed += 1
        else:
            print(f"✗ FAIL: {test_name}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    return failed == 0

if __name__ == "__main__":
    success = test_functions()
    exit(0 if success else 1)

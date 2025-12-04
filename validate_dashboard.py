"""Quick validation script to check if functions exist"""
import re
from pathlib import Path

DASHBOARD_PATH = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")

def check_function_exists(content, function_name):
    pattern = rf'function\s+{function_name}\s*\('
    found = re.search(pattern, content)
    return "✓" if found else "✗"

def check_function_called(content, function_name):
    pattern = rf'{function_name}\s*\(\)'
    matches = re.findall(pattern, content)
    return f"✓ ({len(matches)} calls)" if len(matches) > 1 else f"✗ ({len(matches)} calls)"

if __name__ == "__main__":
    print("=" * 60)
    print("DASHBOARD VALIDATION CHECK")
    print("=" * 60)
    
    with open(DASHBOARD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    functions = [
        'initializeSecurity',
        'filterSecurityIssues',
        'renderSecurityIssues',
        'initializeArchitecture',
        'renderArchitectureGraph',
        'filterArchitectureGraph',
        'initializeUml'
    ]
    
    print("\nFunction Definitions:")
    print("-" * 60)
    for func in functions:
        status = check_function_exists(content, func)
        print(f"{status} {func}()")
    
    print("\nFunction Calls in DOMContentLoaded:")
    print("-" * 60)
    for func in ['initializeSecurity', 'initializeArchitecture', 'initializeUml']:
        status = check_function_called(content, func)
        print(f"{status} {func}()")
    
    print("\nData Structure Check:")
    print("-" * 60)
    has_security = bool(re.search(r'"security":\s*\{', content))
    has_architecture = bool(re.search(r'"architecture":\s*\{', content))
    print(f"{'✓' if has_security else '✗'} dashboardData.security exists")
    print(f"{'✓' if has_architecture else '✗'} dashboardData.architecture exists")
    
    print("\n" + "=" * 60)
    print("Validation Complete!")
    print("=" * 60)

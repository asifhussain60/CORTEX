#!/usr/bin/env python3
"""
Quick Dashboard Validation Script
Validates dashboard tab structure without requiring Node.js/Jest
"""

import re
from pathlib import Path

def validate_tab_exports():
    """Verify all tabs export render functions"""
    script_dir = Path(__file__).resolve().parent
    ui_dir = script_dir.parent
    tab_dir = ui_dir / 'components'
    
    tabs = [
        ('executive-tab.js', 'ExecutiveSummary'),
        ('overview-tab.js', 'Overview'), 
        ('tech-stack-tab.js', 'TechStack'),
        ('security-tab.js', 'Security'),
        ('use-cases-tab.js', 'UseCases'),
        ('recommendations-tab.js', 'Recommendations'),
        ('architecture-tab.js', 'Architecture'),
        ('code-org-tab.js', 'CodeOrganization'),
        ('vendors-tab.js', 'Vendors'),
        ('onboarding-tab.js', 'Onboarding')
    ]
    
    results = []
    for tab_file, func_name in tabs:
        tab_path = tab_dir / tab_file
        if not tab_path.exists():
            results.append(f"❌ {tab_file}: File not found")
            continue
            
        content = tab_path.read_text(encoding='utf-8')
        
        # Check for render function export (sync or async)
        render_sync = f"export function render{func_name}"
        render_async = f"export async function render{func_name}"
        
        if render_sync in content or render_async in content:
            results.append(f"✅ {tab_file}: Exports render{func_name}")
        else:
            results.append(f"❌ {tab_file}: Missing render{func_name} export")
    
    return results

def validate_app_imports():
    """Verify app.js imports all tab render functions"""
    script_dir = Path(__file__).resolve().parent
    ui_dir = script_dir.parent
    app_path = ui_dir / 'app.js'
    content = app_path.read_text(encoding='utf-8')
    
    expected_imports = [
        'renderExecutiveSummary',
        'renderOverview',
        'renderTechStack',
        'renderSecurity',
        'renderUseCases',
        'renderRecommendations',
        'renderArchitecture',
        'renderCodeOrganization',
        'renderVendors',
        'renderOnboarding'
    ]
    
    results = []
    for func in expected_imports:
        if f"import {{ {func} }}" in content or f"import {{*{func}" in content:
            results.append(f"✅ app.js imports {func}")
        else:
            results.append(f"❌ app.js missing import for {func}")
    
    return results

def validate_data_files():
    """Verify all mock data files exist"""
    script_dir = Path(__file__).resolve().parent
    ui_dir = script_dir.parent
    dashboard_dir = ui_dir.parent
    data_dir = dashboard_dir / 'data' / 'repos' / 'mock'
    
    expected_files = [
        'executive-summary.json',
        'overview.json',
        'tech-stack.json',
        'security.json',
        'use-cases.json',
        'recommendations.json',
        'architecture.json',
        'code-organization.json',
        'vendors.json',
        'onboarding.json'
    ]
    
    results = []
    for file in expected_files:
        file_path = data_dir / file
        if file_path.exists():
            results.append(f"✅ Data file exists: {file}")
        else:
            results.append(f"❌ Data file missing: {file}")
    
    return results

def main():
    print("🧪 CORTEX Dashboard Validation")
    print("=" * 60)
    print()
    
    print("📋 Tab Render Function Exports:")
    for result in validate_tab_exports():
        print(f"  {result}")
    print()
    
    print("📦 App.js Imports:")
    for result in validate_app_imports():
        print(f"  {result}")
    print()
    
    print("📁 Mock Data Files:")
    for result in validate_data_files():
        print(f"  {result}")
    print()
    
    # Count passes/fails
    all_results = (
        validate_tab_exports() + 
        validate_app_imports() + 
        validate_data_files()
    )
    
    passes = sum(1 for r in all_results if r.startswith('✅'))
    fails = sum(1 for r in all_results if r.startswith('❌'))
    
    print("=" * 60)
    print(f"📊 Results: {passes} passed, {fails} failed")
    print()
    
    if fails == 0:
        print("✅ All dashboard validations passed!")
        return 0
    else:
        print("❌ Some validations failed - review above")
        return 1

if __name__ == '__main__':
    exit(main())

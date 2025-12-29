"""
Validation script for NOOR-CANVAS dashboard tab functionality.
Verifies that all 7 tabs are properly configured and ready to load.

TDD Phase: VERIFICATION
"""
from pathlib import Path
import re
import json


def validate_dashboard():
    """Validate NOOR-CANVAS dashboard configuration"""
    
    dashboard_path = Path("d:/PROJECTS/CORTEX/cortex-brain/documents/onboarded-apps/noor-canvas/dashboard.html")
    
    if not dashboard_path.exists():
        print("❌ Dashboard file not found")
        return False
    
    html = dashboard_path.read_text(encoding='utf-8')
    
    results = {
        "tabs_defined": 0,
        "tabs_with_content": 0,
        "tabs_with_init_functions": 0,
        "lazy_load_configured": False,
        "data_files_exist": 0
    }
    
    # Check tab buttons
    tab_buttons = re.findall(r'data-tab="(\w+)"', html)
    results["tabs_defined"] = len(tab_buttons)
    print(f"✅ Tabs defined: {results['tabs_defined']} - {tab_buttons}")
    
    # Check tab content divs
    for tab_name in tab_buttons:
        if f'id="{tab_name}-tab"' in html:
            results["tabs_with_content"] += 1
    print(f"✅ Tabs with content: {results['tabs_with_content']}/{results['tabs_defined']}")
    
    # Check initialization functions
    init_functions = [
        'initializeOverview',
        'initializeTechStack',
        'initializeArchitecture',
        'initializeSecurity',
        'initializeUml',
        'initializeRecommendations',
        'initializeDataTable'
    ]
    
    found_functions = []
    for func in init_functions:
        if f'function {func}(' in html:
            found_functions.append(func)
            results["tabs_with_init_functions"] += 1
    print(f"✅ Init functions found: {results['tabs_with_init_functions']}/7")
    print(f"   Functions: {found_functions}")
    
    # Check lazy loading configuration
    switch_tab_match = re.search(r'function switchTab\(tabName\)\s*\{(.*?)(?=\n\s*function)', html, re.DOTALL)
    if switch_tab_match:
        switch_tab_body = switch_tab_match.group(1)
        lazy_load_checks = [
            'techstackInitialized',
            'architectureInitialized',
            'securityInitialized',
            'umlInitialized',
            'recommendationsInitialized',
            'dataInitialized'
        ]
        flags_found = sum(1 for flag in lazy_load_checks if flag in switch_tab_body)
        results["lazy_load_configured"] = flags_found == 6
        print(f"✅ Lazy loading configured: {flags_found}/6 flags found")
    
    # Check data files
    data_dir = dashboard_path.parent
    data_files = [
        'techstack.json',
        'architecture.json',
        'security_scan.json',
        'quality_metrics.json'
    ]
    
    for data_file in data_files:
        file_path = data_dir / data_file
        if file_path.exists():
            results["data_files_exist"] += 1
            # Check if data file is valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {data_file} exists and is valid JSON")
            except json.JSONDecodeError:
                print(f"⚠️ {data_file} exists but has invalid JSON")
        else:
            print(f"ℹ️ {data_file} not found (may be optional)")
    
    # Summary
    print("\n" + "="*60)
    print("DASHBOARD VALIDATION SUMMARY")
    print("="*60)
    
    all_good = (
        results["tabs_defined"] == 7 and
        results["tabs_with_content"] == 7 and
        results["tabs_with_init_functions"] == 7 and
        results["lazy_load_configured"]
    )
    
    if all_good:
        print("✅ ALL CHECKS PASSED")
        print("✅ Dashboard is properly configured for lazy loading")
        print("✅ All 7 tabs are ready to display data")
        return True
    else:
        print("⚠️ Some checks failed - see details above")
        return False


if __name__ == "__main__":
    success = validate_dashboard()
    exit(0 if success else 1)

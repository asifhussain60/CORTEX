#!/usr/bin/env python3
"""
Phase 14 Task 14.4: Dashboard Tab & Diagram Validation

Manual validation checklist for dashboard completeness.

Author: Asif Hussain
"""

from pathlib import Path
import json


def check_dashboard_structure():
    """Validate dashboard file structure and tabs"""
    
    print("\n" + "=" * 80)
    print("PHASE 14 - TASK 14.4: DASHBOARD VALIDATION")
    print("=" * 80 + "\n")
    
    results = {
        "tabs": {},
        "diagrams": {},
        "architecture_docs": {},
        "issues": []
    }
    
    # 1. Check main dashboard HTML exists
    dashboard_html = Path("cortex-brain/dashboards/ui/index.html")
    if dashboard_html.exists():
        print("✅ Main dashboard HTML found:", dashboard_html)
        results["dashboard_html"] = "EXISTS"
    else:
        print("❌ Main dashboard HTML missing:", dashboard_html)
        results["dashboard_html"] = "MISSING"
        results["issues"].append("Main dashboard HTML not found")
    
    # 2. Check tab components
    tabs = {
        "executive-tab.js": "Executive Summary",
        "overview-tab.js": "System Overview",
        "overview-tab-v3.js": "System Overview v3",
        "tech-stack-tab.js": "Tech Stack",
        "security-tab.js": "Security",
        "use-cases-tab.js": "Use Cases",
        "recommendations-tab.js": "Recommendations",
        "architecture-tab.js": "Architecture",
        "code-org-tab.js": "Code Organization",
        "vendors-tab.js": "Dependencies",
        "onboarding-tab.js": "Onboarding"
    }
    
    print("\n📊 Tab Components:")
    print("-" * 80)
    components_dir = Path("cortex-brain/dashboards/ui/components")
    for tab_file, tab_name in tabs.items():
        tab_path = components_dir / tab_file
        if tab_path.exists():
            size = tab_path.stat().st_size
            print(f"  ✅ {tab_name:25} | {tab_file:25} | {size:,} bytes")
            results["tabs"][tab_name] = "EXISTS"
        else:
            print(f"  ❌ {tab_name:25} | {tab_file:25} | MISSING")
            results["tabs"][tab_name] = "MISSING"
            results["issues"].append(f"Tab component missing: {tab_file}")
    
    # 3. Check visualization libraries in HTML
    print("\n📚 Visualization Libraries:")
    print("-" * 80)
    if dashboard_html.exists():
        content = dashboard_html.read_text(encoding='utf-8')
        libs = {
            "D3.js": "d3js.org/d3.v7",
            "Three.js": "three.js/r128",
            "Chart.js": "chart.js@4.4.0",
            "Mermaid": "mermaid@10"
        }
        for lib_name, lib_pattern in libs.items():
            if lib_pattern in content:
                print(f"  ✅ {lib_name:15} | CDN link found")
                results["diagrams"][lib_name] = "LOADED"
            else:
                print(f"  ❌ {lib_name:15} | CDN link missing")
                results["diagrams"][lib_name] = "MISSING"
                results["issues"].append(f"Visualization library missing: {lib_name}")
    
    # 4. Check architecture documentation (from STATUS.md - corrected naming)
    print("\n🏗️ Architecture Documentation (Phase 6.5 + Task 14.3):")
    print("-" * 80)
    arch_docs = {
        # Found in architecture directory (actual naming)
        "TDD_v4": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/TDD-V4-ORCHESTRATOR-ARCHITECTURE.md",
        "PlanningSystem2": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/PLANNING-SYSTEM-2.0-ORCHESTRATOR-ARCHITECTURE.md",
        "DocumentationOrchestrator": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/DOCUMENTATION-ORCHESTRATOR-ARCHITECTURE.md",
        "DevOpsOrchestrator": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/DEVOPS-ORCHESTRATOR-ARCHITECTURE.md",
        "ADOOrchestrator": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/ADO-OPERATIONS-ORCHESTRATOR-ARCHITECTURE.md",
        "CodeSanitizationOrchestrator": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/CODE-SANITIZATION-ORCHESTRATOR-ARCHITECTURE.md",
        "SystemMaintenanceOrchestrator": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/SYSTEM-MAINTENANCE-ORCHESTRATOR-ARCHITECTURE.md",
        # Additional architecture documents found
        "CORTEX_4.0_Architecture": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/CORTEX-4.0-ARCHITECTURE-DESIGN.md",
        "TDD_Redesign": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/TDD-ORCHESTRATOR-REDESIGN.md",
        "CORTEX_Lens_Architecture": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/CORTEX-LENS-ARCHITECTURE-REDESIGN.md",
        "FeatureDiscovery": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/FEATURE-DISCOVERY-ORCHESTRATOR-DESIGN.md",
        "TechnicalDocumentation": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/technical-documentation-orchestrator-design.md",
        "IDEDetection": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/IDE-DETECTION-IMPLEMENTATION-PLAN.md",
        "CrossIDEWorkspace": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/CROSS-IDE-WORKSPACE-DETECTION.md",
        "Phase11DocsAlignment": "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/architecture/PHASE-11-DOCUMENTATION-ALIGNMENT.md",
    }
    
    docs_found = 0
    total_lines = 0
    for doc_name, doc_path in arch_docs.items():
        doc_file = Path(doc_path)
        if doc_file.exists():
            lines = len(doc_file.read_text(encoding='utf-8').splitlines())
            total_lines += lines
            print(f"  ✅ {doc_name:25} | {lines:,} lines")
            results["architecture_docs"][doc_name] = "EXISTS"
            docs_found += 1
        else:
            print(f"  ❌ {doc_name:25} | MISSING")
            results["architecture_docs"][doc_name] = "MISSING"
            results["issues"].append(f"Architecture doc missing: {doc_name}")
    
    print(f"\n  📈 Total: {docs_found}/{len(arch_docs)} docs found | ~{total_lines:,} lines")
    
    # 5. Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    tabs_count = sum(1 for v in results["tabs"].values() if v == "EXISTS")
    libs_count = sum(1 for v in results["diagrams"].values() if v == "LOADED")
    docs_count = sum(1 for v in results["architecture_docs"].values() if v == "EXISTS")
    
    print(f"\n✅ Dashboard HTML:        {'PASS' if results.get('dashboard_html') == 'EXISTS' else 'FAIL'}")
    print(f"✅ Tab Components:        {tabs_count}/{len(tabs)} found")
    print(f"✅ Visualization Libs:    {libs_count}/{len(libs)} loaded")
    print(f"✅ Architecture Docs:     {docs_count}/{len(arch_docs)} found")
    print(f"\n⚠️  Issues Found:          {len(results['issues'])}")
    
    if results["issues"]:
        print("\nIssues:")
        for issue in results["issues"]:
            print(f"  • {issue}")
    
    # Overall status
    all_tabs_ok = tabs_count == len(tabs)
    all_libs_ok = libs_count == len(libs)
    all_docs_ok = docs_count == len(arch_docs)
    
    if all_tabs_ok and all_libs_ok and all_docs_ok:
        print("\n🎉 STATUS: ALL VALIDATION CHECKS PASSED")
        status = "COMPLETE"
    else:
        print("\n⚠️  STATUS: SOME VALIDATION CHECKS FAILED")
        status = "INCOMPLETE"
    
    # Save results
    report_path = Path("cortex-brain/dashboards/phase-14-task-14.4-validation.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results["status"] = status
    results["summary"] = {
        "tabs": f"{tabs_count}/{len(tabs)}",
        "libs": f"{libs_count}/{len(libs)}",
        "docs": f"{docs_count}/{len(arch_docs)}",
        "total_issues": len(results["issues"])
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed report saved: {report_path}")
    print("=" * 80 + "\n")
    
    return status == "COMPLETE"


if __name__ == "__main__":
    import sys
    success = check_dashboard_structure()
    sys.exit(0 if success else 1)

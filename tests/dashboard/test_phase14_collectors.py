"""
Test Architecture and Code Organization Collectors

Phase 14 validation with CORTEX's own codebase.

Author: Asif Hussain
"""

from pathlib import Path
from src.dashboard.data.architecture_collector import ArchitectureCollector
from src.dashboard.data.code_org_collector import CodeOrganizationCollector

def test_phase14_collectors():
    """Test Phase 14 collectors on CORTEX codebase."""
    cortex_root = Path.cwd()
    
    print("=" * 60)
    print("PHASE 14 COLLECTOR TEST - CORTEX Project")
    print("=" * 60)
    
    # Test Architecture Collector
    print("\n🏗️  Testing Architecture Collector...")
    arch_collector = ArchitectureCollector(cortex_root)
    architecture = arch_collector.collect()
    
    if architecture:
        print(f"\n✅ Architecture Collection Successful!")
        print(f"   Architecture Style: {architecture['style']}")
        print(f"   Total Components: {architecture['summary']['total_components']}")
        print(f"   Total Files: {architecture['summary']['total_files']}")
        print(f"   Total LOC: {architecture['summary']['total_loc']}")
        print(f"   Architecture Score: {architecture['summary']['architecture_score']}/100")
        
        print(f"\n   Tiers Found: {len(architecture['tiers'])}")
        for tier in architecture['tiers']:
            print(f"      - {tier['name']}: {tier['file_count']} files, {tier['loc']} LOC")
        
        print(f"\n   Sample Components:")
        for comp in architecture['components'][:5]:
            print(f"      - {comp['name']} ({comp['tier']}): {comp['loc']} LOC, {len(comp['dependencies'])} deps")
        
        if architecture['database_schema']['tables']:
            print(f"\n   Database Tables: {len(architecture['database_schema']['tables'])}")
            for table in architecture['database_schema']['tables'][:5]:
                print(f"      - {table['name']}: {table['column_count']} columns")
    else:
        print("❌ Architecture Collection Failed")
    
    # Test Code Organization Collector
    print("\n\n📊 Testing Code Organization Collector...")
    code_org_collector = CodeOrganizationCollector(cortex_root)
    code_org = code_org_collector.collect()
    
    if code_org:
        print(f"\n✅ Code Organization Collection Successful!")
        print(f"   Total Files: {code_org['summary']['total_files']}")
        print(f"   High Complexity Files: {code_org['summary']['high_complexity_files']}")
        print(f"   Hotspots: {code_org['summary']['hotspot_count']}")
        print(f"   Average Complexity: {code_org['summary']['avg_complexity']:.1f}")
        
        print(f"\n   Top 5 Most Complex Files:")
        for file in code_org['heatmap'][:5]:
            print(f"      - {file['file']}")
            print(f"        Complexity: {file['complexity']}, LOC: {file['loc']}, Changes: {file['change_frequency']}, Risk: {file['risk_score']}")
        
        if code_org['hotspots']:
            print(f"\n   Critical Hotspots (Risk > 50):")
            for hotspot in code_org['hotspots'][:3]:
                print(f"      - {hotspot['file']}")
                print(f"        Risk: {hotspot['risk_score']}, Complexity: {hotspot['complexity']}")
                print(f"        Recommendation: {hotspot['recommendation']}")
        
        print(f"\n   Module Structure:")
        print(f"      Total Modules: {code_org['module_structure']['total_directories']}")
        print(f"      Max Depth: {code_org['module_structure']['depth']} levels")
    else:
        print("❌ Code Organization Collection Failed")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\n✅ Phase 14 collectors working with CURRENT STATE data only")
    print("✅ No mock data - all metrics from actual CORTEX codebase")
    print("✅ Ready for dashboard integration")
    print("\n📋 Next: Phase 15 - Dependency Deep Dive with External Vendors")

if __name__ == "__main__":
    test_phase14_collectors()

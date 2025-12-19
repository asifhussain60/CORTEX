"""
Test RecursiveScanner and Dashboard Collectors with V5.WebServices.PrevalidationWS

Validates that dashboard collectors correctly scan .NET repositories
without hardcoded 'src/' assumptions.

Author: CORTEX
Created: 2025-12-05
"""

import sys
from pathlib import Path
import json
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.dashboard.utils.recursive_scanner import RecursiveScanner
from src.dashboard.data.code_org_collector import CodeOrganizationCollector
from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.architecture_collector import ArchitectureCollector
from src.dashboard.data.security_collector import SecurityCollector
from src.dashboard.data.vendor_detector import VendorDetector

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_recursive_scanner():
    """Test RecursiveScanner on V5.WebServices.PrevalidationWS"""
    print("\n" + "="*80)
    print("TEST 1: RecursiveScanner on V5.WebServices.PrevalidationWS")
    print("="*80)
    
    project_root = Path("C:/PROJECTS/V5.WebServices.PrevalidationWS")
    
    if not project_root.exists():
        print(f"❌ Project not found: {project_root}")
        return False
    
    scanner = RecursiveScanner(project_root)
    
    # Test .NET file scanning
    print("\n📊 Scanning for .NET files...")
    dotnet_files = scanner.scan_dotnet_files()
    print(f"✓ Found {len(dotnet_files)} .NET files")
    
    if dotnet_files:
        # Show first 10 files
        print("\nFirst 10 files:")
        for i, file_path in enumerate(dotnet_files[:10], 1):
            rel_path = file_path.relative_to(project_root)
            print(f"  {i}. {rel_path}")
    
    # Get statistics
    stats = scanner.get_file_stats(dotnet_files)
    print(f"\n📈 Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_kb']:.2f} KB")
    print(f"  By extension:")
    for ext, count in sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"    {ext}: {count} files")
    
    # Verify no 'src/' assumption
    print("\n🔍 Verification:")
    has_src_dir = (project_root / "src").exists()
    print(f"  Has 'src/' directory: {has_src_dir}")
    print(f"  Files found regardless: {len(dotnet_files) > 0}")
    
    if len(dotnet_files) > 0:
        print("✅ RecursiveScanner works correctly (no hardcoded 'src/' assumption)")
        return True
    else:
        print("❌ RecursiveScanner failed to find files")
        return False


def test_code_org_collector():
    """Test CodeOrganizationCollector on V5.WebServices.PrevalidationWS"""
    print("\n" + "="*80)
    print("TEST 2: CodeOrganizationCollector on V5.WebServices.PrevalidationWS")
    print("="*80)
    
    project_root = Path("C:/PROJECTS/V5.WebServices.PrevalidationWS")
    
    if not project_root.exists():
        print(f"❌ Project not found: {project_root}")
        return False
    
    print("\n📊 Running Code Organization Collector...")
    collector = CodeOrganizationCollector(project_root)
    
    try:
        data = collector.collect()
        
        if not data:
            print("❌ Collector returned no data")
            return False
        
        print("✓ Data collected successfully")
        
        # Validate structure
        print(f"\n📈 Results:")
        print(f"  Heatmap entries: {len(data.get('heatmap', []))}")
        print(f"  Hotspots: {len(data.get('hotspots', []))}")
        print(f"  Module directories: {data.get('module_structure', {}).get('total_directories', 0)}")
        print(f"  File sizes analyzed: {len(data.get('file_sizes', {}).get('largest_files', []))}")
        
        # Show sample heatmap entries
        if data.get('heatmap'):
            print(f"\n📁 Sample heatmap entries:")
            for i, entry in enumerate(data['heatmap'][:5], 1):
                print(f"  {i}. {entry['file']} - Complexity: {entry.get('complexity', 0)}, LOC: {entry.get('loc', 0)}")
        
        # Verify multi-language support
        extensions = set()
        for entry in data.get('heatmap', []):
            file_path = Path(entry['file'])
            extensions.add(file_path.suffix)
        
        print(f"\n🔍 File types analyzed: {', '.join(sorted(extensions))}")
        
        if '.cs' in extensions:
            print("✅ CodeOrganizationCollector correctly analyzes .NET files")
            return True
        else:
            print("⚠️  No .cs files in heatmap (unexpected for .NET project)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_collectors():
    """Test all collectors on V5.WebServices.PrevalidationWS"""
    print("\n" + "="*80)
    print("TEST 3: All Collectors on V5.WebServices.PrevalidationWS")
    print("="*80)
    
    project_root = Path("C:/PROJECTS/V5.WebServices.PrevalidationWS")
    
    if not project_root.exists():
        print(f"❌ Project not found: {project_root}")
        return False
    
    collectors = [
        ("Code Organization", CodeOrganizationCollector),
        ("Tech Stack", TechStackCollector),
        ("Architecture", ArchitectureCollector),
        ("Security", SecurityCollector),
        ("Vendor Detection", VendorDetector)
    ]
    
    results = {}
    
    for name, CollectorClass in collectors:
        print(f"\n📊 Testing {name} Collector...")
        try:
            collector = CollectorClass(project_root)
            data = collector.collect()
            
            if data:
                results[name] = "✅ Success"
                print(f"  ✓ Data keys: {', '.join(list(data.keys())[:5])}")
            else:
                results[name] = "⚠️  No data"
                
        except Exception as e:
            results[name] = f"❌ Error: {str(e)[:50]}"
            print(f"  ❌ {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*80)
    print("COLLECTOR TEST SUMMARY")
    print("="*80)
    for name, status in results.items():
        print(f"  {name}: {status}")
    
    success_count = sum(1 for s in results.values() if s.startswith("✅"))
    total_count = len(results)
    
    print(f"\n📊 Success Rate: {success_count}/{total_count} ({100*success_count//total_count}%)")
    
    return success_count == total_count


def generate_dashboard_data():
    """Generate complete dashboard data for V5.WebServices.PrevalidationWS"""
    print("\n" + "="*80)
    print("GENERATING DASHBOARD DATA")
    print("="*80)
    
    project_root = Path("C:/PROJECTS/V5.WebServices.PrevalidationWS")
    output_dir = Path("cortex-brain/dashboards/v5-webservices-prevalidationws")
    
    if not project_root.exists():
        print(f"❌ Project not found: {project_root}")
        return False
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    collectors = [
        ("metadata", None, {"name": "V5 WebServices PrevalidationWS", "last_updated": "2025-12-05"}),
        ("code-organization", CodeOrganizationCollector, None),
        ("tech-stack", TechStackCollector, None),
        ("architecture", ArchitectureCollector, None),
        ("security", SecurityCollector, None),
        ("vendors", VendorDetector, None)
    ]
    
    generated_files = []
    
    for name, CollectorClass, static_data in collectors:
        output_file = output_dir / f"{name}.json"
        
        print(f"\n📝 Generating {name}.json...")
        
        try:
            if static_data:
                data = static_data
            else:
                collector = CollectorClass(project_root)
                data = collector.collect()
            
            if data:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                file_size_kb = output_file.stat().st_size / 1024
                print(f"  ✓ Generated {output_file.name} ({file_size_kb:.2f} KB)")
                generated_files.append(output_file.name)
            else:
                print(f"  ⚠️  No data for {name}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*80)
    print("DASHBOARD GENERATION SUMMARY")
    print("="*80)
    print(f"Output directory: {output_dir}")
    print(f"Generated files: {len(generated_files)}/{len(collectors)}")
    for filename in generated_files:
        print(f"  ✓ {filename}")
    
    return len(generated_files) == len(collectors)


if __name__ == "__main__":
    print("="*80)
    print("DASHBOARD COLLECTOR VALIDATION SUITE")
    print("Testing fixes for hardcoded 'src/' paths")
    print("="*80)
    
    # Run tests
    test1 = test_recursive_scanner()
    test2 = test_code_org_collector()
    test3 = test_all_collectors()
    test4 = generate_dashboard_data()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    tests = [
        ("RecursiveScanner", test1),
        ("CodeOrganizationCollector", test2),
        ("All Collectors", test3),
        ("Dashboard Generation", test4)
    ]
    
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    overall = all(t[1] for t in tests)
    print(f"\n{'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")
    
    sys.exit(0 if overall else 1)

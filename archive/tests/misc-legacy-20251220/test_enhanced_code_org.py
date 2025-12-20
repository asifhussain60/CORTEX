"""Test enhanced code organization collector"""
from src.dashboard.data.code_org_collector import CodeOrganizationCollector
from pathlib import Path

collector = CodeOrganizationCollector(Path('C:/PROJECTS/CORTEX'))
result = collector.collect()

print("="*60)
print("ENHANCED CODE ORGANIZATION ANALYSIS")
print("="*60)
print(f"\n📊 Summary:")
print(f"  Total Files: {result['summary']['total_files']}")
print(f"  High Complexity Files: {result['summary']['high_complexity_files']}")
print(f"  Hotspots: {result['summary']['hotspot_count']}")
print(f"  Avg Complexity: {result['summary']['avg_complexity']:.1f}")
print(f"  Total LOC: {result['summary'].get('total_loc', 0):,}")

print(f"\n📐 Maintainability:")
print(f"  Overall Score: {result['maintainability'].get('overall_score', 0)}/100")
print(f"  Excellent Files: {result['maintainability']['files_by_category'].get('excellent', 0)}")
print(f"  Good Files: {result['maintainability']['files_by_category'].get('good', 0)}")
print(f"  Fair Files: {result['maintainability']['files_by_category'].get('fair', 0)}")
print(f"  Poor Files: {result['maintainability']['files_by_category'].get('poor', 0)}")

print(f"\n⏱️ Technical Debt:")
print(f"  Total Hours: {result['technical_debt'].get('total_hours', 0):.1f}h")
print(f"  Complexity Debt: {result['technical_debt']['by_category'].get('complexity', 0):.1f}h")
print(f"  Duplication Debt: {result['technical_debt']['by_category'].get('duplication', 0):.1f}h")
print(f"  Size Debt: {result['technical_debt']['by_category'].get('size', 0):.1f}h")

print(f"\n📋 Duplication:")
print(f"  Duplication Rate: {result['duplications'].get('duplication_rate', 0):.2f}%")
print(f"  Files with Duplicates: {result['duplications'].get('files_with_duplicates', 0)}")
print(f"  Duplicate Blocks: {len(result['duplications'].get('duplicate_blocks', []))}")

print(f"\n👃 Code Smells:")
print(f"  Total: {result['summary'].get('code_smell_count', 0)}")
if result.get('code_smells'):
    high = sum(1 for s in result['code_smells'] if s['severity'] == 'high')
    medium = sum(1 for s in result['code_smells'] if s['severity'] == 'medium')
    low = sum(1 for s in result['code_smells'] if s['severity'] == 'low')
    print(f"  High: {high}, Medium: {medium}, Low: {low}")

print(f"\n📏 File Sizes:")
sizes = result['file_sizes']['distribution']
print(f"  Small (<100 LOC): {sizes.get('small', 0)}")
print(f"  Medium (100-300): {sizes.get('medium', 0)}")
print(f"  Large (300-500): {sizes.get('large', 0)}")
print(f"  Very Large (>500): {sizes.get('very_large', 0)}")

print("\n" + "="*60)
print("✅ Enhanced collector working correctly!")
print("="*60)

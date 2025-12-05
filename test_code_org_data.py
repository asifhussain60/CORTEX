"""Quick test to see Code Organization collector data structure"""
from pathlib import Path
from src.dashboard.data.code_org_collector import CodeOrganizationCollector
import json

cortex_root = Path(__file__).parent
collector = CodeOrganizationCollector(cortex_root)
data = collector.collect()

print("=" * 70)
print("CODE ORGANIZATION COLLECTOR DATA STRUCTURE")
print("=" * 70)

print("\n📊 Top-level keys:")
for key in data.keys():
    print(f"  - {key}")

print("\n📈 Summary metrics:")
if "summary" in data:
    for key, value in data["summary"].items():
        print(f"  {key}: {value}")

print("\n🔥 Duplications:")
if "duplications" in data:
    print(f"  Found: {data['duplications'].get('duplicate_blocks', [])[:2]}")
    print(f"  Rate: {data['duplications'].get('duplication_rate', 0):.1f}%")

print("\n🔧 Maintainability:")
if "maintainability" in data:
    print(f"  Overall Score: {data['maintainability'].get('overall_score', 0):.1f}")
    print(f"  Interpretation: {data['maintainability'].get('interpretation', 'N/A')}")

print("\n💰 Technical Debt:")
if "technical_debt" in data:
    print(f"  Total Hours: {data['technical_debt'].get('total_hours', 0):.1f}")
    print(f"  Severity: {data['technical_debt'].get('severity_level', 'N/A')}")

print("\n📦 File Sizes:")
if "file_sizes" in data:
    dist = data["file_sizes"].get("distribution", {})
    print(f"  Small: {dist.get('small', 0)}, Medium: {dist.get('medium', 0)}")
    print(f"  Large: {dist.get('large', 0)}, Huge: {dist.get('huge', 0)}")

print("\n👃 Code Smells:")
if "code_smells" in data:
    smells = data["code_smells"]
    print(f"  Total: {len(smells)}")
    if smells:
        print(f"  First 3: {[s['type'] for s in smells[:3]]}")

print("\n" + "=" * 70)
print("✅ Data collection complete!")
print("=" * 70)

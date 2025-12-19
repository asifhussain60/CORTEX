"""
Test Dependency Discovery Feature in Discovery Orchestrator
"""
import sys
from pathlib import Path

# Add CORTEX src to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root / 'src'))

from src.operations.modules.orchestration.discovery_orchestrator import DiscoveryOrchestrator
from src.operations.modules.discovery.models import FileInventory

# Initialize orchestrator
print("🎭 Initializing Discovery Orchestrator...")
orchestrator = DiscoveryOrchestrator(
    cortex_root=cortex_root,
    user_project_root=cortex_root
)

# Create simple file inventory for testing Phase 6
print("📁 Creating file inventory...")
src_files = list((cortex_root / 'src').rglob('*.py'))
print(f"Found {len(src_files)} Python files in src/")

# Create mock FileInventory object
class MockFileInventory:
    def __init__(self, files):
        self.files = files

inventory = MockFileInventory(src_files)

# Run Phase 6: Dependency Discovery
print("\n🔍 Running Phase 6: Dependency Discovery...")
result = orchestrator._phase_6_discover_dependencies(inventory)

# Display results
print("\n" + "="*80)
print("📊 DEPENDENCY DISCOVERY RESULTS")
print("="*80)

print(f"\n✅ Files Scanned: {result.get('total_files_scanned', 0)}")
print(f"\n📦 Declared Packages: {len(result.get('declared_packages', []))}")
print(f"🔬 Actually Used: {len(result.get('used_packages', []))}")
print(f"❌ Unused Packages: {len(result.get('unused_packages', []))}")
print(f"🗑️  Waste Percentage: {result.get('waste_percentage', 0)}%")

print("\n✅ USED PACKAGES:")
for pkg in sorted(result.get('used_packages', [])):
    locations = result.get('import_locations', {}).get(pkg, [])
    print(f"  - {pkg} (imported in {len(locations)} locations)")

print("\n❌ UNUSED PACKAGES (Should be removed or lazy-loaded):")
for pkg in sorted(result.get('unused_packages', [])):
    print(f"  - {pkg}")

print("\n🔬 ACTUAL IMPORTS DETECTED:")
for imp in sorted(result.get('actual_imports', []))[:20]:  # Show first 20
    print(f"  - {imp}")

print("\n" + "="*80)
print("✅ Discovery Orchestrator Phase 6 validation complete!")
print("="*80)

# Generate summary report
print("\n📄 Generating summary for documentation...")
summary_path = cortex_root / 'cortex-brain' / 'documents' / 'reports' / 'dependency-discovery-validation.md'
summary_path.parent.mkdir(parents=True, exist_ok=True)

with open(summary_path, 'w', encoding='utf-8') as f:
    f.write("# Dependency Discovery Validation Report\n\n")
    f.write(f"**Date:** {Path(__file__).stat().st_mtime}\n")
    f.write(f"**Orchestrator Version:** 1.1.0\n\n")
    f.write("## Results\n\n")
    f.write(f"- **Files Scanned:** {result.get('total_files_scanned', 0)}\n")
    f.write(f"- **Declared Packages:** {len(result.get('declared_packages', []))}\n")
    f.write(f"- **Actually Used:** {len(result.get('used_packages', []))}\n")
    f.write(f"- **Unused Packages:** {len(result.get('unused_packages', []))}\n")
    f.write(f"- **Waste Percentage:** {result.get('waste_percentage', 0)}%\n\n")
    f.write("## Used Packages\n\n")
    for pkg in sorted(result.get('used_packages', [])):
        f.write(f"- `{pkg}`\n")
    f.write("\n## Unused Packages\n\n")
    for pkg in sorted(result.get('unused_packages', [])):
        f.write(f"- `{pkg}` ⚠️ Should be removed or moved to optional\n")

print(f"\n✅ Report saved to: {summary_path}")

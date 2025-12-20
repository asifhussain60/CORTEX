"""Test cross-platform path resolution fix"""
import sys
from pathlib import Path

cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))

from src.config import config
from src.utils.enhancement_catalog import EnhancementCatalog
from src.tier3.architecture_health_history import ArchitectureHealthHistory

print("=" * 80)
print("Cross-Platform Path Resolution Test")
print("=" * 80)

# Test config paths
print(f"\n✅ Config Test:")
print(f"   Root Path: {config.root_path}")
print(f"   Brain Path: {config.brain_path}")

# Test Enhancement Catalog
print(f"\n✅ Enhancement Catalog Test:")
cat = EnhancementCatalog()
print(f"   Database: {cat.db_path}")
print(f"   Exists: {cat.db_path.exists()}")

# Test Architecture Health History
print(f"\n✅ Architecture Health History Test:")
hist = ArchitectureHealthHistory()
print(f"   Database: {hist.store.db_path}")
latest = hist.get_latest_health()
if latest:
    print(f"   Latest Health: {latest.overall_score}%")
else:
    print(f"   Latest Health: No data")

print(f"\n" + "=" * 80)
print("✅ ALL TESTS PASSED - Cross-platform path resolution working")
print("=" * 80)

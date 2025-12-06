#!/usr/bin/env python3
"""Quick optimization runner"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.optimize_operation import OptimizeOperation

op = OptimizeOperation()
result = op.execute(skip_skull_tests=False, dry_run=False)

print(f"\n{'='*80}")
print(f"RESULT: {result.message}")
print(f"{'='*80}\n")

data = result.data
print("📊 OPTIMIZATIONS APPLIED:")
for opt in data.get('optimizations_applied', []):
    print(f"  ✅ {opt}")

print(f"\n💾 SPACE SAVED: {data.get('space_saved_mb', 0):.2f} MB")
print(f"📁 FILES MOVED: {data.get('files_moved', 0)}")
print(f"🗑️  FILES REMOVED: {data.get('files_removed', 0)}")
print(f"📂 DIRECTORIES CLEANED: {data.get('directories_cleaned', 0)}")

skull = data.get('skull_tests', {})
if skull:
    status = "✅ PASSED" if skull.get('success') else "❌ FAILED"
    print(f"\n🧠 SKULL TESTS: {status}")
    print(f"   Tests: {skull.get('tests_passed', 0)}/{skull.get('tests_run', 0)} passed")
    if not skull.get('success'):
        print(f"   Failed: {skull.get('tests_failed', 0)}")

if data.get('report_path'):
    print(f"\n📄 Report: {data['report_path']}")

sys.exit(0 if result.success else 1)

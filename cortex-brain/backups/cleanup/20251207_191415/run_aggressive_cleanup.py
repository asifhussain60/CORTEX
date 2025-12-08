"""Run aggressive cleanup with duplicate deletion."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator

print("=" * 70)
print("AGGRESSIVE CLEANUP - DUPLICATE DELETION ENABLED")
print("=" * 70)

cleanup = CleanupOrchestrator(Path.cwd())
result = cleanup.execute({
    'dry_run': False,
    'skip_duplicate_analysis': False,
    'auto_delete_archived': True
})

print(f"\nResult: {result.status.name}")
print(f"Message: {result.message}")
print(f"Report: {result.data.get('report_path', 'N/A')}")

# Show metrics
metrics = result.data.get('metrics', {})
print(f"\nMetrics:")
print(f"  Files moved: {metrics.get('files_moved', 0)}")
print(f"  Files removed: {metrics.get('files_removed', 0)}")
print(f"  Duplicates deleted: {metrics.get('duplicates_deleted', 0)}")
print(f"  Space freed: {metrics.get('space_freed_mb', 0):.2f} MB")

if result.data.get('duplicate_report'):
    print(f"\nDuplicate Analysis:")
    print(f"  Found: {metrics.get('duplicates_found', 0)}")
    print(f"  Safe to delete: {metrics.get('safe_to_delete', 0)}")
    print(f"  Need review: {metrics.get('needs_review', 0)}")

print("\n" + "=" * 70)

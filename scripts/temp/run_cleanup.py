"""Quick script to run cleanup in safe mode"""
from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
from pathlib import Path

print("=" * 80)
print("CORTEX CLEANUP - SAFE MODE")
print("=" * 80)
print("Running with backup enabled, dry_run=False")
print()

orchestrator = CleanupOrchestrator(project_root=Path('D:/PROJECTS/CORTEX'))
result = orchestrator.execute({
    'profile': 'standard',
    'dry_run': False
})

print()
print("=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)

metrics = result.result.get('metrics', {})
print(f"Files deleted: {metrics.get('files_deleted', 0)}")
print(f"Backups archived: {metrics.get('backups_deleted', 0)}")
print(f"Space freed: {metrics.get('space_freed_bytes', 0) / (1024*1024):.2f} MB")
print(f"Success: {result.success}")
print(f"Message: {result.message}")

"""Run cleanup orchestrator."""
from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator

co = CleanupOrchestrator()
result = co.execute({'dry_run': False})

print('Status:', 'SUCCESS' if result.success else 'FAILED')
metrics = result.data.get('metrics', {})
print(f'Files moved: {metrics.get("files_moved", 0)}')
print(f'Files removed: {metrics.get("files_removed", 0)}')
print(f'References updated: {metrics.get("references_updated", 0)}')

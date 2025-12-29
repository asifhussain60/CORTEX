"""
Execute CORTEX Story Refresh Operation

This script executes the story refresh operation and provides detailed monitoring.
"""
from src.operations import execute_operation

print("=" * 60)
print("CORTEX STORY REFRESH OPERATION")
print("=" * 60)
print()

# Execute the story refresh operation
report = execute_operation('refresh story')

# Display results
print(f"Operation: {report.operation_name}")
print(f"Success: {report.success}")
print(f"Duration: {report.total_duration_seconds:.2f}s")
print()
print(f"Modules Executed: {len(report.modules_executed)}")
print(f"Modules Succeeded: {len(report.modules_succeeded)}")
print(f"Modules Failed: {len(report.modules_failed)}")
print(f"Modules Skipped: {len(report.modules_skipped)}")
print()

print("--- Module Results ---")
for mod_id, result in report.module_results.items():
    status_icon = "✅" if result.status.value == "COMPLETED" else "❌" if result.status.value == "FAILED" else "⏭️"
    print(f"  {status_icon} {mod_id}: {result.status.value}")
    print(f"     {result.message}")
    if result.warnings:
        for warning in result.warnings:
            print(f"     ⚠️  {warning}")
    if result.errors:
        for error in result.errors:
            print(f"     ❌ {error}")
    print()

if report.errors:
    print("--- Overall Errors ---")
    for err in report.errors:
        print(f"  ❌ {err}")
    print()

# Check context for file updates
if 'story_file_path' in report.context:
    print(f"Story updated at: {report.context['story_file_path']}")
if 'backup_file_path' in report.context:
    print(f"Backup created at: {report.context['backup_file_path']}")

print()
print("=" * 60)
if report.success:
    print("✅ STORY REFRESH COMPLETED SUCCESSFULLY")
else:
    print("❌ STORY REFRESH FAILED")
print("=" * 60)

"""Quick test script for design sync operation."""
from src.operations import execute_operation
import json

# Run design sync
print("Running design sync with 'standard' profile...")
result = execute_operation('sync design', profile='standard')

print("\n" + "="*80)
print("DESIGN SYNC DETAILED REPORT")
print("="*80)

print(f"\nOperation: {result.operation_name}")
print(f"Operation ID: {result.operation_id}")
print(f"Success: {result.success}")
print(f"Duration: {result.total_duration_seconds:.1f}s")
print(f"Timestamp: {result.timestamp}")

print(f"\nModules Executed: {len(result.modules_executed)}")
print(f"Modules Succeeded: {len(result.modules_succeeded)}")
print(f"Modules Failed: {len(result.modules_failed)}")
print(f"Modules Skipped: {len(result.modules_skipped)}")

if result.modules_executed:
    print(f"\nExecuted Modules: {', '.join(result.modules_executed)}")

if result.errors:
    print(f"\nErrors ({len(result.errors)}):")
    for error in result.errors:
        print(f"  • {error}")

print("\n" + "-"*80)
print("MODULE RESULTS:")
print("-"*80)

for mod_id, mod_result in result.module_results.items():
    print(f"\n{mod_id}:")
    print(f"  Status: {mod_result.status}")
    print(f"  Message: {mod_result.message}")
    
    if mod_result.data:
        print(f"  Data:")
        for key, value in mod_result.data.items():
            # Handle non-JSON-serializable types
            if isinstance(value, (dict, list)):
                try:
                    print(f"    {key}: {json.dumps(value, indent=6, default=str)}")
                except:
                    print(f"    {key}: {value}")
            else:
                print(f"    {key}: {value}")
    
    if mod_result.errors:
        print(f"  Errors: {', '.join(mod_result.errors)}")
    
    if mod_result.warnings:
        print(f"  Warnings: {', '.join(mod_result.warnings)}")

print("\n" + "="*80)
print("END REPORT")
print("="*80)

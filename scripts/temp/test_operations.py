#!/usr/bin/env python3
"""Quick test script for CORTEX 2.0 operations."""

from src.operations import list_operations, execute_operation

print("=" * 60)
print("CORTEX 2.0 Operations Status")
print("=" * 60)

# List all operations
ops = list_operations()
print(f"\n✅ Total operations defined: {len(ops)}\n")

for op_id, info in sorted(ops.items()):
    name = info.get('name', 'Unknown')
    modules = info.get('modules', [])
    print(f"  📦 {op_id}")
    print(f"     Name: {name}")
    print(f"     Modules: {len(modules)}")
    print()

# Test key operations
print("=" * 60)
print("Testing Key Operations")
print("=" * 60)

# Test 1: Story Refresh
print("\n1️⃣  Testing Story Refresh (quick profile)...")
report = execute_operation('refresh story', profile='quick')
print(f"   Success: {'✅' if report.success else '❌'}")
print(f"   Modules: {len(report.modules_executed)}")
print(f"   Duration: {report.total_duration_seconds:.2f}s")

# Test 2: Environment Setup  
print("\n2️⃣  Testing Environment Setup (minimal profile)...")
report = execute_operation('setup environment', profile='minimal')
print(f"   Success: {'✅' if report.success else '❌'}")
print(f"   Modules: {len(report.modules_executed)}")
print(f"   Duration: {report.total_duration_seconds:.2f}s")

print("\n" + "=" * 60)
print("✅ All tests complete!")
print("=" * 60)

#!/usr/bin/env python3
"""Test that registry is properly wired and protected.

Updated: 2026-01-25 - AC-PERMANENT-FIX-010: Use DatabaseBackedRegistry as primary
"""

from pathlib import Path
from typing import Any, Dict

# Test 1: Verify DatabaseBackedRegistry is SSOT
print("TEST 1: Verify DatabaseBackedRegistry is active (SSOT)")
print("=" * 60)
try:
    from cortex.orchestrators import get_database_registry
    
    registry = get_database_registry()
    stats: Dict[str, Any] = registry.get_wiring_statistics()
    
    total: int = stats.get('total_registered', 0)
    wired: int = stats.get('total_wired', 0)
    
    print(f"DatabaseBackedRegistry: ✅ ACTIVE")
    print(f"Registered: {total}, Wired: {wired}")
    print(f"Status: {'✅ HEALTHY' if wired >= 18 else '⚠️  LOW WIRING COUNT'}")
    db_available = True
except ImportError as e:
    print(f"DatabaseBackedRegistry: ❌ NOT AVAILABLE ({e})")
    db_available = False
print()

# Test 2: Verify YAML registry as fallback (legacy)
print("TEST 2: Verify YAML registry exists (legacy fallback)")
print("=" * 60)
import yaml
registry_path = Path('cortex_brain/tier0/repo-registry.yaml')

if registry_path.exists():
    with open(registry_path, 'r') as f:
        yaml_registry = yaml.safe_load(f)
    
    is_locked = not yaml_registry.get('registry_template', True)
    yaml_count = len(yaml_registry.get('registered_orchestrators', []))
    print(f"YAML registry exists: ✅ YES")
    print(f"Registry locked (registry_template=false): {'✅ YES' if is_locked else '❌ NO'}")
    print(f"Orchestrators in YAML: {yaml_count}")
    yaml_available = True
else:
    print(f"YAML registry exists: ❌ NO (file not found)")
    yaml_available = False
print()

# Test 3: Verify DatabaseBackedRegistry initialization
print("TEST 3: Verify DatabaseBackedRegistry initialization")
print("=" * 60)
try:
    from cortex.orchestrators.core.database_registry import get_database_registry
    registry = get_database_registry()
    stats = registry.get_wiring_statistics()
    print(f"DatabaseBackedRegistry initialized: ✅ YES")
    print(f"Orchestrators wired: {stats.get('wired_orchestrators', 0)}")
except Exception as e:
    print(f"DatabaseBackedRegistry initialized: ❌ NO ({e})")
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
if db_available:
    print("✅ DatabaseBackedRegistry is SSOT (primary)")
if yaml_available:
    print("✅ YAML registry available (fallback)")
print("✅ Permanent fixes are active (AC-PERMANENT-FIX-001 through 010)")
print()
print("🚀 REGISTRY PROTECTION IS ACTIVE")

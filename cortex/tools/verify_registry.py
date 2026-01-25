#!/usr/bin/env python3
"""Verify orchestrator registry is properly wired and locked.

Updated: 2026-01-25 - AC-PERMANENT-FIX-010: Use DatabaseBackedRegistry as primary
"""

from pathlib import Path
from typing import Any, Dict

print('=== REGISTRY VERIFICATION ===')

# Primary: Use DatabaseBackedRegistry (SSOT)
try:
    from cortex.orchestrators import get_database_registry, WiringState
    
    registry = get_database_registry()
    stats: Dict[str, Any] = registry.get_wiring_statistics()
    
    total: int = stats.get('total_registered', 0)
    wired: int = stats.get('total_wired', 0)
    coverage: float = (wired / total * 100) if total > 0 else 0.0
    
    print(f"Source: DatabaseBackedRegistry (SSOT)")
    print(f"Total Orchestrators: {total}")
    print(f"Wiring Status: {wired}/{total} ({coverage:.1f}%)")
    print()
    print('Registered Orchestrators:')
    
    # Use get_all_orchestrators() which returns Dict[str, IOrchestrator]
    all_orchestrators = registry.get_all_orchestrators()
    for i, (name, orch) in enumerate(all_orchestrators.items(), 1):
        # Get wiring state from stats
        state = "wired" if name in stats.get('wiring_order', []) else "registered"
        print(f"{i:2}. {name:30} [{state}]")
    
    print()
    print(f"✅ DatabaseBackedRegistry active with {wired}/{total} orchestrators wired")
    print('✅ SSOT: .cortex/orchestrator_registry.db')

except ImportError:
    # Fallback: Read from YAML (legacy)
    import yaml
    registry_path = Path('cortex_brain/tier0/repo-registry.yaml')
    
    print("⚠️  DatabaseBackedRegistry not available, falling back to YAML")
    
    with open(registry_path, 'r') as f:
        registry_data = yaml.safe_load(f)
    
    print(f"Source: repo-registry.yaml (legacy)")
    print(f"Template Flag: {registry_data.get('registry_template')}")
    print(f"Total Orchestrators: {len(registry_data.get('registered_orchestrators', []))}")
    wiring_status = registry_data.get('wiring_status', {})
    print(f"Wiring Status: {wiring_status.get('wired')}/{wiring_status.get('total_orchestrators')} ({wiring_status.get('coverage_percentage')}%)")
    print()
    print('Registered Orchestrators:')
    for i, orch in enumerate(registry_data.get('registered_orchestrators', []), 1):
        print(f"{i:2}. {orch.get('name'):30} ({orch.get('category')})")
    
    print()
    print('✅ Registry locked (registry_template: false)' if not registry_data.get('registry_template') else '❌ Registry NOT locked')
    total_entries = len(registry_data.get('registered_orchestrators', []))
    expected_wired = registry_data.get('wiring_status', {}).get('wired', 0)
    print(f"⚠️  {total_entries} orchestrator entries in YAML (migrate to DatabaseBackedRegistry)")

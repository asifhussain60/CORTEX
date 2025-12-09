#!/usr/bin/env python3
"""Run system maintenance orchestrator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd() / 'src'))

from operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator

print('🔧 CORTEX System Maintenance')
print('=' * 60)

orchestrator = SystemMaintenanceOrchestrator()
result = orchestrator.execute({})

print('\n' + '=' * 60)
if result.success:
    print('✅ SUCCESS')
else:
    print('❌ FAILED')

print(f"Phases: {result.data.get('phases_completed', 0)}/{result.data.get('phases_total', 6)}")
print(f"Duration: {result.duration_seconds:.2f}s")

if result.data.get('report_path'):
    print(f"Report: {result.data['report_path']}")

if result.data.get('improvements'):
    print(f"\nImprovements: {len(result.data['improvements'])}")
    for improvement in result.data['improvements'][:5]:
        print(f"  - {improvement}")

if result.data.get('warnings'):
    print(f"\nWarnings: {len(result.data['warnings'])}")
    for warning in result.data['warnings'][:5]:
        print(f"  ⚠️  {warning}")

#!/usr/bin/env python3
"""
Validate Phase 1 implementation of Planning System 2.0 manifest requirements.
"""
import sys
from pathlib import Path

# Add src to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.utils.manifest_validator import ManifestValidator

def main():
    print("=" * 80)
    print("PHASE 1 VALIDATION: Planning System 2.0 Manifest Compliance")
    print("=" * 80)
    
    validator = ManifestValidator(cortex_root=cortex_root)
    
    # Load manifest
    manifest_path = cortex_root / 'cortex-brain' / 'orchestrator-manifests' / 'planning-system-2.0-manifest.yaml'
    manifest = validator.load_manifest(str(manifest_path))
    
    print(f"\n📋 Manifest: {manifest.get('metadata', {}).get('name', 'Unknown')}")
    print(f"   Version: {manifest.get('metadata', {}).get('version', 'Unknown')}")
    
    # Validate orchestrator
    orchestrator_path = cortex_root / 'src' / 'orchestrators' / 'planning_orchestrator.py'
    report = validator.validate_orchestrator(
        'PlanningOrchestrator',
        manifest,
        str(orchestrator_path)
    )
    
    print(f"\n📊 Compliance Score: {report.compliance_percentage:.1f}%")
    print(f"   Status: {report.status}")
    print(f"   Implemented: {report.implemented_count}/{report.total_requirements}")
    
    # Show Phase 1 requirements status
    print("\n🎯 Phase 1 Requirements (Critical Priority):")
    phase1_reqs = ['REQ-001', 'REQ-002', 'REQ-003']
    
    for req in manifest.get('requirements', []):
        req_id = req.get('id')
        if req_id in phase1_reqs:
            implemented = req_id not in [i.requirement_id for i in report.issues]
            status_icon = "✅" if implemented else "❌"
            print(f"   {status_icon} {req_id}: {req.get('description', 'Unknown')}")
    
    # Show remaining issues
    if report.issues:
        print(f"\n⏳ Remaining Requirements ({len(report.issues)}):")
        for issue in report.issues[:5]:
            print(f"   - {issue.requirement_id}: {issue.description}")
        if len(report.issues) > 5:
            print(f"   ... and {len(report.issues) - 5} more")
    
    print("\n" + "=" * 80)
    
    # Return 0 if Phase 1 complete, 1 otherwise
    phase1_complete = all(req not in [i.requirement_id for i in report.issues] for req in phase1_reqs)
    return 0 if phase1_complete else 1

if __name__ == '__main__':
    sys.exit(main())

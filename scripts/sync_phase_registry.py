#!/usr/bin/env python3
"""
Registry Synchronization Script
Purpose: Sync cortex-registry/_cortex-master/index.yaml with phase YAML files
Authority: Implementation Truth (CORE-030)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def load_phase_yaml(phase_file: Path) -> Dict[str, Any]:
    """Load and parse a phase YAML file (handles multi-document YAML and errors)."""
    try:
        with open(phase_file, 'r') as f:
            # Load all documents and return the first one (metadata)
            docs = list(yaml.safe_load_all(f))
            return docs[0] if docs else {}
    except yaml.YAMLError as e:
        print(f"⚠️  Warning: Could not parse {phase_file.name}: {e}")
        return {}


def scan_phase_files() -> Dict[str, List[Dict[str, Any]]]:
    """Scan all phase files and categorize by status."""
    registry_root = Path("cortex-registry/_cortex-master")
    
    phases = {
        "active": [],
        "complete": [],
        "planned": []
    }
    
    # Scan active directory
    active_dir = registry_root / "phases" / "active"
    if active_dir.exists():
        for phase_file in active_dir.glob("*.yaml"):
            data = load_phase_yaml(phase_file)
            metadata = data.get('metadata', {})
            status = metadata.get('status', data.get('status', 'unknown'))
            
            phase_info = {
                'id': metadata.get('phase_id', phase_file.stem),
                'name': metadata.get('title', 'Unknown'),
                'file': f"phases/active/{phase_file.name}",
                'status': status.lower(),
                'priority': metadata.get('priority', 'P2'),
                'created': metadata.get('created_date', metadata.get('created', 'unknown'))
            }
            
            # Categorize by actual status in YAML
            if status.lower() in ['complete', 'completed']:
                phases['complete'].append(phase_info)
            elif status.lower() in ['active', 'in_progress']:
                phases['active'].append(phase_info)
            else:
                phases['planned'].append(phase_info)
    
    # Scan completed directory
    completed_dir = registry_root / "phases" / "completed"
    if completed_dir.exists():
        # Scan 2026 subdirectory
        completed_2026 = completed_dir / "2026"
        if completed_2026.exists():
            for phase_file in completed_2026.glob("*.yaml"):
                try:
                    data = load_phase_yaml(phase_file)
                    metadata = data.get('metadata', {})
                    
                    phase_info = {
                        'id': metadata.get('phase_id', phase_file.stem),
                        'name': metadata.get('title', 'Unknown'),
                        'file': f"phases/completed/2026/{phase_file.name}",
                        'status': 'complete',
                        'priority': metadata.get('priority', 'P2'),
                        'completed': metadata.get('completed', metadata.get('completed_date', 'unknown'))
                    }
                    phases['complete'].append(phase_info)
                except Exception as e:
                    print(f"⚠️  Warning: Could not process {phase_file.name}: {e}")
        
        # Scan root completed directory (for files not in subdirectories)
        for phase_file in completed_dir.glob("*.yaml"):
            try:
                data = load_phase_yaml(phase_file)
                metadata = data.get('metadata', {})
                
                phase_info = {
                    'id': metadata.get('phase_id', phase_file.stem),
                    'name': metadata.get('title', 'Unknown'),
                    'file': f"phases/completed/{phase_file.name}",
                    'status': 'complete',
                    'priority': metadata.get('priority', 'P2'),
                    'completed': metadata.get('completed', metadata.get('completed_date', 'unknown'))
                }
                phases['complete'].append(phase_info)
            except Exception as e:
                print(f"⚠️  Warning: Could not process {phase_file.name}: {e}")
    
    return phases


def generate_sync_report(phases: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate human-readable synchronization report."""
    report = []
    report.append("=" * 80)
    report.append("CORTEX Registry Synchronization Report")
    report.append(f"Generated: {datetime.now().isoformat()}")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    total = sum(len(phases[cat]) for cat in phases)
    report.append(f"📊 Phase Statistics:")
    report.append(f"   Total Phases: {total}")
    report.append(f"   ✅ Complete: {len(phases['complete'])}")
    report.append(f"   🔵 Active: {len(phases['active'])}")
    report.append(f"   ⚪ Planned: {len(phases['planned'])}")
    report.append("")
    
    # Complete phases
    if phases['complete']:
        report.append("✅ Complete Phases:")
        for phase in sorted(phases['complete'], key=lambda x: x['id']):
            report.append(f"   - {phase['id']}: {phase['name']}")
        report.append("")
    
    # Active phases
    if phases['active']:
        report.append("🔵 Active Phases:")
        for phase in sorted(phases['active'], key=lambda x: x['id']):
            report.append(f"   - {phase['id']}: {phase['name']}")
        report.append("")
    
    # Planned phases
    if phases['planned']:
        report.append("⚪ Planned Phases:")
        for phase in sorted(phases['planned'], key=lambda x: x['id']):
            report.append(f"   - {phase['id']}: {phase['name']}")
        report.append("")
    
    report.append("=" * 80)
    return "\n".join(report)


def main():
    """Main synchronization workflow."""
    print("🔍 Scanning phase files...")
    phases = scan_phase_files()
    
    print("\n" + generate_sync_report(phases))
    
    # Generate recommendation
    print("\n📋 Recommended Actions:")
    print(f"1. Move {len(phases['complete'])} complete phases to phases/completed/2026/")
    print(f"2. Update index.yaml active_phases to only include {len(phases['active'])} active phases")
    print(f"3. Update index.yaml completed_phases to include all {len(phases['complete'])} complete phases")
    print(f"4. Update statistics.active_phases = {len(phases['active'])}")
    print(f"5. Update statistics.completed_phases = {len(phases['complete'])}")
    print(f"6. Update statistics.total_phases = {len(phases['complete']) + len(phases['active']) + len(phases['planned'])}")
    
    return phases


if __name__ == "__main__":
    phases = main()

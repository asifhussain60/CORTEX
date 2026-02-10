#!/usr/bin/env python3
"""
Enhanced Vacuum Cleanup Script - Comprehensive Root Organization

Executes:
1. Folder cleanup (delete caches, consolidate duplicates)
2. Root file cleanup (archive Docker files, move reports)
3. Phase marker archival
4. Root reorganization
"""

import sys
import json
from pathlib import Path

# Add cortex to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator


def main():
    """Execute comprehensive vacuum cleanup."""
    print("\n" + "="*80)
    print("🧹 ENHANCED VACUUM CLEANUP - Root Organization & Consolidation")
    print("="*80)
    
    orchestrator = VacuumOrchestrator()
    root_path = "."
    
    # Step 1: Scan folders for cleanup
    print("\n[1/5] 📁 Scanning folders for cleanup opportunities...")
    folder_scan = orchestrator.scan_folders_for_cleanup(root_path)
    
    if folder_scan["status"] == "success":
        print(f"    ✅ Folders to delete: {folder_scan['summary']['total_for_deletion']}")
        print(f"    ⚠️  Folders to consolidate: {folder_scan['summary']['total_for_consolidation']}")
        
        for folder in folder_scan["folders_to_delete"]:
            print(f"       • {folder['name']} ({folder['size_human']}) - {folder['reason']}")
    
    # Step 2: Scan root-level files
    print("\n[2/5] 📄 Scanning root-level files...")
    root_scan = orchestrator.scan_root_level(root_path)
    
    if root_scan["status"] == "success":
        phase_markers = root_scan.get('phase_markers', [])
        if isinstance(phase_markers, dict):
            phase_markers = list(phase_markers.keys())
        
        print(f"    ✅ Phase markers: {len(phase_markers)}")
        print(f"    ⚠️  Recommendations: {len(root_scan['recommendations'])}")
        
        if phase_markers:
            for marker in phase_markers:
                if isinstance(marker, dict):
                    marker_name = marker.get('file', str(marker))
                else:
                    marker_name = marker
                print(f"       • {marker_name}")
    
    # Step 3: Execute folder cleanup
    print("\n[3/5] 🗑️  Executing folder cleanup (safe mode)...")
    folder_cleanup = orchestrator.execute_folder_cleanup(folder_scan, root_path, safe_mode=True)
    
    if folder_cleanup["status"] == "success":
        print(f"    ✅ Folders deleted: {folder_cleanup['folders_deleted']}")
        print(f"    ⚠️  Folders consolidated (planned): {folder_cleanup['folders_consolidated']}")
        if folder_cleanup["errors"]:
            for error in folder_cleanup["errors"]:
                print(f"    ⚠️  {error}")
    
    # Step 4: Archive phase markers and Docker files
    print("\n[4/5] 📦 Archiving phase markers and Docker files...")
    
    # Create archive directory
    archive_dir = Path(root_path) / "docs/archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Archive Docker files (if they exist)
    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "docker-compose.monitoring.yml",
        ".dockerignore",
    ]
    
    archived_docker = 0
    for docker_file in docker_files:
        docker_path = Path(root_path) / docker_file
        if docker_path.exists():
            deploy_docker_dir = Path(root_path) / "deployment/docker"
            deploy_docker_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            dest = deploy_docker_dir / docker_file
            shutil.move(str(docker_path), str(dest))
            archived_docker += 1
            print(f"    ✅ Moved {docker_file} to deployment/docker/")
    
    # Archive phase markers
    phase_archive_dir = archive_dir / "phase-markers"
    phase_archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived_phases = 0
    phase_markers = root_scan.get("phase_markers", [])
    if isinstance(phase_markers, dict):
        phase_markers = list(phase_markers.keys())
    
    for marker in phase_markers:
        if isinstance(marker, dict):
            marker_file = marker.get('file', str(marker))
        else:
            marker_file = marker
        
        marker_path = Path(root_path) / marker_file
        if marker_path.exists():
            import shutil
            dest = phase_archive_dir / marker_file
            shutil.move(str(marker_path), str(dest))
            archived_phases += 1
            print(f"    ✅ Archived {marker_file} to docs/archive/phase-markers/")
    
    # Archive .DS_Store (macOS)
    ds_store = Path(root_path) / ".DS_Store"
    if ds_store.exists():
        ds_store.unlink()
        print(f"    ✅ Deleted .DS_Store (macOS artifact)")
    
    # Archive .coverage
    coverage_file = Path(root_path) / ".coverage"
    if coverage_file.exists():
        reports_dir = Path(root_path) / "reports/coverage"
        reports_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        dest = reports_dir / ".coverage"
        shutil.move(str(coverage_file), str(dest))
        print(f"    ✅ Moved .coverage to reports/coverage/")
    
    # Step 5: Final verification
    print("\n[5/5] ✅ Verification & Summary...")
    
    # List remaining root files
    remaining_files = list(Path(root_path).glob("*"))
    remaining_files = [f for f in remaining_files if f.is_file()]
    remaining_dirs = list(Path(root_path).glob("*"))
    remaining_dirs = [d for d in remaining_dirs if d.is_dir() and not d.name.startswith(".")]
    
    print(f"\n    📊 Root-Level Summary:")
    print(f"       Files: {len(remaining_files)}")
    print(f"       Directories: {len(remaining_dirs)}")
    print(f"       Docker files moved: {archived_docker}")
    print(f"       Phase markers archived: {archived_phases}")
    
    # Final status
    print("\n" + "="*80)
    print("✅ VACUUM CLEANUP COMPLETE")
    print("="*80)
    print(f"""
Summary:
  • Deleted cache folders: {folder_cleanup['folders_deleted']}
  • Archived Docker files: {archived_docker}
  • Archived phase markers: {archived_phases}
  • Remaining root files: {len(remaining_files)}
  • Remaining directories: {len(remaining_dirs)}

Next Steps:
  1. Review consolidation recommendations
  2. Consider moving cortex_brain → cortex/brain
  3. Consider moving cortex_lens → cortex/lens
  4. Commit changes: git add -u && git commit -m "Vacuum: Clean root directory structure"
  5. Push: git push origin CORTEX
""")


if __name__ == "__main__":
    main()

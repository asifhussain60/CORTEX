"""
Plan Converter Orchestrator

Intelligently transforms plan folders into Planning System v5 compliant structures.
Auto-detects EPIC vs FEATURE mode and reorganizes folders accordingly.

Author: CORTEX v5
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import yaml


class PlanConverterOrchestrator:
    """
    Intelligent plan folder structure transformer.
    
    Features:
    - Auto-detect EPIC vs FEATURE mode
    - Transform .md features to folder hierarchies
    - Root cleanup (preserve only plan-viewer.html + CONTINUATION-PROMPT.md)
    - Generate missing folders/files
    - Update plan-viewer.html references
    - Atomic conversion with backup
    - Verification (no lost requirements)
    - Auto-cleanup successful backups
    """
    
    def __init__(self, plan_path: Path):
        """
        Initialize converter.
        
        Args:
            plan_path: Path to plan folder to convert
        """
        self.plan_path = Path(plan_path).resolve()
        self.plan_name = self.plan_path.name
        self.backup_path: Optional[Path] = None
        self.mode: Optional[str] = None  # 'EPIC' or 'FEATURE'
        self.conversion_log: List[str] = []
        
    def execute(self) -> Dict[str, Any]:
        """
        Execute plan conversion.
        
        Returns:
            Conversion report with status and changes
        """
        try:
            # Phase 1: Validation
            self._log("Phase 1: Validation")
            if not self.plan_path.exists():
                return self._error(f"Plan folder not found: {self.plan_path}")
            
            # Phase 2: Mode Detection
            self._log("Phase 2: Mode Detection")
            self.mode = self._detect_mode()
            self._log(f"Detected mode: {self.mode}")
            
            # Phase 3: Backup
            self._log("Phase 3: Creating backup")
            self.backup_path = self._create_backup()
            self._log(f"Backup created: {self.backup_path}")
            
            # Phase 4: Conversion
            self._log("Phase 4: Structure conversion")
            changes = self._convert_structure()
            
            # Phase 5: Verification
            self._log("Phase 5: Verification")
            verification = self._verify_conversion()
            
            if not verification['passed']:
                self._log(f"Verification FAILED: {verification['errors']}")
                self._rollback()
                return self._error(f"Verification failed: {verification['errors']}")
            
            # Phase 6: Cleanup
            self._log("Phase 6: Cleanup")
            if verification['passed']:
                self._cleanup_backup()
                self._log("Backup deleted (conversion successful)")
            
            return {
                'success': True,
                'plan_name': self.plan_name,
                'mode': self.mode,
                'changes': changes,
                'verification': verification,
                'log': self.conversion_log
            }
            
        except Exception as e:
            self._log(f"ERROR: {str(e)}")
            if self.backup_path and self.backup_path.exists():
                self._rollback()
            return self._error(str(e))
    
    def _detect_mode(self) -> str:
        """
        Detect EPIC vs FEATURE mode.
        
        Returns:
            'EPIC' or 'FEATURE'
        """
        epic_tracker = self.plan_path / "tracking" / "epic-progress-tracker.json"
        feature_tracker = self.plan_path / "tracking" / "progress-tracker.json"
        
        if epic_tracker.exists():
            return "EPIC"
        elif feature_tracker.exists():
            return "FEATURE"
        else:
            # Check for features/ folder as secondary indicator
            features_folder = self.plan_path / "features"
            if features_folder.exists():
                return "EPIC"
            return "FEATURE"
    
    def _create_backup(self) -> Path:
        """
        Create atomic backup of plan folder.
        
        Returns:
            Path to backup folder
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.plan_name}_backup_{timestamp}"
        backup_path = self.plan_path.parent / backup_name
        
        shutil.copytree(self.plan_path, backup_path)
        return backup_path
    
    def _convert_structure(self) -> Dict[str, Any]:
        """
        Convert plan structure based on mode.
        
        Returns:
            Dictionary of changes made
        """
        changes = {
            'folders_created': [],
            'files_moved': [],
            'files_renamed': [],
            'features_converted': [],
            'files_generated': []
        }
        
        # Create missing standard folders
        standard_folders = ['scripts', 'architecture']
        if self.mode == "EPIC":
            standard_folders.append('phases')
        
        for folder_name in standard_folders:
            folder_path = self.plan_path / folder_name
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                changes['folders_created'].append(folder_name)
                self._log(f"Created folder: {folder_name}/")
        
        # Convert features/ structure if EPIC mode
        if self.mode == "EPIC":
            features_changes = self._convert_features()
            changes['features_converted'] = features_changes
            
            # Populate phase folders in existing feature folders
            phase_changes = self._populate_feature_phases()
            changes['phase_folders_created'] = phase_changes
        
        # Reorganize root files
        root_changes = self._reorganize_root()
        changes['files_moved'].extend(root_changes)
        
        # Rename master-plan.md if exists
        master_plan = self.plan_path / "master-plan.md"
        target_name = f"00-{self.plan_name}.md"
        target_path = self.plan_path / target_name
        
        if master_plan.exists() and not target_path.exists():
            master_plan.rename(target_path)
            changes['files_renamed'].append(f"master-plan.md → {target_name}")
            self._log(f"Renamed: master-plan.md → {target_name}")
        
        # Generate launch_plan_viewer.py
        if not (self.plan_path / "launch_plan_viewer.py").exists():
            self._generate_launcher()
            changes['files_generated'].append("launch_plan_viewer.py")
        
        # Update plan-viewer.html if exists
        plan_viewer = self.plan_path / "plan-viewer.html"
        if plan_viewer.exists():
            self._update_plan_viewer_references(target_name)
            self._log("Updated plan-viewer.html references")
        
        return changes
    
    def _convert_features(self) -> List[str]:
        """
        Convert feature .md files to folder structures with phases/.
        
        Returns:
            List of converted feature names
        """
        features_folder = self.plan_path / "features"
        if not features_folder.exists():
            return []
        
        converted = []
        
        for item in features_folder.iterdir():
            if item.is_file() and item.suffix == '.md':
                feature_name = item.stem
                feature_folder = features_folder / feature_name
                
                # Create feature folder structure
                feature_folder.mkdir(exist_ok=True)
                phases_folder = feature_folder / "phases"
                phases_folder.mkdir(exist_ok=True)
                (feature_folder / "analysis").mkdir(exist_ok=True)
                (feature_folder / "artifacts").mkdir(exist_ok=True)
                (feature_folder / "context").mkdir(exist_ok=True)
                (feature_folder / "reports").mkdir(exist_ok=True)
                (feature_folder / "tracking").mkdir(exist_ok=True)
                
                # Create standard phase subfolders (phase-0 through phase-3)
                for phase_num in range(4):
                    phase_folder = phases_folder / f"phase-{phase_num}"
                    phase_folder.mkdir(exist_ok=True)
                    (phase_folder / "artifacts").mkdir(exist_ok=True)
                    (phase_folder / "reports").mkdir(exist_ok=True)
                    (phase_folder / "tracking").mkdir(exist_ok=True)
                    self._log(f"Created phase-{phase_num}/ in {feature_name}")
                
                # Move .md file into context/
                target = feature_folder / "context" / item.name
                shutil.move(str(item), str(target))
                
                converted.append(feature_name)
                self._log(f"Converted feature: {feature_name}")
        
        return converted
    
    def _populate_feature_phases(self) -> List[str]:
        """
        Populate phase subfolders in existing feature folders.
        
        Returns:
            List of features with phases populated
        """
        features_folder = self.plan_path / "features"
        if not features_folder.exists():
            return []
        
        populated = []
        
        for feature_folder in features_folder.iterdir():
            if feature_folder.is_dir():
                phases_folder = feature_folder / "phases"
                if phases_folder.exists() and not any(phases_folder.iterdir()):
                    # phases/ folder exists but is empty - populate it
                    for phase_num in range(4):
                        phase_folder = phases_folder / f"phase-{phase_num}"
                        if not phase_folder.exists():
                            phase_folder.mkdir(exist_ok=True)
                            (phase_folder / "artifacts").mkdir(exist_ok=True)
                            (phase_folder / "reports").mkdir(exist_ok=True)
                            (phase_folder / "tracking").mkdir(exist_ok=True)
                            self._log(f"Created phase-{phase_num}/ in {feature_folder.name}")
                    
                    populated.append(feature_folder.name)
        
        return populated
    
    def _reorganize_root(self) -> List[str]:
        """
        Clean root folder - only plan-viewer.html + CONTINUATION-PROMPT.md allowed.
        
        Returns:
            List of files moved
        """
        moved = []
        allowed_root_files = {'plan-viewer.html', 'CONTINUATION-PROMPT.md', 'launch_plan_viewer.py'}
        
        # Add renamed master plan to allowed files
        renamed_master = f"00-{self.plan_name}.md"
        allowed_root_files.add(renamed_master)
        
        for item in self.plan_path.iterdir():
            if item.is_file() and item.name not in allowed_root_files:
                # Determine target folder
                if item.suffix == '.md':
                    target_folder = self.plan_path / "reports"
                elif item.suffix in ['.json', '.yaml', '.yml']:
                    target_folder = self.plan_path / "tracking"
                elif item.suffix in ['.py', '.sh', '.ps1']:
                    target_folder = self.plan_path / "scripts"
                else:
                    target_folder = self.plan_path / "artifacts"
                
                target_folder.mkdir(parents=True, exist_ok=True)
                target = target_folder / item.name
                
                if not target.exists():
                    shutil.move(str(item), str(target))
                    moved.append(f"{item.name} → {target_folder.name}/")
                    self._log(f"Moved: {item.name} → {target_folder.name}/")
        
        return moved
    
    def _generate_launcher(self) -> None:
        """Generate launch_plan_viewer.py script."""
        launcher_content = f'''#!/usr/bin/env python3
"""
Plan Viewer Launcher for {self.plan_name}

Auto-generated by Plan Converter Orchestrator.
Launches HTTP server for plan-viewer.html on port 8000-8010.
"""

import http.server
import socketserver
import os
from pathlib import Path

def find_available_port(start_port=8000, end_port=8010):
    """Find first available port in range."""
    for port in range(start_port, end_port + 1):
        try:
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as test_server:
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports in range {{start_port}}-{{end_port}}")

if __name__ == "__main__":
    # Change to plan folder
    plan_folder = Path(__file__).parent
    os.chdir(plan_folder)
    
    # Find available port
    port = find_available_port()
    
    # Start server
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"🚀 Plan Viewer Server Started")
        print(f"📊 URL: http://localhost:{{port}}/plan-viewer.html")
        print(f"📁 Serving: {{plan_folder}}")
        print(f"🛑 Press Ctrl+C to stop")
        httpd.serve_forever()
'''
        
        launcher_path = self.plan_path / "launch_plan_viewer.py"
        launcher_path.write_text(launcher_content)
        launcher_path.chmod(0o755)
        self._log("Generated launch_plan_viewer.py")
    
    def _update_plan_viewer_references(self, new_master_plan_name: str) -> None:
        """
        Update plan-viewer.html references to match new structure.
        
        Args:
            new_master_plan_name: New name for master plan file
        """
        plan_viewer = self.plan_path / "plan-viewer.html"
        if not plan_viewer.exists():
            return
        
        content = plan_viewer.read_text()
        
        # Update master-plan.md reference
        content = content.replace(
            "{ name: 'master-plan.md'",
            f"{{ name: '{new_master_plan_name}'"
        )
        content = content.replace(
            "path: 'master-plan.md'",
            f"path: '{new_master_plan_name}'"
        )
        
        plan_viewer.write_text(content)
    
    def _verify_conversion(self) -> Dict[str, Any]:
        """
        Verify conversion success - no requirements lost.
        
        Returns:
            Verification report
        """
        errors = []
        warnings = []
        
        # Check required folders exist
        required_folders = ['analysis', 'artifacts', 'context', 'reports', 'tracking', 'scripts', 'architecture']
        if self.mode == "EPIC":
            required_folders.extend(['features', 'phases'])
        
        for folder in required_folders:
            if not (self.plan_path / folder).exists():
                errors.append(f"Missing required folder: {folder}/")
        
        # Check root cleanup
        allowed_root = {'plan-viewer.html', 'CONTINUATION-PROMPT.md', 'launch_plan_viewer.py', f'00-{self.plan_name}.md'}
        root_files = [f.name for f in self.plan_path.iterdir() if f.is_file()]
        unexpected_root = set(root_files) - allowed_root
        
        if unexpected_root:
            warnings.append(f"Unexpected root files: {', '.join(unexpected_root)}")
        
        # Check progress tracker exists
        if self.mode == "EPIC":
            tracker = self.plan_path / "tracking" / "epic-progress-tracker.json"
        else:
            tracker = self.plan_path / "tracking" / "progress-tracker.json"
        
        if not tracker.exists():
            errors.append(f"Missing progress tracker: {tracker.name}")
        
        # Verify feature folders if EPIC
        if self.mode == "EPIC":
            features_folder = self.plan_path / "features"
            if features_folder.exists():
                for feature in features_folder.iterdir():
                    if feature.is_dir():
                        required_subfolders = ['phases', 'analysis', 'artifacts', 'context', 'reports', 'tracking']
                        for subfolder in required_subfolders:
                            if not (feature / subfolder).exists():
                                errors.append(f"Missing {subfolder}/ in feature: {feature.name}")
                        
                        # Check that phases/ folder has phase subfolders
                        phases_folder = feature / "phases"
                        if phases_folder.exists():
                            phase_subfolders = [f for f in phases_folder.iterdir() if f.is_dir() and f.name.startswith('phase-')]
                            if len(phase_subfolders) == 0:
                                warnings.append(f"Empty phases/ folder in feature: {feature.name}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _rollback(self) -> None:
        """Rollback to backup if conversion failed."""
        if self.backup_path and self.backup_path.exists():
            self._log(f"Rolling back to backup: {self.backup_path}")
            
            # Remove failed conversion
            if self.plan_path.exists():
                shutil.rmtree(self.plan_path)
            
            # Restore backup
            shutil.copytree(self.backup_path, self.plan_path)
            self._log("Rollback complete")
    
    def _cleanup_backup(self) -> None:
        """Delete backup after successful conversion."""
        if self.backup_path and self.backup_path.exists():
            shutil.rmtree(self.backup_path)
    
    def _log(self, message: str) -> None:
        """Add message to conversion log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.conversion_log.append(f"[{timestamp}] {message}")
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Return error response."""
        return {
            'success': False,
            'error': message,
            'log': self.conversion_log
        }


def convert_plan(plan_path: str) -> Dict[str, Any]:
    """
    Convert plan folder to Planning System v5 structure.
    
    Args:
        plan_path: Path to plan folder
    
    Returns:
        Conversion report
    """
    orchestrator = PlanConverterOrchestrator(Path(plan_path))
    return orchestrator.execute()

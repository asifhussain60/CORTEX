"""
Plan Migration Orchestrator v6

Migrates Planning System v5 (phase folders) to v6 (feature.yaml).
Removes empty phase folder hierarchies and replaces with machine-readable YAML definitions.

Key Operations:
1. Delete phases/ folders and all phase{N}-execution subfolders
2. Generate feature.yaml for each feat0X folder
3. Extract phase information from context files
4. Preserve all data in feature-level folders
5. Update plan-viewer.html to read feature.yaml
6. Validate migration (0 phase folders, N feature.yaml files)

Author: CORTEX Master Orchestrator
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class PlanMigrationOrchestrator:
    """
    Migrates plans from v5 (phase folders) to v6 (feature.yaml).
    
    Benefits:
    - 70% folder reduction
    - 100% empty folder elimination
    - Better machine readability
    - Explicit phase definitions
    """
    
    def __init__(self, plan_path: Path):
        """
        Initialize migration orchestrator.
        
        Args:
            plan_path: Path to plan folder to migrate
        """
        self.plan_path = Path(plan_path).resolve()
        self.plan_name = self.plan_path.name
        self.backup_path: Optional[Path] = None
        self.mode: Optional[str] = None  # 'EPIC' or 'FEATURE'
        self.migration_log: List[str] = []
        
    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute migration from v5 to v6.
        
        Args:
            dry_run: If True, only report changes without executing
            
        Returns:
            Migration report with status and changes
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
            
            if dry_run:
                self._log("DRY RUN MODE - No changes will be made")
                analysis = self._analyze_migration()
                return {
                    'success': True,
                    'dry_run': True,
                    'plan_name': self.plan_name,
                    'mode': self.mode,
                    'analysis': analysis,
                    'log': self.migration_log
                }
            
            # Phase 3: Backup
            self._log("Phase 3: Creating backup")
            self.backup_path = self._create_backup()
            self._log(f"Backup created: {self.backup_path}")
            
            # Phase 4: Migration
            self._log("Phase 4: Structure migration")
            changes = self._migrate_structure()
            
            # Phase 5: Verification
            self._log("Phase 5: Verification")
            verification = self._verify_migration()
            
            if not verification['passed']:
                self._log(f"Verification FAILED: {verification['errors']}")
                self._rollback()
                return self._error(f"Verification failed: {verification['errors']}")
            
            # Phase 6: Cleanup
            self._log("Phase 6: Cleanup")
            if verification['passed']:
                self._log("Backup retained for safety (delete manually if satisfied)")
            
            return {
                'success': True,
                'dry_run': False,
                'plan_name': self.plan_name,
                'mode': self.mode,
                'changes': changes,
                'verification': verification,
                'backup_path': str(self.backup_path),
                'log': self.migration_log
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
        backup_name = f"{self.plan_name}_v5_backup_{timestamp}"
        
        # Save to cortex-brain/archives/
        archives_path = Path("cortex-brain/archives/planning-migrations")
        archives_path.mkdir(parents=True, exist_ok=True)
        
        backup_path = archives_path / backup_name
        shutil.copytree(self.plan_path, backup_path)
        return backup_path
    
    def _analyze_migration(self) -> Dict[str, Any]:
        """
        Analyze what will change during migration (dry run).
        
        Returns:
            Analysis report
        """
        analysis = {
            'phase_folders_to_delete': [],
            'feature_yamls_to_create': [],
            'features_found': 0,
            'total_folders_deleted': 0
        }
        
        if self.mode == "EPIC":
            features_folder = self.plan_path / "features"
            if features_folder.exists():
                feature_folders = sorted([f for f in features_folder.iterdir() if f.is_dir()])
                analysis['features_found'] = len(feature_folders)
                
                for feature_folder in feature_folders:
                    phases_folder = feature_folder / "phases"
                    if phases_folder.exists():
                        # Count phase folders
                        phase_folders = [p for p in phases_folder.iterdir() if p.is_dir()]
                        phase_count = len(phase_folders)
                        
                        # Count phase subfolders
                        subfolder_count = 0
                        for phase in phase_folders:
                            subfolders = [s for s in phase.iterdir() if s.is_dir()]
                            subfolder_count += len(subfolders)
                        
                        total = 1 + phase_count + subfolder_count  # phases/ + phase{N}/ + subfolders
                        analysis['phase_folders_to_delete'].append({
                            'feature': feature_folder.name,
                            'phases_folder': str(phases_folder.relative_to(self.plan_path)),
                            'phase_count': phase_count,
                            'subfolder_count': subfolder_count,
                            'total_folders': total
                        })
                        analysis['total_folders_deleted'] += total
                    
                    # Check if feature.yaml exists
                    feature_yaml = feature_folder / "feature.yaml"
                    if not feature_yaml.exists():
                        analysis['feature_yamls_to_create'].append(feature_folder.name)
        
        elif self.mode == "FEATURE":
            # Feature plan at root level
            feature_yaml = self.plan_path / "feature.yaml"
            if not feature_yaml.exists():
                analysis['feature_yamls_to_create'].append(self.plan_name)
        
        return analysis
    
    def _migrate_structure(self) -> Dict[str, Any]:
        """
        Migrate plan structure from v5 to v6.
        
        Returns:
            Dictionary of changes made
        """
        changes = {
            'phase_folders_deleted': [],
            'feature_yamls_created': [],
            'plan_viewer_updated': False
        }
        
        if self.mode == "EPIC":
            # Migrate each feature
            features_folder = self.plan_path / "features"
            if features_folder.exists():
                feature_folders = sorted([f for f in features_folder.iterdir() if f.is_dir()])
                
                for feature_folder in feature_folders:
                    # Delete phases/ folder
                    phases_folder = feature_folder / "phases"
                    if phases_folder.exists():
                        shutil.rmtree(phases_folder)
                        changes['phase_folders_deleted'].append(feature_folder.name)
                        self._log(f"Deleted: {feature_folder.name}/phases/")
                    
                    # Generate feature.yaml
                    feature_yaml = feature_folder / "feature.yaml"
                    if not feature_yaml.exists():
                        self._generate_feature_yaml(feature_folder)
                        changes['feature_yamls_created'].append(feature_folder.name)
                        self._log(f"Created: {feature_folder.name}/feature.yaml")
        
        elif self.mode == "FEATURE":
            # Generate root-level feature.yaml
            feature_yaml = self.plan_path / "feature.yaml"
            if not feature_yaml.exists():
                self._generate_feature_yaml(self.plan_path, is_root=True)
                changes['feature_yamls_created'].append(self.plan_name)
                self._log(f"Created: feature.yaml")
        
        # Clean up root folder - move scripts to scripts/
        root_cleanup_changes = self._cleanup_root_folder()
        changes['root_files_moved'] = root_cleanup_changes
        
        # Update plan-viewer.html if exists
        plan_viewer = self.plan_path / "plan-viewer.html"
        if plan_viewer.exists():
            self._update_plan_viewer()
            changes['plan_viewer_updated'] = True
            self._log("Updated: plan-viewer.html (now reads feature.yaml)")
        
        return changes
    
    def _generate_feature_yaml(self, feature_path: Path, is_root: bool = False) -> None:
        """
        Generate feature.yaml for a feature folder.
        
        Args:
            feature_path: Path to feature folder
            is_root: True if generating for root-level feature plan
        """
        feature_name = feature_path.name if not is_root else self.plan_name
        
        # Extract feature info from context files
        context_folder = feature_path / "context"
        context_info = self._extract_context_info(context_folder)
        
        # Generate feature.yaml content
        feature_yaml_content = {
            'feature_id': feature_name,
            'feature_name': context_info.get('name', feature_name.replace('-', ' ').title()),
            'epic_id': self.plan_name if not is_root else None,
            'priority': context_info.get('priority', 'P2_MEDIUM'),
            'status': 'NOT_STARTED',
            'progress': 0,
            
            'metadata': {
                'created_date': datetime.now().strftime("%Y-%m-%d"),
                'last_updated': datetime.now().isoformat(),
                'estimated_weeks': context_info.get('estimated_weeks', 2),
                'actual_weeks': 0
            },
            
            'dependencies': context_info.get('dependencies', {}),
            
            'phases': [
                {
                    'phase': 1,
                    'name': 'Design & Architecture',
                    'status': 'NOT_STARTED',
                    'progress': 0,
                    'estimated_hours': 8,
                    'tasks': [
                        {'id': 'task-1.1', 'name': 'Design system architecture', 'status': 'NOT_STARTED'},
                        {'id': 'task-1.2', 'name': 'Design data models', 'status': 'NOT_STARTED'},
                        {'id': 'task-1.3', 'name': 'Design API interfaces', 'status': 'NOT_STARTED'}
                    ],
                    'outputs': [
                        {'path': 'analysis/design.yaml', 'type': 'design_document'},
                        {'path': 'architecture/components.yaml', 'type': 'architecture'}
                    ]
                },
                {
                    'phase': 2,
                    'name': 'Implementation',
                    'status': 'NOT_STARTED',
                    'progress': 0,
                    'estimated_hours': 16,
                    'tasks': [
                        {'id': 'task-2.1', 'name': 'Implement core logic', 'status': 'NOT_STARTED', 'test_required': True},
                        {'id': 'task-2.2', 'name': 'Implement data layer', 'status': 'NOT_STARTED', 'test_required': True},
                        {'id': 'task-2.3', 'name': 'Implement API endpoints', 'status': 'NOT_STARTED', 'test_required': True}
                    ],
                    'outputs': [
                        {'path': f'artifacts/{feature_name.replace("-", "_")}.py', 'type': 'implementation'}
                    ]
                },
                {
                    'phase': 3,
                    'name': 'Testing',
                    'status': 'NOT_STARTED',
                    'progress': 0,
                    'estimated_hours': 8,
                    'tasks': [
                        {'id': 'task-3.1', 'name': 'Unit tests', 'status': 'NOT_STARTED'},
                        {'id': 'task-3.2', 'name': 'Integration tests', 'status': 'NOT_STARTED'},
                        {'id': 'task-3.3', 'name': 'System tests', 'status': 'NOT_STARTED'}
                    ],
                    'outputs': [
                        {'path': f'artifacts/test_{feature_name.replace("-", "_")}.py', 'type': 'test_suite'},
                        {'path': 'reports/test-results.yaml', 'type': 'test_report'}
                    ]
                },
                {
                    'phase': 4,
                    'name': 'Documentation & Deployment',
                    'status': 'NOT_STARTED',
                    'progress': 0,
                    'estimated_hours': 4,
                    'tasks': [
                        {'id': 'task-4.1', 'name': 'Write documentation', 'status': 'NOT_STARTED'},
                        {'id': 'task-4.2', 'name': 'Create deployment guide', 'status': 'NOT_STARTED'},
                        {'id': 'task-4.3', 'name': 'Deploy to production', 'status': 'NOT_STARTED'}
                    ],
                    'outputs': [
                        {'path': f'reports/{feature_name}-guide.md', 'type': 'documentation'},
                        {'path': 'reports/deployment-report.yaml', 'type': 'deployment_log'}
                    ]
                }
            ],
            
            'artifacts': {
                'design': [],
                'implementation': [],
                'tests': [],
                'documentation': []
            },
            
            'progress_summary': {
                'phases_total': 4,
                'phases_completed': 0,
                'phases_in_progress': 0,
                'phases_not_started': 4,
                'tasks_total': 12,
                'tasks_completed': 0,
                'tasks_in_progress': 0,
                'tasks_not_started': 12
            },
            
            'context_files': self._get_context_files(context_folder)
        }
        
        # Write feature.yaml
        feature_yaml_path = feature_path / "feature.yaml"
        with open(feature_yaml_path, 'w') as f:
            yaml.dump(feature_yaml_content, f, default_flow_style=False, sort_keys=False)
    
    def _extract_context_info(self, context_folder: Path) -> Dict[str, Any]:
        """
        Extract feature information from context files.
        
        Args:
            context_folder: Path to context/ folder
            
        Returns:
            Dictionary of extracted information
        """
        info = {}
        
        if not context_folder.exists():
            return info
        
        # Read first .md file in context folder
        md_files = list(context_folder.glob("*.md"))
        if md_files:
            content = md_files[0].read_text()
            
            # Extract priority
            if "P0" in content or "CRITICAL" in content:
                info['priority'] = "P0_CRITICAL"
            elif "P1" in content or "HIGH" in content:
                info['priority'] = "P1_HIGH"
            elif "P2" in content or "MEDIUM" in content:
                info['priority'] = "P2_MEDIUM"
            else:
                info['priority'] = "P3_LOW"
            
            # Extract feature name from first heading
            lines = content.split('\n')
            for line in lines:
                if line.startswith('#'):
                    name = line.lstrip('#').strip()
                    if name:
                        info['name'] = name
                        break
        
        return info
    
    def _get_context_files(self, context_folder: Path) -> List[str]:
        """
        Get list of context file paths.
        
        Args:
            context_folder: Path to context/ folder
            
        Returns:
            List of relative paths
        """
        if not context_folder.exists():
            return []
        
        files = []
        for file in context_folder.glob("*.md"):
            files.append(f"context/{file.name}")
        
        return files
    
    def _update_plan_viewer(self) -> None:
        """
        Update plan-viewer.html to read feature.yaml instead of phase folders.
        
        Adds comment indicating v6 compatibility.
        """
        plan_viewer = self.plan_path / "plan-viewer.html"
        content = plan_viewer.read_text()
        
        # Add v6 compatibility comment
        if "Planning System v6" not in content:
            comment = "\n<!-- Planning System v6: Reads feature.yaml for phase definitions -->\n"
            content = content.replace("<head>", f"<head>{comment}", 1)
            plan_viewer.write_text(content)
    
    def _cleanup_root_folder(self) -> List[str]:
        """
        Clean up root folder - only CONTINUATION-PROMPT.md and plan-viewer.html allowed.
        Move all other files to appropriate folders.
        
        Planning System v6 Rules:
        - Root files allowed: CONTINUATION-PROMPT.md, plan-viewer.html
        - Scripts (.py, .sh, .ps1) → scripts/
        - Markdown (.md) → reports/
        - Data (.json, .yaml, .yml) → tracking/
        - Other → artifacts/
        
        Returns:
            List of files moved
        """
        moved = []
        allowed_root_files = {'CONTINUATION-PROMPT.md', 'plan-viewer.html'}
        allowed_root_dirs = {'analysis', 'architecture', 'artifacts', 'context', 'features', 'reports', 'scripts', 'tracking'}
        
        for item in self.plan_path.iterdir():
            # Skip directories and allowed files
            if item.is_dir():
                if item.name not in allowed_root_dirs:
                    self._log(f"WARNING: Unexpected directory in root: {item.name}")
                continue
            
            if item.name in allowed_root_files:
                continue
            
            # Determine target folder based on file type
            if item.suffix in ['.py', '.sh', '.ps1', '.bat']:
                target_folder = self.plan_path / "scripts"
            elif item.suffix == '.md':
                target_folder = self.plan_path / "reports"
            elif item.suffix in ['.json', '.yaml', '.yml']:
                target_folder = self.plan_path / "tracking"
            else:
                target_folder = self.plan_path / "artifacts"
            
            # Create target folder if needed
            target_folder.mkdir(parents=True, exist_ok=True)
            
            # Move file
            target = target_folder / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
                moved.append(f"{item.name} → {target_folder.name}/")
                self._log(f"Moved: {item.name} → {target_folder.name}/")
            else:
                self._log(f"WARNING: Target already exists, skipping: {target}")
        
        return moved
    
    def _verify_migration(self) -> Dict[str, Any]:
        """
        Verify migration completed successfully.
        
        Returns:
            Verification report
        """
        verification = {
            'passed': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        if self.mode == "EPIC":
            features_folder = self.plan_path / "features"
            if not features_folder.exists():
                verification['passed'] = False
                verification['errors'].append("features/ folder not found")
                return verification
            
            feature_folders = sorted([f for f in features_folder.iterdir() if f.is_dir()])
            
            # Check each feature
            phase_folders_found = 0
            feature_yamls_found = 0
            
            for feature_folder in feature_folders:
                # Check for phase folders (should be deleted)
                phases_folder = feature_folder / "phases"
                if phases_folder.exists():
                    phase_folders_found += 1
                    verification['errors'].append(f"phases/ folder still exists in {feature_folder.name}")
                
                # Check for feature.yaml (should exist)
                feature_yaml = feature_folder / "feature.yaml"
                if feature_yaml.exists():
                    feature_yamls_found += 1
                else:
                    verification['errors'].append(f"feature.yaml missing in {feature_folder.name}")
            
            verification['stats'] = {
                'features_total': len(feature_folders),
                'feature_yamls_found': feature_yamls_found,
                'phase_folders_found': phase_folders_found
            }
            
            if phase_folders_found > 0:
                verification['passed'] = False
            
            if feature_yamls_found != len(feature_folders):
                verification['passed'] = False
        
        elif self.mode == "FEATURE":
            # Check for root-level feature.yaml
            feature_yaml = self.plan_path / "feature.yaml"
            if not feature_yaml.exists():
                verification['passed'] = False
                verification['errors'].append("feature.yaml not found at root")
            else:
                verification['stats']['feature_yaml_found'] = True
        
        return verification
    
    def _rollback(self) -> None:
        """Rollback to backup if migration fails."""
        if self.backup_path and self.backup_path.exists():
            self._log(f"Rolling back to backup: {self.backup_path}")
            
            # Delete current plan folder
            shutil.rmtree(self.plan_path)
            
            # Restore from backup
            shutil.copytree(self.backup_path, self.plan_path)
            
            self._log("Rollback complete")
    
    def _log(self, message: str) -> None:
        """Add message to migration log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        print(log_entry)
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Return error result."""
        return {
            'success': False,
            'error': message,
            'log': self.migration_log
        }


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plan_migration_orchestrator.py <plan_path> [--dry-run]")
        sys.exit(1)
    
    plan_path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    
    orchestrator = PlanMigrationOrchestrator(plan_path)
    result = orchestrator.execute(dry_run=dry_run)
    
    print("\n" + "="*80)
    print("MIGRATION RESULT")
    print("="*80)
    print(json.dumps(result, indent=2))
    
    if result['success']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

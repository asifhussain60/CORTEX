"""
Smart Remediation Engine for System Alignment

Generates fix templates, provides before/after previews,
coordinates user confirmation, and applies fixes safely
with git checkpoint rollback capability.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FixTemplate:
    """Template for fixing a specific conflict."""
    conflict_id: str
    fix_type: str  # 'file_move', 'code_edit', 'yaml_update', 'delete'
    description: str
    before_state: str
    after_state: str
    commands: List[str]  # Shell commands to execute
    affected_files: List[Path]
    reversible: bool
    risk_level: str  # 'low', 'medium', 'high'


class RemediationEngine:
    """
    Smart remediation engine for CORTEX conflicts.
    
    Features:
    - Generates fix templates for each conflict type
    - Shows before/after preview
    - Requests user confirmation
    - Creates git checkpoint before changes
    - Applies fixes atomically
    - Provides rollback on failure
    """
    
    def __init__(self, project_root: Path):
        """Initialize remediation engine."""
        self.project_root = project_root
        self.checkpoint_created = False
        self.checkpoint_sha: Optional[str] = None
    
    def generate_fix_template(self, conflict: 'Conflict') -> Optional[FixTemplate]:
        """
        Generate fix template for a conflict.
        
        Args:
            conflict: Detected conflict
            
        Returns:
            FixTemplate with remediation steps or None if not fixable
        """
        if conflict.conflict_type == 'drift':
            return self._generate_drift_fix(conflict)
        elif conflict.conflict_type == 'orphaned_wiring':
            return self._generate_orphaned_wiring_fix(conflict)
        elif conflict.conflict_type == 'duplicate_module':
            return self._generate_duplicate_fix(conflict)
        elif conflict.conflict_type == 'missing_dependency':
            return self._generate_dependency_fix(conflict)
        
        return None
    
    def _generate_drift_fix(self, conflict: 'Conflict') -> FixTemplate:
        """Generate fix for architectural drift."""
        source_file = conflict.affected_files[0]
        
        # Extract suggested location from conflict description
        # e.g., "Move file.py to one of: src/operations/modules"
        suggested_dir = self._extract_suggested_dir(conflict.suggested_fix)
        
        if not suggested_dir:
            return None
        
        target_file = suggested_dir / source_file.name
        
        return FixTemplate(
            conflict_id=conflict.title,
            fix_type='file_move',
            description=f"Move {source_file.name} to correct directory",
            before_state=f"Location: {source_file.relative_to(self.project_root)}",
            after_state=f"Location: {target_file.relative_to(self.project_root)}",
            commands=[
                f"git mv {source_file} {target_file}",
                "# Update imports in affected files (manual step)"
            ],
            affected_files=[source_file, target_file],
            reversible=True,
            risk_level='medium'
        )
    
    def _generate_orphaned_wiring_fix(self, conflict: 'Conflict') -> FixTemplate:
        """Generate fix for orphaned wiring."""
        # Extract trigger name from title
        trigger = conflict.title.replace("Orphaned trigger: ", "").strip("'")
        
        # Generate scaffold for missing orchestrator
        class_name = self._trigger_to_class_name(trigger)
        file_name = self._class_to_filename(class_name)
        
        # Determine appropriate directory based on trigger type
        if 'admin' in trigger.lower() or 'deploy' in trigger.lower() or 'align' in trigger.lower():
            target_dir = self.project_root / "src" / "operations" / "modules" / "admin"
        else:
            target_dir = self.project_root / "src" / "operations" / "modules" / file_name.replace("_orchestrator.py", "")
        
        target_file = target_dir / file_name
        
        # Ensure target_file is within project_root
        try:
            rel_path = target_file.relative_to(self.project_root)
            after_state_msg = f"New file: {rel_path}"
        except ValueError:
            # If path calculation fails, use absolute path
            after_state_msg = f"New file: {target_file}"
        
        scaffold_code = self._generate_orchestrator_scaffold(class_name, trigger)
        
        return FixTemplate(
            conflict_id=conflict.title,
            fix_type='code_edit',
            description=f"Create missing orchestrator for trigger '{trigger}'",
            before_state="Trigger exists in YAML but no implementation",
            after_state=after_state_msg,
            commands=[
                f"mkdir -p {target_dir}",
                f"# Create {file_name} with scaffold code (see preview)"
            ],
            affected_files=[target_file],
            reversible=True,
            risk_level='low'
        )
    
    def _generate_duplicate_fix(self, conflict: 'Conflict') -> FixTemplate:
        """Generate fix for duplicate module names."""
        files = conflict.affected_files
        
        # Strategy: Keep first file, rename others
        keep_file = files[0]
        rename_files = files[1:]
        
        commands = []
        for idx, file_path in enumerate(rename_files, start=2):
            new_name = file_path.stem + f"_v{idx}" + file_path.suffix
            new_path = file_path.parent / new_name
            commands.append(f"git mv {file_path} {new_path}")
        
        return FixTemplate(
            conflict_id=conflict.title,
            fix_type='file_move',
            description=f"Resolve duplicate class names by renaming",
            before_state=f"{len(files)} files with same class name",
            after_state=f"Keep {keep_file.name}, rename others with _v2, _v3 suffix",
            commands=commands,
            affected_files=files,
            reversible=True,
            risk_level='medium'
        )
    
    def _generate_dependency_fix(self, conflict: 'Conflict') -> FixTemplate:
        """Generate fix for missing dependencies."""
        # Extract module name from title
        module_name = conflict.title.replace("Unresolved import: ", "").strip()
        
        return FixTemplate(
            conflict_id=conflict.title,
            fix_type='code_edit',
            description=f"Fix unresolved import: {module_name}",
            before_state=f"Import statement: from {module_name} import ...",
            after_state="Import statement corrected or module created",
            commands=[
                "# Manual fix required:",
                f"# 1. Check if '{module_name}' path is correct",
                f"# 2. Create missing module if needed",
                f"# 3. Update import statement"
            ],
            affected_files=conflict.affected_files,
            reversible=True,
            risk_level='high'
        )
    
    def preview_fix(self, fix_template: FixTemplate) -> str:
        """
        Generate human-readable preview of fix.
        
        Returns:
            Formatted preview string
        """
        lines = [
            "",
            "=" * 80,
            f"FIX PREVIEW: {fix_template.description}",
            "=" * 80,
            "",
            f"Risk Level: {fix_template.risk_level.upper()}",
            f"Reversible: {'Yes' if fix_template.reversible else 'No'}",
            "",
            "BEFORE:",
            "-" * 80,
            fix_template.before_state,
            "",
            "AFTER:",
            "-" * 80,
            fix_template.after_state,
            "",
            "COMMANDS TO EXECUTE:",
            "-" * 80
        ]
        
        for cmd in fix_template.commands:
            lines.append(f"  {cmd}")
        
        lines.extend([
            "",
            "AFFECTED FILES:",
            "-" * 80
        ])
        
        for file_path in fix_template.affected_files:
            try:
                rel_path = file_path.relative_to(self.project_root)
                lines.append(f"  {rel_path}")
            except ValueError:
                lines.append(f"  {file_path}")
        
        lines.append("=" * 80)
        lines.append("")
        
        return "\n".join(lines)
    
    def request_confirmation(self, fix_template: FixTemplate) -> bool:
        """
        Request user confirmation for fix.
        
        Returns:
            True if user confirms, False otherwise
        """
        preview = self.preview_fix(fix_template)
        print(preview)
        
        response = input("Apply this fix? [y/N]: ").strip().lower()
        return response == 'y'
    
    def create_checkpoint(self) -> bool:
        """
        Create git checkpoint before applying fixes.
        
        Returns:
            True if checkpoint created successfully
        """
        if self.checkpoint_created:
            logger.info("Git checkpoint already exists")
            return True
        
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                logger.warning("⚠️ Uncommitted changes detected")
                response = input("Create checkpoint with uncommitted changes? [y/N]: ").strip().lower()
                if response != 'y':
                    return False
            
            # Create checkpoint commit
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            message = f"CORTEX Align: Pre-remediation checkpoint {timestamp}"
            
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                check=True
            )
            
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.project_root,
                check=True
            )
            
            # Get commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.checkpoint_sha = result.stdout.strip()
            self.checkpoint_created = True
            
            logger.info(f"✅ Created checkpoint: {self.checkpoint_sha[:8]}")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create checkpoint: {e}")
            return False
    
    def apply_fix(self, fix_template: FixTemplate) -> bool:
        """
        Apply fix atomically.
        
        Returns:
            True if fix applied successfully
        """
        logger.info(f"Applying fix: {fix_template.description}")
        
        try:
            # Execute commands
            for cmd in fix_template.commands:
                if cmd.startswith("#"):
                    continue  # Skip comments
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"Command failed: {cmd}")
                    logger.error(f"Error: {result.stderr}")
                    return False
            
            logger.info(f"✅ Fix applied successfully")
            return True
        
        except Exception as e:
            logger.error(f"❌ Fix application failed: {e}")
            return False
    
    def rollback(self) -> bool:
        """
        Rollback to checkpoint if fix fails.
        
        Returns:
            True if rollback successful
        """
        if not self.checkpoint_sha:
            logger.error("No checkpoint available for rollback")
            return False
        
        try:
            logger.warning(f"⚠️ Rolling back to {self.checkpoint_sha[:8]}...")
            
            subprocess.run(
                ["git", "reset", "--hard", self.checkpoint_sha],
                cwd=self.project_root,
                check=True
            )
            
            logger.info("✅ Rollback successful")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    # Helper methods
    
    def _extract_suggested_dir(self, suggestion: str) -> Optional[Path]:
        """Extract directory from suggestion text."""
        # Parse "Move file.py to one of: src/operations/modules"
        if "to one of:" in suggestion:
            dir_str = suggestion.split("to one of:")[-1].strip()
            dir_str = dir_str.split(',')[0].strip()  # Take first suggestion
            return self.project_root / dir_str
        return None
    
    def _trigger_to_class_name(self, trigger: str) -> str:
        """Convert trigger to class name."""
        words = trigger.split()
        return ''.join(w.capitalize() for w in words) + 'Orchestrator'
    
    def _class_to_filename(self, class_name: str) -> str:
        """Convert class name to filename."""
        # CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return name + ".py"
    
    def _generate_orchestrator_scaffold(self, class_name: str, trigger: str) -> str:
        """Generate scaffold code for orchestrator."""
        return f'''"""
{class_name} - Auto-generated scaffold

Generated by CORTEX Align remediation engine.

Author: CORTEX Auto-remediation
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus
)


class {class_name}(BaseOperationModule):
    """
    Orchestrator for '{trigger}' trigger.
    
    TODO: Implement orchestration logic
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize orchestrator."""
        super().__init__()
        self.project_root = project_root or Path.cwd()
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute orchestration.
        
        Args:
            context: Execution context
            
        Returns:
            OperationResult with execution status
        """
        start_time = datetime.now()
        
        try:
            # TODO: Implement logic here
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message="Operation completed successfully",
                data={{}},
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
        
        except Exception as e:
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Operation failed: {{e}}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
'''

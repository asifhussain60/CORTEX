"""
Configuration auto-repair system for CORTEX
Automatically fixes common config issues: missing files, malformed JSON, incorrect permissions

Part of Phase 4: Alignment Orchestrator
"""

import json
import os
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class RepairStatus(Enum):
    """Status of repair operation"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    NO_ACTION_NEEDED = "no_action_needed"


@dataclass
class RepairAction:
    """Represents a repair action taken"""
    description: str
    target_path: str
    action_type: str  # create_directory, repair_json, fix_permissions, etc.
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RepairResult:
    """Result of repair operations"""
    status: RepairStatus
    message: str
    actions: List[RepairAction] = field(default_factory=list)
    
    def add_action(self, action: RepairAction):
        """Add repair action to result"""
        self.actions.append(action)


class ConfigRepair:
    """
    Auto-repair system for CORTEX configuration issues
    
    Repairs:
    - Missing brain directories
    - Missing or malformed config files
    - Incorrect file permissions
    - Missing required structure fields
    """
    
    REQUIRED_BRAIN_DIRS = [
        "tier0",
        "tier1",
        "tier2",
        "tier3",
        "documents",
        "admin",
        "agents"
    ]
    
    REQUIRED_CONFIG_KEYS = ["machines", "version"]
    
    DEFAULT_CONFIG = {
        "machines": {},
        "version": "3.2.0",
        "governance": {
            "tdd_enforcement": True,
            "skull_protection": True
        }
    }
    
    def __init__(self, root_path: Path):
        """
        Initialize config repair system
        
        Args:
            root_path: Path to CORTEX root directory
        """
        self.root_path = Path(root_path)
        self.brain_path = self.root_path / "cortex-brain"
        self.config_path = self.root_path / "cortex.config.json"
        self.template_path = self.root_path / "cortex.config.template.json"
    
    def create_missing_directories(self) -> RepairResult:
        """
        Create missing brain directories
        
        Returns:
            RepairResult with created directories
        """
        result = RepairResult(
            status=RepairStatus.SUCCESS,
            message="Directory creation complete"
        )
        
        try:
            # Ensure brain directory exists
            if not self.brain_path.exists():
                self.brain_path.mkdir(parents=True)
                result.add_action(RepairAction(
                    description="Created brain directory",
                    target_path=str(self.brain_path),
                    action_type="create_directory"
                ))
            
            # Create required subdirectories
            for dir_name in self.REQUIRED_BRAIN_DIRS:
                dir_path = self.brain_path / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    result.add_action(RepairAction(
                        description=f"Created directory: {dir_name}",
                        target_path=str(dir_path),
                        action_type="create_directory"
                    ))
            
            if len(result.actions) == 0:
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "All directories already exist"
        
        except PermissionError as e:
            result.status = RepairStatus.FAILED
            result.message = f"Permission denied: {str(e)}"
        except Exception as e:
            result.status = RepairStatus.FAILED
            result.message = f"Failed to create directories: {str(e)}"
        
        return result
    
    def backup_config(self) -> Optional[Path]:
        """
        Create backup of existing config file
        
        Returns:
            Path to backup file, or None if config doesn't exist
        """
        if not self.config_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_path.parent / f"cortex.config.json.backup"
        
        try:
            shutil.copy2(self.config_path, backup_path)
            return backup_path
        except Exception:
            return None
    
    def repair_config_file(self) -> RepairResult:
        """
        Repair or create config file from template
        
        Returns:
            RepairResult with repair actions
        """
        result = RepairResult(
            status=RepairStatus.SUCCESS,
            message="Config file repaired"
        )
        
        try:
            # Check if config exists
            if not self.config_path.exists():
                # Try to copy from template
                if self.template_path.exists():
                    shutil.copy2(self.template_path, self.config_path)
                    result.add_action(RepairAction(
                        description="Created config from template",
                        target_path=str(self.config_path),
                        action_type="create_config"
                    ))
                else:
                    # Create default config
                    with open(self.config_path, 'w') as f:
                        json.dump(self.DEFAULT_CONFIG, f, indent=2)
                    result.add_action(RepairAction(
                        description="Created default config",
                        target_path=str(self.config_path),
                        action_type="create_config"
                    ))
                return result
            
            # Try to load existing config
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                
                # Config is valid, no action needed
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "Config file is valid"
                return result
            
            except json.JSONDecodeError:
                # Malformed JSON - backup and restore
                backup_path = self.backup_config()
                if backup_path:
                    result.add_action(RepairAction(
                        description="Backed up malformed config",
                        target_path=str(backup_path),
                        action_type="backup"
                    ))
                
                # Restore from template or create default
                if self.template_path.exists():
                    shutil.copy2(self.template_path, self.config_path)
                    result.add_action(RepairAction(
                        description="Restored config from template",
                        target_path=str(self.config_path),
                        action_type="repair_json"
                    ))
                else:
                    with open(self.config_path, 'w') as f:
                        json.dump(self.DEFAULT_CONFIG, f, indent=2)
                    result.add_action(RepairAction(
                        description="Created default config",
                        target_path=str(self.config_path),
                        action_type="repair_json"
                    ))
        
        except Exception as e:
            result.status = RepairStatus.FAILED
            result.message = f"Failed to repair config: {str(e)}"
        
        return result
    
    def repair_config_structure(self) -> RepairResult:
        """
        Repair config structure (add missing keys)
        
        Returns:
            RepairResult with structural repairs
        """
        result = RepairResult(
            status=RepairStatus.SUCCESS,
            message="Config structure repaired"
        )
        
        try:
            if not self.config_path.exists():
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "Config file doesn't exist"
                return result
            
            # Load config
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            modified = False
            
            # Check and add missing keys
            for key in self.REQUIRED_CONFIG_KEYS:
                if key not in config:
                    config[key] = self.DEFAULT_CONFIG[key]
                    modified = True
                    result.add_action(RepairAction(
                        description=f"Added missing key: {key}",
                        target_path=str(self.config_path),
                        action_type="add_key"
                    ))
            
            # Save if modified
            if modified:
                with open(self.config_path, 'w') as f:
                    json.dump(config, f, indent=2)
            else:
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "Config structure is valid"
        
        except json.JSONDecodeError:
            result.status = RepairStatus.FAILED
            result.message = "Cannot repair structure - config has invalid JSON"
        except Exception as e:
            result.status = RepairStatus.FAILED
            result.message = f"Failed to repair structure: {str(e)}"
        
        return result
    
    def fix_permissions(self) -> RepairResult:
        """
        Fix file permissions for config files
        
        Returns:
            RepairResult with permission fixes
        """
        result = RepairResult(
            status=RepairStatus.SUCCESS,
            message="Permissions fixed"
        )
        
        try:
            if not self.config_path.exists():
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "Config file doesn't exist"
                return result
            
            # Check if readable
            if not os.access(self.config_path, os.R_OK):
                # Try to fix permissions (readable by owner)
                os.chmod(self.config_path, 0o644)
                result.add_action(RepairAction(
                    description="Fixed config file permissions",
                    target_path=str(self.config_path),
                    action_type="fix_permissions"
                ))
            else:
                result.status = RepairStatus.NO_ACTION_NEEDED
                result.message = "Permissions are correct"
        
        except PermissionError as e:
            result.status = RepairStatus.FAILED
            result.message = f"Cannot fix permissions: {str(e)}"
        except Exception as e:
            result.status = RepairStatus.FAILED
            result.message = f"Failed to fix permissions: {str(e)}"
        
        return result
    
    def repair_all(self) -> RepairResult:
        """
        Run all repair operations
        
        Returns:
            Comprehensive RepairResult
        """
        all_actions = []
        all_results = []
        
        # Run all repairs
        repairs = [
            ("directories", self.create_missing_directories),
            ("config_file", self.repair_config_file),
            ("config_structure", self.repair_config_structure),
            ("permissions", self.fix_permissions)
        ]
        
        for name, repair_func in repairs:
            try:
                result = repair_func()
                all_results.append(result)
                all_actions.extend(result.actions)
            except Exception as e:
                all_results.append(RepairResult(
                    status=RepairStatus.FAILED,
                    message=f"{name} repair failed: {str(e)}"
                ))
        
        # Determine overall status
        if all(r.status in [RepairStatus.SUCCESS, RepairStatus.NO_ACTION_NEEDED] 
               for r in all_results):
            status = RepairStatus.SUCCESS
            message = "All repairs completed successfully"
        elif any(r.status == RepairStatus.SUCCESS for r in all_results):
            status = RepairStatus.PARTIAL
            message = "Some repairs completed, some failed"
        else:
            status = RepairStatus.FAILED
            message = "All repairs failed"
        
        return RepairResult(
            status=status,
            message=message,
            actions=all_actions
        )

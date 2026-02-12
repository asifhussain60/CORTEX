"""
Rule-Based Cleanup Planner - Declarative cleanup rules.

AC-ID: AC-VAC-ENH-004 | Phase: Enhancement #4
Purpose: Load cleanup rules from YAML and generate execution plans
Authority: CORTEX Vacuum Enhancement Phase 2

Rules defined in: .cortex/vacuum-rules.yaml
Enables: Non-developers to add cleanup rules without code changes
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import yaml
from datetime import datetime


class CleanupAction(Enum):
    """Actions that can be applied to matching files."""
    
    MOVE = "move"           # Move to destination directory
    DELETE = "delete"       # Remove from repository
    ARCHIVE = "archive"     # Move to docs/archive
    REVIEW = "review"       # Flag for manual review
    KEEP = "keep"          # Keep in current location
    IGNORE = "ignore"      # Ignore in cleanup


@dataclass
class CleanupRule:
    """Declarative cleanup rule specification."""
    
    name: str                      # Rule name for logging
    pattern: str                   # File glob pattern to match
    action: CleanupAction         # Action to take
    destination: Optional[str] = None  # Destination for MOVE/ARCHIVE
    priority: int = 5             # 1=highest, 10=lowest (default 5)
    condition: Optional[str] = None  # Optional predicate (not yet implemented)
    pre_action: Optional[Dict[str, Any]] = None  # Hook before action
    post_action: Optional[Dict[str, Any]] = None # Hook after action
    description: str = ""         # Human-readable description
    enabled: bool = True          # Can disable rules
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CleanupRule:
        """Create rule from dictionary (e.g., loaded from YAML)."""
        return cls(
            name=data.get("name", "unnamed"),
            pattern=data.get("pattern", ""),
            action=CleanupAction(data.get("action", "keep")),
            destination=data.get("destination"),
            priority=data.get("priority", 5),
            condition=data.get("condition"),
            pre_action=data.get("pre_action"),
            post_action=data.get("post_action"),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
        )


@dataclass
class CleanupItem:
    """Single file marked for cleanup by a rule."""
    
    file_path: str
    action: CleanupAction
    rule_name: str
    destination: Optional[str] = None
    priority: int = 5
    reason: str = ""
    confidence: float = 1.0


@dataclass
class CleanupPlan:
    """Complete cleanup plan generated from rules."""
    
    items: List[CleanupItem] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    rules_applied: int = 0
    files_matched: int = 0
    total_priority_score: int = 0
    
    @property
    def files_to_move(self) -> List[CleanupItem]:
        """Get files marked for moving."""
        return [i for i in self.items if i.action == CleanupAction.MOVE]
    
    @property
    def files_to_delete(self) -> List[CleanupItem]:
        """Get files marked for deletion."""
        return [i for i in self.items if i.action == CleanupAction.DELETE]
    
    @property
    def files_to_archive(self) -> List[CleanupItem]:
        """Get files marked for archival."""
        return [i for i in self.items if i.action == CleanupAction.ARCHIVE]
    
    @property
    def files_for_review(self) -> List[CleanupItem]:
        """Get files flagged for manual review."""
        return [i for i in self.items if i.action == CleanupAction.REVIEW]
    
    def sort_by_priority(self) -> None:
        """Sort items by priority (lower number = higher priority)."""
        self.items.sort(key=lambda x: (x.priority, x.file_path))


class RuleBasedPlanner:
    """Generate cleanup plans from declarative YAML rules."""
    
    DEFAULT_RULES_FILE = Path(".cortex/vacuum-rules.yaml")
    
    def __init__(self, repo_root: Path = Path("."), rules_file: Optional[Path] = None):
        """Initialize planner.
        
        Args:
            repo_root: Repository root path
            rules_file: Path to rules YAML file (default: .cortex/vacuum-rules.yaml)
        """
        self.repo_root = Path(repo_root)
        self.rules_file = rules_file or self.repo_root / self.DEFAULT_RULES_FILE
        self.rules: List[CleanupRule] = []
        
        # Load rules if file exists
        if self.rules_file.exists():
            self.load_rules()
    
    def load_rules(self) -> bool:
        """Load rules from YAML file.
        
        Returns:
            True if rules loaded successfully
        """
        try:
            with open(self.rules_file, "r") as f:
                data = yaml.safe_load(f) or {}
            
            self.rules = []
            for rule_dict in data.get("rules", []):
                rule = CleanupRule.from_dict(rule_dict)
                if rule.enabled:
                    self.rules.append(rule)
            
            # Sort by priority
            self.rules.sort(key=lambda r: r.priority)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to load rules from {self.rules_file}: {e}")
            return False
    
    def generate_plan(self, root_path: Optional[Path] = None) -> CleanupPlan:
        """Generate cleanup plan by applying rules to repository.
        
        Args:
            root_path: Path to scan (default: repo_root)
            
        Returns:
            CleanupPlan with all matched files
        """
        root_path = root_path or self.repo_root
        plan = CleanupPlan()
        
        # Collect all files
        all_files = list(root_path.rglob("*"))
        
        # Apply each rule
        for rule in self.rules:
            matched_files = self._match_files(all_files, rule.pattern)
            
            for file_path in matched_files:
                # Skip if already matched by higher-priority rule
                if any(
                    item.file_path == str(file_path.relative_to(root_path))
                    for item in plan.items
                ):
                    continue
                
                # Create cleanup item
                item = CleanupItem(
                    file_path=str(file_path.relative_to(root_path)),
                    action=rule.action,
                    rule_name=rule.name,
                    destination=rule.destination,
                    priority=rule.priority,
                    reason=rule.description,
                )
                
                plan.items.append(item)
                plan.rules_applied += 1
            
            plan.files_matched += len(matched_files)
        
        # Sort by priority
        plan.sort_by_priority()
        
        return plan
    
    def _match_files(self, files: List[Path], pattern: str) -> List[Path]:
        """Match files against glob pattern.
        
        Args:
            files: List of all files to check
            pattern: Glob pattern to match
            
        Returns:
            List of matching file paths
        """
        from fnmatch import fnmatch
        
        matched = []
        for file_path in files:
            if file_path.is_file():
                # Try relative path matching
                rel_path = str(file_path.relative_to(self.repo_root))
                if fnmatch(rel_path, pattern) or fnmatch(file_path.name, pattern):
                    matched.append(file_path)
        
        return matched
    
    def save_default_rules(self) -> bool:
        """Create default rules file if it doesn't exist.
        
        Returns:
            True if file created or already exists
        """
        if self.rules_file.exists():
            return True
        
        try:
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)
            
            default_rules = {
                "rules": [
                    {
                        "name": "utility_scripts",
                        "pattern": "scripts/utilities/*.py",
                        "action": "keep",
                        "priority": 1,
                        "description": "Keep utility scripts in scripts/utilities/",
                    },
                    {
                        "name": "phase_markers",
                        "pattern": ".phase*",
                        "action": "archive",
                        "destination": "cortex_brain/state/archive/phase-markers/",
                        "priority": 2,
                        "description": "Archive phase completion markers",
                    },
                    {
                        "name": "macos_artifacts",
                        "pattern": ".DS_Store",
                        "action": "delete",
                        "priority": 1,
                        "description": "Remove macOS artifacts",
                    },
                    {
                        "name": "pycache",
                        "pattern": "__pycache__",
                        "action": "delete",
                        "priority": 1,
                        "description": "Remove Python cache directories",
                    },
                ]
            }
            
            with open(self.rules_file, "w") as f:
                yaml.dump(default_rules, f, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"Warning: Failed to create default rules: {e}")
            return False


# AC_START: AC-VAC-ENH-004 | Rule-based cleanup planning
__all__ = [
    "CleanupAction",
    "CleanupRule",
    "CleanupItem",
    "CleanupPlan",
    "RuleBasedPlanner",
]
# AC_COMPLETE: AC-VAC-ENH-004 ✅ Rule-based planner with YAML configuration

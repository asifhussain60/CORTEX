"""
Conflict Detection Engine for System Alignment

Detects internal CORTEX ecosystem conflicts:
- Duplicate module names across directories
- Orphaned wiring (YAML references non-existent modules)
- Architectural drift (modules in wrong locations)
- Missing dependencies (imports don't resolve)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass, field
import importlib.util
import ast
import yaml

logger = logging.getLogger(__name__)


@dataclass
class Conflict:
    """Represents a detected conflict in CORTEX ecosystem."""
    conflict_type: str  # 'duplicate_module', 'orphaned_wiring', 'drift', 'missing_dependency'
    severity: str  # 'critical', 'warning', 'info'
    title: str
    description: str
    affected_files: List[Path] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            'type': self.conflict_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'affected_files': [str(f) for f in self.affected_files],
            'suggested_fix': self.suggested_fix,
            'auto_fixable': self.auto_fixable
        }


class ConflictDetector:
    """
    Detects internal conflicts in CORTEX ecosystem.
    
    Detection Algorithms:
    1. Duplicate Module Names: Scans src/ for classes with same name
    2. Orphaned Wiring: YAML triggers pointing to non-existent modules
    3. Architectural Drift: Modules in wrong directory structure
    4. Missing Dependencies: Import statements that don't resolve
    """
    
    def __init__(self, project_root: Path):
        """Initialize conflict detector."""
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.brain_path = project_root / "cortex-brain"
        self.conflicts: List[Conflict] = []
    
    def detect_all_conflicts(self) -> List[Conflict]:
        """
        Run all conflict detection algorithms.
        
        Returns:
            List of detected conflicts
        """
        logger.info("🔍 Running conflict detection...")
        
        self.conflicts = []
        
        # Run all detectors
        self._detect_duplicate_modules()
        self._detect_orphaned_wiring()
        self._detect_architectural_drift()
        self._detect_missing_dependencies()
        
        logger.info(f"✅ Found {len(self.conflicts)} conflicts")
        
        # Sort by severity
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        self.conflicts.sort(key=lambda c: severity_order[c.severity])
        
        return self.conflicts
    
    def _detect_duplicate_modules(self) -> None:
        """Detect duplicate module names across directories."""
        logger.debug("Checking for duplicate module names...")
        
        # Scan all Python files for class definitions
        class_registry: Dict[str, List[Path]] = {}
        
        for py_file in self.src_path.rglob("*.py"):
            if py_file.stem.startswith("_") or "test_" in py_file.stem:
                continue  # Skip private and test files
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        if class_name.endswith(('Orchestrator', 'Agent', 'Module', 'Handler')):
                            if class_name not in class_registry:
                                class_registry[class_name] = []
                            class_registry[class_name].append(py_file)
            
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue
        
        # Find duplicates
        for class_name, files in class_registry.items():
            if len(files) > 1:
                self.conflicts.append(Conflict(
                    conflict_type='duplicate_module',
                    severity='warning',
                    title=f"Duplicate class name: {class_name}",
                    description=f"Class '{class_name}' defined in {len(files)} locations. This can cause import ambiguity.",
                    affected_files=files,
                    suggested_fix=f"Rename one of the classes or consolidate into single implementation",
                    auto_fixable=False
                ))
    
    def _detect_orphaned_wiring(self) -> None:
        """Detect YAML triggers that point to non-existent modules."""
        logger.debug("Checking for orphaned wiring...")
        
        # Load response templates
        templates_file = self.brain_path / "response-templates.yaml"
        if not templates_file.exists():
            return
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_data = yaml.safe_load(f)
            
            # Extract triggers
            triggers = set()
            for category in templates_data.values():
                if isinstance(category, dict):
                    for template in category.values():
                        if isinstance(template, dict):
                            trigger_list = template.get('triggers', [])
                            triggers.update(trigger_list)
            
            # Check each trigger has corresponding implementation
            for trigger in triggers:
                # Search for orchestrator/agent with matching name
                found = self._find_implementation_for_trigger(trigger)
                
                if not found:
                    self.conflicts.append(Conflict(
                        conflict_type='orphaned_wiring',
                        severity='critical',
                        title=f"Orphaned trigger: '{trigger}'",
                        description=f"Response template defines trigger '{trigger}' but no corresponding orchestrator/agent found",
                        affected_files=[templates_file],
                        suggested_fix=f"Either implement orchestrator for '{trigger}' or remove trigger from templates",
                        auto_fixable=False
                    ))
        
        except Exception as e:
            logger.warning(f"Could not validate wiring: {e}")
    
    def _find_implementation_for_trigger(self, trigger: str) -> bool:
        """Check if implementation exists for a trigger."""
        # Convert trigger to possible class names
        # e.g., "plan ado" -> PlanAdoOrchestrator, ADOPlanningOrchestrator, etc.
        words = trigger.split()
        possible_names = [
            ''.join(w.capitalize() for w in words) + 'Orchestrator',
            ''.join(w.capitalize() for w in words) + 'Agent',
            ''.join(w.capitalize() for w in words) + 'Module',
        ]
        
        # Search src/ for these class names
        for py_file in self.src_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for class_name in possible_names:
                    if f"class {class_name}" in content:
                        return True
            
            except Exception:
                continue
        
        return False
    
    def _detect_architectural_drift(self) -> None:
        """Detect modules in wrong directory structure."""
        logger.debug("Checking for architectural drift...")
        
        # Define expected locations for different module types
        expected_locations = {
            'Orchestrator': [
                self.src_path / 'operations' / 'modules',
                self.src_path / 'workflows',
                self.src_path / 'orchestrators'
            ],
            'Agent': [
                self.src_path / 'agents',
                self.src_path / 'cortex_agents'
            ],
            'Module': [
                self.src_path / 'operations' / 'modules',
                self.src_path / 'tier0',
                self.src_path / 'tier1',
                self.src_path / 'tier2',
                self.src_path / 'tier3'
            ]
        }
        
        # Scan all Python files
        for py_file in self.src_path.rglob("*.py"):
            if py_file.stem.startswith("_") or "test_" in py_file.stem:
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        # Check if class matches expected pattern
                        for suffix, expected_dirs in expected_locations.items():
                            if class_name.endswith(suffix):
                                # Check if file is in expected location
                                in_correct_location = any(
                                    py_file.is_relative_to(expected_dir)
                                    for expected_dir in expected_dirs
                                    if expected_dir.exists()
                                )
                                
                                if not in_correct_location:
                                    expected_str = ' or '.join(str(d.relative_to(self.project_root)) for d in expected_dirs if d.exists())
                                    actual_str = str(py_file.relative_to(self.project_root).parent)
                                    
                                    self.conflicts.append(Conflict(
                                        conflict_type='drift',
                                        severity='warning',
                                        title=f"Architectural drift: {class_name}",
                                        description=f"{class_name} should be in {expected_str} but found in {actual_str}",
                                        affected_files=[py_file],
                                        suggested_fix=f"Move {py_file.name} to one of: {expected_str}",
                                        auto_fixable=True  # Can auto-generate move command
                                    ))
            
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue
    
    def _detect_missing_dependencies(self) -> None:
        """Detect import statements that don't resolve."""
        logger.debug("Checking for missing dependencies...")
        
        # Scan all Python files for imports
        for py_file in self.src_path.rglob("*.py"):
            if py_file.stem.startswith("_"):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        # Get module name
                        if isinstance(node, ast.Import):
                            module_names = [alias.name for alias in node.names]
                        else:
                            module_names = [node.module] if node.module else []
                        
                        # Check if module can be resolved
                        for module_name in module_names:
                            if module_name and module_name.startswith('src.'):
                                # Internal CORTEX import - verify it exists
                                if not self._can_resolve_import(module_name):
                                    self.conflicts.append(Conflict(
                                        conflict_type='missing_dependency',
                                        severity='critical',
                                        title=f"Unresolved import: {module_name}",
                                        description=f"{py_file.name} imports '{module_name}' which cannot be resolved",
                                        affected_files=[py_file],
                                        suggested_fix=f"Check if module exists or fix import path",
                                        auto_fixable=False
                                    ))
            
            except Exception as e:
                logger.debug(f"Could not parse {py_file}: {e}")
                continue
    
    def _can_resolve_import(self, module_name: str) -> bool:
        """Check if an import can be resolved."""
        # Convert module name to file path
        # e.g., 'src.operations.base' -> 'src/operations/base.py' or 'src/operations/base/__init__.py'
        parts = module_name.split('.')
        
        # Try as file
        file_path = self.project_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
        if file_path.exists():
            return True
        
        # Try as package
        package_path = self.project_root / Path(*parts) / "__init__.py"
        if package_path.exists():
            return True
        
        return False
    
    def get_conflicts_by_severity(self, severity: str) -> List[Conflict]:
        """Get conflicts filtered by severity."""
        return [c for c in self.conflicts if c.severity == severity]
    
    def get_auto_fixable_conflicts(self) -> List[Conflict]:
        """Get conflicts that can be auto-fixed."""
        return [c for c in self.conflicts if c.auto_fixable]

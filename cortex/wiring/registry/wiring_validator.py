"""
Wiring Validator - Validate orchestrator wiring integrity.

Authority: cortex-registry/_cortex-master/phases/completed/2025/ (Phase 3)
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)


class WiringValidator:
    """
    Validate wiring.yaml for common issues and best practices.
    
    Checks:
    - No circular dependencies
    - All dependencies exist
    - Required fields present
    - Module paths valid
    - Tier ordering correct
    - No duplicate names
    
    Example:
        >>> validator = WiringValidator()
        >>> errors, warnings = validator.validate()
        >>> if errors:
        ...     print(f"Validation failed: {errors}")
    """
    
    def __init__(self, wiring_file: Optional[Path] = None) -> None:
        """
        Initialize validator.
        
        Args:
            wiring_file: Path to wiring.yaml (default: cortex/wiring/specifications/wiring.yaml)
        """
        if wiring_file is None:
            wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
        
        self.wiring_file = wiring_file
        self._spec: Optional[Dict[str, Any]] = None
    
    def validate(self) -> Tuple[List[str], List[str]]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (errors, warnings)
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # Load specification
        try:
            self._load_spec()
        except Exception as e:
            errors.append(f"Failed to load wiring specification: {e}")
            return errors, warnings
        
        # Run validation checks
        errors.extend(self._check_required_structure())
        errors.extend(self._check_circular_dependencies())
        errors.extend(self._check_missing_dependencies())
        errors.extend(self._check_duplicate_names())
        
        warnings.extend(self._check_tier_ordering())
        warnings.extend(self._check_module_paths())
        warnings.extend(self._check_health_checks())
        
        return errors, warnings
    
    def _load_spec(self) -> None:
        """Load YAML specification."""
        if not self.wiring_file.exists():
            raise FileNotFoundError(f"Wiring file not found: {self.wiring_file}")
        
        with open(self.wiring_file, 'r') as f:
            self._spec = yaml.safe_load(f)
    
    def _check_required_structure(self) -> List[str]:
        """Check that required top-level keys exist."""
        errors: List[str] = []
        
        if not self._spec:
            errors.append("Specification is empty")
            return errors
        
        if 'orchestrators' not in self._spec:
            errors.append("Missing 'orchestrators' key")
            return errors
        
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                errors.append(f"Missing '{category}' category")
        
        # Check required fields for each orchestrator
        required_fields = {'name', 'module', 'class', 'tier', 'priority', 'dependencies', 'capabilities', 'health_check'}
        
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            
            for orch in self._spec['orchestrators'][category]:
                name = orch.get('name', 'UNKNOWN')
                missing = required_fields - set(orch.keys())
                if missing:
                    errors.append(f"Orchestrator '{name}' missing fields: {missing}")
        
        return errors
    
    def _check_circular_dependencies(self) -> List[str]:
        """Check for circular dependencies."""
        errors: List[str] = []
        
        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                deps = orch.get('dependencies', [])
                graph[name] = deps
        
        # DFS cycle detection
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    errors.append(f"Circular dependency: {' -> '.join(cycle)}")
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        visited: Set[str] = set()
        for node in graph:
            if node not in visited:
                has_cycle(node, visited, set(), [])
        
        return errors
    
    def _check_missing_dependencies(self) -> List[str]:
        """Check that all dependency names reference existing orchestrators."""
        errors: List[str] = []
        
        # Collect all orchestrator names
        all_names: Set[str] = set()
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                all_names.add(orch['name'])
        
        # Verify all dependencies exist
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                for dep in orch.get('dependencies', []):
                    if dep not in all_names:
                        errors.append(f"Orchestrator '{name}' depends on non-existent '{dep}'")
        
        return errors
    
    def _check_duplicate_names(self) -> List[str]:
        """Check for duplicate orchestrator names."""
        errors: List[str] = []
        
        seen: Set[str] = set()
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                if name in seen:
                    errors.append(f"Duplicate orchestrator name: '{name}'")
                seen.add(name)
        
        return errors
    
    def _check_tier_ordering(self) -> List[str]:
        """Check that lower tiers don't depend on higher tiers."""
        warnings: List[str] = []
        
        # Build tier map
        tier_map: Dict[str, int] = {}
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                tier_map[orch['name']] = orch['tier']
        
        # Check dependencies
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                tier = orch['tier']
                for dep in orch.get('dependencies', []):
                    dep_tier = tier_map.get(dep)
                    if dep_tier and dep_tier > tier:
                        warnings.append(
                            f"Tier violation: '{name}' (tier {tier}) depends on '{dep}' (tier {dep_tier})"
                        )
        
        return warnings
    
    def _check_module_paths(self) -> List[str]:
        """Check that module paths look valid."""
        warnings: List[str] = []
        
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                module = orch.get('module', '')
                
                if not module.startswith('cortex.'):
                    warnings.append(f"Orchestrator '{name}' has non-cortex module: {module}")
        
        return warnings
    
    def _check_health_checks(self) -> List[str]:
        """Check that all orchestrators have health checks defined."""
        warnings: List[str] = []
        
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch in self._spec['orchestrators'][category]:
                name = orch['name']
                if not orch.get('health_check'):
                    warnings.append(f"Orchestrator '{name}' missing health check")
        
        return warnings


def validate_wiring(wiring_file: Optional[Path] = None) -> bool:
    """
    Validate wiring and print results.
    
    Args:
        wiring_file: Path to wiring.yaml
        
    Returns:
        True if valid (no errors), False otherwise
    """
    validator = WiringValidator(wiring_file)
    errors, warnings = validator.validate()
    
    if errors:
        print("❌ Wiring validation FAILED:")
        for error in errors:
            print(f"  ERROR: {error}")
    
    if warnings:
        print("⚠️  Wiring validation warnings:")
        for warning in warnings:
            print(f"  WARNING: {warning}")
    
    if not errors and not warnings:
        print("✅ Wiring validation PASSED")
    
    return len(errors) == 0
